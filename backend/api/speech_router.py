import io
from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import StreamingResponse

from backend.services.speech_service import (
    speech_to_text,
    text_to_speech,
    get_available_voices,
)
from backend.services.translation_service import (
    detect_language,
    translate_text,
)

router = APIRouter(
    prefix="/api",
    tags=["Speech"],
)


# ---------------------------------------------------------
# Speech → Text
# ---------------------------------------------------------

@router.post("/speech-to-text")
async def speech_to_text_endpoint(
    audio: UploadFile = File(...),
    language: str = Form("auto"),
):
    try:
        audio_bytes = await audio.read()

        if not audio_bytes:
            return {
                "success": False,
                "error": "Empty audio file.",
            }

        result = speech_to_text(audio_bytes, language=language)

        if not result["text"]:
            return {
                "success": False,
                "error": "Could not detect any speech in the audio.",
            }

        return {
            "success": True,
            "text": result["text"],
            "detected_language": result["language"],
            "confidence": result["confidence"],
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Speech-to-text failed: {str(e)}",
        }


# ---------------------------------------------------------
# Text → Speech
# ---------------------------------------------------------

@router.post("/text-to-speech")
async def text_to_speech_endpoint(
    text: str = Form(...),
    language: str = Form("en"),
):
    try:
        if not text.strip():
            return {
                "success": False,
                "error": "Please provide some text.",
            }

        audio_bytes = await text_to_speech(text, language=language)

        if not audio_bytes:
            return {
                "success": False,
                "error": "Failed to generate speech.",
            }

        return StreamingResponse(
            io.BytesIO(audio_bytes),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline; filename=speech.mp3"
            },
        )

    except Exception as e:
        return {
            "success": False,
            "error": f"Text-to-speech failed: {str(e)}",
        }


# ---------------------------------------------------------
# Voice → Voice Translation (returns both text + audio)
# ---------------------------------------------------------

@router.post("/voice-translate")
async def voice_translate(
    audio: UploadFile = File(...),
    target: str = Form(...),
    source: str = Form("auto"),
):
    try:
        if not target:
            return {
                "success": False,
                "error": "Please select a target language.",
            }

        audio_bytes = await audio.read()

        if not audio_bytes:
            return {
                "success": False,
                "error": "Empty audio file.",
            }

        # 1. Speech → Text
        stt_result = speech_to_text(
            audio_bytes,
            language=source if source != "auto" else None,
        )

        original_text = stt_result["text"]
        detected_source = stt_result["language"] or "en"

        if not original_text:
            return {
                "success": False,
                "error": "Could not detect any speech in the audio.",
            }

        # 2. Translate
        if source == "auto":
            source_lang = detected_source
        else:
            source_lang = source

        if source_lang == target:
            translated_text = original_text
        else:
            translated_text = translate_text(
                original_text,
                target=target,
                source=source_lang,
            )

        # 3. Text → Speech (in target language)
        audio_bytes_out = await text_to_speech(
            translated_text,
            language=target,
        )

        # We return JSON with text + base64 audio
        # (cleaner for frontend than multipart)
        import base64

        audio_base64 = base64.b64encode(audio_bytes_out).decode("utf-8")

        return {
            "success": True,
            "source_language": source_lang,
            "target_language": target,
            "original_text": original_text,
            "translated_text": translated_text,
            "audio_base64": audio_base64,
            "audio_format": "mp3",
            "stt_confidence": stt_result["confidence"],
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Voice translation failed: {str(e)}",
        }


# ---------------------------------------------------------
# Helper: list available voices
# ---------------------------------------------------------

@router.get("/voices")
async def list_voices():
    return {
        "success": True,
        "voices": get_available_voices(),
    }