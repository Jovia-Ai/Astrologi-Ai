# V26 Core Story — Downstream Consumer Audit (S2.1)

## Scope

Audit-only artifact for the V26 LIVE branch identified by the
previous trace (`v26_trace_audit.md`).

- No code changes.
- No runtime changes.
- No deletes.
- No refactor.

Target symbols / response fields:

- `build_core_story_plan(...)` writes `response["core_story_plan"]`
  (`natal_interpretation.py:2581`)
- `render_core_story(...)` writes `response["core_story"]`
  (`natal_interpretation.py:2589`)

Question this audit answers:

> Beyond `build_public_natal_view`, what consumes
> `response["core_story"]` and `response["core_story_plan"]` —
> backend, mobile, tests? Is the V26 LIVE branch
> RESCUE-as-is / CONSOLIDATE-into-Signature / DEPRECATE-with-mobile?

## Executive Verdict

**Both V26 LIVE fields have multiple confirmed downstream consumers,
including a direct mobile consumer.**

The V26 LIVE branch cannot be deleted without coordinated migration.
RESCUE-as-is keeps it but freezes dual-narrative-engine drift.
CONSOLIDATE-into-Signature is technically possible but requires
contract-preserving care to not break the `core_story` field
shape that mobile reads.

Recommendation per layer:

- `response["core_story"]` — **migration-with-contract-preservation
  required**: public field, mobile reads it, profile_v8 falls back to
  it. Cannot just disappear.
- `response["core_story_plan"]` — **migration possible without mobile
  coordination**: backend-only consumers (core_story_ui builder +
  data_quality payload).

## Consumer Tables

### `response["core_story"]` consumers

| Consumer | Type | Strength | Evidence |
|---|---|---|---|
| `public_builder.py` `core_story` field on `PublicNatalView` | backend / public-contract field | **strong (public contract)** | `public_builder.py:83-88` reads `response.get("core_story")`, humanizes via `humanize_natal_core_story_tr`, stores as `core_story` on PublicNatalView |
| `PublicNatalView` dataclass declares `core_story: Optional[str] = None` | backend / public schema | **strong (typed public field)** | `backend/app/natal/public_models.py:43` |
| `profile_v8_payload_builder.py` `identity_axis_body` fallback | backend / second public surface | **strong (used as fallback)** | `profile_v8_payload_builder.py:1749`: `str(core_story_ui.get("text") or response.get("core_story") or "").strip()`. If `core_story_ui.text` is missing, this V26-produced text fills `profile_v8.identity_axis.body` |
| `humanize_tr.py` dedicated "core_story" layer handling | backend / post-process | **medium (layer label)** | `humanize_tr.py:802, 834, 849` — special dedupe threshold (0.82 vs 0.84) and naturalize call when layer == "core_story". Layer label is passed in, doesn't directly depend on V26 function existing, but post-process expects this content shape |
| `narrative_contract_v2.py` defines "core_story" layer mapping | backend / contract definition | **medium (declared layer)** | `narrative_contract_v2.py:135` maps to "lived_experience + mechanism"; `:153` maps to "big_picture". "core_story" is a recognized layer in the v2 contract |
| **`mobile/lib/app/tabs/chart_lab_page.dart`** direct API read | **mobile / direct consumer** | **strong (live runtime consumer)** | Reads `pub['core_story']` on the `/interpret` path at lines 775-779 (primary fallback chain). Also referenced at 793 and 799 as one of several text sources in pick chains |
| Test fixture input | tests | **weak (only test input, not assertion)** | `test_natal_public_builder.py:101` feeds `"core_story": "Kisa test metni."` into the test response dict. No direct assertion on `public["core_story"]` shape/content found |

### `response["core_story_plan"]` consumers

