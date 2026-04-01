from fastapi import APIRouter

from app.api.routes.health import router as router_health
from app.api.routes.db_test import router as db_test_router
from app.api.routes.conversations import router as conversations_router
from app.api.routes.messages import router as messages_router
from app.api.routes.memory import router as memory_router
from app.api.routes.chat import router as chat_router
from app.api.routes.retrieval import router as retrieval_router
from app.api.routes.ingestion import router as ingestion_router
from app.api.routes.chat_stream import router as chat_stream_router
from app.api.routes.tickets import router as tickets_router
from app.api.routes.feedback import router as feedback_router
from app.api.routes.documents import router as documents_router
api_router = APIRouter()

api_router.include_router(router_health, prefix="/health", tags=["Health"])
api_router.include_router(db_test_router, prefix="/db", tags=["Database"])
api_router.include_router(conversations_router, prefix="/conversations", tags=["Conversations"])
api_router.include_router(messages_router, prefix="/messages", tags=["Messages"])
api_router.include_router(memory_router, prefix="/memory", tags=["Memory"])
api_router.include_router(chat_router, prefix="/chat", tags=["Chat"])
api_router.include_router(retrieval_router, prefix="/retrieval", tags=["Retrieval"])
api_router.include_router(ingestion_router, prefix="/ingestion", tags=["Ingestion"])
api_router.include_router(chat_stream_router, prefix="/chat/stream", tags=["Chat Stream"])
api_router.include_router(tickets_router, prefix="/tickets", tags=["Tickets"])
api_router.include_router(feedback_router, prefix="/feedback", tags=["Feedback"])
api_router.include_router(documents_router, prefix="/documents", tags=["Documents"])