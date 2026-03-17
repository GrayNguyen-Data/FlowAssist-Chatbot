from app.db.repositories import ConversationRepository


class ConversationService:
    def __init__(self, conversation_repo: ConversationRepository):
        self.conversation_repo = conversation_repo

    async def create_conversation(
        self,
        user_id: str = "default",
        title: str | None = None,
        channel: str = "chat",
    ):
        return await self.conversation_repo.create(
            user_id=user_id,
            title=title,
            channel=channel,
        )

    async def get_conversation(self, conversation_id: str):
        return await self.conversation_repo.get_by_id(conversation_id)

    async def list_user_conversations(self, user_id: str):
        return await self.conversation_repo.list_by_user(user_id)