"""Polish Tutor: 9-month TELC Polski B1 preparation (Streamlit).

Run with:  streamlit run app.py
"""
import datetime as dt
import re

import streamlit as st

from agent.graders import (
    grade_exercises, grade_listening, grade_quiz, grade_speaking, grade_writing,
)
from agent.lesson_generator import LessonGenerationError, generate_lesson
from agent.llm import transcribe
from agent.schemas import Lesson, ProductionFeedback, SpeakingAttempt, WritingAttempt
from agent.tts import synthesize_dialogue, synthesize_speech, tts_available
from agent.tutor_chat import stream_tutor_reply
from config import DATA_DIR, OPENAI_API_KEY, QUIZ_PASS_SCORE, TIME_PLAN
from curriculum import (
    GRAMMAR, SPEAKING_PART_NAMES, TOTAL_DAYS, WEEKS, get_plan_day, plan_markdown,
)
from storage.repository import LessonRepository

st.set_page_config(page_title="Polish Tutor · TELC B1", page_icon="🇵🇱", layout="wide")

QUIZ_TYPE_LABELS = {
    "multiple_choice": "Choose the correct answer",
    "fill_blank": "Fill in the gap with the correct form",
    "open": "Answer in a full Polish sentence",
}


@st.cache_resource
def get_repository() -> LessonRepository:
    return LessonRepository(DATA_DIR)


repo = get_repository()
today = dt.date.today()


# =========================================================================
# helpers
# =========================================================================
def now_iso() -> str:
    return dt.datetime.now().isoformat(timespec="seconds")


def highlight_words(text: str, lesson: Lesson) -> str:
    forms = sorted({v.form_in_story for v in lesson.new_vocabulary if v.form_in_story}, key=len, reverse=True)
    if not forms:
        return text
    pattern = r"(?<!\w)(" + "|".join(re.escape(f) for f in forms) + r")(?!\w)"
    return re.sub(pattern, r"**\1**", text, flags=re.IGNORECASE)


def after_attempt(day: int) -> None:
    """Re-check completion after any saved attempt."""
    if not repo.is_completed(day) and repo.update_completion(day):
        st.session_state["just_completed"] = day


def audio_block(day: int, kind: str, label: str, make_audio) -> None:
    path = repo.audio_path(day, kind)
    if path.exists():
        st.audio(path.read_bytes(), format="audio/mpeg")
    elif not tts_available():
        st.caption("🔇 Add ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID to secrets.toml to enable audio.")
    elif st.button(label, key=f"tts_{day}_{kind}"):
        with st.spinner("Recording…"):
            try:
                path.write_bytes(make_audio())
                st.rerun()
            except Exception as exc:
                st.error(str(exc))


def render_feedback(fb: ProductionFeedback, max_score: int = 20) -> None:
    st.metric("Score (estimate)", f"{fb.total}/{max_score}")
    st.progress(fb.total / max_score)
    st.table([{"Criterion": c.name, "Score": f"{c.score}/5", "Comment": c.comment} for c in fb.criteria])
    if fb.feedback:
        st.info(fb.feedback)
    if fb.mistakes:
        st.markdown("**Mistakes**")
        st.table([{"You wrote/said": m.original, "Correct": m.correction, "Why": m.explanation}
                  for m in fb.mistakes])
    if fb.corrected_text:
        with st.expander("Corrected version"):
            st.write(fb.corrected_text)


def correct_answer_text(item) -> str:
    if getattr(item, "type", "choice") == "choice" or not getattr(item, "accepted_answers", None):
        return item.options[item.correct_option]
    return " / ".join(item.accepted_answers)


