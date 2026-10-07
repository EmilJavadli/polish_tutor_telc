"""Pydantic models for lessons and attempts."""
from typing import Literal

from pydantic import BaseModel, Field


# ---------------- lesson content (LLM call 1: core) ----------------
class VocabItem(BaseModel):
    polish: str
    form_in_story: str
    english: str
    part_of_speech: str = ""
    why_important: str = ""
    example_pl: str
    example_en: str


class Example(BaseModel):
    polish: str
    english: str


class GrammarRule(BaseModel):
    id: str
    title: str
    explanation: str
    pattern: str = ""
    examples: list[Example] = Field(default_factory=list)
    story_examples: list[str] = Field(default_factory=list)


class DialogueLine(BaseModel):
    speaker: str
    text: str


class ChoiceTask(BaseModel):
    id: int
    question: str
    options: list[str]
    correct_option: int


class Listening(BaseModel):
    type: str
    situation_en: str
    instruction_pl: str = ""
    lines: list[DialogueLine]
    tasks: list[ChoiceTask]


class CoreLesson(BaseModel):
    title_pl: str
    title_en: str
    reading_pl: str
    reading_en: str
    new_vocabulary: list[VocabItem]
    grammar_rules: list[GrammarRule]
    listening: Listening


# ---------------- practice (LLM call 2) ----------------
class Exercise(BaseModel):
    id: int
    section: Literal["vocabulary", "grammar", "language_elements"]
    type: Literal["choice", "gap_fill"]
    grammar_id: str = ""
    instruction_en: str = ""
    prompt: str
    options: list[str] = Field(default_factory=list)
    correct_option: int | None = None
    accepted_answers: list[str] = Field(default_factory=list)
    explanation_en: str = ""


class WritingTask(BaseModel):
    situation_pl: str
    situation_en: str
    points_pl: list[str]


class SpeakingTask(BaseModel):
    part: int
    title: str
    instructions_pl: str
    instructions_en: str
    prompts: list[str]
    useful_phrases: list[Example] = Field(default_factory=list)
    opinions: list[str] = Field(default_factory=list)


class QuizQuestion(BaseModel):
    id: int
    type: Literal["multiple_choice", "fill_blank", "open"]
    question: str
    hint_en: str = ""
    options: list[str] = Field(default_factory=list)
    correct_option: int | None = None
    accepted_answers: list[str] = Field(default_factory=list)
    reference_answer: str = ""


class Practice(BaseModel):
    exercises: list[Exercise]
    writing_tasks: list[WritingTask]
    speaking: SpeakingTask
    quiz: list[QuizQuestion]


# ---------------- full lesson ----------------
class Lesson(CoreLesson, Practice):
    day: int = 0
    week: int = 0
    level: str = ""
    lesson_type: str = "lesson"
    theme_en: str = ""
    situation: str = ""
    text_type: str = ""
    created: str = ""


# ---------------- attempts ----------------
class QuestionResult(BaseModel):
    id: int
    score: float
    feedback: str = ""


class QuizAttempt(BaseModel):
    attempt: int
    score: float
    passed: bool
    answers: dict[str, str]
    results: list[QuestionResult]


class ExerciseAttempt(BaseModel):
    score: float
    answers: dict[str, str]
    correct: dict[str, bool]


class ListeningAttempt(BaseModel):
    score: float
    answers: dict[str, str]
    correct: dict[str, bool]


class Criterion(BaseModel):
    name: str
    score: int = Field(ge=0, le=5)
    comment: str = ""


class Mistake(BaseModel):
    original: str
    correction: str
    explanation: str = ""


class ProductionFeedback(BaseModel):
    """Feedback on a written or spoken answer (4 criteria x 5 points = 20)."""
    criteria: list[Criterion]
    corrected_text: str = ""
    mistakes: list[Mistake] = Field(default_factory=list)
    feedback: str = ""

    @property
    def total(self) -> int:
        return sum(c.score for c in self.criteria)


class WritingAttempt(BaseModel):
    task_index: int
    text: str
    word_count: int
    result: ProductionFeedback
    timestamp: str


class SpeakingAttempt(BaseModel):
    transcript: str
    typed: bool = False
    audio_file: str = ""
    result: ProductionFeedback
    timestamp: str
