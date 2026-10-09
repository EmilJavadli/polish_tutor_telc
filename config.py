"""Application configuration loaded from Streamlit secrets, then environment variables."""
import os
from pathlib import Path

def _secret(name: str, default=None, section: str | None = None):
    try:
        import streamlit as st
        if section and section in st.secrets and name in st.secrets[section]:
            return st.secrets[section][name]
        for key in (name, name.lower()):
            if key in st.secrets:
                return st.secrets[key]
    except Exception:
        pass
    env_name = f"{section.upper()}_{name.upper()}" if section else name
    return os.getenv(env_name, default)

OPENAI_API_KEY = _secret("OPENAI_API_KEY")
ELEVENLABS_API_KEY = _secret("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = _secret("ELEVENLABS_VOICE_ID")
ELEVENLABS_VOICE_ID_2 = _secret("ELEVENLABS_VOICE_ID_2")
DATABASE_URL = _secret("DATABASE_URL", section="database")

LLM_MODEL = "gpt-6-luna"
STT_MODEL = "gpt-transcribe"
ELEVENLABS_MODEL = "eleven_v4_turbo"
ELEVENLABS_LANGUAGE_CODE = "pl"
PLACEMENT_VERSION = "v1"
DATA_DIR = Path(str("data"))

NEW_WORDS_PER_LESSON = 15
GRAMMAR_RULES_PER_LESSON = 3
LISTENING_TASKS = 5
EXERCISE_COMPOSITION = {"vocabulary": 5, "grammar": 9, "language_elements": 5}
GRAMMAR_EXERCISES_PER_RULE = 3
MAX_GENERATION_ATTEMPTS = 3
MAX_KNOWN_WORDS_IN_PROMPT = 400
QUIZ_COMPOSITION = {"multiple_choice": 4, "fill_blank": 3, "open": 3}
QUIZ_PASS_SCORE = .80
TIME_PLAN = {"Reading":10,"Listening":10,"Words":5,"Grammar":5,"Exercises":10,"Writing":10,"Speaking":5,"Quiz":5}
