from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.embedding_service import embed_query


def retrieve_chunks(db: Session, question: str, k: int = 6) -> list[dict]:
    query_vector = embed_query(question)

    sql = text(
        """
        SELECT
            chunks.id AS chunk_id,
            chunks.document_id AS document_id,
            chunks.content AS content,
            chunks.language AS language,
            chunks.truth_level AS truth_level,
            chunks.source_type AS source_type,
            chunks.section_title AS section_title,
            documents.title AS title,
            documents.file_path AS file_path,
            documents.document_uid AS document_uid,
            1 - (chunks.embedding <=> CAST(:query_vector AS vector)) AS score
        FROM chunks
        JOIN documents ON documents.id = chunks.document_id
        ORDER BY chunks.embedding <=> CAST(:query_vector AS vector)
        LIMIT :k
        """
    )

    rows = db.execute(
        sql,
        {
            "query_vector": str(query_vector),
            "k": k,
        },
    ).mappings().all()

    return [dict(row) for row in rows]