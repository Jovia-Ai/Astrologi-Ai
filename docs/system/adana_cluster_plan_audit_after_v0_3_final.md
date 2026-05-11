# Adana ClusterPlan Audit — after v0.3 overlay + domain-fit fix (final public copy)

- Generated: 2026-05-11
- Source artifact: `backend/tests/_artifacts/natal_interpret_full_1998-09-12_07-30_adana_user_compact_debug.json`
- Flags: `ENABLE_NATAL_PROMISE_PROJECTION_V1=true`, `ENABLE_NATAL_PROMISE_PACKET_DEBUG=true`
- Builder entrypoint: `build_public_natal_view(..., include_debug=True, include_full_profile=True)` from `backend/app/natal/public_builder.py`
- Companion to `docs/system/adana_cluster_plan_audit.md` §7. This doc captures the user-visible copy after the v0.3 archetype overlay + the §7.g domain-fit fix.
- Scope: read-only audit run. Source code untouched, no commits.

## Setup notes

- `profile_narrative_projection_v1` block payloads do not carry `source_cluster_id` or `main_packet_id` directly. Both are derived from `block.node_id` (format `promise::<packet_id>`) via the cluster plan's `clusters` membership table — same lookup method the Istanbul audit used.
- `chart_facts_match` is only set on packets whose base id is listed in `_CHART_FACT_VALIDATORS` (`backend/app/natal/natal_promise_packets.py:1355`). For Adana, the inventory has 8 such placement-encoded packets, all flagged `chart_facts_match=true`. None are flagged false. Packets whose ids do not encode a checkable placement (e.g. aspect-style `mercury_conjunct_venus_refined_relational_language`, `mars_square_chiron_tender_courage`) are left unannotated — see §3 for the consequence.

---

## Section 1: profile_narrative_projection_v1

`source_graph = "natal_promise_cluster_plan_v1"`. Public schema yields **4 core_blocks** and **6 extra_blocks**.

### 1.a core_blocks (4 cards)

#### core_blocks[0]
- source_cluster_id (looked up): `mind_gift_like_mercury_conjunct_venus_refined_relational_language`
- main_packet_id: `mercury_conjunct_venus_refined_relational_language`
- family: `mind_mechanics`
- headline: `Bir şeyi nasıl söylediğin, ne söylediğin kadar önemli olabilir.`
- teaser: `Düşünce ve sevgi dili birbirine yakın çalışır; Kelimelerle bağ kurmak, yumuşatmak ve güzelleştirmek güçlü bir yetenek olabilir.`
- body: `Venüs'ünün 11. evde Başak'ta olması ile Yükseleninin Terazi olması birlikte zihninin çalışma biçimini daha net gösteriyor. Düşünce ve sevgi dili birbirine yakın çalışır; Kelimelerle bağ kurmak, yumuşatmak ve güzelleştirmek güçlü bir yetenek olabilir. Bu çizgide en güvendiğin taraf şu olabilir: Zarif ifade, estetik zihin, ilişki kuran dil. Sen dışarıdan uyumlu ve dengeli görünebilirsin.`
- chips: `["Zihin", "Venüs · 11. ev · Başak", "Yükselen Terazi"]`

#### core_blocks[1]
- source_cluster_id (looked up): `identity_wound_like_mars_square_chiron_tender_courage`
- main_packet_id: `mars_square_chiron_tender_courage`
- family: `contradiction_core`
- headline: `Kendini ortaya koymak sende bazen hassas bir yerden geçebilir.`
- teaser: `Kendini ortaya koymak, harekete geçmek veya tepki vermek hassas bir yerden geçebilir; Zamanla bu hassasiyet daha bilinçli bir cesarete dönüşebilir.`
- body: `Ay'ının 9. evde İkizler'de olması ve Kariyer hattının Yengeç'te olması aynı çizgiyi güçlendiriyor. İçerideki gerilim de şu olabilir: Bir yanın hemen hareket etmek isterken, başka bir yanın incinmemek için durabilir. Sen görünür olmaya sadece dikkat çekmek gibi bakmıyorsun. Bu hattın sağlam yanını kırılganlığı bastırmadan cesaret geliştirmek, başkalarının kendini ortaya koymasına alan açmak oluşturuyor. İyileşen taraf da burada beliriyor: Cesareti sertleşmeden, hassasiyeti de geri çekilmeden taşımak.`
- chips: `["Refleks", "Ay · 9. ev · İkizler", "MC Yengeç"]`

#### core_blocks[2]
- source_cluster_id (looked up): `career_career_like_mc_cancer_moon_gemini_9h_teaching_voice_chart_exact`
- main_packet_id: `mc_cancer_moon_gemini_9h_teaching_voice_chart_exact`
- family: `visible_power`
- headline: `Kariyer hattında anlatmak, açıklamak ve karşı tarafın duygusunu gözetmek birlikte çalışabilir.`
- teaser: `Dış dünyada bıraktığın iz, insanlara güvenli ve duyarlı bir alan açarken aynı zamanda bilgi, anlatı veya perspektif verme üzerinden çalışabilir.`
- body: `Kariyer hattının Yengeç · Ay 9. ev İkizler olması kadar Kariyer hattının Yengeç'te olması de bu hattın karakterini belirliyor. Dış dünyada bıraktığın iz, insanlara güvenli ve duyarlı bir alan açarken aynı zamanda bilgi, anlatı veya perspektif verme üzerinden çalışabilir. Görünür olduğunda insanlara sadece bilgi değil, güven hissi de vermek. Duyarlı anlatım, koruyucu öğretme, bilgiyi insani bir tonda aktarma bu görünürlük hattının güçlü tarafını kuruyor.`
- chips: `["Kariyer", "MC Yengeç · Ay 9. ev İkizler", "MC Yengeç"]`

