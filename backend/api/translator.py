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


# Detect prices, numbers, and numeric expressions.

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

    # Check that all characters are numeric or allowed symbols.
    if not all(ch in allowed_chars for ch in compact):
        return False

    # Require at least one digit in the value.
    if not any(ch.isdigit() for ch in compact):
        return False

    return True


# Detect OCR results that may contain numeric values.

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


# Clean extra whitespace from translated text.

def clean_translation(text: str) -> str:
    if not text:
        return ""

    text = str(text).strip()

    # Remove unnecessary whitespace around lines.
    text = re.sub(r"[ \t]+", " ", text)

    return text


# Translate normal text.

@router.post("/translate")
async def translate(payload: dict):

    text = (payload.get("text") or "").strip()
    source = (payload.get("source") or "auto").strip()
    target = (payload.get("target") or "").strip()

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

        # Detect the source language when Auto Detect is selected.

        if source.lower() in ["auto", "auto detect"]:
            detected_source = detect_language(text)
        else:
            detected_source = source

        # Keep numbers and prices unchanged.

        if is_numeric_or_price(text):

            translated = text

        else:

            translated = translate_text(
                text,
                target,
                detected_source,
            )

        translated = clean_translation(
            translated
        )

        return {

            "success": True,

            "source_language": detected_source,

            "target_language": target,

            "original_text": text,

            "translated_text": translated,

        }

    except Exception as e:

        print(
            f"Translation error: {e}",
            flush=True,
        )

        return {

            "success": False,

            "error": str(e),

        }


# Translate text extracted from an image.

@router.post("/image-translate")
async def image_translate(
    image: UploadFile = File(...),
    target: str = Form(...),
):

    try:

        # Validate the selected target language.

        if not target:

            return {
                "success": False,
                "error": "Please select a target language.",
            }

        # Read the uploaded image.

        data = await image.read()

        if not data:

            return {
                "success": False,
                "error": "The uploaded image is empty.",
            }

        # Convert the uploaded image to RGB format.

        img = Image.open(
            io.BytesIO(data)
        ).convert("RGB")

        original_width, original_height = img.size

        # Extract text and its positions using OCR.

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

        # Detect the language of the extracted text.

        source = detect_language(text)

        # Translate each detected text region separately.

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

            # Keep detected numbers and prices unchanged.

            if is_numeric_or_price(original):

                # Never send prices or numbers to the translator.
                translated = original

                content_type = "numeric"

            # Keep likely numeric OCR results unchanged.

            elif looks_like_numeric_ocr(original):

                # Preserve the OCR result without translation.
                translated = original

                content_type = "numeric"

            # Translate normal text.

            else:

                try:

                    translated = translate_text(
                        original,
                        target,
                        source,
                    )

                except Exception:

                    # Retry with automatic language detection.
                    translated = translate_text(
                        original,
                        target,
                        "auto",
                    )

                content_type = "text"

            translated = clean_translation(
                translated
            )

            # Mark OCR results with low confidence.

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

        # Combine translated OCR regions into one text block.

        translated_full = "\n".join(
            item["translated_text"]
            for item in positioned_items
        )

        # Return the translation and OCR details.

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