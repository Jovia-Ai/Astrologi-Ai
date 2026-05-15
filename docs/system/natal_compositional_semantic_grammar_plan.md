# Natal Compositional Semantic Grammar Plan

## 1. Decision Summary

The system is now a strong curated semantic engine with an emerging discovery layer, but it is not yet a full compositional grammar engine.

The next strategic goal is to reduce raw generic fallback ownership in ordinary charts without sacrificing truthfulness, specificity, or SHOU voice quality.

This plan extends the current architecture. It does not propose replacing:
- `NatalPromisePacketV1`
- `NatalPromiseClusterPlanV1`
- registry overlays
- renderer integration
- truthfulness guards

Current strategic direction:
- Registry remains quality memory and exact override.
- Compositional semantic grammar becomes the middle layer that creates meaning for new charts.
- ClusterPlan remains the public-surface selector.
- Renderer remains the SHOU language layer.

Core operating principle:
- Matrix / discovery tells us where to look.
- Grammar builds the meaning.
- Registry provides high-quality examples and overrides.
- ClusterPlan decides `public_main / support / detail`.
- Renderer says it in SHOU language.

Accepted golden charts that must remain the regression baseline:
- Istanbul 1996
- Adana 1998
- Istanbul 2020
- Izmir 1996
- Istanbul 1994
- Istanbul 1997

## 2. Why Registry-Only Will Not Scale

The current registry/packet system is not a mistake. It created the quality memory needed to avoid generic `Moon trine Venus = loving` interpretations.

But continuing only with manual addendums creates structural risk:
- registry grows too large
- similar meanings appear under different names
- golden chart overfitting increases
- maintenance burden grows
- mixed charts still fall into generic fallback
- new combinations remain uncovered unless manually added
- `public_main` can still be occupied by generic fallback when an exact packet is missing

The `v0.6` Discovery Metrics Report changed the diagnosis.

Important current finding:
- most common missing domains: none

This means the core problem is no longer “we do not know where to look.”

The core problem is:
we do not yet have enough compositional grammar to turn discovery signals into publishable semantic candidates.

In other words:
- discovery is increasingly good at finding chart-relevant areas
- registry is increasingly good at exact high-quality matches
- but the middle layer between them is still too thin

Without that middle layer, ordinary mixed charts remain vulnerable to:
- raw generic fallback ownership
- under-promoted domain signals
- discovery candidates that stay debug-only because no semantic bridge exists

## 3. What Compositional Semantic Grammar Should Do

Compositional semantic grammar is the missing middle layer between discovery and public selection.

It should combine:
- planet nature
- sign tone
- house scene
- aspect action
- orb / angularity / intensity
- dignity / condition if available
- ruler role
- dispositor route
- house ruler route
- domain role
- natal promise / contradiction
- chart spine
- node / axis involvement
- public surface job

It should produce:
- composed semantic candidates
- meaning family
- domain
- `domain_reason`
- `public_job`
- `lived_scene`
- `lived_scene_atoms`
- `gift`
- `inner_tension`
- `growth_direction`
- `avoid_readings`
- `confidence`
- `evidence_trace`

It should not directly write public copy.

`v0.9` compositional grammar should first emit non-public composed semantic candidates. Those candidates should be eligible for `debug`, `detail`, `support`, or later `public_main`, but they must not automatically become public surfaces.

ClusterPlan remains the decision layer that determines whether a composed candidate becomes:
- `public_main`
- `public_support`
- `detail`
- `debug`

## 4. Proposed Final Architecture

Target layered architecture:

### 1. Primitive Astro Facts
- planets
- signs
- houses
- aspects
- orbs
- dignity / condition
- angularity
- nodes
- ruler chains
- dispositor routes
- house ruler routes

### 2. Candidate Discovery
- identity route
- relationship route
- career route
- emotional route
- mind route
- `2H/8H` axis
- `3H/9H` axis
- `4H/IC`
- `5H` creativity
- `12H` saturation
- tight aspects

### 3. Compositional Semantic Grammar
- turns discovered structure into composed semantic candidates

### 4. Archetype Registry
- exact, high-quality, manually validated archetype memory
- overrides or strengthens composed candidates when an exact trusted match exists

