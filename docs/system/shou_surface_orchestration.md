# SHOU Product Surface Orchestration

Date: 2026-04-26  
Scope: Product orchestration only (no backend builder changes)

## 1) Orchestration Contract

This document turns the existing semantic role + voice mode map into concrete surface behavior.

- Canonical semantic input: `public.meaning_graph_v1_1`
- Render-oriented inputs (existing): `profile_narrative`, `profile_v8`, `sections_v2`, `full_map_v8`, `supporting_threads`
- Source fallbacks (existing): `core_story_ui`, `user_compact`, `personality_imprint`
- No new meaning generation is introduced here.

### 1.1 Source Precedence (all surfaces)
1. `graph`: `meaning_graph_v1_1` (semantic truth)
2. `projection`: `profile_narrative_projection_v1`, `profile_v8_projection_v1` (graph-derived render)
3. `source`: legacy/source branches (fallback only when above is missing)

### 1.2 Existing Semantic Roles Used
- Core Hook
- Effect / First Impression
- Mechanism Narrative
- Shadow Narrative
- Potential Narrative
- Cause / Past Layer
- Pattern Label Surrogate
- Share Line Surrogate
- Raw Proof Anchor
- Evidence Graph / Trace
- Context Surrogate
- Rationale Surrogate
- Caution Surrogate
- Voice Axes Profile (render calibration meta)

## 2) Surface Definitions

## 2.1 Home

| order | semantic role | card type | voice mode | length constraint | data source |
|---|---|---|---|---|---|
| 1 | Core Hook | `hook_card` | `effect_hook` | 1 line, 6–14 words | graph → projection → `core_story_ui.headline` |
| 2 | Effect / First Impression | `insight_card` | `effect_voice` | 1–2 sentences, 120–260 chars | graph (`effect`/`recognition`) → projection |
| 3 | Mechanism or Potential (top-1) | `insight_card` | `mechanism_voice` or `potential_voice` | 1–2 sentences, 120–280 chars | graph (`mechanism`/`potential`) → `user_compact.domains[]` |
| 4 | Context Surrogate (if active) | `list_card` (single row) | `context_mode` | 1 short line, 35–90 chars | projection/context fallback |
| 5 | Share Line Surrogate (optional CTA) | `hook_card` | `share_line_mode` | 6–12 words | projection teaser/micro fallback |

Home rules:
- Must be short: orders 1–3.
- Must be list: context row if present.
- Must not be deep: no long narrative body.
- Narrative allowance: max 1 short narrative-style card.

## 2.2 Profile Top

| order | semantic role | card type | voice mode | length constraint | data source |
|---|---|---|---|---|---|
| 1 | Pattern Label Surrogate + Core Hook | `hook_card` | `pattern_naming_mode` + `effect_hook` | 1 title + 1 line teaser | graph title projection → `profile_v8.identity_axis` |
| 2 | Effect / First Impression | `insight_card` | `effect_voice` | 1–2 sentences, 140–320 chars | projection → `profile_v8.first_impression` |
| 3 | Mechanism Narrative (compact) | `mechanism_card` | `mechanism_voice` | 2 sentences, 180–360 chars | graph → projection → `core_story_ui.text` |
| 4 | Share Line Surrogate | `hook_card` | `share_line_mode` | 6–12 words | projection teaser/micro |

Profile Top rules:
- Must be short: hook + share line.
- Standard depth: effect + compact mechanism.
- Must not be list-heavy.
- Narrative usage limit: max 1 `narrative_card` equivalent.

## 2.3 Profile Cards

| order | semantic role | card type | voice mode | length constraint | data source |
|---|---|---|---|---|---|
| 1 | Mechanism Narrative | `mechanism_card` | `mechanism_voice` | 2–4 sentences, 260–520 chars | graph/projection → `sections_v2` / `supporting_threads` |
| 2 | Shadow Narrative | `insight_card` | `shadow_safe` | 2–3 sentences, 220–480 chars | graph (`shadow`) → `personality_imprint.shadow` / `full_map_v8.*.shadow_fragments` |
| 3 | Potential Narrative | `insight_card` | `potential_voice` | 2–3 sentences, 220–480 chars | graph (`potential`) → `full_map_v8.*.potentials` |
| 4 | Cause / Past Layer | `insight_card` | `cause_voice` | 1–2 sentences, 140–320 chars | graph (`cause`) → `full_map_v8.*.past_fragments` |
| 5 | Raw Proof Anchor (optional) | `proof_card` | `proof_raw_voice` | 1 compact line per card | evidence/projection → `proof_raw` |

