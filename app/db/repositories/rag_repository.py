from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import RagMetadata, RagChunk, RagEmbedding


class RagRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def upsert_metadata(self, doc_id: str, doc_metadata: dict | None = None):
        existing = await self.db.get(RagMetadata, doc_id)
        if existing:
            existing.doc_metadata = doc_metadata
            await self.db.commit()
            await self.db.refresh(existing)
            return existing

        item = RagMetadata(
            doc_id=doc_id,
            doc_metadata=doc_metadata,
        )
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def clear_doc_data(self, doc_id: str):
        await self.db.execute(
            delete(RagEmbedding).where(RagEmbedding.doc_id == doc_id)
        )
        await self.db.execute(
            delete(RagChunk).where(RagChunk.doc_id == doc_id)
        )
        await self.db.commit()

    async def create_chunk(
        self,
        doc_id: str,
        chunk_index: int,
        chunk_text: str,
    ):
        item = RagChunk(
            doc_id=doc_id,
            chunk_index=chunk_index,
            chunk_text=chunk_text,
        )
        self.db.add(item)
        await self.db.flush()
        return item

    async def create_embedding(
        self,
        doc_id: str,
        chunk_index: int,
        summary: str,
        summary_vector: str,
    ):
        item = RagEmbedding(
            doc_id=doc_id,
            chunk_index=chunk_index,
            summary=summary,
            summary_vector=summary_vector,
        )
        self.db.add(item)
        await self.db.flush()
        return item

    async def commit(self):
        await self.db.commit()

    
    async def get_metadata(self, doc_id: str):
        return await self.db.get(RagMetadata, doc_id)

    async def list_metadata(self):
        stmt = select(RagMetadata).order_by(RagMetadata.doc_id.asc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())