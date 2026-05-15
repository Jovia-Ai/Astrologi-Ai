# Istanbul 1997 ClusterPlan Audit - after v0.8 overlay

Chart: `1997-01-21 10:30 Istanbul, TR`

Scope:
- P0 truthfulness guard preserved.
- v0.8 Aries/Cancer-IC/Capricorn-MC/Aquarius-11H semantic coverage applied.
- Generated from live route-equivalent `interpret_natal_chart_ui`.

Artifacts:
- Raw debug artifact: `backend/tests/_artifacts/natal_interpret_full_1997-01-21_10-30_istanbul_user_compact_debug.json`
- Public-surface snapshot: `docs/system/_generated_outputs/fresh_natal_interpret_ui_1997-01-21_10-30_istanbul_after_v0_8_public_surfaces.json`

## candidate_inventory

| packet_id | domain | promise_type | strength | chart_facts_match |
|---|---:|---:|---:|---:|
| `aquarius_11h_future_collective_signal_chart_exact` | community | community_signature | 1.0000 | true |
| `aries_asc_mars_libra_6h_action_through_balance_chart_exact` | action | identity_action_style | 1.0000 | true |
| `capricorn_10h_mercury_venus_neptune_public_style_responsibility_chart_exact` | career | career_signature | 1.0000 | true |
| `career_career_visibility` | career | career_signature | 1.0000 | n/a |
| `career_career_visibility_aux` | career | career_signature | 1.0000 | n/a |
| `career_career_visibility_aux` | career | career_signature | 1.0000 | n/a |
| `libra_dsc_chiron_scorpio_7h_harmony_wound_depth_chart_exact` | relationship | relationship_wound_to_gift | 1.0000 | true |
| `mars_opposite_saturn_action_restraint_inner_brake_chart_exact` | action | action_friction_to_strength | 1.0000 | true |
| `mercury_capricorn_mc_public_voice_strategic_mind_chart_exact` | career | career_mind_signature | 1.0000 | true |
| `moon_cancer_ic_home_security_roots_chart_exact` | home_family | emotional_home_signature | 1.0000 | true |
| `moon_mercury_ic_mc_private_security_public_voice_axis` | mind | axis_tension | 1.0000 | true |
| `moon_mercury_ic_mc_private_security_public_voice_axis` | axis_tension | axis_tension | 1.0000 | true |
| `moon_mercury_ic_mc_private_security_public_voice_axis_aux` | mind | axis_tension | 1.0000 | true |
| `moon_mercury_ic_mc_private_security_public_voice_axis_aux` | axis_tension | axis_tension | 1.0000 | true |
| `saturn_aries_12h_private_pressure_hidden_self_control_chart_exact` | inner_world | inner_pressure_to_maturity | 1.0000 | true |
| `saturn_sextile_uranus_structured_originality_chart_exact` | mind | gift | 1.0000 | false |
| `saturn_sextile_uranus_structured_originality_identity_chart_exact` | identity | gift | 1.0000 | false |
| `saturn_trine_pluto_deep_resilience_chart_exact` | identity | gift | 1.0000 | n/a |
| `sun_aquarius_11h_collective_identity_future_networks_chart_exact` | community | collective_identity | 1.0000 | true |
| `venus_capricorn_10h_public_love_style_responsibility_chart_exact` | relationship | career_love_style | 1.0000 | true |
| `mercury_conjunct_venus_refined_relational_language_chart_exact` | communication | gift | 0.9988 | n/a |
| `libra_aries_6h_12h_service_action_axis_chart_exact` | axis_tension | life_direction_axis | 0.9613 | true |

## focus_map

| domain | tier | score |
|---|---:|---:|
| career | strong | 1.0000 |
| axis_tension | strong | 0.8842 |
| home_family | strong | 0.8800 |
| mind | medium_strong | 0.8301 |
| community | medium_strong | 0.7558 |
| relationship | medium_strong | 0.7058 |
| action | medium_strong | 0.6800 |
| inner_world | supporting | 0.4600 |
| identity | detail_only | 0.4018 |

