from __future__ import annotations

from typing import Literal

EvidenceLayer = Literal[
    "placement",
    "aspect",
    "house_ruler",
    "dispositor",
    "pattern",
    "motif",
    "contradiction",
    "promise",
]

EvidenceRole = Literal[
    "root",
    "driver",
    "modifier",
    "support",
    "contradiction",
    "manifestation_channel",
    "governing_filter",
]

EVIDENCE_LAYERS: tuple[str, ...] = (
    "placement",
    "aspect",
    "house_ruler",
    "dispositor",
    "pattern",
    "motif",
    "contradiction",
    "promise",
)

EVIDENCE_ROLES: tuple[str, ...] = (
    "root",
    "driver",
    "modifier",
    "support",
    "contradiction",
    "manifestation_channel",
    "governing_filter",
)

