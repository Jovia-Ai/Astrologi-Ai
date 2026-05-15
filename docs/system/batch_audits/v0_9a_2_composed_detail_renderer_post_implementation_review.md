# v0.9a.2 Composed Detail Renderer Post-Implementation Review

## Scope

- Implemented slice: `career_route` only
- Subtype: `public_voice` only
- Surface class: composed detail cards only
- Still disabled:
  - `public_main`
  - `public_support`
  - non-`public_voice` career subtypes
  - `identity_route`
  - `relationship_route`
  - `moon_signature`

## Flag State

Required flags for composed detail rendering:

- `ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9=true`
- `ENABLE_NATAL_COMPOSED_SEMANTICS_DETAIL_SUPPORT=true`
- `ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_VOICE_DETAIL_SUPPORT=true`
- `ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_MAIN=false`
- `ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL=true`

Default behavior remains:

- `ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL=false`
- when false, composed candidates stay internal/debug only
- user-visible public surfaces stay unchanged

## Lane Status

Dedicated public `composed_detail_cards` lane does **not** exist yet.

Current implementation therefore uses:

- debug/audit-visible traceability lane only:
  - `public.profile_narrative_projection_v1.traceability.composed_detail_cards_v0_9a_2`
  - `public.profile_v8_projection_v1.traceability.composed_detail_cards_v0_9a_2`

Current implementation explicitly does **not** render composed cards into:

- `profile_narrative_projection_v1.profile_public.blocks`
- `profile_narrative_projection_v1.profile_public.extra_blocks`
- `profile_v8_projection_v1.differentiators`
- `profile_v8_projection_v1.insight_strip`
- `hero`
- `identity_axis`

## Visibility Matrix

| Chart | Render Flag Off | Render Flag On | User-visible surface change | Debug traceability card |
|---|---|---|---|---|
| `fix04_h10_career_stellium` | no composed card | 1 composed card | no | yes |
| `tokyo_1998_06_21` | no composed card | 1 composed card | no | yes |
| `toronto_1976_06_26` | no composed card | 1 composed card | no | yes |

Interpretation:

- with render flag off: strict no-op
- with render flag on: composed cards become traceable in debug payloads only
- user-facing public copy remains unchanged

## Target Chart Outputs

### 1. `fix04_h10_career_stellium`

Rendered composed detail card:

- `headline`: `İnsanlar sende sadece ne yaptığını değil, nasıl söylediğini de fark ediyor.`
- `teaser`: `Dışarıdaki etkin çoğu zaman sözünün tonu ve kurduğun pozisyonla güçleniyor.`
- `body`: `Bir işi yalnız tamamlaman değil, onu nasıl anlattığın da sende görünür rolün parçası oluyor. İnsanlar çoğu zaman önce fikrinin tonunu, sonra o tonun yarattığı etkiyi fark edebilir. Buradaki güç, sesini daha yüksek kullanmakta değil; doğru yerde netleştiğinde dışarıdaki rolün zaten belirginleşmesinde yatıyor.`
- `chips`: `["Kariyer", "Söz", "Görünür rol"]`
- `source_candidate_id`: `composed_career_route_v0_9a`
- `source_type`: `composed_semantic`

Trace summary:

- `family`: `career_route`
- `subtype`: `public_voice`
- `domain_reason`: `["MC route", "MC ruler involved", "10H planet"]`
- `technical_anchors`: `["MC Gemini", "Mercury · Cancer · 10. ev", "Mercury · 10. ev", "Mars · 10. ev"]`

### 2. `tokyo_1998_06_21`

Rendered composed detail card:

- `headline`: `Dışarıdaki yerin çoğu zaman kurduğun cümleyle netleşiyor.`
- `teaser`: `Ne söylediğin kadar, onu hangi sakinlik ve yön duygusuyla söylediğin de fark yaratıyor.`
- `body`: `İnsanlar sende yalnızca çalışmanı değil, o çalışmayı nasıl taşıdığını da duyabilir. Bir konuda netleştiğinde sözün dışarıdaki rolünü hızlıca güçlendirebilir. Burada asıl fark, görünür olmak için zorlaman değil; doğru cümle geldiğinde yerinin zaten daha belirgin hale gelmesi.`
- `chips`: `["Kariyer", "İfade", "Konum"]`
- `source_candidate_id`: `composed_career_route_v0_9a`
- `source_type`: `composed_semantic`

Trace summary:

- `family`: `career_route`
- `subtype`: `public_voice`
- `domain_reason`: `["MC route", "MC ruler involved", "10H planet"]`
- `technical_anchors`: `["MC Gemini", "Mercury · Cancer · 10. ev", "Sun · 10. ev", "Mercury · 10. ev"]`

### 3. `toronto_1976_06_26`

Rendered composed detail card:

- `headline`: `Görünür olduğunda bunu en çok sözün taşıyor.`
- `teaser`: `Dış dünyadaki etkin, anlatım biçiminle ve insanlarda bıraktığın zihinsel iz ile büyüyebilir.`
- `body`: `Bazı insanlar işini yapar; sende ise işin nasıl konuşulduğu da rolün önemli bir parçası olabilir. Bir cümleyi doğru kurduğunda ya da bir şeyi doğru çerçevelediğinde dışarıdaki ağırlığın daha hızlı hissedilebilir. Bu yüzden kariyer hattın yalnız görünürlük değil, görünürlükle birlikte çalışan bir ifade gücü de taşıyor.`
- `chips`: `["Kariyer", "Söz", "Etki"]`
- `source_candidate_id`: `composed_career_route_v0_9a`
- `source_type`: `composed_semantic`

