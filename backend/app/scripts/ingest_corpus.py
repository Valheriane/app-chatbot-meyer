from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import Base, SessionLocal, engine, init_pgvector
from app.models.chunk import Chunk
from app.models.document import Document
from app.services.chunking_service import chunk_document
from app.services.embedding_service import embed_passages
from app.services.loader_service import load_corpus

from app import models  # noqa: F401


def get_meta(metadata: dict, key: str, default=None):
    return metadata.get(key, default)


def upsert_document(db: Session, metadata: dict) -> Document:
    document_uid = get_meta(metadata, "id") or get_meta(metadata, "document_uid")

    existing = (
        db.query(Document)
        .filter(Document.document_uid == document_uid)
        .first()
    )

    if existing:
        db.query(Chunk).filter(Chunk.document_id == existing.id).delete()
        db.delete(existing)
        db.commit()

    document = Document(
        document_uid=document_uid,
        title=get_meta(metadata, "title"),
        author=get_meta(metadata, "author"),
        date_original=str(get_meta(metadata, "date_original", "")),
        manuscript=get_meta(metadata, "manuscript"),
        source_type=get_meta(metadata, "source_type"),
        language=get_meta(metadata, "language"),
        original_language=get_meta(metadata, "original_language"),
        weapon=get_meta(metadata, "weapon"),
        tradition=get_meta(metadata, "tradition"),
        source_platform=get_meta(metadata, "source_platform"),
        source_url=get_meta(metadata, "source_url"),
        translator=get_meta(metadata, "translator"),
        transcriber=get_meta(metadata, "transcriber"),
        truth_level=get_meta(metadata, "truth_level"),
        status=get_meta(metadata, "status"),
        file_path=get_meta(metadata, "file_path"),
        notes=get_meta(metadata, "notes"),
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document


def ingest():
    init_pgvector()
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        loaded_docs = load_corpus(settings.data_dir)

        print(f"{len(loaded_docs)} documents/pages chargés.")

        for text, metadata in loaded_docs:
            document = upsert_document(db, metadata)
            chunks = chunk_document(text)

            contents = [chunk["content"] for chunk in chunks]
            embeddings = embed_passages(contents)

            for chunk, embedding in zip(chunks, embeddings):
                db.add(
                    Chunk(
                        document_id=document.id,
                        chunk_index=chunk["chunk_index"],
                        section_title=chunk["section_title"],
                        content=chunk["content"],
                        language=document.language,
                        truth_level=document.truth_level,
                        source_type=document.source_type,
                        embedding=embedding,
                    )
                )

            db.commit()
            print(f"Ingestion terminée : {document.document_uid} — {len(chunks)} chunks")

    finally:
        db.close()


if __name__ == "__main__":
    ingest()