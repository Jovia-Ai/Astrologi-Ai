# FREE-PROFILE-R3B — Read-Only Legacy Editorial Library Adapter TR v0.1

> Additive, dormant read-only adapter. No visible output change, no public/mobile
> change, no SHOU semantic selection, no legacy rewrite, no cross-family fallback,
> no LLM. Meaning ownership stays with the resolved placement key; the legacy
> library only supplies already-reviewed expression.

## 1. Starting commit

- Worktree: `/Users/sahradenizozdogan/.codex/worktrees/free-profile-r3b`
- Branch: `codex/free-profile-r3b-adapter`
- Started from integrated HEAD: `544a7a493a39952aaa1664f310c1cc06d592b79a`
- History at start: R3A (`544a7a4`) → R2 (`f2c14ae`) → foundation (`c12473a`). Began clean.

## 2. Canonical boundary

```text
resolved placement key → registry eligibility → exact legacy content asset → normalized expression
NEVER: legacy content → meaning selection
```

`ResolvedEditorialAsset.authority` is fixed to
`meaning_owner="external_resolved_key"`, `expression_owner="editorial_asset"`,
`selection_performed=false`. The adapter imports no SHOU selector/renderer and
performs no chart/cohort-dependent behavior.

## 3. Files changed (additive only)

- `backend/app/natal/editorial_profile/legacy_asset_contracts.py`
- `backend/app/natal/editorial_profile/legacy_library_adapter.py`
- `backend/app/natal/editorial_profile/legacy_source_readers.py`
- `backend/tests/natal/editorial_profile/test_legacy_library_adapter.py`
- `backend/docs/product/FREE_PROFILE_R3B_Read_Only_Legacy_Editorial_Library_Adapter_TR_v0_1.md`

No existing file modified (R3A `__init__.py` untouched; registry JSON unchanged —
no source-symbol correction was necessary).

## 4. Adapter-supported source families (9)

| reader family id | source module | symbol |
|---|---|---|
| PERSONALITY_IMPRINT_LIBRARY_TR_PRIORITY_HOUSES_V1 | contracts.py | exact |
| PERSONALITY_IMPRINT_LIBRARY_TR_SUPPORT_HOUSES_V1 | contracts.py | exact |
| PERSONALITY_IMPRINT_LIBRARY_TR_V3.{moon,mercury,venus,mars}_signs | sign_support_library.py | exact |
| PERSONALITY_IMPRINT_LIBRARY_TR_V4.{sun,jupiter,saturn}_signs | tone_support_library.py | exact |

Field normalization (verbatim content; only field names normalized):
`title←label_tr`, `summary←aura`, `body←drive`, `trait`, `shadow`,
`gift` (house only), `background_hint` (house only, ""→None).

