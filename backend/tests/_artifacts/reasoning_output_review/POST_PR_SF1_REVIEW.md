# POST PR-SF1 Review

Generated on 2026-05-05 after rerunning:

```bash
PYTHONPATH=backend backend/venv/bin/python backend/scripts/dev/extract_reasoning_outputs.py
```

This review compares:

1. **Before PR-SF1**: the previously checked-in extraction artifacts and the notes already captured in [OUTPUT_REVIEW_INDEX.md](/Users/sahradenizozdogan/Astrologi-Ai/backend/tests/_artifacts/reasoning_output_review/OUTPUT_REVIEW_INDEX.md)
2. **After PR-SF1 script rerun**: the refreshed JSON artifacts in this folder
3. **After PR-SF1 runtime path**: direct `build_period_core(...)` checks for the same fixtures

That split matters because the extraction script still builds `PeriodStoryContext(...)` manually and does **not** go through the new runtime `build_period_core(...)` path where PR-SF1 computes `semantic_focus`.

## Topline

- **Runtime truth improved**: `period_core.semantic_focus` now exists in the real `build_period_core(...)` path.
- **Tier-1 ownership works in runtime**: Aries 3rd Saturn return, Cancer 8th Saturn return, and NN Aries / SN Libra nodal case all resolve to `semantic_focus.source == "life_chapter"`.
- **Renderer debug improved in runtime**: `_period_story_debug.semantic_focus` is now present and mirrors the selected semantic owner.
- **Extraction script truth is now partially stale**: its JSON artifacts still show `period_core.semantic_focus = null` because the script bypasses `build_period_core(...)`.
- **Renderer gap remains**: even in the runtime path, `period_opening` is still dominated by the old generic opener, and `mechanism/growth_edge/what_it_builds` do not yet sound like direct renderings of the chapter handoff.
- **Public payload shape stayed additive/safe**: the new semantic ownership surface appears as additive `period_core.semantic_focus` and debug fields, not as a breaking top-level schema change.

## Case 1 — Aries 3rd Saturn Return + South Node Overlap

### Before PR-SF1

- `active_life_chapter.selected_meaning`
  - `Koç 3. ev hattında söz ve zihinsel reflekslerin, düğüm ekseniyle birlikte, daha seçilmiş ve daha sorumlu bir forma yerleşmesi`
- `period_opening`
  - `Asıl omurga burada yavaş ama kalıcı biçimde kuruluyor. Bu dönem hayatının bir alanı daha görünür hale geliyor ve senden daha bilinçli seçimler istiyor.`
- `mechanism`
  - `Bu dönem hikâye önce zihin ve iletişim tarafında başlıyor, sonra yavaş yavaş zihin ve iletişim alanına yayılıyor. Yani küçük görünen bir hareket daha büyük bir yön değişimini tetikleyebilir.`
- `growth_edge`
  - `Risk, ilk hissi sonuç sanıp süreci aceleye getirmek.`
- `period_core.semantic_focus`
  - `null`
- `period story debug.semantic_focus`
  - missing / effectively absent

### After PR-SF1 script rerun

- `active_life_chapter.selected_meaning`
  - unchanged
- `period_opening`
  - unchanged
- `mechanism`
  - unchanged
- `growth_edge`
  - unchanged
- `period_core.semantic_focus`
  - still `null`
- `period story debug.semantic_focus`
  - now present as `{}` only

### After PR-SF1 runtime path

- `period_core.semantic_focus`
  - `selected_meaning: speech_authority`
  - `meaning_family: speech_authority_maturation`
  - `primary_domain: communication_learning`
  - `confidence: 0.85`
  - `source: life_chapter`
  - `suppressed_meanings`: includes `generic communication difficulty`, `sibling conflict prediction`, `ordinary transit framing`
- `period story debug.semantic_focus`
  - mirrors the same summary and keeps `source: life_chapter`
- `period_opening`
  - still: `Asıl omurga burada yavaş ama kalıcı biçimde kuruluyor...`
- `mechanism`
  - now: `Sende zaten çalışan birkaç ayrı taraf var. Bu dönem onlar birbirine daha yakın duruyor. Bu tema daha çok büyük resmi kurduğun yer içinden görünür oluyor.`
- `growth_edge`
  - now: `Asıl ayrım, büyük resmi kurduğun yer tarafında büyüyen tepkiyi bütün hikayenin yerine koymamak.`
- `what_it_builds`
  - now: `Sende daha bütünlüklü bir yön kuruyor; içeride ayrı konuşan parçalar aynı cümlede toplanıyor.`

### What changed

