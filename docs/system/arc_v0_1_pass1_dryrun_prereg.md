# ARC v0.1 — Pass-1 Dry-Run Pre-Registration & Lever Spec

> Frozen BEFORE running, per §10.2.3 / §10.4 of the Calibration Design
> Proposal. Pre-registration prevents goalpost-moving: the per-family
> success criteria and the regression guards are committed here, before
> any number is seen. Design/doc only — no code, no merge, no public
> output change. A dry-run is a score-time `--experiment` transform
> (like A2); it never edits the committed salience formula.

## 1. Baseline (committed, un-experimented)

```
n_scored = 16
extraction mean/worst = 1.000 / 1.000
salience mean/worst    = 0.906 / 0.500
false_emphasis         = 11
framing deferred       = 46
unsupported            = ["final_dispositor"]
```

A2 (`dryrun_a2_outer_endpoint_gate`, already accepted as candidate)
reduced false_emphasis meaningfully with no canonical regression.
Remaining false_emphasis under A2:
- `1985` Neptune Capricorn 2 (outer–outer exact generational)
- `1994` Mars fall headline + Mercury-led pressure
- `2002` Venus fall headline (lone angular debility)

Pass-1 = A2 **plus** two new levers, **stacked**, run as attributable
variants (never conflated in one run).

## 2. Levers — precise deterministic definitions

### Lever 2 — Contextual tightness cap (`pass1_l2_tightness_cap`)

Problem family: exact generational aspect inflation (§3.2) — a partile
aspect between two purely generational outers reads like a headline.

Rule (score-time, stacks on A2): when resolving a `tight_aspect`
anchor's engine tier, if **both** endpoints are outer/generational
(Uranus, Neptune, Pluto) **and** neither endpoint is angular, a
luminary, or the chart/MC ruler, then the aspect tier is **capped at
`strong`** (cannot resolve `defining`) regardless of orb.

Astrologically principled: a tight Neptune–Pluto is real but it is a
generational signature, not a personal headline, unless an endpoint is
personalised by house/luminary/ruler. Does NOT touch exact aspects with
a personal/luminary/ruler/angular endpoint.

Pre-registered expectation:
- MUST resolve: `1985` Neptune-Pluto false_emphasis.
- MUST NOT regress: any chart where a tight outer aspect is genuinely
  personalised (angular outer / outer = chart-or-MC ruler / outer tied
  to a luminary). Canonical 4, 1973/1975/2010 no-dominant unaffected.

### Lever 3 — Structural owner priority (`pass1_l3_owner_priority`)

Problem family: exact pressure vs true structural owner (§3.4) — a
secondary exact aspect behaves like the chart owner when a denser
structural owner already exists.

Rule (score-time, stacks on A2+L2): a salience-kind must_not
false_emphasis flag is **suppressed** for an anchored element IF ALL:
1. the chart has ≥1 rank-1 defining_signature whose primary anchors are
   owner-type (`chart_ruler` / `mc_ruler` / `luminary` /
   `house_concentration`) and all matched at `defining`; AND
2. the flagged element is loud ONLY via `tight_aspect` /
   `house_concentration` membership / exactness; AND
3. the flagged element is NOT itself owner-type (not chart/MC ruler,
   not a luminary, not angular, not in the rank-1 anchor set).

I.e. a clearly-established structural owner is privileged; a purely
secondary exact participant does not get counted as a competing owner.
It does NOT mute charts where the aspect IS the owner (then condition 3
fails — the element is owner-linked — so no suppression).

Pre-registered expectation:
- MUST help: `1994` exact-pressure-vs-6H-owner family; `1982`
  Moon-Uranus exact-soft vs stronger pressure spine.
- MUST NOT regress: hard-aspect / T-square charts where the aspect is
  legitimately the owner (1972 angular+afflicted must keep its valid
  multi-loaded structure); no canonical regression.

Lever 3 is rated medium-low readiness in the proposal — run it as a
SEPARATE stacked variant so its effect is attributable and revertible.

## 3. Run plan (attributable, score-once per variant)

Score the 16-gold set under each, in order, comparing to the prior:

```
V0  baseline (committed)                         FE = 11   [known]
V1  A2                                            FE ≈ 4    [known]
V2  A2 + L2 (tightness cap)
V3  A2 + L2 + L3 (owner priority)
```

Each variant: extraction, salience mean/worst, false_emphasis,
framing-deferred, unsupported, per-family delta, charts improved,
charts harmed, regression-guard pass/fail. No goalpost change on WHICH
families/charts count (frozen in §2).

## 4. Pre-registered regression guards (frozen)

A variant is acceptable only if (Calibration Proposal §6 + §10.2):
- extraction mean/worst stays 1.000 / 1.000
- canonical 4 references still pass pre-registered criteria
- 1973 / 1975 / 2010 no-dominant: no fabricated single spine
- 1972 angular+afflicted: valid multi-loaded structure preserved
- 1985 relationship / 2007 12H: no whole-identity collapse
- no genuinely personalised outer is suppressed
- no secondary-visibility fix sneaks in (deferred levers stay deferred)

## 5. Target-commit & merge gate (non-circular reading of §10.2.3)

Pre-registration freezes the **qualitative** criteria (§2 expectations,
§4 guards, the no-goalpost rule). The **numeric** false_emphasis target
is committed AFTER the dry-run reveals the achievable floor but BEFORE
any merge decision — the calibration owner records the achieved
`false_emphasis` of the best clean variant as the committed target;
the eventual merged pass must meet it.

Merge is NOT authorised by this dry-run. Per Calibration Proposal §8 +
§10.2.6, merge requires: all §4 guards green, the committed target met,
**and the §10.3 Product-Validation Checkpoint passed** (one chart end
to end through the real voice/slide path, astrologer blind to scorer).
A passing dry-run only authorises proceeding to that checkpoint.

## 6. Anti-infinite-loop binding (§10.4)

Any NEW false_emphasis family that L2/L3 surface (not in §2) is logged
to the post-ship backlog; it does NOT extend Pass-1. Pass-1 is bounded
to the families named in §2. Further families = a separate scheduled
pass with its own pre-registration.

## 7. Decision

This document is the frozen Pass-1 design. Next action: implement L2,
then L3, as stacked score-time `--experiment` variants (non-production,
like A2), run V2 and V3, produce the dry-run report against the frozen
§2/§4 criteria. No merge, no coefficient change, no public output —
the report feeds the §5 target-commit and the mandatory §10.3 product
checkpoint.
