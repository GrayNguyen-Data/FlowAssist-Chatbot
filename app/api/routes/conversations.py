from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.repositories import ConversationRepository, MessageRepository
from app.schemas.conversation import (
    ConversationCreateRequest,
    ConversationResponse,
)
from app.schemas.message import MessageResponse
from app.services import ConversationService, MessageService

router = APIRouter()


@router.post("", response_model=ConversationResponse)
async def create_conversation(
    payload: ConversationCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    conversation_repo = ConversationRepository(db)
    service = ConversationService(conversation_repo)

    return await service.create_conversation(
        user_id=payload.user_id,
        title=payload.title,
        channel=payload.channel,
    )


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
):
    conversation_repo = ConversationRepository(db)
    service = ConversationService(conversation_repo)

    return await service.get_conversation(conversation_id)


@router.get("/{conversation_id}/messages", response_model=list[MessageResponse])
async def get_conversation_messages(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
):
    conversation_repo = ConversationRepository(db)
    message_repo = MessageRepository(db)
    service = MessageService(conversation_repo, message_repo)

    return await service.list_conversation_messages(conversation_id)