# v0.9b.1 Plan — Narrow Detail Rollout for `moon_signature.home_inner_security`

> Planning artifact. **No code, registry, scoring, renderer, or
> selection changes are made by this document.** Implementation
> follows the same staged path the v0.9a.2 / Phase B rollout took.

## Scope

The v0.9b.1 cut promotes a single composed-semantic subtype into the
existing Phase B public detail lane behind a per-family +
per-subtype flag, with a 3-chart allowlist:

- family: `moon_signature`
- subtype: `home_inner_security`
- confidence threshold: `>= 0.80`
- allowlist:
  - `trabzon_2001_09_14`
  - `fix08_cancer_capricorn_nodes`
  - `cairo_1991_01_15`

Phase A (debug-only) of v0.9b has already shipped (v0.9b.0 + v0.9b.0.1
calibration). v0.9b.1 is Phase B for the Moon family — narrow,
allowlist-gated, renderer-gated, copy-bespoke.

## Out of Scope

- public_main, public_support routing
- `relationship_route` rendering (cross-family Moon-ownership rule
  actively blocks relationship promotion on these charts — see §10)
- other moon_signature subtypes (`intimacy_depth`,
  `private_emotional_processing`, `daily_sensitivity`,
  `creative_emotional_expression`, `emotional_rhythm`)
- renderer broadening beyond `home_inner_security`
- mobile / Flutter changes
- registry edits
- changes to existing accepted goldens beyond what the *opt-in* flag
  enables
- copy authoring for any chart outside the 3-chart allowlist

---

## 1. Detail Eligibility Gate

A `moon_signature` composed candidate becomes detail-eligible for the
v0.9b.1 Phase B-style lane when **all** of the following hold:

```
source_type == "composed_semantic"
family       == "moon_signature"
subtype      == "home_inner_security"
chart_facts_match is True
confidence   >= 0.80
public_eligibility.public_main_eligible    is False (hard-coded)
public_eligibility.public_support_eligible is False (hard-coded)
meta.subtype_default_fallback              is False
meta.moon_evidence_owned_by               == "moon_signature"
chart's variant signature is in the v0.9b.1 allowlist (§5)
ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9B_DETAIL_SUPPORT       is true
ENABLE_NATAL_COMPOSED_SEMANTICS_MOON_HOME_INNER_SECURITY_PUBLIC_DETAIL_LANE is true
the renderer's variant matcher returns a non-None variant (§2)
```

The gate lives in a single new helper —
`is_moon_home_inner_security_detail_lane_eligible(candidate)` —
parallel to v0.9a.2 / Phase B's
`is_composed_detail_lane_eligible`. It is referenced from a single
call site (the projection helper that emits
`profile_public.composed_detail_cards`), never from any other path.

`public_main_eligible` / `public_support_eligible` stay hard-coded
`False` for **all** moon_signature candidates across all v0.9b.1 flag
combinations. The gate does not — and cannot — graduate a Moon card
to either of those lanes.

---

## 2. Composed Detail Renderer Support for `moon_signature.home_inner_security`

The existing `backend/app/meaning/composed_detail_renderer.py` is
extended with **three new variant entries** plus a Moon-family
signature matcher.

### 2.1 New Variant Allowlist

```python
_MOON_HOME_INNER_SECURITY_VARIANT_ALLOWLIST: tuple[str, ...] = (
    "trabzon_2001_09_14_moon_home_inner_security",
    "fix08_cancer_capricorn_nodes_moon_home_inner_security",
    "cairo_1991_01_15_moon_home_inner_security",
)
```

These variant ids are deliberately distinct from the Phase B
career variants (`fix04_h10_career_stellium`, `tokyo_1998_06_21`,
`toronto_1976_06_26`) — so the Phase B career allowlist stays
untouched and the v0.9b.1 moon allowlist is independently gated.

### 2.2 New Signature Matcher

```python
def _match_supported_moon_home_inner_security_variant(
    candidate: Mapping[str, Any],
) -> str | None:
    ...
```

The matcher reads `candidate.evidence_trace.primitive_facts`:

- Moon house (target: 4, IC route, or Moon ruler in 4H)
- Moon sign (water signs preferred; Cancer especially)
- IC sign
- 4H planet content
- Moon-luminary aspect presence

