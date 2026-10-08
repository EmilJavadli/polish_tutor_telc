"""Generates a lesson in two validated LLM calls: core content, then practice material."""
import datetime as dt
import json
import re
from collections.abc import Callable
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from agent.llm import chat_json
from agent.prompts import (
    CORE_SYSTEM, CORE_USER, PRACTICE_SYSTEM, PRACTICE_USER, VOCAB_NEW, VOCAB_REVIEW, fill,
)
from agent.schemas import CoreLesson, Lesson, Practice
from config import (
    EXERCISE_COMPOSITION, GRAMMAR_EXERCISES_PER_RULE, LISTENING_TASKS, MAX_GENERATION_ATTEMPTS,
    MAX_KNOWN_WORDS_IN_PROMPT, NEW_WORDS_PER_LESSON, QUIZ_COMPOSITION,
)
from curriculum import GRAMMAR, SPEAKING_PART_NAMES, PlanDay


T = TypeVar("T", bound=BaseModel)


class LessonGenerationError(Exception):
    """Raised when no valid lesson could be produced."""


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip().lower()


def contains_phrase(text: str, phrase: str) -> bool:
    """True if `phrase` occurs in `text` as whole word(s), case-insensitive."""
    pattern = rf"(?<!\w){re.escape(normalize(phrase))}(?!\w)"
    return re.search(pattern, normalize(text)) is not None


def _check_choice(prefix: str, options: list[str], correct: int | None, n_options: tuple[int, ...]) -> list[str]:
    problems = []
    if len(options) not in n_options:
        problems.append(f"{prefix} must have {' or '.join(map(str, n_options))} options.")
    if correct is None or not 0 <= correct < len(options):
        problems.append(f"{prefix} has an invalid correct_option.")
    return problems


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------
def validate_core(core: CoreLesson, plan: PlanDay, known_words: list[str], week_words: list[str]) -> list[str]:
    p: list[str] = []

    # Vocabulary
    if len(core.new_vocabulary) != NEW_WORDS_PER_LESSON:
        p.append(f"new_vocabulary has {len(core.new_vocabulary)} items; exactly {NEW_WORDS_PER_LESSON} required.")
    known = {normalize(w) for w in known_words}
    week = {normalize(w) for w in week_words}
    seen: set[str] = set()
    for v in core.new_vocabulary:
        key = normalize(v.polish)
        if key in seen:
            p.append(f"'{v.polish}' is listed twice.")
        seen.add(key)
        if plan.lesson_type == "lesson" and key in known:
            p.append(f"'{v.polish}' is already known; choose another word.")
        if plan.lesson_type == "review" and week and key not in week:
            p.append(f"'{v.polish}' is not in this week's word list (review lesson).")
        if not contains_phrase(core.reading_pl, v.form_in_story):
            p.append(f"form_in_story '{v.form_in_story}' does not appear exactly in reading_pl.")

    # Grammar: exactly the assigned syllabus points
    ids = [g.id for g in core.grammar_rules]
    if ids != list(plan.grammar_ids):
        p.append(f"grammar_rules ids must be exactly {list(plan.grammar_ids)} in this order (got {ids}).")
    for g in core.grammar_rules:
        if len(g.examples) < 3:
            p.append(f"Grammar '{g.id}' needs at least 3 examples.")
        if not g.story_examples:
            p.append(f"Grammar '{g.id}' needs story_examples.")

    # Reading length (25% tolerance)
    lo, hi = plan.reading_length
    n = len(core.reading_pl.split())
    if n < lo * 0.75 or n > hi * 1.25:
        p.append(f"reading_pl has {n} words; it should have {lo}-{hi}.")

    # Listening
    lst = core.listening
    if len(lst.lines) < 2 and "message" not in lst.type:
        p.append("listening needs at least 2 lines.")
    lo, hi = plan.listening_length
    n = sum(len(line.text.split()) for line in lst.lines)
    if n < lo * 0.7 or n > hi * 1.3:
        p.append(f"listening has {n} words; it should have {lo}-{hi}.")
    if len(lst.tasks) != LISTENING_TASKS:
        p.append(f"listening needs exactly {LISTENING_TASKS} tasks.")
    for t in lst.tasks:
        p += _check_choice(f"Listening task {t.id}", t.options, t.correct_option, (2, 3))
    return p



