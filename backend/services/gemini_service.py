import json
import os
import re
import time

from dotenv import load_dotenv
from google import genai


# Load environment variables from the .env file.

load_dotenv()


# Read the Gemini API key from the environment.

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not configured."
    )


# Use the configured Gemini model or the default model.

MODEL_NAME = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash"
)


# Create the Gemini client using the API key.

client = genai.Client(
    api_key=GEMINI_API_KEY
)

print(
    f"Gemini model configured: {MODEL_NAME}",
    flush=True
)


# Define the instructions used to generate consistent travel responses.

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


ATTRACTIONS

Each attraction MUST be an object:

{
    "name": "Attraction name",
    "description": "Description",
    "category": "Historical",
    "best_time": "Morning",
    "estimated_time": "1-2 hours",
    "location": "Location"
}


FOOD

Each food recommendation MUST be an object:

{
    "name": "Food name",
    "description": "Description",
    "type": "Main Course",
    "must_try": true,
    "best_for": "Families",
    "approximate_cost": "₹300"
}


TRANSPORTATION

Each transportation option MUST be an object:

{
    "mode": "Taxi",
    "description": "Description",
    "best_for": "Families",
    "approximate_cost": "₹500",
    "travel_time": "30 minutes"
}


TRAVEL TIPS

Each tip MUST be an object:

{
    "title": "Travel tip",
    "description": "Description"
}


ITINERARY

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


VERY IMPORTANT ITINERARY RULE

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


SIMPLE QUESTIONS

If the user asks a simple question:

- answer conversationally
- do not generate unnecessary itinerary information
- use empty arrays for irrelevant sections


TRIP PLANNING

If the user asks for a complete trip plan:

- provide destination information
- attractions
- food
- transportation
- tips
- detailed itinerary


SAFETY

Never invent dangerous or clearly false information.

When information is uncertain, say so clearly.

"""


# Create a consistent empty response when no valid data is available.

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


# Clean and parse Gemini's response into a JSON object.

def clean_json_response(text):

    if not text:
        return empty_response()

    text = str(text).strip()

    # Remove Markdown JSON code fences if Gemini adds them.

    text = re.sub(
        r"^```json\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    # Remove a generic Markdown code fence.

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

    # Extract the JSON object if Gemini adds extra text around it.

    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1 and end > start:
        text = text[start:end + 1]

    try:

        # Parse the cleaned response as JSON.

        parsed = json.loads(text)

        if isinstance(parsed, dict):
            return parsed

        return empty_response(text)

    except json.JSONDecodeError:

        # Return a safe response when the JSON cannot be parsed.

        return empty_response(text)


# Convert itinerary activities into a consistent object structure.

def normalize_activity(activity):

    # Convert string activities into the required object format.

    if isinstance(activity, str):

        activity = activity.strip()

        if " - " in activity:

            # Separate the time from the activity description.

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

        # Keep activity details while filling missing optional fields.

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

    # Convert unexpected activity values into text.

    return {
        "activity": str(activity)
    }


# Normalize one itinerary day into the expected structure.

def normalize_itinerary_day(day, index):

    # Return an empty day when Gemini provides invalid day data.

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

        # Ignore invalid activity sections instead of raising an error.

        if not isinstance(value, list):
            return []

        # Normalize every activity into a consistent structure.

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


# Normalize the complete Gemini response before returning it.

def normalize_response(response):

    # Return a safe response when Gemini does not return a dictionary.

    if not isinstance(response, dict):

        return empty_response(
            str(response)
        )

    itinerary = response.get(
        "itinerary",
        []
    )

    # Make sure the itinerary is always represented as a list.

    if not isinstance(itinerary, list):
        itinerary = []

    # Normalize each itinerary day into the expected structure.

    itinerary = [
        normalize_itinerary_day(
            day,
            index
        )
        for index, day in enumerate(itinerary)
    ]

    def safe_list(value):

        # Keep only valid list values for recommendation sections.

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


# Generate a structured travel response using Gemini.

def generate_chat_response(
    message,
    language="English",
    conversation_history=None
):

    # Use an empty history when no previous conversation is available.

    conversation_history = (
        conversation_history
        or []
    )

    # Convert previous conversations into text for Gemini context.

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

            # Convert structured assistant responses into JSON text.

            assistant_message = json.dumps(
                assistant_message,
                ensure_ascii=False
            )

        history_text += (
            f"\nUser: {user_message}"
            f"\nTravelMate: {assistant_message}"
            "\n"
        )

    # Build the prompt using the language, history, and current message.

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

    # Try the Gemini request up to three times for temporary failures.

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

            # Check whether the error is temporary and can be retried.

            is_temporary_error = (
                "503" in error_text
                or "UNAVAILABLE" in error_text
                or "temporarily unavailable" in error_text.lower()
            )

            if is_temporary_error:

                if attempt < max_retries - 1:

                    # Increase the wait time after each failed attempt.

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

            # Stop immediately for errors that are not temporary.

            raise RuntimeError(
                error_text
            )

    # Make sure Gemini returned a response after all attempts.

    if response is None:

        raise RuntimeError(
            "Gemini failed after all retry attempts."
        )

    # Extract the text returned by Gemini.

    response_text = getattr(
        response,
        "text",
        None
    )

    if not response_text:

        raise RuntimeError(
            "Gemini returned an empty response."
        )

    # Parse Gemini's response into the expected JSON structure.

    parsed = clean_json_response(
        response_text
    )

    # Normalize the parsed response before returning it to the API.

    return normalize_response(
        parsed
    )