# Istanbul ClusterPlan Audit

- Generated: 2026-05-11
- Source artifact: `backend/tests/_artifacts/natal_interpret_full_1996-12-28_07-10_istanbul_user_compact_debug.json`
- Flags: `ENABLE_NATAL_PROMISE_PROJECTION_V1=true`, `ENABLE_NATAL_PROMISE_PACKET_DEBUG=true`
- Build path: raw natal response -> `build_public_natal_view(..., include_debug=True, include_full_profile=True)` -> packet builders -> cluster plan -> projection builders

## 1. candidate_inventory summary

- Total candidate packet count: `5`
- Selected packet count: `3`
- Top candidate packets (max 15; current inventory only has 5):

### 1. `capricorn_asc_sun_1h_composed_self_construction`
- domain: `mind`
- promise_type: `mind_style`
- strength: `0.5724`
- technical_anchors: ["Yükselen Oğlak", "Satürn 3. ev"]
- direct_meaning: Dışarıda toparlanmış ve kontrollü görünmek senin için önemli olabilir.

### 2. `moon_leo_8h_deep_proud_heart`
- domain: `relationship`
- promise_type: `love_style`
- strength: `0.5724`
- technical_anchors: ["7. ev Yengeç", "Ay 8. ev"]
- direct_meaning: Derin, gururlu, kolay açılmayan ama açıldığında güçlü bağlanan kalp.

### 3. `venus_sagittarius_12h_hidden_expansive_love`
- domain: `career`
- promise_type: `career_signature`
- strength: `0.5724`
- technical_anchors: ["MC Terazi", "Venüs 12. ev"]
- direct_meaning: Üretim ve görünürlük sende önce içeride olgunlaşmak isteyebilir.

### 4. `capricorn_asc_sun_1h_composed_self_construction`
- domain: `identity`
- promise_type: `behavior_reflex`
- strength: `0.5424`
- technical_anchors: ["Yükselen Oğlak", "Satürn 3. ev"]
- direct_meaning: Dışarıda toparlanmış ve kontrollü görünmek senin için önemli olabilir.

### 5. `saturn_3h_aries_speech_decision_language_behavior_reflex_overlay`
- domain: `behavior_reflex`
- promise_type: `mind_style`
- strength: `0.5424`
- technical_anchors: ["Yükselen Oğlak", "Satürn 3. ev"]
- direct_meaning: Söz, ton ve karar dili sende kimliğe yakın bir yerden çalışıyor olabilir.

## 2. focus_map

### `identity`
- score: `0.6213`
- tier: `supporting`
- packet_ids: ["capricorn_asc_sun_1h_composed_self_construction", "saturn_3h_aries_speech_decision_language_behavior_reflex_overlay"]
- evidence_summary: ["chart ruler support", "angular support", "repeated packet support"]
- scoring_breakdown:
  - `packet_strength_sum`: `0.4616`
  - `chart_ruler`: `1.0`
  - `angularity`: `1.0`
  - `luminary`: `0.0`
  - `house_chain`: `0.0`
  - `repeated_support`: `0.8`
  - `contradiction`: `0.0`
  - `archetype_confidence`: `0.18`

### `career`
- score: `0.5421`
- tier: `supporting`
- packet_ids: ["venus_sagittarius_12h_hidden_expansive_love"]
- evidence_summary: ["chart ruler support", "angular support"]
- scoring_breakdown:
  - `packet_strength_sum`: `0.2436`
  - `chart_ruler`: `1.0`
  - `angularity`: `1.0`
  - `luminary`: `0.0`
  - `house_chain`: `0.0`
  - `repeated_support`: `0.4`
  - `contradiction`: `0.0`
  - `archetype_confidence`: `0.18`

### `mind`
- score: `0.5421`
- tier: `supporting`
- packet_ids: ["capricorn_asc_sun_1h_composed_self_construction"]
- evidence_summary: ["chart ruler support", "angular support"]
- scoring_breakdown:
  - `packet_strength_sum`: `0.2436`
  - `chart_ruler`: `1.0`
  - `angularity`: `1.0`
  - `luminary`: `0.0`
  - `house_chain`: `0.0`
  - `repeated_support`: `0.4`
  - `contradiction`: `0.0`
  - `archetype_confidence`: `0.18`

