# Istanbul 1994-06-25 ClusterPlan Audit After v0.7 Overlay

- Generated: 2026-05-13
- Chart: 1994-06-25 10:00 Istanbul, TR
- Source artifact: `backend/tests/_artifacts/natal_interpret_full_1994-06-25_10-00_istanbul_user_compact_debug.json`
- Flags: `ENABLE_NATAL_PROMISE_PROJECTION_V1=true`, `ENABLE_NATAL_PROMISE_PACKET_DEBUG=true`
- Scope: additive v0.7 registry coverage plus the smallest routing needed to let new semantic domains surface.

## 1. Registry / Routing Changes

- Added additive registry overlay `NATAL_PROMISE_LIBRARY_V0_7`.
- Updated registry authority to `v0.1_plus_manual_delta_v0_2_plus_v0_3_plus_v0_4_plus_v0_5_plus_v0_7`.
- Added chart-exact guards for Leo ASC, Cancer 11H Sun/Mercury, Scorpio 4H Pluto/Node, Capricorn 5H Moon/Uranus/Neptune, Taurus MC/Mars 10H, Aquarius DSC/Saturn 7H, Venus Leo 12H, Jupiter Scorpio 3H, and Chiron Virgo 1H.
- Small routing change: `home_family` and `creativity` now remain distinct ClusterPlan domain families instead of collapsing into identity/career fallback.
- Public labels added for `home_family` and `creativity`.

## 2. Candidate Inventory

Candidate inventory count: **14**.

1. `aquarius_dsc_saturn_pisces_7h_freedom_responsibility_sensitivity_chart_exact` — relationship / relationship_need / strength 1.0
2. `chiron_virgo_1h_visible_sensitivity_self_correction_chart_exact` — identity / wound_to_gift / strength 1.0
3. `jupiter_scorpio_3h_deep_speech_psychological_learning_chart_exact` — mind / mind_style / strength 1.0
4. `leo_asc_sun_cancer_11h_warm_visibility_belonging_chart_exact` — identity / identity_style / strength 1.0
5. `mars_opposite_pluto_public_power_roots_tension_chart_exact` — career / career_friction_to_power / strength 1.0
6. `mc_taurus_mars_10h_steady_public_drive_chart_exact` — career / career_signature / strength 1.0
7. `moon_capricorn_5h_serious_heart_creative_form_chart_exact` — creativity / creative_emotional_style / strength 1.0
8. `moon_uranus_neptune_capricorn_5h_structured_imagination_chart_exact` — creativity / creative_signature / strength 1.0
9. `pluto_node_scorpio_4h_roots_inner_security_transformation_chart_exact` — home_family / roots_transformation / strength 1.0
10. `sun_mercury_cancer_11h_social_emotional_intelligence` — mind / social_mind_style / strength 1.0
11. `sun_mercury_cancer_11h_social_emotional_intelligence_aux` — mind / social_mind_style / strength 1.0
12. `sun_mercury_cancer_11h_social_emotional_intelligence_aux` — mind / social_mind_style / strength 1.0
13. `venus_leo_12h_hidden_romantic_pride_chart_exact` — relationship / love_style / strength 1.0
14. `ic_scorpio_pluto_node_private_emotional_inheritance_chart_exact` — home_family / home_family_signature / strength 0.9584

Selected packet mode remains thin (**2 packets**) because this chart is now primarily represented by candidate-inventory ClusterPlan:

1. `mars_opposite_pluto_public_power_roots_tension`
2. `sun_mercury_cancer_11h_social_emotional_intelligence_aux`

## 3. Focus Map

| domain | tier | score |
|---|---:|---:|
| mind | strong | 0.8641 |
| identity | medium_strong | 0.8358 |
| home_family | medium_strong | 0.7010 |
| career | supporting | 0.6253 |
| creativity | supporting | 0.5558 |
| relationship | supporting | 0.5458 |

Result: v0.7 recovers the missing home/roots, creativity, identity, relationship, and mind signatures. Career is present and public-main despite a supporting focus score because the MC/Mars packet has strong chart-exact priority.

