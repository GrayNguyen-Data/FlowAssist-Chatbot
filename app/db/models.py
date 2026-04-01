from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column,
    String,
    Integer,
    BigInteger,
    Text,
    DateTime,
    ForeignKey,
    JSON,
)
import datetime
import uuid

from app.db.base import Base


class RagMetadata(Base):
    __tablename__ = "rag_metadata"

    doc_id = Column(String(255), primary_key=True, nullable=False, index=True)
    doc_metadata = Column(JSON, nullable=True)

    embeddings = relationship(
        "RagEmbedding",
        back_populates="meta",
        cascade="all, delete-orphan",
    )

    chunks = relationship(
        "RagChunk",
        back_populates="meta",
        cascade="all, delete-orphan",
    )


class RagEmbedding(Base):
    __tablename__ = "rag_embeddings"

    embed_id = Column(BigInteger, primary_key=True, autoincrement=True)

    doc_id = Column(
        String(255),
        ForeignKey("rag_metadata.doc_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    chunk_index = Column(Integer, nullable=False, index=True)

    summary = Column(Text, nullable=True)

    # Tạm để Text cho dễ migrate.
    # Sau này nếu muốn dùng vector type của TiDB thì sẽ chỉnh ở migration raw SQL.
    summary_vector = Column(Text, nullable=True)

    meta = relationship(
        "RagMetadata",
        back_populates="embeddings",
    )


class RagChunk(Base):
    __tablename__ = "rag_chunks"

    chunk_id = Column(BigInteger, primary_key=True, autoincrement=True)

    doc_id = Column(
        String(255),
        ForeignKey("rag_metadata.doc_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    chunk_index = Column(Integer, nullable=False, index=True)

    chunk_text = Column(Text, nullable=False)

    meta = relationship(
        "RagMetadata",
        back_populates="chunks",
    )


class Conversation(Base):
    __tablename__ = "conversations"

    conversation_id = Column(
        String(255),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        nullable=False,
    )

    user_id = Column(String(255), default="default", nullable=False, index=True)

    title = Column(String(255), nullable=True)
    summary = Column(Text, nullable=True)
    status = Column(String(50), default="active", nullable=False, index=True)
    channel = Column(String(50), default="chat", nullable=False)

    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
    )

    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
    )

    tickets = relationship(
        "Ticket",
        back_populates="conversation",
        cascade="all, delete-orphan",
    )


class Message(Base):
    __tablename__ = "messages"

    message_id = Column(BigInteger, primary_key=True, autoincrement=True)

    conversation_id = Column(
        String(255),
        ForeignKey("conversations.conversation_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    role = Column(String(20), nullable=False)

    content = Column(Text, nullable=False)

    model_name = Column(String(100), nullable=True)
    status = Column(String(50), default="completed", nullable=False)

    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        nullable=False,
    )

    conversation = relationship(
        "Conversation",
        back_populates="messages",
    )

    retrieval_logs = relationship(
        "RetrievalLog",
        back_populates="message",
        cascade="all, delete-orphan",
    )


class Ticket(Base):
    __tablename__ = "tickets"

    ticket_id = Column(
        String(255),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        nullable=False,
    )

    conversation_id = Column(
        String(255),
        ForeignKey("conversations.conversation_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user_id = Column(String(255), nullable=True, index=True)

    title = Column(String(255), nullable=True)
    user_input = Column(Text, nullable=True)
    wrong_answer = Column(Text, nullable=True)
    feedback = Column(Text, nullable=True)

    status = Column(String(20), default="open", nullable=False, index=True)
    priority = Column(String(20), default="normal", nullable=False)

    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        nullable=False,
    )

    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(String(255), nullable=True)
    resolution = Column(Text, nullable=True)

    conversation = relationship(
        "Conversation",
        back_populates="tickets",
    )

    events = relationship(
        "TicketEvent",
        back_populates="ticket",
        cascade="all, delete-orphan",
    )


class TicketEvent(Base):
    __tablename__ = "ticket_events"

    event_id = Column(BigInteger, primary_key=True, autoincrement=True)

    ticket_id = Column(
        String(255),
        ForeignKey("tickets.ticket_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    event_type = Column(String(100), nullable=False)
    actor = Column(String(255), nullable=True)
    note = Column(Text, nullable=True)

    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        nullable=False,
    )

    ticket = relationship(
        "Ticket",
        back_populates="events",
    )


class RetrievalLog(Base):
    __tablename__ = "retrieval_logs"

    retrieval_log_id = Column(BigInteger, primary_key=True, autoincrement=True)

    message_id = Column(
        BigInteger,
        ForeignKey("messages.message_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    query_text = Column(Text, nullable=False)
    rewritten_query = Column(Text, nullable=True)
    results_json = Column(JSON, nullable=True)

    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        nullable=False,
    )

    message = relationship(
        "Message",
        back_populates="retrieval_logs",
    )