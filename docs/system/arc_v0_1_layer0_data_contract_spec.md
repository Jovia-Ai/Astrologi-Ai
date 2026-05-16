# ARC v0.1 — Layer 0 + Data Contract Spec

**Skeleton-Guided Meaning Governance — Foundation Layer**

> Planning artifact only. No code, renderer, registry, scoring, or runtime
> changes are made by this document. This spec defines the *data foundation*
> that every later ARC layer (Tension, Spine, Promotion Gate, Surface
> Governance, Synthesis) will consume. Nothing downstream can be specced
> concretely until this contract is fixed.

---

## 0. Scope and Invariants

ARC (Astrologer Reading Core) changes **what surfaces and who owns it**, not
how meaning is generated or voiced. This document specs only:

1. The `chart_skeleton` object — deterministic chart facts **plus** salience
   scoring of those facts.
2. The per-candidate contract fields every meaning candidate must carry so
   later layers can govern it.
3. The redefined role of `chart_exact` / registry.
4. The locked architectural decisions (three independent reviews converged).
5. The open questions that must NOT be closed prematurely.

Hard invariants:

- No implementation in this pass.
- No change to packet generation, cluster plan, projection, or voice.
- ARC governs selection/ownership; it does **not** author meaning and does
  **not** render voice.
- "Skeleton presence" guarantees a signal is **read/considered**, never that
  it becomes a separate public card.
- Public output still requires truth + evidence + voice gates downstream.
- The existing fallback/safety-net path is preserved.

Why Layer 0 first (dependency argument):

```
Layer 0 (chart_skeleton object + salience + data contract)   ← FOUNDATION
   ↓ consumed by
Layer 2 (Core Tension Engine)   — cannot rank tensions without dignity/
                                  angularity/tightest-aspect salience
   ↓ consumed by
Layer 1 / Layer 3 (Spine Forcing / Promotion Gate)
   ↓ consumed by
Layer 5 / Layer 6 (Surface Governance / Synthesis)
```

Layer 2 cannot even be *written* without the exact shape of the object it
reads. The data contract is the true foundation.

---

## 1. Locked Decisions (do not re-litigate)

Three independent reviews (initial ARC design + two feedback rounds + synthesis)
converged on the following. These are settled:

| # | Decision |
|---|---|
| L1 | `mandatory_skeleton_presence = true`, `mandatory_public_card = false`. Spine signals must be read; whether they become a separate card is a later Surface Governance decision. |
| L2 | Spine forcing does **not** auto-bypass debug-only. It elevates a signal to *public consideration*; public output still needs evidence + voice gates. |
| L3 | `semantic_promotable` and `renderable_public` are **two separate scores**. A semantically-correct but voice-weak candidate is kept (renderer backlog), never discarded as if it were semantically weak. |
| L4 | `chart_exact` loses authority over **what** surfaces, but keeps value as **how** it is said. It is high-confidence registry memory / preferred rendering, not mere "polish". Owner-selection authority belongs to ARC skeleton. |
| L5 | One mandatory `core_drama`; `0–2` optional `secondary_tension`. Public surfaces core; debug/detail retains the rest. Selection is deterministic, not "we liked this drama". |
| L6 | Card count is dynamic **per surface tier** (hero/core small, support/compressed flexible, composed-detail evidence-driven, debug unlimited) — not a single global cap. |

The four-role hierarchy that resolves "spine cannot be empty":

```
SELECTION AUTHORITY  →  ARC skeleton      (WHAT surfaces, WHO owns)
RENDER PREFERENCE    →  chart_exact       (if a hand-authored exact match
                                           exists for a skeleton-selected
                                           owner, use it — it is the highest
                                           voice quality / registry memory)
GENERALIZATION       →  composed/discovery (fills the gap when no chart_exact;
                                           voice may not be public-ready)
SAFETY NET           →  generic_fallback  (last resort)
```

This makes `chart_exact` the **voice-ready fallback for spine signals**: when
ARC selects a spine owner and a `chart_exact` exists, it is the preferred
rendering; if none exists, composed (if renderable) → generic fallback. The
spine is therefore never empty even when composed voice is not yet ready.

---

## 2. The `chart_skeleton` Object

Layer 0 produces one object per chart, before any packet/cluster work. It has
**two halves**: (A) deterministic extraction, (B) salience scoring. Half B is
the hard, astrologer-judgment part and must not be skipped — Layers 1/2/3
depend on salience, not raw extraction.

