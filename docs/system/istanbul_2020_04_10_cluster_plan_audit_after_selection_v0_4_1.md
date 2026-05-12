# Istanbul 2020-04-10 ClusterPlan Audit After Selection v0.4.1

- Generated: 2026-05-12
- Birth data: `2020-04-10 08:26`, `Istanbul, TR`
- Flags: `ENABLE_NATAL_PROMISE_PROJECTION_V1=true`, `ENABLE_NATAL_PROMISE_PACKET_DEBUG=true`
- Registry authority: `v0.1_plus_manual_delta_v0_2_plus_v0_3_plus_v0_4`
- Source artifact: `backend/tests/_artifacts/natal_interpret_full_2020-04-10_08-26_istanbul_user_compact_debug.json`
- Public payload snapshot: `docs/system/_generated_outputs/fresh_natal_interpret_ui_2020-04-10_08-26_istanbul.json`
- Scope: selection tuning only. No source-richness expansion, no architecture change, no broad renderer change.

Companion audits:
- baseline: `docs/system/istanbul_2020_04_10_cluster_plan_audit.md`
- additive overlay only: `docs/system/istanbul_2020_04_10_cluster_plan_audit_after_v0_4.md`

## 1. Executive read

This round fixes the main selection problem from the v0.4 overlay pass.

- candidate inventory stays at `12`
- selected packet count broadens from `3` to `4`
- relationship public_main is now specific, not generic
- generic `relationship_relationships` is demoted to detail
- career and identity wins stay stable
- v8 hero and identity_axis stay stable

The key change is not new coverage. The key change is that the richer relationship subtype set now actually influences cluster selection.

## 2. Delta vs v0.4 overlay

### Before

- candidate packet count: `12`
- selected packet count: `3`
- relationship public_main cluster: `relationship_love_like_relationship_relationships`
- relationship subtype packets existed, but all stayed in detail
- selected packets:
  - `aquarius_mc_mars_conjunct_mc_visible_freedom_drive`
  - `mind_mind_system`
  - `relationship_relationships`

### After

- candidate packet count: `12` unchanged
- selected packet count: `4`
- relationship public_main cluster: `relationship_trust_bond`
- generic `relationship_relationships` moved to detail
- selected packets:
  - `aquarius_mc_mars_conjunct_mc_visible_freedom_drive`
  - `mind_mind_system`
  - `relationship_relationships`
  - `gemini_asc_venus_1h_social_relational_presence_chart_exact`

### Interpretation

This is the right shape:

- selected inventory is still conservative, but no longer too thin for this chart
- relationship no longer wastes its only public-main slot on the generic fallback
- detail still keeps the remaining relationship subtypes alive

## 3. Candidate inventory

### Counts

- candidate packet count: `12`
- selected packet count: `4`
- public_main cluster count: `4`
- public_support cluster count: `0`
- detail cluster count: `5`

### Candidate packet ids

1. `aquarius_mc_mars_conjunct_mc_visible_freedom_drive`
2. `aquarius_mc_mars_conjunct_mc_visible_freedom_drive_aux`
3. `gemini_asc_venus_1h_social_relational_presence_chart_exact`
4. `mercury_sextile_9h_capricorn_aquarius_intellectual_authority_chart_exact`
5. `mind_mind_system`
6. `mind_mind_system_aux`
7. `mind_mind_system_aux`
8. `moon_scorpio_6h_emotional_routine_sensitivity_chart_exact`
9. `sun_aries_12h_hidden_private_fire_chart_exact`
10. `venus_trine_mars_relational_attraction_signal_chart_exact`
11. `venus_trine_saturn_trust_bond_chart_exact`
12. `relationship_relationships`

### Selection read

Selected packet broadening is intentionally narrow.

- It activates only when selected inventory is still thin, generic relationship is occupying a slot, and the chart also carries multiple specific relationship signatures plus a missing domain candidate.
- On this chart, that adds the missing identity packet without inflating aux noise.
- 1996 Istanbul and Adana stay behaviorally stable under the regression suite.

## 4. Focus map

| domain | score | tier | packet_ids |
|---|---:|---|---|
| `career` | `0.9911` | `strong` | `aquarius_mc_mars_conjunct_mc_visible_freedom_drive`, `aquarius_mc_mars_conjunct_mc_visible_freedom_drive_aux` |
| `mind` | `0.8206` | `medium_strong` | `mercury_sextile_9h_capricorn_aquarius_intellectual_authority_chart_exact`, `mind_mind_system`, `mind_mind_system_aux` |
| `identity` | `0.7158` | `medium_strong` | `gemini_asc_venus_1h_social_relational_presence_chart_exact`, `sun_aries_12h_hidden_private_fire_chart_exact` |
| `relationship` | `0.5882` | `supporting` | `moon_scorpio_6h_emotional_routine_sensitivity_chart_exact`, `venus_trine_mars_relational_attraction_signal_chart_exact`, `venus_trine_saturn_trust_bond_chart_exact`, `relationship_relationships` |

