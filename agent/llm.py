"""OpenAI wrapper: JSON calls, streaming chat and speech-to-text."""
import json
from collections.abc import Iterator
from functools import lru_cache

from openai import OpenAI

from config import LLM_MODEL, OPENAI_API_KEY, STT_MODEL


@lru_cache(maxsize=1)
def get_client() -> OpenAI:
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is missing in .streamlit/secrets.toml")
    return OpenAI(api_key=OPENAI_API_KEY)


def chat_json(messages: list[dict]) -> dict:
    """Call the model in JSON mode and return the parsed object.

    Raises:
        json.JSONDecodeError: if the model returns invalid JSON.
    """
    response = get_client().chat.completions.create(
        model=LLM_MODEL, messages=messages, response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content or "")


def chat_stream(messages: list[dict]) -> Iterator[str]:
    """Stream a plain-text chat response."""
    stream = get_client().chat.completions.create(model=LLM_MODEL, messages=messages, stream=True)
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


def transcribe(audio: bytes, filename: str = "answer.wav", context: str = "") -> str:
    """Transcribe Polish speech. Language hints are passed as `languages` (gpt-transcribe)."""
    kwargs: dict = {"model": STT_MODEL, "file": (filename, audio)}
    if context:
        kwargs["prompt"] = context
    if STT_MODEL.startswith("gpt-transcribe") or STT_MODEL.startswith("gpt-live"):
        kwargs["extra_body"] = {"languages": ["pl"]}
    else:
        kwargs["language"] = "pl"
    result = get_client().audio.transcriptions.create(**kwargs)
    return (getattr(result, "text", None) or str(result)).strip()
