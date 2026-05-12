# Izmir 1996-03-08 ClusterPlan Audit

- Generated: 2026-05-12
- Source artifact: `backend/tests/_artifacts/natal_interpret_full_1996-03-08_08-30_izmir_user_compact_debug.json`
- Public snapshot: `docs/system/_generated_outputs/fresh_natal_interpret_ui_1996-03-08_08-30_izmir.json`
- Request: `1996-03-08 08:30 Izmir, TR`
- Flags: `ENABLE_NATAL_PROMISE_PROJECTION_V1=true`, `ENABLE_NATAL_PROMISE_PACKET_DEBUG=true`
- Scope: analysis-only audit for a new chart. No selection, registry, or renderer changes were made in this pass.

## 1. Topline

This chart is on the cluster-plan path and does produce a valid
`natal_promise_cluster_plan_v1` projection. But it is not yet a healthy
golden.

What works:

- cluster-plan path activates correctly
- `source_graph == natal_promise_cluster_plan_v1`
- candidate inventory is not empty
- public-main cards are capped and suppression is functioning

What looks weak or wrong:

- candidate inventory is still thin and repetitive
- only `career`, `relationship`, and `mind` surface
- `identity` disappears from the focus map entirely
- public-main count is only `3`
- `public_support` is empty
- a 2020-specific Gemini-style copy override appears to leak onto this chart
- relationship copy mixes incompatible facts (`7. ev Yay` in body vs `7. ev Akrep` in chips/evidence)
- `profile_v8_projection_v1.hero` and `identity_axis` collapse onto the same mind family

Net assessment:

This is a good audit chart because it exposes two things clearly:

1. cluster selection is still too dependent on generic packet families
2. some packet-level copy overrides are not sufficiently chart-guarded

## 2. Projection Path

- `profile_narrative_projection_v1.source_graph`: `natal_promise_cluster_plan_v1`
- `profile_v8_projection_v1.source_graph`: `natal_promise_cluster_plan_v1`
- selected packet count: `3`
- cluster public-main count: `3`
- cluster detail count: `1`

This confirms the committed cluster-plan architecture is active for this
chart too; the issue here is output quality, not fallback failure.

## 3. Candidate Inventory

Raw candidate packet count in the cluster-plan payload: `10`

Important note:

- The raw list includes repeated `_aux` packet ids more than once.
- The effective debug packet inventory is `7` unique packet ids.
- So the candidate list looks broader numerically than it really is.

Candidate packets:

1. `career_career_visibility`
   - domain: `career`
   - promise_type: `career_signature`
   - strength: `1.0`
   - technical_anchors: `Satürn · 12. ev · Balık`, `MC Oğlak`, `Satürn 12. ev`
   - direct_meaning: `Perde açılmadan önce içeride uzun bir son prova olur.`

2. `career_career_visibility_aux`
   - domain: `career`
   - promise_type: `career_signature`
   - strength: `1.0`
   - technical_anchors: `Satürn · 12. ev · Balık`, `MC Oğlak`, `Satürn 12. ev`
   - direct_meaning: `Perde açılmadan önce içeride uzun bir son prova olur.`

3. `mind_mind_system`
   - domain: `mind`
   - promise_type: `mind_style`
   - strength: `1.0`
   - technical_anchors: `Venüs · 12. ev · Boğa`, `Yükselen Boğa`, `Venüs 12. ev`
   - direct_meaning: `Ne yapacağını bildiğin an tempo kendiliğinden yükselir.`

4. `mind_mind_system_aux`
   - domain: `mind`
   - promise_type: `mind_style`
   - strength: `1.0`
   - technical_anchors: `Venüs · 12. ev · Boğa`, `Yükselen Boğa`, `Venüs 12. ev`
   - direct_meaning: `Ne yapacağını bildiğin an tempo kendiliğinden yükselir.`

5. `relationship_relationships`
   - domain: `relationship`
   - promise_type: `love_style`
   - strength: `1.0`
   - technical_anchors: `Mars · 12. ev · Balık`, `7. ev Akrep`, `Mars 12. ev`
   - direct_meaning: `İnsanlar sende sıcaklıktan önce güven eşiğini hisseder.`

6. `relationship_relationships_aux`
   - domain: `relationship`
   - promise_type: `love_style`
   - strength: `1.0`
   - technical_anchors: `Mars · 12. ev · Balık`, `7. ev Akrep`, `Mars 12. ev`
   - direct_meaning: `İnsanlar sende sıcaklıktan önce güven eşiğini hisseder.`

