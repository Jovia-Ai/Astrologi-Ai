# Normal-Case ClusterPlan Audit

Scope:
- analysis only
- live current system
- no code / registry / scoring / renderer / selection changes

Method:
- raw chart computed through `compute_natal_chart(...)` with explicit coordinates/timezone
- public output computed through route-equivalent `interpret_natal_chart_ui(..., include_full_profile=True)`
- current `candidate_inventory`, `focus_map`, `clusters`, `public_main/support/detail`, `profile_narrative_projection_v1`, and `profile_v8_projection_v1` evaluated as-is

## Chart 1

### `1959-10-21 11:00 Kütahya`

### 1. Raw chart signature

- Angles:
  - `ASC Sagittarius`
  - `MC Libra`
  - `DSC Gemini`
  - `IC Aries`
- Major placements:
  - `Sun Libra 10H`
  - `Moon Gemini 6H`
  - `Mercury Scorpio 11H`
  - `Venus Virgo 9H`
  - `Mars Libra 10H`
  - `Jupiter Sagittarius 11H`
  - `Saturn Capricorn 1H`
  - `Uranus Leo 8H`
  - `Neptune Scorpio 10H`
  - `Pluto Virgo 8H`
  - `North Node Libra 9H`
  - `Chiron Aquarius 2H`
- Strong concentrations:
  - `10H`: Sun, Mars, Neptune
  - `11H`: Mercury, Jupiter
  - `8H`: Uranus, Pluto
  - `9H`: Venus, Node
- Tight aspects under `5°`:
  - `Sun conjunct Mars 2.77`
  - `Sun sextile Saturn 4.94`
  - `Mars sextile Saturn 2.17`
  - `Mercury square Uranus 2.74`
  - `Moon sextile Uranus 1.52`
  - `Saturn trine Pluto 3.43`
  - `Saturn sextile Neptune 4.19`
  - `Jupiter square Pluto 2.56`
- Natural dominant domains:
  - `career/public role` strong
  - `mind/social vision/community` strong
  - `identity/authority` medium-strong
  - `depth / 8H intensity` secondary
- Not naturally dominant:
  - `relationship` is not a primary chart driver here

### 2. Current system state

- `candidate_inventory`:
  - `career_career_visibility`
  - `career_career_visibility_aux`
  - `career_career_visibility_aux`
  - `mind_mind_system`
  - `mind_mind_system_aux`
  - `mind_mind_system_aux`
  - `relationship_relationships`
  - `relationship_relationships_aux`
  - `relationship_relationships_aux`
  - `saturn_trine_pluto_deep_resilience_chart_exact`
- `focus_map`:
  - `mind strong`
  - `relationship strong`
  - `career strong`
  - `identity detail_only`
- `clusters`:
  - `career_career_like_career_career_visibility`
  - `mind_mind_like_mind_mind_system`
  - `relationship_love_like_relationship_relationships`
  - `identity_gift_like_saturn_trine_pluto_deep_resilience_chart_exact`
- `public_main`:
  - `mind_mind_like_mind_mind_system`
  - `relationship_love_like_relationship_relationships`
  - `career_career_like_career_career_visibility`
  - `identity_gift_like_saturn_trine_pluto_deep_resilience_chart_exact`
- `public_support`: empty
- `detail`: empty
- `suppressed_packets`:
  - duplicate `mind_mind_system_aux`
  - duplicate `relationship_relationships_aux`
  - duplicate `career_career_visibility_aux`

### 3. Public surfaces summary

- `profile_narrative_projection_v1`
  - core:
    - `mind_mind_system`: `Cümle yerine oturduğu anda iç ritmin de hızlanır.`
    - `relationship_relationships`: `Sen ilişkide yüzeysel bir sıcaklıktan çok, içine oturan bir güven arıyorsun.`
    - `career_career_visibility`: `İnsanlar önce kalite çıtasını, sonra etkini görür.`
    - `saturn_trine_pluto_deep_resilience_chart_exact`: `Zorlandığında bile dağılıp gitmeyen, içeride yapı kuran bir gücün var.`
  - extra: empty
- `profile_v8_projection_v1`
  - hero: `mind_mind_system`
  - identity_axis: `saturn_trine_pluto_deep_resilience_chart_exact`
  - insight_strip:
    - relationship
    - career
    - mind aux
  - differentiators:
    - relationship aux
    - career aux
    - `mind_mind_system`

