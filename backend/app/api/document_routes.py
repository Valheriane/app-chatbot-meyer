from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.document import Document
from app.schemas.source import DocumentResponse

from app.models.chunk import Chunk


router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("", response_model=list[DocumentResponse])
def list_documents(db: Session = Depends(get_db)):
    return db.query(Document).order_by(Document.id.desc()).all()

@router.get("/stats")
def stats(db: Session = Depends(get_db)):
    document_count = db.query(Document).count()
    chunk_count = db.query(Chunk).count()

    return {
        "documents": document_count,
        "chunks": chunk_count,
    }