# Adana ClusterPlan Audit

- Generated: 2026-05-11
- Source artifact: `backend/tests/_artifacts/natal_interpret_full_1998-09-12_07-30_adana_user_compact_debug.json` (newly built for this audit)
- Flags: `ENABLE_NATAL_PROMISE_PROJECTION_V1=true`, `ENABLE_NATAL_PROMISE_PACKET_DEBUG=true`
- Scope: read-only execution of the existing cluster-plan + projection pipeline against a different chart. No cluster, packet, or renderer logic was changed.
- Companion to `docs/system/istanbul_cluster_plan_audit_after_renderer_polish.md` — same shape, same checks. Differences in output reflect the chart, not the pipeline.

## 0. Chart-shape snapshot

Birth data: **1998-09-12, 07:30 Adana, TR** (`Europe/Istanbul`, lat 37.0000, lon 35.3213). Birth datetime resolved as `1998-09-12T07:30:00+03:00`.

Placements (Placidus):

| Body | Sign | House | Lon |
|---|---|---|---|
| Sun | Virgo | 12 | 19°13′ |
| Moon | Gemini | 9 | 7°36′ |
| Mercury | Virgo | 12 | 7°12′ |
| Venus | Virgo | 11 | 6°39′ |
| Mars | Leo | 11 | 14°16′ |
| Jupiter | Pisces | 6 | 23°35′ Rx |
| Saturn | Taurus | 8 | 2°59′ Rx |
| Uranus | Aquarius | 5 | 9°20′ Rx |
| Neptune | Capricorn | 4 | 29°37′ Rx |
| Pluto | Sagittarius | 3 | 5°30′ |
| Chiron | Scorpio | 2 | 15°37′ |
| North Node | Virgo | 11 | 1°22′ |

Angles: **ASC Libra 3°07′**, **MC Cancer 3°29′**. Chart ruler is therefore Venus (Libra ASC), which sits in Virgo, 11h, conjunct Mercury (orb 0.55°) and Vertex (orb 0.0°), and squares Pluto (orb 1.15°).

Tight, defining aspects detected (orb ≤ 4°):
- Moon (Gemini 9h) square Mercury 0.40° / square Venus 0.95° / trine Uranus 1.74° / opposite Pluto 2.10°.
- Mercury–Venus conjunction (Virgo) 0.55°.
- Mercury / Venus square Pluto (1.7° / 1.15°).
- Mars (Leo 11h) opposition Uranus 4.92° / square Chiron 1.35°.
- Saturn (Taurus 8h) sextile MC 0.50° / trine IC 0.50° / square Neptune 3.38°.
- Neptune square Lilith 0.58° / trine ASC 3.51°.
- Sun–Jupiter opposition 4.36° / Sun sextile Chiron 3.61°.

Dominant tone reads as **mutable / earth-heavy** (Virgo stellium: Sun, Mercury, Venus, North Node) with an air ASC + air Moon. Hard-aspect spine: Moon-square-Mercury-Venus + Mars-Uranus opposition + Mercury/Venus-square-Pluto. This is a chart with strong cognitive friction, a Virgo-style craft/quality axis, and a relational signature dominated by Mars–Uranus / Venus–Pluto rather than the Moon–8h architecture the pipeline ends up labelling it with (see §5).

## 1. profile_narrative_projection_v1

`source_graph = "natal_promise_cluster_plan_v1"`, `source_graph_version = "natal_promise_cluster_plan_v1"`.

Unlike Istanbul (6 public_main → 4 core + 6 extra), Adana surfaces **3 public_main, 0 public_support, 0 detail**, so the public schema yields **3 core_blocks** (all 3 public_main clusters) and **3 extra_blocks** (the three `_aux` mirror packets re-rendered from the same clusters).

Block fields shown below: `source_cluster_id` and `main_packet_id` are not stored on the block itself in the output payload — `block.source_cluster_id` and `block.main_packet_id` are both `None` in this build for every block (same behaviour observed when re-running the Istanbul artifact through the same builder). What is stored is `block.node_id` (form `promise::<packet_id>`) and `block.trace.node_id`. The cluster id below is therefore looked up from the cluster plan via packet membership.

### 1.a core_blocks (3 cards)

#### core_blocks[0]
- source_cluster_id (looked up): `career_career_like_career_career_visibility`
- main_packet_id (from node_id): `career_career_visibility`
- family: `visible_power`
- headline: "İnsanlar önce kalite çıtasını, sonra etkini görür."
- teaser: "Sen görünür olmaya sadece dikkat çekmek gibi bakmıyorsun. MC'nin Yengeç olduğu için dış dünyada daha koruyucu ve duyarlı bir etki bırakıyorsun. İnsanlar sende yalnızca sonucu deği…" *(truncated mid-word — see §3)*
- body: "Ay'ının 9. evde İkizler'de olması ve Kariyer hattının Yengeç'te olması aynı çizgiyi güçlendiriyor. İnsanlar önce kalite çıtasını, sonra etkini görür. Sen görünür olmaya sadece dikkat çekmek gibi bakmıyorsun. Üretiminde sana özgün bir imza veren yer de burada: i̇nsanlar önce kalite çıtasını, sonra etkini görür. Bunu dengelediğinde görünürlük hattı senin burada öğrenmeye geldiğin şey şu olabilir: görünür olmak için her şeyi tamamen bitirmiş olman gerekmiyor. Kalite duygun çok değerli ama bazen seni gereğinden uzun h…" *(truncated)*
- chips: `["Kariyer", "Ay · 9. ev · İkizler", "MC Yengeç"]`