### 4. What the system captures well

- It does recognize that this chart is not thin; `career`, `mind`, and `public presence` all surface.
- `saturn_trine_pluto_deep_resilience_chart_exact` is a fair secondary signature for the Capricorn 1H / structural backbone side.
- Generic `career` fallback is directionally plausible because the chart really is 10H-heavy.

### 5. What it misses or over-forces

- It over-forces `relationship` into a primary domain. Raw chart support for relationship is weaker than the system ranking suggests.
- It misses the actual `10H Libra + Sun/Mars/Neptune` public style and the `11H Mercury/Jupiter` collective/mind signature.
- It misses the chart’s `8H/11H/9H` richness and collapses too quickly into generic `mind / relationship / career`.
- `ASC Sagittarius + Saturn 1H Capricorn` identity structure is under-read.

### 6. Structural flags

- `chart-fact leaks`: none found
- `generic fallback dominance`: high
- `empty support/detail`: yes
- `v8 duplication`: yes
  - differentiators repeat core-level material (`mind`, `career`)

### 7. Verdict

- `healthy enough / accepted as normal-case sample`: borderline
- strongest call: `needs semantic coverage`
- reason:
  - current system is directionally plausible, but too fallback-heavy and too relationship-forward for the actual chart

## Chart 2

### `1996-05-20 00:45 İzmir`

### 1. Raw chart signature

- Angles:
  - `ASC Aquarius`
  - `MC Scorpio`
  - `DSC Leo`
  - `IC Taurus`
- Major placements:
  - `Sun Taurus 4H`
  - `Moon Gemini 5H`
  - `Mercury Taurus 3H`
  - `Venus Gemini 5H`
  - `Mars Taurus 3H`
  - `Jupiter Capricorn 12H`
  - `Saturn Aries 2H`
  - `Uranus Aquarius 1H`
  - `Neptune Capricorn 12H`
  - `Pluto Sagittarius 10H`
  - `North Node Libra 8H`
  - `Chiron Libra 8H`
- Strong concentrations:
  - `3H`: Mercury, Mars
  - `5H`: Moon, Venus
  - `8H`: Node, Chiron
  - `12H`: Jupiter, Neptune
  - `1H`: Uranus
- Tight aspects under `5°`:
  - `Saturn sextile Uranus 0.02`
  - `Moon conjunct Venus 1.59`
  - `Sun trine Neptune 1.53`
  - `Sun opposite Pluto 2.64`
  - `Uranus sextile Pluto 2.72`
  - `Saturn trine Pluto 2.74`
  - `Mercury trine Jupiter 4.48`
  - `Mars trine Jupiter 4.52`
- Natural dominant domains:
  - `identity / self-definition` strong
  - `mind / voice / communication` strong
  - `creativity / romance / self-expression` medium-strong
  - `home / roots` medium-strong
  - `inner world / 12H` medium-strong
  - `8H depth / threshold / intimacy` medium-strong
- Not naturally dominant:
  - `career` is not the first native owner of this chart, even with `MC Scorpio + Pluto 10H`

### 2. Current system state

- `candidate_inventory`:
  - `saturn_sextile_uranus_structured_originality_identity_chart_exact` `chart_facts_match=false`
  - `saturn_trine_pluto_deep_resilience_chart_exact`
  - `career_career_visibility`
- `focus_map`:
  - `career supporting`
  - `identity detail_only`
- `clusters`:
  - `identity_gift_like_saturn_trine_pluto_deep_resilience_chart_exact`
  - `career_career_like_career_career_visibility`
- `public_main`:
  - `career_career_like_career_career_visibility`
  - `identity_gift_like_saturn_trine_pluto_deep_resilience_chart_exact`
- `public_support`: empty
- `detail`: empty
- `suppressed_packets`:
  - `saturn_sextile_uranus_structured_originality_identity_chart_exact`
  - correctly held in `debug/transit_activation` only

### 3. Public surfaces summary

- `profile_narrative_projection_v1`
  - core:
    - `career_career_visibility`: `Perde açılmadan önce içeride uzun bir son prova olur.`
    - `saturn_trine_pluto_deep_resilience_chart_exact`
    - `saturn_sextile_uranus_structured_originality`
    - one raw `mgv11` shadow node
  - extra:
    - multiple raw `mgv11_node_*` blocks
    - includes labels like `Ay Kavuşum Venüs Gölge`
    - includes `Micro Insight`
