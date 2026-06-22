# FREE-PROFILE-R4A — Narrow Editorial Profile Payload TR v0.1

> First scope that connects the canonical editorial registry/projection to the
> public payload — additively, behind a default-off flag, byte-identical when off.
> No SHOU selection, no Premium, no aspects, no cross-placement synthesis, no LLM.

## 1. Starting commit & worktree

- Branch: `codex/free-profile-r4-narrow-binding`
- Started from: `229599324269e52c06a12f4a714ecf9903425e9a` (R3D), began clean.
- History: R3D → R3C → R3B → R3A → R2 → foundation.
- Protected files (`public_builder.py`, `config.py`) verified unmodified vs `c12473a`
  before this scope. `config.py` is **not** modified by R4A.

## 2. Files changed

Additive (new):
- `backend/app/natal/editorial_profile/free_profile_plan_contracts.py`
- `backend/app/natal/editorial_profile/free_profile_plan_builder.py`
- `backend/app/natal/editorial_profile/free_profile_payload_contracts.py`
- `backend/app/natal/editorial_profile/free_profile_payload_builder.py`
- `backend/tests/natal/editorial_profile/test_free_profile_payload.py`
- `backend/docs/product/FREE_PROFILE_R4A_Narrow_Editorial_Profile_Payload_TR_v0_1.md`

Modified (minimal, additive):
- `backend/app/natal/public_builder.py` — one additive block at the return of
  `build_public_natal_view`: when `FREE_EDITORIAL_PROFILE_ENABLED` is on, attach
  `out["editorial_profile"]`. No existing field altered.
- `backend/tests/natal/editorial_profile/test_content_asset_registry_contract.py` —
  the R3A dormancy test is updated to allow the single sanctioned R4 importer
  (`public_builder.py`, flag-gated) and still forbid any other/mobile importer.

`config.py` and `public_models.py` untouched.

## 3. Feature flag

- Name: `FREE_EDITORIAL_PROFILE_ENABLED` (env flag, repo-standard `_env_enabled`
  pattern, same as `ENABLE_DYNAMIC_INSIGHTS` / `ENABLE_NATAL_PROMISE_PROJECTION_V1`).
- Default: **off**. Disabled mode produces a byte-identical legacy payload.

## 4. Canonical flow

```
natal planets facts (response["planets"], structured sign+house)
→ build_free_placement_plan (Sun,Moon,Mercury,Venus,Mars; sign then house; no rank/fallback)
→ project_shadow_card (registry eligibility → read-only adapter → ownership-safe card)
→ build_free_editorial_profile (omit unresolved; typed diagnostics; immutable)
→ build_public_natal_view (additive out["editorial_profile"] when flag on)
```

Free V1 semantic owner = the natal placement fact itself. Domains fixed:
Sun→identity, Moon→emotion, Mercury→mind, Venus→relationship, Mars→action.
Surface eligibility is checked as `identity` (the universal Free gate); the domain
is a separate fixed presentation bucket.

## 5. Fixture A result

10 requested, **10 resolved**, 0 missing, fallback=false. Order (sign then house):

| ord | domain | key | asset_id | title | chips |
|--|--|--|--|--|--|
| 0 | identity | sun_leo | editorial.sun.leo.tr.v1 | Güneş Aslan | Güneş · Aslan |
| 1 | identity | sun_house_4 | editorial.sun.house_4.tr.v1 | Güneş 4. Ev | Güneş · 4. Ev |
| 2 | emotion | moon_gemini | editorial.moon.gemini.tr.v1 | Ay İkizler | Ay · İkizler |
| 3 | emotion | moon_house_1 | editorial.moon.house_1.tr.v1 | Ay 1. Ev | Ay · 1. Ev |
| 4 | mind | mercury_virgo | editorial.mercury.virgo.tr.v1 | Merkür Başak | Merkür · Başak |
| 5 | mind | mercury_house_5 | editorial.mercury.house_5.tr.v1 | Merkür 5. Ev | Merkür · 5. Ev |
| 6 | relationship | venus_virgo | editorial.venus.virgo.tr.v1 | Venüs Başak | Venüs · Başak |
| 7 | relationship | venus_house_5 | editorial.venus.house_5.tr.v1 | Venüs 5. Ev | Venüs · 5. Ev |
| 8 | action | mars_sagittarius | editorial.mars.sagittarius.tr.v1 | Mars Yay | Mars · Yay |
| 9 | action | mars_house_7 | editorial.mars.house_7.tr.v1 | Mars 7. Ev | Mars · 7. Ev |

All chips sourced from the card's own `primary_key`; sign cards carry 3 blocks
(recognition/mechanism/tension), house cards 4 (+capacity); no background_hint.

## 6. Fixture B result

10 requested, **9 resolved**, 1 missing, fallback=false. `mars_house_9 →
ASSET_NOT_FOUND`; the action domain contains only `mars_virgo` (no substitute
house, no sign-copy borrow). Cards re-ordinalized 0..8 after the omission.

## 7. Ownership invariant counts

For both fixtures: title mismatch 0 · body mismatch 0 · chip mismatch 0 · proof
mismatch 0 · cross-family merge 0 · fallback 0 · duplicate surface assignment 0 ·
alias primary owner 0 · Premium leakage 0 · SHOU leakage 0. Every card:
`meaning_owner = natal_placement:<key>`, `expression_owner = <asset_id>`,
`status = aligned`.

## 8. Omitted-key diagnostics

Fixture A: none. Fixture B: `[{ "primary_key": "mars_house_9", "reason":
"ASSET_NOT_FOUND" }]`. No borrowing, no generic prose, no aspect/SHOU substitute.

## 9. Payload compatibility proof

- Flag default-off: `build_public_natal_view(...)` has no `editorial_profile` key.
- Disabled byte parity: repeated off-builds serialize identically; no new key.
- Enabled additive: with the flag on, every baseline key is unchanged and
  `editorial_profile` (10 cards for Fixture A) is added.
- Public-builder suite: **10 failed / 74 passed** with the flag off — identical to
  the base; this change introduces **no** new failure (the 10 are pre-existing base
  debt, unrelated to R4).

## 10. Tests & results

`pytest tests/natal/editorial_profile` → **86 passed** (69 inherited R3 + 17 R4A).
R4A covers L-backend 1–17 (plan, order, real-facts-not-text, exact resolution,
omission, no-fallback, ownership, chips, field mapping, no background_hint, flag
default-off, disabled parity, enabled additive, Fixture A, Fixture B, stable
serialization, no SHOU/Premium import).

## 11. Known remaining design debt

- Multi-slide visual system not built (R5).
- Aspect/dominant cards have no Free owner (intentionally excluded from Free V1).
- `mars_house_9` (and similarly absent houses) is editorial coverage debt.

## 12. Exact R5 structured-slide scope (preview)

Take the resolved `content_blocks` (recognition/mechanism/tension/capacity) and
define a structured slide contract (one role per slide, non-paged or a real
slide system), replacing the legacy `_splitBodyIntoSlides` per-sentence behavior.
No new prose; no SHOU. Word-budget + role-order acceptance.

## 13. Commit & dirty files

Commit: `FREE-PROFILE-R4A: project narrow editorial profile payload` (hash in
final response). After commit, remaining dirty files = the R4B mobile scope only.

## Verdict (backend slice)

Backend narrow editorial payload is ownership-clean and additive; proceed to R4B
mobile binding.
