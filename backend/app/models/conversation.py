from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    mode: Mapped[str] = mapped_column(String(100), default="search")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")