#### core_blocks[1]
- source_cluster_id (looked up): `relationship_attachment_architecture`
- main_packet_id (from node_id): `moon_leo_8h_deep_proud_heart`
- family: `intimacy_guard`
- headline: "Kalbin güven olmadan tam açılmıyor olabilir."
- teaser: "Yakınlık sende yüzeyde değil; güven oluşunca derinleşiyor."
- body: "Mars'ının 11. evde Aslan'da olması ile 7. evinin Koç olması birlikte ilişkideki bu hattı daha net hissettiriyor. Yakınlık sende yüzeyde değil; güven oluşunca derinleşiyor. Sen ilişkide sadece biriyle olmak istemiyorsun. Bu hat sana yakınlıkta sıcak ve sağlam bir omurga veriyor: bağlandığında hem sıcak hem de sadık kalabilmek. Duygusal tarafta seni zorlayan şey de bu olabilir: kalbin hem güven hem de özel hissetme ihtiyacı taşıyor olabilir."
- chips: `["İlişki", "Mars · 11. ev · Aslan", "7. ev Koç"]`

#### core_blocks[2]
- source_cluster_id (looked up): `mind_mind_like_mind_mind_system`
- main_packet_id (from node_id): `mind_mind_system`
- family: `mind_mechanics`
- headline: *(loaded as a 500+ char body-shape paragraph — see §3 for the bug)* "Sen dışarıdan uyumlu ve dengeli görünebilirsin. Yükselenin Terazi olduğu için bir ortama girdiğinde önce havayı, tonu ve insanlar arasındaki dengeyi yokluyorsun. Ama iş zihnine ve kendini ifade etme biçimine geldiğinde içeride çok daha ölçülü, seçici ve eleştirel bir şey çalışıyor. Çünkü senin yöneticin Venüs Başak'ta ve 11. evde. Yani dışarıdan daha sakin görünsen de içeride hep çalışan, tetikte kalan ya da pozisyon alan bir tarafın var. Bu yüzden dışarıdaki sakinlik, içerideki başlatan ve cesur enerjiyi her zaman göstermiyor olabilir."
- teaser: "Ne yapacağını bildiğin an tempo kendiliğinden yükselir."
- body: "Venüs'ünün 11. evde Başak'ta olması kadar Yükseleninin Terazi olması de bu hattın karakterini belirliyor. Ne yapacağını bildiğin an tempo kendiliğinden yükselir. Sen dışarıdan uyumlu ve dengeli görünebilirsin. Bu çizgide en güvendiğin taraf şu olabilir: ne yapacağını bildiğin an tempo kendiliğinden yükselir. Zorlayan tarafta ise yükselen terazi dışarıda daha uyumlu ve dengeli bir izlenim bırakıyor; ama zihnin özellikle bağlam netleşince hızlanıyor."
- chips: `["Zihin", "Venüs · 11. ev · Başak", "Yükselen Terazi"]`

### 1.b extra_blocks (3 cards)

Public-main also fills extra_blocks here because the cluster plan produced no public_support or detail clusters; the renderer falls back to the `_aux` mirror packet for each of the same three clusters. The result is **3 near-duplicate cards** of the 3 core ones (see §3).

#### extra_blocks[0]
- source_cluster_id (looked up): `relationship_attachment_architecture`
- main_packet_id (from node_id): `moon_leo_8h_deep_proud_heart_aux`
- family: `intimacy_guard`
- headline: "Kalbin güven olmadan tam açılmıyor olabilir."  *(identical to core_blocks[1])*
- teaser: "Derin, gururlu, kolay açılmayan ama açıldığında güçlü bağlanan kalp."
- body: "Mars'ının 11. evde Aslan'da olması ile 7. evinin Koç olması birlikte ilişkideki bu hattı daha net hissettiriyor. Derin, gururlu, kolay açılmayan ama açıldığında güçlü bağlanan kalp. Sen ilişkide sadece biriyle olmak istemiyorsun. Bağlandığında hem sıcak hem de sadık kalabilmek bu bağın sıcak tarafını kuruyor. İçeride çoğu zaman şu ikilik çalışıyor: kalbin hem güven hem de özel hissetme ihtiyacı taşıyor olabilir."
- chips: `["İlişki", "Mars · 11. ev · Aslan", "7. ev Koç"]`

#### extra_blocks[1]
- source_cluster_id (looked up): `career_career_like_career_career_visibility`
- main_packet_id (from node_id): `career_career_visibility_aux`
- family: `visible_power`
- headline: "İnsanlar önce kalite çıtasını, sonra etkini görür."  *(identical to core_blocks[0])*
- teaser: same truncated paragraph as core_blocks[0].
- body: same body as core_blocks[0], with the mid-block "Üretiminde sana özgün…" replaced by the milder "İnsanlar önce kalite çıtasını, sonra etkini görür bu görünürlük hattının güçlü tarafını kuruyor."
- chips: `["Kariyer", "Ay · 9. ev · İkizler", "MC Yengeç"]`

