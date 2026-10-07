"""Run: python -m unittest discover tests -v"""
import datetime as dt
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agent.graders import (
    _parse_feedback, grade_exercises, grade_quiz, is_correct_gap, normalize_answer,
)
from agent.lesson_generator import validate_core, validate_practice
from agent.prompts import PRODUCTION_CRITERIA
from agent.schemas import ExerciseAttempt, ProductionFeedback, SpeakingAttempt, WritingAttempt
from curriculum import GRAMMAR, TOTAL_DAYS, WEEKS, get_plan_day, plan_markdown
from storage.repository import LessonRepository
from tests.helpers import WORDS, make_core, make_lesson, make_practice

CLOSED_OK = {**{str(i): "1" for i in range(1, 5)}, **{str(i): "Kawę." for i in range(5, 8)}}


def fake_open_grader(scores):
    return lambda _m: {"results": [{"id": i, "score": s, "feedback": "hint"} for i, s in scores.items()]}


class TestCurriculum(unittest.TestCase):
    def test_plan_is_9_months(self):
        self.assertEqual(TOTAL_DAYS, 273)
        self.assertEqual(len(WEEKS), 39)
        self.assertEqual({w.month for w in WEEKS}, set(range(1, 10)))

    def test_every_grammar_point_is_used_and_valid(self):
        used = {g for w in WEEKS for g in w.grammar}
        self.assertEqual(used, set(GRAMMAR))

    def test_each_day_has_3_distinct_grammar_points(self):
        for d in range(1, TOTAL_DAYS + 1):
            self.assertEqual(len(set(get_plan_day(d).grammar_ids)), 3, d)

    def test_day_7_is_review(self):
        self.assertEqual(get_plan_day(7).lesson_type, "review")
        self.assertEqual(get_plan_day(8).lesson_type, "lesson")

    def test_levels_progress(self):
        self.assertEqual(get_plan_day(1).level, "A1")
        self.assertEqual(get_plan_day(60).level, "A2")
        self.assertEqual(get_plan_day(273).level, "B1")

    def test_plan_markdown(self):
        self.assertIn("Week 39", plan_markdown())


class TestValidation(unittest.TestCase):
    def test_valid_core(self):
        self.assertEqual(validate_core(make_core(), get_plan_day(1), [], []), [])

    def test_wrong_grammar_ids(self):
        core = make_core()
        core.grammar_rules[0].id = "G50"
        self.assertTrue(any("grammar_rules ids" in p for p in validate_core(core, get_plan_day(1), [], [])))

    def test_known_word_rejected(self):
        p = validate_core(make_core(), get_plan_day(1), ["kawa"], [])
        self.assertTrue(any("already known" in x for x in p))

    def test_review_words_must_be_from_week(self):
        p = validate_core(make_core(7), get_plan_day(7), [], ["kot"])
        self.assertTrue(any("not in this week" in x for x in p))
        self.assertEqual(validate_core(make_core(7), get_plan_day(7), WORDS, WORDS), [])

    def test_valid_practice(self):
        for d in (1, 2, 3):
            self.assertEqual(validate_practice(make_practice(d), get_plan_day(d)), [], d)

    def test_practice_wrong_speaking_part(self):
        pr = make_practice(1)
        pr.speaking.part = 3
        self.assertTrue(any("speaking.part" in p for p in validate_practice(pr, get_plan_day(1))))


class TestGrading(unittest.TestCase):
    def test_diacritics_matter(self):
        self.assertTrue(is_correct_gap(" Kawę! ", ["kawę"]))
        self.assertFalse(is_correct_gap("kawe", ["kawę"]))
        self.assertEqual(normalize_answer("Kawę."), "kawę")

    def test_exercises(self):
        lesson = make_lesson()
        answers = {str(e.id): ("0" if e.section == "vocabulary" else "x") for e in lesson.exercises}
        result = grade_exercises(lesson.exercises, answers)
        self.assertAlmostEqual(result.score, 5 / 19, places=3)

    def test_quiz_pass_at_80(self):
        with patch("agent.graders.chat_json", fake_open_grader({8: 1, 9: 0, 10: 0})):
            r = grade_quiz(make_lesson(), {**CLOSED_OK, "8": "a", "9": "b", "10": "c"}, 1)
        self.assertTrue(r.passed)
        self.assertAlmostEqual(r.score, 0.8)

    def test_quiz_fail_below_80(self):
        with patch("agent.graders.chat_json", fake_open_grader({8: 1, 9: 0.5, 10: 0})):
            r = grade_quiz(make_lesson(), {**CLOSED_OK, "1": "0", "8": "a", "9": "b", "10": "c"}, 1)
        self.assertFalse(r.passed)

    def test_parse_feedback_clamps_and_fills(self):
        names = PRODUCTION_CRITERIA["writing"]
        fb = _parse_feedback({"criteria": [{"name": names[0], "score": 9}, {"name": "x", "score": "3"}],
                              "mistakes": [{"original": "a"}]}, names)
        self.assertEqual([c.score for c in fb.criteria], [5, 3, 0, 0])
        self.assertEqual(fb.total, 8)
        self.assertEqual(fb.mistakes, [])


class TestRepository(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = LessonRepository(Path(self.tmp.name))

    def tearDown(self):
        self.tmp.cleanup()

    def _fb(self):
        return ProductionFeedback(criteria=[])

    def test_completion_requires_all_parts(self):
        self.repo.save_lesson(make_lesson(1))
        with patch("agent.graders.chat_json", fake_open_grader({8: 1, 9: 1, 10: 1})):
            self.repo.add_attempt(1, "quiz", grade_quiz(make_lesson(), {**CLOSED_OK, "8": "a", "9": "b", "10": "c"}, 1))
        self.assertFalse(self.repo.update_completion(1))
        self.repo.add_attempt(1, "exercises", ExerciseAttempt(score=0.5, answers={}, correct={}))
        self.repo.add_attempt(1, "writing", WritingAttempt(task_index=0, text="t", word_count=1,
                                                           result=self._fb(), timestamp="t"))
        self.assertFalse(self.repo.update_completion(1))
        self.repo.add_attempt(1, "speaking", SpeakingAttempt(transcript="t", result=self._fb(), timestamp="t"))
        self.assertTrue(self.repo.update_completion(1, dt.date(2026, 10, 5)))
        stats = self.repo.stats(dt.date(2026, 10, 5))
        self.assertEqual((stats["lessons"], stats["words"], stats["grammar"], stats["streak"]), (1, 15, 3, 1))

    def test_review_lessons_do_not_add_words(self):
        self.repo.save_lesson(make_lesson(1))
        self.repo.save_lesson(make_lesson(7))
        self.assertEqual(len(self.repo.taught_words()), 15)
        self.assertEqual(len(self.repo.week_words(1)), 15)

    def test_reset_day(self):
        self.repo.add_attempt(2, "exercises", ExerciseAttempt(score=1, answers={}, correct={}))
        self.repo.reset_day(2)
        self.assertEqual(self.repo.attempts(2, "exercises"), [])

    def test_current_day_setting(self):
        self.assertEqual(self.repo.current_day, 1)
        self.repo.current_day = 5
        self.assertEqual(self.repo.current_day, 5)


if __name__ == "__main__":
    unittest.main()
