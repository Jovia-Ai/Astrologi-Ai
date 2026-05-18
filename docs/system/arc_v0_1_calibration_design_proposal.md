# ARC v0.1 — Calibration Design Proposal

## 1. Objective

The goal is not to maximize salience alignment blindly.

The goal is to:
- reduce false emphasis
- improve secondary visibility
- preserve extraction stability
- preserve anti-false-spine behavior
- avoid suppressing genuinely personalized signatures

This is a design proposal, not a patch.

## 2. Corpus State

Current state:
- `n_scored = 16`
- extraction mean/worst = `1.000 / 1.000`
- salience mean/worst = `0.906 / 0.500`
- `false_emphasis = 11`
- `framing deferred = 46`
- unsupported anchor types = `["final_dispositor"]`

State:
- extraction is stable
- salience is provisional and uncalibrated
- calibration design can begin
- final coefficients are not yet authorized

## 3. Failure Family Map

### 3.1 Public / MC generational inflation

Description:
- When a real public/career owner exists, a generational `10H` or public-route participant can still become a false headline.

Evidence charts:
- `1980 Tokyo`: Neptune `10H` false emphasis
- `1989 Istanbul`: exact `Saturn-Neptune` public-route contact false emphasis

Failure type:
- `false_emphasis`

Likely mechanism:
- exact public-route participation
- outer/generational inheritance
- weak containment by owner priority

Patch readiness:
- medium

Regression risk:
- suppressing genuinely personalized outer signatures that are angular, owner-linked, or repeatedly personalized

### 3.2 Exact generational aspect inflation

Description:
- Exactness can currently make generational aspect participation read like a headline even when the structural owner is elsewhere.

Evidence charts:
- `1985 Istanbul`: `Neptune-Pluto` exact/tight generational aspect false emphasis
- related: `1989 Istanbul` `Saturn-Neptune` public-route contact

Failure type:
- `false_emphasis`

Likely mechanism:
- `tight_aspect` member-max
- exactness treated as undifferentiated loudness

Patch readiness:
- medium

Regression risk:
- muting real exact aspects involving luminaries, chart rulers, or angular personal planets

### 3.3 Outer stellium / member inheritance inflation

Description:
- A generational outer can inherit too much loudness through stellium or house-concentration membership without enough independent personalization.

Evidence charts:
- `2007 Helsinki`: `Uranus/Neptune` inside `12H` stellium false emphasis

Failure type:
- `false_emphasis`

Likely mechanism:
- `house_concentration` member-max
- stellium membership inheritance

Patch readiness:
- medium

Regression risk:
- erasing charts where an outer is genuinely personalized

### 3.4 Exact pressure vs true structural owner

Description:
- Exact pressure lines can become louder than they should when a denser structural owner is already clearly present.

Evidence charts:
- `1994 Helsinki`: `Mars-Neptune` / `Mercury-Mars` pressure false emphasis while true `6H` structure held
- `1982 Nairobi`: `Moon-Uranus` exact soft aspect false emphasis against stronger pressure spine

Failure type:
- `false_emphasis`

Likely mechanism:
- tightness overpowering ownership context
- exact soft/hard aspect treated too similarly

Patch readiness:
- medium-low

Regression risk:
- understating legitimately central hard-aspect charts or T-square-like structures

### 3.5 Lone angular debility pressure

Description:
- A single angular debilitated planet can become too loud and act like the chart’s main wound/headline even when the true structure lies elsewhere.

Evidence charts:
- `2002 Helsinki`: angular `Venus fall` false emphasis
- `1994 Helsinki`: angular `Mars fall` false emphasis

Failure type:
- `false_emphasis`

Likely mechanism:
- angularity + debility loudness
- insufficient owner-hierarchy containment

Patch readiness:
- medium

Regression risk:
- demoting charts where angular debility is truly defining

### 3.6 Debility-heavy secondary strain under-visibility

Description:
- After a primary debility route is recognized, secondary debilitated strain anchors can remain too low, especially without angular support.

Evidence charts:
- `1968 Buenos Aires`: `Saturn` rank-2 background
- `1997 Helsinki`: `Saturn` rank-3 background

Failure type:
- `under_visibility`

Likely mechanism:
- affliction-cluster support favors the main route but does not preserve secondary burden nodes
- lack of angular support sinks secondary strain too low

Patch readiness:
- low-medium

Regression risk:
- making every debilitated planet loud and overcorrecting affliction

