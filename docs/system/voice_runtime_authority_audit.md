# Voice Runtime Authority Audit

Date: 2026-05-03  
Scope: backend voice ownership audit before `SHOU_VOICE_VNEXT.md` migration work.  
Method: import graph + route trace + live runtime owners. No behavior changes.

## Goal

Bu audit'in işi hangi dokümanın daha güzel olduğuna karar vermek değil. Önce şunu netleştirir:

```text
Bugün runtime'da gerçekten kim konuşuyor?
Kim canonical authority adayı?
Kim renderer?
Kim legacy ama hâlâ canlı?
Kim sadece debug/shadow/fallback katmanı?
```

Bu katman netleşmeden `voice_doc_registry.yml`, `SHOU_VOICE_VNEXT.md` ve sample validation yanıltıcı olabilir.

## Authority Model

Bu audit boyunca şu statüler kullanılır:

- `canonical_authority`: yeni canonical mimaride korunacak reasoning/policy owner
- `renderer`: canonical state/policy'den metin çıkaran canlı render katmanı
- `legacy_compat`: hâlâ canlı ama gelecekte authority olmaması gereken katman
- `debug_shadow`: canlı akışta sadece debug/shadow/compat etkisi olan katman
- `fallback_only`: yalnız boşluk kapatan veya normalize eden yardımcı katman

## Route Trace

### Transit / period path

Current live path:

```text
/api/routes/transits.py
  -> daily_selection.select_daily_and_period_event_cards(...)
  -> daily_synthesis.build_daily_synthesis(...)
  -> today_story_candidate.build_today_story_candidate(...)
  -> deep_archetype_engine.build_event_card(...) / build_period_core(...)
  -> astrolog_narrative_engine.build_period_story(...)
  -> period_voice_policy.build_period_voice_policy(...)
  -> manifestation_context_policy.build_manifestation_context(...)
```

Observed live imports/calls:

- `transits.py` imports `generate_daily_from_event`, `humanize_event_card_tr`, `summarize_daily_micro_copy`, `build_daily_synthesis`, `select_daily_and_period_event_cards`, `build_today_story_candidate`, `tr_normalize_tree`
- `transits.py` writes `daily_synthesis["today_story_candidate"] = build_today_story_candidate(...)`
- `deep_archetype_engine.py` calls `build_period_story(PeriodStoryContext(...))`
- `deep_archetype_engine.py` still imports `voice_engine_tr.build_card_copy` and `text_quality_tr`

### Natal path

Current live path:

```text
/api/routes/natal_interpretation.py
  -> master_selector.build_master_natal_selector(...)
  -> public/profile builders
  -> profile_narrative_engine and related render branches
```

Observed live imports/calls:

- `natal_interpretation.py` imports `build_master_natal_selector`
- `master_selector_v1` is built in-route and passed into multiple builders
- `_master_selector_v1` is preserved in payload/debug flow
- `profile_narrative_engine.py` remains a live narrative owner in natal runtime

## Runtime Authority Table

### Period / transit / daily

| Path | Domain | Runtime role | Called by / entrypoint | Authority status | Notes |
|---|---|---|---|---|---|
| `backend/app/transit/narrative/period_voice_policy.py` | period | period-level voice policy | `today_story_candidate.py`, `astrolog_narrative_engine.py` | `canonical_authority` | Current owner for `spine_line + event_nature + meaning_intent + rhetorical_frame` decisions. |
| `backend/app/transit/narrative/manifestation_context_policy.py` | period/daily | life-scene context policy | `period_voice_policy.py` | `canonical_authority` | Owns house-to-life-scene resolution and technical leakage boundary. |
| `backend/app/transit/narrative/astrolog_narrative_engine.py` | period | canonical period renderer | `deep_archetype_engine.py` | `renderer` | Renders `build_period_story(...)` from policy/context; carries policy debug fields. |
| `backend/app/transit/narrative/today_story_candidate.py` | daily | canonical daily reasoning object builder | `transits.py` | `canonical_authority` | Daily story candidate authority; consumes period voice policy and trigger selection. |
| `backend/app/transit/narrative/daily_selection.py` | daily | trigger/support selector | `transits.py` | `canonical_authority` | Demoted from final story owner; still live as selection layer. |
| `backend/app/transit/narrative/daily_synthesis.py` | daily | daily synthesis assembler | `transits.py` | `renderer` | Still assembles daily output and now carries `today_story_candidate`. |
| `backend/app/transit/narrative/deep_archetype_engine.py` | period/event | orchestration bridge | transit narrative runtime | `renderer` | Still glues event cards, period core, and period story into payload slots. |
| `backend/app/transit/narrative/voice_engine_tr.py` | transit/event | legacy event card copy builder | `deep_archetype_engine.py` | `legacy_compat` | Live in event-card path; should not be treated as future semantic authority. |
| `backend/app/transit/narrative/daily_humanizer_tr.py` | daily/event | legacy daily/event humanizer | `transits.py`, `daily_selection.py` | `legacy_compat` | Still produces event-facing daily phrasing and preview text. |
| `backend/app/transit/narrative/text_quality_tr.py` | shared transit voice | normalization / rewrite support | `transits.py`, `deep_archetype_engine.py`, `astrolog_narrative_engine.py`, `content_loader.py`, `public_builder.py`, `archetype_engine.py` | `legacy_compat` | Broadly live. Useful quality layer, but not canonical meaning authority. |
| `backend/app/transit/narrative/chain_explainer_tr.py` | transit/event | event explanation helper | deep event-card chain | `legacy_compat` | Enrichment/helper role; not a top-level authority. |
| `backend/app/transit/present/public_builder.py` | transit public surface | public payload normalizer | transit public layer | `fallback_only` | Uses `text_quality_tr` normalization in presentational layer. |
| `backend/app/transit/interpret/content_loader.py` | transit interpret | content normalization bridge | interpret layer | `fallback_only` | Runtime-adjacent normalization only. |

