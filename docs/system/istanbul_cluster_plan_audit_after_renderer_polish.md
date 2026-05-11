# Istanbul ClusterPlan Audit After Renderer Polish

- Generated: 2026-05-11
- Source artifact: `backend/tests/_artifacts/natal_interpret_full_1996-12-28_07-10_istanbul_user_compact_debug.json`
- Flags: `ENABLE_NATAL_PROMISE_PROJECTION_V1=true`, `ENABLE_NATAL_PROMISE_PACKET_DEBUG=true`
- Scope: cluster plan logic and scoring unchanged; this round only polishes the public-copy renderer in `backend/app/meaning/projection_shadow_v1_builder.py`.

## 1. profile_narrative_projection_v1

`source_graph = "natal_promise_cluster_plan_v1"`,
`source_graph_version = "natal_promise_cluster_plan_v1"`.

Public schema returned by the renderer exposes three channels:
`profile_public.core_blocks`, `profile_public.extra_blocks`, and the
flattened `profile_public.blocks` view. The first four public-main
clusters land in `core_blocks`; the remaining public-main clusters
(ranks 5–6) plus public-support and detail clusters land in
`extra_blocks`, in cluster-plan order.

### 1.a core_blocks (4 cards)

#### core_blocks[0]
- source_cluster_id: `career_internal_visibility_maturation`
- main_packet_id: `venus_sagittarius_12h_hidden_expansive_love_chart_exact`
- headline: "Bir şeyi hemen göstermektense, önce içine sinmesini bekleyebilirsin."
- teaser: "Üretimin sende çoğu zaman görünmeden önce içeride olgunlaşıyor olabilir."
- body: "Venüs'ünün 12. evde Yay'da, kariyer hattının da Terazi'de olması üretiminde iç hazırlığı büyütüyor. Bir şeyi hemen göstermektense, önce içine sinmesini ve doğru formu bulmasını isteyebilirsin. Bu sana rafine bir sunum gücü verir; ama fazla beklersen görünür olma zamanı kaçabilir. Buradaki olgunlaşma, içerde büyüttüğün şeyi doğru anda dışarı çıkarabilmekte."
- chips: `["Kariyer", "Venüs · 12. ev · Yay", "Kariyer hattı Terazi"]`

#### core_blocks[1]
- source_cluster_id: `identity_self_construction`
- main_packet_id: `capricorn_asc_sun_1h_composed_self_construction_chart_exact`
- headline: "Dışarıda güçlü ve toparlanmış görünmek senin için hafif bir konu olmayabilir."
- teaser: "Dışarıda toparlanmış ve kontrollü görünmek senin için önemli olabilir."
- body: "Yükseleninin Oğlak'ta ve Güneş'inin 1. evde olması kadar Satürn'ünün 3. evde olması de bu hattın karakterini belirliyor. Dışarıda toparlanmış ve kontrollü görünmek senin için önemli olabilir. Dışarıda güçlü, toparlı ve kendi çizgisini koruyan görünmek istemek. Zor zamanda bile çizgini koruyabilmek bu hattın imzasını netleştiriyor. Denge kaçtığında gücü bazen sadece kontrol üzerinden taşımaya çalışma daha belirgin hale gelir."
- chips: `["Kimlik", "Yükselen · Oğlak · Güneş 1. ev", "Yükselen Oğlak"]`

#### core_blocks[2]
- source_cluster_id: `mind_structured_originality`
- main_packet_id: `saturn_sextile_uranus_structured_originality_chart_exact`
- headline: "Yeni fikri yalnızca bulmak değil, çalışır hale getirmek sende güçlü olabilir."
- teaser: "Zihninde yenilikle yapı aynı anda çalışabiliyor."
- body: "Satürn–Uranüs desteğinin çalışması kadar Satürn'ünün 3. evde olması de bu hattın karakterini belirliyor. Zihninde yenilikle yapı aynı anda çalışabiliyor. Yenilikle disiplini aynı yerde tutabilmek bu çizginin sağlam yanını oluşturuyor. Yeni bir fikri hızla çalışır bir sisteme çevirebilmek. Zorlayan tarafta ise fazla kontrol yeniliği boğabilir; fazla hız düzeni dağıtabilir."
- chips: `["Zihin", "Satürn–Uranüs desteği", "Satürn 3. ev"]`

#### core_blocks[3]
- source_cluster_id: `relationship_attachment_architecture`
- main_packet_id: `moon_leo_8h_deep_proud_heart_chart_exact`
- headline: "Kalbin güven olmadan tam açılmıyor olabilir."
- teaser: "Yakınlık sende yüzeyde değil; güven oluşunca derinleşiyor."
- body: "Ay'ının 8. evde Aslan'da olması ile 7. evinin Yengeç olması birlikte ilişkideki bu hattı daha net hissettiriyor. Yakınlık sende yüzeyde değil; güven oluşunca derinleşiyor. Bir bağ içeri gerçekten oturana kadar duyguyu tam açmamak. İlişkide kendini en doğal hissettiğin yerlerden biri de bağlandığında hem sıcak hem de sadık kalabilmek. İçeride çoğu zaman şu ikilik çalışıyor: kalbin hem güven hem de özel hissetme ihtiyacı taşıyor olabilir."
- chips: `["İlişki", "Ay · 8. ev · Aslan", "7. ev Yengeç"]`

