# Istanbul 1997 ClusterPlan Audit - after P0 truthfulness fix

Chart: `1997-01-21 10:30 Istanbul, TR`

Scope:
- P0 truthfulness suppression applied.
- No semantic coverage addendum applied.
- No selection/scoring changes beyond P0 suppression.
- Generated from live route-equivalent `interpret_natal_chart_ui`.

Artifacts:
- Raw debug artifact: `backend/tests/_artifacts/natal_interpret_full_1997-01-21_10-30_istanbul_user_compact_debug.json`
- Public-surface snapshot: `docs/system/_generated_outputs/fresh_natal_interpret_ui_1997-01-21_10-30_istanbul_after_p0_truthfulness_fix_public_surfaces.json`

Important distinction:
- The raw debug artifact intentionally retains suppressed false-anchor packet labels in `candidate_packets` for debug/transit activation.
- Public grep checks were run against the rendered public-surface snapshot, not against debug inventory.

## Stale Artifact Confirmation

The pre-P0 leakage came from stale markdown/snapshot output, not from the current live public projection. The live public-surface snapshot regenerated after the P0 fix has zero matches for the four requested forbidden phrases.

## 1. candidate_inventory

Full live candidate list, public-safe view:

| packet_id | domain | promise_type | strength | priority | chart_facts_match | public status |
|---|---:|---:|---:|---:|---:|---|
| `career_career_visibility` | career | career_signature | 1.0000 | 1.0791 | n/a | public_main |
| `career_career_visibility_aux` | career | career_signature | 1.0000 | 1.0791 | n/a | duplicate suppressed from public_main; kept detail/modifier/debug/transit |
| `career_career_visibility_aux` | career | career_signature | 1.0000 | 1.0791 | n/a | duplicate inventory row |
| `mind_mind_system` | mind | mind_style | 1.0000 | 1.3636 | n/a | public_main / v8 hero |
| `mind_mind_system_aux` | mind | mind_style | 1.0000 | 1.3636 | n/a | duplicate suppressed from public_main; kept detail/modifier/debug/transit |
| `mind_mind_system_aux` | mind | mind_style | 1.0000 | 1.3636 | n/a | duplicate inventory row |
| `relationship_relationships` | relationship | love_style | 1.0000 | 1.2823 | n/a | public_main |
| `relationship_relationships_aux` | relationship | love_style | 1.0000 | 1.2823 | n/a | duplicate suppressed from public_main; kept detail/modifier/debug/transit |
| `relationship_relationships_aux` | relationship | love_style | 1.0000 | 1.2823 | n/a | duplicate inventory row |
| `saturn_sextile_uranus_structured_originality_chart_exact` | mind | gift | 1.0000 | 1.1301 | false | suppressed; debug/transit only |
| `saturn_sextile_uranus_structured_originality_identity_chart_exact` | identity | gift | 1.0000 | 1.0801 | false | suppressed; debug/transit only |
| `saturn_trine_pluto_deep_resilience_chart_exact` | identity | gift | 1.0000 | 1.2200 | n/a | public_main / v8 identity_axis |
| `mercury_conjunct_venus_refined_relational_language_chart_exact` | communication | gift | 0.9988 | 0.9988 | n/a | detail / extra / v8 differentiator |

False-anchor packet note:
- The two Saturn-Uranus structured-originality packets are still present in debug candidate inventory, but both have `chart_facts_match=false`.
- Their placement-specific false anchors are not rendered in public surfaces.

## 2. selected packets

The live plan does not emit a separate `selected_packets` field. Selection is materialized through `surface_plan` and rendered public blocks.

Public-facing selected packet ids:
- `career_career_visibility`
- `relationship_relationships`
- `mind_mind_system`
- `saturn_trine_pluto_deep_resilience_chart_exact`
- `mercury_conjunct_venus_refined_relational_language_chart_exact`

Suppressed from public despite inventory presence:
- `saturn_sextile_uranus_structured_originality_chart_exact`
- `saturn_sextile_uranus_structured_originality_identity_chart_exact`

## 3. focus_map

| domain | tier | score | packet_ids |
|---|---:|---:|---|
| career | strong | 1.0000 | `career_career_visibility`, `career_career_visibility_aux`, `career_career_visibility_aux` |
| relationship | strong | 1.0000 | `relationship_relationships`, `relationship_relationships_aux`, `relationship_relationships_aux` |
| mind | strong | 0.9871 | `mind_mind_system`, `mind_mind_system_aux`, `mind_mind_system_aux`, `mercury_conjunct_venus_refined_relational_language_chart_exact` |
| identity | detail_only | 0.4018 | `saturn_trine_pluto_deep_resilience_chart_exact` |

## 4. clusters

| cluster_id | domain | main_packet_id | target_surface_role | strength |
|---|---:|---|---:|---:|
| `career_career_like_career_career_visibility` | career | `career_career_visibility` | public_main | 0.7953 |
| `mind_mind_like_mind_mind_system` | mind | `mind_mind_system` | public_main | 0.7925 |
| `relationship_love_like_relationship_relationships` | relationship | `relationship_relationships` | public_main | 0.7953 |
| `identity_gift_like_saturn_trine_pluto_deep_resilience_chart_exact` | identity | `saturn_trine_pluto_deep_resilience_chart_exact` | public_main | 0.5171 |
| `mind_gift_like_mercury_conjunct_venus_refined_relational_language_chart_exact` | communication | `mercury_conjunct_venus_refined_relational_language_chart_exact` | detail | 0.6458 |