# =========================================================================
# sections
# =========================================================================
def render_reading(lesson: Lesson) -> None:
    st.caption(f"Text type: **{lesson.text_type}**, as in TELC *Rozumienie tekstu pisanego*. "
               "Read it twice: first for the general idea, then for details.")
    if st.toggle("Show English translation", key=f"tr_{lesson.day}"):
        left, right = st.columns(2)
        left.markdown(highlight_words(lesson.reading_pl, lesson))
        right.markdown(lesson.reading_en)
    else:
        st.markdown(highlight_words(lesson.reading_pl, lesson))
    st.caption("**Bold** = key words. Ask the tutor about anything you don't understand →")
    with st.expander("🔊 Read-along audio"):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("🐢 Slow")
            audio_block(lesson.day, "reading_slow", "Create slow audio",
                        lambda: synthesize_speech(lesson.reading_pl, "slow"))
        with c2:
            st.markdown("▶️ Normal")
            audio_block(lesson.day, "reading_normal", "Create normal audio",
                        lambda: synthesize_speech(lesson.reading_pl, "normal"))


def render_listening(lesson: Lesson) -> None:
    lst = lesson.listening
    st.markdown(f"**{lst.type}**  \n{lst.situation_en}")
    if lst.instruction_pl:
        st.caption(lst.instruction_pl)
    st.caption("Exam tip: in TELC, some recordings are played only once. "
               "Try to answer after one listening.")
    audio_block(lesson.day, "listening", "🎧 Create the recording",
                lambda: synthesize_dialogue([(l.speaker, l.text) for l in lst.lines]))

    attempts = repo.attempts(lesson.day, "listening")
    retry_key = f"listen_retry_{lesson.day}"
    if attempts and not st.session_state.get(retry_key):
        last = attempts[-1]
        st.success(f"Result: **{last.score:.0%}**")
        for t in lst.tasks:
            ok = last.correct.get(str(t.id))
            mark = "✅" if ok else "❌"
            given = last.answers.get(str(t.id), "")
            given_txt = t.options[int(given)] if given.isdigit() and int(given) < len(t.options) else "-"
            st.markdown(f"{mark} **{t.question}**  \nYour answer: {given_txt}"
                        + ("" if ok else f"  \nCorrect: **{t.options[t.correct_option]}**"))
        with st.expander("📜 Transcript"):
            for l in lst.lines:
                st.markdown(f"**{l.speaker}:** {l.text}")
        if st.button("🔁 Try again", key=f"listen_again_{lesson.day}"):
            st.session_state[retry_key] = True
            st.rerun()
        return

    with st.form(f"listen_form_{lesson.day}_{len(attempts)}"):
        answers = {}
        for t in lst.tasks:
            choice = st.radio(t.question, list(range(len(t.options))), index=None,
                              format_func=lambda i, o=t.options: o[i], key=f"l_{lesson.day}_{len(attempts)}_{t.id}")
            answers[str(t.id)] = "" if choice is None else str(choice)
        if st.form_submit_button("Check answers", type="primary"):
            repo.add_attempt(lesson.day, "listening", grade_listening(lst.tasks, answers))
            st.session_state[retry_key] = False
            st.rerun()


def render_words(lesson: Lesson) -> None:
    plan = get_plan_day(lesson.day)
    title = (f"The {plan.target_words} most useful new words for today's {plan.level} lesson"
             if lesson.lesson_type == "lesson" else f"This week's {plan.target_words} key words (review)")
    st.write(f"**{title}**")
    for i, v in enumerate(lesson.new_vocabulary, start=1):
        with st.expander(f"{i}. **{v.polish}**: {v.english}"):
            st.markdown(f"*{v.part_of_speech}* · in the text: **{v.form_in_story}**")
            if v.why_important:
                st.markdown(f"💡 {v.why_important}")
            st.markdown(f"🇵🇱 {v.example_pl}  \n🇬🇧 {v.example_en}")


def render_grammar(lesson: Lesson) -> None:
    plan = get_plan_day(lesson.day)
    st.write(f"**Grammar at {plan.level}: {len(plan.new_grammar_ids)} new focus point(s), plus spaced review**")
    for i, g in enumerate(lesson.grammar_rules, start=1):
        marker = "🆕" if g.id in plan.new_grammar_ids else "🔁"
        with st.expander(f"{marker} {i}. {g.title}", expanded=(g.id in plan.new_grammar_ids)):
            st.write(g.explanation)
            if g.pattern:
                st.code(g.pattern, language=None)
            if g.examples:
                st.table([{"Polish": e.polish, "English": e.english} for e in g.examples])
            if g.story_examples:
                st.markdown("**In today's text**")
                for s in g.story_examples:
                    st.markdown(f"- {s}")


