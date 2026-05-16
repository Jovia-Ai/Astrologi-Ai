# v0.9c.0 Plan — Debug-Only Mercury Family for `mercury_signature`

> Planning artifact. **No code, runtime, registry, renderer, scoring,
> selection, or public-output changes are made by this document.**
> This plan defines a narrow debug-only grammar slice for Mercury-led
> mental/speech signatures.

## Purpose

The v0.9c.0 cut introduces a new composed-semantic family,
`mercury_signature`, in **debug-only** mode.

Its purpose is narrow:

- capture strong Mercury-led thought / speech / decision-language
  signatures that are currently under-read by generic `mind`
  fallback
- add semantic trace coverage without changing any current public
  lane
- establish clean ownership boundaries between `identity_route`,
  `mercury_signature`, and `career_route`

This is **not** a rollout plan. It is a debug-family plan whose first
job is to improve semantic trace completeness on Mercury-heavy charts,
especially `1988-10-10 05:30 Sanliurfa, TR`.

---

## 1. Why Mercury Needs Its Own Family

The current system already sees parts of the Mercury-led pattern, but
it does so in fragmented ways:

- `identity_route` can correctly absorb `ASC + Sun/Mercury 1H` when
  the chart's self-presentation is the strongest signal
- exact registry packets such as speech / structured-originality
  packets can sometimes capture a slice of the pattern
- `mind_mind_system` can hold the public owner slot even when the
  chart's actual speech/mental style is more specific than a generic
  mind fallback

This leaves a real gap:

- charts can visibly carry a Mercury-led speech / decision / mental
  processing signature
- but that signature may remain under-specified at the composed level
- and can be misread as generic intelligence, generic mind activity,
  or a side-note under identity

`mercury_signature` exists to solve that middle layer:

- more specific than `mind_mind_system`
- narrower than `identity_route`
- not yet a public-facing lane

The family should read **how the mind forms, organizes, breaks, and
delivers thought**, not who the person is socially, and not how the
person is publicly positioned.

---

## 2. Ownership Boundaries

The family is only safe if ownership is explicit.

### 2.1 `identity_route` owns persona / self-presentation

`identity_route` remains the owner when the chart is primarily about:

- persona
- visible self-presentation
- embodied selfhood
- how the person appears, carries themselves, or is immediately read

Examples:

- ASC-led identity signatures
- Sun in 1H identity-spine signatures
- chart-ruler-driven self-construction signatures

Mercury can contribute to this layer when it sits close to identity
anchors, but Mercury does **not** take ownership merely because the
person's identity is articulate.

### 2.2 `mercury_signature` owns thought / speech / decision language / mental processing

`mercury_signature` owns:

- thought formation
- speech pattern
- decision language
- mental pacing
- structured vs disruptive cognition
- how the person links, edits, sharpens, organizes, or breaks
  thought

It should answer:

- how the person thinks
- how the sentence gets formed
- how the mind moves under pressure
- how speech and mental processing become distinctive

It should **not** answer:

- who the person is at core identity level
- how the person is socially perceived in a broad persona sense
- what their public role is

### 2.3 `career_route` owns public role / professional voice

`career_route` remains the owner when the chart is primarily about:

- public role
- visible professional contribution
- social/career positioning
- public-facing strategy, authority, or recognized voice

Mercury can be part of the evidence stack for `career_route`, but
Mercury does not own the public role merely because the chart shows a
strong mental style.

Important boundary:

- **MC Cancer square Sun/Mercury is not solved here.**
  That belongs to a future `career_route` expansion around
  public-role vs identity-voice tension.

Also explicitly out of scope:

- **Chiron Cancer 9H / Neptune opposition Chiron is not solved here.**
  That belongs to a future belief / `9H` sensitivity family.

---

## 3. Initial Subtypes

v0.9c.0 opens only **two** initial Mercury subtypes.

### 3.1 `speech_identity_spine`

Core meaning:

- speech is close to selfhood
- the person shows themselves through wording, tone, phrasing, and
  verbal stance
- the sentence itself becomes a carrier of identity

This subtype is for charts where Mercury is closely tied to the
identity axis, but where the meaningful read is still specifically
about language / tone / wording rather than broad persona.

Semantic target example:

> Kendini çoğu zaman ne söylediğin kadar, o cümleyi hangi tonla
> kurduğun üzerinden de gösterirsin.

### 3.2 `structured_disruptive_mind`

Core meaning:

- the mind wants structure, correctness, weight, and placement
- but also carries interruption, re-linking, originality, or a sudden
  break from the expected thought-line
- thought can be both disciplined and disruptive

This subtype is for charts where Mercury is materially shaped by
Saturn/Uranus/3H-style signal combinations and produces a distinct
mental rhythm rather than only generic intelligence.

Semantic target example:

> Zihnin bir yandan cümleyi doğru yere oturtmak isterken, başka bir
> yandan alışılmış bağlantıyı bir anda kırabilir.

---

## 4. Detection Rules

The v0.9c.0 family should behave like the other composed families:

- evidence-led
- subtype-bounded
- debug-only
- conservative on weak charts

### 4.1 Family-level gate

A `mercury_signature` candidate should require all of the following:

- `source_type == "composed_semantic"`
- Mercury is a meaningful anchor in the chart, not a weak bystander
- at least one of these routes is meaningfully active:
  - Mercury angularity / identity proximity
  - `3H/9H` axis participation
  - strong Mercury aspect pattern
  - ruler-route support tied to Mercury-style cognition
- chart facts match
- subtype is not a default fallback
- candidate remains `debug_only`

### 4.2 `speech_identity_spine` detection

Preferred evidence stack:

- Mercury in `1H`, conjunct Ascendant, conjunct Sun, or otherwise
  tightly identity-bound
- Mercury visibly linked to self-expression rather than only abstract
  thought
- speech/wording/tone is the right read, not just "persona"

Support signals:

- Mercury angular
- Sun/Mercury proximity
- Ascendant or chart-ruler route reinforcing expressive identity
- `3H` signal as secondary support, not required

Rejection rules:

- do not emit if the chart is mostly an `identity_route` case with no
  real speech-pattern distinctiveness
- do not emit if the evidence only supports generic cleverness or
  intelligence

### 4.3 `structured_disruptive_mind` detection

Preferred evidence stack:

- Mercury materially involved in a `3H`/speech/mental-processing line
- Saturn contributes structure, weight, discipline, or measured
  framing
- Uranus contributes breakage, jump, disruption, originality, or
  non-linear association

Strong examples of evidence:

- Mercury with `Saturn` and/or `Uranus`
- Mercury linked into `3H`
- Saturn in `3H`
- Uranian contact shaping Mercury rhythm
- ruler-route support that makes the speech/decision line chart-wide

Support signals:

- Mercury in `1H`
- Sun/Mercury identity proximity
- `3H/9H` axis participation
- exact speech / structured-originality packet echoes already present

Rejection rules:

- do not emit for charts that are only "structured"
- do not emit for charts that are only "original"
- do not emit when the pattern is better owned by future belief /
  worldview grammar rather than thought/speech formation

---

## 5. Confidence Scoring

The family should score conservatively at launch.

### 5.1 Scoring principles

Confidence should rise when:

- Mercury is angular or identity-close
- Mercury has multiple reinforcing anchors
- the `3H/9H` axis is genuinely involved
- Saturn/Uranus support is not incidental
- the chart carries a clear thought/speech signature that existing
  exact packets already partially echo

Confidence should fall when:

- Mercury is present but diffuse
- the signal is mostly identity and only weakly mental/speech-based
- the signal is mostly public-role and better owned by career
- the pattern would require belief / worldview grammar to read
  truthfully

### 5.2 Suggested confidence bands

- `>= 0.80`
  - strong, chart-defining Mercury line
  - safe candidate for future calibration fixtures
- `0.70 - 0.79`
  - meaningful Mercury pattern
  - probably valid but still needs comparative chart review
- `0.60 - 0.69`
  - debug-visible, weaker or mixed ownership
  - useful for calibration but not rollout-grade
- `< 0.60`
  - should not emit

### 5.3 Subtype-specific expectation

At launch:

- `speech_identity_spine` should generally need stronger identity
  proximity than `structured_disruptive_mind`
- `structured_disruptive_mind` should generally need stronger
  multi-signal Mercury + Saturn/Uranus structure than simple Mercury
  angularity

---

## 6. Sanliurfa 1988 Expected Behavior

Target chart:

- `1988-10-10 05:30 Sanliurfa, TR`

This chart is the lead Mercury calibration fixture for v0.9c.0.

### 6.1 What remains unchanged

- `relationship_route.direct_relational_activation` remains unchanged
- `moon_signature.private_emotional_processing` remains unchanged
- `identity_route` remains unchanged
- public output remains unchanged

This is essential. The Mercury family must add coverage without
rewriting the already-accepted relationship / Moon / identity reads.

### 6.2 What should newly appear

The expected new debug-only candidate is:

- `mercury_signature.structured_disruptive_mind`

Why this chart is the right fixture:

- Mercury is identity-close
- the chart already shows `Libra ASC + Sun/Mercury 1H`
- the audit gap is specifically `Mercury 1H + Saturn/Uranus 3H`
- the missing read is not persona, not relationship, not Moon, but
  speech/mental processing

### 6.3 What this plan does not try to solve on Sanliurfa

Still out of scope:

- `MC Cancer square Sun/Mercury`
  - future `career_route` expansion
