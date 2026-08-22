import json
import os
import re
import time

from dotenv import load_dotenv
from google import genai


# Load the values from the .env file.

load_dotenv()


# Get the Gemini API key.

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not configured."
    )


# Get the Gemini model name from .env.
# If it is not there, use this default model.

MODEL_NAME = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash"
)


# Create the Gemini client.

client = genai.Client(
    api_key=GEMINI_API_KEY
)

print(
    f"Gemini model configured: {MODEL_NAME}",
    flush=True
)


# These instructions tell Gemini how TravelMate should behave.

SYSTEM_PROMPT = """

You are TravelMate AI, a multilingual tourist assistant.

You help users with:

- travel planning
- destinations
- attractions
- itineraries
- food
- transportation
- budgets
- travel tips
- local culture
- sightseeing
- tourism questions


VERY IMPORTANT LANGUAGE RULE:

The user's selected target language is the ONLY language
that should be used for the response.

Always answer in the requested target language.

Do NOT use the language of the user's input message
unless it is the same as the requested target language.

Do NOT use the language from previous messages.

Previous conversation is only for understanding context.

The CURRENT requested language always has higher priority
than previous conversation language.

For example:

User input:
हैदराबाद की तीन दिवसीय यात्रा की योजना बनाएं

Requested language:
English

The response must be completely in English.

Another example:

User input:
Plan a three day trip to Hyderabad

Requested language:
Hindi

The response must be completely in Hindi.

Another example:

User input:
Plan a three day trip to Hyderabad

Requested language:
Telugu

The response must be completely in Telugu.


LANGUAGE CONSISTENCY:

The selected language must be used for:

- message
- trip_overview
- destination when it is descriptive text
- trip_duration
- travel_style
- best_time_to_visit
- estimated_budget
- attraction names when translation is natural
- attraction descriptions
- attraction categories
- food names when translation is natural
- food descriptions
- transportation descriptions
- travel tips
- itinerary titles
- itinerary summaries
- activity names
- activity descriptions
- accommodation
- travel notes
- all other human-readable fields

Proper nouns such as official place names can remain in
their commonly used form when necessary.

Currency symbols and numbers can remain unchanged.


VERY IMPORTANT:

Return ONLY valid JSON.

Do NOT use Markdown.

Do NOT use code fences.

Do NOT write explanations outside JSON.


The JSON must follow this structure:

{
    "message": "Helpful response",
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


ATTRACTIONS:

Each attraction must be an object:

{
    "name": "Attraction name",
    "description": "Description",
    "category": "Category",
    "best_time": "Best time",
    "estimated_time": "Time required",
    "location": "Location"
}


FOOD:

Each food recommendation must be an object:

{
    "name": "Food name",
    "description": "Description",
    "type": "Food type",
    "must_try": true,
    "best_for": "Best for",
    "approximate_cost": "Cost"
}


TRANSPORTATION:

Each transportation option must be an object:

{
    "mode": "Transport mode",
    "description": "Description",
    "best_for": "Best for",
    "approximate_cost": "Cost",
    "travel_time": "Travel time"
}


TRAVEL TIPS:

Each tip must be an object:

{
    "title": "Tip title",
    "description": "Tip description"
}


ITINERARY:

Each itinerary day must be an object:

{
    "day": 1,
    "title": "Day title",
    "summary": "Day summary",

    "morning": [
        {
            "time": "08:00",
            "activity": "Activity",
            "location": "Location",
            "duration": "1 hour",
            "description": "Description",
            "estimated_cost": "Cost"
        }
    ],

    "afternoon": [
        {
            "time": "13:00",
            "activity": "Activity",
            "location": "Location",
            "duration": "1 hour",
            "description": "Description",
            "estimated_cost": "Cost"
        }
    ],

    "evening": [
        {
            "time": "18:00",
            "activity": "Activity",
            "location": "Location",
            "duration": "2 hours",
            "description": "Description",
            "estimated_cost": "Cost"
        }
    ],

    "night": [
        {
            "time": "20:00",
            "activity": "Activity",
            "location": "Location",
            "duration": "1 hour",
            "description": "Description",
            "estimated_cost": "Cost"
        }
    ],

    "activities": [],
    "meals": [],
    "accommodation": null,
    "travel_notes": "Travel information",
    "estimated_cost": "Cost",
    "distance": "Distance"
}


VERY IMPORTANT ITINERARY RULE:

morning, afternoon, evening and night MUST contain
objects.

NEVER return:

"09:00 - Breakfast"

Instead return:

{
    "time": "09:00",
    "activity": "Breakfast"
}


SIMPLE QUESTIONS:

If the user asks a simple question:

- answer the question directly
- use the requested language
- do not create unnecessary itinerary information
- keep unrelated arrays empty


TRIP PLANNING:

If the user asks for a complete trip plan:

- provide destination information
- provide attractions
- provide food recommendations
- provide transportation
- provide travel tips
- provide a detailed itinerary
- use the requested language everywhere


CONVERSATION:

Use previous conversation only to understand context.

Do not copy the previous response language.

The current requested language has priority.

If the user changes the target language,
immediately use the newly selected language.


SAFETY:

Do not invent dangerous or clearly false information.

If information is uncertain, clearly mention that it is uncertain.

"""


# Return an empty response when there is no useful AI response.

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


# Remove code fences and extract JSON from Gemini's response.

