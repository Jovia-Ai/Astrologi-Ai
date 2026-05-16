# SHOU Tone-Aware Composition Plan

> Planning artifact. No code, runtime, renderer, registry, scoring, or public-output changes are made by this document.

## 1. Executive Framing

SHOU should not treat tone as a finishing filter that runs after copy is already written. `apply_tone`-style post-processing is insufficient for the next quality bar because it operates on already-composed sentences, while SHOU meaning now lives upstream in the semantic plan.

Why post-process tone is insufficient:

- **Semantic drift:** once a sentence already chose its claim, contrast shape, and pacing, later wording rewrites can soften or harden it in ways that distort packet truth.
- **Turkish grammar issues:** post-hoc swaps tend to break person choice, clause order, connector balance, and natural emphasis.
- **Structure lock-in:** tone cannot change sentence architecture after the sentence is built; it can only repaint vocabulary and punctuation.
- **SHOU mismatch:** SHOU quality depends on how a line opens, where it places contrast, whether it names the inside before the outside, and how it carries emotional distance. Those are composition decisions, not cleanup decisions.

Core principle:

> Tone is a composition constraint, not a text patch.

This plan keeps SHOU aligned with the current layered architecture:

```text
primitive chart facts
-> discovery / composed semantic candidates
-> promise packets
-> NatalPromiseClusterPlanV1
-> card_frame + promise_type + slide_role
-> tone-aware sentence strategy
-> SHOU public copy
```

The system must not:

- fall back to a static full-sentence phrase library
- make the LLM the primary renderer
- let the renderer invent meaning not already present in packet / cluster evidence

## 2. Quality Reference Extraction

The attached Venus 12H hidden/private love prototype should be treated as a quality reference, not as a template to copy literally.

Structure learned from the prototype:

- the parent card stays short and does not try to explain everything
- tapping opens a horizontal slide flow, not one long collapsed body
- each slide reveals a different face of the same promise
- slide roles are internal composition handles; the public title stays human-facing
- technical astrology is light, selective, and only used when it improves clarity
- hidden/private content unfolds through a meaningful sequence rather than generic positivity

Quality rules extracted from the prototype:

- do not restate the parent card on every slide
- do not expose raw role names as titles
- do not let every slide sound like it came from the same sentence mold
- do not over-explain astrology before lived experience is established
- do let the sequence move from inner experience toward safer visibility

Hidden/private reference flow:

1. inside experience
2. hidden mechanism
3. protective pattern
4. gift in silence
5. safe visibility

## 3. Current SHOU-Compatible Target

The target is not a new meaning system. The target is a new composition layer that reads the existing plan more intelligently.

Sentence construction inputs should be:

- `tone_profile`
- `card_frame`
- `promise_type`
- `valence_frame`
- `slide_role`

Required context that may refine those inputs:

- `cluster_id`
- `packet_id`
- `domain_frame`
- `public_job`
- `chart_role`
- `source_evidence`

Interpretation boundary:

- meaning ownership stays in discovery, packet building, cluster planning, and evidence selection
- sentence strategy ownership begins only after the meaning plan is already fixed
- renderer output must remain traceable back to packet, cluster, and evidence inputs

## 4. Audience And Length Constraints

Tone-aware composition needs explicit audience and length constraints or it will drift into over-writing.

### 4.1 Audience bands

| Surface | Primary audience state | Composition job |
|---|---|---|
| Parent card | scanning, low attention, comparison mode | compress the promise into one clear signal without flattening it |
| Tapped slide title | orienting, medium attention | name the current face of the promise in human language |
| Tapped slide body | reflective, high attention | unfold one specific semantic move with emotional precision |
| Microcopy (`push`, `share`, CTA, empty state) | interrupt-driven, retention-sensitive | create a clean emotional hook with tone-preserving brevity |

### 4.2 Length budgets

| Surface | Max title | Max body | Max sentences | Notes |
|---|---|---|---|---|
| Parent card | 52 chars | 140 chars | 1-2 | must stay glanceable |
| Tapped slide | 56 chars | 260 chars | 2-3 | one semantic move per slide |
| Deep explanatory fallback | 64 chars | 380 chars | 3-4 | only for selected surfaces, not default |
| Push / share / CTA / empty state | 48 chars | 110 chars | 1 | variant-friendly and tone-tagged |