#### extra_blocks[2]
- source_cluster_id (looked up): `mind_mind_like_mind_mind_system`
- main_packet_id (from node_id): `mind_mind_system_aux`
- family: `mind_mechanics`
- headline: same 500+ char body-shape paragraph as core_blocks[2].
- teaser: "Ne yapacağını bildiğin an tempo kendiliğinden yükselir."
- body: differs from core_blocks[2] only in the closing sentence ("Denge kaçtığında … daha belirgin hale gelir." vs. "Zorlayan tarafta ise …").
- chips: `["Zihin", "Venüs · 11. ev · Başak", "Yükselen Terazi"]`

## 2. profile_v8_projection_v1

`version = "profile_v8_projection_v1"`, `source_graph = "natal_promise_cluster_plan_v1"`.

### Hero
- node_id: `promise::mind_mind_system`
- headline: the same 500+ char paragraph that core_blocks[2] uses (see §3).
- summary: opens with "Venüs'ünün 11. evde Başak'ta olması kadar Yükseleninin Terazi olması de bu hattın karakterini belirliyor…" (truncated by hero policy).
- eyebrow / chips on the hero node are both `None`.

### Identity Axis
- eyebrow: "Kimlik Ekseni"
- node_id: `promise::mind_mind_system_aux`  *(same cluster as hero, only the aux packet — see §5)*
- headline: same 500+ char paragraph again.
- chips: `["Zihin", "Venüs · 11. ev · Başak", "Yükselen Terazi"]`

### Insight Strip
1. label "İlişki" / title "Kalbin güven olmadan tam açılmıyor olabilir." / subtitle "Mars'ının 11. evde Aslan'da olması ile 7. evinin Koç olması birlikte ilişkideki bu hattı daha net hissettiriyor." / node `moon_leo_8h_deep_proud_heart`
2. label "Kariyer" / title "İnsanlar önce kalite çıtasını, sonra etkini görür." / subtitle "Ay'ının 9. evde İkizler'de olması ve Kariyer hattının Yengeç'te olması aynı çizgiyi güçlendiriyor." / node `career_career_visibility`
3. label "İlişki" / title "Kalbin güven olmadan tam açılmıyor olabilir." / subtitle "Mars'ının 11. evde Aslan'da olması ile 7. evinin Koç olması…" / node `moon_leo_8h_deep_proud_heart_aux`

Strip slots 0 and 2 are the same İlişki card with the same headline — see §3.

### Differentiators
1. headline "İnsanlar önce kalite çıtasını, sonra etkini görür." — node `career_career_visibility_aux`
2. headline: the 500+ char Mind paragraph — node `mind_mind_system`
3. headline: the same 500+ char Mind paragraph — node `mind_mind_system_aux`

## 3. Copy quality scan

- **No raw English aspect names in headlines / teasers / bodies.** Regex on `\b(sextile|trine|square|conjunction|conjunct|opposition|opposite|midheaven|ascendant)\b` across all 6 cards: zero hits.
- **Duplicate headline+teaser pairs across cards: FAIL.**
  - core_blocks[0] and extra_blocks[1] share the same headline + teaser (Career / Ay 9h İkizler / MC Yengeç).
  - core_blocks[2] and extra_blocks[2] share the same headline + teaser (Mind / Venüs 11h Başak / Yükselen Terazi).
  - core_blocks[1] and extra_blocks[0] share the same headline but the teaser differs (the relationship card and its aux variant).
  Root cause is structural, not copy: when the cluster plan has no public_support and no detail clusters, the public renderer re-renders the same cluster with its `_aux` packet as an extra_block. The `_aux` packet shares the cluster's main headline and only swaps the teaser/body skeleton. This was masked on the Istanbul chart because Istanbul had distinct support + detail clusters to fill `extra_blocks`.