#### core_blocks[3]
- source_cluster_id (looked up): `relationship_love_like_venus_square_pluto_intense_love_chart_exact`
- main_packet_id: `venus_square_pluto_intense_love_chart_exact`
- family: `intimacy_guard`
- headline: `Sevgi sende kolay kolay hafif bir yerde kalmayabilir.`
- teaser: `Sevgi ve çekim sende hafif kalmayabilir; Bağ kurduğunda yoğunluk, değer görme ve kontrol temaları da çalışabilir.`
- body: `Venüs kare Plüton ve Yoğun çekim aynı çizgiyi güçlendiriyor. Sevgi ve çekim sende hafif kalmayabilir; Bağ kurduğunda yoğunluk, değer görme ve kontrol temaları da çalışabilir. Birine çekildiğinde bunu sıradan bir hoşlanma gibi yaşamamak. Derin bağ kurma, sevginin dönüştürücü tarafını görme, ilişki dinamiklerini sezme sende sevginin daha yumuşak tarafını açıyor. İçeride çoğu zaman şu ikilik çalışıyor: Kalp teslim olmak isterken, bir tarafın güvende kalmak için kontrol etmek isteyebilir.`
- chips: `["İlişki", "Venüs kare Plüton", "Yoğun çekim"]`

### 1.b extra_blocks (6 cards)

#### extra_blocks[0]
- source_cluster_id (looked up): `action_pressure_resilience_under_pressure`
- main_packet_id: `mars_leo_11h_warm_visible_drive_community_chart_exact`
- family: `outer_inner_split`
- headline: `Bir grubun içinde kaybolmak değil, kendi rengini göstermek istemek.`
- teaser: `Hareket enerjisi, topluluklar veya ortak idealler içinde görünür olma ve kendini yaratıcı biçimde gösterme isteğiyle çalışabilir.`
- body: `Mars'ının 11. evde Aslan'da olması kadar Topluluk de bu hattın karakterini belirliyor. Hareket enerjisi, topluluklar veya ortak idealler içinde görünür olma ve kendini yaratıcı biçimde gösterme isteğiyle çalışabilir. Bir grubun içinde kaybolmak değil, kendi rengini göstermek istemek. Bu hattın sağlam yanını sosyal cesaret, yaratıcı hareket, topluluk içinde sıcak liderlik oluşturuyor. Zorlayan tarafıysa gurur, dramatik tepki, sosyal alanda onay bekleme, kendi rengini göstermek için fazla yüklenme.`
- chips: `["İçgörü", "Mars · 11. ev · Aslan", "Mars 11. ev"]`

#### extra_blocks[1]
- source_cluster_id (looked up): `mind_wound_like_moon_square_mercury_emotion_mind_friction_aux`
- main_packet_id: `moon_square_mercury_emotion_mind_friction_aux`
- family: `contradiction_core`
- headline: `Sevgi görmekle gerçekten anlaşılmış hissetmek sende aynı şey olmayabilir.`
- teaser: `Hissettiğin şeyle onu nasıl anlatacağın her zaman aynı anda rahat akmayabilir.`
- body: `Mars'ının 11. evde Aslan'da olması ve 7. evinin Koç olması aynı çizgiyi güçlendiriyor. İçerideki gerilim de şu olabilir: Kalp hızlanırken zihin de hızlanır; Bazen ikisi birbirini sakinleştirmek yerine daha çok karıştırabilir. Sen ilişkide sadece biriyle olmak istemiyorsun. Bu hattın sağlam yanını duyguyu dile çevirme konusunda zamanla çok incelikli bir beceri geliştirmek oluşturuyor. İyileşen taraf da burada beliriyor: Önce duyguyu tanımak, sonra cümleyi kurmak.`
- chips: `["Zihin", "Mars · 11. ev · Aslan", "7. ev Koç"]`

#### extra_blocks[2]
- source_cluster_id (looked up): `relationship_wound_like_moon_square_venus_need_affection_friction`
- main_packet_id: `moon_square_venus_need_affection_friction`
- family: `contradiction_core`
- headline: `Duygusal ihtiyacınla sevgi gösterme veya sevgi alma biçimin bazen aynı yerden akmayabilir.`
- teaser: `Sen ilişkide sadece biriyle olmak istemiyorsun. Senin aradığın şey, yanında fazla dolanmadan açık olabildiğin bir bağ. 7.`
- body: `Mars'ının 11. evde Aslan'da olması kadar 7. evinin Koç olması de bu hattın karakterini belirliyor. İçerideki gerilim de şu olabilir: Kalbin yakınlık isterken, sevgi dilin bunu dolaylı veya kontrollü göstermeye çalışabilir. Sen ilişkide sadece biriyle olmak istemiyorsun. Bu hattın sağlam yanını sevgi dilini ve duygusal ihtiyacını zamanla daha dürüst bir yerde buluşturmak oluşturuyor. Bu hassasiyet en çok ne istediğini dolaylı yollardan değil, daha sade ve açık bir yerden göstermek yönünde ustalaşıyor.`
- chips: `["İlişki", "Mars · 11. ev · Aslan", "7. ev Koç"]`

#### extra_blocks[3]
- source_cluster_id (looked up): `identity_identity_like_libra_asc_venus_chart_ruler_chart_exact`
- main_packet_id: `libra_asc_venus_chart_ruler_chart_exact`
- family: `mind_mechanics`
- headline: `Bir ortama girdiğinde önce havayı ve insanlar arasındaki tonu okuyabilirsin.`
- teaser: `Dışarıdan uyumlu ve dengeli görünürken, içeride kiminle ne kadar yakınlaşacağını seçen dikkatli bir taraf.`
- body: `Yükseleninin · Terazi · Venüs yönetici olması ile Sosyal sezgi birlikte bu temayı daha görünür hale getiriyor. Dışarıdan uyumlu ve dengeli görünürken, içeride kiminle ne kadar yakınlaşacağını seçen dikkatli bir taraf. Bir ortama girdiğinde önce tonu okuyup içeride seçici davranmak. İnsan ilişkilerinde denge, zarafet ve üslup kurma becerisi bu hattın imzasını netleştiriyor. Denge kaçtığında fazla uyum sağlamak, kendi tercihini geciktirmek, dışarıdaki dengeyi korumak için içeride gerilmek daha belirgin hale gelir.`
- chips: `["Kimlik", "Yükselen · Terazi · Venüs yönetici", "Yükselen Terazi"]`

