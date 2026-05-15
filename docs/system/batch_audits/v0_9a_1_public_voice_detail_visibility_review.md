# v0.9a.1 Public Voice Detail Visibility Review

## Scope

This is a qualitative review of the `v0.9a.1` rollout using:

- [v0_9a_1_public_voice_detail_support_post_rollout_review.md](/Users/sahradenizozdogan/Astrologi-Ai/docs/system/batch_audits/v0_9a_1_public_voice_detail_support_post_rollout_review.md)

Reviewed charts:

- `fix04_h10_career_stellium`
- `tokyo_1998_06_21`
- `toronto_1976_06_26`

Flags used for inspection:

- `ENABLE_NATAL_PROMISE_PROJECTION_V1=true`
- `ENABLE_NATAL_PROMISE_PACKET_DEBUG=true`
- `ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9=true`
- `ENABLE_NATAL_COMPOSED_SEMANTICS_DETAIL_SUPPORT=true`
- `ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_VOICE_DETAIL_SUPPORT=true`
- `ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_MAIN=false`

No code changes were made for this review.

## Headline Finding

`v0.9a.1` is not metadata-only in the current implementation.

For all three focus charts, the `public_voice` composed packet is currently user-visible in:

- `profile_narrative_projection_v1.profile_public.extra_blocks`
- `profile_narrative_projection_v1.profile_public.blocks`
- `profile_v8_projection_v1.differentiators`

It does **not** currently appear in:

- `surface_plan.detail_cluster_ids`
- `profile_narrative_projection_v1.profile_public.detail_cards`
- `profile_v8_projection_v1.insight_strip`

So the rollout is already visible, but it is visible through packet-level extra-surface injection, not through a new detail-cluster route.

The semantic signal is strong. The copy-readiness is mixed. The current rendered text is noticeably more chart-specific than the generic career fallback, but it is still too templated and too uniform across all three charts to justify `public_support` yet.

---

## Chart Review

### 1. `fix04_h10_career_stellium`

#### 1. Current public career owner

- `cluster_id`: `career_career_like_career_career_visibility`
- `headline`: `İçinde yerine oturmayan şeyi dışarı taşımak istemezsin.`
- `body summary`: Current owner is still the generic `career_career_visibility` packet. It references `MC` and `Mercury 10H`, but the body loops around generic visibility language and repeated inner-readiness phrasing rather than owning the chart’s public-speech route cleanly.
- `source_type`: `generic_fallback`
- `fallback_quality`: `raw_generic_fallback`

#### 2. Composed public_voice candidate

- `subtype`: `public_voice`
- `confidence`: `0.94`
- `evidence_trace`:
  - `family_inputs`: `MC`, `MC_ruler`, `10H_planets`
  - `subtype_inputs`: `public_voice`
  - `primitive_facts`: `MC Gemini`, `Mercury Cancer 10H`, `Mars Cancer 10H`
- `domain_reason`: `["MC route", "MC ruler involved", "10H planet"]`
- `lived_scene`: `Dış dünyada yalnız ne yaptığın değil, nasıl konuştuğun ve nasıl konum aldığın da görünür hale geliyor.`
- `lived_scene_atoms`:
  - `bir toplantıda söz aldığında tonunun ağırlık taşıması`
  - `ne söylediğinin dışarıdaki rolünü güçlendirmesi`
- `gift`: `Kariyer/public rol hattını MC ve yöneticisi üzerinden daha net ayırabilmek.`
- `inner_tension`: `Görünür olmak, sorumluluk almak ve gerçekten hangi rolde görünmek istediğin her zaman aynı hızla çözülmeyebilir.`
- `growth_direction`: `Kariyer hattını yalnız görünürlük olarak değil, MC-yönetici-10. ev rotası olarak okumak.`
- `public_eligibility`:
  - `debug_eligible: true`
  - `detail_eligible: true`
  - `public_support_eligible: false`
  - `public_main_eligible: false`
- `keep_for / suppression state`: `["detail", "debug"]`

#### 3. Detail visibility

- Does the composed packet appear in `candidate_inventory` only?
  - No.
- Does it appear in ClusterPlan `suppressed/keep_for detail`?
  - Yes.
- Does it appear in `detail_cluster_ids`?
  - No.
- Does it appear in `profile_narrative_projection_v1` extra/detail blocks?
  - Yes, in `extra_blocks` and therefore also in `blocks`.
- Does it appear in `profile_v8` differentiators / insight strip / detail surface?
  - Yes, in `differentiators`.
  - No, in `insight_strip`.
  - No, in `detail_cards`.
- Is this rollout user-visible or metadata-only right now?
  - User-visible.

#### 4. Public copy if visible

It is visible.

