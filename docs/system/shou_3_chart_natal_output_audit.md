# SHOU 3 Chart Natal Output Audit

## 1. Executive Summary
- Overall health: the engine is semantically strongest on Chart A, structurally richest but category-weak on Chart B, and undercovered/generic on Chart C.
- Biggest risks: generic-fallback cards occupying public-main, missing `public_job`, missing emitted `composed_detail_cards`, partial or absent `chart_fact_match`, duplicate-semantic public mirrors, and one real `packet_id` collision on Chart B.
- Best-performing chart: Chart A. It produces several chart-specific exact-registry cards with enough anchor depth to justify real slide expansion.
- Weakest chart: Chart C. It still finds one strong exact-registry identity card, but the rest of public output leans on generic fallback and the detail lane is empty.
- Immediate P0/P1 decisions:
  - No confirmed false chart-fact leak was found in current public copy, so there is no hard P0 delete based on explicit wrong astrology.
  - P1 before broader public use: fix generic-fallback public-main ownership on Charts B/C, suppress or compress duplicate mirrors on Chart A, dedupe the Chart B `moon_square_mercury_emotion_mind_friction_aux` collision, and emit `chart_fact_match` for fallback/discovery packets.
- Direct answer to the core audit question:
  - Reliable meaning today: Chart A `self_construction`, `attachment_architecture`, `speech_decision_language`; Chart B `refined_relational_language`, `tender_courage`, `need_affection_friction`; Chart C `unsettled_outer_signal`.
  - Correctly categorized today: mostly Chart A main owners; Chart B semantics are often right but current public owners are generic-fallback; Chart C only the identity lane is clearly correct.
  - Slide-strong today: A `capricorn_asc_sun_1h_composed_self_construction`, A `moon_leo_8h_deep_proud_heart`, A `saturn_3h_aries_speech_decision_language`, B `mercury_conjunct_venus_refined_relational_language` after ownership cleanup, B `mars_square_chiron_tender_courage` after renderer cleanup, B `moon_square_venus_need_affection_friction` as detail, C `uranus_square_asc_venus_unsettled_outer_signal`.
  - Compressed/debug today: most career/public-presence cards on B/C, the warm/aux mirrors on A, hidden/private on A, and all discovery-only C packets.

## Chart A — Istanbul 1996
### Raw Output Summary
- Raw capture: `docs/system/_generated_outputs/shou_natal_audit_raw_1996-12-28_07-10_istanbul.json`
- Full Card Passport table: `docs/system/_generated_outputs/shou_3_chart_card_passports_A.tsv`
- Truth issue table: `docs/system/_generated_outputs/shou_3_chart_truth_issues_A.tsv`
- Duplicate table: `docs/system/_generated_outputs/shou_3_chart_duplicate_groups_A.tsv`
- Voice table: `docs/system/_generated_outputs/shou_3_chart_voice_readiness_A.tsv`
- Slide decision table: `docs/system/_generated_outputs/shou_3_chart_slide_decisions_A.tsv`
- Surface recommendation table: `docs/system/_generated_outputs/shou_3_chart_surface_recommendations_A.tsv`
- Public cards: `10`
- Core blocks: `4`
- Extra blocks: `6`
- Composed detail cards: `0`
- Packets: `11`
- Clusters: `8`
- Coverage warnings: `generic_fallback_public_main`
- Health score: `94`
- Missing fields that materially affect the audit: `composed_detail_cards, public_job`