### 3.7 Distributed / no-dominant secondary visibility

Description:
- The system can avoid fabricating a false spine, yet still let real secondary centres become too dim.

Evidence charts:
- `1975 Helsinki`: no false spine, but `Mars/Jupiter` too dim
- `2010 Sydney`: no false spine, but `Mercury/Venus/Jupiter-Uranus` too dim

Failure type:
- `under_visibility`

Likely mechanism:
- absolute thresholds protect against false spine but under-represent secondary centers
- lack of a secondary visibility floor

Patch readiness:
- low-medium

Regression risk:
- reintroducing false-spine behavior through relative or compensatory visibility logic

### 3.8 Gift / dignified steering under-promotion

Description:
- In a genuinely multi-centred gift chart, a rank-1 dignified steering owner may remain `strong` instead of `defining` without any false emphasis elsewhere.

Evidence charts:
- `2009 Nairobi`: `Mercury` double-ruler domicile rank-1 scored `strong`, not `defining`

Failure type:
- `salience_miss`

Likely mechanism:
- rank semantics
- pressure-shaped loudness rewarded more than gift-shaped loudness

Patch readiness:
- low-medium

Regression risk:
- forcing every dignified ruler to `defining` in genuinely balanced charts

## 4. Candidate Calibration Levers

Do not implement. Design only.

### 4.1 Outer / generational participation gate

Current dry-run status:
- original Dry-run A was rejected as too blunt
- revised Dry-run A2 is accepted as the candidate lever
- A2 reduced `false_emphasis` from `11 -> 4`
- A2 restored Dry-run A collateral damage:
- `1962 Nairobi` Mars trine Pluto restored
- `2007 Helsinki` Jupiter owner-route restored
- A2 created no new canonical regression
- A2 intentionally leaves `1985` outer-outer exact aspect inflation unresolved
- if continuing to Dry-run B, stack on A2, not on the original A implementation

What it changes conceptually:
- makes outer/generational promotion conditional on real personalization, rather than letting exactness or membership alone push them into owner-like territory

Which family it targets:
- public / MC generational inflation
- exact generational aspect inflation
- outer stellium/member inheritance inflation

Expected positive effect:
- fewer false outer headlines
- better separation between contextual outer participation and real owner status

Expected negative risk:
- under-reading genuinely personalized outer signatures

Charts expected to improve:
- `1980`
- `1989`
- `2007`

Charts that must not regress:
- any chart where an outer is angular, owner-linked, luminary-linked, or repeatedly personalized

Pass 1 or defer?
- Pass 1

Open scope after A2:
- `1985` remains as the unresolved outer-outer exact aspect case
- this should be handled by the next dry-run layer, not by reverting to the blunter original gate

### 4.2 Contextual tightness cap

What it changes conceptually:
- stops exactness from acting as a universal loudness escalator by modulating it through context

Which family it targets:
- exact generational aspect inflation
- exact pressure vs true structural owner
- exact soft-aspect inflation

Expected positive effect:
- fewer exact-aspect false headlines when a clearer owner already exists

Expected negative risk:
- muting genuinely central exact hard aspects

Charts expected to improve:
- `1982`
- `1985`
- `1989`
- `1994`

Charts that must not regress:
- legitimately aspect-driven charts, especially hard-pressure structures

Pass 1 or defer?
- Pass 1

### 4.3 Structural owner priority

What it changes conceptually:
- explicitly privileges a clearly established structural owner over exact secondary aspects when deciding effective headline loudness

Which family it targets:
- exact pressure vs true structural owner
- public-route generational inflation

Expected positive effect:
- keeps chart-ruler / MC-ruler / luminary / concentration owners from being displaced by secondary exact signals

Expected negative risk:
- under-reading legitimate aspect-driven charts where the aspect really is the owner

Charts expected to improve:
- `1980`
- `1989`
- `1994`

Charts that must not regress:
- cases where aspect structure is itself the real owner, not merely a modifier

Pass 1 or defer?
- Pass 1

### 4.4 Lone angular debility containment

What it changes conceptually:
- treats angular debility as loud but not automatically owner-level unless it has additional support

Which family it targets:
- lone angular debility pressure

Expected positive effect:
- fewer false wounded-headline results from a single angular fall/detriment point

Expected negative risk:
- demoting charts where angular debility really is central

Charts expected to improve:
- `2002`
- `1994`