### 5. ClusterPlan
- decides `public_main / public_support / detail / debug`
- handles domain representation
- suppresses duplicate/generic fallback
- prevents chart-fact leakage

### 6. Projection Renderer
- turns selected clusters into SHOU public copy
- does not choose meaning

Text architecture diagram:

```text
Primitive Astro Facts
  -> Candidate Discovery
      -> Compositional Semantic Grammar
          -> Archetype Registry Match / Override
              -> ClusterPlan Selection
                  -> Projection Renderer

Primitive Astro Facts:
  placements, aspects, houses, signs, rulers, routes, axes, angularity

Candidate Discovery:
  identifies where the chart is structurally active

Compositional Semantic Grammar:
  builds traceable semantic candidates with domain, public_job, lived_scene,
  tension, gift, growth, confidence, and evidence

Archetype Registry:
  quality memory, exact examples, high-trust overrides, promotion target

ClusterPlan:
  selects main/support/detail/debug, controls fallback, guards truthfulness

Renderer:
  SHOU language only, not meaning selection
```

## 5. Registry’s New Role

Registry should be treated as quality memory, not the whole brain.

Registry should:
- provide exact high-quality archetype matches
- provide strong voice seeds
- provide chart-family-specific nuance
- override generic or composed interpretations when exact and trusted
- act as the promotion target for patterns that recur in batch audits

Registry should not:
- be the only way to create meaning
- require manual exact packets for every chart
- turn into a massive unstructured dictionary
- override compositional grammar when a different domain/context is stronger

Priority rule:

`high-confidence exact registry packet > high-confidence composed semantic candidate > generic fallback > debug-only discovery scaffold`

This preserves the current strength of SHOU while allowing coverage to scale beyond hand-authored exact families.

## 6. Public Eligibility for Composed Candidates

A composed semantic candidate must not automatically become `public_main`.

It must first pass public eligibility:
- chart-fact safe
- clear domain
- `lived_scene` present
- enough confidence
- `evidence_trace` present
- not duplicative with a stronger exact registry packet
- not generic/template-only
- no suppressed reading conflict
- `public_job` defined

If a composed candidate fails public eligibility:
- it can remain `debug`
- or it can remain `detail` / `support`
- or it can remain discovery-only

But it should not silently become `public_main`.

This rule is necessary to preserve:
- truthfulness
- chart specificity
- SHOU voice quality
- stability against accidental genericness

## 7. Specific Composed Candidate Beats Generic Fallback

Selection principle:

Specific composed candidate beats generic fallback when:
- it is traceable
- it has coherent domain/context
- confidence is high enough
- chart facts match
- it has `lived_scene` and `public_job`
- it is not duplicative with a better exact registry packet

Generic fallback should only win when no better exact or composed candidate exists.

Examples:
- `relationship_relationships` should not own `public_main` if a specific Venus/Saturn, Venus/Mars, Moon/Venus, or DSC-ruler candidate exists with comparable support.
- generic career visibility should not own `public_main` if an `MC + ruler + 10H` career-route candidate exists.
- generic `mind_mind_system` should not crowd out a stronger Mercury / `3H/9H` intellectual-authority route when the latter is more chart-specific.

This principle is central to reducing raw generic fallback on ordinary charts.

## 8. `domain_reason` and `public_job` Fields

Future candidates and packets should carry explicit structural role fields.

### `domain_reason`

Question answered:
Why is this candidate in this domain?

Examples:
- `MC ruler involved`
- `10H planet`
- `DSC ruler involved`
- `Venus aspect`
- `Moon need signature`
- `ASC/chart ruler identity route`
- `2H/8H axis`
- `3H/9H mind-belief axis`

### `public_job`

Question answered:
What should this candidate do on the public surface?

Allowed examples:
- `hero`
- `main_identity`
- `main_relationship`
- `main_career`
- `main_mind`
- `detail_shadow`
- `support_gift`
- `activation_hook`
- `transit_triggerable`
- `proof_only`
- `debug_only`

Why these fields matter:
- they prevent the same anchor from rendering with the wrong public role
- they make ClusterPlan decisions easier to justify
- they separate semantic meaning from surface job
- they reduce accidental cross-domain copy reuse

## 9. Same Anchor, Different Domain Disambiguation

The same anchor can mean different things depending on cluster/domain.

