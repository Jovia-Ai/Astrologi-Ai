# Period Semantic Focus Resolver Audit

Date: 2026-05-04  
Scope: current period pipeline only  
Goal: decide whether the repo already contains the pieces of a true `PeriodSemanticFocusResolver`, whether they are in the wrong layer, and what the safest next PR should be

## Executive Verdict

Short answer:

```text
We do not already have a true PeriodSemanticFocusResolver.
```

What we do have is a scattered set of partial ingredients:

- canonical period domain activation
- house-scene manifestation selection
- event-level natal promise / rulership / dispositor enrichment
- period selection / clustering heuristics
- period voice policy

But these pieces do **not** currently converge into one explicit period-level object that answers:

```text
Which meaning of this activated placement/sign/pattern is selected here?
Why this meaning?
Why not the alternatives?
What evidence decided it?
```

Current state:

- `canonical_natal_activation.py` selects a **domain spine**, not a final semantic meaning.
- `period_voice_policy.py` selects **how the period is framed**, not which meaning of a placement/sign should win.
- `hybrid_context.py` and `natal_promise.py` compute rich natal context, but that context mostly remains **event-card enrichment**, not period meaning authority.
- `deep_archetype_engine.py` and `text_quality_tr.py` cluster selected events into broad `root_causes` and `story_track`, but these are still broad narrative heuristics, not a resolver with `selected_meaning` and `suppressed_meanings`.

Final verdict:

```text
The pieces exist, but they are fragmented across canonical, transitional, and legacy layers.
Safest next move: build a PeriodSemanticFocusResolver facade that promotes existing calculators instead of writing a brand-new parallel intelligence.
```

Recommended next PR:

```text
PR-3.6 — Period Semantic Focus Resolver Spec / Facade
```

Not delete-first.  
Not rewrite-first.  
Promote-and-wrap first.

---

## 1. Current Pipeline Discovery

## 1.1 Route-to-period pipeline

Live route path:

1. Transit route builds raw engine response in [transits.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/api/routes/transits.py:2384)
2. Public payload is assembled by [public_builder.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/present/public_builder.py:1373)
3. Event cards are built by `build_event_card(...)` in [deep_archetype_engine.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/deep_archetype_engine.py:663)
4. Canonical period spine is built by [canonical_natal_activation.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/canonical_natal_activation.py:245)
5. Period core is built by `build_period_core(...)` in [deep_archetype_engine.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/deep_archetype_engine.py:784)
6. Final period prose is built by `build_period_story(...)` in [astrolog_narrative_engine.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/astrolog_narrative_engine.py:462)
7. Period voice framing is selected by `build_period_voice_policy(...)` in [period_voice_policy.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/period_voice_policy.py:71)
8. Manifestation scene is selected by [manifestation_context_policy.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/manifestation_context_policy.py:87)

Current shape:

```text
raw transit events
-> interpreted public events
-> selected event cards
-> canonical period spine
-> period core / root causes / track
-> period voice policy
-> renderer
```

Missing shape:

```text
activated natal factor
-> full natal context enrichment
-> explicit selected meaning
-> suppressed alternatives
-> voice policy
-> renderer
```

## 1.2 Module-by-module role table

