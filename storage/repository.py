"""File-based storage. Lessons are keyed by PLAN DAY (1..273), so a missed calendar
day never skips a lesson.

data/lessons/day_001.json    lesson content
data/audio/day_001_*.mp3     generated audio
data/recordings/day_001_*.wav  your speaking recordings
data/progress.json           settings, attempts, completion
"""
import datetime as dt
import json
from pathlib import Path

from pydantic import ValidationError

from agent.schemas import (
    ExerciseAttempt, Lesson, ListeningAttempt, QuizAttempt, SpeakingAttempt, WritingAttempt,
)

ATTEMPT_KINDS = {
    "quiz": QuizAttempt,
    "exercises": ExerciseAttempt,
    "listening": ListeningAttempt,
    "writing": WritingAttempt,
    "speaking": SpeakingAttempt,
}
REQUIRED_FOR_COMPLETION = ("exercises", "writing", "speaking")  # + a passed quiz


class LessonRepository:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.lessons_dir = self.root / "lessons"
        self.audio_dir = self.root / "audio"
        self.recordings_dir = self.root / "recordings"
        self.progress_file = self.root / "progress.json"
        for d in (self.lessons_dir, self.audio_dir, self.recordings_dir):
            d.mkdir(parents=True, exist_ok=True)

    # ---------- lessons ----------
    def _lesson_path(self, day: int) -> Path:
        return self.lessons_dir / f"day_{day:03d}.json"

    def save_lesson(self, lesson: Lesson) -> None:
        self._lesson_path(lesson.day).write_text(lesson.model_dump_json(indent=2), encoding="utf-8")

    def load_lesson(self, day: int) -> Lesson | None:
        path = self._lesson_path(day)
        if not path.exists():
            return None
        try:
            return Lesson.model_validate_json(path.read_text(encoding="utf-8"))
        except (ValidationError, json.JSONDecodeError):
            return None

    def lesson_days(self) -> list[int]:
        days = []
        for p in self.lessons_dir.glob("day_*.json"):
            try:
                days.append(int(p.stem.split("_")[1]))
            except (IndexError, ValueError):
                continue
        return sorted(days)

    def _lessons(self, exclude_day: int | None = None) -> list[Lesson]:
        out = []
        for d in self.lesson_days():
            if d != exclude_day and (lesson := self.load_lesson(d)):
                out.append(lesson)
        return out

    def taught_words(self, exclude_day: int | None = None) -> list[str]:
        """Words introduced in normal lessons (review lessons don't add words)."""
        return [v.polish for l in self._lessons(exclude_day) if l.lesson_type == "lesson"
                for v in l.new_vocabulary]

    def week_words(self, week: int, exclude_day: int | None = None) -> list[str]:
        return [v.polish for l in self._lessons(exclude_day)
                if l.week == week and l.lesson_type == "lesson" for v in l.new_vocabulary]

    # ---------- files ----------
    def audio_path(self, day: int, kind: str) -> Path:
        return self.audio_dir / f"day_{day:03d}_{kind}.mp3"

    def delete_audio(self, day: int) -> None:
        for p in self.audio_dir.glob(f"day_{day:03d}_*.mp3"):
            p.unlink(missing_ok=True)

    def save_recording(self, day: int, audio: bytes, suffix: str = "wav") -> str:
        n = len(list(self.recordings_dir.glob(f"day_{day:03d}_*"))) + 1
        path = self.recordings_dir / f"day_{day:03d}_{n:02d}.{suffix}"
        path.write_bytes(audio)
        return path.name

    def recording_path(self, name: str) -> Path:
        return self.recordings_dir / name

    # ---------- progress ----------
    def _read(self) -> dict:
        default = {"settings": {}, "completed": {}, "attempts": {}}
        if not self.progress_file.exists():
            return default
        try:
            data = json.loads(self.progress_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return default
        for k, v in default.items():
            data.setdefault(k, v)
        return data

    def _write(self, data: dict) -> None:
        self.progress_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def get_setting(self, key: str, default=None):
        return self._read()["settings"].get(key, default)

    def set_setting(self, key: str, value) -> None:
        data = self._read()
        data["settings"][key] = value
        self._write(data)

    @property
    def current_day(self) -> int:
        return int(self.get_setting("current_day", 1))

    @current_day.setter
    def current_day(self, day: int) -> None:
        self.set_setting("current_day", max(1, int(day)))

    # ---------- attempts ----------
    def add_attempt(self, day: int, kind: str, attempt) -> None:
        data = self._read()
        data["attempts"].setdefault(str(day), {}).setdefault(kind, []).append(attempt.model_dump())
        self._write(data)

    def attempts(self, day: int, kind: str) -> list:
        raw = self._read()["attempts"].get(str(day), {}).get(kind, [])
        return [ATTEMPT_KINDS[kind].model_validate(a) for a in raw]

    def reset_day(self, day: int) -> None:
        """Remove attempts and completion (used when a lesson is regenerated)."""
        data = self._read()
        data["attempts"].pop(str(day), None)
        data["completed"].pop(str(day), None)
        self._write(data)

    # ---------- completion ----------
    def checklist(self, day: int) -> dict[str, bool]:
        status = {kind: bool(self.attempts(day, kind)) for kind in REQUIRED_FOR_COMPLETION}
        status["quiz"] = any(a.passed for a in self.attempts(day, "quiz"))
        return status

    def update_completion(self, day: int, today: dt.date | None = None) -> bool:
        """Mark the day completed when all requirements are met. Returns True if completed."""
        if self.is_completed(day):
            return True
        if all(self.checklist(day).values()):
            data = self._read()
            data["completed"][str(day)] = (today or dt.date.today()).isoformat()
            self._write(data)
            return True
        return False

    def is_completed(self, day: int) -> bool:
        return str(day) in self._read()["completed"]

    def stats(self, today: dt.date) -> dict:
        completed: dict[str, str] = self._read()["completed"]
        dates = set(completed.values())
        streak, d = 0, today
        if d.isoformat() not in dates:
            d -= dt.timedelta(days=1)
        while d.isoformat() in dates:
            streak += 1
            d -= dt.timedelta(days=1)
        done = [l for l in self._lessons() if str(l.day) in completed]
        return {
            "lessons": len(done),
            "words": sum(len(l.new_vocabulary) for l in done if l.lesson_type == "lesson"),
            "grammar": len({g.id for l in done for g in l.grammar_rules}),
            "streak": streak,
        }