| Consumer | Type | Strength | Evidence |
|---|---|---|---|
| `build_core_story_ui(...)` input | backend / feeds another builder | **strong (drives core_story_ui content)** | `natal_interpretation.py:2591` passes `response.get("core_story_plan") or {}` into `build_core_story_ui(...)`. So `core_story_plan` is the upstream input that drives the active-canonical `core_story_ui` builder |
| `_build_data_quality_payload(...)` input | backend / drives data_quality | **strong (drives data_quality)** | `natal_interpretation.py:2645` passes `response.get("core_story_plan") or {}` into `_build_data_quality_payload(...)`. Data-quality summary depends on the plan structure |
| Mobile direct reads | — | **none found** | No grep hits for `core_story_plan` / `coreStoryPlan` in `mobile/lib` |
| Test assertions | — | **none found** | No direct test assertion on `core_story_plan` content |

## Per-Consumer Evidence

### A. `build_public_natal_view` (public_builder.py)

`public_builder.py:83-88`:

```python
raw_core_story = response.get("core_story")
core_story = (
    humanize_natal_core_story_tr(str(raw_core_story))
    if isinstance(raw_core_story, str) and raw_core_story.strip()
    else raw_core_story
)
core_story_ui = _humanize_core_story_ui(response.get("core_story_ui"))
```

`core_story` then becomes `PublicNatalView.core_story` and is
emitted in the public payload. This is the canonical public-facing
exposure of the V26 output.

### B. `profile_v8_payload_builder.py` identity_axis fallback

`profile_v8_payload_builder.py:1749`:

```python
"identity_axis_body": str(core_story_ui.get("text") or response.get("core_story") or "").strip(),
```

If `core_story_ui.text` is empty, the V26-produced `core_story`
fills `profile_v8.identity_axis.body`. This is a real fallback
that does fire whenever `core_story_ui` is unavailable for any
reason (locale issue, builder failure, etc.).

### C. `humanize_tr.py` layer-specific behavior

`humanize_tr.py:802`:

```python
if layer == "core_story":
    ...
```

`humanize_tr.py:834`:

```python
cleaned = _semantic_dedupe(cleaned, threshold=0.82 if layer == "core_story" else 0.84)
```

`humanize_tr.py:849`:

```python
normalized = _naturalize_natal_longform(paragraph, max_sentences=4, layer="core_story")
```

The humanizer has dedicated logic for the `core_story` layer.
Removing the layer label would not break the humanizer (it has
default behavior) but would lose the V26-specific tuning.

### D. Mobile direct read (chart_lab_page.dart)

`mobile/lib/app/tabs/chart_lab_page.dart:773-779`:

```dart
if (path.startsWith('/interpret')) {
  final pub = data['public'];
  if (pub is Map && pub['core_story'] != null) {
    uiText = pub['core_story'].toString();
  } else if (data['core_story'] != null) {
    uiText = data['core_story'].toString();
  }
}
```

The mobile chart_lab page treats `core_story` as a primary text
source for the `/interpret` natal endpoint. A `null` here breaks
the lab display of the core narrative text. This is **the most
important constraint**: the field SHAPE must survive any migration.

Lines 793 and 799 also reference `pub['core_story']` in fallback
pick chains alongside `narrative_text`, `summary`, `text`. So
`core_story` is part of an OR-chain — if it's `null`, the chain
falls through to other fields. But "other fields" are not
guaranteed to exist either, so removing `core_story` would risk
empty display in lab.

### E. `core_story_plan` → `build_core_story_ui`

`natal_interpretation.py:2591`:

```python
response["core_story_ui"] = build_core_story_ui(
    response.get("core_story_plan") or {},
    ...
)
```

V26's `build_core_story_plan` writes `response["core_story_plan"]`,
which is then consumed by `build_core_story_ui(...)` (the
active-canonical core_story_ui builder per inventory §4.1).

**This is structurally significant**: it means `core_story_ui`
(active-canonical) is downstream of `core_story_plan` (V26 LIVE).
Migrating `build_core_story_plan` requires preserving the plan
schema that `build_core_story_ui` consumes.

### F. `core_story_plan` → `_build_data_quality_payload`

`natal_interpretation.py:2645`:

```python
response["data_quality"] = _build_data_quality_payload(
    response.get("core_story_plan") or {},
    ...
)
```

Second backend consumer of `core_story_plan`. Data-quality summary
depends on the plan structure.

## Mobile-Specific Findings

Three `core_story` references found in `mobile/lib`:

1. **`chart_lab_page.dart` — actual API consumer** (see §D above).
2. **`home_page_v2.dart:243-393` — DIFFERENT context**. References
   `periodCore.coreStory` which is the TRANSIT period_core's
   core_story field, not V26's natal `core_story`. Not a V26
   consumer; same field name, different source.
3. **`l10n/app_localizations*.dart`** — references `core_story_ui`
   (not `core_story`) in localization help text describing what
   fills the profile screen. Not a runtime consumer; static text
   only.

**Single mobile dependency**: `chart_lab_page.dart`. This is a
debug/lab surface, not the main natal user flow. That matters for
migration urgency:

- The main natal screens (`profile_page.dart`,
  `profile_detail_flow_page.dart`, etc.) consume `core_story_ui` +
  `profile_narrative` + `personality_imprint` + `insight_modules`
  per the l10n string; they do NOT directly read `core_story`.
- Only the lab/chart-inspection surface reads `core_story` directly.

This means migration impact on end-users is low (lab is internal /
power-user). But the field still must not be silently dropped
without coordinating with lab page.

## Test Findings

| Test | Reference | Type |
|---|---|---|
| `test_natal_public_builder.py:101` | sets `"core_story": "Kisa test metni."` in input response dict | test input only |
| `test_natal_public_builder.py:304-305` | asserts `public["core_story_ui"]["text"]` | asserts on `core_story_ui`, NOT `core_story` |
| `test_natal_summary_only.py:42-43` | asserts `public["core_story_ui"]["headline"]` / `["text"]` | asserts on `core_story_ui`, NOT `core_story` |
| `test_pr_d_v1_flag.py:61` | contains "core_story" in a list | context unclear, low signal |
| Several transit / period tests | reference TRANSIT period_core.core_story | different domain, not V26 |

**No direct natal test assertion on `public["core_story"]` content
or shape was found.** Test coverage protects `core_story_ui` (the
downstream-of-plan field) but not the V26-produced `core_story`
text itself. This is a coverage gap worth noting separately.

## Implication for Matrix §7.2a

The V26 LIVE branch (`build_core_story_plan` + `render_core_story`)
has three concrete downstream surfaces that cannot break:

1. **`PublicNatalView.core_story`** — public contract field, mobile-consumed
2. **`profile_v8.identity_axis_body`** (fallback)
3. **`core_story_ui` builder + `data_quality` payload** (both fed by `core_story_plan`)

This restricts the decision space:

| Option | Description | Cost | Risk |
|---|---|---|---|
| **A · RESCUE-as-is** | Keep V26 LIVE branch where it is. No structural migration. Accept dual-narrative-engine ownership permanently | Lowest | Drift / future readers re-discovering "wait, V26 is alive?" |
| **B · CONSOLIDATE-with-contract-preservation** | Re-home `build_core_story_plan` + `render_core_story` inside Signature renderer (4.4) or a dedicated consolidated module. Public response fields (`core_story` + `core_story_plan`) keep identical shape. Mobile contract unchanged. Internal owner shifts | Medium (refactor + test coverage gap closure) | Refactor risk; especially because no direct test asserts on `public["core_story"]` content (coverage gap) |
| **C · DEPRECATE-with-mobile-coordination** | Phase out the `core_story` field. Mobile `chart_lab_page.dart` migrates to `core_story_ui.text` (or another canonical field). Backend `profile_v8` fallback removed. Field marked deprecated, then removed. V26 LIVE branch can then DELETE | Highest (cross-stack coordination) | Mobile + backend release coordination; can be staged but slow |

This audit does NOT choose between A / B / C. The choice depends
on strategic preference (consolidation aggressiveness vs short-term
stability) that should be decided at the matrix level with full
context.

