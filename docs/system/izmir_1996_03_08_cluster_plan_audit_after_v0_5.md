# Izmir 1996-03-08 08:30 Cluster Plan Audit After v0.5 Overlay

- Generated: 2026-05-12
- Source artifact: `backend/tests/_artifacts/natal_interpret_full_1996-03-08_08-30_izmir_user_compact_debug.json`
- Public snapshot: `docs/system/_generated_outputs/fresh_natal_interpret_ui_1996-03-08_08-30_izmir.json`
- Flags: `ENABLE_NATAL_PROMISE_PROJECTION_V1=true`, `ENABLE_NATAL_PROMISE_PACKET_DEBUG=true`
- Scope: additive v0.5 registry overlay only; no architecture rewrite, no broad renderer pass, no generic-packet retuning.

## 1. Summary

v0.5 materially fixes semantic coverage for the Izmir chart.

Before v0.5:
- `identity` disappeared
- `inner_world / 12H saturation` was effectively unread
- relationship fell back to generic `relationship_relationships`
- career stayed generic instead of `MC Capricorn -> Saturn Pisces 12H`
- `Mercury square Pluto` existed but stayed under-read

After v0.5:
- `identity` now appears and is `strong`
- `inner_world` now appears and is `medium_strong`
- relationship public-main is now Scorpio / Mars-12H specific
- career public-main is now Capricorn-MC / Saturn-12H invisible-preparation specific
- `Mercury square Pluto` is retained in surfaced detail
- no Gemini-ASC copy leakage
- no `7H Sagittarius` fact drift

## 2. Candidate Inventory

Candidate inventory count: **17**

Packet ids:
1. `dsc_scorpio_ruler_mars_pisces_12h_trust_threshold_silent_desire_chart_exact`
2. `mars_pisces_12h_hidden_action_soft_drive_chart_exact`
3. `mc_capricorn_ruler_saturn_pisces_12h_invisible_preparation_chart_exact`
4. `mercury_pisces_11h_social_intuition_mind_chart_exact`
5. `pisces_12h_stellium_inner_world_saturation_chart_exact`
6. `pluto_7h_relationship_power_depth_chart_exact`
7. `saturn_pisces_12h_private_maturity_boundary_sensitivity_chart_exact`
8. `sun_mars_pisces_12h_private_will_and_hidden_drive`
9. `sun_mars_pisces_12h_private_will_and_hidden_drive_aux`
10. `taurus_asc_venus_12h_hidden_value_identity_chart_exact`
11. `uranus_square_asc_venus_unsettled_outer_signal`
12. `uranus_square_asc_venus_unsettled_outer_signal`
13. `uranus_square_asc_venus_unsettled_outer_signal_aux`
14. `uranus_square_asc_venus_unsettled_outer_signal_aux`
15. `venus_12h_conjunct_asc_soft_hidden_magnetism_chart_exact`
16. `venus_taurus_12h_private_love_inner_beauty_chart_exact`
17. `mercury_square_pluto_deep_mind_pressure_chart_exact`

Notes:
- Effective semantic pool is now much broader than the pre-v0.5 state.
- There is still aux inflation around `sun_mars_*` and `uranus_square_*`; these stay acceptable for now because ClusterPlan keeps them out of public-main duplication.

## 3. Focus Map

| domain | tier | score |
|---|---|---|
| identity | strong | 1.0000 |
| career | strong | 0.8669 |
| relationship | medium_strong | 0.8372 |
| inner_world | medium_strong | 0.7888 |
| mind | supporting | 0.6206 |

Read:
- Identity is fully recovered.
- Career is now chart-correct and strong.
- Relationship is no longer generic fallback.
- `inner_world` is now visible as its own domain family.
- Mind no longer dominates the chart incorrectly; it is present but secondary.

## 4. Clusters

### public_main
1. `identity_hidden_value_identity`
   - main packet: `taurus_asc_venus_12h_hidden_value_identity_chart_exact`
2. `relationship_trust_threshold_silent_desire`
   - main packet: `dsc_scorpio_ruler_mars_pisces_12h_trust_threshold_silent_desire_chart_exact`
3. `inner_world_inner_world_saturation`
   - main packet: `pisces_12h_stellium_inner_world_saturation_chart_exact`
4. `career_invisible_preparation`
   - main packet: `mc_capricorn_ruler_saturn_pisces_12h_invisible_preparation_chart_exact`
5. `mind_social_intuition_mind`
   - main packet: `mercury_pisces_11h_social_intuition_mind_chart_exact`

### public_support
- none

### detail
1. `inner_world_hidden_action_soft_drive`
2. `identity_unsettled_outer_signal`
3. `relationship_wound_like_uranus_square_asc_venus_unsettled_outer_signal`
4. `relationship_private_love_inner_beauty`
5. `relationship_relationship_power_depth`
6. `inner_world_private_maturity`
7. `mind_deep_mind_pressure`

## 5. Public Surface Readout

### profile_narrative_projection_v1 core_blocks
1. `promise::taurus_asc_venus_12h_hidden_value_identity_chart_exact`
   - headline: `Sessiz çekim, sadelik, güven veren varlık, içte büyüyen değer ve derin bağlılık.`