- **Headline contamination on core_blocks[2] / extra_blocks[2] / v8 hero / v8 identity axis / v8 differentiators[1][2]: FAIL.** The headline string is a 500+ character body-shape paragraph that begins "Sen dışarıdan uyumlu ve dengeli görünebilirsin. Yükselenin Terazi olduğu için…" and ends with "…her zaman göstermiyor olabilir." The teaser slot ("Ne yapacağını bildiğin an tempo kendiliğinden yükselir.") is what would normally be the headline. The bespoke override for `mind_mind_system` appears to be feeding the long-form bespoke block into the `headline` slot. This affects 5 of the 6 visible v8 surfaces.
- **No "Hem X hem de Y" body openers.** Verified — zero card bodies open with that template.
- **No "sende güçlü taraflarından" / "bu çizginin daha da güçlenmesi" template closers.** Verified — zero occurrences across all 6 cards.
- **Teaser truncation on core_blocks[0] / extra_blocks[1]: FAIL.** Teaser ends with "İnsanlar sende yalnızca sonucu deği…" — mid-word truncation. The teaser is being filled with a long-form lived-scene paragraph that overflows whatever character budget the teaser slot uses.
- **Body truncation on core_blocks[0] / extra_blocks[1]: FAIL.** Body ends with "…seni gereğinden uzun h…" — same mid-word cut, longer budget but still overflowing.
- **Sentence-start capitalization regression on core_blocks[0] body.** Phrase "Üretiminde sana özgün bir imza veren yer de burada: i̇nsanlar önce kalite çıtasını…" — the "İ" after the colon is rendered as lowercase Turkish "i̇" (i + combining dot). This is an unrelated capitalization bug in the post-colon concatenation; Istanbul's "Bazen de …" capitalization fix has a matching gap for the post-colon path.
- **Cluster anchor / chart anchor mismatch on core_blocks[1] / extra_blocks[0]: WARNING.** The cluster id is `relationship_attachment_architecture` and the underlying packet is `moon_leo_8h_deep_proud_heart`, but the Adana chart has Moon in **Gemini 9h**, not Leo 8h. The body's chart anchors ("Mars'ının 11. evde Aslan'da olması ile 7. evinin Koç olması") are real for this chart (Mars Leo 11h, 7h cusp Aries), so the rendered copy is internally consistent. But the packet id/cluster label is a template name that does not describe this chart's actual Moon position. This is a packet-generation upstream concern, not a renderer one — the public-facing copy never says "Moon in Leo 8h." Flagged for awareness.
- **No semantic Career vs. Relationship overlap.** Career card is the visibility / quality-bar narrative; relationship card is the closeness / loyalty narrative. Bodies are disjoint.
- **Career card mentions "Ay 9. ev İkizler" but Mind card mentions "Venüs 11. ev Başak / Yükselen Terazi" — no overlap on chart anchors.**
- **`extra_blocks` provides zero net new information.** Each extra_block is the `_aux` mirror of an existing core cluster, sharing the same headline. There is no `career_healing_voice`-style second-rank cluster and no support/detail layer to diversify the carousel.

## 4. Cluster / source checks

- `source_graph == "natal_promise_cluster_plan_v1"` ✓
- Public schema **does not** expose the full cluster plan without debug:
  - With `ENABLE_NATAL_PROMISE_PACKET_DEBUG` cleared (and the module re-imported so the env-read at import time is fresh), `profile_narrative_projection_v1.traceability` keys are `[cluster_public_main_count, evidence_count, node_count, packet_count]`. Neither `natal_promise_cluster_plan_v1` nor `natal_promise_packets_v1` is present. Verified by a second build pass in a fresh interpreter.
- candidate_inventory count: **8**.
- public_main cluster count: **3**.
- public_support cluster count: **0**.
- detail cluster count: **0**.
- public_main cluster ids (in order):
  1. `career_career_like_career_career_visibility`
  2. `relationship_attachment_architecture`
  3. `mind_mind_like_mind_mind_system`
- Suppressed packets (3): `career_career_visibility_aux`, `moon_leo_8h_deep_proud_heart_aux`, `mind_mind_system_aux`. All have `keep_for ⊇ {detail, debug, transit_activation}` ✓. Reason: "weaker duplicate for the same domain card job and lived scene". These same `_aux` packets are then re-surfaced as the three extra_blocks despite being marked as `weaker duplicate` — see verdict below.
- Focus map (3 entries, all `strong`):
  - career: tier=strong, score=1.0
  - relationship: tier=strong, score=0.9674
  - mind: tier=strong, score=0.854
- **Identity domain is missing from focus_map entirely.** Istanbul had identity tier `strong` with two clusters (`identity_self_construction`, `identity_gift_like_saturn_trine_pluto_…`). Adana has neither. With Libra ASC, Sun 12h Virgo, and chart ruler Venus square Pluto, an identity track was plausibly expected; its absence is the largest single shape difference vs. Istanbul.

## 5. Product-readiness verdict per block

| Block | Cluster | Verdict | Notes |
|---|---|---|---|
| core_blocks[0] | career_career_like_career_career_visibility | **needs minor copy polish** | Headline + chart-anchor sentence are clean. Teaser overflows (`İnsanlar sende yalnızca sonucu deği…`) and body has a mid-word truncation (`gereğinden uzun h…`). Also a lowercased "i̇nsanlar" after a colon. Underlying narrative is on-voice. |
| core_blocks[1] | relationship_attachment_architecture | **ready** | Headline + teaser + body are coherent and on-voice. Chart anchors (Mars Leo 11h, 7h Koç) match the chart. Only flag: the packet id (`moon_leo_8h_deep_proud_heart`) is a template label that doesn't reflect the actual Moon position; copy never surfaces this, so it's invisible to the user. |
| core_blocks[2] | mind_mind_like_mind_mind_system | **semantically wrong** | The `headline` slot is filled with a 500+ char body-shape paragraph (`"Sen dışarıdan uyumlu ve dengeli görünebilirsin…"`). The actual short headline expected here ("Ne yapacağını bildiğin an tempo kendiliğinden yükselir.") is in the teaser slot. The body is fine. This is a slot-routing bug for the `mind_mind_system` bespoke override. |
| extra_blocks[0] | relationship_attachment_architecture | **semantically wrong (duplicate)** | Same headline as core_blocks[1], different teaser. Duplicates the same cluster card. No new astrological territory. With no public_support or detail layer, the renderer fell back to the aux packet of an existing cluster. |
| extra_blocks[1] | career_career_like_career_career_visibility | **semantically wrong (duplicate)** | Same headline + same teaser as core_blocks[0]. Body differs only mid-paragraph. Same duplication pattern as extra_blocks[0]. |
| extra_blocks[2] | mind_mind_like_mind_mind_system | **semantically wrong (duplicate + slot bug)** | Same long-headline slot-routing bug as core_blocks[2], plus a duplicate of the core mind card. |

