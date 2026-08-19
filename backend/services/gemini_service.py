import json
import os
import re
import time

from dotenv import load_dotenv
from google import genai


# =========================================================
# LOAD ENVIRONMENT
# =========================================================

load_dotenv()


# =========================================================
# GEMINI CONFIGURATION
# =========================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not configured."
    )


MODEL_NAME = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash"
)


# =========================================================
# GEMINI CLIENT
# =========================================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)

print(
    f"Gemini model configured: {MODEL_NAME}",
    flush=True
)


# =========================================================
# SYSTEM PROMPT
# =========================================================

SYSTEM_PROMPT = """

You are TravelMate AI, an intelligent multilingual
tourist assistant.

You help travelers with:

- destinations
- attractions
- itineraries
- food
- transportation
- budgets
- travel tips
- local culture
- sightseeing
- trip planning

Always answer in the language requested by the user.

IMPORTANT:

Return ONLY valid JSON.

Do NOT use markdown.

Do NOT use code fences.

Do NOT add explanations outside JSON.

The JSON must follow EXACTLY this structure:

{
    "message": "Helpful conversational response",

    "destination": null,

    "trip_overview": "",

    "trip_duration": "",

    "travel_style": "",

    "best_time_to_visit": "",

    "estimated_budget": "",

    "attractions": [],

    "food": [],

    "transportation": [],

    "tips": [],

    "itinerary": []
}


=========================================================
ATTRACTIONS
=========================================================

Each attraction MUST be an object:

{
    "name": "Attraction name",
    "description": "Description",
    "category": "Historical",
    "best_time": "Morning",
    "estimated_time": "1-2 hours",
    "location": "Location"
}


=========================================================
FOOD
=========================================================

Each food recommendation MUST be an object:

{
    "name": "Food name",
    "description": "Description",
    "type": "Main Course",
    "must_try": true,
    "best_for": "Families",
    "approximate_cost": "₹300"
}


=========================================================
TRANSPORTATION
=========================================================

Each transportation option MUST be an object:

{
    "mode": "Taxi",
    "description": "Description",
    "best_for": "Families",
    "approximate_cost": "₹500",
    "travel_time": "30 minutes"
}


=========================================================
TRAVEL TIPS
=========================================================

Each tip MUST be an object:

{
    "title": "Travel tip",
    "description": "Description"
}


=========================================================
ITINERARY
=========================================================

Each itinerary day MUST be an object:

{
    "day": 1,
    "title": "Day title",
    "summary": "Day summary",

    "morning": [
        {
            "time": "08:00",
            "activity": "Breakfast",
            "location": "Location",
            "duration": "1 hour",
            "description": "Description",
            "estimated_cost": "₹300"
        }
    ],

    "afternoon": [
        {
            "time": "13:00",
            "activity": "Lunch",
            "location": "Location",
            "duration": "1 hour",
            "description": "Description",
            "estimated_cost": "₹500"
        }
    ],

    "evening": [
        {
            "time": "18:00",
            "activity": "Sunset sightseeing",
            "location": "Location",
            "duration": "2 hours",
            "description": "Description",
            "estimated_cost": "₹0"
        }
    ],

    "night": [],

    "activities": [],

    "meals": [],

    "accommodation": null,

    "travel_notes": "Travel information",

    "estimated_cost": "₹1500",

    "distance": "10 km"
}


=========================================================
VERY IMPORTANT ITINERARY RULE
=========================================================

morning, afternoon, evening and night MUST contain
OBJECTS.

NEVER return strings such as:

"09:00 - Breakfast"

Instead return:

{
    "time": "09:00",
    "activity": "Breakfast"
}

This rule is mandatory.


=========================================================
SIMPLE QUESTIONS
=========================================================

If the user asks a simple question:

- answer conversationally
- do not generate unnecessary itinerary information
- use empty arrays for irrelevant sections


=========================================================
TRIP PLANNING
=========================================================

If the user asks for a complete trip plan:

- provide destination information
- attractions
- food
- transportation
- tips
- detailed itinerary


=========================================================
SAFETY
=========================================================

Never invent dangerous or clearly false information.

When information is uncertain, say so clearly.

"""


