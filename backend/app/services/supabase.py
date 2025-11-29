"""Supabase client initialisation."""
from __future__ import annotations

from supabase import create_client

from app.core.config import Settings

settings = Settings()

supabase = create_client(
    settings.supabase_url,
    settings.supabase_anon_key,
)
