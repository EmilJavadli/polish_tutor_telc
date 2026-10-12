"""CEFR evidence-based placement UI with resumable initial and retake modes."""
import streamlit as st
from placement.test_bank import (
    GRAMMAR_VOCAB, READING, READING_BLOCKS, LISTENING, LISTENING_BLOCKS,
    WRITING_PROMPT, SPEAKING_PROMPTS,
)
from placement.scoring import objective_profile, normalize_productive, classify, SKILL_LABELS
from placement.grader import grade_productive
from agent.tts import synthesize_speech
from agent.llm import transcribe


def _choices(items, prefix):
    answers = {}
    for item in items:
        value = st.radio(
            item["q"], range(len(item["options"])),
            format_func=lambda i, options=item["options"]: options[i],
            index=None, key=f"{prefix}{item['id']}",
        )
        answers[item["id"]] = "" if value is None else str(value)
    return answers


def _missing(items, answers):
    return [item["id"] for item in items if not str(answers.get(item["id"], "")).strip()]


def _level_table(scores):
    rows = []
    for key, label in SKILL_LABELS.items():
        profile = scores.get(key, {})
        if isinstance(profile, dict):
            rows.append({
                "Skill": label,
                "CEFR estimate": profile.get("level", "A0"),
                "Secondary score": f"{float(profile.get('score', 0)):.0f}%",
                "Confidence": f"{float(profile.get('confidence', 0)):.0%}",
            })
        else:
            rows.append({"Skill": label, "CEFR estimate": "Legacy", "Secondary score": f"{float(profile):.0f}%", "Confidence": "-"})
    return rows