### Card Passport Table
| card_id | current surface | family | promise_type | origin | evidence | recommended surface | slide decision | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `capricorn_asc_sun_1h_composed_self_construction` | `core_block` | `identity_route` | `behavior_reflex` | `exact_registry` | `high` | `hero / core` | `5 slide` | Most reliable identity owner; chart-specific and multi-anchor. |
| `moon_leo_8h_deep_proud_heart` | `core_block` | `trust_intimacy` | `love_style` | `exact_registry` | `high` | `secondary core` | `3-4 slide` | Strong relationship owner; duplicate family mirrors should collapse under this one. |
| `saturn_3h_aries_speech_decision_language` | `core_block` | `need` | `mind_style` | `exact_registry` | `high` | `secondary core` | `3-4 slide` | Good chart-specific mind/decision lane. |
| `chiron_conjunct_mc_visibility_wound_to_voice_chart_exact` | `core_block` | `wound_to_gift` | `wound_to_gift` | `exact_registry` | `low` | `compressed trait/card` | `compressed card only` | Semantically useful but packet evidence too thin for slide expansion. |
| `saturn_trine_pluto_deep_resilience_chart_exact` | `extra_block` | `identity_route` | `gift` | `generic_fallback` | `low` | `compressed trait/card` | `compressed card only` | Public-main generic fallback occupant; keep only as compressed resilience trait. |
| `moon_trine_venus_emotional_warmth` | `extra_block` | `trust_intimacy` | `love_style` | `exact_registry` | `high` | `compressed trait/card` | `compressed card only` | Warmth sub-angle; should not compete with the main attachment card. |
| `moon_trine_venus_emotional_warmth_aux` | `extra_block` | `trust_intimacy` | `love_style` | `exact_registry` | `high` | `suppressed` | `suppress` | Aux mirror of the same meaning. |
| `saturn_3h_aries_speech_decision_language_behavior_reflex_overlay` | `extra_block` | `need` | `mind_style` | `exact_registry` | `high` | `compressed trait/card` | `compressed card only` | Useful modifier, not a separate public card. |
| `saturn_sextile_uranus_structured_originality_identity_chart_exact` | `extra_block` | `identity_route` | `gift` | `generic_fallback` | `low` | `composed detail` | `3-4 slide` | Can work as a narrow detail card after owner cleanup, not as free-standing public extra. |
| `mercury_conjunct_jupiter_big_mind_chart_exact` | `extra_block` | `mercury_signature` | `gift` | `generic_fallback` | `low` | `compressed trait/card` | `compressed card only` | Interesting but current public copy is too generic and mirrored. |
| `venus_sagittarius_12h_hidden_expansive_love_relationship_chart_exact` | `suppressed` | `hidden_private` | `career_signature` | `exact_registry` | `low` | `debug only` | `debug only` | Correctly withheld from public-main; keep as detail/debug candidate until hidden/private lane exists. |

### Family / Promise Distribution
- Strongest live families: `identity_route`, `trust_intimacy`, `need/mercury_signature`.
- Theoretical but not public: one `hidden_private` relationship packet is present and correctly suppressed out of public-main.
- Category quality: main owners are mostly correct, but one generic-fallback public-main occupant and several extra/detail mirrors blur the surface.

### Truthfulness Issues
| card_id | issue_type | severity | why it matters | recommended fix |
| --- | --- | --- | --- | --- |
| `chiron_conjunct_mc_visibility_wound_to_voice_chart_exact` | `weak_evidence` | `P2_quality_improvement` | Ortaya çıkmadan önce çok hazır olmak istemen, bazen sesinin değerini olduğundan geç vermene neden olabilir. | emit chart_fact_match for fallback/discovery packets or keep compressed/debug-only |
| `moon_leo_8h_deep_proud_heart` | `duplicate_semantic` | `P1_fix_before_public` | Kalbin güven olmadan tam açılmıyor olabilir. | keep one owner card; compress or suppress mirror card |
| `saturn_3h_aries_speech_decision_language_behavior_reflex_overlay` | `generic_fallback` | `P2_quality_improvement` | Bir şey sana çarptığında zihnin boşta kalmıyor; içeride hemen pozisyon alan bir taraf çalışıyor olabilir. | re-rank exact_registry owner above generic fallback or compress this card |