Hero / Identity Axis / Differentiators (v8): all five v8 surfaces driven by the Mind cluster inherit the same headline slot-routing bug. The Identity Axis is additionally drawn from the **Mind** cluster (specifically `mind_mind_system_aux`) because no identity-family cluster exists in this chart's plan, so the axis falls back to the next-ranked cluster — but the "Kimlik Ekseni" eyebrow remains. Net effect: an "Identity" header pointing at a Mind packet whose body talks about Libra ASC + Venus 11h Başak.

## Top-line findings (vs. Istanbul)

| Dimension | Istanbul | Adana |
|---|---|---|
| Strong-tier domains | identity, mind, relationship, career (4) | career, relationship, mind (3) — **no identity** |
| public_main / public_support / detail | 6 / 2 / 3 | 3 / 0 / 0 |
| candidate inventory | 11 | 8 |
| core_blocks | 4 | 3 |
| extra_blocks | 6 (diverse: ranks 5–6 + support + detail) | 3 (forced fallback to aux mirrors of core clusters) |
| Duplicate headline+teaser pairs | 0 | 2 |
| Long-form paragraph in headline slot | 0 | 5 surfaces (core[2], extra[2], v8 hero, v8 identity_axis, v8 differentiators[1][2]) |
| Mid-word teaser/body truncation | 0 | core[0] + extra[1] |
| Identity axis driven by identity-family cluster | yes | no — falls back to Mind |

## Out-of-scope follow-ups suggested

1. **Renderer headline-slot bug for `mind_mind_system` bespoke override.** Long-form body content is being placed into the `headline` field; the expected short headline is in the teaser field. Affects 5 v8 surfaces here, including hero and identity axis.
2. **Teaser/body length budget on the `career_career_visibility` packet.** Both fields overflow with mid-word ellipsis. Compare to Istanbul's `chiron_conjunct_mc_visibility_wound_to_voice_chart_exact` which fits cleanly.
3. **Sentence-start capitalization after `:` in body composition.** `Üretiminde … burada: i̇nsanlar` should be `… İnsanlar`. Same template path as Istanbul's "Bazen de …" fix, different trigger.
4. **Empty extra_blocks fallback.** When `surface_plan.public_support_cluster_ids` and `detail_cluster_ids` are both empty, the renderer currently fills `extra_blocks` with the aux mirrors of the core clusters, producing duplicate cards. Consider either (a) leaving `extra_blocks` empty and letting the carousel collapse, or (b) sourcing additional candidates from suppressed inventory beyond strict cluster membership.
5. **Identity-domain coverage gap.** Adana has Libra ASC, Sun 12h Virgo, Venus (chart ruler) square Pluto — none of these landed an identity-family cluster. Investigate whether the packet builder for `identity_self_construction` requires Saturn–ASC contact specifically and is therefore unfired for charts without one.
6. **Packet id vs. chart fact mismatch on `moon_leo_8h_deep_proud_heart`.** The packet label persists even when Moon is elsewhere; the rendered body anchors are correct, but the upstream label is misleading for debugging.

## 6. After P0 fixes

The five P0 bugs surfaced above were fixed in
`backend/app/meaning/projection_shadow_v1_builder.py` and
`backend/app/natal/natal_promise_packets.py`. Re-running the same Adana
artifact through the same builder (via
`backend/scripts/audit_regen_projection.py`) shows every P0 cleared. The
upstream cluster scoring, packet library, and selection logic were NOT
touched — these are renderer-side guards plus one packet-payload
debugging flag.

### 6.a Per-bug verification

