# Transit Engine Toggles

Single source of truth for runtime kill-switches and A/B flags exposed by the
transit engine. Every entry lists the option name, default, purpose, and the
rollback scenario it was introduced for.

New toggles should only be added when there is a concrete rollback or A/B
justification. If this list grows past ~5 entries without good reason, treat
that as a refactor signal — the engine shouldn't accumulate branches.

## Conventions

- Toggles live on `app.engine.transit_engine.TransitOptions` and are passed
  through the `options` dict of `build_transit_report()`.
- Defaults reflect **current production behavior**. Flipping a toggle to the
  non-default value should reproduce a specific prior engine state or enable
  a specific experimental code path.
- Bench comparisons should prefer **frozen baseline artifacts**
  (`tests/_artifacts/bench_baseline_sprint1/`) over toggle-based A/B. Toggles
  are for runtime rollback; artifacts are for measurement integrity.

## Active toggles

### `apply_out_of_sign_filter` · default `True`

Introduced: PR3 (commit `7158ae5`).

When `True`, dissociate aspects (transit and natal body at the geometric
angle but in signs that don't share the aspect's natural element/modality
relationship) have their effective `orb_max` multiplied by 0.6. Tight
dissociate aspects still qualify; borderline ones are filtered out. The
emitted aspect dict also carries `out_of_sign: bool` for downstream
narrative.

Set to `False` to reproduce the pre-PR3 engine — all aspects filtered by
raw orb only, no dissociate dampening, no `out_of_sign` flag behavior.

Rollback scenario: if PR3's 0.6× multiplier turns out to over-filter a
class of user-relevant aspects, this toggle lets production revert
instantly via config without a redeploy.

### `orb_decay_mode` · default `"gaussian"`

Introduced: PR6a.

Selects the orb → strength decay curve:

- `"linear"` — `strength = 1 - orb / orb_max` (pre-PR6 behavior)
- `"gaussian"` — `strength = exp(-0.5 * (orb / sigma)²)` with
  `sigma = orb_max / 2.355`

Set to `"linear"` to reproduce the pre-PR6 engine.

PR6a measured threshold-bucket counts under both curves (probe in the
commit message, 3 fixtures × 5 dates): all shifts within ±6%, so no
threshold recalibration was needed. Reverting to linear is therefore
safe — it will slightly decrease the "high" bucket (~-6%) and slightly
increase the "eligible" bucket (~+4%), but no eligibility surface
collapses.

Rollback scenario: if the Gaussian curve shifts ranking in a way that
hurts user experience at scale, flipping to `"linear"` restores prior
behavior.

### `apply_stack_boost` · default `True`

Introduced: PR7.

Scope: **event-level**, not engine-level. The toggle is a kwarg on
`app.transit.astro_event_v2.build_personal_multi_event_payload`, not on
`TransitOptions`. The PR7 plan originally placed it on TransitOptions;
during implementation it became clear that stack detection runs at
event aggregation, not at aspect assembly, so the toggle lives at the
correct layer.

When `True`, events that fall on the same natal-local calendar day and
each clear `significance_score >= 0.42` receive a synergy boost:

    boost = 1.0
            + size_bonus   (0.06 if size=2, 0.10 if size=3, 0.13 if size>=4)
            + 0.05 per modifier present:
                · polarity_mix       (at least one hard + one soft aspect)
                · planet_diversity   (3+ distinct transit bodies)
                · outer_present      (Saturn/Uranus/Neptune/Pluto in stack)
    capped at 1.20

Each boosted event's `significance_score` is scaled in place, and a
`stack_meta` dict is written into the event's `provenance` field:

    {
      "day": "YYYY-MM-DD",      # natal-local calendar date
      "size": 3,                # collapsed group count (PR7.1+)
      "raw_count": 4,           # pre-collapse raw event count
      "boost": 1.15,
      "raw_bonus": 0.15,
      "flags": ["planet_diversity"],
      "capped": false
    }

PR7.1 adds axis-shadow collapse: targets that are axis partners
(ASC/DSC, MC/IC, North Node/South Node) and share the same transit
body represent a single astrological contact and count once. The raw
axis-partner events still receive the boost so their scores stay
consistent. Non-stack events are unmodified.

PR7.1a extends collapse to source-side node axis (NN/SN as transit
source hitting the same target) and nodal ingress pairs (one rule
covers both because both match on same event_family + axis-partner
sources + equal target_points set, including empty-empty).

PR7b adds a single-sentence narrative clause appended to `why_now_tr`
on the top-sig stack member per day, gated by:
  size >= 3 OR (size >= 2 AND boost >= 1.15)
Marginal size=2-no-modifier stacks (boost=1.06) stay silent. The
clause is idempotent via provenance.stack_narrative_applied flag.
Disabling `apply_stack_boost` naturally silences the narrative too
(no stack_meta → gate fails) — no separate toggle.

Set to `False` to disable stack detection entirely. Events retain their
individual significance scores; no stack_meta is emitted.

Rollback scenario: if the boost shifts rankings in a way that hurts the
daily highlight experience at scale, flipping to `False` restores
pre-PR7 event ordering without a redeploy. Frozen baseline bench stays
valid either way — stack boost is event-level, bench measures aspect
ranking which is untouched.

## Deprecated / removed toggles

None yet.

## How to add a new toggle

1. Demonstrate in the PR description that a frozen baseline artifact
   alone cannot satisfy the need (i.e., there's a real runtime rollback
   or A/B requirement).
2. Add the option to `TransitOptions` with a conservative default that
   matches current behavior.
3. Thread it through the relevant engine functions. Avoid deep threading —
   if more than two function signatures need to change, reconsider the
   architecture instead.
4. Register the toggle in this document under "Active toggles" with
   default, purpose, and rollback scenario.
5. Reference this doc from the PR commit message.
