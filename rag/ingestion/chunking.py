from unstructured.partition.pdf import partition_pdf
from loader import get_raw_data_from_minio
import sys
from pathlib import Path
import io
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# tách các phần của PDF Unsstructure -> text, img, table 
def get_chunks_from_pdf(file_buffer):
    pdf_bytes = file_buffer.read()
    pdf_io = io.BytesIO(pdf_bytes)
    pdf_io.seek(0)
    
    chunks = partition_pdf(
        file=pdf_io,
        strategy="fast",
        chunking_strategy="by_title",
        max_characters=4000,
        combine_text_under_n_chars=1000,
        new_after_n_chars=3000,
        extract_images_in_pdf=True,
        infer_table_structure=True,
        include_page_breaks=False,
    )
    return chunks

def process_pdf_from_minio(prefix: str = "raw_data/"):
    for object_name, file_buffer in get_raw_data_from_minio(prefix=prefix):
        if object_name.endswith(".pdf"):
                chunks = get_chunks_from_pdf(file_buffer)
                
                table = []
                text = []
                images_b64 = []
                
                for chunk in chunks:
                    if "Table" in str(type(chunk)):
                          table.append(chunk)
                          
                    if "CompositeElement" in str(type(chunk)):
                         text.append(chunk)
                         
                         chunk_els = chunk.metadata.orig_elements
                         for el in chunk_els:
                              if "Image" in str(type(el)):
                                   images_b64.append(el.metadata.image_base64)
                
                return table, text, images_b64

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
model = ChatGroq(temperature=0.5, model = 'llama-3.1-8b-instant')
summary_chain = {"element": lambda x: x} | prompt | model | StrOutputParser()


