from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    groq_api_key: str
    groq_model: str = "llama-3.1-8b-instant"

    embedding_model: str = "intfloat/multilingual-e5-base"
    embedding_dim: int = 768

    data_dir: str = "../data"

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()