### Duplicate Risks
| duplicate_group_id | cards_involved | duplicate_type | decision |
| --- | --- | --- | --- |
| `A_dup_1` | `moon_leo_8h_deep_proud_heart|moon_trine_venus_emotional_warmth` | `core_extra_mirror` | keep `moon_leo_8h_deep_proud_heart`, demote `moon_trine_venus_emotional_warmth` |
| `A_dup_2` | `moon_leo_8h_deep_proud_heart|moon_trine_venus_emotional_warmth_aux` | `core_extra_mirror` | keep `moon_leo_8h_deep_proud_heart`, demote `moon_trine_venus_emotional_warmth_aux` |
| `A_dup_3` | `moon_trine_venus_emotional_warmth|moon_trine_venus_emotional_warmth_aux` | `support_as_main_duplicate` | keep `moon_trine_venus_emotional_warmth`, demote `moon_trine_venus_emotional_warmth_aux` |
| `A_dup_4` | `saturn_3h_aries_speech_decision_language_behavior_reflex_overlay|mercury_conjunct_jupiter_big_mind_chart_exact` | `support_as_main_duplicate` | keep `saturn_3h_aries_speech_decision_language_behavior_reflex_overlay`, demote `mercury_conjunct_jupiter_big_mind_chart_exact` |

### Slide Eligibility
- `5 slide`: `capricorn_asc_sun_1h_composed_self_construction`.
- `3-4 slide`: `moon_leo_8h_deep_proud_heart`, `saturn_3h_aries_speech_decision_language`.
- `compressed only`: `chiron_conjunct_mc_visibility_wound_to_voice_chart_exact`, `saturn_trine_pluto_deep_resilience_chart_exact`, `moon_trine_venus_emotional_warmth`, `saturn_sextile_uranus_structured_originality_identity_chart_exact`, `mercury_conjunct_jupiter_big_mind_chart_exact`.
- `debug only / suppress`: `moon_trine_venus_emotional_warmth_aux`, `venus_sagittarius_12h_hidden_expansive_love_relationship_chart_exact`.

### UX Surface Recommendation
- Keep identity/self-construction as hero/core.
- Keep `moon_leo_8h_deep_proud_heart` and `saturn_3h_aries_speech_decision_language` as secondary core lanes.
- Collapse `moon_trine_venus_*` into compressed/support, not separate public cards.
- Move hidden/private relationship output to composed-detail or debug until the lane exists.

### Fixes
- Remove or suppress relationship mirror cards so one cluster does not occupy three public slots.
- Demote the generic-fallback resilience/big-mind cards from public-main importance.
- Emit `chart_fact_match` consistently for the fallback/generic packets that still reach public.

## Chart B — Adana 1998
### Raw Output Summary
- Raw capture: `docs/system/_generated_outputs/shou_natal_audit_raw_1998-09-12_07-30_adana.json`
- Full Card Passport table: `docs/system/_generated_outputs/shou_3_chart_card_passports_B.tsv`
- Truth issue table: `docs/system/_generated_outputs/shou_3_chart_truth_issues_B.tsv`
- Duplicate table: `docs/system/_generated_outputs/shou_3_chart_duplicate_groups_B.tsv`
- Voice table: `docs/system/_generated_outputs/shou_3_chart_voice_readiness_B.tsv`
- Slide decision table: `docs/system/_generated_outputs/shou_3_chart_slide_decisions_B.tsv`
- Surface recommendation table: `docs/system/_generated_outputs/shou_3_chart_surface_recommendations_B.tsv`
- Public cards: `10`
- Core blocks: `4`
- Extra blocks: `6`
- Composed detail cards: `0`
- Packets: `22`
- Clusters: `19`
- Coverage warnings: `generic_fallback_public_main`
- Health score: `74`
- Missing fields that materially affect the audit: `composed_detail_cards, public_job`

