# ARC v0.1 — Stratified Corpus & Astrologer Rubric Spec

> Planning artifact. This is the **falsification harness design**. It is
> the dependency that unblocks PR-2 (salience calibration) and validates
> generalization (Layer 0 spec §6). Corpus *execution* (collecting charts,
> producing astrologer gold reads) is **not** an engineering task — it
> needs an astrologer. This document defines exactly what must be
> collected and how it is scored so that work can start concretely.

---

## 0. Why this exists

Every ARC document says "validate on a stratified corpus." That corpus is
still vapor. Consequences if it stays vapor:

- PR-2 salience weights (Layer 0 spec §2.2) cannot be calibrated — they
  stay `UNCALIBRATED` guesses forever.
- "Does it generalize to a totally different chart?" — the core question of
  this whole effort — stays **unanswerable**.
- The 2019 proof is **one anecdote**. One chart never demonstrates
  generalization (established early in this project).

This spec converts "validate on a corpus" from a promissory note into a
collectible, scoreable artifact.

## 1. Scope and invariants

- No code. This designs *what to collect* and *how to score*, not an
  implementation.
- The corpus is the single source of truth for: salience calibration
  (PR-2), generalization pass/fail (§6), and every future ARC layer's
  acceptance.
- Charts with **any manual addendum / hand-authored bias must be
  excluded** from the generalization set. Specifically 1996/1998 (global
  hand-authored registry/variant bias — Layer 0 spec §6). They may live in
  a separate, clearly labelled "known-overfit" reference set, never in the
  scored generalization corpus.
- Pass is defined **across the stratified corpus**, never per inspected
  chart.

## 2. Corpus size and structure

- **40 charts** total (range 30–50; 40 is the target).
- **Scored subset: 16 charts** get full astrologer gold reads (the
  expensive `[human]` artifact). The other 24 get automated
  skeleton-coverage checks only (`[automated]`).
- Every chart is tagged with its **stratification cell** (below) so corner
  cases are guaranteed, not left to chance.

## 3. Stratification axes (deliberately span the space)

The corpus must cover the *corners*, not cluster in the common center.
Nine axes; each chart records its value on every axis:

| Axis | Values | Why |
|---|---|---|
| A. Dominant element | fire / earth / air / water-led | element bias changes salience reading |
| B. Dominant modality | cardinal / fixed / mutable-led | modality bias |
| C. Angular density | angular-heavy / balanced / cadent-heavy | angularity is a salience driver |
| D. Concentration | stellium present / scattered | stellium is a forced-spine signal |
| E. Chart-ruler condition | dignified / peregrine / debilitated ruler | tests dignity-aware routing |
| F. Luminary dignity | both dignified / mixed / both debilitated | luminaries are top-salience |
| G. Sect | day / night | sect modifies salience |
| H. Aspect-tightness profile | tight-dominant / mixed / loose | tightest-aspect salience |
| **I. Library coverage** | **well-covered / partially / NOT covered** | **the critical generalization axis** |

**Axis I is the most important.** Over-sample the *NOT-covered* end:
≥50% of the corpus must be charts the hand-authored `chart_signature`
variant library does **not** match well (2019 is the archetype of this
cell). Generalization is defined precisely as: ARC reads these correctly
*without* a hand-authored variant existing.

Coverage requirement: every value of axes A–H appears ≥3 times; axis I's
"NOT covered" appears ≥20 times.

## 4. Per-chart record format

```json
{
  "chart_id": "YYYY-MM-DD_HH-MM_place",
  "birth": { "date": "", "time": "", "place": "", "lat": 0, "lon": 0, "tz": "" },
  "strata": { "A":"water","B":"fixed","C":"cadent-heavy","D":"stellium",
              "E":"dignified","F":"mixed","G":"night","H":"tight-dominant",
              "I":"not-covered" },
  "in_scored_subset": true,
  "engine_skeleton": "<output of build_chart_skeleton(compute_natal_chart(...))>",
  "astrologer_gold": { ... see §5 ... }   // only if in_scored_subset
}
```

The `engine_skeleton` is generated deterministically (already possible
today — PR-1/PR-1b shipped). No engineering blocker on collection.

## 5. The astrologer gold read (the `[human]` artifact)

For each of the 16 scored charts, an astrologer (qualification: §8 open)
produces a **structured** gold — not free prose:

```json
{
  "defining_signatures": [
    { "what": "Sun Scorpio 4th", "why": "core identity, private depth",
      "rank": 1 },
    { "what": "Saturn Capricorn 6th (domicile)", "rank": 2 },
    { "what": "Jupiter Sagittarius 5th (domicile)", "rank": 3 }
  ],
  "core_tension": {
    "between": ["Sun Scorpio 4th (private)", "Leo Asc (visible)"],
    "is_central": true
  },
  "secondary_tensions": [ { "between": [...] } ],
  "must_not_lead_with": [
    "generic relationship card", "minor cadent placements"
  ],
  "one_line_person": "private, disciplined depth behind a warm public mask"
}
```

