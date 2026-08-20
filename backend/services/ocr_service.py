import re

import cv2
import easyocr
import numpy as np


# Languages supported by the OCR readers.
READER_LANGS = [
    "en",
    "hi",
    "te",
    "kn",
    "mr",
    "bn",
    "ar",
]

_readers = {}


# Unicode ranges used to identify the detected script.
SCRIPT_RANGES = {
    "en": [
        (0x0041, 0x024F),
        (0x1E00, 0x1EFF),
    ],
    "hi": [(0x0900, 0x097F)],
    "mr": [(0x0900, 0x097F)],
    "te": [(0x0C00, 0x0C7F)],
    "ta": [(0x0B80, 0x0BFF)],
    "kn": [(0x0C80, 0x0CFF)],
    "bn": [(0x0980, 0x09FF)],
    "ar": [(0x0600, 0x06FF)],
    "ja": [(0x3040, 0x30FF), (0x4E00, 0x9FFF)],
    "ko": [(0xAC00, 0xD7AF)],
    "ch_sim": [(0x4E00, 0x9FFF)],
    "ru": [(0x0400, 0x04FF)],
    "fr": [(0x0041, 0x024F)],
    "de": [(0x0041, 0x024F)],
    "es": [(0x0041, 0x024F)],
    "it": [(0x0041, 0x024F)],
}


# Create and reuse an OCR reader for each language.
def get_reader(lang):
    """
    Create and cache one EasyOCR reader per language.
    """
    if lang not in READER_LANGS:
        lang = "en"

    if lang not in _readers:
        if lang == "en":
            langs = ["en"]
        elif lang == "ch_sim":
            langs = ["ch_sim", "en"]
        else:
            langs = [lang, "en"]

        print(f"Loading EasyOCR reader: {langs}")
        _readers[lang] = easyocr.Reader(langs, gpu=False)

    return _readers[lang]


# Improve the image before passing it to EasyOCR.
def preprocess(image):
    arr = np.array(image)
    bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)

    h, w = bgr.shape[:2]

    if max(h, w) < 1600:
        scale = 1600 / max(h, w)
        bgr = cv2.resize(
            bgr,
            None,
            fx=scale,
            fy=scale,
            interpolation=cv2.INTER_CUBIC,
        )

    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l)

    enhanced = cv2.cvtColor(cv2.merge((l, a, b)), cv2.COLOR_LAB2BGR)
    return enhanced


# Convert OCR box coordinates into integer values.
def clean_box(box):
    return [[int(point[0]), int(point[1])] for point in box]


# Create a simplified key for comparing OCR boxes.
def _box_key(box):
    xs = [round(float(point[0]) / 12) for point in box]
    ys = [round(float(point[1]) / 12) for point in box]
    return tuple(xs + ys)


# Check whether a character belongs to a script range.
def _in_ranges(char, ranges):
    code = ord(char)
    return any(start <= code <= end for start, end in ranges)


# Calculate how much of the text matches the expected script.
def script_match_ratio(text, lang):
    chars = [c for c in text if c.isalpha()]
    if not chars:
        return 0.0

    ranges = SCRIPT_RANGES.get(lang, SCRIPT_RANGES["en"])
    matched = sum(_in_ranges(c, ranges) for c in chars)
    return matched / len(chars)


# Calculate the percentage of alphabetic characters that are Latin.
def latin_ratio(text):
    chars = [c for c in text if c.isalpha()]
    if not chars:
        return 0.0
    return sum(("A" <= c <= "Z") or ("a" <= c <= "z") for c in chars) / len(chars)


# Remove unnecessary spaces from OCR output.
def clean_text(text):
    text = str(text).strip()
    text = re.sub(r"[ \t]+", " ", text)
    return text


# Normalize text before comparing OCR results.
def normalize_text(text):
    return re.sub(
        r"[^0-9A-Za-z"
        r"\u0900-\u097F"   # Devanagari
        r"\u0980-\u09FF"   # Bengali
        r"\u0B80-\u0BFF"   # Tamil
        r"\u0C00-\u0C7F"   # Telugu
        r"\u0C80-\u0CFF"   # Kannada
        r"\u0600-\u06FF"   # Arabic
        r"\u0400-\u04FF"   # Cyrillic
        r"\u3040-\u30FF"   # Japanese
        r"\u4E00-\u9FFF"   # CJK
        r"\uAC00-\uD7AF"   # Korean
        r"]+",
        "",
        text,
    ).lower()


# Characters commonly found in prices and numeric values.
NUMERIC_CHARS = "0123456789$€£¥₹.,:%/-+()"


# Check whether OCR output mainly contains numeric characters.
def is_numeric_text(text):
    compact = text.replace(" ", "").strip()
    if not compact:
        return False
    if not any(ch.isdigit() for ch in compact):
        return False

    allowed = sum(ch in NUMERIC_CHARS for ch in compact)
    return (allowed / len(compact)) >= 0.60


# Check whether the text contains a supported currency symbol.
def contains_currency_symbol(text):
    return any(symbol in text for symbol in ["₹", "$", "€", "£", "¥"])


# Calculate how much of the text contains numeric characters.
def numeric_ratio(text):
    compact = text.replace(" ", "").strip()
    if not compact:
        return 0.0
    return sum(ch in NUMERIC_CHARS for ch in compact) / len(compact)


# Remove duplicate OCR results while keeping the higher-confidence result.
def deduplicate_items(items):
    unique = {}
    for item in items:
        text_key = normalize_text(item["text"])
        key = (_box_key(item["box"]), text_key)

        if key not in unique or item["confidence"] > unique[key]["confidence"]:
            unique[key] = item

    return list(unique.values())


