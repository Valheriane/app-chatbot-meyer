from pydantic import BaseModel



class ChatRequest(BaseModel):
    question: str
    conversation_id: int | None = None
    mode: str = "search"
    k: int = 6
    verbosity: str = "normal"
    temperature: float = 0.2


class SourceResponse(BaseModel):
    chunk_id: int
    document_id: int
    source_name: str | None = None
    title: str | None = None
    language: str | None = None
    truth_level: str | None = None
    source_type: str | None = None
    score: float
    content: str


class ChatResponse(BaseModel):
    conversation_id: int
    answer: str
    sources: list[SourceResponse]