### `relationship`
- score: `0.4021`
- tier: `detail_only`
- packet_ids: ["moon_leo_8h_deep_proud_heart"]
- evidence_summary: ["angular support", "luminary support"]
- scoring_breakdown:
  - `packet_strength_sum`: `0.2436`
  - `chart_ruler`: `0.0`
  - `angularity`: `1.0`
  - `luminary`: `1.0`
  - `house_chain`: `0.0`
  - `repeated_support`: `0.4`
  - `contradiction`: `0.0`
  - `archetype_confidence`: `0.18`

## 3. clusters

### `mind_mind_like`
- domain: `mind`
- domain_family: `mind`
- cluster_label: `mind_like`
- cluster_strength: `0.6946`
- public_card_priority: `0.8046`
- target_surface_role: `public_main`
- main_packet_id: `capricorn_asc_sun_1h_composed_self_construction`
- packet_members:
  - packet_id: `capricorn_asc_sun_1h_composed_self_construction`
    - cluster_role: `primary_anchor`
    - contribution_type: `main_promise`
    - explicit_anchor_allowed: `True`
    - reason: main packet of cluster
  - packet_id: `saturn_3h_aries_speech_decision_language_behavior_reflex_overlay`
    - cluster_role: `modifier`
    - contribution_type: `mind_style`
    - explicit_anchor_allowed: `True`
    - reason: distinct lived scene keeps a separate support angle
- shared_themes: ["bazen", "bile", "calisma", "capricorn_asc_sun_1h_composed_self_construction", "cizgini", "disarida"]
- distinct_lived_scene: Az cümleyle sınır koyduğunda hem zihnin hem ritmin rahatlıyor; sende hız çoğu zaman bu sadeleşmeden geliyor.
- allowed_public_cards: `1`
- allowed_detail_cards: `2`
- selection_notes: ["hero-capable cluster", "has reusable sub-angles for detail"]

### `relationship_attachment_architecture`
- domain: `relationship`
- domain_family: `relationship`
- cluster_label: `attachment_architecture`
- cluster_strength: `0.6638`
- public_card_priority: `0.7738`
- target_surface_role: `public_main`
- main_packet_id: `moon_leo_8h_deep_proud_heart`
- packet_members:
  - packet_id: `moon_leo_8h_deep_proud_heart`
    - cluster_role: `primary_anchor`
    - contribution_type: `main_promise`
    - explicit_anchor_allowed: `True`
    - reason: main packet of cluster
  - packet_id: `venus_sagittarius_12h_hidden_expansive_love`
    - cluster_role: `secondary_anchor`
    - contribution_type: `internal_visibility_maturation`
    - explicit_anchor_allowed: `True`
    - reason: distinct subtype enriches cluster without duplicating main card
- shared_themes: ["acildiginda", "acilmayan", "baglanan", "baglandiginda", "baglardan", "birakmamak"]
- distinct_lived_scene: Bir cümleyle temas kurman, duyguyu sade ama açık biçimde koyman, ilişkideki en güçlü yollarından biri.
- allowed_public_cards: `1`
- allowed_detail_cards: `2`
- selection_notes: ["has reusable sub-angles for detail"]

### `career_internal_visibility_maturation`
- domain: `career`
- domain_family: `career`
- cluster_label: `internal_visibility_maturation`
- cluster_strength: `0.7106`
- public_card_priority: `0.8206`
- target_surface_role: `public_main`
- main_packet_id: `venus_sagittarius_12h_hidden_expansive_love`
- packet_members:
  - packet_id: `venus_sagittarius_12h_hidden_expansive_love`
    - cluster_role: `primary_anchor`
    - contribution_type: `main_promise`
    - explicit_anchor_allowed: `True`
    - reason: main packet of cluster
  - packet_id: `capricorn_asc_sun_1h_composed_self_construction`
    - cluster_role: `secondary_anchor`
    - contribution_type: `mind_style`
    - explicit_anchor_allowed: `True`
    - reason: distinct lived scene keeps a separate support angle
- shared_themes: ["acabilmek", "bicimde", "buyuttugun", "ceride", "daha", "dealize"]
- distinct_lived_scene: Tek paylaşım, tek sunum ya da tek toplantıyla görünür olman, sende baskıyı azaltırken etkiyi büyütüyor.
- allowed_public_cards: `1`
- allowed_detail_cards: `2`
- selection_notes: ["has reusable sub-angles for detail"]

