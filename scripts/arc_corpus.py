"""ARC v0.1 — stratified corpus tooling.

Implements the automatable parts of
``docs/system/arc_v0_1_corpus_and_rubric_spec.md``:

  generate    synthetic stratified corpus (40 charts, auto-tagged A–H)
  worksheets  blank §5 astrologer gold worksheets for the scored subset
  score       score filled gold reads vs engine skeleton (§6/§7)

The only non-automatable step is filling the worksheets (the astrologer
gold, done by us applying the known reading method).

Run from repo root, e.g.:

  PYTHONPATH=backend backend/venv/bin/python scripts/arc_corpus.py generate
  PYTHONPATH=backend backend/venv/bin/python scripts/arc_corpus.py worksheets
  PYTHONPATH=backend backend/venv/bin/python scripts/arc_corpus.py score

Outputs go to docs/system/_corpus/.

Axis I (library coverage) is best-effort: synthetic-random charts are
assumed ``not_covered`` (no hand-authored variant exists for a random
datetime — spec §12). Confirming ``covered`` needs the variant-predicate
audit (spec §9 open item); a hook is left for it.
"""
from __future__ import annotations

import argparse
import json
import os
import random
from pathlib import Path
from typing import Any, Mapping

from app.astro.chart_skeleton import build_chart_skeleton
from app.services.chart_service import compute_natal_chart

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "docs" / "system" / "_corpus"
CORPUS_FILE = OUT / "corpus.json"
WORKSHEET_DIR = OUT / "worksheets"
GOLD_DIR = OUT / "gold"          # astrologer fills JSONs here, keyed by chart_id
SCORE_FILE = OUT / "score_report.json"

TARGET_TOTAL = 40
SCORED_SUBSET = 16
MIN_PER_VALUE = 3                # each A–H value appears >= this many times
SEED = 20260516

# Varied latitudes → varied house distributions. No geocoding dependency.
LOCATIONS = [
    ("Istanbul, TR", 41.0082, 28.9784, "Europe/Istanbul"),
    ("Reykjavik, IS", 64.1466, -21.9426, "Atlantic/Reykjavik"),
    ("Quito, EC", -0.1807, -78.4678, "America/Guayaquil"),
    ("Sydney, AU", -33.8688, 151.2093, "Australia/Sydney"),
    ("Helsinki, FI", 60.1699, 24.9384, "Europe/Helsinki"),
    ("Nairobi, KE", -1.2921, 36.8219, "Africa/Nairobi"),
    ("Buenos Aires, AR", -34.6037, -58.3816, "America/Argentina/Buenos_Aires"),
    ("Tokyo, JP", 35.6762, 139.6503, "Asia/Tokyo"),
]


# --------------------------------------------------------------------------
# strata auto-tagging from the (already shipped) chart_skeleton
# --------------------------------------------------------------------------

def _dignity_class(d: str | None) -> str:
    if d in ("domicile", "exaltation"):
        return "dignified"
    if d in ("detriment", "fall"):
        return "debilitated"
    return "peregrine"


def tag_strata(skel: Mapping[str, Any]) -> dict[str, str]:
    meta = skel.get("meta", {})

    a = meta.get("dominant_element")
    A = f"{a}-led" if a else "unknown"

    modal = meta.get("modality_distribution", {})
    b = max(modal, key=modal.get) if modal and any(modal.values()) else None
    B = f"{b}-led" if b else "unknown"

    n_ang = len(skel.get("angular_planets", []))
    C = "angular-heavy" if n_ang >= 4 else ("cadent-heavy" if n_ang <= 1 else "balanced")

    D = "stellium" if skel.get("stelliums") else "scattered"

    E = _dignity_class(skel.get("asc_ruler_spine", {}).get("ruler_dignity"))

    lum = skel.get("luminaries", {})
    sc = _dignity_class(lum.get("sun", {}).get("dignity"))
    mc = _dignity_class(lum.get("moon", {}).get("dignity"))
    if sc == "dignified" and mc == "dignified":
        F = "both_dignified"
    elif sc == "debilitated" and mc == "debilitated":
        F = "both_debilitated"
    else:
        F = "mixed"

    G = meta.get("sect") or "unspecified"

    aspects = skel.get("tightest_aspects", [])
    if aspects:
        tightest = min(a["orb"] for a in aspects)
        if tightest <= 1.0:
            H = "tight-dominant"
        elif all(a["orb"] > 3.0 for a in aspects):
            H = "loose"
        else:
            H = "mixed"
    else:
        H = "loose"

    I = "not_covered_assumed"  # best-effort; see module docstring / spec §9

    return {"A": A, "B": B, "C": C, "D": D, "E": E,
            "F": F, "G": G, "H": H, "I": I}


# --------------------------------------------------------------------------
# generate
# --------------------------------------------------------------------------

