import io
import json
import uuid
import time
from pathlib import Path
from unstructured.partition.pdf import partition_pdf
from minio import Minio
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# =========================
# PROJECT UTILS
# =========================
from loader import get_raw_data_from_minio
from core.setting_loader import load_settings

# ======================================================
# LOAD CONFIG
# ======================================================
settings = load_settings()

# ===== MinIO config =====
minio_cfg = settings["minio"]
MAIN_BUCKET = minio_cfg["minio_bucket_name"]

RAW_PREFIX = "raw_data/"
PROCESSED_PREFIX = "processed_data/"

# ===== Groq config =====
groq_cfg = settings["groq"]
groq_api_key = groq_cfg["groq_api_key"]


# ======================================================
# CREATE MINIO CLIENT
# ======================================================
def create_minio_client() -> Minio:
    return Minio(
        minio_cfg["minio_endpoint"],
        access_key=minio_cfg["minio_username"],
        secret_key=minio_cfg["minio_password"],
        secure=False,
    )
minio_client = create_minio_client()

# ======================================================
# INIT LLM SUMMARY CHAIN
# ======================================================
SUMMARY_PROMPT = """
You are an assistant tasked with summarizing text extracted from a PDF.
Give a concise and clear summary.

Respond ONLY with the summary.
Text: {element}
"""
prompt = ChatPromptTemplate.from_template(SUMMARY_PROMPT)

model = ChatGroq(
    api_key=groq_api_key,
    model="llama-3.1-8b-instant",
    temperature=0.5,
)

summary_chain = prompt | model | StrOutputParser()

# ======================================================
# CHUNK PDF (RAM → RAM)
# ======================================================
def get_chunks_from_pdf(file_buffer):
    # đọc PDF thành bytes
    pdf_bytes = file_buffer.read()

    # tạo file-like object trong RAM
    pdf_io = io.BytesIO(pdf_bytes)
    pdf_io.seek(0)

    chunks = partition_pdf(
        file=pdf_io,
        strategy="hi_res",                 # layout-aware
        chunking_strategy="by_title",
        max_characters=1500,
        combine_text_under_n_chars=200,
        new_after_n_chars=2000,
        infer_table_structure=True,
        extract_images_in_pdf=False,
        include_page_breaks=False,
    )

    return chunks
# ======================================================
# UPLOAD JSON DIRECTLY TO MINIO (NO TEMP FILE)
# ======================================================
def upload_json_to_minio(bucket: str, object_name: str, data: dict):
    payload = json.dumps(data, ensure_ascii=False).encode("utf-8")

    minio_client.put_object(
        bucket_name=bucket,
        object_name=object_name,
        data=io.BytesIO(payload),
        length=len(payload),
        content_type="application/json",
    )

# ======================================================
# MAIN PIPELINE: PROCESS ALL PDF
# ======================================================
def process_all_pdfs():
    for object_name, file_buffer in get_raw_data_from_minio(RAW_PREFIX):

        # chỉ xử lý PDF
        if not object_name.lower().endswith(".pdf"):
            continue
        print(f"\nProcessing: {object_name}")

        # tên file không có .pdf
        doc_id = Path(object_name).stem

        # =====================
        # 1. CHUNK PDF
        # =====================
        chunks = get_chunks_from_pdf(file_buffer)

        # chỉ lấy chunk có text
        text_chunks = [
            ch for ch in chunks
            if hasattr(ch, "text") and ch.text and ch.text.strip()
        ]

        print(f"Found {len(text_chunks)} text chunks")

        # =====================
        # 2. SUMMARY + STORE
        # =====================
        for idx, chunk in enumerate(text_chunks):
            # gọi LLM summary
            summary = summary_chain.invoke({
                "element": chunk.text
            })

            # record chuẩn cho RAG
            record = {
                "id": str(uuid.uuid4()),

                # ===== CONTENT (embed, rerank dùng)
                "content": {
                    "text": chunk.text,
                    "summary": summary,
                },

                # ===== METADATA (filter, trace)
                "metadata": {
                    "doc_id": doc_id,
                    "page": getattr(chunk.metadata, "page_number", None),
                    "chunk_index": idx,
                    "source": f"minio://{MAIN_BUCKET}/{object_name}",
                    "type": "text",
                }
            }


            # path object trong bucket
            object_path = (
                f"{PROCESSED_PREFIX}"
                f"{doc_id}/"
                f"chunk_{idx}.json"
            )

            upload_json_to_minio(
                bucket=MAIN_BUCKET,
                object_name=object_path,
                data=record,
            )

            print(f"Uploaded: {object_path}")

            # tránh rate limit
            time.sleep(1.2)

        print(f"DONE: {doc_id}")

