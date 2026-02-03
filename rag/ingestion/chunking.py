from unstructured.partition.pdf import partition_pdf
from loader import get_raw_data_from_minio
import sys
from pathlib import Path
import io
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from core.setting_loader import load_settings
import time 
from langchain_openai import ChatOpenAl

# ===== load env =====
setting = load_settings()
groq_config = setting['groq']
groq_api_key = groq_config['groq_api_key']


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
# tách các phần của PDF Unsstructure -> text, img, table 
def get_chunks_from_pdf(file_buffer):
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
        extract_images_in_pdf=True,
        infer_table_structure=True,
        include_page_breaks=False,
    )
    return chunks

def process_pdf_from_minio(prefix: str = "raw_data/"):
    for object_name, file_buffer in get_raw_data_from_minio(prefix=prefix):
        if object_name.endswith(".pdf"):
            chunks = get_chunks_from_pdf(file_buffer)

            tables = []
            texts = []
            images_b64 = []

            for chunk in chunks:
                if "CompositeElement" in str(type(chunk)):
                    texts.append(chunk)

                    if hasattr(chunk.metadata, "orig_elements"): # tức là kiểm tra xem orig_elements có trong chunk metadataa không
                        for el in chunk.metadata.orig_elements:
                            if "Table" in str(type(el)):
                                tables.append(el)

                            if "Image" in str(type(el)):
                                images_b64.append(el.metadata.image_base64)

            print(f"Found {len(tables)} tables")
            print(f"Found {len(texts)} text chunks")
            print(f"Found {len(images_b64)} images")

            return tables, texts, images_b64


# summary nó nhờ vào model 

# config prompt cho table và text
prompt_text = """
You are an assist tasked with summarizing tables and text.
Give a concise summary of the table or text.

Respond only with the summary, no additional comment.
Do not start your message by saying "Here is a summary" or any thing like chat. 
Just give the summary at it is.

Table or text chunk: {element}
"""

prompt = ChatPromptTemplate.from_template(prompt_text)

# summary chain 
model = ChatGroq(
    api_key=groq_api_key,
    temperature=0.5,
    model="llama-3.1-8b-instant"
)
summary_chain = prompt | model | StrOutputParser()


def summary(elements, delay = 1.5):
    results = []
    for element in elements:
        res = summary_chain.invoke({'element': element})
        results.append(res)
        time.sleep(delay)
    return results

# ==== Summary image ====




