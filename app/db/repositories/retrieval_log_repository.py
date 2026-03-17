from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import RetrievalLog


class RetrievalLogRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        message_id: int,
        query_text: str,
        rewritten_query: str | None = None,
        results_json: dict | list | None = None,
    ) -> RetrievalLog:
        item = RetrievalLog(
            message_id=message_id,
            query_text=query_text,
            rewritten_query=rewritten_query,
            results_json=results_json,
        )
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        return item