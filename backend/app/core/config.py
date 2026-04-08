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

    debug: bool = Field(default=False, validation_alias="DEBUG")
    allowed_origins: List[str] = Field(
        default_factory=lambda: ["http://localhost:5173"],
        validation_alias="ALLOWED_ORIGINS",
    )
    swisseph_path: str = Field(default="./ephe", validation_alias="SWISSEPH_PATH")
    opencage_api_key: str | None = Field(default=None, validation_alias="OPENCAGE_API_KEY")
    groq_api_key: str | None = Field(default=None, validation_alias="GROQ_API_KEY")
    groq_model: str = Field(default="llama-3.1-8b-instant", validation_alias="GROQ_MODEL")
    groq_api_url: str = Field(
        default="https://api.groq.com/openai/v1/chat/completions",
        validation_alias="GROQ_API_URL",
    )
    cors_supports_credentials: bool = Field(default=True, validation_alias="CORS_SUPPORTS_CREDENTIALS")
    environment: str = Field(default="development", validation_alias="APP_ENV")
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    supabase_url: str | None = Field(default=None, validation_alias="SUPABASE_URL")
    supabase_anon_key: str | None = Field(default=None, validation_alias="SUPABASE_ANON_KEY")
    supabase_service_role_key: str | None = Field(default=None, validation_alias="SUPABASE_SERVICE_ROLE_KEY")
    house_system: str = Field(default="P", validation_alias="HOUSE_SYSTEM")
    enable_home_fast_cache: bool = Field(default=True, validation_alias="ENABLE_HOME_FAST_CACHE")
    enable_home_deep_cache: bool = Field(default=True, validation_alias="ENABLE_HOME_DEEP_CACHE")
    enable_stale_while_revalidate: bool = Field(default=True, validation_alias="ENABLE_STALE_WHILE_REVALIDATE")
    enable_background_refresh: bool = Field(default=True, validation_alias="ENABLE_BACKGROUND_REFRESH")
    enable_timing_logs: bool = Field(default=True, validation_alias="ENABLE_TIMING_LOGS")
    global_transits_ttl_seconds: int = Field(default=3600, validation_alias="GLOBAL_TRANSITS_TTL_SECONDS")
    global_transits_stale_ttl_seconds: int = Field(default=43200, validation_alias="GLOBAL_TRANSITS_STALE_TTL_SECONDS")
    transit_narrative_ttl_seconds: int = Field(default=900, validation_alias="TRANSIT_NARRATIVE_TTL_SECONDS")
    transit_narrative_stale_ttl_seconds: int = Field(
        default=1800,
        validation_alias="TRANSIT_NARRATIVE_STALE_TTL_SECONDS",
    )
    home_fast_ttl_seconds: int = Field(default=1800, validation_alias="HOME_FAST_TTL_SECONDS")
    home_fast_stale_ttl_seconds: int = Field(default=3600, validation_alias="HOME_FAST_STALE_TTL_SECONDS")
    home_deep_ttl_seconds: int = Field(default=7200, validation_alias="HOME_DEEP_TTL_SECONDS")
    home_deep_stale_ttl_seconds: int = Field(default=14400, validation_alias="HOME_DEEP_STALE_TTL_SECONDS")

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

    @field_validator("swisseph_path", mode="before")
    @classmethod
    def _resolve_swisseph_path(cls, value: str | None) -> str:
        raw = (value or "./ephe").strip()
        path = Path(raw)
        if path.is_absolute():
            return str(path)
        return str((BASE_DIR / path).resolve())

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


settings = Settings()
PROJECT_ROOT = Path(__file__).resolve().parents[3]