Each of the three target charts produces a unique placement
signature; the matcher returns the corresponding allowlist variant
id when the placement set matches, else `None`.

The matcher is **only** wired into the v0.9b.1 renderer entry point —
not into the existing Phase B `_match_supported_public_voice_variant`,
which remains career-only.

### 2.3 Per-Variant Bespoke Copy

Like Phase B, each allowlisted variant gets its own pre-authored TR
copy. This is deliberate:

- per-chart copy reads as a real reading rather than a template
- the small N (3 charts) keeps the authoring load minimal
- per-chart copy lets us anchor the lived_scene to the specific
  primitive facts the matcher just verified

The copy must follow the semantic direction in §6.

---

## 3. Public Card Contract

The v0.9b.1 cards reuse the **existing**
`profile_public.composed_detail_cards` lane (introduced in Phase B).
**No new public field is added.**

### 3.1 Visible Fields (strict subset)

Same contract as Phase B career cards:

```
id           : composed_detail::composed_moon_signature_v0_9b::<variant>
node_id      : promise::composed_moon_signature_v0_9b
headline     : single sentence (Turkish, diacritics required)
teaser       : single sentence
body         : 3 sentences
chips        : list of 3 short labels
family       : "moon_home_inner_security"
emphasis     : "detail"
origin       : "composed_detail_renderer_v0_9b_1"
```

### 3.2 Fields Stripped from Public Card

The same `_strip_to_public_visible` projection already used by Phase B
strips:

```
source_type, source_candidate_id, public_job,
source_anchor_trace, detail_items, evidence_summary
```

`source_anchor_trace` (technical anchors, domain reasons, scoring)
remains in the traceability lane only.

### 3.3 Lane Emission Rule

The lane only emits when there is **at least one** card to promote.
When the v0.9b.1 flags are on but no chart matches the allowlist, the
field is omitted entirely (same behavior as Phase B career).

When both Phase B career and v0.9b.1 moon variants fire on the same
chart (theoretically possible — none of the 3 v0.9b.1 charts overlap
the 3 Phase B charts, but the rule must hold), the field becomes a
list of multiple cards, ordered:

1. Phase B career cards (existing)
2. v0.9b.1 moon cards (new)

This ordering is a deliberate display contract — career cards take
top placement when both exist.

---

## 4. Flag Gating

### 4.1 New Flag

```
ENABLE_NATAL_COMPOSED_SEMANTICS_MOON_HOME_INNER_SECURITY_PUBLIC_DETAIL_LANE
default: false
```

Naming notes:

- mirrors the v0.9a.3 Phase B flag pattern
  (`PUBLIC_DETAIL_LANE`) with an explicit per-subtype suffix
- explicit family + subtype in the name so a future engineer adding
  another subtype (e.g. `private_emotional_processing`) has a clear
  precedent: separate flag, not a wildcard

### 4.2 Flag Layering

| Flag (in order) | What it does in v0.9b.1 |
|---|---|
| `ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9` | enable composed semantics base — unchanged |
| `ENABLE_NATAL_COMPOSED_SEMANTICS_MOON_SIGNATURE_V0_9B` | produce moon_signature composed candidates — unchanged (v0.9b.0) |
| `ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9B_DETAIL_SUPPORT` | flip `detail_eligible=True` on qualifying moon candidates — unchanged (v0.9b.0) |
| `ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL` | render eligible cards into the trace lane — unchanged (Phase B) |
| `ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_DETAIL_LANE` | promote rendered cards into `profile_public.composed_detail_cards` — **shared with Phase B** |
| `ENABLE_NATAL_COMPOSED_SEMANTICS_MOON_HOME_INNER_SECURITY_PUBLIC_DETAIL_LANE` | **new** — opens the moon variant matcher in the renderer; without this flag, the renderer's moon path returns None even when all upstream flags are on |
| `ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_MAIN` | stays `false` |

### 4.3 Activation Matrix (Moon only)

| RENDER_DETAIL | PUBLIC_DETAIL_LANE | MOON_HOME_INNER_SECURITY_PUBLIC_DETAIL_LANE | trace Moon card | public Moon card |
|---|---|---|---|---|
| off | * | * | absent | absent |
| on | off | * | present (allowlist + signature match) | absent |
| on | on | off | present | absent |
| on | on | on (allowlist + signature match + conf ≥ 0.80) | present | present |
| on | on | on (chart not in allowlist) | present | absent |
| on | on | on (chart in allowlist but candidate Moon-owned-elsewhere=False... irrelevant for moon family, see §10) | present | present |

