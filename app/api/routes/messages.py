from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.repositories import ConversationRepository, MessageRepository
from app.schemas.message import MessageCreateRequest, MessageResponse
from app.services import MessageService

router = APIRouter()


@router.post("", response_model=MessageResponse)
async def create_message(
    payload: MessageCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    conversation_repo = ConversationRepository(db)
    message_repo = MessageRepository(db)
    service = MessageService(conversation_repo, message_repo)

    return await service.create_message(
        conversation_id=payload.conversation_id,
        role=payload.role,
        content=payload.content,
        model_name=payload.model_name,
    )