### `identity_self_construction`
- domain: `identity`
- domain_family: `identity`
- cluster_label: `self_construction`
- cluster_strength: `0.728`
- public_card_priority: `0.878`
- target_surface_role: `public_main`
- main_packet_id: `capricorn_asc_sun_1h_composed_self_construction`
- packet_members:
  - packet_id: `capricorn_asc_sun_1h_composed_self_construction`
    - cluster_role: `primary_anchor`
    - contribution_type: `main_promise`
    - explicit_anchor_allowed: `True`
    - reason: main packet of cluster
  - packet_id: `saturn_3h_aries_speech_decision_language_behavior_reflex_overlay`
    - cluster_role: `modifier`
    - contribution_type: `mind_style`
    - explicit_anchor_allowed: `True`
    - reason: distinct lived scene keeps a separate support angle
- shared_themes: ["olabilir"]
- distinct_lived_scene: Az cümleyle sınır koyduğunda hem zihnin hem ritmin rahatlıyor; sende hız çoğu zaman bu sadeleşmeden geliyor.
- allowed_public_cards: `1`
- allowed_detail_cards: `2`
- selection_notes: ["hero-capable cluster", "identity support should survive even if not hero", "has reusable sub-angles for detail"]

## 4. surface_plan

- public_main_cluster_ids: ["identity_self_construction", "career_internal_visibility_maturation", "mind_mind_like", "relationship_attachment_architecture"]
- public_support_cluster_ids: []
- detail_cluster_ids: []
- debug_packet_ids count: `4`

## 5. suppressed_packets

- No suppressed packets emitted in this run.

## 6. anchor_usage

### `yukselen oglak`
- public_main_explicit_uses: `2`
- explicit_use_budget: `2`
- cluster_ids: ["mind_mind_like", "career_internal_visibility_maturation", "identity_self_construction"]
- chart_defining_override: `True`

### `saturn 3 ev`
- public_main_explicit_uses: `2`
- explicit_use_budget: `2`
- cluster_ids: ["mind_mind_like", "career_internal_visibility_maturation", "identity_self_construction"]
- chart_defining_override: `False`

### `section:mind_system`
- public_main_explicit_uses: `2`
- explicit_use_budget: `2`
- cluster_ids: ["mind_mind_like", "career_internal_visibility_maturation", "identity_self_construction"]
- chart_defining_override: `False`

### `thread:identity_mechanics`
- public_main_explicit_uses: `2`
- explicit_use_budget: `2`
- cluster_ids: ["mind_mind_like", "career_internal_visibility_maturation", "identity_self_construction"]
- chart_defining_override: `False`

### `7 ev yengec`
- public_main_explicit_uses: `1`
- explicit_use_budget: `2`
- cluster_ids: ["relationship_attachment_architecture"]
- chart_defining_override: `False`

### `ay 8 ev`
- public_main_explicit_uses: `1`
- explicit_use_budget: `2`
- cluster_ids: ["relationship_attachment_architecture"]
- chart_defining_override: `False`

### `section:relationships`
- public_main_explicit_uses: `1`
- explicit_use_budget: `2`
- cluster_ids: ["relationship_attachment_architecture"]
- chart_defining_override: `False`

### `thread:relationships_depth`
- public_main_explicit_uses: `1`
- explicit_use_budget: `2`
- cluster_ids: ["relationship_attachment_architecture"]
- chart_defining_override: `False`

### `mc terazi`
- public_main_explicit_uses: `1`
- explicit_use_budget: `2`
- cluster_ids: ["relationship_attachment_architecture", "career_internal_visibility_maturation"]
- chart_defining_override: `True`

### `venus 12 ev`
- public_main_explicit_uses: `1`
- explicit_use_budget: `2`
- cluster_ids: ["relationship_attachment_architecture", "career_internal_visibility_maturation"]
- chart_defining_override: `False`

### `section:career_visibility`
- public_main_explicit_uses: `1`
- explicit_use_budget: `2`
- cluster_ids: ["relationship_attachment_architecture", "career_internal_visibility_maturation"]
- chart_defining_override: `False`

### `thread:career_visibility`
- public_main_explicit_uses: `1`
- explicit_use_budget: `2`
- cluster_ids: ["relationship_attachment_architecture", "career_internal_visibility_maturation"]
- chart_defining_override: `False`

## 7. projection outputs after cluster integration