### 4.4 Cache Key

The new flag is added to `_interpret_ui_cache_key`'s
`composed_semantic_flag_signature`:

```
f"v09b_moon_hi_lane:{...MOON_HOME_INNER_SECURITY_PUBLIC_DETAIL_LANE...}"
```

Following the same pattern as Phase B (`v09_public_detail_lane`).

---

## 5. Allowlist Behavior

### 5.1 Chart Allowlist

```
trabzon_2001_09_14            (Moon imza @ home_inner_security, conf 0.88)
fix08_cancer_capricorn_nodes  (Moon imza @ home_inner_security, conf 0.85)
cairo_1991_01_15              (Moon imza @ home_inner_security, conf 0.81)
```

All three exceed the 0.80 confidence floor in the v0.9b.0.1 audit.

### 5.2 Allowlist Implementation

The allowlist is **derived from variant ids**, not from chart_ids.
The renderer's `_match_supported_moon_home_inner_security_variant`
function inspects `evidence_trace.primitive_facts` and returns one of
three variant ids when the placement signature matches. This:

- matches the Phase B design exactly
- keeps birth-data out of production logic (test-safe, no PII
  surface)
- makes the allowlist easy to extend in v0.9b.2 (new variant id +
  new copy entry)

### 5.3 Allowlist Behavior Under Edge Cases

- **Chart outside allowlist**: matcher returns `None` → renderer
  returns `None` → no card. Public field omits the moon entry.
- **Chart in allowlist but confidence < 0.80**: should not happen
  given the v0.9b.0.1 audit shows all three charts above 0.80, but
  the gate (§1) still enforces ≥ 0.80 as defensive depth.
- **Chart in allowlist but `chart_facts_match=False`**: renderer
  refuses. (Defensive — should not happen but the contract holds.)
- **Chart in allowlist but `meta.subtype_default_fallback=True`**:
  refused by the gate (§1). The v0.9b.0.1 calibration's correct
  fallback labeling makes this gate meaningful.

---

## 6. Copy Quality Rules

### 6.1 Semantic Direction (mandatory)

The card must describe `home_inner_security` as **emotional safety,
inner base, regulation, and belonging** — *not* generic family copy.

Each card's `body` must touch (in order, in TR):

1. **What happens when the person feels emotionally safe** —
   regulation, returning to base, settled rhythm
2. **What happens when that safety is missing** — friction surfaces,
   outer rhythm is harder to sustain, mood becomes environment-bound
3. **How home / roots / inner base affects outer rhythm** — the
   Moon-line carries the person's regulation surface; without inner
   ground, outer performance becomes fragile
4. **The gift** — emotional memory, care, grounding, protection
   capacity
5. **The friction** — over-attachment, retreat into the familiar,
   mood tied to environment, hyper-sensitivity to changes in the
   inner space
6. **The growth direction** — building inner safety as a portable
   state, not depending only on external security

The teaser captures (4) + (5) in a single sentence. The headline
distills (1) or (3) into a single sharp line.

### 6.2 Vocabulary — Recommended

Words that route correctly to the semantic direction (use freely):

- iç güven, duygusal zemin, iç düzen, kök, ait olma
- duygusal hafıza, sığınma, kendine dönme, geri çekilme
- bakım, koruma, sakinleşme, toparlanma
- içeriden taşınan, içeriden gelen, içeride kurulan

### 6.3 Vocabulary — Banned

Words / phrases that route to generic family copy or fatalistic
readings (must NOT appear in the card):

| Banned phrase | Why |
|---|---|
| "Aile önemlidir" | generic, doesn't carry the Moon route |
| "Ev hayatın güçlüdür" | generic, doesn't carry safety/regulation |
| "Annenle ilişkin" / "Babanla ilişkin" | implies literal family unless evidence shows it — Moon route is about inner base, not the literal mother |
| "Ailen senin için her şey" | fatalistic / sentimental |
| any phrase implying literal family problems | only legitimate when an aspect explicitly evidences it, which the home_inner_security path does not |
| "kalbinde yer eden aile" | overly sentimental |
| "ev sıcaklığı" used alone (not paired with regulation/inner-base) | nostalgic register, loses the Moon-line meaning |

