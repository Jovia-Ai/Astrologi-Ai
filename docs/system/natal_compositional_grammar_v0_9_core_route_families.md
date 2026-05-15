# Natal Compositional Grammar v0.9 Core Route Families Plan

## 1. Decision Summary

`v0.9` should be the first compositional semantic grammar pack, but it should not try to solve every discovery gap at once.

The `50`-chart audit shows a clear pattern:
- discovery is working
- the system usually knows where to look
- discovery signals still do not become public-ready semantic candidates
- raw and cluster-level generic fallback still own too many `public_main` slots

Most frequent gaps from the audit:
- `relationship_route`: `41`
- `career_route`: `41`
- `identity_route`: `38`
- `moon_signature`: `34`
- `axis_2h_8h`: `21`
- `axis_3h_9h`: `19`
- `house_4h_ic`: `15`
- `house_5h`: `13`
- `house_12h`: `12`

Decision:
- `v0.9` should focus only on the four core route families most needed to reduce generic fallback in ordinary mixed charts:
  - `identity_route`
  - `relationship_route`
  - `career_route`
  - `moon_signature`

Out of scope for `v0.9` Core Route Families:
- `axis_2h_8h`
- `axis_3h_9h`
- `house_4h_ic`
- `house_5h`
- `house_12h`
- tight-aspect special families
- new registry addendum
- renderer changes
- public copy generation
- runtime or selection retuning

This is a planning document only. It does not propose code changes in this phase.

## 2. Why v0.9 Should Start Here

The accepted semantic grammar plan established the layered target architecture:

`Primitive Astro Facts -> Candidate Discovery -> Compositional Semantic Grammar -> Archetype Registry -> ClusterPlan -> Renderer`

The `50`-chart audit refined the rollout order.

The key finding is not that discovery is weak. The key finding is that the semantic bridge after discovery is still too thin. The audit already knows where the missing meaning lives:
- identity
- relationship
- career
- Moon-based emotional signatures

These four route families are the best first grammar pack because they:
- are the most common high-frequency gaps
- map directly onto current generic fallback owners
- are broad enough to help mixed charts
- are constrained enough to be implemented safely under rollout guardrails

They are also the families most likely to reduce these repeated fallback owners:
- `career_career_like_career_career_visibility`
- `mind_mind_like_mind_mind_system`
- `relationship_love_like_relationship_relationships`

## 3. Scope and Non-Goals

### In Scope

`v0.9` Core Route Families planning covers:
- compositional candidate construction for `identity_route`
- compositional candidate construction for `relationship_route`
- compositional candidate construction for `career_route`
- compositional candidate construction for `moon_signature`
- rollout guardrails for source typing, public eligibility, and override precedence
- representative examples from the `50`-chart audit
- proposed test coverage for the later implementation phase

### Out of Scope

`v0.9` Core Route Families does not include:
- packet or registry writing
- renderer copy design
- new public prose templates
- selection retuning
- health-score formula changes in code
- new archetype text entries
- axis families outside the four core routes

## 4. Global Rollout Guardrails

These guardrails apply to all four grammar families.

### 4.1 Composed Candidates Start as Debug / Detail / Public Support

Composed candidates should not automatically enter `public_main`.

Initial rollout eligibility:
- `debug`
- `detail`
- `public_support`

`public_main` should require:
- a stricter confidence threshold, or
- a dedicated feature flag, or
- both

### 4.2 `source_type` Is Required

Every future composed candidate must expose:
- `source_type = composed_semantic`

It must remain distinguishable from:
- `exact_registry`
- `generic_fallback`
- `discovery_scaffold`
- `legacy_graph`

### 4.3 Exact Registry Wins Only When Context-Compatible

Exact registry should beat composed semantics only when all of these are true:
- chart facts match
- domain role matches
- `public_job` matches
- cluster context supports the same meaning

If an exact registry packet is chart-fact correct but semantically routed into the wrong domain or public role, a composed semantic candidate may be safer.