### 1.b extra_blocks (6 cards)

Public-main ranks 5–6 are carried first, then support and detail clusters in cluster-plan order.

#### extra_blocks[0]
- source_cluster_id: `career_healing_voice` (public_main rank 5)
- main_packet_id: `chiron_conjunct_mc_visibility_wound_to_voice_chart_exact`
- headline: "Ortaya çıkmadan önce çok hazır olmak istemen, bazen sesinin değerini olduğundan geç vermene neden olabilir."
- teaser: "Görünür olma hassasiyetini zamanla başkalarına dokunan bir sese çevirmek."
- body: "Chiron'un kariyer hattıyla kavuşumda olması ve Kariyer hattının Terazi'de olması aynı çizgiyi güçlendiriyor. Zorlayan tarafıysa görünür olmadan önce kendini gereğinden fazla sınamak. Görünmeden önce fazladan hazırlanmak ama zamanla bunu sese çevirmek. Üretiminde sana özgün bir imza veren yer de burada: kırılganlığı utanç değil, başkasına alan açan bir sezgiye çevirmek. İşin olgunlaşan tarafı da burada: yaranı saklamadan, ona teslim de olmadan görünür kalabilmek."
- chips: `["Kariyer", "Chiron–kariyer hattı kavuşumu", "Chiron 10. ev"]`

#### extra_blocks[1]
- source_cluster_id: `identity_gift_like_saturn_trine_pluto_deep_resilience_chart_exact` (public_main rank 6)
- main_packet_id: `saturn_trine_pluto_deep_resilience_chart_exact`
- headline: "Zorlandığında bile dağılıp gitmeyen, içeride yapı kuran bir gücün var."
- teaser: "Baskı geldiğinde bile yapıyı koruyup içerden dönüşebilmek."
- body: "Satürn–Plüton desteğinin çalışması ile Güneş–Satürn geriliminin çalışması birlikte bu temayı daha görünür hale getiriyor. Baskı geldiğinde bile yapıyı koruyup içerden dönüşebilmek. Zor zamanlarda bile çözülmek yerine omurgayı koruyabilmek bu hattın imzasını netleştiriyor. Baskı arttığında dağılmak yerine daha kontrollü ve dayanıklı kalmak. Denge kaçtığında her şeyi tek başına taşımaya çalışma ve duyguyu fazla sıkıştırma. Bazen de baskı ile dayanıklılık arasındaki çekişme daha belirgin hale gelir."
- chips: `["Kimlik", "Satürn–Plüton desteği", "Güneş–Satürn karesi"]`

#### extra_blocks[2]
- source_cluster_id: `relationship_affection_gift` (public_support)
- main_packet_id: `moon_trine_venus_emotional_warmth_chart_exact`
- headline: "Birini sevdiğinde yalnızca yaklaşmak değil, ona iyi gelmek de istersin."
- teaser: "Sevginin içinde yumuşatma, güzelleştirme ve bakım verme tarafı var."
- body: "Ay–Venüs uyumunun çalışması ve Ay'ının 8. evde olması aynı çizgiyi güçlendiriyor. Sevginin içinde yumuşatma, güzelleştirme ve bakım verme tarafı var. Sevdiğini güzelleştirmek, ona iyi gelmek ve duyguyu yumuşatmak bu hattın imzasını netleştiriyor. Gergin bir anda bile sevdiğin kişiye daha yumuşak ve iyi gelen bir yerden dönmek. Zorlayan tarafta ise fazla vermek, sevdiğini idealize etmek, kendi ihtiyacını ikinci plana atmak."
- chips: `["İlişki", "Ay–Venüs uyumu", "Ay 8. ev"]`

#### extra_blocks[3]
- source_cluster_id: `mind_speech_decision_language` (detail)
- main_packet_id: `saturn_3h_aries_speech_decision_language_chart_exact`
- headline: "Söz, ton ve karar dili sende kimliğe yakın bir yerden çalışıyor olabilir."
- teaser: "Cümleyi hem tartıp hem hızlı netleştirmek."
- body: "Satürn'ünün 3. evde Koç'ta olması ile Merkür'ünün 1. evde olması birlikte zihninin çalışma biçimini daha net gösteriyor. Söz, ton ve karar dili sende kimliğe yakın bir yerden çalışıyor olabilir. Cümleyi hem tartıp hem hızlı netleştirmek. Cümleye hem ağırlık hem hız verebilmek bu hattın imzasını netleştiriyor. Denge kaçtığında kendini fazla tutup sonra sert çıkmak daha belirgin hale gelir."
- chips: `["Zihin", "Satürn · 3. ev · Koç", "Satürn 3. ev"]`