### 6.4 Mechanical Quality Rules (inherited)

The card must additionally pass the existing
`_meets_public_quality` checks from v0.9a.2:

- no banned tokens (`debug`, `candidate`, `fallback`, `MC, yöneticisi`,
  `MC route`, `10H`, `source_type`, `public job`)
- no ASCII Turkish residue (`Insanlar`, `Disaridaki`, `nasil`, etc.)
- body has ≥ 18 words (Phase B minimum body length)
- Turkish diacritics present in headline, teaser, and body

### 6.5 P0 Truthfulness Rules (inherited)

The card must not introduce:

- `"olması de"` (vowel-harmony breaks)
- standalone `"Bazen de."` / `"bazen de."` fragments
- raw English aspect names (`"trine"`, `"square"`, etc.)
- raw house labels in body text (`"4H planet"`, `"IC sign"`)

### 6.6 Per-Chart Copy Authoring Notes

Each of the three target charts will receive bespoke copy that hits
all six semantic-direction beats while anchoring to its specific
primitive facts:

- **trabzon_2001_09_14**: anchor to whatever places Moon in
  `home_inner_security` for this chart (e.g. Moon in 4H, IC in
  Cancer-class).
- **fix08_cancer_capricorn_nodes**: anchor to the
  Cancer/Capricorn-axis weight on the chart's emotional spine; this
  chart's signature is identity↔home axis tension, so the body should
  carry the cardinal-water register without becoming fatalistic.
- **cairo_1991_01_15**: anchor to its specific home_inner_security
  signature.

Concrete authored TR copy will be drafted in implementation; this
plan does not commit to specific wording beyond the §6.1–§6.5
constraints.

---

## 7. Tests

Three layers, mirroring the v0.9a.2 / Phase B test suite.

### 7.1 Renderer Unit Tests (`test_composed_detail_renderer.py`)

For each of the three allowlist variants:

- `test_render_moon_home_inner_security_card_v0_9b_1_flag_off_returns_none`
- `test_render_moon_home_inner_security_card_v0_9b_1_renders_<variant>_when_all_flags_on`
- `test_render_moon_home_inner_security_card_v0_9b_1_rejects_non_target_signature`
- `test_render_moon_home_inner_security_card_v0_9b_1_rejects_below_confidence_threshold`
  (synthesize a candidate with confidence 0.79 and assert renderer
  returns `None`)
- `test_render_moon_home_inner_security_card_v0_9b_1_rejects_when_chart_facts_mismatch`
- `test_render_moon_home_inner_security_card_v0_9b_1_rejects_default_fallback_subtype`
  (synthesize a candidate with subtype=`emotional_rhythm` and assert
  rejection)

Per-card content tests:

- `test_render_moon_home_inner_security_card_carries_required_visible_fields`
  (exactly `{id, node_id, headline, teaser, body, chips, family,
  emphasis, origin}`)
- `test_render_moon_home_inner_security_card_strips_trace_fields`
  (no `source_type`, `source_candidate_id`, `public_job`,
  `source_anchor_trace`, `detail_items`, `evidence_summary` keys)
- `test_render_moon_home_inner_security_card_copy_carries_required_themes`
  (body contains at least one of "iç güven" / "duygusal zemin" /
  "kök" / "ait olma" / "düzenleme")
- `test_render_moon_home_inner_security_card_copy_avoids_banned_phrases`
  (no `"Aile önemlidir"`, no `"Ev hayatın güçlüdür"`, etc.)

### 7.2 Projection / Public Surface Integration Tests (`test_natal_public_builder.py`)

Per-chart, for each of the three target charts:

- `test_v0_9b_1_moon_home_inner_security_flag_off_field_absent`
- `test_v0_9b_1_moon_home_inner_security_flag_on_target_chart_emits_one_card`
- `test_v0_9b_1_moon_home_inner_security_non_target_charts_emit_no_card`
  (run over the 9-chart audit set minus the 3 allowlist charts)
- `test_v0_9b_1_moon_home_inner_security_card_uses_existing_composed_detail_cards_lane`
  (no new public field is introduced; the card sits in the same field
  Phase B uses)
