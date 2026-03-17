from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.repositories import (
    ConversationRepository,
    MessageRepository,
    RetrievalLogRepository,
)
from app.schemas.chat import ChatRequest, ChatResponse
from app.services import ChatService, RetrievalService

router = APIRouter()


@router.post("", response_model=ChatResponse)
async def chat_stream(
    payload: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    conversation_repo = ConversationRepository(db)
    message_repo = MessageRepository(db)
    retrieval_log_repo = RetrievalLogRepository(db)
    retrieval_service = RetrievalService(db)

    service = ChatService(
        conversation_repo=conversation_repo,
        message_repo=message_repo,
        retrieval_log_repo=retrieval_log_repo,
        retrieval_service=retrieval_service,
    )

    try:
        result = await service.chat(
            conversation_id=payload.conversation_id,
            user_message=payload.message,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))