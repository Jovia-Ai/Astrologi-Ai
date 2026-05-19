# SHOU deep_read — Phase-3 Implementation Plan (for approval)

> Planning artifact. **No code in this document.** Seeks explicit
> scope approval (CLAUDE.md: renderer/endpoint/contract changes are
> approval-gated). Bounded per tone_aware §16 + §10 discipline.

## 1. Objective (Phase-3 ONLY)

tone_aware §16 Phase 3 = **internal `slides[]` contract + role/profile
metadata, with ZERO public-output change**. This plan covers Phase 3
only. The tone-aware *renderer* that actually changes copy is Phase 4
(behind a flag) — a separate later approval. Phase 3 is fully
reversible because nothing user-visible changes.

## 2. Pilot scope — exactly ONE family

- Pilot family: **hidden/private `deep_read`** (tone_aware §16's
  pre-selected pilot), worked example **2007** — the chart already
  blind-LOCKED (`shou_voice_deep_read_lock_BLIND.md` = PASS).
- Everything else is **out of scope** (see §7).

## 3. Precondition gate (cannot self-clear)

tone_aware §13.2 requires **human code review of every new constraint
family**. `shou_voice_deep_read_authoring_packet.md` is the input to
that review. Phase-3 code work does **not** start until that review
passes. This plan does not substitute for it.

## 4. Real code surface (mapped, not invented)

| File | Phase-3 role |
|---|---|
| `backend/app/natal/public_models.py` | add **optional, nullable, internal-only** metadata fields: `slide_role`, `voice_mode`, `valence_frame`, `origin_hint_eligible`, `deselected_trace`, `map_trace` |
| `backend/app/natal/natal_promise_packets.py` | populate the metadata on the semantic plan (NatalPromisePacketV1) for the pilot family only |
| `backend/app/natal/public_builder.py` | thread metadata through internally; **assert public payload unchanged** |
| `backend/app/natal/profile_detail_editorial.py` | attach `pattern_to_gift` profile + `origin_hint`/`gift` role tags internally (no text change in Phase 3) |
| `backend/app/engine/tone_apply.py`, `backend/app/narrative/humanize_tr.py` | **not modified in Phase 3** (their narrowing is Phase 4/6) |
| `backend/app/api/routes/natal_interpretation.py` | **not modified** (no endpoint/contract change in Phase 3) |

Exact insertion lines are confirmed during the approved
implementation, not guessed here.

## 5. Hard invariants (Phase-3 reversibility)

1. **Public output byte-identical.** A golden-snapshot test on the
   pilot chart's `/interpret/ui` payload must show zero diff. New
   fields are internal, not emitted, behind a build flag like A2.
2. ARC extraction/regression guards stay green (the frozen Pass-1 §4
   guards; `arc_corpus.py` score unchanged).
3. No `config/`, `core/config.py`, `main.py`, router, or `pubspec`/
   requirements change. No new package. No new endpoint.
4. If any of the above must change → **stop and ask**, do not proceed.

## 6. QA gates wired in Phase-3 (tests only, no public change)

- public-output golden snapshot diff = 0 (the gate of gates)
- banned-phrase scan (tone_aware §8) on internal candidate text
- `origin_hint` determinism scan: every passage ≥1 opt-out clause,
  zero event/blame/clinical tokens; eligibility list (packet §4)
  enforced; default opt-in (not inline)
- `gift` motivational-drift scan (packet §6 bad examples fail)
- Rules 1–4 structural checks (one-spine / thesis-once / lived-scene
  marker / rhythm-tag present)
- §13.3 side-by-side multi-chart read **prepared** (run in Phase 4,
  not Phase 3)

## 7. Explicitly OUT of scope (anti-scope-creep)

- Phase 4 renderer (actual copy change) — separate approval
- scannable-card surface (original §10.3 path)
- other profiles: `identity_polarity`, `held_plurality` (still §13.2
  proposed); other card families
- the **ARC scorer / A2 merge** question — untouched, still its own
  §10.3 owed; this plan does not merge or move it
- themes.yaml "emotional_base" question
- any Flutter/mobile change

## 8. Exit criteria → Phase 4 decision

Phase 3 done when: metadata populated for the pilot, all §6 gates
green, public snapshot unchanged, §13.2 review passed. Then a
**separate** go/no-go for Phase 4 (flagged tone-aware renderer on the
pilot family + §13.3 multi-chart QA + a product-validation read).
Phase 4 is where user-visible copy could change — gated again.

## 9. What approval here authorizes

Only: begin Phase-3 code (internal metadata + tests + snapshot guard)
on the single hidden/private pilot, after §13.2 review, within the §5
invariants. Nothing user-visible. Not Phase 4. Not A2. Not other
families.
