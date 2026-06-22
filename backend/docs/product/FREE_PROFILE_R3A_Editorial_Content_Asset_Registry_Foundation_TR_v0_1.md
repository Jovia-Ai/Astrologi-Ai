# FREE-PROFILE-R3A — Editorial Content Asset Registry Foundation TR v0.1

> Additive, dormant registry foundation. No visible output change, no runtime
> consumer attachment, no SHOU semantic-owner or renderer change, no mobile
> change, no LLM. The registry classifies reviewed editorial expression without
> granting it meaning authority.

## 1. Starting commit and clean worktree

- Branch: `codex/free-profile-r3a-content-asset-registry`
- Worktree: `/Users/sahradenizozdogan/.codex/worktrees/free-profile-r3a`
- Started from commit: **`c12473a70f027ecda0d5454de4ea21a76ce84a50`** (clean).
- Worktree began clean (`git status --short` empty at creation).

**Note on the "R2A commit" prerequisite.** No committed `R2A` (or `R2`) commit
exists in the repository. The R2 audit was produced but left **uncommitted** in
worktree `/Users/sahradenizozdogan/.codex/worktrees/free-profile-r2-audit`
(`codex/free-profile-r2-audit-wt`). Its own declared `starting_commit` is
`c12473a`. R3A therefore branches from `c12473a` (the R2 audit's clean base) and
converts the R2 inventory JSON as the source of truth. This substitution is
recorded here for transparency; the audited baseline counts are preserved 1:1.

## 2. Final contract

Immutable `EditorialContentAssetV1` (see
`backend/app/natal/editorial_profile/content_asset_contracts.py`). Representative
entry:

```json
{
  "asset_id": "editorial.personality_imprint_library_tr_priority_houses_v1.tr.v1",
  "registry_version": "free_profile_asset_registry_v1",
  "locale": "tr-TR",
  "version": "v1",
  "content_kind": "planet_house",
  "primary_key": "priority_house_bank",
  "domain": "identity",
  "source": {
    "path": "backend/app/natal/personality_imprint/contracts.py",
    "symbol_or_family": "PERSONALITY_IMPRINT_LIBRARY_TR_PRIORITY_HOUSES_V1",
    "content_hash": null
  },
  "authority": {
    "meaning_authority": "none",
    "expression_authority": "editorial_library",
    "presentation_authority": "asset_contract"
  },
  "classification": "FREE_MODULAR_READY",
  "is_primary_owner": true,
  "launch_eligible": true,
  "allowed_tiers": ["free"],
  "allowed_surfaces": ["identity", "first_felt"],
  "prohibited_surfaces": ["origin"],
  "presentation": {
    "mode": "single_card", "min_slides": 1, "max_slides": 1,
    "allowed_roles": ["recognition", "lived_pattern"]
  },
  "status": "reviewed",
  "supersedes": [],
  "notes": ["r2_content_kind=placement_library", "..."]
}
```

Authority separation enforced by the contract:

```text
Meaning authority      -> chart placement key / SHOU semantic owner   (registry: always "none")
Expression authority   -> reviewed editorial content asset            (editorial_library | supporting_copy | superseded | none)
Presentation authority -> declared card/slide contract                (asset_contract | none)
```

`content_kind` mapping (R2 taxonomy → task enum; original kept in `notes`):

| R2 content_kind | task content_kind |
|---|---|
| placement_library | planet_house |
| sign_placement_library | planet_sign |
| trigger_bundle, relationship_copy_bank, synthesis_projection | synthesis_narrative |
| section_rule_bank, editorial_template_bank, fallback_and_normalization_bank, reference_tables, microcopy_bank, projection_wrapper, presentation_copy, slide_contract_copy | supporting_copy |
| mobile_copy_fallback, placeholder_copy | mobile_fallback |

## 3. Registry file path

`backend/content/editorial/free_v1/content_asset_registry_tr_v1.json` (25 entries,
deterministic asset_id order, derived from
`backend/docs/product/data/FREE_PROFILE_R2_Content_Asset_Inventory_TR_v0_1.json`).

## 4. Classification counts (match audited baseline)

| classification | count |
|---|---|
| FREE_MODULAR_READY | 11 |
| PREMIUM_SYNTHESIS_ONLY | 3 |
| SUPPORTING_COPY_ONLY | 7 |
| FREE_MODULAR_NEEDS_EDIT | 1 |
| DUPLICATE_OR_SUPERSEDED | 1 |
| UNSAFE_OR_UNSUPPORTED | 1 |
| MISSING_OWNER (unknown/unowned) | 1 |
| **total classified** | **25** |

Free-ready: **11**. Premium-only: **3**. Unknown/unowned: **1**. Launch-eligible: **11**.

## 5. Slide-mode counts (match audited baseline)

| mode | count |
|---|---|
| single_card | 14 |
| multi_slide | 7 |
| long_read | 4 |

## 6. Unknown / unowned asset identity

- `asset_id`: `editorial.legacy_poster_copy.tr.v1`
- classification: `MISSING_OWNER`, status: `unresolved`
- source: `mobile/lib/app/tabs/profile_page.dart` (family: legacy poster copy)
- Kept explicitly unresolved: `launch_eligible=false`, `is_primary_owner=false`,
  `allowed_tiers=[]`. No owner was invented to make the count clean.

## 7. Validator invariants

`content_asset_validator.validate_assets(...)` rejects:

1. duplicate `asset_id`
2. duplicate canonical primary ownership for same tier/surface unless distinct `version`
3. `FREE_MODULAR_READY` without one primary key / primary ownership
4. Free asset with `meaning_authority != none`
5. `PREMIUM_SYNTHESIS_ONLY` that is Free-eligible
6. `MISSING_OWNER` / `UNKNOWN` marked launch-eligible
7. `single_card` with more than one slide
8. Free `multi_slide` with fewer than one or more than three slides
9. `long_read` marked launch-eligible (narrow Free launch)
10. overlapping allowed/prohibited surfaces
11. source paths that do not exist
12. SHOU renderer / internal-preview output declared Free editorial truth
13. mobile fallback / mock copy declared canonical meaning or primary owner
14. supporting-copy asset acting as primary owner

Clean registry result: `ok=True, errors=(), checked=25`.

## 8. Tests and results

`backend/tests/natal/editorial_profile/`:

- `test_content_asset_registry_contract.py` — load determinism, 25 families,
  classification + slide-mode counts, all source paths exist, free-ready surface
  eligibility, premium never-free, unknown stays blocked, zero semantic authority,
  no runtime/public/mobile import, stable serialization across two clean processes,
  dormant (no runtime importer).
- `test_content_asset_registry_validation.py` — one targeted rejection per
  invariant (1–14) plus the versioned-primary-owner allow case.

Result: **30 passed** (`pytest tests/natal/editorial_profile/ -q`).

## 9. No-visible-change proof

- `git diff --name-only` (tracked) is **empty**: no existing file modified.
- Registry is **dormant**: AST scan proves no runtime production module imports
  `editorial_profile` (the only `public_builder.py` match is the unrelated
  pre-existing function `_editorial_profile_title`).
- Public payload snapshot test under identical env, base vs R3A worktree:
  - base `c12473a`: `10 failed, 74 passed`
  - R3A worktree: `10 failed, 74 passed` (identical set; failures are pre-existing
    golden/snapshot drift on the base, unrelated to this change)
- SHOU remains internal-only; no public field, title, body, or card order changed;
  no mobile behavior changed.

## 10. Exact R3B (Legacy Library Adapter) scope

- Add a read-only adapter that, given a registry `asset_id` / `primary_key`,
  resolves the *referenced* legacy library symbol and returns its already-reviewed
  copy **without** the registry becoming a meaning owner.
- Adapter must: import the legacy library lazily; never mutate it; never select by
  chart state; never attach to public payload; compute and pin `source.content_hash`
  for drift detection.
- Out of scope for R3B: changing card selection/ordering, public_builder, mobile,
  SHOU owners/renderers, any visible output, LLM.
- Gate: adapter returns byte-identical legacy copy for all 11 Free-ready assets,
  with a content-hash drift test; still no runtime attachment.

## 11. Remaining dirty files

After commit: none (all new files committed; no untracked production files left).
Pre-commit untracked set was limited to the four allowed groups (package, registry
JSON, tests, report).

## 12. Commit

Commit message: `FREE-PROFILE-R3A: establish editorial content asset registry`
(hash recorded in the final response).

## Verdict

`PROCEED_TO_LEGACY_LIBRARY_ADAPTER`