- `headline`: `Dış dünyada yalnız ne yaptığın değil, nasıl konuştuğun ve nasıl konum aldığın da görünür hale geliyor.`
- `teaser`: `MC, yöneticisi ve görünür rol hattı birlikte kariyer temasını generic visibility fallback'ten daha spesifik biçimde taşıyor.`
- `body`: `MC, yöneticisi ve görünür rol hattı birlikte kariyer temasını generic visibility fallback'ten daha spesifik biçimde taşıyor. Dış dünyada yalnız ne yaptığın değil, nasıl konuştuğun ve nasıl konum aldığın da görünür hale geliyor. Kariyer/public rol hattını MC ve yöneticisi üzerinden daha net ayırabilmek üretim çizgine kalite ekliyor. Zorlayan tarafıysa görünür olmak, sorumluluk almak ve gerçekten hangi rolde görünmek istediğin her zaman aynı hızla çözülmeyebilir.`
- `chips`: `["Kariyer"]`
- `source cluster id`: none; this is currently packet-level detail injection from `promise::composed_career_route_v0_9a`, not a surfaced cluster id.

#### 5. Quality comparison

- Is composed candidate more chart-specific?
  - Yes.
- Is the current owner raw generic, customized, or cluster-specific?
  - Raw generic.
- Would composed candidate improve detail?
  - Yes.
- Would it improve `public_support` later?
  - Possibly, after copy-specific polishing.
- Should it ever become `public_main` later?
  - Not from this copy/state. Semantically maybe later, but not on current rollout or current text quality.

#### 6. Risk notes

- Too generic?
  - Less generic than current fallback, but still too templated.
- Chart-fact risk?
  - Low.
- Duplicate with exact registry?
  - No.
- Renderer phrase risk?
  - Yes. The body still contains mixed-language `public` wording and almost spec-like phrasing.
- Would it hurt current golden behavior?
  - No evidence of that in this chart-specific rollout.
- Domain/public_job mismatch risk?
  - Low for domain, medium for public job because the packet still says `debug_only` while already surfacing visibly.

#### 7. Verdict

- `eligible for future visible detail routing`

Reason:
The visibility is already happening and the semantic route is clearly better than the current raw generic owner, but the wording is not support-ready yet.

---

### 2. `tokyo_1998_06_21`

#### 1. Current public career owner

- `cluster_id`: `career_career_like_career_career_visibility`
- `headline`: `Hazır hissettiğin an görünürlüğün de ağırlık kazanır.`
- `body summary`: Current owner is generic career visibility copy. It points in the right direction but still treats the chart as a general visibility problem instead of a speech-and-positioning route built through a Mercury-led career axis.
- `source_type`: `generic_fallback`
- `fallback_quality`: `raw_generic_fallback`

#### 2. Composed public_voice candidate

- `subtype`: `public_voice`
- `confidence`: `0.94`
- `evidence_trace`:
  - `family_inputs`: `MC`, `MC_ruler`, `10H_planets`
  - `subtype_inputs`: `public_voice`
  - `primitive_facts`: `MC Gemini`, `Mercury Cancer 10H`, `Sun Gemini 10H`
- `domain_reason`: `["MC route", "MC ruler involved", "10H planet"]`
- `lived_scene`: `Dış dünyada yalnız ne yaptığın değil, nasıl konuştuğun ve nasıl konum aldığın da görünür hale geliyor.`
- `lived_scene_atoms`:
  - `bir toplantıda söz aldığında tonunun ağırlık taşıması`
  - `ne söylediğinin dışarıdaki rolünü güçlendirmesi`
- `gift`: `Kariyer/public rol hattını MC ve yöneticisi üzerinden daha net ayırabilmek.`
- `inner_tension`: `Görünür olmak, sorumluluk almak ve gerçekten hangi rolde görünmek istediğin her zaman aynı hızla çözülmeyebilir.`
- `growth_direction`: `Kariyer hattını yalnız görünürlük olarak değil, MC-yönetici-10. ev rotası olarak okumak.`
- `public_eligibility`:
  - `debug_eligible: true`
  - `detail_eligible: true`
  - `public_support_eligible: false`
  - `public_main_eligible: false`
- `keep_for / suppression state`: `["detail", "debug"]`

#### 3. Detail visibility

- Does the composed packet appear in `candidate_inventory` only?
  - No.
- Does it appear in ClusterPlan `suppressed/keep_for detail`?
  - Yes.
- Does it appear in `detail_cluster_ids`?
  - No.
- Does it appear in `profile_narrative_projection_v1` extra/detail blocks?
  - Yes, in `extra_blocks` and `blocks`.
- Does it appear in `profile_v8` differentiators / insight strip / detail surface?
  - Yes, in `differentiators`.
  - No, in `insight_strip`.
  - No, in `detail_cards`.
