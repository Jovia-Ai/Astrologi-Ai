"""Adapter-friendly cache store with a simple in-memory default."""
from __future__ import annotations

import copy
import hashlib
import importlib
import json
import logging
import os
import threading
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from time import perf_counter
from typing import Any, Protocol

from app.core.config import settings

logger = logging.getLogger(__name__)
_cache_runtime_state_lock = threading.RLock()
_cache_runtime_state: dict[str, Any] = {
    "selected_backend": "memory",
    "active_backend": "memory",
    "strict_mode": False,
    "environment": "development",
    "redis_configured": False,
    "redis_ready": False,
    "fallback_active": False,
    "fail_fast_expected": False,
    "shared_cache_expected": False,
    "readiness_ok": True,
    "status": "ready",
    "reason": "memory_backend",
}


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


class SharedCacheInitializationError(RuntimeError):
    """Raised when shared-cache backend is required but unavailable."""


def _key_hash(key: str) -> str:
    return hashlib.sha1(key.encode("utf-8")).hexdigest()[:12]


def _log_cache_event(event: str, **fields: Any) -> None:
    logger.info(
        "performance_cache %s",
        json.dumps(
            {
                "event": event,
                **fields,
            },
            ensure_ascii=False,
            sort_keys=True,
            default=str,
        ),
    )


def _shared_cache_strict_mode(backend: str) -> bool:
    environment = settings.environment.strip().lower()
    fail_fast_envs = {item.strip().lower() for item in settings.performance_cache_fail_fast_envs if item.strip()}
    return backend in {"redis", "layered"} and (
        bool(settings.performance_cache_strict) or environment in fail_fast_envs
    )


def _shared_cache_requested(backend: str) -> bool:
    return backend in {"redis", "layered"}


def _record_cache_runtime_state(
    *,
    selected_backend: str,
    active_backend: str,
    strict_mode: bool,
    environment: str,
    redis_configured: bool,
    status: str,
    reason: str | None = None,
) -> None:
    shared_cache_expected = _shared_cache_requested(selected_backend)
    redis_ready = active_backend in {"redis", "layered"}
    fallback_active = shared_cache_expected and active_backend == "memory"
    readiness_ok = (not shared_cache_expected and active_backend == "memory") or (
        shared_cache_expected and active_backend == selected_backend
    )
    with _cache_runtime_state_lock:
        _cache_runtime_state.update(
            {
                "selected_backend": selected_backend,
                "active_backend": active_backend,
                "strict_mode": strict_mode,
                "environment": environment,
                "redis_configured": redis_configured,
                "redis_ready": redis_ready,
                "fallback_active": fallback_active,
                "fail_fast_expected": strict_mode,
                "shared_cache_expected": shared_cache_expected,
                "readiness_ok": readiness_ok,
                "status": status,
                "reason": reason,
            }
        )


def get_cache_runtime_status() -> dict[str, Any]:
    with _cache_runtime_state_lock:
        return dict(_cache_runtime_state)


def _probe_store_ready(store: Any) -> bool:
    if isinstance(store, InMemoryCacheStore):
        return True
    if isinstance(store, LayeredCacheStore):
        primary = getattr(store, "_primary", None)
        secondary = getattr(store, "_secondary", None)
        return _probe_store_ready(primary) and _probe_store_ready(secondary)
    client = getattr(store, "_client", None)
    ping = getattr(client, "ping", None)
    if callable(ping):
        ping()
        return True
    return False


def get_cache_health_status() -> dict[str, Any]:
    summary = get_cache_runtime_status()
    if not summary.get("shared_cache_expected"):
        return summary
    try:
        live_ready = _probe_store_ready(default_cache_store)
    except Exception:
        live_ready = False
    if not live_ready:
        summary["redis_ready"] = False
        summary["readiness_ok"] = False
        if summary.get("status") == "ready":
            summary["status"] = "degraded"
        if not summary.get("reason"):
            summary["reason"] = "redis_probe_failed"
    return summary


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