Constraints:

- length pressure should force sharper composition, not generic shorthand
- if a line needs more space to become truthful, that means the slide role is wrong or overloaded
- parent cards must remain compressed; the slide system is the expansion surface

## 5. ToneProfile Proposal

SHOU should use four tone dimensions for composition:

```yaml
tone_profile:
  warmth: float
  certainty: float
  distance: float
  intensity: float
```

Why all four matter:

- `warmth`: controls softness, care, and how directly inner life is held
- `certainty`: controls claim firmness and how much declarative structure is allowed
- `distance`: controls whether the line feels close, observational, or slightly removed
- `intensity`: controls density, pressure, and emotional weight; this must remain explicit because heavy/light natal promises are semantically real in SHOU

Out of scope for the first SHOU tone model:

- reducing intensity into certainty or warmth
- treating tempo or directness as primary authoring dimensions
- using one generic tone tag for all promise families

## 6. Strategy Matrix

Sentence strategies should be derived from a controlled matrix, not chosen ad hoc. The strategy list is intentionally small so the system remains learnable, auditable, and testable.

### 6.1 Matrix axes

The derivation matrix should use:

- `slide_role`: what semantic move the slide must perform
- `valence_frame`: gift, friction, wound_to_gift, need, hidden/private, value/boundary, career, roots
- `tone_profile.distance + warmth`: relationship stance
- `tone_profile.certainty`: claim firmness
- `tone_profile.intensity`: pressure and density

### 6.2 Strategy derivation matrix

| Matrix condition | Default strategy |
|---|---|
| close distance + high warmth + medium certainty + inside-facing role | `intimate_observation` |
| medium distance + high certainty + explanatory role | `grounded_assertion` |
| medium distance + medium certainty + mechanism role | `structural_recognition` |
| high intensity + dual-truth role + non-resolving tension | `paradox_holder` |
| close distance + lower certainty + invitation role | `soft_invitation` |
| high evidence density + summary role | `evidence_summary` |
| close distance + high intensity + inner-experience role | `inside_lens` |
| threshold / transition / next-step role | `threshold_statement` |

### 6.3 Role-to-strategy defaults

| slide_role family | Primary strategy | Secondary strategy |
|---|---|---|
| `inside_experience`, `private_scene`, `lived_friction`, `what_you_need` | `inside_lens` | `intimate_observation` |
| `hidden_mechanism`, `role_mechanism`, `root_mechanism`, `old_reflex` | `structural_recognition` | `grounded_assertion` |
| `protective_pattern`, `boundary_tension`, `inner_polarity` | `paradox_holder` | `structural_recognition` |
| `gift_in_silence`, `self_worth_gift`, `natural_capacity`, `capacity_being_built` | `grounded_assertion` | `evidence_summary` |
| `safe_visibility`, `healthier_expression`, `what_becomes_possible`, `use_it_well` | `threshold_statement` | `soft_invitation` |

This matrix should be the learning core of the system: strategy is explained by semantic role plus tone state, not by a bag of stylistic preferences.

## 7. Sentence Strategy Catalog

The first SHOU release should stay within eight strategies.

### 7.1 `intimate_observation`

- **When used:** close-distance, warm, reflective lines that name an inner truth without over-claiming.
- **Sentence shape:** observational, emotionally near, gently clarifying.
- **Good line:** `Bunu hemen dışarı vermeyebilirsin; önce kendi içinde gerçekten yerini bulmasını istersin.`
- **Failure mode:** sounds therapeutic, overly cushioned, or vague.

### 7.2 `grounded_assertion`

- **When used:** clear gift, capacity, or consequence lines where the meaning plan is already strong.
- **Sentence shape:** firm but not mechanical; one anchored claim with lived clarity.
- **Good line:** `Yakınlığı hafife almazsın; sende bağ, yüzeyde değil derinde kurulur.`
- **Failure mode:** turns into flat declarative copy or generic confidence talk.

