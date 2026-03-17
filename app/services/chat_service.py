from app.db.repositories import (
    ConversationRepository,
    MessageRepository,
    RetrievalLogRepository,
)
from app.services.memory_service import MemoryService
from app.services.retrieval_service import RetrievalService
from app.services.llm_service import LLMService
from app.services.retrieval_policy_service import RetrievalPolicyService


class ChatService:
    def __init__(
        self,
        conversation_repo: ConversationRepository,
        message_repo: MessageRepository,
        retrieval_log_repo: RetrievalLogRepository | None = None,
        memory_service: MemoryService | None = None,
        retrieval_service: RetrievalService | None = None,
        llm_service: LLMService | None = None,
        retrieval_policy_service: RetrievalPolicyService | None = None,
    ):
        if retrieval_service is None:
            raise ValueError("retrieval_service must be provided")

        self.conversation_repo = conversation_repo
        self.message_repo = message_repo
        self.retrieval_log_repo = retrieval_log_repo
        self.memory_service = memory_service or MemoryService()
        self.retrieval_service = retrieval_service
        self.llm_service = llm_service or LLMService()
        self.retrieval_policy_service = retrieval_policy_service or RetrievalPolicyService()

    async def chat(
        self,
        conversation_id: str,
        user_message: str,
    ):
        conversation = await self.conversation_repo.get_by_id(conversation_id)
        if not conversation:
            raise ValueError("Conversation not found")

        created_user_message = await self.message_repo.create(
            conversation_id=conversation_id,
            role="user",
            content=user_message,
            model_name=None,
            status="completed",
        )

        await self.memory_service.append_message(
            conversation_id=conversation_id,
            role="user",
            content=user_message,
        )

        memory_messages = await self.memory_service.get_recent_messages(conversation_id)

        should_retrieve = self.retrieval_policy_service.should_retrieve(
            user_message=user_message,
            memory_messages=memory_messages,
        )

        if should_retrieve:
            retrieval_debug = await self.retrieval_service.retrieve_debug(user_message)
            retrieved_contexts = retrieval_debug["contexts"]
        else:
            retrieval_debug = {
                "query": user_message,
                "results": [],
                "contexts": [],
            }
            retrieved_contexts = []

        if self.retrieval_log_repo:
            await self.retrieval_log_repo.create(
                message_id=created_user_message.message_id,
                query_text=user_message,
                rewritten_query=None,
                results_json=retrieval_debug["results"],
            )

        assistant_text = await self.llm_service.generate_answer(
            user_message=user_message,
            memory_messages=memory_messages,
            retrieved_contexts=retrieved_contexts,
        )

        created_assistant_message = await self.message_repo.create(
            conversation_id=conversation_id,
            role="assistant",
            content=assistant_text,
            model_name=self.llm_service.model_name,
            status="completed",
        )

        await self.memory_service.append_message(
            conversation_id=conversation_id,
            role="assistant",
            content=assistant_text,
        )

        return {
            "conversation_id": conversation_id,
            "user_message": created_user_message.content,
            "assistant_message": created_assistant_message.content,
            "retrieved_context": retrieved_contexts,
        }

    async def chat_once(
        self,
        conversation_id: str,
        user_message: str,
    ):
        return await self.chat(
            conversation_id=conversation_id,
            user_message=user_message,
        )