Rules for the gold:
- `defining_signatures`: the 2–5 things the astrologer would actually lead
  a reading with, ranked. This is the spine truth.
- `must_not_lead_with`: the negative space — what the engine must NOT
  over-surface. Equally important as coverage.
- Structured, ranked, finite — so it is machine-comparable.

## 6. Scoring rubric

Per scored chart, the engine output is scored against the gold:

| Metric | Type | Definition |
|---|---|---|
| Spine coverage | `[automated]` | % of gold `defining_signatures` present in `engine_skeleton` (dignity_table / luminaries / angular / stellium / asc-mc spine). PR-1b makes this computable now. |
| Salience alignment | `[automated]` (post PR-2) | of covered defining signatures, % assigned `defining`/`strong` tier; gold rank-1/2 must not land in `background` |
| False emphasis | `[automated]` (post PR-2) | count of `must_not_lead_with` items the engine elevates to `defining` tier — a **penalty** |
| Tension match | `[human]` (Layer 2) | does engine core_tension == gold `core_tension`? (deferred until Layer 2 exists) |
| Voice fidelity | `[golden]/[human]` | only relevant once renderable_public exists — out of scope here |

Per-chart score:

```
chart_score = spine_coverage
            - false_emphasis_penalty
            (salience_alignment folded in once PR-2 lands)
```

## 7. Pass / tolerance definition

Generalization **passes** when, across the scored subset:

- **Spine coverage ≥ 0.85 mean**, AND
- **No scored chart below 0.70 spine coverage**, AND
- **False-emphasis mean ≤ 0.5 items/chart** (post PR-2), AND
- the NOT-covered cell (axis I) performs **within 0.05** of the
  well-covered cell — i.e. ARC reads uncovered charts almost as well as
  covered ones. *This last criterion is the actual definition of "it
  generalizes."*

**Bootstrapping caveat (honest):** these thresholds are themselves a first
guess. The first full corpus pass calibrates BOTH the salience weights
(PR-2) AND these thresholds. Until the first pass, treat them as
provisional, not law.

## 8. What must be delivered (owner: product + astrologer)

To unblock PR-2 and §6:

1. **40 charts' birth data**, each tagged with its §3 strata cell,
   satisfying the §3 coverage requirement (≥50% axis-I "not-covered").
2. **16 astrologer gold reads** in the §5 structured format.
3. Confirmation of the astrologer's qualification + whether ≥2 astrologers
   cross-rate the scored subset (inter-rater reliability — see open items).

Engineering side (already unblocked, no dependency): the automated scoring
harness can be built now since `build_chart_skeleton` ships and the gold
format is fixed.

## 9. Open items (do not close prematurely)

- **Astrologer qualification & inter-rater reliability.** One astrologer's
  gold is a single opinion. ≥2 raters on the scored subset with a
  disagreement-resolution rule is strongly preferred. Unresolved.
- **Threshold bootstrapping.** §7 numbers are provisional until the first
  pass (chicken-and-egg with PR-2 calibration). Plan the first pass as
  *joint* salience+threshold calibration, not sequential.
- **Axis-I labelling.** Deciding whether a chart is "library-covered"
  requires inspecting the hand-authored `chart_signature` variant
  predicates (`natal_promise_packets.py:616-820, 5503-5767`). This
  labelling itself is a small audit task before collection.

## 10. Non-goals

- Not collecting charts here (this is the design; collection is execution).
- Not calibrating salience here (that is PR-2, fed by this corpus).
- Not scoring voice/renderability (out of scope until Voice Gate exists).
- Not including 1996/1998 or any hand-addended chart in the scored set.

## 11. How this plugs into the roadmap

```
NOW: build_chart_skeleton ships (PR-1/PR-1b done)
     → automated scoring harness can be built (engineering, unblocked)
     → corpus collection starts (product+astrologer, this spec)

WHEN corpus + gold ready:
     → first joint pass: calibrate salience (PR-2) + §7 thresholds
     → PR-2 frozen (no longer UNCALIBRATED)
     → §6 generalization verdict produced (pass/fail, axis-I criterion)
     → only then: Layer 2 (Core Tension) spec — its gold is already in
       the corpus (§5 core_tension), so Layer 2 is testable from day one
```

## 12. Final recommendation

Start corpus collection immediately and in parallel with any remaining
engineering — it is the longest-lead, non-engineering, critical-path
dependency, and nothing downstream (PR-2, generalization verdict, Layer 2
acceptance) is real without it. The single most important sampling rule:
**over-sample charts the hand-authored library does NOT cover.** That cell
is where generalization is proven or disproven; everything else is the
comfortable center that already works.