- `Chiron Cancer 9H / Neptune opposition Chiron`
  - future belief / `9H` sensitivity family

So Sanliurfa's expected debug-layer outcome after v0.9c.0 is:

- relationship accepted
- Moon accepted
- identity unchanged
- Mercury newly visible
- public no-op preserved

---

## 7. Non-Goals

- No code changes in this document
- No runtime changes
- No registry changes
- No renderer changes
- No scoring changes are executed by this plan
- No selection changes
- No public output changes
- No detail-lane rollout
- No public-main rollout
- No solution for `MC Cancer square Sun/Mercury`
- No solution for `Chiron Cancer 9H / Neptune opposition Chiron`
- No attempt to solve all Mercury-shaped charts in one cut

---

## 8. Future Mercury Subtypes — Explicitly Out of Scope

The following Mercury-adjacent subtypes are **not** part of v0.9c.0:

- `deep_mind_pressure`
- `public_voice`
- `social_intuition_mind`
- `belief_builder`
- `private_analytical_mind`

Why they are excluded:

- they broaden the family too quickly
- some belong closer to `career_route`
- some belong closer to future `9H` / worldview grammar
- some require a larger calibration fixture before safe subtype
  boundaries can be written

v0.9c.0 must prove that the family can hold two clean subtypes first.

---

## 9. Tests

The test suite should mirror the other composed-family debug launches.

### 9.1 Candidate-generation tests

- Mercury family flag off -> no `mercury_signature` candidate
- family flag on + strong Mercury evidence -> candidate appears
- weak Mercury charts do not emit
- identity-only charts do not incorrectly emit Mercury candidates
- public output stays byte-identical with Mercury debug flag on/off

### 9.2 Subtype tests

For `speech_identity_spine`:

- emits on charts with strong identity-bound Mercury speech signal
- rejects charts where Mercury is identity-adjacent but not actually a
  speech/decision-language owner

For `structured_disruptive_mind`:

- emits on charts with real Mercury + Saturn/Uranus / `3H` structure
- rejects charts that are only structured
- rejects charts that are only unusual/original

### 9.3 Ownership-boundary tests

- `identity_route` remains present when identity signal is primary
- `mercury_signature` does not suppress `identity_route`
- `career_route` remains the owner for public-role / professional
  voice patterns
- Sanliurfa specifically preserves existing accepted relationship and
  Moon debug outcomes

### 9.4 Sanliurfa fixture tests

- `relationship_route.direct_relational_activation` remains present
- `moon_signature.private_emotional_processing` remains present
- `identity_route` remains present
- `mercury_signature.structured_disruptive_mind` newly appears
- no public surface changes

### 9.5 Non-leak tests

Across all visible public surfaces:

- no `composed_mercury_signature_v0_9c` item leaks into public blocks
- no leak into `detail_cards`
- no leak into `profile_public.composed_detail_cards`
- no leak into `profile_v8_projection_v1`

---

## 10. Rollout Plan

### 10.1 `v0.9c.0` — debug-only launch

Ship only:

- family-level candidate generation
- two subtypes
- trace/debug visibility
- no renderer path
- no public lane

Acceptance:

- debug trace quality improves on Mercury-heavy charts
- Sanliurfa behaves as expected
- public no-op holds

### 10.2 `v0.9c.0.1` — calibration pass

After initial debug-only launch:

- review false positives
- review subtype spread on a broader fixture slice
- compare Mercury family ownership against identity/career overlap
- confirm that subtype definitions are not absorbing unrelated charts

Primary questions:

- Is `speech_identity_spine` too close to `identity_route`?
- Is `structured_disruptive_mind` too broad or too narrow?
- Are there charts where Mercury should stay discovery-only rather
  than composed?

### 10.3 No detail/public rollout until later

There should be **no** detail/public rollout in this phase.

A future Mercury detail lane should only be considered after:

- subtype boundaries are stable
- ownership conflicts are audited
- enough fixtures exist for per-subtype calibration
- copy semantics are authored family-by-family

Until then, Mercury remains a debug-only semantic family.

---

## Summary

`v0.9c.0` adds `mercury_signature` as a narrow debug-only composed
family with two initial subtypes:

- `speech_identity_spine`
- `structured_disruptive_mind`

The family exists to capture thought / speech / decision-language
signatures that are currently broader than exact packets but narrower
than generic `mind` fallback, while preserving explicit ownership
boundaries:

- `identity_route` owns persona / self-presentation
- `mercury_signature` owns thought, speech, decision language, mental
  processing
- `career_route` owns public role / professional voice

Sanliurfa is the lead calibration chart. Its relationship, Moon, and
identity readings stay unchanged; the new expected debug-only addition
is `mercury_signature.structured_disruptive_mind`. No public rollout
is part of this plan.
