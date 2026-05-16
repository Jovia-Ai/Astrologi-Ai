# Natal/Profile Detail Slides Contract Plan

> Planning artifact only. No code, renderer, or public-output changes are made by this document.

## 0. Scope And Invariants

This plan defines a future `slides[]` contract for natal/profile detail experiences using the hand-authored Venus 12H hidden/private love prototype as the quality bar.

Hard constraints:

- no implementation in this pass
- no renderer change in this pass
- no current public payload change in this pass
- slides are composition output, not a new meaning owner
- slides adapt to card type; there is no universal fixed template
- fewer strong slides are better than padded slides
- public Turkish must stay natural, scene-based, and non-technical
- headline/body duplication is a regression

Prototype lessons that become contract rules:

1. parent card stays compressed
2. detail opens horizontally as separate semantic faces
3. each slide performs one job
4. hidden/private cards move from inner life toward safer visibility
5. astrology stays supporting, never leading

## 1. `slides[]` Schema

`slides[]` is a per-card detail-expansion contract, not a root collection.

Logical attachment target:

- `profile_public.core_blocks[i].slides[]`
- `profile_public.extra_blocks[i].slides[]`
- `profile_public.composed_detail_cards[i].slides[]`

Attachment invariant:

- `slides[]` is attached to the parent card only
- there is no root `slides` collection anywhere in the payload

Near-term rollout constraint:

- until public rollout is explicitly approved, the contract should exist only as a planning/debug mirror, not as a required public field

Proposed logical schema:

```json
{
  "slides": [
    {
      "id": "slide::venus_taurus_12h_private_love_inner_beauty_chart_exact::private_scene",
      "role": "private_scene",
      "title": "İçeride büyüyen bağ",
      "body": "Birine bağlandığında bunu önce içinde koruyup daha yavaş görünür kılmak.",
      "body_blocks": [
        "Birine bağlandığında bunu önce içinde koruyup daha yavaş görünür kılmak."
      ],
      "sentence_strategy": "inside_lens",
      "tone_mode": "intimate_hidden_private",
      "source_refs": [
        {
          "owner": "card",
          "field": "body"
        },
        {
          "owner": "packet",
          "id": "venus_taurus_12h_private_love_inner_beauty_chart_exact"
        }
      ],
      "debug": {
        "card_frame": "detail_card",
        "promise_type": "love_style",
        "valence_frame": "hidden_private",
        "slide_profile": "hidden_private",
        "sentence_strategy": "inside_lens",
        "tone_mode": "intimate_hidden_private",
        "strategy_reason": "role-first: private scene"
      }
    }
  ]
}
```

Field rules:

- `id`: stable internal handle inside the card, unique per card, in the form `slide::<card_id>::<role>`
- `role`: internal semantic composition role; preferred to remain payload-visible for mobile/analytics, but never rendered as user-facing text
- `title`: human-facing, never raw enum text
- `body`: canonical short body for the slide; keep the field name `body` consistent, with mobile mapping `body -> bodyBlocks`
- `body_blocks`: optional paragraph split when one body needs 2-3 beats
- `sentence_strategy`: canonical runtime/composition field for sentence construction
- `tone_mode`: optional higher-level tonal alias only; not the canonical runtime selector
- `source_refs`: provenance for the slide’s claims
- `debug`: internal derivation metadata only

Schema omissions by design:

- no independent `slides_owner`
- no free-floating `slides_root`
- no new semantic text fields that bypass parent card evidence
- no mandatory five-slide requirement
- no UI rendering of `role`, `tone_mode`, `sentence_strategy`, or `strategy_reason`

## 2. Slide Role Enum

The enum should be one global set with family-specific subsets. Not every card uses every role.
If two roles cannot be explained as clearly different jobs, they should be merged.

### 2.1 Core enum