## clusters

public_main:
- `career_public_voice_strategic_mind`
- `axis_tension_private_security_public_voice_axis`
- `community_collective_identity`
- `relationship_harmony_wound_depth`
- `action_action_through_balance`
- `home_family_home_security_roots`

public_support:
- `career_public_style_responsibility`
- `axis_tension_service_action_axis`
- `community_future_collective_signal`
- `action_action_restraint`
- `relationship_public_love_responsibility`
- `mind_gift_like_mercury_conjunct_venus_refined_relational_language_chart_exact`

detail:
- `career_career_like_career_career_visibility`
- `mind_axis_like_moon_mercury_ic_mc_private_security_public_voice_axis`
- `inner_world_private_pressure`
- `identity_gift_like_saturn_trine_pluto_deep_resilience_chart_exact`

## public surfaces

profile_narrative_projection_v1 core:
- `promise::mercury_capricorn_mc_public_voice_strategic_mind_chart_exact` - Kariyer hattında sözün, aklın ve karar dilin çok görünür olabilir.
- `promise::moon_mercury_ic_mc_private_security_public_voice_axis` - İç güvenliğin, dışarıda nasıl konuştuğunu doğrudan etkileyebilir.
- `promise::sun_aquarius_11h_collective_identity_future_networks_chart_exact` - Kimliğin, hangi çevrede hangi fikri taşıdığından da beslenir.
- `promise::libra_dsc_chiron_scorpio_7h_harmony_wound_depth_chart_exact` - İlişkide denge istersin; ama bu denge yüzeysel bir uyum gibi çalışmaz.

profile_narrative_projection_v1 extra:
- `promise::aries_asc_mars_libra_6h_action_through_balance_chart_exact` - Hızlı hareket etmek isteyen tarafın, dengeyi de hesaba katmak ister.
- `promise::moon_cancer_ic_home_security_roots_chart_exact` - İçeride güvende hissetmediğinde dışarıdaki duruşun da etkilenebilir.
- `promise::saturn_trine_pluto_deep_resilience_chart_exact` - Zorlandığında bile dağılıp gitmeyen, içeride yapı kuran bir gücün var.
- `promise::capricorn_10h_mercury_venus_neptune_public_style_responsibility_chart_exact` - Dış dünyada sözün, üslubun ve duruşun birlikte algılanabilir.
- `promise::venus_capricorn_10h_public_love_style_responsibility_chart_exact` - Sevgi ve değer verme biçimin dışarıda ciddi ve güvenilir bir tonda görünebilir.
- `promise::saturn_aries_12h_private_pressure_hidden_self_control_chart_exact` - Bazı mücadeleleri dışarıdan görünmeden, kendi içinde veriyor olabilirsin.

profile_v8_projection_v1:
- hero: `promise::moon_mercury_ic_mc_private_security_public_voice_axis`
- identity_axis: `promise::saturn_trine_pluto_deep_resilience_chart_exact`
- insight_strip: public voice, home security, collective identity
- differentiators: action-through-balance, IC/MC axis, relationship wound/depth

## truthfulness scan

Public-surface snapshot grep for the four P0-forbidden false-anchor strings returned zero hits.

The two Saturn-Uranus structured-originality packets remain in debug inventory with `chart_facts_match=false` and are suppressed from public surfaces.

## tests

Passed:
- `backend/tests/test_natal_promise_cluster_plan.py::test_natal_promise_cluster_plan_istanbul_1997_truthfulness_guards_block_false_saturn_uranus_packets`
- `backend/tests/test_natal_promise_cluster_plan.py::test_natal_promise_cluster_plan_istanbul_1997_v0_8_overlay_surfaces_axis_and_roots`
- `backend/tests/test_natal_promise_packets.py`
- `backend/tests/test_natal_promise_cluster_plan.py`
- `backend/tests/test_natal_public_builder.py`
- `backend/tests/test_projection_shadow_v1_builder.py`

Broad suite result: `81 passed`.