| Bug | Adana symptom before | Adana state after | How it was fixed |
|---|---|---|---|
| 1. aux-mirror duplicate `extra_blocks` | 3 extras, each the `_aux` mirror of a core cluster (3 duplicate-headline cards) | `extra_blocks` is **empty** — empty carousel is preferable to duplicate cards | New guard in `_profile_block_from_node`'s extra-source filter: when an extra-source node is the `_aux` mirror of a packet whose parent cluster is already in `core_blocks`, skip it. Applied to both the `cluster_main_count >= 3` branch and the hybrid `cluster_main_count > 0` branch. |
| 2. 500+ char body-shape paragraph in headline slot | core_blocks[2], extra_blocks[2], v8 hero, v8 identity_axis, v8 differentiators[1][2] (5 surfaces) | All headlines are short, single-sentence, under 60 chars. v8 hero / identity_axis: 55 chars each. Differentiators: 50–55 chars. core_blocks[2] headline: "Ne yapacağını bildiğin an tempo kendiliğinden yükselir." | New helpers `_is_long_form_headline` + `_clip_to_headline` + `_fallback_short_headline`. When the incoming `node.headline` exceeds 120 chars or contains more than one sentence, callers (block builder, v8 hero, identity axis, differentiator, insight strip) pull a short alternative from packet fields (`override.teaser`, `voice_seeds`, `lived_scene_short`, `direct_meaning`, `lived_scene`, or summary). The demoted long-form string is routed to the body slot when the body would otherwise be empty/short. |
| 3. mid-word teaser/body truncation (`İnsanlar sende yalnızca sonucu deği…`, `gereğinden uzun h…`) | core_blocks[0] / extra_blocks[1] | Regex `[a-zçğıöşü]…` against teaser+body across all blocks: **0 hits** | Replaced hard `_short_text` slicing with new `_smart_clip(text, max_chars)` helper in renderer paths that previously cut into words. Rule order: (a) if it fits, return unchanged; (b) cut at last sentence boundary inside the budget; (c) else cut at last whitespace before `max_chars - 1` and append `…`. Used budgets are unchanged — only the cut algorithm. |
| 4. post-colon decomposed `i̇` (`burada: i̇nsanlar…`) | core_blocks[0] body | Regex `[.!?:;]\s+i̇` across all fields: **0 hits**. The phrase now reads `burada: İnsanlar` with a precomposed U+0130. | Extended the sentence-cap helper in `_localize_public_copy_tr` to also fire after `:` and `;`. Added an explicit `i → İ` mapping so the post-colon capital uses U+0130, not the decomposed `i + U+0307` pair. Added a defensive repair rule that collapses any decomposed `i̇` immediately after `[.!?:;]\s+` back to `İ`. |
| 5. packet id vs. chart fact mismatch (`moon_leo_8h_deep_proud_heart` selected for a chart with Moon in Gemini 9h) | misleading debug label only — copy is chart-correct | Packet now carries `chart_facts_match: false` in its payload. Packet id and copy are unchanged (deliberately, to keep blast radius small). | Added `_annotate_chart_facts_match` post-step in `build_natal_promise_packets_v1`. A small `_CHART_FACT_VALIDATORS` table maps placement-encoded base ids (`moon_leo_8h_*`, `venus_sagittarius_12h_*`, `saturn_3h_aries_*`, `capricorn_asc_sun_1h_*`) to chart-fact predicates. Packets whose id encodes a placement absent from the chart get the flag set to `False`; matching packets get `True`; packets whose id doesn't encode a checkable placement are left untouched. |

### 6.b Decision notes

- For Bug 5, I picked the **flag-on-packet** route over **rename packet id** for the reasons listed in the task spec: the rename approach would have ripple effects through cluster plan grouping, tests that key on packet ids, and the projection node id format `promise::<packet_id>`. The flag is a minimal, additive change that fixes the debugging hazard without touching any of those surfaces. Copy is unaffected on Adana because anchors are already pulled from chart data, not from the packet id.
- For Bug 1, the fix deliberately allows `extra_blocks` to be empty when there is no diverse content to surface. The downstream carousel collapses on empty extras already (verified — no tests broke). This matches the "empty is allowed" constraint in the task spec.
- For Bug 2, the long-form paragraph is preserved (routed to body) rather than discarded. This keeps the bespoke override's craft intact while protecting the headline slot.

### 6.c Quantitative snapshot (Adana, after fixes)

- `core_blocks`: 3 (cluster ids and headline-anchor pairs unchanged from §1.a)
- `extra_blocks`: 0 (was 3 duplicates before)
- duplicate headlines across all blocks: 0 (was 2 before)
- headlines longer than 200 chars: 0 (was 5 surfaces before)
- mid-word teaser/body hits: 0 (was 2 before)
- post-colon decomposed `i̇` hits: 0 (was 1 before)
- aux-mirror duplicates in `extra_blocks`: 0 (was 3 before)
- packets carrying `chart_facts_match: false`: 1 — `moon_leo_8h_deep_proud_heart`, as expected for this chart's Moon in Gemini 9h

### 6.d Test results

`pytest backend/tests/test_natal_promise_cluster_plan.py
backend/tests/test_natal_promise_packets.py
backend/tests/test_natal_public_builder.py
backend/tests/test_projection_shadow_v1_builder.py` — **49 passed** (45 pre-existing + 4 new):

- `test_headline_slot_rejects_body_shape_paragraph` (Bug 2)
- `test_no_aux_mirror_duplicate_when_support_and_detail_empty` (Bug 1)
- `test_smart_clip_never_breaks_mid_word` (Bug 3)
- `test_post_colon_capitalization_uses_turkish_i` (Bug 4)

### 6.e Remaining gaps (not P0, still open)

- The identity-domain coverage gap noted in §4 (Adana has no identity-family cluster despite a Libra ASC + Sun 12h Virgo + Venus square Pluto signature) is unchanged — that is an upstream packet-generation concern, out of scope for this round.
- v8 identity-axis still falls back to the next-ranked Mind cluster because Adana has no identity-family cluster in the plan. The headline-slot guard now keeps that fallback readable (short headline), but the "Kimlik Ekseni" eyebrow over a Mind packet remains a content concern, not a renderer concern.


## 7. After v0.3 archetype overlay

