import base64
import io

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import StreamingResponse

from backend.services.speech_service import (
    speech_to_text,
    text_to_speech,
    get_available_voices,
)

from backend.services.translation_service import (
    translate_text,
)


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/api",
    tags=["Speech"],
)


# =========================================================
# SUPPORTED LANGUAGES
# =========================================================

SUPPORTED_LANGUAGES = {
    "en",
    "hi",
    "te",
    "ta",
    "kn",
    "ml",
    "bn",
    "mr",
    "gu",
    "pa",
    "es",
    "fr",
    "de",
    "it",
    "ja",
    "ko",
    "ar",
    "zh-CN",
    "ru",
}

MAX_AUDIO_SIZE = 25 * 1024 * 1024


# =========================================================
# LANGUAGE VALIDATION
# =========================================================

def normalize_language(language: str | None) -> str:
    """
    Normalize language values received from frontend.
    """

    if not language:
        return "auto"

    language = language.strip()

    if language.lower() == "auto":
        return "auto"

    return language


def validate_language(
    language: str,
    allow_auto: bool = True,
) -> bool:

    if allow_auto and language == "auto":
        return True

    return language in SUPPORTED_LANGUAGES


# =========================================================
# READ AUDIO
# =========================================================

async def read_audio_file(
    audio: UploadFile,
) -> bytes:

    if not audio:
        raise ValueError("Audio file is required.")

    audio_bytes = await audio.read()

    if not audio_bytes:
        raise ValueError("Uploaded audio file is empty.")

    if len(audio_bytes) > MAX_AUDIO_SIZE:
        raise ValueError(
            "Audio file is too large. Maximum size is 25 MB."
        )

    return audio_bytes


# =========================================================
# SPEECH → TEXT
# =========================================================

@router.post("/speech-to-text")
async def speech_to_text_endpoint(
    audio: UploadFile = File(...),
    language: str = Form("auto"),
):
    """
    Convert spoken audio into text using faster-whisper.
    """

    try:

        language = normalize_language(language)

        if not validate_language(language):
            return {
                "success": False,
                "error": f"Unsupported language: {language}",
            }

        audio_bytes = await read_audio_file(audio)

        result = speech_to_text(
            audio_bytes,
            language=language,
        )

        text = (
            result.get("text")
            or ""
        ).strip()

        detected_language = (
            result.get("language")
            or "en"
        )

        confidence = result.get(
            "confidence",
            0.0,
        )

        if not text:

            return {
                "success": False,
                "error": (
                    "Could not detect speech "
                    "from the uploaded audio."
                ),
                "detected_language": detected_language,
            }

        return {
            "success": True,
            "text": text,
            "detected_language": detected_language,
            "confidence": confidence,
        }

    except ValueError as error:

        return {
            "success": False,
            "error": str(error),
        }

    except Exception as error:

        print(
            "Speech-to-text error:",
            repr(error),
        )

        return {
            "success": False,
            "error": (
                "Speech-to-text failed. "
                "Please try again."
            ),
        }


# =========================================================
# TEXT → SPEECH
# =========================================================

@router.post("/text-to-speech")
async def text_to_speech_endpoint(
    text: str = Form(...),
    language: str = Form("en"),
):
    """
    Convert text into MP3 speech using Edge TTS.
    """

    try:

        text = (
            text or ""
        ).strip()

        language = normalize_language(language)

        if not text:

            return {
                "success": False,
                "error": (
                    "Please provide text "
                    "to convert to speech."
                ),
            }

        if not validate_language(
            language,
            allow_auto=False,
        ):

            return {
                "success": False,
                "error": (
                    f"Unsupported target "
                    f"language: {language}"
                ),
            }

        audio_bytes = await text_to_speech(
            text,
            language=language,
        )

        if not audio_bytes:

            return {
                "success": False,
                "error": (
                    "Failed to generate speech."
                ),
            }

        return StreamingResponse(
            io.BytesIO(audio_bytes),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition":
                    "inline; filename=travelmate_speech.mp3"
            },
        )

    except Exception as error:

        print(
            "Text-to-speech error:",
            repr(error),
        )

        return {
            "success": False,
            "error": (
                "Text-to-speech failed. "
                "Please try again."
            ),
        }


# =========================================================
# VOICE → TRANSLATION → VOICE
# =========================================================

