"""Adapter-friendly cache store with a simple in-memory default."""
from __future__ import annotations

import copy
import threading
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Protocol


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class CacheEntry:
    key: str
    value: Any
    generated_at: datetime
    fresh_until: datetime
    stale_until: datetime


@dataclass(frozen=True)
class CacheLookup:
    status: str
    entry: CacheEntry | None = None


class CacheStore(Protocol):
    def get(self, key: str, *, now: datetime | None = None) -> CacheLookup:
        ...

    def set(
        self,
        key: str,
        value: Any,
        *,
        ttl_seconds: int,
        stale_ttl_seconds: int = 0,
        now: datetime | None = None,
    ) -> CacheEntry:
        ...


class InMemoryCacheStore:
    def __init__(self) -> None:
        self._entries: dict[str, CacheEntry] = {}
        self._lock = threading.RLock()

    def get(self, key: str, *, now: datetime | None = None) -> CacheLookup:
        anchor = now or utc_now()
        with self._lock:
            entry = self._entries.get(key)
            if entry is None:
                return CacheLookup(status="miss")
            if entry.stale_until <= anchor:
                self._entries.pop(key, None)
                return CacheLookup(status="miss")
            status = "hit" if entry.fresh_until > anchor else "stale"
            return CacheLookup(
                status=status,
                entry=CacheEntry(
                    key=entry.key,
                    value=copy.deepcopy(entry.value),
                    generated_at=entry.generated_at,
                    fresh_until=entry.fresh_until,
                    stale_until=entry.stale_until,
                ),
            )

    def set(
        self,
        key: str,
        value: Any,
        *,
        ttl_seconds: int,
        stale_ttl_seconds: int = 0,
        now: datetime | None = None,
    ) -> CacheEntry:
        anchor = now or utc_now()
        fresh_until = anchor + timedelta(seconds=max(0, ttl_seconds))
        stale_until = fresh_until + timedelta(seconds=max(0, stale_ttl_seconds))
        entry = CacheEntry(
            key=key,
            value=copy.deepcopy(value),
            generated_at=anchor,
            fresh_until=fresh_until,
            stale_until=stale_until,
        )
        with self._lock:
            self._entries[key] = entry
        return CacheEntry(
            key=entry.key,
            value=copy.deepcopy(entry.value),
            generated_at=entry.generated_at,
            fresh_until=entry.fresh_until,
            stale_until=entry.stale_until,
        )


default_cache_store = InMemoryCacheStore()