### 4.4 Specific Composed Candidate Can Beat Raw Generic Fallback

A composed candidate may outrank raw generic fallback when:
- it is chart-fact safe
- it exposes `domain_reason`
- it exposes `public_job`
- it contains `lived_scene`
- it contains `evidence_trace`
- it is not duplicative with a stronger exact packet
- it is not template-only

### 4.5 Public Eligibility Requirements

A composed semantic candidate must include:
- `source_type`
- `domain`
- `domain_reason`
- `public_job`
- `lived_scene`
- `lived_scene_atoms`
- `evidence_trace`
- `confidence`

Renderer does not write copy in this phase. Grammar creates semantic candidates only.

## 5. Shared Candidate Schema for v0.9

Every core route family should target the same minimum candidate shape:

```text
candidate_id
source_type = composed_semantic
family
subtype
domain
domain_reason
public_job
confidence
chart_facts_match
evidence_trace
lived_scene
lived_scene_atoms
gift
inner_tension
growth_direction
avoid_readings
suppressed_if
```

Shared rules:
- `family` identifies the route family
- `subtype` identifies the internal meaning branch
- `domain_reason` explains why this belongs to that domain
- `public_job` explains what the candidate should do on public surfaces
- `avoid_readings` explicitly lists what the grammar should not oversimplify into

## 6. A. `identity_route`

### Inputs

- `ASC`
- chart ruler
- Sun
- `1H` planets
- angularity
- ASC aspects if available
- chart spine if available

### Candidate Construction Logic

The goal is to compose identity from the chart’s outer entry point and its core vitality route rather than from sign stereotypes alone.

Candidate construction should:
- start from `ASC` sign tone
- identify chart ruler placement by sign, house, and condition
- add Sun’s role as self-construction / core vitality anchor
- add `1H` amplification if one or more planets occupy the first house
- increase signal if ASC, chart ruler, or Sun are angular
- detect tension when ASC route and Sun route point to different scenes
- detect coherence when ASC, ruler, and Sun reinforce the same behavioral story

### Domain Reason Rules

Allowed `domain_reason` examples:
- `ASC route`
- `chart ruler route`
- `Sun identity anchor`
- `1H amplification`
- `angular self-presentation`
- `identity spine contradiction`

### Public Job Suggestions

Initial suggestions:
- `main_identity`
- `support_gift`
- `detail_shadow`
- `debug_only`

`hero` should not be default in the first rollout.

### Confidence Scoring

Increase confidence when:
- ASC and chart ruler clearly support the same identity pattern
- Sun reinforces the same tone or scene
- the chart ruler is angular
- `1H` planets amplify the same route

Reduce confidence when:
- ASC route and chart ruler route conflict without a coherent bridge
- Sun belongs to a stronger non-identity cluster
- the route is only sign-level and not scene-level

Suggested confidence tiers:
- `high`: ASC + ruler + Sun produce a coherent identity spine
- `medium`: ASC + ruler are clear but Sun is only loosely supportive
- `low`: only one route component is strong, or route contradiction is unresolved

### Exact Registry Override Rules

Exact registry wins when:
- a trusted identity packet matches chart facts
- it belongs to the same identity domain
- it serves the same `public_job`
- it is more specific than the composed route

Composed identity remains useful when:
- there is no exact match
- the exact match is domain-misaligned
- the chart has a mixed but still coherent identity route

### Generic Fallback Suppression Rules

Suppress generic identity fallback when:
- a composed identity candidate is `medium` or `high`
- it includes a scene-based `lived_scene`
- it is chart-fact safe
- no stronger exact identity packet exists

Do not suppress fallback when:
- the composed candidate is only abstract sign language
- the route lacks scene evidence
- the meaning would duplicate a stronger public cluster

### Public Eligibility Gates

Identity-route candidate may later become public only if:
- confidence is at least `high` for `public_main`
- `domain_reason` is explicit
- `lived_scene` is present
- `evidence_trace` includes ASC and chart ruler support
- no stronger exact identity packet already owns the same role

