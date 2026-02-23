import json
from pathlib import Path
import sys
from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from rag.embedding.embedder import get_embedder
from storage.minio_client import get_minio
from rag.vectorstore.connect_tidb import get_tidb_engine


class TiDBIngestionPipeline:
    def __init__(self):
        self.BUCKET = "chatbot-data"
        self.PREFIX = "processed_data/"

        self.minio = get_minio()
        self.engine = get_tidb_engine()
        self.embedder = get_embedder()

        self.seen_docs = set()

    def ingest(self):
        objects = self.minio.list_objects(
            self.BUCKET,
            prefix=self.PREFIX,
            recursive=True
        )

        for obj in objects:
            if not obj.object_name.endswith(".json"):
                continue

            data = json.loads(
                self.minio.get_object(
                    self.BUCKET,
                    obj.object_name
                ).read()
            )

            meta = data["metadata"]
            content = data["content"]

            doc_id = meta["doc_id"]
            idx = meta["chunk_index"]

            summary = content["summary"]
            chunk = content["text"]

            vector = self.embedder.encode(
                summary,
                normalize_embeddings=True
            ).tolist()

            with self.engine.begin() as conn:

                # ===== METADATA TABLE =====
                if doc_id not in self.seen_docs:
                    conn.execute(
                        text("""
                            INSERT INTO rag_metadata
                            (doc_id, metadata)
                            VALUES (:doc_id, :meta)
                            ON DUPLICATE KEY UPDATE metadata=metadata
                        """),
                        {
                            "doc_id": doc_id,
                            "meta": json.dumps(meta),
                        }
                    )
                    self.seen_docs.add(doc_id)

                # ===== EMBEDDINGS TABLE =====
                conn.execute(
                    text("""
                        INSERT INTO rag_embeddings
                        (doc_id, chunk_index, summary, summary_vector)
                        VALUES
                        (:doc_id, :idx, :summary,
                         CAST(:vector AS VECTOR))
                    """),
                    {
                        "doc_id": doc_id,
                        "idx": idx,
                        "summary": summary,
                        "vector": json.dumps(vector),
                    }
                )

                # ===== CHUNKS TABLE =====
                conn.execute(
                    text("""
                        INSERT INTO rag_chunks
                        (doc_id, chunk_index, chunk_text)
                        VALUES
                        (:doc_id, :idx, :chunk)
                    """),
                    {
                        "doc_id": doc_id,
                        "idx": idx,
                        "chunk": chunk,
                    }
                )


if __name__ == "__main__":
    pipeline = TiDBIngestionPipeline()
    pipeline.ingest()