def render_exercises(lesson: Lesson) -> None:
    sections = {"vocabulary": "🔤 Vocabulary", "grammar": "📐 Grammar",
                "language_elements": "🧩 Language elements (TELC *Elementy języka*)"}
    attempts = repo.attempts(lesson.day, "exercises")
    retry_key = f"ex_retry_{lesson.day}"

    if attempts and not st.session_state.get(retry_key):
        last = attempts[-1]
        st.success(f"Result: **{last.score:.0%}** ({sum(last.correct.values())}/{len(lesson.exercises)})")
        for section, label in sections.items():
            st.subheader(label)
            for e in [x for x in lesson.exercises if x.section == section]:
                ok = last.correct.get(str(e.id))
                given = last.answers.get(str(e.id), "")
                if e.type == "choice" and given.isdigit() and int(given) < len(e.options):
                    given = e.options[int(given)]
                st.markdown(f"{'✅' if ok else '❌'} {e.prompt}  \nYour answer: *{given or '-'}*"
                            + ("" if ok else f"  \nCorrect: **{correct_answer_text(e)}**"))
                if e.explanation_en:
                    st.caption(e.explanation_en)
        if st.button("🔁 Do the exercises again", key=f"ex_again_{lesson.day}"):
            st.session_state[retry_key] = True
            st.rerun()
        return

    n = len(attempts)
    with st.form(f"ex_form_{lesson.day}_{n}"):
        answers = {}
        for section, label in sections.items():
            st.subheader(label)
            for e in [x for x in lesson.exercises if x.section == section]:
                if e.instruction_en:
                    st.caption(e.instruction_en)
                key = f"ex_{lesson.day}_{n}_{e.id}"
                if e.type == "choice":
                    c = st.radio(e.prompt, list(range(len(e.options))), index=None,
                                 format_func=lambda i, o=e.options: o[i], key=key)
                    answers[str(e.id)] = "" if c is None else str(c)
                else:
                    answers[str(e.id)] = st.text_input(e.prompt, key=key)
        if st.form_submit_button("Check answers", type="primary"):
            repo.add_attempt(lesson.day, "exercises", grade_exercises(lesson.exercises, answers))
            st.session_state[retry_key] = False
            after_attempt(lesson.day)
            st.rerun()