def render_retake_result(repo, profile, evaluation):
    old_scores = dict(profile.skill_profile or {})
    new_scores = dict(evaluation.scores or {})
    st.title("Placement retake results")
    c1, c2 = st.columns(2)
    c1.metric("Current overall level", profile.current_cefr_level or "A0")
    c2.metric("New overall estimate", evaluation.assigned_level or "A0")

    rows = []
    for key, label in SKILL_LABELS.items():
        old = old_scores.get(key, {})
        new = new_scores.get(key, {})
        old_level = old.get("level", "-") if isinstance(old, dict) else "Legacy"
        new_level = new.get("level", "A0") if isinstance(new, dict) else "Legacy"
        rows.append({"Skill": label, "Previous CEFR": old_level, "New CEFR": new_level})
    st.table(rows)
    if evaluation.strengths:
        st.success("Strengths: " + ", ".join(SKILL_LABELS.get(x, x) for x in evaluation.strengths))
    if evaluation.weaknesses:
        st.warning("Priorities: " + ", ".join(SKILL_LABELS.get(x, x) for x in evaluation.weaknesses))
    st.info("Updating the plan changes only future learning. Completed lessons and previous evidence stay saved.")

    left, right = st.columns(2)
    with left:
        if st.button("Update my study plan", type="primary", width="stretch"):
            repo.apply_result(evaluation.id, daily_minutes=profile.daily_study_minutes, target_level=profile.target_cefr_level)
            st.session_state["placement_retake"] = False
            st.session_state["placement_result"] = {"level": evaluation.assigned_level, "overall": _overall_score(new_scores)}
            st.rerun()
    with right:
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
    st.title("Polish CEFR placement" if mode == "initial" else "Retake Polish CEFR placement")
    st.caption("The test estimates what you can do in reading, listening, grammar/vocabulary, writing and speaking from A0 to B1. It is a placement estimate, not an official CEFR certificate.")
    st.progress({"grammar_vocab":.1,"reading":.3,"listening":.5,"writing":.7,"speaking":.9,"complete":1}.get(section,0))

    if mode == "retake":
        st.info("Your current study plan remains active until you accept the new result.")
        if st.button("Cancel placement retake"):
            repo.cancel_in_progress(); st.session_state["placement_retake"] = False; st.rerun()

    if section == "grammar_vocab":
        st.subheader("1. Grammar and vocabulary")
        st.write("Questions progress from familiar A1 language to connected B1 language.")
        with st.form("placement_grammar_vocab"):
            answers = _choices(GRAMMAR_VOCAB, "pg_")
            if st.form_submit_button("Continue", type="primary"):
                missing = _missing(GRAMMAR_VOCAB, answers)
                if missing: st.warning(f"Please answer all {len(missing)} remaining questions.")
                else: repo.save_section(evaluation.id, section, answers, "reading"); st.rerun()

    elif section == "reading":
        st.subheader("2. Reading")
        with st.form("placement_reading"):
            answers = {}
            for block in READING_BLOCKS:
                st.markdown(f"### {block['title']}")
                st.markdown(block["text"])
                answers.update(_choices(block["items"], f"pr_{block['band']}_"))
                st.divider()
            if st.form_submit_button("Continue", type="primary"):
                missing = _missing(READING, answers)
                if missing: st.warning(f"Please answer all {len(missing)} remaining questions.")
                else: repo.save_section(evaluation.id, section, answers, "listening"); st.rerun()

    elif section == "listening":
        st.subheader("3. Listening")
        st.caption("Listen before answering. Each recording provides evidence at a different CEFR band.")
        all_answers = {}
        for block in LISTENING_BLOCKS:
            st.markdown(f"### {block['title']}")
            state_key = f"placement_audio_{evaluation.id}_{block['band']}"
            audio = st.session_state.get(state_key)
            if audio:
                st.audio(audio, format="audio/mpeg")
            elif st.button(f"Create {block['band']} recording", key=f"make_{state_key}"):
                with st.spinner("Creating recording…"):
                    audio = synthesize_speech(block["text"])
                    st.session_state[state_key] = audio
                    st.audio(audio, format="audio/mpeg")
            with st.form(f"listening_{block['band']}"):
                block_answers = _choices(block["items"], f"pl_{block['band']}_")
                submitted = st.form_submit_button(f"Save {block['band']} answers")
                if submitted:
                    saved = dict(st.session_state.get(f"saved_listening_{evaluation.id}", {}))
                    saved.update(block_answers)
                    st.session_state[f"saved_listening_{evaluation.id}"] = saved
                    st.toast(f"{block['band']} answers saved")
            all_answers.update(st.session_state.get(f"saved_listening_{evaluation.id}", {}))
        if st.button("Continue to writing", type="primary"):
            missing = _missing(LISTENING, all_answers)
            if missing: st.warning(f"Please save answers for all recordings. {len(missing)} answers remain.")
            else: repo.save_section(evaluation.id, section, all_answers, "writing"); st.rerun()

    elif section == "writing":
        st.subheader("4. Writing")
        st.markdown(f"**{WRITING_PROMPT['instruction']}**")
        for point in WRITING_PROMPT["points"]: st.markdown(f"- {point}")
        st.caption(WRITING_PROMPT["guidance"])
        text = st.text_area("Your Polish text", value=responses.get("writing", {}).get("text", ""), height=260)
        st.caption(f"Words: {len(text.split())}")
        if st.button("Save and continue", type="primary"):
            if not text.strip(): st.warning("Please write an answer before continuing.")
            else: repo.save_section(evaluation.id, section, {"text": text}, "speaking"); st.rerun()

    elif section == "speaking":
        st.subheader("5. Speaking")
        st.write("Respond to all three prompts in one recording. The assessment uses the transcript and does not assess pronunciation.")
        for item in SPEAKING_PROMPTS: st.markdown(f"**{item['band']} prompt:** {item['prompt']}")
        recording = st.audio_input("Record your response")
        typed = st.text_area("Or type what you would say", height=180)
        if st.button("Complete evaluation", type="primary"):
            speech = transcribe(recording.getvalue(), context="Polish CEFR placement response") if recording is not None else typed.strip()
            if not speech: st.warning("Please record or type a speaking response."); return
            repo.save_section(evaluation.id, section, {"transcript": speech}, "complete")
            all_responses = {**responses, "speaking": {"transcript": speech}}
            with st.spinner("Assessing CEFR evidence across five skills…"):
                profiles = {
                    "grammar_vocab": objective_profile(GRAMMAR_VOCAB, all_responses.get("grammar_vocab", {})),
                    "reading": objective_profile(READING, all_responses.get("reading", {})),
                    "listening": objective_profile(LISTENING, all_responses.get("listening", {})),
                    "writing": normalize_productive(grade_productive("writing", all_responses.get("writing", {}).get("text", ""))),
                    "speaking": normalize_productive(grade_productive("speaking", speech)),
                }
                result = classify(profiles)
            repo.save_result(evaluation.id, result, mode=mode)
            if mode == "initial":
                repo.apply_result(evaluation.id, daily_minutes=st.session_state.get("daily_minutes", 60), target_level=st.session_state.get("target_level", "B1"))
                st.session_state["placement_result"] = result
            else:
                st.session_state["placement_retake"] = True
            st.rerun()

    elif section == "complete":
        if mode == "retake" and (pending := repo.pending_review()) is not None:
            render_retake_result(repo, profile, pending)
        else:
            st.rerun()


def _overall_score(scores):
    values = [float(x.get("score", 0)) for x in scores.values() if isinstance(x, dict)]
    return sum(values) / len(values) if values else 0
