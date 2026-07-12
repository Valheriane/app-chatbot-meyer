from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id"), index=True)

    role: Mapped[str] = mapped_column(String(50))
    content: Mapped[str] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")
    sources = relationship("MessageSource", back_populates="message", cascade="all, delete-orphan")


class MessageSource(Base):
    __tablename__ = "message_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    message_id: Mapped[int] = mapped_column(ForeignKey("messages.id"), index=True)
    chunk_id: Mapped[int] = mapped_column(ForeignKey("chunks.id"), index=True)

    score: Mapped[float] = mapped_column(Float)
    rank: Mapped[int] = mapped_column(Integer)

    message = relationship("Message", back_populates="sources")