2. `promise::dsc_scorpio_ruler_mars_pisces_12h_trust_threshold_silent_desire_chart_exact`
   - headline: `En yoğun arzuların bile bazen önce sessizleşir, içeride büyür.`
3. `promise::pisces_12h_stellium_inner_world_saturation_chart_exact`
   - headline: `Görünmeyen alanda işlediğin şeyler, zamanla dışarıdaki yönünü belirler.`
4. `promise::mc_capricorn_ruler_saturn_pisces_12h_invisible_preparation_chart_exact`
   - headline: `Görünür olmadan önce içeride uzun süre prova yapmak.`

### profile_narrative_projection_v1 extra_blocks
1. `promise::mercury_pisces_11h_social_intuition_mind_chart_exact`
2. `promise::uranus_square_asc_venus_unsettled_outer_signal`
3. `promise::mars_pisces_12h_hidden_action_soft_drive_chart_exact`
4. `promise::venus_12h_conjunct_asc_soft_hidden_magnetism_chart_exact`
5. `promise::mercury_square_pluto_deep_mind_pressure_chart_exact`
6. `promise::venus_taurus_12h_private_love_inner_beauty_chart_exact`

### profile_v8_projection_v1

- hero:
  - node_id: `promise::taurus_asc_venus_12h_hidden_value_identity_chart_exact`
  - headline: `Sessiz çekim, sadelik, güven veren varlık, içte büyüyen değer ve derin bağlılık.`
- identity_axis:
  - eyebrow: `Kimlik Ekseni`
  - node_id: `promise::uranus_square_asc_venus_unsettled_outer_signal`
  - headline: `Dışarıdan sakin görünen duruşunun altında güçlü bir değer duygusu var.`
- insight_strip:
  1. `Kariyer` → `promise::mc_capricorn_ruler_saturn_pisces_12h_invisible_preparation_chart_exact`
  2. `İlişki` → `promise::venus_taurus_12h_private_love_inner_beauty_chart_exact`
  3. `İç dünya` → `promise::pisces_12h_stellium_inner_world_saturation_chart_exact`
- differentiators:
  1. `promise::dsc_scorpio_ruler_mars_pisces_12h_trust_threshold_silent_desire_chart_exact`
  2. `promise::mercury_pisces_11h_social_intuition_mind_chart_exact`
  3. `promise::uranus_square_asc_venus_unsettled_outer_signal_aux`

## 6. Exact Truthfulness Checks

Grep / text scan result on the fresh public surface:

- `Yükseleninin İkizler` → **no hit**
- `Yükselenin İkizler` → **no hit**
- `7. ev Yay` → **no hit**
- `7. evinin Yay` → **no hit**

This confirms the P0 chart-fact leakage remains fixed after the v0.5 overlay.

## 7. What v0.5 Solved

- `Taurus ASC + Venus Taurus 12H` now surfaces as the dominant identity axis.
- `Venus conjunct ASC` is present as secondary identity detail instead of being lost.
- `MC Capricorn + Saturn Pisces 12H` now owns the career signature.
- `Saturn Pisces 12H` now exists as inner-world maturity/support material.
- `Scorpio DSC + Mars Pisces 12H` now owns the relationship main cluster.
- `Pluto 7H` now appears as relationship depth detail.
- `Mars Pisces 12H` now appears as hidden-action detail.
- `12H saturation` now appears as a distinct public-main inner-world cluster.
- `Mercury Pisces 11H` now owns the surfaced mind cluster.
- `Mercury square Pluto` remains present and is now explicitly retained in detail.

## 8. Remaining Non-Blocking Issues

This pass fixed semantic coverage, not copy polish. Remaining issues are now renderer-level:

- several headlines are still registry/gift-forward and do not yet read as premium release copy
- some anchor/body joins remain stiff or broken:
  - `Yükseleninin Boğa Venüs 12. ev Boğa olması...`
  - `...olması de...`
  - `12. evinin yoğunluğu olması...`
- `identity_axis` currently lands on `uranus_square_asc_venus_unsettled_outer_signal`; semantically acceptable, but likely not the final premium choice
- `selected` packet payload is still thinner than the cluster candidate inventory; ClusterPlan itself is no longer blocked, but packet-only fallback richness is not the focus of this pass

## 9. Regression Status

Stable:
- Istanbul 1996
- Adana 1998
- Istanbul 2020

Tests:

```bash
PYTHONPATH=backend backend/venv/bin/pytest \
  backend/tests/test_natal_promise_packets.py \
  backend/tests/test_natal_promise_cluster_plan.py \
  backend/tests/test_natal_public_builder.py \
  backend/tests/test_projection_shadow_v1_builder.py -q
```

Result: `75 passed`

## 10. Verdict

This chart no longer needs a truthfulness fix.

It now reads as a real v0.5 semantic-coverage case:
- identity recovered
- relationship specific
- career chart-correct
- inner world visible
- deep mind retained

The next layer, if desired, is **copy polish**, not more semantic rescue.
