from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.repositories import RagRepository
from app.schemas.document import (
    DocumentUploadResponse,
    DocumentResponse,
    DocumentIngestResponse,
)
from app.services.document_storage_service import DocumentStorageService
from app.services.ingestion_service import IngestionService

router = APIRouter()


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    storage_service = DocumentStorageService()
    rag_repo = RagRepository(db)

    data = await file.read()

    uploaded = await storage_service.upload_raw_file(
        file_name=file.filename,
        content_type=file.content_type,
        data=data,
    )

    await rag_repo.upsert_metadata(
        doc_id=uploaded["doc_id"],
        doc_metadata={
            "file_name": uploaded["file_name"],
            "raw_object_name": uploaded["object_name"],
            "raw_bucket_name": uploaded["bucket_name"],
            "content_type": uploaded["content_type"],
            "size": uploaded["size"],
            "status": "uploaded",
            "source": "minio_raw_upload",
        },
    )

    return {
        "doc_id": uploaded["doc_id"],
        "file_name": uploaded["file_name"],
        "object_name": uploaded["object_name"],
        "content_type": uploaded["content_type"],
        "status": "uploaded",
    }


@router.post("/{doc_id}/ingest", response_model=DocumentIngestResponse)
async def ingest_document(
    doc_id: str,
    db: AsyncSession = Depends(get_db),
):
    rag_repo = RagRepository(db)
    storage_service = DocumentStorageService()
    ingestion_service = IngestionService(rag_repo)

    metadata = await rag_repo.get_metadata(doc_id)
    if not metadata:
        raise HTTPException(status_code=404, detail="Document not found")

    doc_metadata = metadata.doc_metadata or {}
    object_name = doc_metadata.get("raw_object_name")
    file_name = doc_metadata.get("file_name")
    content_type = doc_metadata.get("content_type")

    if not object_name or not file_name:
        raise HTTPException(status_code=400, detail="Document metadata incomplete")

    data = await storage_service.read_raw_file(object_name)

    result = await ingestion_service.ingest_document_bytes(
        doc_id=doc_id,
        file_name=file_name,
        data=data,
        content_type=content_type,
        extra_metadata={
            **doc_metadata,
            "status": "ingested",
        },
    )

    processed_text_info = await storage_service.save_processed_text(
        doc_id=doc_id,
        text=result["extracted_text"],
    )

    processed_chunks_info = await storage_service.save_chunks(
        doc_id=doc_id,
        chunks=result["chunks"],
    )

    await rag_repo.upsert_metadata(
        doc_id=doc_id,
        doc_metadata={
            **doc_metadata,
            "status": "ingested",
            "processed_text_object_name": processed_text_info["object_name"],
            "processed_chunks_object_name": processed_chunks_info["object_name"],
            "processed_bucket_name": processed_text_info["bucket_name"],
        },
    )

    return {
        "doc_id": result["doc_id"],
        "total_chunks": result["total_chunks"],
        "total_embeddings": result["total_embeddings"],
        "status": result["status"],
    }


@router.get("", response_model=list[DocumentResponse])
async def list_documents(
    db: AsyncSession = Depends(get_db),
):
    rag_repo = RagRepository(db)
    docs = await rag_repo.list_metadata()
    return [
        {
            "doc_id": doc.doc_id,
            "doc_metadata": doc.doc_metadata,
        }
        for doc in docs
    ]


@router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(
    doc_id: str,
    db: AsyncSession = Depends(get_db),
):
    rag_repo = RagRepository(db)
    doc = await rag_repo.get_metadata(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    return {
        "doc_id": doc.doc_id,
        "doc_metadata": doc.doc_metadata,
    }