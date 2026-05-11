| Item | Category | Status | Canonical? | Feeds | Used by | Notes |
|------|----------|--------|------------|-------|---------|-------|
| Natal public payload (`/interpret/ui -> public`) | core | implemented | yes | `natal_interpretation.py` + `natal/public_builder.py` | Profile, Home fallback, downstream adapters | Main structured natal output with `profile_v8`, `full_map_v8`, `sections_v2`, `supporting_threads`, `narrative_v2`. |
| Transit narrative payload (`/transit/narrative`) | core | implemented | yes | `transits.py` + `transit/present/public_builder.py` | Home, Calendar, Period detail | Supports `response_mode` + `payload_profile`; currently home/public_only can degrade to empty cards. |
| Synastry analyze payload (`/api/v1/relationship/synastry/analyze`) | core | implemented | yes | `services/synastry_analysis.py` + `synastry/public_builder.py` | Bond result page | Rich schema exists; artifacts show multiple historical schema variants. |
| Archetype profile payload (`/profile/archetype`) | core | implemented | yes | `natal/archetype_profile.py` | Profile archetype page + explainability | Includes `top_archetypes`, `why_this_not_that`, `slots`, confidence and adaptive question support. |
| Story backend route (`/api/story`) | partial | stale | no | `routers/story.py` + `services/stories.py` | Not primary surface | CRUD exists but generation is placeholder and not Story Studio’s source. |
| Story generation function | dead | stale | no | `story/generator.py` | No confirmed production consumer | Returns placeholder text only. |
| Story Studio surface data path | drift | implemented | no | `/interpret` + `personality_imprint` extraction | `story_studio_page.dart` | Surface is branded Story Studio but reads natal imprint, not story system. |
| Profile V8 backend payload builder | core | implemented | yes | `natal/profile_v8_payload_builder.py` | `natal/public_builder.py` -> mobile profile | Contrary to stale docs, builder is actively called. |
| Narrative V2 descriptor debug fields | support | implemented | unclear | `narrative_contract_v2.py` via `public_builder._build_narrative_v2` | Debug/audit views | Full descriptor fields emitted only when `include_debug=true`. |
| Supporting thread proof lines (`proof_raw`) | support | implemented | yes | `supporting_threads_builder.py` + `phrase_lib_tr_natal.py` | Profile sections and proof chips | Additive and covered by backend/mobile tests. |
| `proof_line` soft bridge | partial | emerging | unclear | voice spec intent | Not broadly rendered | Spec defines it; runtime emphasis remains mostly on `proof_raw`. |
| Home legacy page pipeline | support | implemented | no | `/transit/narrative` + forced fallback chain | `home_page.dart` | Heavy merge/fallback telemetry; robust but complex and duplicated with Home V2. |
| Home V2 pipeline | partial | emerging | unclear | `home_v2_providers.dart` + `/transit/narrative` public_only home + `/sky/now` + `/api/calculate-natal-chart` | `home_page_v2.dart` | Enabled in tab shell but still carries staged/mock comments/dev chips. |
| Charts legacy natal endpoint (`/api/calculate-natal-chart`) | drift | implemented | no | `routers/charts.py` | Home V2 natal provider | Uses older chart route and AI interpretation formatter path. |
| Home orchestrator endpoints (`/home/fast`, `/home/deep`) | support | implemented | unclear | `services/performance/home_orchestrator.py` | Potentially mobile/server integrations | Parallel home composition system not primary in observed mobile screens. |
| Transit public text normalization keys | support | implemented | yes | `transit/present/public_builder.py` | Mobile DTO parsing | Builder exposes both new and legacy copy keys for compatibility. |
| Mobile transit DTO remap layer | drift | duplicated | no | `narrative_dtos.dart` | Home/Calendar/Period renderers | Semantic remap (`essence<-big_picture/conflict`, `asks<-upper`) duplicates backend migration logic. |
| Explainability panel | support | implemented | yes | archetype fields (`why_this_not_that`, dignity, direction) | Profile archetype cards | Narrative-only surface; does not compute scores. |
| Voice spec docs (`voice_spec`, playbook, UX contract v3) | support | implemented | yes | docs | Editorial/content decisions | Defines target doctrine; not all fields/flows are fully runtime-aligned yet. |
| Runtime editorial policy module | support | implemented | yes | `editorial_render_policy.py` | Compaction/render helpers | Enforces anti-coaching/anti-cookbook checks and rewrite behavior. |
| Aila chat prompt system | support | implemented | no | `services/ai_chat.py` prompt + OpenAI responses | AI chat UI | Separate tone micro-system; not integrated with SHOU layer taxonomy. |
| Share-line l10n copy bank | support | implemented | unclear | `mobile/lib/l10n/app_*.arb` | Home hero, Story Studio close, Aila signature | Frontend-only share layer exists alongside backend share fields. |
| Artifact folders (`backend/tests/_artifacts`) | support | implemented | yes | tests/export scripts | Audit, regression, contract truth | Best truth source for real emitted payload shapes over docs/comments. |
| Fresh generated outputs (`docs/system/_generated_outputs`) | support | implemented | yes | local runtime captures | This audit | Confirms current payload structure snapshots for April 22, 2026. |
| Fresh regeneration path in this session | unknown | blocked | unclear | uvicorn + curl attempts | Audit validation | Environment-level startup/reachability constraints prevented new live reruns in-session. |

