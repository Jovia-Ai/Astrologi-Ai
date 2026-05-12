# Istanbul 2020-04-10 ClusterPlan Audit After v0.4 Overlay

- Generated: 2026-05-12
- Birth data: `2020-04-10 08:26`, `Istanbul, TR`
- Flags: `ENABLE_NATAL_PROMISE_PROJECTION_V1=true`, `ENABLE_NATAL_PROMISE_PACKET_DEBUG=true`
- Registry authority: `v0.1_plus_manual_delta_v0_2_plus_v0_3_plus_v0_4`
- Source artifact: `backend/tests/_artifacts/natal_interpret_full_2020-04-10_08-26_istanbul_user_compact_debug.json`
- Public payload snapshot: `docs/system/_generated_outputs/fresh_natal_interpret_ui_2020-04-10_08-26_istanbul.json`
- Scope: additive semantic coverage only; architecture unchanged.

Companion baseline:
- pre-v0.4 audit: `docs/system/istanbul_2020_04_10_cluster_plan_audit.md`

## 1. Executive read

v0.4 overlay materially improves this chart.

- candidate inventory grew from `7` to `12`
- identity is no longer missing
- `Sun Aries 12H`, `Gemini ASC + Venus 1H`, `Aquarius MC + Mars conjunct MC + Uranus square MC`, `Moon Scorpio 6H`, and `Mercury sextile 9H Capricorn/Aquarius authority line` now all surface as packets
- surface plan no longer collapses to `3 main / 0 detail`; it is now `4 main / 5 detail`
- v8 no longer duplicates `mind` for both hero and identity_axis

But the chart is not fully “solved” yet:

- selected packet count is still only `3`
- relationship improves in breadth but stays `supporting` in focus_map, not `medium_strong`
- public main relationship card is still the older generic `relationship_relationships` cluster, while the richer v0.4 relationship sub-angles remain in detail

So this round is a real semantic gain, but not the final tuning pass.

## 2. Delta vs pre-v0.4

### Before

- candidate packet count: `7`
- selected packet count: `3`
- focus_map:
  - `career strong`
  - `mind strong`
  - `relationship detail_only`
- no `identity` domain in focus_map
- no support/detail clusters
- v8:
  - hero `mind_mind_system`
  - identity_axis `mind_mind_system_aux`

### After

- candidate packet count: `12`
- selected packet count: `3`
- focus_map:
  - `career strong`
  - `mind medium_strong`
  - `identity medium_strong`
  - `relationship supporting`
- public_main cluster count: `4`
- detail cluster count: `5`
- v8:
  - hero `gemini_asc_venus_1h_social_relational_presence_chart_exact`
  - identity_axis `sun_aries_12h_hidden_private_fire_chart_exact`

## 3. Candidate inventory

### Counts

- candidate packet count: `12`
- selected packet count: `3`
- public_main cluster count: `4`
- detail cluster count: `5`

### Candidate packets

| id | domain | promise_type | strength | read |
|---|---|---|---:|---|
| `aquarius_mc_mars_conjunct_mc_visible_freedom_drive` | career | `career_signature` | `1.00` | visible action / freedom / career initiative |
| `aquarius_mc_mars_conjunct_mc_visible_freedom_drive_aux` | career | `career_signature` | `1.00` | aux variant of same career line |
| `gemini_asc_venus_1h_social_relational_presence_chart_exact` | identity | `behavior_reflex` | `1.00` | social/relational first impression |
| `mercury_sextile_9h_capricorn_aquarius_intellectual_authority_chart_exact` | mind | `mind_style` | `1.00` | intellectual authority / framed thinking |
| `mind_mind_system` | mind | `mind_style` | `1.00` | existing Gemini ASC + Mercury Pisces 11H line |
| `mind_mind_system_aux` | mind | `mind_style` | `1.00` | aux variant |
| `mind_mind_system_aux` | mind | `mind_style` | `1.00` | duplicated aux variant from current builder path |
| `moon_scorpio_6h_emotional_routine_sensitivity_chart_exact` | relationship | `need` | `1.00` | emotional routine / daily sensitivity |
| `sun_aries_12h_hidden_private_fire_chart_exact` | identity | `behavior_reflex` | `1.00` | hidden/private fire |
| `venus_trine_mars_relational_attraction_signal_chart_exact` | relationship | `love_style` | `1.00` | attraction / warmth / motion |
| `venus_trine_saturn_trust_bond_chart_exact` | relationship | `love_style` | `1.00` | trust / loyalty / consistency |
| `relationship_relationships` | relationship | `love_style` | `0.52` | generic 7H Yay + Jupiter 9H relationship line |