Examples:

`Venus 12H`
- career cluster -> creative incubation / invisible preparation before public visibility
- relationship cluster -> private love / hidden feeling / idealization / emotional privacy
- creativity cluster -> inner aesthetic refinement / work prepared behind the scenes

`Saturn-Uranus`
- mind cluster -> structured originality / new idea given working form
- identity cluster -> controlled exterior + unusual inner signature

`Mars Leo 11H`
- community cluster -> social courage / visible warmth in group
- relationship cluster -> warmth, excitement, personal rhythm in closeness

Rule:
when an anchor repeats across domains, cluster role must override copy ingredients.

Do not reuse the same headline/body across different domains.

The anchor can repeat. The public function and semantic framing must not collapse into the same block.

## 10. `lived_scene_atoms`

Plan a renderer-support field:

`lived_scene_atoms`

These are small, natural, user-facing scenes that help the renderer avoid template prose.

Examples:
- `bir mesajı göndermeden önce durduğun an`
- `bir toplantıda geri çekildiğin yer`
- `bir işi göstermeden önce içeride uzun süre hazırlaman`
- `bir ortamın havasını herkesten önce okuman`
- `birine yakınlaşırken kendi alanını kaybetmek istememen`
- `evde sakin kalamadığında bunun yüzüne yansıması`

Rules:
- `lived_scene_atoms` are not meaning owners
- they support public copy
- they must be traceable to packet/candidate evidence
- they should be Turkish-native, not translated phrases

Recommended generation model:
- grammar proposes candidate-level `lived_scene_atoms`
- registry can strengthen or replace them for exact known families
- renderer uses them as copy ingredients, not as semantic authority

## 11. Compositional Grammar Family Proposals

Initial grammar families should follow the gap patterns already visible in `v0.6` metrics.

### 1. `career_route`

Input facts:
- `MC`
- `MC` ruler
- `10H` planets
- relevant Mars/Saturn/Venus/Sun/Jupiter involvement

Generated candidate fields:
- meaning family: career route / public role
- likely domain: `career`
- common `domain_reason`: `MC ruler involved`, `10H planet`, `angular public route`
- likely `public_job`: `main_career`, `support_gift`
- likely `lived_scene`: visibility threshold, role ownership, work identity

Confidence rules:
- stronger when `MC` ruler is angular, in `10H`, tightly aspected, or tied to chart spine

Domain routing:
- mostly `career`
- sometimes `identity` if the public role is the chart’s visible spine

Public_job suggestions:
- `main_career`
- `support_gift`

Examples:
- strategic public voice
- responsible public style
- visible work identity

Failure modes:
- over-forcing career from one mild `10H` indicator
- collapsing visibility and vocation into the same shallow card

Registry override behavior:
- exact `MC + ruler + 10H` archetypes override or strengthen composed output

### 2. `moon_signature`

Input facts:
- Moon sign
- Moon house
- Moon aspects
- Moon ruler route

Generated candidate fields:
- meaning family: emotional rhythm / need signature
- likely domains: `home_family`, `emotional_world`, `relationship`, `inner_world`
- common `domain_reason`: `Moon need signature`, `IC link`, `Moon aspect`
- likely `public_job`: `main_identity`, `main_relationship`, `support_gift`, `detail_shadow`

Confidence rules:
- stronger when Moon is angular, tightly aspected, chart-spine relevant, or in direct axis tension

Domain routing:
- driven by house and axis context first, sign second

Public_job suggestions:
- `main_identity`
- `support_gift`
- `detail_shadow`

Examples:
- home security need
- relational sensitivity pattern
- emotional regulation tension

Failure modes:
- reducing Moon to sentimentality
- ignoring house/aspect context

Registry override behavior:
- exact Moon-family packets should replace generic emotional fallback when trusted

### 3. `identity_route`

Input facts:
- `ASC`
- chart ruler
- Sun
- `1H` planets
- angularity

Generated candidate fields:
- meaning family: identity spine
- likely domain: `identity`
- common `domain_reason`: `ASC/chart ruler identity route`, `1H planet`, `Sun support`
- likely `public_job`: `hero`, `main_identity`, `support_gift`

Confidence rules:
- stronger when ASC ruler and Sun reinforce each other or form the chart’s main behavioral spine

