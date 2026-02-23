from sentence_transformers import SentenceTransformer
from langchain_core.embeddings import Embeddings
from typing import List


class SentenceTransformerEmbeddings(Embeddings):
    """
    LangChain-compatible wrapper for SentenceTransformer embeddings.
    """
    
    def __init__(self, model_name: str = "BAAI/bge-m3"):
        """Initialize the embeddings model."""
        self.model = SentenceTransformer(model_name)
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed search docs.
        """
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()
    
    def embed_query(self, text: str) -> List[float]:
        """
        Embed query text.
        """
        embedding = self.model.encode(text, normalize_embeddings=True)
        return embedding.tolist()


def get_embedder() -> SentenceTransformerEmbeddings:
    """Return a LangChain-compatible embeddings model."""
    return SentenceTransformerEmbeddings(model_name="BAAI/bge-m3")