### `lived_scene_atoms`

Examples:
- `ilk tepkiyi vermeden önce yönünü ayarladığın an`
- `bir ortama girerken nasıl görünmek istediğini hızla kurman`
- `kendi tavrını belli ederken geri çekilip yeniden pozisyon alman`
- `dışarıda görünen tavrınla içerideki niyetinin aynı olmayabildiği yer`

### Failure Modes

- ASC sign becomes the whole meaning
- chart ruler house scene is ignored
- Sun is treated as identity even when it belongs to a stronger career or relationship structure
- `1H` occupancy is over-weighted without coherence
- contradiction is flattened into “mixed personality”

### Proposed Tests

- composed identity candidates are generated when ASC + ruler route is strong
- `source_type == composed_semantic`
- no identity candidate becomes `public_main` by default
- exact identity registry overrides only when context-compatible
- eligible composed identity candidate outranks raw generic identity fallback
- chart-fact mismatch blocks the candidate

## 7. B. `relationship_route`

### Inputs

- `DSC`
- DSC ruler
- Venus
- Mars
- Moon
- `5H / 7H / 8H` links
- Venus / Mars / Moon aspects
- relationship-relevant contradictions if available

### Candidate Construction Logic

The goal is to build relationship meaning from the chart’s actual attachment and intimacy structure, not from generic partnership language.

Candidate construction should:
- start from `DSC` sign and its ruler route
- add Venus for affection, value, and attraction style
- add Mars for pursuit, boundary, and conflict expression
- add Moon for emotional need and receptivity
- add `5H / 7H / 8H` scene weighting
- detect contradictions such as:
  - harmony with hidden control
  - warmth with intensity
  - steadiness with fear of exposure
  - attachment need with boundary defense

### Subtype Routing

Subtypes should include:
- `trust_steadiness`
- `attraction_warmth`
- `boundary_conflict`
- `intimacy_depth`
- `emotional_need_affection`

These subtypes should not all fire equally. Route the strongest one or two.

### Domain Reason Rules

Allowed `domain_reason` examples:
- `DSC route`
- `DSC ruler involved`
- `Venus relationship signature`
- `Mars conflict / desire signature`
- `Moon relational need signature`
- `5H / 7H / 8H reinforcement`
- `relationship contradiction route`

### Public Job Suggestions

Initial suggestions:
- `main_relationship`
- `support_gift`
- `detail_shadow`
- `debug_only`

Avoid `hero` in first rollout.

### Confidence Scoring

Increase confidence when:
- DSC and its ruler point to a clear relational scene
- Venus / Mars / Moon reinforce the same subtype
- `5H / 7H / 8H` provide scene confirmation
- contradiction is interpretable, not noisy

Reduce confidence when:
- relationship meaning depends on only one weak planet cue
- Venus / Mars / Moon point to entirely different stories
- the chart’s strongest route is clearly elsewhere

Suggested tiers:
- `high`: DSC ruler + Venus/Mars/Moon + house scene align
- `medium`: two strong relational anchors align
- `low`: only one anchor exists or conflict is unresolved

### Exact Registry Override Rules

Exact registry wins when:
- chart facts match exactly
- the packet serves the same relationship subtype
- the packet’s `public_job` matches the route need

Composed route remains safer when:
- relationship meaning is structurally clear but not packet-specific
- the exact packet would misroute a trust issue into a simple harmony block
- the chart needs mixed relationship routing rather than one exact archetype

### Generic Relationship Fallback Suppression

Suppress generic relationship fallback when:
- a composed relationship candidate is `medium` or `high`
- subtype is explicit
- it includes a relationship `lived_scene`
- no stronger exact relationship packet exists

### Public Eligibility Gates

Relationship-route candidate may later become public if:
- subtype is explicit
- `lived_scene` is concrete
- `evidence_trace` shows DSC / ruler / Venus-Mars-Moon support
- confidence meets threshold
- no stronger exact packet already owns the same relationship role

