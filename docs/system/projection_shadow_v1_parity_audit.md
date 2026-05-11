# Projection Shadow V1 Parity Audit

Date: 2026-04-24  
Scope: Phase 1 shadow outputs, no code changes.

## Method
- Fresh natal public payload generated with `include_full_profile=true` so both legacy and projection branches are present.
- Request: `birth_date=1996-12-28`, `birth_time=07:10`, `birth_place=Istanbul, TR`, `locale=tr`.
- Source payload: `/tmp/projection_shadow_v1_parity_payload.json`
- Compared pairs:
  - `profile_narrative` vs `profile_narrative_projection_v1`
  - `profile_v8` vs `profile_v8_projection_v1`

## Snapshot

| Metric | Legacy | Projection |
|---|---:|---:|
| profile_narrative blocks | 7 | 10 |
| profile_narrative detail_cards | 12 | 10 |
| profile_narrative insight_modules | 1 | 0 |
| profile_narrative avg body chars | 383.4 | 78.2 |
| profile_narrative avg detail blocks/card | 6.83 | 3.5 |
| profile_v8 sections present | 16 | 4 |
| profile_v8 completeness ratio | 1.00 | 0.25 |

## 1) profile_narrative vs profile_narrative_projection_v1

### Semantic coverage
- Projection keeps semantic linkage to graph nodes (`node_id`) and evidence (`evidence_ids`) for all projected blocks.
- Traceability ratio: `10/10 = 1.0`.
- Coverage breadth is numerically high (10 projected blocks), but semantic framing drifts from legacy editorial families.

### Editorial quality and text richness
- Legacy body richness is much higher (`avg_body_chars=383.4` vs `78.2`).
- Legacy detail depth is higher (`avg_detail_blocks_per_card=6.83` vs `3.5`).
- Projection blocks are mostly short, atomic statements; many read as label+signal instead of multi-claim narrative cards.
- `insight_modules` is present in legacy and absent in projection (`1` -> `0`).

### Completeness and structural quality
- Structural issue found: projected block IDs collide heavily (10 blocks, only 5 unique IDs).
- This creates card identity ambiguity for downstream ordering/dedupe/render anchors.

### Missing domains/layers
- Graph has domains: `emotional, general, identity, life_direction, mind, relationships`
- Projection-selected domains: `general, relationships`
- Missing domains in projection selection: `emotional, identity, life_direction, mind`
- Missing primary layer in projection selection: `mechanism`

### Projected block classification
| Projected Block ID | Headline | Classification | node_id | evidence_ids | Notes |
|---|---|---|---|---:|---|
| `mg_mgv11_node_0` | Merkür 1. Ev Shadow | structurally incomplete | `mgv11_node_028e03d9e37d278a` | 4 | ID collision (3 blocks share `mg_mgv11_node_0`) |
| `mg_mgv11_node_0` | Neptün 1. Ev Potential | structurally incomplete | `mgv11_node_06023a111ee60643` | 5 | ID collision (3 blocks share `mg_mgv11_node_0`) |
| `mg_mgv11_node_1` | Satürn Koç Shadow | editorially too flat | `mgv11_node_172131a14843b858` | 3 | Very low overlap and compressed copy (similarity=0.036) |
| `mg_mgv11_node_4` | Neptün 1. Ev Shadow | structurally incomplete | `mgv11_node_414ac9bd7fd11411` | 5 | ID collision (3 blocks share `mg_mgv11_node_4`) |
| `mg_mgv11_node_0` | Jüpiter 1. Ev | structurally incomplete | `mgv11_node_0a534584b578ee46` | 3 | ID collision (3 blocks share `mg_mgv11_node_0`) |
| `mg_mgv11_node_2` | Uranüs 1. Ev Potential | editorially too flat | `mgv11_node_29cfef067fc18550` | 4 | Very low overlap and compressed copy (similarity=0.056) |
| `mg_mgv11_node_4` | Micro Insight | structurally incomplete | `mgv11_node_47939c5854144d15` | 2 | ID collision (3 blocks share `mg_mgv11_node_4`) |
| `mg_mgv11_node_4` | Venüs 12. Ev Shadow | structurally incomplete | `mgv11_node_4a0aaf3579c83b1a` | 5 | ID collision (3 blocks share `mg_mgv11_node_4`) |
| `mg_mgv11_node_5` | Jüpiter Oğlak | structurally incomplete | `mgv11_node_5384ef6054891ad9` | 3 | ID collision (2 blocks share `mg_mgv11_node_5`) |
| `mg_mgv11_node_5` | Uranüs 1. Ev | structurally incomplete | `mgv11_node_5472d245f4d29506` | 4 | ID collision (2 blocks share `mg_mgv11_node_5`) |