### 7.3 `structural_recognition`

- **When used:** mechanism, system, or pattern explanation slides.
- **Sentence shape:** reveals how something works without sounding technical.
- **Good line:** `Dışarıdan sakin görünebilir ama içeride önce güveni, sonra açıklığı yoklayan bir düzen çalışır.`
- **Failure mode:** becomes diagram prose, debug prose, or raw mechanism naming.

### 7.4 `paradox_holder`

- **When used:** friction, boundary tension, or dual truths that should not be flattened into easy resolution.
- **Sentence shape:** holds two valid pulls in one balanced line.
- **Good line:** `Yakınlık istersin; ama bağ gerçek değilse kendini hemen açmak istemezsin.`
- **Failure mode:** fake depth, sloganized contradiction, or forced positivity.

### 7.5 `soft_invitation`

- **When used:** next-step, safer-expression, or micro guidance lines where the tone should open possibility rather than command.
- **Sentence shape:** permissive, specific, non-coaching.
- **Good line:** `İçinden geçen şeyi saklamadan ama bağı da sıkıştırmadan göstermek burada daha iyi çalışır.`
- **Failure mode:** coaching drift, wellness language, or generic advice voice.

### 7.6 `evidence_summary`

- **When used:** when several evidence atoms need to compress into one public-facing takeaway.
- **Sentence shape:** concise synthesis with visible semantic compression.
- **Good line:** `Bu tema sende hem geri planda çalışır hem de güçlü bağlarda daha belirgin hale gelir.`
- **Failure mode:** listy recap, chip-format prose, or pseudo-technical stacking.

### 7.7 `inside_lens`

- **When used:** hidden/private, wound, need, or emotionally dense slides that should start from lived interiority.
- **Sentence shape:** begins inside, then opens outward only if needed.
- **Good line:** `Önce his büyür; dışarıdan görünmesi ise çoğu zaman daha geç olur.`
- **Failure mode:** melodrama, abstraction, or vague inward fog.

### 7.8 `threshold_statement`

- **When used:** transition slides such as safe visibility, healthier expression, or what becomes possible.
- **Sentence shape:** marks a change in what the pattern allows once a condition is met.
- **Good line:** `Güven kurulduğunda bu tarafın sadece gizli kalmaz; ilişkiye derinlik ve sadakat de taşır.`
- **Failure mode:** generic uplift, motivational ending, or under-evidenced optimism.

## 8. Editorial Constraint Library

SHOU should not build a static phrase library. It should build an editorial constraint library that guides composition.

Allowed library contents:

- `forbidden_patterns`
- `preferred_patterns`
- `title_pattern_families`
- `good_examples`
- `bad_examples`
- `role_specific_language_guidance`
- `words_to_avoid`
- `approved_fragments`

Design rule:

> This library guides composition. It does not replace meaning planning.

### 8.1 Forbidden patterns

- `mesele sadece`
- `otomatik olarak`
- `bu çizgi çalışır`
- `potansiyel birlikte çalışır`
- `ritim` in public copy unless explicitly approved
- too-English noun/adjective phrasing
- chip-format prose
- raw role names as titles

### 8.2 Preferred patterns

- `hemen göstermeyebilirsin`
- `önce kendi içinde...`
- `bu, az hissettiğin anlamına gelmez`
- `içinden geçen şeyi saklamadan ama bağı da sıkıştırmadan...`
- `dışarıda ... görünürken, içeride ... çalışabilir`

### 8.3 Title guidance

Titles should:

- sound human-facing, not ontological
- point to the face of the promise, not the registry label
- differ by role even inside the same card

Titles should not:

- repeat the parent card wording
- expose `slide_role`, `card_frame`, or cluster labels directly
- sound like translated documentation

## 9. Adaptive Slide Composition

SHOU should not force every card into one universal five-slide template. Slide profiles must adapt by:

- `domain_frame`
- `promise_type`
- `valence_frame`

### 9.1 Slide profile families

