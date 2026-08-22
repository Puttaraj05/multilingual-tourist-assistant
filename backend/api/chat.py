import json
from uuid import uuid4
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from backend.models.chat import (
    ChatRequest,
    ChatResponse,
)

from backend.services.gemini_service import (
    generate_chat_response,
)

from backend.database.mongodb import (
    get_chat_messages,
    save_chat_message,
)


# Chat API routes
router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"],
)


# Return an empty response when AI does not return
# the expected travel data.
def empty_chat_response(message: str = ""):

    return {
        "message": message,
        "destination": None,
        "trip_duration": None,
        "travel_style": None,
        "best_time_to_visit": None,
        "estimated_budget": None,
        "attractions": [],
        "food": [],
        "transportation": [],
        "tips": [],
        "itinerary": [],
    }


# Remove ```json and ``` from Gemini responses.
def clean_json_text(text: str) -> str:

    if not text:
        return ""

    text = str(text).strip()

    if text.startswith("```json"):
        text = text[7:].strip()

    elif text.startswith("```"):
        text = text[3:].strip()

    if text.endswith("```"):
        text = text[:-3].strip()

    return text


# Convert one itinerary activity into a standard format.
def normalize_itinerary_activity(item):

    if isinstance(item, str):

        text = item.strip()

        if " - " in text:

            time, activity = text.split(
                " - ",
                1
            )

            return {
                "time": time.strip(),
                "activity": activity.strip(),
            }

        return {
            "time": "",
            "activity": text,
        }

    if isinstance(item, dict):

        return {
            "time": str(
                item.get(
                    "time",
                    ""
                )
            ),

            "activity": str(
                item.get(
                    "activity",
                    item.get(
                        "description",
                        item.get(
                            "name",
                            ""
                        )
                    )
                )
            ),
        }

    return {
        "time": "",
        "activity": str(item),
    }


# Make all itinerary days use the same structure.
def normalize_itinerary(itinerary):

    if not isinstance(itinerary, list):
        return []

    normalized = []

    for day in itinerary:

        if not isinstance(day, dict):
            continue

        new_day = {}

        for period in [
            "morning",
            "afternoon",
            "evening",
            "night",
        ]:

            activities = day.get(
                period,
                []
            )

            if not isinstance(
                activities,
                list
            ):
                activities = []

            new_day[period] = [
                normalize_itinerary_activity(
                    item
                )
                for item in activities
            ]

        # Keep other information such as title,
        # summary, cost and accommodation.
        for key, value in day.items():

            if key not in [
                "morning",
                "afternoon",
                "evening",
                "night",
            ]:

                new_day[key] = value

        normalized.append(new_day)

    return normalized


# Make sure Gemini response matches frontend format.
def normalize_chat_response(response):

    # Gemini may return JSON as a string.
    if isinstance(response, str):

        text = clean_json_text(response)

        try:

            parsed = json.loads(text)

            if isinstance(parsed, dict):
                response = parsed

            else:
                return empty_chat_response(text)

        except json.JSONDecodeError:

            # Do not crash when Gemini returns normal text.
            return empty_chat_response(text)

    if not isinstance(response, dict):

        return empty_chat_response(
            str(response)
        )

    # Sometimes Gemini puts JSON inside "message".
    message_value = response.get("message")

    if isinstance(message_value, str):

        nested_text = clean_json_text(
            message_value
        )

        if (
            nested_text.startswith("{")
            and
            nested_text.endswith("}")
        ):

            try:

                nested = json.loads(
                    nested_text
                )

                if isinstance(nested, dict):
                    response = nested

            except json.JSONDecodeError:
                pass

    # Only accept actual lists.
    def safe_list(value):

        if isinstance(value, list):
            return value

        return []

    return {

        "message": str(
            response.get(
                "message",
                ""
            )
        ),

        "destination":
            response.get("destination"),

        "trip_duration":
            response.get("trip_duration"),

        "travel_style":
            response.get("travel_style"),

        "best_time_to_visit":
            response.get("best_time_to_visit"),

        "estimated_budget":
            response.get("estimated_budget"),

        "attractions":
            safe_list(
                response.get(
                    "attractions",
                    []
                )
            ),

        "food":
            safe_list(
                response.get(
                    "food",
                    []
                )
            ),

        "transportation":
            safe_list(
                response.get(
                    "transportation",
                    []
                )
            ),

        "tips":
            safe_list(
                response.get(
                    "tips",
                    []
                )
            ),

        "itinerary":
            normalize_itinerary(
                safe_list(
                    response.get(
                        "itinerary",
                        []
                    )
                )
            ),
    }


