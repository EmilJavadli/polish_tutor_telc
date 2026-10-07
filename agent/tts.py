"""Text-to-speech with ElevenLabs (reading aloud + listening dialogues)."""
from functools import lru_cache

from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs

from config import (
    ELEVENLABS_API_KEY,
    ELEVENLABS_LANGUAGE_CODE,
    ELEVENLABS_MODEL,
    ELEVENLABS_VOICE_ID,
    ELEVENLABS_VOICE_ID_2,
)

OUTPUT_FORMAT = "mp3_44100_128"
PACE_SPEED = {"normal": 1.0, "slow": 0.8}


def tts_available() -> bool:
    return bool(ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID)


@lru_cache(maxsize=1)
def get_client() -> ElevenLabs:
    if not tts_available():
        raise RuntimeError("ELEVENLABS_API_KEY / ELEVENLABS_VOICE_ID missing in .streamlit/secrets.toml")
    return ElevenLabs(api_key=ELEVENLABS_API_KEY)


def _convert(text: str, voice_id: str, pace: str) -> bytes:
    kwargs: dict = {
        "voice_id": voice_id,
        "model_id": ELEVENLABS_MODEL,
        "text": text.strip(),
        "output_format": OUTPUT_FORMAT,
        "voice_settings": VoiceSettings(
            stability=0.5, similarity_boost=0.75, speed=PACE_SPEED.get(pace, 1.0)
        ),
    }
    if ELEVENLABS_LANGUAGE_CODE:
        kwargs["language_code"] = ELEVENLABS_LANGUAGE_CODE
    try:
        return b"".join(get_client().text_to_speech.convert(**kwargs))
    except Exception:
        # Retry once with default voice settings in case the model rejects a setting
        kwargs.pop("voice_settings")
        return b"".join(get_client().text_to_speech.convert(**kwargs))


def synthesize_speech(text: str, pace: str = "normal") -> bytes:
    """Read a Polish text aloud. Returns MP3 bytes."""
    if not text or not text.strip():
        raise ValueError("Text for speech synthesis is empty.")
    try:
        audio = _convert(text, ELEVENLABS_VOICE_ID, pace)  # type: ignore[arg-type]
    except Exception as exc:
        raise RuntimeError(f"ElevenLabs text-to-speech failed: {exc}") from exc
    if not audio:
        raise RuntimeError("ElevenLabs returned empty audio.")
    return audio


def synthesize_dialogue(lines: list[tuple[str, str]]) -> bytes:
    """Read a dialogue. With ELEVENLABS_VOICE_ID_2 set, speakers alternate between
    two voices (consecutive lines of one speaker are merged into one request)."""
    speakers = list(dict.fromkeys(s for s, _ in lines))
    if not ELEVENLABS_VOICE_ID_2 or len(speakers) < 2:
        return synthesize_speech("\n".join(t for _, t in lines))

    voices = {s: (ELEVENLABS_VOICE_ID if i % 2 == 0 else ELEVENLABS_VOICE_ID_2)
              for i, s in enumerate(speakers)}
    turns: list[tuple[str, str]] = []
    for speaker, text in lines:
        if turns and turns[-1][0] == speaker:
            turns[-1] = (speaker, turns[-1][1] + " " + text)
        else:
            turns.append((speaker, text))
    try:
        return b"".join(_convert(text, voices[s], "normal") for s, text in turns)  # type: ignore[arg-type]
    except Exception as exc:
        raise RuntimeError(f"ElevenLabs text-to-speech failed: {exc}") from exc
