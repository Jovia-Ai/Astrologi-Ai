# Transit Selection Regression Watchlist

This watchlist is the product-facing safety layer for Selection V3 tuning. Each item names the regression, what breaks, how it appears in product, which golden cases cover it, and the first thing to inspect when it fails.

## Daily Selection Regressions

### Daily top pick drifts away from the clearest lived signal
- What breaks: The lead daily card stops matching the strongest today-facing experience.
- Product symptom: The first card reads plausible but no longer feels like the obvious “today” experience.
- Related golden cases: `golden_daily_2026_03_04_top_pick`, `golden_daily_2026_03_04_temporal_contrast`, `golden_daily_2026_02_28_top_pick`, `golden_daily_2026_02_28_temporal_contrast`
- Severity: high
- Recommended first debugging check: compare `daily_selection.score_breakdown` and `selection_v3.evaluation.avg_delta_salience_score` for the winning card vs the displaced card.

### Low-signal day collapses into generic or empty daily
- What breaks: Soft but meaningful days no longer survive scorer or rerank.
- Product symptom: Day page feels empty, generic, or over-dramatized on a subtle date.
- Related golden cases: `golden_daily_2026_02_28_top_pick`, `golden_combined_2026_02_28_product_surface`
- Severity: high
- Recommended first debugging check: inspect daily eligibility gates and the candidate count for the low-signal case.

## Period Spine Regressions

### Story-first spine gets replaced by a merely loud event
- What breaks: Period selection reverts toward raw salience instead of coherent story spine.
- Product symptom: Period core feels noisier and less chapter-like.
- Related golden cases: `golden_period_2026_03_04_spine`, `golden_period_2026_02_28_spine`, `golden_combined_2026_03_04_product_surface`, `golden_combined_2026_02_28_product_surface`
- Severity: high
- Recommended first debugging check: compare `evaluation.spine_event_id`, `avg_story_score`, and `story_score` ordering for selected vs rejected candidates.

### Coverage safety overrides period coherence
- What breaks: Coverage keeps diverse domains but breaks the main narrative spine.
- Product symptom: Period cards look representative but not causally connected.
- Related golden cases: `golden_period_2026_03_04_spine`, `golden_period_2026_03_04_transform_supports`, `golden_period_2026_02_28_angle_supports`
- Severity: high
- Recommended first debugging check: inspect support ids and chapter roles after rerank/fill.

## Clustering Regressions

### Similar daily events stop collapsing
- What breaks: Same-feeling candidates escape clustering and become duplicate cards.
- Product symptom: Two daily cards feel like rewrites of each other.
- Related golden cases: `golden_daily_2026_03_04_cluster_collapse`, `golden_daily_2026_03_04_top_pick`, `golden_combined_2026_03_04_product_surface`
- Severity: high
- Recommended first debugging check: inspect `selection_v3.experience_clusters` and the suppressed support ids for the winning cluster.

### Clustering becomes too aggressive
- What breaks: Distinct second-card contrast gets flattened.
- Product symptom: Daily surface becomes one-note and loses the useful second card.
- Related golden cases: `golden_daily_2026_02_28_flow_shadow_balance`, `golden_combined_2026_02_28_product_surface`
- Severity: medium
- Recommended first debugging check: compare cluster keys and cluster sizes for the second card candidates.

## Fallback Regressions

### Fallback stops firing or fires too late
- What breaks: Truly weak days no longer get a meaningful daily rescue.
- Product symptom: Empty or nearly empty daily surface.
- Related benchmark cases: `daily_period_fallback_story`
- Severity: high
- Recommended first debugging check: inspect `used_period_fallback` and candidate gating before fallback selection.

### Period-derived promotion turns into hard fallback too often
- What breaks: Healthy promoted period cards start counting as fallback or fallback logic overrides better candidates.
- Product symptom: Daily cards feel abstract or stale even when the day has enough signal.
- Related golden cases: `golden_daily_2026_03_04_period_promotion_without_fallback`, `golden_combined_2026_03_04_product_surface`
- Severity: high
- Recommended first debugging check: compare `today_facing_fallback`, `is_period_derived`, and `used_period_fallback`.

## Personalization Regressions

### Personalization tie-break disappears where it should help
- What breaks: Hot-house/domain relevance stops nudging tied cases.
- Product symptom: Some high-context days feel less personal even though the spine is still coherent.
- Related golden cases: `golden_daily_2026_03_04_top_pick`, `golden_period_2026_03_04_spine`, `golden_combined_2026_03_04_product_surface`
- Severity: medium
- Recommended first debugging check: inspect `personalization_score` in daily score breakdown and `avg_personalization_bonus` in period evaluation.

### Personalization bias becomes too strong
- What breaks: Personalization starts overriding better temporal or narrative candidates.
- Product symptom: Different days keep selecting the same domains even when the day signal is elsewhere.
- Related golden cases: `golden_daily_2026_02_28_no_personalization_bias`, `golden_period_2026_02_28_no_personalization_bias`, `golden_combined_2026_02_28_product_surface`
- Severity: medium
- Recommended first debugging check: compare winners with and without personalization bonus on the same case.

## Narrative-Quality Regressions

### Specificity drops while scores still pass
- What breaks: Generic or flat copy starts beating sharper felt experiences.
- Product symptom: Product still renders valid cards, but they feel less “that’s exactly it.”
- Related golden cases: `golden_daily_2026_02_28_top_pick`, `golden_daily_2026_02_28_flow_shadow_balance`
- Severity: medium
- Recommended first debugging check: inspect `avg_narrative_score` and candidate-level narrative quality ratios.

### Balance collapses into shadow-only or flow-only
- What breaks: Rerank and quality weights stop protecting surface contrast.
- Product symptom: Daily surface feels too dramatic or too flat.
- Related golden cases: `golden_daily_2026_03_04_top_pick`, `golden_daily_2026_02_28_flow_shadow_balance`
- Severity: medium
- Recommended first debugging check: inspect selected cards’ `tone_face`, `aspect_mode_diversity`, and `shadow_only_surface`.

## Support-Diversity Regressions

### Period supports flatten into one role
- What breaks: Builder/peak/integrator mix collapses.
- Product symptom: Period section reads as one repeated flavor instead of a chapter.
- Related golden cases: `golden_period_2026_03_04_role_diversity`, `golden_period_2026_02_28_role_diversity`, `golden_period_2026_03_04_transform_supports`, `golden_period_2026_02_28_angle_supports`
- Severity: high
- Recommended first debugging check: inspect `evaluation.distinct_roles` and support ordering after the final fill pass.

## Blocked-Point / Exclusion Regressions

### Blocked public points leak into daily or period selections
- What breaks: Fortune, Vertex, Lilith, or similar noise candidates survive selection.
- Product symptom: Product surfaces start showing technically valid but editorially unwanted cards.
- Related golden cases: `golden_daily_2026_03_04_blocked_point_exclusion`, `golden_period_2026_03_04_blocked_point_exclusion`, `golden_daily_2026_02_28_blocked_point_exclusion`, `golden_period_2026_02_28_blocked_point_exclusion`
- Severity: high
- Recommended first debugging check: inspect the candidate pool before and after public eligibility filtering.