### `lived_scene_atoms`

Examples:
- `birine yaklaşırken hızını düşürdüğün an`
- `yakınlık artarken daha kontrollü olmaya başladığın yer`
- `ilgi duyarken aynı anda mesafeyi de korumaya çalışman`
- `bir ilişkide güven oluşmadan kendini tam açmaman`
- `uyum ararken aslında neye içerlediğini geç fark etmen`

### Failure Modes

- all relationship meaning collapses into Venus
- DSC ruler scene is ignored
- attraction and trust are treated as the same subtype
- intimacy depth gets flattened into generic “yoğun ilişki”
- conflict route is mistaken for incompatibility

### Proposed Tests

- composed relationship candidates are generated when DSC route is strong
- subtype routing distinguishes trust, warmth, conflict, depth, and need
- `source_type == composed_semantic`
- composed relationship stays out of `public_main` by default
- exact relationship registry wins only when domain and `public_job` align
- eligible composed relationship candidate can beat raw generic relationship fallback
- no duplicate `public_main` when a stronger exact packet exists

## 8. C. `career_route`

### Inputs

- `MC`
- MC ruler
- `10H` planets
- Sun / Mars / Saturn / Venus / Jupiter links
- public angularity
- career-related chart spine if available

### Candidate Construction Logic

The goal is to build career meaning from public route structure, not just visibility keywords.

Candidate construction should:
- start from `MC` sign tone
- identify MC ruler sign / house / condition
- add `10H` planets and their functional roles
- detect whether public role is voiced through:
  - communication
  - responsibility
  - action
  - aesthetics / relational style
  - expansion / legitimacy
  - backstage preparation
- identify contradictions between public image and actual working route
- distinguish visible role from invisible preparation

### Subtype Routing

Subtypes should include:
- `public_voice`
- `authority_responsibility`
- `creative_visibility`
- `action_initiative`
- `strategic_role`
- `invisible_preparation_before_visibility`

### Domain Reason Rules

Allowed `domain_reason` examples:
- `MC route`
- `MC ruler involved`
- `10H planet`
- `public angularity`
- `career spine signature`
- `visibility versus preparation contradiction`

### Public Job Suggestions

Initial suggestions:
- `main_career`
- `public_support`
- `detail_shadow`
- `debug_only`

### Confidence Scoring

Increase confidence when:
- MC and MC ruler clearly point to the same public scene
- `10H` planets reinforce the same subtype
- Sun / Mars / Saturn / Venus / Jupiter provide legible public role support
- public angularity is strong

Reduce confidence when:
- only sign-level MC meaning exists
- MC ruler belongs to a stronger non-career route
- the route is only “visible” but not semantically specific

Suggested tiers:
- `high`: MC + ruler + `10H` produce a coherent role route
- `medium`: MC + one major supporting route align
- `low`: route is weak or diffuse

### Exact Registry Override Rules

Exact registry wins when:
- chart facts match
- the exact packet covers the same subtype
- the packet’s `public_job` matches the career route need

Composed route remains necessary when:
- the chart has real career structure but no exact career-family packet
- generic visibility fallback is too broad
- the chart needs a scene such as strategic role or invisible preparation

### Generic Career Fallback Suppression

Suppress generic career fallback when:
- a composed career candidate is eligible
- subtype is explicit
- the route contains real scene evidence
- no stronger exact career packet exists

### Public Eligibility Gates

Career-route candidate may later become public if:
- confidence meets threshold
- subtype is explicit
- `lived_scene` is concrete
- `evidence_trace` shows MC / ruler / `10H` support
- no stronger exact packet already owns the same surface role

### `lived_scene_atoms`

Examples:
- `bir işi sunmadan önce çerçevesini sağlamlaştırman`
- `görünür olmadan önce uzun süre hazırlık yaptığın dönem`
- `bir toplantıda sözü alırken önce konumunu netleştirmen`
- `sorumluluk aldığında tonunun otomatik olarak ciddileşmesi`
- `yaptığın işi değil onu nasıl taşıdığını da önemsemen`