def clean_json_response(text):

    if not text:
        return empty_response()

    text = str(text).strip()

    # Remove ```json if Gemini adds it.

    text = re.sub(
        r"^```json\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    # Remove normal ``` if Gemini adds it.

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

    # Find the JSON object inside the response.

    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1 and end > start:

        text = text[
            start:end + 1
        ]

    try:

        parsed = json.loads(text)

        if isinstance(parsed, dict):

            return parsed

        return empty_response(text)

    except json.JSONDecodeError:

        return empty_response(text)


# Make sure every itinerary activity has the same structure.

def normalize_activity(activity):

    # Gemini sometimes returns an activity as plain text.

    if isinstance(activity, str):

        activity = activity.strip()

        if " - " in activity:

            activity_time, description = (
                activity.split(
                    " - ",
                    1
                )
            )

            return {
                "time": activity_time.strip(),
                "activity": description.strip(),
                "location": None,
                "duration": None,
                "description": None,
                "estimated_cost": None,
            }

        return {
            "time": None,
            "activity": activity,
            "location": None,
            "duration": None,
            "description": None,
            "estimated_cost": None,
        }

    # Gemini normally returns activities as objects.

    if isinstance(activity, dict):

        return {
            "time": activity.get(
                "time"
            ),

            "activity": activity.get(
                "activity",
                activity.get(
                    "name",
                    activity.get(
                        "description",
                        ""
                    )
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

    # Convert unexpected values to text.

    return {
        "time": None,
        "activity": str(activity),
        "location": None,
        "duration": None,
        "description": None,
        "estimated_cost": None,
    }


# Normalize one itinerary day.

def normalize_itinerary_day(
    day,
    index
):

    # Create a safe empty day if the AI returns invalid data.

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

    # Convert an activity section into a list of objects.

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
            "summary",
            ""
        ),

        "morning": normalize_activities(
            day.get(
                "morning",
                []
            )
        ),

        "afternoon": normalize_activities(
            day.get(
                "afternoon",
                []
            )
        ),

        "evening": normalize_activities(
            day.get(
                "evening",
                []
            )
        ),

        "night": normalize_activities(
            day.get(
                "night",
                []
            )
        ),

        "activities": (
            day.get(
                "activities",
                []
            )
            if isinstance(
                day.get(
                    "activities",
                    []
                ),
                list
            )
            else []
        ),

        "meals": (
            day.get(
                "meals",
                []
            )
            if isinstance(
                day.get(
                    "meals",
                    []
                ),
                list
            )
            else []
        ),

        "accommodation": day.get(
            "accommodation"
        ),

        "travel_notes": day.get(
            "travel_notes",
            ""
        ),

        "estimated_cost": day.get(
            "estimated_cost"
        ),

        "distance": day.get(
            "distance"
        ),
    }


# Make the complete response safe for the frontend.

def normalize_response(response):

    if not isinstance(
        response,
        dict
    ):

        return empty_response(
            str(response)
        )

    itinerary = response.get(
        "itinerary",
        []
    )

    if not isinstance(
        itinerary,
        list
    ):

        itinerary = []

    itinerary = [
        normalize_itinerary_day(
            day,
            index
        )
        for index, day in enumerate(
            itinerary
        )
    ]

    # Keep only lists in these sections.

    def safe_list(value):

        if isinstance(
            value,
            list
        ):

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
            "trip_duration",
            ""
        ),

        "travel_style": response.get(
            "travel_style",
            ""
        ),

        "best_time_to_visit": response.get(
            "best_time_to_visit",
            ""
        ),

        "estimated_budget": response.get(
            "estimated_budget",
            ""
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


# Generate the TravelMate response.

def generate_chat_response(
    message,
    language="English",
    conversation_history=None
):

    conversation_history = (
        conversation_history
        or []
    )

    # Build previous conversation text.

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

    # This instruction is repeated here on purpose.
    # It makes the selected language stronger than the old chat language.

    language_instruction = f"""

CURRENT TARGET LANGUAGE: {language}

IMPORTANT:

Generate the ENTIRE response in {language}.

The user's input language does NOT decide the response language.

The previous conversation language does NOT decide the response language.

Only the CURRENT TARGET LANGUAGE decides the response language.

Every human-readable JSON value must be written in {language}.

Do not mix languages unless a proper noun or official place
name normally remains untranslated.

"""


    # Send the conversation and the current request to Gemini.

    prompt = f"""

{SYSTEM_PROMPT}

{language_instruction}

PREVIOUS CONVERSATION:

{history_text}

CURRENT USER MESSAGE:

{message}

Remember:

The current target language is {language}.

Return ONLY valid JSON.

"""


    # Try again when Gemini temporarily fails.

    max_retries = 3

    response = None

    for attempt in range(
        max_retries
    ):

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

            # Retry only temporary server errors.

            temporary_error = (
                "503" in error_text
                or
                "UNAVAILABLE" in error_text
                or
                "temporarily unavailable"
                in error_text.lower()
            )

            if (
                temporary_error
                and
                attempt < max_retries - 1
            ):

                wait_time = (
                    2 ** (attempt + 1)
                )

                print(
                    f"Gemini temporarily unavailable. "
                    f"Retrying in {wait_time} seconds...",
                    flush=True
                )

                time.sleep(
                    wait_time
                )

                continue

            raise RuntimeError(
                error_text
            )

    # Make sure Gemini returned something.

    if response is None:

        raise RuntimeError(
            "Gemini failed after all retry attempts."
        )

    # Get Gemini's text response.

    response_text = getattr(
        response,
        "text",
        None
    )

    if not response_text:

        raise RuntimeError(
            "Gemini returned an empty response."
        )

    # Convert Gemini's JSON text into a Python dictionary.

    parsed = clean_json_response(
        response_text
    )

    # Make sure the dictionary has the structure
    # expected by chat.py and chat.js.

    return normalize_response(
        parsed
    )