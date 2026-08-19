# backend/services/speech_service.py

import io
import os
import tempfile

import edge_tts
from faster_whisper import WhisperModel


# =========================================================
# CONFIGURATION
# =========================================================

# Options:
# tiny  -> fastest
# base  -> better accuracy, slower
# small -> better accuracy, slower
#
# For your Mac/hackathon demo, "base" is a good balance.
WHISPER_MODEL_SIZE = "base"

# CPU is safest for Mac compatibility.
WHISPER_DEVICE = "cpu"

# int8 gives good CPU performance.
WHISPER_COMPUTE_TYPE = "int8"


# =========================================================
# GLOBAL WHISPER MODEL
# =========================================================

_whisper_model = None


def get_whisper_model():
    """
    Load Whisper only once.

    The first speech request will take longer because
    the model needs to be loaded. Subsequent requests
    reuse the same model.
    """

    global _whisper_model

    if _whisper_model is None:

        print(
            f"Loading Whisper model: "
            f"{WHISPER_MODEL_SIZE} ..."
        )

        _whisper_model = WhisperModel(
            WHISPER_MODEL_SIZE,
            device=WHISPER_DEVICE,
            compute_type=WHISPER_COMPUTE_TYPE,
        )

        print("Whisper model loaded successfully.")

    return _whisper_model


# =========================================================
# EDGE-TTS VOICES
# =========================================================

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


# =========================================================
# LANGUAGE NORMALIZATION
# =========================================================

def normalize_language(language: str | None) -> str | None:
    """
    Normalize language values coming from frontend/backend.

    Examples:

        English -> en
        Hindi -> hi
        Telugu -> te
        en-US -> en
        zh -> zh-CN
        auto -> None
    """

    if not language:
        return None

    language = language.strip()

    if not language:
        return None

    if language.lower() == "auto":
        return None


    # Already supported language code

    if language in VOICE_MAP:
        return language


    # Browser / Whisper style codes

    language_lower = language.lower()


    aliases = {

        "english": "en",
        "en-us": "en",
        "en-gb": "en",

        "hindi": "hi",
        "hi-in": "hi",

        "telugu": "te",
        "te-in": "te",

        "tamil": "ta",
        "ta-in": "ta",

        "kannada": "kn",
        "kn-in": "kn",

        "malayalam": "ml",
        "ml-in": "ml",

        "bengali": "bn",
        "bn-in": "bn",

        "marathi": "mr",
        "mr-in": "mr",

        "gujarati": "gu",
        "gu-in": "gu",

        "punjabi": "pa",
        "pa-in": "pa",

        "spanish": "es",
        "es-es": "es",

        "french": "fr",
        "fr-fr": "fr",

        "german": "de",
        "de-de": "de",

        "italian": "it",
        "it-it": "it",

        "japanese": "ja",
        "ja-jp": "ja",

        "korean": "ko",
        "ko-kr": "ko",

        "arabic": "ar",
        "ar-sa": "ar",

        "chinese": "zh-CN",
        "zh": "zh-CN",
        "zh-cn": "zh-CN",

        "russian": "ru",
        "ru-ru": "ru",

    }


    if language_lower in aliases:

        return aliases[language_lower]


    # Handle values such as "en-US"

    base_language = (
        language_lower
        .split("-")[0]
        .split("_")[0]
    )


    if base_language in VOICE_MAP:

        return base_language


    return language


# =========================================================
# SPEECH → TEXT
# =========================================================

