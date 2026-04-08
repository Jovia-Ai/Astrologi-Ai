"""Additive home performance orchestration around existing builders."""
from __future__ import annotations

import copy
import json
import logging
from calendar import monthrange
from dataclasses import dataclass
from datetime import date as date_type, datetime, time, timezone
from typing import Any, Mapping

from app.api.routes.natal_interpretation import NatalInterpretationRequest, interpret_natal_chart_ui
from app.api.routes.transits import TransitNarrativeRequest, build_transit_narrative
from app.core.config import settings
from app.sky_events.service import get_sky_now_feed
from app.transit.narrative.generator import make_birth_fingerprint

from .cache_keys import (
    build_global_transits_key,
    build_home_cache_config_hash,
    build_home_deep_key,
    build_home_fast_key,
)
from .cache_store import CacheEntry, CacheLookup, CacheStore, default_cache_store, utc_now
from .payload_versions import HOME_DEEP_PAYLOAD_VERSION, HOME_FAST_PAYLOAD_VERSION
from .refresh_scheduler import schedule_home_refresh
from .timing import TimingRecorder

logger = logging.getLogger(__name__)
HOME_SECTION_READY = "ready"
HOME_SECTION_STALE = "stale"
HOME_SECTION_DEFERRED = "deferred"


def _json_safe(value: Any) -> Any:
    if isinstance(value, set):
        return sorted(value)
    return str(value)


def _payload_size_bytes(payload: Any) -> int:
    return len(
        json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            default=_json_safe,
        ).encode("utf-8")
    )


@dataclass(frozen=True)
class HomeRequestContext:
    birth_date: str
    birth_time: str
    birth_place: str
    target_date: date_type
    tz: str = "Europe/Istanbul"
    locale: str = "tr"
    lens: str = "general"
    user_id: str | None = None
    transit_place: str | None = None
    birth_latitude: float | None = None
    birth_longitude: float | None = None
    birth_timezone: str | None = None
    transit_latitude: float | None = None
    transit_longitude: float | None = None
    transit_timezone: str | None = None

    @property
    def selected_date(self) -> str:
        return self.target_date.isoformat()

    @property
    def range_start(self) -> str:
        return self.target_date.replace(day=1).isoformat()

    @property
    def range_end(self) -> str:
        last_day = monthrange(self.target_date.year, self.target_date.month)[1]
        return self.target_date.replace(day=last_day).isoformat()

    @property
    def effective_transit_place(self) -> str:
        return (self.transit_place or self.birth_place).strip()

    @property
    def subject_key(self) -> str:
        if self.user_id and self.user_id.strip():
            return self.user_id.strip()
        return make_birth_fingerprint(
            birth_date=self.birth_date,
            birth_time=self.birth_time,
            birth_place=self.birth_place,
            tz=self.tz,
        )


