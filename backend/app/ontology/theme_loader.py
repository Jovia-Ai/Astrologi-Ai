"""Load and validate the deterministic theme ontology for JOVIA."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Tuple

import json

DEFAULT_CONFIG_PATH = (
    Path(__file__).resolve().parents[3] / "config" / "ontology" / "themes.yaml"
)


@dataclass(frozen=True)
class ThemeDefinition:
    theme_id: str
    question: str
    tension: str
    share_weight: float
    keywords: Tuple[str, ...]


@dataclass(frozen=True)
class ThemeOntology:
    max_themes_per_paragraph: int
    top_theme_share_cap: float
    repetition_factor_cap: float
    themes: Tuple[ThemeDefinition, ...]


def load_theme_config(config_path: Path | None = None) -> ThemeOntology:
    path = config_path or DEFAULT_CONFIG_PATH
    if not path.exists():
        raise FileNotFoundError(f"Theme config missing at {path}")
    raw = json.loads(path.read_text())
    ontology = _parse_raw_config(raw)
    _validate_theme_ontology(ontology)
    return ontology


def _parse_raw_config(raw: Mapping[str, object]) -> ThemeOntology:
    if not raw:
        raise ValueError("Theme configuration is empty.")
    defaults = raw.get("defaults") or {}
    caps = raw.get("caps") or {}
    max_per_paragraph = int(defaults.get("max_themes_per_paragraph", 1))
    top_cap = float(defaults.get("top_theme_share_cap", 1.0))
    repetition_cap = float(caps.get("repetition_factor_cap", 1.0))
    theme_entries = raw.get("themes") or {}
    if not isinstance(theme_entries, Mapping):
        raise ValueError("`themes` section must be a mapping.")

    definitions: list[ThemeDefinition] = []
    for raw_id, raw_entry in theme_entries.items():
        if not isinstance(raw_entry, Mapping):
            raise ValueError(f"Theme entry {raw_id!r} must be a mapping.")
        question = str(raw_entry.get("question") or raw_entry.get("description") or "").strip()
        tension = str(raw_entry.get("tension") or "").strip()
        share_value = raw_entry.get("share_weight")
        if share_value is None:
            raise ValueError(f"Theme {raw_id} must declare a share_weight.")
        keywords_raw = raw_entry.get("keywords") or []
        keywords = tuple(dict.fromkeys(str(keyword).strip().lower() for keyword in keywords_raw if keyword))
        definitions.append(
            ThemeDefinition(
                theme_id=str(raw_id),
                question=question,
                tension=tension,
                share_weight=float(share_value),
                keywords=keywords,
            )
        )

    if not definitions:
        raise ValueError("No theme definitions were provided.")

    return ThemeOntology(
        max_themes_per_paragraph=max_per_paragraph,
        top_theme_share_cap=top_cap,
        repetition_factor_cap=repetition_cap,
        themes=tuple(definitions),
    )


def _validate_theme_ontology(ontology: ThemeOntology) -> None:
    if ontology.max_themes_per_paragraph < 1:
        raise ValueError("max_themes_per_paragraph must be at least 1.")
    if not (0 < ontology.top_theme_share_cap <= 1):
        raise ValueError("top_theme_share_cap must be between 0 and 1.")
    if not (0 <= ontology.repetition_factor_cap <= 1):
        raise ValueError("repetition_factor_cap must be between 0 and 1.")

    seen_theme_ids: set[str] = set()
    keyword_map: dict[str, str] = {}
    for theme in ontology.themes:
        if not theme.question:
            raise ValueError(f"Theme {theme.theme_id} is missing a question.")
        if not theme.tension:
            raise ValueError(f"Theme {theme.theme_id} is missing a tension identifier.")
        if not theme.keywords:
            raise ValueError(f"Theme {theme.theme_id} must declare at least one keyword.")
        if theme.theme_id in seen_theme_ids:
            raise ValueError(f"Duplicate theme identifier: {theme.theme_id}")
        seen_theme_ids.add(theme.theme_id)

        if theme.share_weight <= 0 or theme.share_weight > 1:
            raise ValueError(f"share_weight for {theme.theme_id} must be within (0, 1].")
        if theme.share_weight > ontology.top_theme_share_cap:
            raise ValueError(
                f"share_weight for {theme.theme_id} ({theme.share_weight}) exceeds top_theme_share_cap ({ontology.top_theme_share_cap})."
            )

        for keyword in theme.keywords:
            if keyword in keyword_map and keyword_map[keyword] != theme.theme_id:
                raise ValueError(
                    f"Semantic overlap detected between {theme.theme_id} and {keyword_map[keyword]} on keyword '{keyword}'."
                )
            keyword_map[keyword] = theme.theme_id

    tensions_seen: dict[str, str] = {}
    for theme in ontology.themes:
        tension = theme.tension.lower()
        if tension in tensions_seen and tensions_seen[tension] != theme.theme_id:
            raise ValueError(f"Conflicting tension {tension} used by {theme.theme_id} and {tensions_seen[tension]}.")
        tensions_seen[tension] = theme.theme_id
