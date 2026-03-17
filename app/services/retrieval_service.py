import re
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

    def _normalize_query(self, query: str) -> str:
        text = (query or "").strip()
        text = re.sub(r"\s+", " ", text)
        return text

    def _expand_queries(self, query: str) -> list[str]:
        """
        Tạo thêm các biến thể query đơn giản để tăng recall.
        Không dùng LLM, chỉ normalize và rút gọn cụm hỏi tự nhiên.
        """
        original = self._normalize_query(query)
        lowered = original.lower()

        candidates: list[str] = [original]

        prefixes = [
            "hãy cho tôi biết mọi thứ về ",
            "hãy cho tôi biết về ",
            "cho tôi biết mọi thứ về ",
            "cho tôi biết về ",
            "giới thiệu về ",
            "thông tin về ",
            "mọi thứ về ",
            "nói về ",
            "mô tả về ",
            "tìm hiểu về ",
        ]

        trimmed = original
        lowered_trimmed = lowered

        for prefix in prefixes:
            if lowered_trimmed.startswith(prefix):
                trimmed = original[len(prefix):].strip()
                break

        if trimmed and trimmed != original:
            candidates.append(trimmed)

        if trimmed.lower().startswith("công ty "):
            company_name = trimmed[8:].strip()
            if company_name:
                candidates.append(company_name)

        if original.lower().startswith("công ty "):
            company_name = original[8:].strip()
            if company_name:
                candidates.append(company_name)

        # Bỏ trùng, giữ thứ tự
        deduped: list[str] = []
        seen: set[str] = set()

        for item in candidates:
            normalized = self._normalize_query(item)
            key = normalized.lower()
            if normalized and key not in seen:
                seen.add(key)
                deduped.append(normalized)

        return deduped

    async def _search_once(self, query: str, limit: int | None = None) -> list[dict]:
        query_vector = self.embedder.embed_query(query)
        search_limit = limit or self.top_k

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
                "k": search_limit,
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
                "matched_query": query,
            }
            for row in rows
        ]

    async def _search_raw(self, query: str) -> list[dict]:
        expanded_queries = self._expand_queries(query)

        merged: dict[tuple[Any, Any], dict] = {}

        for q in expanded_queries:
            rows = await self._search_once(q, limit=self.top_k)

            for item in rows:
                key = (item.get("doc_id"), item.get("chunk_index"))
                existing = merged.get(key)

                if existing is None:
                    merged[key] = item
                    continue

                old_score = existing.get("score")
                new_score = item.get("score")

                try:
                    if new_score is not None and old_score is not None and float(new_score) < float(old_score):
                        merged[key] = item
                except (TypeError, ValueError):
                    pass

        results = list(merged.values())

        def score_key(x: dict):
            score = x.get("score")
            try:
                return float(score)
            except (TypeError, ValueError):
                return 999999.0

        results.sort(key=score_key)
        return results[: self.top_k]

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
        expanded_queries = self._expand_queries(query)
        results = await self._search_raw(query)
        results = self._filter_results_by_threshold(results)
        contexts = self._extract_contexts(results)

        return {
            "query": query,
            "expanded_queries": expanded_queries,
            "results": results,
            "contexts": contexts,
        }