### Failure Modes

- MC sign becomes a generic career slogan
- `10H` planets are counted but not semantically differentiated
- invisible preparation gets lost under generic visibility
- strategic role and authority are merged into the same block
- career route is over-forced in charts where it is secondary

### Proposed Tests

- composed career candidates are generated from MC + ruler + `10H`
- subtype routing distinguishes voice, authority, action, strategic role, creative visibility, and invisible preparation
- `source_type == composed_semantic`
- composed career stays out of `public_main` by default
- exact career registry overrides only when context-compatible
- eligible composed career candidate can beat raw generic career fallback
- no chart-fact mismatch

## 9. D. `moon_signature`

### Inputs

- Moon sign
- Moon house
- Moon aspects
- Moon ruler route
- `IC / 4H` links
- relational links if Moon routes to `7H / 8H`
- body/routine links if Moon routes to `6H`

### Candidate Construction Logic

The goal is to compose emotional meaning from actual Moon routing, not from generalized “sensitivity” language.

Candidate construction should:
- start from Moon sign tone
- locate Moon house scene
- identify strongest Moon aspects
- follow the Moon ruler route
- detect whether emotional meaning belongs primarily to:
  - inner security
  - relationship need
  - daily rhythm
  - creative expression
  - private processing
- boost home-security routing when Moon strongly links to `IC / 4H`
- boost relational routing when Moon routes to `7H / 8H`
- boost routine/body routing when Moon routes to `6H`

### Subtype Routing

Subtypes should include:
- `emotional_rhythm`
- `home_inner_security`
- `relational_need`
- `daily_sensitivity`
- `creative_emotional_expression`
- `private_emotional_processing`

### Domain Reason Rules

Allowed `domain_reason` examples:
- `Moon need signature`
- `Moon house scene`
- `Moon ruler route`
- `IC / 4H reinforcement`
- `Moon relational route`
- `Moon daily-rhythm route`

### Public Job Suggestions

Initial suggestions:
- `public_support`
- `detail_shadow`
- `support_gift`
- `debug_only`

`main_identity` or `main_relationship` should be exceptional, not default.

### Confidence Scoring

Increase confidence when:
- Moon sign, house, and ruler route tell the same story
- major Moon aspects support the same subtype
- `IC / 4H` or `7H / 8H` or `6H` links reinforce the scene

Reduce confidence when:
- Moon sign is used without house scene
- Moon aspects are noisy and contradictory
- the route is too abstract to produce a lived scene

Suggested tiers:
- `high`: Moon house + ruler route + supporting aspects align
- `medium`: two Moon anchors align
- `low`: only sign-level meaning is available

### Exact Registry Override Rules

Exact registry wins when:
- a trusted Moon-related packet matches chart facts
- it belongs to the same domain context
- it serves the same `public_job`

Composed Moon route remains necessary when:
- the emotional route is clear but not packet-covered
- the chart needs house-specific Moon meaning
- generic emotional fallback is too vague

### Generic Emotional Fallback Suppression

Suppress generic emotional fallback when:
- a Moon-route candidate is `medium` or `high`
- subtype is explicit
- `lived_scene` is concrete
- no stronger exact emotional packet exists

### Public Eligibility Gates

Moon candidate may later become public if:
- subtype is explicit
- confidence meets threshold
- `lived_scene` and `evidence_trace` exist
- no stronger exact packet already owns the same function

### `lived_scene_atoms`

Examples:
- `evdeki havanın gününün tonunu değiştirdiği an`
- `bir şey seni duygusal olarak etkilediğinde ritminin yavaşlaması`
- `yakınlık ihtiyacın arttığında bunu hemen söyleyememen`
- `günün akışı bozulduğunda bedeninin önce tepki vermesi`
- `yalnız kalıp duygunu sindirmeden netleşemediğin yer`

### Failure Modes

