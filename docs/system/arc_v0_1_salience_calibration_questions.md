# ARC v0.1 — Salience Calibration Questions

> The PR-2 final-calibration guide. Salience is shipped UNCALIBRATED
> (`_salience_meta._uncalibrated: true`). These are the questions the
> stratified corpus must answer to calibrate it. Each was surfaced
> STRUCTURALLY from the contrasting reference golds, before any
> calibration — not invented. **Living document: 4 references surfaced
> 3 questions; more references (planned new types) will surface more.**

## Invariant for any calibration change

A calibration change is only acceptable if it:

1. Keeps **extraction coverage** unchanged (salience never touches
   extraction; it stays the stable gating metric).
2. Does **not regress** the 4 reference golds' passing state
   (single-spine / debilitated-ruler / no-dominant / angular+afflicted).
3. Is **astrologically principled**, not curve-fit to a specific chart.
4. Is validated against the **no-dominant reference (1973)** as the
   anti-false-spine guard (see Q3 — calibration questions are coupled).

---

## Q1 — Isolated affliction loudness

**Status:** addressed by an UNCALIBRATED hypothesis (the affliction-
cluster term); the *shape* of the term is the open calibration.

**Evidence trail:**
- PR-2a (2 refs): an isolated debilitated planet with no other role
  scores 'background' — Helsinki Mars (Cancer fall) → 0.24. But the gold
  ranks the Mercury/Venus/Mars debilitation as the chart's #2 struggle.
  Locked principle: debilitated = loud (in context, not in isolation).
- Hypothesis: a debilitated *personal* planet gets `+(n-1)*0.04` only
  when `n>=2` personal planets are debilitated (systemic strain).
- Validated directionally (3 refs, zero regression) and generalized
  (1972, 4th ref): Helsinki Mars → 'strong'; Nairobi (1 debility) →
  zero change; 1972 Jupiter-fall correctly excluded (social, not
  personal) — the boundary held on a new chart.

**Open calibration questions for the corpus:**
- Is `(n-1)*0.04` the right shape, or sub-linear / capped at large `n`?
  (A chart with 4+ debilitated personal planets — does each really keep
  gaining, or does it plateau?)
- Should the cluster bonus be sect-modified (day/night) or
  house-modified (a debilitated personal in an angular house vs cadent)?
- Is `n>=2` the right cluster threshold, or `>=3`?
- Personal-planet set: keep {Sun,Moon,Mercury,Venus,Mars}? (Chart ruler
  is handled separately; should a debilitated chart-ruler that is also
  personal double-count?)

**Corpus must measure:** charts with exactly 2, 3, 4+ debilitated
personal planets across day/night and angular/cadent, scored against
astrologer gold ranks, to fit `k`, the shape, and the threshold.

---

## Q2 — Dignity vs tightness compression

**Status:** observed, NOT addressed. The single clearest unaddressed
calibration target.

**Evidence trail:**
- 1973 (3rd ref, no-dominant): Moon Scorpio **fall** scores 0.48
  ('defining') while Sun Leo **domicile** scores 0.42 ('defining',
  barely) — a fallen luminary outscoring a domiciled one. Cause: the
  tightness modifier (+0.12 for ≤1° orb) swamps the dignity gap
  (domicile +0.12 vs fall +0.06 = only 0.06). The Moon happens to be in
  a tight trine; the Sun is in no tight aspect.
- Both still clear 'defining', so this did NOT surface as a scorer miss
  — it lives in the raw salience numbers, not the tier verdict. It is a
  *calibration* observation, not a scorer failure.

**The tension (why it is not obvious):**
- Astrologically a domiciled luminary arguably should rank ≥ a fallen
  one, all else equal.
- But a partile aspect IS genuinely loud — tightness deserves real
  weight.
- The question is the **relative ceiling**: how far should an accident
  of orb be allowed to override essential dignity?

**Open calibration questions:**
- Widen the dignity gap (domicile ≫ detriment/fall) so dignity is not
  swamped? Or cap the tightness contribution relative to the planet's
  dignity? Or both?
- Does the answer interact with Q1 (the affliction-cluster term already
  lifts debilitated planets — over-correcting Q2 on top could double-
  count)? **Q1 and Q2 are coupled — calibrate jointly, not in sequence.**

**Corpus must measure:** charts pairing a dignified-but-aspectless
luminary against a debilitated-but-tightly-aspected one, against
astrologer judgment of which is more chart-defining.

---

## Q3 — Absolute vs chart-relative tier thresholds

