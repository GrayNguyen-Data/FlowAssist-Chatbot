from unstructured.partition.pdf import partition_pdf
from loader import get_raw_data_from_minio
import sys
from pathlib import Path
import io

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def process_pdf_from_minio(prefix: str = "raw_data/"):
    for object_name, file_buffer in get_raw_data_from_minio(prefix=prefix):
        if object_name.endswith(".pdf"):
                # đọc buffer -> bytes
                pdf_bytes = file_buffer.read()

                # tạo BytesIO mới 
                pdf_io = io.BytesIO(pdf_bytes)
                pdf_io.seek(0)
                chunks = partition_pdf(
                    file=pdf_io,                       # buffer
                    strategy="fast",
                    chunking_strategy="by_title",
                    max_characters=10000,
                    combine_text_under_n_chars=2000,
                    new_after_n_chars=6000,
                )
                table = [], text = []
                for chunk in chunks:
                    if "Table" in str(type(chunk)):
                          table.append(chunk)
                    if "CompositeElement" in str(type(chunk)):
                         text.append(chunk)
def get_image_base64(chunks):
    images_b64 = []
    for chunk in chunks:
          if "CompositeElement" in str(type(chunk)):
               chunk_els = chunk.metadata.orig_elements
               for el in chunk_els:
                    if "Image" in str(type(el)):
                         images_b64.append(el.metadata.image_base64)
    return images_b64



    