- `private_scene`: names how the pattern is lived privately before it becomes visible.
- `hidden_mechanism`: explains why the pattern stays less visible or works from inside.
- `protective_pattern`: shows what the psyche is trying to protect by holding back or filtering.
- `gift_in_silence`: names the quiet strength carried by the pattern when it is not distorted.
- `safe_visibility`: shows how the pattern can become more open without breaking its truth.
- `natural_capacity`: names an ability that works naturally when the card is in balance.
- `expression_scene`: shows where the capacity becomes visible or useful in lived situations.
- `overuse_risk`: shows how a real gift can become rigid, excessive, or flattening.
- `healthier_use`: shows how the same strength works better when carried more consciously.
- `friction_scene`: names the lived difficulty or repeating stuck moment.
- `inner_split`: holds two competing pulls without prematurely resolving them.
- `old_reflex`: shows the protective default move that tends to repeat under pressure.
- `emerging_capacity`: shows what skill or possibility is being built through the friction.
- `need_scene`: names the core need in human terms rather than advice terms.
- `need_pattern`: shows how the person seeks, misses, or organizes around that need.
- `overprotection`: shows how protecting the need can itself become limiting.
- `healthier_expression`: shows a truer and less defended way the need can be expressed.
- `value_scene`: shows how value, worth, or exchange is first felt in lived reality.
- `exchange_pattern`: shows how giving, receiving, and reciprocity tend to work.
- `boundary_tension`: shows where worth and boundary become confused or over-defended.
- `self_worth_gift`: names the strength that appears when value becomes internalized.
- `grounded_exchange`: shows what healthier reciprocity looks like in practice.
- `public_scene`: names how the pattern appears in public role, work, or outer visibility.
- `role_mechanism`: explains how that public pattern structurally works.
- `visibility_friction`: shows what makes being seen difficult, charged, or distorted.
- `authority_voice`: names the stronger public expression once the pattern is owned well.
- `inner_base_scene`: names the inner-home or emotional-base experience.
- `root_mechanism`: explains the deeper structure underneath that inner base.
- `old_pattern`: names the inherited or entrenched root-level repetition.
- `safety_need`: shows what inner condition is required for genuine regulation.
- `re_rooting`: shows what more stable inner grounding becomes possible.

### 2.2 Merged roles

These role pairs are intentionally merged because they are not reliably distinct enough for runtime use:

- `where_it_shows` + `how_it_helps` -> `expression_scene`
- `capacity_being_built` + `what_becomes_possible` -> `emerging_capacity`
- `without_it` + `how_you_seek_it` -> `need_pattern`
- `use_it_well` + `healthier_expression` -> `healthier_use` where the family does not need a separate need-expression role
- `authority_or_voice` + `sustainable_visibility` -> `authority_voice`

### 2.3 Role rules

- roles are internal authoring handles
- `role` may remain payload-visible for machine consumers, but not for direct UI text
- public titles must not expose role names
- one slide should usually map to one role
- combining two roles into one slide is allowed only when the card is semantically thin and the merge still reads as one clean move
- if a role cannot be expressed without redundancy, drop the slide instead of padding
- if `dropped_roles` becomes frequent in production traces, the enum is too broad or the mapping is wrong

## 3. `card_frame` / `promise_type` / `valence_frame` Mapping

`slides[]` should be chosen from a small profile matrix, not by one-size-fits-all templating.

### 3.1 Proposed `card_frame`

- `hero_card`
- `detail_card`
- `support_card`
- `composed_detail_card`

Interpretation:

- `hero_card`: top-level public-main card, usually denser and more identity-defining
- `detail_card`: regular core/extra detail card opened into slides
- `support_card`: lighter side-angle card where over-expansion is risky
- `composed_detail_card`: trace-backed synthetic detail card, usually narrower and evidence-bounded

### 3.2 Existing `promise_type` inputs

Observed live values already include:

- `gift`
- `love_style`
- `mind_style`
- `behavior_reflex`
- `need`
- `career_signature`
- `wound_to_gift`

### 3.3 Proposed `valence_frame`

- `gift`
- `friction`
- `wound_to_gift`
- `need`
- `hidden_private`
- `value_boundary`
- `career`
- `roots`

`valence_frame` is derived from existing card meaning; it does not author new meaning.

### 3.4 Mapping table

