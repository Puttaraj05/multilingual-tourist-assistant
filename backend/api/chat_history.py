from fastapi import APIRouter, HTTPException

from backend.database.mongodb import messages_collection


router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"]
)


@router.get("/history/{session_id}")
async def get_chat_history(session_id: str):

    try:
        messages = list(
            messages_collection
            .find(
                {"session_id": session_id},
                {"_id": 0}
            )
            .sort("created_at", 1)
        )

        return {
            "success": True,
            "session_id": session_id,
            "messages": messages
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve chat history: {str(e)}"
        )