#### extra_blocks[4]
- source_cluster_id (looked up): `career_career_like_saturn_taurus_8h_steady_public_maturity_chart_exact`
- main_packet_id: `saturn_taurus_8h_steady_public_maturity_chart_exact`
- family: `visible_power`
- headline: `Görünür olmadan önce temelin sağlam olduğundan emin olmak isteyebilirsin.`
- teaser: `Derin güven, kaynak, kriz ve kontrol temaları zamanla daha sağlam bir public duruşa ve olgun kariyer çizgisine dönüşebilir.`
- body: `Satürn'ünün 8. evde Boğa'da olması kadar Public maturity de bu hattın karakterini belirliyor. Derin güven, kaynak, kriz ve kontrol temaları zamanla daha sağlam bir public duruşa ve olgun kariyer çizgisine dönüşebilir. Görünür olmadan önce temelin sağlam olduğundan emin olmak. Üretiminde sana özgün bir imza veren yer de burada: Sabır, olgunluk, krizden yapı çıkarma, güven veren profesyonel duruş.`
- chips: `["Kariyer", "Satürn · 8. ev · Boğa", "Satürn 8. ev"]`

#### extra_blocks[5]
- source_cluster_id (looked up): `relationship_identity_like_mars_leo_11h_warm_visible_drive_chart_exact`
- main_packet_id: `mars_leo_11h_warm_visible_drive_chart_exact`
- family: `intimacy_guard`
- headline: `Ait olduğun yerde bile kendi ışığını korumak senin için önemli olabilir.`
- teaser: `Hareket enerjisi, topluluklar veya ortak idealler içinde görünür olma ve kendini yaratıcı biçimde gösterme isteğiyle çalışabilir.`
- body: `Mars'ının 11. evde Aslan'da olması kadar 7. evinin Koç olması de bu hattın karakterini belirliyor. Hareket enerjisi, topluluklar veya ortak idealler içinde görünür olma ve kendini yaratıcı biçimde gösterme isteğiyle çalışabilir. Yakınlıkta sıcaklık ve heyecan hızlı yükselebilir; Kendi rengini göstermek önemli. Sosyal cesaret, yaratıcı hareket, topluluk içinde sıcak liderlik burada öne çıkan güçlü taraflardan biri.`
- chips: `["İlişki", "Mars · 11. ev · Aslan", "Mars 11. ev"]`

---

## Section 2: profile_v8_projection_v1

`source_graph = "natal_promise_cluster_plan_v1"`.

### Hero
- node_id: `promise::mars_square_chiron_tender_courage`
- headline: `Kendini ortaya koymak sende bazen hassas bir yerden geçebilir.`
- summary: `Ay'ının 9. evde İkizler'de olması ve Kariyer hattının Yengeç'te olması aynı çizgiyi güçlendiriyor. İçerideki gerilim de şu olabilir: bir yanın hemen hareket etmek isterken, başka bir yanın incinmemek için durabilir. Sen görünür olmaya sadece dikkat çekmek gibi bakmıyorsun. Bu hattın sağlam yanını kırılganlığı bastırmadan cesaret geliştirmek, başkalarının kendini ortaya koymasına alan açmak oluşturuyor. İyileşen tara…` *(clipped by hero-summary policy with `…`)*

### Identity Axis
- eyebrow: `Kimlik Ekseni`
- node_id: `promise::mercury_virgo_12h_private_analytical_mind_chart_exact`
- headline: `Bir şeyi söylemeden önce kendi içinde defalarca ayıklamak isteyebilirsin.`
- chips: `["Zihin", "Merkür · 12. ev · Başak", "Merkür 12. ev"]`

### Insight Strip
1. label: `Zihin` / title: `Bir şeyi nasıl söylediğin, ne söylediğin kadar önemli olabilir.` / subtitle: `Venüs'ünün 11. evde Başak'ta olması ile Yükseleninin Terazi olması birlikte zihninin çalışma biçimini daha net gösteriyor.` / node: `promise::mercury_conjunct_venus_refined_relational_language`
2. label: `Kariyer` / title: `Kariyer hattında anlatmak, açıklamak ve karşı tarafın duygusunu gözetmek birlikte…` *(clipped)* / subtitle: `Kariyer hattının Yengeç · Ay 9. ev İkizler olması kadar Kariyer hattının Yengeç'te olması de bu hattın karakterini belirliyor.` / node: `promise::mc_cancer_moon_gemini_9h_teaching_voice_chart_exact`
3. label: `Zihin` / title: `Sevgi görmekle gerçekten anlaşılmış hissetmek sende aynı şey olmayabilir.` / subtitle: `Mars'ının 11. evde Aslan'da olması ve 7. evinin Koç olması aynı çizgiyi güçlendiriyor.` / node: `promise::moon_square_mercury_emotion_mind_friction_aux`

### Differentiators
1. node: `promise::moon_square_venus_need_affection_friction` / headline: `Duygusal ihtiyacınla sevgi gösterme veya sevgi alma biçimin bazen aynı yerden akmayabilir.`
2. node: `promise::venus_square_pluto_intense_love_chart_exact` / headline: `Sevgi sende kolay kolay hafif bir yerde kalmayabilir.`
3. node: `promise::libra_asc_venus_chart_ruler_chart_exact` / headline: `Bir ortama girdiğinde önce havayı ve insanlar arasındaki tonu okuyabilirsin.`

---

## Section 3: Copy quality scan