Profile Cards rules:
- Must include list content only as chips/bullets (max 5 chips per card).
- Must include narrative: at least 1 mechanism/shadow/potential card.
- Must include implication in body text (not only labels).
- Must keep proof optional but available.

## 2.4 Profile Deep

| order | semantic role | card type | voice mode | length constraint | data source |
|---|---|---|---|---|---|
| 1 | Mechanism Narrative (deep) | `narrative_card` | `mechanism_voice` | 3–6 sentences, 420–900 chars | projection/source packs (`profile_narrative`, `sections_v2`) guided by graph |
| 2 | Cause + Shadow arc | `narrative_card` | `cause_voice` + `shadow_safe` | 3–5 sentences, 350–760 chars | graph layers + `full_map_v8`/threads |
| 3 | Potential close | `insight_card` | `potential_voice` | 2–3 sentences, 220–500 chars | graph + `mission_preview` / potentials |
| 4 | Raw Proof Anchor | `proof_card` | `proof_raw_voice` | up to 2 proof lines per narrative block | `proof_raw` + graph evidence |
| 5 | Evidence Graph / Trace | `proof_card` | `explainability_voice` | compact trace row | `meaning_graph_v1_1.evidence` |

Profile Deep rules:
- Must be deep: first 2 blocks are narrative.
- Must include proof layer for deep claims.
- Must allow list format only in detail/proof rows.
- Must avoid wall-of-text: split long copy into structured blocks.

## 2.5 Story / Slide

| order | semantic role | card type | voice mode | length constraint | data source |
|---|---|---|---|---|---|
| 1 | Core Hook / Pattern Label | `hook_card` | `effect_hook` + `pattern_naming_mode` | 1 slide title + 1 line | projection (graph-derived) |
| 2 | Mechanism | `mechanism_card` | `mechanism_voice` | 2–3 short sentences | graph layer projection |
| 3 | Shadow | `insight_card` | `shadow_safe` | 2 short sentences | graph layer projection |
| 4 | Potential | `insight_card` | `potential_voice` | 2 short sentences | graph layer projection |
| 5 | Context or Caution | `list_card` | `context_mode` or `caution_mode` | 1 short line | projection/source surrogate |
| 6 | Share Line Surrogate close | `hook_card` | `share_line_mode` | 6–12 words | projection teaser/share alias |

Story rules:
- Must be sequence-driven (each slide one role).
- Must stay concise; no deep paragraph slides.
- Must include one contrast/tension turn (shadow → potential).
- Must end with shareable line.

## 2.6 Share Card

| order | semantic role | card type | voice mode | length constraint | data source |
|---|---|---|---|---|---|
| 1 | Share Line Surrogate | `hook_card` | `share_line_mode` | 6–12 words (hard) | projection share alias/micro |
| 2 | Pattern Label Surrogate (optional) | `list_card` | `pattern_naming_mode` | 2–4 words | projection/title |
| 3 | Raw Proof Anchor (optional, small caption) | `proof_card` | `proof_raw_voice` | one compact proof line | evidence/proof_raw |

Share Card rules:
- Must be very short.
- Must not include long mechanism paragraph.
- Must prioritize memorability over explanation.
- Proof is optional and minimal.

## 2.7 Explainability

| order | semantic role | card type | voice mode | length constraint | data source |
|---|---|---|---|---|---|
| 1 | Rationale Surrogate | `proof_card` | `rationale_mode` | 1–2 lines | category/evidence rationale fields |
| 2 | Raw Proof Anchor | `proof_card` | `proof_raw_voice` | 1 line per proof item | `proof_raw`, typed evidence |
| 3 | Evidence Graph / Trace | `proof_card` | `explainability_voice` | id + source path compact row | `meaning_graph_v1_1.nodes/evidence` |
| 4 | Context Surrogate | `list_card` | `context_mode` | 1 short line | context chips/date/domain |
| 5 | Caution Surrogate (if needed) | `insight_card` | `caution_mode` | 1 sentence | shadow-adjacent safety line |