This section captures the Adana cluster plan after the v0.3 addendum (18 new
archetypes covering Libra ASC / Venus chart-ruler, Virgo Sun/Mercury/Venus,
12H private processing, 11H Venus/Mars social field, Moon Gemini 9H, Moon
square Mercury/Venus, Mercury/Venus square Pluto, Mars-Uranus opposition,
Mars-Chiron square, MC Cancer→Moon ruler route, Saturn Taurus 8H, Sun
opposite Jupiter, Neptune 4H) has been applied as an additive registry
overlay. The renderer P0 fixes from round 6 are untouched.

### 7.a Candidate inventory

- candidate_inventory count: **24** (was 3 before v0.3).
- v0.3 packet ids newly present in the inventory:
  - identity: `libra_asc_venus_chart_ruler_chart_exact`,
    `sun_virgo_12h_quiet_inner_self_chart_exact`,
    `neptune_4h_soft_inner_presence_chart_exact`,
    `sun_opposite_jupiter_service_expansion_tension_chart_exact`
  - mind: `moon_gemini_9h_curious_mind_chart_exact`,
    `mercury_virgo_12h_private_analytical_mind_chart_exact`,
    `mercury_square_pluto_deep_mind_pressure_chart_exact`,
    `mercury_conjunct_venus_refined_relational_language`,
    `moon_square_mercury_emotion_mind_friction`
  - relationship: `venus_virgo_11h_selective_social_care_chart_exact`,
    `venus_square_pluto_intense_love_chart_exact`,
    `mars_leo_11h_warm_visible_drive_chart_exact`,
    `mars_opposite_uranus_freedom_in_action_chart_exact`,
    `moon_square_venus_need_affection_friction`,
    `moon_opposite_pluto_emotional_intensity_control_chart_exact`
  - career: `mc_cancer_moon_gemini_9h_teaching_voice_chart_exact`,
    `saturn_taurus_8h_steady_public_maturity_chart_exact`,
    `mars_square_chiron_tender_courage`
  - community: `mars_leo_11h_warm_visible_drive_community_chart_exact`
- Every `*_chart_exact` packet carries `chart_facts_match: true` — the
  chart-correctness filter (new helper `_filter_entries_against_chart`)
  drops placement-encoded registry entries whose placement is absent on
  Adana so misleading voice_seeds (e.g. `moon_leo_8h_deep_proud_heart`) no
  longer leak through the text-based `_match_registry` path.
- `moon_leo_8h_deep_proud_heart` is **no longer present** in Adana's
  inventory — Moon is in Gemini 9H, so the registry entry is filtered out
  before sections / threads can match it.

### 7.b focus_map

| domain | tier | score |
|---|---|---|
| career | strong | 1.00 |
| identity | medium_strong | 0.80 |
| relationship | medium_strong | 0.75 |
| mind | medium_strong | 0.75 |
| action_pressure | supporting | 0.48 |

v0.3 §17 expected tendencies: mind / identity / relationship / career all at
strong or medium_strong — **met** (was: only `mind` and `career` had
strong coverage; identity had none).

### 7.c Public surface plan

`public_main` (5):

1. `mind_gift_like_mercury_conjunct_venus_refined_relational_language` → `mercury_conjunct_venus_refined_relational_language`
2. `identity_wound_like_mars_square_chiron_tender_courage` → `mars_square_chiron_tender_courage`
3. `career_career_like_mc_cancer_moon_gemini_9h_teaching_voice_chart_exact` → `mc_cancer_moon_gemini_9h_teaching_voice_chart_exact`
4. `relationship_love_like_venus_square_pluto_intense_love_chart_exact` → `venus_square_pluto_intense_love_chart_exact`
5. `action_pressure_resilience_under_pressure` → `mars_leo_11h_warm_visible_drive_community_chart_exact`

Headlines / teasers for the new public_main lineup:

- relationship main (Venus square Pluto):
  - headline / voice_seed: "Yoğunluğu kontrol etmeye çalışmadığında, ilişki seni daha dürüst bir yakınlığa taşıyabilir."
  - direct meaning: "Sevgi ve çekim sende hafif kalmayabilir; bağ kurduğunda yoğunluk, değer görme ve kontrol temaları da çalışabilir."
- career main (MC Cancer → Moon Gemini 9H teaching voice):
  - headline: "Görünür olduğunda insanlara sadece bilgi değil, güven hissi de vermek isteyebilirsin."

`public_support`: empty (Adana focus is well-distributed; nothing falls into
the support tier on this chart).

`detail` (14) includes the Mars-Uranus, Moon-Pluto, Mars Leo 11H warm visible
drive (relationship variant), Moon-Venus need/affection friction, Saturn
Taurus 8H public maturity, Mercury Virgo 12H private analytical mind, Sun
Virgo 12H quiet inner self, Venus Virgo 11H selective social care, Moon
Gemini 9H curious mind, Mercury square Pluto deep mind pressure, and
Libra ASC / Venus chart-ruler identity clusters.

### 7.d Per-block verdict

- **identity_self_recognition (libra_asc_venus_chart_ruler_chart_exact)**:
  semantically correct (Libra ASC, Venus in Virgo as chart ruler). Now sits
  in `detail` because Mars-Chiron tender courage took the higher-priority
  identity-wound slot; the Libra ASC voice still surfaces through Sun Virgo
  12H "Görünür olmadan önce temelin sağlam olduğundan emin olmak isteyebilirsin."
  in `extra_blocks`. **Ready.**
