from sqlalchemy import text
import sys
from pathlib import Path 
sys.path.append(str(Path(__file__).resolve().parent.parent))
from rag.vectorstore import connect_tidb
from sentence_transformers import SentenceTransformer

def create_tables():
    engine = connect_tidb.get_tidb_engine()
    embedder = SentenceTransformer("BAAI/bge-m3")
    EMBED_DIM = embedder.get_sentence_embedding_dimension()

    print("Creating tables...")

    with engine.begin() as conn:
        # ---- Metadata table ----
        conn.execute(text("drop table if exists rag_metadata;"))
        conn.execute(text("""
            create table rag_metadata(
                doc_id varchar(255) primary key,
                metadata json
                );
        """))
        # ---- Embedding table ----
        conn.execute(text("drop table if exists rag_embeddings;"))
        conn.execute(text(f"""
            create table rag_embeddings (
                embed_id bigint primary key auto_increment,
                doc_id varchar(255),
                chunk_index int,
                summary text,
                summary_vector vector({EMBED_DIM}),

                vector index idx_vec((vec_cosine_distance(summary_vector))),
                constraint fk_rag_embeddings_doc foreign key(doc_id) references rag_metadata(doc_id) on delete cascade
                );
        """))

        # ---- Chunk table ----
        conn.execute(text("drop table if exists rag_chunks;"))
        conn.execute(text(""" 
            create table rag_chunks(
                    chunk_id bigint primary key auto_increment,
                    doc_id varchar(255),
                    chunk_index int,
                    chunk_text longtext,
                constraint fk_rag_chunks_doc foreign key(doc_id) references rag_metadata(doc_id) on delete cascade
                );
        """))

        # ---- TIFLASH ----
        conn.execute(text("alter table rag_embeddings set tiflash replica 1;"))

        print("tables ready\n")

if __name__ == "__main__":
    create_tables()