### Coverage verdict

Requested v0.4 targets now surface:

- `Gemini ASC + Venus 1H social/relational presence` -> `PASS`
- `Sun Aries 12H hidden self / private fire` -> `PASS`
- `Aquarius MC + Mars conjunct MC + Uranus square MC career action/freedom` -> `PASS`
- `Venus trine Mars + Venus trine Saturn relationship attraction + trust` -> `PASS`
- `Moon Scorpio 6H emotional routine / daily sensitivity` -> `PASS`
- `Jupiter/Saturn/Pluto 9H + Mercury sextiles belief/intellectual authority` -> `PASS`

## 4. Focus map

| domain | score | tier | read |
|---|---:|---|---|
| `career` | `0.9911` | `strong` | strongest line; career visibility is now read through action/freedom rather than only `Saturn 9H Kova` |
| `mind` | `0.8206` | `medium_strong` | now split between existing `mind_system` and intellectual-authority line |
| `identity` | `0.7158` | `medium_strong` | identity recovered through `Gemini ASC + Venus 1H` and `Sun Aries 12H` |
| `relationship` | `0.5882` | `supporting` | richer than before, but still not promoted enough despite multiple v0.4 packets |

### Read

The chart now reads much closer to its actual shape:

- career/action/freedom is the clearest public line
- social identity and hidden/private identity both exist
- mind now has both mutable/social and structured/intellectual authority sub-angles
- relationship is no longer thin, but its score still lags behind the number of packets now present

## 5. Clusters

### Public main clusters

1. `career_career_like_aquarius_mc_mars_conjunct_mc_visible_freedom_drive`
   - main packet: `aquarius_mc_mars_conjunct_mc_visible_freedom_drive`
   - role: career action / visible freedom / initiative

2. `mind_mind_like_mind_mind_system`
   - main packet: `mind_mind_system`
   - role: existing mutable/social/sezgisel mind line

3. `relationship_love_like_relationship_relationships`
   - main packet: `relationship_relationships`
   - role: generic trust/depth relationship line

4. `identity_identity_like_gemini_asc_venus_1h_social_relational_presence_chart_exact`
   - main packet: `gemini_asc_venus_1h_social_relational_presence_chart_exact`
   - role: social/relational first impression

### Detail clusters

1. `mind_mind_like_mercury_sextile_9h_capricorn_aquarius_intellectual_authority_chart_exact`
2. `relationship_love_like_venus_trine_mars_relational_attraction_signal_chart_exact`
3. `relationship_love_like_venus_trine_saturn_trust_bond_chart_exact`
4. `identity_identity_like_sun_aries_12h_hidden_private_fire_chart_exact`
5. `relationship_need_like_moon_scorpio_6h_emotional_routine_sensitivity_chart_exact`

### Structural read

This is the right direction:

- identity is now a real public-main family
- hidden/private fire survives as detail instead of disappearing
- relationship subtype richness exists in the plan
- intellectual-authority mind line exists in the plan

But selection is still conservative:

- selected packets remain only `3`
- relationship subtype packets are present but not promoted
- detail is doing too much of the semantic lifting

## 6. Public surfaces

## 6.1 `profile_narrative_projection_v1`

- source_graph: `natal_promise_cluster_plan_v1`
- core block count: `4`
- extra block count: `5`

### Core blocks

1. `Görünür işte cesur başlatıcılık, bağımsız hareket ve canlı yön duygusu.`
2. `Ne yapacağını bildiğin an tempo kendiliğinden yükselir.`
3. `Sen ilişkide yüzeysel bir sıcaklıktan çok, içine oturan bir güven arıyorsun.`
4. `Duruşun hafif görünse de kimle ne kadar açılacağını hızlı sezebiliyor olabilirsin.`

