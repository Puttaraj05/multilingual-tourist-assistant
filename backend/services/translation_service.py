from deep_translator import GoogleTranslator
from langdetect import detect, DetectorFactory

DetectorFactory.seed = 0


LANGUAGES = {
    "auto": "Auto Detect",
    "en": "English",
    "hi": "Hindi",
    "te": "Telugu",
    "ta": "Tamil",
    "kn": "Kannada",
    "ml": "Malayalam",
    "bn": "Bengali",
    "mr": "Marathi",
    "gu": "Gujarati",
    "pa": "Punjabi",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "ja": "Japanese",
    "ko": "Korean",
    "ar": "Arabic",
    "zh-CN": "Chinese",
    "ru": "Russian",
}


# Name -> Google Translate code
LANGUAGE_CODES = {
    "Auto Detect": "auto",
    "English": "en",
    "Hindi": "hi",
    "Telugu": "te",
    "Tamil": "ta",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Bengali": "bn",
    "Marathi": "mr",
    "Gujarati": "gu",
    "Punjabi": "pa",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Italian": "it",
    "Japanese": "ja",
    "Korean": "ko",
    "Arabic": "ar",
    "Chinese": "zh-CN",
    "Russian": "ru",
}


def normalize_language(language: str) -> str:

    if not language:
        return "auto"

    language = language.strip()

    # Already a language code
    if language in LANGUAGE_CODES.values():
        return language

    # Language name
    return LANGUAGE_CODES.get(
        language,
        "auto"
    )


def detect_language(text: str) -> str:

    try:

        code = detect(text)

        return code

    except Exception:

        return "auto"


def translate_text(
    text: str,
    target: str,
    source: str = "auto"
) -> str:

    if not text or not text.strip():
        return ""

    target_code = normalize_language(target)
    source_code = normalize_language(source)

    # Same language
    if (
        source_code != "auto"
        and source_code == target_code
    ):
        return text

    return GoogleTranslator(
        source=source_code,
        target=target_code
    ).translate(text)