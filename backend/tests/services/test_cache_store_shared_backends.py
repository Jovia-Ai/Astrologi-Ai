from datetime import datetime, timedelta, timezone

from app.services.performance import cache_store


def test_build_cache_store_from_env_falls_back_to_memory_without_redis_url(monkeypatch) -> None:
    monkeypatch.setattr(cache_store.settings, "performance_cache_backend", "redis")
    monkeypatch.setattr(cache_store.settings, "performance_cache_redis_url", None)
    monkeypatch.setattr(cache_store.settings, "performance_cache_strict", False)
    monkeypatch.setattr(cache_store.settings, "performance_cache_fail_fast_envs", ["staging", "production"])
    monkeypatch.setattr(cache_store.settings, "environment", "development")

    store = cache_store.build_cache_store_from_env()

    assert isinstance(store, cache_store.InMemoryCacheStore)


def test_build_cache_store_from_env_supports_layered_backend(monkeypatch) -> None:
    class FakeRedisStore(cache_store.InMemoryCacheStore):
        def __init__(self, **kwargs) -> None:
            super().__init__()

    monkeypatch.setattr(cache_store.settings, "performance_cache_backend", "layered")
    monkeypatch.setattr(cache_store.settings, "performance_cache_redis_url", "redis://localhost:6379/0")
    monkeypatch.setattr(cache_store.settings, "performance_cache_strict", False)
    monkeypatch.setattr(cache_store.settings, "performance_cache_fail_fast_envs", ["staging", "production"])
    monkeypatch.setattr(cache_store.settings, "environment", "development")
    monkeypatch.setattr(cache_store, "RedisCacheStore", FakeRedisStore)

    store = cache_store.build_cache_store_from_env()

    assert isinstance(store, cache_store.LayeredCacheStore)


def test_layered_missing_redis_url_raises_in_strict_mode(monkeypatch) -> None:
    monkeypatch.setattr(cache_store.settings, "performance_cache_backend", "layered")
    monkeypatch.setattr(cache_store.settings, "performance_cache_redis_url", None)
    monkeypatch.setattr(cache_store.settings, "performance_cache_strict", True)
    monkeypatch.setattr(cache_store.settings, "performance_cache_fail_fast_envs", ["staging", "production"])
    monkeypatch.setattr(cache_store.settings, "environment", "development")

    try:
        cache_store.build_cache_store_from_env()
    except cache_store.SharedCacheInitializationError:
        pass
    else:
        raise AssertionError("strict layered backend should fail fast when Redis URL is missing")


def test_redis_init_failure_raises_in_strict_mode(monkeypatch) -> None:
    class FailingRedisStore:
        def __init__(self, **kwargs) -> None:
            raise RuntimeError("redis init failed")

    monkeypatch.setattr(cache_store.settings, "performance_cache_backend", "redis")
    monkeypatch.setattr(cache_store.settings, "performance_cache_redis_url", "redis://localhost:6379/0")
    monkeypatch.setattr(cache_store.settings, "performance_cache_strict", True)
    monkeypatch.setattr(cache_store.settings, "performance_cache_fail_fast_envs", ["staging", "production"])
    monkeypatch.setattr(cache_store.settings, "environment", "development")
    monkeypatch.setattr(cache_store, "RedisCacheStore", FailingRedisStore)

    try:
        cache_store.build_cache_store_from_env()
    except cache_store.SharedCacheInitializationError:
        pass
    else:
        raise AssertionError("strict redis backend should fail fast when Redis init fails")


def test_layered_missing_redis_url_fails_fast_in_production_environment(monkeypatch) -> None:
    monkeypatch.setattr(cache_store.settings, "performance_cache_backend", "layered")
    monkeypatch.setattr(cache_store.settings, "performance_cache_redis_url", None)
    monkeypatch.setattr(cache_store.settings, "performance_cache_strict", False)
    monkeypatch.setattr(cache_store.settings, "performance_cache_fail_fast_envs", ["staging", "production"])
    monkeypatch.setattr(cache_store.settings, "environment", "production")

    try:
        cache_store.build_cache_store_from_env()
    except cache_store.SharedCacheInitializationError:
        pass
    else:
        raise AssertionError("production layered backend should fail fast when Redis URL is missing")


def test_layered_cache_store_backfills_l1_from_l2() -> None:
    l1 = cache_store.InMemoryCacheStore()
    l2 = cache_store.InMemoryCacheStore()
    layered = cache_store.LayeredCacheStore(primary=l1, secondary=l2)
    anchor = datetime(2026, 4, 8, 12, 0, tzinfo=timezone.utc)

    l2.set(
        "shared:key",
        {"value": "from-l2"},
        ttl_seconds=60,
        stale_ttl_seconds=300,
        now=anchor,
    )

    lookup = layered.get("shared:key", now=anchor + timedelta(seconds=10))

    assert lookup.status == "hit"
    assert lookup.entry is not None
    assert lookup.entry.value == {"value": "from-l2"}
    assert l1.get("shared:key", now=anchor + timedelta(seconds=10)).status == "hit"


def test_layered_cache_store_set_survives_secondary_failure() -> None:
    class FailingStore:
        def get(self, key: str, *, now=None):
            raise RuntimeError("boom")

        def set(self, key: str, value, *, ttl_seconds: int, stale_ttl_seconds: int = 0, now=None):
            raise RuntimeError("boom")

    l1 = cache_store.InMemoryCacheStore()
    layered = cache_store.LayeredCacheStore(primary=l1, secondary=FailingStore())
    anchor = datetime(2026, 4, 8, 12, 0, tzinfo=timezone.utc)

    entry = layered.set(
        "shared:key",
        {"value": "from-l1"},
        ttl_seconds=60,
        stale_ttl_seconds=300,
        now=anchor,
    )

    assert entry.value == {"value": "from-l1"}
    assert l1.get("shared:key", now=anchor + timedelta(seconds=5)).status == "hit"