### 2.1 Half A — Deterministic Extraction (ephemeris facts)

```json
{
  "chart_skeleton": {
    "meta": {
      "chart_id": "1996-12-28_07-10_istanbul",
      "sect": "day | night",
      "chart_shape": "bundle | bowl | bucket | locomotive | splash | seesaw | splay",
      "element_distribution": { "fire": 0, "earth": 0, "air": 0, "water": 0 },
      "modality_distribution": { "cardinal": 0, "fixed": 0, "mutable": 0 },
      "dominant_element": "water",
      "lacking_element": "fire",
      "hemisphere_emphasis": { "north": 0, "south": 0, "east": 0, "west": 0 }
    },
    "luminaries": {
      "sun":  { "sign": "", "house": 0, "dignity": "", "tightest_aspect": {} },
      "moon": { "sign": "", "house": 0, "dignity": "", "tightest_aspect": {} }
    },
    "asc_ruler_spine": {
      "ascendant_sign": "",
      "ruler": "",
      "ruler_sign": "",
      "ruler_house": 0,
      "ruler_dignity": ""
    },
    "mc_ruler_spine": {
      "mc_sign": "",
      "ruler": "",
      "ruler_sign": "",
      "ruler_house": 0,
      "ruler_dignity": ""
    },
    "angular_planets": [
      { "planet": "", "house": 0, "sign": "", "dignity": "" }
    ],
    "dignity_table": [
      { "planet": "", "sign": "", "house": 0,
        "dignity": "domicile | exaltation | detriment | fall | peregrine" }
    ],
    "tightest_aspects": [
      { "a": "", "b": "", "type": "", "orb": 0.0, "applying": true }
    ],
    "stelliums": [
      { "by": "sign | house", "key": "", "planets": [], "count": 0 }
    ],
    "dispositor_chains": [
      { "planet": "", "chain": [], "termination": "domicile | loop | final" }
    ]
  }
}
```

Notes:

- `dignity_table` covers all classical planets; outer planets (Uranus,
  Neptune, Pluto) carry no traditional dignity and are scored by angularity
  / aspect only.
- `dispositor_chains` reuses the existing `dispositor_engine.py:282-341`
  (already produces a `domicile` termination reason — it is just not wired
  into selection today; Layer 0 is where it gets wired in conceptually).
- `tightest_aspects` is the global top-N by orb, not per-planet.

### 2.2 Half B — Salience Scoring (the astrologer-judgment half)

Extraction alone does not tell Layer 2/3 which skeleton element is
*chart-defining* vs *background*. Each skeleton element gets a `salience`
score with an explicit, deterministic rule. **These weights are starting
values and an open calibration item (see §5).**

```
salience(element) = base_role_weight
                  + dignity_modifier
                  + angularity_modifier
                  + tightness_modifier
                  + concentration_modifier
                  + ruler_condition_modifier
```

| Factor | Rule (starting values — calibration pending) |
|---|---|
| base_role_weight | luminary `0.30`; asc_ruler `0.24`; mc_ruler `0.18`; angular planet `0.16`; stellium `0.20`; tightest single aspect `0.18` |
| dignity_modifier | domicile `+0.12`; exaltation `+0.10`; detriment `+0.06` (loud but afflicted — surfaces as tension, not gift); fall `+0.06`; peregrine `0.00` |
| angularity_modifier | house 1/4/7/10 `+0.10`; succedent `+0.04`; cadent `0.00` |
| tightness_modifier | orb ≤1° `+0.12`; ≤3° `+0.08`; ≤6° `+0.04`; else `0.00` |
| concentration_modifier | stellium 4+ `+0.12`; 3 `+0.08` |
| ruler_condition_modifier | chart ruler angular & dignified `+0.10`; debilitated `+0.04` (still salient, as struggle) |

Key principle (astrologer logic, not engineering convenience):
**Debilitated/afflicted ≠ low salience.** A planet in detriment/fall or a
tight hard aspect is *loud* — it surfaces as the chart's tension/struggle,
not as a gift, but it must not be filtered out for being "negative". This is
why detriment/fall carry positive modifiers.

Output: every skeleton element carries
`{ value: <raw>, salience: <score>, salience_tier: "defining | strong | background" }`
with tier thresholds (`defining ≥ 0.42`, `strong ≥ 0.30`, else `background`)
— **thresholds are calibration items, see §5**.

---

## 3. Per-Candidate Contract Fields