**Status:** observed on the 4th reference; the most architecturally
consequential question, and the one with a counter-risk.

**Evidence trail:**
- 1972 (4th ref, angular-heavy + no dignified planet + afflicted
  cluster): 7 of 10 planets scored 'defining'. The gold predicted a
  maximally-loud, multi-loaded chart, so this is defensible — but it
  raises whether 'defining' loses discriminating power when most of the
  chart clears the absolute threshold.

**The counter-risk (why this is NOT a simple fix):**
- Absolute thresholds (current): an extremely loud chart saturates
  'defining'; an extremely flat chart may have nothing 'defining'.
- Chart-relative thresholds (percentile / z-score within the chart):
  fixes saturation BUT would **manufacture a spine on a genuinely
  no-dominant chart** — forcing a top-percentile element to 'defining'
  even when nothing is truly loud. That is exactly the false-spine
  failure the absolute system was praised for NOT doing on 1973.
- So Q3 is coupled to the no-dominant reference: any relative scheme
  MUST be validated to still produce a flat/multi-centred reading on
  1973 (and the planned 2nd no-dominant reference), not a fabricated
  single spine.

**Open calibration questions:**
- Hybrid: absolute floor (nothing below X is 'defining' however
  top-ranked) + relative ceiling (cap how many can be 'defining')?
- Or chart-loudness normalization only above a saturation point?
- Either way: 1973-type charts are the regression guard.

**Corpus must measure:** the full loudness spectrum — maximally-loud
(1972-type), flat/no-dominant (1973-type), and mid — scored against
astrologer gold, to choose a scheme that discriminates on loud charts
WITHOUT fabricating spines on flat ones.

---

## Coupling summary (do not calibrate independently)

```
Q1 (affliction loudness)  ─┐
                            ├─ jointly: both lift debilitated planets;
Q2 (dignity vs tightness) ─┘   over-correcting either double-counts
Q3 (absolute vs relative) ──── guarded by the no-dominant reference(s):
                               a relative scheme must NOT reintroduce
                               the false-spine the absolute one avoids
```

## What the corpus owes this document

Per the planned new-type sequence (relationship-heavy, 12H/hidden-heavy,
soft-aspect/gift-heavy, hard-aspect/T-square-heavy, career/MC-heavy,
dignity-heavy-low-angular, debility-heavy-no-angular, 2nd no-dominant):
each new type is likely to either (a) confirm Q1–Q3 generalize, or
(b) surface a new calibration question. T-square-heavy in particular may
surface a tightness-cluster / hard-aspect-loudness question (analogue of
Q1 for aspects rather than dignities). This document is appended, not
frozen, as the corpus grows. Final calibration is a single JOINT pass
over the completed corpus, not per-question patching.

---

## Batch-1 reveal additions

Batch-1 was the first blind-batch -> commit -> score-once reveal after
the 4 canonical references. The reveal did NOT challenge extraction:
full-scored-set extraction remained mean `1.000`, worst `1.000`. It did
surface three concentrated salience pressure zones from the new batch,
without motivating any immediate patch.

### Candidate question cluster A — Q2 refinement: tightness inflation is not one problem

Batch-1 suggests Q2 should be split analytically into at least three
sub-cases:

- **exact generational aspect inflation**  
  1985: `Neptune-Pluto 0.27` probe surfaced as false emphasis even
  though the chart's actual leading centres held.
- **exact soft-aspect inflation under stronger structure**  
  1982: `Moon-Uranus 0.21` surfaced as false emphasis even while the
  Saturn-8 pressure spine remained intact.
- **tightness overpowering personal relevance**  
  shared pattern: an exact aspect can become loud enough to read like a
  headline even when astrologer judgment says it is secondary to a more
  structural owner.

Open calibration question:
- should exactness be modulated by personal relevance, aspect type,
  structural ownership, or some combination, rather than treated as one
  undifferentiated loudness term?

### Candidate question cluster B — outer participation caps

Batch-1 surfaced two related outer-planet elevation patterns:

- **outer in exact generational aspect**  
  1985 false emphasis on Neptune via exact aspect membership.
- **outer as stellium member**  
  2007 false emphasis on Uranus inside a real 12H concentration.

This suggests a candidate calibration question around when an outer
planet may inherit `defining` from membership versus when it should
remain subordinate unless it also has a stronger personal route.

Open calibration question:
- should generational outers require an additional promotion condition
  (angle, luminary tie, chart-ruler tie, or tight personal contact)
  before a stellium/aspect can make them read as `defining`?

