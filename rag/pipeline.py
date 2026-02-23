from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import sys
from pathlib import Path

# =========================
# PATH SETUP
# =========================
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from rag.retrieval.retriever import TiDBRetriever
from core.setting_loader import load_settings


class RAGPipeline:

    def __init__(self, top_k: int = 5):
        self.retriever = TiDBRetriever(top_k=top_k)

        settings = load_settings()
        groq_cfg = settings["groq"]

        self.llm = ChatGroq(
            api_key=groq_cfg["groq_api_key"],
            model="llama-3.1-8b-instant",
            temperature=0.3,
        )

        self.prompt = ChatPromptTemplate.from_template("""
You are a helpful assistant.
Answer the question using ONLY the provided context.

Context:
{context}

Question:
{question}
""")

        self.chain = self.prompt | self.llm | StrOutputParser()

    def build_context(self, docs):
        return "\n\n".join([doc["summary"] for doc in docs])

    def run(self, question: str):

        # Retrieve
        docs = self.retriever.search(question)

        if not docs:
            return "No relevant documents found."

        # Build context
        context = self.build_context(docs)

        # Generate answer
        answer = self.chain.invoke({
            "context": context,
            "question": question
        })

        return answer


if __name__ == "__main__":
    rag = RAGPipeline(top_k=5)
    response = rag.run("Who is Phan Thi Huyen Trang?")
    print(response)