Explainability rules:
- Must be list/proof first; narrative optional.
- Must be traceable to node/evidence ids.
- Must keep human-readable labels for technical evidence.
- Must not become motivational copy.

## 3) Card Type Definitions

| card type | purpose | allowed roles | default source mode |
|---|---|---|---|
| `hook_card` | short attention + memory anchor | Core Hook, Pattern Label Surrogate, Share Line Surrogate | projection from graph, source fallback |
| `insight_card` | concise meaning with implication | Effect, Shadow, Potential, Cause | graph-first |
| `mechanism_card` | “how it works” structured prose | Mechanism | graph + projection |
| `narrative_card` | deep paced editorial block | Mechanism + Cause/Shadow arcs | projection/source with graph trace |
| `list_card` | chips/rows/context items | Context, Pattern label, compact metadata | projection/source |
| `proof_card` | evidence + traceability | Raw Proof, Rationale, Explainability | graph evidence/source proof |

## 4) Semantic Role → Card Type → Surface Map

| semantic role | primary card type | surfaces |
|---|---|---|
| Core Hook | `hook_card` | Home, Profile Top, Story |
| Effect / First Impression | `insight_card` | Home, Profile Top, Profile Cards |
| Mechanism Narrative | `mechanism_card` / `narrative_card` | Profile Top, Profile Cards, Profile Deep, Story |
| Shadow Narrative | `insight_card` | Profile Cards, Profile Deep, Story |
| Potential Narrative | `insight_card` | Home, Profile Cards, Profile Deep, Story |
| Cause / Past Layer | `insight_card` / `narrative_card` | Profile Cards, Profile Deep |
| Pattern Label Surrogate | `hook_card` / `list_card` | Profile Top, Story, Share Card |
| Share Line Surrogate | `hook_card` | Home, Story close, Share Card |
| Raw Proof Anchor | `proof_card` | Profile Cards, Profile Deep, Explainability, Share caption |
| Evidence Graph / Trace | `proof_card` | Explainability, Profile Deep (secondary) |
| Context Surrogate | `list_card` | Home, Story, Explainability |
| Rationale Surrogate | `proof_card` | Explainability |
| Caution Surrogate | `insight_card` | Story, Explainability, Profile Deep (optional) |
| Voice Axes Profile | UI-only render policy (not a card) | Home, Profile, Story render tuning |

## 5) Surface Constraints

## 5.1 Max Cards Per Surface

| surface | max cards/blocks |
|---|---|
| Home | 4 (plus optional share CTA row) |
| Profile Top | 4 |
| Profile Cards | 8 |
| Profile Deep | 10 |
| Story / Slide | 6 |
| Share Card | 1 main + up to 2 micro rows |
| Explainability | 5 |

## 5.2 Narrative Usage Limits

| surface | narrative rule |
|---|---|
| Home | max 1 short narrative-like card |
| Profile Top | max 1 narrative card |
| Profile Cards | max 2 narrative cards, rest insight/list/proof |
| Profile Deep | 2–4 narrative cards allowed |
| Story / Slide | no deep narrative blocks (short slide prose only) |
| Share Card | narrative disallowed |
| Explainability | narrative optional, proof/list primary |

## 5.3 Repetition Avoidance Rules

- Adjacent cards must not start with the same opening phrase pattern.
- Same semantic role should not appear in more than 2 consecutive cards.
- Same proof string (`proof_raw`) must not repeat on adjacent cards unless tied to different role framing.
- If two candidate cards have highly similar teaser text, keep the one with stronger layer diversity (`primary_layer` differs) and better traceability.

## 5.4 Shareability Rules

- Share headline line stays 6–12 words.
- Share main line should avoid raw astro jargon in main text; proof can live in optional caption.
- Share content prefers `effect`/`recognition`/`potential` dominant nodes over dense mechanism text.
- Share card should map to one clear emotional intent; avoid multi-claim overload.

## 6) Implementation Guardrails (Product Only)

- This orchestration is a consumption contract, not a builder rewrite.
- Existing backend outputs remain valid; orchestration only defines which branch each surface should prioritize.
- `meaning_graph_v1_1` remains canonical semantic truth; projections remain editorial render forms.
- Surfaces may continue to use legacy render packs until parity is proven, but precedence should follow §1.1.