### profile_narrative_projection_v1
- source_graph: `natal_promise_cluster_plan_v1`
- source_graph_version: `natal_promise_cluster_plan_v1`
- blocks:
  - node_id: `promise::capricorn_asc_sun_1h_composed_self_construction`
    - headline: Az cümleyle sınır koyduğunda hem zihnin hem ritmin rahatlıyor; sende hız çoğu zaman bu sadeleşmeden geliyor.
    - teaser: Dışarıda toparlanmış ve kontrollü görünmek senin için önemli olabilir.
    - origin: `meaning_graph_v1_1_projection`
    - family: `mind_mechanics`
    - chips: ["Kimlik", "Yükselen Oğlak", "Satürn 3. ev"]
    - body: Hem Yükseleninin Oğlak olması hem de Satürn 3. ev bu temayı daha görünür kılıyor. Dışarıda toparlanmış ve kontrollü görünmek senin için önemli olabilir. Az cümleyle sınır koyduğunda hem zihnin hem ritmin rahatlıyor; sende hız çoğu zaman bu sadeleşmeden geliyor. Zor zamanda bile çizgini koruyabilmek senin güçlü taraflarından biri olabilir. Omurganı sertlik olmadan da koruyabildiğini görmek zamanla bu çizginin daha da güçlenmesini sağlayabilir.
  - node_id: `promise::venus_sagittarius_12h_hidden_expansive_love`
    - headline: Bir şeyi hemen göstermekten çok, içine sindirip olgunlaştırmak senin ritmine daha yakın olabilir.
    - teaser: Üretim ve görünürlük sende önce içeride olgunlaşmak isteyebilir.
    - origin: `meaning_graph_v1_1_projection`
    - family: `visible_power`
    - chips: ["Kariyer", "MC Terazi", "Venüs 12. ev"]
    - body: Hem MC'nin Terazi'de olması hem de Venüs 12. ev görünürlük çizgine ayrı bir ton veriyor. Üretim ve görünürlük sende önce içeride olgunlaşmak isteyebilir. Tek paylaşım, tek sunum ya da tek toplantıyla görünür olman, sende baskıyı azaltırken etkiyi büyütüyor. Görünmeyen hazırlıkta güç toplayıp işi daha rafine bir biçimde sunabilmek bu çizginin güçlü tarafını oluşturabilir. İçeride büyüttüğün şeyi doğru zamanda hayata açabilmek bu görünürlük çizgisinin daha olgun çalışmasını sağlayabilir.
  - node_id: `promise::moon_leo_8h_deep_proud_heart`
    - headline: Kalbin güven olmadan tam açılmıyor olabilir.
    - teaser: Derin, gururlu, kolay açılmayan ama açıldığında güçlü bağlanan kalp.
    - origin: `meaning_graph_v1_1_projection`
    - family: `intimacy_guard`
    - chips: ["İlişki", "7. ev Yengeç", "Ay 8. ev"]
    - body: Hem 7. evinin Yengeç olması hem de Ay 8. ev bu temayı derinleştiriyor. Derin, gururlu, kolay açılmayan ama açıldığında güçlü bağlanan kalp. Bir cümleyle temas kurman, duyguyu sade ama açık biçimde koyman, ilişkideki en güçlü yollarından biri. Bağlandığında hem sıcak hem de sadık kalabilmek sende doğal bir sıcaklık gibi çalışabilir. Ama bu sıcaklığın içinde kendi ihtiyacını kaybetmemek de önemli. Derinliği krizden değil, güven veren bağlardan kurmak burada ayrı bir önem kazanıyor.
  - node_id: `promise::saturn_3h_aries_speech_decision_language_behavior_reflex_overlay`
    - headline: Az cümleyle sınır koyduğunda hem zihnin hem ritmin rahatlıyor; sende hız çoğu zaman bu sadeleşmeden geliyor.
    - teaser: Söz, ton ve karar dili sende kimliğe yakın bir yerden çalışıyor olabilir.
    - origin: `meaning_graph_v1_1_projection`
    - family: `mind_mechanics`
    - chips: ["Refleks", "Yükselen Oğlak", "Satürn 3. ev"]
    - body: Hem Yükseleninin Oğlak olması hem de Satürn 3. ev zihninin çalışma biçimini daha belirgin kılıyor. Söz, ton ve karar dili sende kimliğe yakın bir yerden çalışıyor olabilir. Az cümleyle sınır koyduğunda hem zihnin hem ritmin rahatlıyor; sende hız çoğu zaman bu sadeleşmeden geliyor. Cümleye hem ağırlık hem hız verebilmek senin güçlü taraflarından biri olabilir. Sesi bastırmadan, sertliğe mahkûm etmeden kullanmak zamanla bu çizginin daha da güçlenmesini sağlayabilir.