def speech_to_text(
    audio_bytes: bytes,
    language: str | None = None,
) -> dict:
    """
    Convert uploaded audio into text using faster-whisper.

    Expected browser audio:
        WebM / Opus

    Returns:

        {
            "text": "...",
            "language": "en",
            "confidence": 0.85
        }
    """

    if not audio_bytes:

        return {
            "text": "",
            "language": None,
            "confidence": 0.0,
        }


    model = get_whisper_model()


    # -----------------------------------------------------
    # Normalize requested language
    # -----------------------------------------------------

    whisper_language = normalize_language(
        language
    )


    # -----------------------------------------------------
    # Save browser audio temporarily
    #
    # IMPORTANT:
    # Browser MediaRecorder normally creates WebM.
    # Do NOT save WebM bytes using a .wav extension.
    # -----------------------------------------------------

    with tempfile.NamedTemporaryFile(
        suffix=".webm",
        delete=False,
    ) as tmp:

        tmp.write(audio_bytes)

        tmp_path = tmp.name


    try:

        # -------------------------------------------------
        # Whisper transcription
        # -------------------------------------------------

        segments, info = model.transcribe(

            tmp_path,

            language=whisper_language,

            # Lower than 5 for better speed.
            beam_size=3,

            # Ignore silent sections.
            vad_filter=True,

            # Helps avoid repetitive context processing.
            condition_on_previous_text=False,

        )


        # -------------------------------------------------
        # Collect segments
        # -------------------------------------------------

        text_parts = []

        total_confidence = 0.0

        confidence_count = 0


        for segment in segments:

            text = (
                segment.text or ""
            ).strip()


            if text:

                text_parts.append(text)


            # -------------------------------------------------
            # Convert avg_logprob into rough 0-1 confidence.
            # This is NOT a calibrated probability.
            # -------------------------------------------------

            if segment.avg_logprob is not None:

                confidence = max(
                    0.0,
                    min(
                        1.0,
                        segment.avg_logprob + 1.0,
                    ),
                )

                total_confidence += confidence

                confidence_count += 1


        # -------------------------------------------------
        # Final text
        # -------------------------------------------------

        full_text = " ".join(
            text_parts
        ).strip()


        # -------------------------------------------------
        # Average confidence
        # -------------------------------------------------

        if confidence_count > 0:

            avg_confidence = (
                total_confidence /
                confidence_count
            )

        else:

            avg_confidence = 0.0


        # -------------------------------------------------
        # Detected language
        # -------------------------------------------------

        detected_language = (
            info.language
            if info and info.language
            else "en"
        )


        detected_language = normalize_language(
            detected_language
        ) or "en"


        return {

            "text": full_text,

            "language": detected_language,

            "confidence": round(
                avg_confidence,
                3,
            ),

        }


    finally:

        # -------------------------------------------------
        # Remove temporary file
        # -------------------------------------------------

        try:

            os.unlink(tmp_path)

        except OSError:

            pass


# =========================================================
# TEXT → SPEECH
# =========================================================

async def text_to_speech(
    text: str,
    language: str = "en",
) -> bytes:
    """
    Convert translated text into MP3 speech using Edge-TTS.
    """

    if not text or not text.strip():

        return b""


    # -----------------------------------------------------
    # Normalize language
    # -----------------------------------------------------

    normalized_language = (
        normalize_language(language)
        or "en"
    )


    # -----------------------------------------------------
    # Find voice
    # -----------------------------------------------------

    voice = VOICE_MAP.get(
        normalized_language,
        DEFAULT_VOICE,
    )


    print(
        f"Generating TTS: "
        f"language={normalized_language}, "
        f"voice={voice}"
    )


    # -----------------------------------------------------
    # Edge TTS
    # -----------------------------------------------------

    communicate = edge_tts.Communicate(
        text=text.strip(),
        voice=voice,
    )


    audio_buffer = io.BytesIO()


    async for chunk in communicate.stream():

        if chunk["type"] == "audio":

            audio_buffer.write(
                chunk["data"]
            )


    audio_data = (
        audio_buffer.getvalue()
    )


    print(
        f"TTS generated: "
        f"{len(audio_data)} bytes"
    )


    return audio_data


# =========================================================
# AVAILABLE VOICES
# =========================================================

def get_available_voices() -> dict:
    """
    Return language -> Edge-TTS voice mapping.
    """

    return VOICE_MAP.copy()