## Risk Notes

### Risk 1 · Coverage gap on `public["core_story"]`

No direct natal test asserts on the content or stability of
`public["core_story"]`. Any migration (B) or deprecation (C) carries
the risk of silently changing what's emitted, undetected by the
test suite. **Suggested mitigation**: add a baseline snapshot test
before any migration begins.

### Risk 2 · `core_story_plan` plan-schema coupling

`core_story_plan` is consumed by TWO downstream builders
(`core_story_ui` and `data_quality`). Any change to the plan
SHAPE (not just the function that produces it) ripples to both.
Migration must preserve plan schema or update both consumers
together.

### Risk 3 · `profile_v8.identity_axis_body` silent fallback

The `identity_axis_body` fallback to `response.get("core_story")`
is silent: there is no flag, log, or test asserting which source
fills it for which charts. If V26 LIVE branch is migrated and the
new producer changes content shape, the fallback could
intermittently swap which text the user sees in identity_axis_body
without any clear signal.

### Risk 4 · Mobile lab page coupling

`chart_lab_page.dart` is the only mobile direct read. It is a
debug surface, NOT the main user flow. So end-user impact of a
broken field is low. But the lab page is the main tool for
debugging natal output, so breaking it would worsen team
diagnostics — a workflow risk, not a user-facing risk.

## Recommendation

**Matrix §7.2a decision: B · CONSOLIDATE-with-contract-preservation**

Rationale:

- A leaves V26 alive as a parallel narrative engine indefinitely;
  doesn't help the consolidation goal.
- B preserves the public contract (mobile + profile_v8 + data
  quality all unaffected) while moving symbolic ownership into the
  consolidated stack.
- C is the cleanest end-state but requires coordinated mobile +
  backend release, longer timeline.

**Sequencing for B** (each step would be a separate bounded request):

1. **Pre-migration coverage**: add baseline snapshot tests on
   `public["core_story"]` content + shape for the existing 1996
   pilot chart (and possibly 2-3 other canonical charts). This
   closes the coverage gap identified in Risk 1 before any
   structural change.
2. **Define migration target**: decide whether `core_story` /
   `core_story_plan` move into Signature renderer (4.4) or into a
   dedicated `core_story_module.py` under the consolidated stack.
   This is a small design call, not yet code.
3. **Refactor in steps**: extract `render_core_story` and
   `build_core_story_plan` into the new home; route caller
   imports; preserve all output shapes byte-identical. Flag-gated
   if necessary.
4. **Delete V26 LIVE half**: after the new home is in place and
   tests pass, the old V26 LIVE symbols + their imports in natal
   route are removed. This collapses to S2.2 (V26 DEAD branch
   delete) and becomes a unified "V26 stack removed" milestone.

## Final Decision

Recommended Matrix §7.2a update:

- Replace "MIGRATE-callers-first — awaiting micro-audit" with
  "**CONSOLIDATE-with-contract-preservation**"
- Anchor consumers: `PublicNatalView.core_story` (mobile-consumed
  via `chart_lab_page.dart`), `profile_v8.identity_axis_body`
  fallback, `core_story_ui` + `data_quality` (both via
  `core_story_plan`)
- Migration prerequisite: snapshot test coverage on
  `public["core_story"]` content
- Mobile coordination: NOT required for option B (contract
  preserved); WOULD be required for option C (field deprecated)

This recommendation supersedes the prior "awaiting micro-audit"
state in matrix §7.2a.

## Next Action

Recommended next action:

- Update matrix §7.2a per the recommendation above
- Schedule **S2.2 (V26 DEAD branch delete)** independently — it
  is unaffected by this audit and can proceed in parallel
- After the matrix update, the next bounded request would be the
  pre-migration snapshot test coverage step (step 1 of B's
  sequencing), still audit/test territory, no production refactor
- Phase-4 work, ARC A2 §10.3, and tier architecture remain
  orthogonal — they are not gated on this consolidation