## 5. public_main / public_support / detail

public_main:
- `career_career_like_career_career_visibility`
- `relationship_love_like_relationship_relationships`
- `mind_mind_like_mind_mind_system`
- `identity_gift_like_saturn_trine_pluto_deep_resilience_chart_exact`

public_support:
- none

detail:
- `mind_gift_like_mercury_conjunct_venus_refined_relational_language_chart_exact`

## 6. suppressed packets

| packet_id | reason | keep_for | suppressed_from_public_main |
|---|---|---|---:|
| `saturn_sextile_uranus_structured_originality_chart_exact` | packet encodes chart facts that do not match this chart | debug, transit_activation | true |
| `saturn_sextile_uranus_structured_originality_identity_chart_exact` | packet encodes chart facts that do not match this chart | debug, transit_activation | true |
| `career_career_visibility_aux` | weaker duplicate for the same domain card job and lived scene | detail, modifier, debug, transit_activation | true |
| `relationship_relationships_aux` | weaker duplicate for the same domain card job and lived scene | detail, modifier, debug, transit_activation | true |
| `mind_mind_system_aux` | weaker duplicate for the same domain card job and lived scene | detail, modifier, debug, transit_activation | true |

## 7. profile_narrative_projection_v1 core/extra blocks

Core blocks:
- `promise::career_career_visibility` - "Perde acilmadan once iceride uzun bir son prova olur."
- `promise::relationship_relationships` - "Sen iliskide yuzeysel bir sicakliktan cok, icine oturan bir guven ariyorsun."
- `promise::mind_mind_system` - "Ne yapacagini bildigin an tempo kendiliginden yukselir."
- `promise::saturn_trine_pluto_deep_resilience_chart_exact` - "Zorlandiginda bile dagilip gitmeyen, iceride yapi kuran bir gucun var."

Extra blocks:
- `promise::mercury_conjunct_venus_refined_relational_language_chart_exact` - "Kelimeler sende sadece anlatmak icin degil, bag kurmak icin de calisabilir."

Detail cards:
- `promise::career_career_visibility`
- `promise::relationship_relationships`
- `promise::mind_mind_system`
- `promise::saturn_trine_pluto_deep_resilience_chart_exact`
- `promise::mercury_conjunct_venus_refined_relational_language_chart_exact`

## 8. profile_v8_projection_v1 surfaces

hero:
- node: `promise::mind_mind_system`
- headline: "Ne yapacagini bildigin an tempo kendiliginden yukselir."
- summary gist: Aries rising plus Mars in Libra 6H; direct outer tempo with internal balancing/control.

identity_axis:
- node: `promise::saturn_trine_pluto_deep_resilience_chart_exact`
- headline: "Zorlandiginda bile dagilip gitmeyen, iceride yapi kuran bir gucun var."
- summary gist: pressure, structure, resilience, Saturn-Pluto support, Sun-Saturn friction.

insight_strip:
- `promise::relationship_relationships` - relationship trust and Libra 7H/Venus 10H line.
- `promise::mind_mind_system_aux` - Aries rising plus Mars Libra 6H line.
- `promise::career_career_visibility` - Saturn 12H Aries plus Capricorn MC career visibility line.

differentiators:
- `promise::relationship_relationships_aux` - relationship security threshold.
- `promise::mercury_conjunct_venus_refined_relational_language_chart_exact` - refined relational language.
- `promise::career_career_visibility_aux` - invisible preparation before public visibility.

## 9. exact truthfulness scan

Grep target:
- `docs/system/_generated_outputs/fresh_natal_interpret_ui_1997-01-21_10-30_istanbul_after_p0_truthfulness_fix_public_surfaces.json`

Result:
- Requested forbidden Turkish rising label: zero hits.
- Requested forbidden Saturn third-house label: zero hits.
- Requested forbidden Uranus first-house label: zero hits.
- Requested forbidden English meta label: zero hits.

Validation:
- Targeted regression: `backend/tests/test_natal_promise_cluster_plan.py::test_natal_promise_cluster_plan_istanbul_1997_truthfulness_guards_block_false_saturn_uranus_packets` passed.

## 10. remaining missing signatures

Still missing or under-read because no semantic coverage addendum has been applied:
- Moon Cancer IC / home security: not publicly centered.
- Mercury Capricorn MC / public voice: under-read; Mercury-Venus communication appears, but MC/public voice axis is not explicit enough.
- Moon-Mercury opposition across IC/MC: present as technical support in cluster anchors, but not narratively centered.
- Sun Aquarius 11H collective identity: still not surfaced as a public identity theme.
- Aries ASC -> Mars Libra 6H action-through-balance: surfaced in hero/mind, but still copy-light and grammatically rough.
- Mars opposite Saturn action restraint: appears only inside resilience identity packet support, not as its own clear action-restraint axis.
- Libra DSC + Chiron Scorpio 7H relationship harmony + wound/depth: relationship output uses Libra/Venus trust language, but Chiron/depth is not covered.
- Saturn Aries 12H private pressure: appears in career visibility and v8 differentiator, but not yet semantically deep enough.

## 11. verdict

Accepted golden?
- No. P0 truthfulness is fixed, but semantic coverage remains incomplete.

Needs semantic coverage addendum?
- Yes. The public projection is now truth-safe, but still misses several chart-defining signatures.

Needs only copy polish?
- No. There are copy polish issues, but the main remaining problem is semantic coverage.

Suggested next action:
- Add a semantic coverage addendum for Istanbul 1997 after keeping the P0 truthfulness guard unchanged.