- **Meaning ownership changed materially in runtime**: chapter is now the explicit semantic owner.
- **Prose did not become chart-specific enough**: the new lines are no longer the old event-mechanism sentence, but they still sound like generic policy/track copy.
- `selected_meaning`, `meaning_family`, `renderer_handoff.human_scene`, `core_contrast`, and `suppressed_readings` are visible in debug but **barely audible** in final prose.

### Remaining renderer gap

- The opening still ignores the chapter handoff almost completely.
- `mechanism` does not render `speech_authority`, `fast response vs chosen stance`, or the South Node overlap.
- The scene translation is currently dragged toward fallback manifestation context (`9th-house / büyük resmi kurduğun yer`) rather than the chapter’s 3rd-house human scene.

## Case 2 — Cancer 8th Saturn Return

### Before PR-SF1

- `active_life_chapter.selected_meaning`
  - `Yengeç 8. ev hattında duygusal güvenlik, ortak yük ve derin bağ kurma biçiminin; birlikte taşınanla içeride tek başına taşınanı daha bilinçli ayıran dayanıklı bir forma yerleşmesi`
- `period_opening`
  - `Asıl omurga burada yavaş ama kalıcı biçimde kuruluyor. Bu dönem neyi sahiplendiğin ve neyi ortak kullanacağın daha görünür hale geliyor.`
- `mechanism`
  - `Bu dönem hikâye önce derin bağlar ve güven tarafında başlıyor, sonra yavaş yavaş derin bağlar ve güven alanına yayılıyor. Yani küçük görünen bir hareket daha büyük bir yön değişimini tetikleyebilir.`
- `growth_edge`
  - `Risk, kişisel değeri başkasının onayına ya da başka birinin gücüne bağlamak.`
- `period_core.semantic_focus`
  - `null`
- `period story debug.semantic_focus`
  - missing / absent

### After PR-SF1 script rerun

- `active_life_chapter.selected_meaning`
  - unchanged
- `period_opening`
  - unchanged
- `mechanism`
  - unchanged
- `growth_edge`
  - unchanged
- `period_core.semantic_focus`
  - still `null`
- `period story debug.semantic_focus`
  - now `{}` only

### After PR-SF1 runtime path

- `period_core.semantic_focus`
  - `selected_meaning: shared_emotional_territory`
  - `meaning_family: shared_trust_maturation`
  - `primary_domain: trust_transformation`
  - `confidence: 0.85`
  - `source: life_chapter`
  - `suppressed_meanings`: includes `generic emotional regulation`, `oversensitivity cliché`, `self-care simplification`, `generic vulnerability language`
  - `scene_translation_request`: carries `trust_axis_anchor`, `shared_vs_private_contrast`, `shared_domain_priority`, `mahrem konuşmalar`, `birlikte taşınan yükler`
- `period story debug.semantic_focus`
  - mirrors the same chapter-owned contract
- `period_opening`
  - still generic: `Asıl omurga burada yavaş ama kalıcı biçimde kuruluyor...`
- `mechanism`
  - now generic-policy again: `Sende zaten çalışan birkaç ayrı taraf var...`
- `growth_edge`
  - now generic-policy again: `Asıl ayrım, uzak hedeflerin ve inançların tarafında büyüyen tepkiyi bütün hikayenin yerine koymamak.`
- `what_it_builds`
  - now generic-policy again: `Sende daha bütünlüklü bir yön kuruyor...`

### What changed

- Ownership is now explicit and correct in runtime.
- The handoff density is present in debug.
- Final prose still fails to render the actual 8th-house trust/shared/private payload.

### Remaining renderer gap

- This is the clearest mismatch.
- `shared_burden`, `emotional_exchange`, `dependency_tension`, `trust_under_pressure`, and `shared_vs_private_contrast` are present upstream but do not reach public prose.
- The runtime renderer is still being steered by generic policy/manifestation fallback more than by the chapter’s 8th-house semantic contract.

## Case 3 — Nodal Activation / NN Aries / SN Libra

### Before PR-SF1

- `active_life_chapter.selected_meaning`
  - `Koç 3. ev hattında başkalarına göre ayar verme refleksinden çıkıp daha doğrudan yön seçmeye alan açılması`
- `period_opening`
  - `Asıl omurga burada yavaş ama kalıcı biçimde kuruluyor. Bu dönem hayatının bir alanı daha görünür hale geliyor ve senden daha bilinçli seçimler istiyor.`
- `mechanism`
  - `Bu dönem hikâye önce zihin ve iletişim tarafında başlıyor, sonra yavaş yavaş zihin ve iletişim alanına yayılıyor. Yani küçük görünen bir hareket daha büyük bir yön değişimini tetikleyebilir.`
- `growth_edge`
  - `Risk, ilk hissi sonuç sanıp süreci aceleye getirmek.`
- `period_core.semantic_focus`
  - `null`
- `period story debug.semantic_focus`
  - missing / absent

