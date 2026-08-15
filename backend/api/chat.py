import json
from uuid import uuid4
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from backend.models.chat import ChatRequest, ChatResponse
from backend.services.chat_service import generate_chat_response
from backend.database.mongodb import messages_collection


router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"]
)


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):

    session_id = request.session_id or str(uuid4())

    # ---------------------------------------------------------
    # 1. Try to load conversation history from MongoDB
    # ---------------------------------------------------------

    conversation_history = []

    try:
        previous_messages = list(
            messages_collection
            .find(
                {"session_id": session_id},
                {"_id": 0}
            )
            .sort("created_at", 1)
        )

        user_message = None

        for item in previous_messages:

            if item.get("role") == "user":
                user_message = item.get("content")

            elif item.get("role") == "assistant" and user_message:

                conversation_history.append({
                    "user": user_message,
                    "assistant": item.get("content")
                })

                user_message = None

    except Exception as e:
        # MongoDB failure should NOT stop the chatbot
        print(f"MongoDB history unavailable: {e}")

        conversation_history = []


    # ---------------------------------------------------------
    # 2. Generate AI response
    # ---------------------------------------------------------

    try:

        response = generate_chat_response(
            message=request.message,
            language=request.language,
            conversation_history=conversation_history
        )

    except RuntimeError as e:
        error_message = str(e)

        if "quota" in error_message.lower():
            raise HTTPException(
                status_code=429,
                detail=error_message
            )

        raise HTTPException(
            status_code=500,
            detail=error_message
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Chat service error: {str(e)}"
        )


    # ---------------------------------------------------------
    # 3. Try to save user + assistant messages
    # ---------------------------------------------------------

    try:

        now = datetime.now(timezone.utc)

        # Save user message
        messages_collection.insert_one({
            "session_id": session_id,
            "role": "user",
            "content": request.message,
            "language": request.language,
            "created_at": now
        })

        # Save assistant response
        messages_collection.insert_one({
            "session_id": session_id,
            "role": "assistant",
            "content": json.dumps(response, ensure_ascii=False),
            "language": request.language,
            "created_at": datetime.now(timezone.utc)
        })

    except Exception as e:

        # MongoDB failure should NOT affect the chatbot response
        print(f"MongoDB save failed: {e}")


    # ---------------------------------------------------------
    # 4. Return response to frontend
    # ---------------------------------------------------------

    return ChatResponse(
    success=True,
    session_id=session_id,
    language=request.language,
    message=response.get("message", ""),
    destination=response.get("destination"),
    attractions=response.get("attractions", []),
    food=response.get("food", []),
    transportation=response.get("transportation", []),
    tips=response.get("tips", []),
    itinerary=response.get("itinerary", [])
)