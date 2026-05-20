# SHOU Voice Tier Architecture — Design Doc

> Planning artifact. **No code.** Asks for design review before any
> prototype work begins. Answers the strategic question raised in
> conversation: "we didn't really solve language scaling — how does
> this become a real product?" Frames a unified two-tier architecture
> (free = pattern grammar, premium = LLM compose) that both consume
> the same committed Plan layer.

## 1. Problem

Phase-4 first-pass shipped one family (hidden/private deep_read) with
**hand-written static TR templates**. Quality bar was met (1996
manual QA PASS); scaling cost is unsustainable: ~12 theme families
× sub-signature variations × hand-authored prose = weeks-to-months
of linear writing labor per family, with maintenance burden after.

The committed architecture explicitly contemplates a tiered approach
(`shou_tone_aware_composition_plan.md §11 LLM Policy`) but the actual
shape of that tier — what the free path looks like, what the premium
path looks like, how they share infrastructure — was never spec'd.
This document closes that gap.

## 2. Strategic frame

Two product tiers, one shared Plan layer:

```
            Plan layer  (Katman 0-3 + packet field consumption / B6+)
                |
                v
        ┌───────┴───────┐
        |               |
     FREE              PREMIUM
   pattern             LLM compose
   grammar             (cached, plan-faithful)
        |               |
        └───────┬───────┘
                v
            Guard layer
                |
                v
            public output
```

Both tiers:
- consume the same deterministic semantic Plan (slide_profile +
  role_bindings + per-chart packet fields: `lived_scene`, `gift`,
  `shadow_or_friction`, `growth_direction`, ...)
- pass through the same Guard layer (banned-phrase scan, length
  budget, role-binding compliance, determinism check, truthfulness
  fidelity)
- honor the same frozen voice contract (`shou_voice_reconciliation_spec.md`:
  Rules 1–4 + origin_hint eligibility + opt-out language + thesis-once)

Difference is only the **render strategy**.

## 3. Free path — Pattern grammar

### 3.1 Concept (not Mad Libs)

Not "one fixed template with variable slots." Instead: **layered
frame library** where each slide-role + rhythm + valence has multiple
fully-authored clause variants, and the renderer selects a frame +
fills semantic slots from the Plan.

Example for `private_scene` role with `[ritim: sakin]`:

```
frame_id: private_scene__sakin__v1
shape: "{açılış} {davranış}; {gerekçe} {nüans}."

açılış variants (each grammatically self-complete TR clause):
  - "Sen birine karşı bir his uyandığında"
  - "Yakınlık duyduğun birine dair bir şey hissettiğinde"
  - "İçinde bir bağ kıpırdadığında"

davranış variants:
  - "onu hemen göstermezsin"
  - "duygun hızlıca dışarı taşmaz"
  - "ilk tepkin içeriye dönüktür"

gerekçe variants (consume packet field):
  - "{lived_scene_atom} olduğu için"
  - "{depth_processing_marker} işliyor olduğun için"

nüans variants:
  - "düşünmeden söylediğinde anlamın bozulacağından çekinirsin"
  - "anlamı kavramadan paylaşmak sana eksik gelir"
```

Renderer per slide:
1. Look up `slide_profile` → list of frame_ids eligible for this role
2. Select frame_id deterministically (chart-hash seeded)
3. For each variant slot, deterministically pick a variant
4. Fill `{packet_field}` slots from the Plan's packet data
5. Concatenate; pass through guards

**Variety from combinatorics, not from "tema değiştirir".** With 5
frame_ids × 3 variants per slot × 4 slots = 60 combinations per
slide-role, but each combination is grammatically a fully-authored
sentence. No "fill in the blank" feel.

### 3.2 Why not a single static template (today)

Today's hidden/private templates are a single fixed sentence per
slide. Every chart that hits the pilot signature sees the identical
slide. This is what fails to scale: per-family, per-signature,
linear hand-craft.

### 3.3 Why this is not "too mechanical"

Mechanical feel emerges from three causes; design defends against
each:

| Cause | Defense |
|---|---|
| Same surface phrase recurs across charts | enough variants per slot + chart-hash seeded selection; analytics on cross-chart variant exposure |
| Slots are dumb fillers, not meaning units | each slot is **a semantic role**, not a noun socket. Packet fields carry chart-specific meaning; frames give them voice |
| Frames are written generically (lowest common denominator) | every variant is hand-authored at the same craft bar as the 1996 manual-QA PASS slides. Quality bar = the LOCK reference voice |

### 3.4 Cross-slide coherence

5 slides each picking variants independently risks jarring
transitions. Design rule:

- Connector tokens at slide-start (`"Bu yüzden"`, `"Aslında"`,
  `"Yine de"`) are governed by the **previous slide's variant
  fingerprint**, not random selection
- Frame variants are tagged by register (`yere basan / kontrast /
  dramsız / sıcak / yatışan`); selection enforces the
  per-slide rhythm map from the slide_profile
