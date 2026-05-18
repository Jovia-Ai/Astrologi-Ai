# ARC v0.1 — Pass-1 Dry-Run Report (V2/V3)

> Scored ONCE per variant against the frozen pre-registration
> `arc_v0_1_pass1_dryrun_prereg.md`. No goalpost change. Dry-run =
> score-time `--experiment` transform; the committed salience formula
> and public output are untouched. **Result: a clean pre-registered
> negative — L2 and L3 as frozen add nothing over A2.**

## Setup

- V0 baseline: default scorer, no experiment flag
- V1 A2: `--experiment dryrun_a2_outer_endpoint_gate` (prior candidate)
- V2 A2+L2: `--experiment pass1_a2_l2`
- V3 A2+L2+L3: `--experiment pass1_a2_l2_l3`
- Production scorer default, gold files, extraction: all unchanged
- L2/L3 implemented faithfully to the frozen §2 rule text, run, scored
  once. No mid-run rule mutation (anti-circularity, prereg §6).

Artifacts:

- V0: `docs/system/_corpus/score_pass1_v0_baseline.json`
- V1: `docs/system/_corpus/score_pass1_v1_a2.json`
- V2: `docs/system/_corpus/score_pass1_v2_a2_l2.json`
- V3: `docs/system/_corpus/score_pass1_v3_a2_l2_l3.json`

## 1. Variant table

| Metric | V0 base | V1 A2 | V2 A2+L2 | V3 A2+L2+L3 |
|---|---:|---:|---:|---:|
| `n_scored` | 16 | 16 | 16 | 16 |
| extraction mean | 1.000 | 1.000 | 1.000 | 1.000 |
| extraction worst | 1.000 | 1.000 | 1.000 | 1.000 |
| salience mean (prov.) | 0.906 | 0.906 | 0.906 | 0.906 |
| salience worst (prov.) | 0.500 | 0.500 | 0.500 | 0.500 |
| **false_emphasis** | **11** | **4** | **4** | **4** |
| framing deferred | 46 | 46 | 46 | 46 |
| unsupported | `[final_dispositor]` | same | same | same |

**Per-family delta:** V2 − V1 = 0. V3 − V2 = 0. L2 and L3 each fired
on **zero** anchors. The entire FE reduction (11 → 4) is A2's; the two
new levers contribute nothing.

## 2. Remaining false_emphasis (identical V1 = V2 = V3)

| Chart | Claim | Resolves "defining" via |
|---|---|---|
| 1985 istanbul | Neptune Cap 2 as a personal headline | `tight_aspect` → **Pluto** |
| 1994 helsinki | Mars Cancer 4 fall as whole identity | `planet_placement` Mars |
| 1994 helsinki | Mars/Mercury pressure as headline | `tight_aspect` → Mercury |
| 2002 helsinki | Venus Virgo 4 fall as main wound | `planet_placement` Venus |

## 3. Why each frozen lever did not fire (diagnostic, not a fix)

### L2 (tightness cap) — pre-registered MUST "resolve 1985": **NOT MET**

The frozen L2 rule caps a both-outer tight aspect *only if neither
endpoint is angular, a luminary, or the chart/MC ruler*. In 1985 the
Neptune–Pluto sextile's endpoint **Pluto is angular** (1st house,
Scorpio, domicile — it is in `angular_planets`). So
`_endpoint_structural(Pluto)` is true and the L2 guard correctly
declines to cap — *faithful to its own frozen text*.

Deeper cause: the 1985 anchor resolves `defining` **through Pluto, not
Neptune**. Pluto in 1H domicile is a genuinely strong personal placement;
the must_not is about *Neptune* not being a headline, but the
`tight_aspect` member-max attributes the aspect's loudness to its
strong endpoint. This is a **scorer-attribution** matter (a must_not
anchored on the weak member of an aspect inherits the strong member's
tier), entirely outside what L2 was designed to catch. The §2
expectation was written against an idealized "purely generational
Neptune–Pluto"; the real chart has an angular, domiciled Pluto.

