import json
from uuid import uuid4
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from backend.models.chat import ChatRequest, ChatResponse
from backend.services.chat_service import generate_chat_response
from backend.database.mongodb import messages_collection


# =========================================================
# Router
# =========================================================

router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"],
)


# =========================================================
# Helper: Empty Response
# =========================================================

def empty_chat_response(message=""):
    """
    Return a safe empty chat response structure.
    """

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
# Helper: Normalize AI Response
# =========================================================

def normalize_chat_response(response):
    """
    Normalize the response returned by Gemini.

    Handles:

    1. Proper Python dictionary.

    2. Entire response returned as JSON string.

    3. Dictionary where the 'message' field contains
       the actual JSON response as a string.

    4. Markdown JSON code fences.

    5. Plain text fallback.
    """

    # =====================================================
    # CASE 1: Entire response is a string
    # =====================================================

    if isinstance(response, str):

        text = response.strip()

        # -------------------------------------------------
        # Remove accidental Markdown code fences
        # -------------------------------------------------

        if text.startswith("```"):

            if text.startswith("```json"):

                text = text[
                    len("```json"):
                ]

            elif text.startswith("```"):

                text = text[
                    len("```"):
                ]

            if text.endswith("```"):

                text = text[
                    :-len("```")
                ]

            text = text.strip()

        # -------------------------------------------------
        # Try parsing JSON
        # -------------------------------------------------

        try:

            parsed = json.loads(text)

            if isinstance(parsed, dict):

                response = parsed

            else:

                return empty_chat_response(
                    text
                )

        except json.JSONDecodeError:

            # Gemini returned normal text.
            return empty_chat_response(
                text
            )


    # =====================================================
    # CASE 2: Unexpected response type
    # =====================================================

    if not isinstance(response, dict):

        return empty_chat_response(
            str(response)
        )


    # =====================================================
    # CASE 3: The "message" field contains JSON
    # =====================================================

    message_value = response.get(
        "message"
    )

    if isinstance(message_value, str):

        nested_text = message_value.strip()

        # -------------------------------------------------
        # Remove Markdown fences from nested JSON
        # -------------------------------------------------

        if nested_text.startswith("```"):

            if nested_text.startswith("```json"):

                nested_text = nested_text[
                    len("```json"):
                ]

            elif nested_text.startswith("```"):

                nested_text = nested_text[
                    len("```"):
                ]

            if nested_text.endswith("```"):

                nested_text = nested_text[
                    :-len("```")
                ]

            nested_text = nested_text.strip()

        # -------------------------------------------------
        # Try nested JSON
        # -------------------------------------------------

        if (
            nested_text.startswith("{")
            and nested_text.endswith("}")
        ):

            try:

                nested = json.loads(
                    nested_text
                )

                if isinstance(nested, dict):

                    response = nested

            except json.JSONDecodeError:

                pass


    # =====================================================
    # Normalize expected fields
    # =====================================================

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
# CHAT
# =========================================================

@router.post(
    "",
    response_model=ChatResponse,
)
async def chat(request: ChatRequest):

    # =====================================================
    # 1. CREATE OR RESTORE SESSION
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
                    "session_id": session_id
                },
                {
                    "_id": 0
                },
            )
            .sort(
                "created_at",
                1,
            )
        )

        pending_user_message = None

        for item in previous_messages:

            role = item.get(
                "role"
            )

            content = item.get(
                "content",
                "",
            )

            # -------------------------------------------------
            # User message
            # -------------------------------------------------

            if role == "user":

                pending_user_message = content

            # -------------------------------------------------
            # Assistant message
            # -------------------------------------------------

            elif (
                role == "assistant"
                and pending_user_message is not None
            ):

                assistant_content = content

                # -------------------------------------------------
                # Stored assistant content is normally JSON
                # -------------------------------------------------

                if isinstance(
                    assistant_content,
                    str,
                ):

                    try:

                        assistant_content = json.loads(
                            assistant_content
                        )

                    except (
                        json.JSONDecodeError,
                        TypeError,
                    ):

                        pass

                conversation_history.append({

                    "user": pending_user_message,

                    "assistant": assistant_content,

                })

                pending_user_message = None


    except Exception as e:

        # MongoDB failure should NOT stop chatbot.

        print(
            f"MongoDB history unavailable: {e}",
            flush=True,
        )

        conversation_history = []


    # =====================================================
    # 3. GENERATE AI RESPONSE
    # =====================================================

    try:

        raw_response = generate_chat_response(

            message=request.message,

            language=request.language,

            conversation_history=conversation_history,

        )

    except RuntimeError as e:

        error_message = str(e)

        # -------------------------------------------------
        # Gemini quota / rate limit
        # -------------------------------------------------

        if (
            "quota" in error_message.lower()
            or "resource_exhausted"
            in error_message.lower()
            or "429" in error_message
        ):

            raise HTTPException(
                status_code=429,
                detail=error_message,
            )

        # -------------------------------------------------
        # Other Gemini runtime errors
        # -------------------------------------------------

        raise HTTPException(
            status_code=500,
            detail=error_message,
        )

    except Exception as e:

        print(
            f"Chat generation error: {e}",
            flush=True,
        )

        raise HTTPException(
            status_code=500,
            detail=(
                f"Chat service error: {str(e)}"
            ),
        )


    # =====================================================
    # 4. NORMALIZE AI RESPONSE
    # =====================================================

    response = normalize_chat_response(
        raw_response
    )


    # =====================================================
    # 5. SAVE CONVERSATION TO MONGODB
    # =====================================================

    try:

        now = datetime.now(
            timezone.utc
        )

        # -------------------------------------------------
        # Save user message
        # -------------------------------------------------

        messages_collection.insert_one({

            "session_id": session_id,

            "role": "user",

            "content": request.message,

            "language": request.language,

            "created_at": now,

        })

        # -------------------------------------------------
        # Save assistant response
        # -------------------------------------------------

        messages_collection.insert_one({

            "session_id": session_id,

            "role": "assistant",

            "content": json.dumps(
                response,
                ensure_ascii=False,
            ),

            "language": request.language,

            "created_at": datetime.now(
                timezone.utc
            ),

        })


    except Exception as e:

        # MongoDB failure should NOT affect
        # chatbot response.

        print(
            f"MongoDB save failed: {e}",
            flush=True,
        )


    # =====================================================
    # 6. RETURN STRUCTURED RESPONSE
    # =====================================================

    return ChatResponse(

        success=True,

        session_id=session_id,

        language=request.language,

        message=response.get(
            "message",
            "",
        ),

        destination=response.get(
            "destination"
        ),

        attractions=response.get(
            "attractions",
            [],
        ),

        food=response.get(
            "food",
            [],
        ),

        transportation=response.get(
            "transportation",
            [],
        ),

        tips=response.get(
            "tips",
            [],
        ),

        itinerary=response.get(
            "itinerary",
            [],
        ),

    )