import re
from io import BytesIO

from docx import Document
from pypdf import PdfReader

from app.db.repositories import RagRepository
from app.services.embedding_service import EmbeddingService


class IngestionService:
    def __init__(
        self,
        rag_repo: RagRepository,
        embedding_service: EmbeddingService | None = None,
    ):
        self.rag_repo = rag_repo
        self.embedding_service = embedding_service or EmbeddingService()

    def _normalize_text(self, text: str) -> str:
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def _split_sentences(self, text: str) -> list[str]:
        text = self._normalize_text(text)
        if not text:
            return []

        parts = re.split(r"(?<=[\.\!\?\:\;])\s+|\n+", text)
        return [part.strip() for part in parts if part and part.strip()]

    def _chunk_text(self, text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
        sentences = self._split_sentences(text)
        if not sentences:
            return []

        chunks: list[str] = []
        current_sentences: list[str] = []
        current_length = 0

        for sentence in sentences:
            sentence_length = len(sentence)

            if sentence_length > chunk_size:
                if current_sentences:
                    chunks.append(" ".join(current_sentences).strip())
                    current_sentences = []
                    current_length = 0

                words = sentence.split()
                temp = ""

                for word in words:
                    candidate = f"{temp} {word}".strip()
                    if len(candidate) <= chunk_size:
                        temp = candidate
                    else:
                        if temp:
                            chunks.append(temp.strip())
                        temp = word

                if temp:
                    chunks.append(temp.strip())
                continue

            candidate_length = current_length + sentence_length + (1 if current_sentences else 0)

            if candidate_length <= chunk_size:
                current_sentences.append(sentence)
                current_length = candidate_length
            else:
                if current_sentences:
                    chunks.append(" ".join(current_sentences).strip())

                overlap_sentences: list[str] = []
                overlap_length = 0

                for prev_sentence in reversed(current_sentences):
                    extra = len(prev_sentence) + (1 if overlap_sentences else 0)
                    if overlap_length + extra <= chunk_overlap:
                        overlap_sentences.insert(0, prev_sentence)
                        overlap_length += extra
                    else:
                        break

                current_sentences = overlap_sentences + [sentence]
                current_length = len(" ".join(current_sentences))

        if current_sentences:
            chunks.append(" ".join(current_sentences).strip())

        deduped: list[str] = []
        for chunk in chunks:
            if not deduped or deduped[-1] != chunk:
                deduped.append(chunk)

        return deduped

    def _extract_text_from_pdf(self, data: bytes) -> str:
        reader = PdfReader(BytesIO(data))
        texts: list[str] = []

        for page in reader.pages:
            page_text = page.extract_text() or ""
            if page_text.strip():
                texts.append(page_text.strip())

        return "\n\n".join(texts).strip()

    def _extract_text_from_docx(self, data: bytes) -> str:
        document = Document(BytesIO(data))
        paragraphs = [p.text.strip() for p in document.paragraphs if p.text and p.text.strip()]
        return "\n".join(paragraphs).strip()

    def _extract_text_from_plain(self, data: bytes) -> str:
        return data.decode("utf-8", errors="ignore")

    def _extract_text_from_bytes(
        self,
        data: bytes,
        file_name: str,
        content_type: str | None = None,
    ) -> str:
        suffix = file_name.lower().split(".")[-1] if "." in file_name else ""

        if content_type and content_type.startswith("text/"):
            return self._extract_text_from_plain(data)

        if suffix in {"txt", "md", "csv", "json"}:
            return self._extract_text_from_plain(data)

        if suffix == "pdf" or content_type == "application/pdf":
            return self._extract_text_from_pdf(data)

        if suffix == "docx":
            return self._extract_text_from_docx(data)

        return self._extract_text_from_plain(data)

    async def ingest_text(
        self,
        doc_id: str,
        content: str,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
    ):
        chunks = self._chunk_text(content, chunk_size, chunk_overlap)

        await self.rag_repo.upsert_metadata(
            doc_id=doc_id,
            doc_metadata={"source": "manual_text_ingest"},
        )

        await self.rag_repo.clear_doc_data(doc_id)

        for idx, chunk_text in enumerate(chunks):
            await self.rag_repo.create_chunk(
                doc_id=doc_id,
                chunk_index=idx,
                chunk_text=chunk_text,
            )

            vector_str = await self.embedding_service.embed_text_as_json(chunk_text)

            await self.rag_repo.create_embedding(
                doc_id=doc_id,
                chunk_index=idx,
                summary=chunk_text,
                summary_vector=vector_str,
            )

        await self.rag_repo.commit()

        return {
            "doc_id": doc_id,
            "total_chunks": len(chunks),
            "total_embeddings": len(chunks),
            "status": "ingested",
        }

    async def ingest_document_bytes(
        self,
        doc_id: str,
        file_name: str,
        data: bytes,
        content_type: str | None = None,
        chunk_size: int = 700,
        chunk_overlap: int = 120,
        extra_metadata: dict | None = None,
    ):
        content = self._extract_text_from_bytes(
            data=data,
            file_name=file_name,
            content_type=content_type,
        )

        chunks = self._chunk_text(content, chunk_size, chunk_overlap)

        metadata = {
            "source": "minio_upload",
            "file_name": file_name,
            "content_type": content_type,
        }
        if extra_metadata:
            metadata.update(extra_metadata)

        await self.rag_repo.upsert_metadata(
            doc_id=doc_id,
            doc_metadata=metadata,
        )

        await self.rag_repo.clear_doc_data(doc_id)

        for idx, chunk_text in enumerate(chunks):
            await self.rag_repo.create_chunk(
                doc_id=doc_id,
                chunk_index=idx,
                chunk_text=chunk_text,
            )

            vector_str = await self.embedding_service.embed_text_as_json(chunk_text)

            await self.rag_repo.create_embedding(
                doc_id=doc_id,
                chunk_index=idx,
                summary=chunk_text,
                summary_vector=vector_str,
            )

        await self.rag_repo.commit()

        return {
            "doc_id": doc_id,
            "extracted_text": content,
            "chunks": chunks,
            "total_chunks": len(chunks),
            "total_embeddings": len(chunks),
            "status": "ingested",
        }