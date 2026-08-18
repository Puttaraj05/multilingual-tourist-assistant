import socket

from google import genai
from google.genai import types

from backend.config import GEMINI_API_KEY


# =========================================================
# Gemini API Key
# =========================================================

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not configured"
    )


# =========================================================
# Force IPv4
# =========================================================

_original_getaddrinfo = socket.getaddrinfo


def ipv4_only_getaddrinfo(
    host,
    port,
    family=0,
    type=0,
    proto=0,
    flags=0,
):
    return _original_getaddrinfo(
        host,
        port,
        socket.AF_INET,
        type,
        proto,
        flags,
    )


socket.getaddrinfo = ipv4_only_getaddrinfo


# =========================================================
# Gemini Client
# =========================================================

client = genai.Client(
    api_key=GEMINI_API_KEY,
    http_options=types.HttpOptions(
        timeout=30000,
    ),
)


# =========================================================
# Generate Text
# =========================================================

def generate_text(prompt: str) -> str:

    print(
        "Gemini request starting...",
        flush=True,
    )

    try:

        response = client.models.generate_content(

            model="gemini-3.1-flash-lite",

            contents=prompt,

            config=types.GenerateContentConfig(

                # IMPORTANT:
                # 500 was too small and caused
                # the JSON to be truncated.
                max_output_tokens=2500,

                # Force Gemini to return JSON.
                response_mime_type="application/json",

                temperature=0.4,
            ),
        )

        print(
            "Gemini response received.",
            flush=True,
        )

        text = response.text or ""

        print(
            f"Gemini response length: {len(text)}",
            flush=True,
        )

        return text

    except Exception as e:

        print(
            f"Gemini error: {e}",
            flush=True,
        )

        raise RuntimeError(f"Gemini API error: {e}")