# 1. Executive summary
Confirmed: the repo has three mature astrology output pipelines (natal, transit, synastry) and one mature profile-archetype pipeline. The strongest contract in practice is endpoint-specific payloads (`/interpret/ui`, `/transit/narrative`, `/profile/archetype`, `/api/v1/relationship/synastry/analyze`) plus mobile adapters that further reshape them.

Confirmed: drift is concentrated in boundary layers, not core engines. The main drifts are (a) dual home systems (legacy + V2), (b) backend transit migration aliases plus additional mobile remap aliases, (c) Story Studio using natal imprint instead of story backend, and (d) stale docs still claiming components are inactive even though they are runtime-active.

Confirmed: artifact truth currently outranks docs/comments. Stored artifacts and fresh generated outputs show contract differences by endpoint/profile and show evolving schemas, especially in synastry and transit-home public-only behavior.

Inferred: without a canonical taxonomy and single adapter boundary per domain, new feature work will keep attaching at different layers (builder, route, mobile DTO, l10n copy), increasing semantic drift even when each local change is “correct”.

# 2. Canonical system map
1. Natal interpretation system (core): calculates chart + meaning layers + public profile payload.
Evidence: `backend/app/api/routes/natal_interpretation.py`, `backend/app/natal/public_builder.py`.

2. Transit narrative system (core): builds event/period narrative payloads with profile-specific shaping.
Evidence: `backend/app/api/routes/transits.py`, `backend/app/transit/present/public_builder.py`.

3. Synastry/bond system (core): computes compatibility/resonance plus narrative/public overlays.
Evidence: `backend/app/services/synastry_analysis.py`, `backend/app/synastry/public_builder.py`.

4. Archetype profile system (core): chart/test/context fusion to archetype ranking + explainability fields.
Evidence: `backend/app/api/routes/natal_interpretation.py` (`/profile/archetype`), `backend/app/natal/archetype_profile.py`.

5. Voice/editorial policy system (support): docs + runtime filters/humanizers + phrase libraries.
Evidence: `docs/voice/*`, `backend/app/narrative/editorial_render_policy.py`, `backend/app/narrative/gold_natal_tone.py`.

6. Surface adapter/render system (support/drift boundary): mobile DTO/adapters merge, fallback, and remap payloads.
Evidence: `mobile/lib/app/timing/narrative_dtos.dart`, `mobile/lib/app/profile/profile_v8_adapter.dart`, `mobile/lib/app/tabs/profile_page.dart`.

7. Home orchestration variants (partial/duplicated): legacy Home, Home V2, and backend `/home/fast|deep` orchestrator coexist.
Evidence: `mobile/lib/app/tabs/home_page.dart`, `mobile/lib/app/tabs/home_page_v2.dart`, `backend/app/services/performance/home_orchestrator.py`.

8. Story system (partial/drifted): `/api/story` CRUD and placeholder generator exist, but Story Studio source is natal imprint.
Evidence: `backend/app/routers/story.py`, `backend/app/story/generator.py`, `mobile/lib/app/tabs/story_studio_page.dart`.

9. Test/artifact truth system (canonical evidence): stored artifacts, fixtures, contract tests, and fresh snapshots.
Evidence: `backend/tests/_artifacts/*`, `backend/tests/test_*`, `mobile/test/*`, `docs/system/_generated_outputs/*`.

# 3. Core outputs
## 3.1 Natal Public Profile Output
Name: `public` payload from `POST /interpret/ui`.
Purpose: primary personal reading output for profile/home/story-adjacent surfaces.
Fed by: chart payload + phase2 fragments + sections/threads + profile narrative + V8 builder.
Shown on: Profile page (`/interpret/ui` + `/profile/fast` + fallback `/interpret` merge), legacy Home fallback, downstream adapters.
Current status: implemented, canonical, but surface adapters add additional transformation.
Evidence:
- Route and public assembly: `backend/app/api/routes/natal_interpretation.py:1183`, `backend/app/natal/public_builder.py:47`.
- Active V8 builder call: `backend/app/natal/public_builder.py:85`.
- Mobile consumption/merge: `mobile/lib/app/tabs/profile_page.dart:1966`, `mobile/lib/app/tabs/profile_page.dart:2049`.
- Fresh output keys: `docs/system/_generated_outputs/fresh_natal_interpret_ui_1996-12-28_07-10_istanbul.json`.

## 3.2 Transit Narrative Output
Name: payload from `POST /transit/narrative`.
Purpose: today/home/calendar/period cards and period-core narrative.
Fed by: transit narrative engines + public builder + route shaping (`payload_profile`, `response_mode`).
Shown on: Home (legacy and V2 providers), Calendar/Period views, period detail.
Current status: implemented, canonical, but home/public_only path can produce empty narrative cards.
Evidence:
- Route shaping: `backend/app/api/routes/transits.py:272`.
- `public_only` path: `backend/app/api/routes/transits.py:3025`.
- Empty/degraded fallback shape: `backend/app/api/routes/transits.py:360`, `backend/app/api/routes/transits.py:3095`.
- Mobile request path: `mobile/lib/app/timing/transit_repositories.dart:178`.
- Stored rich artifact: `backend/tests/_artifacts/transit_narrative_1996-12-28_07-10_istanbul_2026-03-04.json`.
- Fresh empty-home artifact: `docs/system/_generated_outputs/fresh_transit_narrative_public_only_home_2026-04-22.json`.

## 3.3 Synastry/Bond Output
Name: payload from `POST /api/v1/relationship/synastry/analyze` (alias `/api/synastry/analyze`).
Purpose: partner resonance scores, drivers, context, narrative and display lines.
Fed by: synastry engine + resonance/calibration + narrative/imprint builders + public overlay builder.
Shown on: Bond result page.
Current status: implemented, canonical backend path; artifact set shows schema evolution across files.
Evidence:
- Route: `backend/app/routers/synastry.py:24`.
- Public assembly keys: `backend/app/services/synastry_analysis.py:564`.
- Overlay/table/display wrapper: `backend/app/synastry/public_builder.py:237`.
- Mobile expectations: `mobile/lib/app/tabs/bond_result_page.dart:36`.
- Artifact shape drift: `backend/tests/_artifacts/synastry_*`.

## 3.4 Archetype Profile Output
Name: payload from `POST /profile/archetype`.
Purpose: archetype ranking, rationale/explainability fields, adaptive question extension.
Fed by: primitive chart scores + test/context scores + contradiction graph + taxonomy/fusion rules.
Shown on: Profile archetype experience page, explainability panel.
Current status: implemented, canonical.
Evidence:
- Endpoint and response shape: `backend/app/api/routes/natal_interpretation.py:918`.
- Top fields: `backend/app/api/routes/natal_interpretation.py:1032`.
- Surface fetch: `mobile/lib/app/tabs/profile_archetype_page.dart:84`.
- Explainability consumer: `mobile/lib/app/profile/explainability_panel.dart:98`.

## 3.5 AI Chat Output (Secondary Product Output)
Name: payload from `POST /v1/ai/chat`.
Purpose: Aila conversational response with quota/paywall context.
Fed by: OpenAI Responses API wrapper + quota service.
Shown on: AI chat page/service.
Current status: implemented, tone-isolated from main SHOU layer taxonomy.
Evidence:
- Prompt and service: `backend/app/services/ai_chat.py:18`.
- Endpoint: `backend/app/routers/chat.py:54`.
- Mobile client: `mobile/lib/app/ai/ai_chat_service.dart:61`.

# 4. Meaning layer taxonomy
## Confirmed layers in runtime payloads
- Recognition/hook layer: natal `core_story_ui.headline`; transit `headline/opening`.
Evidence: `backend/app/natal/public_builder.py`, `docs/narrative_v2_product_spec.md:38`.
- Mechanism layer: explicit in transit (`mechanism`) and implied in natal sections/threads.
Evidence: `backend/app/transit/present/public_builder.py`, fresh natal section sample in `docs/system/_generated_outputs/fresh_natal_interpret_ui_...json`.
- Shadow/risk layer: natal `shadow` narratives; transit `watchout` and legacy `shadow/conflict` aliases.
Evidence: `backend/app/transit/present/public_builder.py:123`, `mobile/lib/app/timing/narrative_dtos.dart:948`.
- Potential/build layer: transit `what_it_builds` / `upper_meaning`; natal growth-style framing in profile blocks.
Evidence: `docs/narrative_v2_product_spec.md:44`, `backend/app/transit/present/public_builder.py:797`.
- Proof layer: `proof_raw` (thread-level) broadly present; `proof_line` is spec-level but not broadly surfaced.
Evidence: `backend/app/natal/supporting_threads_builder.py:1825`, `docs/voice/voice_spec.md:529`, `mobile/test/profile_v8_adapter_proof_raw_test.dart`.
- Rationale/explainability layer: `why_this_not_that`, dignity and aspect-direction chips.
Evidence: `mobile/lib/app/profile/explainability_panel.dart:7`, `backend/app/natal/archetype_profile.py` (`_attach_why_this_not_that`).
- Share layer: backend `share_headline`/variants and frontend `share*` l10n keys coexist.
Evidence: `docs/voice/share_line_playbook.md`, `mobile/lib/l10n/app_tr.arb`.

## Canonical vs duplicate vs drifted
- Canonical: transit `headline/opening/essence/mechanism/asks/watchout/what_it_builds/technical_note` and period core fields.
Evidence: `docs/narrative_v2_product_spec.md:36`.
- Emerging: natal narrative_v2 8-slot taxonomy as product target.
Evidence: `docs/narrative_v2_product_spec.md:27`.
- Duplicate/drifted: mobile DTO remaps `big_picture/conflict/shadow/upper` into source-of-truth aliases.
Evidence: `mobile/lib/app/timing/narrative_dtos.dart:942`.
- Drifted: Story Studio “story meaning” is currently natal-imprint extraction.
Evidence: `mobile/lib/app/tabs/story_studio_page.dart:330`.

# 5. Surface map
## Home hero
Should live there: short today-facing line from transit daily card or share rotation fallback.
Currently lives there: Home V2 manifesto + provider data plus ARB share rotations (`shareHomeHeroRotation*`); legacy Home uses transit merge/fallback.
Mismatch: two home implementations and two copy sources (payload + l10n rotations) coexist without one canonical policy.
Evidence: `mobile/lib/app/tabs/home_page_v2.dart`, `mobile/lib/l10n/app_tr.arb`, `mobile/lib/app/tabs/home_page.dart:1757`.

## Today/home editorial surface
Should: one clear source (`/transit/narrative`, profile=home).
Current: legacy Home has forced calendar-day fallback and merge heuristics; Home V2 fetches public_only home directly.
Mismatch: same conceptual surface, different resolver logic and quality gates.
Evidence: `mobile/lib/app/tabs/home_page.dart:1810`, `mobile/lib/app/tabs/home_v2_providers.dart:105`.

## Profile top card
Should: `profile_v8.hero + identity_axis` canonical.
Current: Profile page merges `/interpret/ui`, `/profile/fast`, optional `/interpret` fallback and then adapts.
Mismatch: canonical source exists but merge order can mask which upstream source supplied final text.
Evidence: `mobile/lib/app/tabs/profile_page.dart:1966`, `mobile/lib/app/profile/profile_v8_adapter.dart:798`.

## Archetype card (closed)
Should: top archetype summary with clean rationale preview.
Current: `top_archetypes` plus explainability toggle data.
Mismatch: none major in contract; strong coupling to backend field naming.
Evidence: `backend/app/api/routes/natal_interpretation.py:1041`, `mobile/lib/app/profile/explainability_panel.dart:166`.

## Archetype detail
Should: full archetype profile and adaptive context.
Current: separate page calls `/profile/archetype?persist=true` and renders payload.
Mismatch: partial overlap with main profile page archetype summary path.
Evidence: `mobile/lib/app/tabs/profile_archetype_page.dart:84`, `mobile/lib/app/tabs/profile_page.dart:1893`.

## Story studio
Should: story-specific backend output.
Current: calls `/interpret`, extracts `personality_imprint` and renders story-like cards.
Mismatch: story surface is not backed by story backend domain.
Evidence: `mobile/lib/app/tabs/story_studio_page.dart:330`, `backend/app/routers/story.py:12`.

## Bond result
Should: synastry public schema with scores + narrative + display.
Current: consumes `scores/raw_scores/contextual_scores/drivers/resonance_scores/narrative_ready/narrative/synastry_imprint/display` with fallback-safe map parsing.
Mismatch: stored artifacts show multiple schema generations; needs single versioned contract.
Evidence: `mobile/lib/app/tabs/bond_result_page.dart:36`, `backend/tests/_artifacts/synastry_*`.

## Explainability panel
Should: rationale/proof layer only; no score recomputation.
Current: exactly narrative-only panel, computes labels/chips from provided fields.
Mismatch: none major; depends on field threading consistency.
Evidence: `mobile/lib/app/profile/explainability_panel.dart:7`.

## Aila/chat
Should: dedicated conversational tone, not mixed into natal/transit copy.
Current: separate prompt and quota system.
Mismatch: intentional split; no shared tone registry between chat and SHOU core docs.
Evidence: `backend/app/services/ai_chat.py:18`.

# 6. Voice and copy system
## Actual SHOU voice rules encoded
Confirmed in docs:
- Layer model (cause/mechanism/effect/shadow/potential), proof doctrine, share-line rules, naming aliases.
Evidence: `docs/voice/voice_spec.md`, `docs/voice/share_line_playbook.md`, `docs/voice/SHOU_BACKEND_UX_CONTRACT_v3.md`.

Confirmed in runtime policy code:
- Anti-coaching and anti-cookbook regex guards.
- Phrase cleanup/rewrite policy and rhythm-family selection.
Evidence: `backend/app/narrative/editorial_render_policy.py:44`, `backend/app/narrative/editorial_render_policy.py:231`.

Confirmed in tone reference:
- Gold natal tone and forbidden lexicon.
Evidence: `backend/app/narrative/gold_natal_tone.py:10`.

## Share/viral/copy layer on top
- Backend-oriented share field doctrine exists in docs.
- Frontend has independent share phrase bank in ARB keys for Home/Aila/StoryStudio close lines.
Evidence: `docs/voice/share_line_playbook.md`, `mobile/lib/l10n/app_tr.arb`.

## Consistency vs split
Consistent:
- `proof_raw` additive handling and empty-string invariant behavior are test-covered.
Evidence: `backend/tests/test_supporting_threads_proof_raw.py`, `mobile/test/profile_v8_adapter_proof_raw_test.dart`.

Split/drift:
- `proof_line` is documented but not a clearly established rendered layer across surfaces.
- Chat tone (`_CHAT_SYSTEM_PROMPT`) is separate from SHOU tone contracts.
- Some older/legacy payload fields continue to travel with alias semantics.
Evidence: `backend/app/services/ai_chat.py:18`, `mobile/lib/app/timing/narrative_dtos.dart:942`.

# 7. Artifact-backed truth
## Stored artifacts show historical-real contracts
1. Natal full debug artifact (`/interpret` style, no `public` wrapper):
`backend/tests/_artifacts/natal_interpret_full_1996-12-28_07-10_istanbul_user_compact_debug.json`.
Contains top-level keys like `core_story_ui`, `sections_v2`, `supporting_threads`, `phase2_snapshot`, `user_compact`.

2. Transit narrative artifact (`/transit/narrative` capture wrapper):
`backend/tests/_artifacts/transit_narrative_1996-12-28_07-10_istanbul_2026-03-04.json`.
Inside `response.public`: `event_cards` length 5 and populated `period_core` keys.

3. Transit raw artifacts:
- `backend/tests/_artifacts/transits_raw_1996-12-28_2026-02-28.json` -> `item_count: 81`.
- `backend/tests/_artifacts/transits_raw_1996-12-28_2026-03-04_istanbul.json` -> `item_count: 87`.
Shows raw unscored item delta over dates.

4. Synastry artifacts show schema evolution:
- minimal older shape (`display/drivers/formatted/meta/overlays/scores/tables`)
- newer enriched shape (`raw_scores/contextual_scores/narrative_ready/narrative/domain_rankings/...`).
Evidence: `backend/tests/_artifacts/synastry_*debug*.json`.

## Fresh outputs in this repo (April 22, 2026)
1. Natal fresh snapshot:
`docs/system/_generated_outputs/fresh_natal_interpret_ui_1996-12-28_07-10_istanbul.json`.
Contains `public.profile_v8`, `public.full_map_v8`, `public.narrative_v2`, `public.sections_v2`, `public.supporting_threads`.

2. Transit fresh home/public_only:
`docs/system/_generated_outputs/fresh_transit_narrative_public_only_home_2026-04-22.json`.
Observed: `event_cards=0`, `daily_event_cards=0`, `period_event_cards=0`, `period_core={}`, with only minimal `calendar.days` presence.

3. Transit fresh calendar_day/public_only:
`docs/system/_generated_outputs/fresh_transit_narrative_public_only_calendar_day_2026-04-22.json`.
Observed: empty public card sets and no `calendar` block in that capture.

## Fresh generation in this session
Confirmed attempts:
- Local server health + endpoint replay attempts were executed.
- In-session regeneration was blocked by environment constraints (localhost reachability and background startup restrictions including `nice(5)` permission issue in this shell context).
- Existing fresh files in `docs/system/_generated_outputs/` were used as current-code evidence.

# 8. Drift / duplication / dead paths
## Duplicate systems
1. Home delivery duplication:
- Legacy Home (`home_page.dart`) and Home V2 (`home_page_v2.dart`) are both active-level code paths while tab shell points to V2.
Evidence: `mobile/lib/app/tabs/tabs_shell.dart:24`, `mobile/lib/app/tabs/home_page.dart`, `mobile/lib/app/tabs/home_page_v2.dart`.

2. Transit semantic migration duplication:
- Backend public builder carries migration aliases; mobile DTO also remaps/aliases same semantics.
Evidence: `backend/app/transit/present/public_builder.py:123`, `mobile/lib/app/timing/narrative_dtos.dart:942`.

3. Profile aggregation duplication:
- Profile page combines `/interpret/ui` + `/profile/fast` + optional `/interpret` fallback.
Evidence: `mobile/lib/app/tabs/profile_page.dart:1966`.

## Overlapping / drifting schemas
1. Synastry artifact schema drift across versions (`debug`, `debug_current`, `debug_generated`).
Evidence: `backend/tests/_artifacts/synastry_*`.

2. Docs vs runtime contradiction:
- Some docs say `profile_v8_payload_builder.py` is unused; runtime calls it in `build_public_natal_view`.
Evidence: `docs/profile_v8_audit_and_roadmap.md:66` vs `backend/app/natal/public_builder.py:85`.

3. Narrative V2 product spec (8-slot target) vs runtime public payload default surface.
Evidence: `docs/narrative_v2_product_spec.md:27`, `backend/app/natal/public_builder.py:900`.

## Lossy DTOs/mappers
1. Transit card lossy aliasing in mobile (source fields collapsed into fallback synonyms).
Evidence: `mobile/lib/app/timing/narrative_dtos.dart:942-985`.

2. Profile thread extraction fallback produces synthetic entries with `proofRaw: ''` from `full_map_v8` path.
Evidence: `mobile/lib/app/tabs/profile_page.dart:3079`.

## Dead / partial branches
1. Story generation placeholder function.
Evidence: `backend/app/story/generator.py:7`.

2. `/api/story` exists but is not the Story Studio content path.
Evidence: `backend/app/routers/story.py:12`, `mobile/lib/app/tabs/story_studio_page.dart:330`.

3. Legacy chart route `/api/calculate-natal-chart` still feeds Home V2 natal snapshot while newer natal pipelines exist.
Evidence: `mobile/lib/app/tabs/home_v2_natal.dart:242`, `backend/app/routers/charts.py:98`.

## Surfaces using wrong/unclear layer
- Story Studio currently uses natal imprint layer instead of story-specific output layer.
- Home V2 comments still describe mock/staged intent while app shell selects V2 as active home page.
Evidence: `mobile/lib/app/tabs/story_studio_page.dart:312`, `mobile/lib/app/tabs/home_page_v2.dart:21`, `mobile/lib/app/tabs/tabs_shell.dart:59`.

# 9. Canonical future structure
## Proposed canonical taxonomy (single product taxonomy)
1. Domain facts layer (immutable-ish astro computation): chart data, raw transit items, synastry hits.
2. Meaning selection layer: selectors/scoring that choose salient structures (`aspect_bundle_selector`, transit selection buckets, synastry activation bundles).
3. Canonical narrative contract layer (domain-specific):
- `natal_public_v1`
- `transit_public_v1`
- `synastry_public_v1`
- `archetype_profile_v1`
Each contract must define required fields, optional support fields, and compatibility aliases.
4. Support metadata layer: proof (`proof_raw`/future `proof_line`), explainability (`why_this_not_that`, direction, dignity), trace/debug.
5. Share layer: share-line outputs (`share_line` + aliases), independent from core narrative fields.
6. Surface adapter layer: one adapter per surface family; adapters may format but may not redefine meaning semantics.
7. Presentation-only layer: UI typography, ARB-only fallback copy, animation.

## Attachment rule for future changes
Every change must declare exactly one target layer above and one contract owner file.
- If semantic meaning changes: modify layer 2 or 3.
- If phrase/tone changes only: layer 5 or runtime policy in layer 4.
- If UI rendering changes: layer 6/7 only.

# 10. Recommended work order
## Protect first (stabilize what is already solid)
1. Freeze canonical contract snapshots for `natal_public_v1`, `transit_public_v1`, `synastry_public_v1`, `archetype_profile_v1` using artifact tests.
2. Lock proof invariants (`proof_raw` non-null empty-string behavior) and transit source-of-truth mapping tests.

## Finish next (incomplete but strategically central)
3. Complete Home canonicalization: choose one primary home pipeline (V2 or legacy) and codify fallback policy in one place.
4. Define and enforce transit home/public_only minimum contract (non-empty guarantee policy or explicit empty contract semantics).
5. Finalize narrative_v2 public contract scope (what ships in non-debug) and align docs/spec to runtime.

## Merge after (remove duplicated semantics)
6. Consolidate transit semantic alias logic: backend should be single source for canonical+legacy mapping; mobile DTO should stop semantic reinterpretation.
7. Consolidate profile fetch layering: remove redundant `/interpret` fallback once `/interpret/ui` + `/profile/fast` coverage reaches contract guarantees.
8. Align Story Studio to a dedicated story output contract (or explicitly rename surface if it remains imprint-only).

## Postpone later (not on critical drift path)
9. Large tone refactors that do not change contract behavior.
10. Non-critical legacy route removal (`/api/calculate-natal-chart`, old story endpoints) only after migration observability confirms no active dependency.

# 11. Evidence appendix
## Key files
- Natal core: `backend/app/api/routes/natal_interpretation.py`, `backend/app/natal/public_builder.py`, `backend/app/natal/profile_v8_payload_builder.py`, `backend/app/natal/supporting_threads_builder.py`.
- Transit core: `backend/app/api/routes/transits.py`, `backend/app/transit/present/public_builder.py`, `backend/app/transit/narrative/*`.
- Synastry core: `backend/app/routers/synastry.py`, `backend/app/services/synastry_analysis.py`, `backend/app/synastry/public_builder.py`.
- Archetype: `backend/app/natal/archetype_profile.py`, `/profile/archetype` section in `natal_interpretation.py`.
- Voice/copy: `docs/voice/voice_spec.md`, `docs/voice/SHOU_BACKEND_UX_CONTRACT_v3.md`, `docs/voice/share_line_playbook.md`, `backend/app/narrative/editorial_render_policy.py`, `backend/app/narrative/gold_natal_tone.py`.
- Mobile adapters/surfaces: `mobile/lib/app/tabs/profile_page.dart`, `mobile/lib/app/profile/profile_v8_adapter.dart`, `mobile/lib/app/timing/narrative_dtos.dart`, `mobile/lib/app/tabs/home_page.dart`, `mobile/lib/app/tabs/home_page_v2.dart`, `mobile/lib/app/tabs/home_v2_providers.dart`, `mobile/lib/app/tabs/story_studio_page.dart`, `mobile/lib/app/tabs/bond_result_page.dart`, `mobile/lib/app/profile/explainability_panel.dart`.

## Key artifacts
- `backend/tests/_artifacts/natal_interpret_full_1996-12-28_07-10_istanbul_user_compact_debug.json`
- `backend/tests/_artifacts/natal_full_1996-12-28_07-10_istanbul.json`
- `backend/tests/_artifacts/transit_narrative_1996-12-28_07-10_istanbul_2026-03-04.json`
- `backend/tests/_artifacts/transits_raw_1996-12-28_2026-03-04_istanbul.json`
- `backend/tests/_artifacts/transits_raw_1996-12-28_2026-02-28.json`
- `backend/tests/_artifacts/synastry_1996-12-28_07-10_istanbul__1998-09-12_07-30_adana_debug_current.json`
- `backend/tests/_artifacts/synastry_1996-12-28_07-10_istanbul__1998-09-12_07-30_adana_debug_generated.json`

## Fresh outputs used
- `docs/system/_generated_outputs/fresh_natal_interpret_ui_1996-12-28_07-10_istanbul.json`
- `docs/system/_generated_outputs/fresh_transit_narrative_public_only_home_2026-04-22.json`
- `docs/system/_generated_outputs/fresh_transit_narrative_public_only_calendar_day_2026-04-22.json`

## Commands used (representative)
- Discovery: `rg --files ... | rg -i ...`, `find backend/tests ...`, `find mobile/test ...`.
- Contract tracing: `rg -n` against natal/transit/synastry routes and builders.
- Artifact inspection: `jq 'keys' ...`, `jq '.response.public ...' ...`.
- Fresh output checks: inspected `docs/system/_generated_outputs/*`; in-session rerun attempts via uvicorn+curl reported environment startup/reachability issues.

## Confirmed vs inferred marker
- Confirmed findings are anchored to code paths and/or artifact payloads listed above.
- Inferred findings are explicitly marked in sections 1 and 9 where behavior is derived from cross-system evidence rather than a single source.