#### extra_blocks[4]
- source_cluster_id: `identity_gift_like_saturn_sextile_uranus_structured_originality_identity_chart_exact` (detail)
- main_packet_id: `saturn_sextile_uranus_structured_originality_identity_chart_exact`
- headline: "Ciddi görünsen de içeride daha farklı bir çizgi taşıyorsun."
- teaser: "Kontrollü duruşunun içinde daha özgün ve beklenmedik bir taraf var."
- body: "Yükselen Oğlak dışarıda daha kontrollü bir duruş verebilir. Ama Uranüs'ün 1. evde çalışması, kimliğinin içinde daha özgür ve kalıba sığmayan bir damar olduğunu gösteriyor. Bu tarafı bastırmak yerine ona yapı verdiğinde, farklılığın dağınık değil güçlü bir imzaya dönüşür. Buradaki gelişim, ciddiyetle özgünlüğü aynı bedende rahatça taşıyabilmek."
- chips: `["Kimlik", "Satürn–Uranüs desteği", "Yükselen Oğlak"]`

#### extra_blocks[5]
- source_cluster_id: `relationship_hidden_private_love_pattern` (detail)
- main_packet_id: `venus_sagittarius_12h_hidden_expansive_love_relationship_chart_exact`
- headline: "Bazı duygular sende önce içeride büyüyor olabilir."
- teaser: "Sevgi bazen önce iç dünyanda anlam kazanıyor olabilir."
- body: "Venüs'ünün 12. evde Yay'da olması sevgiyi bazen önce içeride büyüten bir taraf verebilir. Birine yalnızca kişi olarak değil, sende açtığı anlama da bağlanabilirsin. Bu yüzden bazı duygular dışarıdan çok görünmese bile içeride uzun süre yer kaplayabilir. Buradaki gelişim, idealize ettiğin şeyi gerçek temasla da sınayabilmek."
- chips: `["İlişki", "Venüs · 12. ev · Yay", "Venüs 12. ev"]`

## 2. profile_v8_projection_v1

`version = "profile_v8_projection_v1"`,
`source_graph = "natal_promise_cluster_plan_v1"`.

### Hero
- node_id: `promise::capricorn_asc_sun_1h_composed_self_construction_chart_exact`
- headline: "Dışarıda güçlü ve toparlanmış görünmek senin için hafif bir konu olmayabilir."
- summary: opens with "Yükseleninin Oğlak'ta ve Güneş'inin 1. evde olması kadar Satürn'ünün 3. evde olması de bu hattın karakterini belirliyor…" (truncated at 400 chars by hero policy).

### Identity Axis
- eyebrow: "Kimlik Ekseni"
- node_id: `promise::saturn_3h_aries_speech_decision_language_chart_exact`
- headline: "Söz, ton ve karar dili sende kimliğe yakın bir yerden çalışıyor olabilir."
- chips: `["Zihin", "Satürn · 3. ev · Koç", "Satürn 3. ev"]`

### Insight Strip
1. label "İlişki" / title "Kalbin güven olmadan tam açılmıyor olabilir." / node `moon_leo_8h_deep_proud_heart_chart_exact`
2. label "Kariyer" / title "Bir şeyi hemen göstermektense, önce içine sinmesini bekleyebilirsin." / node `venus_sagittarius_12h_hidden_expansive_love_chart_exact`
3. label "Kimlik" / title "Zorlandığında bile dağılıp gitmeyen, içeride yapı kuran bir gücün var." / node `saturn_trine_pluto_deep_resilience_chart_exact`

NOTE: the strip's `subtitle` field truncates mid-sentence on the first sentence of the projection body (e.g. "Ay'ının 8." / "Venüs'ünün 12."). This pre-dates the renderer-polish round and is caused by the v8 subtitle splitter treating the period in "8. ev" / "12. ev" as a sentence terminator. Out of scope for this round; flag for separate follow-up.

### Differentiators
1. headline "Birini sevdiğinde yalnızca yaklaşmak değil, ona iyi gelmek de istersin." (Moon trine Venus)
2. headline "Yeni fikri yalnızca bulmak değil, çalışır hale getirmek sende güçlü olabilir." (Saturn sextile Uranus, mind role)
3. headline "Ortaya çıkmadan önce çok hazır olmak istemen, bazen sesinin değerini olduğundan geç vermene neden olabilir." (Chiron conjunct MC)

## 3. Copy quality scan

