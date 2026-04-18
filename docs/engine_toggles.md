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