| Card family | Adaptive slide flow |
|---|---|
| `gift` | `natural_capacity -> where_it_shows -> how_it_helps -> overuse_risk -> use_it_well` |
| `friction` | `lived_friction -> inner_polarity -> old_reflex -> capacity_being_built -> what_becomes_possible` |
| `wound_to_gift` | `sensitive_spot -> protection_pattern -> what_it_notices -> gift_that_grows -> safe_visibility` |
| `need` | `what_you_need -> without_it -> how_you_seek_it -> overprotection -> healthier_expression` |
| `hidden/private` | `private_scene -> hidden_mechanism -> protective_pattern -> gift_in_silence -> safe_visibility` |
| `value/boundary` | `value_scene -> exchange_pattern -> boundary_tension -> self_worth_gift -> grounded_exchange` |
| `career` | `public_scene -> role_mechanism -> visibility_friction -> authority_or_voice -> sustainable_visibility` |
| `roots` | `inner_base_scene -> root_mechanism -> old_pattern -> safety_need -> re_rooting` |

### 9.2 Friction rule

For friction cards, `capacity_being_built` must not become a generic positivity slide. It must answer four things:

1. what this friction creates
2. what skill is being built
3. what old reflex it replaces
4. what becomes possible when the skill develops

### 9.3 Hidden/private rule

For hidden/private cards, the role sequence should keep the prototype logic:

1. what is lived inside
2. why it stays less visible
3. what it protects
4. what quiet gift it carries
5. how safer visibility becomes possible

## 10. Microcopy As First-Class Composition

Push, share line, short headline, CTA, and empty state are not minor surfaces. They are acquisition and retention surfaces, so they deserve deliberate tone handling.

Policy:

- microcopy may use tone-tagged variants
- microcopy can tolerate a tighter pattern library than long-form natal copy
- long natal and period body copy should remain plan-driven and sentence-strategy driven
- short microcopy may be variant-driven because the semantic burden is smaller and the product need is speed

Recommended split:

- long body copy: semantic plan + slide role + strategy selection
- microcopy: semantic plan + tone tag + editorial constraint library

## 11. LLM Policy

LLM must not be the primary renderer for SHOU public copy.

Allowed uses:

- long-tail draft assistance
- editorial assist
- non-public preview
- cached deterministic plan-to-draft experiments

If an LLM is used at all, these conditions are required:

- deterministic meaning plan exists first
- cache exists
- banned-phrase scan exists
- truthfulness guards remain active
- no direct public release without validation

LLM non-goals:

- no direct packet-to-public generation without an intermediate plan
- no freeform invention of titles, meanings, or emotional claims
- no bypass around evidence traceability

## 12. `humanize_tr` And `apply_tone` Migration

Tone-aware composition should move earlier. `humanize_tr` and `apply_tone` should narrow in responsibility over time.

### 12.1 Target role definitions

- `apply_tone`: fallback safety net only, then gradually deprecated on new surfaces
- `humanize_tr`: grammar, punctuation, normalization, and duplicate-cleanup only
- tone-aware composition: upstream sentence strategy and line construction before copy exists

### 12.2 Migration mapping

| Current path / tool | Current role | Target role | Action | Fallback status | Required tests |
|---|---|---|---|---|---|
| `apply_tone` on new SHOU slide surfaces | post-build tone mutation | none on primary path | stop using as default for new slide composition | fallback-only | assert new surfaces do not call `apply_tone` except explicit fallback |
| `apply_tone` on legacy public text | safety rewrite | safety rewrite | keep temporarily while old surfaces migrate | keep | regression tests for no semantic drift on legacy outputs |
| `humanize_tr_text` in long-form SHOU copy | mixed normalization + softening | normalization only | remove tone-shaping responsibility | keep | assert tone structure is unchanged before/after humanization |
| parent card composition | compressed summary | compressed strategy-led summary | migrate first | no fallback preferred | title/body length, tone-structure, banned-phrase tests |
| tapped slide body composition | often editorial cleanup after text exists | primary tone-aware composition surface | migrate first | fallback allowed behind guard | slide-role sequencing, strategy diversity, no repetition tests |
| deep explanatory detail blocks | editorial expansion | later migration | migrate after slide path stabilizes | fallback allowed | side-by-side read, repetition, clinical-tone checks |
| push/share/CTA/empty states | ad hoc microcopy risk | tone-tagged microcopy variants | migrate after core slide path | variants acceptable | microcopy lint, tone-family coherence tests |