- `test_v0_9b_1_moon_home_inner_security_relationship_card_does_not_render_on_same_chart`
  (cross-family ownership rule, §10)

Non-leakage across all v0.9b.1 flag combinations:

- `test_v0_9b_1_moon_home_inner_security_does_not_leak_into_blocks`
- `…core_blocks`
- `…extra_blocks`
- `…detail_cards`
- `…profile_v8_projection_v1.hero`
- `…identity_axis`
- `…insight_strip`
- `…differentiators`

### 7.3 Cluster Plan Trace Tests (`test_natal_promise_cluster_plan.py`)

- `test_v0_9b_1_moon_home_inner_security_appears_in_trace_when_flag_on`
- `test_v0_9b_1_moon_home_inner_security_keep_for_excludes_public_main_and_support`
  (the suppression entry must use `keep_for=["debug", "detail"]` or a
  strict subset)
- `test_v0_9b_1_does_not_alter_existing_phase_b_career_lane`
  (the existing 3-chart Phase B career rendering is byte-equal
  before/after v0.9b.1 flag flips)

### 7.4 Cache Key Test (`test_natal_public_builder.py`)

- `test_v0_9b_1_moon_home_inner_security_flag_changes_interpret_ui_cache_key`
  (toggle the new flag, assert cache key changes)

### 7.5 P0 Truthfulness Scan

Extend the existing connector-defect scanner:

- `test_v0_9b_1_no_p0_truthfulness_regression`
  (run `_collect_dangling_connector_scan_chunks` over the 3 allowlist
  charts with all v0.9b.1 flags on; assert zero `"olması de"`,
  `"Bazen de."`, `"bazen de."` occurrences)

### 7.6 Semantic Direction Scan

A direct check that the v0.9b.1 cards hit the user-specified
semantic vocabulary and avoid the user-specified anti-vocabulary:

- `test_v0_9b_1_moon_home_inner_security_card_copy_uses_safety_vocabulary`
- `test_v0_9b_1_moon_home_inner_security_card_copy_does_not_use_generic_family_phrases`

---

## 8. Public No-Leak Requirements

The v0.9b.1 rollout must continue Phase B's zero-leak guarantee. With
all v0.9b.1 + v0.9b.0.1 + Phase B flags simultaneously on, **none**
of these surfaces may carry an item whose `node_id` starts with
`promise::composed_moon_signature_v0_9b` OR whose `id` starts with
`composed_detail::composed_moon_signature_v0_9b::`:

- `profile_narrative_projection_v1.profile_public.blocks`
- `profile_narrative_projection_v1.profile_public.core_blocks`
- `profile_narrative_projection_v1.profile_public.extra_blocks`
- `profile_narrative_projection_v1.profile_public.detail_cards`
- `profile_v8_projection_v1.hero`
- `profile_v8_projection_v1.identity_axis`
- `profile_v8_projection_v1.insight_strip`
- `profile_v8_projection_v1.differentiators`

Additionally, `profile_v8_projection_v1` must not gain its own
`composed_detail_cards` field — v8 has no `profile_public` container;
the lane stays exclusive to `profile_narrative_projection_v1`.

The v0.9b.1 cards may only appear in:

- `profile_narrative_projection_v1.profile_public.composed_detail_cards`
  (the Phase B lane, now also carrying moon cards on the 3 allowlist
  charts)
- `profile_narrative_projection_v1.traceability.composed_detail_cards_v0_9a_2`
  (the existing trace lane — note we **may** extend this trace key to
  carry both career and moon cards; alternatively, introduce a sibling
  trace key `composed_detail_cards_v0_9b_1`. Decision deferred to
  implementation.)

The non-leak invariant is checked by integration tests (§7.2) on
every target chart × every flag combination.

---

## 9. Accepted Golden Stability

Two stability invariants:

### 9.1 Flag-Off Baseline Identical

With all v0.9b.1 flags off (default state):

- 5 Group-A audit charts (Istanbul 1994/1997/2020, Izmir 1996 v0.5,
  Adana 1998) — `_projection_surface_snapshot` byte-equal to
  pre-v0.9b.1 baseline
