from fastapi import APIRouter
from pydantic import BaseModel

# import your retriever or pipeline
from rag.retrieval.retriever import TiDBRetriever

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    top_k: int = 3
    score_threshold: float = 0.7

@router.post("/search")
def search(request: QueryRequest):
    retriever = TiDBRetriever(top_k=request.top_k, score_threshold=request.score_threshold)
    rows = retriever.search(request.query)
    return {"results": [dict(row) for row in rows]}