### Card Passport Table
| card_id | current surface | family | promise_type | origin | evidence | recommended surface | slide decision | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `mercury_conjunct_venus_refined_relational_language` | `core_block` | `mercury_signature` | `gift` | `generic_fallback` | `medium` | `secondary core` | `3-4 slide` | Best current public mind card, but ownership is still generic-fallback. |
| `mars_square_chiron_tender_courage` | `core_block` | `wound_to_gift` | `wound_to_gift` | `generic_fallback` | `high` | `secondary core` | `3-4 slide` | Strong semantic packet; renderer/body ownership needs cleanup. |
| `mc_cancer_moon_gemini_9h_teaching_voice_chart_exact` | `core_block` | `public_presence` | `career_signature` | `generic_fallback` | `low` | `compressed trait/card` | `compressed card only` | Good route, thin evidence. |
| `venus_square_pluto_intense_love_chart_exact` | `core_block` | `trust_intimacy` | `love_style` | `generic_fallback` | `low` | `compressed trait/card` | `compressed card only` | Meaningful but too thin for slide deck. |
| `mars_leo_11h_warm_visible_drive_community_chart_exact` | `extra_block` | `gift` | `drive` | `generic_fallback` | `low` | `compressed trait/card` | `compressed card only` | Community color is visible, but not depth-ready. |
| `moon_square_mercury_emotion_mind_friction_aux` | `extra_block` | `wound_to_gift` | `wound_to_gift` | `generic_fallback` | `medium` | `debug only` | `debug only` | Current id-collision makes public use unsafe. |
| `moon_square_venus_need_affection_friction` | `extra_block` | `wound_to_gift` | `wound_to_gift` | `generic_fallback` | `high` | `composed detail` | `3-4 slide` | Best detail candidate in the chart; evidence and tension are both usable. |
| `libra_asc_venus_chart_ruler_chart_exact` | `extra_block` | `need` | `behavior_reflex` | `generic_fallback` | `low` | `compressed trait/card` | `compressed card only` | Nice social-reading trait, not enough depth. |
| `saturn_taurus_8h_steady_public_maturity_chart_exact` | `extra_block` | `public_presence` | `career_signature` | `generic_fallback` | `low` | `compressed trait/card` | `compressed card only` | Good compressed public maturity trait. |
| `mars_leo_11h_warm_visible_drive_chart_exact` | `extra_block` | `trust_intimacy` | `drive` | `generic_fallback` | `low` | `compressed trait/card` | `compressed card only` | Relationship/community overlap should stay compressed. |

### Family / Promise Distribution
- Semantically active families: `mercury_signature`, `wound_to_gift`, `trust_intimacy`, `public_presence`, `community/gift`.
- Current categorization problem: all public-main owners are still `generic_fallback` at cluster level even though exact-registry packets exist underneath.
- Hidden/private exists only in candidate space (`mercury_virgo_12h_private_analytical_mind_chart_exact`, `sun_virgo_12h_quiet_inner_self_chart_exact`) and is not public-ready yet.

### Truthfulness Issues
| card_id | issue_type | severity | why it matters | recommended fix |
| --- | --- | --- | --- | --- |
| `libra_asc_venus_chart_ruler_chart_exact` | `generic_fallback` | `P2_quality_improvement` | Bir ortama girdiğinde önce havayı ve insanlar arasındaki tonu okuyabilirsin. | re-rank exact_registry owner above generic fallback or compress this card |
| `libra_asc_venus_chart_ruler_chart_exact` | `weak_evidence` | `P2_quality_improvement` | Bir ortama girdiğinde önce havayı ve insanlar arasındaki tonu okuyabilirsin. | compress or rebuild packet with stronger support anchors |
| `moon_square_mercury_emotion_mind_friction_aux` | `raw_astro_leak` | `P2_quality_improvement` | Ay–Merkür geriliminin çalışması zihninin çalışma biçimini daha net gösteriyor. İçerideki gerilim de şu olabilir: Kalp hızlanırken zihin de h | renderer-side rewrite; keep semantics |
| `moon_square_mercury_emotion_mind_friction_aux` | `wrong_owner` | `P1_fix_before_public` | moon_square_mercury_emotion_mind_friction_aux | dedupe packet ids or append deterministic variant suffix |
| `moon_square_mercury_emotion_mind_friction_aux` | `duplicate_semantic` | `P2_quality_improvement` | Sevgi görmekle gerçekten anlaşılmış hissetmek sende aynı şey olmayabilir. | keep one owner card; compress or suppress mirror card |

