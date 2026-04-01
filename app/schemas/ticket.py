from pydantic import BaseModel
from datetime import datetime


class TicketCreateRequest(BaseModel):
    conversation_id: str
    user_id: str | None = None
    title: str | None = None
    user_input: str | None = None
    wrong_answer: str | None = None
    feedback: str | None = None
    priority: str = "normal"


class TicketUpdateRequest(BaseModel):
    status: str | None = None
    resolved_by: str | None = None
    resolution: str | None = None
    note: str | None = None


class TicketResponse(BaseModel):
    ticket_id: str
    conversation_id: str
    user_id: str | None = None
    title: str | None = None
    user_input: str | None = None
    wrong_answer: str | None = None
    feedback: str | None = None
    status: str
    priority: str
    created_at: datetime
    resolved_at: datetime | None = None
    resolved_by: str | None = None
    resolution: str | None = None

    class Config:
        from_attributes = True


class TicketEventResponse(BaseModel):
    event_id: int
    ticket_id: str
    event_type: str
    actor: str | None = None
    note: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True