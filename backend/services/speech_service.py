# Speech recognition and text-to-speech services for TravelMate.

import io
import os
import tempfile

import edge_tts


# Whisper configuration.

WHISPER_MODEL_SIZE = "base"
WHISPER_DEVICE = "cpu"
WHISPER_COMPUTE_TYPE = "int8"


# Whisper is loaded only when speech recognition is actually used.
_whisper_model = None


def get_whisper_model():
    """
    Load Whisper only when speech recognition is requested.

    The first speech request takes longer because the model
    needs to be loaded. Later requests reuse the same model.
    """

    global _whisper_model

    if _whisper_model is None:

        # Lazy import keeps the heavy Whisper dependencies
        # out of the application's startup path.
        from faster_whisper import WhisperModel

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


# Language codes and their corresponding Edge-TTS voices.

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


def normalize_language(
    language: str | None
) -> str | None:
    """
    Normalize language values from the frontend or backend.

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

    # Return the code directly when it is already supported.
    if language in VOICE_MAP:
        return language

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

    # Handle values such as en-US or te-IN.
    base_language = (
        language_lower
        .split("-")[0]
        .split("_")[0]
    )

    if base_language in VOICE_MAP:
        return base_language

    return language


def speech_to_text(
    audio_bytes: bytes,
    language: str | None = None,
) -> dict:
    """
    Convert uploaded audio into text using faster-whisper.

    Whisper is loaded only when this function is called.

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

    # Load Whisper only when speech recognition is requested.
    model = get_whisper_model()

    # Normalize the requested language before sending it to Whisper.
    whisper_language = normalize_language(language)

    # Save the browser audio temporarily so Whisper can process it.
    # Browser MediaRecorder normally creates WebM.
    # Do not save WebM bytes using a .wav extension.

    with tempfile.NamedTemporaryFile(
        suffix=".webm",
        delete=False,
    ) as tmp:

        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:

        # Transcribe the temporary audio file.
        segments, info = model.transcribe(
            tmp_path,
            language=whisper_language,
            beam_size=3,
            vad_filter=True,
            condition_on_previous_text=False,
        )

        text_parts = []

        total_confidence = 0.0
        confidence_count = 0

        for segment in segments:

            text = (
                segment.text or ""
            ).strip()

            if text:
                text_parts.append(text)

            # Convert avg_logprob into a rough 0-1 confidence.
            # This is not a calibrated probability.

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

        # Combine all transcription segments.
        full_text = " ".join(
            text_parts
        ).strip()

        # Calculate average confidence.
        if confidence_count > 0:

            avg_confidence = (
                total_confidence /
                confidence_count
            )

        else:

            avg_confidence = 0.0

        # Get the language detected by Whisper.
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

        # Remove the temporary audio file.
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


async def text_to_speech(
    text: str,
    language: str = "en",
) -> bytes:
    """
    Convert translated text into MP3 speech using Edge-TTS.
    """

    if not text or not text.strip():
        return b""

    # Normalize the requested language.
    normalized_language = (
        normalize_language(language)
        or "en"
    )

    # Select the appropriate Edge-TTS voice.
    voice = VOICE_MAP.get(
        normalized_language,
        DEFAULT_VOICE,
    )

    print(
        f"Generating TTS: "
        f"language={normalized_language}, "
        f"voice={voice}"
    )

    # Generate speech using Edge-TTS.
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

    audio_data = audio_buffer.getvalue()

    print(
        f"TTS generated: "
        f"{len(audio_data)} bytes"
    )

    return audio_data


def get_available_voices() -> dict:
    """
    Return the language-to-voice mapping supported by TravelMate.
    """

    return VOICE_MAP.copy()