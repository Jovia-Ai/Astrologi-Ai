# ARC v0.1 — Gold Authoring Guide

> Single source of truth for the corpus volume phase. Consolidates rules
> that accreted across PR-2a/b/c and the 4 reference golds. Anyone
> filling a gold worksheet follows THIS. The scorer matches anchors
> only — never prose.

## The 4 canonical worked examples (read these first)

| Reference | Type it teaches |
|---|---|
| `_corpus/gold/1962-01-07_10-30_nairobi.json` | single strong spine (Saturn-Capricorn) |
| `_corpus/gold/1993-03-09_08-50_helsinki.json` | debilitated chart-ruler / personal strain |
| `_corpus/gold/1973-08-05_01-20_istanbul.json` | no-dominant / multi-centred (close ranks) |
| `_corpus/gold/1972-10-12_15-20_istanbul.json` | angular-heavy + affliction cluster |

A new gold should resemble the one closest to its type in structure.

## The 10-step method (apply in order)

1. luminaries → 2. angles + chart ruler → 3. dignity →
4. tightest aspects → 5. stellium / final dispositor → 6. synthesis →
7. ranked `defining_signatures` → 8. `core_tension` →
9. `must_not_lead_with` → 10. `one_line_person`

The gold is the answer key — what a correct reading LEADS WITH (ranked),
plus what it must NOT lead with. **Not personal taste: the method.**

## Field model — human vs machine

- **Human fields** (you write, applying the method): `what`, `why`,
  `between`, `claim`, `reason`, `one_line_person`, `_note`.
- **Machine fields** (`anchors`): derived from the worksheet placement
  table (planet/sign/house/dignity, stellium, tight_aspect, ascendant,
  mc). Tool-proposed, you only approve/correct. **Scored, not prose.**

## Anchor schema

Each anchor: a `type` plus the fields that type needs. Optional `role`.

Supported anchor types (scorer checks these): `planet_placement`,
`luminary`, `ascendant`, `mc`, `chart_ruler`, `mc_ruler`,
`angular_planet`, `dignity`, `stellium`, `tight_aspect`,
`house_concentration`.

Reported-but-unsupported (NEVER scored as engine failure):
`final_dispositor`, `dispositor_chain`, `axis_emphasis`. Use them in
prose/`why` freely; as anchors they are noted, not failed.

Field cheatsheet:
- `planet_placement` / `dignity` / `luminary`: `planet` [+`sign`
  +`house` +`dignity`]
- `chart_ruler` / `mc_ruler`: `planet` [+`sign` +`house` +`dignity`]
- `ascendant` / `mc`: `sign`
- `angular_planet`: `planet` [+`house`]
- `stellium`: `by` (`sign`|`house`), `key`, `min_count` (default 3)
- `house_concentration`: `house`, `min_count` (default 3)
- `tight_aspect`: `a`, `b`, `aspect`, `max_orb`

### `role` (on defining/core/secondary anchors)

- `primary_anchor` (default if absent): carries the rank expectation,
  IS scored for salience.
- `supporting_route` / `context`: the route not the light. A salience
  tier mismatch is an informational note, NOT a hard miss, excluded
  from the alignment ratio. Use for a chart-ruler/MC-ruler that
  channels but should not outrank a dignified primary (see 1973: Sun
  primary, Mercury chart-ruler supporting_route).

### `kind` (on every `must_not_lead_with` item — REQUIRED)

- `salience`: "don't make this minor/generational thing the spine."
  SCORED — its anchored subject must NOT be 'defining'. (e.g. peregrine
  generational outer planets.)
- `framing`: "don't render this genuinely-salient feature clichely."
  The anchored thing IS legitimately salient; a Voice-Gate concern,
  recorded and deferred, NEVER scored as a salience failure. (e.g.
  "Leo Sun as a generic showman" — the Sun IS the spine.)

Missing `kind` defaults to `framing` (never false-flag a real spine).

## Rank semantics

Ranks may be close (1973, 1972) — that closeness is data, add a `_note`
("multi-centred; ranks intentionally close"). Scorer policy
(UNCALIBRATED): only **rank 1 must be 'defining'**; rank 2+ satisfied by
'defining' or 'strong'.

## Locked invariants (do not violate when authoring)

- Salience is UNCALIBRATED scaffold; gold encodes the *correct reading*,
  not the engine's current numbers. Author blind to engine salience
  where possible (read from placements, not from score output).
- Extraction is the stable gating metric; salience is provisional and
  never gates.
- `anchors` are the only scored content. Prose is for humans/voice.
- Generational outers (peregrine, no tight personal aspect) → expect
  background; encode as a `salience`-kind must_not when relevant.

