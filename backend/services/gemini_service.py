import socket
import httpx

from google import genai
from google.genai import types

from backend.config import GEMINI_API_KEY


if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not configured")


# Force IPv4 for Google API connections.
_original_getaddrinfo = socket.getaddrinfo


def ipv4_only_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    return _original_getaddrinfo(
        host,
        port,
        socket.AF_INET,
        type,
        proto,
        flags,
    )


socket.getaddrinfo = ipv4_only_getaddrinfo


client = genai.Client(
    api_key=GEMINI_API_KEY,
    http_options=types.HttpOptions(
        timeout=15000,
    ),
)


def generate_text(prompt: str) -> str:
    print("Gemini request starting...", flush=True)

    try:
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=500,
            ),
        )

        print("Gemini response received.", flush=True)

        return response.text or ""

    except Exception as e:
        print(f"Gemini error: {e}", flush=True)
        raise RuntimeError(f"Gemini API error: {e}")