Every meaning candidate (registry/chart_exact, composed, discovery,
fallback) must carry these fields so later layers can govern it without
re-deriving:

```json
{
  "candidate_id": "",
  "source_type": "chart_exact | composed | discovery | fallback",
  "public_job": "main_owner | support | detail | modifier | debug_only | suppressed",
  "skeleton_role": "luminary | asc_ruler | mc_ruler | angular | core_tension | stellium | dignity | tightest_aspect | none",
  "skeleton_salience_tier": "defining | strong | background | none",
  "semantic_promotable": true,
  "renderable_public": false,
  "current_decision": "debug_only",
  "post_fix_potential": "main_owner | support | composed_detail | none",
  "owner_authority": "arc_skeleton | chart_exact_registry | composed | fallback",
  "evidence_ref": { "node_id": "", "evidence_ids": [] }
}
```

Field semantics:

- `skeleton_role` — corrected enum: `angular` and `tightest_aspect` added
  (initial feedback enum omitted them; a 10th-house angular non-luminary
  like 2019 Uranus had no role otherwise).
- `semantic_promotable` — **ARC decides.** "Is this meaning chart-defining,
  correctly owned, evidence-backed?"
- `renderable_public` — **voice gate decides.** "Can this be written safely
  in SHOU voice today?" *What computes this is an open question — see §5.*
- `owner_authority` — records who won owner selection. ARC skeleton outranks
  chart_exact for *selection*; chart_exact wins *render preference* when it
  exists for an ARC-selected owner.
- `post_fix_potential` — for `semantic_promotable=true,
  renderable_public=false`: where it would go once voiced (this field is the
  prioritized renderer/content backlog).

The two-score split made concrete:

```
semantic_promotable = false   → genuinely weak meaning; stays suppressed
semantic_promotable = true
   renderable_public = true   → eligible for public (subject to Surface
                                Governance + truth/evidence gates)
   renderable_public = false  → keep as composed_detail_candidate;
                                enters renderer backlog; NOT discarded
```

---

## 4. 2019 Test Case — Contract Proof

Chart `2019-11-03_23-40_istanbul` (verified from the live projection
artifact). This is the clean, addendum-free generalization test.

Reconstructed placements: Leo Asc · Sun Scorpio 4th · Mercury 4th (conj
Venus) · Moon Aquarius 6th (sq Uranus, opp Asc, sextile Venus) · **Saturn
Capricorn 6th (domicile)** · **Jupiter Sagittarius 5th (domicile)** + Venus
5th · Mars Libra 3rd (detriment) · Uranus Taurus 10th (sq Asc) · MC Aries ·
DSC/7th Aquarius · Chiron 9th · Juno 3rd.

Expected `chart_skeleton` extraction + salience:

| Element | Extracted | Dignity | Salience tier | Today's engine |
|---|---|---|---|---|
| Sun Scorpio 4th | luminary | peregrine | **defining** (luminary + angular 4th) | buried as `discovery_house_4h` candidate, never visible |
| Moon Aquarius 6th | luminary | peregrine | **defining** | only fragment via `uranus_square_asc` |
| **Saturn Capricorn 6th** | dignity | **domicile** | **defining** (domicile +0.12) | misrouted into relationship card |
| **Jupiter Sagittarius 5th** | dignity + stellium(5th) | **domicile** | **defining** | invisible — `discovery_house_5h` candidate only |
| Uranus Taurus 10th | angular | none | **strong** (angular 10th) | partial in career card |
| Mars Libra 3rd | dignity | **detriment** | strong (loud-afflicted +0.06) | absent |
| Sun↔Asc (Scorpio4th ↔ Leo) | core_tension cand. | — | **defining** | not framed as spine |
| Moon□Uranus (fixed) | core_tension cand. | — | strong | fragment only |

What the contract proves immediately:

- The **dignity table alone** surfaces the two things the current engine
  most badly misses: Jupiter domicile in the 5th (the creative signature
  buried as a discovery candidate) and Saturn domicile in the 6th
  (misrouted to relationship). No new "discovery" needed — these are
  deterministic dignity facts the engine currently never weighs.
- Sun Scorpio 4th becomes `skeleton_role: luminary`, `salience_tier:
  defining` → `semantic_promotable: true`. Whether it is a separate card or
  woven into an identity spine is deferred to Surface Governance (L1).
