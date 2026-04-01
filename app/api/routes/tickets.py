from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.repositories import (
    ConversationRepository,
    TicketRepository,
    TicketEventRepository,
)
from app.schemas.ticket import (
    TicketCreateRequest,
    TicketUpdateRequest,
    TicketResponse,
    TicketEventResponse,
)
from app.services import TicketService

router = APIRouter()


@router.post("", response_model=TicketResponse)
async def create_ticket(
    payload: TicketCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    conversation_repo = ConversationRepository(db)
    ticket_repo = TicketRepository(db)
    ticket_event_repo = TicketEventRepository(db)

    service = TicketService(
        conversation_repo=conversation_repo,
        ticket_repo=ticket_repo,
        ticket_event_repo=ticket_event_repo,
    )

    return await service.create_ticket(
        conversation_id=payload.conversation_id,
        user_id=payload.user_id,
        title=payload.title,
        user_input=payload.user_input,
        wrong_answer=payload.wrong_answer,
        feedback=payload.feedback,
        priority=payload.priority,
    )


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: str,
    db: AsyncSession = Depends(get_db),
):
    conversation_repo = ConversationRepository(db)
    ticket_repo = TicketRepository(db)
    ticket_event_repo = TicketEventRepository(db)

    service = TicketService(
        conversation_repo=conversation_repo,
        ticket_repo=ticket_repo,
        ticket_event_repo=ticket_event_repo,
    )

    return await service.get_ticket(ticket_id)


@router.patch("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(
    ticket_id: str,
    payload: TicketUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    conversation_repo = ConversationRepository(db)
    ticket_repo = TicketRepository(db)
    ticket_event_repo = TicketEventRepository(db)

    service = TicketService(
        conversation_repo=conversation_repo,
        ticket_repo=ticket_repo,
        ticket_event_repo=ticket_event_repo,
    )

    return await service.update_ticket(
        ticket_id=ticket_id,
        status=payload.status,
        resolved_by=payload.resolved_by,
        resolution=payload.resolution,
        note=payload.note,
    )


@router.get("/conversation/{conversation_id}", response_model=list[TicketResponse])
async def list_conversation_tickets(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
):
    conversation_repo = ConversationRepository(db)
    ticket_repo = TicketRepository(db)
    ticket_event_repo = TicketEventRepository(db)

    service = TicketService(
        conversation_repo=conversation_repo,
        ticket_repo=ticket_repo,
        ticket_event_repo=ticket_event_repo,
    )

    return await service.list_conversation_tickets(conversation_id)


@router.get("/{ticket_id}/events", response_model=list[TicketEventResponse])
async def list_ticket_events(
    ticket_id: str,
    db: AsyncSession = Depends(get_db),
):
    conversation_repo = ConversationRepository(db)
    ticket_repo = TicketRepository(db)
    ticket_event_repo = TicketEventRepository(db)

    service = TicketService(
        conversation_repo=conversation_repo,
        ticket_repo=ticket_repo,
        ticket_event_repo=ticket_event_repo,
    )

    return await service.list_ticket_events(ticket_id)