Domain routing:
- mostly `identity`
- sometimes `community` or `career` if the identity spine is carried publicly

Public_job suggestions:
- `hero`
- `main_identity`

Examples:
- action-through-balance
- hidden-value identity
- visible self-construction theme

Failure modes:
- pure sign-summary identity cards
- ignoring chart ruler route

Registry override behavior:
- exact identity-route families should outrank generic identity fallback

### 4. `relationship_route`

Input facts:
- `DSC`
- `DSC` ruler
- Venus / Mars / Moon
- `7H / 8H / 5H` links

Generated candidate fields:
- meaning family: attachment / intimacy / relationship pattern
- likely domain: `relationship`
- common `domain_reason`: `DSC ruler involved`, `Venus aspect`, `7H/8H link`
- likely `public_job`: `main_relationship`, `support_gift`, `detail_shadow`

Confidence rules:
- stronger when `DSC` ruler, Venus/Mars, and relational houses converge

Domain routing:
- primarily `relationship`
- sometimes `inner_world` if trust and vulnerability dominate more than pairing

Public_job suggestions:
- `main_relationship`
- `support_gift`
- `detail_shadow`

Examples:
- trust threshold
- harmony plus wound-depth
- serious love style

Failure modes:
- flattening all relationship meaning into one harmony card
- over-reading one Venus aspect

Registry override behavior:
- exact relationship archetypes outrank `relationship_relationships`

### 5. `axis_2h_8h`

Input facts:
- `2H / 8H` planets
- `2H / 8H` rulers
- Venus / Mars / Moon / Saturn / Pluto involvement

Generated candidate fields:
- meaning family: worth / exchange / dependency / trust axis
- likely domains: `money_self_worth`, `relationship`, `inner_world`
- common `domain_reason`: `2H/8H axis`, `shared resource tension`, `trust exchange`
- likely `public_job`: `detail_shadow`, `support_gift`, sometimes `main_relationship`

Confidence rules:
- stronger when both sides of the axis are activated or the rulers/aspects intensify exchange themes

Domain routing:
- driven by whether the chart expresses the axis as value, intimacy, survival, or power exchange

Public_job suggestions:
- `detail_shadow`
- `support_gift`

Examples:
- self-worth vs shared dependency
- trust and control exchange

Failure modes:
- confusing money and intimacy
- collapsing all `8H` content into trauma language

Registry override behavior:
- exact `2H/8H` archetypes replace generic scarcity/intimacy fallback when available

### 6. `mercury_signature`

Input facts:
- Mercury
- `3H / 9H`
- aspects
- ruler chain

Generated candidate fields:
- meaning family: mind / speech / learning route
- likely domain: `mind`
- common `domain_reason`: `Mercury route`, `3H/9H axis`, `Mercury aspect`
- likely `public_job`: `main_mind`, `support_gift`, `detail_shadow`

Confidence rules:
- stronger when Mercury is angular, tightly aspected, or tied to `3H/9H` or career visibility

Domain routing:
- mostly `mind`
- can route to `career` when speech/strategy is publicly visible

Public_job suggestions:
- `main_mind`
- `support_gift`

Examples:
- strategic mind
- intellectual authority
- social intuition in language

Failure modes:
- reducing Mercury to generic intelligence
- missing worldview vs communication distinctions

Registry override behavior:
- exact Mercury-route packets should outrank `mind_mind_system`

### 7. `house_5h`

Input facts:
- `5H` planets
- `5H` ruler
- relevant aspects

Generated candidate fields:
- meaning family: joy / creativity / romantic expression
- likely domains: `creativity`, `relationship`, `identity`
- common `domain_reason`: `5H concentration`, `5H ruler`, `play/romance route`
- likely `public_job`: `support_gift`, `detail_shadow`

Confidence rules:
- stronger when multiple `5H` signals converge or the ruler is highly emphasized

Domain routing:
- depends on whether the chart expresses `5H` through art, romance, play, or self-display

Public_job suggestions:
- `support_gift`
- `detail_shadow`

Examples:
- romantic warmth
- expressive joy
- visible creative play

Failure modes:
- confusing romance, creativity, and attention-seeking

Registry override behavior:
- exact `5H` families should displace generic romance or creativity fallback when chart-specific

