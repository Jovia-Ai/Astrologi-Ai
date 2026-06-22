# FREE-PROFILE-R4C — Default-Off Host Wiring & Manual Visual Validation Handoff TR v0.1

> Bounded host wiring + diagnostics + tests. No structured-slide work, no visual
> redesign, no editorial-copy change, no SHOU/Premium/Tam Okuma, legacy path kept.

## 1. Starting commit & worktree

- Branch: `codex/free-profile-r4c-host-wiring`
- Started from: `a9f8fc1246d0bd9914f329e2a40d905034142c8b` (R4B), began clean.
- History: R4B → R4A → R3D → …
- Protected files (`app_router.dart`, `main.dart`, `config.py`, `public_models.py`)
  verified unmodified vs `c12473a` before and after this scope.

## 2. Exact host wiring point

- File: `mobile/lib/app/tabs/profile_page.dart`
- Function: `_ProfilePageState.build` → the `_segmentIndex == 0` content branch.
- One explicit, flag-gated branch:
  ```dart
  final freeEditorialDecision = decideFreeEditorialHost(
    flagEnabled: kFreeEditorialProfileEnabled,
    payload: _activeProfilePayload,
  );
  // segment 0:
  freeEditorialDecision.showNarrow
    ? FreeEditorialProfileView(profile: freeEditorialDecision.model)
    : <existing ProfileV8SectionsView / legacyContentView expression>
  ```
- Decision logic lives in the pure, testable seam
  `mobile/lib/app/profile/free_editorial_profile_host.dart`
  (`decideFreeEditorialHost`). Narrow content is **never** routed through
  `ProfileV8Adapter`, legacy poster selection, supporting threads, or aura.

## 3. Files changed

New:
- `mobile/lib/app/profile/free_editorial_profile_host.dart`
- `mobile/test/free_editorial_profile_host_test.dart`
- `backend/docs/product/data/FREE_PROFILE_R4C_Manual_Visual_Validation_Checklist_TR_v0_1.json`
- `backend/docs/product/FREE_PROFILE_R4C_Default_Off_Host_Wiring_And_Manual_Visual_Validation_Handoff_TR_v0_1.md`

Modified (additive, one branch):
- `mobile/lib/app/tabs/profile_page.dart` — 3 imports + the gated branch. No
  existing legacy selection changed when the flag is off; no legacy payload
  mutated; no blending of narrow and legacy components.

## 4. Flag names

- Backend: `FREE_EDITORIAL_PROFILE_ENABLED=1` (env, `_env_enabled`; default off).
- Mobile: `--dart-define=FREE_EDITORIAL_PROFILE_ENABLED=true`
  (`kFreeEditorialProfileEnabled = bool.fromEnvironment(...)`; default false).

## 5. Fallback policy (§D)

| condition | host behavior | reason code |
|---|---|---|
| flag off | existing legacy Profile (byte/widget-equivalent) | EDITORIAL_FLAG_MISMATCH |
| flag on + no `editorial_profile` | legacy fallback (production-safe) | EDITORIAL_PAYLOAD_ABSENT |
| flag on + malformed payload | legacy fallback | EDITORIAL_PAYLOAD_INVALID |
| flag on + valid shape, 0 cards | legacy fallback | EDITORIAL_CARDS_EMPTY |
| flag on + valid cards | FreeEditorialProfileView | EDITORIAL_SHOW |

The reason is internal diagnostics only and never masquerades as user content. No
empty premium-looking page, no mock content, no silent legacy/narrow blending.

## 6. Profile / user isolation proof

- The narrow model derives ONLY from `_activeProfilePayload` (the signed-in user's
  loaded natal payload), which is fully replaced on each natal load
  (`profile_page.dart:2180`) and nulled on error/profile-change
  (`profile_page.dart:2219`). No separate cache holds narrow cards.
- Therefore switching profiles or recalculating a chart cannot preserve the
  previous user's narrow cards (proven by tests 6 and 7: changing the payload
  changes the card set; nulling it yields the empty/absent state).
- No Fixture A/B production pins, no hard-coded planet keys, no demo-chart
  substitution, no generic cards on miss (verified: `decideFreeEditorialHost`
  reads only `editorial_profile`; the view/adapter never synthesize).

## 7. Tests & analyzer

- `flutter test test/free_editorial_profile_host_test.dart
  test/free_editorial_profile_test.dart` → **All tests passed (11 host + 24
  R4B)**. Host tests cover §E 1–11 (flag off preserves path; flag on+valid opens
  narrow; absent→no mock; mutual exclusivity; backend order; profile-change
  replaces set; stale not retained; malformed→safe state; no Koruyucu dalga; no
  ProfileV8/supporting-thread consult; no Tam Okuma).
- `flutter analyze` on all changed Dart files (host, adapter, view, profile_page,
  both tests) → **No issues found!** (§E.12).

## 8. Deferred-capture checklist

`backend/docs/product/data/FREE_PROFILE_R4C_Manual_Visual_Validation_Checklist_TR_v0_1.json`
— 9 captures, all `DEFERRED_REQUIRES_FULL_APP_RUNTIME`, with expected keys and
empty `actual_keys`/`acceptance_checks` until a real runtime capture is recorded.

## 9. Manual run instructions

Backend (with flag), repo start command from `render.yaml`:
```bash
FREE_EDITORIAL_PROFILE_ENABLED=1 \
  PYTHONPATH=backend python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```
Mobile (from `mobile/`):
```bash
flutter run --dart-define=FREE_EDITORIAL_PROFILE_ENABLED=true
```
Sign in as the Fixture A user, open the Profile tab → narrow surface. Capture the
9 filenames in §G; for Fixture B confirm the action domain shows only Mars Başak
(`mars_house_9 → ASSET_NOT_FOUND`, no substitute). Verify all per-capture checks.

## 10. Known visual debt

- Detail is non-paged structured (final multi-slide visual system is R5).
- Aura badge (`Koruyucu dalga`) remains in the legacy path (out of scope here);
  it does not render in the narrow path.
- Aspect/dominant cards and absent houses remain out of Free V1.

## 11. R5 entry gate

R5 (`PROCEED_TO_STRUCTURED_SLIDE_AND_VISUAL_POLISH`) may begin only after all nine
captures are completed and reviewed against the checklist. Until then the verdict
is `PROCEED_TO_MANUAL_VISUAL_VALIDATION`.

## 12. Commit & dirty files

Commit: `FREE-PROFILE-R4C: wire narrow editorial profile behind flag` (hash in
final response). After commit: clean.

## Verdict

`PROCEED_TO_MANUAL_VISUAL_VALIDATION`