@router.post("/voice-translate")
async def voice_translate(
    audio: UploadFile = File(...),
    target: str = Form(...),
    source: str = Form("auto"),
):
    """
    Complete voice translation pipeline:

    Audio
       ↓
    Whisper
       ↓
    Detected text
       ↓
    Translation
       ↓
    Edge TTS
       ↓
    Base64 MP3

    Returns:
    - original text
    - detected source language
    - translated text
    - target language
    - generated audio
    """

    try:

        # -------------------------------------------------
        # Normalize languages
        # -------------------------------------------------

        source = normalize_language(source)
        target = normalize_language(target)

        # -------------------------------------------------
        # Validate target
        # -------------------------------------------------

        if target == "auto":

            return {
                "success": False,
                "error": (
                    "Target language cannot "
                    "be Auto Detect."
                ),
            }

        if not validate_language(
            target,
            allow_auto=False,
        ):

            return {
                "success": False,
                "error": (
                    f"Unsupported target "
                    f"language: {target}"
                ),
            }

        # -------------------------------------------------
        # Validate source
        # -------------------------------------------------

        if not validate_language(source):

            return {
                "success": False,
                "error": (
                    f"Unsupported source "
                    f"language: {source}"
                ),
            }

        # -------------------------------------------------
        # Read audio
        # -------------------------------------------------

        audio_bytes = await read_audio_file(
            audio
        )

        # =================================================
        # STEP 1 — SPEECH TO TEXT
        # =================================================

        stt_result = speech_to_text(
            audio_bytes,
            language=(
                None
                if source == "auto"
                else source
            ),
        )

        original_text = (
            stt_result.get("text")
            or ""
        ).strip()

        detected_source = (
            stt_result.get("language")
            or "en"
        )

        confidence = stt_result.get(
            "confidence",
            0.0,
        )

        if not original_text:

            return {
                "success": False,
                "error": (
                    "Could not detect speech "
                    "from the audio."
                ),
                "detected_language":
                    detected_source,
            }

        # =================================================
        # STEP 2 — DETERMINE SOURCE LANGUAGE
        # =================================================

        if source == "auto":

            source_language = detected_source

        else:

            source_language = source

        # =================================================
        # STEP 3 — TRANSLATION
        # =================================================

        if (
            source_language == target
        ):

            translated_text = (
                original_text
            )

        else:

            translated_text = translate_text(
                original_text,
                target=target,
                source=source_language,
            )

        translated_text = (
            translated_text or ""
        ).strip()

        if not translated_text:

            return {
                "success": False,
                "error": (
                    "Translation returned "
                    "empty text."
                ),
            }

        # =================================================
        # STEP 4 — TEXT TO SPEECH
        # =================================================

        audio_bytes_out = await text_to_speech(
            translated_text,
            language=target,
        )

        if not audio_bytes_out:

            return {
                "success": False,
                "error": (
                    "Translation succeeded, "
                    "but speech generation failed."
                ),
                "original_text":
                    original_text,
                "translated_text":
                    translated_text,
            }

        # =================================================
        # STEP 5 — BASE64 AUDIO
        # =================================================

        audio_base64 = base64.b64encode(
            audio_bytes_out
        ).decode("utf-8")

        # =================================================
        # FINAL RESPONSE
        # =================================================

        return {
            "success": True,

            "source_language":
                source_language,

            "target_language":
                target,

            "original_text":
                original_text,

            "translated_text":
                translated_text,

            "audio_base64":
                audio_base64,

            "audio_format":
                "mp3",

            "stt_confidence":
                confidence,
        }

    except ValueError as error:

        return {
            "success": False,
            "error": str(error),
        }

    except Exception as error:

        print(
            "Voice translation error:",
            repr(error),
        )

        return {
            "success": False,
            "error": (
                "Voice translation failed. "
                "Please try again."
            ),
        }


# =========================================================
# AVAILABLE VOICES
# =========================================================

@router.get("/voices")
async def list_voices():
    """
    Return available Edge-TTS voices.
    """

    try:

        voices = get_available_voices()

        return {
            "success": True,
            "voices": voices,
        }

    except Exception as error:

        print(
            "Voice list error:",
            repr(error),
        )

        return {
            "success": False,
            "voices": {},
            "error": (
                "Unable to load available voices."
            ),
        }