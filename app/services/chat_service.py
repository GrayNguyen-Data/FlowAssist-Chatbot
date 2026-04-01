from app.db.repositories import (
    ConversationRepository,
    MessageRepository,
    RetrievalLogRepository,
)
from app.services.memory_service import MemoryService
from app.services.retrieval_service import RetrievalService
from app.services.llm_service import LLMService
from app.services.retrieval_policy_service import RetrievalPolicyService
from app.services.ticket_service import TicketService


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
        ticket_service: TicketService | None = None,
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
        self.ticket_service = ticket_service

    def _is_complaint_message(self, message: str) -> bool:
        text = (message or "").lower().strip()

        complaint_patterns = [
            "sai rồi",
            "trả lời sai",
            "câu này sai",
            "không đúng",
            "khong dung",
            "không chính xác",
            "khong chinh xac",
            "bị lỗi",
            "bi loi",
            "lỗi rồi",
            "loi roi",
            "bug",
            "tạo ticket",
            "tao ticket",
            "ghi nhận lỗi",
            "ghi nhan loi",
            "báo lỗi",
            "bao loi",
            "issue",
        ]

        return any(p in text for p in complaint_patterns)

    async def _get_latest_assistant_message(self, conversation_id: str):
        messages = await self.message_repo.list_by_conversation(conversation_id)
        assistant_messages = [m for m in messages if getattr(m, "role", None) == "assistant"]
        if not assistant_messages:
            return None
        return assistant_messages[-1]

    async def _handle_complaint(
        self,
        conversation_id: str,
        user_message: str,
    ):
        if self.ticket_service is None:
            return None

        latest_assistant_message = await self._get_latest_assistant_message(conversation_id)
        if latest_assistant_message is None:
            return None

        ticket = await self.ticket_service.create_ticket(
            conversation_id=conversation_id,
            user_id=None,
            title="Người dùng báo câu trả lời sai",
            user_input=user_message,
            wrong_answer=latest_assistant_message.content,
            feedback=user_message,
            priority="normal",
        )

        assistant_text = "Mình đã ghi nhận lỗi và tạo ticket để kiểm tra rồi nhé."

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
            "user_message": user_message,
            "assistant_message": created_assistant_message.content,
            "retrieved_context": [],
            "ticket_created": True,
            "ticket_id": ticket.ticket_id,
        }

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

        if self._is_complaint_message(user_message):
            complaint_response = await self._handle_complaint(
                conversation_id=conversation_id,
                user_message=user_message,
            )
            if complaint_response is not None:
                return complaint_response

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
            "ticket_created": False,
            "ticket_id": None,
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