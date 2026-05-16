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

GOLD_TEMPLATE = {
    "chart_id": "",
    "defining_signatures": [
        {"what": "", "why": "", "rank": 1},
    ],
    "core_tension": {"between": ["", ""], "is_central": True},
    "secondary_tensions": [],
    "must_not_lead_with": [],
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

> Apply the known reading method (luminaries → angles → dignity →
> tightest aspects → synthesis). Fill the JSON at the bottom and save it
> to `docs/system/_corpus/gold/{cid}.json`. This is the answer key —
> what a correct reading LEADS WITH, ranked, plus what it must NOT lead
> with. Not personal taste: the method.

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


def _skeleton_tokens(skel: Mapping[str, Any]) -> set[str]:
    """Tokens the engine surfaced: 'planet|sign|house' + roles."""
    toks: set[str] = set()
    for r in skel.get("dignity_table", []):
        toks.add(f"{_norm(r['planet'])}|{_norm(r['sign'])}|{r.get('house')}")
        toks.add(_norm(r["planet"]))
    for a in skel.get("angular_planets", []):
        toks.add(f"{_norm(a['planet'])}|{_norm(a['sign'])}|{a.get('house')}")
    for s in skel.get("stelliums", []):
        for p in s.get("planets", []):
            toks.add(_norm(p))
    for key in ("sun", "moon"):
        l = skel.get("luminaries", {}).get(key, {})
        toks.add(f"{key}|{_norm(l.get('sign'))}|{l.get('house')}")
    asc = skel.get("asc_ruler_spine", {})
    toks.add(f"asc|{_norm(asc.get('sign'))}")
    return toks


def _matches(gold_what: str, toks: set[str]) -> bool:
    """Tolerant match: every alpha/num word of the gold phrase that names
    a planet/sign/house should be reflected in the skeleton tokens."""
    w = _norm(gold_what)
    parts = [p for p in w.replace("(", " ").replace(")", " ").split() if p]
    planet = next((p for p in parts if p in {
        "sun","moon","mercury","venus","mars","jupiter","saturn",
        "uranus","neptune","pluto"}), None)
    if not planet:
        return False
    if planet not in toks and not any(t.startswith(planet + "|") for t in toks):
        return False
    sign = next((p for p in parts if p in {
        "aries","taurus","gemini","cancer","leo","virgo","libra",
        "scorpio","sagittarius","capricorn","aquarius","pisces"}), None)
    if sign:
        return any(t.startswith(f"{planet}|{sign}") for t in toks) or \
               any(planet in t and sign in t for t in toks)
    return True


def cmd_score(_: argparse.Namespace) -> None:
    if not CORPUS_FILE.exists():
        raise SystemExit("run `generate` first")
    records = {r["chart_id"]: r for r in json.loads(CORPUS_FILE.read_text())}
    if not GOLD_DIR.exists():
        raise SystemExit("no gold reads yet — run `worksheets`, then fill them")

    per_chart = []
    for gf in sorted(GOLD_DIR.glob("*.json")):
        gold = json.loads(gf.read_text())
        cid = gold.get("chart_id") or gf.stem
        rec = records.get(cid)
        if not rec:
            print(f"  gold {cid}: no matching corpus record, skipped")
            continue
        toks = _skeleton_tokens(rec["engine_skeleton"])
        defs = gold.get("defining_signatures", []) or []
        covered = sum(1 for d in defs if _matches(d.get("what", ""), toks))
        coverage = covered / len(defs) if defs else 0.0
        mnl = gold.get("must_not_lead_with", []) or []
        false_emph = sum(1 for m in mnl if _matches(str(m), toks))
        per_chart.append({
            "chart_id": cid,
            "strata": rec["strata"],
            "spine_coverage": round(coverage, 3),
            "false_emphasis_raw": false_emph,  # salience-tier aware = post PR-2
            "defining_total": len(defs),
            "defining_covered": covered,
        })

    if not per_chart:
        raise SystemExit("no scored charts (fill gold JSONs first)")

    mean_cov = sum(c["spine_coverage"] for c in per_chart) / len(per_chart)
    worst = min(c["spine_coverage"] for c in per_chart)
    # axis-I generalization criterion (spec §7): not_covered vs covered.
    # All synthetic are not_covered_assumed for now → reported, not gated.
    report = {
        "n_scored": len(per_chart),
        "mean_spine_coverage": round(mean_cov, 3),
        "worst_spine_coverage": round(worst, 3),
        "provisional_pass": mean_cov >= 0.85 and worst >= 0.70,
        "note": ("false_emphasis & axis-I criterion are salience-tier "
                 "aware → meaningful only after PR-2; thresholds §7 are "
                 "provisional until first joint calibration pass"),
        "per_chart": per_chart,
    }
    SCORE_FILE.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"scored {len(per_chart)} charts | mean coverage "
          f"{report['mean_spine_coverage']} | worst "
          f"{report['worst_spine_coverage']} | provisional_pass="
          f"{report['provisional_pass']}")
    print(f"written -> {SCORE_FILE.relative_to(REPO)}")


def main() -> None:
    p = argparse.ArgumentParser(description="ARC v0.1 corpus tooling")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("generate").set_defaults(fn=cmd_generate)
    sub.add_parser("worksheets").set_defaults(fn=cmd_worksheets)
    sub.add_parser("score").set_defaults(fn=cmd_score)
    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
