import sys
from pathlib import Path
from sqlalchemy import text
from sentence_transformers import SentenceTransformer

# Add parent directory to path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from rag.vectorstore.connect_tidb import get_tidb_engine

# ======================================================
# LOAD EMBEDDING MODEL
# ======================================================
embedder = SentenceTransformer("BAAI/bge-m3")

# ======================================================
# SIMILARITY SEARCH
# ======================================================
def similarity_search(query: str, top_k: int = 5, score_threshold: float = 0.0):
    """
    Search for similar chunks using vector similarity.
    
    Args:
        query: Search query string
        top_k: Number of top results to return
        score_threshold: Minimum similarity score (0-1)
    
    Returns:
        List of dicts with keys: doc_id, chunk_index, text, summary, score
    """
    # Encode query
    query_vector = embedder.encode(query, normalize_embeddings=True).tolist()
    vector_json = str(query_vector).replace("'", '"')
    
    engine = get_tidb_engine()
    
    try:
        with engine.connect() as conn:
            # Query TiDB with vector similarity
            result = conn.execute(
                text(f"""
                    SELECT 
                        re.embed_id,
                        re.doc_id,
                        re.chunk_index,
                        re.summary,
                        rc.chunk_text,
                        VEC_COSINE_DISTANCE(re.summary_vector, CAST(:query_vector AS VECTOR)) as score
                    FROM rag_embeddings re
                    LEFT JOIN rag_chunks rc ON re.doc_id = rc.doc_id AND re.chunk_index = rc.chunk_index
                    WHERE VEC_COSINE_DISTANCE(re.summary_vector, CAST(:query_vector AS VECTOR)) > :threshold
                    ORDER BY score DESC
                    LIMIT :top_k
                """),
                {
                    "query_vector": vector_json,
                    "threshold": score_threshold,
                    "top_k": top_k
                }
            )
            
            rows = result.fetchall()
            results = []
            
            for row in rows:
                results.append({
                    "embed_id": row[0],
                    "doc_id": row[1],
                    "chunk_index": row[2],
                    "summary": row[3],
                    "text": row[4],
                    "score": float(row[5])
                })
            
            return results
    
    except Exception as e:
        print(f"Error during similarity search: {e}")
        return []