### profile_v8_projection_v1
- source_graph: `natal_promise_cluster_plan_v1`
- source_graph_version: `natal_promise_cluster_plan_v1`
- hero:
  - node_id: `promise::capricorn_asc_sun_1h_composed_self_construction`
  - headline: Az cümleyle sınır koyduğunda hem zihnin hem ritmin rahatlıyor; sende hız çoğu zaman bu sadeleşmeden geliyor.
  - summary: Hem Yükseleninin Oğlak olması hem de Satürn 3. ev bu temayı daha görünür kılıyor. Dışarıda toparlanmış ve kontrollü görünmek senin için önemli olabilir. Az cümleyle sınır koyduğunda hem zihnin hem ritmin rahatlıyor; sende hız çoğu zaman bu sadeleşmeden geliyor. Zor zamanda bile çizgini koruyabilmek senin güçlü taraflarından biri olabilir. Omurganı sertlik olmadan da koruyabildiğini görmek zamanla bu çizginin daha da…
- identity_axis:
  - node_id: `promise::saturn_3h_aries_speech_decision_language_behavior_reflex_overlay`
  - headline: Az cümleyle sınır koyduğunda hem zihnin hem ritmin rahatlıyor; sende hız çoğu zaman bu sadeleşmeden geliyor.
  - body: Hem Yükseleninin Oğlak olması hem de Satürn 3. ev zihninin çalışma biçimini daha belirgin kılıyor. Söz, ton ve karar dili sende kimliğe yakın bir yerden çalışıyor olabilir. Az cümleyle sınır koyduğunda hem zihnin hem ritmin rahatlıyor; sende hız çoğu zaman bu sadeleşmeden geliyor. Cümleye hem ağırlık hem hız verebilmek senin güçlü taraflarından biri olabilir. Sesi bastırmadan, sertliğe mahkûm etmeden kullanmak zamanla bu çizginin daha da güçlenmesini sağlayabilir.
- insight_strip:
  - node_id: `promise::venus_sagittarius_12h_hidden_expansive_love`
    - label: Kariyer
    - title: Bir şeyi hemen göstermekten çok, içine sindirip olgunlaştırmak senin ritmine daha y…
    - subtitle: Hem MC'nin Terazi'de olması hem de Venüs 12.
  - node_id: `promise::moon_leo_8h_deep_proud_heart`
    - label: İlişki
    - title: Kalbin güven olmadan tam açılmıyor olabilir.
    - subtitle: Hem 7.
  - node_id: `promise::capricorn_asc_sun_1h_composed_self_construction`
    - label: Kimlik
    - title: Az cümleyle sınır koyduğunda hem zihnin hem ritmin rahatlıyor; sende hız çoğu zaman…
    - subtitle: Hem Yükseleninin Oğlak olması hem de Satürn 3.
- differentiators:
  - node_id: `promise::saturn_3h_aries_speech_decision_language_behavior_reflex_overlay`
    - headline: Az cümleyle sınır koyduğunda hem zihnin hem ritmin rahatlıyor; sende hız çoğu zaman bu sadeleşmeden geliyor.
    - stat_label: zihin
    - body: Hem Yükseleninin Oğlak olması hem de Satürn 3. ev zihninin çalışma biçimini daha belirgin kılıyor. Söz, ton ve karar dili sende kimliğe yakın bir yerden çalışıyor olabilir. Az cümleyle sınır koyduğunda hem zihnin hem ritmin rahatlıyor; sende hız çoğu zaman bu sadeleşmeden geliyor. Cümleye hem ağırlık hem hız verebilme…
  - node_id: `promise::capricorn_asc_sun_1h_composed_self_construction`
    - headline: Az cümleyle sınır koyduğunda hem zihnin hem ritmin rahatlıyor; sende hız çoğu zaman bu sadeleşmeden geliyor.
    - stat_label: refleks
    - body: Hem Yükseleninin Oğlak olması hem de Satürn 3. ev bu temayı daha görünür kılıyor. Dışarıda toparlanmış ve kontrollü görünmek senin için önemli olabilir. Az cümleyle sınır koyduğunda hem zihnin hem ritmin rahatlıyor; sende hız çoğu zaman bu sadeleşmeden geliyor. Zor zamanda bile çizgini koruyabilmek senin güçlü tarafla…
  - node_id: `promise::venus_sagittarius_12h_hidden_expansive_love`
    - headline: Bir şeyi hemen göstermekten çok, içine sindirip olgunlaştırmak senin ritmine daha yakın olabilir.
    - stat_label: iz
    - body: Hem MC'nin Terazi'de olması hem de Venüs 12. ev görünürlük çizgine ayrı bir ton veriyor. Üretim ve görünürlük sende önce içeride olgunlaşmak isteyebilir. Tek paylaşım, tek sunum ya da tek toplantıyla görünür olman, sende baskıyı azaltırken etkiyi büyütüyor. Görünmeyen hazırlıkta güç toplayıp işi daha rafine bir biçimd…

