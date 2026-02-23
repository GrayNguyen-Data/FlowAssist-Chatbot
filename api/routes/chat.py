from fastapi import APIRouter
from pydantic import BaseModel

# Example of using LangSmith tracer with an LLM for chat responses
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from langchain.tracers import LangSmithTracer

router = APIRouter()

# configure tracer once
tracer = LangSmithTracer()
tracer.load_default_session()

class ChatRequest(BaseModel):
    user_input: str

@router.post("/reply")
def reply(req: ChatRequest):
    llm = ChatOpenAI(temperature=0.5, callbacks=[tracer])
    # simple echo or you could integrate RAG pipeline here
    resp = llm.predict_messages([HumanMessage(content=req.user_input)])
    return {"reply": resp.content}
