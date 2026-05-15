# v0.9a.3 Plan — Dedicated Composed Detail Lane

> Planning artifact. **Do not implement yet.** This document defines how
> `composed_detail_cards_v0_9a_2` can graduate from a debug-only
> traceability payload into a controlled, user-facing detail lane —
> without leaking into any of the existing public surfaces.

## Scope Boundaries (non-negotiable)

The lane defined here must **never** route a composed card into:

- `profile_narrative_projection_v1.profile_public.blocks` (public_main)
- `profile_narrative_projection_v1.profile_public.core_blocks`
- `profile_narrative_projection_v1.profile_public.extra_blocks`
- `profile_v8_projection_v1.differentiators`
- `profile_v8_projection_v1.insight_strip`
- `profile_v8_projection_v1.hero`
- `profile_v8_projection_v1.identity_axis`
- `public_support` (any surface that consumes it)

The `traceability.composed_detail_cards_v0_9a_2` debug payload remains
unchanged and continues to exist independently.

## Current State (as of v0.9a.2)

- Renderer: `backend/app/meaning/composed_detail_renderer.py`
  - flag-gated by `ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL`
  - emits only `career_route` / `public_voice` for three allowlisted
    chart signatures
  - public text passes Turkish diacritic / ASCII-residue QA (v0.9a.2
    follow-up)
- Projection injection points:
  - `profile_narrative_projection_v1.traceability.composed_detail_cards_v0_9a_2`
  - `profile_v8_projection_v1.traceability.composed_detail_cards_v0_9a_2`
- Eligibility model on candidates: `debug_eligible`, `detail_eligible`,
  `public_support_eligible`, `public_main_eligible`.
- Renderer requires `detail_eligible=true` AND
  `public_support_eligible=false` AND `public_main_eligible=false`.

---

## 1. Public Payload Field

**Recommendation:** introduce a single, clearly experimental field on the
public projection — separate from `detail_cards`, `blocks`, and
`extra_blocks`.

Proposed field name:

- `profile_public.composed_detail_cards`

Naming rationale:

- Mirrors the existing `traceability.composed_detail_cards_v0_9a_2` key
  so engineers can grep both ends of the pipeline with the same term.
- Drops the `_v0_9a_2` version suffix from the public field — the
  payload contract should stay stable across renderer revisions; version
  info belongs on the card's `origin` field (already
  `composed_detail_renderer_v0_9a_2`).
- Deliberately *not* `experimental_detail_cards`: the public payload
  field is consumed by mobile and should not signal instability in its
  name. Experimental status is conveyed via the flag, allowlist, and
  per-card `origin`.

Field shape:

```jsonc
"profile_public": {
  "blocks": [...],
  "core_blocks": [...],
  "extra_blocks": [...],
  "detail_cards": [...],
  "composed_detail_cards": [
    {
      "id": "composed_detail::composed_career_route_v0_9a::fix04_h10_career_stellium",
      "node_id": "promise::composed_career_route_v0_9a",
      "headline": "...",
      "teaser": "...",
      "body": "...",
      "chips": [...],
      "family": "career_public_voice",
      "emphasis": "detail",
      "origin": "composed_detail_renderer_v0_9a_2",
      "source_type": "composed_semantic",
      "source_candidate_id": "composed_career_route_v0_9a",
      "public_job": "detail_only"
      // source_anchor_trace intentionally omitted from public payload;
      // it remains in the traceability lane only.
    }
  ]
}
```

Notes:

- `source_anchor_trace` (technical anchors, domain reasons) stays in the
  debug traceability lane and is **not** mirrored to the public field.
- Mobile must treat the field as **optional** and tolerate it being
  absent or empty.

---

## 2. New Flag

**Recommendation:** add a new, separate flag dedicated to this lane.

Proposed flag:

- `ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_DETAIL_LANE`
- default: `false`
- semantics: "emit rendered composed detail cards into
  `profile_public.composed_detail_cards`"

Layering with existing flags:

| Flag | v0.9a.2 role | v0.9a.3 role |
|---|---|---|
| `ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9` | enable composed semantics base | unchanged |
| `ENABLE_NATAL_COMPOSED_SEMANTICS_DETAIL_SUPPORT` | flag detail eligibility | unchanged |
| `ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_VOICE_DETAIL_SUPPORT` | scope to public_voice subtype | unchanged |
| `ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL` | render card into debug payload | unchanged (still gates render → trace) |
| `ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_DETAIL_LANE` | **new** — promote rendered card into `profile_public.composed_detail_cards` | new gate |
| `ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_MAIN` | stays `false` | stays `false` |

Activation matrix:

| `RENDER_DETAIL` | `PUBLIC_DETAIL_LANE` | Debug trace card | Public field |
|---|---|---|---|
| off | off | absent | absent |
| on | off | present | absent |
| off | on | absent | absent (lane requires a rendered card) |
| on | on | present | present (target charts only) |

Important: the new flag is a **promotion gate**, not a substitute
renderer. A card must already exist in the traceability lane for it to
be eligible for promotion. This keeps the failure mode safe — the public
lane cannot exist without a successful render.

---

## 3. Candidate Eligibility

A candidate is eligible for the public detail lane only if **all** of:

- `source_type == "composed_semantic"`
- `family == "career_route"` (no other families in this slice)
- `subtype == "public_voice"` (no other subtypes in this slice)
- `chart_facts_match is True`
- `public_eligibility.detail_eligible is True`
- `public_eligibility.public_support_eligible is False`
- `public_eligibility.public_main_eligible is False`
- the renderer returns a non-None card (i.e. variant matched, quality
  pass, no Turkish ASCII residue)
- chart matches the v0.9a.2 allowlist (3 signatures: `fix04`, `tokyo`,
  `toronto`) **for Phase B**; allowlist relaxes in later phases

The eligibility check itself lives in a single new function next to the
renderer, e.g. `is_composed_detail_lane_eligible(candidate, card)`, so
that the criteria are testable in isolation and so the public_main path
cannot accidentally call into it.

---

## 4. UI Surfacing

**Phase B (server only):** mobile does not read the new field. Backend
emits it; mobile ignores it; QA inspects raw payloads.

**Phase C (mobile-gated detail surface):** the field becomes user-visible
in a deliberately narrow context. Options ranked:

1. **Preferred: profile deeper-details drawer / "Neden önemli?" detail
   section.** A clearly secondary surface reached from the profile detail
   flow (`profile_detail_flow_page.dart`), never the hero, never the
   home feed. The card is rendered with its `headline` / `teaser` /
   `body` / `chips`, no technical anchors.
2. Acceptable: a separate "Daha derin okuma" tab inside the existing
   detail flow.
3. **Not acceptable:** `home_page.dart`, hero, identity axis, calendar
   hub, sky event feed, any feed-like surface, any onboarding step.

Explicitly excluded UI placements:

- not in hero
- not in `home` `transit/event summary` panel
- not in `identity_axis`
- not in `differentiators`
- not in `insight_strip`
- not in `sky_event_feed`
- not in story/forum/AI tabs

Mobile-side feature gating (Phase C) should be guarded by a mobile build
flag or remote-config switch so we can disable rendering without
re-deploying the backend.

---

## 5. Rollout Path

| Phase | Backend | Mobile | Audience |
|---|---|---|---|
| **A** (= v0.9a.2 today) | rendered → traceability only | n/a | internal debug |
| **B** | + `PUBLIC_DETAIL_LANE` flag → `profile_public.composed_detail_cards`; allowlist = 3 charts | does not read field | internal + payload QA |
| **C** | unchanged from B, allowlist still 3 charts | mobile reads field behind a mobile gate; renders in deeper-detail surface only | internal QA + dogfood |
| **D** | allowlist widens (relaxed chart constraint, more subtypes if/when added) | mobile gate stays, possibly graduates to default-on | broader rollout |

Phase exit criteria:

- A → B: payload contract review, copy QA on the three target charts
  passes, no spillover into existing public fields under any flag combo.
- B → C: at least one round of QA on staging payloads; mobile shell
  built and reviewed with the new surface stub.
- C → D: SHOU copy QA on widened chart pool; regression coverage for
  every new chart class added to the allowlist; explicit product
  approval before relaxing the allowlist.

Each phase is **strictly additive**. No phase removes the traceability
trace card. No phase changes registry or selection.