| Input shape | Default slide profile | Typical slide count | Sentence strategy spine | Notes |
|---|---|---:|---|---|
| `detail_card` + `love_style` + `hidden_private` | `hidden_private` | 3-5 | `inside_lens -> structural_recognition -> paradox_holder -> grounded_assertion -> threshold_statement` | Venus 12H prototype family |
| `detail_card` + `gift` + `gift` | `gift` | 3-4 | `grounded_assertion -> evidence_summary -> grounded_assertion -> healthier_use` | stays affirmative without becoming generic |
| `detail_card` + `wound_to_gift` + `wound_to_gift` | `wound_to_gift` | 4-5 | `inside_lens -> paradox_holder -> structural_recognition -> threshold_statement` | must preserve tension before resolution |
| `detail_card` + `need` + `need` | `need` | 3-4 | `inside_lens -> structural_recognition -> soft_invitation` | centers felt need, not advice |
| `hero_card` + `career_signature` + `career` | `career` | 3-4 | `grounded_assertion -> structural_recognition -> threshold_statement` | role/visibility pacing, no generic ambition talk |
| `support_card` + any + any | `compressed_support` | 2-3 | `evidence_summary`-led | prefer fewer slides |
| `composed_detail_card` + any + any | `evidence_bounded` | 2-3 | `structural_recognition`-led | narrow, traceable, no semantic inflation |

### 3.5 Hidden/private prototype mapping

For the prototype family:

- `card_frame`: `detail_card`
- `promise_type`: `love_style`
- `valence_frame`: `hidden_private`
- canonical `sentence_strategy` progression:
  1. `inside_lens`
  2. `structural_recognition`
  3. `paradox_holder`
  4. `grounded_assertion`
  5. `threshold_statement`
- optional `tone_mode` alias: `intimate_hidden_private`
- required role order:
  1. `private_scene`
  2. `hidden_mechanism`
  3. `protective_pattern`
  4. `gift_in_silence`
  5. `safe_visibility`

This sequence is the quality bar for hidden/private cards, not a universal rule for every card.

## 4. Attachment To `core_blocks` / `extra_blocks` / `composed_detail_cards`

### 4.1 Core principle

Slides belong to the card they expand. They do not become a separate selection lane.

### 4.2 Attachment rules by lane

`core_blocks`

- highest chance of getting slides
- can use 3-5 slides if the card has real semantic breadth
- should prefer role diversity over raw count

`extra_blocks`

- usually 2-4 slides
- only expand if the extra card has a distinct lived scene, not just leftover evidence
- if the card is already borderline repetitive, it should stay unslid

`composed_detail_cards`

- usually 2-3 slides max
- should stay tightly evidence-bounded
- should not pretend to have the same editorial depth as a hand-authored exact-family card unless the source plan genuinely supports it

### 4.3 No duplicate-semantic expansion

If a cluster already has one stronger expanded card in `core_blocks`, a weaker mirror in `extra_blocks` should usually not receive its own full slide flow.

Priority order:

1. strongest semantically distinct core card
2. semantically non-overlapping extra card
3. narrow composed detail card if it adds a truly separate angle

### 4.4 Attachment source of truth

Meaning source remains:

1. packet fields
2. cluster plan
3. already selected public card text/evidence

Slide composition source begins only after that.

## 5. `source_refs` And Debug Fields

### 5.1 `source_refs`

`source_refs` explain where a slide’s claim came from. They do not carry new prose.

Proposed shape:

```json
{
  "owner": "card|packet|cluster|evidence",
  "id": "optional-stable-id",
  "field": "optional-source-field",
  "note": "optional-short-derivation-note"
}
```

Allowed examples:

- card field refs: `title`, `teaser`, `body`, `detail_blocks[1]`
- packet refs: `packet_id`, `direct_meaning`, `lived_scene`, `gift`, `shadow_or_friction`, `growth_direction`
- cluster refs: `cluster_id`, `distinct_lived_scene`, `subtypes`
- evidence refs: existing `source_evidence_ids`, `source_section_ids`, `source_category_ids`

Rules:

- `source_refs` point back to existing owners only
- at least one ref should connect to the selected card surface
- hidden/private slides should usually carry both lived-scene and packet/cluster provenance
- in early phases, `source_refs` should stay debug/trace-only
- public UI should not render raw refs unless a separate “why this exists” surface is explicitly approved

### 5.2 Debug fields

Debug should explain composition, not become a second semantic layer.

Proposed debug fields:

- `card_frame`
- `promise_type`
- `valence_frame`
- `slide_profile`
- `slide_role`
- `role`
- `sentence_strategy`
- `tone_mode`
- `strategy_reason`
- `quality_flags`
- `dropped_roles`
- `role_merge_reason`

Rules:

- debug must not contain alternative public copy candidates
- debug must not contain freeform semantic invention
- debug is inspectability only
- future rollout should keep debug in traceability or debug-only lanes first
- `sentence_strategy` is the canonical runtime/composition field
- `tone_mode` is optional and, if present, is only a higher-level tonal alias
- `sentence_strategy`, `tone_mode`, and `strategy_reason` are debug-only and must never be rendered in UI