class HomeOrchestrator:
    def __init__(self, *, cache_store: CacheStore | None = None) -> None:
        self._cache_store = cache_store or default_cache_store

    def get_fast(self, context: HomeRequestContext, *, now: datetime | None = None) -> dict[str, Any]:
        return self._get_payload(mode="fast", context=context, now=now)

    def get_deep(self, context: HomeRequestContext, *, now: datetime | None = None) -> dict[str, Any]:
        return self._get_payload(mode="deep", context=context, now=now)

    def _get_payload(self, *, mode: str, context: HomeRequestContext, now: datetime | None) -> dict[str, Any]:
        anchor = now or utc_now()
        timer = TimingRecorder()
        cache_enabled = self._cache_enabled(mode)
        cache_key = self._cache_key(mode=mode, context=context)
        payload_version = self._payload_version(mode)
        payload_bytes = 0

        lookup = CacheLookup(status="miss")
        if cache_enabled:
            with timer.stage("cache_lookup"):
                lookup = self._safe_cache_get(cache_key, now=anchor)

        if lookup.status == "hit" and lookup.entry is not None:
            payload = self._materialize_response(entry=lookup.entry, cache_status="hit")
            payload_bytes = _payload_size_bytes(payload)
            self._log_timing(
                mode=mode,
                context=context,
                cache_status="hit",
                cache_key=cache_key,
                timer=timer,
                payload_version=payload_version,
                payload_bytes=payload_bytes,
            )
            return payload

        if (
            lookup.status == "stale"
            and lookup.entry is not None
            and settings.enable_stale_while_revalidate
        ):
            self._schedule_stale_refresh(mode=mode, context=context)
            payload = self._materialize_response(entry=lookup.entry, cache_status="stale")
            payload_bytes = _payload_size_bytes(payload)
            self._log_timing(
                mode=mode,
                context=context,
                cache_status="stale",
                cache_key=cache_key,
                timer=timer,
                payload_version=payload_version,
                payload_bytes=payload_bytes,
            )
            return payload

        if mode == "fast":
            payload = self._build_deferred_fast_payload(context=context, now=anchor, timer=timer)
            response_body = {
                **payload,
                "generated_at": anchor.isoformat(),
                "fresh_until": anchor.isoformat(),
                "payload_version": payload_version,
                "cache_status": "miss",
            }
            with timer.stage("serialization"):
                response_body = copy.deepcopy(response_body)
            self._schedule_background_prewarm(context=context)
            payload_bytes = _payload_size_bytes(response_body)
            self._log_timing(
                mode=mode,
                context=context,
                cache_status=response_body["cache_status"],
                cache_key=cache_key,
                timer=timer,
                payload_version=payload_version,
                payload_bytes=payload_bytes,
            )
            return response_body

        payload = self._compute_payload(mode=mode, context=context, now=anchor, timer=timer)
        fresh_until = self._fresh_until(mode=mode, now=anchor).isoformat()
        response_body = {
            **payload,
            "generated_at": anchor.isoformat(),
            "fresh_until": fresh_until,
            "payload_version": payload_version,
            "cache_status": "miss",
        }

        if cache_enabled and self._should_store_payload(mode=mode, payload=response_body):
            with timer.stage("serialization"):
                entry = self._safe_cache_set(
                    cache_key,
                    {key: value for key, value in response_body.items() if key != "cache_status"},
                    ttl_seconds=self._ttl_seconds(mode),
                    stale_ttl_seconds=self._stale_ttl_seconds(mode),
                    now=anchor,
                )
                if entry is not None:
                    response_body = self._materialize_response(entry=entry, cache_status="miss")
                    if mode == "deep":
                        self._warm_fast_cache_from_deep(context=context, payload=response_body, now=anchor)
                    elif mode == "fast":
                        self._schedule_background_prewarm(context=context)
        else:
            with timer.stage("serialization"):
                response_body = copy.deepcopy(response_body)
            if mode == "fast":
                self._schedule_background_prewarm(context=context)

        payload_bytes = _payload_size_bytes(response_body)
        self._log_timing(
            mode=mode,
            context=context,
            cache_status=response_body["cache_status"],
            cache_key=cache_key,
            timer=timer,
            payload_version=payload_version,
            payload_bytes=payload_bytes,
        )
        return response_body

    def _compute_payload(
        self,
        *,
        mode: str,
        context: HomeRequestContext,
        now: datetime,
        timer: TimingRecorder,
    ) -> dict[str, Any]:
        with timer.stage("global_compute"):
            sky_payload = self._get_global_sky_payload(context=context, now=now)
        with timer.stage("user_overlay"):
            natal_public = self._build_natal_public(context)
        with timer.stage("ranking"):
            transit_payload = self._build_transit_payload(
                context,
                include_best_times=mode == "deep",
            )
        with timer.stage("composer"):
            if mode == "fast":
                return self._assemble_fast_payload(
                    natal_public=natal_public,
                    transit_payload=transit_payload,
                    sky_payload=sky_payload,
                )
            return self._assemble_deep_payload(
                context=context,
                natal_public=natal_public,
                transit_payload=transit_payload,
                sky_payload=sky_payload,
            )

    def _build_natal_public(self, context: HomeRequestContext) -> dict[str, Any]:
        response = interpret_natal_chart_ui(
            NatalInterpretationRequest(
                birth_date=context.birth_date,
                birth_time=context.birth_time,
                birth_place=context.birth_place,
                birth_latitude=context.birth_latitude,
                birth_longitude=context.birth_longitude,
                birth_timezone=context.birth_timezone,
                locale=context.locale,
            )
        )
        return dict(response.get("public") or {})

    def _build_natal_summary_public(self, context: HomeRequestContext) -> dict[str, Any]:
        response = interpret_natal_chart_ui(
            NatalInterpretationRequest(
                birth_date=context.birth_date,
                birth_time=context.birth_time,
                birth_place=context.birth_place,
                birth_latitude=context.birth_latitude,
                birth_longitude=context.birth_longitude,
                birth_timezone=context.birth_timezone,
                locale=context.locale,
                summary_only=True,
            )
        )
        return dict(response.get("public") or {})

    def _build_transit_payload(self, context: HomeRequestContext, *, include_best_times: bool) -> dict[str, Any]:
        return build_transit_narrative(
            TransitNarrativeRequest(
                birth_date=context.birth_date,
                birth_time=context.birth_time,
                birth_place=context.birth_place,
                birth_latitude=context.birth_latitude,
                birth_longitude=context.birth_longitude,
                birth_timezone=context.birth_timezone,
                start=context.range_start,
                end=context.range_end,
                selected_date=context.selected_date,
                tz=context.tz,
                transit_place=context.effective_transit_place,
                transit_latitude=context.transit_latitude,
                transit_longitude=context.transit_longitude,
                transit_timezone=context.transit_timezone,
                lens=context.lens,
                intent="general",
                include_best_times=include_best_times,
                top=5,
                window=3,
            )
        )

    def _get_global_sky_payload(self, *, context: HomeRequestContext, now: datetime) -> dict[str, Any]:
        cache_key = build_global_transits_key(day=context.target_date, tz=context.tz)
        if settings.global_transits_ttl_seconds > 0:
            lookup = self._safe_cache_get(cache_key, now=now)
            if lookup.entry is not None and lookup.status in {"hit", "stale"}:
                return dict(lookup.entry.value or {})

        anchor = datetime.combine(context.target_date, time(hour=12), tzinfo=timezone.utc)
        payload = get_sky_now_feed(
            now=anchor,
            tz=context.tz,
            limit=4,
            event_types=None,
            debug=False,
        ).model_dump()
        if settings.global_transits_ttl_seconds > 0:
            self._safe_cache_set(
                cache_key,
                payload,
                ttl_seconds=settings.global_transits_ttl_seconds,
                stale_ttl_seconds=settings.global_transits_stale_ttl_seconds,
                now=now,
            )
        return payload

    def _assemble_fast_payload(
        self,
        *,
        natal_public: Mapping[str, Any],
        transit_payload: Mapping[str, Any],
        sky_payload: Mapping[str, Any],
        section_states: Mapping[str, str] | None = None,
    ) -> dict[str, Any]:
        transit_public = transit_payload.get("public") if isinstance(transit_payload.get("public"), Mapping) else {}
        core_story_ui = natal_public.get("core_story_ui") if isinstance(natal_public.get("core_story_ui"), Mapping) else {}
        period_core = transit_public.get("period_core") if isinstance(transit_public.get("period_core"), Mapping) else {}
        sky_hero = sky_payload.get("hero") if isinstance(sky_payload.get("hero"), Mapping) else {}
        sky_editorial_summary = self._editorialize_sky_summary(sky_hero or {}, fallback=sky_payload.get("summary_tr"))

        highlights = self._build_fast_highlights(transit_public=transit_public, sky_payload=sky_payload)
        headline = self._first_text(
            period_core.get("title"),
            core_story_ui.get("headline"),
            sky_hero.get("title_tr"),
            sky_hero.get("short_title_tr"),
        )
        summary = self._first_text(
            period_core.get("core_story"),
            core_story_ui.get("text"),
            period_core.get("upper_meaning"),
            sky_editorial_summary,
            sky_payload.get("summary_tr"),
        )

        return {
            "headline": headline,
            "summary": summary,
            "highlights": highlights,
            "energy": {
                "badge": self._first_text(sky_hero.get("badge_tr"), "Home"),
                "focus": self._first_text(period_core.get("title"), core_story_ui.get("headline")),
                "summary": self._first_text(
                    sky_editorial_summary,
                    sky_hero.get("summary_tr"),
                    sky_payload.get("summary_tr"),
                ),
            },
            "cta": {
                "label": "Derin akisi ac",
                "target": "/home/deep",
            },
            "source_snapshot": {
                "natal_domains": len((natal_public.get("user_compact") or {}).get("domains") or []),
                "transit_cards": len(transit_public.get("event_cards") or []),
                "sky_items": len(sky_payload.get("items") or []),
            },
            "section_states": dict(
                section_states
                or {
                    "sky": HOME_SECTION_READY,
                    "transit_summary": HOME_SECTION_READY,
                    "natal_summary": HOME_SECTION_READY,
                }
            ),
        }

    def _assemble_deep_payload(
        self,
        *,
        context: HomeRequestContext,
        natal_public: Mapping[str, Any],
        transit_payload: Mapping[str, Any],
        sky_payload: Mapping[str, Any],
    ) -> dict[str, Any]:
        transit_public = transit_payload.get("public") if isinstance(transit_payload.get("public"), Mapping) else {}
        preview = self._assemble_fast_payload(
            natal_public=natal_public,
            transit_payload=transit_payload,
            sky_payload=sky_payload,
        )
        profile_narrative = (natal_public.get("profile_narrative") or {}).get("profile_public") or {}
        profile_blocks = profile_narrative.get("blocks") if isinstance(profile_narrative, Mapping) else []
        sections_v2 = natal_public.get("sections_v2") if isinstance(natal_public.get("sections_v2"), list) else []
        event_cards = transit_public.get("event_cards") if isinstance(transit_public.get("event_cards"), list) else []
        best_times = transit_payload.get("best_times") if isinstance(transit_payload.get("best_times"), Mapping) else {}
        sky_items = sky_payload.get("items") if isinstance(sky_payload.get("items"), list) else []

        sections = [
            {
                "id": "natal_sections",
                "title": "Kimlik katmanları",
                "items": copy.deepcopy(sections_v2[:3]),
            },
            {
                "id": "period_story",
                "title": "Aktif tema",
                "items": [
                    {
                        "title": self._first_text((transit_public.get("period_core") or {}).get("title"), "Donem"),
                        "summary": self._first_text(
                            (transit_public.get("period_core") or {}).get("core_story"),
                            (transit_public.get("period_core") or {}).get("upper_meaning"),
                        ),
                    }
                ],
            },
            {
                "id": "collective_pulse",
                "title": "Kolektif konu",
                "items": [
                    {
                        "title": self._first_text(item.get("short_title_tr"), item.get("title_tr")),
                        "summary": self._first_text(
                            self._editorialize_sky_summary(item),
                            item.get("summary_tr"),
                            item.get("badge_tr"),
                        ),
                    }
                    for item in sky_items[:3]
                    if isinstance(item, Mapping)
                ],
            },
        ]
        guidance = self._collect_guidance(event_cards=event_cards, best_times=best_times)
        story_hooks = [
            {
                "id": str(block.get("id") or f"hook-{index}"),
                "title": self._first_text(block.get("headline"), block.get("teaser")),
                "summary": self._first_text(block.get("micro"), block.get("teaser")),
            }
            for index, block in enumerate(profile_blocks[:4], start=1)
            if isinstance(block, Mapping)
        ]
        if not story_hooks:
            story_hooks = [
                {
                    "id": "fallback-hook",
                    "title": preview.get("headline") or "Bugunun akisina gir",
                    "summary": preview.get("summary") or "",
                }
            ]

        return {
            "preview": preview,
            "sections": sections,
            "expanded_cards": copy.deepcopy(event_cards[:5]),
            "guidance": guidance,
            "story_hooks": story_hooks,
            "context": {
                "selected_date": context.selected_date,
                "range": {
                    "start": context.range_start,
                    "end": context.range_end,
                    "tz": context.tz,
                },
            },
        }

    def _build_fast_highlights(
        self,
        *,
        transit_public: Mapping[str, Any],
        sky_payload: Mapping[str, Any],
    ) -> list[dict[str, Any]]:
        highlights: list[dict[str, Any]] = []
        for card in transit_public.get("event_cards") or []:
            if not isinstance(card, Mapping):
                continue
            highlights.append(
                {
                    "id": str(card.get("event_id") or card.get("id") or f"event-{len(highlights) + 1}"),
                    "kind": "transit",
                    "title": self._first_text(card.get("headline"), card.get("title")),
                    "summary": self._first_text(card.get("essence"), card.get("summary"), card.get("opening")),
                }
            )
            if len(highlights) >= 2:
                break
        if highlights:
            return highlights

        for item in sky_payload.get("items") or []:
            if not isinstance(item, Mapping):
                continue
            highlights.append(
                {
                    "id": str(item.get("id") or f"sky-{len(highlights) + 1}"),
                    "kind": "sky",
                    "title": self._first_text(item.get("short_title_tr"), item.get("title_tr")),
                    "summary": self._first_text(
                        self._editorialize_sky_summary(item),
                        item.get("summary_tr"),
                        item.get("badge_tr"),
                    ),
                }
            )
            if len(highlights) >= 2:
                break
        return highlights

    def _collect_guidance(
        self,
        *,
        event_cards: list[Any],
        best_times: Mapping[str, Any],
    ) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for card in event_cards[:3]:
            if not isinstance(card, Mapping):
                continue
            asks = [str(item).strip() for item in (card.get("asks") or []) if str(item).strip()]
            watch = [str(item).strip() for item in (card.get("watchout") or card.get("watch") or []) if str(item).strip()]
            summary = asks[0] if asks else (watch[0] if watch else self._first_text(card.get("essence"), card.get("summary")))
            items.append(
                {
                    "title": self._first_text(card.get("headline"), card.get("title")),
                    "summary": summary,
                }
            )
        for candidate in best_times.get("candidates") or []:
            if not isinstance(candidate, Mapping):
                continue
            items.append(
                {
                    "title": self._first_text(candidate.get("label"), candidate.get("date")),
                    "summary": self._first_text(candidate.get("reason")),
                }
            )
            if len(items) >= 5:
                break
        return items[:5]

    def _editorialize_sky_summary(
        self,
        item: Mapping[str, Any],
        *,
        fallback: Any | None = None,
    ) -> str:
        short_title = self._first_text(item.get("short_title_tr"), item.get("title_tr")).strip()
        badge = str(item.get("badge_tr") or "").strip()
        summary = self._first_text(item.get("summary_tr"), fallback).strip()
        if not short_title and not summary:
            return ""
        lower_title = short_title.lower() if short_title else ""
        if badge == "Tutulma" and lower_title:
            return f"{lower_title} kolektif atmosferde daha sert bir eşik hissi yaratabilir."
        if badge in {"Retro başlıyor", "Retro bitiyor"} and lower_title:
            return f"{lower_title} yüzünden kolektif ritim hızdan çok ayar istiyor."
        if " arasındaki " in summary and lower_title:
            return f"{lower_title} şu sıralar kolektif ritimde daha görünür çalışıyor."
        return summary

    def _warm_fast_cache_from_deep(self, *, context: HomeRequestContext, payload: Mapping[str, Any], now: datetime) -> None:
        if not settings.enable_home_fast_cache:
            return
        preview = payload.get("preview")
        if not isinstance(preview, Mapping):
            return
        fast_key = self._cache_key(mode="fast", context=context)
        preview_payload = {
            **dict(preview),
            "generated_at": payload.get("generated_at") or now.isoformat(),
            "fresh_until": self._fresh_until(mode="fast", now=now).isoformat(),
            "payload_version": HOME_FAST_PAYLOAD_VERSION,
        }
        self._safe_cache_set(
            fast_key,
            preview_payload,
            ttl_seconds=settings.home_fast_ttl_seconds,
            stale_ttl_seconds=settings.home_fast_stale_ttl_seconds,
            now=now,
        )

    def _schedule_stale_refresh(self, *, mode: str, context: HomeRequestContext) -> None:
        def _task() -> None:
            self._refresh_cached_mode(mode=mode, context=context, now=utc_now())

        schedule_home_refresh(
            name=f"{mode}-{context.subject_key}-{context.selected_date}",
            task=_task,
            enabled=settings.enable_stale_while_revalidate,
        )

    def _schedule_background_prewarm(self, *, context: HomeRequestContext) -> None:
        schedule_home_refresh(
            name=f"fast-refresh-{context.subject_key}-{context.selected_date}",
            task=lambda: self._refresh_cached_mode(mode="fast", context=context, now=utc_now()),
            enabled=settings.enable_background_refresh,
        )
        schedule_home_refresh(
            name=f"deep-prewarm-{context.subject_key}-{context.selected_date}",
            task=lambda: self._refresh_cached_mode(mode="deep", context=context, now=utc_now()),
            enabled=settings.enable_background_refresh,
        )

    def _refresh_cached_mode(self, *, mode: str, context: HomeRequestContext, now: datetime) -> None:
        payload = self._compute_payload(mode=mode, context=context, now=now, timer=TimingRecorder())
        cache_key = self._cache_key(mode=mode, context=context)
        cached_payload = {
            **payload,
            "generated_at": now.isoformat(),
            "fresh_until": self._fresh_until(mode=mode, now=now).isoformat(),
            "payload_version": self._payload_version(mode),
        }
        self._safe_cache_set(
            cache_key,
            cached_payload,
            ttl_seconds=self._ttl_seconds(mode),
            stale_ttl_seconds=self._stale_ttl_seconds(mode),
            now=now,
        )
        if mode == "deep":
            self._warm_fast_cache_from_deep(context=context, payload=cached_payload, now=now)

    def _safe_cache_get(self, key: str, *, now: datetime) -> CacheLookup:
        try:
            return self._cache_store.get(key, now=now)
        except Exception:  # pragma: no cover - fallback path
            logger.exception("performance cache get failed", extra={"cache_key": key})
            return CacheLookup(status="miss")

    def _safe_cache_set(
        self,
        key: str,
        value: Any,
        *,
        ttl_seconds: int,
        stale_ttl_seconds: int,
        now: datetime,
    ) -> CacheEntry | None:
        try:
            return self._cache_store.set(
                key,
                value,
                ttl_seconds=ttl_seconds,
                stale_ttl_seconds=stale_ttl_seconds,
                now=now,
            )
        except Exception:  # pragma: no cover - fallback path
            logger.exception("performance cache set failed", extra={"cache_key": key})
            return None

    def _materialize_response(self, *, entry: CacheEntry, cache_status: str) -> dict[str, Any]:
        payload = dict(entry.value or {})
        payload["generated_at"] = payload.get("generated_at") or entry.generated_at.isoformat()
        payload["fresh_until"] = payload.get("fresh_until") or entry.fresh_until.isoformat()
        payload["cache_status"] = cache_status
        section_states = payload.get("section_states")
        if isinstance(section_states, Mapping):
            normalized = {}
            for name, state in section_states.items():
                state_text = str(state or "").strip() or HOME_SECTION_READY
                if cache_status == "stale" and state_text == HOME_SECTION_READY:
                    state_text = HOME_SECTION_STALE
                normalized[str(name)] = state_text
            payload["section_states"] = normalized
        return payload

    def _build_deferred_fast_payload(
        self,
        *,
        context: HomeRequestContext,
        now: datetime,
        timer: TimingRecorder,
    ) -> dict[str, Any]:
        with timer.stage("global_compute"):
            sky_payload = self._get_global_sky_payload(context=context, now=now)

        natal_public: dict[str, Any] = {}
        natal_state = HOME_SECTION_DEFERRED
        with timer.stage("user_overlay"):
            try:
                natal_public = self._build_natal_summary_public(context)
                if natal_public:
                    natal_state = HOME_SECTION_READY
            except Exception:  # pragma: no cover - keep fast payload resilient
                logger.exception(
                    "home fast natal summary failed",
                    extra={"subject_key": context.subject_key, "date": context.selected_date},
                )

        with timer.stage("ranking"):
            transit_payload: dict[str, Any] = {"public": {}}

        with timer.stage("composer"):
            return self._assemble_fast_payload(
                natal_public=natal_public,
                transit_payload=transit_payload,
                sky_payload=sky_payload,
                section_states={
                    "sky": HOME_SECTION_READY,
                    "transit_summary": HOME_SECTION_DEFERRED,
                    "natal_summary": natal_state,
                },
            )

    def _should_store_payload(self, *, mode: str, payload: Mapping[str, Any]) -> bool:
        if mode != "fast":
            return True
        section_states = payload.get("section_states")
        if not isinstance(section_states, Mapping):
            return True
        return str(section_states.get("transit_summary") or HOME_SECTION_READY) == HOME_SECTION_READY

    def _cache_key(self, *, mode: str, context: HomeRequestContext) -> str:
        config_hash = build_home_cache_config_hash()
        if mode == "fast":
            return build_home_fast_key(subject_key=context.subject_key, day=context.target_date, config_hash=config_hash)
        return build_home_deep_key(subject_key=context.subject_key, day=context.target_date, config_hash=config_hash)

    def _cache_enabled(self, mode: str) -> bool:
        return settings.enable_home_fast_cache if mode == "fast" else settings.enable_home_deep_cache

    def _ttl_seconds(self, mode: str) -> int:
        return settings.home_fast_ttl_seconds if mode == "fast" else settings.home_deep_ttl_seconds

    def _stale_ttl_seconds(self, mode: str) -> int:
        return settings.home_fast_stale_ttl_seconds if mode == "fast" else settings.home_deep_stale_ttl_seconds

    def _payload_version(self, mode: str) -> str:
        return HOME_FAST_PAYLOAD_VERSION if mode == "fast" else HOME_DEEP_PAYLOAD_VERSION

    def _fresh_until(self, *, mode: str, now: datetime) -> datetime:
        return now + (self._time_delta_seconds(self._ttl_seconds(mode)))

    def _time_delta_seconds(self, seconds: int):
        from datetime import timedelta

        return timedelta(seconds=max(0, seconds))

    def _log_timing(
        self,
        *,
        mode: str,
        context: HomeRequestContext,
        cache_status: str,
        cache_key: str,
        timer: TimingRecorder,
        payload_version: str,
        payload_bytes: int,
    ) -> None:
        if not settings.enable_timing_logs:
            return
        stage_breakdown = timer.stage_breakdown_ms
        logger.info(
            "home_timing %s",
            json.dumps(
                {
                    "endpoint": f"/home/{mode}",
                    "user_id": context.user_id,
                    "subject_key": context.subject_key,
                    "date": context.selected_date,
                    "cache_status": cache_status,
                    "cache_key": cache_key,
                    "duration_ms": timer.total_ms(),
                    "cache_lookup_ms": stage_breakdown.get("cache_lookup", 0.0),
                    "global_compute_ms": stage_breakdown.get("global_compute", 0.0),
                    "user_overlay_ms": stage_breakdown.get("user_overlay", 0.0),
                    "ranking_ms": stage_breakdown.get("ranking", 0.0),
                    "composer_ms": stage_breakdown.get("composer", 0.0),
                    "serialization_ms": stage_breakdown.get("serialization", 0.0),
                    "stage_breakdown": stage_breakdown,
                    "range_start": context.range_start,
                    "range_end": context.range_end,
                    "range_days": (date_type.fromisoformat(context.range_end) - date_type.fromisoformat(context.range_start)).days + 1,
                    "selected_date": context.selected_date,
                    "transit_window": "monthly_range_with_selected_day",
                    "include_best_times": mode == "deep",
                    "payload_bytes": payload_bytes,
                    "payload_version": payload_version,
                },
                ensure_ascii=False,
                sort_keys=True,
            ),
        )

    @staticmethod
    def _first_text(*values: Any) -> str:
        for value in values:
            if isinstance(value, str) and value.strip():
                return value.strip()
        return ""


home_orchestrator = HomeOrchestrator()
