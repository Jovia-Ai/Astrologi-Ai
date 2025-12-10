"""Synastry pair persistence helpers."""
from __future__ import annotations

from app.services.supabase import supabase


def create_synastry_pair(user_id: str, partner_id: str):
    response = (
        supabase.table("synastry_pairs")
        .insert(
            {
                "user_id": user_id,
                "partner_id": partner_id,
            }
        )
        .execute()
    )
    return response.data


def get_synastry_pairs(user_id: str):
    response = (
        supabase.table("synastry_pairs")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )
    return response.data