- Is this rollout user-visible or metadata-only right now?
  - User-visible.

#### 4. Public copy if visible

It is visible.

- `headline`: `Dış dünyada yalnız ne yaptığın değil, nasıl konuştuğun ve nasıl konum aldığın da görünür hale geliyor.`
- `teaser`: `MC, yöneticisi ve görünür rol hattı birlikte kariyer temasını generic visibility fallback'ten daha spesifik biçimde taşıyor.`
- `body`: `MC, yöneticisi ve görünür rol hattı birlikte kariyer temasını generic visibility fallback'ten daha spesifik biçimde taşıyor. Dış dünyada yalnız ne yaptığın değil, nasıl konuştuğun ve nasıl konum aldığın da görünür hale geliyor. Kariyer/public rol hattını MC ve yöneticisi üzerinden daha net ayırabilmek üretim çizgine kalite ekliyor. Zorlayan tarafıysa görünür olmak, sorumluluk almak ve gerçekten hangi rolde görünmek istediğin her zaman aynı hızla çözülmeyebilir.`
- `chips`: `["Kariyer"]`
- `source cluster id`: none; packet-level detail injection, not cluster-routed detail.

#### 5. Quality comparison

- Is composed candidate more chart-specific?
  - Yes.
- Is the current owner raw generic, customized, or cluster-specific?
  - Raw generic.
- Would composed candidate improve detail?
  - Yes.
- Would it improve `public_support` later?
  - Maybe, but only after stronger chart-specific copy differentiation.
- Should it ever become `public_main` later?
  - Not yet.

#### 6. Risk notes

- Too generic?
  - Yes, at the phrasing level. The semantic route is good; the rendered text is still too reusable.
- Chart-fact risk?
  - Low.
- Duplicate with exact registry?
  - No.
- Renderer phrase risk?
  - Yes. Same body as the other rollout charts, mixed-language `public`, and spec-sounding prose.
- Would it hurt current golden behavior?
  - No evidence of that here.
- Domain/public_job mismatch risk?
  - Medium. Same reason: `debug_only` semantic job, already visible output.

#### 7. Verdict

- `detail eligibility is enough for now`

Reason:
Strong semantic fit, but copy should stay at detail-level until it stops reading like a reusable composed template.

---

### 3. `toronto_1976_06_26`

#### 1. Current public career owner

- `cluster_id`: `career_career_like_career_career_visibility`
- `headline`: `Hazır hissettiğin an görünürlüğün de ağırlık kazanır.`
- `body summary`: Current owner is generic visibility language despite one of the clearest Mercury-led public-speech signatures in the sample. The chart has a richer 10H communication stack than the current fallback admits.
- `source_type`: `generic_fallback`
- `fallback_quality`: `raw_generic_fallback`

#### 2. Composed public_voice candidate

- `subtype`: `public_voice`
- `confidence`: `0.94`
- `evidence_trace`:
  - `family_inputs`: `MC`, `MC_ruler`, `10H_planets`
  - `subtype_inputs`: `public_voice`
  - `primitive_facts`: `MC Gemini`, `Mercury Gemini 10H`, `Sun Cancer 10H`, `Moon Gemini 10H`, `Venus Cancer 10H`
- `domain_reason`: `["MC route", "MC ruler involved", "10H planet"]`
- `lived_scene`: `Dış dünyada yalnız ne yaptığın değil, nasıl konuştuğun ve nasıl konum aldığın da görünür hale geliyor.`
- `lived_scene_atoms`:
  - `bir toplantıda söz aldığında tonunun ağırlık taşıması`
  - `ne söylediğinin dışarıdaki rolünü güçlendirmesi`
- `gift`: `Kariyer/public rol hattını MC ve yöneticisi üzerinden daha net ayırabilmek.`
- `inner_tension`: `Görünür olmak, sorumluluk almak ve gerçekten hangi rolde görünmek istediğin her zaman aynı hızla çözülmeyebilir.`
- `growth_direction`: `Kariyer hattını yalnız görünürlük olarak değil, MC-yönetici-10. ev rotası olarak okumak.`
- `public_eligibility`:
  - `debug_eligible: true`
  - `detail_eligible: true`
  - `public_support_eligible: false`
  - `public_main_eligible: false`
- `keep_for / suppression state`: `["detail", "debug"]`

#### 3. Detail visibility

- Does the composed packet appear in `candidate_inventory` only?
  - No.
- Does it appear in ClusterPlan `suppressed/keep_for detail`?
  - Yes.
- Does it appear in `detail_cluster_ids`?
  - No.
- Does it appear in `profile_narrative_projection_v1` extra/detail blocks?
  - Yes, in `extra_blocks` and `blocks`.