### Read

Relationship is still only `supporting` in score terms. But selection is healthier now because the domain’s representative is subtype-led instead of generic.

That is the intended tuning:

- do not fake relationship dominance
- do not leave the domain on a generic fallback when subtype richness exists

## 5. Clusters

## 5.1 Public main

1. `relationship_trust_bond`
   - main packet: `venus_trine_saturn_trust_bond_chart_exact`
   - subtype: `trust_bond`
   - cluster strength: `0.5581`
   - public priority: `0.6681`
   - read: relationship public-main is now anchored in trust / steadiness / consistency

2. `career_career_like_aquarius_mc_mars_conjunct_mc_visible_freedom_drive`
   - main packet: `aquarius_mc_mars_conjunct_mc_visible_freedom_drive`
   - members:
     - `aquarius_mc_mars_conjunct_mc_visible_freedom_drive` as `primary_anchor`
     - `aquarius_mc_mars_conjunct_mc_visible_freedom_drive_aux` as `modifier`
   - read: career still owns the clearest chart-defining outward line

3. `mind_mind_like_mind_mind_system`
   - main packet: `mind_mind_system`
   - member:
     - `mind_mind_system` as `primary_anchor`
     - `mind_mind_system_aux` as `modifier`
   - read: current mind-system line stays the main public mind representative

4. `identity_identity_like_gemini_asc_venus_1h_social_relational_presence_chart_exact`
   - main packet: `gemini_asc_venus_1h_social_relational_presence_chart_exact`
   - read: identity remains public-main and no longer relies on packet fallback alone

## 5.2 Detail

1. `mind_mind_like_mercury_sextile_9h_capricorn_aquarius_intellectual_authority_chart_exact`
   - main packet: `mercury_sextile_9h_capricorn_aquarius_intellectual_authority_chart_exact`

2. `relationship_attraction_signal`
   - main packet: `venus_trine_mars_relational_attraction_signal_chart_exact`
   - subtype: `attraction_signal`

3. `relationship_love_like_relationship_relationships`
   - main packet: `relationship_relationships`
   - role after tuning: generic fallback only

4. `identity_identity_like_sun_aries_12h_hidden_private_fire_chart_exact`
   - main packet: `sun_aries_12h_hidden_private_fire_chart_exact`

5. `relationship_emotional_routine_sensitivity`
   - main packet: `moon_scorpio_6h_emotional_routine_sensitivity_chart_exact`
   - subtype: `emotional_routine_sensitivity`

### Cluster verdict

This is much closer to the intended structure:

- one specific relationship subtype wins public_main
- the second relationship subtype remains available in detail
- Moon Scorpio daily sensitivity stays available as a separate need/detail line
- generic relationship remains preserved, but no longer monopolizes the domain

## 6. Public surfaces

## 6.1 `profile_narrative_projection_v1`

- core block count: `4`
- extra block count: `5`
- source graph: `natal_promise_cluster_plan_v1`

### Core blocks

1. `promise::venus_trine_saturn_trust_bond_chart_exact`
   - headline: `Sevgi verdiğinde bunun içinde tutarlılık ve söz taşıyan bir taraf var.`

2. `promise::aquarius_mc_mars_conjunct_mc_visible_freedom_drive`
   - headline: `Görünür işte cesur başlatıcılık, bağımsız hareket ve canlı yön duygusu.`

3. `promise::mind_mind_system`
   - headline: `Ne yapacağını bildiğin an tempo kendiliğinden yükselir.`

4. `promise::gemini_asc_venus_1h_social_relational_presence_chart_exact`
   - headline: `Duruşun hafif görünse de kimle ne kadar açılacağını hızlı sezebiliyor olabilirsin.`

### Extra blocks

1. `promise::moon_scorpio_6h_emotional_routine_sensitivity_chart_exact`
   - headline: `Duygun, günlük akışta bile kolay yüzeyde kalmayabilir; küçük şeyler içeride daha derine işleyebilir.`

2. `promise::mercury_sextile_9h_capricorn_aquarius_intellectual_authority_chart_exact`
   - headline: `Bir fikri sadece bulmak değil, ona sağlam bir çerçeve vermek sende güçlü olabilir.`

3. `promise::sun_aries_12h_hidden_private_fire_chart_exact`
   - headline: `Sende dışarıdan hemen görünmeyen ama içeride hızla alevlenen bir taraf olabilir.`

4. `promise::venus_trine_mars_relational_attraction_signal_chart_exact`
   - headline: `Birine yaklaşırken bunu yalnızca sözle değil tonunla ve enerjinle de hissettirmek.`