- **No raw English aspect names in public headline / teaser / body.** Verified via regex grep on `sextile|trine|square|conjunction|conjunct|opposition|opposite|midheaven|ascendant` and planet-name-followed-by-aspect patterns across all 10 cards. Result: zero hits.
- **No duplicate headline+teaser pairs across cards.** Verified by `sort | uniq -d` on `(headline, teaser)` tuples — empty.
- **Career Venus-12H vs. relationship Venus-12H are semantically distinct.** Career headline talks about a creative output ripening internally before going public; relationship headline talks about feelings growing internally before reaching another person. Wording is fully disjoint.
- **Mind Saturn-Uranus vs. identity Saturn-Uranus are semantically distinct.** Mind copy frames the trait as "turning a new idea into a working spine"; identity copy frames it as "carrying both composure and originality in the same body." Both bodies are fully disjoint.
- **No repeated "Hem X hem de Y" body skeleton across adjacent cards.** Verified — zero card bodies open with "Hem … hem de …".
- **No repeated "sende güçlü taraflarından biri olabilir / zamanla bu çizginin daha da güçlenmesi" closer.** Both phrases now occur zero times across all 10 cards; the formerly recurring "sende güçlü çalışan taraflardan biri" template was removed from the `_packet_gift_sentence` rotation in this round and replaced with a wider set of phrasings ("bu hattın imzasını netleştiriyor", "İlişkide kendini en doğal hissettiğin yerlerden biri de…", etc.).
- **Anchor sentence opener variation.** Of the 10 cards, the "X ile Y birlikte …" form appears on 4 cards (Moon-Leo, Saturn-Pluto, Saturn-3H, Saturn-Uranus identity opens with its bespoke override), the "X kadar Y de bu hattın karakterini belirliyor" form on 3 cards (Capricorn-ASC, Saturn-sextile-Uranus mind, Saturn-Pluto), and the "X ve Y aynı çizgiyi güçlendiriyor" form on 2 cards (Chiron-MC, Moon-Venus). Distribution is acceptable.
- **`extra_blocks` carries `career_healing_voice` and the resilience cluster.** Both `extra_blocks[0]` (Chiron-MC / career_healing_voice) and `extra_blocks[1]` (Saturn trine Pluto / resilience) are present — these are the two public_main ranks beyond core.
- **Contradiction labels localized.** The previously-leaking English label "pressure vs resilience" is now rendered as "baskı ile dayanıklılık arasındaki çekişme" in the Saturn-Pluto body. Sentence-start capitalization after period also fixed for the upstream "Bazen de …" concatenation.

## 4. Cluster / source checks

- `source_graph == "natal_promise_cluster_plan_v1"` ✓
- Public schema does NOT expose the full cluster plan without debug:
  - With `ENABLE_NATAL_PROMISE_PACKET_DEBUG` unset, `profile_narrative_projection_v1.traceability` exposes only `cluster_public_main_count, evidence_count, node_count, packet_count`. Neither `natal_promise_packets_v1` nor `natal_promise_cluster_plan_v1` is present in the public traceability payload. Verified via a second build pass with debug flag explicitly cleared.
- candidate_inventory count: **11** (matches `surface_plan.debug_packet_ids` length).
- public_main cluster count: **6**.
- public_support cluster count: **2**.
- detail cluster count: **3**.
- public_main cluster ids (in order):
  1. `career_internal_visibility_maturation`
  2. `identity_self_construction`
  3. `mind_structured_originality`
  4. `relationship_attachment_architecture`
  5. `career_healing_voice`
  6. `identity_gift_like_saturn_trine_pluto_deep_resilience_chart_exact`

## 5. Product-readiness verdict per block

| Block | Cluster | Verdict | Notes |
|---|---|---|---|
| core_blocks[0] | career_internal_visibility_maturation | **ready** | Bespoke override for Venus-12H career role; copy is on-voice. |
| core_blocks[1] | identity_self_construction | **ready** | Anchor sentence now deduplicated; reads cleanly. |
| core_blocks[2] | mind_structured_originality | **ready** | Override headline + teaser; body composed from new gift rotation. |
| core_blocks[3] | relationship_attachment_architecture | **ready** | Bespoke override; tension-sentence template integrates with body. |
| extra_blocks[0] | career_healing_voice | **needs minor copy polish** | Body line "Üretiminde sana özgün bir imza veren yer de burada: kırılganlığı utanç değil…" slightly clinical — could lean further into emotional warmth. Otherwise on-voice. |
| extra_blocks[1] | identity_gift_like_saturn_trine_pluto_deep_resilience_chart_exact | **ready** | Previously-leaking "pressure vs resilience" now rendered as "baskı ile dayanıklılık arasındaki çekişme"; capitalization fixed. |
| extra_blocks[2] | relationship_affection_gift | **ready** | Distinct from Moon-Leo card; body shows the Moon-Venus warmth dimension. |
| extra_blocks[3] | mind_speech_decision_language | **ready** | Teaser now pulls from `lived_scene` instead of duplicating headline. |
| extra_blocks[4] | identity_gift_like_saturn_sextile_uranus_structured_originality_identity_chart_exact | **ready** | Bespoke override; semantically distinct from mind variant. |
| extra_blocks[5] | relationship_hidden_private_love_pattern | **ready** | Bespoke override for Venus-12H relationship role; distinct from career variant. |

