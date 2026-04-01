import re
import unicodedata
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

        self.stopwords = {
            "là", "và", "của", "cho", "về", "tôi", "mình", "bạn", "anh", "chị",
            "em", "có", "không", "ở", "được", "này", "kia", "đó", "thì", "mà",
            "như", "với", "các", "những", "một", "hay", "khi", "gì", "đâu", "ai",
            "nào", "đi", "ạ", "ừ", "ờ", "nhé", "ha", "hả", "giúp", "biết", "hỏi",
            "thông", "tin",
        }

    def _normalize_query(self, query: str) -> str:
        text_value = (query or "").strip()
        text_value = re.sub(r"\s+", " ", text_value)
        return text_value

    def _remove_accents(self, value: str) -> str:
        normalized = unicodedata.normalize("NFD", value)
        return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")

    def _normalize_for_keywords(self, value: str) -> str:
        value = (value or "").lower().strip()
        value = self._remove_accents(value)
        value = re.sub(r"[^a-z0-9\s]", " ", value)
        value = re.sub(r"\s+", " ", value).strip()
        return value

    def _expand_queries(self, query: str) -> list[str]:
        """
        Tạo thêm các biến thể query để tăng recall.
        Không dùng LLM, chỉ rule-based.
        """
        original = self._normalize_query(query)
        lowered = original.lower()

        candidates: list[str] = [original]

        prefixes = [
            "hãy cho tôi biết mọi thứ về ",
            "hãy cho tôi biết về ",
            "cho tôi biết mọi thứ về ",
            "cho tôi biết về ",
            "tôi muốn biết về ",
            "tôi muốn hỏi về ",
            "giới thiệu về ",
            "thông tin về ",
            "mọi thứ về ",
            "nói về ",
            "mô tả về ",
            "tìm hiểu về ",
            "giải thích về ",
        ]

        trimmed = original
        for prefix in prefixes:
            if lowered.startswith(prefix):
                trimmed = original[len(prefix):].strip()
                break

        if trimmed and trimmed != original:
            candidates.append(trimmed)

        # một số rút gọn thường gặp
        suffixes = [
            "là gì",
            "là ai",
            "gồm những gì",
            "gồm cái gì",
            "như thế nào",
            "ra sao",
            "ở đâu",
        ]

        trimmed_lower = trimmed.lower()
        for suffix in suffixes:
            if trimmed_lower.endswith(suffix):
                short_q = trimmed[: -len(suffix)].strip(" ?.,")
                if short_q:
                    candidates.append(short_q)

        # bỏ "công ty "
        if trimmed.lower().startswith("công ty "):
            company_name = trimmed[8:].strip()
            if company_name:
                candidates.append(company_name)

        if original.lower().startswith("công ty "):
            company_name = original[8:].strip()
            if company_name:
                candidates.append(company_name)

        # thêm bản không dấu để hỗ trợ query gõ lệch dấu
        accentless = self._remove_accents(trimmed).strip()
        if accentless and accentless.lower() != trimmed.lower():
            candidates.append(accentless)

        deduped: list[str] = []
        seen: set[str] = set()

        for item in candidates:
            normalized = self._normalize_query(item)
            key = normalized.lower()
            if normalized and key not in seen:
                seen.add(key)
                deduped.append(normalized)

        return deduped

    def _extract_keywords(self, query: str) -> list[str]:
        """
        Tách keyword để keyword fallback hoạt động tốt hơn khi vector search miss.
        """
        normalized = self._normalize_for_keywords(query)
        if not normalized:
            return []

        words = normalized.split()

        keywords: list[str] = []
        seen: set[str] = set()

        for word in words:
            if len(word) < 2:
                continue
            if word in self.stopwords:
                continue
            if word.isdigit() and len(word) < 4:
                continue
            if word not in seen:
                seen.add(word)
                keywords.append(word)

        return keywords[:8]

    async def _search_once_vector(self, query: str, limit: int | None = None) -> list[dict]:
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
                "source": "vector",
            }
            for row in rows
        ]

    async def _search_once_keyword(self, keywords: list[str], limit: int | None = None) -> list[dict]:
        """
        Keyword fallback bằng ILIKE để xử lý case user hỏi không đúng phrasing.
        Không phụ thuộc extension full text search.
        """
        if not keywords:
            return []

        search_limit = limit or self.top_k
        conditions: list[str] = []
        params: dict[str, Any] = {"k": search_limit}

        for idx, kw in enumerate(keywords):
            param_name = f"kw_{idx}"
            conditions.append(
                f"(LOWER(COALESCE(c.chunk_text, '')) LIKE :{param_name} OR LOWER(COALESCE(e.summary, '')) LIKE :{param_name})"
            )
            params[param_name] = f"%{kw.lower()}%"

        where_clause = " OR ".join(conditions)

        sql = text(f"""
            SELECT
                e.doc_id,
                e.chunk_index,
                e.summary,
                c.chunk_text
            FROM rag_embeddings e
            LEFT JOIN rag_chunks c
                ON e.doc_id = c.doc_id
               AND e.chunk_index = c.chunk_index
            WHERE {where_clause}
            LIMIT :k
        """)

        result = await self.db.execute(sql, params)
        rows = result.fetchall()

        items: list[dict] = []
        for row in rows:
            chunk_text = row.chunk_text or ""
            summary = row.summary or ""
            haystack = f"{summary}\n{chunk_text}".lower()

            matched_terms = []
            for kw in keywords:
                if kw.lower() in haystack:
                    matched_terms.append(kw)

            items.append(
                {
                    "doc_id": row.doc_id,
                    "chunk_index": row.chunk_index,
                    "summary": row.summary,
                    "chunk_text": row.chunk_text,
                    "score": None,
                    "keyword_hits": len(set(matched_terms)),
                    "matched_keywords": sorted(set(matched_terms)),
                    "matched_query": " ".join(keywords),
                    "source": "keyword",
                }
            )

        items.sort(
            key=lambda x: (
                -(x.get("keyword_hits") or 0),
                len((x.get("chunk_text") or x.get("summary") or "")),
            )
        )
        return items[:search_limit]

    def _filter_vector_results_by_threshold(self, results: list[dict]) -> list[dict]:
        if self.score_threshold <= 0:
            return results

        filtered: list[dict] = []
        for item in results:
            score = item.get("score")
            if score is None:
                filtered.append(item)
                continue

            try:
                # cosine distance: càng thấp càng tốt
                if float(score) <= self.score_threshold:
                    filtered.append(item)
            except (TypeError, ValueError):
                filtered.append(item)

        return filtered

    def _rrf_merge(
        self,
        vector_results: list[dict],
        keyword_results: list[dict],
        top_k: int,
    ) -> list[dict]:
        """
        Reciprocal Rank Fusion:
        - không cần scale score giữa vector/keyword về cùng hệ
        - khá ổn để trộn 2 nguồn kết quả
        """
        rrf_k = 60
        merged: dict[tuple[Any, Any], dict] = {}

        for rank, item in enumerate(vector_results, start=1):
            key = (item.get("doc_id"), item.get("chunk_index"))
            score = 1.0 / (rrf_k + rank)

            if key not in merged:
                merged[key] = {**item, "fusion_score": 0.0}
            merged[key]["fusion_score"] += score

        for rank, item in enumerate(keyword_results, start=1):
            key = (item.get("doc_id"), item.get("chunk_index"))
            score = 1.0 / (rrf_k + rank)

            if key not in merged:
                merged[key] = {**item, "fusion_score": 0.0}
            else:
                existing_source = merged[key].get("source")
                if existing_source == "vector":
                    merged[key]["source"] = "hybrid"
                elif existing_source != "hybrid":
                    merged[key]["source"] = "keyword"

                # giữ keyword metadata nếu có
                if item.get("keyword_hits") is not None:
                    merged[key]["keyword_hits"] = item.get("keyword_hits")
                if item.get("matched_keywords") is not None:
                    merged[key]["matched_keywords"] = item.get("matched_keywords")

            merged[key]["fusion_score"] += score

        results = list(merged.values())
        results.sort(
            key=lambda x: (
                -(x.get("fusion_score") or 0.0),
                x.get("score") if x.get("score") is not None else 999999.0,
                -(x.get("keyword_hits") or 0),
            )
        )
        return results[:top_k]

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

    async def _search_raw(self, query: str) -> dict:
        expanded_queries = self._expand_queries(query)
        keywords = self._extract_keywords(query)

        merged_vector: dict[tuple[Any, Any], dict] = {}

        for q in expanded_queries:
            rows = await self._search_once_vector(q, limit=self.top_k)

            for item in rows:
                key = (item.get("doc_id"), item.get("chunk_index"))
                existing = merged_vector.get(key)

                if existing is None:
                    merged_vector[key] = item
                    continue

                old_score = existing.get("score")
                new_score = item.get("score")

                try:
                    if new_score is not None and old_score is not None and float(new_score) < float(old_score):
                        merged_vector[key] = item
                except (TypeError, ValueError):
                    pass

        vector_results = list(merged_vector.values())
        vector_results.sort(
            key=lambda x: float(x.get("score")) if x.get("score") is not None else 999999.0
        )
        vector_results = self._filter_vector_results_by_threshold(vector_results)[: self.top_k]

        keyword_results = await self._search_once_keyword(
            keywords=keywords,
            limit=max(self.top_k * 2, self.top_k),
        )

        fused_results = self._rrf_merge(
            vector_results=vector_results,
            keyword_results=keyword_results,
            top_k=self.top_k,
        )

        return {
            "expanded_queries": expanded_queries,
            "keywords": keywords,
            "vector_results": vector_results,
            "keyword_results": keyword_results,
            "results": fused_results,
        }

    async def retrieve(self, query: str) -> list[str]:
        search_data = await self._search_raw(query)
        return self._extract_contexts(search_data["results"])

    async def retrieve_debug(self, query: str) -> dict:
        search_data = await self._search_raw(query)
        contexts = self._extract_contexts(search_data["results"])

        return {
            "query": query,
            "expanded_queries": search_data["expanded_queries"],
            "keywords": search_data["keywords"],
            "vector_results": search_data["vector_results"],
            "keyword_results": search_data["keyword_results"],
            "results": search_data["results"],
            "contexts": contexts,
        }