- Core tension candidate "Sun Scorpio 4th (private depth) ↔ Leo Asc
  (visibility)" is *recorded as a candidate with salience*, not yet
  selected — selection is Layer 2's deterministic job (open: §5).

This is the concrete generalization proof: the contract fixes the 2019
under-read using **deterministic skeleton facts**, before any packet
matching, with zero hand-authored variant for this chart.

---

## 5. Open Questions — DO NOT close prematurely

Two feedback rounds did not resolve these. They are flagged here and must be
answered in their own specs before the dependent layer ships.

1. **Secondary-tension determinism.** `core_drama` has a deterministic rule
   (both sides strong, light/angle/ruler/dignity, orb/evidence sufficient,
   no stronger drama). `secondary_tension` does not. Resolution direction: a
   strength threshold that *produces* the count (1 core + 0–2 secondary)
   rather than a hardcoded cap. Owned by: Layer 2 spec.
2. **What computes `renderable_public`.** Named everywhere, defined nowhere.
   Must bind to concrete QA: automated banned-phrase/chip-format lint vs
   golden-similarity score vs human review — with the
   `[automated]/[human]/[golden]` tagging from the Slides Contract QA.
   Owned by: Voice Gate spec.
3. **`_aux` root cause is orphaned.** Audit §6: anchor-based aux
   multiplication + theme_key dedup-escape
   (`natal_promise_packets.py:4657-4701`). ARC Layer 6 (synthesis/weave)
   *masks* it but does not fix the generator. Needs its own targeted fix;
   must not be lost in architecture work. Owned by: separate `_aux` fix.
4. **Salience weights & tier thresholds (§2.2) are uncalibrated.** Starting
   values only. Calibration requires the stratified corpus (below), not
   anecdotal tuning on 3 charts.

---

## 6. Validation

The contract is validated only against a **stratified corpus**, never the
3 hand-looked charts:

- 30–50 charts, deliberately spanning configurations the hand-authored
  variant library does **not** cover (2019-type cases): each element/modality
  dominance, angular-heavy vs cadent-heavy, stellium vs scattered, each
  planet as chart ruler, dignified vs debilitated luminaries, day vs night.
- 1996/1998 are excluded from the generalization set — they carry the global
  hand-authored registry/variant bias and would mask gaps (audit §8: no
  date-keyed injection, but a global variant library that fits some charts).
- Astrologer rubric (scored, automatable where possible): did the skeleton
  surface luminaries? angular planets? domicile/exaltation planets? the
  tightest aspect? the stellium? Did salience tiers match an
  astrologer-grade manual read?
- Pass = rubric holds across the stratified set, not on the inspected charts.

---

## 7. Non-Goals

- Not deleting the hand-authored library — demoting it from selection
  authority to render preference / registry memory.
- Not making LLM the primary renderer.
- Not forcing equal card count across charts.
- Not auto-fixing `_aux` (separate item).
- Not implementing code, renderer, scoring, or runtime change in this pass.
- Not making every spine signal a separate public card.

---

## 8. Sequencing After Layer 0

```
THIS SPEC: Layer 0 + Data Contract  (extraction + salience + candidate fields)
   ↓
Layer 2 spec: Core Tension Engine    (resolves open Q1; consumes salience)
   ↓
Layer 3 spec: Promotion Gate         (consumes semantic_promotable +
                                      skeleton_role + salience_tier)
   ↓
Voice Gate spec: renderable_public   (resolves open Q2)
   ↓
Layer 5/6 spec: Surface Governance + Synthesis
   ↓
(parallel, independent) `_aux` root-cause fix (open Q3)
```

---

## 9. Final Recommendation

Adopt this as the ARC foundation. It is deliberately the *data contract*,
not the clever part — because every clever layer (tension, gate, synthesis)
is non-speccable without the exact skeleton object shape and salience
scoring it consumes. The 2019 proof shows the contract alone — through the
deterministic dignity table — already surfaces what the current
packet-matching architecture structurally buries, with no chart-specific
hand authoring.

Build order: extraction first (deterministic, low-risk), salience scoring
second (astrologer judgment, the real work), candidate-field plumbing third.
Calibrate salience only on the stratified corpus. Keep the four open
questions visibly open until their owning specs close them.

The single sentence this whole architecture is built to make true:

> ARC computes the chart's spine first; evaluates registry, discovery and
> composed candidates against that spine; and lets only chart-defining,
> evidence-backed, correctly-owned, voice-ready meaning reach the public —
> reading from the skeleton, not from memorized combinations.