def render_writing(lesson: Lesson) -> None:
    plan = get_plan_day(lesson.day)
    lo, hi = plan.writing_length
    if lesson.level == "A0":
        st.caption(f"Guided beginner writing: choose 1 task and write {lo}-{hi} words using the prompts.")
    elif lesson.level in ("A1", "A2"):
        st.caption(f"Progressive writing practice: choose 1 task and cover all points. Target: {lo}-{hi} words.")
    else:
        st.caption(f"TELC *Pisanie*: choose 1 of 2 tasks and cover **all** points. Target: {lo}-{hi} words.")
    labels = [f"Task {i + 1}: {t.situation_en}" for i, t in enumerate(lesson.writing_tasks)]
    idx = st.radio("Choose a task", list(range(len(labels))), format_func=lambda i: labels[i],
                   key=f"w_task_{lesson.day}")
    task = lesson.writing_tasks[idx]
    st.markdown(f"**{task.situation_pl}**")
    st.markdown("\n".join(f"- {p}" for p in task.points_pl))

    with st.form(f"w_form_{lesson.day}"):
        text = st.text_area("Your text", height=220, key=f"w_text_{lesson.day}",
                            placeholder="Napisz tekst po polsku…")
        submitted = st.form_submit_button("Submit for feedback", type="primary")
    words = len(text.split())
    st.caption(f"Words: {words}")
    if submitted:
        minimum = max(5, lo // 2) if lesson.level == "A0" else max(10, lo // 2)
        if words < minimum:
            st.warning(f"Please write at least {minimum} words.")
        else:
            with st.spinner("Your examiner is reading…"):
                try:
                    fb = grade_writing(task, text, lesson.level, (lo, hi))
                except Exception as exc:
                    st.error(f"Grading failed: {exc}")
                    return
            repo.add_attempt(lesson.day, "writing", WritingAttempt(
                task_index=idx, text=text, word_count=words, result=fb, timestamp=now_iso()))
            after_attempt(lesson.day)
            st.rerun()

    attempts = repo.attempts(lesson.day, "writing")
    if attempts:
        last = attempts[-1]
        st.divider()
        st.subheader(f"Feedback · attempt {len(attempts)}")
        render_feedback(last.result)


def render_speaking(lesson: Lesson) -> None:
    s = lesson.speaking
    plan = get_plan_day(lesson.day)
    heading = (SPEAKING_PART_NAMES.get(s.part, f"Part {s.part}")
               if lesson.level == "B1" else plan.speaking_mode.title())
    st.markdown(f"**{heading}**")
    st.subheader(s.title)
    st.markdown(f"{s.instructions_pl}  \n*{s.instructions_en}*")
    st.markdown("\n".join(f"- {p}" for p in s.prompts))
    if s.opinions:
        st.markdown("**Opinions to react to:**")
        st.markdown("\n".join(f"> {o}" for o in s.opinions))
    with st.expander("💬 Useful phrases"):
        st.table([{"Polish": p.polish, "English": p.english} for p in s.useful_phrases])
    st.text_area("Preparation notes (keywords only; in TELC, reading a script lowers your score)",
                 key=f"notes_{lesson.day}", height=80)
    duration = "20-45 seconds" if lesson.level == "A0" else ("45-90 seconds" if lesson.level == "A1" else "1-3 minutes")
    st.caption(f"Aim for {duration}. Pronunciation is not assessed: feedback is based on a transcript.")

    n = len(repo.attempts(lesson.day, "speaking"))
    rec = st.audio_input("🎙️ Record your answer", key=f"rec_{lesson.day}_{n}")
    if rec is not None and st.button("Submit recording", type="primary", key=f"rec_send_{lesson.day}_{n}"):
        audio = rec.getvalue()
        with st.spinner("Transcribing and assessing…"):
            try:
                transcript = transcribe(audio, "answer.wav", context=f"{s.title}. {s.instructions_pl}")
                if not transcript:
                    st.warning("No speech detected. Please record again.")
                    return
                fb = grade_speaking(s, transcript, lesson.level)
            except Exception as exc:
                st.error(f"Processing failed: {exc}")
                return
        name = repo.save_recording(lesson.day, audio)
        repo.add_attempt(lesson.day, "speaking", SpeakingAttempt(
            transcript=transcript, audio_file=name, result=fb, timestamp=now_iso()))
        after_attempt(lesson.day)
        st.rerun()

    with st.expander("⌨️ No microphone? Type what you would say"):
        typed = st.text_area("Your answer", key=f"typed_{lesson.day}_{n}")
        if st.button("Submit typed answer", key=f"typed_send_{lesson.day}_{n}"):
            minimum = 5 if lesson.level == "A0" else 10
            if len(typed.split()) < minimum:
                st.warning(f"Please write at least {minimum} words.")
            else:
                with st.spinner("Assessing…"):
                    try:
                        fb = grade_speaking(s, typed, lesson.level)
                    except Exception as exc:
                        st.error(f"Grading failed: {exc}")
                        return
                repo.add_attempt(lesson.day, "speaking", SpeakingAttempt(
                    transcript=typed, typed=True, result=fb, timestamp=now_iso()))
                after_attempt(lesson.day)
                st.rerun()

    attempts = repo.attempts(lesson.day, "speaking")
    if attempts:
        last = attempts[-1]
        st.divider()
        st.subheader(f"Feedback · attempt {len(attempts)}")
        if last.audio_file and repo.recording_path(last.audio_file).exists():
            st.audio(repo.recording_path(last.audio_file).read_bytes())
        st.markdown("**Transcript:** " + last.transcript)
        render_feedback(last.result)


def render_quiz(lesson: Lesson) -> None:
    attempts = repo.attempts(lesson.day, "quiz")
    passed = next((a for a in attempts if a.passed), None)
    pass_pct = int(QUIZ_PASS_SCORE * 100)
    if passed:
        st.success(f"🎉 Quiz passed with **{passed.score:.0%}** on attempt {passed.attempt}.")
        res = {r.id: r for r in passed.results}
        for i, q in enumerate(lesson.quiz, start=1):
            r = res.get(q.id)
            icon = "✅" if r and r.score == 1 else ("🟡" if r and r.score > 0 else "❌")
            st.markdown(f"{icon} **{i}.** {q.question}")
        return

    last = attempts[-1] if attempts else None
    st.write(f"**{len(lesson.quiz)} questions · pass mark {pass_pct}%.** Answers are never shown; "
             "retry until you pass.")
    if last:
        st.error(f"Attempt {last.attempt}: **{last.score:.0%}**; you need {pass_pct}%. "
                 "Fix the questions marked ❌/🟡 and submit again.")
    prev_answers = last.answers if last else {}
    prev_results = {r.id: r for r in last.results} if last else {}
    attempt_no = len(attempts) + 1

    with st.form(f"quiz_{lesson.day}_{attempt_no}"):
        answers: dict[str, str] = {}
        for i, q in enumerate(lesson.quiz, start=1):
            qid = str(q.id)
            st.markdown(f"**{i}. {q.question}**")
            st.caption(QUIZ_TYPE_LABELS[q.type] + (f" · hint: {q.hint_en}" if q.hint_en else ""))
            key = f"q_{lesson.day}_{attempt_no}_{qid}"
            prev = prev_answers.get(qid, "")
            if q.type == "multiple_choice":
                c = st.radio("Answer", list(range(len(q.options))), format_func=lambda j, o=q.options: o[j],
                             index=int(prev) if prev.isdigit() and int(prev) < len(q.options) else None,
                             key=key, label_visibility="collapsed")
                answers[qid] = "" if c is None else str(c)
            elif q.type == "fill_blank":
                answers[qid] = st.text_input("Answer", value=prev, key=key, label_visibility="collapsed",
                                             placeholder="Wpisz brakujące słowo…")
            else:
                answers[qid] = st.text_area("Answer", value=prev, key=key, height=80,
                                            label_visibility="collapsed",
                                            placeholder="Odpowiedz pełnym zdaniem po polsku…")
            r = prev_results.get(q.id)
            if r is not None:
                if r.score == 1:
                    st.markdown("✅ Correct last time")
                else:
                    icon = "🟡 Partly correct" if r.score > 0 else "❌ Incorrect"
                    st.markdown(f"{icon} last time" + (f": {r.feedback}" if r.feedback else ""))
        submitted = st.form_submit_button("Submit answers", type="primary")

    if submitted:
        missing = [i for i, q in enumerate(lesson.quiz, start=1) if not answers[str(q.id)].strip()]
        if missing:
            st.warning(f"Please answer all questions first (missing: {', '.join(map(str, missing))}).")
            return
        with st.spinner("Checking your answers…"):
            try:
                result = grade_quiz(lesson, answers, attempt=attempt_no)
            except Exception as exc:
                st.error(f"Grading failed, please submit again: {exc}")
                return
        repo.add_attempt(lesson.day, "quiz", result)
        after_attempt(lesson.day)
        st.rerun()


def render_chat(lesson: Lesson) -> None:
    st.subheader("💬 Ask your tutor")
    key = f"chat_{lesson.day}"
    history: list[dict] = st.session_state.setdefault(key, [])
    box = st.container(height=560)
    with box:
        if not history:
            st.caption("Examples: *What does „zamówić” mean?* · *Why „kawę” and not „kawa”?* · "
                       "*Is my sentence correct: …?*")
        for msg in history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
    question = st.chat_input("Ask about a word, phrase or grammar…")
    if question:
        history.append({"role": "user", "content": question})
        with box:
            with st.chat_message("user"):
                st.markdown(question)
            with st.chat_message("assistant"):
                try:
                    answer = st.write_stream(stream_tutor_reply(lesson, history))
                except Exception as exc:
                    answer = f"⚠️ Sorry, something went wrong: {exc}"
                    st.error(answer)
        history.append({"role": "assistant", "content": answer})


def render_plan_page() -> None:
    current = get_plan_day(repo.current_day)
    st.header("📅 9-month TELC Polski B1 plan")
    st.write("1 hour a day · 39 weeks · 273 lessons. Days 1-6 of each week are new lessons; "
             "day 7 is a weekly review. Every lesson covers all four TELC skills.")
    st.markdown(
        "| TELC module | In every lesson |\n|---|---|\n"
        "| Listening (25 min, 4 parts) | 🎧 voice messages, dialogues, interviews, opinions, rotating daily |\n"
        "| Reading (40 min, 4 parts) | 📖 e-mails, forum posts, notices, official texts, articles |\n"
        "| Language elements (20 min) | 🧩 gap tasks in conversations and semi-formal e-mails |\n"
        "| Writing (30 min, semi-formal e-mail) | 📝 1 of 2 tasks with guiding points + examiner feedback |\n"
        "| Speaking (~16 min, 3 parts) | 🗣️ experiences / presentation / discussion, rotating daily |"
    )
    st.info(f"You are on **day {current.day}/{TOTAL_DAYS}**: week {current.week}, month {current.month} "
            f"({current.phase}).")
    for month in range(1, 10):
        weeks = [w for w in WEEKS if w.month == month]
        with st.expander(f"Month {month}: {get_plan_day((weeks[0].number-1)*7+1).phase}", expanded=(month == current.month)):
            for w in weeks:
                marker = "👉 " if w.number == current.week else ""
                week_plan = get_plan_day((w.number - 1) * 7 + 1)
                st.markdown(f"{marker}**Week {w.number}: {w.theme_en}** *({w.theme_pl})* · {week_plan.level}")
                st.caption("Grammar: " + "; ".join(GRAMMAR[g][0] for g in w.grammar))
                st.caption("Situations: " + "; ".join(w.situations))
                st.caption("Writing: " + w.writing_focus)
    st.download_button("⬇️ Download plan (Markdown)", plan_markdown(), file_name="PLAN.md")


# =========================================================================
# sidebar
# =========================================================================
with st.sidebar:
    st.title("🇵🇱 Polish Tutor")
    st.caption("TELC Polski B1 · 9-month plan")
    if not OPENAI_API_KEY:
        st.error("OPENAI_API_KEY is missing in `.streamlit/secrets.toml`.")
        st.stop()

    page = st.radio("Page", ["📘 Lesson", "📅 Plan"], horizontal=True, label_visibility="collapsed")

    current_day = repo.current_day
    plan_today = get_plan_day(current_day)
    st.markdown(f"**Day {current_day}/{TOTAL_DAYS}** · Week {plan_today.week} · Month {plan_today.month}  \n"
                f"{plan_today.level} · {plan_today.theme_en} · {plan_today.target_words} words")
    st.progress(min(current_day, TOTAL_DAYS) / TOTAL_DAYS)

    days = sorted(set(repo.lesson_days()) | {current_day}, reverse=True)
    selected_day = st.selectbox(
        "Lesson", days, index=days.index(current_day),
        format_func=lambda d: f"Day {d} · week {get_plan_day(d).week}"
                              + (" ✅" if repo.is_completed(d) else "") + (" (current)" if d == current_day else ""),
    )
    lesson = repo.load_lesson(selected_day)

    if selected_day == current_day:
        if lesson is None:
            generate = st.button("✨ Generate today's lesson", type="primary", width="stretch")
        else:
            if repo.is_completed(current_day):
                if st.button("➡️ Next lesson", type="primary", width="stretch"):
                    repo.current_day = current_day + 1
                    st.rerun()
            with st.popover("🔄 Regenerate", width="stretch"):
                st.caption("Replaces this lesson and deletes its attempts.")
                generate = st.button("Yes, regenerate", key="regen_confirm")
        if lesson is None or generate:
            if generate:
                plan = get_plan_day(current_day)
                with st.status("Your tutor is preparing the lesson… (≈1-2 min)", expanded=True) as status:
                    try:
                        new_lesson = generate_lesson(
                            plan,
                            known_words=repo.taught_words(exclude_day=current_day),
                            week_words=repo.week_words(plan.week, exclude_day=current_day),
                            progress=status.write,
                        )
                    except LessonGenerationError as exc:
                        status.update(label="Generation failed", state="error")
                        st.error(str(exc))
                        st.stop()
                    except Exception as exc:
                        status.update(label="OpenAI request failed", state="error")
                        st.error(str(exc))
                        st.stop()
                repo.save_lesson(new_lesson)
                repo.delete_audio(current_day)
                repo.reset_day(current_day)
                st.session_state.pop(f"chat_{current_day}", None)
                st.rerun()

    with st.expander("⚙️ Jump to another day"):
        st.caption("Use this to skip ahead if lessons are too easy, or to go back.")
        target = st.number_input("Plan day", 1, TOTAL_DAYS, value=min(current_day, TOTAL_DAYS))
        if st.button("Go"):
            repo.current_day = int(target)
            st.rerun()

    st.divider()
    stats = repo.stats(today)
    c1, c2 = st.columns(2)
    c1.metric("🔥 Streak", f"{stats['streak']} d")
    c2.metric("📚 Completed", stats["lessons"])
    c1.metric("🔤 Words", stats["words"])
    c2.metric("📐 Grammar", stats["grammar"])


# =========================================================================
# main
# =========================================================================
if page == "📅 Plan":
    render_plan_page()
    st.stop()

if lesson is None:
    p = get_plan_day(selected_day)
    st.header(f"Day {p.day}: {p.situation}")
    st.caption(f"Week {p.week}: {p.theme_en} · {p.level} · Grammar: {'; '.join(p.grammar_titles)}")
    st.info("Click **Generate today's lesson** in the sidebar.")
    st.stop()

if st.session_state.pop("just_completed", None) == lesson.day:
    st.balloons()

plan = get_plan_day(lesson.day)
kind = "📝 Weekly review" if lesson.lesson_type == "review" else "📘 Lesson"
st.header(lesson.title_pl)
st.caption(f"{lesson.title_en} · {kind} · Day {lesson.day}/{TOTAL_DAYS} · Week {lesson.week}: "
           f"{lesson.theme_en} · {lesson.level}")

check = repo.checklist(lesson.day)
labels = {"exercises": "Exercises", "writing": "Writing", "speaking": "Speaking", "quiz": "Quiz passed"}
status_line = " · ".join(f"{'✅' if check[k] else '⬜'} {v}" for k, v in labels.items())
if repo.is_completed(lesson.day):
    st.success(f"Lesson completed! {status_line}")
else:
    st.caption(f"To complete the lesson: {status_line}")

lesson_col, chat_col = st.columns([3, 2], gap="large")
with lesson_col:
    tabs = st.tabs([
        f"📖 Reading · {TIME_PLAN['Reading']}′", f"🎧 Listening · {TIME_PLAN['Listening']}′",
        f"🔤 Words · {TIME_PLAN['Words']}′", f"📐 Grammar · {TIME_PLAN['Grammar']}′",
        f"✏️ Exercises · {TIME_PLAN['Exercises']}′", f"📝 Writing · {TIME_PLAN['Writing']}′",
        f"🗣️ Speaking · {TIME_PLAN['Speaking']}′", f"✅ Quiz · {TIME_PLAN['Quiz']}′",
    ])
    renderers = [render_reading, render_listening, render_words, render_grammar,
                 render_exercises, render_writing, render_speaking, render_quiz]
    for tab, render in zip(tabs, renderers):
        with tab:
            render(lesson)
with chat_col:
    render_chat(lesson)
