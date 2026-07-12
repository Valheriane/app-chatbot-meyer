from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse, SourceResponse
from app.services.rag_service import ask_rag


router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        result = ask_rag(
            db=db,
            question=request.question,
            conversation_id=request.conversation_id,
            mode=request.mode,
            k=request.k,
            verbosity=request.verbosity,
            temperature=request.temperature,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    sources = [
        SourceResponse(
            chunk_id=source["chunk_id"],
            document_id=source["document_id"],
            source_name=source.get("file_path"),
            title=source.get("title"),
            language=source.get("language"),
            truth_level=source.get("truth_level"),
            source_type=source.get("source_type"),
            score=float(source.get("score", 0)),
            content=source.get("content", ""),
        )
        for source in result["sources"]
    ]

    return ChatResponse(
        conversation_id=result["conversation_id"],
        answer=result["answer"],
        sources=sources,
    )