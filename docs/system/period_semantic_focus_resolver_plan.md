# Period Semantic Focus Resolver Plan

Date: 2026-05-04  
Scope: design-only, no runtime implementation yet  
Goal: define how the system should choose which meaning of a placement/sign/aspect is active in a period, using existing code and audits without changing live behavior yet

## Executive Summary

We are not implementing `LifeChapterDetector` yet.  
We are not implementing profection, progression, solar-return-led period ownership, Daily changes, or Best Times work yet.

This plan is narrower:

```text
Build the design for a PeriodSemanticFocusResolver facade,
then use handcrafted validation to test whether semantic-focus-aware
period writing improves “This sees me”.
```

The key separation is:

```text
PeriodSemanticFocusResolver = what meaning should be read?
PeriodVoicePolicy          = how should that selected meaning be said?
AstrologNarrativeEngine    = how does that become final SHOU prose?
```

This plan assumes:

- period remains the active surface
- life-chapter awareness is limited and optional for handcrafted validation only
- runtime behavior stays unchanged until validation proves the layer is worth building

---

## 1. Existing Inputs Already in Repo

The resolver does not need to invent all inputs from scratch. Most inputs already exist, but are fragmented.

### 1.1 Canonical period domain inputs

[canonical_natal_activation.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/canonical_natal_activation.py:245) already gives:

- `hook_id`
- `target_node_id`
- `primary_domain`
- `theme`
- `prefix`
- `spine_lines`
- `matched_event_ids`

This is a strong broad-domain starter, but it does not choose final meaning.

### 1.2 Natal relevance inputs

[natal_promise.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/natal_promise.py:74) already gives:

- event-to-natal relevance
- drivers
- connected points
- verdict / gate
- promise evidence

This is one of the most important future meaning-governors.

### 1.3 Placement/context inputs

[hybrid_context.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/hybrid_context.py:65) already computes:

- target planet
- natal house
- sign
- dispositor
- ruled houses
- natal aspects
- connected points
- derived context / motifs

This is the best current raw source for “which possible meaning palette is available?”

### 1.4 Explainability inputs

[chain_explainer_tr.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/chain_explainer_tr.py:6) gives angle-ruler technical explanation.

This is not a meaning owner, but it can later help fill `evidence[]`.

### 1.5 Scene inputs

[manifestation_context_policy.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/manifestation_context_policy.py:87) already chooses:

- `life_scene`
- primary house scene
- how the motion lands

This should fill `manifestation_scene`, not decide core meaning.

### 1.6 Voice framing inputs

[period_voice_policy.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/period_voice_policy.py:71) already chooses:

- `event_nature`
- `meaning_intent`
- `rhetorical_frame`
- `valence_mode`
- `intensity_mode`

This is downstream from semantic focus, not upstream.

### 1.7 Aspect texture inputs

[aspect_valence_mapper.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/aspect_valence_mapper.py:1) now gives:

- pair-aware valence bias
- intensity bias
- dense integration vs tension distinction

This should remain texture, not final meaning owner.

### 1.8 Canonical natal ontology inputs

Canonical natal meaning graph in [meaning_graph.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/astro_os/natal/meaning_graph.py:218) already gives:

- activation hooks
- target nodes
- promise-oriented spine candidates

This is the right place to source semantic grounding, but not yet the full resolver.

### 1.9 Period cluster inputs

Current period selection and aggregation already give:

- selected event IDs from [selection.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/selection.py:37)
- root-cause heuristics in [text_quality_tr.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/text_quality_tr.py:2131)
- track aggregation in [deep_archetype_engine.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/deep_archetype_engine.py:784)

These are useful for support-cluster logic, even though they are not yet explicit semantic focus owners.

---

## 2. Module Classification

