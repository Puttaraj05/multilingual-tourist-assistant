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
    ensure_conversation,
    update_conversation_timestamp,
)


# Chat API routes.
router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"],
)


# Return an empty response when the AI does not return
# the expected structured chat data.
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


# Remove markdown code blocks from an AI JSON response.
def clean_json_text(text: str) -> str:

    if not text:
        return ""

    text = str(text).strip()

    if text.startswith("```json"):
        text = text[len("```json"):].strip()

    elif text.startswith("```"):
        text = text[len("```"):].strip()

    if text.endswith("```"):
        text = text[:-3].strip()

    return text


# Convert an itinerary activity into a consistent format.
def normalize_itinerary_activity(item):

    # Handle activities returned as plain text.
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

    # Handle activities returned as objects.
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

    # Convert unexpected activity formats to text.
    return {
        "time": "",
        "activity": str(item),
    }


# Normalize the different parts of the itinerary.
def normalize_itinerary(itinerary):

    if not isinstance(
        itinerary,
        list
    ):
        return []

    normalized = []

    for day in itinerary:

        # Ignore invalid day entries.
        if not isinstance(
            day,
            dict
        ):
            continue

        new_day = {}

        # Keep morning, afternoon and evening activities
        # in the same format.
        for period in [
            "morning",
            "afternoon",
            "evening"
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

        # Keep any additional information returned for the day.
        for key, value in day.items():

            if key not in [
                "morning",
                "afternoon",
                "evening"
            ]:

                new_day[key] = value

        normalized.append(
            new_day
        )

    return normalized


# Make sure the AI response follows the format expected
# by the frontend and API response model.
def normalize_chat_response(response):

    # Convert a string response into JSON when possible.
    if isinstance(
        response,
        str
    ):

        text = clean_json_text(
            response
        )

        try:

            parsed = json.loads(
                text
            )

            if isinstance(
                parsed,
                dict
            ):

                response = parsed

            else:

                return empty_chat_response(
                    text
                )

        except json.JSONDecodeError:

            return empty_chat_response(
                text
            )

    # Return an empty response for unsupported formats.
    if not isinstance(
        response,
        dict
    ):

        return empty_chat_response(
            str(response)
        )

    # Sometimes Gemini places the JSON inside the message field.
    message_value = response.get(
        "message"
    )

    if isinstance(
        message_value,
        str
    ):

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

                if isinstance(
                    nested,
                    dict
                ):

                    response = nested

            except json.JSONDecodeError:

                pass

    # Only return lists when the value is actually a list.
    def safe_list(value):

        if isinstance(
            value,
            list
        ):
            return value

        return []

    # Normalize the itinerary before returning the response.
    itinerary = normalize_itinerary(
        safe_list(
            response.get(
                "itinerary",
                []
            )
        )
    )

    return {

        "message":
            response.get(
                "message",
                ""
            ),

        "destination":
            response.get(
                "destination"
            ),

        "trip_duration":
            response.get(
                "trip_duration"
            ),

        "travel_style":
            response.get(
                "travel_style"
            ),

        "best_time_to_visit":
            response.get(
                "best_time_to_visit"
            ),

        "estimated_budget":
            response.get(
                "estimated_budget"
            ),

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
            itinerary,
    }


# Handle chat messages and return a structured AI response.
@router.post(
    "",
    response_model=ChatResponse
)
async def chat(
    request: ChatRequest
):

    # Create a new session ID when one is not provided.
    session_id = (
        request.session_id
        or str(uuid4())
    )

    # Load previous messages so Gemini can understand
    # the current conversation.
    conversation_history = []

    try:

        previous_messages = get_chat_messages(
            session_id
        )

        pending_user_message = None

        for item in previous_messages:

            role = item.get(
                "role"
            )

            content = item.get(
                "content",
                ""
            )

            # Store the latest user message until
            # its assistant response is found.
            if role == "user":

                pending_user_message = (
                    content
                )

            elif (
                role == "assistant"
                and
                pending_user_message
                is not None
            ):

                assistant_content = (
                    content
                )

                # Convert saved JSON strings back into objects.
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

                })

                pending_user_message = None

    except Exception as e:

        print(
            f"MongoDB history unavailable: {e}",
            flush=True
        )

        conversation_history = []

    # Generate the response using the Gemini service.
    try:

        raw_response = generate_chat_response(

            message=request.message,

            language=request.language,

            conversation_history=
                conversation_history,

        )

    except RuntimeError as e:

        error_message = str(e)

        # Handle Gemini quota and rate-limit errors.
        if (
            "quota"
            in error_message.lower()

            or

            "resource_exhausted"
            in error_message.lower()

            or

            "429"
            in error_message
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

    # Convert the AI response into the expected structure.
    response = normalize_chat_response(
        raw_response
    )

    # Save the conversation in MongoDB.
    try:

        now = datetime.now(
            timezone.utc
        )

        # Save the user's message.
        save_chat_message(
            session_id=session_id,
            role="user",
            content=request.message,
            language=request.language,
        )

        # Save the assistant's structured response.
        save_chat_message(
            session_id=session_id,
            role="assistant",
            content=json.dumps(
                response,
                ensure_ascii=False
            ),
            language=request.language,
        )

    except Exception as e:

        print(
            f"MongoDB save failed: {e}",
            flush=True
        )

    # Return the structured response to the frontend.
    return ChatResponse(

        success=True,

        # Current conversation session.
        session_id=
            session_id,

        # Language used for the response.
        language=
            request.language,

        # Main AI response.
        message=
            response.get(
                "message",
                ""
            ),

        # Destination information.
        destination=
            response.get(
                "destination"
            ),

        # Trip details.
        trip_duration=
            response.get(
                "trip_duration"
            ),

        travel_style=
            response.get(
                "travel_style"
            ),

        best_time_to_visit=
            response.get(
                "best_time_to_visit"
            ),

        estimated_budget=
            response.get(
                "estimated_budget"
            ),

        # Recommended attractions.
        attractions=
            response.get(
                "attractions",
                []
            ),

        # Recommended food options.
        food=
            response.get(
                "food",
                []
            ),

        # Suggested transportation options.
        transportation=
            response.get(
                "transportation",
                []
            ),

        # Helpful travel tips.
        tips=
            response.get(
                "tips",
                []
            ),

        # Detailed day-by-day itinerary.
        itinerary=
            response.get(
                "itinerary",
                []
            ),
    )