def _choice_consistency_problems(pr: Practice) -> list[str]:
    """Catch internally inconsistent generated choice exercises without an extra API call.

    This cannot prove Polish semantics in general, but it catches the high-value failure mode
    where the model's explanation itself names/supports a different option than correct_option.
    """
    problems: list[str] = []
    for e in pr.exercises:
        if e.type != "choice" or e.correct_option is None or not e.explanation_en.strip():
            continue
        chosen = normalize(e.options[e.correct_option]) if e.correct_option < len(e.options) else ""
        explanation = normalize(e.explanation_en)
        mentioned = [opt for opt in e.options if normalize(opt) and contains_phrase(explanation, opt)]
        # If the explanation explicitly mentions one option, that option must be the declared answer.
        if len(mentioned) == 1 and normalize(mentioned[0]) != chosen:
            problems.append(
                f"Exercise {e.id} is internally inconsistent: correct_option points to "
                f"'{e.options[e.correct_option]}' but explanation_en supports '{mentioned[0]}'. "
                "Solve the exercise again and fix correct_option/options/explanation_en."
            )
    return problems

def validate_practice(pr: Practice, plan: PlanDay) -> list[str]:
    p: list[str] = []

    # Exercises
    total = sum(EXERCISE_COMPOSITION.values())
    if len(pr.exercises) != total:
        p.append(f"exercises has {len(pr.exercises)} items; exactly {total} required.")
    for section, expected in EXERCISE_COMPOSITION.items():
        actual = sum(1 for e in pr.exercises if e.section == section)
        if actual != expected:
            p.append(f"exercises: {actual} '{section}' items; {expected} required.")
    for gid in plan.grammar_ids:
        n = sum(1 for e in pr.exercises if e.section == "grammar" and e.grammar_id == gid)
        if n < GRAMMAR_EXERCISES_PER_RULE:
            p.append(f"Grammar point {gid} needs {GRAMMAR_EXERCISES_PER_RULE} exercises (has {n}).")
    for e in pr.exercises:
        if e.type == "choice":
            p += _check_choice(f"Exercise {e.id}", e.options, e.correct_option, (2, 3, 4))
        else:
            if e.prompt.count("___") != 1:
                p.append(f"Exercise {e.id} must contain exactly one '___'.")
            if not e.accepted_answers:
                p.append(f"Exercise {e.id} needs accepted_answers.")
    if len({e.id for e in pr.exercises}) != len(pr.exercises):
        p.append("exercise ids must be unique.")

    # Writing
    if len(pr.writing_tasks) != 2:
        p.append("writing_tasks must contain exactly 2 alternative tasks.")
    for i, w in enumerate(pr.writing_tasks, start=1):
        if not 3 <= len(w.points_pl) <= 4:
            p.append(f"Writing task {i} needs 3-4 points_pl.")

    # Speaking
    s = pr.speaking
    if s.part != plan.speaking_part:
        p.append(f"speaking.part must be {plan.speaking_part}.")
    if len(s.prompts) < 3:
        p.append("speaking.prompts needs at least 3 items.")
    if s.part == 3 and len(s.opinions) < 3:
        p.append("speaking part 3 needs at least 3 opinions.")
    if len(s.useful_phrases) < 5:
        p.append("speaking.useful_phrases needs at least 5 phrases.")

    # Quiz
    expected_total = sum(QUIZ_COMPOSITION.values())
    if len(pr.quiz) != expected_total:
        p.append(f"quiz has {len(pr.quiz)} questions; exactly {expected_total} required.")
    for qtype, expected in QUIZ_COMPOSITION.items():
        actual = sum(1 for q in pr.quiz if q.type == qtype)
        if actual != expected:
            p.append(f"quiz has {actual} '{qtype}' questions; {expected} required.")
    if len({q.id for q in pr.quiz}) != len(pr.quiz):
        p.append("quiz ids must be unique.")
    for q in pr.quiz:
        if q.type == "multiple_choice":
            p += _check_choice(f"Quiz question {q.id}", q.options, q.correct_option, (4,))
        elif q.type == "fill_blank":
            if q.question.count("___") != 1:
                p.append(f"Quiz question {q.id} must contain exactly one '___'.")
            if not q.accepted_answers:
                p.append(f"Quiz question {q.id} needs accepted_answers.")
        elif not q.reference_answer.strip():
            p.append(f"Quiz question {q.id} needs a reference_answer.")
    p += _choice_consistency_problems(pr)
    return p


# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------
def _generate(messages: list[dict], model: type[T],
              validate: Callable[[T], list[str]], label: str) -> T:
    """Call the model, validate, and feed problems back until valid."""
    problems: list[str] = []
    for _ in range(MAX_GENERATION_ATTEMPTS):
        raw_text = ""
        try:
            raw = chat_json(messages)
            raw_text = json.dumps(raw, ensure_ascii=False)
            obj = model.model_validate(raw)
            problems = validate(obj)
        except json.JSONDecodeError as exc:
            problems = [f"The response was not valid JSON: {exc}"]
        except ValidationError as exc:
            problems = [f"The JSON does not match the required structure: {exc}"]
        if not problems:
            return obj
        if raw_text:
            messages.append({"role": "assistant", "content": raw_text})
        messages.append({"role": "user", "content":
                         "Fix these problems and return the full corrected JSON:\n- " + "\n- ".join(problems)})
    raise LessonGenerationError(f"Could not generate valid {label}. Last problems:\n- " + "\n- ".join(problems))


def build_core_messages(plan: PlanDay, known_words: list[str], week_words: list[str]) -> list[dict]:
    grammar_list = "\n".join(f'    {gid}: "{GRAMMAR[gid][0]}" (e.g. {GRAMMAR[gid][1]})' for gid in plan.grammar_ids)
    vocab_rule = (fill(VOCAB_REVIEW, n=NEW_WORDS_PER_LESSON, week_words=", ".join(week_words))
                  if plan.lesson_type == "review" else fill(VOCAB_NEW, n=NEW_WORDS_PER_LESSON))
    system = fill(
        CORE_SYSTEM, text_type=plan.text_type, reading_min=plan.reading_length[0],
        reading_max=plan.reading_length[1], level=plan.level, n_words=NEW_WORDS_PER_LESSON,
        vocab_rule=vocab_rule, grammar_list=grammar_list, listening_min=plan.listening_length[0],
        listening_max=plan.listening_length[1], listening_type=plan.listening_type,
        n_listening=LISTENING_TASKS,
    )
    user = fill(
        CORE_USER, day=plan.day, week=plan.week, phase=plan.phase, level=plan.level,
        theme=plan.theme_en, situation=plan.situation, lesson_type=plan.lesson_type,
        known_words=", ".join(known_words[-MAX_KNOWN_WORDS_IN_PROMPT:]) or "(none yet)",
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def build_practice_messages(plan: PlanDay, core: CoreLesson) -> list[dict]:
    system = fill(
        PRACTICE_SYSTEM, speaking_part=plan.speaking_part,
        n_ex_total=sum(EXERCISE_COMPOSITION.values()), n_ex_vocab=EXERCISE_COMPOSITION["vocabulary"],
        n_ex_grammar=EXERCISE_COMPOSITION["grammar"], per_rule=GRAMMAR_EXERCISES_PER_RULE,
        n_ex_le=EXERCISE_COMPOSITION["language_elements"], writing_focus=plan.writing_focus,
        level=plan.level, writing_min=plan.writing_length[0], writing_max=plan.writing_length[1],
        speaking_part_name=SPEAKING_PART_NAMES[plan.speaking_part],
        n_quiz=sum(QUIZ_COMPOSITION.values()), n_mc=QUIZ_COMPOSITION["multiple_choice"],
        n_fill=QUIZ_COMPOSITION["fill_blank"], n_open=QUIZ_COMPOSITION["open"],
    )
    user = fill(
        PRACTICE_USER, level=plan.level, theme=plan.theme_en, situation=plan.situation,
        reading=core.reading_pl, words=", ".join(v.polish for v in core.new_vocabulary),
        grammar="\n".join(f"{g.id}: {g.title}" for g in core.grammar_rules),
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def generate_lesson(plan: PlanDay, known_words: list[str], week_words: list[str],
                    progress: Callable[[str], None] | None = None) -> Lesson:
    """Generate and validate a full lesson for one plan day."""
    say = progress or (lambda _msg: None)

    say("Writing the reading text, words, grammar and listening…")
    core = _generate(build_core_messages(plan, known_words, week_words), CoreLesson,
                     lambda c: validate_core(c, plan, known_words, week_words), "lesson content")

    say("Creating exercises, writing and speaking tasks and the quiz…")
    practice = _generate(build_practice_messages(plan, core), Practice,
                         lambda pr: validate_practice(pr, plan), "practice material")

    return Lesson(
        **core.model_dump(), **practice.model_dump(),
        day=plan.day, week=plan.week, level=plan.level, lesson_type=plan.lesson_type,
        theme_en=plan.theme_en, situation=plan.situation, text_type=plan.text_type,
        created=dt.date.today().isoformat(),
    )