### Duplicate Risks
- No high-confidence visible duplicate group was found on this chart.

### Slide Eligibility
- `3-4 slide after owner cleanup`: `mercury_conjunct_venus_refined_relational_language`, `mars_square_chiron_tender_courage`, `moon_square_venus_need_affection_friction`.
- `compressed only`: `mc_cancer_moon_gemini_9h_teaching_voice_chart_exact`, `venus_square_pluto_intense_love_chart_exact`, `mars_leo_11h_warm_visible_drive_community_chart_exact`, `libra_asc_venus_chart_ruler_chart_exact`, `saturn_taurus_8h_steady_public_maturity_chart_exact`, `mars_leo_11h_warm_visible_drive_chart_exact`.
- `debug only`: `moon_square_mercury_emotion_mind_friction_aux` until id-collision is fixed.

### UX Surface Recommendation
- Do not trust current `core` vs `extra` labels as category truth; the payload is semantically richer than the cluster owners suggest.
- Promote only the strongest three semantics into prototype slide surfaces after ownership cleanup.
- Keep the rest as compressed traits; avoid opening separate public detail sheets from current generic-fallback cards.

### Fixes
- Fix cluster ownership: exact-registry packets exist, but generic-fallback clusters own every public-main card.
- Resolve the `moon_square_mercury_emotion_mind_friction_aux` duplicate id collision before public use.
- Separate strong semantics from weak public copy: this chart needs owner/category fixes before voice polish.

## Chart C — Istanbul 2019
### Raw Output Summary
- Raw capture: `docs/system/_generated_outputs/shou_natal_audit_raw_2019-11-03_23-40_istanbul.json`
- Full Card Passport table: `docs/system/_generated_outputs/shou_3_chart_card_passports_C.tsv`
- Truth issue table: `docs/system/_generated_outputs/shou_3_chart_truth_issues_C.tsv`
- Duplicate table: `docs/system/_generated_outputs/shou_3_chart_duplicate_groups_C.tsv`
- Voice table: `docs/system/_generated_outputs/shou_3_chart_voice_readiness_C.tsv`
- Slide decision table: `docs/system/_generated_outputs/shou_3_chart_slide_decisions_C.tsv`
- Surface recommendation table: `docs/system/_generated_outputs/shou_3_chart_surface_recommendations_C.tsv`
- Public cards: `4`
- Core blocks: `4`
- Extra blocks: `0`
- Composed detail cards: `0`
- Packets: `14`
- Clusters: `4`
- Coverage warnings: `support_detail_empty|generic_fallback_public_main|mixed_chart_undercovered`
- Health score: `64`
- Missing fields that materially affect the audit: `composed_detail_cards, public_job`

### Card Passport Table
| card_id | current surface | family | promise_type | origin | evidence | recommended surface | slide decision | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `relationship_relationships` | `core_block` | `trust_intimacy` | `love_style` | `generic_fallback` | `medium` | `compressed trait/card` | `compressed card only` | Plausible but generic relationship owner; not distinct enough for slides. |
| `uranus_square_asc_venus_unsettled_outer_signal` | `core_block` | `wound_to_gift` | `wound_to_gift` | `exact_registry` | `high` | `hero / core` | `5 slide` | Best proof that the engine can still produce chart-specific meaning on the new chart. |
| `career_career_visibility` | `core_block` | `public_presence` | `career_signature` | `generic_fallback` | `low` | `compressed trait/card` | `compressed card only` | Meaning is generic and copy is not voice-ready. |
| `mercury_conjunct_venus_refined_relational_language_chart_exact` | `core_block` | `mercury_signature` | `gift` | `generic_fallback` | `low` | `compressed trait/card` | `compressed card only` | Semantic lane is real, but current rendered body leaks raw astro and generic fallback phrasing. |
| `relationship_relationships_aux` | `suppressed` | `trust_intimacy` | `love_style` | `generic_fallback` | `medium` | `debug only` | `debug only` | Weaker duplicate of the same relationship card. |
| `discovery_relationship_dsc_ruler_signature_composed` | `debug_only` | `trust_intimacy` | `` | `discovery_scaffold` | `low` | `debug only` | `debug only` | Discovery signal exists but is not public-quality yet. |
| `discovery_emotional_moon_signature_composed` | `debug_only` | `moon_signature` | `` | `discovery_scaffold` | `low` | `debug only` | `debug only` | Useful debug evidence that discovery/compositional grammar is searching new chart structure. |

