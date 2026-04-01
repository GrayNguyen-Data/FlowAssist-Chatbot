from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import TicketEvent


class TicketEventRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        ticket_id: str,
        event_type: str,
        actor: str | None = None,
        note: str | None = None,
    ) -> TicketEvent:
        item = TicketEvent(
            ticket_id=ticket_id,
            event_type=event_type,
            actor=actor,
            note=note,
        )
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def list_by_ticket(self, ticket_id: str) -> list[TicketEvent]:
        stmt = (
            select(TicketEvent)
            .where(TicketEvent.ticket_id == ticket_id)
            .order_by(TicketEvent.created_at.asc(), TicketEvent.event_id.asc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())