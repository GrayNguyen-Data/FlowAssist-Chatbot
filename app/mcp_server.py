from mcp.server.fastmcp import FastMCP

from app.db.repositories import (
    ConversationRepository,
    MessageRepository,
    TicketRepository,
    TicketEventRepository,
)
from app.services import RetrievalService, TicketService
from app.db.session import AsyncSessionLocal

mcp = FastMCP(
    "FlowAssist MCP",
    stateless_http=True,
    json_response=True,
)

mcp.settings.streamable_http_path = "/"


@mcp.tool()
async def search_knowledge(query: str, top_k: int = 5) -> dict:
    """
    Search the FlowAssist knowledge base and return retrieved contexts.
    """
    async with AsyncSessionLocal() as db:
        service = RetrievalService(db)
        result = await service.retrieve_debug(query)

        return {
            "query": result["query"],
            "results": result["results"][:top_k],
            "contexts": result["contexts"][:top_k],
        }


@mcp.tool()
async def get_conversation_messages(conversation_id: str) -> list[dict]:
    """
    Get all messages for a conversation.
    """
    async with AsyncSessionLocal() as db:
        conversation_repo = ConversationRepository(db)
        message_repo = MessageRepository(db)

        conversation = await conversation_repo.get_by_id(conversation_id)
        if not conversation:
            return []

        messages = await message_repo.list_by_conversation(conversation_id)
        return [
            {
                "message_id": msg.message_id,
                "conversation_id": msg.conversation_id,
                "role": msg.role,
                "content": msg.content,
                "model_name": msg.model_name,
                "status": msg.status,
                "created_at": msg.created_at.isoformat() if msg.created_at else None,
            }
            for msg in messages
        ]


@mcp.tool()
async def create_ticket(
    conversation_id: str,
    user_id: str | None = None,
    title: str | None = None,
    user_input: str | None = None,
    wrong_answer: str | None = None,
    feedback: str | None = None,
    priority: str = "normal",
) -> dict:
    """
    Create a support ticket linked to a conversation.
    """
    async with AsyncSessionLocal() as db:
        conversation_repo = ConversationRepository(db)
        ticket_repo = TicketRepository(db)
        ticket_event_repo = TicketEventRepository(db)

        service = TicketService(
            conversation_repo=conversation_repo,
            ticket_repo=ticket_repo,
            ticket_event_repo=ticket_event_repo,
        )

        ticket = await service.create_ticket(
            conversation_id=conversation_id,
            user_id=user_id,
            title=title,
            user_input=user_input,
            wrong_answer=wrong_answer,
            feedback=feedback,
            priority=priority,
        )

        return {
            "ticket_id": ticket.ticket_id,
            "conversation_id": ticket.conversation_id,
            "status": ticket.status,
            "priority": ticket.priority,
            "title": ticket.title,
            "feedback": ticket.feedback,
        }


@mcp.tool()
async def get_ticket(ticket_id: str) -> dict | None:
    """
    Get a ticket by id.
    """
    async with AsyncSessionLocal() as db:
        ticket_repo = TicketRepository(db)
        ticket = await ticket_repo.get_by_id(ticket_id)
        if not ticket:
            return None

        return {
            "ticket_id": ticket.ticket_id,
            "conversation_id": ticket.conversation_id,
            "user_id": ticket.user_id,
            "title": ticket.title,
            "user_input": ticket.user_input,
            "wrong_answer": ticket.wrong_answer,
            "feedback": ticket.feedback,
            "status": ticket.status,
            "priority": ticket.priority,
            "created_at": ticket.created_at.isoformat() if ticket.created_at else None,
            "resolved_at": ticket.resolved_at.isoformat() if ticket.resolved_at else None,
            "resolved_by": ticket.resolved_by,
            "resolution": ticket.resolution,
        }


@mcp.resource("conversation://{conversation_id}")
async def conversation_resource(conversation_id: str) -> str:
    """
    Read a conversation as a plain text resource.
    """
    async with AsyncSessionLocal() as db:
        conversation_repo = ConversationRepository(db)
        message_repo = MessageRepository(db)

        conversation = await conversation_repo.get_by_id(conversation_id)
        if not conversation:
            return "Conversation not found"

        messages = await message_repo.list_by_conversation(conversation_id)

        lines = [
            f"Conversation ID: {conversation.conversation_id}",
            f"User ID: {conversation.user_id}",
            f"Title: {conversation.title}",
            f"Status: {conversation.status}",
            f"Channel: {conversation.channel}",
            "",
            "Messages:",
        ]

        for msg in messages:
            lines.append(f"[{msg.role}] {msg.content}")

        return "\n".join(lines)


@mcp.resource("ticket://{ticket_id}")
async def ticket_resource(ticket_id: str) -> str:
    """
    Read a ticket as a plain text resource.
    """
    async with AsyncSessionLocal() as db:
        ticket_repo = TicketRepository(db)
        ticket_event_repo = TicketEventRepository(db)

        ticket = await ticket_repo.get_by_id(ticket_id)
        if not ticket:
            return "Ticket not found"

        events = await ticket_event_repo.list_by_ticket(ticket_id)

        lines = [
            f"Ticket ID: {ticket.ticket_id}",
            f"Conversation ID: {ticket.conversation_id}",
            f"Status: {ticket.status}",
            f"Priority: {ticket.priority}",
            f"Title: {ticket.title}",
            f"Feedback: {ticket.feedback}",
            "",
            "Events:",
        ]

        for ev in events:
            lines.append(f"[{ev.event_type}] actor={ev.actor} note={ev.note}")

        return "\n".join(lines)