- Moon sign becomes generic softness language
- Moon house is ignored
- IC / `4H` links are missed
- relational Moon routes are flattened into identity
- `6H` body/routine sensitivity is mistaken for relationship need

### Proposed Tests

- composed Moon candidates are generated when Moon route is strong
- subtype routing distinguishes security, need, rhythm, routine, creativity, and private processing
- `source_type == composed_semantic`
- composed Moon candidate is not `public_main` by default
- exact Moon packet overrides only when context-compatible
- eligible composed Moon candidate can beat raw generic emotional fallback
- no chart-fact mismatches

## 10. Representative Examples From the 50-Chart Audit

### `relationship_route`

#### `fix06_grand_trine_flow`
- Raw signature: `ASC Cancer; MC Taurus; Sun Scorpio 4H; Moon Pisces 8H; Mercury Sagittarius 5H; Venus Scorpio 4H; Mars Sagittarius 5H; Jupiter Leo 1H; Saturn Virgo 2H; Uranus Scorpio 4H; Neptune Sagittarius 5H; Pluto Libra 3H`
- Current public issue: generic fallback still owns visible surfaces; relationship structure stays debug-only
- Discovery candidate: `relationship_route`
- Expected composed semantic candidate: intensity + depth + affective warmth routed through trust / intimacy instead of generic relationship copy
- Why it matters: this chart has clear relational structure even without a neat exact packet
- Later registry promotion: possible if the same relationship-depth structure repeats across multiple charts

#### `ankara_1993_06_10`
- Raw signature: `ASC Sagittarius; MC Libra; Sun Gemini 7H; Moon Pisces 3H; Mercury Cancer 7H; Venus Taurus 5H; Mars Leo 8H; Jupiter Libra 10H; Saturn Pisces 3H; Uranus Capricorn 2H; Neptune Capricorn 2H; Pluto Scorpio 11H`
- Current public issue: relationship route is discovered but still loses to fallback
- Discovery candidate: `relationship_route`
- Expected composed semantic candidate: affection + intimacy + trust threshold with a clearer subtype split
- Why it matters: the chart is mixed, but its relationship route is not generic
- Later registry promotion: possible only if subtype stability repeats

#### `buenos_aires_1980_09_09`
- Raw signature: `ASC Gemini; MC Pisces; Sun Virgo 3H; Moon Virgo 3H; Mercury Virgo 4H; Venus Leo 2H; Mars Scorpio 5H; Jupiter Virgo 3H; Saturn Virgo 4H; Uranus Scorpio 6H; Neptune Sagittarius 7H; Pluto Libra 4H`
- Current public issue: discovery knows the route, but public meaning stays too broad
- Discovery candidate: `relationship_route`
- Expected composed semantic candidate: attraction + control/depth tension rather than generic relationship filler
- Why it matters: mixed charts need subtype routing, not one relationship fallback
- Later registry promotion: not yet; grammar-first is safer

### `career_route`

#### `ankara_1993_06_10`
- Raw signature: `ASC Sagittarius; MC Libra; Sun Gemini 7H; Moon Pisces 3H; Mercury Cancer 7H; Venus Taurus 5H; Mars Leo 8H; Jupiter Libra 10H; Saturn Pisces 3H; Uranus Capricorn 2H; Neptune Capricorn 2H; Pluto Scorpio 11H`
- Current public issue: public route exists, but generic career fallback still owns `public_main`
- Discovery candidate: `career_route`
- Expected composed semantic candidate: diplomatic public role + relational intelligence + visible legitimacy
- Why it matters: MC+ruler+`10H` structure should not collapse into generic visibility
- Later registry promotion: possible after repeated public-role stability