## 4. Clusters

| cluster | domain_family | main_packet_id | role |
|---|---|---|---|
| `mind_social_emotional_intelligence` | mind | `sun_mercury_cancer_11h_social_emotional_intelligence` | public_main |
| `identity_warm_visibility_belonging` | identity | `leo_asc_sun_cancer_11h_warm_visibility_belonging_chart_exact` | public_main |
| `home_family_roots_inner_security_transformation` | home_family | `pluto_node_scorpio_4h_roots_inner_security_transformation_chart_exact` | public_main |
| `relationship_freedom_responsibility_sensitivity` | relationship | `aquarius_dsc_saturn_pisces_7h_freedom_responsibility_sensitivity_chart_exact` | public_main |
| `career_steady_public_drive` | career | `mc_taurus_mars_10h_steady_public_drive_chart_exact` | public_main |
| `creativity_structured_imagination` | creativity | `moon_uranus_neptune_capricorn_5h_structured_imagination_chart_exact` | public_main |
| `identity_visible_sensitivity_self_correction` | identity | `chiron_virgo_1h_visible_sensitivity_self_correction_chart_exact` | public_support |
| `home_family_private_emotional_inheritance` | home_family | `ic_scorpio_pluto_node_private_emotional_inheritance_chart_exact` | public_support |
| `mind_deep_speech_psychological_learning` | mind | `jupiter_scorpio_3h_deep_speech_psychological_learning_chart_exact` | detail |
| `relationship_hidden_romantic_pride` | relationship | `venus_leo_12h_hidden_romantic_pride_chart_exact` | detail |
| `career_public_power_roots_tension` | career | `mars_opposite_pluto_public_power_roots_tension_chart_exact` | detail |
| `creativity_serious_heart_creative_form` | creativity | `moon_capricorn_5h_serious_heart_creative_form_chart_exact` | detail |

## 5. Public Surface Plan

`public_main` (6):

1. `mind_social_emotional_intelligence`
2. `identity_warm_visibility_belonging`
3. `home_family_roots_inner_security_transformation`
4. `relationship_freedom_responsibility_sensitivity`
5. `career_steady_public_drive`
6. `creativity_structured_imagination`

`public_support` (2):

1. `identity_visible_sensitivity_self_correction`
2. `home_family_private_emotional_inheritance`

`detail` (4):

1. `mind_deep_speech_psychological_learning`
2. `relationship_hidden_romantic_pride`
3. `career_public_power_roots_tension`
4. `creativity_serious_heart_creative_form`

## 6. Public Surfaces

### profile_narrative_projection_v1 core_blocks

1. `promise::sun_mercury_cancer_11h_social_emotional_intelligence` — "Zihnin sadece bilgi toplamak için değil, insanları duygusal olarak anlamak için çalışabilir."
2. `promise::leo_asc_sun_cancer_11h_warm_visibility_belonging_chart_exact` — "Parlamak senin için yalnızca görünmek değil, kalpten bağ kurduğun yerde anlam kazanabilir."
3. `promise::pluto_node_scorpio_4h_roots_inner_security_transformation_chart_exact` — "Köklerden gelen yoğunluğu dönüştürerek kendi iç alanını yeniden kurmak."
4. `promise::aquarius_dsc_saturn_pisces_7h_freedom_responsibility_sensitivity_chart_exact` — "Yakınlıkta hem kendi alanını korumak hem de güvenilir bir bağ aramak."

### profile_narrative_projection_v1 extra_blocks

