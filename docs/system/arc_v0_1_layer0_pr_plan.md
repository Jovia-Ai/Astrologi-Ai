# ARC v0.1 — Layer 0 PR Implementation Plan

> Planning artifact. No code in this document. Grounded in
> `arc_v0_1_layer0_implementation_readiness.md` (empirical, `file:line`)
> and `arc_v0_1_layer0_data_contract_spec.md` (the contract).
> This converts the analysis into an actionable build sequence.

## Scope and invariants

- 4 PRs, deliberately small. A single PR is rejected as too risky.
- PRs 1, 3, 4 are corpus-independent and can proceed now.
- **PR-2 (salience) is corpus-blocked** — it must not be frozen/merged with
  calibrated weights until the stratified corpus + astrologer rubric exist.
- No change to `charts.py` (Groq path), packet generation, cluster plan,
  projection, voice, or the existing fallback safety net.
- Insertion point is one seam: `_prepare_payload_from_chart`
  (`natal_interpretation.py:1634`), after `compute_natal_chart`, before
  `build_natal_graph`/packets.
- Locked decisions (Layer 0 spec §1) carry forward unchanged. The four open
  questions (spec §5) stay open; this plan does not close them.

## Dependency graph

```
PR-1 extraction ──┬──> PR-3 contract plumbing ──> PR-4 2019 oracle test
                  └──> PR-2 salience  [BLOCKED on corpus track]
Corpus track (parallel, needs astrologer input) ──> unblocks PR-2
```

---

## PR-1 — chart_skeleton extraction (corpus-independent, low risk)

**Goal:** produce the deterministic half (spec §2.1) of `chart_skeleton`
from existing structured `chart_data`. Pure assembly of existing functions
+ one tiny net-new detector.

Consumes:
- `chart_data` from `compute_natal_chart` (`chart_service.py:9` →
  `builder.py:243`): planets (sign/house/retrograde/degree), houses,
  house_positions, aspects (with orb).

Produces: `chart_skeleton.meta`, `.luminaries`, `.asc_ruler_spine`,
`.mc_ruler_spine`, `.angular_planets`, `.dignity_table`,
`.tightest_aspects`, `.stelliums`, `.dispositor_chains`.

Assembly map (reuse, do not rebuild):
- dignity_table → `astro/dignity.py:essential_dignity(planet, sign)` per planet
- dispositor_chains → `dispositor_engine.py:build_dispositor_chain`
- asc/mc ruler spine → `dispositor_engine.py:ruler_of_sign` +
  `build_house_ruler_map`
- angular_planets → filter planets where `house ∈ {1,4,7,10}` (planets
  already carry assigned house, `positions.py:89-93`)
- tightest_aspects → sort `chart_data["aspects"]` by `orb`; **explicitly
  call** `aspect_direction.py:compute_direction` to add `applying` (not
  auto-attached — analysis caveat)
- element/modality/sect/chart_shape → derive from planet sign/house set

Net-new (small): general **stellium detector** — group planets by sign and
by house, emit groups with count ≥3. Only hand-authored `match_id` strings
exist today (`natal_promise_packets.py:5029`); no reusable detector.

Insertion: compute once inside `_prepare_payload_from_chart`
(`natal_interpretation.py:1634`), attach to the payload/context object that
already flows to `build_natal_graph` (`:1713`) and downstream.

Acceptance: PR-1 emits `chart_skeleton` (Half A only; `salience` fields
absent/empty) for the 2019 chart matching the oracle values (see PR-4).
No public-payload change (skeleton is internal/debug-only at this stage).

Risk: **low.** Mostly wiring existing, tested functions + one tiny detector.

---

## PR-2 — salience scoring (CORPUS-BLOCKED — the real work)

**Goal:** add spec §2.2 — `salience`, `salience_tier` per skeleton element.
This is the only genuinely net-new logic and the astrologer-judgment core.

Consumes: PR-1's Half-A skeleton.

Produces: every skeleton element carries
`{value, salience, salience_tier: "defining|strong|background"}`.

