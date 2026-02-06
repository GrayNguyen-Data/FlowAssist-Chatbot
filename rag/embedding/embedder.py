from sentence_transformers import SentenceTransformer

def get_embedder():
    model = SentenceTransformer("BAAI/bge-m3")
    return model
