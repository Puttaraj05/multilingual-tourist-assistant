from fastapi import APIRouter, HTTPException

from backend.database.mongodb import (
    get_chat_messages,
)


router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"]
)


@router.get("/history/{session_id}")
async def get_chat_history(session_id: str):

    try:

        messages = get_chat_messages(
            session_id
        )

        return {
            "success": True,
            "session_id": session_id,
            "messages": messages
        }

    except Exception as e:

        print(
            f"Chat history error: {e}",
            flush=True
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to retrieve chat history: "
                f"{str(e)}"
            )
        )
