"""Grading: exercises, listening, quiz (code + LLM), writing and speaking (LLM)."""
import re
import unicodedata

from agent.llm import chat_json
from agent.prompts import (
    PRODUCTION_CRITERIA, PRODUCTION_GRADER_SYSTEM, QUIZ_GRADER_SYSTEM, SPEAKING_EXTRA, fill,
)
from agent.schemas import (
    ChoiceTask, Criterion, Exercise, ExerciseAttempt, Lesson, ListeningAttempt,
    ProductionFeedback, QuestionResult, QuizAttempt, QuizQuestion, SpeakingTask, WritingTask,
)
from config import QUIZ_PASS_SCORE


def normalize_answer(text: str) -> str:
    """Lower-case, NFC, strip punctuation/extra spaces. Diacritics are kept (they matter)."""
    text = unicodedata.normalize("NFC", text or "").lower()
    text = re.sub(r"[^\w\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def is_correct_gap(answer: str, accepted: list[str]) -> bool:
    return normalize_answer(answer) in {normalize_answer(a) for a in accepted}


def is_correct_choice(answer: str, correct: int | None) -> bool:
    return answer.isdigit() and correct is not None and int(answer) == correct


# ---------------- exercises & listening (practice: answers shown afterwards) ----------------
def grade_exercises(exercises: list[Exercise], answers: dict[str, str]) -> ExerciseAttempt:
    correct: dict[str, bool] = {}
    for e in exercises:
        a = answers.get(str(e.id), "")
        correct[str(e.id)] = (is_correct_choice(a, e.correct_option) if e.type == "choice"
                              else is_correct_gap(a, e.accepted_answers))
    score = sum(correct.values()) / len(exercises) if exercises else 0.0
    return ExerciseAttempt(score=round(score, 4), answers=answers, correct=correct)


def grade_listening(tasks: list[ChoiceTask], answers: dict[str, str]) -> ListeningAttempt:
    correct = {str(t.id): is_correct_choice(answers.get(str(t.id), ""), t.correct_option) for t in tasks}
    score = sum(correct.values()) / len(tasks) if tasks else 0.0
    return ListeningAttempt(score=round(score, 4), answers=answers, correct=correct)


# ---------------- quiz (no answers revealed) ----------------
def _grade_open(lesson: Lesson, questions: list[QuizQuestion], answers: dict[str, str]) -> list[QuestionResult]:
    results, to_grade = [], []
    for q in questions:
        a = answers.get(str(q.id), "").strip()
        if not a:
            results.append(QuestionResult(id=q.id, score=0.0, feedback="No answer given."))
        else:
            to_grade.append({"id": q.id, "question": q.question,
                             "reference": q.reference_answer, "answer": a})
    if not to_grade:
        return results
    body = [f"TEXT:\n{lesson.reading_pl}\n", "ANSWERS TO GRADE:"]
    for it in to_grade:
        body.append(f"\nid: {it['id']}\nquestion: {it['question']}\n"
                    f"reference answer (secret): {it['reference']}\nlearner answer: {it['answer']}")
    raw = chat_json([{"role": "system", "content": QUIZ_GRADER_SYSTEM},
                     {"role": "user", "content": "\n".join(body)}])
    graded = {}
    for r in raw.get("results", []):
        try:
            graded[int(r["id"])] = r
        except (KeyError, TypeError, ValueError):
            continue
    for it in to_grade:
        r = graded.get(it["id"], {})
        try:
            s = float(r.get("score", 0))
        except (TypeError, ValueError):
            s = 0.0
        s = min((0.0, 0.5, 1.0), key=lambda allowed: abs(allowed - s))
        results.append(QuestionResult(id=it["id"], score=s, feedback=str(r.get("feedback", ""))))
    return results


def grade_quiz(lesson: Lesson, answers: dict[str, str], attempt: int) -> QuizAttempt:
    results: list[QuestionResult] = []
    open_qs: list[QuizQuestion] = []
    for q in lesson.quiz:
        a = answers.get(str(q.id), "")
        if q.type == "multiple_choice":
            ok = is_correct_choice(a, q.correct_option)
            results.append(QuestionResult(id=q.id, score=float(ok), feedback="" if ok else
                                          "Read the text again carefully: the answer depends on a detail."))
        elif q.type == "fill_blank":
            ok = is_correct_gap(a, q.accepted_answers)
            results.append(QuestionResult(id=q.id, score=float(ok), feedback="" if ok else
                                          "Check the case/ending and the Polish letters (ą, ę, ł…)."))
        else:
            open_qs.append(q)
    results += _grade_open(lesson, open_qs, answers)
    order = {q.id: i for i, q in enumerate(lesson.quiz)}
    results.sort(key=lambda r: order.get(r.id, 0))
    score = sum(r.score for r in results) / len(lesson.quiz) if lesson.quiz else 0.0
    return QuizAttempt(attempt=attempt, score=round(score, 4), passed=score >= QUIZ_PASS_SCORE,
                       answers=answers, results=results)


# ---------------- writing & speaking ----------------
def _parse_feedback(raw: dict, criteria_names: list[str]) -> ProductionFeedback:
    """Parse grader JSON robustly: missing criteria get 0, scores are clamped to 0-5."""
    by_name = {}
    for c in raw.get("criteria", []) or []:
        if isinstance(c, dict) and c.get("name"):
            by_name[normalize_answer(str(c["name"]))] = c
    criteria = []
    for i, name in enumerate(criteria_names):
        c = by_name.get(normalize_answer(name))
        if c is None and i < len(raw.get("criteria", []) or []):
            c = raw["criteria"][i] if isinstance(raw["criteria"][i], dict) else {}
        c = c or {}
        try:
            score = int(round(float(c.get("score", 0))))
        except (TypeError, ValueError):
            score = 0
        criteria.append(Criterion(name=name, score=max(0, min(5, score)), comment=str(c.get("comment", ""))))
    mistakes = [m for m in raw.get("mistakes", []) or [] if isinstance(m, dict)
                and m.get("original") is not None and m.get("correction") is not None]
    return ProductionFeedback(
        criteria=criteria,
        corrected_text=str(raw.get("corrected_text", "")),
        mistakes=[{"original": str(m["original"]), "correction": str(m["correction"]),
                   "explanation": str(m.get("explanation", ""))} for m in mistakes],
        feedback=str(raw.get("feedback", "")),
    )


def _grade_production(kind: str, level: str, task_text: str, answer: str, extra: str = "") -> ProductionFeedback:
    names = PRODUCTION_CRITERIA[kind]
    system = fill(PRODUCTION_GRADER_SYSTEM, kind=kind, level=level,
                  criteria="\n".join(f"- {n}" for n in names), extra=extra)
    user = f"TASK:\n{task_text}\n\nLEARNER'S {kind.upper()}:\n{answer}"
    raw = chat_json([{"role": "system", "content": system}, {"role": "user", "content": user}])
    return _parse_feedback(raw, names)


def grade_writing(task: WritingTask, text: str, level: str, length: tuple[int, int]) -> ProductionFeedback:
    task_text = (f"{task.situation_pl}\n({task.situation_en})\nCover these points:\n"
                 + "\n".join(f"- {p}" for p in task.points_pl)
                 + f"\nTarget length: {length[0]}-{length[1]} words.")
    return _grade_production("writing", level, task_text, text)


def grade_speaking(task: SpeakingTask, transcript: str, level: str) -> ProductionFeedback:
    task_text = (f"{task.title}\n{task.instructions_pl}\n({task.instructions_en})\n"
                 + "\n".join(f"- {p}" for p in task.prompts)
                 + ("\nOpinions given:\n" + "\n".join(f"- {o}" for o in task.opinions) if task.opinions else ""))
    return _grade_production("speaking", level, task_text, transcript, SPEAKING_EXTRA)