### 8. `house_4h_ic`

Input facts:
- `IC`
- `4H`
- Moon
- ruler route

Generated candidate fields:
- meaning family: home / roots / inner security
- likely domain: `home_family`
- common `domain_reason`: `IC route`, `4H emphasis`, `Moon root signature`
- likely `public_job`: `main_identity`, `support_gift`, `detail_shadow`

Confidence rules:
- stronger when Moon/IC are angular, opposed by `MC`/Mercury, or clearly chart-defining

Domain routing:
- mostly `home_family`
- can extend into `identity` if inner security strongly shapes behavior

Public_job suggestions:
- `main_identity`
- `support_gift`
- `detail_shadow`

Examples:
- emotional roots
- home security axis
- inherited emotional pattern

Failure modes:
- using family language when the chart is more about inner base than literal family

Registry override behavior:
- exact Moon/IC or `4H` archetypes should replace generic emotional/home fallback

### 9. `axis_3h_9h`

Input facts:
- `3H / 9H`
- Mercury / Jupiter
- supporting aspects

Generated candidate fields:
- meaning family: speech / belief / perspective axis
- likely domain: `mind`
- common `domain_reason`: `3H/9H mind-belief axis`, `Mercury/Jupiter route`
- likely `public_job`: `main_mind`, `support_gift`

Confidence rules:
- stronger when both houses, rulers, or Mercury/Jupiter themes are active together

Domain routing:
- mostly `mind`
- occasionally `community` or `career` if teaching/perspective is public-facing

Public_job suggestions:
- `main_mind`
- `support_gift`

Examples:
- learning vs worldview tension
- teaching / writing perspective

Failure modes:
- collapsing communication and belief into a flat mind card

Registry override behavior:
- exact `3H/9H` families should outrank generic mind fallback when sufficiently specific

### 10. `house_12h`

Input facts:
- `12H` concentration
- Venus / Sun / Mars / Saturn / Neptune

Generated candidate fields:
- meaning family: private world / hidden preparation / invisibility route
- likely domains: `inner_world`, `relationship`, `career`, `identity`
- common `domain_reason`: `12H concentration`, `hidden preparation`, `invisible pressure`
- likely `public_job`: `detail_shadow`, `support_gift`, sometimes `main_identity`

Confidence rules:
- stronger when multiple `12H` placements, ruler ties, or angular compensations make the backstage world chart-defining

Domain routing:
- must be disambiguated by cluster context

Public_job suggestions:
- `detail_shadow`
- `support_gift`
- sometimes `main_identity`

Examples:
- invisible preparation
- private maturity
- hidden action or hidden value

Failure modes:
- vague spirituality copy
- treating every `12H` signature as loss or secrecy

Registry override behavior:
- exact `12H` archetypes should refine domain context and prevent generic mysticism fallback

## 12. Discovery -> Grammar -> Registry Promotion Loop

The long-term learning loop should work like this:

1. Batch audit surfaces discovery gaps.
2. Compositional grammar turns recurring gaps into composed semantic candidates.
3. Batch audit tests whether composed candidates reduce raw generic fallback `public_main`.
4. Repeated, high-quality, stable composed candidates become registry archetypes.
5. Registry stores the best exact examples and voice seeds.
6. Golden regression protects accepted chart behavior.

This keeps the system dynamic without losing quality.

Discovery finds structure.
Grammar turns structure into meaning.
Registry remembers the best exact meanings.

## 13. Metrics for 50-Chart Batch Audit

Per chart, record:
- `chart_id / birth data`
- `candidate_packet_count`
- `unique_candidate_packet_count`
- `selected_packet_count`
- `public_main_count`
- `public_support_count`
- `detail_count`
- `fallback_public_main_count`
- `generic_public_main_count`
- `customized_fallback_public_main_count`
- `cluster_specific_fallback_count`
- `non_public_discovery_packet_count`
- `focus_map` domains and tiers
- `public_main_source_type` distribution:
  - `exact_registry`
  - `composed_semantic`
  - `generic_fallback`
  - `discovery_only`
  - `legacy_graph`
- `missing_domain_flags`
- `coverage_warnings`
- `chart_facts_match_false_count`
- `duplicate_headline_count`
- `v8_duplication` flag
- `health_score`
- `top_discovery_gaps`
- `top_underpromoted_domains`
- `top_overused_fallbacks`