#### `buenos_aires_1980_09_09`
- Raw signature: `ASC Gemini; MC Pisces; Sun Virgo 3H; Moon Virgo 3H; Mercury Virgo 4H; Venus Leo 2H; Mars Scorpio 5H; Jupiter Virgo 3H; Saturn Virgo 4H; Uranus Scorpio 6H; Neptune Sagittarius 7H; Pluto Libra 4H`
- Current public issue: career meaning is structurally present but semantically under-promoted
- Discovery candidate: `career_route`
- Expected composed semantic candidate: service/intellect route with a more specific strategic-role or invisible-preparation reading
- Why it matters: mixed charts need career scene specificity
- Later registry promotion: only if the route recurs with stable subtype

#### `dubai_1995_01_03`
- Raw signature: `ASC Sagittarius; MC Virgo; Sun Capricorn 2H; Moon Aquarius 2H; Mercury Capricorn 2H; Venus Scorpio 12H; Mars Virgo 9H; Jupiter Sagittarius 1H; Saturn Pisces 3H; Uranus Capricorn 2H; Neptune Capricorn 2H; Pluto Scorpio 12H`
- Current public issue: career route is discovered, but public fallback is still broader than the actual chart route
- Discovery candidate: `career_route`
- Expected composed semantic candidate: strategic role + disciplined public direction + invisible preparation before visibility
- Why it matters: this is exactly the kind of mixed chart where grammar should beat generic visibility
- Later registry promotion: maybe, but only after batch recurrence

### `identity_route`

#### `fix06_grand_trine_flow`
- Raw signature: `ASC Cancer; MC Taurus; Sun Scorpio 4H; Moon Pisces 8H; Mercury Sagittarius 5H; Venus Scorpio 4H; Mars Sagittarius 5H; Jupiter Leo 1H; Saturn Virgo 2H; Uranus Scorpio 4H; Neptune Sagittarius 5H; Pluto Libra 3H`
- Current public issue: identity route is discovered but not promoted into public-ready meaning
- Discovery candidate: `identity_route`
- Expected composed semantic candidate: protective outer stance + intense inner will + expressive warmth
- Why it matters: identity should come from ASC+ruler+Sun, not generic resilience fallback
- Later registry promotion: not until pattern recurrence is proven

#### `ankara_1993_06_10`
- Raw signature: `ASC Sagittarius; MC Libra; Sun Gemini 7H; Moon Pisces 3H; Mercury Cancer 7H; Venus Taurus 5H; Mars Leo 8H; Jupiter Libra 10H; Saturn Pisces 3H; Uranus Capricorn 2H; Neptune Capricorn 2H; Pluto Scorpio 11H`
- Current public issue: mixed-chart identity route stays structurally visible but semantically thin
- Discovery candidate: `identity_route`
- Expected composed semantic candidate: outward openness with relationally mediated self-presentation
- Why it matters: identity route should not be lost just because the chart is mixed
- Later registry promotion: only if repeated family appears across audit batches

#### `buenos_aires_1980_09_09`
- Raw signature: `ASC Gemini; MC Pisces; Sun Virgo 3H; Moon Virgo 3H; Mercury Virgo 4H; Venus Leo 2H; Mars Scorpio 5H; Jupiter Virgo 3H; Saturn Virgo 4H; Uranus Scorpio 6H; Neptune Sagittarius 7H; Pluto Libra 4H`
- Current public issue: identity is discoverable but not sufficiently scene-based
- Discovery candidate: `identity_route`
- Expected composed semantic candidate: mental/observational self-presentation with stronger inner control than generic mind fallback suggests
- Why it matters: identity route must remain distinct from mind route
- Later registry promotion: grammar-first, registry later

### `moon_signature`

#### `fix06_grand_trine_flow`
- Raw signature: `ASC Cancer; MC Taurus; Sun Scorpio 4H; Moon Pisces 8H; Mercury Sagittarius 5H; Venus Scorpio 4H; Mars Sagittarius 5H; Jupiter Leo 1H; Saturn Virgo 2H; Uranus Scorpio 4H; Neptune Sagittarius 5H; Pluto Libra 3H`
- Current public issue: emotional route is clearly present but remains debug-only
- Discovery candidate: `moon_signature`
- Expected composed semantic candidate: deep emotional processing + sensitivity to trust and inner safety
- Why it matters: Moon meaning should not disappear behind relationship or career fallback
- Later registry promotion: maybe for a repeated Moon-depth family, not yet