- 3 v0.9b.1 allowlist charts (trabzon, fix08, cairo) — same
- All other v0.9a, v0.9a.1, v0.9a.2, v0.9a.3, v0.9b.0, v0.9b.0.1
  goldens — byte-equal

### 9.2 Flag-On Public Surface Stable Except for the New Lane Field

With all v0.9b.1 flags on:

- For Group-A goldens (none in the v0.9b.1 allowlist):
  `_projection_surface_snapshot` is byte-equal to flag-off (these
  charts never receive a v0.9b.1 card).
- For the 3 v0.9b.1 allowlist charts: `composed_detail_cards` field
  is **the only public surface that changes**; all other surfaces
  (blocks, core_blocks, extra_blocks, detail_cards, v8 hero,
  identity_axis, differentiators, insight_strip) byte-equal to
  flag-off baseline.

### 9.3 Snapshot Helper

The existing `_projection_surface_snapshot` strips
`traceability` and compares only public surfaces. For v0.9b.1, a
helper variant that also strips `composed_detail_cards` from the
snapshot can be used to assert "everything except the new lane is
unchanged":

```python
def _projection_surface_snapshot_without_composed_detail_lane(public):
    return _projection_surface_snapshot({
        ...,
        "profile_public": {
            k: v for k, v in (public.get("profile_public") or {}).items()
            if k != "composed_detail_cards"
        },
    })
```

This helper makes the §9.2 invariant trivially testable.

---

## 10. Cross-Family Moon Ownership — Blocking Duplicate Relationship Rendering

The v0.9b.0.1 calibration introduced the cross-family Moon ownership
metadata. v0.9b.1 must honor it.

### 10.1 The Rule (already shipped in v0.9b.0.1)

When `relationship_route` and `moon_signature` both fire on the same
chart, and the relationship subtype consumed Moon evidence
(`emotional_need_affection`, `intimacy_depth`), the post-pass
compares confidences:

- if `moon_confidence >= relationship_confidence + 0.05`:
  → `relationship.meta.moon_evidence_owned_by = "moon_signature"`
  → `relationship.public_eligibility.future_renderer_eligibility_blocked = True`
  → `relationship.public_eligibility.reason_codes`
    appends `"moon_evidence_owned_elsewhere"`

The relationship candidate stays debug-visible (trace only). It is
not suppressed at the cluster plan layer.

### 10.2 How v0.9b.1 Honors the Block

The v0.9b.1 renderer-eligibility gate (§1) does **not** route
`relationship_route` candidates — those are out of scope for v0.9b.1.
But to defend against a future v0.9b.2 that opens a relationship
lane, the same gate logic that will eventually live in
`is_relationship_route_detail_lane_eligible` must check:

```
if candidate["public_eligibility"].get("future_renderer_eligibility_blocked"):
    return False
```

For v0.9b.1, this is **future-proofing only** — no relationship card
is being rendered yet. A test at §10.3 asserts the metadata is in
place so the future gate has what it needs.

### 10.3 Specific v0.9b.1 Test for Moon Ownership

```
test_v0_9b_1_moon_home_inner_security_does_not_grant_relationship_card_rendering
```

For each of the 3 allowlist charts:

- If the chart also fires a `relationship_route` candidate AND the
  candidate consumes Moon evidence, the relationship candidate's
  `public_eligibility.future_renderer_eligibility_blocked` must be
  `True`.
- No `composed_detail::composed_relationship_route_v0_9b::*` card is
  in `profile_public.composed_detail_cards` (or any other public
  lane).
- Only the moon card is in `composed_detail_cards`.

### 10.4 Charts in Scope of the Block Rule

From the v0.9b.0.1 50-chart audit, the 4 charts where Moon takes
ownership of relationship's Moon evidence are:

- antalya_1999_02_27
- cairo_1991_01_15
- madrid_2004_04_18
- diyarbakir_1994_03_22

**`cairo_1991_01_15` is in the v0.9b.1 allowlist**, so the rule fires
on this chart. The test in §10.3 explicitly covers this case.

- cairo's `moon_signature.home_inner_security @ 0.81` will render
- cairo's `relationship_route.intimacy_depth @ 0.71` will stay
  debug-only (Moon owns, future-eligibility blocked)

For `trabzon_2001_09_14` and `fix08_cancer_capricorn_nodes`:

