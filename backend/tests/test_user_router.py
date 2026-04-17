from __future__ import annotations

from fastapi import HTTPException

from app.auth.supabase_auth import AuthenticatedSupabaseUser
from app.routers import user as user_router
from app.services.users import AccountDeletionResult


def test_delete_current_user_returns_success_payload(monkeypatch) -> None:
    monkeypatch.setattr(
        user_router,
        "delete_user_account",
        lambda user_id: AccountDeletionResult(
            user_id=user_id,
            warnings=("stories.user_id",),
        ),
    )

    response = user_router.delete_current_user(
        AuthenticatedSupabaseUser(
            id="user-123",
            email="ada@example.com",
            full_name="Ada",
        )
    )

    assert response == {
        "ok": True,
        "user_id": "user-123",
        "warnings": ["stories.user_id"],
    }


def test_delete_current_user_wraps_unexpected_errors(monkeypatch) -> None:
    def _boom(_: str) -> None:
        raise RuntimeError("boom")

    monkeypatch.setattr(user_router, "delete_user_account", _boom)

    try:
        user_router.delete_current_user(
            AuthenticatedSupabaseUser(
                id="user-123",
                email="ada@example.com",
                full_name="Ada",
            )
        )
    except HTTPException as exc:
        assert exc.status_code == 500
        assert exc.detail == "Unable to delete account."
    else:  # pragma: no cover - defensive assertion
        raise AssertionError("Expected HTTPException to be raised")