### Family / Promise Distribution
- Public families are thin: `trust_intimacy`, `wound_to_gift`, `public_presence`, `mercury_signature`.
- Candidate-only families still exist (`need`, `home_family_signature`, `creative_signature`), but they do not reach public with enough quality.
- New-chart generalization: discovery/compositional grammar is active as debug evidence, but not yet strong enough to turn into public detail/core reliably.

### Truthfulness Issues
| card_id | issue_type | severity | why it matters | recommended fix |
| --- | --- | --- | --- | --- |
| `mercury_conjunct_venus_refined_relational_language_chart_exact` | `generic_fallback` | `P1_fix_before_public` | Kelimeler sende sadece anlatmak için değil, bağ kurmak için de çalışabilir. | re-rank exact_registry owner above generic fallback or compress this card |
| `mercury_conjunct_venus_refined_relational_language_chart_exact` | `weak_evidence` | `P1_fix_before_public` | Kelimeler sende sadece anlatmak için değil, bağ kurmak için de çalışabilir. | emit chart_fact_match for fallback/discovery packets or keep compressed/debug-only |
| `mercury_conjunct_venus_refined_relational_language_chart_exact` | `raw_astro_leak` | `P2_quality_improvement` | Merkür kavuşum Venüs ve Zarif dil aynı çizgiyi güçlendiriyor. Düşünce ve sevgi dili birbirine yakın çalışır; kelimelerle bağ kurmak, yumuşat | renderer-side rewrite; keep semantics |
| `relationship_relationships_aux` | `wrong_owner` | `P1_fix_before_public` | relationship_relationships_aux | dedupe packet ids or append deterministic variant suffix |
- Special note: Chart C has no emitted `chart_fact_match` flags on candidate packets. That is a data-contract gap, not yet a confirmed false-fact leak.

### Duplicate Risks
- No high-confidence visible duplicate group was found on this chart.

### Slide Eligibility
- `5 slide`: `uranus_square_asc_venus_unsettled_outer_signal`.
- `compressed only`: `relationship_relationships`, `career_career_visibility`, `mercury_conjunct_venus_refined_relational_language_chart_exact`.
- `debug only`: all `discovery_*` packets and `relationship_relationships_aux`.

### UX Surface Recommendation
- One real hero exists: `uranus_square_asc_venus_unsettled_outer_signal`.
- Relationship, career, and mercury cards should stay compressed.
- Discovery-only packets should remain debug-only until the grammar can emit public-quality owners.

### Fixes
- Fill the missing detail/support lane; `support_detail_empty` is real, not cosmetic.
- Emit truth flags for all candidate packets; right now Chart C cannot be truth-audited at packet level.
- Convert at least one discovery signal into a non-generic public/detail owner if the new-chart generalization is expected to hold.

### New Chart Generalization Quality
- The engine is not completely trapped by golden familiarity: `uranus_square_asc_venus_unsettled_outer_signal` is chart-specific and meaningful.
- But the broader generalization is still weak: 7 discovery packets are debug-only, 3 of 4 public-main owners are generic fallback, and there is no composed detail lane.
- Verdict: discovery/compositional grammar is present, but it is not yet robust enough to claim strong public generalization on a new chart.

## 5. Cross-Chart Family Inventory
Full TSV: `docs/system/_generated_outputs/shou_3_chart_family_inventory.tsv`

