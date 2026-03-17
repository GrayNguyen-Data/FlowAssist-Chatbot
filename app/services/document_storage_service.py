import json
import uuid
from datetime import datetime
from io import BytesIO
from pathlib import Path

from app.core.config import settings
from app.storage.minio_client import get_minio


class DocumentStorageService:
    def __init__(self):
        self.client = get_minio()
        self.raw_bucket = settings.MINIO_RAW_BUCKET_NAME
        self.processed_bucket = settings.MINIO_PROCESSED_BUCKET_NAME

    def ensure_bucket(self, bucket_name: str):
        if not self.client.bucket_exists(bucket_name):
            self.client.make_bucket(bucket_name)

    def _get_extension_folder(self, file_name: str) -> str:
        suffix = Path(file_name).suffix.lower().lstrip(".")

        if not suffix:
            return "other"

        allowed = {
            "txt",
            "pdf",
            "doc",
            "docx",
            "md",
            "csv",
            "json",
            "xlsx",
            "xls",
            "ppt",
            "pptx",
        }

        return suffix if suffix in allowed else "other"

    def _build_raw_object_name(self, ext_folder: str, doc_id: str, file_name: str) -> str:
        return f"{ext_folder}/{doc_id}/original/{file_name}"

    def _build_processed_text_object_name(self, ext_folder: str, doc_id: str) -> str:
        return f"{ext_folder}/{doc_id}/text.txt"

    def _build_processed_chunks_object_name(self, ext_folder: str, doc_id: str) -> str:
        return f"{ext_folder}/{doc_id}/chunks.json"

    async def upload_raw_file(
        self,
        file_name: str,
        content_type: str | None,
        data: bytes,
    ):
        self.ensure_bucket(self.raw_bucket)

        doc_id = str(uuid.uuid4())
        ext_folder = self._get_extension_folder(file_name)
        object_name = self._build_raw_object_name(ext_folder, doc_id, file_name)

        self.client.put_object(
            bucket_name=self.raw_bucket,
            object_name=object_name,
            data=BytesIO(data),
            length=len(data),
            content_type=content_type or "application/octet-stream",
            metadata={
                "uploaded-at": datetime.utcnow().isoformat(),
                "extension": ext_folder,
            },
        )

        return {
            "doc_id": doc_id,
            "file_name": file_name,
            "object_name": object_name,
            "bucket_name": self.raw_bucket,
            "content_type": content_type,
            "size": len(data),
            "extension": ext_folder,
        }

    async def read_raw_file(self, object_name: str) -> bytes:
        response = self.client.get_object(self.raw_bucket, object_name)
        try:
            return response.read()
        finally:
            response.close()
            response.release_conn()

    async def save_processed_text(self, doc_id: str, text: str, file_name: str | None = None):
        self.ensure_bucket(self.processed_bucket)

        ext_folder = self._get_extension_folder(file_name) if file_name else "other"
        object_name = self._build_processed_text_object_name(ext_folder, doc_id)
        data = text.encode("utf-8")

        self.client.put_object(
            bucket_name=self.processed_bucket,
            object_name=object_name,
            data=BytesIO(data),
            length=len(data),
            content_type="text/plain; charset=utf-8",
            metadata={
                "processed-at": datetime.utcnow().isoformat(),
                "extension": ext_folder,
            },
        )

        return {
            "bucket_name": self.processed_bucket,
            "object_name": object_name,
            "extension": ext_folder,
        }

    async def save_chunks(self, doc_id: str, chunks: list[str], file_name: str | None = None):
        self.ensure_bucket(self.processed_bucket)

        ext_folder = self._get_extension_folder(file_name) if file_name else "other"
        object_name = self._build_processed_chunks_object_name(ext_folder, doc_id)

        payload = json.dumps(
            [{"chunk_index": i, "chunk_text": chunk} for i, chunk in enumerate(chunks)],
            ensure_ascii=False,
            indent=2,
        ).encode("utf-8")

        self.client.put_object(
            bucket_name=self.processed_bucket,
            object_name=object_name,
            data=BytesIO(payload),
            length=len(payload),
            content_type="application/json",
            metadata={
                "processed-at": datetime.utcnow().isoformat(),
                "extension": ext_folder,
            },
        )

        return {
            "bucket_name": self.processed_bucket,
            "object_name": object_name,
            "extension": ext_folder,
        }