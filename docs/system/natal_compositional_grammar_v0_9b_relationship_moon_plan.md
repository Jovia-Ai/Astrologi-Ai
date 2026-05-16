# v0.9b Compositional Grammar Plan — `relationship_route` and `moon_signature`

> Planning artifact. **No code, registry, scoring, renderer, or
> selection changes** are made by this document. Implementation
> follows after explicit approval, in the same staged path used for
> v0.9a / v0.9a.1 / v0.9a.2 / v0.9a.3.

## Scope

Extend the v0.9 compositional grammar beyond `identity_route` and
`career_route` into two new families:

- `relationship_route`
- `moon_signature`

These are the two highest-frequency gaps in the post-v0.9a.3 50-chart
audit. Eight of the nine audited charts have `relationship` at
medium_strong or higher in their focus map; six of nine have
`inner_world` or `home_family` at medium_strong or higher, both of
which Moon-signature candidates would directly fill.

## Out of Scope

- public_main routing for `relationship_route` or `moon_signature`
- public_support routing in the first rollout (gated behind a
  per-family flag, identical to v0.9a's pattern)
- registry entry additions
- renderer (`composed_detail_renderer`) widening — Phase B's allowlist
  stays at the current three career fixtures until v0.9b proves
  candidate-level coverage
- changes to `_normalize_packet_field_text`, projection builders,
  cluster plan scoring, or selection
- changes to existing accepted goldens beyond what the *opt-in* flag
  layer can introduce
- mobile changes (Phase C of the v0.9a.3 plan stays deferred)

## Anchor Pattern (mirrors v0.9a)

```
chart facts → _build_v0_9_composed_semantic_candidates(...)
            ├── _build_career_route_candidates(...)       ← v0.9a (lives in production)
            ├── _build_relationship_route_candidates(...) ← v0.9b (NEW)
            └── _build_moon_signature_candidates(...)     ← v0.9b (NEW)

emits: candidate packet with
       source_type = "composed_semantic"
       family       = "relationship_route" | "moon_signature"
       subtype      = explicit subtype name
       public_eligibility = { debug_eligible, detail_eligible,
                              public_support_eligible (false in v0.9b.0),
                              public_main_eligible (false) }
       domain_reason / public_job / technical_anchors / chart_facts_match
```

The candidate flow into `natal_promise_cluster_plan_v1` is unchanged;
the cluster plan still suppresses these to `keep_for=["debug"]` until
the rollout flags promote them.

---

## 1. `relationship_route` Candidate Construction

### 1.1 Inputs

Primitive facts consumed (read-only — sourced from the existing
`primitive_facts` evidence trace):

- **DSC** sign
- **DSC ruler** (sign + house)
- **Venus** (sign + house + aspects)
- **Mars** (sign + house + aspects)
- **Moon** (sign + house + aspects — re-used; the same Moon entry
  feeds the `moon_signature` family but with a different framing
  contract)
- **5H / 7H / 8H** planets
- **Venus / Mars** to **Saturn / Pluto / Neptune** aspects
  (slow-planet aspects to relationship significators)
- relationship-domain contradictions if available (e.g.
  `closeness_vs_threshold`)

### 1.2 Construction Algorithm

```
1. Resolve DSC sign and DSC ruler placement.
2. Collect 7H planets; collect Venus + Mars placements; collect Moon
   placement (Moon is read but kept secondary — it's owned by the
   moon_signature family).
3. Score each subtype channel (§1.3). Pick the highest-scoring
   subtype with a margin of >= 0.04 over the runner-up; otherwise
   fall back to the "trust_steadiness" subtype as the neutral default
   (analogous to career_route's "strategic_role" fallback) and apply
   a small `subtype_penalty`.
4. Build `lived_scene` and `atoms` text seeds from the subtype's
   pre-authored TR copy table (no LLM, no per-chart string interp
   beyond noun substitution like sign / house labels).
5. Apply the gate at §1.6 before returning the candidate.
```

### 1.3 Subtype Routing

Eight subtypes — the v0.9 spec drafted 5; v0.9b adds 3 to cover the
gaps the 50-chart audit flagged.

| Subtype | Primary signal (any-of) | Secondary boost (each adds to score) |
|---|---|---|
| `trust_steadiness` | DSC ruler in earth sign or in 4H/10H; Venus or Saturn in 7H | Venus–Saturn trine/sextile; Mercury 7H |
| `attraction_warmth` | Venus in 5H/7H; Venus in fire sign; Sun in 5H | Mars–Venus harmonious aspect |
| `boundary_conflict` | Mars in 7H/8H; Mars–Saturn hard aspect; DSC ruler under Mars hard aspect | 1H/7H axis tension; Mars in cardinal in 7H |
| `intimacy_depth` | 8H planets (esp. Venus / Mars / Pluto / Moon); Venus–Pluto aspect | DSC ruler in 8H; Moon in 8H |
| `emotional_need_affection` | Moon in 7H/8H; Venus–Moon aspect; Cancer / Pisces 7H | Moon in water sign + 7H planet present |
| `hidden_private_love` *(new)* | Venus / Mars / DSC ruler in 12H; 12H planets aspecting 7H | Neptune in 5H/7H/8H; Pisces 7H |
| `freedom_space` *(new)* | Uranus in 7H/8H; Mars in air sign + 7H planet present; DSC ruler in 11H | Sun / Venus 11H; Aquarius 5H/7H |
| `wound_to_gift` *(new)* | Chiron in 5H/7H/8H; Saturn–Venus or Saturn–Moon hard aspect; DSC ruler in 12H + hard aspect | repeated "boundary then trust" pattern across multiple significators |

Subtype names line up with the user-supplied list. The default
fallback (`trust_steadiness`) carries the neutral-anchor penalty so
under-evidenced charts do not promote anything beyond
`debug_only` even if rollout flags are enabled.

### 1.3.1 Sanliurfa 1988 + Mexico City 1988 Calibration Addendum

The chart `1988-10-10 05:30 Sanliurfa, TR` should join the next
v0.9b calibration set as a normal/mixed relationship-route stress
case.

Observed debug-only read on the live pipeline:

- `moon_signature` fires correctly as
  `private_emotional_processing @ 0.66`
- `relationship_route` does not fire at all
- `identity_route` does register the Libra ASC + Sun/Mercury 1H
  spine on the v0.9a side
- `career_route` currently resolves to
  `invisible_preparation_before_visibility`, which is useful as a gap
  marker but not the best semantic fit for this chart

The relationship miss is load-bearing because the chart carries a
clear activation pattern that should not collapse into a generic
trust-only read:

- `DSC Aries`
- `DSC ruler Mars in Aries 6H retrograde`
- `Mars` hard aspects to `Saturn / Uranus / Neptune`
- `Moon Libra 12H + Moon square Neptune` already correctly owned by
  `moon_signature`
- strong daily-action / immediate-response tone in the relationship
  signature

Two calibration options are open for the next v0.9b pass:

**Option A — widen `boundary_conflict` detection**

Allow `boundary_conflict` to score from a broader Mars-anchored
relationship activation pattern, not only a 7H/8H house lock:

- `Aries` or `Scorpio` DSC
- DSC ruler `Mars` strongly dignified, angular, or otherwise
  functionally loud
- `Mars` in `1H / 6H / 10H / 12H`
- `Mars` hard aspects to `Saturn / Uranus / Neptune / Chiron`
- extra weight when `Mars` is retrograde
- extra weight when `Mars` is tied to daily/action houses
  (`6H` especially)

This path keeps subtype count stable and treats the Sanliurfa chart as
a wider reading of relationship conflict/stance activation.

**Option B — add a new subtype: `direct_relational_activation`**

Meaning:

- relationship activates response, positioning, and visible action
- closeness makes it harder to stay vague, imply, or wait too long
- daily interaction can trigger clarification or a more explicit
  stance
- conflict can happen, but it is not the semantic owner

This option is the safer planning direction. Widening
`boundary_conflict` is likely to over-pull Mars-led relationship cases
into a harsher subtype than the chart actually wants. Sanliurfa does
not primarily read as "conflict"; it reads as relationship activating
clearer positioning, quicker response, and visible movement inside the
bond. That semantic is narrower and more truthful under a dedicated
subtype than under an enlarged conflict bucket.

#### Recommendation

- prefer **Option B** for the next calibration pass
- keep **Option A** only as a fallback if later chart review shows the
  pattern is genuinely conflict-owned rather than activation-owned
- do **not** widen `boundary_conflict` in the same patch that first
  captures Sanliurfa

#### Detection rules for Option B

Primary gate:

- `DSC` sign is `Aries` or `Scorpio`
  **or**
- DSC ruler is materially Mars-led

Mars relevance gate:

- `Mars` is the DSC ruler
  **or**
- `Mars` is strong by sign (`Aries` / `Scorpio`)
  **or**
- `Mars` sits in `1H / 6H / 10H / 12H` with clear relationship-route
  relevance

Support factors:

- `Mars` in `6H` adds a daily/action route signal
- `Mars` in `1H` adds an identity/reaction route signal
- `Mars` in `10H` adds a visible-action route signal
- `Mars` in `12H` adds a hidden-action / indirect-response route
  signal
- hard aspects from `Mars` to `Saturn / Uranus / Neptune / Chiron`
  strengthen the subtype
- `Mars retrograde` is only a small support modifier and must never
  create the subtype by itself

Do not trigger when:

- Mars is strong but unrelated to the relationship route
- the chart is clearly better owned by `intimacy_depth`
- the chart is clearly better owned by `hidden_private_love`
- the chart is clearly better owned by `freedom_space`
- the chart is clearly better owned by `wound_to_gift`
- the emotional meaning is primarily Moon-owned, in which case
  `moon_signature` should keep ownership of that part

#### Confidence scoring changes

Keep the first-pass target at `medium`, not `high`.

Suggested calibration buckets:

- keep `dsc_route_strength` unchanged
- keep `dsc_ruler_strength` unchanged as the base route signal
- add a new `mars_activation_support` bucket
- add explicit `6H daily/action support`
- treat hard Mars aspects as a strengthening layer, not a subtype by
  themselves
- keep `Mars retrograde` as a small modifier only

Sanliurfa target after calibration:

- `subtype = direct_relational_activation`
- `confidence_target = medium`
- `public_job = debug_only`

#### False-positive risks

The main risk of **Option A** is semantic overreach:

- assertive Mars-led charts get misread as conflict-owned
- daily-action relationship charts get pulled into unnecessary
  friction language
- Uranus-led freedom cases drift away from `freedom_space`
- Chiron-led sensitivity cases drift away from `wound_to_gift`
- Scorpio/12H or 8H charts get flattened instead of staying under
  `hidden_private_love` or `intimacy_depth`

Option B has narrower risks:

- over-triggering on any `Aries DSC` chart
- mistaking fast response for relationship meaning
- double-counting Moon permeability already owned by
  `moon_signature`

These risks are easier to contain because Option B can require both a
Mars-led DSC route **and** real hard-aspect / action-house support.

#### Interaction with existing subtypes

- `boundary_conflict`
  remains the owner when the chart is genuinely about friction,
  threshold, or sustained boundary pressure; it should not absorb
  every Mars-led relationship chart
- `freedom_space`
  stays primary when Uranian space/independence is the semantic owner,
  even if Mars is present
- `intimacy_depth`
  stays primary when 8H / Pluto / deep-merging symbolism is stronger
- `hidden_private_love`
  stays primary when 12H secrecy/private-containment is the center of
  gravity
- `wound_to_gift`
  stays primary when Chiron/Saturn vulnerability and repair are the
  actual owners
- `emotional_need_affection`
  stays primary when Moon attachment / care-seeking is stronger than
  the Mars action pattern

#### Moon evidence ownership

Sanliurfa is the clearest example of why the Mars-led relationship
subtype must not consume Moon ownership:

- `Moon Libra 12H + Moon square Neptune` is already correctly handled
  by `moon_signature.private_emotional_processing`
- the relationship fix should only add the missing Mars-led response /
  stance / clarification meaning
- the emotional permeability, hidden feeling, and blurred-boundary
  material should remain owned by `moon_signature`
- if a future chart shows both signals, Moon ownership should still
  stay with `moon_signature` whenever Moon is the stronger semantic
  owner

#### Test plan

Positive:

- Sanliurfa 1988 should emit a debug-only relationship candidate once
  the subtype is implemented
- `moon_signature` must still emit
  `private_emotional_processing`
- `mexico_city_1988_08_31` should stay in the calibration review set
  as a mixed-case chart where
  `relationship_route.direct_relational_activation` coexists with a
  possible Moon-attachment reading
- public output must remain unchanged

Negative:

- `Aries DSC` + strong `Mars` but no hard aspects and no
  daily/action-route support should not auto-fire
- Mars hard aspects without a Mars-led relationship route should not
  auto-fire
- charts better captured by `intimacy_depth`,
  `hidden_private_love`, `freedom_space`, or `wound_to_gift` must
  remain there
- existing `boundary_conflict` and `trust_steadiness` cases must stay
  stable

Regression:

- accepted goldens stay byte-identical
- no `public_main` / `public_support` movement
- no renderer or public-surface change

#### Rollout recommendation

- keep this future subtype `debug_only` first
- review it on the 50-chart batch plus Sanliurfa and
  `mexico_city_1988_08_31` before any renderer or public-lane
  planning
- add it to the v0.9b plan as a future calibration subtype, not as an
  immediate rollout target

Expected debug-only candidate shape for Sanliurfa 1988 after
calibration:

```yaml
family: relationship_route
subtype: direct_relational_activation
domain: relationship
domain_reason:
  - DSC route
  - DSC ruler involved
  - Mars boundary/desire signature
  - 6H daily/action route
confidence_target: medium
public_job: debug_only
lived_scene: Birine yaklaştığında, belirsizliği uzun süre taşımak sana kolay gelmeyebilir.
```

Recommendation for planning:

- record `direct_relational_activation` as a future calibration
  subtype in the v0.9b plan
- treat Sanliurfa 1988 as the lead stress case for that subtype
- track `mexico_city_1988_08_31` as the immediate follow-up
  calibration chart for mixed Mars-led + Moon-attachment ownership
- keep runtime and public behavior unchanged until the subtype is
  batch-validated

#### Follow-up calibration chart: `mexico_city_1988_08_31`

The chart `mexico_city_1988_08_31` should now be tracked alongside
Sanliurfa as a second debug-only calibration fixture for
`direct_relational_activation`.

Observed debug-only read after the first Mars-led calibration pass:

- `relationship_route.direct_relational_activation` fires at
  `medium` confidence
- the chart also carries a plausible Moon-attachment edge case via
  `Moon Taurus 7H`
- public output remains unchanged

Why this chart matters:

- Sanliurfa is the cleaner split case:
  `direct_relational_activation` +
  `moon_signature.private_emotional_processing`
- Mexico City is the mixed-ownership case:
  Mars-led relationship activation is real, but Moon-in-7H may also
  support `emotional_need_affection`
- this makes Mexico City the right chart to answer the next ownership
  question before any broader relationship calibration continues

Future calibration question for this pair:

- when `Moon` is in `7H` and Mars-led relationship activation also
  exists, should ownership split as:
  `relationship_route.direct_relational_activation` owning
  action/stance/clarification and Moon-led routing owning emotional
  need/attachment
- or should one subtype suppress the other when the signals are too
  overlapping

Current planning direction:

- keep both Sanliurfa and Mexico City `debug_only`
- do not suppress either family automatically without a batch review
- treat Mexico City as the lead edge case for deciding whether the
  system should support split ownership or single-owner suppression in
  mixed Moon-attachment + Mars-activation charts

### 1.4 Confidence Scoring

```
dsc_route_strength     : 0.00 – 0.25   (DSC angularity / sign clarity)
dsc_ruler_strength     : 0.00 – 0.20   (ruler condition + house)
venus_support          : 0.00 – 0.15   (Venus tied to subtype evidence)
mars_support           : 0.00 – 0.15   (Mars tied to subtype evidence)
moon_support           : 0.00 – 0.10   (Moon tied to subtype evidence)
house_scene_support    : 0.00 – 0.10   (5H/7H/8H reinforcement)
contradiction_coherence: 0.00 – 0.05   (when a relationship contradiction aligns)
subtype_penalty        : 0.00 – 0.10   (subtracted; fires on fallback / under-evidenced)
```

Sum is clamped to `[0.0, 0.94]` then rounded to 4 decimals — same
shape as `_build_career_route_candidates` to keep score distributions
comparable across families.

Reduce score (apply `subtype_penalty` ≥ 0.05) when:

- Only one of `Venus / Mars / Moon` carries evidence for the picked
  subtype
- DSC ruler lies in a "neutral" house (2/3/9/11 with no aspect
  evidence) and no 7H planet is present
- Venus / Mars / Moon evidence points at different subtypes (the
  signal is split — confidence should not stack)

### 1.5 `domain_reason` and `public_job`

`domain_reason` (always a list, ordered most-specific first):

- `DSC route`
- `DSC ruler involved`
- `7H planet`
- `Venus relationship signature`
- `Mars boundary/desire signature`
- `Moon attachment signature`
- `8H intimacy signature`
- `12H hidden-love signature`
- `Uranus freedom signature`
- `Chiron wound-to-gift signature`

`public_job` for v0.9b.0:

- always emit `"debug_only"` in the first rollout
- detail-eligible candidates additionally tag `"detail_shadow"` in
  meta but the public_job stays `debug_only` until v0.9b.1 (see §7)

### 1.6 Eligibility Gate (returns `None` when not met)

```
return None if:
    DSC sign is unknown
    DSC ruler placement is unknown
    no 7H planet AND DSC ruler not in {1, 5, 7, 8}
    no Venus/Mars/Moon evidence tied to picked subtype
    final confidence < 0.60
```

Confidence floor matches v0.9a career_route (`< 0.6 → None`). This
keeps the candidate-inventory noise floor stable.

---

## 2. `moon_signature` Candidate Construction

### 2.1 Inputs

- **Moon** sign, house, aspects
- **Moon ruler** placement
- **IC / 4H** content (Moon at IC, Moon ruler in 4H, 4H planets)
- **6H** for daily rhythm (6H planets aspecting Moon, Moon in 6H)
- **8H** for emotional depth (Moon in 8H, Moon–Pluto/Scorpio routes)
- **12H** for private processing (Moon in 12H, Moon ruler in 12H,
  Moon–Neptune aspects)
- **5H** for creative emotional expression (Moon in 5H, Moon ruler in
  5H, Moon–Venus aspects with 5H involvement)
- Moon–luminary and Moon–angular aspects for emphasis

### 2.2 Construction Algorithm

```
1. Resolve Moon sign and house.
2. Resolve Moon ruler placement.
3. For each candidate subtype, score the channel evidence (§2.3).
4. Pick the highest-scoring subtype with margin >= 0.04; fall back
   to `emotional_rhythm` (neutral default) with `subtype_penalty`.
5. Build lived_scene / atoms from the subtype TR copy table.
6. Apply the gate at §2.6 before returning.
```

### 2.3 Subtype Routing

Six subtypes — directly map to the six anchor surfaces the user
listed (sign / house / aspects / ruler / IC-4H plus the three deeper
houses):

| Subtype | Primary signal | Secondary boost |
|---|---|---|
| `emotional_rhythm` (default) | Moon sign tone w/ neutral house | Moon–Sun harmonious aspect |
| `home_inner_security` | Moon in 4H; Moon at IC; Moon ruler in 4H | 4H planets present; Cancer ASC/MC |
| `daily_sensitivity` | Moon in 6H; 6H planets aspecting Moon | Virgo Moon; Moon–Mercury aspect with 6H involvement |
| `creative_emotional_expression` | Moon in 5H; Moon–Venus aspect with 5H | Moon ruler in 5H; Leo/Pisces Moon in 5H |
| `intimacy_depth` (Moon flavor) | Moon in 8H; Moon–Pluto aspect; Scorpio Moon | Moon ruler in 8H; 8H planets aspecting Moon |
| `private_emotional_processing` | Moon in 12H; Moon–Neptune aspect; 12H planets aspecting Moon | Moon ruler in 12H; Pisces Moon |

`intimacy_depth` deliberately overlaps with `relationship_route.intimacy_depth`
on the user-facing label but the **family is different** (`moon_signature`
vs `relationship_route`). The cluster plan can choose between them
based on `family` and `domain_reason`. The selection layer's existing
dedup keys (`node_id`, `id`) keep them from colliding in any single
public surface.

### 2.4 Confidence Scoring

```
moon_sign_strength     : 0.00 – 0.15
moon_house_scene       : 0.00 – 0.20
moon_ruler_route       : 0.00 – 0.20
aspect_support         : 0.00 – 0.20
reinforcement_support  : 0.00 – 0.15   (IC/4H/6H/8H/12H/5H reinforcement)
subtype_coherence      : 0.00 – 0.10
subtype_penalty        : 0.00 – 0.10   (subtracted on default fallback)
```

Sum clamped to `[0.0, 0.94]`, rounded to 4 decimals.

Reduce score when:

- Only sign tone exists (no house / no ruler / no aspect evidence)
- Moon aspects are noisy (≥3 active aspects, none > weight 0.7)
  without a clear subtype channel
- Moon ruler is debilitated AND none of the reinforcement channels
  (4H/6H/8H/12H/5H) fire

### 2.5 `domain_reason` and `public_job`

`domain_reason`:

- `Moon need signature`
- `Moon house scene`
- `Moon ruler route`
- `IC/4H reinforcement`
- `6H daily-rhythm route`
- `8H intimacy route`
- `12H private-processing route`
- `5H creative-emotional route`
- `Moon-luminary aspect`

`public_job` for v0.9b.0:

- always `"debug_only"` initially
- detail-eligible candidates may tag `"detail_shadow"` in meta only

### 2.6 Eligibility Gate

```
return None if:
    Moon sign is unknown
    Moon house is unknown
    Moon ruler placement is unknown
    final confidence < 0.60
    moon_signature would tie 1:1 with an existing exact-registry
      Moon packet covering the same anchor (deduplicated upstream by
      `id` and `node_id` keys — see §5)
```

---

## 3. Confidence Scoring — Cross-Family Notes

The two new families share the same scoring shape as `career_route`:

- max score 0.94 (capped — leaves visible headroom under registry
  exact packets that float around 0.95–0.99)
- min publishable threshold 0.60
- penalty applied on default subtype fallback
- rounded to 4 decimals
- separate "discovery_routes" entry in candidate `meta` (`["relationship_route"]`
  / `["moon_signature"]`) for the cluster plan's per-route ledger

Confidence distribution targets for v0.9b.0 (debug-only) — measured on
the 50-chart batch:

| Bucket | Target distribution |
|---|---|
| ≥ 0.80 (strong) | ~25% of charts produce ≥ 1 such candidate per family |
| 0.65–0.80 (medium) | ~50% |
| 0.60–0.65 (low pub) | ~20% |
| < 0.60 (filtered) | ~5% — should self-suppress via the eligibility gate |

If actual measurements skew significantly above this (e.g. > 60% of
charts hit ≥ 0.80 on relationship_route), the rollout pauses and the
scoring weights are recalibrated *before* any public flag flips.

### 3.1 Sanliurfa 1988 — Cross-Family Calibration Read

Sanliurfa 1988 is a useful calibration chart because the four family
signals separate cleanly:

- `moon_signature` already fires in the expected direction:
  `Moon Libra 12H + Moon square Neptune -> private_emotional_processing`
- `relationship_route` under-detects a real Mars-led activation
  pattern and currently misses entirely
- `identity_route` already sees the `Libra ASC + Sun/Mercury 1H`
  identity-speech spine on the v0.9a side
- `career_route` currently overfits a backstage/preparation subtype
  where the chart more likely wants a future voice/public-role tension
  subtype

This makes the chart especially valuable for v0.9b calibration
because it shows:

- one Moon success case
- one relationship miss
- one identity confirmation outside v0.9b scope
- one future career mismatch note without requiring any immediate
  v0.9b implementation change

### 3.2 Future Career Note — Not Part of v0.9b

For the same Sanliurfa chart, the current `career_route` resolution
(`invisible_preparation_before_visibility`) is not the best semantic
fit for:

- `MC Cancer`
- `Sun/Mercury 1H`
- `MC` square `Sun/Mercury`

Future career grammar planning should consider a subtype closer to:

`public_role_identity_voice_tension`

This note is not a v0.9b implementation target. It is recorded here
only so the chart is not misread later as a pure Moon or relationship
calibration case.

---

## 4. `domain_reason` and `public_job` — Schema Notes

Both families must:

- emit a non-empty `domain_reason: list[str]` whose first entry is the
  primary route anchor (e.g. `"DSC route"`, `"Moon need signature"`)
- emit `public_job` from the allowed set per §1.5 / §2.5
- emit `technical_anchors: list[str]` with concrete chart facts — the
  same shape Phase B's renderer trace consumes via
  `source_anchor_trace`

This keeps both families forward-compatible with the v0.9a.2 renderer
contract without changing the renderer.

---

## 5. Exact Registry Override Compatibility

The registry currently has authored packets for many relationship and
Moon shapes. Compatibility rules:

- Composed candidates and registry packets are matched by `id` and
  `node_id` upstream. v0.9b composed packets use ids of the form:
  ```
  composed_relationship_route_v0_9b
  composed_moon_signature_v0_9b
  ```
  These will not collide with any registry id.

- When a registry exact packet covers the **same domain + same
  subtype + same primary anchor**, the cluster plan's existing
  scoring path already prefers the registry packet (registry exacts
  score ~0.95–0.99; composed caps at 0.94). No change needed.

- A composed candidate that overlaps a registry exact will still be
  emitted into the candidate inventory but will be **suppressed by
  the existing dedup-by-anchor logic** at cluster plan selection
  time. It remains visible in trace for audit but does not enter the
  public surface.

- When a registry exact packet is *missing* the family's primary
  subtype on a given chart (e.g. registry has `attraction_warmth` but
  not `boundary_conflict` for this chart's shape), the composed
  candidate fills the gap. This is the intended growth surface — and
  is itself gated by `public_job=debug_only` in v0.9b.0.

No registry edits are required for v0.9b.0.

---

## 6. Generic Fallback Suppression

Both new families participate in the existing generic-fallback
suppression logic with one addition:

A composed `relationship_route` or `moon_signature` candidate may
suppress a `generic_fallback` packet **only when**:

1. composed candidate's `family` matches the fallback's `domain` (e.g.
   `relationship_route` → `relationship` domain)
2. composed candidate's subtype is explicit (not the default fallback
   subtype with `subtype_penalty` applied)
3. composed confidence ≥ 0.70 (one notch above the inclusion floor,
   to ensure suppression replaces fallback only when the composed
   evidence is unambiguous)
4. composed candidate's `lived_scene` is non-empty and at least one
   `technical_anchors` entry exists
5. composed `domain_reason` includes at least one of the family's
   "primary anchor" markers (DSC/DSC-ruler/7H for relationship; Moon
   itself or a house-scene marker for Moon)

This rule matches the v0.9a career_route generic-fallback suppression
behavior. When the rule does not fire, the generic_fallback stays
and the composed candidate goes to `keep_for=["debug"]` only.

---

## 7. Initial Rollout Flags

v0.9b.0 introduces three new flags (all default `false`). The naming
convention mirrors v0.9a:

```
ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_ROUTE_V0_9B          (master gate for the family)
ENABLE_NATAL_COMPOSED_SEMANTICS_MOON_SIGNATURE_V0_9B              (master gate for the family)
ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9B_DETAIL_SUPPORT              (shared detail-support gate)
```

Behavior matrix at v0.9b.0:

| Flag(s) | Candidate inventory | Cluster plan | Public output |
|---|---|---|---|
| All off | composed relationship / moon candidates NOT produced | unchanged | unchanged |
| `*_RELATIONSHIP_ROUTE_V0_9B=true` only | composed relationship candidates produced, `keep_for=["debug"]` | candidate visible in trace, NOT in surface_plan | unchanged |
| `*_MOON_SIGNATURE_V0_9B=true` only | composed moon candidates produced, `keep_for=["debug"]` | candidate visible in trace, NOT in surface_plan | unchanged |
| Both family flags on | both families produce; both stay debug-only | trace visible | unchanged |
| Either family + `*_V0_9B_DETAIL_SUPPORT=true` | candidates become `detail_eligible=true` | suppressed_packets entry adds `"detail"` to `keep_for` | unchanged — **Phase B renderer allowlist still gates public emission**; widening the allowlist is v0.9b.1+ |

Phase B's `ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_DETAIL_LANE` keeps
its three-fixture allowlist. v0.9b.0 explicitly does **not** widen
the renderer; even with all v0.9b flags on, no v0.9b candidate
reaches `profile_public.composed_detail_cards`. Lane expansion to new
families is a separate, later, deliberate step (v0.9b.1).

`public_main_eligible` is hard-coded `false` for both families across
all v0.9b.0 flag combinations — there is no flag combination in
v0.9b.0 that can promote relationship or moon composed candidates
into public_main.

Cache key impact: each new flag must be added to
`_interpret_ui_cache_key` in `app/api/routes/natal_interpretation.py`
so toggle changes invalidate cached responses (the same change
pattern used for `v09_public_detail_lane`).

---

## 8. Debug-Only-First Behavior

The first deployable cut of v0.9b is **debug-only**:

- composed candidates appear in `candidate_packets` with
  `source_type="composed_semantic"` and `keep_for=["debug"]`
- they appear in `traceability.natal_promise_cluster_plan_v1.candidate_packets`
  and `traceability.composed_detail_cards_v0_9a_2` is **not**
  expanded — that key keeps its career-only contract
- they appear in cluster plan's `composed_candidate_public_eligibility_distribution`
  ledger
- they do **not** appear in:
  - `profile_public.blocks`
  - `profile_public.core_blocks`
  - `profile_public.extra_blocks`
  - `profile_public.detail_cards`
  - `profile_public.composed_detail_cards` (Phase B's lane stays
    career-only)
  - `profile_v8_projection_v1.hero` / `identity_axis` / `differentiators`
    / `insight_strip`
- they do not influence:
  - `surface_plan.public_main_cluster_ids`
  - `surface_plan.public_support_cluster_ids`
  - `focus_map` tier assignment (which is computed before composed
    candidates apply suppression)

This is the same path v0.9a took through v0.9a.1, v0.9a.2, and Phase B
of v0.9a.3. The proven sequence is:

1. v0.9b.0 — debug-only emission, no public effect
2. v0.9b.1 — widen the `composed_detail_renderer` allowlist (signature
   matcher) to the new families, behind `PUBLIC_DETAIL_LANE` and a
   per-family allowlist gate
3. v0.9b.2 — explicit per-family public_support routing (only if
   v0.9b.1 measurements are clean)
4. v0.9c+ — eventual public_main routing, only after at least one
   public_support cycle measures clean on the 50-chart batch

Each step is its own approved rollout with its own audit. Nothing in
v0.9b.0 commits us to v0.9b.1.

---

## 9. Tests

### 9.1 Unit-level (in `test_natal_promise_packets.py`)

For each new family:

- `test_build_<family>_candidates_returns_none_when_master_flag_off`
- `test_build_<family>_candidates_returns_none_when_inputs_missing`
  (DSC unknown for relationship; Moon sign unknown for moon)
- `test_build_<family>_candidates_emits_subtype_<each_subtype>_when_signals_present`
  (one test per subtype, fixtures with the exact primary-signal shape)
- `test_build_<family>_candidates_default_fallback_subtype_carries_penalty`
- `test_build_<family>_candidates_confidence_floor_filters_under_0_60`
- `test_build_<family>_candidates_domain_reason_first_entry_is_primary_anchor`
- `test_build_<family>_candidates_public_job_is_debug_only_in_v0_9b_0`
- `test_build_<family>_candidates_public_eligibility_main_is_false`

### 9.2 Cluster plan (in `test_natal_promise_cluster_plan.py`)

- `test_v0_9b_<family>_candidates_stay_debug_only_with_master_flag_on`
  (confirm `suppressed_packets[…].keep_for == ["debug"]`)
- `test_v0_9b_<family>_with_detail_support_flag_adds_detail_to_keep_for`
- `test_v0_9b_<family>_does_not_override_exact_registry_public_clusters`
  (mirrors the v0.9a equivalent test)
- `test_v0_9b_<family>_generic_fallback_suppression_fires_only_above_0_70_confidence`
- `test_v0_9b_<family>_does_not_appear_in_public_main_or_public_support_cluster_ids`
- `test_v0_9b_<family>_appears_in_composed_candidate_public_eligibility_distribution_ledger`

### 9.3 Public surface (in `test_natal_public_builder.py`)

For both families, with all v0.9b flags on:

- `test_v0_9b_<family>_does_not_leak_into_profile_public_blocks`
- `test_v0_9b_<family>_does_not_leak_into_core_blocks_or_extra_blocks`
- `test_v0_9b_<family>_does_not_leak_into_legacy_detail_cards`
- `test_v0_9b_<family>_does_not_leak_into_profile_public_composed_detail_cards`
  (Phase B lane stays career-only)
- `test_v0_9b_<family>_does_not_leak_into_v8_hero_identity_axis_differentiators_insight_strip`
- `test_v0_9b_<family>_flag_off_baseline_matches_accepted_goldens`
  (using the existing `_projection_surface_snapshot` helper)
- `test_v0_9b_<family>_flag_on_keeps_target_public_surfaces_stable`
  (snapshot equality across flag-off vs flag-on; this is the
  critical golden-stability gate — same pattern as
  `test_public_natal_view_v0_9a_2_render_detail_flag_on_keeps_target_public_surfaces_stable`)

### 9.4 P0 truthfulness scans (extend the existing audit-driven scans)

Run the existing
`_collect_dangling_connector_scan_chunks` over the v0.9b-enabled
outputs of `_DANGLING_CONNECTOR_AFFECTED_CHARTS` (and the 50-chart
batch fixtures listed in §10) — confirm zero new `"olması de"` or
`"Bazen de."` occurrences are introduced by the new families' TR
copy seeds.

### 9.5 Cache key

- `test_v0_9b_flags_change_interpret_ui_cache_key` — toggling each of
  the three v0.9b flags produces a different cache key.

### 9.6 Per-flag-combination matrix

A single integration test that walks the 4-combo matrix
(family-off, family-on, family-on+detail-support-off,
family-on+detail-support-on) on three sentinel charts (one each:
relationship-strong, moon-strong, both-strong) and asserts the
expected `keep_for` / candidate visibility transitions per the
table in §7.

### 9.7 Add Sanliurfa 1988 to the next calibration batch

Include `1988-10-10 05:30 Sanliurfa, TR` in the next v0.9b
debug-only review slice with these expectations:

- `moon_signature` fires as
  `private_emotional_processing` at medium confidence and stays
  `debug_only`
- `relationship_route` is currently a known miss and should become the
  lead calibration assertion for the future
  `direct_relational_activation` subtype from §1.3.1
- `identity_route` remains a confirming side-signal for
  `Libra ASC + Sun/Mercury 1H`
- `mind` is logged as a future grammar gap (`Mercury 1H` +
  `Saturn/Uranus 3H`)
- `career_route` is logged as a future subtype-mismatch note, not as
  evidence that the chart is already well covered
- public surfaces remain unchanged across all v0.9b debug-only flag
  combinations

Add `mexico_city_1988_08_31` to the same debug-only review slice with
these expectations:

- `relationship_route.direct_relational_activation` remains present as
  a debug-only candidate
- `Moon Taurus 7H` is explicitly tracked as a possible
  `emotional_need_affection` ownership edge case rather than ignored
- the chart is used to answer whether mixed Moon-attachment +
  Mars-activation charts should split ownership or suppress to a
  single owner
- public surfaces remain unchanged across all v0.9b debug-only flag
  combinations

---

## 10. Expected Metrics on the 50-Chart Batch

Targets to validate v0.9b.0 before the rollout flag flips. Numbers
are derived from the post-v0.9a.3 health audit's pattern distribution
across the 9-chart slice extrapolated to the 50-chart fixture
(`natal_50_chart_discovery_metrics.json`). Concrete thresholds for
acceptance:

### 10.1 Candidate-level

| Metric | Target for v0.9b.0 |
|---|---|
| Charts producing ≥ 1 `relationship_route` composed candidate | ≥ 35 / 50 (70%) |
| Charts producing ≥ 1 `moon_signature` composed candidate | ≥ 40 / 50 (80%) |
| Mean composed candidates per chart (across both new families) | 2.0–3.5 |
| Charts where a composed candidate would **replace** a `generic_fallback` packet (per §6 rule) | ≥ 15 / 50 (30%) |
| Charts where a composed candidate would **replace** a `discovery_scaffold` packet | ≥ 10 / 50 (20%) |
| Charts where the default fallback subtype fires (penalty applied) | ≤ 12 / 50 (24%) |

### 10.2 Confidence distribution

Each family's score histogram on the 50-chart batch should hit:

| Bucket | Target |
|---|---|
| ≥ 0.80 | ~25% of candidates |
| 0.70–0.80 | ~35% |
| 0.60–0.70 | ~35% |
| < 0.60 (suppressed by gate) | ≤ 5% of pre-gate trials |

### 10.3 Public-surface invariants (zero-tolerance)

| Invariant | Target |
|---|---|
| Composed v0.9b candidates appearing in `profile_public.blocks` | 0 across all 50 charts × all flag combos |
| Composed v0.9b candidates in `core_blocks` / `extra_blocks` / `detail_cards` | 0 |
| Composed v0.9b candidates in `profile_public.composed_detail_cards` | 0 (Phase B lane stays career-only) |
| Composed v0.9b candidates in any v8 lane (hero, identity_axis, insight_strip, differentiators) | 0 |
| Charts whose accepted goldens drift under v0.9b flags off | 0 (default behavior must match v0.9a.3 exactly) |
| Charts whose accepted goldens drift under v0.9b flags on (debug-only path) | 0 (debug-only must be invisible to all public surfaces) |

### 10.4 P0 / copy-quality invariants

| Invariant | Target |
|---|---|
| `"olması de"` introductions in any public surface | 0 |
| `"Bazen de."` / `"bazen de."` introductions | 0 |
| English aspect names ("trine", "square", …) leaking into TR public copy | 0 |
| ASCII Turkish residue in any composed-rendered text | 0 (continues v0.9a.2 follow-up coverage) |

### 10.5 Health-score impact (informational)

Re-running the post-v0.9a.3 health audit harness with v0.9b.0 flags
on should show:

- Median health score ≥ 65 (no regression vs the v0.9a.3 baseline)
- Charts in the 30–49 health bucket (currently Kutahya 1959, Izmir
  1996 v0.5, Izmir 2007) gain a composed_semantic candidate count
  increase of at least +2 per chart — without changing their public
  surface
- No new appearance in the 0–29 bucket

These are informational targets; v0.9b.0 ships if the zero-tolerance
invariants in §10.3 and §10.4 all hold, even if §10.5's score targets
miss.

### 10.6 Sanliurfa 1988 — Expected outcome after calibration

Once the next relationship calibration pass lands, Sanliurfa 1988 is
expected to move from:

- Moon-only composed coverage
- generic relationship fallback ownership

to:

- `moon_signature.private_emotional_processing`
- `relationship_route.direct_relational_activation`

with both candidates remaining `debug_only` in the immediate v0.9b
phase.

Acceptance target for this specific chart:

- relationship candidate confidence reaches `medium`
- `domain_reason` includes `DSC route`, `DSC ruler involved`, and a
  Mars-led relationship anchor
- Moon-owned emotional material remains with
  `moon_signature.private_emotional_processing`
- public output remains unchanged
- the chart joins the ongoing calibration set rather than any public
  rollout allowlist

### 10.7 Mexico City 1988 — Ownership edge case to keep in calibration

`mexico_city_1988_08_31` should remain in the v0.9b calibration set
as a mixed ownership chart:

- `relationship_route.direct_relational_activation` is a valid
  Mars-led read
- `Moon Taurus 7H` may also support
  `relationship_route.emotional_need_affection` or a Moon-family
  emotional-need owner, depending on later Moon/relationship
  calibration decisions
- public output must remain unchanged while this is unresolved

This chart is not a public-rollout candidate. It is a calibration
question-holder:

- should action/stance ownership and emotional-need ownership split
  across two families or subtypes
- or should one owner suppress the other when overlap is high

Until that question is answered in a later calibration pass, Mexico
City stays debug-only and is reviewed together with Sanliurfa in the
next relationship batch.

---

## Acceptance Criteria for v0.9b.0

The implementation is ready to ship when:

1. All §9 tests pass.
2. Focused test suite (the five files used in the v0.9a.3 audit)
   passes with both families enabled.
3. Accepted goldens are byte-identical under v0.9b flags off.
4. Accepted goldens are byte-identical under v0.9b flags on
   (debug-only invisibility).
5. §10.3 and §10.4 invariants hold across the 50-chart batch.
6. Health audit harness re-run shows no new public-surface defects.
7. Cache key invalidates correctly per §9.5.

If any of (3), (4), (5.public-surface invariants), or (6) fail, the
rollout halts and the family is reverted to flag-default.

---

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Double-counting Moon evidence between `relationship_route.emotional_need_affection` and `moon_signature.relational_route` | The cluster plan's existing `id`/`node_id` dedup catches this; additionally, §1.4 reduces score when Venus/Mars/Moon evidence splits across subtypes |
| Default-fallback subtype dominates the candidate distribution | §1.4 `subtype_penalty` + §10.1 target ("≤ 24% fallback firing rate") — if measurements miss, recalibrate weights before flipping any rollout flag |
| TR copy seeds in `lived_scene` / `atoms` reintroduce the "olması de" / "Bazen de." class of defects | §9.4 scan extends the existing P0 connector audit over v0.9b output; the §3 of v0.9a.3 P0 fix (vowel-harmonized `de`/`da` particle, connector-aware `_normalize_packet_field_text`) already catches mid-pipeline emissions |
| A composed candidate sneaks into `profile_public.composed_detail_cards` because the renderer signature matcher widens too aggressively in v0.9b.1 | v0.9b.0 ships without renderer changes; the renderer's variant allowlist explicitly stays at the 3-chart Phase B set; v0.9b.1 is a separate audit |
| Existing accepted goldens drift because v0.9b composed candidates change the cluster plan's `composed_candidate_public_eligibility_distribution` ledger | Goldens are snapshotted on `_projection_surface_snapshot` which strips `traceability`; the ledger lives under traceability and is not in the snapshot |
| Rollout flags multiply and developers forget the cache-key add | §9.5 test fails fast on omission; the v0.9a.3 audit established this as a required check |

---

## Non-Goals (restated)

- No public_main routing in v0.9b.0.
- No public_support routing in v0.9b.0.
- No renderer changes.
- No registry edits.
- No selection-scoring changes.
- No mobile work.
- No changes to existing accepted goldens.
- No changes to existing flag behaviors.

---

## Summary

v0.9b.0 adds two compositional families
(`relationship_route`, `moon_signature`) behind three new
default-`false` flags. Their candidates appear in trace and in the
cluster plan's debug ledger; they never reach any public surface.
The eight relationship subtypes (`trust_steadiness`,
`attraction_warmth`, `boundary_conflict`, `intimacy_depth`,
`emotional_need_affection`, `hidden_private_love`, `freedom_space`,
`wound_to_gift`) and six moon subtypes (`emotional_rhythm`,
`home_inner_security`, `daily_sensitivity`, `creative_emotional_expression`,
`intimacy_depth`, `private_emotional_processing`) line up with the
v0.9a career_route construction shape so the same selection, scoring,
and dedup paths apply unchanged. Renderer, registry, and public
output stay frozen. Sanliurfa 1988 is explicitly added as the next
relationship/moon calibration chart: Moon already resolves in the
expected `private_emotional_processing` direction, while the
relationship family currently misses a Mars-led Aries-DSC activation
signature that should inform the next subtype/rule adjustment.
`mexico_city_1988_08_31` is retained alongside it as the mixed
Moon-attachment + Mars-activation edge case for the next ownership
calibration pass, still under debug-only constraints.

Phase C mobile work and renderer allowlist widening explicitly remain
out of scope. v0.9b.1 (renderer allowlist) and v0.9b.2 (public_support
routing) are separate, later approvals, each with its own audit.