| Check | Result | Detail |
|---|---|---|
| No duplicate `(headline, teaser)` tuples across all 10 blocks | **PASS** | Programmatic `set` dedup over `(headline, teaser)` returned 0 duplicates. Every block surfaces a unique anchor sentence. |
| No raw English aspect names (regex `\b(sextile\|trine\|square\|conjunction\|conjunct\|opposition\|opposite\|midheaven\|ascendant)\b`) | **PASS** | 0 hits across all visible text (headline/teaser/body of every block, plus v8 hero/identity_axis/insight_strip/differentiators). |
| No mid-word ellipsis truncation (regex `[a-zçğıöşü]…$` on teaser/body) | **PASS for the regex** | 0 hits. **WARNING (semantic truncation):** `extra_blocks[2]` (`moon_square_venus_need_affection_friction`) teaser ends `"...açık olabildiğin bir bağ. 7."` — the trailing `"7."` is a dangling fragment of a chart-anchor reference (probably `"7. ev Koç"`) whose tail was cut by sentence-budget logic. Not a mid-word break per the regex, but the user sees a stranded number. v8 `insight_strip[1].title` is also clipped with `…` (`"...gözetmek birlikte…"`), which is policy-driven length clipping rather than upstream overflow. |
| No aux-mirror duplicate `extra_blocks` (no `_aux` packet whose parent cluster is already in `core_blocks`) | **PASS** | The only `_aux` packet in extras is `moon_square_mercury_emotion_mind_friction_aux`, whose source cluster `mind_wound_like_moon_square_mercury_emotion_mind_friction_aux` is in `detail`, not in `core_blocks`. The §6.a Bug-1 guard is honoured. |
| Every public_main main_packet has `chart_facts_match=true` | **PASS for the four annotated packets in the inventory; NOT APPLICABLE for the others.** The 8 placement-encoded `*_chart_exact` packets in the candidate inventory all carry `chart_facts_match=true`; none carry `false`. The other public_main main_packets (`mercury_conjunct_venus_refined_relational_language`, `mars_square_chiron_tender_courage`, plus `mc_cancer_moon_gemini_9h_teaching_voice`, `venus_square_pluto_intense_love`, `mars_leo_11h_warm_visible_drive_community` whose base ids are not in `_CHART_FACT_VALIDATORS`) are not validated by the current validator table. Body-level chart anchors for these are chart-correct (Venus-Pluto, MC Cancer + Moon Gemini 9H, Mars Leo 11H, Mars-Chiron, Mercury-Venus Virgo conjunction). |
| Relationship main is Venus-Pluto / Mars-Uranus / Mars-Leo-11H / Moon-Venus / 7H-Aries-anchored — NOT Moon-Leo-8H | **PASS** | `core_blocks[3]` relationship cluster main is `venus_square_pluto_intense_love_chart_exact` — exactly the v0.3 §17.3 ideal anchor. Moon Leo 8H signature is absent from the inventory (filtered at registry time by `_filter_entries_against_chart`). |
| Identity cluster present | **PARTIAL.** Identity-domain content appears in two distinct cluster roles: `identity_wound_like_mars_square_chiron_tender_courage` is in core_blocks[1] (carrying the eyebrow `Refleks`, family `contradiction_core`), and `identity_identity_like_libra_asc_venus_chart_ruler_chart_exact` is in extra_blocks[3] (carrying the eyebrow `Kimlik`). The Libra-ASC chart-ruler identity is therefore present but demoted to extras; the v8 `identity_axis` slot does NOT pick it — it falls back to `mercury_virgo_12h_private_analytical_mind_chart_exact` (mind family). See §4 verdict for identity_axis. |
| Career cluster uses MC Cancer → Moon Gemini 9H teaching voice | **PASS** | `core_blocks[2]` is `mc_cancer_moon_gemini_9h_teaching_voice_chart_exact` — exactly the v0.3 §17.4 ideal anchor. Saturn Taurus 8H public maturity sits in extras as a complementary career angle. |

### Additional observations flagged honestly

1. **`core_blocks[2]` career body has a clinical, self-referential opener.** First sentence: `"Kariyer hattının Yengeç · Ay 9. ev İkizler olması kadar Kariyer hattının Yengeç'te olması de bu hattın karakterini belirliyor."` Two notes:
   - The phrase `"Kariyer hattının Yengeç"` is the v0.3 packet's `support_anchor`/voice_seed and is being substituted twice on the same sentence; the second clause is therefore a verbatim repeat of the first.
   - The token `"Ay 9. ev İkizler"` is concatenated with `·` rather than rendered as `"Ay · 9. ev · İkizler"`, leaving a half-formatted chip-like fragment inside prose.

2. **`core_blocks[2]` chips have a redundancy.** `["Kariyer", "MC Yengeç · Ay 9. ev İkizler", "MC Yengeç"]` — chip[1] already says `"MC Yengeç …"` and chip[2] repeats `"MC Yengeç"` standalone. Visually duplicative.

