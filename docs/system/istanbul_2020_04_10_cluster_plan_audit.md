# Istanbul 2020-04-10 ClusterPlan Audit

- Generated: 2026-05-11
- Birth data: `2020-04-10 08:26`, `Istanbul, TR`
- Flags: `ENABLE_NATAL_PROMISE_PROJECTION_V1=true`, `ENABLE_NATAL_PROMISE_PACKET_DEBUG=true`
- Source artifact: `backend/tests/_artifacts/natal_interpret_full_2020-04-10_08-26_istanbul_user_compact_debug.json`
- Public payload snapshot: `docs/system/_generated_outputs/fresh_natal_interpret_ui_2020-04-10_08-26_istanbul.json`
- Build path: raw natal response -> `build_public_natal_view(..., include_debug=True, include_full_profile=True)` -> packet builders -> cluster plan -> projection builders

## 1. Chart snapshot

- Sun: `Koç 12. ev`
- Moon: `Akrep 6. ev`
- Mercury: `Balık 11. ev`
- Venus: `İkizler 1. ev`
- Mars: `Kova 10. ev`
- Jupiter: `Oğlak 9. ev`
- Saturn: `Kova 9. ev`
- Pluto: `Oğlak 9. ev`
- Ascendant: `İkizler`

Notable raw-chart signatures that exist in the artifact but do **not** meaningfully surface in the current ClusterPlan:

- `Sun square Jupiter`
- `Sun square Pluto`
- `Moon trine Neptune`
- `Moon sextile Jupiter`
- `Moon sextile Pluto`
- `Mercury sextile Jupiter`
- `Mercury sextile Saturn`
- `Mercury sextile Pluto`
- `Venus 1H Gemini`
- `Mars 10H Aquarius`

## 2. Candidate inventory

Current inventory is thin and duplicate-heavy.

- candidate packet count: `7`
- selected packet count: `3`
- unique candidate ids: `5`
- selected ids: `career_career_visibility`, `mind_mind_system`, `relationship_relationships`

### Candidate packets

| id | domain | promise_type | strength | technical_anchors | direct_meaning |
|---|---|---:|---:|---|---|
| `career_career_visibility` | career | `career_signature` | `1.00` | `Satürn 9H Kova`, `MC Kova`, `10th house ruler route` | `İnsanlar önce kalite çıtasını, sonra etkini görür.` |
| `career_career_visibility_aux` | career | `career_signature` | `1.00` | `Satürn 9H Kova`, `MC Kova`, `10th house ruler route` | `İnsanlar önce kalite çıtasını, sonra etkini görür.` |
| `career_career_visibility_aux` | career | `career_signature` | `1.00` | `Satürn 9H Kova`, `MC Kova`, `10th house ruler route` | `İnsanlar önce kalite çıtasını, sonra etkini görür.` |
| `mind_mind_system` | mind | `mind_style` | `1.00` | `Merkür 11H Balık`, `Yükselen İkizler`, `ASC angle` | `Ne yapacağını bildiğin an tempo kendiliğinden yükselir.` |
| `mind_mind_system_aux` | mind | `mind_style` | `1.00` | `Merkür 11H Balık`, `Yükselen İkizler`, `ASC angle` | `Ne yapacağını bildiğin an tempo kendiliğinden yükselir.` |
| `mind_mind_system_aux` | mind | `mind_style` | `1.00` | `Merkür 11H Balık`, `Yükselen İkizler`, `ASC angle` | `Ne yapacağını bildiğin an tempo kendiliğinden yükselir.` |
| `relationship_relationships` | relationship | `love_style` | `0.52` | `Jüpiter 9H Oğlak`, `7H Yay` | `Yakınlık burada hafif ilerlemez; bir anda derine çekilir.` |

## 3. Focus map

| domain | score | tier | packet_ids | read |
|---|---:|---|---|---|
| `career` | `1.0000` | `strong` | `career_career_visibility`, duplicated aux variants | Career/visibility line dominates because the builder finds repeated ruler-route support around `MC Kova + Satürn 9H`. |
| `mind` | `0.8714` | `strong` | `mind_mind_system`, duplicated aux variants | Mind also scores as chart-defining via `Mercury 11H Pisces + Gemini ASC`, but it currently collapses into one repeated phrasing family. |
| `relationship` | `0.3861` | `detail_only` | `relationship_relationships` | Relationship exists, but only as one thin packet anchored to `7H Yay + Jupiter 9H Capricorn`; the richer emotional signatures do not surface. |

Scoring notes from raw traceability:

- `career` gets full marks from `packet_strength_sum`, `chart_ruler`, `angularity`, and `house_chain`.
- `mind` also maxes `packet_strength_sum`, `chart_ruler`, and `angularity`, but has no `house_chain`.
- `relationship` has `luminary` + `angularity`, but low packet strength and no repeated support.

## 4. Clusters

### 4.1 `career_career_like_career_career_visibility`

- domain: `career`
- cluster_strength: `0.7953`
- target_surface_role: `public_main`
- main_packet_id: `career_career_visibility`
- members:
  - `career_career_visibility` -> `primary_anchor`
  - `career_career_visibility_aux` -> `modifier`
- distinct_lived_scene:
  `MC Kova` is being read as visibility through independence, originality, and a composed public tone.

### 4.2 `mind_mind_like_mind_mind_system`

- domain: `mind`
- cluster_strength: `0.7670`
- target_surface_role: `public_main`
- main_packet_id: `mind_mind_system`
- members:
  - `mind_mind_system` -> `primary_anchor`
  - `mind_mind_system_aux` -> `modifier`