1. `promise::mc_taurus_mars_10h_steady_public_drive_chart_exact` — "Dış dünyada gücünü sözle değil, yaptığı işle göstermek."
2. `promise::moon_uranus_neptune_capricorn_5h_structured_imagination_chart_exact` — "Yaratıcılığın hem farklı hem de disiplinli bir yerden akabilir."
3. `promise::chiron_virgo_1h_visible_sensitivity_self_correction_chart_exact` — "İnce dikkat, iyileştirici varlık, başkalarına alan açan hassasiyet, görünür alanda geliştirme becerisi."
4. `promise::moon_capricorn_5h_serious_heart_creative_form_chart_exact` — "Sevgi ve üretim sende sadece coşkuyla değil, emek ve yapı ile de çalışır."
5. `promise::jupiter_scorpio_3h_deep_speech_psychological_learning_chart_exact` — "Yakın çevrendeki küçük sözler bile sende büyük içgörüler açabilir."
6. `promise::venus_leo_12h_hidden_romantic_pride_chart_exact` — "Romantik duyguyu içeride büyütüp dışarıda daha kontrollü göstermek."

### profile_v8_projection_v1

- hero: `promise::leo_asc_sun_cancer_11h_warm_visibility_belonging_chart_exact` — "Parlamak senin için yalnızca görünmek değil, kalpten bağ kurduğun yerde anlam kazanabilir."
- identity_axis: `promise::chiron_virgo_1h_visible_sensitivity_self_correction_chart_exact` — "İnce dikkat, iyileştirici varlık, başkalarına alan açan hassasiyet, görünür alanda geliştirme becerisi."
- insight_strip:
  1. `promise::sun_mercury_cancer_11h_social_emotional_intelligence`
  2. `promise::pluto_node_scorpio_4h_roots_inner_security_transformation_chart_exact`
  3. `promise::moon_uranus_neptune_capricorn_5h_structured_imagination_chart_exact`
- differentiators:
  1. `promise::mc_taurus_mars_10h_steady_public_drive_chart_exact`
  2. `promise::aquarius_dsc_saturn_pisces_7h_freedom_responsibility_sensitivity_chart_exact`
  3. `promise::jupiter_scorpio_3h_deep_speech_psychological_learning_chart_exact`

## 7. Coverage Verdict

- Leo ASC + Sun Cancer 11H identity: **covered**, public_main + v8 hero.
- Sun-Mercury Cancer 11H social-emotional intelligence: **covered**, public_main.
- Pluto + North Node Scorpio 4H roots: **covered**, public_main.
- Moon Capricorn 5H + Uranus/Neptune structured imagination: **covered**, public_main.
- Taurus MC + Mars Taurus 10H visible drive: **covered**, public_main.
- Mars opposite Pluto public power tension: **covered**, detail.
- Aquarius DSC + Saturn Pisces 7H relationship: **covered**, public_main.
- Venus Leo 12H hidden romantic pride: **covered**, detail.
- Jupiter Scorpio 3H deep speech: **covered**, detail.
- Chiron Virgo 1H visible sensitivity: **covered**, public_support + v8 identity_axis.

## 8. Product Notes

- Architecture issue fixed for this chart: the plan no longer collapses into generic `mind_mind_system`, `relationship_relationships`, and `career_career_visibility`.
- Copy quality is not yet final. Several headlines still read like voice-seed/gift fragments rather than fully polished SHOU public copy. This is expected because this pass was semantic coverage first, not a renderer polish pass.
- `sun_mercury_cancer_11h_social_emotional_intelligence` appears as a text-matched packet plus aux copies, not a separate `_chart_exact` id in the final deduped inventory. It is still chart-correct and public_main; the exact chart signature is represented by the same registry id.

## 9. Regression / Tests

Tests run:

`PYTHONPATH=backend backend/venv/bin/pytest backend/tests/test_natal_promise_packets.py backend/tests/test_natal_promise_cluster_plan.py backend/tests/test_natal_public_builder.py backend/tests/test_projection_shadow_v1_builder.py -q`

Result: **79 passed**.

Compile check:

`PYTHONPATH=backend backend/venv/bin/python -m py_compile backend/app/natal/promise_archetype_registry_sprint1.py backend/app/natal/natal_promise_packets.py backend/app/natal/natal_promise_cluster_plan.py backend/app/meaning/projection_shadow_v1_builder.py`

Result: **passed**.
