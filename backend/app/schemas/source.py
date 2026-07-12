from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: int
    document_uid: str
    title: str | None = None
    language: str | None = None
    source_type: str | None = None
    truth_level: str | None = None
    file_path: str

    class Config:
        from_attributes = True