| Module | What semantic decision it makes | Meaning owner or enrichment only? | Layer | Canonical vs legacy | Live in public output? |
|---|---|---|---|---|---|
| [transits.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/api/routes/transits.py:2384) | orchestrates raw events, public payload, canonical activation plumbing | orchestration only | route | canonical/transitional | yes |
| [public_builder.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/present/public_builder.py:1518) | attaches canonical period spine and period core | orchestration only | public payload | canonical/transitional | yes |
| [selection.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/selection.py:37) | selects story-worthy events and support structure | selection only | pre-period | canonical/transitional | yes |
| [canonical_natal_activation.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/canonical_natal_activation.py:107) | chooses activation hooks and broad domains | partial reasoning | period/daily bridge | canonical | yes |
| [deep_archetype_engine.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/deep_archetype_engine.py:663) | builds event card meaning + period core aggregation | mixed reasoning + enrichment + rendering bridge | event + period | transitional / legacy bridge | yes |
| [natal_promise.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/natal_promise.py:74) | scores event-to-natal relevance and emits drivers / connected_points | partial reasoning, mostly event-level | event | legacy-compatible but live | yes |
| [hybrid_context.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/hybrid_context.py:65) | computes target house/sign/dispositor/rulership/aspects | source calculator / enrichment | event | transitional | yes |
| [chain_explainer_tr.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/chain_explainer_tr.py:6) | builds technical angle-ruler explanation line | copy enrichment only | event explainability | legacy-compatible | yes |
| [text_quality_tr.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/text_quality_tr.py:2131) | broad period copy mode + root cause heuristics | mixed transitional reasoning + renderer | period | transitional | yes |
| [period_voice_policy.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/period_voice_policy.py:71) | chooses event_nature, meaning_intent, rhetorical_frame, valence, intensity | voice reasoning only | period | canonical | yes |
| [manifestation_context_policy.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/manifestation_context_policy.py:87) | chooses life-scene / house scene | scene calculator only | period/daily | canonical | yes |
| [astrolog_narrative_engine.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/astrolog_narrative_engine.py:462) | renders final period prose from selected policy/context | renderer only | period | canonical renderer | yes |

---

## 2. Existing Semantic-Focus Candidates

## 2.1 Classification table

| Module / concept | Classification | Why |
|---|---|---|
| `canonical_natal_activation.build_canonical_period_spine` | `semantic_focus_candidate` | Selects broad period target hook/domain/spine, but stops at domain/theme/prefix level. |
| `period_voice_policy.build_period_voice_policy` | `semantic_focus_candidate` | Chooses framing and valence, but not full placement/sign meaning selection. |
| `manifestation_context_policy.build_manifestation_context` | `source_calculator` | Strong scene selector; does not decide which meaning family wins. |
| `natal_promise.build_natal_promise` | `source_calculator` | Computes event relevance, connected points, drivers, gate; rich evidence, but event-level and not final period focus owner. |
| `hybrid_context.build_hybrid_event_context` | `source_calculator` | Computes house/sign/dispositor/rulership/aspect context; does not choose final meaning. |
| `deep_archetype_engine.build_period_core` | `semantic_focus_candidate` | Aggregates selected events, dominant house, promise labels, root_causes, story_tracks; broad transitional meaning staging. |
| `text_quality_tr.build_root_causes` | `semantic_focus_candidate` | Clusters events into broad axes (`identity_spine`, `mind_axis_3_9`, etc.), but not explicit semantic focus. |
| `text_quality_tr.build_period_copy` | `renderer` | Uses root causes to write period prose; broad heuristics, not explicit meaning selection contract. |
| `chain_explainer_tr.build_chain_explainer_tr` | `copy_enrichment` | Technical explainability line only. |
| `selection.select_event_ids` | `source_calculator` | Chooses which events enter the period cluster; not the final semantic interpretation of those events. |
| canonical natal `activation_hooks` in [meaning_graph.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/astro_os/natal/meaning_graph.py:218) | `source_calculator` | Supplies activation metadata, but not selected period meaning. |

## 2.2 Strong existing raw materials

The strongest building blocks already exist:

1. Canonical natal activation hooks
2. Event-level natal promise scoring
3. Event-level house/ruler/dispositor/aspect enrichment
4. Period event selection / support clustering
5. Period scene selection
6. Period voice framing

The missing thing is the **single explicit joining layer**.

---

## 3. Meaning Selection Audit

## 3.1 Where does the system currently decide relationship vs work vs emotional security?

There are several partial answers, not one owner.

### A. Domain selection via canonical natal activation

[canonical_natal_activation.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/canonical_natal_activation.py:8) maps:

- event tags/domains
- scene start/outcome houses

