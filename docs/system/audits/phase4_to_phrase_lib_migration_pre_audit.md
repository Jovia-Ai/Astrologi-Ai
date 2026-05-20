# S4 Pre-Audit — Phase-4 hidden/private → `phrase_lib_tr_profile` migration anatomy

## Scope

Trace + design-anatomy audit. No code. No structural change.

Inputs:
- `backend/app/natal/narrative/phrase_lib_tr_profile.py` (387 lines)
- `backend/app/meaning/composed_detail_renderer.py` Phase-4 slide builder

Question this audit answers:

> Matrix §5.2 says Phase-4 hidden/private slide templates migrate
> into `phrase_lib_tr_profile.BODY_TEMPLATES_TR` as a hidden/private
> family entry. Does that shape actually fit? What are the real
> options? What does S4 design need to choose between?

## Executive verdict

**The matrix §5.2 phrasing oversimplifies the contract gap.** The two
sides emit at different granularities and use different parameter
vocabularies. A direct drop-in into `BODY_TEMPLATES_TR` does NOT
fit cleanly. Four real options exist; S4 should choose between them
explicitly.

**Recommendation: phased migration — Option D first (smallest API
impact, real consolidation), Option C as long-term end-state.**

## Contract A — `render_block_template` (the frame engine)

`phrase_lib_tr_profile.py`:

- **Output**: ONE block per call
  ```
  {headline, teaser, body, micro, mode, mode_label,
   template_index, title_index, quality_issues, opening_key}
  ```
- **Parameterization**: `block_id` (domain-like: `identity_aura`,
  `mind_voice`, `drive_rhythm`, `love_depth`, `career_visibility`,
  `home_roots`, `luck_creation`) + `mode` ∈ A/B/C/D
  (stylistic: direct/observational/cinematic/intimate)
- **Slot vocabulary**: `{copy.core}`, `{copy.mechanism}`,
  `{copy.shadow}`, `{copy.gift}` (+ teaser, micro at block level)
- **Variation axis**: stylistic — same domain, 4 voice modes
- **Title** comes from `TITLE_FAMILIES_TR[block_id]` (one per block)

## Contract B — Phase-4 deep_read slide builder

`composed_detail_renderer.py` `_build_relationship_hidden_private_love_phase4_deep_read_slides`:

- **Output**: FIVE slides per call (a slide flow)
  ```
  [{id, title, body}, {id, title, body}, ...] × 5
  ```
- **Parameterization**: `source_id` only — the 5 slides are
  hand-authored prose with per-rhythm cadence baked in
- **Per-slide structure**: each slide is a different *surface_role
  beat* in the deep_read profile:
  `private_scene → hidden_mechanism → protective_pattern →
   gift_in_silence → safe_visibility`
- **Variation axis**: semantic — different beats in the slide flow,
  not stylistic variants of the same beat
- **No teaser/micro at slide level** — the parent card holds
  teaser; slides carry only `{id, title, body}`

## The gap

| Axis | render_block_template | Phase-4 builder |
|---|---|---|
| Emission granularity | one block | five slides |
| block_id semantics | domain (love_depth, mind_voice) | n/a (single function) |
| Variation parameter | mode A/B/C/D (stylistic) | surface_role (semantic beat) |
| Slot vocabulary | `{copy.core/mechanism/shadow/gift}` | free-form TR prose |
| Title source | TITLE_FAMILIES_TR[block_id] | hand-authored per slide |
| Per-emission fields | headline+teaser+body+micro+meta | id+title+body |

