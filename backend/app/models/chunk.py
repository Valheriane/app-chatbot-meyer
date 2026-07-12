from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import settings
from app.core.database import Base


class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), index=True)
    chunk_index: Mapped[int] = mapped_column(Integer)

    section_title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    content: Mapped[str] = mapped_column(Text)

    language: Mapped[str | None] = mapped_column(String(100), nullable=True)
    truth_level: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source_type: Mapped[str | None] = mapped_column(String(100), nullable=True)

    embedding: Mapped[list[float]] = mapped_column(Vector(settings.embedding_dim))

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="chunks")