into canonical domains like:

- `relationship`
- `career_visibility`
- `health_rhythm`
- `growth_shadow`

This is the cleanest current period-level semantic selector, but it only reaches:

```text
domain / theme / prefix / spine_lines
```

not:

```text
selected_meaning / suppressed_meanings / evidence reasons
```

### B. Domain selection via selection heuristics

[selection.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/selection.py:122) uses angle/house/domain logic to choose which events should enter the selected set.

This affects semantic outcome indirectly, but it is still:

```text
selection-time scoring
```

not:

```text
meaning-time decision explanation
```

### C. Scene selection via manifestation_context

[manifestation_context_policy.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/manifestation_context_policy.py:87) cleanly decides:

```text
where this period lands
```

but not:

```text
which meaning of Cancer / Sun / 6th / Saturn should win
```

### D. Event-level natal meaning via hybrid context and natal promise

[hybrid_context.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/hybrid_context.py:65) and [natal_promise.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/natal_promise.py:74) know a lot about:

- target planet
- house
- sign
- dispositor
- rulership houses
- natal aspect focus
- connected points
- event score / verdict / drivers

But this mostly stays attached to **event cards**.  
It does not become the explicit owner of period-level meaning selection.

## 3.2 Where does the system currently decide “Cancer means family vs care vs emotional security vs routine”?

Current answer:

```text
Nowhere explicitly.
```

The system may approximate it indirectly through:

- house-derived domain mapping
- activation hook domain mapping
- manifestation scene wording
- event-card enrichment motifs

But there is no module that takes:

```text
Sun in Cancer in 6th
+ Moon dispositor in X
+ ruled houses
+ natal promise
+ current transit trigger
+ support cluster
```

and returns:

```text
selected_meaning = emotional safety through routine
suppressed_meanings = family/home, intuition, etc.
```

## 3.3 Does any code suppress alternative meanings?

Not explicitly.

What exists:

- top-hook selection in [canonical_natal_activation.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/canonical_natal_activation.py:245)
- fallback order in [period_voice_policy.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/period_voice_policy.py:404)
- root cause ranking in [text_quality_tr.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/text_quality_tr.py:2226)

These suppress alternatives only implicitly:

- by picking the top hook
- by picking the top root cause
- by picking the first fallback

What does **not** exist:

- `suppressed_meanings[]`
- `reason_not_selected`
- explicit alternative-meaning competition

## 3.4 Does any code explain why one meaning was selected?

Partially, but not at the right level.

Existing explanation-style traces:

- `debug.policy_match.level` in [period_voice_policy.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/period_voice_policy.py:404)
- `source_debug` in [canonical_natal_activation.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/canonical_natal_activation.py:273)
- `drivers`, `connected_points`, `gate` in [natal_promise.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/natal_promise.py:122)
- `derived_context` in [hybrid_context.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/hybrid_context.py:115)

But none of these explicitly say:

```text
Cancer was interpreted as care-through-routine rather than family/home
because 6th-house manifestation + Saturn pressure + Moon disposition + support cluster tilted it there.
```

## 3.5 Does any code use ruled houses or dispositor for actual selection, not just copy?

Mostly no, at period level.

What happens today:

- [hybrid_context.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/hybrid_context.py:88) computes house rulers, dispositor, rulership houses, natal aspects
- [natal_promise.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/natal_promise.py:104) scores event relevance using graph walk and dispositor chain

But these feed:

- event-card `connected_points`
- event-card `natal_context_pack`
- section injections
- quality layer inputs

They do **not** currently drive final period selected meaning.

## 3.6 Does any code use natal promise as primary meaning governor?

No.

What natal promise does today:

- event-level salience/relevance scoring
- drivers and connected points
- copy injection support

What period uses from it:

- only a reduced `promise_themes` list in [deep_archetype_engine.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/deep_archetype_engine.py:890)

That means natal promise is currently:

```text
supporting evidence / backing flavor
```

not:

