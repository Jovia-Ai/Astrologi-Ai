"""Phase-2 selector enforcing the deterministic contract with quota, diversity, and telemetry."""

from __future__ import annotations

import hashlib
from collections import Counter
from typing import Iterable, Mapping, Sequence

from app.ontology.theme_loader import load_theme_config, ThemeOntology

POOL_K = 30
MAX_SLOTS = 6
BUFFER_MULTIPLIER = 2
SLOT_ORDER = ("cause", "mechanism", "effect", "shadow", "potential")
DOMAIN_PRIORITY = ["identity", "relating", "career", "resources", "inner_life", "public_life"]
AXIS_PRIORITY = ["1-7", "4-10", "2-8", "3-9"]
TOP_THEME_SHARE_CAP = 0.55


class Phase2SelectionError(Exception):
    """Raised when the selector cannot honor the deterministic contract."""


class Phase2Selector:
    """Deterministic selector for phase-2 slots."""

    def __init__(self):
        self.ontology: ThemeOntology = load_theme_config()
        self._allow_single_reuse = True
        self._relaxation_flags: list[str] = []
        self._deadlock_snapshot: dict[str, int] | None = None
        self._theme_shares: Mapping[str, float] = {}
        self._duplicate_signature_candidates: list[tuple[Mapping[str, object], str]] = []
        self._signature_relaxation_used = False

    def select_phase2_slots(
        self,
        chart_hash: str,
        signals: Sequence[Mapping[str, object]],
    ) -> list[Mapping[str, object]]:
        self._allow_single_reuse = True
        self._relaxation_flags = []
        self._deadlock_snapshot = None
        self._theme_shares = {}
        self._duplicate_signature_candidates = []
        self._signature_relaxation_used = False
        validated = self._validate_signals(signals)
        pool = self._build_pool(validated)
        buffered = pool[: min(len(pool), MAX_SLOTS * BUFFER_MULTIPLIER)]
        if not buffered:
            raise Phase2SelectionError("No valid signals after buffering.")
        staged = [self._enrich_signal(sig, chart_hash) for sig in buffered]
        assigned = self._assign_slots(staged)
        quota_adjusted = self._apply_theme_quota(assigned, staged)
        diversified = self._apply_diversity_check(quota_adjusted, staged)
        anchored = self._apply_anchor_guard(diversified, staged)
        felt_map = self._build_felt_intensity_map(anchored)
        for slot in anchored:
            slot["relaxation_flags"] = list(self._relaxation_flags)
            slot["felt_intensity_map"] = dict(felt_map) if felt_map else {}
            if self._deadlock_snapshot:
                slot["deadlock_snapshot"] = dict(self._deadlock_snapshot)
        return anchored

    def _validate_signals(self, signals: Sequence[Mapping[str, object]]) -> list[Mapping[str, object]]:
        if not signals:
            raise Phase2SelectionError("No signals provided.")
        validated: list[Mapping[str, object]] = []
        theme_ids = {theme.theme_id for theme in self.ontology.themes}
        seen_signatures: set[str] = set()
        for signal in signals:
            theme = signal.get("theme")
            if not theme or theme not in theme_ids:
                raise Phase2SelectionError("Missing or unknown theme in signal.")
            provenance = signal.get("provenance")
            if not (isinstance(provenance, list) and 1 <= len(provenance) <= 3):
                raise Phase2SelectionError("Signal provenance must be a list of 1-3 items.")
            for item in provenance:
                if not (isinstance(item, Mapping) and item.get("type") and item.get("ref_id")):
                    raise Phase2SelectionError("Provenance items must declare type and ref_id.")
            signature = f"{theme}-{signal.get('signal_id')}"
            if signature in seen_signatures:
                raise Phase2SelectionError("Duplicate signal signature detected.")
            seen_signatures.add(signature)
            if not signal.get("domain_candidates"):
                raise Phase2SelectionError("Signal must provide domain_candidates.")
            if not signal.get("axis_candidates"):
                raise Phase2SelectionError("Signal must provide axis_candidates.")
            validated.append(signal)
        return validated

    def _build_pool(self, signals: Sequence[Mapping[str, object]]) -> list[Mapping[str, object]]:
        return sorted(
            signals,
            key=lambda item: float(item.get("experienced_weight", 0.0)),
            reverse=True,
        )[:POOL_K]

    def _choose_domain(self, signal: Mapping[str, object], chart_hash: str) -> str:
        candidates = [str(item) for item in signal.get("domain_candidates", [])]
        focus = str(signal.get("focus_object", ""))
        return self._choose_from_priority(candidates, DOMAIN_PRIORITY, chart_hash, signal.get("signal_id"), focus)

    def _choose_axis(self, signal: Mapping[str, object], chart_hash: str) -> str:
        candidates = [str(item) for item in signal.get("axis_candidates", [])]
        focus = str(signal.get("focus_object", ""))
        return self._choose_from_priority(candidates, AXIS_PRIORITY, chart_hash, signal.get("signal_id"), focus)

    def _choose_from_priority(
        self,
        candidates: Sequence[str],
        priority: Sequence[str],
        chart_hash: str,
        signal_id: object,
        focus: str | None = None,
    ) -> str:
        filtered = [candidate for candidate in candidates if candidate]
        for item in priority:
            if item in filtered:
                return item
        if not filtered:
            return ""
        normalized_focus = focus or ""
        seed = f"{chart_hash}-{normalized_focus}-{signal_id}-{','.join(filtered)}"
        digest = hashlib.sha256(seed.encode("utf-8")).digest()
        return filtered[digest[0] % len(filtered)]

    def _enrich_signal(self, signal: Mapping[str, object], chart_hash: str) -> Mapping[str, object]:
        return {
            **signal,
            "domain": self._choose_domain(signal, chart_hash),
            "axis": self._choose_axis(signal, chart_hash),
            "selection_reason": None,
            "rejected_reasons": [],
        }

    def _assign_slots(self, buffer: Sequence[Mapping[str, object]]) -> list[Mapping[str, object]]:
        assigned: list[Mapping[str, object]] = []
        theme_counts: Counter[str] = Counter()
        used_signatures: set[str] = set()
        used_slots: set[str] = set()
        for signal in buffer:
            slot_candidate = self._find_slot_candidate(signal, used_slots)
            if not slot_candidate:
                signal.setdefault("rejected_reasons", []).append("slot_unavailable")
                continue
            signature = self._signature(signal, slot_candidate)
            if signature in used_signatures:
                self._duplicate_signature_candidates.append((signal, slot_candidate))
                signal.setdefault("rejected_reasons", []).append("duplicate_signature")
                continue
            if not self._within_share_cap(signal, theme_counts, assigned):
                signal.setdefault("rejected_reasons", []).append("share_cap")
                continue
            entry = self._build_slot_entry(signal, slot_candidate)
            entry["selection_reason"] = "slot_priority_match"
            entry["rejected_reasons"] = list(signal.get("rejected_reasons", []))
            assigned.append(entry)
            theme_counts[signal["theme"]] += 1
            used_signatures.add(signature)
            used_slots.add(slot_candidate)
        if len(assigned) < min(len(buffer), len(SLOT_ORDER)) and self._allow_single_reuse:
            reuse = self._reuse_slot_if_deadlock(buffer, assigned, used_signatures)
            if reuse:
                self._allow_single_reuse = False
                assigned.append(reuse)
        return assigned

    def _within_share_cap(
        self,
        signal: Mapping[str, object],
        theme_counts: Counter[str],
        assigned: Iterable[Mapping[str, object]],
    ) -> bool:
        candidate_theme = signal["theme"]
        projected = theme_counts[candidate_theme] + 1
        total = len(list(assigned)) + 1
        return (projected / total) <= TOP_THEME_SHARE_CAP

    def _build_slot_entry(self, signal: Mapping[str, object], slot_name: str) -> dict[str, object]:
        return {
            "slot": slot_name,
            "theme": signal["theme"],
            "domain": signal["domain"],
            "axis": signal["axis"],
            "focus_object": signal.get("focus_object"),
            "activation_type": signal.get("activation_type"),
            "trigger_tags": signal.get("trigger_tags", []),
            "provenance": signal.get("provenance", []),
            "experienced_weight": max(
                0.05,
                float(signal.get("experienced_weight", signal.get("signal_score", 0))),
            ),
            "selection_reason": None,
            "rejected_reasons": [],
            "domain_candidates": list(signal.get("domain_candidates", [])),
            "axis_candidates": list(signal.get("axis_candidates", [])),
        }

    def _signature(self, signal: Mapping[str, object], slot: str) -> str:
        return "|".join(
            [
                signal.get("theme", ""),
                str(signal.get("focus_object", "")),
                signal.get("domain", ""),
                slot,
            ]
        )

    def _find_slot_candidate(
        self,
        signal: Mapping[str, object],
        used_slots: set[str],
        allow_used: bool = False,
    ) -> str | None:
        for slot in SLOT_ORDER:
            if slot not in signal.get("slot_candidates", []):
                continue
            if slot in used_slots and not allow_used:
                continue
            return slot
        return None

    def _reuse_slot_if_deadlock(
        self,
        buffer: Sequence[Mapping[str, object]],
        assigned: list[Mapping[str, object]],
        used_signatures: set[str],
    ) -> Mapping[str, object] | None:
        if len(assigned) >= min(len(buffer), len(SLOT_ORDER)):
            return None
        for signal in buffer:
            slot_candidate = self._find_slot_candidate(signal, set(), allow_used=True)
            if not slot_candidate:
                continue
            signature = self._signature(signal, slot_candidate)
            if signature in used_signatures:
                continue
            entry = self._build_slot_entry(signal, slot_candidate)
            entry["selection_reason"] = "deadlock_reuse"
            entry["rejected_reasons"] = list(signal.get("rejected_reasons", []))
            return entry
        return None

    def _apply_theme_quota(
        self,
        assigned: list[Mapping[str, object]],
        buffer: Sequence[Mapping[str, object]],
    ) -> list[Mapping[str, object]]:
        weight_values: Counter[str] = Counter()
        for slot in assigned:
            weight_values[slot["theme"]] += slot.get("experienced_weight", 0.0)
        selected = list(assigned)
        while True:
            total = sum(weight_values.values()) or 1
            shares = {theme: weight_values[theme] / total for theme in set(weight_values)}
            self._theme_shares = shares
            if shares and max(shares.values(), default=0) <= TOP_THEME_SHARE_CAP:
                break
            promote = self._best_signal_from(
                buffer,
                lambda x: shares.get(x["theme"], 0) < TOP_THEME_SHARE_CAP,
                selected,
            )
            if not promote:
                break
            entry = self._build_slot_entry(promote, promote.get("slot_candidates", ["cause"])[0])
            entry["selection_reason"] = "theme_share_promote"
            entry["rejected_reasons"] = list(promote.get("rejected_reasons", []))
            selected.append(entry)
            weight_values[promote["theme"]] += entry["experienced_weight"]
        return selected

    def _best_signal_from(
        self,
        buffer: Sequence[Mapping[str, object]],
        condition,
        selected: Sequence[Mapping[str, object]],
    ) -> Mapping[str, object] | None:
        selected_signatures = {self._signature(slot, slot["slot"]) for slot in selected}
        for signal in sorted(buffer, key=lambda item: float(item.get("experienced_weight", 0.0)), reverse=True):
            if condition(signal):
                candidate_signature = self._signature(signal, signal.get("slot_candidates", ["cause"])[0])
                if candidate_signature in selected_signatures:
                    continue
                return signal
        return None

    def _apply_diversity_check(
        self,
        slots: list[Mapping[str, object]],
        buffer: Sequence[Mapping[str, object]],
    ) -> list[Mapping[str, object]]:
        status = self._diversity_status(slots)
        if status == "DEADLOCK" and not self._deadlock_snapshot:
            axes = {slot.get("axis") for slot in slots if slot.get("axis")}
            domains = {slot.get("domain") for slot in slots if slot.get("domain")}
            self._deadlock_snapshot = {"axes": len(axes), "domains": len(domains)}
        if status != "DEADLOCK":
            return slots
        for step in (
            self._allow_template_variant_flag,
            self._drop_trigger_tags,
            self._shorten_provenance,
            self._swap_theme_candidate,
            self._reduce_slot_count_keep_anchor,
            self._fallback_anchor_plus_micro,
            self._relax_signature_for_micro_insight,
            self._widen_domain_for_micro_only,
        ):
            slots = step(slots, buffer)
            if self._diversity_status(slots) != "DEADLOCK":
                return slots
        return slots

    def _diversity_status(self, slots: Sequence[Mapping[str, object]]) -> str:
        axes = {slot.get("axis") for slot in slots if slot.get("axis")}
        domains = {slot.get("domain") for slot in slots if slot.get("domain")}
        if len(axes) >= 2 and len(domains) >= 2:
            return "PASS"
        if len(axes) >= 2 or len(domains) >= 2:
            return "PASS_MIN"
        return "DEADLOCK"

    def _allow_template_variant_flag(
        self,
        slots: list[Mapping[str, object]],
        _: Sequence[Mapping[str, object]],
    ) -> list[Mapping[str, object]]:
        if "allow_template_variant_flag" not in self._relaxation_flags:
            self._relaxation_flags.append("allow_template_variant_flag")
        return slots

    def _drop_trigger_tags(
        self,
        slots: list[Mapping[str, object]],
        _: Sequence[Mapping[str, object]],
    ) -> list[Mapping[str, object]]:
        self._relaxation_flags.append("drop_trigger_tags")
        return [slot for slot in slots if len(slot.get("trigger_tags", [])) <= 2]

    def _shorten_provenance(
        self,
        slots: list[Mapping[str, object]],
        _: Sequence[Mapping[str, object]],
    ) -> list[Mapping[str, object]]:
        self._relaxation_flags.append("shorten_provenance")
        return sorted(slots, key=lambda item: len(item.get("provenance", [])))[:MAX_SLOTS]

    def _swap_theme_candidate(
        self,
        slots: list[Mapping[str, object]],
        buffer: Sequence[Mapping[str, object]],
    ) -> list[Mapping[str, object]]:
        self._relaxation_flags.append("swap_theme_candidate")
        used_themes = {slot["theme"] for slot in slots}
        for signal in buffer:
            if signal["theme"] not in used_themes:
                swapped = slots.copy()
                if swapped:
                    swapped[-1] = self._build_slot_entry(signal, swapped[-1]["slot"])
                    swapped[-1]["selection_reason"] = "diversity_swap"
                    swapped[-1]["rejected_reasons"] = list(signal.get("rejected_reasons", []))
                    return swapped
        return slots

    def _reduce_slot_count_keep_anchor(
        self,
        slots: list[Mapping[str, object]],
        _: Sequence[Mapping[str, object]],
    ) -> list[Mapping[str, object]]:
        self._relaxation_flags.append("reduce_slot_count_keep_anchor")
        anchor = next((slot for slot in slots if slot["slot"] in {"cause", "mechanism"}), None)
        others = [slot for slot in slots if slot != anchor]
        return ([anchor] + others[:1]) if anchor else slots[:2]

    def _fallback_anchor_plus_micro(
        self,
        slots: list[Mapping[str, object]],
        _: Sequence[Mapping[str, object]],
    ) -> list[Mapping[str, object]]:
        self._relaxation_flags.append("fallback_anchor_plus_micro")
        anchor = next((slot for slot in slots if slot["slot"] in {"cause", "mechanism"}), None)
        if not anchor:
            return slots
        micro = {
            "slot": "micro_insight",
            "theme": anchor["theme"],
            "domain": anchor["domain"],
            "axis": anchor.get("axis"),
            "focus_object": anchor.get("focus_object"),
            "activation_type": anchor.get("activation_type"),
            "trigger_tags": anchor.get("trigger_tags", []),
            "provenance": anchor.get("provenance", []),
            "experienced_weight": anchor.get("experienced_weight", 0.0),
            "selection_reason": "anchor_micro_insight",
            "rejected_reasons": [],
        }
        return [anchor, micro]

    def _widen_domain_for_micro_only(
        self,
        slots: list[Mapping[str, object]],
        _: Sequence[Mapping[str, object]],
    ) -> list[Mapping[str, object]]:
        self._relaxation_flags.append("widen_domain_for_micro_only")
        seen_domains = {slot.get("domain") for slot in slots if slot.get("domain")}
        for slot in slots:
            if slot["slot"] != "micro_insight":
                continue
            candidates = slot.get("domain_candidates") or []
            for domain in candidates:
                if domain not in seen_domains:
                    slot["domain"] = domain
                    slot["selection_reason"] = "domain_widened"
                    slot["rejected_reasons"] = slot.get("rejected_reasons", [])
                    seen_domains.add(domain)
                    return slots
        return slots

    def _relax_signature_for_micro_insight(
        self,
        slots: list[Mapping[str, object]],
        _: Sequence[Mapping[str, object]],
    ) -> list[Mapping[str, object]]:
        if self._signature_relaxation_used:
            return slots
        if any(slot.get("slot") == "micro_insight" for slot in slots):
            return slots
        if not self._duplicate_signature_candidates:
            return slots
        anchor = next((slot for slot in slots if slot["slot"] in {"cause", "mechanism"}), None)
        if not anchor:
            return slots
        best_entry = max(
            self._duplicate_signature_candidates,
            key=lambda entry: float(entry[0].get("experienced_weight", 0.0)),
            default=None,
        )
        if not best_entry:
            return slots
        signal, _ = best_entry
        micro = self._build_slot_entry(signal, "micro_insight")
        micro["focus_object"] = None
        micro["selection_reason"] = "signature_relaxed_micro_insight"
        micro["rejected_reasons"] = list(signal.get("rejected_reasons", []))
        self._signature_relaxation_used = True
        self._duplicate_signature_candidates.clear()
        self._relaxation_flags.append("signature_relaxed_micro")
        return slots + [micro]

    def _apply_anchor_guard(
        self,
        slots: list[Mapping[str, object]],
        buffer: Sequence[Mapping[str, object]],
    ) -> list[Mapping[str, object]]:
        cause_mech = next((slot for slot in slots if slot["slot"] in {"cause", "mechanism"}), None)
        if cause_mech:
            return slots
        anchor = self._select_anchor(buffer)
        if not anchor:
            return slots
        slot_candidate = self._find_slot_candidate(anchor, set()) or "cause"
        entry = self._build_slot_entry(anchor, slot_candidate)
        entry["selection_reason"] = "anchor_selected"
        entry["rejected_reasons"] = list(anchor.get("rejected_reasons", []))
        return [entry]

    def _select_anchor(self, buffer: Sequence[Mapping[str, object]]) -> Mapping[str, object] | None:
        candidates = [
            signal
            for signal in buffer
            if any(slot in signal.get("slot_candidates", []) for slot in {"cause", "mechanism"})
        ]
        if not candidates:
            return None
        top_themes = self._top_share_themes()
        best: Mapping[str, object] | None = None
        best_score = -1.0
        for signal in candidates:
            score = self._anchor_score(signal, top_themes)
            if score > best_score:
                best_score = score
                best = signal
        return best

    def _top_share_themes(self) -> set[str]:
        if not self._theme_shares:
            return set()
        max_share = max(self._theme_shares.values(), default=0)
        return {theme for theme, share in self._theme_shares.items() if share == max_share}

    def _anchor_score(self, signal: Mapping[str, object], top_themes: set[str]) -> float:
        base = float(signal.get("experienced_weight", signal.get("signal_score", 0)))
        bonus = 0.0
        if signal.get("theme") in top_themes:
            bonus += 0.15
        focus = str(signal.get("focus_object", "")).upper()
        if focus in {"CHART_RULER", "ASC", "MC"}:
            bonus += 0.1
        return base * (1 + min(bonus, 0.25))

    def _build_felt_intensity_map(self, slots: Sequence[Mapping[str, object]]) -> dict[str, float]:
        totals: Counter[str] = Counter()
        for slot in slots:
            domain = str(slot.get("domain") or "unknown")
            weight = float(slot.get("experienced_weight", 0.0))
            if weight > 0:
                totals[domain] += weight
        total = sum(totals.values())
        if total <= 0:
            return {}
        return {domain: value / total for domain, value in totals.items()}
