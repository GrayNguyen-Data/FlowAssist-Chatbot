from app.db.repositories import (
    ConversationRepository,
    MessageRepository,
    TicketRepository,
    TicketEventRepository,
)
from app.services.ticket_service import TicketService


class FeedbackService:
    def __init__(
        self,
        conversation_repo: ConversationRepository,
        message_repo: MessageRepository,
        ticket_repo: TicketRepository,
        ticket_event_repo: TicketEventRepository,
    ):
        self.conversation_repo = conversation_repo
        self.message_repo = message_repo
        self.ticket_repo = ticket_repo
        self.ticket_event_repo = ticket_event_repo

    def _should_create_ticket(
        self,
        rating: int | None,
        feedback_text: str | None,
        create_ticket: bool,
    ) -> bool:
        if create_ticket:
            return True

        if rating is not None and rating <= 2:
            return True

        text = (feedback_text or "").lower().strip()

        negative_patterns = [
            "sai",
            "không đúng",
            "khong dung",
            "lỗi",
            "loi",
            "support",
            "hỗ trợ",
            "ho tro",
            "ticket",
            "không hài lòng",
            "khong hai long",
            "complaint",
            "bug",
        ]

        return any(p in text for p in negative_patterns)

    async def submit_feedback(
        self,
        conversation_id: str,
        message_id: int | None = None,
        user_id: str | None = None,
        rating: int | None = None,
        feedback_text: str | None = None,
        create_ticket: bool = False,
    ) -> dict:
        conversation = await self.conversation_repo.get_by_id(conversation_id)
        if not conversation:
            return {
                "conversation_id": conversation_id,
                "message_id": message_id,
                "accepted": False,
                "should_create_ticket": False,
                "ticket_id": None,
                "status": "error",
                "detail": "Conversation not found",
            }

        if message_id is not None:
            messages = await self.message_repo.list_by_conversation(conversation_id)
            message_ids = {m.message_id for m in messages}
            if message_id not in message_ids:
                return {
                    "conversation_id": conversation_id,
                    "message_id": message_id,
                    "accepted": False,
                    "should_create_ticket": False,
                    "ticket_id": None,
                    "status": "error",
                    "detail": "Message not found in conversation",
                }

        should_create_ticket = self._should_create_ticket(
            rating=rating,
            feedback_text=feedback_text,
            create_ticket=create_ticket,
        )

        if not should_create_ticket:
            return {
                "conversation_id": conversation_id,
                "message_id": message_id,
                "accepted": True,
                "should_create_ticket": False,
                "ticket_id": None,
                "status": "accepted",
                "detail": "Feedback accepted. No ticket created.",
            }

        ticket_service = TicketService(
            conversation_repo=self.conversation_repo,
            ticket_repo=self.ticket_repo,
            ticket_event_repo=self.ticket_event_repo,
        )

        title = "Feedback từ người dùng cần hỗ trợ"
        if rating is not None:
            title = f"Feedback rating={rating} cần xử lý"

        wrong_answer = None
        if message_id is not None:
            messages = await self.message_repo.list_by_conversation(conversation_id)
            for msg in messages:
                if msg.message_id == message_id:
                    wrong_answer = msg.content
                    break

        ticket = await ticket_service.create_ticket(
            conversation_id=conversation_id,
            user_id=user_id,
            title=title,
            user_input=feedback_text,
            wrong_answer=wrong_answer,
            feedback=feedback_text,
            priority="normal",
        )

        return {
            "conversation_id": conversation_id,
            "message_id": message_id,
            "accepted": True,
            "should_create_ticket": True,
            "ticket_id": ticket.ticket_id,
            "status": "ticket_created",
            "detail": "Feedback accepted and ticket created.",
        }