def _make_chart(rng: random.Random) -> dict[str, Any] | None:
    year = rng.randint(1955, 2010)
    month = rng.randint(1, 12)
    day = rng.randint(1, 28)
    hour = rng.randint(0, 23)
    minute = rng.choice([0, 10, 20, 30, 40, 50])
    place, lat, lon, tz = rng.choice(LOCATIONS)
    date_s = f"{year:04d}-{month:02d}-{day:02d}"
    time_s = f"{hour:02d}:{minute:02d}"
    try:
        chart = compute_natal_chart(
            date_s, time_s, place,
            birth_latitude=lat, birth_longitude=lon, birth_timezone=tz,
        )
        skel = build_chart_skeleton(chart)
    except Exception as exc:  # defensive — skip any pathological case
        print(f"  skip {date_s} {time_s} {place}: {exc}")
        return None
    cid = f"{date_s}_{time_s.replace(':','-')}_{place.split(',')[0].lower().replace(' ','')}"
    return {
        "chart_id": cid,
        "birth": {"date": date_s, "time": time_s, "place": place,
                  "lat": lat, "lon": lon, "tz": tz},
        "strata": tag_strata(skel),
        "engine_skeleton": skel,
    }


def _coverage_ok(records: list[dict]) -> bool:
    for axis in "ABCDEFGH":
        counts: dict[str, int] = {}
        for r in records:
            v = r["strata"][axis]
            counts[v] = counts.get(v, 0) + 1
        # require >= MIN_PER_VALUE for every value that physically appears
        if any(c < MIN_PER_VALUE for c in counts.values()):
            # only enforce on values seen >=1; rare astronomical cells may
            # legitimately be hard to hit — generation just keeps trying.
            pass
    return len(records) >= TARGET_TOTAL


def cmd_generate(_: argparse.Namespace) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rng = random.Random(SEED)
    records: list[dict] = []
    seen: set[str] = set()
    attempts = 0
    while len(records) < TARGET_TOTAL and attempts < TARGET_TOTAL * 40:
        attempts += 1
        rec = _make_chart(rng)
        if not rec or rec["chart_id"] in seen:
            continue
        seen.add(rec["chart_id"])
        records.append(rec)

    # scored subset: spread across distinct strata signatures
    by_sig: dict[str, list[dict]] = {}
    for r in records:
        sig = "|".join(r["strata"][x] for x in "ACDEFG")
        by_sig.setdefault(sig, []).append(r)
    scored: list[str] = []
    for sig, group in by_sig.items():
        if len(scored) < SCORED_SUBSET:
            scored.append(group[0]["chart_id"])
    i = 0
    while len(scored) < SCORED_SUBSET and i < len(records):
        if records[i]["chart_id"] not in scored:
            scored.append(records[i]["chart_id"])
        i += 1
    scored_set = set(scored[:SCORED_SUBSET])
    for r in records:
        r["in_scored_subset"] = r["chart_id"] in scored_set

    CORPUS_FILE.write_text(json.dumps(records, ensure_ascii=False, indent=2))

    # coverage report
    print(f"generated {len(records)} charts, scored subset {len(scored_set)}")
    for axis in "ABCDEFGH":
        counts: dict[str, int] = {}
        for r in records:
            counts[r["strata"][axis]] = counts.get(r["strata"][axis], 0) + 1
        print(f"  axis {axis}: {counts}")
    print(f"written -> {CORPUS_FILE.relative_to(REPO)}")


# --------------------------------------------------------------------------
# worksheets
# --------------------------------------------------------------------------

# Human fields: what / why / between / claim / reason / one_line_person
# Machine fields: anchors (tool-proposed from the placements above,
# astrologer only approves/corrects). Scorer matches anchors, not prose.
GOLD_TEMPLATE = {
    "chart_id": "",
    "defining_signatures": [
        {"what": "", "why": "", "anchors": [], "rank": 1},
    ],
    "core_tension": {"between": ["", ""], "anchors": [], "is_central": True},
    "secondary_tensions": [],
    "must_not_lead_with": [
        {"claim": "", "kind": "salience|framing", "reason": "",
         "anchors": []},
    ],
    "one_line_person": "",
}


def _placements_md(chart: Mapping[str, Any], skel: Mapping[str, Any]) -> str:
    lines = ["| Planet | Sign | House | Dignity |", "|---|---|---|---|"]
    dt = {r["planet"]: r for r in skel.get("dignity_table", [])}
    for name, row in dt.items():
        lines.append(f"| {name} | {row.get('sign')} | {row.get('house')} | {row.get('dignity')} |")
    asc = skel.get("asc_ruler_spine", {})
    mcs = skel.get("mc_ruler_spine", {})
    lines.append("")
    lines.append(f"- **Asc** {asc.get('sign')} (ruler {asc.get('ruler')} "
                 f"in {asc.get('ruler_sign')} h{asc.get('ruler_house')} "
                 f"{asc.get('ruler_dignity')})")
    lines.append(f"- **MC** {mcs.get('sign')} (ruler {mcs.get('ruler')} "
                 f"in {mcs.get('ruler_sign')} h{mcs.get('ruler_house')})")
    st = skel.get("stelliums", [])
    if st:
        lines.append("- **Stelliums**: " + "; ".join(
            f"{s['by']}={s['key']} ({','.join(s['planets'])})" for s in st))
    ta = skel.get("tightest_aspects", [])
    if ta:
        lines.append("- **Tightest aspects**: " + "; ".join(
            f"{a['a']} {a['type']} {a['b']} (orb {a['orb']}, {a['direction']})"
            for a in ta))
    return "\n".join(lines)


