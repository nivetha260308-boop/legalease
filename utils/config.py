from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    gemini_api_key: str = Field(
        default="",
        validation_alias="GEMINI_API_KEY"
    )

    gemini_model: str = Field(
        default="gemini-2.5-flash",
        validation_alias="GEMINI_MODEL"
    )

    demo_mode: bool = Field(
        default=True,
        validation_alias="DEMO_MODE"
    )

    backend_host: str = Field(
        default="127.0.0.1",
        validation_alias="BACKEND_HOST"
    )

    backend_port: int = Field(
        default=8000,
        validation_alias="BACKEND_PORT"
    )

    frontend_api_url: str = Field(
        default="http://127.0.0.1:8000",
        validation_alias="FRONTEND_API_URL"
    )

    allowed_origins: str = Field(
        default="http://localhost:8501,http://127.0.0.1:8501",
        validation_alias="ALLOWED_ORIGINS"
    )

    max_document_chars: int = Field(
        default=30000,
        validation_alias="MAX_DOCUMENT_CHARS"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.allowed_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()