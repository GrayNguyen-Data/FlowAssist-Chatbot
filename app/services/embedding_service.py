import json
from typing import List

from langchain_core.embeddings import Embeddings
from sentence_transformers import SentenceTransformer

from app.core.config import settings


class SentenceTransformerEmbeddings(Embeddings):
    """
    LangChain-compatible wrapper for SentenceTransformer embeddings.
    """

    def __init__(self, model_name: str):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        embedding = self.model.encode(text, normalize_embeddings=True)
        return embedding.tolist()


def get_embedder() -> SentenceTransformerEmbeddings:
    return SentenceTransformerEmbeddings(model_name=settings.EMBEDDING_MODEL)


class EmbeddingService:
    def __init__(self):
        self.embedder = get_embedder()

    async def embed_text(self, text: str) -> list[float]:
        return self.embedder.embed_query(text)

    async def embed_text_as_json(self, text: str) -> str:
        vector = await self.embed_text(text)
        return json.dumps(vector, ensure_ascii=False)