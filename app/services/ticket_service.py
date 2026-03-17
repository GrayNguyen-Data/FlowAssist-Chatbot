import uuid
import datetime
from fastapi import HTTPException

from app.db.repositories import (
    ConversationRepository,
    TicketRepository,
    TicketEventRepository,
)


class TicketService:
    def __init__(
        self,
        conversation_repo: ConversationRepository,
        ticket_repo: TicketRepository,
        ticket_event_repo: TicketEventRepository,
    ):
        self.conversation_repo = conversation_repo
        self.ticket_repo = ticket_repo
        self.ticket_event_repo = ticket_event_repo

    async def create_ticket(
        self,
        conversation_id: str,
        user_id: str | None = None,
        title: str | None = None,
        user_input: str | None = None,
        wrong_answer: str | None = None,
        feedback: str | None = None,
        priority: str = "normal",
    ):
        conversation = await self.conversation_repo.get_by_id(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        ticket_id = str(uuid.uuid4())

        ticket = await self.ticket_repo.create(
            ticket_id=ticket_id,
            conversation_id=conversation_id,
            user_id=user_id,
            title=title,
            user_input=user_input,
            wrong_answer=wrong_answer,
            feedback=feedback,
            priority=priority,
            status="open",
        )

        await self.ticket_event_repo.create(
            ticket_id=ticket.ticket_id,
            event_type="created",
            actor=user_id,
            note=feedback or "Ticket created",
        )

        return ticket

    async def get_ticket(self, ticket_id: str):
        ticket = await self.ticket_repo.get_by_id(ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        return ticket

    async def list_conversation_tickets(self, conversation_id: str):
        conversation = await self.conversation_repo.get_by_id(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return await self.ticket_repo.list_by_conversation(conversation_id)

    async def list_ticket_events(self, ticket_id: str):
        ticket = await self.ticket_repo.get_by_id(ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        return await self.ticket_event_repo.list_by_ticket(ticket_id)

    async def update_ticket(
        self,
        ticket_id: str,
        status: str | None = None,
        resolved_by: str | None = None,
        resolution: str | None = None,
        note: str | None = None,
    ):
        ticket = await self.ticket_repo.get_by_id(ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")

        changed = []

        if status and status != ticket.status:
            ticket.status = status
            changed.append(f"status={status}")

        if resolution is not None:
            ticket.resolution = resolution
            changed.append("resolution_updated")

        if resolved_by is not None:
            ticket.resolved_by = resolved_by
            changed.append(f"resolved_by={resolved_by}")

        if status == "resolved" and ticket.resolved_at is None:
            ticket.resolved_at = datetime.datetime.utcnow()
            changed.append("resolved_at_set")

        updated_ticket = await self.ticket_repo.update(ticket)

        await self.ticket_event_repo.create(
            ticket_id=updated_ticket.ticket_id,
            event_type="updated",
            actor=resolved_by,
            note=note or ", ".join(changed) or "Ticket updated",
        )

        return updated_ticket