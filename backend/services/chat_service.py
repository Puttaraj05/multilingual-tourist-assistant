import json
from uuid import uuid4
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from backend.models.chat import (
    ChatRequest,
    ChatResponse,
)

from backend.database.mongodb import (
    get_chat_messages,
    save_chat_message,
    ensure_conversation,
    update_conversation_timestamp,
)

from backend.services.gemini_service import (
    generate_chat_response,
)


# Create the chat API router.
router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"],
)


def normalize_chat_response(response):

    # Convert a JSON string into a Python dictionary.
    if isinstance(response, str):

        try:
            response = json.loads(response)

        except json.JSONDecodeError:

            return {
                "message": response,
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

    # Return a safe response when Gemini returns an unexpected type.
    if not isinstance(response, dict):

        return {
            "message": str(response),
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

    # Make sure list fields always contain lists.
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

        "itinerary": safe_list(
            response.get(
                "itinerary",
                []
            )
        ),
    }


@router.post(
    "",
    response_model=ChatResponse
)
async def chat(
    request: ChatRequest
):

    # Create a new session ID when the client does not provide one.
    session_id = (
        request.session_id
        or str(uuid4())
    )

    # Load previous messages to maintain conversation context.
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

            # Store the latest user message until its reply is found.
            if role == "user":

                pending_user_message = content

            # Pair each assistant response with the previous user message.
            elif (
                role == "assistant"
                and
                pending_user_message
                is not None
            ):

                assistant_content = content

                # Convert stored JSON responses back into dictionaries.
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

    # Generate a response using Gemini and the previous conversation.
    try:

        raw_response = generate_chat_response(

            message=request.message,

            language=request.language,

            conversation_history=
                conversation_history,

        )

    except RuntimeError as e:

        error_message = str(e)

        # Return HTTP 429 when the Gemini API quota is exceeded.
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

    # Ensure the generated response matches the API structure.
    response = normalize_chat_response(
        raw_response
    )

    # Save the user's message to MongoDB.
    try:

        save_chat_message(
            session_id=session_id,
            role="user",
            content=request.message,
            language=request.language,
        )

    except Exception as e:

        print(
            f"Could not save user message: {e}",
            flush=True
        )

    # Save the generated assistant response to MongoDB.
    try:

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
            f"Could not save assistant message: {e}",
            flush=True
        )

    # Return the session, language, and generated response.
    return {

        "session_id":
            session_id,

        "language":
            request.language,

        **response,

    }