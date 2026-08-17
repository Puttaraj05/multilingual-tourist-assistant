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


def detect_language(text: str) -> str:
    try:
        code = detect(text)
        return code
    except Exception:
        return "auto"


def translate_text(text: str, target: str, source: str = "auto") -> str:
    if not text.strip():
        return ""

    if source == target:
        return text

    # GoogleTranslator accepts "auto" for source language.
    return GoogleTranslator(source=source or "auto", target=target).translate(text)