```text
primary period semantic governor
```

## 3.7 Does any code cluster multiple period events before choosing meaning?

Yes, but only broadly.

There are three cluster-like layers:

1. `select_event_ids(...)` in [selection.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/selection.py:37)
   - chooses spine + supports
2. `build_root_causes(...)` in [text_quality_tr.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/text_quality_tr.py:2226)
   - clusters into broad causes like `identity_spine`, `mirror_axis_1_7`, `mind_axis_3_9`
3. `infer_story_track_id(...)` in [astrolog_narrative_engine.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/astrolog_narrative_engine.py:368)
   - maps event/root-cause combo to a broad story track

This is useful, but still not a full semantic focus resolver.

---

## 4. Copy Enrichment vs Reasoning

This distinction is the core of the audit.

## 4.1 Reasoning owners

Current true reasoning owners:

- [selection.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/selection.py:37)
  - chooses which events matter
- [canonical_natal_activation.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/canonical_natal_activation.py:107)
  - chooses broad canonical domain hook
- [period_voice_policy.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/period_voice_policy.py:71)
  - chooses event_nature, meaning_intent, rhetorical_frame, valence, intensity

## 4.2 Enrichment-only modules

- [hybrid_context.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/hybrid_context.py:65)
  - rich natal context pack, but not period meaning owner
- [chain_explainer_tr.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/chain_explainer_tr.py:6)
  - explainability/copy only
- `build_section_injections(...)` in [natal_promise.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/natal_promise.py:177)
  - prose injection layer, not semantic owner

## 4.3 Transitional mixed owners

- [deep_archetype_engine.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/deep_archetype_engine.py:784)
  - period aggregation + legacy bridge
- [text_quality_tr.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/text_quality_tr.py:2131)
  - period copy builder + root-cause heuristics

These are important because they *look* like meaning engines, but they are mixed:

- partly reasoning
- partly renderer
- partly legacy normalization

## 4.4 Renderer-only

- [astrolog_narrative_engine.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/astrolog_narrative_engine.py:462)

It should remain renderer-only.

Audit conclusion:

```text
The repo already has calculators and heuristics, but no single period-level semantic focus owner.
```

---

## 5. Gap Analysis: What a True PeriodSemanticFocusResolver Still Needs

Missing today:

- `selected_meaning`
- `meaning_family`
- `primary_domain`
- `secondary_domains`
- `manifestation_scene` as part of one explicit focus object
- `why_this_meaning[]`
- `evidence[]`
- `suppressed_meanings[]`
- `confidence`
- `source_trace`

What exists in pieces:

| Needed field | Current partial source | Gap |
|---|---|---|
| `primary_domain` | `canonical_period_spine.primary_domain` | too broad |
| `secondary_domains` | `event domains`, selection coverage | not assembled into one object |
| `manifestation_scene` | `manifestation_context.life_scene` | available, but downstream only |
| `evidence[]` | natal promise drivers, hybrid connected points, top hooks, root cause evidence ids | not unified |
| `why_this_meaning[]` | distributed debug traces | not phrased as meaning-choice explanation |
| `suppressed_meanings[]` | none | fully missing |
| `selected_meaning` | none | fully missing |
| `confidence` | promise score / hook score / story score exist separately | not unified |

---

## 6. Proposed Architecture

## 6.1 Best next step

Best option:

```text
Option C: hybrid promote-and-wrap
```

Reason:

- enough raw materials already exist
- too many are in the wrong layer
- a brand-new independent resolver would duplicate intelligence
- direct rewrite/delete would be risky

## 6.2 Proposed placement

New facade module:

```text
backend/app/transit/narrative/period_semantic_focus_resolver.py
```

Position in pipeline:

```text
selected period events
+ canonical_period_spine
+ canonical_natal_activation_context
+ natal_promise / hybrid_context summaries
+ manifestation_context candidate
+ root_cause / story_track hints
-> PeriodSemanticFocusResolver
-> PeriodVoicePolicy
-> AstrologNarrativeEngine
```