5. `promise::relationship_relationships`
   - headline: `Sen ilişkide yüzeysel bir sıcaklıktan çok, içine oturan bir güven arıyorsun.`

### Narrative verdict

The main improvement is obvious here:

- relationship core is now specific and subtype-led
- generic relationship copy survives only as extra/detail
- the chart now reads as trust-bond first, attraction and emotional-sensitivity second

## 6.2 `profile_v8_projection_v1`

### Hero

- node: `promise::gemini_asc_venus_1h_social_relational_presence_chart_exact`
- headline: `Duruşun hafif görünse de kimle ne kadar açılacağını hızlı sezebiliyor olabilirsin.`

### Identity axis

- node: `promise::sun_aries_12h_hidden_private_fire_chart_exact`
- headline: `Sende dışarıdan hemen görünmeyen ama içeride hızla alevlenen bir taraf olabilir.`

### Insight strip

1. `Kariyer`
   - node: `promise::aquarius_mc_mars_conjunct_mc_visible_freedom_drive`
   - title: `Görünür işte cesur başlatıcılık, bağımsız hareket ve canlı yön duygusu.`

2. `İlişki`
   - node: `promise::venus_trine_saturn_trust_bond_chart_exact`
   - title: `Sevgi verdiğinde bunun içinde tutarlılık ve söz taşıyan bir taraf var.`

3. `Zihin`
   - node: `promise::mind_mind_system`
   - title: `Sen dışarıdan meraklı ve hareketli görünebilirsin.`

### Differentiators

1. `promise::aquarius_mc_mars_conjunct_mc_visible_freedom_drive_aux`
2. `promise::moon_scorpio_6h_emotional_routine_sensitivity_chart_exact`
3. `promise::mercury_sextile_9h_capricorn_aquarius_intellectual_authority_chart_exact`

### V8 verdict

v8 remains stable where it should:

- hero stays on Gemini ASC + Venus 1H
- identity_axis stays on Sun Aries 12H hidden/private fire
- relationship becomes more specific in the insight layer without displacing the chart’s current hero logic

## 7. What changed in code

Only selection-layer behavior changed.

### Cluster-plan tuning

- relationship v0.4 packets now resolve to explicit subtypes:
  - `trust_bond`
  - `attraction_signal`
  - `emotional_routine_sensitivity`
- relationship becomes a required represented domain at `supporting` tier when subtype richness exists
- generic relationship clusters are suppressed from public_main when multiple specific subtype alternatives exist at comparable priority

### Packet-selection tuning

- selected packet inventory gets a narrow backfill from existing chart-signature packets when:
  - selected inventory is still thin
  - generic relationship is occupying a slot
  - multiple specific relationship packets exist
  - an additional missing domain packet can be added without aux inflation

This is why selected count increases from `3` to `4` on this chart, while 1996 Istanbul and Adana stay stable under the test suite.

## 8. Remaining issues

This is better, but not final-perfect.

1. relationship score is still `supporting`, not `medium_strong`
   - selection is fixed, but focus scoring still underweights the domain relative to its subtype count

2. selected packets still include generic `relationship_relationships`
   - this is acceptable for fallback continuity
   - but if packet-only fallback quality becomes a priority later, selected-path representative choice can be tuned separately

3. mind main is still `mind_mind_system`
   - `mercury_sextile_9h_capricorn_aquarius_intellectual_authority_chart_exact` remains detail
   - that is acceptable for this pass because renderer/hero architecture was intentionally left untouched

4. detail is still carrying important semantic weight
   - `Sun Aries 12H`
   - `Moon Scorpio 6H`
   - `Venus trine Mars`
   - `Mercury sextile 9H authority`

That is not wrong, but it means the next tuning pass, if needed, should be about promotion heuristics rather than packet coverage.

## 9. Regression status

Target test run:

```bash
PYTHONPATH=backend backend/venv/bin/pytest \
  backend/tests/test_natal_promise_packets.py \
  backend/tests/test_natal_promise_cluster_plan.py \
  backend/tests/test_natal_public_builder.py \
  backend/tests/test_projection_shadow_v1_builder.py -q
```

Result:

- `67 passed`

Spot-checks:

- 1996 Istanbul selected packets remain `3`
- 1996 Istanbul public_main ordering remains unchanged
- Adana public_main still surfaces specific relationship and identity families; no aux inflation regression observed

## 10. Verdict

v0.4.1 solves the right problem.

The 2020 chart no longer wastes its relationship slot on generic fallback copy. Candidate coverage stays the same, but selection now converts that coverage into a more believable public surface:

- specific relationship trust line in main
- generic relationship demoted
- identity broadening in selected path
- no architectural blast radius

This is a clean selection-layer improvement, not a source-layer or renderer-layer workaround.
