import re

import cv2
import easyocr
import numpy as np


# =========================================================
# OCR LANGUAGES
# =========================================================

# Do not include Tamil for now because your installed/cached
# Tamil EasyOCR model is incompatible with the current model.
#
# Tamil can still be used as a TRANSLATION target.
READER_LANGS = [
    "en",
    "hi",
    "te",
    "kn",
    "mr",
]

_readers = {}


# =========================================================
# SCRIPT RANGES
# =========================================================

SCRIPT_RANGES = {
    "en": [
        (0x0041, 0x024F),
        (0x1E00, 0x1EFF),
    ],

    "hi": [
        (0x0900, 0x097F),
    ],

    "mr": [
        (0x0900, 0x097F),
    ],

    "te": [
        (0x0C00, 0x0C7F),
    ],

    "ta": [
        (0x0B80, 0x0BFF),
    ],

    "kn": [
        (0x0C80, 0x0CFF),
    ],
}


# =========================================================
# READER
# =========================================================

def get_reader(lang):
    """
    Create and cache one EasyOCR reader per language.
    """

    if lang not in READER_LANGS:
        lang = "en"

    if lang not in _readers:

        if lang == "en":
            langs = ["en"]

        else:
            langs = [lang, "en"]

        print(
            f"Loading EasyOCR reader: {langs}"
        )

        _readers[lang] = easyocr.Reader(
            langs,
            gpu=False,
        )

    return _readers[lang]


# =========================================================
# IMAGE PREPROCESSING
# =========================================================

def preprocess(image):
    """
    Prepare image for OCR.
    """

    arr = np.array(image)

    bgr = cv2.cvtColor(
        arr,
        cv2.COLOR_RGB2BGR,
    )

    h, w = bgr.shape[:2]

    # -----------------------------------------------------
    # Upscale smaller images
    # -----------------------------------------------------

    if max(h, w) < 1600:

        scale = 1600 / max(h, w)

        bgr = cv2.resize(
            bgr,
            None,
            fx=scale,
            fy=scale,
            interpolation=cv2.INTER_CUBIC,
        )

    # -----------------------------------------------------
    # Improve local contrast
    # -----------------------------------------------------

    lab = cv2.cvtColor(
        bgr,
        cv2.COLOR_BGR2LAB,
    )

    l, a, b = cv2.split(lab)

    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8),
    )

    l = clahe.apply(l)

    enhanced = cv2.cvtColor(
        cv2.merge((l, a, b)),
        cv2.COLOR_LAB2BGR,
    )

    return enhanced


# =========================================================
# BOX HELPERS
# =========================================================

def clean_box(box):
    """
    Convert NumPy values into normal Python ints.
    """

    return [
        [
            int(point[0]),
            int(point[1]),
        ]
        for point in box
    ]


def _box_key(box):
    """
    Coarse spatial key for duplicate filtering.
    """

    xs = [
        round(float(point[0]) / 12)
        for point in box
    ]

    ys = [
        round(float(point[1]) / 12)
        for point in box
    ]

    return tuple(xs + ys)


# =========================================================
# SCRIPT HELPERS
# =========================================================

def _in_ranges(char, ranges):

    code = ord(char)

    return any(
        start <= code <= end
        for start, end in ranges
    )


def script_match_ratio(text, lang):

    chars = [
        c
        for c in text
        if c.isalpha()
    ]

    if not chars:
        return 0.0

    ranges = SCRIPT_RANGES.get(
        lang,
        SCRIPT_RANGES["en"],
    )

    matched = sum(
        _in_ranges(c, ranges)
        for c in chars
    )

    return matched / len(chars)


def latin_ratio(text):

    chars = [
        c
        for c in text
        if c.isalpha()
    ]

    if not chars:
        return 0.0

    return sum(
        ("A" <= c <= "Z")
        or
        ("a" <= c <= "z")
        for c in chars
    ) / len(chars)


# =========================================================
# TEXT CLEANING
# =========================================================

def clean_text(text):

    text = str(text).strip()

    text = re.sub(
        r"[ \t]+",
        " ",
        text,
    )

    return text


def normalize_text(text):

    return re.sub(
        r"[^0-9A-Za-z"
        r"\u0900-\u097F"
        r"\u0B80-\u0BFF"
        r"\u0C00-\u0C7F"
        r"\u0C80-\u0CFF"
        r"]+",
        "",
        text,
    ).lower()


# =========================================================
# NUMERIC / PRICE HELPERS
# =========================================================

