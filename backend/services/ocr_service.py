import re
import numpy as np
import cv2
import easyocr

# EasyOCR language models must be loaded in compatible combinations.
# We run one reader at a time and choose the best result instead of
# combining several OCR models (which caused duplicate/misread text).
READER_LANGS = ["en", "hi", "te", "ta", "kn", "mr"]
_readers = {}

# Unicode ranges used to judge whether an OCR result matches its
# intended script. This helps prevent an English image from being
# polluted by Hindi/Telugu/Tamil OCR guesses.
SCRIPT_RANGES = {
    "en": [(0x0041, 0x024F), (0x1E00, 0x1EFF)],
    "hi": [(0x0900, 0x097F)],   # Devanagari
    "mr": [(0x0900, 0x097F)],   # Devanagari
    "te": [(0x0C00, 0x0C7F)],
    "ta": [(0x0B80, 0x0BFF)],
    "kn": [(0x0C80, 0x0CFF)],
}


def get_reader(lang):
    if lang not in READER_LANGS:
        lang = "en"

    if lang not in _readers:
        langs = ["en"] if lang == "en" else [lang, "en"]
        _readers[lang] = easyocr.Reader(langs, gpu=False)

    return _readers[lang]


def preprocess(image):
    arr = np.array(image)
    bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)

    h, w = bgr.shape[:2]

    # Upscale smaller images for better OCR.
    if max(h, w) < 1600:
        scale = 1600 / max(h, w)
        bgr = cv2.resize(
            bgr,
            None,
            fx=scale,
            fy=scale,
            interpolation=cv2.INTER_CUBIC,
        )

    # Improve local contrast.
    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    enhanced = cv2.cvtColor(cv2.merge((l, a, b)), cv2.COLOR_LAB2BGR)

    return enhanced


def clean_box(box):
    # Convert NumPy numeric types into normal Python ints so FastAPI
    # can serialize the response to JSON.
    return [
        [int(point[0]), int(point[1])]
        for point in box
    ]


def _box_key(box):
    # Coarse spatial key for duplicate filtering.
    xs = [round(float(p[0]) / 12) for p in box]
    ys = [round(float(p[1]) / 12) for p in box]
    return tuple(xs + ys)


def _in_ranges(char, ranges):
    code = ord(char)
    return any(start <= code <= end for start, end in ranges)


def script_match_ratio(text, lang):
    chars = [c for c in text if c.isalpha()]
    if not chars:
        return 0.0

    ranges = SCRIPT_RANGES.get(lang, SCRIPT_RANGES["en"])
    matched = sum(_in_ranges(c, ranges) for c in chars)
    return matched / len(chars)


def latin_ratio(text):
    chars = [c for c in text if c.isalpha()]
    if not chars:
        return 0.0
    return sum(("A" <= c <= "Z") or ("a" <= c <= "z") for c in chars) / len(chars)


def clean_text(text):
    text = str(text).strip()
    text = re.sub(r"[ \t]+", " ", text)
    return text


def normalize_text(text):
    return re.sub(r"[^0-9A-Za-z\u0900-\u097F\u0B80-\u0BFF\u0C00-\u0C7F\u0C80-\u0CFF]+", "", text).lower()


def deduplicate_items(items):
    unique = {}

    for item in items:
        text_key = normalize_text(item["text"])
        key = (_box_key(item["box"]), text_key)

        if key not in unique or item["confidence"] > unique[key]["confidence"]:
            unique[key] = item

    return list(unique.values())


def score_result(items, lang):
    if not items:
        return -1.0

    text = " ".join(item["text"] for item in items).strip()
    if not text:
        return -1.0

    avg_conf = sum(item["confidence"] for item in items) / len(items)
    chars = [c for c in text if c.isalpha()]
    char_count = len(chars)

    if lang == "en":
        script_ratio = latin_ratio(text)
    else:
        script_ratio = script_match_ratio(text, lang)

    # Strongly prefer OCR results written in the expected script.
    # Confidence and amount of readable text provide secondary signals.
    length_bonus = min(char_count / 80.0, 1.0)

    score = (
        0.55 * avg_conf
        + 0.35 * script_ratio
        + 0.10 * length_bonus
    )

    # Penalize very low script matches for non-English readers.
    if lang != "en" and script_ratio < 0.35:
        score -= 0.35

    return score


def extract_text_from_image(image):
    processed = preprocess(image)
    processed_height, processed_width = processed.shape[:2]

    candidates = []

    # Run compatible readers independently.
    # IMPORTANT: we do not merge all languages together.
    for lang in READER_LANGS:
        try:
            reader = get_reader(lang)
            results = reader.readtext(
                processed,
                detail=1,
                paragraph=False,
            )

            items = []

            for box, text, confidence in results:
                text = clean_text(text)

                if not text:
                    continue

                items.append({
                    "text": text,
                    "confidence": float(confidence),
                    "box": clean_box(box),
                    "ocr_language": lang,
                })

            items = deduplicate_items(items)
            score = score_result(items, lang)

            if items:
                candidates.append({
                    "language": lang,
                    "score": score,
                    "items": items,
                })

        except Exception as exc:
            # A broken/cached model for one language must not stop the
            # other OCR models from working.
            print(f"OCR skipped {lang}: {exc}")

    if not candidates:
        return {
            "text": "",
            "items": [],
            "ocr_language": None,
            "ocr_score": 0.0,
            "processed_width": processed_width,
            "processed_height": processed_height,
        }

    # Choose ONE best OCR result instead of mixing multiple model guesses.
    best = max(candidates, key=lambda x: x["score"])

    items = best["items"]

    # Read in natural top-to-bottom / left-to-right order.
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