- trabzon: only moon home_inner_security fires; no relationship card
  to dedupe.
- fix08: produces `relationship_route.trust_steadiness @ 0.80` (real,
  not fallback). But trust_steadiness is **not** a Moon-anchored
  subtype, so cross-family ownership does not apply. The relationship
  card stays debug-only because v0.9b.1 only opens the Moon lane —
  not because of the Moon-ownership rule.

So the cross-family block is **load-bearing on cairo and on cairo
only** within the v0.9b.1 allowlist.

---

## Acceptance Criteria for v0.9b.1

The implementation is ready to ship when:

1. All §7 tests pass.
2. Focused test suite (the five files used in the v0.9a.3 audit)
   passes with all v0.9b.1 flags enabled.
3. Accepted goldens are byte-identical under v0.9b.1 flags off.
4. Accepted goldens are byte-identical under v0.9b.1 flags on for
   any chart **not** in the v0.9b.1 allowlist.
5. For the 3 allowlist charts under flags-on, only
   `profile_public.composed_detail_cards` differs from the flag-off
   snapshot; every other public surface is byte-equal.
6. §8 non-leak invariants hold across 50-chart batch.
7. P0 truthfulness scan returns zero defects on the 3 allowlist
   charts' public copy.
8. Each authored card body passes §6 semantic-direction guardrails
   (manual review + automated banned-phrase scan).
9. Cache key invalidates correctly when the new flag toggles.
10. `cairo_1991_01_15` renders the moon card AND has its
    relationship card marked
    `future_renderer_eligibility_blocked=True` (cross-family rule
    holds end-to-end).

If any of (3), (4), (5), or (10) fails, the rollout halts and the
flag is reverted to default-`false`.

---

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Authored Moon copy slides into generic-family / sentimental register | §6.3 banned-phrase list + §7.6 semantic direction scan + manual copy review per card |
| The 3-chart allowlist accidentally widens through a too-liberal signature matcher | §2.2 matcher tightly references primitive_facts; §7.1 has explicit reject tests for non-target signatures |
| Confidence drift pushes a chart below 0.80 in a future scoring tweak | §1 gate enforces 0.80 floor as defensive depth — the renderer refuses below it even if the matcher returns a variant id |
| Relationship card sneaks into the new public lane on cairo via a wider eligibility gate | §10.3 dedicated test; §1 gate also requires `family == "moon_signature"` |
| `composed_detail_cards` field carries both career and moon cards in unexpected order | §3.3 explicit ordering contract: career first, then moon |
| Phase B career allowlist accidentally widens to include moon variants | §2.2 introduces a **separate** signature matcher; Phase B's `_match_supported_public_voice_variant` stays career-only — no shared mutable state |
| Mobile or downstream consumer expects only career cards in `composed_detail_cards` | Field name is family-agnostic; mobile contract was already documented as "list of detail cards" — Phase C work (deferred) will explicitly handle multi-family |

---

## Non-Goals (restated)

- No public_main / public_support routing.
- No registry edits.
- No renderer broadening beyond `moon_signature.home_inner_security`.
- No copy for other moon subtypes
  (`private_emotional_processing`, etc.).
- No relationship_route promotion of any kind.
- No mobile changes.
- No existing accepted-golden drift.
- No new public field beyond what Phase B already added.

---

## Summary

v0.9b.1 promotes a single composed-semantic subtype
(`moon_signature.home_inner_security`) into the existing Phase B
`profile_public.composed_detail_cards` lane behind a new
default-false flag and a 3-chart allowlist (trabzon, fix08, cairo).
The lane already exists; v0.9b.1 widens its renderer-side signature
matcher to recognize three moon variants and authors bespoke TR copy
for each, following a strict semantic direction (emotional safety /
inner base / regulation — not generic family copy). The v0.9b.0.1
cross-family Moon-ownership rule actively blocks cairo's
relationship card from any future render. Public_main, public_support,
relationship_route, and all other moon subtypes remain untouched in
v0.9b.1.

Subsequent steps (out of scope here): v0.9b.2 (second moon subtype —
likely `private_emotional_processing`), v0.9b.3 (relationship
`intimacy_depth` if and when ownership rule + audit allow), and
eventually Phase C mobile-side detail surface once the lane carries
≥ 6 chart fixtures.