class RedisCacheStore:
    def __init__(
        self,
        *,
        redis_url: str,
        key_prefix: str = "astrologi-ai",
        socket_timeout_seconds: float = 0.2,
        connect_timeout_seconds: float = 0.2,
    ) -> None:
        redis_module = importlib.import_module("redis")
        self._client = redis_module.Redis.from_url(
            redis_url,
            decode_responses=True,
            socket_timeout=socket_timeout_seconds,
            socket_connect_timeout=connect_timeout_seconds,
        )
        self._key_prefix = key_prefix.strip() or "astrologi-ai"
        self._client.ping()

    def get(self, key: str, *, now: datetime | None = None) -> CacheLookup:
        anchor = now or utc_now()
        started = perf_counter()
        redis_key = self._redis_key(key)
        try:
            raw = self._client.get(redis_key)
            duration_ms = round((perf_counter() - started) * 1000.0, 3)
            if raw is None:
                _log_cache_event(
                    "get",
                    backend="redis",
                    status="miss",
                    key_hash=_key_hash(key),
                    duration_ms=duration_ms,
                )
                return CacheLookup(status="miss")
            envelope = json.loads(raw)
            entry = self._entry_from_envelope(key=key, envelope=envelope)
            if entry.stale_until <= anchor:
                self._client.delete(redis_key)
                _log_cache_event(
                    "get",
                    backend="redis",
                    status="miss",
                    key_hash=_key_hash(key),
                    duration_ms=duration_ms,
                    bypass_reason="expired_at_read",
                )
                return CacheLookup(status="miss")
            status = "hit" if entry.fresh_until > anchor else "stale"
            _log_cache_event(
                "get",
                backend="redis",
                status=status,
                key_hash=_key_hash(key),
                duration_ms=duration_ms,
            )
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
        except Exception:
            duration_ms = round((perf_counter() - started) * 1000.0, 3)
            _log_cache_event(
                "get",
                backend="redis",
                status="bypass",
                key_hash=_key_hash(key),
                duration_ms=duration_ms,
                bypass_reason="redis_get_failed",
            )
            raise

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
        ttl_total_seconds = max(1, int((stale_until - anchor).total_seconds()))
        started = perf_counter()
        try:
            self._client.set(
                self._redis_key(key),
                json.dumps(self._envelope_for_entry(entry), ensure_ascii=False, sort_keys=True, default=str),
                ex=ttl_total_seconds,
            )
            _log_cache_event(
                "set",
                backend="redis",
                status="stored",
                key_hash=_key_hash(key),
                duration_ms=round((perf_counter() - started) * 1000.0, 3),
            )
            return CacheEntry(
                key=entry.key,
                value=copy.deepcopy(entry.value),
                generated_at=entry.generated_at,
                fresh_until=entry.fresh_until,
                stale_until=entry.stale_until,
            )
        except Exception:
            _log_cache_event(
                "set",
                backend="redis",
                status="bypass",
                key_hash=_key_hash(key),
                duration_ms=round((perf_counter() - started) * 1000.0, 3),
                bypass_reason="redis_set_failed",
            )
            raise

    def _redis_key(self, key: str) -> str:
        return f"{self._key_prefix}:{key}"

    def _envelope_for_entry(self, entry: CacheEntry) -> dict[str, Any]:
        return {
            "key": entry.key,
            "value": entry.value,
            "generated_at": entry.generated_at.isoformat(),
            "fresh_until": entry.fresh_until.isoformat(),
            "stale_until": entry.stale_until.isoformat(),
        }

    def _entry_from_envelope(self, *, key: str, envelope: Any) -> CacheEntry:
        payload = envelope if isinstance(envelope, dict) else {}
        return CacheEntry(
            key=key,
            value=copy.deepcopy(payload.get("value")),
            generated_at=datetime.fromisoformat(str(payload.get("generated_at"))),
            fresh_until=datetime.fromisoformat(str(payload.get("fresh_until"))),
            stale_until=datetime.fromisoformat(str(payload.get("stale_until"))),
        )