**Logical-alias note (documented, no registry change):** registry assets #1
(`PERSONALITY_IMPRINT_LIBRARY_TR_V1`, `house_placements_and_aspects`) and #2
(`PERSONALITY_IMPRINT_LIBRARY_TR_V2`, `priority_house_bank`) are logical R2 family
names without a distinct literal symbol; the reader aliases them onto the concrete
priority-house bank for representative resolution. They are **not** canonical
per-key owners (priority/support keys are governed by the exact-match assets #3/#4),
so no key is double-governed and no content is borrowed across families.

## 5. Resolution governance

174 placement keys are governed (priority 50 + support 40 + 4 sign families ×12 +
3 tone families ×12). Per-key governance is single-valued: each key maps to exactly
one FREE_MODULAR_READY registry asset whose source symbol exactly matches the
reader family. Premium/supporting/duplicate/unsafe/missing assets govern **no**
placement keys.

## 6. Launch eligibility

Only `FREE_MODULAR_READY` resolves as launch-eligible Free. Blocked (diagnostic
only, never returned as success): `FREE_MODULAR_NEEDS_EDIT`,
`PREMIUM_SYNTHESIS_ONLY`, `SUPPORTING_COPY_ONLY`, `DUPLICATE_OR_SUPERSEDED`,
`UNSAFE_OR_UNSUPPORTED`, `MISSING_OWNER`.

Blocked-asset checks (via `resolve_asset(<registry family id>, tier=free, surface=identity)`):

| classification | result |
|---|---|
| PREMIUM_SYNTHESIS_ONLY | `CLASSIFICATION_NOT_LAUNCH_ELIGIBLE` |
| SUPPORTING_COPY_ONLY | `CLASSIFICATION_NOT_LAUNCH_ELIGIBLE` |
| FREE_MODULAR_NEEDS_EDIT | `CLASSIFICATION_NOT_LAUNCH_ELIGIBLE` |
| DUPLICATE_OR_SUPERSEDED | `CLASSIFICATION_NOT_LAUNCH_ELIGIBLE` |
| UNSAFE_OR_UNSUPPORTED | `CLASSIFICATION_NOT_LAUNCH_ELIGIBLE` |
| MISSING_OWNER | `UNKNOWN_OWNER` |

## 7. Successfully resolved Free-ready count

**11 / 11** Free-ready registry assets resolve a representative governed key
(no source-incomplete). `adapter_summary()`: 9 supported families, 174 governed
keys, `free_ready_resolved_count=11`.

## 8. Unresolved Free-ready assets and reasons

None. All 11 Free-ready assets resolve.

## 9. Fixture A/B resolution matrix

Tier `free`, surface `identity`.

### Fixture A

| key | result | registry owner | mode | title |
|---|---|---|---|---|
| sun_house_4 | RESOLVED | support_houses_v1 (#4) | single_card | Güneş 4. Ev |
| moon_gemini | RESOLVED | V3.moon_signs (#5) | single_card | Ay İkizler |
| mercury_virgo | RESOLVED | V3.mercury_signs (#6) | single_card | Merkür Başak |
| venus_virgo | RESOLVED | V3.venus_signs (#7) | single_card | Venüs Başak |
| mars_sagittarius | RESOLVED | V3.mars_signs (#8) | single_card | Mars Yay |

### Fixture B

| key | result | registry owner | mode | title / reason |
|---|---|---|---|---|
| sun_house_1 | RESOLVED | priority_houses_v1 (#3) | single_card | Güneş 1. Ev |
| sun_capricorn | RESOLVED | V4.sun_signs (#9) | single_card | Güneş Oğlak |
| moon_leo | RESOLVED | V3.moon_signs (#5) | single_card | Ay Aslan |
| moon_house_8 | RESOLVED | priority_houses_v1 (#3) | single_card | Ay 8. Ev |
| mercury_capricorn | RESOLVED | V3.mercury_signs (#6) | single_card | Merkür Oğlak |
| mercury_house_1 | RESOLVED | priority_houses_v1 (#3) | single_card | Merkür 1. Ev |
| venus_sagittarius | RESOLVED | V3.venus_signs (#7) | single_card | Venüs Yay |
| venus_house_12 | RESOLVED | priority_houses_v1 (#3) | single_card | Venüs 12. Ev |
| mars_virgo | RESOLVED | V3.mars_signs (#8) | single_card | Mars Başak |
| mars_house_9 | **FAILED** | — | — | `ASSET_NOT_FOUND` (key absent from libraries; no cross-fallback) |

`mars_house_9` is genuinely absent (mars houses present: 1,2,4,5,7,8,10,11,12).
The adapter returns a typed failure rather than borrowing another key's content.
Fixtures are diagnostic only; no production pins were added.

## 10. Tests and results

`pytest backend/tests/natal/editorial_profile` → **47 passed** (30 inherited R3A +
17 R3B). R3B proofs 1–15 plus tier and fixture-matrix checks:

1 exact-key only · 2 title/body from one asset · 3 legacy constants unmutated ·
4 blocked classes fail predictably · 5 unknown/unowned fails · 6 prohibited surface
fails (+ disallowed tier) · 7 Premium never Free · 8 missing content no cross-fallback ·
9 deterministic source hashes · 10 deterministic repeat · 11 two clean processes
identical · 12 no public/mobile importer · 13 no SHOU selection import ·
14 registry totals unchanged (25/11/3/1) · 15 all 11 Free-ready resolved-or-incomplete.

Direct registry validation remains: 25 checked, 0 errors.

## 11. No-visible-change proof

- `git diff --name-only` (tracked) empty: no existing production file modified.
- Registry JSON unchanged; R3A `__init__.py` unchanged.
- Adapter is dormant: no `app/` module imports `legacy_library_adapter` /
  `legacy_source_readers` (AST-checked in test 12).
- Adapter imports no SHOU selector/renderer, no `public_builder`, no mobile
  (AST-checked in test 13).
- Public payload, visible titles/bodies, card order, mobile output: unchanged
  (nothing imports the adapter; legacy constants are read-only).
- **Known base debt (not used as proof of success):** the inherited public snapshot
  suite is red on the base (`10 failed / 74 passed`) and is unrelated to this change.

## 12. Final worktree status

Clean after commit. Dirty files before commit limited to the four allowed groups
(adapter package files, focused test, report).

## 13. R3C scope (next)

Shadow card projection: map a resolved editorial asset to a non-public shadow card
contract (title/summary/body → card/slide fields) behind a dormant flag, with a
no-visible-change proof and no public payload attachment.

## Verdict

`PROCEED_TO_SHADOW_CARD_PROJECTION`
