import json
from pathlib import Path
import sys
from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from rag.embedding.embedder import get_embedder
from storage.minio_client import get_minio
from rag.vectorstore.connect_tidb import get_tidb_engine

BUCKET = "chatbot-data"
PREFIX = "processed_data/"

def ingest():
    minio = get_minio()
    engine = get_tidb_engine()
    embedder = get_embedder()

    objects = minio.list_objects(
        BUCKET, prefix=PREFIX, recursive=True
    )

    seen_docs = set()

    for obj in objects:
        if not obj.object_name.endswith(".json"):
            continue

        data = json.loads(
            minio.get_object(BUCKET, obj.object_name).read()
        )

        meta = data["metadata"]
        content = data["content"]

        doc_id = meta["doc_id"]
        idx = meta["chunk_index"]

        summary = content["summary"]
        chunk = content["text"]

        vector = embedder.encode(
            summary, normalize_embeddings=True
        ).tolist()


    
        with engine.begin() as conn:
            if doc_id not in seen_docs:
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
                seen_docs.add(doc_id)

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