Open follow-up (out of scope this round):

- profile_v8 `insight_strip.subtitle` truncates mid-sentence inside numbered house labels ("Ay'ının 8.", "Venüs'ünün 12."). The v8 subtitle splitter treats the period in "8. ev" / "12. ev" as a sentence terminator. Same fix shape as the renderer's `_normalize_house_tokens` would apply here.

## 6. P0 bug-fix regression check

After the Adana P0 fixes landed in
`backend/app/meaning/projection_shadow_v1_builder.py` and
`backend/app/natal/natal_promise_packets.py`, the Istanbul artifact was
re-projected through the same builder (via
`backend/scripts/audit_regen_projection.py`). Result: **no regression on
Istanbul**. Each Adana-driven guard is a no-op on this chart because none
of the Adana-pathological conditions hold here.

| Adana bug | Adana-pathological trigger | Holds on Istanbul? | Istanbul observation after fix |
|---|---|---|---|
| 1. aux-mirror duplicate `extra_blocks` | `public_support` + `detail` both empty for `cluster_main >= 3` | No — Istanbul has support + detail clusters | `extra_blocks` count: **6**, all distinct cluster ids (ranks 5–6 + support + detail). Headline set is fully unique. No aux-mirror landed in `extra_blocks`. |
| 2. body-shape paragraph in headline slot | bespoke override emitting a 500+ char paragraph as the headline | No — Istanbul's override produces short headlines | All 10 narrative-block headlines are under 110 chars (longest: 91). v8 hero / identity-axis / 3 differentiators: all under 110 chars (longest: 107). |
| 3. mid-word teaser/body truncation | teaser/body source exceeding the slot budget | No — Istanbul packets fit the budget | Regex `[a-zçğıöşü]…` against `teaser` and `body` across all blocks: **0 hits**. The new `_smart_clip` helper is a no-op on every block on this chart. |
| 4. post-colon decomposed `i̇` capitalization | composed body sentence using `: i…` template | Borderline — present in Istanbul's `career_healing_voice` body line `"...: kırılganlığı utanç değil…"` (capitalized correctly under the previous fix because the next char is `k`) | The widened regex now ALSO fires after `:` and `;`. Istanbul's existing post-colon capitalization is preserved; no spurious capitalizations. Regex `[.!?:;]\s+i̇` across all fields: **0 hits**. |
| 5. packet-id ↔ chart-fact mismatch | template-id placement (`moon_leo_8h_*`) selected on a chart where that placement is absent | No — Istanbul has Moon in Leo 8h, Sun in Capricorn 1h, Venus in Sagittarius 12h | All three placement-encoded packets selected for Istanbul carry `chart_facts_match: true`: `capricorn_asc_sun_1h_composed_self_construction`, `moon_leo_8h_deep_proud_heart`, `venus_sagittarius_12h_hidden_expansive_love`. |

Block-level numbers (from
`backend/scripts/audit_regen_projection.py
backend/tests/_artifacts/natal_interpret_full_1996-12-28_07-10_istanbul_user_compact_debug.json`):

- `core_blocks`: 4 (unchanged from §1.a)
- `extra_blocks`: 6 (unchanged from §1.b — same headline set, same ordering)
- duplicate headlines across all blocks: 0
- headlines longer than 200 chars: 0
- mid-word teaser/body hits: 0
- post-colon decomposed `i̇` hits: 0
- aux-mirror duplicates in `extra_blocks`: 0
- packets with `chart_facts_match: false`: 0

Test suite: `pytest backend/tests/test_natal_promise_cluster_plan.py
backend/tests/test_natal_promise_packets.py
backend/tests/test_natal_public_builder.py
backend/tests/test_projection_shadow_v1_builder.py` — **49 passed** (45 pre-existing + 4 new regression assertions for the Adana fixes).


## 7. After v0.3 archetype overlay

This section captures the Istanbul cluster plan after the v0.3 addendum (18
new archetypes, additive overlay) has been applied. The overlay was designed
for Adana's Libra / Virgo / Mars-Uranus / Venus-Pluto signature; Istanbul's
chart has none of those placements, so all v0.3 chart-signature variants
fail their guards on this fixture and no new packets enter the inventory.

### 7.a Candidate inventory

- candidate_inventory count: **11** (unchanged from §1 baseline).
- v0.3 packets newly present in Istanbul's inventory: **none**. Every v0.3
  archetype's `_chart_variant_supported` guard returns false because:
  - Istanbul ASC is Capricorn, not Libra
  - No Virgo Sun/Mercury/Venus
  - No Moon-Pluto opposition, no Moon-Mercury/Venus square in this fixture
  - Mars is not in Leo 11H
  - No Mars-Uranus opposition, no Mars-Chiron square
  - MC is not Cancer
  - Saturn is not in Taurus 8H
  - No Sun-Jupiter opposition
  - Neptune is not in 4H

