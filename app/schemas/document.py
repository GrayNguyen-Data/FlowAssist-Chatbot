from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    doc_id: str
    file_name: str
    object_name: str
    content_type: str | None = None
    status: str


class DocumentResponse(BaseModel):
    doc_id: str
    doc_metadata: dict | None = None


class DocumentIngestResponse(BaseModel):
    doc_id: str
    total_chunks: int
    total_embeddings: int
    status: str