7. `mercury_square_pluto_deep_mind_pressure_chart_exact`
   - domain: `mind`
   - promise_type: `wound_to_gift`
   - strength: `0.9536`
   - technical_anchors: `Merkür kare Plüton`, `Derin düşünce`
   - direct_meaning: `Zihin yüzeyde kalmak istemez; bir şeyi anlamak istediğinde köküne inene kadar bırakmak zor olabilir.`

Main candidate-inventory conclusion:

- inventory is effectively narrow
- no strong identity packet
- no richer relationship subtype split
- no second career subtype
- no supportive subtype diversity outside one mind-pressure packet

## 4. Focus Map

### career

- score: `1.0`
- tier: `strong`
- packet_ids:
  - `career_career_visibility`
  - `career_career_visibility_aux`
  - `career_career_visibility_aux`
- evidence_summary:
  - `chart ruler support`
  - `angular support`
  - `house-chain support`
  - `repeated packet support`
- scoring_breakdown:
  - `packet_strength_sum=1.0`
  - `chart_ruler=1.0`
  - `angularity=1.0`
  - `house_chain=1.0`
  - `repeated_support=0.4`

### relationship

- score: `1.0`
- tier: `strong`
- packet_ids:
  - `relationship_relationships`
  - `relationship_relationships_aux`
  - `relationship_relationships_aux`
- evidence_summary:
  - `chart ruler support`
  - `angular support`
  - `house-chain support`
  - `repeated packet support`
- scoring_breakdown:
  - `packet_strength_sum=1.0`
  - `chart_ruler=1.0`
  - `angularity=1.0`
  - `house_chain=1.0`
  - `repeated_support=0.4`

### mind

- score: `0.9726`
- tier: `strong`
- packet_ids:
  - `mind_mind_system`
  - `mind_mind_system_aux`
  - `mind_mind_system_aux`
  - `mercury_square_pluto_deep_mind_pressure_chart_exact`
- evidence_summary:
  - `chart ruler support`
  - `angular support`
  - `house-chain support`
  - `repeated packet support`
- scoring_breakdown:
  - `packet_strength_sum=1.0`
  - `chart_ruler=0.75`
  - `angularity=0.75`
  - `house_chain=0.75`
  - `repeated_support=0.8`
  - `archetype_confidence=0.2288`

Focus-map conclusion:

- the chart is being read as a three-domain chart
- `identity` is absent
- all three visible domains look over-inflated by repeated generic main/aux packet families

## 5. Clusters

### `career_career_like_career_career_visibility`

- domain: `career`
- cluster_strength: `0.7953`
- target_surface_role: `public_main`
- main_packet_id: `career_career_visibility`
- members:
  - `career_career_visibility` as `primary_anchor`
  - `career_career_visibility_aux` as `modifier`
- notes:
  - `strong focus-map domain`
  - `has reusable sub-angles for detail`

### `relationship_love_like_relationship_relationships`

- domain: `relationship`
- cluster_strength: `0.7953`
- target_surface_role: `public_main`
- main_packet_id: `relationship_relationships`
- members:
  - `relationship_relationships` as `primary_anchor`
  - `relationship_relationships_aux` as `modifier`
- notes:
  - `strong focus-map domain`
  - `has reusable sub-angles for detail`

### `mind_mind_like_mind_mind_system`

- domain: `mind`
- cluster_strength: `0.7893`
- target_surface_role: `public_main`
- main_packet_id: `mind_mind_system`
- members:
  - `mind_mind_system` as `primary_anchor`
  - `mind_mind_system_aux` as `modifier`
- notes:
  - `strong focus-map domain`
  - `hero-capable cluster`
  - `has reusable sub-angles for detail`

### `mind_wound_like_mercury_square_pluto_deep_mind_pressure_chart_exact`

- domain: `mind`
- cluster_strength: `0.6426`
- target_surface_role: `detail`
- main_packet_id: `mercury_square_pluto_deep_mind_pressure_chart_exact`
- members:
  - `mercury_square_pluto_deep_mind_pressure_chart_exact` as `primary_anchor`

Cluster conclusion:

- clustering itself is coherent
- the problem is upstream packet richness and downstream copy mapping
- main-feed diversity is weak because each public-main cluster is still a generic base family

## 6. Surface Plan

- public_main_cluster_ids:
  - `career_career_like_career_career_visibility`
  - `relationship_love_like_relationship_relationships`
  - `mind_mind_like_mind_mind_system`
