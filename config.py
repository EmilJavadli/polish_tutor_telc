"""Configuration. Secrets are read from .streamlit/secrets.toml (falls back to env vars)."""
import os
from pathlib import Path


def _secret(name: str, default: str | None = None) -> str | None:
    """Read a value from st.secrets (exact or lower-case key), then environment variables."""
    try:
        import streamlit as st

        for key in (name, name.lower()):
            if key in st.secrets:
                value = st.secrets[key]
                return str(value) if value not in (None, "") else default
    except Exception:  # no secrets.toml (e.g. when running unit tests)
        pass
    return os.getenv(name, default)


# --- API keys / models ---
OPENAI_API_KEY: str | None = _secret("OPENAI_API_KEY")
LLM_MODEL: str = _secret("LLM_MODEL", "gpt-6-luna") or "gpt-6-luna"
STT_MODEL: str = _secret("STT_MODEL", "gpt-transcribe") or "gpt-transcribe"

ELEVENLABS_API_KEY: str | None = _secret("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID: str | None = _secret("ELEVENLABS_VOICE_ID")
ELEVENLABS_VOICE_ID_2: str | None = _secret("ELEVENLABS_VOICE_ID_2")  # optional 2nd voice for dialogues
ELEVENLABS_MODEL: str = _secret("ELEVENLABS_MODEL", "eleven_v4_turbo") or "eleven_v4_turbo"
ELEVENLABS_LANGUAGE_CODE: str | None = _secret("ELEVENLABS_LANGUAGE_CODE") or "pl"

DATA_DIR: Path = Path(_secret("DATA_DIR", "data") or "data")

# --- Lesson content ---
NEW_WORDS_PER_LESSON: int = 15
GRAMMAR_RULES_PER_LESSON: int = 3
LISTENING_TASKS: int = 5
EXERCISE_COMPOSITION: dict[str, int] = {"vocabulary": 5, "grammar": 9, "language_elements": 5}
GRAMMAR_EXERCISES_PER_RULE: int = 3
MAX_GENERATION_ATTEMPTS: int = 3
MAX_KNOWN_WORDS_IN_PROMPT: int = 400

# --- Quiz ---
QUIZ_COMPOSITION: dict[str, int] = {"multiple_choice": 4, "fill_blank": 3, "open": 3}
QUIZ_PASS_SCORE: float = 0.80

# --- Suggested time split of the daily hour (minutes) ---
TIME_PLAN: dict[str, int] = {
    "Reading": 10, "Listening": 10, "Words": 5, "Grammar": 5,
    "Exercises": 10, "Writing": 10, "Speaking": 5, "Quiz": 5,
}
