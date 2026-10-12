"""Placement test UI with initial-placement and optional-retake modes."""
import streamlit as st
from placement.test_bank import GRAMMAR_VOCAB, READING, READING_TEXT, LISTENING, LISTENING_TEXT
from placement.scoring import objective_score, classify
from placement.grader import grade_productive
from agent.tts import synthesize_speech
from agent.llm import transcribe


def _choices(items, prefix):
    answers = {}
    for item in items:
        value = st.radio(
            item["q"],
            range(len(item["options"])),
            format_func=lambda i, options=item["options"]: options[i],
            index=None,
            key=f"{prefix}{item['id']}",
        )
        answers[item["id"]] = "" if value is None else str(value)
    return answers


def render_retake_result(repo, profile, evaluation):
    old_scores = dict(profile.skill_profile or {})
    new_scores = dict(evaluation.scores or {})
    old_level = profile.current_cefr_level or "A0"
    new_level = evaluation.assigned_level or "A0"

    st.title("Placement retake results")
    c1, c2 = st.columns(2)
    c1.metric("Current level", old_level)
    c2.metric("New placement result", new_level)

    labels = {
        "reading": "Reading",
        "listening": "Listening",
        "grammar_vocab": "Grammar and vocabulary",
        "writing": "Writing",
        "speaking": "Speaking",
    }
    comparison = []
    for key, label in labels.items():
        before = float(old_scores.get(key, 0))
        after = float(new_scores.get(key, 0))
        comparison.append({
            "Skill": label,
            "Previous": f"{before:.0f}%",
            "New": f"{after:.0f}%",
            "Change": f"{after-before:+.0f}",
        })
    st.table(comparison)

    if evaluation.strengths:
        st.success("Strengths: " + ", ".join(labels.get(x, x) for x in evaluation.strengths))
    if evaluation.weaknesses:
        st.warning("Priority areas: " + ", ".join(labels.get(x, x) for x in evaluation.weaknesses))

    st.info(
        "Updating the plan changes only future lessons. Completed lessons, attempts, "
        "vocabulary progress, grammar progress and older evaluations remain saved."
    )
    update_col, keep_col = st.columns(2)
    with update_col:
        if st.button("Update my study plan", type="primary", width="stretch"):
            repo.apply_result(
                evaluation.id,
                daily_minutes=profile.daily_study_minutes,
                target_level=profile.target_cefr_level,
            )
            st.session_state["placement_retake"] = False
            st.session_state["placement_result"] = {
                "level": new_level,
                "overall": sum(new_scores.values()) / len(new_scores) if new_scores else 0,
            }
            st.rerun()
    with keep_col:
        if st.button("Keep my current plan", width="stretch"):
            repo.keep_current_plan(evaluation.id)
            st.session_state["placement_retake"] = False
            st.rerun()


def render(repo, profile, *, mode="initial"):
    pending = repo.pending_review()
    if mode == "retake" and pending is not None:
        render_retake_result(repo, profile, pending)
        return

    evaluation = repo.get_or_create(mode=mode)
    section = evaluation.current_section
    responses = dict(evaluation.responses or {})

    st.title("Polish placement evaluation" if mode == "initial" else "Retake Polish placement evaluation")
    st.caption("Your progress is saved after each section. You can leave and return later.")

    if mode == "retake":
        st.info("Your current plan remains active until you explicitly accept the new result.")
        if st.button("Cancel placement retake"):
            repo.cancel_in_progress()
            st.session_state["placement_retake"] = False
            st.rerun()

    if section == "grammar_vocab":
        with st.form("placement_grammar_vocab"):
            answers = _choices(GRAMMAR_VOCAB, "pg_")
            if st.form_submit_button("Continue", type="primary"):
                repo.save_section(evaluation.id, section, answers, "reading")
                st.rerun()

    elif section == "reading":
        st.markdown(READING_TEXT)
        with st.form("placement_reading"):
            answers = _choices(READING, "pr_")
            if st.form_submit_button("Continue", type="primary"):
                repo.save_section(evaluation.id, section, answers, "listening")
                st.rerun()

    elif section == "listening":
        st.write("Listen and answer the questions.")
        audio = st.session_state.get("placement_audio")
        if audio:
            st.audio(audio, format="audio/mpeg")
        elif st.button("Create placement audio"):
            with st.spinner("Creating recording…"):
                audio = synthesize_speech(LISTENING_TEXT)
                st.session_state["placement_audio"] = audio
                st.audio(audio, format="audio/mpeg")
        with st.form("placement_listening"):
            answers = _choices(LISTENING, "pl_")
            if st.form_submit_button("Continue", type="primary"):
                repo.save_section(evaluation.id, section, answers, "writing")
                st.rerun()

    elif section == "writing":
        st.write("Write about yourself, life in Poland, a normal week, and one past or future plan.")
        text = st.text_area("Your Polish text", height=220)
        if st.button("Save and continue", type="primary"):
            if not text.strip():
                st.warning("Please write an answer before continuing.")
            else:
                repo.save_section(evaluation.id, section, {"text": text}, "speaking")
                st.rerun()

    elif section == "speaking":
        st.write("Introduce yourself, describe a normal day, and mention one past experience or future plan.")
        recording = st.audio_input("Record your answer")
        typed = st.text_area("Or type what you would say")
        if st.button("Complete evaluation", type="primary"):
            speech = transcribe(recording.getvalue()) if recording is not None else typed.strip()
            if not speech:
                st.warning("Please record or type a speaking answer.")
                return

            repo.save_section(evaluation.id, section, {"transcript": speech}, "complete")
            all_responses = {**responses, "speaking": {"transcript": speech}}
            scores = {
                "grammar_vocab": objective_score(GRAMMAR_VOCAB, all_responses.get("grammar_vocab", {})),
                "reading": objective_score(READING, all_responses.get("reading", {})),
                "listening": objective_score(LISTENING, all_responses.get("listening", {})),
                "writing": grade_productive("writing", all_responses.get("writing", {}).get("text", "")),
                "speaking": grade_productive("speaking", speech),
            }
            result = classify(scores)
            repo.save_result(evaluation.id, result, mode=mode)

            if mode == "initial":
                repo.apply_result(
                    evaluation.id,
                    daily_minutes=st.session_state.get("daily_minutes", 60),
                    target_level=st.session_state.get("target_level", "B1"),
                )
                st.session_state["placement_result"] = result
            else:
                st.session_state["placement_retake"] = True
            st.rerun()

    elif section == "complete":
        pending = repo.pending_review()
        if mode == "retake" and pending is not None:
            render_retake_result(repo, profile, pending)
        else:
            st.rerun()