- `profile_v8_projection_v1`
  - hero: `saturn_sextile_uranus_structured_originality`
  - identity_axis: `saturn_trine_pluto_deep_resilience_chart_exact`
  - insight_strip:
    - `Uranüs 1. ev`
    - `Ay 5. ev`
    - `Plüto 10. ev Gölge`
  - differentiators:
    - `Kendini dışarıdan çok içeride, ait olduğun yerde ve özel alanında daha gerçek yaşarsın.`
    - `Micro Insight`
    - `Ay Kavuşum Venüs Gölge`

### 4. What the system captures well

- It does pick up a real `identity` axis through Uranus/Saturn/Pluto-type structure.
- It does not publicly leak the false `chart_exact` Saturn-Uranus identity packet; the correctness guard is holding.
- It senses that there is depth and structural resilience in the chart.

### 5. What it misses or over-forces

- It severely under-reads the actual chart:
  - `Aquarius ASC + Uranus 1H`
  - `Mercury/Mars Taurus 3H`
  - `Sun Taurus 4H`
  - `Moon/Venus Gemini 5H`
  - `Jupiter/Neptune 12H`
  - `Node/Chiron 8H`
- It over-forces `career` from a thin fallback path.
- It lets legacy `mgv11` nodes dominate public surfaces because candidate inventory is too sparse.
- This is not a copy-only problem; the chart is semantically under-covered.

### 6. Structural flags

- `chart-fact leaks`: no false-anchor leak found
  - `Uranüs 1. ev` is actually true on this chart
- `generic fallback dominance`: extreme
- `empty support/detail`: yes
- `v8 duplication`: less duplication than some others, but public surfaces degrade into raw/legacy node labels
- `public quality problem`: yes
  - `Micro Insight`
  - `Ay Kavuşum Venüs Gölge`
  - multiple `mgv11_node_*` surfaces

### 7. Verdict

- `needs semantic coverage`
- not `P0 truthfulness`
- not `copy polish only`
- reason:
  - the main issue is sparse chart-specific coverage causing legacy/generic surfaces to take over

## Chart 3

### `2007-07-19 13:30 İzmir`

### 1. Raw chart signature

- Angles:
  - `ASC Libra`
  - `MC Cancer`
  - `DSC Aries`
  - `IC Capricorn`
- Major placements:
  - `Sun Cancer 9H`
  - `Moon Virgo 11H`
  - `Mercury Cancer 9H`
  - `Venus Virgo 10H`
  - `Mars Taurus 7H`
  - `Jupiter Sagittarius 2H`
  - `Saturn Leo 10H`
  - `Uranus Pisces 5H`
  - `Neptune Aquarius 4H`
  - `Pluto Sagittarius 3H`
  - `North Node Pisces 5H`
  - `Chiron Aquarius 4H`
- Strong concentrations:
  - `9H`: Sun, Mercury
  - `10H/11H`: Venus, Saturn, Moon
  - `4H`: Neptune, Chiron
  - `5H`: Uranus, Node
- Tight aspects under `5°`:
  - `Sun sextile Moon 1.14`
  - `Mercury sextile Venus 4.61`
  - `Moon square Pluto 1.64`
  - `Saturn trine Pluto 2.53`
  - `Saturn opposition Neptune 3.07`
  - `Mars sextile Uranus 1.05`
  - `Mars square Chiron 3.42`
- Natural dominant domains:
  - `career / contribution / visible competence` strong
  - `mind / worldview / 9H meaning` strong
  - `home / inner sensitivity / roots` medium-strong
  - `creativity / self-expression` medium
  - `relationship` secondary, not primary owner

### 2. Current system state

- `candidate_inventory`:
  - `career_career_visibility`
  - `career_career_visibility_aux`
  - `career_career_visibility_aux`
  - `libra_asc_venus_chart_ruler_chart_exact`
  - `mind_mind_system`
  - `mind_mind_system_aux`
  - `mind_mind_system_aux`
  - `relationship_relationships`
  - `relationship_relationships_aux`
  - `relationship_relationships_aux`
  - `saturn_trine_pluto_deep_resilience_chart_exact`
  - `neptune_4h_soft_inner_presence_chart_exact`
  - `mars_square_chiron_tender_courage_chart_exact`
- `focus_map`:
  - `career strong`
  - `mind strong`
  - `relationship strong`
  - `identity medium_strong`