### 5.3 Debug metrics

These metrics should be monitored in internal runs:

- `role_distribution`
- `dropped_roles`
- `role_merge_reason`
- `sentence_strategy_distribution`

Interpretation rule:

- if `dropped_roles` is frequent, the enum is too broad or the role-profile mapping is wrong

## 6. Fallback Behavior If Slides Are Absent

Fallback must preserve current app behavior.

Primary rule:

- absence of `slides[]` means the mobile app continues using current card-to-scene derivation from `summary`, `body`, `detail_blocks`, `chips`, `astro_sources`, and `proof_raw`

Fallback ladder:

1. if `slides[]` exists and passes validation, consume it
2. else if explicit `detail_blocks` exist, use them
3. else split `body`
4. else use `summary` or `teaser`
5. else do not open a padded detail flow

Important behavior:

- no synthetic empty slides
- no mandatory “5 slides” backfill
- if a card only supports 2 strong detail beats, render 2
- if a card does not justify expansion, keep it as a compressed card only

## 7. Quality Rules

These are the contract-level gates. The Venus 12H prototype is the bar.

### 7.1 Must-have rules

- [golden][human] each slide must add a distinct semantic move
- [automated] titles must be human-facing and non-technical
- [human] body copy must sound natural in Turkish
- [golden][human] copy should start from scene/lived experience before explanation
- [golden][human] hidden/private cards should move from inside to safer visibility
- [human] astrology should support clarity, not dominate the first sentence

### 7.2 Regression rules

- [automated] no repeated parent headline/body on slides
- [human] no same title shape repeated across all slides
- [automated] no chip-format prose
- [automated] no raw English aspect names in public text
- [human] no coaching/self-help drift
- [golden][human] no “generic uplift ending” on friction or hidden/private cards
- [automated][golden] no new claims that are not grounded in card/packet/cluster evidence
- [automated][human] no slide count padding just to hit a target

### 7.3 Count rules

- [human] 2 slides is acceptable if they are strong
- [human] 3 slides is the default healthy minimum for expandable cards
- [golden] 5 slides is reserved for families with real semantic sequencing, like hidden/private or wound-to-gift
- [automated] more than 5 slides should be considered a failure unless a future surface explicitly requires it

### 7.4 Prototype-specific rule

For hidden/private cards, the slide flow should feel like:

1. what is lived inside
2. why it stays less visible
3. what that protects
4. what quiet gift it carries
5. how safer visibility becomes possible

If a hidden/private card cannot support that logic truthfully, it should collapse to 3-4 stronger slides, not a fake five-step arc.

### 7.5 Family-entry rule

No new slide family ships without a hand-authored reference prototype.

Every family must have:

- one golden example
- one explicit role sequence
- good examples
- bad examples
- a QA checklist

Until those exist, the family stays planning-only or debug-only.

## 8. Tests

No code is implemented here, but these are the required tests for rollout.

### 8.1 Schema tests

- per-card `slides[]` shape validates
- required fields present by slide
- `role` values stay inside enum
- duplicate slide ids inside one card fail

### 8.2 Mapping tests

- `card_frame`/`promise_type`/`valence_frame` derive the expected slide profile
- hidden/private cards choose hidden/private role order
- support cards do not over-expand
- composed detail cards stay within evidence-bounded role/count limits

### 8.3 Quality tests

- no repeated headline/body between parent and slides
- no duplicate slide bodies inside one card
- title/body length budgets hold
- banned phrase scan passes
- raw role names do not surface as titles
- Turkish sentence-shape diversity is real, not synonym swapping

### 8.4 Truthfulness tests

- every slide has valid `source_refs`
- slides do not cite nonexistent packet/cluster/evidence ids
- no slide introduces a semantic claim absent from upstream meaning owners
- chart-truthfulness scans remain clean

### 8.5 Stability tests

- current public payload snapshot stays unchanged while contract is debug-only
- current renderer output stays unchanged while slides are not consumed
- cards with no slides still open with today’s fallback flow
- no UI surface renders debug-only fields as text

### 8.6 Golden QA bundles

- Venus 12H hidden/private love prototype comparison
- one adjacent `love_style` card that is not hidden/private
- one `wound_to_gift` card
- one `career_signature` card
- one `composed_detail_card`