Important:
if `composed_semantic` is not implemented yet, record it as `0` and use `discovery_only` counts to infer first `v0.9` targets.

Fallback quality classification:
- `raw_generic_fallback` = severe quality risk
- `customized_fallback_with_bespoke_copy` = lower risk
- `cluster_specific_fallback` = lower risk

Only `raw_generic_fallback` should heavily penalize `health_score`.

Aggregate outputs should include:
1. most frequent discovery gaps
2. most frequent raw generic fallback `public_main` owners
3. most common underpromoted domains
4. lowest health score charts
5. highest health score charts
6. top 20 grammar / archetype families to consider next
7. top 10 representative charts for next golden review
8. recommended `v0.9` addendum theme

## 14. Health Score Refinement

Suggested penalties:
- raw generic fallback in `public_main`
- support/detail empty despite rich candidate inventory
- missing domain flags
- chart-facts mismatch public risk
- duplicate headline/body
- `v8 hero / identity_axis` duplication
- semantically wrong public block
- `public_main` overcrowding by one technical family
- high non-public discovery count with no corresponding public candidate

Suggested bonuses:
- specific registry packet in `public_main`
- composed semantic candidate in `public_main`
- balanced domain representation
- support/detail populated
- chart-fact-validated `public_main`
- no duplicated public copy
- `v8 hero` and `identity_axis` distinct and domain-correct

Health score design note:
- do not over-penalize customized fallback that is still semantically usable
- do heavily penalize raw generic fallback ownership
- reward domain-correct specificity more than raw candidate count

## 15. v0.9 Rollout Guardrails

### 1. Composed candidates start as `debug / detail / support`

Composed semantic candidates in `v0.9` must not automatically become `public_main`.

Initial eligibility should be:
- `debug`
- `detail`
- `public_support`

`public_main` eligibility should require either:
- a stricter confidence / public-eligibility threshold
- or a dedicated feature flag

### 2. `source_type` is required

Every candidate / packet / cluster trace should expose `source_type`.

Allowed values:
- `exact_registry`
- `composed_semantic`
- `generic_fallback`
- `discovery_scaffold`
- `legacy_graph`

Audit rule:
- if `composed_semantic` is not implemented yet, batch audits should record it as `0`
- `discovery_scaffold` or `discovery_only` counts should be used to infer first grammar targets

### 3. Exact registry wins only when context-compatible

Exact registry should beat composed candidates only when:
- chart facts match
- domain role matches
- `public_job` matches
- cluster context supports the same meaning

If an exact packet is chart-fact correct but routed into the wrong domain or public role, a composed semantic candidate may be safer.

### 4. Registry promotion criteria

A composed semantic pattern should be promoted into registry only when:
- it appears across multiple charts
- chart facts are consistently safe
- domain routing is stable
- it reduces raw generic fallback usage
- public copy can reach SHOU quality
- accepted golden regressions stay stable
- `lived_scene` / `public_job` metadata is stable

Do not promote every composed candidate.

### 5. Fallback taxonomy

Not all fallback is equally risky.

Classify `fallback_public_main_quality` as:
- `raw_generic_fallback`: severe quality risk
- `customized_fallback_with_bespoke_copy`: lower risk
- `cluster_specific_fallback`: lower risk

Only `raw_generic_fallback` should heavily penalize `health_score`.

Example:
`career_career_visibility` can be:
- `raw_generic_fallback` if only generic title/body exists
- `customized_fallback_with_bespoke_copy` if it has chart-specific override
- `cluster_specific_fallback` if the id is generic but the cluster members make it chart-specific

### 6. Representative examples in 50-chart audit

For each top gap family, the 50-chart batch should include `2–3` representative chart excerpts.

Each excerpt should include:
- raw signature
- current public issue
- discovery candidate
- expected semantic family
- why it matters
- whether it should become a grammar candidate or registry archetype

## 16. 50-Chart Batch Audit Prompt

Ready-to-run Codex prompt:

```text
Run 50-chart Natal Discovery / Coverage Batch Audit.

Scope:
- no code changes
- no registry additions
- no renderer changes
- no selection tuning
- no public copy generation for every chart unless needed for diagnosis
- metrics only + representative examples

Use the live current pipeline with:
- ENABLE_NATAL_PROMISE_PROJECTION_V1=true
- ENABLE_NATAL_PROMISE_PACKET_DEBUG=true

Outputs:
- docs/system/batch_audits/natal_50_chart_discovery_coverage_audit.md
- backend/tests/_artifacts/natal_batch_audits/natal_50_chart_discovery_metrics.json

For each chart, return:
- chart_id / birth data
- candidate_packet_count
- unique_candidate_packet_count
- selected_packet_count
- public_main_count
- public_support_count
- detail_count
- fallback_public_main_count
- generic_public_main_count
- customized_fallback_public_main_count
- cluster_specific_fallback_count
- non_public_discovery_packet_count
- focus_map domains and tiers
- public_main_source_type distribution:
  - exact_registry
  - composed_semantic
  - generic_fallback
  - discovery_scaffold
  - discovery_only
  - legacy_graph
- missing_domain_flags
- coverage_warnings
- chart_facts_match_false_count
- duplicate_headline_count
- v8_duplication flag
- health_score
- top_discovery_gaps
- top_underpromoted_domains
- top_overused_fallbacks

Important:
- if composed_semantic is not implemented yet, record it as 0
- if composed_semantic is not implemented yet, use discovery_scaffold or discovery_only counts to infer first grammar targets
- classify fallback quality:
  - raw_generic_fallback
  - customized_fallback_with_bespoke_copy
  - cluster_specific_fallback
- only raw_generic_fallback should heavily penalize health_score

Aggregate:
1. most frequent discovery gaps
2. most frequent raw generic fallback public_main owners
3. most common underpromoted domains
4. lowest health score charts
5. highest health score charts
6. top 20 grammar / archetype families to consider next
7. top 10 representative charts for next golden review
8. recommended v0.9 addendum theme

For each top gap family, include `2–3` representative chart excerpts with:
- raw signature
- current public issue
- discovery candidate
- expected semantic family
- why it matters
- whether it should become a grammar candidate or registry archetype

Do not implement fixes.
This is audit only.
```

## 17. Phased Roadmap

### Short Term
1. `1997` final acceptance / commit
2. 50-chart batch audit
3. top fallback/gap report

### Medium Term
4. Compositional Semantic Grammar `v0.9`
5. specific composed candidate beats generic fallback
6. generic fallback suppression rules

### Then
7. 200-chart batch audit
8. repeated composed patterns -> registry promotion
9. transit activation over `NatalPromiseClusterPlan`

### Long Term
10. Transit / period system activates natal promise clusters

Example trajectory:

`Neptune square Sun`
-> `identity/self-construction cluster`
-> soften/dissolve
-> `güçlü görünmek için kullandığın eski yollar yumuşuyor`

## 18. Risks / Anti-goals

Risks:
- grammar becomes another hidden generic fallback engine
- composed candidates become public too early
- registry override logic becomes too aggressive
- domain routing becomes unstable across similar charts
- health score over-penalizes customized fallback that is still semantically usable

Anti-goals:
- do not replace the current registry
- do not remove ClusterPlan as selector
- do not let renderer invent meaning
- do not flood public surfaces with debug discovery scaffolds
- do not optimize only for mixed charts at the expense of accepted goldens

## 19. Open Questions

- What confidence threshold should a composed semantic candidate need before `public_support`?
- Should composed candidates first enter `detail` only before `public_main`?
- How should `domain_reason` be weighted when a candidate could belong to relationship and career?
- Should `lived_scene_atoms` be grammar-generated, registry-seeded, or hybrid?
- How should registry override precedence interact with chart spine or contradiction signatures?
- When should repeated composed patterns be promoted into exact registry archetypes?
- Which fallback categories are acceptable in `public_main` and which are release blockers?

## 20. Final Statement

This system is no longer just a registry of hand-written archetypes.
It is becoming a layered semantic engine.

The registry should remain SHOU’s quality memory.
Compositional grammar should become the dynamic meaning layer.
ClusterPlan should remain the public-surface selector.
Renderer should remain the language layer.

The next strategic goal is to reduce raw generic fallback ownership in ordinary charts without sacrificing truthfulness, specificity, or SHOU voice quality.