### Natal

| Path | Domain | Runtime role | Called by / entrypoint | Authority status | Notes |
|---|---|---|---|---|---|
| `backend/app/natal/narrative/master_selector.py` | natal | spine/selector authority candidate | `natal_interpretation.py` | `canonical_authority` | Must stay in audit scope. Live selector data already flows through route and debug/public builders. |
| `backend/app/natal/narrative/profile_narrative_engine.py` | natal | legacy narrative renderer | natal route/public builders | `legacy_compat` | Still live and meaning-bearing, but should not define future source-of-truth. |
| `backend/app/natal/narrative/profile_narrative_engine_signature.py` | natal | signature narrative support | profile narrative engine | `legacy_compat` | Narrative helper in old branch family. |
| `backend/app/natal/narrative/voice_profile_resolver.py` | natal/shared voice | tone/voice calibration helper | natal narrative runtime | `debug_shadow` | Voice calibration support, not a semantic authority. |
| `backend/app/natal/personality_imprint/tone_support_library.py` | natal/shared voice | tone support library | natal narrative runtime | `debug_shadow` | Still useful as support copy/tone material, not authority. |

### Shared editorial / style

| Path | Domain | Runtime role | Called by / entrypoint | Authority status | Notes |
|---|---|---|---|---|---|
| `backend/app/narrative/editorial_render_policy.py` | shared | editorial rendering policy | multiple narrative surfaces | `debug_shadow` | Shared editorial contract reference; not period/daily canonical owner. |
| `backend/app/narrative/style_packs/tr_v26.py` | shared | style pack | shared narrative runtime | `fallback_only` | Style/tone pack, not meaning source. |
| `backend/app/style/style_pack_v26_tr.py` | shared | style/tone pack | shared runtime | `fallback_only` | Same class as above; presentation support. |
| `backend/app/engine/tone_profile.py` | shared | tone profile meta | shared runtime | `fallback_only` | Voice calibration support only. |
| `backend/app/engine/tone_apply.py` | shared | tone applier | shared runtime | `fallback_only` | Output shaping support only. |

## Primary Findings

### 1. Period voice already has a canonical policy split

The current strongest canonical candidates are:

- `period_voice_policy.py`
- `manifestation_context_policy.py`
- `today_story_candidate.py`

These files already encode the new separation:

```text
reasoning decides meaning
policy decides how it should be said
renderer writes
```

### 2. Period rendering is canonical-ish, but event voice is still mixed

`astrolog_narrative_engine.py` is now the main period-story renderer, but `deep_archetype_engine.py` still routes through older event-card copy layers such as:

- `voice_engine_tr.py`
- `text_quality_tr.py`

So period voice is closer to canonical than event-card voice.

### 3. Daily is in transition, not fully canonical yet

Daily now has:

- `today_story_candidate.py`
- demoted `daily_selection.py`
- `daily_synthesis.py`

But the live route still imports and uses:

- `daily_humanizer_tr.py`
- legacy previews/micro summaries

So daily is currently a mixed authority system:

```text
canonical story candidate
+ legacy humanizer/render helpers
```

### 4. Natal still has a live selector authority that migration must not ignore

`master_selector.py` is not optional audit context. It is a live runtime owner in natal route flow and already shapes how identity/spine lines are selected and propagated.

If voice migration ignores `master_selector.py`, later natal/daily/period alignment will drift.

### 5. `text_quality_tr.py` is still deeply embedded

`text_quality_tr.py` appears in:

- `transits.py`
- `deep_archetype_engine.py`
- `astrolog_narrative_engine.py`
- `content_loader.py`
- `public_builder.py`
- `archetype_engine.py`

That makes it a live compatibility layer, not dead code. It should be demoted in authority, not assumed removable.

## Migration Implications

### Canonical runtime owners to align first

- `backend/app/transit/narrative/period_voice_policy.py`
- `backend/app/transit/narrative/manifestation_context_policy.py`
- `backend/app/transit/narrative/today_story_candidate.py`
- `backend/app/transit/narrative/daily_selection.py`
- `backend/app/transit/narrative/astrolog_narrative_engine.py`
- `backend/app/natal/narrative/master_selector.py`

### Live legacy owners that must be registry-marked before cleanup

- `backend/app/transit/narrative/voice_engine_tr.py`
- `backend/app/transit/narrative/daily_humanizer_tr.py`
- `backend/app/transit/narrative/text_quality_tr.py`
- `backend/app/natal/narrative/profile_narrative_engine.py`

### Immediate next artifacts

This audit is intended to feed:

- `docs/voice/voice_doc_registry.yml`
- `docs/voice/SHOU_VOICE_VNEXT.md`

## PR Sequencing Note

Recommended migration order:

1. `PR-0 Runtime Authority Audit`
2. `PR-1 Voice Docs Registry`
3. `PR-2 SHOU Voice vNext Spec + Lint Tests`
4. `PR-2v Sample Validation`
5. `PR-3 Runtime Alignment Plan`
6. `PR-4 Migration & Cleanup`
7. `PR-5 Daily Today-ness Signal`

`PR-5`'ten sonraki roadmap: `Daily Manifestation Context Consumption`, `Daily Canonical Renderer`. Bu audit foundation katmanını kapsar; daily feature work `PR-5` ile başlar.
