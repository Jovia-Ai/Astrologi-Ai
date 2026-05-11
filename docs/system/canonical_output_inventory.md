# Canonical Output Inventory

## Core systems
### 1) Natal Public Output System
Scope: `POST /interpret/ui` public payload, including `profile_v8`, `full_map_v8`, `sections_v2`, `supporting_threads`, `narrative_v2`.
Primary files:
- `backend/app/api/routes/natal_interpretation.py`
- `backend/app/natal/public_builder.py`
- `backend/app/natal/profile_v8_payload_builder.py`
- `backend/app/natal/supporting_threads_builder.py`
Key consumers:
- `mobile/lib/app/tabs/profile_page.dart`
- `mobile/lib/app/profile/profile_v8_adapter.dart`
Status: implemented, canonical.

### 2) Transit Narrative Output System
Scope: `POST /transit/narrative` with profile/mode shaping for home/calendar/period.
Primary files:
- `backend/app/api/routes/transits.py`
- `backend/app/transit/present/public_builder.py`
- `backend/app/transit/narrative/*`
Key consumers:
- `mobile/lib/app/timing/transit_repositories.dart`
- `mobile/lib/app/timing/narrative_dtos.dart`
- `mobile/lib/app/tabs/home_page.dart`
- `mobile/lib/app/tabs/home_v2_providers.dart`
Status: implemented, canonical contract; observed runtime degradation for home/public_only in fresh outputs.

### 3) Synastry/Bond Output System
Scope: `/api/v1/relationship/synastry/analyze` and alias endpoint.
Primary files:
- `backend/app/routers/synastry.py`
- `backend/app/services/synastry_analysis.py`
- `backend/app/synastry/public_builder.py`
Key consumers:
- `mobile/lib/app/tabs/bond_page.dart`
- `mobile/lib/app/tabs/bond_result_page.dart`
Status: implemented, canonical endpoint; schema evolution visible in artifacts.

### 4) Archetype Profile Output System
Scope: `/profile/archetype`, adaptive question flow, explainability fields.
Primary files:
- `backend/app/api/routes/natal_interpretation.py` (`/profile/archetype`)
- `backend/app/natal/archetype_profile.py`
- `backend/app/natal/archetype_question_bank.py`
Key consumers:
- `mobile/lib/app/tabs/profile_archetype_page.dart`
- `mobile/lib/app/profile/explainability_panel.dart`
Status: implemented, canonical.

## Supporting systems
### 1) Voice/editorial doctrine and runtime policy
Files:
- `docs/voice/voice_spec.md`
- `docs/voice/SHOU_BACKEND_UX_CONTRACT_v3.md`
- `docs/voice/share_line_playbook.md`
- `backend/app/narrative/editorial_render_policy.py`
- `backend/app/narrative/gold_natal_tone.py`
Status: implemented and active, but doc/runtime parity not complete.

### 2) Proof and explainability support
Files:
- `backend/app/natal/supporting_threads_builder.py`
- `backend/app/natal/narrative/phrase_lib_tr_natal.py`
- `mobile/lib/app/profile/explainability_panel.dart`
- `mobile/lib/app/profile/proof_chip.dart`
Status: implemented (`proof_raw` strong); `proof_line` still emerging.

### 3) Artifact and regression truth layer
Files:
- `backend/tests/_artifacts/*`
- `backend/tests/_fixtures/*`
- `backend/tests/test_natal_public_builder.py`
- `backend/tests/test_transit_narrative_public_payload.py`
- `backend/tests/test_supporting_threads_proof_raw.py`
- `mobile/test/transit_source_mapping_test.dart`
Status: implemented, canonical truth source for contracts.

### 4) Share-copy support layer
Files:
- `mobile/lib/l10n/app_tr.arb`
- `mobile/lib/l10n/app_en.arb`
- voice playbook docs above.
Status: implemented; split between backend-share doctrine and frontend-only static copy.

### 5) Home orchestrator support stack
Files:
- `backend/app/api/routes/home.py`
- `backend/app/services/performance/home_orchestrator.py`
Status: implemented; not primary observed mobile path in this audit.

### 6) Aila chat support stack
Files:
- `backend/app/routers/chat.py`
- `backend/app/services/ai_chat.py`
- `mobile/lib/app/ai/ai_chat_service.dart`
Status: implemented; separate tone system.

## Partial systems
### 1) Home V2 surface migration
Files:
- `mobile/lib/app/tabs/home_page_v2.dart`
- `mobile/lib/app/tabs/home_v2_providers.dart`
- `mobile/lib/app/tabs/tabs_shell.dart`
Status: emerging/partial (active shell flag + staged/mock commentary + dev chips).

### 2) Story system as dedicated domain
Files:
- `backend/app/routers/story.py`
- `backend/app/story/generator.py`
- `mobile/lib/app/tabs/story_studio_page.dart`
Status: partial/drifted (surface uses natal imprint, not story domain output).

### 3) Narrative V2 slot contract as shipped payload standard
Files:
- `docs/narrative_v2_product_spec.md`
- `backend/app/natal/public_builder.py` (`_build_narrative_v2`)
Status: emerging (descriptor exists; production non-debug fields are narrower than full spec intent).

## Dead / drifted systems
### 1) Story placeholder generator
File:
- `backend/app/story/generator.py`
Status: stale placeholder.

### 2) Stale docs claiming inactive V8 builder
Files:
- `docs/profile_v8_audit_and_roadmap.md` (claims unused)
- runtime contradictor: `backend/app/natal/public_builder.py` (active call)
Status: stale documentation branch.

### 3) Legacy chart endpoint dependency in modern Home V2
Files:
- `mobile/lib/app/tabs/home_v2_natal.dart` (`/api/calculate-natal-chart`)
- `backend/app/routers/charts.py`
Status: drift (legacy route still connected to a modern surface).

### 4) Semantic alias duplication across backend and mobile
Files:
- `backend/app/transit/present/public_builder.py`
- `mobile/lib/app/timing/narrative_dtos.dart`
Status: duplicated drift risk.

## Unresolved questions
1. Should Home V2 fully replace legacy Home now, or should legacy remain canonical until V2 parity checks pass?
Evidence: both `home_page.dart` and `home_page_v2.dart` remain active-level code paths.

2. Is empty `home/public_only` transit payload an intentional “no signal day” contract or a degraded path symptom for selected profiles/dates?
Evidence: fresh outputs in `docs/system/_generated_outputs/fresh_transit_narrative_public_only_home_2026-04-22.json` show empty cards while stored March artifact is rich.

3. Which synastry public schema version is canonical for frontend assumptions?
Evidence: artifact variants (`debug`, `debug_current`, `debug_generated`) have materially different key sets.

4. Should Story Studio continue as natal-imprint presentation, or migrate to a dedicated story output contract?
Evidence: `story_studio_page.dart` calls `/interpret`; `/api/story` exists separately.

5. Should transit semantic migration stay in backend only, with mobile DTO consuming canonical fields strictly?
Evidence: duplication in backend aliases + mobile fallback remaps.

6. Is `/home/fast` and `/home/deep` expected to be a long-term public contract or an internal/support path?
Evidence: orchestrator exists; primary mobile flow appears to use `/transit/narrative` directly.

## Reference captures used for this inventory
- Fresh captures: `docs/system/_generated_outputs/*.json`
- Stored truth set: `backend/tests/_artifacts/*.json`
- Working inventory source: `docs/system/_working_inventory.md`