- distinct_lived_scene:
  `Gemini ASC + Mercury Pisces 11H` is being read as fast outer curiosity with a more porous, internally edited mind.

### 4.3 `relationship_love_like_relationship_relationships`

- domain: `relationship`
- cluster_strength: `0.5136`
- target_surface_role: `public_main`
- main_packet_id: `relationship_relationships`
- members:
  - `relationship_relationships` -> `primary_anchor`
- distinct_lived_scene:
  `7H Yay + Jupiter 9H Capricorn` is being read as wanting spaciousness, honesty, and a bond that still feels substantial.

## 5. Surface plan

- public_main_cluster_ids:
  - `career_career_like_career_career_visibility`
  - `mind_mind_like_mind_mind_system`
  - `relationship_love_like_relationship_relationships`
- public_support_cluster_ids: `[]`
- detail_cluster_ids: `[]`
- debug_packet_ids count: `5`

Read: the plan collapses to **3 main / 0 support / 0 detail**. For this chart, that is a structural signal that the current packet inventory is not broad enough yet.

## 6. Anchor reuse

The most important reuse fact in this chart is not over-budget explicit anchor repetition; it is **cross-surface duplication** around the same thin packet families.

- `composure_vs_internal_pressure` is reused across both `career` and `mind` clusters and reaches `public_main_explicit_uses = 2`, exactly at budget.
- `MC Kova` and `Satürn 9H Kova` are only used once in `public_main`, so anchor budget is technically respected.
- `Gemini ASC / Mercury 11H Pisces` anchors are also within budget.

This chart's current problem is therefore **not** anchor-budget overflow. It is lack of domain breadth and too much semantic reuse from too few packets.

## 7. Projection outputs

## 7.1 `profile_narrative_projection_v1`

- source_graph: `natal_promise_cluster_plan_v1`
- core block count: `3`
- extra block count: `0`

Core blocks:

1. `career_career_visibility`
   - headline: `İnsanlar önce kalite çıtasını, sonra etkini görür.`
2. `mind_mind_system`
   - headline: `Ne yapacağını bildiğin an tempo kendiliğinden yükselir.`
3. `relationship_relationships`
   - headline: `Sen ilişkide yüzeysel bir sıcaklıktan çok, içine oturan bir güven arıyorsun.`

Important renderer note:

- `source_cluster_id` is `null` on all three rendered core blocks in this payload.

## 7.2 `profile_v8_projection_v1`

- source_graph: `natal_promise_cluster_plan_v1`
- hero: `mind_mind_system`
- identity_axis: `mind_mind_system_aux`

Insight strip:

1. `career` -> `İnsanlar önce kalite çıtasını, sonra etkini görür.`
2. `relationship` -> `Sen ilişkide sadece biriyle olmak istemiyorsun.`
3. `career` -> `İnsanlar önce kalite çıtasını, sonra etkini görür.`

Differentiators:

1. `mind_mind_system`
2. `mind_mind_system_aux`
3. `career_career_visibility`

Read: v8 currently over-reuses the same `mind` and `career` packets. This is visible even without deep scoring inspection.

## 8. Audit findings

### 8.1 What is working

- ClusterPlan path is active on a non-golden chart.
- Career and mind do surface as strong domains.
- Relationship is not fully lost; it still becomes a public-main card.
- Public-main count is conservative at `3`, so there is no crowding.

### 8.2 What is weak

1. Candidate inventory is still too small for this chart.
   Current inventory is `7`, with only `5` unique ids and heavy aux duplication.

2. Identity is missing.
   This chart has `Gemini ASC` and `Venus 1H Gemini`, but no identity-family cluster survives into the plan.

3. Emotional depth is under-read.
   `Moon Scorpio 6H`, `Moon trine Neptune`, `Moon sextile Jupiter/Pluto` do not become distinct emotional or attachment packets.

4. Pressure / transformation is under-read.
   `Sun square Jupiter`, `Sun square Pluto`, and the 9H Capricorn/Aquarius stack do not form a separate resilience or intensity packet family.

5. Support/detail architecture is empty.
   The plan produces `0` support and `0` detail clusters, which means overflow routing is not helping this chart yet.

6. V8 selection visibly duplicates meaning.
   `hero` and `identity_axis` are both mind-family; insight strip repeats career; differentiators repeat the exact same mind sentence family.

7. Renderer provenance is incomplete.
   `source_cluster_id` is `null` on rendered narrative core blocks.

## 9. Structural takeaway for next ClusterPlan passes

This chart is useful because it stresses a different shape than the 1996 Istanbul golden:

- airy/future-facing career-visibility line: `MC Kova + Mars 10H Aquarius + Saturn 9H Aquarius`
- mutable/social/sezgisel mind line: `Gemini ASC + Mercury Pisces 11H + Neptune Pisces 11H`
- hidden/private fire line: `Sun Aries 12H`
- intense emotional-regulation line: `Moon Scorpio 6H`
- visible charm/identity line: `Venus Gemini 1H`

Current ClusterPlan only captures the first two cleanly, and relationship in a thin form. It does **not** yet express:

- private will / inner fire (`Sun 12H Aries`)
- identity/playfulness/social signal (`Venus 1H Gemini`)
- emotional depth / porousness (`Moon Scorpio`, `Moon-Neptune`)
- pressure-resilience / transformation (`Sun-Pluto`, 9H Capricorn/Aquarius stack)

So this chart should be treated as a useful expansion case for:

- identity-family recovery
- emotional-world and relationship subtype splitting
- support/detail overflow generation on non-golden charts
- v8 anti-duplication rules
