"""Chat tutor grounded in the current lesson."""
from collections.abc import Iterator

from agent.llm import chat_stream
from agent.prompts import TUTOR_SYSTEM, fill
from agent.schemas import Lesson

MAX_HISTORY_MESSAGES = 20


def build_tutor_system_prompt(lesson: Lesson) -> str:
    return fill(
        TUTOR_SYSTEM, day=lesson.day, level=lesson.level, theme=lesson.theme_en,
        reading=lesson.reading_pl, translation=lesson.reading_en,
        vocabulary="\n".join(f"- {v.polish} ({v.form_in_story}) = {v.english}" for v in lesson.new_vocabulary),
        grammar="\n".join(f"- {g.title}: {g.explanation}" for g in lesson.grammar_rules),
        listening="\n".join(f"{line.speaker}: {line.text}" for line in lesson.listening.lines),
    )


def stream_tutor_reply(lesson: Lesson, history: list[dict]) -> Iterator[str]:
    messages = [{"role": "system", "content": build_tutor_system_prompt(lesson)}]
    messages += history[-MAX_HISTORY_MESSAGES:]
    yield from chat_stream(messages)
