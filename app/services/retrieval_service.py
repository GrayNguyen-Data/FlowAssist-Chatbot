from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.services.embedding_service import get_embedder


class RetrievalService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.top_k = settings.RETRIEVAL_TOP_K
        self.score_threshold = settings.RETRIEVAL_SCORE_THRESHOLD
        self.embedder = get_embedder()

    async def _search_raw(self, query: str) -> list[dict]:
        query_vector = self.embedder.embed_query(query)

        sql = text("""
            SELECT
                e.doc_id,
                e.chunk_index,
                e.summary,
                c.chunk_text,
                vec_cosine_distance(e.summary_vector, :query_vec) AS score
            FROM rag_embeddings e
            LEFT JOIN rag_chunks c
                ON e.doc_id = c.doc_id
               AND e.chunk_index = c.chunk_index
            ORDER BY score ASC
            LIMIT :k
        """)

        result = await self.db.execute(
            sql,
            {
                "query_vec": str(query_vector),
                "k": self.top_k,
            },
        )

        rows = result.fetchall()

        return [
            {
                "doc_id": row.doc_id,
                "chunk_index": row.chunk_index,
                "summary": row.summary,
                "chunk_text": row.chunk_text,
                "score": row.score,
            }
            for row in rows
        ]

    def _extract_contexts(self, results: list[Any]) -> list[str]:
        contexts: list[str] = []

        for item in results:
            if isinstance(item, dict):
                if item.get("chunk_text"):
                    contexts.append(item["chunk_text"])
                elif item.get("summary"):
                    contexts.append(item["summary"])
                elif item.get("text"):
                    contexts.append(item["text"])
                else:
                    contexts.append(str(item))
            else:
                contexts.append(str(item))

        return contexts

    def _filter_results_by_threshold(self, results: list[dict]) -> list[dict]:
        if self.score_threshold <= 0:
            return results

        filtered: list[dict] = []
        for item in results:
            score = item.get("score")
            if score is None:
                filtered.append(item)
                continue

            try:
                # score là distance, càng thấp càng tốt
                if float(score) <= self.score_threshold:
                    filtered.append(item)
            except (TypeError, ValueError):
                filtered.append(item)

        return filtered

    async def retrieve(self, query: str) -> list[str]:
        results = await self._search_raw(query)
        results = self._filter_results_by_threshold(results)
        return self._extract_contexts(results)

    async def retrieve_debug(self, query: str) -> dict:
        results = await self._search_raw(query)
        results = self._filter_results_by_threshold(results)
        contexts = self._extract_contexts(results)

        return {
            "query": query,
            "results": results,
            "contexts": contexts,
        }