| family | total | A | B | C | avg evidence | slide-worthy | priority for golden voice | notes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `hidden_private` | 4 | 1 | 2 | 1 | 0.35 | 0 | `low` | candidate-based normalized family; payload has no canonical public family field |
| `mercury_signature` | 4 | 1 | 2 | 1 | 0.50 | 0 | `low` | candidate-based normalized family; payload has no canonical public family field |
| `need` | 9 | 3 | 3 | 3 | 0.53 | 1 | `medium` | candidate-based normalized family; payload has no canonical public family field |
| `public_presence` | 3 | 0 | 2 | 1 | 0.35 | 0 | `low` | candidate-based normalized family; payload has no canonical public family field |
| `trust_intimacy` | 9 | 3 | 3 | 3 | 0.66 | 1 | `medium` | candidate-based normalized family; payload has no canonical public family field |
| `wound_to_gift` | 11 | 1 | 8 | 2 | 0.63 | 0 | `low` | candidate-based normalized family; payload has no canonical public family field |

Missing expected families in public-quality form: `home_roots`, `creative_expression`, and any stable `hidden_private` slide lane.

## 6. Cross-Chart Slide-Worthy Inventory
- Strong 5-slide prototypes today: `capricorn_asc_sun_1h_composed_self_construction`, `uranus_square_asc_venus_unsettled_outer_signal`.
- Solid 3-4 slide prototypes after limited cleanup: `moon_leo_8h_deep_proud_heart`, `saturn_3h_aries_speech_decision_language`, `mercury_conjunct_venus_refined_relational_language`, `mars_square_chiron_tender_courage`, `moon_square_venus_need_affection_friction`.
- Compressed-only set today: most career/public-presence cards, generic relationship warmth mirrors, and all thin-evidence extras.
- Debug-only set today: hidden/private on A, id-collision mind friction on B, all discovery packets on C.

## 7. Data Contract Gaps
- `public_job` is absent in all three charts. This blocks direct audit of public/detail/debug ownership.
- `composed_detail_cards` is absent in all three charts even when detail clusters exist; the UX detail lane cannot be judged from emitted public data alone.
- `chart_fact_match` is partial on A/B and completely absent on C. Truthfulness is therefore only partially machine-auditable.
- `coverage_warnings` and `audit_metrics` only live under `cluster_plan.meta`; block-level surfaces do not expose them.
- Public blocks do not expose a canonical `family` field; the family inventory had to be normalized from packet id, promise_type, cluster domain, and anchors.
- There is no explicit card-level `origin` on blocks; it must be reconstructed from owner packet/cluster.

## 8. Voice Readiness Summary
Full TSV: `docs/system/_generated_outputs/shou_3_chart_voice_readiness.tsv`

- Best current voice-ready-ish cards: `chiron_conjunct_mc_visibility_wound_to_voice_chart_exact`, `uranus_square_asc_venus_unsettled_outer_signal`, `venus_square_pluto_intense_love_chart_exact` from a tone perspective only.
- Biggest voice failures: Chart C `mercury_conjunct_venus_refined_relational_language_chart_exact` (raw astro leak and fallback skeleton), Chart C `career_career_visibility` (repetition and translation smell), Chart B `moon_square_mercury_emotion_mind_friction_aux` (raw astro intro), Chart B `mars_square_chiron_tender_courage` (owner mismatch and repeated renderer skeleton).
- Systemic voice issue: many bodies repeat the same renderer skeletons (`aynı çizgiyi güçlendiriyor`, `bu hattın sağlam yanını`, `denge kaçtığında`). This is a renderer problem, not necessarily a semantic problem.

## 9. UX Surface Recommendations
Full TSV: `docs/system/_generated_outputs/shou_3_chart_surface_recommendations.tsv`

- Hero/core should be extremely selective: one hero and at most two strong secondary cores per chart.
- Extra should hold meaningful but non-owner cards, not mirrors of a stronger owner.
- Composed detail is currently a recommendation, not an emitted lane; A hidden/private and B need-affection friction are the clearest candidates once the lane exists.
- Compressed should absorb thin-evidence career/public-presence traits and generic-fallback relation warmers.
- Debug-only should contain discovery packets, id-collision cards, and unverified hidden/private or mind-friction variants.

