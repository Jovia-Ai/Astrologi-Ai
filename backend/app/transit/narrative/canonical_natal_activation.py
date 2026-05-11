from __future__ import annotations

from typing import Any, Mapping

from app.astro_os.natal.contracts import CanonicalNatalStateV1

_TRANSIT_TO_CANONICAL_DOMAIN = {
    "identity": "identity",
    "relationships": "relationship",
    "relationship": "relationship",
    "career": "career_visibility",
    "mind": "communication_learning",
    "home": "home_family",
    "body": "health_rhythm",
    "money": "money_self_worth",
    "inner": "growth_shadow",
    "general": "spiritual_meaning",
}

_HOUSE_TO_CANONICAL_DOMAIN = {
    1: "identity",
    2: "money_self_worth",
    3: "communication_learning",
    4: "home_family",
    5: "identity",
    6: "health_rhythm",
    7: "relationship",
    8: "growth_shadow",
    9: "spiritual_meaning",
    10: "career_visibility",
    11: "career_visibility",
    12: "growth_shadow",
}

_PERIOD_PREFIX_BY_DOMAIN = {
    "identity": "Bu dönem doğum haritandaki kimlik ve duruş hattını özellikle çalıştırıyor.",
    "relationship": "Bu dönem doğum haritandaki yakınlık ve güven hattını özellikle çalıştırıyor.",
    "career_visibility": "Bu dönem doğum haritandaki yön ve görünürlük hattını özellikle çalıştırıyor.",
    "communication_learning": "Bu dönem doğum haritandaki zihin ve ifade hattını özellikle çalıştırıyor.",
    "home_family": "Bu dönem doğum haritandaki temel güven ve köklenme hattını özellikle çalıştırıyor.",
    "growth_shadow": "Bu dönem doğum haritandaki iç eşik ve dönüşüm hattını özellikle çalıştırıyor.",
    "money_self_worth": "Bu dönem doğum haritandaki değer ve güvenlik hattını özellikle çalıştırıyor.",
    "health_rhythm": "Bu dönem doğum haritandaki ritim ve düzen hattını özellikle çalıştırıyor.",
    "spiritual_meaning": "Bu dönem doğum haritandaki anlam ve yön hattını özellikle çalıştırıyor.",
}

_PERIOD_THEME_BY_DOMAIN = {
    "identity": "kimlik ve duruş",
    "relationship": "yakınlık ve güven",
    "career_visibility": "yön ve görünürlük",
    "communication_learning": "zihin ve ifade",
    "home_family": "temel güven ve köklenme",
    "growth_shadow": "iç eşik ve dönüşüm",
    "money_self_worth": "değer ve güvenlik",
    "health_rhythm": "ritim ve düzen",
    "spiritual_meaning": "anlam ve yön",
}


def _safe_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _canonical_domain(token: Any) -> str | None:
    normalized = str(token or "").strip().lower().replace(" ", "_")
    return _TRANSIT_TO_CANONICAL_DOMAIN.get(normalized)


def _event_domains(event: Mapping[str, Any]) -> list[str]:
    domains: list[str] = []
    tags = event.get("tags") if isinstance(event.get("tags"), Mapping) else {}
    tag_domain = _canonical_domain(tags.get("domain"))
    if tag_domain and tag_domain not in domains:
        domains.append(tag_domain)

    raw_domains = event.get("domains") if isinstance(event.get("domains"), list) else []
    for item in raw_domains:
        mapped = _canonical_domain(item)
        if mapped and mapped not in domains:
            domains.append(mapped)

    scene = event.get("scene") if isinstance(event.get("scene"), Mapping) else {}
    for house_value in (scene.get("start_house"), scene.get("outcome_house")):
        house = _safe_int(house_value)
        mapped = _HOUSE_TO_CANONICAL_DOMAIN.get(house)
        if mapped and mapped not in domains:
            domains.append(mapped)

    return domains or ["spiritual_meaning"]


