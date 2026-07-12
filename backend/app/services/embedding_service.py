from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.core.config import settings


@lru_cache
def get_embedding_model():
    return SentenceTransformer(settings.embedding_model)


def embed_passages(texts: list[str]) -> list[list[float]]:
    model = get_embedding_model()
    passages = [f"passage: {text}" for text in texts]
    vectors = model.encode(passages, normalize_embeddings=True)
    return vectors.tolist()


def embed_query(question: str) -> list[float]:
    model = get_embedding_model()
    vector = model.encode([f"query: {question}"], normalize_embeddings=True)
    return vector[0].tolist()