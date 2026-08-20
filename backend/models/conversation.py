from datetime import datetime


def create_message(
    role: str,
    content: str,
    language: str
):
    # Create a chat message with its role, language, and timestamp.
    return {
        "role": role,
        "content": content,
        "language": language,
        "timestamp": datetime.utcnow()
    }