This is a **model mismatch**, not a cosmetic difference. Matrix §5.2's
phrasing ("migrate into `BODY_TEMPLATES_TR` as a hidden/private family
entry") implies a one-row drop-in. The actual shapes don't allow that.

## Four real options

### Option A — 5 new `block_id` entries (loop pattern)

Add `private_scene`, `hidden_mechanism`, `protective_pattern`,
`gift_in_silence`, `safe_visibility` as new top-level entries in:
- `TITLE_FAMILIES_TR`
- `BODY_TEMPLATES_TR` (the 4 A/B/C/D modes per block)
- `SOFT_ASTRO_HINTS_TR`
- `DEFAULT_PUBLIC_CHIPS_TR`

Phase-4 adapter calls `render_block_template` 5 times in a loop,
collects results into `slides[]`.

- **Pros**: reuses existing machinery; symbol-level consolidation
- **Cons**: conflates *domain block_ids* (love_depth, mind_voice) with
  *surface_role beats* (private_scene, hidden_mechanism) — one
  taxonomy, two semantically different roots. Future readers
  will struggle to tell which is which. Also: the A/B/C/D stylistic
  modes don't naturally map to the surface-role-beat axis Phase-4
  uses (rhythm modulation per beat, not stylistic variant per chart)

### Option B — Extend `render_block_template` to multi-block sequences

Change `render_block_template` signature to accept a `Sequence[str]`
of block_ids and emit a list of payloads.

- **Pros**: single entry point
- **Cons**: API change → breaks signature narrative renderer's
  current call pattern (line 1792 calls it for single blocks); risk
  cascades into matrix §4.4 RESCUE assumption

### Option C — New `render_slide_flow` parallel to `render_block_template`

New helper in `phrase_lib_tr_profile.py`:
```
render_slide_flow(
    *, slide_profile, seed, slot_payloads_by_role, signature_id
) -> list[{id, title, body}]
```
Reuses the underlying template/combinator/cleanup machinery but emits
slides[] shape. `render_block_template` untouched.

- **Pros**: clean separation between block emission and slide-flow
  emission; honors that they are genuinely different output
  shapes
- **Cons**: two entry points to maintain; needs a parallel set of
  slide-flow template structures (`SLIDE_PROFILE_TEMPLATES_TR` or
  similar) — real design work

### Option D — Phase-4 prose as DATA in canonical library, builder stays in place

Move the slide PROSE (the actual TR strings) from
`composed_detail_renderer.py` INTO `phrase_lib_tr_profile.py` as a
constant:
```
HIDDEN_PRIVATE_DEEP_READ_SLIDES_TR = {
    "private_scene": {"title": "...", "body": "..."},
    "hidden_mechanism": {"title": "...", "body": "..."},
    ...
}
```
Phase-4 builder becomes a thin adapter that imports the constant and
formats slide ids.

- **Pros**: minimum API impact; smallest meaningful consolidation
  (prose lives in canonical library); does the easy 80% of what
  matrix §5.2 wanted; preserves the deep_read voice contract
- **Cons**: does NOT unify with `render_block_template`'s 4-mode
  machinery; Phase-4 stays static (no variant rotation); doesn't
  scale to multi-chart variant pool that the user's "şablon hissi
  olmasın" instinct wants

## Where each option sits on the consolidation arc

| | Consolidation depth | API change | Phase-4 still static? | Path to variant rotation |
|---|---|---|---|---|
| A — loop pattern | medium | none (5 new entries) | per-mode variation, but odd | partial |
| B — extend render_block_template | medium | breaks callers | per-mode variation, awkward | partial |
| C — new render_slide_flow | high | additive (new helper) | NO (full machinery) | yes (purpose-built) |
| D — prose-as-data | low | none | YES (still static) | no |

## Recommendation

**Phased: Option D first, Option C as end-state.**

### Why D first

- Smallest safe step; honors matrix §5.2's intent ("templates migrate
  into canonical library") without forcing a model muddle (Option A)
  or an API change (Option B)
- The user has already manually edited Phase-4 prose 5 times this
  session through QA cycles (v0→v4→v4.1→B5). Centralizing the prose
  in `phrase_lib_tr_profile.py` means future TR copy edits live in
  the canonical library, not buried in a renderer function
- Phase-4 hard invariants (B0-B5) all hold trivially because the
  builder shape doesn't change

### Why C eventually

- The user's earlier "şablon hissi olmasın" feedback (commit thread)
  pointed at WANT for variant rotation per slide. Option D doesn't
  deliver that. Option C does
- Once D ships, S4b can introduce `render_slide_flow(...)` and rewire
  Phase-4 adapter to consume it; the prose can be expanded into the
  variant pool naturally
- This is the same "phased after first migration" pattern V26 cleanup
  used (S2.1.3 single migration → S2.1.7/S2.1.8 deeper cleanup)

### Why NOT A or B (now)

- A muddles the taxonomy and stretches the 4-mode axis past its design
- B breaks the signature narrative call site (matrix §4.4 RESCUE) for
  a small win

## Matrix §5.2 update needed

Current matrix row:
> Phase-4 slide templates migrate into
> `phrase_lib_tr_profile.BODY_TEMPLATES_TR` as a hidden/private family
> entry; the renderer becomes a thin adapter

Recommended replacement (after S4 chooses a path):
> S4a: Phase-4 slide PROSE moves into `phrase_lib_tr_profile.py` as
> `HIDDEN_PRIVATE_DEEP_READ_SLIDES_TR` constant; Phase-4 renderer
> becomes a thin adapter importing the constant. S4b (later):
> introduce `render_slide_flow(...)` to unify slide-flow rendering
> machinery; Phase-4 adapter rewired to consume it; variant pool
> per slide becomes possible.

## Risk notes

### Risk 1 — premature unification
Choosing Option C without first proving the prose-in-library shape
works (Option D) is the bigger version of the V26 "v2 replaces v1"
mistake. Phased reduces this risk.

### Risk 2 — variant rotation expectation
The user has expressed a clear "şablon hissi olmasın" goal. Option D
alone does not deliver it. Documenting that the variant rotation is
S4b (not S4a) avoids the disappointment of "we consolidated but it
still feels templated."

### Risk 3 — DEFAULT_PUBLIC_CHIPS_TR / SOFT_ASTRO_HINTS_TR drift
If Phase-4's hidden/private later gets chips + soft hints, those need
their own canonical home — likely a sibling extension when S4b lands.
Not action-required for S4a.

### Risk 4 — origin_hint surface deferral (still active per Phase-4
authoring packet §4)
The current Phase-4 explicitly does NOT inline origin_hint; that
remains opt-in expandable surface for a later authorization. S4a /
S4b must preserve this; the migration MUST NOT accidentally enable
origin_hint as an inline slide.

## Recommendation summary

- **S4 design step should propose Option D as S4a** (immediate
  bounded request) and document Option C as S4b (later, separate)
- **S4a scope**: move Phase-4 prose constants into
  `phrase_lib_tr_profile.py`, rewire builder to import them, run
  full Phase-4 B0-B5 regression suite
- **S4b scope** (later): introduce `render_slide_flow(...)`, rewire
  adapter, design variant pool per slide
- **Matrix §5.2 row** updated to reflect phased S4a/S4b plan

## Status

Pre-audit complete. Surfaced the contract gap that matrix §5.2's
phrasing hides. Phased Option D → Option C recommended.

S4 design step (next bounded request) consumes this audit as input.