- Repetition cap: same variant cannot appear in two adjacent
  slides; same opener token cannot repeat within the card

### 3.5 TR-specific design concerns (real, named)

Turkish is morphologically rich. Naive slot-fill produces
grammatical errors that English-style template systems hide:

| Risk | Concrete example | Mitigation |
|---|---|---|
| Possessive agreement | `anlam{POSS}` — "anlamım/anlamın/anlamı" varies by subject | Variants are full clauses with morphology baked in (no morpheme-level slots in v1); packet-fill slots are nouns/full phrases, not bare roots |
| Vowel harmony | `yapıda{COPULA}{PERSON}` — "yapıdayım" vs wrong forms | Same — full-clause variants, no suffix-level fill |
| Register drift | "ama / oysa / yine de / ne var ki" carry different formality | Connector tokens are part of frame, not free choice |
| Yoda-Turkish word order | naive concatenation breaks SOV cadence | Frames are pre-composed sentences; only noun/phrase slots fill |
| Capitalization / quotation marks | TR uses « », " ", etc. inconsistently in MT output | Library style guide; one canonical form |

**Design call for prototype**: **no morpheme-level slot-fill in v1**.
Slots accept whole noun phrases or short clauses only. Morphology
is baked into hand-authored variants. This is safer and cheaper to
start; a TR-morphology engine is a future investment if variant
counts become prohibitive.

### 3.6 What lives where in code (sketch — not committed)

- `backend/app/narrative/frame_library/` (new dir) — YAML or Python
  module per role (`private_scene.yaml`, `gift_in_silence.yaml`, …)
  with frame definitions
- `backend/app/narrative/frame_renderer.py` (new) — selection +
  fill + guard hooks
- `backend/app/narrative/frame_grammar_tr.py` (new) — TR-specific
  cadence / connector / capitalization helpers
- `backend/app/meaning/composed_detail_renderer.py` — Phase-4
  renderer branch calls `frame_renderer` instead of returning
  static templates, when a "frame_grammar" render strategy is
  selected
- Existing `humanize_tr.py` / `apply_tone.py` continue to play
  grammar-only / fallback roles per `tone_aware §12`

**Important**: scope decision deferred. This is a *sketch*, not
an authorization to touch any file.

### 3.7 What about the existing `editorial constraint library`?

Already in the committed architecture (`tone_aware §8`):
- `approved_fragments`
- `preferred_patterns`
- `title_pattern_families`
- `role_specific_language_guidance`

Pattern grammar is literally the operational form of §8. The slot
library + frame library + variant tags = §8's constraint library
made executable. Not net-new; filled in.

## 4. Premium path — LLM compose

### 4.1 Concept