### 8.7 Family-launch QA pack

Before a new slide family moves beyond debug:

- one hand-authored reference prototype exists
- one golden output exists in test fixtures
- role sequence is documented
- good/bad examples are attached to the family
- QA checklist is completed and archived

## 9. Mobile Consumption Notes

Current mobile detail flows already consume card-like scene inputs:

- `title`
- `intro`
- `bodyBlocks`
- `chips`
- `astroSources`
- `whyText`
- `proofRaw`

Current fallback behavior is useful and should remain the safety net.

### 9.1 Proposed scene mapping

Each slide maps cleanly to one `ProfileDetailSceneData` scene:

- `slide.title` -> `scene.title`
- first sentence or short body -> `scene.intro`
- `slide.body_blocks` -> `scene.bodyBlocks`
- card-level chips remain available unless a future slide-specific subset is truly needed
- `source_refs` may feed `whyText` / proof affordances later, but should not force raw-debug UI

### 9.2 Mobile behavior rules

- parent card remains the entry surface
- tapped flow remains horizontal
- header remains fixed
- slide count indicator should reflect real count, not padded count
- mobile design must handle variable slide counts gracefully
- scene variants can still adapt by density, but semantic sequencing should come from `slides[]`, not ad hoc sentence splitting

### 9.3 Consumption constraints

- mobile should not need to infer slide roles from prose once `slides[]` exists
- mobile should not own semantic re-ordering
- mobile may still choose presentation variant by density or illustration mode
- if `slides[]` is missing or invalid, mobile must quietly fall back to current derivation

## 10. Migration Plan

### Phase 1. Contract planning

- freeze the quality bar from the hand-authored Venus 12H hidden/private love prototype
- define per-card `slides[]`, `slide_role`, mapping, and provenance rules
- no runtime changes

### Phase 2. Hand-authored reference packet

- create one exact reference example for the Venus 12H hidden/private love family
- do not generate slides for all cards in this phase
- validate title/body/sequence quality against the prototype
- still no renderer/public rollout

### Phase 3. Debug-only shadow contract

- generate `slides[]` in a traceability/debug-only lane
- attach logically by card id
- prove no public payload drift
- keep `source_refs`, `sentence_strategy`, `tone_mode`, and `strategy_reason` trace/debug-only in this phase

### Phase 4. Internal consumer trial

- let mobile or a local preview tool read `slides[]` only when explicitly enabled
- compare side-by-side with current fallback-derived scenes
- reject rollout if the new path is merely more structured but not better written

### Phase 5. Family-by-family expansion

- hidden/private first
- one adjacent family second, likely `wound_to_gift` or `gift`
- career and composed-detail later, because they are more vulnerable to generic padding

Phase 5 exit criteria:

- hand-authored prototypes are complete for every family entering rollout
- side-by-side review passes against fallback-derived detail flows
- no semantic-owner drift is found in traceability review
- no copy QA failure remains open
- mobile internal trial passes with variable slide counts
- golden bundle stays stable
- `dropped_roles` metrics do not show systematic role collapse
- good/bad examples and QA checklist are present for each launched family

### Phase 6. Optional public additive rollout

- add `slides[]` per card, never as a new root
- keep fallback path for legacy cards

Phase 6 entry criteria:

- all Phase 5 exit criteria pass
- public-payload-visible `role` handling is confirmed safe for mobile/analytics
- `source_refs` scope is explicitly approved for any non-debug consumer
- no semantic-owner drift appears in pre-public audit
- internal copy QA and golden bundle remain green at launch-candidate commit

### Phase 7. Cleanup

- once enough cards have strong authored slide contracts, reduce mobile dependence on sentence splitting
- keep card-level fallback permanently for weak or legacy cards

Roadmap addition:

- add a future `SHOU Editorial Operations Plan` covering authoring workflow, review ownership, golden maintenance, and content-velocity governance

## Final Recommendation

The contract should be per-card, adaptive, and evidence-owned by existing card/packet/cluster semantics. The Venus 12H hidden/private love prototype should define the bar for sequencing and natural Turkish, but not force every card into a five-slide mold.

The safest path is:

1. keep meaning ownership where it already is
2. define `slides[]` as a card-local expansion contract
3. start with one hand-authored Venus 12H hidden/private love reference card, not all cards
4. roll it out in debug/internal lanes first
5. preserve today’s renderer and public output until the slide path proves clearly better
