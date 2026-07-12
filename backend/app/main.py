from fastapi import FastAPI

from app.api.chat_routes import router as chat_router
from app.api.conversation_routes import router as conversation_router
from app.api.document_routes import router as document_router
from app.core.database import Base, engine, init_pgvector



# Important : importer les modèles pour que SQLAlchemy les connaisse
from app import models  # noqa: F401


app = FastAPI(
    title="Meyer RAG API",
    description="Backend RAG pour Joachim Meyer à l'épée longue.",
    version="0.1.0",
)


@app.on_event("startup")
def startup():
    init_pgvector()
    Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {
        "app": "Meyer RAG API",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
def health():
    return {"status": "ok"}




app.include_router(chat_router)
app.include_router(conversation_router)
app.include_router(document_router)