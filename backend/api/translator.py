import io
import re

from fastapi import APIRouter, File, Form, UploadFile
from PIL import Image

from backend.services.ocr_service import extract_text_from_image
from backend.services.translation_service import (
    detect_language,
    translate_text,
)


router = APIRouter(
    prefix="/api",
    tags=["Translator"],
)


# ---------------------------------------------------------
# Numeric / price detection
# ---------------------------------------------------------

def is_numeric_or_price(text: str) -> bool:
    """
    Detect prices, numbers and numeric expressions.

    Examples:
        ₹250
        $20
        €15.50
        £100
        ¥500
        250
        25.50
        10%
        2/5
        10-20
        +91
        (250)
    """

    compact = text.replace(" ", "").strip()

    if not compact:
        return False

    allowed_chars = (
        "0123456789"
        "$€£¥₹"
        ".,:%/-+()"
    )

    # Every character must be numeric/currency/punctuation.
    if not all(ch in allowed_chars for ch in compact):
        return False

    # Must contain at least one digit.
    if not any(ch.isdigit() for ch in compact):
        return False

    return True


# ---------------------------------------------------------
# Detect likely OCR numeric errors
# ---------------------------------------------------------

def looks_like_numeric_ocr(text: str) -> bool:
    """
    Detect OCR results that are probably numbers/prices.

    This is slightly more relaxed than is_numeric_or_price()
    because OCR may produce unexpected characters.
    """

    compact = text.replace(" ", "").strip()

    if not compact:
        return False

    numeric_chars = (
        "0123456789"
        "$€£¥₹"
        ".,:%/-+()"
    )

    digit_count = sum(
        ch.isdigit()
        for ch in compact
    )

    allowed_count = sum(
        ch in numeric_chars
        for ch in compact
    )

    if digit_count == 0:
        return False

    ratio = allowed_count / len(compact)

    return ratio >= 0.60


# ---------------------------------------------------------
# Clean translated text
# ---------------------------------------------------------

def clean_translation(text: str) -> str:
    if not text:
        return ""

    text = str(text).strip()

    # Remove accidental whitespace around lines.
    text = re.sub(r"[ \t]+", " ", text)

    return text


# ---------------------------------------------------------
# Normal text translation
# ---------------------------------------------------------

@router.post("/translate")
async def translate(payload: dict):

    text = (payload.get("text") or "").strip()
    target = payload.get("target")

    if not target:
        return {
            "success": False,
            "error": "Please select a target language.",
        }

    if not text:
        return {
            "success": False,
            "error": "Please enter some text.",
        }

    try:

        source = detect_language(text)

        # Numbers/prices don't need translation.
        if is_numeric_or_price(text):
            translated = text

        else:
            translated = translate_text(
                text,
                target,
                source,
            )

        translated = clean_translation(translated)

        return {
            "success": True,
            "source_language": source,
            "target_language": target,
            "original_text": text,
            "translated_text": translated,
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e),
        }


# ---------------------------------------------------------
# Image translation
# ---------------------------------------------------------

@router.post("/image-translate")
async def image_translate(
    image: UploadFile = File(...),
    target: str = Form(...),
):

    try:

        # -------------------------------------------------
        # Validate target language
        # -------------------------------------------------

        if not target:

            return {
                "success": False,
                "error": "Please select a target language.",
            }

        # -------------------------------------------------
        # Read uploaded image
        # -------------------------------------------------

        data = await image.read()

        if not data:

            return {
                "success": False,
                "error": "The uploaded image is empty.",
            }

        # -------------------------------------------------
        # Open image
        # -------------------------------------------------

        img = Image.open(
            io.BytesIO(data)
        ).convert("RGB")

        original_width, original_height = img.size

        # -------------------------------------------------
        # OCR
        # -------------------------------------------------

        ocr_result = extract_text_from_image(img)

        text = (
            ocr_result.get("text") or ""
        ).strip()

        if not text:

            return {
                "success": False,
                "error": "No readable text was found in the image.",
                "ocr": ocr_result,
            }

        # -------------------------------------------------
        # Detect source language
        # -------------------------------------------------

        source = detect_language(text)

        # -------------------------------------------------
        # Translate every OCR item separately
        # -------------------------------------------------

        positioned_items = []

        for item in ocr_result.get("items", []):

            original = (
                item.get("text") or ""
            ).strip()

            if not original:
                continue

            confidence = float(
                item.get("confidence", 0.0)
            )

            # -------------------------------------------------
            # Numbers / prices
            # -------------------------------------------------

            if is_numeric_or_price(original):

                # IMPORTANT:
                # Never send prices/numbers to translator.
                translated = original

                content_type = "numeric"

            # -------------------------------------------------
            # Possible OCR numeric result
            # -------------------------------------------------

            elif looks_like_numeric_ocr(original):

                # Do NOT translate likely numeric OCR.
                # Keep exactly what OCR produced.
                translated = original

                content_type = "numeric"

            # -------------------------------------------------
            # Normal text
            # -------------------------------------------------

            else:

                try:

                    translated = translate_text(
                        original,
                        target,
                        source,
                    )

                except Exception:

                    # Mixed/short OCR text.
                    translated = translate_text(
                        original,
                        target,
                        "auto",
                    )

                content_type = "text"

            translated = clean_translation(
                translated
            )

            # -------------------------------------------------
            # Low confidence warning
            # -------------------------------------------------

            low_confidence = confidence < 0.65

            positioned_items.append({

                "text": original,

                "translated_text": translated,

                "confidence": confidence,

                "low_confidence": low_confidence,

                "content_type": content_type,

                "box": item["box"],

                "ocr_language": item.get(
                    "ocr_language"
                ),

            })

        # -------------------------------------------------
        # Full translated text
        # -------------------------------------------------

        translated_full = "\n".join(
            item["translated_text"]
            for item in positioned_items
        )

        # -------------------------------------------------
        # Return response
        # -------------------------------------------------

        return {

            "success": True,

            "source_language": source,

            "target_language": target,

            "original_text": text,

            "translated_text": translated_full,

            "ocr": ocr_result,

            "positioned_items": positioned_items,

            "image": {
                "width": original_width,
                "height": original_height,
            },

        }

    except Exception as e:

        return {

            "success": False,

            "error": f"Image processing failed: {e}",

        }