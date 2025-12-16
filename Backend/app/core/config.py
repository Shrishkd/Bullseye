# app/core/config.py

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    PROJECT_NAME: str = "Bullseye Backend"

    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./bullseye.db"
    )

    SECRET_KEY: str = "dev-secret-key"

    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    FINNHUB_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
