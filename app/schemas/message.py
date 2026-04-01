from pydantic import BaseModel
from datetime import datetime


class MessageCreateRequest(BaseModel):
    conversation_id: str
    role: str
    content: str
    model_name: str | None = None


class MessageResponse(BaseModel):
    message_id: int
    conversation_id: str
    role: str
    content: str
    model_name: str | None = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True