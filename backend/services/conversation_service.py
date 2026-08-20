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
    # Get previous messages using the shared MongoDB helper.
    messages = get_chat_messages(
        session_id=session_id,
        limit=limit
    )

    history = []

    # Group each user message with its assistant response.
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

            # Attach the assistant response to the latest user message.
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
    # Save the chat message using the shared MongoDB writer.
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
    # Create the conversation only if it does not already exist.
    return ensure_conversation(
        session_id=session_id,
        language=language
    )