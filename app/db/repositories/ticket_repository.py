from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Ticket


class TicketRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        ticket_id: str,
        conversation_id: str,
        user_id: str | None = None,
        title: str | None = None,
        user_input: str | None = None,
        wrong_answer: str | None = None,
        feedback: str | None = None,
        priority: str = "normal",
        status: str = "open",
    ) -> Ticket:
        item = Ticket(
            ticket_id=ticket_id,
            conversation_id=conversation_id,
            user_id=user_id,
            title=title,
            user_input=user_input,
            wrong_answer=wrong_answer,
            feedback=feedback,
            priority=priority,
            status=status,
        )
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def get_by_id(self, ticket_id: str) -> Ticket | None:
        stmt = select(Ticket).where(Ticket.ticket_id == ticket_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_conversation(self, conversation_id: str) -> list[Ticket]:
        stmt = (
            select(Ticket)
            .where(Ticket.conversation_id == conversation_id)
            .order_by(Ticket.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update(self, ticket: Ticket) -> Ticket:
        await self.db.commit()
        await self.db.refresh(ticket)
        return ticket