def _score_hook_match(hook: Mapping[str, Any], event_domains: list[str]) -> float:
    hook_domains = [str(item).strip() for item in (hook.get("domains") or []) if str(item).strip()]
    if not hook_domains or not event_domains:
        return 0.0
    overlap = len(set(hook_domains) & set(event_domains))
    if overlap <= 0:
        return 0.0
    return round(min(1.0, 0.45 + (0.2 * overlap) + (0.05 * len(hook.get("spine_lines") or []))), 3)


def build_transit_natal_activation_context(
    *,
    canonical_state: CanonicalNatalStateV1,
    period_core: Mapping[str, Any] | None,
    daily_event_cards: list[Mapping[str, Any]] | None,
    period_event_cards: list[Mapping[str, Any]] | None,
) -> dict[str, Any]:
    graph = canonical_state.meaning_graph if isinstance(canonical_state.meaning_graph, Mapping) else {}
    hooks = [dict(item) for item in (graph.get("activation_hooks") or []) if isinstance(item, Mapping)]
    event_rows: list[dict[str, Any]] = []

    for scope, cards in (
        ("daily", daily_event_cards or []),
        ("period", period_event_cards or []),
    ):
        for raw_event in cards:
            if not isinstance(raw_event, Mapping):
                continue
            event_id = str(raw_event.get("event_id") or "").strip()
            if not event_id:
                continue
            domains = _event_domains(raw_event)
            matches = []
            for hook in hooks:
                score = _score_hook_match(hook, domains)
                if score <= 0.0:
                    continue
                matches.append(
                    {
                        "hook_id": str(hook.get("hook_id") or ""),
                        "target_node_id": str(hook.get("target_node_id") or ""),
                        "score": score,
                        "domains": list(hook.get("domains") or []),
                        "spine_lines": list(hook.get("spine_lines") or []),
                    }
                )
            matches.sort(key=lambda item: (-float(item["score"]), item["target_node_id"]))
            event_rows.append(
                {
                    "event_id": event_id,
                    "scope": scope,
                    "domains": domains,
                    "matched_hooks": matches[:3],
                }
            )

    hook_summary: dict[str, dict[str, Any]] = {}
    for row in event_rows:
        for match in row["matched_hooks"]:
            slot = hook_summary.setdefault(
                match["hook_id"],
                {
                    "hook_id": match["hook_id"],
                    "target_node_id": match["target_node_id"],
                    "domains": list(match["domains"]),
                    "spine_lines": list(match["spine_lines"]),
                    "score": 0.0,
                    "matched_event_ids": [],
                },
            )
            slot["score"] = round(float(slot["score"]) + float(match["score"]), 3)
            if row["event_id"] not in slot["matched_event_ids"]:
                slot["matched_event_ids"].append(row["event_id"])

    top_hooks = sorted(
        hook_summary.values(),
        key=lambda item: (-float(item["score"]), str(item["target_node_id"])),
    )[:5]
    by_event_id = {
        row["event_id"]: {
            "scope": row["scope"],
            "domains": row["domains"],
            "matched_hook_ids": [match["hook_id"] for match in row["matched_hooks"]],
            "target_node_ids": [match["target_node_id"] for match in row["matched_hooks"]],
        }
        for row in event_rows
    }
    period_event_ids = [
        str(item.get("event_id") or "").strip()
        for item in (period_event_cards or [])
        if isinstance(item, Mapping) and str(item.get("event_id") or "").strip()
    ]
    daily_event_ids = [
        str(item.get("event_id") or "").strip()
        for item in (daily_event_cards or [])
        if isinstance(item, Mapping) and str(item.get("event_id") or "").strip()
    ]

    return {
        "version": "canonical_natal_activation_v1",
        "chart_id": canonical_state.chart_id,
        "graph_version": str(graph.get("version") or ""),
        "top_hooks": top_hooks,
        "by_event_id": by_event_id,
        "period_core": {
            "title": str((period_core or {}).get("title") or ""),
            "matched_event_ids": [event_id for event_id in period_event_ids if event_id in by_event_id],
            "top_hook_ids": [
                item["hook_id"]
                for item in top_hooks
                if any(event_id in item["matched_event_ids"] for event_id in period_event_ids)
            ],
        },
        "daily_selection": {
            "matched_event_ids": [event_id for event_id in daily_event_ids if event_id in by_event_id],
            "top_hook_ids": [
                item["hook_id"]
                for item in top_hooks
                if any(event_id in item["matched_event_ids"] for event_id in daily_event_ids)
            ],
        },
        "daily_synthesis": {
            "top_target_node_ids": [
                item["target_node_id"]
                for item in top_hooks
                if any(event_id in item["matched_event_ids"] for event_id in [*daily_event_ids, *period_event_ids])
            ][:3],
        },
    }