### Candidate question cluster C — gift / soft-strength visibility

2009 surfaced a different pattern: not false emphasis, but a rank-1
under-promotion.

- **dual-gift / multi-centred dignified chart**  
  Mercury as chart ruler + MC ruler in domicile anchored rank 1, but the
  scorer left it at `strong`, not `defining`.
- The feared bad behavior did NOT happen: Mercury did not monopolize the
  chart and the generational tightness probe did not false-fire.

This creates a new candidate question about whether the current rank-1
expectation is too strict for gift-heavy charts whose loudness is real
but not pressure-shaped.

Open calibration question:
- in a genuinely multi-centred dignified chart, should a rank-1 steering
  spine always have to be `defining`, or can `strong` be astrologically
  acceptable without counting as a provisional miss?

### Batch-1 interpretation rule

These additions are **joint-calibration candidates**, not patch
instructions. Batch-1 supports:

- extraction stability
- the existing separation of extraction vs provisional salience
- the need for more corpus volume before coefficient decisions

Batch-1 does **not** authorize:

- formula edits
- tightness coefficient changes
- outer-planet penalties/caps
- threshold rewrites

Any answer to the new questions above must be validated jointly against
the existing 4 canonical references plus subsequent batch types
(`career/MC-heavy`, `dignity-heavy-low-angular`, `debility-heavy-no-angular`, `2nd no-dominant`).

---

## Batch-2 reveal additions

Batch-2 extended the scored set from 8 to 12 charts. It again did NOT
challenge extraction: full-scored-set extraction remained mean `1.000`,
worst `1.000`. It refined the salience question set in four concrete
directions, all of which remain calibration questions rather than patch
instructions.

### Candidate question cluster D — public / MC generational inflation

1980 Tokyo showed that public-domain charts can still false-emphasize a
generational 10H participant even when the actual career spine is
elsewhere.

- **real public/career spine present**  
  Sun in the 10th plus the Jupiter-Saturn route carried the actual
  vocational structure.
- **false emphasis still surfaced**  
  Neptune in the 10th was elevated as a public headline anyway.

Open calibration question:
- in a genuinely MC-heavy chart, when does 10H generational
  participation stay contextual rather than inheriting headline
  loudness?

### Candidate question cluster E — exact friction + lone angular debility pressure

2002 Helsinki showed that a dignity-led, relatively low-angular chart
can still be pressured by two separate loudness mechanisms:

- **exact friction / permeability pressure**  
  Sun-Neptune exactness tried to read like the whole identity.
- **lone angular debility pressure**  
  Venus fall as the lone angular wound-point also surfaced as false
  emphasis.

This suggests a combined calibration question rather than two isolated
ones: dignity-led charts may need protection from both exactness and a
single angular debility stealing the reading.

Open calibration question:
- when a chart's real strength is dignity-led and only lightly angular,
  how should the scorer keep exact pressure and lone angular debility
  from overpowering the true centre?

### Candidate question cluster F — debility-heavy no-angular secondary strain

1968 Buenos Aires did not collapse into a false clean headline, but it
did show a different issue:

- the primary debility-heavy structure held
- a secondary debilitated strain owner (`Saturn` at rank 2) stayed too
  low without angular support

So the question is not only "can clustered debility become loud?" It is
also whether secondary debility nodes inside that same system can remain
visible without needing angular reinforcement.

Open calibration question:
- in debility-heavy, low-angular charts, what keeps secondary strain
  anchors from sinking to `background` once one primary debility route is
  already recognized?

### Candidate question cluster G — no-dominant secondary visibility

1975 Helsinki passed the main Q3 guard:

- **no false spine was fabricated**

But it surfaced a subtler issue:

- real secondary centres (`Mars`, `Jupiter`) became too dim while the
  chart remained distributed

So Q3 is no longer only an anti-false-spine problem. It also has a
visibility side: how to preserve a distributed chart without letting the
secondary real centres vanish.

Open calibration question:
- in no-dominant charts, what preserves truthful secondary visibility
  without sliding back into a relative-threshold scheme that manufactures
  a single dominant owner?

### Batch-2 interpretation rule

These additions are **joint-calibration candidates**, not patch
instructions. Batch-2 does **not** authorize:

- scorer logic edits
- salience formula changes
- coefficient tweaks
- per-chart corrective exceptions

Any answer to clusters D–G must be validated jointly against:

- the 4 canonical references
- Batch-1's tightness / outer / dual-gift questions
- subsequent blind batches authored before reveal
