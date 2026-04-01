from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.retrieval import (
    RetrievalSearchRequest,
    RetrievalSearchResponse,
)
from app.services import RetrievalService

router = APIRouter()


@router.post("/search", response_model=RetrievalSearchResponse)
async def retrieval_search(
    payload: RetrievalSearchRequest,
    db: AsyncSession = Depends(get_db),
):
    service = RetrievalService(db)
    result = await service.retrieve_debug(payload.query)

    return RetrievalSearchResponse(
        query=result["query"],
        results=result["results"],
        contexts=result["contexts"],
    )