Implements the §2.2 formula:
`base_role_weight + dignity_modifier + angularity_modifier +
tightness_modifier + concentration_modifier + ruler_condition_modifier`,
including the **"debilitated/afflicted ≠ low salience"** rule (detriment/
fall/tight-hard-aspect carry positive modifiers — they surface as the
chart's tension, not as filtered-out negatives).

**Blocking condition (hard):** the §2.2 weights and tier thresholds are
starting values only. They MUST NOT be merged as calibrated truth until the
stratified corpus + astrologer rubric exist and have been used to tune them.
PR-2 may land the *formula scaffold* behind a flag with the starting
weights, explicitly labeled `UNCALIBRATED`, but the calibrated values are a
corpus deliverable, not an engineering guess.

Acceptance (post-corpus): salience tiers for the corpus sample match the
astrologer rubric within tolerance (rubric defines tolerance).

Risk: **medium-high** — semantic correctness depends on calibration, which
depends on the corpus.

---

## PR-3 — candidate contract fields (plumbing, corpus-independent)

**Goal:** add spec §3 fields to every candidate so later layers (2/3/Voice
Gate) can govern without re-derivation.

Adds (declared on all candidates): `public_job`, `skeleton_role`
(enum corrected to include `angular` + `tightest_aspect`),
`skeleton_salience_tier`, `semantic_promotable`, `renderable_public`,
`current_decision`, `post_fix_potential`, `owner_authority`, `evidence_ref`.

**Precision rule (do not violate):** Layer 0 populates ONLY skeleton-derived
fields (`skeleton_role`, `skeleton_salience_tier` — the latter after PR-2).
Gate-decision fields (`semantic_promotable`, `renderable_public`,
`public_job`) are **declared but left null** — they are Layer 2 / Layer 3 /
Voice-Gate outputs. An implementer must NOT compute them in Layer 0.

Acceptance: contract schema present on all candidates; skeleton-derived
fields populated; gate fields null; no public-payload drift.

Risk: **low** (plumbing), but the precision rule is the one place a mistake
breaks the architecture — call it out in PR review explicitly.

---

## PR-4 — 2019 oracle snapshot (validation, corpus-independent)

**Goal:** lock a deterministic regression so PR-1/PR-3 cannot silently drift.

Method: call `compute_natal_chart` for `2019-11-03 23:40 Istanbul` +
`essential_dignity` per planet → authoritative expected skeleton.

Expected skeleton highlights (the proof targets, from spec §4):

| Element | Expected | Currently |
|---|---|---|
| Sun Scorpio 4th | luminary, defining-tier | buried as `discovery_house_4h` candidate |
| Moon Aquarius 6th | luminary, defining | fragment only |
| **Saturn Capricorn 6th** | dignity=**domicile**, defining | misrouted to relationship |
| **Jupiter Sagittarius 5th** | dignity=**domicile** + 5th-stellium | invisible (`discovery_house_5h`) |
| Uranus Taurus 10th | angular, strong | partial in career card |
| Mars Libra 3rd | dignity=**detriment**, strong (loud-afflicted) | absent |
| Sun↔Asc (Scorpio4th↔Leo) | core-tension candidate | not framed as spine |

Acceptance: extracted skeleton == oracle, byte-stable; the dignity table
alone surfaces Jupiter-domicile-5th and Saturn-domicile-6th (the two
biggest current misses) with zero chart-specific hand authoring.

Risk: **low.**

---

## Corpus track (parallel, NOT producible by engineering alone)

This unblocks PR-2 and validates spec §6. It needs astrologer input — it is
**not** a doc the engine team writes alone.

Required deliverables (owner: product + astrologer):
1. **30–50 chart corpus**, stratified deliberately across configurations the
   hand-authored variant library does NOT cover (2019-type cases): each
   element/modality dominance, angular-heavy vs cadent-heavy, stellium vs
   scattered, each planet as chart ruler, dignified vs debilitated
   luminaries, day vs night. Exclude 1996/1998 (carry global hand-authored
   bias — spec §6).
2. **Astrologer rubric:** for a sample, an astrologer-grade manual read of
   "expected core themes / expected skeleton" — the gold the engine is
   scored against (did it surface luminaries? angular? domicile/exaltation?
   tightest aspect? stellium? did salience tiers match?).
3. **Scoring harness:** automated where possible (skeleton-coverage rubric),
   human where not (does the read feel right).

What the team must provide before PR-2 can be calibrated/frozen:
- The 30–50 charts (birth data).
- The astrologer gold reads for the scored sample.
- The rubric pass/tolerance definition.

Until these exist, PR-2 stays `UNCALIBRATED` behind a flag.

---

## Sequencing & open questions

```
NOW (parallel):
  Eng:    PR-1 → PR-3 → PR-4   (corpus-independent, can ship)
  Product+Astrologer: build corpus + rubric (blocks PR-2)

AFTER corpus:
  PR-2 calibrated & frozen
  → Layer 2 (Core Tension) spec — resolves open Q1 (secondary-tension determinism)
  → Voice Gate spec — resolves open Q2 (what computes renderable_public)
  → (parallel, independent) _aux root-cause fix — open Q3
```

Open-question priority (carried from spec §5, prioritized here):
- **Q2 renderable_public — critical path** (keystone of locked decision L3;
  blocks Layer 3 from being operational; resolve before Layer 3 spec).
- Q1 secondary-tension determinism — owned by Layer 2 spec.
- Q4 salience calibration — owned by corpus track (above).
- Q3 `_aux` root cause — independent, parallel, blocks nothing.

## Final recommendation

Start PR-1 now: it is low-risk assembly of existing, tested functions at one
clean seam, with a deterministic 2019 oracle (PR-4) guarding it. In
parallel, start the corpus track immediately — it is the longest-lead,
non-engineering dependency and it gates PR-2 (the real work) plus all
generalization validation. Do not write Layer 2 / Voice Gate specs until
PR-1–PR-4 land and the corpus exists; speccing further without a
falsification harness produces unverifiable theory.
