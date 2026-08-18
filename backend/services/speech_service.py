import io
import os
import tempfile
import uuid
from pathlib import Path

import edge_tts
from faster_whisper import WhisperModel

# =========================================================
# CONFIG
# =========================================================

# Load model once (base is good balance of speed/accuracy)
# Options: tiny, base, small, medium, large-v3
WHISPER_MODEL_SIZE = "base"
WHISPER_DEVICE = "cpu"          # change to "cuda" if you have GPU
WHISPER_COMPUTE_TYPE = "int8"   # good for CPU

_whisper_model = None

# Edge-TTS voices (good quality free voices)
# You can expand this list later
VOICE_MAP = {
    "en": "en-US-JennyNeural",
    "hi": "hi-IN-SwaraNeural",
    "te": "te-IN-ShrutiNeural",
    "ta": "ta-IN-PallaviNeural",
    "kn": "kn-IN-SapnaNeural",
    "ml": "ml-IN-SobhanaNeural",
    "bn": "bn-IN-TanishaaNeural",
    "mr": "mr-IN-AarohiNeural",
    "gu": "gu-IN-DhwaniNeural",
    "pa": "pa-IN-GurpreetNeural",
    "es": "es-ES-ElviraNeural",
    "fr": "fr-FR-DeniseNeural",
    "de": "de-DE-KatjaNeural",
    "it": "it-IT-ElsaNeural",
    "ja": "ja-JP-NanamiNeural",
    "ko": "ko-KR-SunHiNeural",
    "ar": "ar-SA-ZariyahNeural",
    "zh-CN": "zh-CN-XiaoxiaoNeural",
    "ru": "ru-RU-SvetlanaNeural",
}

DEFAULT_VOICE = "en-US-JennyNeural"


def get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        print(f"Loading Whisper model: {WHISPER_MODEL_SIZE} ...")
        _whisper_model = WhisperModel(
            WHISPER_MODEL_SIZE,
            device=WHISPER_DEVICE,
            compute_type=WHISPER_COMPUTE_TYPE,
        )
    return _whisper_model


# =========================================================
# SPEECH TO TEXT
# =========================================================

def speech_to_text(audio_bytes: bytes, language: str | None = None) -> dict:
    """
    Convert audio bytes to text using faster-whisper.
    Returns: { "text": str, "language": str, "confidence": float }
    """
    if not audio_bytes:
        return {"text": "", "language": None, "confidence": 0.0}

    model = get_whisper_model()

    # Write to temporary file (faster-whisper works better with file path)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        segments, info = model.transcribe(
            tmp_path,
            language=language if language and language != "auto" else None,
            beam_size=5,
            vad_filter=True,
        )

        text_parts = []
        total_prob = 0.0
        count = 0

        for segment in segments:
            text_parts.append(segment.text.strip())
            if segment.avg_logprob is not None:
                # Convert logprob to rough confidence
                total_prob += max(0.0, min(1.0, (segment.avg_logprob + 1.0)))
                count += 1

        full_text = " ".join(text_parts).strip()
        avg_confidence = (total_prob / count) if count > 0 else 0.0

        detected_lang = info.language if info.language else "en"

        return {
            "text": full_text,
            "language": detected_lang,
            "confidence": round(avg_confidence, 3),
        }

    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


# =========================================================
# TEXT TO SPEECH
# =========================================================

async def text_to_speech(text: str, language: str = "en") -> bytes:
    """
    Convert text to speech using edge-tts.
    Returns audio bytes (mp3).
    """
    if not text or not text.strip():
        return b""

    voice = VOICE_MAP.get(language, DEFAULT_VOICE)

    communicate = edge_tts.Communicate(text=text, voice=voice)

    # Collect audio into memory
    audio_buffer = io.BytesIO()

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_buffer.write(chunk["data"])

    return audio_buffer.getvalue()


def get_available_voices() -> dict:
    """Return the voice map for frontend reference."""
    return VOICE_MAP