## 8. explicit pass/fail notes against rubric

### Raw checks requested
- PASS: public main card count <= 7. Actual: `4`.
- MIXED: identity/self-construction is not strong in focus_map (`supporting`), but it does surface as `public_main`. This passes the surface-presence check but fails the expected focus-strength reading.
- PASS: Venus 12H appears in both career and relationship clusters with different roles. Actual roles: `[('relationship', 'secondary_anchor'), ('career', 'primary_anchor')]`.
- N/A: no suppressed packets were emitted, so retention into detail/debug/transit_activation is not exercised in this run.
- PASS: v8 hero remains mind/identity, not relationship. Actual hero: `promise::capricorn_asc_sun_1h_composed_self_construction`.
- PASS: normal public schema does not expose cluster plan as a new top-level field. In this debug run, cluster details are only visible through projection debug traceability / direct internal build output.

### Rubric verdict
- FAIL: Mind / communication / structured originality is not scored strong. Focus tier is only `supporting`, and the main mind packet is mis-keyed to `capricorn_asc_sun_1h_composed_self_construction` instead of surfacing `saturn_sextile_uranus_structured_originality` and `saturn_3h_aries_speech_decision_language` as expected.
- FAIL: Identity / self-construction does surface, but focus tier is only `supporting`. The same anchor set is reused to create both a mind public-main cluster and an identity public-main cluster, which reads like duplicate chart cards rather than distinct angles.
- FAIL: Relationship / love / emotional depth is misread as `detail_only` in focus_map. The run preserves only `attachment_architecture`; it does not surface `affection_gift` and does not preserve a clean `hidden_private_love_pattern` subtype label.
- FAIL: Career / visibility / creative channel is only `supporting`, not strong, despite MC/Venus visibility evidence. Only one career candidate packet survives the inventory step.
- FAIL: Action / pressure / resilience does not appear as a separate medium_strong/detail-support domain. No explicit Sun-Saturn / Mars-Saturn / Saturn-Pluto pressure packet survives candidate inventory.
- PASS: Money/self-worth is not forced into the public-main feed.
- FAIL: Public main does not read like 5-7 chart-defining cards. It returns 4 cards, but two of them are effectively the same Oğlak ASC / Satürn 3H anchor family split into separate mind and identity cards with very similar lived-scene language.
- FAIL: Same-domain / same-anchor duplication is not being resolved in a human-meaning-first way. `mind_mind_like` and `identity_self_construction` both use `capricorn_asc_sun_1h_composed_self_construction` as the main packet.
- MIXED: Reused anchors are budgeted correctly at the explicit-use level, but the underlying inventory is so thin that anchor reuse mostly reflects duplicated packet sourcing rather than healthy cross-cluster semantic reuse.
- FAIL: Venus 12H is allowed in both career and relationship clusters structurally, but the relationship-side usage is flattened into a secondary anchor carrying the career-oriented subtype `internal_visibility_maturation` instead of a distinct `hidden_private_love_pattern` reading.
- PASS: V8 hero stays on an identity/mind/angular line rather than drifting to relationship.
- PASS: Public schema does not expose cluster plan as a normal top-level field.

### Likely cause of the weak audit
- The cluster plan in this run is being built from the already-humanized public `sections_v2` and `supporting_threads` output. In this rebuilt public payload, `sections_v2` no longer carries `category_support` or `proof_raw`, and `supporting_threads[].evidence` is empty. That strips away the exact `Moon trine Venus`, `Saturn sextile Uranus`, chart-ruler-route, contradiction, and repeated-motif evidence the richer packet inventory needs.
- Evidence of that loss is visible directly in this run: candidate inventory only contains 5 packets, none of them are `moon_trine_venus_emotional_warmth` or `saturn_sextile_uranus_structured_originality`, and all packet `scoring_breakdown` values collapse to minimal text/anchor bonuses with `salience=0`, `confidence=0`, `primary_anchor=0`, `aspect_strength=0`, `hidden_strength=0`.