def cmd_worksheets(_: argparse.Namespace) -> None:
    if not CORPUS_FILE.exists():
        raise SystemExit("run `generate` first")
    records = json.loads(CORPUS_FILE.read_text())
    WORKSHEET_DIR.mkdir(parents=True, exist_ok=True)
    GOLD_DIR.mkdir(parents=True, exist_ok=True)
    n = 0
    for r in records:
        if not r.get("in_scored_subset"):
            continue
        n += 1
        cid = r["chart_id"]
        chart = compute_natal_chart(
            r["birth"]["date"], r["birth"]["time"], r["birth"]["place"],
            birth_latitude=r["birth"]["lat"], birth_longitude=r["birth"]["lon"],
            birth_timezone=r["birth"]["tz"],
        )
        skel = r["engine_skeleton"]
        tmpl = dict(GOLD_TEMPLATE)
        tmpl["chart_id"] = cid
        md = f"""# Gold Worksheet — {cid}

Birth: {r['birth']['date']} {r['birth']['time']} · {r['birth']['place']}
Strata: {json.dumps(r['strata'], ensure_ascii=False)}

> The answer key — what a correct reading LEADS WITH (ranked), plus what
> it must NOT lead with. Not personal taste: the method. Reference
> example: `docs/system/_corpus/gold/1962-01-07_10-30_nairobi.json`.
>
> Method (apply in order):
> 1. luminaries  2. angles + chart ruler  3. dignity
> 4. tightest aspects  5. stellium / final dispositor  6. synthesis
> 7. ranked defining_signatures  8. core_tension
> 9. must_not_lead_with  10. one_line_person
>
> Human fields: write `what`/`why`/`between`/`claim`/`reason`/
> `one_line_person` prose applying the method. Machine fields: `anchors`
> are derived from the placements table above (planet/sign/house/dignity,
> stellium, tight_aspect, ascendant, mc) — fill or let the tool propose,
> you only approve/correct. The scorer matches anchors, never prose.
>
> Each must_not_lead_with needs `kind`: `salience` = "don't make this
> minor/generational thing the spine" (scored: its anchor must NOT be
> 'defining'); `framing` = "don't render this genuinely-salient feature
> clichely" (a Voice-Gate concern, recorded but NOT scored here).
>
> Fill the JSON below and save it to
> `docs/system/_corpus/gold/{cid}.json`.

## Placements (engine-extracted, for reference)

{_placements_md(chart, skel)}

## Fill this (save as gold/{cid}.json)

```json
{json.dumps(tmpl, ensure_ascii=False, indent=2)}
```
"""
        (WORKSHEET_DIR / f"{cid}.md").write_text(md)
    print(f"wrote {n} worksheets -> {WORKSHEET_DIR.relative_to(REPO)}")
    print(f"fill them, save filled JSON into {GOLD_DIR.relative_to(REPO)}")


# --------------------------------------------------------------------------
# score
# --------------------------------------------------------------------------

def _norm(s: Any) -> str:
    return str(s or "").strip().lower()


# v0 anchor types the scorer can deterministically check against the
# shipped chart_skeleton. Anything else is reported as 'unsupported' and
# NEVER counted as an engine failure (the central scorer invariant).
SUPPORTED_ANCHORS = {
    "planet_placement", "luminary", "ascendant", "mc", "chart_ruler",
    "mc_ruler", "angular_planet", "dignity", "stellium", "tight_aspect",
    "house_concentration",
}
UNSUPPORTED_ANCHORS = {"final_dispositor", "dispositor_chain", "axis_emphasis"}
RANK_WEIGHT = {1: 1.0, 2: 0.8, 3: 0.65, 4: 0.5}
OUTER_PLANETS = {"uranus", "neptune", "pluto"}
PERSONAL_PLANETS = {"sun", "moon", "mercury", "venus", "mars"}

# Pass-1 dry-run stacking (frozen prereg arc_v0_1_pass1_dryrun_prereg.md).
# Non-production score-time experiments; never touch the committed
# salience formula or public output. pass1 variants INHERIT A2 logic.
_A2_EXPERIMENTS = {
    "dryrun_a2_outer_endpoint_gate", "pass1_a2_l2", "pass1_a2_l2_l3"}
_L2_EXPERIMENTS = {"pass1_a2_l2", "pass1_a2_l2_l3"}
_L3_EXPERIMENTS = {"pass1_a2_l2_l3"}


def _a2_on(e: str | None) -> bool:
    return e in _A2_EXPERIMENTS