### 12.3 Which paths migrate first

Migrate first:

1. tapped slide bodies for one selected card family
2. parent card summary for that same family
3. adjacent microcopy for the same family

Migrate later:

1. other slide families
2. deep editorial detail blocks
3. non-SHOU legacy public surfaces

## 13. Authoring Workflow

Editorial constraints should be authored as reviewable config plus examples, not buried as opaque string rewrites.

### 13.1 Authoring format

Recommended:

- YAML or structured config for constraint definitions
- code review required for every new constraint family
- hot reload can be a later convenience, not a first requirement

### 13.2 Authoring requirements

Every new constraint or strategy addition should include:

- rationale
- good examples
- bad examples
- affected slide roles
- affected card families
- banned phrase considerations
- QA notes

### 13.3 Side-by-side read QA

For each promise family, review multiple outputs side by side and ask:

- do they feel like the same person?
- do they contradict each other?
- are they too similar?
- does one sound translated?
- does one sound too clinical?
- does one sound too therapeutic?

This read should be mandatory for any new family before public rollout.

## 14. Data Model Proposal

Suggested composition-facing fields:

```yaml
tone_profile:
  warmth: float
  certainty: float
  distance: float
  intensity: float

card_frame: str
promise_type: str
valence_frame: str
slide_profile: str
slide_role: str
sentence_strategy: str
forbidden_patterns: list[str]
preferred_patterns: list[str]
lived_scene_atoms: list[str]
copy_quality_flags: list[str]
```

Additional useful composition metadata:

- `cluster_id`
- `packet_id`
- `domain_frame`
- `chart_role`
- `public_job`
- `source_evidence_ids`
- `strategy_reason`

Design rule:

- sentence strategy should be derivable from state
- strategy selection should be inspectable in debug traces
- public copy should remain explainable without exposing internal authoring labels publicly

## 15. Tests

Required tests for the new system:

- no post-process semantic drift
- no banned phrases
- no chip-format prose
- no raw role names as public titles
- no repeated slide structures when `card_frame` differs
- no same slide repeated inside one card
- friction slide includes `capacity_being_built` and `what_becomes_possible`
- hidden/private slide flow matches inside/protection/gift/visibility logic
- tone strategy produces different sentence structures, not just word substitutions
- `humanize_tr` does not change tone
- `apply_tone` is not used on new surfaces except fallback
- title/body length budgets hold by surface
- audience band is respected by surface type

Recommended QA bundles:

- golden chart regression checks
- banned phrase scan
- side-by-side family read
- chart-truthfulness scan
- same-family variation read across multiple charts

## 16. Rollout Plan

### Phase 1

- planning
- static examples
- no code

### Phase 2

- one card prototype using Venus 12H hidden/private love
- prove slide roles, strategy selection, and quality gates on one controlled family

### Phase 3

- `slides[]` contract
- internal structure for adaptive slide profiles and role metadata

### Phase 4

- tone-aware renderer for selected card frames
- migrate hidden/private and one adjacent family first

### Phase 5

- microcopy variant library for push / share / headline surfaces

### Phase 6

- deprecate `apply_tone` from new surfaces
- keep only explicit fallback safety use where legacy paths still need it

## 17. Non-Goals

- no LLM primary renderer
- no full-sentence phrase library as core architecture
- no renderer meaning invention
- no public rollout without QA
- no one-size-fits-all slide template

## 18. Final Recommendation

SHOU should build tone-aware composition, not tone post-processing.

The recommended system is:

- semantic plans from `NatalPromisePacketV1` and `NatalPromiseClusterPlanV1`
- adaptive slide profiles
- matrix-derived sentence strategies
- editorial constraint library
- tone-tagged microcopy variants
- grammar-only humanization

This is the path most likely to produce public copy that feels written rather than patched, while preserving SHOU's current architecture, truthfulness discipline, and evidence ownership.