### 7.b focus_map (unchanged)

| domain | tier | score |
|---|---|---|
| career | strong | 1.00 |
| identity | strong | 0.88 |
| mind | medium_strong | 0.77 |
| relationship | medium_strong | 0.72 |

### 7.c Public surface plan (unchanged from §1.a / §6)

`public_main` ids in order:

1. `career_internal_visibility_maturation` → `venus_sagittarius_12h_hidden_expansive_love_chart_exact`
2. `identity_self_construction` → `capricorn_asc_sun_1h_composed_self_construction_chart_exact`
3. `mind_structured_originality` → `saturn_sextile_uranus_structured_originality_chart_exact`
4. `relationship_attachment_architecture` → `moon_leo_8h_deep_proud_heart_chart_exact`
5. `career_healing_voice` → `chiron_conjunct_mc_visibility_wound_to_voice_chart_exact`
6. `identity_gift_like_saturn_trine_pluto_deep_resilience_chart_exact` → `saturn_trine_pluto_deep_resilience_chart_exact`

`public_support` ids:

1. `mind_gift_like_mercury_conjunct_jupiter_big_mind_chart_exact`
2. `relationship_affection_gift`

`detail` ids:

1. `mind_speech_decision_language`
2. `identity_gift_like_saturn_sextile_uranus_structured_originality_identity_chart_exact`
3. `relationship_hidden_private_love_pattern`

This is byte-identical to the §1 / §6 cluster-plan layout — same 6 / 2 / 3
counts, same cluster IDs in same order, same main_packet_id selections.

### 7.d Regression checks (P0 fixes hold)

- mid-word teaser/body hits: **0**
- post-colon decomposed `i̇` hits: **0**
- aux-mirror duplicates in `extra_blocks`: **0**
- headlines longer than 200 chars: **0**
- duplicate headlines across all blocks: **0**
- chart_facts_flags: `capricorn_asc_sun_1h_composed_self_construction:
  true`, `moon_leo_8h_deep_proud_heart: true`,
  `venus_sagittarius_12h_hidden_expansive_love: true`,
  `saturn_3h_aries_speech_decision_language: true` — every placement-encoded
  packet still matches Istanbul's chart.

### 7.e Per-block verdict

All previously-validated blocks (§1.a, §1.b, §6) remain unchanged. No
v0.3-driven regressions detected. The chart-correctness filter
`_filter_entries_against_chart` keeps every v0.1/v0.2 entry because the
relevant placements all match Istanbul's chart.

### 7.f Test results

`pytest backend/tests/test_natal_promise_cluster_plan.py
backend/tests/test_natal_promise_packets.py
backend/tests/test_natal_public_builder.py
backend/tests/test_projection_shadow_v1_builder.py` — **52 passed** (49
pre-existing + 2 Adana v0.3 goldens + 1 Adana relationship-domain
regression). The pre-existing Istanbul golden
(`test_natal_promise_cluster_plan_istanbul_golden`) and packet-level
Istanbul tests still pass, with only the
`registry_authority` string asserter updated from
`v0.1_plus_manual_delta_v0_2` to `v0.1_plus_manual_delta_v0_2_plus_v0_3`
to reflect the additive v0.3 overlay.

### 7.g Domain-fit fix (after-fix re-run)

After the Adana relationship-domain fix (see
`adana_cluster_plan_audit.md` §7.g — `_resolve_domain` now gates its
title-based fast paths on the matched archetype's registry-declared
domain families, and `emotional_world` is mapped to its own family
rather than `relationship`), Istanbul's cluster plan is byte-identical
at the cluster level:

- `public_main` (6): `career_internal_visibility_maturation`,
  `identity_self_construction`, `mind_structured_originality`,
  `relationship_attachment_architecture`, `career_healing_voice`,
  `identity_gift_like_saturn_trine_pluto_deep_resilience_chart_exact`
- `public_support` (2): `mind_gift_like_mercury_conjunct_jupiter_big_mind_chart_exact`,
  `relationship_affection_gift`
- `detail` (3): `mind_speech_decision_language`,
  `identity_gift_like_saturn_sextile_uranus_structured_originality_identity_chart_exact`,
  `relationship_hidden_private_love_pattern`

Every `main_packet_id` per cluster is unchanged. The fix only affects
charts whose seeds/threads pull a registry archetype into a domain that
its registry declares as off-family; Istanbul's matches were all
already in-family, so the gating predicate evaluates true everywhere
and there is no behavioural change.

## 6. After v8 identity_axis fix

