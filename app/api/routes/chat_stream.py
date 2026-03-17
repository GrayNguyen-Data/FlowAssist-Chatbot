import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.repositories import (
    ConversationRepository,
    MessageRepository,
    RetrievalLogRepository,
)
from app.schemas.chat import ChatRequest
from app.services import ChatService

router = APIRouter()


@router.post("")
async def chat_stream(
    payload: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    conversation_repo = ConversationRepository(db)
    message_repo = MessageRepository(db)
    retrieval_log_repo = RetrievalLogRepository(db)

    service = ChatService(
        conversation_repo=conversation_repo,
        message_repo=message_repo,
        retrieval_log_repo=retrieval_log_repo,
    )

    async def event_generator():
        try:
            yield f"data: {json.dumps({'event': 'start', 'conversation_id': payload.conversation_id})}\n\n"

            result = await service.chat(
                conversation_id=payload.conversation_id,
                user_message=payload.message,
            )

            yield f"data: {json.dumps({'event': 'retrieval', 'contexts': result['retrieved_context']}, ensure_ascii=False)}\n\n"

            yield f"data: {json.dumps({'event': 'message', 'assistant_message': result['assistant_message']}, ensure_ascii=False)}\n\n"

            yield f"data: {json.dumps({'event': 'done'}, ensure_ascii=False)}\n\n"

        except ValueError as e:
            yield f"data: {json.dumps({'event': 'error', 'detail': str(e)}, ensure_ascii=False)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'event': 'error', 'detail': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )