"""User account lifecycle helpers."""
from __future__ import annotations

from dataclasses import dataclass
import logging

from app.services.supabase import supabase_admin

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AccountDeletionResult:
    """Result payload for account deletion."""

    user_id: str
    warnings: tuple[str, ...] = ()


def delete_user_account(user_id: str) -> AccountDeletionResult:
    """Delete the auth user and best-effort cleanup owned records."""

    warnings: list[str] = []

    cleanup_targets = (
        ("birth_data", "user_id"),
        ("astro_settings", "user_id"),
        ("archetype_profiles", "user_id"),
        ("ai_entitlements", "user_id"),
        ("ai_usage_events", "user_id"),
        ("revenuecat_webhook_events", "app_user_id"),
        ("stories", "user_id"),
        ("synastry_pairs", "user_id"),
        ("synastry_pairs", "partner_id"),
        ("forum_post_likes", "user_id"),
        ("forum_replies", "user_id"),
        ("forum_posts", "user_id"),
        ("profiles", "id"),
    )

    for table_name, column_name in cleanup_targets:
        try:
            supabase_admin.table(table_name).delete().eq(column_name, user_id).execute()
        except Exception as exc:  # pragma: no cover - environment/schema specific
            logger.warning(
                "Account deletion cleanup skipped for %s.%s user=%s: %s",
                table_name,
                column_name,
                user_id,
                exc,
            )
            warnings.append(f"{table_name}.{column_name}")

    supabase_admin.auth.admin.delete_user(user_id, should_soft_delete=False)
    return AccountDeletionResult(user_id=user_id, warnings=tuple(warnings))