# Handle a chat message.
@router.post(
    "",
    response_model=ChatResponse
)
async def chat(
    request: ChatRequest
):

    # Use the existing session or create a new one.
    session_id = (
        request.session_id
        or str(uuid4())
    )

    # Use the language selected by the user.
    selected_language = (
        request.language
        or "English"
    ).strip()

    if not selected_language:
        selected_language = "English"

    print(
        f"Chat request received | "
        f"Language: {selected_language} | "
        f"Message: {request.message}",
        flush=True
    )

    # Load previous conversation.
    conversation_history = []

    try:

        previous_messages = get_chat_messages(
            session_id
        )

        pending_user_message = None

        pending_user_language = (
            selected_language
        )

        for item in previous_messages:

            role = item.get(
                "role"
            )

            content = item.get(
                "content",
                ""
            )

            message_language = (
                item.get("language")
                or selected_language
            )

            if role == "user":

                pending_user_message = content

                pending_user_language = (
                    message_language
                )

            elif (
                role == "assistant"
                and
                pending_user_message
                is not None
            ):

                assistant_content = content

                if isinstance(
                    assistant_content,
                    str
                ):

                    try:

                        assistant_content = json.loads(
                            assistant_content
                        )

                    except (
                        json.JSONDecodeError,
                        TypeError
                    ):

                        pass

                conversation_history.append({

                    "user":
                        pending_user_message,

                    "assistant":
                        assistant_content,

                    "language":
                        pending_user_language,
                })

                pending_user_message = None

    except Exception as e:

        print(
            f"MongoDB history unavailable: {e}",
            flush=True
        )

        conversation_history = []

    # Ask Gemini for the answer.
    try:

        raw_response = generate_chat_response(

            message=request.message,

            # IMPORTANT:
            # This is the language selected by the user.
            language=selected_language,

            conversation_history=
                conversation_history,
        )

        print(
            "Gemini response received.",
            flush=True
        )

    except RuntimeError as e:

        error_message = str(e)

        print(
            f"Gemini RuntimeError: {error_message}",
            flush=True
        )

        if (
            "quota" in error_message.lower()
            or
            "resource_exhausted"
            in error_message.lower()
            or
            "429" in error_message
        ):

            raise HTTPException(
                status_code=429,
                detail=error_message
            )

        raise HTTPException(
            status_code=500,
            detail=error_message
        )

    except Exception as e:

        print(
            f"Chat generation error: {e}",
            flush=True
        )

        raise HTTPException(
            status_code=500,
            detail=f"Chat service error: {str(e)}"
        )

    # Convert Gemini output into our standard format.
    response = normalize_chat_response(
        raw_response
    )

    # Save both user and assistant messages.
    try:

        save_chat_message(
            session_id=session_id,
            role="user",
            content=request.message,
            language=selected_language,
        )

        save_chat_message(
            session_id=session_id,
            role="assistant",
            content=json.dumps(
                response,
                ensure_ascii=False
            ),
            language=selected_language,
        )

    except Exception as e:

        print(
            f"MongoDB save failed: {e}",
            flush=True
        )

    # Send response back to frontend.
    return ChatResponse(

        success=True,

        session_id=session_id,

        language=selected_language,

        message=response.get(
            "message",
            ""
        ),

        destination=response.get(
            "destination"
        ),

        trip_duration=response.get(
            "trip_duration"
        ),

        travel_style=response.get(
            "travel_style"
        ),

        best_time_to_visit=response.get(
            "best_time_to_visit"
        ),

        estimated_budget=response.get(
            "estimated_budget"
        ),

        attractions=response.get(
            "attractions",
            []
        ),

        food=response.get(
            "food",
            []
        ),

        transportation=response.get(
            "transportation",
            []
        ),

        tips=response.get(
            "tips",
            []
        ),

        itinerary=response.get(
            "itinerary",
            []
        ),
    )