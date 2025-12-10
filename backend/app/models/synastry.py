"""Synastry schemas."""
from __future__ import annotations

from pydantic import BaseModel


class SynastryPairSchema(BaseModel):
    user_id: str
    partner_id: str
