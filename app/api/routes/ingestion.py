from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.repositories import RagRepository
from app.schemas.ingestion import IngestTextRequest, IngestTextResponse
from app.services import IngestionService

router = APIRouter()


@router.post("/text", response_model=IngestTextResponse)
async def ingest_text(
    payload: IngestTextRequest,
    db: AsyncSession = Depends(get_db),
):
    rag_repo = RagRepository(db)
    service = IngestionService(rag_repo)

    result = await service.ingest_text(
        doc_id=payload.doc_id,
        content=payload.content,
        chunk_size=payload.chunk_size,
        chunk_overlap=payload.chunk_overlap,
    )
    return result