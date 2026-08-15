import json
from typing import Optional, List

from backend.services.gemini_service import generate_text
from backend.prompts.tourist_chat import TOURIST_SYSTEM_PROMPT


def generate_chat_response(
    message: str,
    language: str,
    conversation_history: Optional[List] = None
) -> dict:

    prompt = TOURIST_SYSTEM_PROMPT.format(
        language=language
    )

    if conversation_history:
        prompt += "\n\nConversation history:\n"

        for item in conversation_history:
            prompt += f"User: {item['user']}\n"
            prompt += f"Assistant: {item['assistant']}\n"

    prompt += f"""

Current user message:
{message}

You are a multilingual tourist assistant.

Respond in {language}.

IMPORTANT:
Return ONLY valid JSON.
Do not use Markdown.
Do not add explanations outside the JSON.

Use exactly this structure:

{{
    "message": "A short helpful summary for the user",
    "destination": "Destination name",
    "attractions": [
        {{
            "name": "Attraction name",
            "description": "Short useful description",
            "category": "Historical / Nature / Museum / Entertainment"
        }}
    ],
    "food": [
        {{
            "name": "Food or restaurant",
            "description": "Short useful description",
            "type": "Local food / Restaurant / Dessert / Drink"
        }}
    ],
    "transportation": [
        {{
            "mode": "Metro / Bus / Taxi / Auto / Walking",
            "description": "Useful transportation information"
        }}
    ],
    "tips": [
        {{
            "title": "Tip title",
            "description": "Useful travel tip"
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

Rules:
- Keep information practical and useful for tourists.
- If the user asks about a specific destination, focus on that destination.
- Do not invent exact prices, opening hours, availability, or other time-sensitive facts unless you are given reliable data.
- If a section is not relevant, return an empty array.
"""

    response = generate_text(prompt)

    try:
        # Remove accidental markdown code fences
        response = response.strip()

        if response.startswith("```"):
            response = response.replace("```json", "")
            response = response.replace("```", "")
            response = response.strip()

        return json.loads(response)

    except json.JSONDecodeError:
        # Fallback if Gemini returns normal text
        return {
            "message": response,
            "destination": None,
            "attractions": [],
            "food": [],
            "transportation": [],
            "tips": [],
            "itinerary": []
        }