---

## 6. Tests

Required test coverage before Phase B ships:

### Renderer / eligibility (extends `test_composed_detail_renderer.py`)

- `flag off (lane) → field absent` — `PUBLIC_DETAIL_LANE=false` and
  `RENDER_DETAIL=true`: `profile_public.composed_detail_cards` is
  absent (or empty list) on every target chart.
- `flag on → field present for target charts only` — for each of the
  three allowlist charts, the field contains exactly one card; for any
  non-target chart (including charts that triggered other promise
  packets), the field is absent or empty.
- `eligibility gating` — a candidate with
  `public_support_eligible=true` or `public_main_eligible=true` is
  **not** promoted to the lane even if a card renders.
- `non-matching variant signature` — a chart that does not match any of
  the three variant signatures yields an absent/empty field.

### Public surface non-leakage (extends `test_natal_public_builder.py` and `test_projection_shadow_v1_builder.py`)

- `no composed card in profile_public.blocks`
- `no composed card in profile_public.core_blocks`
- `no composed card in profile_public.extra_blocks`
- `no composed card in profile_public.detail_cards` (the legacy detail
  cards lane stays separate)
- `no composed card in profile_v8_projection_v1.differentiators`
- `no composed card in profile_v8_projection_v1.insight_strip`
- `no composed card in profile_v8_projection_v1.hero`
- `no composed card in profile_v8_projection_v1.identity_axis`
- Each test runs with both flag combinations
  (`PUBLIC_DETAIL_LANE` on/off).

### Copy QA

- Turkish diacritic presence in `headline` / `teaser` / `body` / `chips`
  (continues v0.9a.2 coverage, now applied at the lane level).
- No ASCII Turkish residue in lane output.
- No banned tokens (`MC route`, `10H`, `source_type`, `debug`,
  `candidate`, `fallback`, `MC, yöneticisi`) in lane output.
- `source_anchor_trace` is **absent** from the public card (test that
  trace fields are stripped before promotion).

### Golden stability

- Re-run the v0.9a.2 focused suite (`test_composed_detail_renderer`,
  `test_natal_public_builder`, `test_natal_promise_packets`,
  `test_natal_promise_cluster_plan`, `test_projection_shadow_v1_builder`)
  and confirm accepted goldens stable.
- New goldens for the lane payload itself on the three target charts
  (one per chart), stored as accepted snapshots.

### Negative tests

- `RENDER_DETAIL=off, PUBLIC_DETAIL_LANE=on` → field absent (lane cannot
  conjure a card without a rendered source).
- Bad eligibility shape (missing `public_eligibility` map, non-bool
  values) → field absent, no crash.

---

## Open Questions (for product / design sign-off before Phase C)

1. Does the deeper-details surface already exist in
   `profile_detail_flow_page.dart` in a shape that can host these
   cards, or do we need a new sub-route?
2. What is the visual contract for these cards — same as legacy
   `detail_cards`, or a distinct styling that signals "experimental
   composed reading"?
3. Should `chips` from the composed card be deduplicated against chips
   already shown elsewhere in the detail surface (e.g. `Kariyer` chip
   shown in both the legacy card and the composed card)?
4. Mobile telemetry: do we want a separate impression event for the
   composed detail surface so we can measure engagement without
   conflating with `detail_cards`?
5. Localization: is the `en` locale in scope for Phase C, or
   Turkish-only first?

---

## Non-Goals

This plan deliberately does **not** cover:

- adding new families or subtypes (still `career_route` / `public_voice`
  only)
- relaxing the chart allowlist beyond the three v0.9a.2 signatures
- any change to the selection or registry layer
- any change to `public_main` or `public_support`
- changing the traceability payload shape
- any LLM or generative pass over the card text (rendered text remains
  authored)

---

## Summary

- New public field: `profile_public.composed_detail_cards`
- New promotion-gate flag: `ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_DETAIL_LANE`
  (defaults to `false`)
- Eligibility = v0.9a.2 renderer eligibility + allowlist + render success
- Surfacing = deeper-detail-only, never hero/feed/identity
- Rollout = additive 4-phase path with explicit exit gates
- Tests = lane presence/absence, public-surface non-leakage, copy QA,
  golden stability