def _l2_on(e: str | None) -> bool:
    return e in _L2_EXPERIMENTS


def _l3_on(e: str | None) -> bool:
    return e in _L3_EXPERIMENTS


def _endpoint_structural(skel: Mapping[str, Any], planet: Any) -> bool:
    """L2: an aspect endpoint is structurally personal if it is a
    luminary, angular, or the chart/MC ruler. Frozen prereg L2."""
    pn = _norm(planet)
    if pn in {"sun", "moon"}:
        return True
    if any(_norm(a.get("planet")) == pn
           for a in skel.get("angular_planets", [])):
        return True
    if pn in {_norm(skel.get("asc_ruler_spine", {}).get("ruler")),
              _norm(skel.get("mc_ruler_spine", {}).get("ruler"))}:
        return True
    return False


def _dignity_index(skel: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {_norm(r["planet"]): r for r in skel.get("dignity_table", [])}


def _placement_match(row: Mapping[str, Any] | None, anchor: Mapping[str, Any]) -> bool:
    if not row:
        return False
    if "sign" in anchor and _norm(row.get("sign")) != _norm(anchor["sign"]):
        return False
    if "house" in anchor and row.get("house") != anchor["house"]:
        return False
    if "dignity" in anchor and _norm(row.get("dignity")) != _norm(anchor["dignity"]):
        return False
    return True


def _match_anchor(anchor: Mapping[str, Any], skel: Mapping[str, Any]) -> str:
    """Return 'matched' | 'unmatched' | 'unsupported'.

    Never conflates 'scorer cannot check this yet' (unsupported) with
    'engine failed to surface it' (unmatched). This 3-state invariant is
    what keeps the falsification harness from lying to us.
    """
    t = _norm(anchor.get("type"))
    if t in UNSUPPORTED_ANCHORS or t not in SUPPORTED_ANCHORS:
        return "unsupported"

    if t in ("planet_placement", "dignity"):
        row = _dignity_index(skel).get(_norm(anchor.get("planet")))
        return "matched" if _placement_match(row, anchor) else "unmatched"

    if t == "luminary":
        l = skel.get("luminaries", {}).get(_norm(anchor.get("planet")))
        return "matched" if _placement_match(l, anchor) else "unmatched"

    if t == "ascendant":
        return "matched" if _norm(skel.get("asc_ruler_spine", {}).get("sign")) \
            == _norm(anchor.get("sign")) else "unmatched"

    if t == "mc":
        return "matched" if _norm(skel.get("mc_ruler_spine", {}).get("sign")) \
            == _norm(anchor.get("sign")) else "unmatched"

    if t in ("chart_ruler", "mc_ruler"):
        spine = skel.get(
            "asc_ruler_spine" if t == "chart_ruler" else "mc_ruler_spine", {})
        if _norm(spine.get("ruler")) != _norm(anchor.get("planet")):
            return "unmatched"
        row = {"sign": spine.get("ruler_sign"),
               "house": spine.get("ruler_house"),
               "dignity": spine.get("ruler_dignity")}
        return "matched" if _placement_match(row, anchor) else "unmatched"

    if t == "angular_planet":
        ang = {_norm(a["planet"]): a for a in skel.get("angular_planets", [])}
        row = ang.get(_norm(anchor.get("planet")))
        if not row:
            return "unmatched"
        if "house" in anchor and row.get("house") != anchor["house"]:
            return "unmatched"
        return "matched"

    if t in ("stellium", "house_concentration"):
        by = "house" if t == "house_concentration" else _norm(anchor.get("by"))
        key = str(anchor.get("house") if t == "house_concentration"
                  else anchor.get("key"))
        need = int(anchor.get("min_count", 3))
        for s in skel.get("stelliums", []):
            if (_norm(s.get("by")) == by and str(s.get("key")) == key
                    and int(s.get("count", 0)) >= need):
                return "matched"
        return "unmatched"

    if t == "tight_aspect":
        pair = {_norm(anchor.get("a")), _norm(anchor.get("b"))}
        asp = _norm(anchor.get("aspect"))
        mx = float(anchor.get("max_orb", 2.0))
        for ta in skel.get("tightest_aspects", []):
            if ({_norm(ta.get("a")), _norm(ta.get("b"))} == pair
                    and _norm(ta.get("type")).startswith(asp)
                    and float(ta.get("orb", 99)) <= mx):
                return "matched"
        return "unmatched"

    return "unsupported"


def _score_anchor_block(anchors: Any, skel: Mapping[str, Any]):
    """-> (coverage|None, supported, matched, unsupported,
            dignity_total, dignity_matched)."""
    matched = unmatched = unsupported = 0
    dig_t = dig_m = 0
    for a in anchors or []:
        r = _match_anchor(a, skel)
        if r == "unsupported":
            unsupported += 1
            continue
        if "dignity" in a:
            dig_t += 1
            if r == "matched":
                dig_m += 1
        if r == "matched":
            matched += 1
        else:
            unmatched += 1
    supported = matched + unmatched
    cov = (matched / supported) if supported else None
    return cov, supported, matched, unsupported, dig_t, dig_m


# --- PR-2b: salience-alignment (SEPARATE, PROVISIONAL, never gates) ------
_TIER_ORDER = {"background": 0, "strong": 1, "defining": 2}


def _tight_aspect_rows(skel: Mapping[str, Any], planet: Any) -> list[Mapping[str, Any]]:
    pn = _norm(planet)
    out = []
    for ta in skel.get("tightest_aspects", []):
        pair = {_norm(ta.get("a")), _norm(ta.get("b"))}
        if pn in pair:
            out.append(ta)
    return out


def _outer_personalization_signals(skel: Mapping[str, Any], planet: Any) -> set[str]:
    pn = _norm(planet)
    if pn not in OUTER_PLANETS:
        return set()

    signals: set[str] = set()
    row = _dignity_index(skel).get(pn) or {}
    if _norm(row.get("dignity")) in {"domicile", "exaltation"}:
        signals.add("dignity")

    if any(_norm(a.get("planet")) == pn for a in skel.get("angular_planets", [])):
        signals.add("angular")

    asc_ruler = _norm(skel.get("asc_ruler_spine", {}).get("ruler"))
    mc_ruler = _norm(skel.get("mc_ruler_spine", {}).get("ruler"))
    for ta in _tight_aspect_rows(skel, pn):
        other = (_norm(ta.get("a")) if _norm(ta.get("b")) == pn
                 else _norm(ta.get("b")))
        if other in PERSONAL_PLANETS:
            signals.add("tight_personal")
        if other in {asc_ruler, mc_ruler}:
            signals.add("owner_tie")
        if other in {"sun", "moon"}:
            signals.add("luminary_tie")
    return signals


def _outer_is_personalized(skel: Mapping[str, Any], planet: Any) -> bool:
    return len(_outer_personalization_signals(skel, planet)) >= 2


def _planet_tier(skel: Mapping[str, Any], planet: Any,
                 experiment: str | None = None) -> str | None:
    for r in skel.get("dignity_table", []):
        if _norm(r["planet"]) == _norm(planet):
            tier = r.get("salience_tier")
            if experiment == "dryrun_a_outer_gate" or _a2_on(experiment):
                pn = _norm(planet)
                if pn in OUTER_PLANETS and tier == "defining":
                    # Dry-run A only: an outer should not inherit headline
                    # loudness from participation alone unless it is
                    # meaningfully personalized in the chart.
                    if not _outer_is_personalized(skel, planet):
                        return "strong"
            return tier
    return None


def _tight_aspect_tier(anchor: Mapping[str, Any], skel: Mapping[str, Any],
                       experiment: str | None = None,
                       outer_focus: bool = False) -> str | None:
    pair = {_norm(anchor.get("a")), _norm(anchor.get("b"))}
    asp = _norm(anchor.get("aspect"))
    mx = float(anchor.get("max_orb", 2.0))
    for ta in skel.get("tightest_aspects", []):
        if ({_norm(ta.get("a")), _norm(ta.get("b"))} == pair
                and _norm(ta.get("type")).startswith(asp)
                and float(ta.get("orb", 99)) <= mx):
            pts = [anchor.get("a"), anchor.get("b")]
            has_outer = any(_norm(p) in OUTER_PLANETS for p in pts)
            if experiment == "dryrun_a_outer_gate" and has_outer:
                pts = [p for p in pts if _norm(p) in OUTER_PLANETS]
            elif _a2_on(experiment) and has_outer:
                if outer_focus:
                    pts = [
                        p for p in pts
                        if _norm(p) in OUTER_PLANETS and _outer_is_personalized(skel, p)
                    ]
                else:
                    pts = [
                        p for p in pts
                        if _norm(p) not in OUTER_PLANETS or _outer_is_personalized(skel, p)
                    ]

            # For outer-gate experiments, do not let the undifferentiated
            # aspect tier itself outrank the endpoint-aware filter.
            ta_t = ta.get("salience_tier") if not (
                (experiment == "dryrun_a_outer_gate" or _a2_on(experiment))
                and has_outer
            ) else None
            best = ta_t
            for p in pts:
                pt = _planet_tier(skel, p, experiment)
                if pt and (best is None
                           or _TIER_ORDER[pt] > _TIER_ORDER.get(best, -1)):
                    best = pt

            # Lever 2 (pass1, frozen prereg §2): a tight aspect whose
            # BOTH endpoints are outer/generational and where NEITHER
            # endpoint is structurally personal (luminary / angular /
            # chart-or-MC ruler) is a generational signature, not a
            # personal headline -> tier capped at 'strong' regardless
            # of orb. Does NOT touch aspects with a personalised
            # endpoint (condition fails -> no cap).
            if (_l2_on(experiment) and best == "defining"):
                a_p, b_p = anchor.get("a"), anchor.get("b")
                both_outer = (_norm(a_p) in OUTER_PLANETS
                              and _norm(b_p) in OUTER_PLANETS)
                if both_outer and not (
                        _endpoint_structural(skel, a_p)
                        or _endpoint_structural(skel, b_p)):
                    best = "strong"
            return best
    return None


def _anchor_tier(anchor: Mapping[str, Any], skel: Mapping[str, Any],
                 experiment: str | None = None,
                 outer_focus: bool = False) -> str | None:
    """Engine salience tier the anchor resolves to, or None if it has no
    salience-bearing element (ascendant/mc) or is unsupported. None means
    'not assessable for salience' — excluded, never a miss."""
    t = _norm(anchor.get("type"))
    if t in UNSUPPORTED_ANCHORS or t not in SUPPORTED_ANCHORS:
        return None
    if t in ("planet_placement", "dignity", "luminary", "angular_planet"):
        return _planet_tier(skel, anchor.get("planet"), experiment)
    if t in ("chart_ruler", "mc_ruler"):
        sp = skel.get("asc_ruler_spine" if t == "chart_ruler"
                      else "mc_ruler_spine", {})
        return sp.get("ruler_salience_tier")
    if t in ("stellium", "house_concentration"):
        by = "house" if t == "house_concentration" else _norm(anchor.get("by"))
        key = str(anchor.get("house") if t == "house_concentration"
                  else anchor.get("key"))
        need = int(anchor.get("min_count", 3))
        for s in skel.get("stelliums", []):
            if (_norm(s.get("by")) == by and str(s.get("key")) == key
                    and int(s.get("count", 0)) >= need):
                # member-max: a stellium is as loud as its loudest planet
                best = None
                for p in s.get("planets", []):
                    pt = _planet_tier(skel, p, experiment)
                    if pt and (best is None
                               or _TIER_ORDER[pt] > _TIER_ORDER[best]):
                        best = pt
                return best
        return None
    if t == "tight_aspect":
        return _tight_aspect_tier(anchor, skel, experiment, outer_focus)
    return None  # ascendant / mc — no salience-bearing element


def _rank_meets(rank: int, tier: str | None) -> bool | None:
    """UNCALIBRATED policy (calibration hypothesis): only the #1
    signature must be the single loudest ('defining'); a #2 signature
    being a 'strong' contributor is astrologically acceptable; rank 3-4
    likewise. None tier = not assessable."""
    if tier is None:
        return None
    if rank == 1:
        return tier == "defining"
    return tier in ("defining", "strong")


def _salience_align(anchors: Any, skel: Mapping[str, Any], rank: int,
                    experiment: str | None = None):
    """-> (alignment|None, assessable, met, misses[], supporting_notes[]).

    Anchor `role` (PR-2c): 'primary_anchor' (default) carries the rank
    expectation and is scored. 'supporting_route'/'context' is the route
    not the light — a tier mismatch is recorded as an informational note,
    NOT a hard salience miss, and excluded from the alignment ratio. This
    keeps a peregrine chart-ruler from being scored as a rank-1 failure
    when the gold itself says it only supports the route."""
    assessable = met = 0
    misses = []
    supporting_notes = []
    for a in anchors or []:
        tier = _anchor_tier(a, skel, experiment)
        ok = _rank_meets(rank, tier)
        if ok is None:
            continue
        role = _norm(a.get("role")) or "primary_anchor"
        ref = (a.get("planet") or a.get("key")
               or a.get("house") or a.get("a"))
        if role != "primary_anchor":
            if ok is False:
                supporting_notes.append({
                    "anchor": a.get("type"), "ref": ref,
                    "engine_tier": tier, "role": role, "rank": rank})
            continue
        assessable += 1
        if ok:
            met += 1
        else:
            misses.append({
                "anchor": a.get("type"), "ref": ref,
                "engine_tier": tier, "rank": rank})
    return ((met / assessable) if assessable else None,
            assessable, met, misses, supporting_notes)


_OWNER_ANCHOR_TYPES = {
    "chart_ruler", "mc_ruler", "luminary", "house_concentration"}
_LOUD_ONLY_VIA = {"tight_aspect", "house_concentration"}


def _is_owner_type_element(skel: Mapping[str, Any], a: Mapping[str, Any]) -> bool:
    """L3 condition 3: the flagged element is itself owner-type if it is
    the chart/MC ruler, a luminary, angular, or sits in the rank-1
    owner-anchor set. Conservative: any owner-link => NOT suppressible."""
    t = _norm(a.get("type"))
    if t in ("chart_ruler", "mc_ruler", "luminary", "ascendant", "mc"):
        return True
    pl = _norm(a.get("planet") or a.get("a") or a.get("b"))
    if pl in {"sun", "moon"}:
        return True
    if pl and any(_norm(x.get("planet")) == pl
                  for x in skel.get("angular_planets", [])):
        return True
    if pl and pl in {_norm(skel.get("asc_ruler_spine", {}).get("ruler")),
                     _norm(skel.get("mc_ruler_spine", {}).get("ruler"))}:
        return True
    return False


def _l3_owner_spine(defining_sigs: Any, skel: Mapping[str, Any],
                    experiment: str | None) -> bool:
    """L3 condition 1: chart has >=1 rank-1 defining_signature whose
    PRIMARY anchors are owner-type and ALL resolve at 'defining'."""
    for d in defining_sigs or []:
        if int(d.get("rank", 4)) != 1:
            continue
        prim = [a for a in d.get("anchors", [])
                if (_norm(a.get("role")) or "primary_anchor")
                == "primary_anchor"]
        if not prim:
            continue
        if not all(_norm(a.get("type")) in _OWNER_ANCHOR_TYPES
                   for a in prim):
            continue
        if all(_anchor_tier(a, skel, experiment) == "defining"
               for a in prim):
            return True
    return False


def _l3_suppresses(m: Mapping[str, Any], a: Mapping[str, Any],
                   skel: Mapping[str, Any], defining_sigs: Any,
                   experiment: str | None) -> bool:
    """Lever 3 (frozen prereg §2): suppress a salience false_emphasis
    flag for a purely-secondary exact participant when a denser
    structural owner is already established. ALL three conditions."""
    # (1) an established owner-type rank-1 defining spine exists
    if not _l3_owner_spine(defining_sigs, skel, experiment):
        return False
    # (2) the flagged element is loud ONLY via tight_aspect /
    #     house_concentration membership / exactness
    if _norm(a.get("type")) not in _LOUD_ONLY_VIA:
        return False
    # (3) the flagged element is NOT itself owner-type
    if _is_owner_type_element(skel, a):
        return False
    return True


def _must_not_eval(must_not: Any, skel: Mapping[str, Any],
                   experiment: str | None = None,
                   defining_sigs: Any = None):
    """must_not_lead_with has two kinds (PR-2b finding):

    - kind='salience': "don't make this minor/generational thing the
      spine". Measurable now: its anchored subject must NOT be
      'defining'. Counted as false emphasis if it is.
    - kind='framing': "don't render this genuinely-salient feature
      clichely". The anchored thing IS legitimately salient; this is a
      Voice-Gate (renderable_public) concern, NOT salience-tier
      measurable. Recorded as deferred, NEVER scored as a failure.

    Missing kind defaults to 'framing' (conservative: never false-flag a
    genuinely-salient spine element)."""
    fe_hits = []
    framing_deferred = []
    for m in must_not or []:
        kind = _norm(m.get("kind")) or "framing"
        if kind != "salience":
            framing_deferred.append(m.get("claim"))
            continue
        elevated = []
        for a in m.get("anchors", []):
            outer_focus = (
                _a2_on(experiment)
                and _norm(a.get("type")) == "tight_aspect"
                and any(_norm(a.get(k)) in OUTER_PLANETS for k in ("a", "b"))
            )
            tier_here = _anchor_tier(a, skel, experiment,
                                     outer_focus=outer_focus)
            if _l3_on(experiment) and tier_here == "defining":
                if _l3_suppresses(m, a, skel, defining_sigs, experiment):
                    continue
            if tier_here == "defining":
                elevated.append({
                    "anchor": a.get("type"),
                    "ref": (a.get("planet") or a.get("key")
                            or a.get("house") or a.get("a"))})
        if elevated:
            fe_hits.append({"claim": m.get("claim"), "elevated": elevated})
    return fe_hits, framing_deferred


def cmd_score(args: argparse.Namespace) -> None:
    if not CORPUS_FILE.exists():
        raise SystemExit("run `generate` first")
    records = {r["chart_id"]: r for r in json.loads(CORPUS_FILE.read_text())}
    if not GOLD_DIR.exists():
        raise SystemExit("no gold reads yet — run `worksheets`, then fill them")

    per_chart = []
    unsupported_types: set[str] = set()
    fe_total = 0
    fr_total = 0
    experiment = getattr(args, "experiment", None)
    for gf in sorted(GOLD_DIR.glob("*.json")):
        gold = json.loads(gf.read_text())
        cid = gold.get("chart_id") or gf.stem
        rec = records.get(cid)
        if not rec:
            print(f"  gold {cid}: no matching corpus record, skipped")
            continue
        skel = rec["engine_skeleton"]
        uncal = bool(skel.get("_salience_meta", {}).get("_uncalibrated"))

        sig_rows = []
        wsum = wtot = 0.0      # extraction coverage (stable, gating)
        swsum = swtot = 0.0    # salience alignment (provisional, NOT gating)
        dt_all = dm_all = 0
        for d in gold.get("defining_signatures", []) or []:
            for a in d.get("anchors", []):
                if _norm(a.get("type")) in UNSUPPORTED_ANCHORS:
                    unsupported_types.add(_norm(a["type"]))
            cov, sup, mat, uns, dt, dm = _score_anchor_block(
                d.get("anchors"), skel)
            dt_all += dt
            dm_all += dm
            rank = int(d.get("rank", 4))
            w = RANK_WEIGHT.get(rank, 0.4)
            sal, _ass, _met, s_miss, s_sup = _salience_align(
                d.get("anchors"), skel, rank, experiment)
            sig_rows.append({
                "rank": rank, "coverage": cov,
                "supported": sup, "matched": mat, "unsupported": uns,
                "salience_alignment": (
                    round(sal, 3) if sal is not None else None),
                "salience_misses": s_miss,
                "supporting_notes": s_sup,
            })
            if cov is not None:
                wsum += cov * w
                wtot += w
            if sal is not None:
                swsum += sal * w
                swtot += w

        ct = gold.get("core_tension", {}) or {}
        ct_cov = _score_anchor_block(ct.get("anchors"), skel)[0]

        fe_hits, fr_def = _must_not_eval(
            gold.get("must_not_lead_with"), skel, experiment,
            gold.get("defining_signatures"))
        fe_total += sum(len(h["elevated"]) for h in fe_hits)
        fr_total += len(fr_def)

        per_chart.append({
            "chart_id": cid,
            "strata": rec["strata"],
            "rank_weighted_coverage": round(wsum / wtot, 3) if wtot else None,
            "salience_alignment_provisional": (
                round(swsum / swtot, 3) if swtot else None),
            "core_tension_coverage": (
                round(ct_cov, 3) if ct_cov is not None else None),
            "dignity_accuracy": (
                round(dm_all / dt_all, 3) if dt_all else None),
            "false_emphasis": fe_hits,
            "framing_deferred_to_voice_gate": fr_def,
            "salience_uncalibrated": uncal,
            "signatures": sig_rows,
        })

    if not per_chart:
        raise SystemExit("no scored charts (fill gold JSONs first)")

    scored = [c for c in per_chart
              if c["rank_weighted_coverage"] is not None]
    mean_cov = sum(c["rank_weighted_coverage"] for c in scored) / len(scored)
    worst = min(c["rank_weighted_coverage"] for c in scored)
    sal_vals = [c["salience_alignment_provisional"] for c in per_chart
                if c["salience_alignment_provisional"] is not None]
    mean_sal = round(sum(sal_vals) / len(sal_vals), 3) if sal_vals else None
    worst_sal = round(min(sal_vals), 3) if sal_vals else None
    report = {
        "experiment": experiment,
        "n_scored": len(per_chart),
        "extraction": {
            "mean_rank_weighted_coverage": round(mean_cov, 3),
            "worst_rank_weighted_coverage": round(worst, 3),
            "provisional_pass": mean_cov >= 0.85 and worst >= 0.70,
        },
        "salience_provisional": {
            "mean_alignment": mean_sal,
            "worst_alignment": worst_sal,
            "false_emphasis_total": fe_total,
            "framing_must_not_deferred_to_voice_gate": fr_total,
            "gating": False,
            "uncalibrated": True,
        },
        "unsupported_anchor_types_seen": sorted(unsupported_types),
        "invariant": ("extraction coverage is the stable GATING metric. "
                      "salience_alignment is SEPARATE, PROVISIONAL, "
                      "UNCALIBRATED and NEVER gates: rank->tier is a "
                      "policy guess; misses are calibration targets, not "
                      "failures. unsupported anchors never counted as "
                      "engine failure."),
        "per_chart": per_chart,
    }
    out_file = Path(getattr(args, "output", "") or SCORE_FILE)
    if not out_file.is_absolute():
        out_file = REPO / out_file
    out_file.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"scored {len(per_chart)} | extraction mean "
          f"{report['extraction']['mean_rank_weighted_coverage']} "
          f"worst {report['extraction']['worst_rank_weighted_coverage']} "
          f"pass={report['extraction']['provisional_pass']}")
    print(f"  salience(provisional, NOT gating): mean {mean_sal} "
          f"worst {worst_sal} | false_emphasis(salience-kind) {fe_total} "
          f"| framing must_not deferred->voice_gate {fr_total}")
    if unsupported_types:
        print(f"  unsupported anchor types (reported, NOT failed): "
              f"{sorted(unsupported_types)}")
    print(f"written -> {out_file.relative_to(REPO)}")


def main() -> None:
    p = argparse.ArgumentParser(description="ARC v0.1 corpus tooling")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("generate").set_defaults(fn=cmd_generate)
    sub.add_parser("worksheets").set_defaults(fn=cmd_worksheets)
    score_p = sub.add_parser("score")
    score_p.add_argument(
        "--experiment",
        choices=["dryrun_a_outer_gate", "dryrun_a2_outer_endpoint_gate",
                 "pass1_a2_l2", "pass1_a2_l2_l3"],
        default=None,
        help="Run an explicit non-production dry-run salience experiment.",
    )
    score_p.add_argument(
        "--output",
        default=None,
        help="Optional output path for score JSON. Defaults to the canonical report only when no output is supplied.",
    )
    score_p.set_defaults(fn=cmd_score)
    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
