from backend.services.gemini_service import generate_text
from backend.prompts.tourist_chat import TOURIST_SYSTEM_PROMPT
from typing import Optional, List

def generate_chat_response(
    message: str,
    language: str,
    conversation_history: Optional[List] = None
) -> str:

    prompt = TOURIST_SYSTEM_PROMPT.format(
        language=language
    )

    if conversation_history:
        prompt += "\n\nConversation history:\n"

        for item in conversation_history:
            prompt += f"User: {item['user']}\n"
            prompt += f"Assistant: {item['assistant']}\n"

    prompt += f"""

Current user message:
{message}

Respond in {language}.
"""

    return generate_text(prompt)