## Chart selection rule (volume phase)

Every new chart must answer: **"what salience behaviour does this chart
test?"** Don't add charts that test nothing new. Planned type sequence
(each a generalization test, no longer target-discovery):

1. relationship-heavy → 2. 12H / hidden-heavy →
3. soft-aspect / gift-heavy → 4. hard-aspect / T-square-heavy →
5. career / MC-heavy → 6. dignity-heavy, low-angular →
7. debility-heavy, no-angular → 8. 2nd no-dominant (Q3 guard)

T-square-heavy is high-value: likely surfaces a tightness-cluster /
hard-aspect-loudness question (the aspect analogue of calibration Q1).

## Blind-batch discipline (volume phase — PROCEDURAL, not intent)

The hypothesis-building phase used iterative read→reveal→verify and that
was correct. The volume phase MUST NOT: iterative per-gold scoring lets
the author (even unconsciously) tune the next gold to the last reveal,
which quietly makes the corpus circular and destroys the statistical
generalization evidence. Therefore:

1. Author a whole batch (e.g. relationship + 12H + gift + T-square)
   blind to engine salience, reading only the placement table.
2. Each gold carries a pre-registered `_audit_note` (below), written
   and committed BEFORE any score run, IMMUTABLE afterwards.
3. Commit the whole batch.
4. Run `scripts/arc_corpus.py score` **once** over the batch.
5. Only then interpret, against pre-registered `_audit_note`s and
   `arc_v0_1_salience_calibration_questions.md`.

A genuinely ambiguous chart may be escalated to a collaborative read —
but still authored blind and pre-registered before any reveal.

### `_audit_note` (REQUIRED, pre-registration, immutable)

```json
"_audit_note": {
  "tests_behavior": "what salience behaviour this chart probes",
  "main_risk": "the specific over/under-promotion this chart could expose",
  "expected_failure_if_bad": "what a bad engine would do here",
  "calibration_question_link": "Q1 | Q2 | Q3 | new"
}
```

Written before the score reveal; never edited after. It is
pre-registration (the discipline that made the 1972 test trustworthy),
not post-hoc rationalisation.

## Workflow

1. Pick a chart by the selection rule (a type not yet covered).
2. Open its worksheet; read placements; apply the 10-step method
   BEFORE looking at any engine salience.
3. Fill human fields; let the tool propose anchors; approve/correct;
   set `role` and `kind`; write the pre-registered `_audit_note`.
4. Save to `_corpus/gold/<chart_id>.json`; commit (still blind).
5. Repeat for the whole batch; escalate genuinely ambiguous charts to a
   collaborative read (still blind + pre-registered).
6. After the batch (~8–12 scored): run `scripts/arc_corpus.py score`
   ONCE and do the first statistical salience evaluation against
   `arc_v0_1_salience_calibration_questions.md`.

First batch target (selected blind, extraction-only):
`1985-06-20_15-50_istanbul` — Venus Taurus 7th domicile; tests whether
the engine over-promotes a textbook relationship significator into a
fake whole-identity spine.

## Domain-monopolization guard (relationship-heavy, and any domain-heavy)

A domain-heavy chart (relationship-, career-, 12H-heavy …) is selected
to probe ONE risk: **does the engine let that domain's signals become
the whole-identity spine, erasing the rest of the chart?**

This is NOT cleanly a `salience` or `framing` must_not — the domain
signature (e.g. Venus domicile 7th) IS legitimately defining; the
failure is *monopolization* (it becomes the ONLY defining centre →
false single spine). Do NOT add a new `kind` for this — it is already
measurable through the existing mechanism, conditionally:

- If the chart has a genuine NON-domain centre: the gold MUST include
  it as a defining_signature. Then monopolization shows up as an
  extraction/salience MISS on that non-domain signature — measured, no
  new schema.
- If the chart is genuinely domain-monocentric: the gold says so; the
  test inverts to non-fabrication ("did the engine invent a false other
  centre?").

The `_audit_note` MUST pre-register which case this chart is, so the
probed failure mode is locked before any reveal. Never force a
non-domain signature into a gold that the chart does not support — a
gold that lies about the chart defeats the test.

Every domain-heavy gold also carries the Voice-Gate reminder:

```json
{ "claim": "<domain> as the whole identity",
  "kind": "framing",
  "reason": "<domain> signatures are strong but must not erase the rest
             of the chart", "anchors": [] }
```

This is recorded/deferred (not scored — it is framing); the actual
monopolization test is the non-domain defining_signature above.

Pass shape per chart: extraction 1.0; salience misses only where a
calibration question predicts them; generational stays background;
false_emphasis(salience-kind)=0; multi-loaded charts not collapsed to a
false single spine.
