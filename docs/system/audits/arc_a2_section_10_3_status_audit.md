# ARC/A2 §10.3 — Status Audit

## Scope

Trace + design-state audit. No code, no production change.

Inputs:
- `scripts/arc_corpus.py` (A2 implementation)
- `backend/app/astro/chart_skeleton.py` (ARC v0.1 spec implementation)
- `backend/app/api/routes/natal_interpretation.py` (canonical natal pipeline)
- `docs/system/arc_v0_1_calibration_design_proposal.md` (§10 ship gate definition)
- `docs/system/arc_v0_1_pass1_dryrun_report.md` (A2 / L2 / L3 result)
- `docs/system/arc_v0_1_product_checkpoint_1985.md` (the §10.3 checkpoint #1 doc)
- `docs/system/arc_v0_1_product_checkpoint_1985_BLIND.md` (the blind read sheet)

Question this audit answers:

> The session started with ARC/A2 §10.3 product-validation checkpoint as the
> open ship gate. After many turns of voice consolidation work, what's
> A2's actual current state, and what does completing §10.3 actually require?

## Executive verdict

**A2 §10.3 is much closer to closure than the session's open-ticket
framing suggested.** Three findings:

1. **A2 was always design-only, never production-wired.** It lives in
   `scripts/arc_corpus.py` as a score-time `--experiment` transform.
   No production code path reads it. Therefore "merge A2" was always
   semi-aspirational; the actual gate was design-acceptance via §10.3,
   not production code rewiring.

2. **§10.3 is a MANUAL checkpoint by design** — the calibration
   proposal explicitly says "take one chart ... blind judge the
   felt-experience output." No production wiring required for §10.3
   itself.

3. **The 1985 checkpoint doc is ~90% done.** Engineering-side trace
   (sections 1–4 of the doc, the prototype output, the blind sheet) is
   complete. Only the **blind verdict** (section 5) is outstanding.
   Recorded engineering status: "REVISE (pending blind verdict)".

**Recommendation: Path M (complete the blind verdict on the existing
1985 checkpoint). Path E (engineered production wiring) is a separate,
much-later conversation that §10.3 does NOT depend on.**

## 1. A2's actual code position

`scripts/arc_corpus.py` line 347:
```python
_A2_EXPERIMENTS = {
    "dryrun_a2_outer_endpoint_gate", "pass1_a2_l2", "pass1_a2_l2_l3"}
```

A2 is a `--experiment` value to the `cmd_score` CLI command. It's a
score-time transform applied to gold-tagged corpus charts to test
whether changing salience rules reduces `false_emphasis`.

**It is never invoked at runtime.** No production code imports or calls
the A2 logic. The natal `/interpret` route uses `primitive_engine_v2`
+ `master_selector` + `signature_engine` + `promise_vector_engine` —
none of which read chart_skeleton's salience formula or A2's transforms.

## 2. `chart_skeleton.py` — also not in production

`backend/app/astro/chart_skeleton.py` is the ARC v0.1 spec
implementation (Half-A extraction + Half-B salience formula). Carries
`_uncalibrated: true` marker.

Repo-wide consumer scan: **zero imports of `chart_skeleton` from
`backend/app/`**. The file exists as the data contract reference
implementation; it is consumed only by the corpus tooling
(`scripts/arc_corpus.py`) for dry-run scoring. The production pipeline
runs through entirely different engines.

**Implication**: even the "committed" salience formula in
`chart_skeleton.py` (the pre-A2 baseline) is not what production uses.
A2 vs baseline is a comparison *within the dry-run / spec layer*, not
a comparison of production behaviors.

## 3. §10.3's actual design

`arc_v0_1_calibration_design_proposal.md`:
> "**10.3 Product-Validation Checkpoint (proxy ↔ felt experience)**
> After Pass-1 dry-run passes 10.2.1–10.2.5, before declaring the gate
> met: take **one** chart (recommended: a canonical reference whose
> gold...)"

The checkpoint is:
- ONE chart
- Trace the scorer (A2) output → semantic plan → surface plan → voice
  output (manual; no production pipeline required)
- Have a scorer-blind judge read the voice output
- Verdict: PASS / REVISE / FAIL

**No production code change is required for §10.3.** The matrix §11
already says "ARC/A2 §10.3 is fully orthogonal; can run any time."
The checkpoint validates the *design hypothesis* (A2 selection →
felt-quality output), not the *production wiring* (does the natal
route use A2).

## 4. The 1985 checkpoint's actual state

`arc_v0_1_product_checkpoint_1985.md` exists in repo. Reading its
status:

- **Sections 1–3**: ARC internal summary (scorer-aware), surface plan,
  voice handoff. Complete.
- **Section 4**: prototype output — parent card + 5 slides + share
  line. Complete. (This is the V0 voice quality — predates the v4 LOCK
  reference voice work that came later.)
- **Section 5**: felt-experience blind read sheet for a scorer-blind
  judge to fill. **EMPTY** — no verdict recorded.
- **Section 6**: engineering non-blind note — recorded recommendation
  is **REVISE** ("promising, not yet production-ready"). Specifically:
  - "Blind verdict outstanding — §10.3 is not satisfied until a
    scorer-blind reader completes section 5"
  - 5 production-integration blockers listed (these are operational
    items, not §10.3 prerequisites)
- **Section 8**: status = "REVISE (pending blind verdict)"

`arc_v0_1_product_checkpoint_1985_BLIND.md` exists; the prototype
output is there for the blind reader; verdict field is empty.

**The single outstanding item for §10.3 closure is the blind verdict
on the existing 1985 BLIND sheet.**

## 5. One real complication — the prototype is V0 voice quality

The 1985 prototype output (section 4 of the checkpoint doc) was
hand-authored BEFORE the voice quality iterations that came later in
the session:

- Session arc later produced v0 → v1 → v2 → v3 → v4 → v4.1 → LOCK
  on a DIFFERENT chart (2007 deep_read reference)
- The LOCK PASS we recorded was on the 2007 chart, NOT on the 1985
  prototype

So the 1985 BLIND sheet shows V0-era voice quality. If the user judges
it now, voice quality limitations will contaminate the A2 selection
verdict. Two options within Path M:

### Path M-strict — judge the V0 prototype as-is

- Honors the original §10.3 design (snapshot from when A2 candidate was
  defined)
- Cleaner *historical* verdict, muddier *forward* verdict
- Risk: voice quality, not A2 selection, drives the blind verdict
- Cost: minimal (user reads existing BLIND sheet, writes verdict)

### Path M-refreshed — regenerate the 1985 prototype with v4 voice quality, then blind-judge

- Cleaner separation of "selection quality" (A2) from "voice quality"
  (LOCK voice contract Rules 1–4)
- Tests A2's selection through the *current* voice machinery
- Cost: regenerate prototype (~1 hand-authoring pass like v4
  reference); refresh BLIND sheet; user reads and verdicts
- This is what a faithful §10.3 verdict would look like *today*, given
  voice tier consolidation since the original checkpoint

## 6. Path E — engineered production wiring (separate, much later)

If A2's design hypothesis is accepted, the question of "does A2 actually
run in production" is a much larger downstream conversation. It would
involve:

- Choosing a Plan-layer engine to modify (likely `primitive_engine_v2`
  + `promise_vector_engine`, possibly `master_selector`)
- Designing how A2's salience tiers (defining / strong / background)
  map into those engines' existing scoring logic
- §13.2-style review + bounded implementation request + parity tests
- Mobile/Chart Lab contract considerations
- Phase-4 deep_read consumer impact

**§10.3 does NOT require any of this.** Path E is a multi-PR backend
consolidation conversation that is its own arc. §10.3 closes
independently.

## 7. Recommendation

**Path M-refreshed**, then close §10.3.

Concrete sequence:

1. **Regenerate the 1985 prototype** with v4 voice quality + LOCK
   reference style, applied to A2's selection of 1985. Single
   hand-authoring pass, same B0–B5 voice rules.
2. **Refresh the BLIND sheet** with the new prototype content. Empty
   verdict field for user to fill.
3. **User reads BLIND sheet scorer-blind, records verdict** (PASS /
   REVISE / FAIL).
4. **If PASS**: §10.3 closed. A2 is design-accepted as the calibration
   target. Update matrix: A2 status = "design-accepted via §10.3,
   production wiring deferred to a separate later conversation
   (Path E)." Original §10 ship gate met for the calibration question.
5. **If REVISE**: surface specifically what didn't feel seen — likely
   selection-level issue (e.g. A2 chose wrong defining signature for
   1985). Then either: (a) iterate prototype within the constraint
   that voice quality is locked + A2 selection is the variable; (b)
   conclude A2 isn't the right calibration after all and reopen the
   pre-registered Pass-2 conversation.
6. **If FAIL**: A2 design is not viable as currently structured.
   Significant rework needed; outside §10.3's bounded scope.

This honors the original §10 ship gate language ("after Pass-1 passes,
before declaring the gate met, ONE chart through product path") while
acknowledging that the voice work since the original 1985 checkpoint
gave us better voice machinery — using the OLD voice quality would
unfairly disadvantage A2's selection verdict.

## 8. What Path M does NOT close

Path M closes §10.3 (the design-acceptance question).

Path M does NOT close:
- Production wiring of A2 into the natal pipeline (Path E)
- Whether all charts in the corpus benefit from A2 (only one chart
  is judged — §10.3 design intent)
- Whether voice quality scales to multi-chart variant pool (that's
  S4b territory)
- Phase-4 hidden/private adapter rewire for A2-aware selection
  (separate)

These are all real questions but they're not §10.3 questions. The
§10 ship gate is satisfied by §10.3 PASS; downstream wiring is a
later product engineering decision.

## 9. Risk notes

### Risk 1 — assuming PASS means "ship A2 in production"
PASS on §10.3 = design-acceptance, NOT production wiring authorization.
Documenting this distinction in the matrix update prevents future
readers from thinking A2 is "in production" just because §10.3 closed.

### Risk 2 — voice quality contamination of selection verdict
This is exactly why Path M-refreshed (not M-strict) is recommended.
The original V0 prototype would conflate selection and voice issues.
Path M-refreshed isolates the variable.

### Risk 3 — REVISE/FAIL re-opens a treadmill
The §10 anti-treadmill discipline says max one more hand cycle on
calibration. If §10.3 REVISES, the response must be small bounded
iteration OR conclusion that A2 isn't the answer, NOT an unbounded
re-calibration loop.

### Risk 4 — Path E may never happen
A2 may stay design-accepted but never get wired into production. That's
acceptable IF the production pipeline's existing engines
(`primitive_engine_v2` + `promise_vector_engine` + `master_selector`)
deliver felt-quality output without A2's specific transform. The §10.3
verdict on 1985 doesn't tell us this for other charts. Path E would
require its own much larger validation arc.

## 10. Suggested matrix updates after §10.3 closes

If §10.3 PASS:
- Matrix §11 row updates: "ARC/A2 §10.3 fully orthogonal; can run any
  time" → "ARC/A2 §10.3 PASSED on YYYY-MM-DD; A2 design-accepted;
  production wiring is Path E, a separate later conversation"
- Open question §14 closes for §10.3 specifically
- Matrix gains an explicit "Path E open" line for the production
  wiring discussion (not yet authorized, no specific timeline)

If §10.3 REVISE/FAIL: matrix records the verdict + the chosen response
(bounded iteration OR new pre-registration).

## Final recommendation

Run §10.3 via Path M-refreshed. Single hand-authoring pass to refresh
the 1985 prototype with v4 voice quality, then user blind-reads, then
verdict. This is the smallest meaningful step that closes the session's
oldest open ticket.

No production code change. No matrix structural change. Just close
§10.3 and record the outcome.