def build_period_prefix_from_activation_context(
    activation_context: Mapping[str, Any] | None,
) -> str | None:
    context = activation_context if isinstance(activation_context, Mapping) else {}
    period_core = context.get("period_core") if isinstance(context.get("period_core"), Mapping) else {}
    top_hook_ids = {str(item).strip() for item in (period_core.get("top_hook_ids") or []) if str(item).strip()}
    top_hooks = [dict(item) for item in (context.get("top_hooks") or []) if isinstance(item, Mapping)]
    for hook in top_hooks:
        hook_id = str(hook.get("hook_id") or "").strip()
        if top_hook_ids and hook_id not in top_hook_ids:
            continue
        domains = [str(item).strip() for item in (hook.get("domains") or []) if str(item).strip()]
        for domain in domains:
            prefix = _PERIOD_PREFIX_BY_DOMAIN.get(domain)
            if prefix:
                return prefix
    return None


def build_canonical_period_spine(
    *,
    canonical_state: CanonicalNatalStateV1,
    period_event_cards: list[Mapping[str, Any]] | None,
    period_core: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    activation_context = build_transit_natal_activation_context(
        canonical_state=canonical_state,
        period_core=period_core,
        daily_event_cards=[],
        period_event_cards=period_event_cards or [],
    )
    top_hooks = [dict(item) for item in (activation_context.get("top_hooks") or []) if isinstance(item, Mapping)]
    period_match = activation_context.get("period_core") if isinstance(activation_context.get("period_core"), Mapping) else {}
    period_hook_ids = {str(item).strip() for item in (period_match.get("top_hook_ids") or []) if str(item).strip()}
    matched_hook = next(
        (
            hook
            for hook in top_hooks
            if not period_hook_ids or str(hook.get("hook_id") or "").strip() in period_hook_ids
        ),
        None,
    )
    if matched_hook is None:
        return {}
    domains = [str(item).strip() for item in (matched_hook.get("domains") or []) if str(item).strip()]
    primary_domain = domains[0] if domains else ""
    return {
        "version": "canonical_period_spine_v1",
        "source": "canonical_natal_activation_v1",
        "chart_id": str(activation_context.get("chart_id") or canonical_state.chart_id),
        "graph_version": str(activation_context.get("graph_version") or ""),
        "hook_id": str(matched_hook.get("hook_id") or ""),
        "target_node_id": str(matched_hook.get("target_node_id") or ""),
        "domains": domains,
        "primary_domain": primary_domain,
        "theme": _PERIOD_THEME_BY_DOMAIN.get(primary_domain, ""),
        "prefix": _PERIOD_PREFIX_BY_DOMAIN.get(primary_domain, ""),
        "spine_lines": list(matched_hook.get("spine_lines") or []),
        "matched_event_ids": list(period_match.get("matched_event_ids") or []),
        "source_debug": {
            "top_hook_ids": list(period_match.get("top_hook_ids") or []),
            "matched_event_ids": list(period_match.get("matched_event_ids") or []),
            "source_version": "canonical_natal_activation_v1",
        },
    }


def build_period_prefix_from_period_spine(period_spine: Mapping[str, Any] | None) -> str | None:
    spine = period_spine if isinstance(period_spine, Mapping) else {}
    prefix = str(spine.get("prefix") or "").strip()
    return prefix or None


def select_period_theme_from_spine(period_spine: Mapping[str, Any] | None) -> str | None:
    spine = period_spine if isinstance(period_spine, Mapping) else {}
    theme = str(spine.get("theme") or "").strip()
    return theme or None