### Extra blocks

1. `İnce sezgi, duygusal alt akımı erken fark etme ve gündelik olanda bile derin bağ kurma.`
2. `Bir fikri sadece bulmak değil, ona sağlam bir çerçeve vermek sende güçlü olabilir.`
3. `Sende dışarıdan hemen görünmeyen ama içeride hızla alevlenen bir taraf olabilir.`
4. `Yakınlıkta sende oyunla çekimin aynı anda açılması kolay olabilir.`
5. `Sevgiyi güven, sadakat ve uzun vadeli emekle taşıyabilmek.`

### Narrative verdict

This is materially healthier than the pre-v0.4 state:

- core is now diverse across career / mind / relationship / identity
- extras are no longer empty
- new v0.4 semantics are visible to the user

But the relationship main card is still the generic one, while the richer v0.4 relationship cards stay below the fold.

## 6.2 `profile_v8_projection_v1`

- source_graph: `natal_promise_cluster_plan_v1`

### Hero

- `gemini_asc_venus_1h_social_relational_presence_chart_exact`
- headline: `Duruşun hafif görünse de kimle ne kadar açılacağını hızlı sezebiliyor olabilirsin.`

### Identity axis

- `sun_aries_12h_hidden_private_fire_chart_exact`
- headline: `Sende dışarıdan hemen görünmeyen ama içeride hızla alevlenen bir taraf olabilir.`

### Insight strip

1. `career` -> `Görünür işte cesur başlatıcılık, bağımsız hareket ve canlı yön duygusu.`
2. `mind` -> `Sen dışarıdan meraklı ve hareketli görünebilirsin.`
3. `relationship/detail-style emotional line` -> `İnce sezgi, duygusal alt akımı erken fark etme ve gündelik olanda bile derin bağ…`

### Differentiators

1. career action/freedom line
2. intellectual-authority mind line
3. Venus trine Mars attraction line

### V8 verdict

This is a clear upgrade.

Pre-v0.4:
- hero and identity_axis were both mind-family

After v0.4:
- hero is social-identity
- identity_axis is hidden/private fire
- differentiators are more semantically diverse

## 7. Stability checks

Targeted regression status:

- 1996 Istanbul golden behavior: `PASS`
- Adana v0.3 golden behavior: `PASS`
- public builder/projection tests: `PASS`

Test command:

```bash
PYTHONPATH=backend backend/venv/bin/pytest backend/tests/test_natal_promise_packets.py backend/tests/test_natal_promise_cluster_plan.py backend/tests/test_natal_public_builder.py backend/tests/test_projection_shadow_v1_builder.py -q
```

Result:

- `66 passed`

## 8. Remaining issues

1. Relationship is still under-promoted.
   There are now multiple real relationship packets, but focus_map still lands at `supporting`.

2. Selected packet count is still only `3`.
   Candidate inventory improved, but selected path is still thin.

3. Relationship main is still generic.
   `relationship_relationships` wins public_main over more specific v0.4 packets like:
   - `venus_trine_mars_relational_attraction_signal_chart_exact`
   - `venus_trine_saturn_trust_bond_chart_exact`
   - `moon_scorpio_6h_emotional_routine_sensitivity_chart_exact`

4. Mind still prefers legacy `mind_mind_system` over the new intellectual-authority line.
   That may be acceptable, but it means the stronger semantic recovery is in detail, not main.

5. Candidate inventory still includes duplicate aux behavior.
   `mind_mind_system_aux` still appears duplicated in candidate ids.

## 9. Verdict

v0.4 is a meaningful win.

It fixes the biggest semantic hole in this chart:

- identity now exists
- private fire now exists
- career action/freedom now exists
- relationship attraction/trust now exists
- emotional routine sensitivity now exists
- intellectual-authority mind now exists

But this is still a coverage pass, not the final selection pass.

The next likely tuning target for this chart is not more source richness. It is:

- relationship promotion
- selected packet broadening
- main-vs-detail rebalancing for v0.4 packets
