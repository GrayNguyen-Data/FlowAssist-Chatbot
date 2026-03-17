from fastapi import HTTPException

from app.db.repositories import ConversationRepository, MessageRepository
from app.services.memory_service import MemoryService


class MessageService:
    def __init__(
        self,
        conversation_repo: ConversationRepository,
        message_repo: MessageRepository,
        memory_service: MemoryService | None = None,
    ):
        self.conversation_repo = conversation_repo
        self.message_repo = message_repo
        self.memory_service = memory_service or MemoryService()

    async def create_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        model_name: str | None = None,
    ):
        conversation = await self.conversation_repo.get_by_id(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        message = await self.message_repo.create(
            conversation_id=conversation_id,
            role=role,
            content=content,
            model_name=model_name,
        )

        await self.memory_service.append_message(
            conversation_id=conversation_id,
            role=role,
            content=content,
        )

        return message

    async def list_conversation_messages(self, conversation_id: str):
        conversation = await self.conversation_repo.get_by_id(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        return await self.message_repo.list_by_conversation(conversation_id)

    async def get_recent_memory(self, conversation_id: str):
        conversation = await self.conversation_repo.get_by_id(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        return await self.memory_service.get_recent_messages(conversation_id)