- **relationship cluster main**: now `venus_square_pluto_intense_love_chart_exact`
  — exactly the v0.3 §17.3 ideal anchor (Venus square Pluto, deep love
  pattern). Chart-correct, headline reads cleanly, no friction-layer bleed.
  Moon-Venus square need/affection friction sits in `detail` as a
  complementary support angle. **Ready.**
- **mind cluster main**: `mercury_conjunct_venus_refined_relational_language`
  — chart-correct (Mercury conjunct Venus in Virgo). **Ready.**
- **career cluster main**: now `mc_cancer_moon_gemini_9h_teaching_voice_chart_exact`
  — the v0.3 §17.4 ideal MC Cancer → Moon Gemini 9H teaching voice, exactly
  what the Adana brief asked for. Mars-Chiron tender courage moved to
  `identity_wound_like_*` (its more accurate home). Saturn Taurus 8H public
  maturity remains in `detail`. **Ready.**
- **action_pressure cluster**:
  `mars_leo_11h_warm_visible_drive_community_chart_exact` got assigned to
  `action_pressure` domain_family via the text-token heuristic in
  `_domain_family` (mars / community / aquarius tokens). Reads cleanly as a
  community-leadership block. **Ready.**

### 7.e Regression checks (P0 fixes hold)

- mid-word teaser/body hits: **0**
- post-colon decomposed `i̇` hits: **0**
- aux-mirror duplicates in `extra_blocks`: **0**
- headlines longer than 200 chars: **0**
- duplicate headlines across all blocks: **0**
- packets with `chart_facts_match: false`: **0** (Moon Leo 8H no longer
  fires on this chart at all)

### 7.f Test results

`pytest backend/tests/test_natal_promise_cluster_plan.py
backend/tests/test_natal_promise_packets.py
backend/tests/test_natal_public_builder.py
backend/tests/test_projection_shadow_v1_builder.py` — **52 passed** (49
pre-existing + 2 Adana v0.3 goldens + 1 new relationship-domain regression):

- `test_natal_promise_cluster_plan_adana_golden_v0_3_overlay`: asserts
  mind/identity/relationship/career focus tiers are strong/medium_strong,
  Libra ASC chart-ruler fires, ≥3 of Mars-Uranus / Venus-Pluto / Mars Leo
  11H / Moon-Venus anchors fire, Moon Leo 8H does NOT fire on Adana, and
  every `*_chart_exact` packet carries `chart_facts_match: true`.
- `test_natal_promise_packets_chart_correctness_filter_drops_misencoded_archetypes`:
  asserts the Moon Leo 8H signature voice_seed does not leak into Adana
  packets via the text-based registry match.
- `test_natal_promise_cluster_plan_adana_relationship_main_is_chart_anchored`
  (new this round): asserts no `relationship_*` cluster carries the mind
  archetype `moon_square_mercury_emotion_mind_friction` in any role, and
  Adana's relationship public_main resolves to one of the spec-listed
  relationship anchors (Mars Leo 11H / Mars-Uranus / Venus-Pluto / Moon-Venus).

### 7.g Domain-fit fix (this round)

The previous round shipped 18 v0.3 archetypes but Adana's relationship
public_main resolved to `moon_square_mercury_emotion_mind_friction`, which
is a mind/cognitive friction archetype per spec §16.6 — wrong family for
a relationship cluster.

Root cause: in `app/natal/natal_promise_packets.py::_resolve_domain`, the
title-based fast paths (`"ilişki" in title -> return "relationship"`) fired
unconditionally, so a mind archetype matched under a relationship-titled
section was tagged `domain="relationship"`. That `relationship` variant then
participated in the cluster plan as if it were a real relationship archetype
and won the public_main slot.

Fix (minimal-touch, additive): teach `_resolve_domain` to look at the matched
archetype's registry-declared `domains` and only honour a title-based fast
path when the archetype's registry families include the title's family.
Implemented via a new `_DOMAIN_FAMILY_MAP` constant and a
`_registry_domain_families(match)` helper. `emotional_world` is mapped to
its own family (not `relationship`) because it denotes inner emotional life,
not interpersonal relationships, so a `mind` archetype listing
`emotional_world` no longer unlocks relationship-section domain bleed.

Result on Adana:
- the rogue `domain="relationship"` variant of
  `moon_square_mercury_emotion_mind_friction` is no longer generated
- relationship public_main is now `venus_square_pluto_intense_love_chart_exact`
  (one of the spec §17.3 ideal anchors)
- career public_main is now `mc_cancer_moon_gemini_9h_teaching_voice_chart_exact`
  (one of the spec §17.4 ideal anchors) — a knock-on improvement, because the
  Mars-Chiron tender_courage packet moved to its more accurate
  `identity_wound_like_*` cluster

Istanbul is byte-identical at cluster level (see
`istanbul_cluster_plan_audit_after_renderer_polish.md` §7.h).

### 7.h Remaining gaps (not P0, still open)

- None of the previously listed gaps in this section. The Adana relationship
  / career main_packet_id concerns are resolved by the §7.g domain-fit fix.
