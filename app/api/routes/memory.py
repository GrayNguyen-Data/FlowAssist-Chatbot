from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.repositories import ConversationRepository, MessageRepository
from app.services import MessageService, MemoryService

router = APIRouter()


@router.get("/{conversation_id}")
async def get_conversation_memory(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
):
    conversation_repo = ConversationRepository(db)
    message_repo = MessageRepository(db)
    memory_service = MemoryService()

    service = MessageService(
        conversation_repo=conversation_repo,
        message_repo=message_repo,
        memory_service=memory_service,
    )

    return await service.get_recent_memory(conversation_id)