class LayeredCacheStore:
    def __init__(self, *, primary: CacheStore, secondary: CacheStore) -> None:
        self._primary = primary
        self._secondary = secondary

    def get(self, key: str, *, now: datetime | None = None) -> CacheLookup:
        anchor = now or utc_now()
        primary_lookup = self._safe_get(self._primary, key, now=anchor, backend="l1")
        if primary_lookup is not None and primary_lookup.status in {"hit", "stale"}:
            _log_cache_event(
                "layered_get",
                backend="layered",
                status=primary_lookup.status,
                key_hash=_key_hash(key),
                l1_status=primary_lookup.status,
                l2_status="skipped",
            )
            return primary_lookup

        secondary_lookup = self._safe_get(self._secondary, key, now=anchor, backend="l2")
        if secondary_lookup is None or secondary_lookup.entry is None:
            _log_cache_event(
                "layered_get",
                backend="layered",
                status="miss",
                key_hash=_key_hash(key),
                l1_status=primary_lookup.status if primary_lookup is not None else "bypass",
                l2_status=secondary_lookup.status if secondary_lookup is not None else "bypass",
            )
            return CacheLookup(status="miss")

        self._backfill_primary(key, secondary_lookup.entry, now=anchor)
        _log_cache_event(
            "layered_get",
            backend="layered",
            status=secondary_lookup.status,
            key_hash=_key_hash(key),
            l1_status=primary_lookup.status if primary_lookup is not None else "bypass",
            l2_status=secondary_lookup.status,
        )
        return secondary_lookup

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
        stored_entry: CacheEntry | None = None
        secondary_entry = self._safe_set(
            self._secondary,
            key,
            value,
            ttl_seconds=ttl_seconds,
            stale_ttl_seconds=stale_ttl_seconds,
            now=anchor,
            backend="l2",
        )
        primary_entry = self._safe_set(
            self._primary,
            key,
            value,
            ttl_seconds=ttl_seconds,
            stale_ttl_seconds=stale_ttl_seconds,
            now=anchor,
            backend="l1",
        )
        stored_entry = secondary_entry or primary_entry
        if stored_entry is None:
            raise RuntimeError("all cache backends failed")
        _log_cache_event(
            "layered_set",
            backend="layered",
            status="stored",
            key_hash=_key_hash(key),
            l1_status="stored" if primary_entry is not None else "bypass",
            l2_status="stored" if secondary_entry is not None else "bypass",
        )
        return stored_entry

    def _safe_get(
        self,
        store: CacheStore,
        key: str,
        *,
        now: datetime,
        backend: str,
    ) -> CacheLookup | None:
        try:
            return store.get(key, now=now)
        except Exception:
            _log_cache_event(
                "layered_backend_get",
                backend=backend,
                status="bypass",
                key_hash=_key_hash(key),
                bypass_reason=f"{backend}_get_failed",
            )
            return None

    def _safe_set(
        self,
        store: CacheStore,
        key: str,
        value: Any,
        *,
        ttl_seconds: int,
        stale_ttl_seconds: int,
        now: datetime,
        backend: str,
    ) -> CacheEntry | None:
        try:
            return store.set(
                key,
                value,
                ttl_seconds=ttl_seconds,
                stale_ttl_seconds=stale_ttl_seconds,
                now=now,
            )
        except Exception:
            _log_cache_event(
                "layered_backend_set",
                backend=backend,
                status="bypass",
                key_hash=_key_hash(key),
                bypass_reason=f"{backend}_set_failed",
            )
            return None

    def _backfill_primary(self, key: str, entry: CacheEntry, *, now: datetime) -> None:
        fresh_remaining = max(0, int((entry.fresh_until - now).total_seconds()))
        stale_total_remaining = max(0, int((entry.stale_until - now).total_seconds()))
        stale_remaining = max(0, stale_total_remaining - fresh_remaining)
        self._safe_set(
            self._primary,
            key,
            entry.value,
            ttl_seconds=fresh_remaining,
            stale_ttl_seconds=stale_remaining,
            now=now,
            backend="l1",
        )


