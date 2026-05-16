# ARC v0.1 — Layer 0 Implementation-Readiness Analysis

> Empirical, code-grounded audit. Read-only investigation. No code changed.
> This is the factual foundation the PR plan
> (`arc_v0_1_layer0_pr_plan.md`) consumes. Every claim carries
> `file:line` evidence.

## Headline

Layer 0 is **largely an assembly/wiring job, not a build job.** ~85% of the
primitives the Layer 0 spec requires already exist as working functions in
`backend/app/astro/`. The only genuinely net-new logic is **salience
scoring** — exactly the part the spec already flagged as the
astrologer-judgment / open-calibration half. This is now proven from code,
not assumed.

## The 8 readiness questions — answered with evidence

| # | Question | Finding | Evidence |
|---|---|---|---|
| 1 | Chart-fact source | `build_natal_chart` returns structured dict: `planets` (sign/house/retrograde/degree), `houses` (cusps), `house_positions`, `aspects` | `backend/app/astro/chart_engine/builder.py:243, 309-322` |
| 2 | Dignity data | `essential_dignity(planet, sign)` already returns the exact `Literal["domicile","exaltation","detriment","fall","peregrine"]` the spec needs. EXALTATIONS/RULERSHIPS/detriment/fall all tabled | `backend/app/astro/dignity.py:132-167` |
| 3 | Dispositor | `build_dispositor_chain()` returns `{primary_chain, reason:"domicile"...}`; plus reusable `ruler_of_sign`, `build_house_ruler_map`, `get_house_sign` | `backend/app/natal/dispositor_engine.py:~294, 196, 222` |
| 4 | Insertion point | `_prepare_payload_from_chart` — `chart_data` ready, before `build_natal_graph`/packets | `backend/app/api/routes/natal_interpretation.py:1610→1621→1634, 1713` |
| 5 | **Structured vs string (critical)** | Structured data fully exists at source. String anchors ("Satürn · 6. ev · Oğlak") are downstream rendering. Layer 0 = read existing `chart_data`, NOT reparse strings | `builder.py:309-322`, `positions.py:54-93` |
| 6 | Aspect orb + direction | `orb` is in aspect output; `compute_direction()→Literal["applying","separating","exact"]` exists but is **not auto-attached** to the aspect list | `chart_engine/aspects.py:65`, `astro/aspect_direction.py:80` |
| 7 | Stellium / angular | Angular = free (planets carry assigned house; filter house∈{1,4,7,10}). Stellium = net-new but tiny (only hand-authored `match_id` strings exist, no general detector) | `positions.py:89-93`; `natal_promise_packets.py:5029` (match_id only) |
| 8 | 2019 oracle | `compute_natal_chart(2019)` + `essential_dignity()` per planet → authoritative table. No reconstruction needed | `chart_service.py:9`, `dignity.py:132` |

## Wiring vs net-new

**Ready, only needs wiring (low risk):**

- Structured chart → `compute_natal_chart` / `build_natal_chart`
- Dignity table → `essential_dignity` — **exists but selection NEVER calls it**
  (callers grep: only `archetype_profile.py:323`, `aspect_direction.py:207`).
  This precisely confirms the selection audit's "dignity-blind selection".
- Dispositor chains → `build_dispositor_chain`
- House ruler map → `build_house_ruler_map`
- Angular planets → trivial from house assignment
- Applying/separating → `compute_direction` (exists; wire into aspect list)

**Genuinely net-new:**

1. `chart_skeleton` object schema + the assembly function that calls the
   above and packages them.
2. **Salience scoring (Half B)** — the only real net-new logic; the spec's
   open-calibration item.
3. General stellium detector (tiny: group planets by sign and by house,
   count ≥3).
4. Candidate-contract-field plumbing + threading skeleton down the pipeline.

## Precise insertion point

```
natal_interpretation.py:1610  chart_data = compute_natal_chart(...)
            :1634  _prepare_payload_from_chart(chart_data, ...)
                   ← HERE: chart_skeleton = build_chart_skeleton(chart_data)
            :1713  build_natal_graph(chart_data, planets, aspects)
                   skeleton added to context, flows to packet/cluster/projection
```

**Do not touch** `build_natal_chart`'s other caller `charts.py` (the Groq
LLM chart path — different consumer). ARC path is only
`compute_natal_chart → _prepare_payload_from_chart`.

## Honest caveats

- **applying/separating not auto-attached.** `calculate_chart_aspects`
  returns only `{type, orb}`; `compute_direction` is a separate module.
  PR-1 must explicitly call it for `tightest_aspects.applying`. Logic
  exists, just unwired.
- **Stellium is the one net-new extraction primitive.** All others have
  ready functions. Trivial but must be written in PR-1.
- **Salience cannot be calibrated without the corpus.** PR-1 is
  corpus-independent; PR-2 (salience) cannot be frozen without the
  stratified corpus.

## Conclusion

Implementation-readiness is strongly positive: the spec's architecture maps
cleanly onto existing code, ~85% of primitives are ready functions, the
insertion point is a clean single seam, the 2019 oracle is reachable. The
real work is salience + corpus — exactly as flagged. The PR plan can now be
written code-grounded, not speculative.