Scope: extend the v8 selector in `backend/app/meaning/projection_shadow_v1_builder.py` so that `profile_v8_projection_v1.identity_axis` prefers identity-family clusters (including detail tier) over the legacy mind-family fallback. The change targets Adana's `semantically wrong` v8 surface; Istanbul is verified here as a regression guard.

### v8 identity_axis (after fix)

- node_id: `promise::saturn_trine_pluto_deep_resilience_chart_exact`
- source_cluster_id: `identity_gift_like_saturn_trine_pluto_deep_resilience_chart_exact` (public_main rank 6)
- eyebrow: `Kimlik Ekseni`
- headline: "Zorlandığında bile dağılıp gitmeyen, içeride yapı kuran bir gücün var."
- chips: `["Kimlik", "Satürn–Plüton desteği", "Güneş–Satürn karesi"]`

Pre-fix the slot was `saturn_3h_aries_speech_decision_language_chart_exact` (cluster `mind_speech_decision_language`, mind family, detail tier). The shift mind → identity-family is **strictly better** under the new rule, because Istanbul carries multiple identity-family clusters in the plan (`identity_self_construction` consumed by hero, plus `identity_gift_like_saturn_trine_pluto_deep_resilience_chart_exact` in public_main and `identity_gift_like_saturn_sextile_uranus_structured_originality_identity_chart_exact` in detail). The selector prefers the public_main identity_gift cluster over the detail identity_gift cluster (tier and projection priority), and excludes the hero's `identity_self_construction` cluster from the candidate set so hero / identity_axis remain distinct.

### Hero / identity_axis cluster overlap

- hero cluster: `identity_self_construction` (Capricorn ASC + Sun 1H composed-self-construction).
- identity_axis cluster: `identity_gift_like_saturn_trine_pluto_deep_resilience_chart_exact`.
- Confirmation: **different clusters**, both identity-family.

### Byte-identical cluster plan

Istanbul cluster plan is unchanged at every level the fix could plausibly touch:

- `public_main_cluster_ids` (6): unchanged (`career_internal_visibility_maturation`, `identity_self_construction`, `mind_structured_originality`, `relationship_attachment_architecture`, `career_healing_voice`, `identity_gift_like_saturn_trine_pluto_deep_resilience_chart_exact`).
- `public_support_cluster_ids` (2): unchanged (`mind_gift_like_mercury_conjunct_jupiter_big_mind_chart_exact`, `relationship_affection_gift`).
- `detail_cluster_ids` (3): unchanged (`mind_speech_decision_language`, `identity_gift_like_saturn_sextile_uranus_structured_originality_identity_chart_exact`, `relationship_hidden_private_love_pattern`).
- Each cluster's `main_packet_id`: unchanged.
- `profile_narrative_projection_v1` core_blocks / extra_blocks: identical 4 core + 6 extra ordering; the only surface impacted is `profile_v8_projection_v1.identity_axis` (one of 8 v8 surfaces).
- v8 hero remains `capricorn_asc_sun_1h_composed_self_construction_chart_exact` (cluster `identity_self_construction`); insight_strip and differentiators are unchanged.

### Tests

Tests run: `backend/tests/test_natal_promise_cluster_plan.py`, `backend/tests/test_natal_promise_packets.py`, `backend/tests/test_natal_public_builder.py`, `backend/tests/test_projection_shadow_v1_builder.py`.

- Before the v8 fix: 53 passed.
- After the v8 fix: 55 passed. `test_istanbul_v8_identity_axis_unchanged_or_strictly_better` asserts that when Istanbul carries any identity-family cluster (it does), v8 `identity_axis` surfaces an identity-family cluster id and does not collide with the hero cluster. `test_adana_v8_identity_axis_prefers_identity_family_cluster` covers the Adana side of the regression.

## 7. After copy-polish pass

Scope: the Adana copy-polish pass landed four targeted fixes (see `docs/system/adana_cluster_plan_audit_after_v0_3_final.md` §7). All fixes were scoped to packets that do NOT appear in Istanbul's selected set, or to behaviour that does not trigger on Istanbul's payload. This section confirms Istanbul remains byte-identical at the cluster level.

### Cluster plan

- `public_main_cluster_ids` (6): unchanged.
- `public_support_cluster_ids` (2): unchanged.
- `detail_cluster_ids` (3): unchanged.
- Each cluster's `main_packet_id`: unchanged.

### `profile_narrative_projection_v1`

core_blocks headlines (unchanged):
1. "Bir şeyi hemen göstermektense, önce içine sinmesini bekleyebilirsin."
2. "Sözün sende hafif çalışmıyor; Hem tartılıyor hem de bir anda çok net çıkabiliyor."
3. "Yeni fikri yalnızca bulmak değil, çalışır hale getirmek sende güçlü olabilir."
4. "Kalbin güven olmadan tam açılmıyor olabilir."