#### `ankara_1993_06_10`
- Raw signature: `ASC Sagittarius; MC Libra; Sun Gemini 7H; Moon Pisces 3H; Mercury Cancer 7H; Venus Taurus 5H; Mars Leo 8H; Jupiter Libra 10H; Saturn Pisces 3H; Uranus Capricorn 2H; Neptune Capricorn 2H; Pluto Scorpio 11H`
- Current public issue: emotional rhythm is found, but not promoted into a usable public-support candidate
- Discovery candidate: `moon_signature`
- Expected composed semantic candidate: emotionally porous perception with relationally colored sensitivity
- Why it matters: Moon route often explains mixed-chart undercoverage
- Later registry promotion: only after subtype recurrence

#### `buenos_aires_1980_09_09`
- Raw signature: `ASC Gemini; MC Pisces; Sun Virgo 3H; Moon Virgo 3H; Mercury Virgo 4H; Venus Leo 2H; Mars Scorpio 5H; Jupiter Virgo 3H; Saturn Virgo 4H; Uranus Scorpio 6H; Neptune Sagittarius 7H; Pluto Libra 4H`
- Current public issue: Moon route is discovered, but emotional specificity remains weaker than the chart supports
- Discovery candidate: `moon_signature`
- Expected composed semantic candidate: daily/emotional rhythm with mental filtering and stronger private processing
- Why it matters: Moon route should not be swallowed by mind or relationship fallback
- Later registry promotion: not before grammar proves stable

## 11. Proposed Test Plan for the Later Implementation Phase

Core rollout tests should prove behavior, not copy.

### Candidate Generation
- composed candidates are generated for the four core route families when evidence exists
- candidates remain absent when evidence is weak or contradictory
- `source_type == composed_semantic`

### Safety and Eligibility
- composed candidates do not enter `public_main` by default
- chart-fact mismatch blocks composed candidate eligibility
- candidates without `domain_reason`, `public_job`, `lived_scene`, or `evidence_trace` remain non-public

### Override Behavior
- `exact_registry` beats composed only when context-compatible
- composed candidate may beat `raw_generic_fallback` when eligible
- composed candidate does not duplicate a stronger exact registry packet

### Stability
- accepted golden charts remain stable:
  - Istanbul 1996
  - Adana 1998
  - Istanbul 2020
  - Izmir 1996
  - Istanbul 1994
  - Istanbul 1997

### Health-Score Improvement Targets
- representative low-health mixed charts should improve after future implementation:
  - `fix06_grand_trine_flow`
  - `ankara_1993_06_10`
  - `buenos_aires_1980_09_09`
  - `dubai_1995_01_03`

The later implementation should specifically reduce:
- raw generic fallback ownership
- discovery-only dead ends
- empty support/detail on mixed charts

## 12. v0.9 Success Criteria

`v0.9` Core Route Families should be considered successful only if a later implementation can show:
- composed candidates exist for the four route families
- composed candidates remain traceable and chart-fact safe
- generic fallback loses some ownership on mixed charts
- accepted golden regressions stay stable
- renderer remains untouched
- registry remains unchanged
- the system becomes more semantically dynamic without becoming more generic

## 13. Final Recommendation

The first compositional grammar pack should be narrow and structural.

Do not start `v0.9` by writing new public copy.
Do not start `v0.9` by adding more exact registry families.
Do not start `v0.9` by broad axis coverage.

Start with the four route families that the `50`-chart audit already proved are most central:
- `identity_route`
- `relationship_route`
- `career_route`
- `moon_signature`

This is the smallest grammar pack most likely to reduce generic fallback ownership in ordinary charts while preserving SHOU’s current strengths:
- truthfulness
- exact registry quality
- stable goldens
- renderer separation