### L3 (owner priority) — pre-registered MUST "help 1994/1982": **NOT MET**

- **1982** Moon–Uranus was already resolved by A2 (not in the A2
  remaining set), so L3 had nothing to act on.
- **1994** rank-1 defining_signature primary anchors are
  `house_concentration` + `planet_placement Sun` + `planet_placement
  Pluto`. Frozen L3 condition 1 requires *all* rank-1 primary anchors
  to be owner-type (`chart_ruler`/`mc_ruler`/`luminary`/
  `house_concentration`). `planet_placement` is not owner-type, so the
  owner-spine test fails — *faithful to the frozen text*.
- The 1994 Mars FE is a `planet_placement` anchor; L3 condition 2 only
  suppresses elements loud *solely via* `tight_aspect` /
  `house_concentration`. Mars is loud via its own fall/placement, so L3
  correctly excludes it by design.

L3 is inert on the entire 16-set: no rank-1 signature in the corpus has
an all-owner-type primary anchor set that also resolves all-`defining`
while a purely-secondary exact participant is flagged.

## 4. Pre-registered regression guards (§4) — ALL GREEN

- extraction mean/worst 1.000 / 1.000 — unchanged across V2, V3
- salience mean/worst 0.906 / 0.500 — unchanged
- canonical 4, 1973/1975/2010 no-dominant, 1972 angular+afflicted,
  1985 relationship, 2007 12H: per-chart FE identical to A2 — **no
  regression, no fabricated spine, no whole-identity collapse**
- no genuinely-personalised outer suppressed (L2 inert)
- no secondary-visibility fix introduced (L3 inert; deferred levers
  stayed deferred)
- FE increased on **zero** charts under V2 or V3

The negative result is *safe*: the levers did no harm; they simply did
no work as frozen.

## 5. §5 target-commit (non-circular)

Per prereg §5 the committed numeric target = the achieved
`false_emphasis` of the best clean variant. **Best clean variant = A2,
FE = 4.** L2/L3 did not lower the floor. The committed Pass-1 target is
therefore **FE ≤ 4**, met only by A2 (= V1 = V2 = V3).

## 6. §6 anti-infinite-loop binding

The diagnosis surfaces, but does **not** fix, three issues. Each is
logged to the post-ship backlog and is **out of Pass-1 scope**:

1. **Scorer attribution**: a `salience`-kind must_not anchored on the
   weak member of a tight aspect inherits the strong member's tier
   (1985 Neptune via Pluto). Candidate: tier a `tight_aspect` must_not
   by the *named/weak* endpoint, not member-max. Needs its own
   pre-registration.
2. **L3 owner-spine definition** is too strict for real golds whose
   rank-1 mixes `house_concentration` with `planet_placement` (1994).
   Any relaxation is a redesign → separate scheduled pass.
3. **Lone angular debility** (2002 Venus 4 fall; 1994 Mars 4 fall):
   a single afflicted angular planet read as whole-chart wound. Not in
   §2 families; new family → separate pre-registered pass.

Redefining L2/L3 now to chase these would be exactly the
goalpost-moving the pre-registration exists to prevent. Not done.

## 7. Decision

- **Merge NOT authorised** (prereg §5/§7). L2/L3 add nothing, so there
  is no new merge candidate; A2 remains the only FE-reducing transform
  and is still a *dry-run experiment*, not production.
- A2 (FE = 4) still requires the mandatory **§10.3 Product-Validation
  Checkpoint** (one chart end-to-end through the real voice/slide path,
  astrologer blind to scorer) before any merge is even considered.
- Pass-1 is **closed** with a documented negative for L2/L3. The three
  §6 backlog items are the input to a *future, separately
  pre-registered* pass — not an extension of this one.

This report is the deliverable. No coefficient change, no public output
change, no merge.
