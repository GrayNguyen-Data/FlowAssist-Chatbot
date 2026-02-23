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

from loader import get_data_from_minio
from core.setting_loader import load_settings


class PDFProcessingPipeline:
    def __init__(self):
        # =========================
        # LOAD CONFIG
        # =========================
        self.settings = load_settings()

        # ===== MinIO config =====
        minio_cfg = self.settings["minio"]
        self.MAIN_BUCKET = minio_cfg["minio_bucket_name"]
        self.RAW_PREFIX = "raw_data/"
        self.PROCESSED_PREFIX = "processed_data/"

        # ===== Groq config =====
        groq_cfg = self.settings["groq"]
        self.groq_api_key = groq_cfg["groq_api_key"]

        # =========================
        # INIT MINIO CLIENT
        # =========================
        self.minio_client = Minio(
            minio_cfg["minio_endpoint"],
            access_key=minio_cfg["minio_username"],
            secret_key=minio_cfg["minio_password"],
            secure=False,
        )

        # =========================
        # INIT LLM CHAIN
        # =========================
        SUMMARY_PROMPT = """
        You are an assistant tasked with summarizing text extracted from a PDF.
        Give a concise and clear summary.

        Respond ONLY with the summary.
        Text: {element}
        """

        prompt = ChatPromptTemplate.from_template(SUMMARY_PROMPT)

        model = ChatGroq(
            api_key=self.groq_api_key,
            model="llama-3.1-8b-instant",
            temperature=0.5,
        )

        self.summary_chain = prompt | model | StrOutputParser()

    # ======================================================
    # CHUNK PDF (RAM → RAM)
    # ======================================================
    def get_chunks_from_pdf(self, file_buffer):
        pdf_bytes = file_buffer.read()
        pdf_io = io.BytesIO(pdf_bytes)
        pdf_io.seek(0)

        chunks = partition_pdf(
            file=pdf_io,
            strategy="hi_res",
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
    # UPLOAD JSON TO MINIO
    # ======================================================
    def upload_json_to_minio(self, object_name: str, data: dict):
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")

        self.minio_client.put_object(
            bucket_name=self.MAIN_BUCKET,
            object_name=object_name,
            data=io.BytesIO(payload),
            length=len(payload),
            content_type="application/json",
        )

    # ======================================================
    # MAIN PIPELINE
    # ======================================================
    def process_all_pdfs(self):
        for object_name, file_buffer in get_data_from_minio(self.RAW_PREFIX):

            if not object_name.lower().endswith(".pdf"):
                continue

            print(f"\nProcessing: {object_name}")
            doc_id = Path(object_name).stem

            # 1️⃣ CHUNK
            chunks = self.get_chunks_from_pdf(file_buffer)

            text_chunks = [
                ch for ch in chunks
                if hasattr(ch, "text") and ch.text and ch.text.strip()
            ]

            print(f"Found {len(text_chunks)} text chunks")

            # 2️⃣ SUMMARY + STORE
            for idx, chunk in enumerate(text_chunks):

                summary = self.summary_chain.invoke({
                    "element": chunk.text
                })

                record = {
                    "id": str(uuid.uuid4()),
                    "content": {
                        "text": chunk.text,
                        "summary": summary,
                    },
                    "metadata": {
                        "doc_id": doc_id,
                        "page": getattr(chunk.metadata, "page_number", None),
                        "chunk_index": idx,
                        "source": f"minio://{self.MAIN_BUCKET}/{object_name}",
                        "type": "text",
                    }
                }

                object_path = (
                    f"{self.PROCESSED_PREFIX}"
                    f"{doc_id}/"
                    f"chunk_{idx}.json"
                )

                self.upload_json_to_minio(
                    object_name=object_path,
                    data=record,
                )

                print(f"Uploaded: {object_path}")

                time.sleep(1.2)

            print(f"DONE: {doc_id}")


if __name__ == "__main__":
    pipeline = PDFProcessingPipeline()
    pipeline.process_all_pdfs()
