from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    document_uid: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)

    date_original: Mapped[str | None] = mapped_column(String(50), nullable=True)
    manuscript: Mapped[str | None] = mapped_column(String(255), nullable=True)

    source_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    language: Mapped[str | None] = mapped_column(String(100), nullable=True)
    original_language: Mapped[str | None] = mapped_column(String(100), nullable=True)

    weapon: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tradition: Mapped[str | None] = mapped_column(String(100), nullable=True)

    source_platform: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    translator: Mapped[str | None] = mapped_column(String(255), nullable=True)
    transcriber: Mapped[str | None] = mapped_column(String(255), nullable=True)

    truth_level: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str | None] = mapped_column(String(100), nullable=True)

    file_path: Mapped[str] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")