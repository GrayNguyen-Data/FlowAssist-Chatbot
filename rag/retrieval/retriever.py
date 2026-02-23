import sys
from pathlib import Path
from typing import List
from sqlalchemy import text

# PATH SETUP
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from rag.embedding.embedder import get_embedder
from rag.vectorstore.connect_tidb import get_tidb_engine


class TiDBRetriever:

    def __init__(self, top_k: int = 5):
        self.engine = get_tidb_engine()
        self.embedder = get_embedder()
        self.top_k = top_k

    def search(self, query: str) -> List[dict]:
        query_vector = self.embedder.embed_query(query)

        sql = text("""
            SELECT 
                summary,
                doc_id,
                vec_cosine_distance(summary_vector, :query_vec) AS score
            FROM rag_embeddings
            ORDER BY score ASC
            LIMIT :k
        """)

        with self.engine.connect() as conn:
            result = conn.execute(
                sql,
                {
                    "query_vec": str(query_vector),
                    "k": self.top_k
                }
            ).fetchall()

        # Trả về list dict cho dễ build context
        return [
            {
                "summary": row.summary,
                "doc_id": row.doc_id,
                "score": row.score
            }
            for row in result
        ]