| Module | Classification | Why |
|---|---|---|
| [canonical_natal_activation.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/canonical_natal_activation.py:245) | `semantic_focus_candidate` | selects broad domain/hook/spine, but not final selected meaning |
| [natal_promise.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/natal_promise.py:74) | `source_calculator` | computes relevance and promise evidence |
| [hybrid_context.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/hybrid_context.py:65) | `source_calculator` | computes sign/house/dispositor/rulership/aspect inputs |
| [chain_explainer_tr.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/chain_explainer_tr.py:6) | `copy_enrichment` | explainability/copy support only |
| [manifestation_context_policy.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/manifestation_context_policy.py:87) | `source_calculator` | scene selector only |
| [period_voice_policy.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/period_voice_policy.py:71) | `semantic_focus_candidate` | currently forced to answer some meaning-adjacent questions, but should be downstream |
| [aspect_valence_mapper.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/aspect_valence_mapper.py:1) | `source_calculator` | aspect texture and semantic direction bias |
| [meaning_graph.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/astro_os/natal/meaning_graph.py:218) | `source_calculator` | canonical natal hook ontology |
| current period spine | `semantic_focus_candidate` | domain-level focus, not final meaning |
| [astrolog_narrative_engine.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/astrolog_narrative_engine.py:462) | `renderer` | final prose only |
| [text_quality_tr.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/text_quality_tr.py:2131) | `legacy_compat` | still live, but transitional broad heuristics and renderer baggage |
| debug rails / sample pack helpers | `debug_only` | validation and tracing support only |

---

## 3. Proposed Facade

Proposed future file:

```text
backend/app/transit/narrative/period_semantic_focus_resolver.py
```

This file should **not** be built yet in runtime.  
In the next PR, it should begin as a facade around existing calculators.

Core idea:

```text
Do not write a second independent intelligence.
Wrap and join the existing intelligence.
```

Facade inputs should come from:

- selected period events
- canonical period spine
- canonical natal state / activation hooks
- natal promise
- hybrid context
- manifestation context
- aspect valence/intensity mapping
- root-cause/support cluster hints

Facade outputs should be a single explicit object:

```text
PeriodSemanticFocus
```

---

## 4. Proposed Contract

```ts
interface PeriodSemanticFocus {
  focus_id: string;

  activated_factor: {
    type: "planet" | "angle" | "house" | "ruler" | "aspect_pattern" | "promise";
    name: string;
  };

  primary_domain: string;
  secondary_domains: string[];

  selected_meaning: string;
  meaning_family:
    | "identity"
    | "emotional_security"
    | "home_family"
    | "work_rhythm"
    | "relationship"
    | "career_visibility"
    | "money_self_worth"
    | "communication"
    | "creative_expression"
    | "body_rhythm"
    | "inner_work";

  manifestation_scene: string;

  why_this_meaning: string[];

  evidence: Array<{
    factor: string;
    role:
      | "placement"
      | "house"
      | "rulership"
      | "dispositor"
      | "aspect"
      | "natal_promise"
      | "period_trigger"
      | "supporting_signal";
    explanation: string;
  }>;

  suppressed_meanings: Array<{
    meaning: string;
    reason: string;
  }>;

  confidence: "low" | "medium" | "high";
  debug: Record<string, unknown>;
}
```

Key principle:

```text
This contract must make the selection explainable.
Not only what was chosen, but what was not chosen and why.
```

---

## 5. Core Semantic Rule

### 5.1 Sign archetype is palette, not verdict

Example:

```text
Cancer is a meaning palette, not a final meaning.
```

Cancer palette can include:

- emotional_security
- home_family
- care
- protection
- belonging
- memory
- sensitivity
- body_emotion_rhythm

But final period meaning should not be:

```text
Cancer = family
```

It should be chosen by:

```text
planet
+ house
+ ruled_houses
+ dispositor
+ natal_promise
+ period_trigger
+ supporting_cluster
```

### 5.2 Meaning selection rule

The resolver should work like this:

1. collect possible meanings from sign + planet + house palette
2. weight them using ruled houses and dispositor
3. raise meanings supported by natal promise
4. raise meanings supported by selected period cluster
5. lower meanings unsupported by the current period configuration
6. select one primary meaning plus optional secondary domains
7. suppress alternatives explicitly with reasons

---

## 6. Worked Example: Sun in Cancer in 6th House

Possible meanings:

- emotional safety through routine
- care as labor
- workplace belonging
- body/emotion rhythm
- family obligations through daily work
- direct family/home change
- intuition/spiritual sensitivity

Wrong shortcut:

```text
Sun in Cancer = family.
```

Better resolver logic:

- `Sun` gives identity / direction / conscious vitality
- `Cancer` gives the palette
- `6th house` shifts scene toward routine, work rhythm, body, sustainability, service
- ruled houses may widen the domain
- Moon/dispositor condition filters how Cancer behaves
- natal promise decides whether routine/security is actually central
- period trigger decides whether this is Saturn-like maturation, Venus-like ease, Pluto-like control, etc.
- cluster support decides whether the period is really about work rhythm, care burden, body regulation, or family obligations spilling into daily structure