Trace summary:

- `family`: `career_route`
- `subtype`: `public_voice`
- `domain_reason`: `["MC route", "MC ruler involved", "10H planet"]`
- `technical_anchors`: `["MC Gemini", "Mercury · Gemini · 10. ev", "Sun · 10. ev", "Moon · 10. ev", "Mercury · 10. ev"]`

## Copy Quality Scan

Quality checks on the rendered composed detail cards:

- no `debug` language in public fields
- no `candidate` language in public fields
- no `fallback` language in public fields
- no raw `source_type` / `public_job` prose leakage
- no raw `MC route` / `10H` / `MC, yoneticisi...` body leakage
- no mixed English/Turkish debug wording in public fields
- no technical astrology in `headline`, `teaser`, or `body`
- public fields (`headline` / `teaser` / `body` / `chips`) carry proper Turkish diacritics (`İ`, `ı`, `ş`, `ğ`, `ç`, `ö`, `ü`)
- no ASCII Turkish residue (`Insanlar`, `Disaridaki`, `nasil`, `soyledigini`, `Soz`, `Gorunur`, `guc`, `dogru`, `cumle`, `cercevelediginde`, `agirligin`, `Ifade`, …) in public fields

Result:

- pass for all three target cards

### Turkish Text Normalization Patch (v0.9a.2 follow-up)

The first cut of the composed detail renderer emitted ASCII-normalized
Turkish (missing diacritics) in `headline` / `teaser` / `body` / `chips`.
Although the cards were already gated to the traceability lane only, the
text would have failed Turkish copy QA on any future public surface.

Fix applied:

- Authored the renderer's hardcoded variant strings with full Turkish
  diacritics (`İnsanlar`, `Dışarıdaki`, `nasıl`, `söylediğini`, `söz`,
  `görünür`, `güç`, `doğru`, `cümle`, `çerçevelediğinde`, `ağırlığın`,
  `İfade`, etc.).
- Added a narrow composed-detail normalization helper
  (`_has_turkish_ascii_residue` / `_TURKISH_ASCII_RESIDUE_PATTERN`) and
  wired it into `_meets_public_quality`. Any card whose public fields
  contain a banned ASCII-Turkish form is rejected before render.
- Matching is intentionally case-sensitive: Python's simple case folding
  treats `i`/`I`/`ı`/`İ` as equivalent under `re.IGNORECASE`, which would
  cause false positives against correct Turkish (e.g. `İnsanlar` matching
  the ASCII pattern `insanlar`, or `yalnız` matching `yalniz`). For words
  whose lowercase Turkish form contains a diacritic (`ı`, `ş`, `ğ`, `ç`,
  `ö`, `ü`), the lowercase ASCII variant is banned directly; for words
  like `İnsanlar`/`İfade` whose lowercase form is identical between ASCII
  and Turkish, only the capitalized ASCII form is banned.

Scope guard:

- `source_anchor_trace` and other technical fields (`technical_anchors`,
  `domain_reason`, ids) are unchanged — these are technical traceability,
  not public copy.
- No change to flag-gating, no change to the registry, no change to
  selection, no public lane added.

## Public Surface Protection

Confirmed with render flag on:

- `public_main` unchanged
- `public_support` unchanged
- `detail_cluster_ids` unchanged
- no composed card inserted into `blocks`
- no composed card inserted into `extra_blocks`
- no composed card inserted into `differentiators`
- no composed card inserted into `insight_strip`

This means the slice is:

- renderer-capable
- traceability-visible
- still non-user-visible

## Golden Stability

Focused regression result:

- `backend/tests/test_composed_detail_renderer.py`
- `backend/tests/test_natal_public_builder.py`
- `backend/tests/test_natal_promise_packets.py`
- `backend/tests/test_natal_promise_cluster_plan.py`
- `backend/tests/test_projection_shadow_v1_builder.py`

Result:

- `106 passed` (includes the new Turkish diacritic / ASCII-residue tests
  on `test_composed_detail_renderer.py`)

Accepted goldens remain stable because:

- composed detail rendering is gated by a dedicated flag
- no composed card enters `public_main`
- no composed card enters `public_support`
- no existing generic renderer path was widened

## Limitations Before Future Public Display

Remaining limitations:

1. There is still no dedicated user-facing composed-detail lane.
2. Current composed cards are only exposed through traceability/debug payloads.
3. Public-facing activation would still need:
   - a dedicated composed detail lane or detail-card contract in the public payload
   - a deliberate routing rule for where those cards should appear
   - a separate copy QA pass on SHOU voice consistency
   - regression coverage proving no spillover into `differentiators`, `extra_blocks`, or `public_main`

## Conclusion

`v0.9a.2` is technically successful in the intended narrow sense:

- eligible `career_route.public_voice` composed candidates can now be rendered into structured detail cards
- rendering is safely flag-gated
- cards remain traceable
- public surfaces remain unchanged

The next required work before any real public display is still:

- a dedicated composed detail lane
- explicit public routing
- final SHOU copy QA for visible surfaces