Same Plan input. Output is an LLM-composed slide set, with the LLM
constrained by:
- the deterministic Plan (slide_profile + role_bindings + packet
  fields → these become the prompt's structured input)
- the frozen voice contract (Rules 1–4 communicated as prompt
  constraints + post-generation guard)
- TR-only generation; locale-aware
- forbidden-phrase + determinism + truthfulness guards (same as free)
- cached: same Plan → same output (deterministic from the user's
  perspective despite stochastic LLM)

### 4.2 What §11 already allows

> "cached deterministic plan-to-draft experiments"
> conditions: "deterministic meaning plan exists first · cache exists
> · banned-phrase scan exists · truthfulness guards remain active ·
> no direct public release without validation"

We have the Plan layer. We have guard infrastructure (Phase-4 B3
tests). Caching infrastructure exists in Astrologi (CLAUDE.md
mentions memory + Redis backends). LLM infrastructure exists (Groq
→ OpenAI → local Llama fallback per CLAUDE.md). The remaining
design work:
- Prompt that consumes Plan in a stable structured way
- Cache key (Plan hash + locale + tier)
- Cost / latency budget per request
- Fallback path: if LLM fails or guards reject, fall through to
  free-tier pattern grammar output

### 4.3 Truthfulness fidelity rule

LLM must NOT invent astrological claims beyond the Plan. The Plan
provides the semantic units (e.g., `gift = "depth processing"`);
LLM phrases them as TR prose. Truthfulness check: every named
placement / aspect in the output must trace to a Plan field.
Guard rejects output that introduces unauthored claims.

### 4.4 What premium actually buys

- Chart-specific phrasing without per-family hand-craft (LLM picks
  the words; Plan controls the meaning)
- Higher ceiling on variation across charts
- Easier extension to new families (a new family = new Plan
  schema additions, no new prose library)
- Potential multi-locale fluency (TR-primary, EN parallel) without
  re-authoring frame libraries

What it does NOT buy:
- Truthfulness (Plan provides truth; LLM is voice only)
- Determinism (cache provides this; LLM alone does not)
- Architectural simplicity (LLM adds operational surface)

## 5. Shared layers

### 5.1 Plan layer (already mostly built)

- Katman 0–3 ARC pipeline (deterministic, in production)
- Phase-3 `deep_read_phase3` metadata (role_bindings, eligibility,
  slide_profile selection) — built for hidden/private; needs
  extension to other families
- Per-chart packet fields (`lived_scene`, `gift`,
  `shadow_or_friction`, `growth_direction`) — exist on
  natal_promise_packets; consumption deferred to B6+

**Open work** (NOT in scope of this doc):
- B6+ packet field consumption in renderer
- Extending Phase-3 metadata to other families
- Plan schema design for cross-family expressiveness

### 5.2 Guard layer (shared)

Identical for both tiers. Already implemented for free path in
Phase-4 B3 tests; same rules applied to premium:
- banned-phrase scan (tone_aware §8)
- origin_hint determinism + opt-out clause requirement
  (packet §4)
- gift motivational-drift scan
- trace-surface containment
- length budget
- role-binding compliance
- truthfulness fidelity (premium-specific: every named
  astrological claim traces to Plan)

## 6. Feasibility prototype proposal

To answer the "does pattern grammar actually feel non-mechanical"
question empirically before larger investment:

**Scope:**
- ONE family: hidden/private (already validated at LOCK quality bar)
- ONE slide: `private_scene` (the slide that triggered the user's
  "ilk cümlede kayboldum" feedback originally)
- 5 frame_ids × 3 variants per slot, hand-authored at LOCK-quality
- chart-hash seeded selection
- behind a NEW dedicated experiment flag (independent from Phase-4)
- public output unchanged; renders to internal-only path for QA
- manual side-by-side read: static template (current B5 output) vs
  3-4 pattern-grammar permutations on the same chart, side-by-side

**Out of scope for prototype:**
- LLM premium path
- Other slides / families
- B6+ packet field consumption (use the existing pilot's static
  meaning for slot-fill in v1 to isolate the grammar question)
- TR morphology engine
- Any public-output change

**Success criteria:**
- 3-4 permutations read as distinct natural TR prose without
  feeling mechanical
- Each permutation passes all existing Phase-4 B3 guards
- Cross-permutation variant exposure is meaningfully different
- TR grammar is clean across all permutations (no agreement bugs)

**Failure criteria:**
- Permutations feel templated even after authoring effort
- TR grammar fails on any permutation
- Variant authoring takes disproportionate effort vs static template
- → If failure, escalate to premium LLM as primary, free path
  becomes simpler static templates (current state)

## 7. What this doc grants vs does NOT

**Grants:**
- An agreed design frame for tier architecture
- The pattern grammar approach as the proposed free path
- The LLM compose approach as the proposed premium path
- A concrete feasibility prototype scope

**Does NOT grant:**
- Any code work (separate bounded request with §13.2-style review)
- Any production change
- Any public schema widening
- Authorization to touch any file
- Premium LLM implementation
- B6+ packet field consumption
- ARC/A2 merge (the original §10.3 question is still owed)

## 8. Open design questions for review

1. **Frame library format**: YAML vs Python module per role?
2. **Selection determinism**: chart-hash seed alone, or also user-stable
   seed (so a returning user doesn't see different variants)?
3. **TR morphology**: stay full-clause-only in v1, or invest in a
   small morphology helper now?
4. **Cross-slide coherence**: connector-token state machine, or
   slide-N+1's frame_id constrained by slide-N's tag?
5. **Frame authoring workflow**: who writes? review process per
   `tone_aware §13.2`?
6. **Premium LLM model choice**: Groq Llama (fast, cheap, lower
   ceiling) vs OpenAI / Anthropic (higher quality, higher cost)?
   Per-family or per-user?
7. **Caching strategy**: Plan-hash as key; per-locale; per-tier; TTL?
8. **Fallback**: premium LLM → free pattern grammar → static
   template, or a tighter ladder?
9. **EN parallel**: build EN frame library in parallel with TR, or
   defer? LLM premium handles EN more naturally than free path —
   does that argue for EN-only premium?
10. **Sequencing with A2 §10.3**: voice tier work proceeds while
    salience calibration is still pending — does any tier-design
    choice depend on A2 outcome?

## 9. Suggested next step

Bounded "feasibility prototype" implementation request, scoped
per §6 above. Same B0-B5 discipline as Phase-4. Flag-gated,
internal-only output for QA, no public-facing change. After the
prototype, the answer to "tier architecture: full pattern grammar
investment, full LLM investment, or hybrid?" becomes
evidence-based rather than guess-based.

If the prototype confirms pattern grammar feels right: tier
architecture commits, frame library expansion begins per family,
LLM premium tier designed in parallel.

If the prototype fails: tier architecture pivots — LLM becomes the
primary scaling path, free tier remains static templates for the
most-used families only, pattern grammar is shelved.

Either outcome is informative. The current state (one hand-built
family, no scaling plan) is the only outcome we can't afford.
