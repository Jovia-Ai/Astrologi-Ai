"""Central configuration management for the Astrologi-AI backend."""
from __future__ import annotations

from pathlib import Path
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.env import BASE_DIR, load_environment

# Ensure .env variables are loaded before Settings is instantiated.
load_environment()


class Settings(BaseSettings):
    """Pydantic powered settings object with sane defaults."""

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    debug: bool = Field(default=False, env="DEBUG")
    allowed_origins: List[str] = Field(default_factory=lambda: ["http://localhost:5173"], env="ALLOWED_ORIGINS")
    swisseph_path: str = Field(default="./ephe", env="SWISSEPH_PATH")
    opencage_api_key: str | None = Field(default=None, env="OPENCAGE_API_KEY")
    groq_api_key: str | None = Field(default=None, env="GROQ_API_KEY")
    groq_model: str = Field(default="llama-3.1-8b-instant", env="GROQ_MODEL")
    groq_api_url: str = Field(default="https://api.groq.com/openai/v1/chat/completions", env="GROQ_API_URL")
    cors_supports_credentials: bool = Field(default=True, env="CORS_SUPPORTS_CREDENTIALS")
    environment: str = Field(default="development", env="APP_ENV")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    supabase_url: str | None = Field(default=None, env="SUPABASE_URL")
    supabase_anon_key: str | None = Field(default=None, env="SUPABASE_ANON_KEY")
    supabase_service_role_key: str | None = Field(default=None, env="SUPABASE_SERVICE_ROLE_KEY")
    house_system: str = Field(default="P", env="HOUSE_SYSTEM")

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def _split_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator("house_system", mode="before")
    @classmethod
    def _normalize_house_system(cls, value: str | None) -> str:
        if not value:
            return "P"
        normalized = str(value).strip().upper()
        return normalized if normalized in {"P", "O", "E"} else "P"

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


settings = Settings()
PROJECT_ROOT = Path(__file__).resolve().parents[3]