Charts that must not regress:
- charts where angular debility is also ruler-linked, luminary-linked, repeated, or domain-concentrated

Pass 1 or defer?
- Pass 1, but more cautiously than 4.1–4.3

### 4.5 Secondary visibility floor

What it changes conceptually:
- gives real secondary centres a minimum visibility in charts that are genuinely multi-centred or pressure-distributed

Which family it targets:
- debility-heavy secondary strain under-visibility
- distributed / no-dominant secondary visibility

Expected positive effect:
- reduces dim secondary real centres without relying on false owner promotion

Expected negative risk:
- reintroducing false-spine through disguised relative-threshold behavior

Charts expected to improve:
- `1968`
- `1975`
- `1997`
- `2010`

Charts that must not regress:
- `1973`
- `1975`
- `2010`

Pass 1 or defer?
- defer

### 4.6 Rank semantics refinement

What it changes conceptually:
- keeps the current rank convention but allows a narrow exception for close-rank, dual-gift, explicitly multi-centred charts

Which family it targets:
- gift / dignified steering under-promotion

Expected positive effect:
- avoids false negative salience misses where a rank-1 `strong` is astrologically acceptable

Expected negative risk:
- weakening rank-1 expectation too much and making evaluation inconsistent

Charts expected to improve:
- `2009`

Charts that must not regress:
- charts where rank-1 truly should be `defining`

Pass 1 or defer?
- defer

### 4.7 Hybrid absolute + relative tiering

What it changes conceptually:
- combines an absolute floor, a relative ceiling, and a secondary visibility floor to manage both saturation and dimness

Which family it targets:
- absolute vs chart-relative tier thresholds
- distributed secondary visibility

Expected positive effect:
- may solve both too-many-defining and too-dim-secondary problems in one architecture

Expected negative risk:
- highest false-spine risk if implemented naively

Charts expected to improve:
- `1975`
- `2010`

Charts that must not regress:
- `1973`
- `1975`
- `2010`

Pass 1 or defer?
- defer

## 5. Minimal Viable Calibration Pass

Recommended first safe calibration slice:
- false-emphasis containment first, not secondary visibility

Reason:
- false emphasis is more product-dangerous because it makes the wrong thing too loud
- secondary under-visibility is important but riskier to fix because visibility floors can create false spines

Suggested Pass 1:
- outer / generational participation gate using the A2 endpoint-aware variant, not the original A implementation
- contextual tightness cap
- structural owner priority

Explicitly defer:
- secondary visibility floor
- hybrid relative tiering
- rank semantics exception

Reason for deferral:
- these are more likely to affect no-dominant and multi-centred charts
- they need more careful design because the regression risk is architecturally higher

Immediate next dry-run candidates after A2:
- lone angular debility pressure
- exact pressure vs true structural owner
- outer-outer exact aspect inflation

## 6. Regression Guard Suite

Before any calibration patch, require:

- extraction mean/worst remains `1.000 / 1.000`
- canonical 4 references still pass
- `1973` no-dominant does not fabricate a spine
- `1975` no-dominant does not fabricate a spine
- `2010` distributed chart preserves secondary centres without creating false owner
- `1972` angular+afflicted does not lose valid multi-loaded structure
- `1985` relationship-heavy does not become relationship-as-whole-identity
- `2007` 12H-heavy does not become 12H-as-whole-identity
- outer/generational penalties do not suppress genuinely personalized outer signatures
- secondary visibility fixes do not become relative-threshold false-spine

## 7. Dry-Run Reporting Contract

Any future calibration experiment must report:

- extraction mean/worst
- salience mean/worst
- false_emphasis count
- framing deferred count
- under_visibility count
- unsupported anchors
- per-family deltas
- charts improved
- charts harmed
- regression guard pass/fail
- unresolved tradeoffs

Dry-run should compare baseline vs proposed calibration.

## 8. Decision Gates

### Implement patch

Allowed only if:
- extraction unchanged
- false_emphasis reduces meaningfully
- no new false spine
- canonical 4 still pass
- no critical regression in personalized outer signatures

### Revise design

If:
- target family improves but regression appears
- false emphasis moves to another family
- no-dominant guards weaken

Observed example:
- original Dry-run A belongs here; its direction was accepted, but it was too blunt and caused canonical collateral damage

### Collect another batch

If:
- evidence remains too sparse for a family
- tradeoff cannot be resolved from current 16 golds
- personalized outer counterexamples are missing

