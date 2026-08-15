from uuid import uuid4

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

    try:
        session_id = request.session_id or str(uuid4())

        # Get previous conversation
        previous_messages = list(
            messages_collection
            .find(
                {"session_id": session_id},
                {"_id": 0}
            )
            .sort("created_at", 1)
        )

        conversation_history = []

        for item in previous_messages:
            if item.get("role") == "user":
                # Find corresponding assistant response
                continue

        # Build history as user/assistant pairs
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

        # Generate AI response
        response = generate_chat_response(
            message=request.message,
            language=request.language,
            conversation_history=conversation_history
        )

        # Save user message
        from datetime import datetime, timezone

        messages_collection.insert_one({
            "session_id": session_id,
            "role": "user",
            "content": request.message,
            "language": request.language,
            "created_at": datetime.now(timezone.utc)
        })

        # Save assistant response
        messages_collection.insert_one({
            "session_id": session_id,
            "role": "assistant",
            "content": response,
            "language": request.language,
            "created_at": datetime.now(timezone.utc)
        })

        return ChatResponse(
            success=True,
            session_id=session_id,
            language=request.language,
            response=response
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Chat service error: {str(e)}"
        )