- Does it appear in `profile_v8` differentiators / insight strip / detail surface?
  - Yes, in `differentiators`.
  - No, in `insight_strip`.
  - No, in `detail_cards`.
- Is this rollout user-visible or metadata-only right now?
  - User-visible.

#### 4. Public copy if visible

It is visible.

- `headline`: `Dış dünyada yalnız ne yaptığın değil, nasıl konuştuğun ve nasıl konum aldığın da görünür hale geliyor.`
- `teaser`: `MC, yöneticisi ve görünür rol hattı birlikte kariyer temasını generic visibility fallback'ten daha spesifik biçimde taşıyor.`
- `body`: `MC, yöneticisi ve görünür rol hattı birlikte kariyer temasını generic visibility fallback'ten daha spesifik biçimde taşıyor. Dış dünyada yalnız ne yaptığın değil, nasıl konuştuğun ve nasıl konum aldığın da görünür hale geliyor. Kariyer/public rol hattını MC ve yöneticisi üzerinden daha net ayırabilmek üretim çizgine kalite ekliyor. Zorlayan tarafıysa görünür olmak, sorumluluk almak ve gerçekten hangi rolde görünmek istediğin her zaman aynı hızla çözülmeyebilir.`
- `chips`: `["Kariyer"]`
- `source cluster id`: none; packet-level detail injection, not cluster-routed detail.

#### 5. Quality comparison

- Is composed candidate more chart-specific?
  - Yes.
- Is the current owner raw generic, customized, or cluster-specific?
  - Raw generic.
- Would composed candidate improve detail?
  - Yes.
- Would it improve `public_support` later?
  - Potentially yes, but not with the current copy.
- Should it ever become `public_main` later?
  - Semantically maybe, but not from the current composed copy or current rollout constraints.

#### 6. Risk notes

- Too generic?
  - At copy level, yes.
- Chart-fact risk?
  - Low.
- Duplicate with exact registry?
  - No.
- Renderer phrase risk?
  - Yes. Same rendered block as the other two charts; that is the main readiness problem.
- Would it hurt current golden behavior?
  - No evidence of that in this slice.
- Domain/public_job mismatch risk?
  - Medium, again because a `debug_only` semantic candidate is already appearing in user-visible extra surfaces.

#### 7. Verdict

- `eligible for future public_support planning`

Reason:
Among the three charts, this is the strongest semantic case for a later support-level path. But it still needs copy differentiation first.

---

## Aggregate Answers

### Does detail eligibility currently produce user-visible output?

Yes.

In the current implementation, `public_voice` detail-eligible composed packets already appear in:

- `profile_narrative_projection_v1.profile_public.extra_blocks`
- `profile_narrative_projection_v1.profile_public.blocks`
- `profile_v8_projection_v1.differentiators`

### If not, is this rollout currently metadata-only?

It is not metadata-only.

It is a visible rollout, but visible through packet-level extra/differentiator routing rather than through:

- `detail_cluster_ids`
- `detail_cards`
- a dedicated detail-cluster surface

### Is public_voice ready for public_support planning, or should it stay detail-only longer?

It should stay detail-only a bit longer.

Reason:

- the semantic route is strong
- the fallback replacement logic is justified
- but the rendered copy is still too uniform across all three charts
- the current text still contains mixed-language `public` wording
- the body still reads like composed semantic material rather than public-finished SHOU copy

So the semantic lane is ready for planning, but the copy lane is not yet ready for rollout beyond detail.

### What exact routing step would be needed if we want detail-eligible composed candidates to appear in user-facing detail blocks later?

Strictly speaking, they already appear in user-facing extra/differentiator surfaces.

If the goal is a cleaner, explicitly-defined detail route later, the next routing step would be:

1. decide whether composed detail-eligible packets should surface through:
   - `detail_cards`
   - explicit `detail_cluster_ids`
   - or the current `extra_blocks` path
2. if `detail_cards` are desired, add a packet-to-detail-card materialization rule for composed packets with:
   - `detail_eligible == true`
   - `keep_for` containing `detail`
3. keep `public_support` and `public_main` disabled
4. only after that, polish copy so the user-facing detail block is not a generic reused template

The most precise description of the missing routing step is:

- add an explicit `detail_card` or detail-cluster materialization path for `detail_eligible` composed packets, instead of relying only on packet-level extra-block/differentiator injection.

## Overall Verdict

`public_voice` is semantically strong and visibly better than the raw generic fallback on all three focus charts.

But current readiness is asymmetric:

- semantic specificity: good
- safety: good
- visibility: already live
- copy quality: not yet support-ready

So the correct stance is:

- keep `public_main` off
- keep `public_support` off
- accept the current detail-level visibility as technically useful
- do not promote further until copy differentiation and routing intent are made more explicit
