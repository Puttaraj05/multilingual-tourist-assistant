from datetime import datetime


def create_message(
    role: str,
    content: str,
    language: str
):
    return {
        "role": role,
        "content": content,
        "language": language,
        "timestamp": datetime.utcnow()
    }