Example selected meaning:

```text
duygusal güvenliğin günlük ritim ve iş düzeni üzerinden kurulması
```

Example suppressed meanings:

- `direct family/home change`
  - unless `4th house / IC / ruler` support exists
- `intuition/spiritual sensitivity`
  - unless `Moon / Neptune / 12th` support exists

This is the minimum astrologer-like behavior the resolver should create.

---

## 7. Suppression Is Required

Suppression is not an optional debug luxury. It is part of correct interpretation.

Why:

```text
A placement or sign always offers multiple possible readings.
Without suppression, the system cannot prove that it chose consciously.
```

Minimum suppression behaviors:

- suppress direct home/family reading when house scene does not support it
- suppress spiritual/sensitivity reading when no Neptune/Moon/12th support exists
- suppress relationship reading when rulership/promise/cluster support is weak
- suppress public visibility reading when scene and cluster stay private/routine-based

This is how the system stops sounding like:

```text
Cancer = family
Saturn = burden
10th house = career pressure
```

and starts sounding like a selective astrologer.

---

## 8. Downstream Relationship

Correct future order:

```text
PeriodSemanticFocusResolver
-> PeriodVoicePolicy
-> AstrologNarrativeEngine
```

Meaning:

- `PeriodSemanticFocusResolver`
  - chooses what meaning is active
- `PeriodVoicePolicy`
  - chooses event nature, meaning intent, rhetorical frame, valence, intensity
- `AstrologNarrativeEngine`
  - turns the selected meaning into SHOU prose

Critical rule:

```text
Voice policy should not decide what meaning to read.
Voice policy should decide how to say the selected meaning.
```

This is the main architectural cleanup target.

---

## 9. Implementation Options

### Option A — Refactor existing logic only

Description:

- keep current modules
- try to stretch period spine + root causes + voice policy into semantic focus

Pros:

- low new-file count

Cons:

- meaning ownership stays blurred
- copy, scene, selection, and semantic choice stay mixed
- hard to test cleanly

Verdict:

```text
Not recommended.
```

### Option B — Build a brand-new resolver from scratch

Description:

- ignore current partial calculators
- write a new semantic engine

Pros:

- clean conceptual model

Cons:

- duplicates working intelligence
- high risk
- easy to create two competing systems

Verdict:

```text
Too risky right now.
```

### Option C — Hybrid promote-and-wrap

Description:

- create `period_semantic_focus_resolver.py`
- wrap existing canonical/hybrid/promise/scene inputs
- expose one explicit contract without deleting current calculators

Pros:

- safest migration path
- preserves working sources
- makes future tests possible
- cleanly separates meaning selection from voice

Cons:

- transitional complexity remains for a while

Verdict:

```text
Recommended safest option.
```

---

## 10. Tests Needed

When implementation starts later, minimum tests should cover:

- Cancer 6th does not automatically become family/home
- 10th house supportive event can become recognition/opening
- hard aspect can become dense integration, not automatic tension
- ruled houses affect selected meaning
- dispositor affects selected meaning
- natal promise affects selected meaning
- alternative meanings are suppressed with reasons
- multiple events cluster before selected period meaning is chosen

Additional design checks:

- scene selection is not mistaken for meaning selection
- valence/intensity is not mistaken for meaning selection
- selected meaning can be traced back to evidence sources

---

## 11. Recommended Next Step

Immediate next step is not runtime code.

Immediate next step is:

```text
Use this plan to rewrite the handcrafted period validation pack
with semantic focus awareness and limited life-chapter awareness.
```

Then:

1. human blind validation
2. scenario decision
3. if positive, runtime migration plan

Only after that:

- resolver implementation
- life-chapter implementation
- daily today-ness and daily renderer work

---

## Final Recommendation

```text
Do not build LifeChapterDetector yet.
Do not build full resolver runtime yet.
Do not expand scope into daily or timing engines yet.
```

Do this instead:

```text
Period Semantic Focus Resolver Spec / Facade Plan
+ handcrafted validation rewrite
+ human blind validation
```

If validation proves value, then the safest implementation path is:

```text
hybrid promote-and-wrap facade
```