NUMERIC_CHARS = (
    "0123456789"
    "$€£¥₹"
    ".,:%/-+()"
)


def is_numeric_text(text):
    """
    Detect text consisting mainly of numbers/currency.

    Examples:

        250
        2250
        ₹250
        $20
        €15.50
        10%
        2/5
    """

    compact = (
        text
        .replace(" ", "")
        .strip()
    )

    if not compact:
        return False

    if not any(
        ch.isdigit()
        for ch in compact
    ):
        return False

    allowed = sum(
        ch in NUMERIC_CHARS
        for ch in compact
    )

    ratio = allowed / len(compact)

    return ratio >= 0.60


def contains_currency_symbol(text):

    return any(
        symbol in text
        for symbol in [
            "₹",
            "$",
            "€",
            "£",
            "¥",
        ]
    )


def numeric_ratio(text):

    compact = (
        text
        .replace(" ", "")
        .strip()
    )

    if not compact:
        return 0.0

    return sum(
        ch in NUMERIC_CHARS
        for ch in compact
    ) / len(compact)


# =========================================================
# DUPLICATION
# =========================================================

def deduplicate_items(items):

    unique = {}

    for item in items:

        text_key = normalize_text(
            item["text"]
        )

        key = (
            _box_key(item["box"]),
            text_key,
        )

        if (
            key not in unique
            or
            item["confidence"]
            >
            unique[key]["confidence"]
        ):

            unique[key] = item

    return list(
        unique.values()
    )


# =========================================================
# OCR RESULT SCORING
# =========================================================

def score_result(items, lang):

    if not items:
        return -1.0

    text = " ".join(
        item["text"]
        for item in items
    ).strip()

    if not text:
        return -1.0

    avg_conf = (
        sum(
            item["confidence"]
            for item in items
        )
        /
        len(items)
    )

    chars = [
        c
        for c in text
        if c.isalpha()
    ]

    char_count = len(chars)

    if lang == "en":

        script_ratio = latin_ratio(
            text
        )

    else:

        script_ratio = script_match_ratio(
            text,
            lang,
        )

    length_bonus = min(
        char_count / 80.0,
        1.0,
    )

    score = (
        0.55 * avg_conf
        +
        0.35 * script_ratio
        +
        0.10 * length_bonus
    )

    if (
        lang != "en"
        and
        script_ratio < 0.35
    ):

        score -= 0.35

    return score


# =========================================================
# NUMERIC REGION RECOGNITION
# =========================================================

def refine_numeric_text(
    reader,
    image,
    box,
):
    """
    Re-run OCR on a small numeric region.

    IMPORTANT:
    This does NOT convert 2250 into ₹250.

    It only gives EasyOCR another opportunity to recognize
    currency symbols and numeric characters.
    """

    try:

        points = np.array(
            box,
            dtype=np.float32,
        )

        x_min = max(
            0,
            int(points[:, 0].min()) - 20,
        )

        y_min = max(
            0,
            int(points[:, 1].min()) - 20,
        )

        x_max = min(
            image.shape[1],
            int(points[:, 0].max()) + 20,
        )

        y_max = min(
            image.shape[0],
            int(points[:, 1].max()) + 20,
        )

        if (
            x_max <= x_min
            or
            y_max <= y_min
        ):
            return None

        crop = image[
            y_min:y_max,
            x_min:x_max,
        ]

        if crop.size == 0:
            return None

        # -------------------------------------------------
        # Upscale
        # -------------------------------------------------

        crop = cv2.resize(
            crop,
            None,
            fx=3.0,
            fy=3.0,
            interpolation=cv2.INTER_CUBIC,
        )

        # -------------------------------------------------
        # Try original crop
        # -------------------------------------------------

        results_original = reader.readtext(
            crop,
            detail=1,
            paragraph=False,
            allowlist=(
                "0123456789"
                "₹$€£¥"
                ".,:%/-+()"
            ),
            text_threshold=0.4,
            low_text=0.2,
            link_threshold=0.2,
        )

        # -------------------------------------------------
        # Try grayscale crop
        # -------------------------------------------------

        gray = cv2.cvtColor(
            crop,
            cv2.COLOR_BGR2GRAY,
        )

        results_gray = reader.readtext(
            gray,
            detail=1,
            paragraph=False,
            allowlist=(
                "0123456789"
                "₹$€£¥"
                ".,:%/-+()"
            ),
            text_threshold=0.4,
            low_text=0.2,
            link_threshold=0.2,
        )

        results = (
            results_original
            +
            results_gray
        )

        if not results:
            return None

        candidates = []

        for _, text, confidence in results:

            text = clean_text(text)

            if not text:
                continue

            text = text.replace(
                " ",
                "",
            )

            cleaned = "".join(
                ch
                for ch in text
                if ch.isdigit()
                or ch in (
                    "₹$€£¥"
                    ".,:%/-+()"
                )
            )

            if not cleaned:
                continue

            confidence = float(
                confidence
            )

            # Give a small bonus to a recognized
            # currency symbol.
            score = confidence

            if contains_currency_symbol(
                cleaned
            ):
                score += 0.10

            candidates.append(
                (
                    cleaned,
                    score,
                )
            )

        if not candidates:
            return None

        candidates.sort(
            key=lambda x: x[1],
            reverse=True,
        )

        best_text = candidates[0][0]

        return best_text

    except Exception as exc:

        print(
            "Numeric OCR refinement failed:",
            exc,
        )

        return None