- `clusters`:
  - `career_career_like_career_career_visibility`
  - `identity_identity_like_libra_asc_venus_chart_ruler_chart_exact`
  - `mind_mind_like_mind_mind_system`
  - `relationship_love_like_relationship_relationships`
  - `identity_gift_like_saturn_trine_pluto_deep_resilience_chart_exact`
  - `identity_identity_like_neptune_4h_soft_inner_presence_chart_exact`
  - `identity_wound_like_mars_square_chiron_tender_courage_chart_exact`
- `public_main`:
  - `career_career_like_career_career_visibility`
  - `mind_mind_like_mind_mind_system`
  - `relationship_love_like_relationship_relationships`
  - `identity_gift_like_saturn_trine_pluto_deep_resilience_chart_exact`
- `public_support`: empty
- `detail`:
  - `identity_identity_like_libra_asc_venus_chart_ruler_chart_exact`
  - `identity_identity_like_neptune_4h_soft_inner_presence_chart_exact`
  - `identity_wound_like_mars_square_chiron_tender_courage_chart_exact`

### 3. Public surfaces summary

- `profile_narrative_projection_v1`
  - core:
    - `career_career_visibility`: `İnsanlar önce kalite çıtasını, sonra etkini görür.`
    - `mind_mind_system`: `İçeride netleştiğin an dışarıdaki tempo da rahatlar.`
    - `relationship_relationships`
    - `saturn_trine_pluto_deep_resilience_chart_exact`
  - extra:
    - `libra_asc_venus_chart_ruler_chart_exact`
    - `mars_square_chiron_tender_courage_chart_exact`
    - `neptune_4h_soft_inner_presence_chart_exact`
- `profile_v8_projection_v1`
  - hero: `mind_mind_system`
  - identity_axis: `libra_asc_venus_chart_ruler_chart_exact`
  - insight_strip:
    - resilience
    - relationship
    - career
  - differentiators:
    - `relationship_relationships_aux`
    - `career_career_visibility_aux`
    - `mars_square_chiron_tender_courage_chart_exact`

### 4. What the system captures well

- It does pick up several genuinely present strands:
  - social/relational Libra rising tone
  - career/public competency
  - Neptune 4H softness
  - Mars-Chiron vulnerability/courage
- This is the healthiest of the four ordinary charts structurally.

### 5. What it misses or over-forces

- It over-forces `relationship` as a strong public-main owner.
- It misses the actual `Cancer 9H Sun/Mercury` meaning/worldview/learning signature.
- It also under-reads `Virgo 10H/11H` competence/service/community specifics.
- `4H Neptune/Chiron` is present but not given enough weight compared with generic relationship fallback.

### 6. Structural flags

- `chart-fact leaks`: none found
- `generic fallback dominance`: high
  - `career`, `mind`, and `relationship` are all generic fallback-owned
- `empty support/detail`: support empty, detail present
- `v8 duplication`: yes
  - differentiator repeats the same `career` headline as core

### 7. Verdict

- `healthy enough / accepted as normal-case sample`
- secondary note: `needs semantic coverage`
- reason:
  - the system is not broken here, but it still defaults too quickly to generic owners instead of chart-exact 9H/10H/4H semantics

## Chart 4

### `2012-08-02 13:45 İstanbul`

### 1. Raw chart signature

- Angles:
  - `ASC Scorpio`
  - `MC Leo`
  - `DSC Taurus`
  - `IC Aquarius`
- Major placements:
  - `Sun Leo 9H`
  - `Moon Aquarius 3H`
  - `Mercury Leo 9H`
  - `Venus Gemini 8H`
  - `Mars Libra 11H`
  - `Jupiter Gemini 8H`
  - `Saturn Libra 12H`
  - `Uranus Aries 5H`
  - `Neptune Pisces 4H`
  - `Pluto Capricorn 2H`
  - `North Node Sagittarius 1H`
  - `Chiron Pisces 4H`
- Strong concentrations:
  - `3H/9H axis`: Moon 3H, Sun/Mercury 9H
  - `8H`: Venus, Jupiter
  - `4H`: Neptune, Chiron
  - `11H`: Mars
  - `12H`: Saturn