# Score OCR results using confidence, script matching, and text length.
def score_result(items, lang):
    if not items:
        return -1.0

    text = " ".join(item["text"] for item in items).strip()
    if not text:
        return -1.0

    avg_conf = sum(item["confidence"] for item in items) / len(items)
    chars = [c for c in text if c.isalpha()]
    char_count = len(chars)

    if lang in ["en", "fr", "de", "es", "it"]:
        script_ratio = latin_ratio(text)
    else:
        script_ratio = script_match_ratio(text, lang)

    length_bonus = min(char_count / 80.0, 1.0)

    score = (0.55 * avg_conf) + (0.35 * script_ratio) + (0.10 * length_bonus)

    if lang not in ["en", "fr", "de", "es", "it"] and script_ratio < 0.35:
        score -= 0.35

    return score


# Run a second OCR pass to improve recognition of prices and symbols.
def refine_numeric_text(reader, image, box):
    """
    Stronger second-pass OCR for prices.
    Helps fix cases like ₹250 → 2250
    """
    try:
        points = np.array(box, dtype=np.float32)

        x_min = max(0, int(points[:, 0].min()) - 35)
        y_min = max(0, int(points[:, 1].min()) - 35)
        x_max = min(image.shape[1], int(points[:, 0].max()) + 35)
        y_max = min(image.shape[0], int(points[:, 1].max()) + 35)

        if x_max <= x_min or y_max <= y_min:
            return None

        crop = image[y_min:y_max, x_min:x_max]
        if crop.size == 0:
            return None

        # Upscale the crop to improve recognition of small symbols.
        crop = cv2.resize(crop, None, fx=4.0, fy=4.0, interpolation=cv2.INTER_CUBIC)

        allowlist = "0123456789₹$€£¥.,:%/-+() "

        candidates = []

        def run_ocr(img):
            return reader.readtext(
                img,
                detail=1,
                paragraph=False,
                allowlist=allowlist,
                text_threshold=0.30,
                low_text=0.20,
                link_threshold=0.20,
            )

        # Try several image versions to improve price recognition.
        results = run_ocr(crop)

        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        results += run_ocr(gray)

        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        results += run_ocr(thresh)

        inverted = cv2.bitwise_not(thresh)
        results += run_ocr(inverted)

        for _, text, confidence in results:
            text = clean_text(text).replace(" ", "")
            if not text:
                continue

            cleaned = "".join(
                ch for ch in text
                if ch.isdigit() or ch in "₹$€£¥.,:%/-+()"
            )

            if not cleaned or not any(c.isdigit() for c in cleaned):
                continue

            score = float(confidence)

            # Give preference to results that correctly detect currency.
            if contains_currency_symbol(cleaned):
                score += 0.40

            if 2 <= len(cleaned) <= 7:
                score += 0.10

            candidates.append((cleaned, score))

        if not candidates:
            return None

        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[0][0]

    except Exception as exc:
        print("Numeric OCR refinement failed:", exc)
        return None


# Extract text, language, confidence, and bounding boxes from an image.
def extract_text_from_image(image):
    processed = preprocess(image)
    processed_height, processed_width = processed.shape[:2]

    candidates = []

    for lang in READER_LANGS:
        try:
            reader = get_reader(lang)

            results = reader.readtext(
                processed,
                detail=1,
                paragraph=False,
                text_threshold=0.6,
                low_text=0.3,
                link_threshold=0.3,
            )

            items = []

            for box, text, confidence in results:
                text = clean_text(text)
                if not text:
                    continue

                confidence = float(confidence)
                cleaned_box = clean_box(box)

                is_numeric_region = is_numeric_text(text) and confidence < 0.92
                final_text = text

                if is_numeric_region:
                    refined = refine_numeric_text(reader, processed, cleaned_box)

                    if refined:
                        has_currency_original = contains_currency_symbol(final_text)
                        has_currency_refined = contains_currency_symbol(refined)

                        # Prefer the refined result when it identifies currency correctly.
                        if has_currency_refined and not has_currency_original:
                            print(f"Currency fixed: '{final_text}' → '{refined}'")
                            final_text = refined

                        elif has_currency_refined and has_currency_original:
                            if len(refined) <= len(final_text) + 2:
                                final_text = refined

                        elif confidence < 0.55 and len(refined) <= len(final_text) + 2:
                            final_text = refined

                items.append({
                    "text": final_text,
                    "confidence": confidence,
                    "box": cleaned_box,
                    "ocr_language": lang,
                    "is_numeric": is_numeric_text(final_text),
                    "has_currency": contains_currency_symbol(final_text),
                })

            items = deduplicate_items(items)
            score = score_result(items, lang)

            if items:
                candidates.append({
                    "language": lang,
                    "score": score,
                    "items": items,
                })

        except Exception as exp:
            print(f"OCR skipped {lang}: {exp}")

    if not candidates:
        return {
            "text": "",
            "items": [],
            "ocr_language": None,
            "ocr_score": 0.0,
            "processed_width": processed_width,
            "processed_height": processed_height,
        }

    best = max(candidates, key=lambda x: x["score"])
    items = best["items"]

    # Sort detected text into a natural reading order.
    items.sort(
        key=lambda x: (
            min(point[1] for point in x["box"]),
            min(point[0] for point in x["box"]),
        )
    )

    text = "\n".join(item["text"] for item in items)

    return {
        "text": text,
        "items": items,
        "ocr_language": best["language"],
        "ocr_score": round(float(best["score"]), 4),
        "processed_width": processed_width,
        "processed_height": processed_height,
    }