## 10. Prioritized Fix List
| priority | fix_area | issue | affected_charts | affected_cards | recommended_patch | expected_impact | risk |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `P0` | public truth/suppression | No confirmed false chart fact leaked; keep current suppression guard intact. | `A,B,C` | n/a | Preserve truthfulness guard; do not loosen for coverage. | Protects trust. | Low |
| `P1` | category/ownership | Generic-fallback clusters own public-main where exact-registry packets already exist. | `B,C` and one lane in `A` | multiple public-main cards | Re-rank owner selection so chart-specific exact-registry cards beat generic fallback on public-main. | Immediate public quality jump without inventing semantics. | Medium |
| `P1` | engine/data fix | Duplicate `packet_id` collision for `moon_square_mercury_emotion_mind_friction_aux`. | `B` | `moon_square_mercury_emotion_mind_friction_aux` | Deduplicate ids or append deterministic variant suffix. | Removes unsafe public/debug ambiguity. | Medium |
| `P1` | slide eligibility/data contract | Missing `chart_fact_match` on all C packets and many A/B fallback packets. | `A,B,C` | fallback/discovery cards | Emit truth flags for every candidate packet that can influence public output. | Makes truth audit machine-checkable. | Low |
| `P1` | category/ownership | One semantic relationship cluster occupies three public cards. | `A` | `moon_leo_8h_deep_proud_heart`, `moon_trine_venus_*` | Keep one owner card, compress the warmer, suppress the aux mirror. | Reduces duplicate-semantic noise. | Low |
| `P2` | UX contract fix | Detail clusters exist but `composed_detail_cards` are not emitted. | `A,B` | hidden/private and detail candidates | Expose composed detail lane when packet quality threshold is met. | Unlocks slide UX without bloating core. | Medium |
| `P2` | renderer/voice fix | Repeated renderer skeletons and raw astro intros. | `A,B,C` | multiple public cards | Rewrite renderer templates; keep semantics fixed. | Voice readiness improves without reselecting semantics. | Low |
| `P3` | registry/grammar fix | C chart relies heavily on debug-only discovery packets and generic fallback. | `C` | discovery_* and generic public-main | Promote at least one discovery family into a public-quality owner where evidence is sufficient. | Better new-chart generalization. | Medium |
| `P4` | test/snapshot | Need regression coverage for new-chart undercoverage, id-collision, and duplicate public mirrors. | `A,B,C` | targeted cards above | Add snapshot assertions on surface-plan, suppressed packets, and duplicate ids. | Prevents silent drift. | Low |

## 11. Go / No-Go Recommendation
- Families ready for a golden voice contract now: `identity_route` on A (`self_construction`), `trust_intimacy` on A (`moon_leo_8h_deep_proud_heart`), `need/mercury_signature` on A (`saturn_3h_aries_speech_decision_language`), and `wound_to_gift` on C (`uranus_square_asc_venus_unsettled_outer_signal`).
- Families that can become Phase 2 slide prototypes after one ownership/renderer pass: `mercury_signature` on B, `wound_to_gift` on B, and `trust_intimacy` detail on B.
- Outputs that must stay compressed today: almost all `public_presence` cards, generic fallback relationship warmers, generic mercury gifts on C, and the thin-evidence identity/career fallback extras on A/B.
- Outputs that should stay suppressed/debug-only today: A hidden/private love, B `moon_square_mercury_emotion_mind_friction_aux`, all C `discovery_*` packets, and any aux mirror that duplicates an already stronger public owner.
- Final go/no-go answer:
  - Go for narrow Phase 2 slide prototyping on the six cards named above.
  - No-go for broad public rollout of B/C current surfaces until generic-fallback ownership and truth-flag gaps are fixed.
  - The engine today reliably produces a small set of chart-specific meanings, partially categorizes them correctly, and still overuses compressed/debug/generic fallback for the rest.