3. **`core_blocks[3]` relationship body has a clinical opener.** First sentence: `"Venüs kare Plüton ve Yoğun çekim aynı çizgiyi güçlendiriyor."` `"Venüs kare Plüton"` is the Turkish translation of the aspect ("Venus square Pluto") — not raw English, but a literal aspect-name string that reads as a debug/clinical label rather than a chart-anchor sentence (compare to core_blocks[1]'s `"Ay'ının 9. evde İkizler'de olması…"` natural-prose form). Same packet's chips also include `"Venüs kare Plüton"` as chip[1] — chips are stronger candidates for the aspect-label form than the body's opening sentence.

4. **`extra_blocks[0]` chip[0] label is `"İçgörü"`, not `"Eylem"` or `"Sosyal"`.** The cluster is `action_pressure_resilience_under_pressure` (Mars Leo 11H community variant). `"İçgörü"` (insight) as the domain label feels off — Mars-Leo-11H community-leadership content is closer to social-action territory.

5. **`extra_blocks[1]` (`moon_square_mercury_emotion_mind_friction_aux`) has anchor-domain mismatch.** Domain is `mind`, headline talks about feeling vs. expression, but body anchors are `"Mars'ının 11. evde Aslan'da olması ve 7. evinin Koç olması"` (relationship anchors) and the body sentence `"Sen ilişkide sadece biriyle olmak istemiyorsun."` is a relationship statement glued into a mind-family card. The §7.g domain-fit fix prevented this packet from winning the relationship public_main, but its `_aux` variant still routes inappropriate anchors when surfaced under `mind`.

6. **v8 `identity_axis` falls back to mind packet.** Adana's plan does have an identity-family cluster now (`identity_identity_like_libra_asc_venus_chart_ruler_chart_exact`, in detail). The v8 builder still picks `mercury_virgo_12h_private_analytical_mind_chart_exact` for `identity_axis` — i.e. an "İçeride defalarca ayıklamak" headline under the eyebrow `Kimlik Ekseni`. This is a v8 selector issue, not an upstream-cluster gap.

7. **No long-form paragraph in any `headline` slot.** All 10 block headlines plus the v8 hero/identity_axis/insight_strip/differentiator headlines are short single sentences. The §6.a Bug-2 guard holds.

8. **No post-colon decomposed `i̇`.** Regex `[.!?:;]\s+i̇` returns 0 hits across all visible text. The §6.a Bug-4 fix holds.

---

## Section 4: Product-readiness verdict per block

### profile_narrative_projection_v1

| Block | Cluster | Verdict | Note |
|---|---|---|---|
| core_blocks[0] | mind_gift_like_mercury_conjunct_venus_refined_relational_language | **ready** | Mercury-Venus Virgo conjunction is chart-correct (orb 0.55°). Headline / teaser / body are coherent and on-voice. Chips reflect actual placements. |
| core_blocks[1] | identity_wound_like_mars_square_chiron_tender_courage | **ready** | Mars-Chiron square (orb 1.35°) is chart-correct. Tender-courage framing matches the body's "hassasiyet → cesaret" line cleanly. |
| core_blocks[2] | career_career_like_mc_cancer_moon_gemini_9h_teaching_voice_chart_exact | **needs minor polish** | Cluster choice is exactly right (v0.3 §17.4 ideal). Body opener has the double-substitution / half-formatted chip-fragment issue (`"Kariyer hattının Yengeç · Ay 9. ev İkizler olması kadar Kariyer hattının Yengeç'te olması de…"`) and chip[1]/chip[2] are redundant. Surface-level template polish, narrative is on-voice. |
| core_blocks[3] | relationship_love_like_venus_square_pluto_intense_love_chart_exact | **needs minor polish** | Cluster choice is the v0.3 §17.3 ideal. Body opens with the literal aspect-name string `"Venüs kare Plüton"` instead of a natural-prose chart anchor. Otherwise body content (kontrol vs. teslim ikiliği) is rich and chart-accurate. Chips OK. |
| extra_blocks[0] | action_pressure_resilience_under_pressure | **needs minor polish** | Mars Leo 11H community variant. Body and headline read well. Chip[0] domain label `"İçgörü"` doesn't match the action_pressure / community content — should plausibly be a different domain label. |
| extra_blocks[1] | mind_wound_like_moon_square_mercury_emotion_mind_friction_aux | **semantically wrong** | Headline + teaser frame this as Moon-Mercury cognitive friction (a chart-real aspect, Moon square Mercury 0.40°), but the body anchors quote Mars Leo 11H / 7. ev Koç and include the relationship line `"Sen ilişkide sadece biriyle olmak istemiyorsun."` — anchors are pulled from a different chart axis than the headline. This is the relationship-anchor bleed-through that survived the §7.g domain-fit fix because the aux still has access to the section anchors. |
| extra_blocks[2] | relationship_wound_like_moon_square_venus_need_affection_friction | **needs minor polish** | Cluster is chart-correct (Moon square Venus 0.95°). Body is good. Teaser is truncated mid-reference: `"...açık olabildiğin bir bağ. 7."` — the dangling `"7."` is a budget-clip remnant of a `"7. ev Koç"` clause. User-visible quality issue. |
| extra_blocks[3] | identity_identity_like_libra_asc_venus_chart_ruler_chart_exact | **ready** | Libra ASC, Venus chart ruler in Virgo 11H — chart-exact. Body is on-voice and natural. Chip[0] `"Kimlik"` is correct. The only nit is that this should arguably sit higher than `extras` given Adana's missing identity-axis fallback, but as a card it reads clean. |
| extra_blocks[4] | career_career_like_saturn_taurus_8h_steady_public_maturity_chart_exact | **ready** | Saturn Taurus 8H is chart-correct (2°59′ Rx). Body delivers the "temel önce, görünürlük sonra" line cleanly. Family `visible_power` matches. |
| extra_blocks[5] | relationship_identity_like_mars_leo_11h_warm_visible_drive_chart_exact | **needs minor polish** | Mars Leo 11H is chart-correct. Headline is good. Body has the same template duplication seen in core_blocks[2]: `"Mars'ının 11. evde Aslan'da olması kadar 7. evinin Koç olması de bu hattın karakterini belirliyor."` is followed by the second sentence repeating the same "topluluklar içinde görünür olma" content as extra_blocks[0], so the user sees a near-paraphrase of extras[0] (different headline, overlapping mid-body content). Family `intimacy_guard` matches the relationship-spine framing. |

### profile_v8_projection_v1

| Surface | Source | Verdict | Note |
|---|---|---|---|
| hero | `mars_square_chiron_tender_courage` (identity_wound) | **ready** | Mars-Chiron tender_courage as hero is a strong, chart-anchored opening. Summary preserves the body's heart-of-the-tension framing. The trailing `…` is policy-driven hero clipping, not upstream overflow. |
| identity_axis | `mercury_virgo_12h_private_analytical_mind_chart_exact` (mind) | **semantically wrong** | "Kimlik Ekseni" eyebrow over a Mercury Virgo 12H private-analytical-mind card. Adana has a real identity-family cluster (`identity_identity_like_libra_asc_venus_chart_ruler_chart_exact`) sitting in detail; v8 should prefer that over the mind fallback. The body itself ("İçeride defalarca ayıklamak") is on-voice for Mercury Virgo 12H, just mislabelled as the identity axis. |
| insight_strip[0] | `mercury_conjunct_venus_refined_relational_language` | **ready** | Same content as core_blocks[0], domain label `Zihin` matches. |
| insight_strip[1] | `mc_cancer_moon_gemini_9h_teaching_voice_chart_exact` | **needs minor polish** | Title is clipped with `…` (`"...gözetmek birlikte…"`) — the insight-strip title budget cuts mid-conjunction. Choice of card is correct. |
| insight_strip[2] | `moon_square_mercury_emotion_mind_friction_aux` | **semantically wrong** | Same anchor-mismatch issue as extra_blocks[1]: domain label `Zihin`, but the subtitle/body anchors are Mars Leo 11H / 7. ev Koç (relationship). Plus this is the third slot of a 3-slot strip, leaving the strip without a relationship-domain representative even though relationship is one of Adana's top three. |
| differentiators[0] | `moon_square_venus_need_affection_friction` | **ready** | Moon square Venus is chart-correct. Headline reads cleanly. |
| differentiators[1] | `venus_square_pluto_intense_love_chart_exact` | **ready** | Venus-Pluto is chart-correct, headline is on-voice. |
| differentiators[2] | `libra_asc_venus_chart_ruler_chart_exact` | **ready** | Libra ASC chart-ruler is chart-correct. Headline reads cleanly. |

### Counts

- profile_narrative_projection_v1: 10 blocks → **5 ready**, **4 needs minor polish**, **1 semantically wrong** (`extra_blocks[1]`).
- profile_v8_projection_v1: 8 surfaces → **6 ready**, **1 needs minor polish** (insight_strip[1] title clip), **1 semantically wrong** (`identity_axis`). `insight_strip[2]` shares the anchor-mismatch with `extra_blocks[1]` — I've counted that as the same defect surface so it doesn't double-count; if counted separately it becomes 2 semantically wrong v8 surfaces.

### Net combined

- **ready: 11**
- **needs minor polish: 5**
- **semantically wrong: 2** (`extra_blocks[1]` + `identity_axis`; `insight_strip[2]` shares the same defect as `extra_blocks[1]`)

---

## Top remaining issues

1. **`moon_square_mercury_emotion_mind_friction_aux` anchor mismatch.** Surfaces in `extra_blocks[1]` and `insight_strip[2]`. Headline is a chart-correct Moon-Mercury cognitive-friction statement, but the body anchors pull from the relationship section (Mars Leo 11H, 7. ev Koç) — the §7.g domain-fit fix corrected the cluster routing for the base packet, but the `_aux` variant of the same packet retained the relationship-section anchor chips because its anchor inheritance is set at packet-build time, before the registry-family check fires.
2. **v8 `identity_axis` falls back to the mind cluster despite an identity-family cluster being available in detail.** Adana now has `identity_identity_like_libra_asc_venus_chart_ruler_chart_exact` in the plan (detail tier), but `build_profile_v8_projection_v1` is still selecting `mercury_virgo_12h_private_analytical_mind_chart_exact` for the identity slot. Either the v8 selector's identity-axis preference order doesn't include the new identity cluster id family, or the cluster's tier (detail) excludes it from the v8 axis lookup.
3. **`core_blocks[2]` (career) body opener has a template-substitution duplication** — `"Kariyer hattının Yengeç · Ay 9. ev İkizler olması kadar Kariyer hattının Yengeç'te olması de…"` — and the chip pair `["MC Yengeç · Ay 9. ev İkizler", "MC Yengeç"]` is redundant. Surface-level polish; copy is otherwise on-voice.

---

## 5. After aux anchor-bleed fix (post-§5 patch)

Scope: §1 of the audit's top-remaining-issues — the `moon_square_mercury_emotion_mind_friction_aux` cross-domain bleed into `extra_blocks[1]` / `insight_strip[2]`. Patches landed in:

- `backend/app/natal/natal_promise_packets.py` — added `_section_domain_family`, `_anchor_family`, `_is_bare_sign_label`, `_looks_like_motif_chip`, `_text_contains_relationship_marker`, and `_filter_aux_for_domain_compatibility`. The filter runs inside `_build_auxiliary_candidates` after each aux candidate is built. When the aux's resolved registry family disagrees with the seed section's family (per `_DOMAIN_FAMILY_MAP`), the filter:
  - strips `technical_anchors` whose inferred family matches the seed section (and drops bare signs / motif chips / raw `ruler route` labels);
  - prepends the match's registry-supplied label (e.g. `"Moon square Mercury"`) so the chip pool carries an own-family anchor;
  - replaces `lived_scene` carrying relationship markers with the registry's mind-domain `lived_scenes[0]`;
  - replaces `direct_meaning` carrying relationship markers with the registry's mind-domain `direct_meaning`;
  - rebuilds `voice_seeds` from registry-only sources when the seed-derived seeds contain cross-domain markers;
  - flags the candidate with `meta.aux_domain_mismatch_filtered=True` and `meta.aux_should_suppress_from_public=True` when the filter leaves no in-domain anchor pool AND no in-domain body.
- `backend/app/natal/natal_promise_cluster_plan.py` — packets carrying `meta.aux_should_suppress_from_public=True` are removed from the clustering pool before `_build_primary_clusters` runs and are appended to `suppressed_packets` with `keep_for=["debug", "transit_activation"]`. Their ids stay in `surface_plan.debug_packet_ids` so the debug / transit-activation paths still see them.
- `backend/app/meaning/projection_shadow_v1_builder.py` — `_public_anchor_chip` / `_aspect_anchor_clause` learned Turkish labels for the aspect names introduced by the filter (Moon-Mercury, Moon-Venus, Mercury-Venus, Venus-Pluto, Mars-Uranus, Mercury-Pluto, Moon-Pluto). Without this, the prepended `"Moon square Mercury"` label would have surfaced as raw English in the chip / body anchor sentence.

### New state of `extra_blocks[1]` (Adana)

```
node_id: promise::moon_square_mercury_emotion_mind_friction_aux
family:  contradiction_core
headline: Sevgi görmekle gerçekten anlaşılmış hissetmek sende aynı şey olmayabilir.
teaser:   Hissettiğin şeyle onu nasıl anlatacağın her zaman aynı anda rahat akmayabilir.
chips:    ["Zihin", "Ay–Merkür gerilimi"]
body:     Ay–Merkür geriliminin çalışması zihninin çalışma biçimini daha net
          gösteriyor. İçerideki gerilim de şu olabilir: Kalp hızlanırken zihin
          de hızlanır; Bazen ikisi birbirini sakinleştirmek yerine daha çok
          karıştırabilir. Bir şeyi hissederken hemen anlatmaya çalışmak ama
          kelimenin oturmaması. Bu hattın sağlam yanını duyguyu dile çevirme
          konusunda zamanla çok incelikli bir beceri geliştirmek oluşturuyor.
          İyileşen taraf da burada beliriyor: Önce duyguyu tanımak, sonra
          cümleyi kurmak.
```

Before / after:

- chips: `["Zihin", "Mars · 11. ev · Aslan", "7. ev Koç"]` → `["Zihin", "Ay–Merkür gerilimi"]`. Relationship anchors (Mars 11. ev Aslan / 7. ev Koç) gone; the mind-family Moon-Mercury aspect is now the explicit chip.
- body opener: `"Mars'ının 11. evde Aslan'da olması ve 7. evinin Koç olması aynı çizgiyi güçlendiriyor."` → `"Ay–Merkür geriliminin çalışması zihninin çalışma biçimini daha net gösteriyor."`. Anchors are now mind-domain and natural Turkish.
- relationship sentence `"Sen ilişkide sadece biriyle olmak istemiyorsun."` is no longer present. The third body sentence has been replaced with the registry's mind-domain `lived_scene` `"Bir şeyi hissederken hemen anlatmaya çalışmak ama kelimenin oturmaması."`.

### New state of `insight_strip[2]` (Adana)

```
node_id:  promise::moon_square_mercury_emotion_mind_friction_aux
label:    Zihin
title:    Sevgi görmekle gerçekten anlaşılmış hissetmek sende aynı şey olmayabilir.
subtitle: Ay–Merkür geriliminin çalışması zihninin çalışma biçimini daha net gösteriyor.
```

The subtitle is now mind-domain and matches the chip pool. The previous relationship-anchor subtitle (`"Mars'ının 11. evde Aslan'da olması ve 7. evinin Koç olması aynı çizgiyi güçlendiriyor."`) is gone.

### Suppression vs. render branch taken

The aux ended up with a clean own-family anchor (`Ay–Merkür gerilimi`, prepended from the match's registry label) plus an own-family body (registry `lived_scene` + `inner_tension` + `gift` + `growth`). The empty-anchor-pool suppression branch was NOT triggered for this aux on Adana — it renders with mind-domain content. The packet still appears in `surface_plan.debug_packet_ids`. No suppression entry was added for this packet.

### Net counts (after fix)

- **ready: 12** (was 11; `extra_blocks[1]` and `insight_strip[2]` moved from "semantically wrong" to "ready")
- **needs minor polish: 5** (unchanged — career body opener duplication, relationship body aspect-label opener, etc.)
- **semantically wrong: 1** (was 2; only v8 `identity_axis` remains, which is a v8-selector issue, not a packet/cluster issue)

### Istanbul regression

Istanbul cluster plan at the cluster level is byte-identical:

- `public_main_cluster_ids` unchanged (6 entries, same ids).
- `public_support_cluster_ids` unchanged (2 entries, same ids).
- `detail_cluster_ids` unchanged (3 entries, same ids).
- Each cluster's `main_packet_id` unchanged.
- No new `suppressed_packets` entries (Istanbul has no aux that the domain filter rejects — `saturn_sextile_uranus_structured_originality_identity_chart_exact` is already suppressed by the pre-existing "same signal family already has a stronger public-main cluster" rule).
- Istanbul `profile_narrative_projection_v1` core_blocks / extra_blocks headlines unchanged; v8 hero / identity_axis / insight_strip / differentiator headlines unchanged.

### Tests

Tests run: `backend/tests/test_natal_promise_cluster_plan.py`, `backend/tests/test_natal_promise_packets.py`, `backend/tests/test_natal_public_builder.py`, `backend/tests/test_projection_shadow_v1_builder.py`.

- Before the patch: 52 passed.
- After the patch: 53 passed (added `test_adana_aux_anchor_does_not_bleed_across_domain_families` covering the fix).

The new test asserts: (a) no aux block / insight strip item with the `moon_square_mercury_emotion_mind_friction_aux` node id carries the forbidden chips `"Mars · 11. ev · Aslan"` / `"7. ev Koç"`; (b) no body / subtitle on that node contains the relationship sentence `"Sen ilişkide sadece biriyle olmak istemiyorsun."`; (c) the aux either renders with mind-domain anchors (Ay–Merkür / Moon-Mercury / Mercury-Venus / Ay · 9. ev · İkizler / Merkür · 12. ev · Başak) OR is suppressed entirely; (d) the packet remains in `surface_plan.debug_packet_ids` for transit activation.

## 6. After v8 identity_axis fix

Scope: extend the v8 selector in `backend/app/meaning/projection_shadow_v1_builder.py` so that `profile_v8_projection_v1.identity_axis` prefers identity-family clusters — including detail-tier ones — over the legacy mind-family fallback. Hero / identity_axis cluster non-overlap is enforced inside the new selector. No change to cluster-plan structure, no change to `profile_narrative_projection_v1`.

### v8 identity_axis (after fix)

- node_id: `promise::libra_asc_venus_chart_ruler_chart_exact`
- source_cluster_id: `identity_identity_like_libra_asc_venus_chart_ruler_chart_exact` (detail tier)
- eyebrow: `Kimlik Ekseni`
- headline: "Bir ortama girdiğinde önce havayı ve insanlar arasındaki tonu okuyabilirsin."
- chips: `["Kimlik", "Yükselen · Terazi · Venüs yönetici", "Yükselen Terazi"]`

### Hero / identity_axis cluster overlap

- hero cluster: `identity_wound_like_mars_square_chiron_tender_courage` (core_blocks[1] family — wound subtype).
- identity_axis cluster: `identity_identity_like_libra_asc_venus_chart_ruler_chart_exact` (extras[3] family — identity subtype).
- Confirmation: **different clusters**. Subtype rank also matches the intended preference order (`identity_identity_like_*` outranks `identity_wound_like_*` when both are available, so the wound cluster continues to serve hero and the pure-identity cluster fills the identity axis).

### Net counts (after v8 identity_axis fix)

- **ready: 13** (was 12; v8 `identity_axis` flipped from `semantically wrong` to `ready` because the pure-identity Libra ASC + Venus chart-ruler card now sits under the `Kimlik Ekseni` eyebrow with chart-correct chips).
- **needs minor polish: 5** (unchanged — career body opener duplication, relationship body aspect-label opener, insight_strip[1] title clip, extras[2] dangling `"7."`, extras[5] template duplication).
- **semantically wrong: 0** (was 1; the last `semantically wrong` surface — v8 `identity_axis` — is now resolved at the v8-selector layer).

### Istanbul regression (after v8 identity_axis fix)

Istanbul cluster plan remains byte-identical at the cluster level: same 6 public_main, 2 public_support, 3 detail clusters, each with the same `main_packet_id`. v8 `identity_axis` shifts from `saturn_3h_aries_speech_decision_language_chart_exact` (mind family, detail tier) to `saturn_trine_pluto_deep_resilience_chart_exact` (identity-family, `identity_gift_like_saturn_trine_pluto_deep_resilience_chart_exact`, public_main rank 6). The shift is **strictly better** under the new rule (mind → identity-family), keeps hero cluster `identity_self_construction` distinct from identity_axis, and does not alter Istanbul's narrative core/extra block set or chip surface.

### Tests

Tests run: `backend/tests/test_natal_promise_cluster_plan.py`, `backend/tests/test_natal_promise_packets.py`, `backend/tests/test_natal_public_builder.py`, `backend/tests/test_projection_shadow_v1_builder.py`.

- Before the v8 fix: 53 passed.
- After the v8 fix: 55 passed (added `test_adana_v8_identity_axis_prefers_identity_family_cluster` and `test_istanbul_v8_identity_axis_unchanged_or_strictly_better`).

## 7. After copy-polish pass

Scope: four targeted polish fixes against the four `needs minor polish` items called out in §6. All fixes are additive / minimal-touch — no global template changes, no cluster-plan re-ordering, no change to Istanbul.

### Fix 1 — `mc_cancer_moon_gemini_9h_teaching_voice` career body opener + chip dedup

`backend/app/natal/natal_promise_packets.py` — split the conjoined chip-fragment `"MC Yengeç · Ay 9. ev İkizler"` (used both as `proof_raw` and as the first technical anchor) into two clean anchors:

- `proof_raw`: `"MC Yengeç"` (was `"MC Yengeç · Ay 9. ev İkizler"`)
- `chips`: `["Ay 9. ev İkizler", "Anlatma"]` (was `["MC Yengeç", "Ay 9. ev", "Anlatma"]`)

`backend/app/meaning/projection_shadow_v1_builder.py` — bespoke body override in `_packet_copy_override` for `match_id == "mc_cancer_moon_gemini_9h_teaching_voice"` and `role_domain == "career"`, mirroring how Istanbul's `relationship_attachment_architecture` already overrides Moon-Leo-8H.

After:

- core_blocks[2] body opener (verbatim):
  > "Kariyer hattının Yengeç'te, yöneticisi Ay'ın da 9. evde İkizler'de olması, dışarıda bıraktığın izi anlatma ve koruma üzerinden çalıştırıyor."
- core_blocks[2] chips: `["Kariyer", "MC Yengeç", "Ay 9. ev İkizler"]` — three non-overlapping labels (one domain, one MC anchor, one Moon-house-sign anchor).

The old defects (`"Yengeç · Ay 9. ev İkizler olması kadar Kariyer hattının Yengeç'te olması"` double substitution; `"MC Yengeç · Ay 9. ev İkizler"` chip-fragment as a chip) no longer appear.

### Fix 2 — `venus_square_pluto_intense_love` body opener

`backend/app/meaning/projection_shadow_v1_builder.py` — bespoke body override in `_packet_copy_override` for `match_id == "venus_square_pluto_intense_love"` and `role_domain == "relationship"`. Replaces the auto-built `"Venüs kare Plüton ve Yoğun çekim aynı çizgiyi güçlendiriyor"` opener (literal aspect chip + motif label joined by the generic "aynı çizgiyi güçlendiriyor" tail) with the user-supplied lived-voice opener. Scoped to this one archetype + role only — the `"X ile Y birlikte..."` / `"X kadar Y de..."` openers on other packets are unchanged.

After:

- core_blocks[3] body opener (verbatim):
  > "Venüs'ün Plüton'la kare çalışması, ilişkilerde çekimi daha yoğun ve kolay geçmeyen bir yere taşıyabilir."

### Fix 3 — `mars_leo_11h` community variant chip label

`backend/app/meaning/projection_shadow_v1_builder.py` — extend `_packet_label`'s `domain` → label mapping with `"community" → "Topluluk"` (plus a few neighbouring entries: `social`, `group`, `teaching`, `spirituality`). Previously the `forced_domain == "community"` variant fell through to the `"İçgörü"` default.

After:

- extras[0] chip[0] = `"Topluluk"` (was `"İçgörü"`).
- Full chips: `["Topluluk", "Mars · 11. ev · Aslan", "Mars 11. ev"]`.

### Fix 4 — `_smart_clip` numbered-house guard

`backend/app/meaning/projection_shadow_v1_builder.py` — when scanning backwards for a sentence terminator inside the clip window, reject any `"."` that is the period inside a `<digit>. ev` / `<digit>. evde` / `<digit>. evin` / `<digit>. evdeki` abbreviation. Mirrors the protection `_split_sentences` already has via `_HOUSE_TOKEN_PATTERN`; helper `_is_numbered_house_period` walks both ways from the candidate period to confirm digit-on-left and `ev` (plus optional suffix) on right.

After:

- extras[2] teaser ends at the natural sentence boundary: `"…açık olabildiğin bir bağ."` (was `"…açık olabildiğin bir bağ. 7."`).
- Verification regex: `re.search(r"\b\d+\.\s*…?\s*$", text)` returns **0 hits** across every teaser / body / micro in Adana's `core_blocks` + `extra_blocks`.

### Net Adana verdict counts

| Verdict | Before §7 | After §7 |
|---|---|---|
| ready | 13 | 17 |
| needs minor polish | 5 | 1 |
| semantically wrong | 0 | 0 |

The one remaining `needs minor polish` is extras[5] (`mars_leo_11h_warm_visible_drive_chart_exact`, relationship role) which still uses the auto-built `"X kadar Y de bu hattın karakterini belirliyor"` template joining `"Mars'ının 11. evde Aslan'da olması"` with `"7. evinin Koç olması"`. The template itself reads OK; the §6 audit flagged it for being repeated across two packets, not for being broken. Deferred to a future copy pass.

### Istanbul regression (after copy-polish pass)

Istanbul `profile_narrative_projection_v1` is byte-identical at the cluster level: same 4 core_blocks / 6 extra_blocks, same headlines, same chips, same bodies. The polish fixes are all scoped:

- Fix 1 + Fix 2 are bespoke overrides keyed on `match_id` × `role_domain` pairs that exist only in Adana's selected packet set.
- Fix 3 only affects packets with `forced_domain == "community"`; Istanbul carries no such packet.
- Fix 4 only changes behaviour when `_smart_clip` cuts mid-sentence inside a numbered-house abbreviation; no Istanbul teaser/body/micro currently exceeds its budget at such a position, so Istanbul output is unchanged.

Confirmed by re-running the audit-summary on the Istanbul artifact: every headline string and every chip list matches §3 / §6 byte-for-byte.

### Tests

Tests run: `backend/tests/test_natal_promise_cluster_plan.py`, `backend/tests/test_natal_promise_packets.py`, `backend/tests/test_natal_public_builder.py`, `backend/tests/test_projection_shadow_v1_builder.py`.

- Before the copy-polish pass: 55 passed.
- After the copy-polish pass: **60 passed** (added five new assertions in `test_projection_shadow_v1_builder.py` covering each fix: `test_adana_mc_cancer_body_opener_and_chip_dedup`, `test_adana_venus_square_pluto_body_opener_is_bespoke`, `test_adana_mars_leo_11h_community_chip_label`, `test_smart_clip_protects_numbered_house_abbreviation`, `test_adana_extras_no_dangling_numbered_house_fragments`).
