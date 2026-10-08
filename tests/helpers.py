"""Builds valid fake lessons for tests."""
from agent.schemas import (
    ChoiceTask, CoreLesson, DialogueLine, Example, Exercise, GrammarRule, Lesson, Listening,
    Practice, QuizQuestion, SpeakingTask, WritingTask,
)
from curriculum import get_plan_day

WORDS = ["sąsiadka", "klatka schodowa", "dzień dobry", "mieszkanie", "piętro", "nazywać się",
         "pochodzić", "pracować", "kawa", "herbata", "miły", "nowy", "Kraków", "ulica", "wieczorem"]


def make_core(day: int = 1, words=None) -> CoreLesson:
    plan = get_plan_day(day)
    words = words or WORDS
    sentence = " ".join(words) + ". "
    lo, hi = plan.reading_length
    reading = (sentence * 20).split()
    reading = " ".join(reading[: (lo + hi) // 2])
    lines = [DialogueLine(speaker="Anna" if i % 2 else "Piotr", text="Dzień dobry, jak się pan ma dzisiaj rano?")
             for i in range(6)]
    return CoreLesson(
        title_pl="Nowa sąsiadka", title_en="The new neighbour",
        reading_pl=reading, reading_en="translation",
        new_vocabulary=[{"polish": w, "form_in_story": w, "english": "x", "example_pl": "x", "example_en": "x"}
                        for w in words[:plan.target_words]],
        grammar_rules=[GrammarRule(id=g, title=t, explanation="Explained.",
                                   examples=[Example(polish="a", english="a")] * 3, story_examples=["x"])
                       for g, t in zip(plan.grammar_ids, plan.grammar_titles)],
        listening=Listening(type=plan.listening_type, situation_en="Two neighbours meet.",
                            lines=lines,
                            tasks=[ChoiceTask(id=i, question=f"Pytanie {i}?", options=["a", "b", "c"],
                                              correct_option=1) for i in range(1, 6)]),
    )


def make_practice(day: int = 1) -> Practice:
    plan = get_plan_day(day)
    ex = [Exercise(id=i, section="vocabulary", type="choice", prompt="Wybierz", options=["a", "b", "c"],
                   correct_option=0) for i in range(1, 6)]
    i = 6
    for n in range(9):
        gid = plan.grammar_ids[n % len(plan.grammar_ids)]
        ex.append(Exercise(id=i, section="grammar", type="gap_fill", grammar_id=gid,
                           prompt="Piję ___ (kawa).", accepted_answers=["kawę"]))
        i += 1
    ex += [Exercise(id=j, section="language_elements", type="choice", prompt="___", options=["a", "b", "c"],
                    correct_option=2) for j in range(15, 20)]
    quiz = ([QuizQuestion(id=k, type="multiple_choice", question=f"P{k}?", options=["a", "b", "c", "d"],
                          correct_option=1) for k in range(1, 5)]
            + [QuizQuestion(id=k, type="fill_blank", question="Piję ___ (kawa).", accepted_answers=["kawę"])
               for k in range(5, 8)]
            + [QuizQuestion(id=k, type="open", question=f"Dlaczego {k}?", reference_answer="Bo tak.")
               for k in range(8, 11)])
    return Practice(
        exercises=ex,
        writing_tasks=[WritingTask(situation_pl="Napisz SMS.", situation_en="Write an SMS.",
                                   points_pl=["a", "b", "c"])] * 2,
        speaking=SpeakingTask(part=plan.speaking_part, title="O sobie", instructions_pl="Opowiedz.",
                              instructions_en="Tell.", prompts=["a", "b", "c"],
                              useful_phrases=[Example(polish="x", english="y")] * 6,
                              opinions=["o1", "o2", "o3"] if plan.speaking_part == 3 else []),
        quiz=quiz,
    )


def make_lesson(day: int = 1) -> Lesson:
    plan = get_plan_day(day)
    return Lesson(**make_core(day).model_dump(), **make_practice(day).model_dump(), day=day, week=plan.week,
                  level=plan.level, lesson_type=plan.lesson_type, theme_en=plan.theme_en,
                  situation=plan.situation, text_type=plan.text_type)