### After PR-SF1 script rerun

- `active_life_chapter.selected_meaning`
  - unchanged
- `period_opening`
  - unchanged
- `mechanism`
  - unchanged
- `growth_edge`
  - unchanged
- `period_core.semantic_focus`
  - still `null`
- `period story debug.semantic_focus`
  - now `{}` only

### After PR-SF1 runtime path

- `period_core.semantic_focus`
  - `selected_meaning: directional_self_definition`
  - `meaning_family: nodal_direction_self_definition`
  - `primary_domain: identity_presence`
  - `confidence: 0.85`
  - `source: life_chapter`
  - `suppressed_meanings`: includes `generic self/other balance` and `fated relationship drama`
- `period story debug.semantic_focus`
  - present and chapter-owned
- `period_opening`
  - still the same generic opening
- `mechanism`
  - now generic-policy:
    - `Sende zaten çalışan birkaç ayrı taraf var. Bu dönem onlar birbirine daha yakın duruyor. Bu tema daha çok uzak hedeflerin ve inançların içinden görünür oluyor.`
- `growth_edge`
  - generic-policy:
    - `Asıl ayrım, uzak hedeflerin ve inançların tarafında büyüyen tepkiyi bütün hikayenin yerine koymamak.`
- `what_it_builds`
  - generic-policy:
    - `Sende daha bütünlüklü bir yön kuruyor; içeride ayrı konuşan parçalar aynı cümlede toplanıyor.`

### What changed

- Ownership is now correct and explicit.
- Directional node logic survives into `semantic_focus`.
- Renderer still does not say the actual thing the chapter selected: leaving relational over-adjustment and choosing a more direct vector.

### Remaining renderer gap

- The prose still does not use `directional_self_definition`, `chart_specific_anchor`, or the Aries/Libra contrast in public copy.
- Suppressed shallow readings are working upstream, but the public result still feels semantically flattened.

## Case 4 — Daily Sample

### After rerun

- `daily_synthesis_sample.json` still has `period_core.semantic_focus = null`.

### Interpretation

- This is **not** evidence that PR-SF1 failed for daily.
- It shows the daily extraction sample is still built from an older transit narrative artifact path and does not currently rehydrate the new runtime period-core semantic focus.

### Remaining gap

- Daily is still not a reliable proof surface for PR-SF1.
- If daily review is needed after SF1, the extraction harness should be upgraded to consume a live public payload that already includes the new additive `period_core.semantic_focus`.

## Answers to the requested focus questions

### 1. Does `period_core.semantic_focus` exist?

- **Yes in the real runtime `build_period_core(...)` path.**
- **No in the current extraction script artifacts**, because the script still bypasses that path.

### 2. Is `semantic_focus.source == "life_chapter"` for high-confidence Tier-1 cases?

- **Yes in runtime** for:
  - Aries 3rd Saturn return + South Node overlap
  - Cancer 8th Saturn return
  - NN Aries / SN Libra nodal case
- **No visible proof in the current extraction script JSONs**, because they do not compute runtime `period_core.semantic_focus`.

### 3. Does period story debug include `semantic_focus`?

- **Yes in runtime**.
- In the current extraction script path it is only `{}` because `build_period_story(...)` receives `active_life_chapter` but not a computed `semantic_focus_result`.

### 4. Do `period_opening` / `mechanism` / `growth_edge` now show influence from selected meaning / meaning family / scene translation / handoff / suppressed readings?

- **Some influence, but weak and indirect.**
- The clearest change is that runtime `mechanism/growth_edge/what_it_builds` are no longer the exact old event-template lines.
- But the new prose still does **not** sound like a direct rendering of:
  - `selected_meaning`
  - `meaning_family`
  - `renderer_handoff.human_scene`
  - `renderer_handoff.core_contrast`
  - `suppressed_readings`

### 5. Are old generic openings still dominant?

- **Yes.**
- `period_opening` is still dominated by the generic:
  - `Asıl omurga burada yavaş ama kalıcı biçimde kuruluyor...`

### 6. Did public payload shape remain additive/safe?

- **Yes.**
- The new semantic ownership surface is additive:
  - `period_core.semantic_focus`
  - `_period_story_debug.semantic_focus`
- No broad top-level contract break was observed.

## Net conclusion

PR-SF1 succeeded at **semantic ownership wiring** in the real runtime path.

It did **not** yet succeed at **renderer realization**.

The biggest post-SF1 truth is now:

- upstream meaning ownership is visible
- `life_chapter` can win as the semantic owner
- but public prose still mostly sounds like policy/track fallback

So the next gap is no longer ownership plumbing. It is **renderer consumption quality**.

That points directly at a PR-4.1 style composer / renderer pass rather than another ownership-contract PR.
