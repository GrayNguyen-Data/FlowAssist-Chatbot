from pydantic import BaseModel


class ChatRequest(BaseModel):
    conversation_id: str
    message: str


class ChatResponse(BaseModel):
    conversation_id: str
    user_message: str
    assistant_message: str
    retrieved_context: list[str] = []