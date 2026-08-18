import json
from typing import Optional, List

from backend.services.gemini_service import generate_text
from backend.prompts.tourist_chat import TOURIST_SYSTEM_PROMPT


# =========================================================
# Empty Response
# =========================================================

def empty_chat_response(message: str = "") -> dict:

    return {
        "message": message,
        "destination": None,
        "attractions": [],
        "food": [],
        "transportation": [],
        "tips": [],
        "itinerary": [],
    }


# =========================================================
# Clean Gemini JSON
# =========================================================

def clean_json_response(response: str) -> str:

    if not response:
        return ""

    response = str(response).strip()

    if response.startswith("```json"):
        response = response[7:].strip()

    elif response.startswith("```"):
        response = response[3:].strip()

    if response.endswith("```"):
        response = response[:-3].strip()

    return response


# =========================================================
# Parse JSON
# =========================================================

def parse_json_response(response: str) -> Optional[dict]:

    if not response:
        return None

    response = clean_json_response(response)

    # -----------------------------------------------------
    # Normal JSON
    # -----------------------------------------------------

    try:

        parsed = json.loads(response)

        if isinstance(parsed, dict):
            return parsed

    except json.JSONDecodeError:
        pass

    # -----------------------------------------------------
    # JSON embedded in other text
    # -----------------------------------------------------

    start = response.find("{")
    end = response.rfind("}")

    if start == -1 or end == -1:
        return None

    try:

        parsed = json.loads(
            response[start:end + 1]
        )

        if isinstance(parsed, dict):
            return parsed

    except json.JSONDecodeError:
        return None

    return None


# =========================================================
# Normalize
# =========================================================

def normalize_response(response: dict) -> dict:

    return {

        "message": response.get(
            "message",
            "",
        ),

        "destination": response.get(
            "destination"
        ),

        "attractions": response.get(
            "attractions",
            [],
        ),

        "food": response.get(
            "food",
            [],
        ),

        "transportation": response.get(
            "transportation",
            [],
        ),

        "tips": response.get(
            "tips",
            [],
        ),

        "itinerary": response.get(
            "itinerary",
            [],
        ),
    }


# =========================================================
# Generate Chat Response
# =========================================================

def generate_chat_response(
    message: str,
    language: str,
    conversation_history: Optional[List] = None,
) -> dict:

    prompt = TOURIST_SYSTEM_PROMPT.format(
        language=language
    )


    # =====================================================
    # Conversation History
    # =====================================================

    if conversation_history:

        prompt += (
            "\n\nConversation history:\n"
        )

        for item in conversation_history:

            user_text = item.get(
                "user",
                "",
            )

            assistant_text = item.get(
                "assistant",
                "",
            )

            if isinstance(
                assistant_text,
                dict,
            ):

                assistant_text = json.dumps(
                    assistant_text,
                    ensure_ascii=False,
                )

            prompt += (
                f"User: {user_text}\n"
            )

            prompt += (
                f"Assistant: {assistant_text}\n"
            )


    # =====================================================
    # Current Request
    # =====================================================

    prompt += f"""

Current user message:
{message}

Return ONE JSON object using exactly this structure:

{{
    "message": "Short helpful answer",
    "destination": "Destination name or null",
    "attractions": [
        {{
            "name": "Attraction name",
            "description": "Short description",
            "category": "Historical"
        }}
    ],
    "food": [
        {{
            "name": "Food or restaurant",
            "description": "Short description",
            "type": "Local food"
        }}
    ],
    "transportation": [
        {{
            "mode": "Metro",
            "description": "Useful information"
        }}
    ],
    "tips": [
        {{
            "title": "Tip title",
            "description": "Useful tip"
        }}
    ],
    "itinerary": [
        {{
            "day": 1,
            "title": "Day title",
            "activities": [
                "Activity 1",
                "Activity 2",
                "Activity 3"
            ]
        }}
    ]
}}

IMPORTANT RULES:

- Return JSON only.
- Do not use Markdown.
- Do not wrap JSON in code fences.
- Do not put the JSON inside the "message" field.
- "message" must contain only the human-readable summary.
- Use the requested language: {language}.
- If the user asks for a destination, provide useful attractions.
- If the user asks for a trip plan, provide an itinerary.
- Keep each description concise.
- Use real tourist destinations and commonly known information.
- Do not invent exact prices.
- Do not invent opening hours.
- Do not invent live availability.
- If something is unknown, omit it or use a general statement.
- Keep the entire response compact enough to complete fully.
"""


    # =====================================================
    # Call Gemini
    # =====================================================

    raw_response = generate_text(
        prompt
    )


    # =====================================================
    # Parse
    # =====================================================

    parsed = parse_json_response(
        raw_response
    )


    # =====================================================
    # Success
    # =====================================================

    if parsed is not None:

        return normalize_response(
            parsed
        )


    # =====================================================
    # Fallback
    # =====================================================

    print(
        "WARNING: Gemini returned invalid JSON.",
        flush=True,
    )

    print(
        raw_response,
        flush=True,
    )

    return empty_chat_response(
        "I couldn't format the travel response correctly. Please try again."
    )