def build_cache_store_from_env() -> CacheStore:
    backend = settings.performance_cache_backend.strip().lower() or "memory"
    strict_mode = _shared_cache_strict_mode(backend)
    environment = settings.environment.strip().lower() or "development"
    redis_configured = bool((settings.performance_cache_redis_url or "").strip())
    _log_cache_event(
        "backend_selection",
        backend=backend,
        strict_mode=strict_mode,
        environment=environment,
    )
    if backend == "memory":
        _record_cache_runtime_state(
            selected_backend="memory",
            active_backend="memory",
            strict_mode=strict_mode,
            environment=environment,
            redis_configured=redis_configured,
            status="ready",
            reason="memory_backend",
        )
        _log_cache_event(
            "backend_init",
            backend="memory",
            status="ready",
            strict_mode=strict_mode,
            environment=environment,
        )
        return InMemoryCacheStore()

    redis_url = (settings.performance_cache_redis_url or "").strip()
    if not redis_url:
        payload = {
            "backend": backend,
            "status": "fail_fast" if strict_mode else "fallback",
            "strict_mode": strict_mode,
            "environment": environment,
            "bypass_reason": "redis_url_missing",
            "fallback_backend": "memory",
        }
        _record_cache_runtime_state(
            selected_backend=backend,
            active_backend="unavailable" if strict_mode else "memory",
            strict_mode=strict_mode,
            environment=environment,
            redis_configured=False,
            status="fail_fast" if strict_mode else "fallback",
            reason="redis_url_missing",
        )
        _log_cache_event("backend_init", **payload)
        if strict_mode:
            logger.critical("Shared cache initialization failed: Redis URL missing for backend=%s", backend)
            raise SharedCacheInitializationError("Redis URL missing for strict shared-cache backend.")
        return InMemoryCacheStore()

    key_prefix = settings.performance_cache_redis_prefix
    socket_timeout_seconds = float(settings.performance_cache_redis_socket_timeout_seconds)
    connect_timeout_seconds = float(settings.performance_cache_redis_connect_timeout_seconds)

    try:
        redis_store = RedisCacheStore(
            redis_url=redis_url,
            key_prefix=key_prefix,
            socket_timeout_seconds=socket_timeout_seconds,
            connect_timeout_seconds=connect_timeout_seconds,
        )
    except Exception as exc:
        _record_cache_runtime_state(
            selected_backend=backend,
            active_backend="unavailable" if strict_mode else "memory",
            strict_mode=strict_mode,
            environment=environment,
            redis_configured=True,
            status="fail_fast" if strict_mode else "fallback",
            reason="redis_init_failed",
        )
        _log_cache_event(
            "backend_init",
            backend=backend,
            status="fail_fast" if strict_mode else "fallback",
            strict_mode=strict_mode,
            environment=environment,
            bypass_reason="redis_init_failed",
            fallback_backend="memory",
            error_type=type(exc).__name__,
        )
        if strict_mode:
            logger.critical(
                "Shared cache initialization failed: Redis init error for backend=%s (%s)",
                backend,
                type(exc).__name__,
            )
            raise SharedCacheInitializationError("Redis initialization failed for strict shared-cache backend.") from exc
        return InMemoryCacheStore()

    if backend == "redis":
        _record_cache_runtime_state(
            selected_backend="redis",
            active_backend="redis",
            strict_mode=strict_mode,
            environment=environment,
            redis_configured=True,
            status="ready",
            reason=None,
        )
        _log_cache_event(
            "backend_init",
            backend="redis",
            status="ready",
            strict_mode=strict_mode,
            environment=environment,
        )
        return redis_store
    if backend == "layered":
        _record_cache_runtime_state(
            selected_backend="layered",
            active_backend="layered",
            strict_mode=strict_mode,
            environment=environment,
            redis_configured=True,
            status="ready",
            reason=None,
        )
        _log_cache_event(
            "backend_init",
            backend="layered",
            status="ready",
            strict_mode=strict_mode,
            environment=environment,
        )
        return LayeredCacheStore(primary=InMemoryCacheStore(), secondary=redis_store)

    _record_cache_runtime_state(
        selected_backend=backend,
        active_backend="memory",
        strict_mode=strict_mode,
        environment=environment,
        redis_configured=redis_configured,
        status="fallback",
        reason="unknown_backend",
    )
    _log_cache_event(
        "backend_init",
        backend=backend,
        status="fallback",
        strict_mode=strict_mode,
        environment=environment,
        bypass_reason="unknown_backend",
        fallback_backend="memory",
    )
    return InMemoryCacheStore()


default_cache_store = build_cache_store_from_env()
