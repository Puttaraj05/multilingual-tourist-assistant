from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    language: str = "English"
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    success: bool
    session_id: str
    language: str
    response: str