from pydantic import BaseModel
from datetime import datetime


class ConversationCreateRequest(BaseModel):
    user_id: str = "default"
    title: str | None = None
    channel: str = "chat"


class ConversationResponse(BaseModel):
    conversation_id: str
    user_id: str
    title: str | None = None
    status: str
    channel: str
    summary: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True