# =========================================================
# MAIN OCR
# =========================================================

def extract_text_from_image(image):

    processed = preprocess(
        image
    )

    processed_height, processed_width = (
        processed.shape[:2]
    )

    candidates = []

    # =====================================================
    # Run each OCR language independently
    # =====================================================

    for lang in READER_LANGS:

        try:

            reader = get_reader(
                lang
            )

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

                text = clean_text(
                    text
                )

                if not text:
                    continue

                confidence = float(
                    confidence
                )

                cleaned_box = clean_box(
                    box
                )

                # -----------------------------------------
                # Detect numeric / price region
                # -----------------------------------------

                is_numeric_region = (
                    is_numeric_text(text)
                    and
                    confidence < 0.90
                )

                final_text = text

                # -----------------------------------------
                # Second OCR pass only for numeric regions
                # -----------------------------------------

                if is_numeric_region:

                    refined = refine_numeric_text(
                        reader,
                        processed,
                        cleaned_box,
                    )

                    if refined:

                        # Only replace the original OCR
                        # when the refined result is clearly
                        # better.
                        #
                        # Most importantly, don't replace
                        # "2250" with another plain number
                        # just because it came from the
                        # second pass.
                        if (
                            contains_currency_symbol(
                                refined
                            )
                            and
                            not contains_currency_symbol(
                                final_text
                            )
                        ):

                            print(
                                f"Numeric OCR improved: "
                                f"'{final_text}' -> "
                                f"'{refined}'"
                            )

                            final_text = refined

                        elif (
                            confidence < 0.55
                            and
                            len(refined)
                            <= len(final_text) + 2
                        ):

                            # Only use a refined result for
                            # very low confidence OCR.
                            final_text = refined

                items.append({

                    "text": final_text,

                    "confidence": confidence,

                    "box": cleaned_box,

                    "ocr_language": lang,

                    "is_numeric": is_numeric_text(
                        final_text
                    ),

                    "has_currency": contains_currency_symbol(
                        final_text
                    ),

                })

            # =================================================
            # Remove duplicates
            # =================================================

            items = deduplicate_items(
                items
            )

            score = score_result(
                items,
                lang,
            )

            if items:

                candidates.append({

                    "language": lang,

                    "score": score,

                    "items": items,

                })

        except Exception as exc:

            print(
                f"OCR skipped {lang}: {exc}"
            )

    # =====================================================
    # No OCR result
    # =====================================================

    if not candidates:

        return {

            "text": "",

            "items": [],

            "ocr_language": None,

            "ocr_score": 0.0,

            "processed_width":
                processed_width,

            "processed_height":
                processed_height,

        }

    # =====================================================
    # Choose best OCR language
    # =====================================================

    best = max(
        candidates,
        key=lambda x: x["score"],
    )

    items = best["items"]

    # =====================================================
    # Natural reading order
    # =====================================================

    items.sort(
        key=lambda x: (
            min(
                point[1]
                for point in x["box"]
            ),

            min(
                point[0]
                for point in x["box"]
            ),
        )
    )

    # =====================================================
    # Full OCR text
    # =====================================================

    text = "\n".join(
        item["text"]
        for item in items
    )

    # =====================================================
    # Final response
    # =====================================================

    return {

        "text": text,

        "items": items,

        "ocr_language":
            best["language"],

        "ocr_score":
            round(
                float(best["score"]),
                4,
            ),

        "processed_width":
            processed_width,

        "processed_height":
            processed_height,

    }