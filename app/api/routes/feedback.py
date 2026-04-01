from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.repositories import (
    ConversationRepository,
    MessageRepository,
    TicketRepository,
    TicketEventRepository,
)
from app.schemas.feedback import FeedbackRequest, FeedbackResponse
from app.services import FeedbackService

router = APIRouter()


@router.post("", response_model=FeedbackResponse)
async def submit_feedback(
    payload: FeedbackRequest,
    db: AsyncSession = Depends(get_db),
):
    conversation_repo = ConversationRepository(db)
    message_repo = MessageRepository(db)
    ticket_repo = TicketRepository(db)
    ticket_event_repo = TicketEventRepository(db)

    service = FeedbackService(
        conversation_repo=conversation_repo,
        message_repo=message_repo,
        ticket_repo=ticket_repo,
        ticket_event_repo=ticket_event_repo,
    )

    result = await service.submit_feedback(
        conversation_id=payload.conversation_id,
        message_id=payload.message_id,
        user_id=payload.user_id,
        rating=payload.rating,
        feedback_text=payload.feedback_text,
        create_ticket=payload.create_ticket,
    )

    return FeedbackResponse(**result)