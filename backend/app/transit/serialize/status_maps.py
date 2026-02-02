# -*- coding: utf-8 -*-
from __future__ import annotations

RATING_MAP_BEAUTY = {
    0: "Önermiyoruz",
    1: "Uygun / hafif",
    2: "İyi",
    3: "Çok ideal",
}

RATING_MAP_TRANSIT = {
    0: "Hassas",
    1: "Dengeli",
    2: "Destekleyici",
    3: "Güçlü",
}


def map_status(rating: int, intent: str) -> str:
    rating = int(rating or 0)
    if intent == "beauty_care":
        return RATING_MAP_BEAUTY.get(rating, "Uygun / hafif")
    return RATING_MAP_TRANSIT.get(rating, "Dengeli")
