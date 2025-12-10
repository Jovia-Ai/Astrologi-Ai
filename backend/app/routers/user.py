"""User routes placeholder."""
from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("")
def list_users():
    return {"users": []}