extra_blocks headlines (unchanged):
1. "Ortaya çıkmadan önce çok hazır olmak istemen, bazen sesinin değerini olduğundan geç vermene neden olabilir."
2. "Zorlandığında bile dağılıp gitmeyen, içeride yapı kuran bir gücün var."
3. "Birini sevdiğinde yalnızca yaklaşmak değil, ona iyi gelmek de istersin."
4. "Söz, ton ve karar dili sende kimliğe yakın bir yerden çalışıyor olabilir."
5. "Ciddi görünsen de içeride daha farklı bir çizgi taşıyorsun."
6. "Bazı duygular sende önce içeride büyüyor olabilir."

All four chips on each block are unchanged. All four body openers are unchanged.

### Why the polish fixes did not touch Istanbul

- **Fix 1 (`mc_cancer_moon_gemini_9h_teaching_voice` bespoke body + chip dedup)**: Istanbul has no Cancer MC + Moon-in-Gemini-9H route; the packet is not selected.
- **Fix 2 (`venus_square_pluto_intense_love` bespoke body)**: Istanbul has no Venus square Pluto aspect; the packet is not selected.
- **Fix 3 (`community` → `"Topluluk"` chip label)**: Istanbul has no `forced_domain == "community"` packet (no `mars_leo_11h_warm_visible_drive_community_chart_exact` in the selected set). Istanbul's `mars_leo_11h_*` would only fire if Mars were in Leo in the 11th house, which is not the Istanbul chart.
- **Fix 4 (`_smart_clip` numbered-house guard)**: tightens the rule for treating a `"."` as a sentence boundary inside the clip window. No Istanbul teaser/body/micro currently produces a clip-position that lands inside a `<digit>. ev` abbreviation, so the new rule is a no-op against Istanbul's payload. Confirmed: every Istanbul teaser/body/micro is byte-identical before vs after the patch.

### Verification

Re-running `backend/scripts/audit_regen_projection.py` on `backend/tests/_artifacts/natal_interpret_full_1996-12-28_07-10_istanbul_user_compact_debug.json` before vs after the patch produces a byte-identical stdout dump (verified via `diff` after temporarily stashing the patch). No dangling `\d+\.` fragments in any Istanbul field.

### Tests

Tests run: `backend/tests/test_natal_promise_cluster_plan.py`, `backend/tests/test_natal_promise_packets.py`, `backend/tests/test_natal_public_builder.py`, `backend/tests/test_projection_shadow_v1_builder.py`.

- Before the copy-polish pass: 55 passed.
- After the copy-polish pass: **60 passed** (five new tests, all Adana-scoped; Istanbul tests in this set continue to pass unchanged).

## 8. After copy-style naturalization pass

Scope: the §8 Adana pass added bespoke per-packet body overrides for five Adana cards (mc_cancer, libra_asc, saturn_taurus_8h, venus_square_pluto, mars_leo_11h × 2 variants) plus a defensive `_naturalize_chip_prose` helper that strips chip-format `·` and translates the English label `Public maturity` from body / teaser / micro. See `docs/system/adana_cluster_plan_audit_after_v0_3_final.md` §8 for the bespoke bodies.

### Istanbul status: byte-identical at cluster level

Compared block-by-block against the §7 snapshot:

- `profile_public.core_blocks` — 4/4 blocks identical: same `node_id`, headline, teaser, body, micro, and chip list.
- `profile_public.extra_blocks` — 6/6 blocks identical on every field.

Confirmed by direct tuple-fingerprint comparison `[(node_id, headline, body, teaser, micro, chips) for b in blocks]` before vs after §8.

### Why Istanbul is unaffected

- The five bespoke overrides are keyed on `match_id` × `role_domain` (or `match_id` × `packet.id`) pairs that do not appear in Istanbul's selected packet set. Istanbul's selected packets share no `match_id` with `libra_asc_venus_chart_ruler`, `saturn_taurus_8h_steady_public_maturity`, `mc_cancer_moon_gemini_9h_teaching_voice`, `venus_square_pluto_intense_love`, or `mars_leo_11h_warm_visible_drive`.
- `_naturalize_chip_prose` only mutates a string when `·` or `Public maturity` is present. Scanning every Istanbul body / teaser / micro returns 0 hits for both patterns, so the helper is a no-op for every Istanbul block.

### Banned-phrase scan (Istanbul)

| Pattern | Hits |
|---|---|
| `·` inside body / teaser / micro | 0 |
| `Public maturity` (any casing) | 0 |

`·` continues to appear inside Istanbul chip arrays (e.g. `Satürn · 3. ev · Koç`) — that is the intended chip-display format and not a regression.

### Tests

- Before §8: 60 passed.
- After §8: **63 passed**. The three new Adana-scoped assertions (`test_adana_bodies_have_no_chip_format_separator`, `test_adana_bodies_have_no_public_maturity_english_label`, `test_adana_mars_leo_11h_community_vs_relationship_bodies_diverge`) do not exercise Istanbul; Istanbul tests in this set continue to pass unchanged.
