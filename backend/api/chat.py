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
    messages_collection,
)


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"],
)


# =========================================================
# EMPTY RESPONSE
# =========================================================

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


# =========================================================
# CLEAN JSON TEXT
# =========================================================

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


# =========================================================
# NORMALIZE ITINERARY ACTIVITY
# =========================================================

def normalize_itinerary_activity(item):

    # -----------------------------------------------------
    # Gemini returned a string
    # Example:
    #
    # "09:00 - Breakfast at a local cafe"
    # -----------------------------------------------------

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

        # No time supplied
        return {
            "time": "",
            "activity": text,
        }

    # -----------------------------------------------------
    # Gemini returned an object
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # Unknown format
    # -----------------------------------------------------

    return {
        "time": "",
        "activity": str(item),
    }


# =========================================================
# NORMALIZE ITINERARY
# =========================================================

def normalize_itinerary(itinerary):

    if not isinstance(
        itinerary,
        list
    ):
        return []

    normalized = []

    for day in itinerary:

        # -------------------------------------------------
        # Skip invalid days
        # -------------------------------------------------

        if not isinstance(
            day,
            dict
        ):
            continue

        new_day = {}

        # -------------------------------------------------
        # Normalize morning / afternoon / evening
        # -------------------------------------------------

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

        # -------------------------------------------------
        # Preserve other day-level fields
        # -------------------------------------------------

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


# =========================================================
# NORMALIZE AI RESPONSE
# =========================================================

def normalize_chat_response(response):

    # =====================================================
    # CASE 1 — STRING RESPONSE
    # =====================================================

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

    # =====================================================
    # CASE 2 — INVALID RESPONSE
    # =====================================================

    if not isinstance(
        response,
        dict
    ):

        return empty_chat_response(
            str(response)
        )

    # =====================================================
    # CASE 3 — NESTED JSON INSIDE MESSAGE
    # =====================================================

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

    # =====================================================
    # SAFE LIST
    # =====================================================

    def safe_list(value):

        if isinstance(
            value,
            list
        ):
            return value

        return []

    # =====================================================
    # NORMALIZE ITINERARY
    # =====================================================

    itinerary = normalize_itinerary(
        safe_list(
            response.get(
                "itinerary",
                []
            )
        )
    )

    # =====================================================
    # FINAL RESPONSE
    # =====================================================

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
    # 1. SESSION MANAGEMENT
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

            # =============================================
            # USER
            # =============================================

            if role == "user":

                pending_user_message = (
                    content
                )

            # =============================================
            # ASSISTANT
            # =============================================

            elif (
                role == "assistant"
                and
                pending_user_message
                is not None
            ):

                assistant_content = (
                    content
                )

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
    # 3. GENERATE AI RESPONSE
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

        # =================================================
        # GEMINI QUOTA / RATE LIMIT
        # =================================================

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

    # =====================================================
    # 4. NORMALIZE RESPONSE
    # =====================================================

    response = normalize_chat_response(
        raw_response
    )

    # =====================================================
    # 5. SAVE TO MONGODB
    # =====================================================

    try:

        now = datetime.now(
            timezone.utc
        )

        # -------------------------------------------------
        # USER MESSAGE
        # -------------------------------------------------

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
                now,

        })

        # -------------------------------------------------
        # ASSISTANT RESPONSE
        # -------------------------------------------------

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
            f"MongoDB save failed: {e}",
            flush=True
        )

    # =====================================================
    # 6. RETURN STRUCTURED RESPONSE
    # =====================================================

    return ChatResponse(

        success=True,

        # -------------------------------------------------
        # Session
        # -------------------------------------------------

        session_id=
            session_id,

        # -------------------------------------------------
        # Language
        # -------------------------------------------------

        language=
            request.language,

        # -------------------------------------------------
        # Main response
        # -------------------------------------------------

        message=
            response.get(
                "message",
                ""
            ),

        # -------------------------------------------------
        # Destination
        # -------------------------------------------------

        destination=
            response.get(
                "destination"
            ),

        # -------------------------------------------------
        # Trip information
        # -------------------------------------------------

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

        # -------------------------------------------------
        # Attractions
        # -------------------------------------------------

        attractions=
            response.get(
                "attractions",
                []
            ),

        # -------------------------------------------------
        # Food
        # -------------------------------------------------

        food=
            response.get(
                "food",
                []
            ),

        # -------------------------------------------------
        # Transportation
        # -------------------------------------------------

        transportation=
            response.get(
                "transportation",
                []
            ),

        # -------------------------------------------------
        # Travel tips
        # -------------------------------------------------

        tips=
            response.get(
                "tips",
                []
            ),

        # -------------------------------------------------
        # Detailed itinerary
        # -------------------------------------------------

        itinerary=
            response.get(
                "itinerary",
                []
            ),
    )