### Verdict (profile_narrative projection parity)
- **Over-flattening risk: High.**
- **Can replace legacy now? No.**
- **Can replace later? Yes, but only after:**
  - ID collision fix,
  - deeper editorial composition (teaser/body/detail cadence),
  - domain/layer coverage balancing,
  - restoring module-level richness (e.g., insight module equivalents).

## 2) profile_v8 vs profile_v8_projection_v1

### Semantic coverage
- Traceability ratio: `8/8 = 1.0`.
- Projection carries clean node/evidence trace per emitted section item.

### Editorial quality and text richness
- Identity axis body compression: legacy `483` chars vs projection `67` chars.
- Hero editorial/context contract is not parity-equivalent.
  - Legacy hero keys: `display_name, followers_text, forum_status_text, location_age, moon_sign, rising_sign, sun_sign`
  - Projection hero keys: `evidence_ids, headline, node_id, summary, trace`

### Section/block completeness
- Legacy sections present: `16`
- Projection sections present: `4`
- Completeness ratio: `0.25`
- Missing in projection:
  - `past_teaser`
  - `past_teasers`
  - `first_impression`
  - `talents`
  - `conversation_hooks`
  - `affects_you`
  - `defense`
  - `first_felt`
  - `intimacy`
  - `mind`
  - `mission_preview`
  - `archetype_portal`

### Projected section classification
| Projected Section | Classification | Notes |
|---|---|---|
| `hero` | structurally incomplete | Traceable but contract shape differs from legacy hero (sign/location/social fields missing). |
| `identity_axis` | missing important nuance | Section exists, but editorial depth/length is substantially compressed vs legacy. |
| `insight_strip` | weaker but acceptable | Section present with traceability; semantic snippets exist but expressive range is narrower. |
| `differentiators` | weaker but acceptable | Section present with traceability; still flatter and less socially contextual than legacy. |
| `past_teaser` | structurally incomplete | Present in legacy, absent in projection output. |
| `past_teasers` | structurally incomplete | Present in legacy, absent in projection output. |
| `first_impression` | structurally incomplete | Present in legacy, absent in projection output. |
| `talents` | structurally incomplete | Present in legacy, absent in projection output. |
| `conversation_hooks` | structurally incomplete | Present in legacy, absent in projection output. |
| `affects_you` | structurally incomplete | Present in legacy, absent in projection output. |
| `defense` | structurally incomplete | Present in legacy, absent in projection output. |
| `first_felt` | structurally incomplete | Present in legacy, absent in projection output. |
| `intimacy` | structurally incomplete | Present in legacy, absent in projection output. |
| `mind` | structurally incomplete | Present in legacy, absent in projection output. |
| `mission_preview` | structurally incomplete | Present in legacy, absent in projection output. |
| `archetype_portal` | structurally incomplete | Present in legacy, absent in projection output. |

### Verdict (profile_v8 projection parity)
- **Over-flattening risk: High.**
- **Can replace legacy now? No.**
- **Can replace later? Not with current Phase 1 shape; requires substantial section completeness + richer editorial projection layer.**

## Final readiness conclusion
- `profile_narrative_projection_v1`: **not yet** for UI replacement; useful as traceable shadow artifact for parity iteration.
- `profile_v8_projection_v1`: **not yet**; currently too incomplete to replace profile contract.
- Recommendation for Phase 1 remains: keep shadow outputs for comparison only, do not switch UI.
