from datetime import datetime
from backend.database.mongodb import conversations_collection, messages_collection


def get_conversation_history(session_id: str, limit: int = 10):
    """
    Get the previous conversation messages for a session.
    Returns them in the format expected by chat_service.py.
    """

    messages = list(
        messages_collection.find(
            {"session_id": session_id},
            {"_id": 0}
        )
        .sort("timestamp", 1)
        .limit(limit)
    )

    history = []

    for message in messages:
        if message.get("role") == "user":
            history.append({
                "user": message.get("content", ""),
                "assistant": ""
            })

        elif message.get("role") == "assistant":
            if history and history[-1]["assistant"] == "":
                history[-1]["assistant"] = message.get("content", "")

    return history


def save_message(
    session_id: str,
    role: str,
    content: str,
    language: str
):
    """
    Save a single conversation message.
    """

    messages_collection.insert_one({
        "session_id": session_id,
        "role": role,
        "content": content,
        "language": language,
        "timestamp": datetime.utcnow()
    })


def create_conversation(session_id: str, language: str):
    """
    Create a conversation document if it does not already exist.
    """

    existing = conversations_collection.find_one({
        "session_id": session_id
    })

    if not existing:
        conversations_collection.insert_one({
            "session_id": session_id,
            "language": language,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })