# FREE-PROFILE-R3C — Internal Shadow Modular Card Projection TR v0.1

> Dormant internal projection. No visible output change, no public payload
> attachment, no API/mobile change, no SHOU selection, no new prose, no slide
> splitting, no LLM. Meaning ownership stays with the externally resolved key;
> expression ownership with the editorial asset; presentation with the shadow
> card contract.

## 1. Starting commit and history

- Worktree: `/Users/sahradenizozdogan/.codex/worktrees/free-profile-r3c`
- Branch: `codex/free-profile-r3c-shadow-card-projection`
- Started from: `9c9c446525f031ee35f0f9cc46fa1ebfdde3f619`, began clean.
- History: R3B (`9c9c446`) → R3A (`544a7a4`) → R2 (`f2c14ae`) → foundation (`c12473a`).

## 2. Files changed (additive only)

- `backend/app/natal/editorial_profile/shadow_card_contracts.py`
- `backend/app/natal/editorial_profile/shadow_card_projection.py`
- `backend/tests/natal/editorial_profile/test_shadow_card_projection.py`
- `backend/docs/product/FREE_PROFILE_R3C_Internal_Shadow_Modular_Card_Projection_TR_v0_1.md`

No existing file modified (registry, adapter, legacy libraries, `__init__.py` untouched).

## 3. Final shadow-card contract

`ShadowEditorialCard` (immutable): `card_id` (`free.shadow.<primary_key>`),
`projection_version` (`free_profile_shadow_card_v1`), `primary_key`, `asset_id`
(`editorial.<planet>.<rest>.tr.v1`), `domain`, `tier`, `surface`,
`ownership{meaning_owner=external_resolved_key, expression_owner=<placement asset_id>,
presentation_owner=shadow_card_contract, selection_performed=false,
ownership_status=aligned}`, `source{path, symbol_or_family, content_hash}`,
`content{title, summary, blocks[]}`, `presentation_intent{mode, allowed_roles,
min_slides, max_slides, slides_generated=false}`,
`diagnostics{fallback_used, alias_owner_used, missing_fields[], warnings[]}`.

Each block: `block_id`, `role`, `text` (verbatim), `source_field`, `launch_visibility`.

## 4. Field-to-role mapping

| legacy field | card field / block | role | launch_visibility |
|---|---|---|---|
| `label_tr` | content.title | — | — |
| `aura` | content.summary | — | — |
| `trait` | block `recognition` | recognition | eligible |
| `drive` | block `mechanism` | mechanism | eligible |
| `shadow` | block `tension` | tension | optional |
| `gift` | block `capacity` | capacity | optional |
| `background_hint` | block `origin` | origin | internal_only |

Text is copied verbatim; fields are never concatenated, rewritten or synthesized.
Empty fields become **absent blocks** (recorded in `diagnostics.missing_fields`),
not empty cards. `background_hint` is `internal_only` by default; `shadow`/`gift`
remain optional. No slides are generated (`slides_generated=false`).

## 5. Ownership invariants

For every successful card, `primary_key` == adapter-resolved key == the placement
key canonically governed by the resolved registry asset; title, summary and all
blocks are read from that single resolved asset. Enforced rejections:

| condition | failure |
|---|---|
| title/content from different assets (governance owner ≠ resolved owner) | `OWNERSHIP_MISMATCH` |
| supporting-copy / blocked classification requested | `ASSET_NOT_LAUNCH_ELIGIBLE` |
| Premium requested for Free | `ASSET_NOT_LAUNCH_ELIGIBLE` |
| unknown / missing-owner requested | `UNKNOWN_OWNER` |
| registry alias used as canonical owner | `ALIAS_NOT_CANONICAL_OWNER` |
| required title/primary body absent | `CONTENT_INCOMPLETE` |
| prohibited surface | `SURFACE_NOT_ALLOWED` |
| source hash differs from adapter | `SOURCE_HASH_MISMATCH` |
| key not resolvable / cross-family fallback would be required | `ASSET_NOT_FOUND` |

## 6. Alias policy

Registry logical assets `_V1` (`house_placements_and_aspects`) and `_V2`
(`priority_house_bank`) are audit-family representations only. They are never the
projected `asset_id`, primary content owner, title/body owner, or launch-visible
provenance. `_canonical_owner_check` rejects any resolved card whose registry owner
symbol is an alias. Canonical per-key ownership stays with the exact-match priority
(#3) / support (#4) house assets and the sign/tone families (#5–11). Verified by
`test_13_aliases_cannot_become_canonical_owners` (direct guard + crafted alias
owner rejected + no real card uses an alias symbol).

## 7. Free-ready corpus result (11/11)

| metric | value |
|---|---|
| projected | **11 / 11** |
| ownership aligned | 11 |
| alias-primary owners | 0 |
| cross-family fallback | 0 |
| Premium leakage | 0 |
| unknown-owner leakage | 0 |
| source-hash mismatch | 0 |
| with `trait` | 11 |
| with `drive` | 11 |
| with `shadow` | 11 |
| with `gift` | 4 |
| with `background_hint` | 0 (representatives carry empty `background_hint`) |
| missing optional (`background_hint`/`gift`) | 11 / 7 |
| presentation mode | single_card × 11 |

## 8. Fixture A matrix (tier free, surface identity)

| key | result | card_id | blocks |
|---|---|---|---|
| sun_house_4 | CARD | free.shadow.sun_house_4 | recognition, mechanism, tension, capacity |
| moon_gemini | CARD | free.shadow.moon_gemini | recognition, mechanism, tension |
| mercury_virgo | CARD | free.shadow.mercury_virgo | recognition, mechanism, tension |
| venus_virgo | CARD | free.shadow.venus_virgo | recognition, mechanism, tension |
| mars_sagittarius | CARD | free.shadow.mars_sagittarius | recognition, mechanism, tension |

5 cards, 5 aligned owners, no fallback, no alias owner, no synthesis, input order
preserved.

## 9. Fixture B matrix

| key | result |
|---|---|
| sun_house_1 | CARD (aligned) |
| sun_capricorn | CARD (aligned) |
| moon_leo | CARD (aligned) |
| moon_house_8 | CARD (aligned) |
| mercury_capricorn | CARD (aligned) |
| mercury_house_1 | CARD (aligned) |
| venus_sagittarius | CARD (aligned) |
| venus_house_12 | CARD (aligned) |
| mars_virgo | CARD (aligned) |
| mars_house_9 | **FAILURE `ASSET_NOT_FOUND`** |

9 cards; `mars_house_9` fails with no replacement/fallback.

## 10. `mars_house_9` coverage finding

`mars_house_9` is genuinely absent from the legacy libraries (mars houses present:
1, 2, 4, 5, 7, 8, 10, 11, 12). The projection records it as editorial coverage debt
(`summary.missing_coverage_keys = ("mars_house_9",)`) and returns a typed
`ASSET_NOT_FOUND`. No cross-family fallback, no production pin.

## 11. Deterministic serialization proof

`test_15` (repeated projection equal), `test_16` (two clean subprocesses produce
byte-identical serialized packets), input order preserved, duplicate keys
deterministically deduplicated with duplicates recorded.

## 12. Dormancy proof

- `git diff --name-only` (tracked) empty: no existing production file changed.
- `test_20`: AST scan proves no `app/` module imports `shadow_card_projection` /
  `shadow_card_contracts`; `public_builder.py`, API routes, mobile do not import it.
- `test_projection_does_not_import_shou_selection`: projection imports no SHOU
  selector/renderer, no `public_builder`, no mobile.
- Not attached to any public payload; current visible Profile behavior unchanged.
- **Known inherited red snapshot debt:** the public snapshot suite is red on the
  base (`10 failed / 74 passed`), unrelated to and unchanged by this scope — not
  claimed as introduced or fixed here.

## 13. Tests and results

`pytest backend/tests/natal/editorial_profile` → **69 passed** (30 R3A + 17 R3B +
22 R3C). R3C covers proofs J1–J20 plus the ownership-mismatch guard and the
no-SHOU-import check.

## 14. Next scope (R3D — Shadow Profile Parity Audit / Binding)

Compare the dormant shadow packet against the current visible Profile output for
the same explicit key set: prove structural parity (titles/blocks/order) without
binding, quantify editorial coverage debt (e.g. `mars_house_9`), and define the
exact, still-dormant binding contract — no public attachment, no selection.

## 15. Remaining dirty files

After commit: none. Pre-commit untracked limited to the three allowed groups
(projection package files, focused test, report).

## 16. Commit

Commit message: `FREE-PROFILE-R3C: add internal shadow modular card projection`
(hash in final response).

## Verdict

`PROCEED_TO_SHADOW_PROFILE_PARITY_AUDIT`
