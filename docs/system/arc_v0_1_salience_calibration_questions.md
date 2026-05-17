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
