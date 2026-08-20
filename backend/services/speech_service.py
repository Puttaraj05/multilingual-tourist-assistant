# Speech recognition and text-to-speech services for TravelMate.

import io
import os
import tempfile

import edge_tts
from faster_whisper import WhisperModel


# Configure the Whisper model for speech recognition.

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


# Keep one shared Whisper model instance so it does not need to be loaded for every request.

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


# Map supported language codes to their Edge-TTS voices.

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


# Convert different language formats into the codes used by the speech services.

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


    # Return the language code directly when it is already supported.

    if language in VOICE_MAP:
        return language


    # Normalize browser and frontend language values.

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


    # Handle values such as "en-US" by using the base language code.

    base_language = (
        language_lower
        .split("-")[0]
        .split("_")[0]
    )


    if base_language in VOICE_MAP:

        return base_language


    return language


# Convert uploaded speech audio into text using faster-whisper.

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


    # Normalize the requested language before sending it to Whisper.

    whisper_language = normalize_language(
        language
    )


    # Save the browser audio temporarily so Whisper can process the file.

    # Browser MediaRecorder normally creates WebM.
    # Do NOT save WebM bytes using a .wav extension.

    with tempfile.NamedTemporaryFile(
        suffix=".webm",
        delete=False,
    ) as tmp:

        tmp.write(audio_bytes)

        tmp_path = tmp.name


    try:

        # Transcribe the temporary audio file with Whisper.

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


        # Collect the text returned by each transcription segment.

        text_parts = []

        total_confidence = 0.0

        confidence_count = 0


        for segment in segments:

            text = (
                segment.text or ""
            ).strip()


            if text:

                text_parts.append(text)


            # Convert avg_logprob into rough 0-1 confidence.
            # This is NOT a calibrated probability.

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


        # Combine all transcription segments into the final text.

        full_text = " ".join(
            text_parts
        ).strip()


        # Calculate the average confidence across the transcription segments.

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

        # Remove the temporary audio file after transcription is complete.

        try:

            os.unlink(tmp_path)

        except OSError:

            pass


# Convert text into MP3 speech using Edge-TTS.

async def text_to_speech(
    text: str,
    language: str = "en",
) -> bytes:
    """
    Convert translated text into MP3 speech using Edge-TTS.
    """

    if not text or not text.strip():

        return b""


    # Normalize the language before selecting the voice.

    normalized_language = (
        normalize_language(language)
        or "en"
    )


    # Select the voice for the requested language.

    voice = VOICE_MAP.get(
        normalized_language,
        DEFAULT_VOICE,
    )


    print(
        f"Generating TTS: "
        f"language={normalized_language}, "
        f"voice={voice}"
    )


    # Generate speech using the selected Edge-TTS voice.

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


# Return the language-to-voice mapping supported by TravelMate.

def get_available_voices() -> dict:
    """
    Return language -> Edge-TTS voice mapping.
    """

    return VOICE_MAP.copy()