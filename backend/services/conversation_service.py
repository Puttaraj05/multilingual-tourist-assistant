from backend.database.mongodb import (
    conversations_collection,
    get_chat_messages,
    save_chat_message,
    ensure_conversation,
)


def get_conversation_history(
    session_id: str,
    limit: int = 10
):
    """
    Get previous conversation messages.

    Uses the central MongoDB history helper so that
    sorting and timestamp handling remain consistent.
    """

    messages = get_chat_messages(
        session_id=session_id,
        limit=limit
    )

    history = []

    for message in messages:

        role = message.get("role")

        content = message.get(
            "content",
            ""
        )

        if role == "user":

            history.append({
                "user": content,
                "assistant": ""
            })

        elif role == "assistant":

            if (
                history
                and history[-1]["assistant"] == ""
            ):
                history[-1]["assistant"] = content

    return history


def save_message(
    session_id: str,
    role: str,
    content: str,
    language: str
):
    """
    Save one chat message using the central
    MongoDB message writer.
    """

    return save_chat_message(
        session_id=session_id,
        role=role,
        content=content,
        language=language
    )


def create_conversation(
    session_id: str,
    language: str
):
    """
    Create a conversation if it doesn't exist.
    """

    return ensure_conversation(
        session_id=session_id,
        language=language
    )
