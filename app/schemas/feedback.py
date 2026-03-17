from pydantic import BaseModel


class FeedbackRequest(BaseModel):
    conversation_id: str
    message_id: int | None = None
    user_id: str | None = None
    rating: int | None = None
    feedback_text: str | None = None
    create_ticket: bool = False


class FeedbackResponse(BaseModel):
    conversation_id: str
    message_id: int | None = None
    accepted: bool
    should_create_ticket: bool
    ticket_id: str | None = None
    status: str
    detail: str