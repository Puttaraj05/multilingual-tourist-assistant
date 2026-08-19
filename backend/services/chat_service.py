import json
from uuid import uuid4
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from backend.models.chat import (
    ChatRequest,
    ChatResponse,
)

from backend.database.mongodb import (
    messages_collection,
)

from backend.services.gemini_service import (
    generate_chat_response,
)


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"],
)


# =========================================================
# NORMALIZE API RESPONSE
# =========================================================

def normalize_chat_response(response):

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


# =========================================================
# CHAT ENDPOINT
# =========================================================

@router.post(
    "",
    response_model=ChatResponse
)
async def chat(
    request: ChatRequest
):

    # =====================================================
    # 1. SESSION
    # =====================================================

    session_id = (
        request.session_id
        or str(uuid4())
    )

    # =====================================================
    # 2. LOAD CONVERSATION HISTORY
    # =====================================================

    conversation_history = []

    try:

        previous_messages = list(

            messages_collection
            .find(
                {
                    "session_id":
                        session_id
                },
                {
                    "_id": 0
                }
            )
            .sort(
                "created_at",
                1
            )
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

            # -------------------------------------------------
            # USER MESSAGE
            # -------------------------------------------------

            if role == "user":

                pending_user_message = content

            # -------------------------------------------------
            # ASSISTANT MESSAGE
            # -------------------------------------------------

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

                })

                pending_user_message = None

    except Exception as e:

        print(
            f"MongoDB history unavailable: {e}",
            flush=True
        )

        conversation_history = []

    # =====================================================
    # 3. GENERATE GEMINI RESPONSE
    # =====================================================

    try:

        raw_response = generate_chat_response(

            message=request.message,

            language=request.language,

            conversation_history=
                conversation_history,

        )

    except RuntimeError as e:

        error_message = str(e)

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

    # =====================================================
    # 4. NORMALIZE RESPONSE
    # =====================================================

    response = normalize_chat_response(
        raw_response
    )

    # =====================================================
    # 5. SAVE USER MESSAGE
    # =====================================================

    try:

        messages_collection.insert_one({

            "session_id":
                session_id,

            "role":
                "user",

            "content":
                request.message,

            "language":
                request.language,

            "created_at":
                datetime.now(
                    timezone.utc
                ),

        })

    except Exception as e:

        print(
            f"Could not save user message: {e}",
            flush=True
        )

    # =====================================================
    # 6. SAVE ASSISTANT MESSAGE
    # =====================================================

    try:

        messages_collection.insert_one({

            "session_id":
                session_id,

            "role":
                "assistant",

            "content":
                json.dumps(
                    response,
                    ensure_ascii=False
                ),

            "language":
                request.language,

            "created_at":
                datetime.now(
                    timezone.utc
                ),

        })

    except Exception as e:

        print(
            f"Could not save assistant message: {e}",
            flush=True
        )

    # =====================================================
    # 7. RETURN RESPONSE
    # =====================================================

    return {

        "session_id":
            session_id,

        "language":
            request.language,

        **response,

    }