## 6.3 Input contract

Resolver input should receive at least:

- `selected_period_events`
- `canonical_period_spine`
- `canonical_natal_activation_context`
- `natal_snapshot`
- `selected_event_cards` or a reduced event-context payload
- `manifestation_context`
- `root_causes`
- `chapter_role`

It should **not** read final prose.

## 6.4 Output contract

Recommended object:

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

---

## 7. Sign Archetype as Palette, Not Final Meaning

This is the key rule the current system still lacks.

Example:

```text
Cancer is not the final meaning.
Cancer is a meaning palette.
```

Cancer palette may include:

- emotional security
- home/family
- care
- protection
- belonging
- memory
- sensitivity
- body-emotion rhythm

Final meaning should be chosen by:

- planet function
- house manifestation
- ruled houses
- dispositor behavior filter
- natal promise relevance
- current trigger
- support cluster

Current system approximates this only partially:

- house -> scene exists
- trigger domain exists
- valence/intensity exists
- rulership/dispositor exist in event context

But the **final choice among competing Cancer meanings** is not yet explicit.

---

## 8. Example Decision Walkthrough

Example:

```text
Sun in Cancer in 6th house
```

Possible meanings:

- direct family/home focus
- emotional safety through routine
- care as labor
- workplace belonging
- body/emotion rhythm
- intuition/sensitivity

Resolver should evaluate:

1. `Sun`:
   - identity / vitality / conscious direction
2. `Cancer`:
   - emotional security / care / protection / belonging palette
3. `6th house`:
   - daily rhythm / work / labor / service / maintenance / body regulation
4. dispositor `Moon`:
   - where does emotional processing actually route?
5. ruled houses:
   - does the Sun carry 2nd / 7th / 10th implications?
6. transit trigger:
   - Saturn vs Jupiter vs Venus vs Pluto changes the reading
7. support cluster:
   - do period events drag the theme toward career, relationship, health, or home?

Example selected output:

```json
{
  "selected_meaning": "duygusal güvenliğin günlük ritim ve iş düzeni üzerinden kurulması",
  "meaning_family": "work_rhythm",
  "manifestation_scene": "günlük işleyiş ve sürdürülebilir ritim",
  "suppressed_meanings": [
    {
      "meaning": "doğrudan aile/ev hikayesi",
      "reason": "Cancer palette exists, but no 4th house / IC / ruler support won the period cluster."
    },
    {
      "meaning": "sezgisel/ruhsal hassasiyet hattı",
      "reason": "No Moon/Neptune/12th-house support was central in the selected cluster."
    }
  ]
}
```

This is exactly the level current code does not yet reach.

---

## 9. How It Should Feed Current Period Voice

Correct separation:

### PeriodSemanticFocusResolver

Decides:

```text
what meaning is active?
```

### PeriodVoicePolicy

Decides:

```text
how should this selected meaning be spoken?
```

using:

- `meaning_intent`
- `rhetorical_frame`
- `valence_mode`
- `intensity_mode`

### AstrologNarrativeEngine

Decides:

```text
how to render that policy into Turkish SHOU prose?
```

Important architecture rule:

```text
Voice policy should not decide what Cancer means here.
Voice policy should decide how the already-selected meaning sounds.
```

Current system violates this separation partially, because `period_voice_policy.py` still carries some meaning-choice burden through:

- `spine_line`
- `event_nature`
- `meaning_intent`

without an upstream `selected_meaning` object.

---

## 10. Migration Recommendation

## Option A — Refactor existing logic only

Use:

- `canonical_natal_activation.py`
- `hybrid_context.py`
- `natal_promise.py`
- `manifestation_context_policy.py`
- `text_quality_tr.build_root_causes`

Risk:

- high coupling
- mixed legacy/canonical semantics stay tangled

Benefit:

- smaller code diff

Verdict:

```text
Not preferred.
```