- Tight aspects under `5°`:
  - `Sun sextile Jupiter 0.02`
  - `Mercury trine North Node 0.40`
  - `Sun trine Uranus 2.16`
  - `Moon trine Mars 2.40`
  - `Sun opposition Moon 3.94`
  - `Venus trine Saturn 1.64`
  - `Jupiter sextile Uranus 2.14`
  - `Neptune square North Node 0.37`
- Natural dominant domains:
  - `mind / learning / worldview axis` strong
  - `home / inner world / emotional base` medium-strong
  - `depth / 8H intimacy / resources` medium-strong
  - `community / 11H action` medium
  - `identity` secondary
- Not naturally dominant:
  - `career` is not a primary chart owner here

### 2. Current system state

- `candidate_inventory`:
  - `career_career_visibility`
  - `career_career_visibility_aux`
  - `career_career_visibility_aux`
  - `venus_trine_saturn_trust_bond`
  - `venus_trine_saturn_trust_bond_aux`
  - `venus_trine_saturn_trust_bond_aux`
  - `neptune_4h_soft_inner_presence_chart_exact`
- `focus_map`:
  - `career strong`
  - `relationship strong`
  - `identity supporting`
- `clusters`:
  - `career_career_like_career_career_visibility`
  - `relationship_trust_bond`
  - `identity_identity_like_neptune_4h_soft_inner_presence_chart_exact`
- `public_main`:
  - `career_career_like_career_career_visibility`
  - `relationship_trust_bond`
  - `identity_identity_like_neptune_4h_soft_inner_presence_chart_exact`
- `public_support`: empty
- `detail`: empty

### 3. Public surfaces summary

- `profile_narrative_projection_v1`
  - core:
    - `career_career_visibility`: `İçinde yerine oturmayan şeyi dışarı taşımak istemezsin.`
    - `venus_trine_saturn_trust_bond`
    - `neptune_4h_soft_inner_presence_chart_exact`
  - extra: empty
- `profile_v8_projection_v1`
  - hero: `career_career_visibility`
  - identity_axis: `neptune_4h_soft_inner_presence_chart_exact`
  - insight_strip:
    - trust bond
    - career aux
    - trust bond aux
  - differentiators:
    - `career_career_visibility`
    - `neptune_4h_soft_inner_presence_chart_exact`
    - `venus_trine_saturn_trust_bond`

### 4. What the system captures well

- It does catch two real chart strands:
  - `Venus trine Saturn` trust / reliability
  - `Neptune 4H` soft inner presence
- It senses that the chart is not raw or loud; there is an internal filtering quality.

### 5. What it misses or over-forces

- It over-forces `career` into the dominant owner position.
- It almost completely misses the chart’s strongest axis:
  - `Sun/Mercury 9H`
  - `Moon 3H`
  - `Sun opposite Moon`
- It also misses:
  - `Venus/Jupiter 8H`
  - `Saturn 12H`
  - `Mars 11H`
  - `Node 1H`
- This chart reads like a mixed `mind / worldview / depth / inner-world` chart, but the system compresses it into `career + relationship + soft identity`.

### 6. Structural flags

- `chart-fact leaks`: none found
- `generic fallback dominance`: very high
- `empty support/detail`: yes
- `v8 duplication`: severe
  - all three differentiators repeat the same three core themes

### 7. Verdict

- `needs semantic coverage`
- not `P0 truthfulness`
- not `copy polish only`
- reason:
  - raw chart emphasis and current selected/public emphasis are materially misaligned

## Overall Read

### Healthy enough / accepted as normal-case sample

- `2007-07-19 13:30 İzmir`

### Needs semantic coverage

- `1959-10-21 11:00 Kütahya`
- `1996-05-20 00:45 İzmir`
- `2012-08-02 13:45 İstanbul`

### Needs P0 truthfulness fix

- none in this batch

### Needs only copy polish

- none as primary verdict

### No action needed

- none

## Cross-chart pattern

On ordinary mixed charts, the current system tends to:

- over-promote generic `career_career_visibility`
- over-promote generic `relationship_relationships` even when relationship is not a raw dominant
- leave `public_support` and `detail` empty too often
- fall back to repeated v8 surfaces instead of producing distinct differentiators
- under-read 3H/4H/5H/8H/9H/12H mixed signatures unless an exact overlay already exists

The current system performs best when the chart already resembles an existing overlay family. It performs less naturally on mixed charts whose strongest signatures are distributed across communication, home, creativity, inner world, and worldview rather than one obvious identity/career/relationship archetype.