### Abandon lever

If:
- lever improves one chart but harms multiple guards
- lever is not astrologically principled
- lever requires too many exceptions

## 9. Final Statement

Batch-3 moves ARC from corpus accumulation into calibration readiness. This document proposes calibration design only. It does not authorize immediate coefficient changes.

## 10. Ship Gate & Product-Validation Checkpoint

Added after a process review: the calibration loop has no defined stop
condition, and the salience scorer (a proxy for "the user feels seen")
has never been validated against the actual product surface. Without a
gate this becomes an unbounded research treadmill — technically
flawless, product-stalled. This section bounds it.

### 10.1 The risk being closed

- Salience is non-gating and has never touched public output. ~30
  iterations of rigorous internal work have not moved the
  product-facing needle (voice, slide, "this sees me").
- Each batch surfaces new families → new design → new dry-run, with no
  "good enough, ship it" criterion. The loop can run forever.
- A proxy optimized for many turns without validating it against the
  real felt experience can silently diverge from the product goal.

### 10.2 Pass-1 Ship Gate (the stop condition)

Calibration Pass-1 is **bounded to reaching this gate**, not to
"keep improving". Pass-1 is shippable-behind-voice when ALL hold:

1. Regression guard suite (§6) fully green.
2. Extraction mean/worst unchanged at 1.000 / 1.000.
3. `false_emphasis` reduced to the Pass-1 dry-run target across the
   16-gold + canonical set. *(The exact integer is set by the
   calibration owner from the Pass-1 dry-run result — NOT pre-set here,
   to avoid premature/curve-fit calibration. The gate is the existence
   of a committed target + meeting it, not a number invented now.)*
4. No new false-spine on the no-dominant guards (1973, 1975, 2010).
5. The canonical 4 + the relationship/12H monopolization guards
   (1985, 2007) still pass their pre-registered criteria.
6. **Product-Validation Checkpoint (10.3) passes.**

Deferred levers (5.5 secondary-visibility floor, 5.6 rank exception,
5.7 hybrid tiering) and any newly-surfaced family are **explicitly NOT
gate conditions**. The gate is a *ship* decision, not a *perfection*
decision (see 10.4).

### 10.3 Product-Validation Checkpoint (proxy ↔ felt experience)

After Pass-1 dry-run passes 10.2.1–10.2.5, before declaring the gate
met: take **one** chart (recommended: a canonical reference whose gold
we trust, e.g. 1962 Nairobi or 1985), run it end-to-end through the
actual product path — salience → voice/slide rendering — behind a flag,
NOT to public users.

Then a human (astrologer) answers, blind to the salience numbers:

- Does the rendered reading lead with what the gold says it should?
- Does it feel "this sees me" — specific, not generic, not a confident
  wrong reading?
- Did a must_not (framing) cliché leak into the voiced output?
- Does a non-dominant / multi-centred chart still read as multi-centred
  in the actual prose, or did voice collapse it to a false spine?

If the scorer says ~0.95 but the voiced reading feels generic or wrong,
**the proxy has diverged and the gate is NOT met** — regardless of the
number. This is the one check that catches scorer-vs-product drift; it
is mandatory, not optional.

### 10.4 Anti-infinite-loop rule

Once the Pass-1 gate (10.2) is met:

- New calibration families surfaced afterward go to a **post-ship
  backlog**, they do NOT reopen the gate.
- Further calibration is a *separate, scheduled* pass with its own
  gate, not a continuous treadmill.
- The default after gate = wire Pass-1 salience behind the voice/surface
  layer (flagged) and let real product iteration, not the scorer alone,
  drive the next priorities.

### 10.5 Thin parallel product thread

To keep the project anchored to "user feels seen" and not "scorer
number", a minimal product thread runs in parallel with calibration:
one chart family carried through the voice/slide path so there is
always a tangible felt-experience artifact to check the substrate
against. This is the structural guard against the calibration-treadmill
failure mode.

### 10.6 Decision

- Corpus sufficient for Calibration Readiness Review: **yes**.
- Calibration Pass-1 now **bounded by 10.2**, not open-ended.
- Ship gate includes a **mandatory product-felt-experience check**
  (10.3), not just scorer metrics.
- Post-gate new families = backlog, not blockers (10.4).

This converts the calibration work from an unbounded research loop into
a bounded, product-anchored pass with a defined exit and a proxy↔product
validation.