- public_support_cluster_ids:
  - none
- detail_cluster_ids:
  - `mind_wound_like_mercury_square_pluto_deep_mind_pressure_chart_exact`
- debug_packet_ids:
  - `career_career_visibility`
  - `career_career_visibility_aux`
  - `mercury_square_pluto_deep_mind_pressure_chart_exact`
  - `mind_mind_system`
  - `mind_mind_system_aux`
  - `relationship_relationships`
  - `relationship_relationships_aux`

Surface conclusion:

- public-main is underfilled at `3`
- support is empty
- detail is almost empty
- this is not yet golden-grade surface diversity

## 7. Suppression

Suppressed packets are structurally kept correctly:

- `career_career_visibility_aux`
- `relationship_relationships_aux`
- `mind_mind_system_aux`

All three remain available for:

- `detail`
- `modifier`
- `debug`
- `transit_activation`

This part behaves as intended.

## 8. Public Surface Snapshot

### `profile_narrative_projection_v1.core_blocks`

1. `promise::career_career_visibility`
   - headline: `Perde açılmadan önce içeride uzun bir son prova olur.`
   - issue: body repeats the same core sentence multiple times and ends in a stitched instructional sentence

2. `promise::relationship_relationships`
   - headline: `Sen ilişkide yüzeysel bir sıcaklıktan çok, içine oturan bir güven arıyorsun.`
   - issue: body says `7. evinin Yay'da açılması`, but the packet chips/evidence say `7. ev Akrep`

3. `promise::mind_mind_system`
   - headline: `Ne yapacağını bildiğin an tempo kendiliğinden yükselir.`
   - issue: body says `Yükseleninin İkizler`, while chips/evidence on this chart point to `Yükselen Boğa`

### `profile_narrative_projection_v1.extra_blocks`

1. `promise::mercury_square_pluto_deep_mind_pressure_chart_exact`
   - headline: `Zihnin bir konunun yüzeyinde kalmak istemeyebilir.`
   - issue: body opener still contains broken join grammar:
     - `Merkür kare Plüton kadar Derin düşünce de ...`

### `profile_v8_projection_v1`

- hero:
  - `promise::mind_mind_system`
  - same Gemini-specific body leak appears here
- identity_axis:
  - `promise::mind_mind_system_aux`
  - duplicates the hero family instead of surfacing a distinct identity cluster
- insight_strip:
  - relationship / career / mind-pressure
- differentiators:
  - repeat the same generic packet families
  - career differentiator repeats the core career headline verbatim
  - mind differentiator repeats the core mind headline verbatim

## 9. Key Problems Exposed By This Chart

### 1. Chart-specific override leak

The most serious issue in this audit is that a mind packet is rendered using
Gemini-specific prose on a chart whose packet anchors still say `Yükselen
Boğa`.

This means at least one public-copy override is not sufficiently gated by the
exact chart signature that justified it on another golden chart.

### 2. Relationship copy fact drift

Relationship copy mixes:

- chips/evidence: `7. ev Akrep`
- body prose: `7. evinin Yay'da açılması`

That is semantically unsafe and should block this chart from being accepted as
a golden without a fix.

### 3. Identity disappearance

Even if the chart genuinely centers career / mind / relationship, a full
absence of `identity` makes the surface feel thin. This chart needs a check on
whether identity packet coverage is missing or whether existing packets are
being over-grouped into mind.

### 4. Candidate inflation without real diversity

`candidate_packet_count=10` looks healthier than it is. In practice the audit
shows only:

- one career family
- one relationship family
- one generic mind family
- one mind-pressure detail packet

So the inventory is still semantically small.

### 5. v8 duplication

`hero` and `identity_axis` should not collapse onto the same main family when
the surface is already this thin. Even if the cluster plan is valid, the v8
selector here is not producing a high-value distinct identity axis.

## 10. Verdict

This chart is useful as a stress-test audit, but it is **not an accepted
golden** in its current state.

Why:

- cluster-plan path works
- suppression works
- debug traceability is present

But:

- packet richness is too narrow
- `identity` disappears
- public copy leaks wrong chart facts
- v8 hero / identity_axis collapse onto the same family

If we continue from this chart later, the first review target should be:

1. chart-guarding of packet-specific copy overrides
2. why `mind_mind_system` is inheriting Gemini-specific prose here
3. why relationship body drifts from `Akrep` to `Yay`
4. whether this chart needs additive registry coverage or just safer routing
