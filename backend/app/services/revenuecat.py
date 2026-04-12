"""RevenueCat webhook helpers for AI entitlements."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping

from app.services.supabase import supabase_admin

_CREDIT_PRODUCT_MAP = {
    "jovia_q1": 1,
    "jovia_q5": 5,
    "jovia_q15": 15,
}
_PRO_PRODUCT_ID = "jovia_pro_monthly"
_CREDIT_GRANT_EVENT_TYPES = {"INITIAL_PURCHASE", "NON_RENEWING_PURCHASE"}
_PRO_STATE_EVENT_TYPES = {
    "BILLING_ISSUE",
    "CANCELLATION",
    "EXPIRATION",
    "INITIAL_PURCHASE",
    "PRODUCT_CHANGE",
    "RENEWAL",
    "TEMPORARY_ENTITLEMENT_GRANT",
    "UNCANCELLATION",
}


@dataclass(frozen=True)
class RevenueCatProcessResult:
    """Webhook processing result."""

    duplicate: bool
    action: str


@dataclass(frozen=True)
class RevenueCatEvent:
    """Normalized RevenueCat event payload."""

    event_id: str
    event_type: str
    app_user_id: str | None
    product_id: str | None
    expires_at: datetime | None
    raw_payload: Mapping[str, Any]

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any], *, raw_body: str) -> RevenueCatEvent:
        event = payload.get("event") if isinstance(payload.get("event"), Mapping) else payload
        event_id = str(event.get("id") or "").strip() if isinstance(event, Mapping) else ""
        if not event_id:
            event_id = hashlib.sha256(raw_body.encode("utf-8")).hexdigest()
        event_type = str((event or {}).get("type") or "").strip().upper()
        app_user_id = str((event or {}).get("app_user_id") or "").strip() or None
        product_id = str((event or {}).get("product_id") or "").strip() or None
        expires_at = _parse_revenuecat_datetime(event if isinstance(event, Mapping) else {})
        return cls(
            event_id=event_id,
            event_type=event_type,
            app_user_id=app_user_id,
            product_id=product_id,
            expires_at=expires_at,
            raw_payload=payload,
        )


def _parse_revenuecat_datetime(event: Mapping[str, Any]) -> datetime | None:
    expires_ms = event.get("expiration_at_ms")
    if expires_ms is not None:
        try:
            return datetime.fromtimestamp(float(expires_ms) / 1000, tz=timezone.utc)
        except (TypeError, ValueError, OSError):
            return None

    raw_value = event.get("expiration_at")
    if not raw_value:
        return None
    if isinstance(raw_value, datetime):
        return raw_value.astimezone(timezone.utc)
    if isinstance(raw_value, str):
        try:
            return datetime.fromisoformat(raw_value.replace("Z", "+00:00")).astimezone(timezone.utc)
        except ValueError:
            return None
    return None


class RevenueCatWebhookService:
    """Apply RevenueCat events to AI entitlements."""

    def process(self, payload: Mapping[str, Any], *, raw_body: str) -> RevenueCatProcessResult:
        event = RevenueCatEvent.from_payload(payload, raw_body=raw_body)
        if self._is_duplicate(event.event_id):
            return RevenueCatProcessResult(duplicate=True, action="ignored_duplicate")

        (
            supabase_admin.table("revenuecat_webhook_events")
            .insert(
                {
                    "event_id": event.event_id,
                    "event_type": event.event_type or None,
                    "app_user_id": event.app_user_id,
                    "product_id": event.product_id,
                    "payload": dict(event.raw_payload),
                }
            )
            .execute()
        )

        action = self._apply_event(event)
        (
            supabase_admin.table("revenuecat_webhook_events")
            .update({"processed_at": datetime.now(timezone.utc).isoformat()})
            .eq("event_id", event.event_id)
            .execute()
        )
        return RevenueCatProcessResult(duplicate=False, action=action)

    def _is_duplicate(self, event_id: str) -> bool:
        response = (
            supabase_admin.table("revenuecat_webhook_events")
            .select("event_id")
            .eq("event_id", event_id)
            .limit(1)
            .execute()
        )
        return bool(response.data)

    def _apply_event(self, event: RevenueCatEvent) -> str:
        if event.event_type == "TEST":
            return "test_event"
        if not event.app_user_id or not event.product_id:
            return "ignored_missing_identity"

        (
            supabase_admin.table("ai_entitlements")
            .upsert({"user_id": event.app_user_id}, on_conflict="user_id")
            .execute()
        )

        if event.product_id in _CREDIT_PRODUCT_MAP and event.event_type in _CREDIT_GRANT_EVENT_TYPES:
            self._grant_credits(event.app_user_id, _CREDIT_PRODUCT_MAP[event.product_id])
            return f"granted_{_CREDIT_PRODUCT_MAP[event.product_id]}_credits"

        if event.product_id == _PRO_PRODUCT_ID and event.event_type in _PRO_STATE_EVENT_TYPES:
            self._apply_pro_state(event.app_user_id, expires_at=event.expires_at)
            return "updated_pro_state"

        return "ignored_event"

    def _grant_credits(self, user_id: str, credits: int) -> None:
        response = (
            supabase_admin.table("ai_entitlements")
            .select("credits_remaining")
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
        current = int(((response.data or [{}])[0]).get("credits_remaining") or 0)
        (
            supabase_admin.table("ai_entitlements")
            .update({"credits_remaining": max(0, current + credits)})
            .eq("user_id", user_id)
            .execute()
        )

    def _apply_pro_state(self, user_id: str, *, expires_at: datetime | None) -> None:
        response = (
            supabase_admin.table("ai_entitlements")
            .select("pro_until")
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
        current_raw = ((response.data or [{}])[0]).get("pro_until")
        current_pro_until = None
        if isinstance(current_raw, str) and current_raw.strip():
            try:
                current_pro_until = datetime.fromisoformat(current_raw.replace("Z", "+00:00")).astimezone(timezone.utc)
            except ValueError:
                current_pro_until = None

        now = datetime.now(timezone.utc)
        if current_pro_until and expires_at:
            next_pro_until = max(current_pro_until, expires_at)
        else:
            next_pro_until = expires_at or current_pro_until

        is_pro = next_pro_until is None or next_pro_until > now
        (
            supabase_admin.table("ai_entitlements")
            .update(
                {
                    "is_pro": is_pro,
                    "pro_until": next_pro_until.isoformat() if next_pro_until else None,
                }
            )
            .eq("user_id", user_id)
            .execute()
        )


revenuecat_webhook_service = RevenueCatWebhookService()