## Option B — Write a new resolver from scratch

New module with no reuse.

Risk:

- duplicates existing logic
- creates second intelligence stack

Benefit:

- clean contract

Verdict:

```text
Too risky unless existing pieces prove unusable.
```

## Option C — Promote-and-wrap facade

Create:

```text
backend/app/transit/narrative/period_semantic_focus_resolver.py
```

Use existing sources as inputs:

- canonical activation hooks
- manifestation context
- natal promise summary
- hybrid context summary
- selected event cluster
- root cause hints

Risk:

- medium

Benefit:

- preserves current working pieces
- gives one clean owner
- allows gradual demotion of legacy enrichment paths later

Verdict:

```text
Safest and recommended.
```

---

## 11. Recommended Tests

Add tests for:

1. `Cancer 6th` does **not** automatically resolve to home/family
2. `Cancer 6th + Saturn trigger` can resolve to:
   - emotional safety through routine
   - care as labor
3. `Cancer 6th + Jupiter trigger` can resolve to:
   - expansion through healthier rhythm
4. `10th house + supportive event` can resolve to recognition/opening, not automatic burden
5. hard aspect can become `dense integration`, not automatic tension
6. ruled houses can redirect meaning family
7. dispositor can redirect meaning family
8. natal promise can govern final chosen meaning
9. multiple period events cluster before final meaning selection
10. suppressed alternatives are emitted with reasons

---

## 12. Final Answers to the Audit Questions

### 1. Where in current period pipeline does semantic meaning get selected?

Broadly:

- in canonical domain hook selection
- in event selection / clustering
- in period root cause heuristics

But not in one explicit period semantic resolver.

### 2. Does current period_voice_policy choose meaning only from spine_line/event_nature?

Mostly yes.

It also uses:

- chapter role
- event bodies
- natal backing
- valence/intensity

But it still does not explicitly choose among multiple sign/placement meanings.

### 3. Where are natal planet condition, house, ruled houses, dispositor, natal promise, aspect bundle, and period cluster available?

Available across:

- [hybrid_context.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/hybrid_context.py:65)
- [natal_promise.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/natal_promise.py:74)
- [canonical_natal_activation.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/canonical_natal_activation.py:107)
- [selection.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/selection.py:37)
- [text_quality_tr.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/text_quality_tr.py:2226)

### 4. Are these currently used for selecting meaning, or only for copy enrichment/debug?

Mostly enrichment/debug at period level.  
More meaning-bearing at event-card level.  
Not yet unified into one period meaning owner.

### 5. Where should a PeriodSemanticFocusResolver sit?

Before `PeriodVoicePolicy`, after:

- selected period events
- canonical period spine
- semantic enrichment sources

### 6. What input contract should it receive?

- selected events
- canonical period spine
- canonical natal activation context
- natal promise summary
- hybrid context summary
- manifestation context
- root causes
- natal snapshot

### 7. What output contract should it produce?

`PeriodSemanticFocus` with:

- activated_factor
- primary_domain
- secondary_domains
- selected_meaning
- meaning_family
- manifestation_scene
- why_this_meaning[]
- evidence[]
- suppressed_meanings[]
- confidence
- debug

### 8. How should it suppress alternative meanings?

Explicitly, with reasons.

### 9. How should it feed PeriodVoicePolicy and AstrologNarrativeEngine?

- resolver outputs `selected_meaning` and semantic evidence
- voice policy maps that to frame/valence/intensity
- renderer realizes it into prose

---

## Final Verdict

```text
We do not already have a PeriodSemanticFocusResolver.
But we do have enough parts to build one safely by promoting and wrapping existing logic.
```

Safest next PR:

```text
PR-3.6 — Period Semantic Focus Resolver Spec / Facade Plan
```

Recommended approach:

- no deletions yet
- no blind rewrite
- classify and wrap existing calculators
- make `selected_meaning` explicit
- make `suppressed_meanings` explicit
- move meaning authority upstream from voice policy
