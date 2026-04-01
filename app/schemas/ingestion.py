from pydantic import BaseModel


class IngestTextRequest(BaseModel):
    doc_id: str
    content: str
    chunk_size: int = 500
    chunk_overlap: int = 50


class IngestTextResponse(BaseModel):
    doc_id: str
    total_chunks: int
    total_embeddings: int
    status: str