# =========================================================
# EMPTY RESPONSE
# =========================================================

def empty_response(message=""):
    return {
        "message": message,
        "destination": None,
        "trip_overview": "",
        "trip_duration": "",
        "travel_style": "",
        "best_time_to_visit": "",
        "estimated_budget": "",
        "attractions": [],
        "food": [],
        "transportation": [],
        "tips": [],
        "itinerary": [],
    }


# =========================================================
# CLEAN JSON RESPONSE
# =========================================================

def clean_json_response(text):

    if not text:
        return empty_response()

    text = str(text).strip()

    # Remove ```json
    text = re.sub(
        r"^```json\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    # Remove ```
    text = re.sub(
        r"^```\s*",
        "",
        text
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    text = text.strip()

    # Find JSON object if Gemini adds extra text
    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1 and end > start:
        text = text[start:end + 1]

    try:

        parsed = json.loads(text)

        if isinstance(parsed, dict):
            return parsed

        return empty_response(text)

    except json.JSONDecodeError:

        return empty_response(text)


# =========================================================
# NORMALIZE ITINERARY ACTIVITY
# =========================================================

def normalize_activity(activity):

    # Gemini sometimes returns a string.
    # Convert it into the structure required
    # by ItineraryActivity.

    if isinstance(activity, str):

        activity = activity.strip()

        if " - " in activity:

            activity_time, description = activity.split(
                " - ",
                1
            )

            return {
                "time": activity_time.strip(),
                "activity": description.strip(),
            }

        return {
            "activity": activity
        }

    if isinstance(activity, dict):

        return {
            "time": activity.get("time"),

            "activity": activity.get(
                "activity",
                activity.get(
                    "description",
                    ""
                )
            ),

            "location": activity.get(
                "location"
            ),

            "duration": activity.get(
                "duration"
            ),

            "description": activity.get(
                "description"
            ),

            "estimated_cost": activity.get(
                "estimated_cost"
            ),
        }

    return {
        "activity": str(activity)
    }


# =========================================================
# NORMALIZE ITINERARY DAY
# =========================================================

def normalize_itinerary_day(day, index):

    if not isinstance(day, dict):

        return {
            "day": index + 1,
            "title": f"Day {index + 1}",
            "summary": "",
            "morning": [],
            "afternoon": [],
            "evening": [],
            "night": [],
            "activities": [],
            "meals": [],
            "accommodation": None,
            "travel_notes": "",
            "estimated_cost": None,
            "distance": None,
        }

    def normalize_activities(value):

        if not isinstance(value, list):
            return []

        return [
            normalize_activity(item)
            for item in value
        ]

    return {

        "day": day.get(
            "day",
            index + 1
        ),

        "title": day.get(
            "title",
            f"Day {index + 1}"
        ),

        "summary": day.get(
            "summary"
        ),

        "morning": normalize_activities(
            day.get("morning", [])
        ),

        "afternoon": normalize_activities(
            day.get("afternoon", [])
        ),

        "evening": normalize_activities(
            day.get("evening", [])
        ),

        "night": normalize_activities(
            day.get("night", [])
        ),

        "activities": (
            day.get("activities", [])
            if isinstance(
                day.get("activities", []),
                list
            )
            else []
        ),

        "meals": (
            day.get("meals", [])
            if isinstance(
                day.get("meals", []),
                list
            )
            else []
        ),

        "accommodation": day.get(
            "accommodation"
        ),

        "travel_notes": day.get(
            "travel_notes"
        ),

        "estimated_cost": day.get(
            "estimated_cost"
        ),

        "distance": day.get(
            "distance"
        ),
    }


# =========================================================
# NORMALIZE COMPLETE RESPONSE
# =========================================================

def normalize_response(response):

    if not isinstance(response, dict):

        return empty_response(
            str(response)
        )

    itinerary = response.get(
        "itinerary",
        []
    )

    if not isinstance(itinerary, list):
        itinerary = []

    itinerary = [
        normalize_itinerary_day(
            day,
            index
        )
        for index, day in enumerate(itinerary)
    ]

    def safe_list(value):

        if isinstance(value, list):
            return value

        return []

    return {

        "message": response.get(
            "message",
            ""
        ),

        "destination": response.get(
            "destination"
        ),

        "trip_overview": response.get(
            "trip_overview",
            ""
        ),

        "trip_duration": response.get(
            "trip_duration"
        ),

        "travel_style": response.get(
            "travel_style"
        ),

        "best_time_to_visit": response.get(
            "best_time_to_visit"
        ),

        "estimated_budget": response.get(
            "estimated_budget"
        ),

        "attractions": safe_list(
            response.get(
                "attractions",
                []
            )
        ),

        "food": safe_list(
            response.get(
                "food",
                []
            )
        ),

        "transportation": safe_list(
            response.get(
                "transportation",
                []
            )
        ),

        "tips": safe_list(
            response.get(
                "tips",
                []
            )
        ),

        "itinerary": itinerary,
    }


# =========================================================
# GENERATE CHAT RESPONSE
# =========================================================

def generate_chat_response(
    message,
    language="English",
    conversation_history=None
):

    conversation_history = (
        conversation_history
        or []
    )

    # =====================================================
    # BUILD HISTORY
    # =====================================================

    history_text = ""

    for item in conversation_history:

        user_message = item.get(
            "user",
            ""
        )

        assistant_message = item.get(
            "assistant",
            ""
        )

        if isinstance(
            assistant_message,
            dict
        ):

            assistant_message = json.dumps(
                assistant_message,
                ensure_ascii=False
            )

        history_text += (
            f"\nUser: {user_message}"
            f"\nTravelMate: {assistant_message}"
            "\n"
        )

    # =====================================================
    # BUILD PROMPT
    # =====================================================

    prompt = f"""

{SYSTEM_PROMPT}

Requested response language:

{language}

Previous conversation:

{history_text}

Current user message:

{message}

Return ONLY valid JSON.

"""

    # =====================================================
    # GEMINI REQUEST WITH RETRIES
    # =====================================================

    max_retries = 3

    response = None

    for attempt in range(max_retries):

        try:

            print(
                f"Calling Gemini {MODEL_NAME} "
                f"(attempt {attempt + 1}/{max_retries})",
                flush=True
            )

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
            )

            print(
                "Gemini request successful.",
                flush=True
            )

            break

        except Exception as e:

            error_text = str(e)

            print(
                f"Gemini API error: {error_text}",
                flush=True
            )

            # =============================================
            # RETRY TEMPORARY 503 ERRORS
            # =============================================

            is_temporary_error = (
                "503" in error_text
                or "UNAVAILABLE" in error_text
                or "temporarily unavailable" in error_text.lower()
            )

            if is_temporary_error:

                if attempt < max_retries - 1:

                    # 2 sec -> 4 sec -> 8 sec
                    wait_time = 2 ** (attempt + 1)

                    print(
                        f"Gemini temporarily unavailable. "
                        f"Retrying in {wait_time} seconds...",
                        flush=True
                    )

                    time.sleep(
                        wait_time
                    )

                    continue

            # =============================================
            # DO NOT RETRY OTHER ERRORS
            # =============================================

            raise RuntimeError(
                error_text
            )

    # =====================================================
    # SAFETY CHECK
    # =====================================================

    if response is None:

        raise RuntimeError(
            "Gemini failed after all retry attempts."
        )

    # =====================================================
    # GET RESPONSE TEXT
    # =====================================================

    response_text = getattr(
        response,
        "text",
        None
    )

    if not response_text:

        raise RuntimeError(
            "Gemini returned an empty response."
        )

    # =====================================================
    # PARSE JSON
    # =====================================================

    parsed = clean_json_response(
        response_text
    )

    # =====================================================
    # NORMALIZE RESPONSE
    # =====================================================

    return normalize_response(
        parsed
    )