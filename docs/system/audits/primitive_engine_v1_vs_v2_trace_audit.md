# S3 — `primitive_engine` v1 vs v2 Trace Audit

## Scope

This is a trace-only audit artifact.

- No code.
- No runtime change.
- No deletion.
- No refactor.

Target files:

- `backend/app/natal/narrative/primitive_engine.py` (v1, 233 lines)
- `backend/app/natal/narrative/primitive_engine_v2.py` (v2, 322 lines)

Question this audit answers:

> Matrix §4.13b says v1 is **FREEZE → DELETE after trace audit confirms
> v2 fully replaces it**. Does it?

## Executive verdict

**No. v2 does NOT replace v1. They are intentionally coupled, not
competing. v1 is NOT delete-safe.**

The matrix §4.13b assumption was wrong. The trace reveals a **layered**
design: v1 generates legacy primitive hits; v2 re-scores them with the
natal feature graph. v2 explicitly imports and calls v1 internally as
`legacy_hits`.

**Recommendation: change matrix §4.13b from "FREEZE → DELETE" to
"RESCUE-as-is — intentional v1 / v2 layering, not legacy redundancy."**

## Caller map

### v1 — `primitive_engine.build_primitives`

Three live callers, all on canonical paths:

| Caller | Path | Class |
|---|---|---|
| `signature_engine.py:8` | `from app.natal.narrative.primitive_engine import build_primitives` | active-canonical-upstream import (matrix §4.11 RESCUE) |
| `profile_narrative_engine_signature.py:10` + `:1792` `primitive_hits = build_primitives(chart, natal_graph, facts=facts)` | RUNTIME caller in primary natal narrative orchestrator (matrix §4.4 RESCUE+EXTEND) | **runtime canonical** |
| `primitive_engine_v2.py:5` + `:268` `legacy_hits = build_primitives(chart, natal_graph, facts=facts)` | v2 itself depends on v1 | **runtime canonical (inside v2)** |

### v2 — `primitive_engine_v2.build_primitives_v2`

Live callers on canonical paths + tests:

| Caller | Path | Class |
|---|---|---|
| `api/routes/natal_interpretation.py:99` + `:1748` `primitive_scores_v2 = build_primitives_v2(...)` | RUNTIME caller in natal route | **runtime canonical** |
| `astro_os/natal/runtime.py:11` + `:36` `primitive_scores = build_primitives_v2(...)` | RUNTIME caller in natal runtime | **runtime canonical** |
| `tests/natal/test_natal_selection_v3.py` (multiple lines) | Test coverage | test-canonical |
| `tests/test_natal_internal_state_route.py:67` | Test coverage | test-canonical |

### The decisive evidence — v2 line 268

`primitive_engine_v2.py:268`:

```python
facts = normalize_facts(chart, natal_graph)
legacy_hits = build_primitives(chart, natal_graph, facts=facts)
rescored_hits: list[dict[str, Any]] = []
for hit in legacy_hits:
    primitive_id = str(hit.get("primitive_id") or "")
    legacy_score = float(hit.get("score") or 0.0)
    feature_support, source_features = _feature_bucket_score(primitive_id, feature_graph)
    ...
```

v2 calls v1 (`build_primitives`) to produce `legacy_hits`, then iterates
each hit and **rescores it** with feature-graph support derived from
`build_natal_feature_graph(...)`. v2's output schema (line 311) carries
`"engine_version": "primitive_engine_v2"` to mark itself as the
*rescoring layer*, not a from-scratch reimplementation.

## Architecture interpretation

The two engines are **deliberately layered**:

```
chart + natal_graph
        ↓
v1 (primitive_engine):
    build_primitives(chart, natal_graph, facts=facts)
        emits: legacy primitive hits (rule-based pattern detection)
        ↓
v2 (primitive_engine_v2):
    build_primitives_v2(chart, natal_graph, ...):
        1. computes natal_feature_graph
        2. calls v1 to get legacy_hits
        3. for each hit: _feature_bucket_score(primitive_id, feature_graph)
                          → blends legacy_score + feature_support
        4. emits: rescored_hits with engine_version "primitive_engine_v2"
```

Two distinct surfaces depend on these:

- **signature narrative renderer** (`profile_narrative_engine_signature.py`
  line 1792) consumes **v1's raw primitive hits** directly — uses
  `primitive_hits = build_primitives(chart, natal_graph, facts=facts)`
- **natal route + natal_os runtime** consume **v2's rescored output** —
  use `build_primitives_v2(...)` for `primitive_scores_v2` in the
  response payload

So v1 and v2 have **different consumers**:
- signature narrative uses v1 directly (raw pattern detection)
- public response carries v2's rescored output (feature-graph-blended)

Both surfaces are canonical. Neither is going away.

## Partition

- **v1 status**: active-canonical-upstream (3 live callers: signature
  engine, profile narrative signature renderer, v2)
- **v2 status**: active-canonical-upstream (2 runtime callers + tests)
- **v1 delete-safety**: NO. Deleting v1 would break:
  - `profile_narrative_engine_signature.py` (canonical signature
    narrative path)
  - `primitive_engine_v2.py` itself (v2 cannot compute legacy_hits)
  - `signature_engine.py` import (would fail at module load)
  - The natal `/interpret` runtime path (cascades through above)

## Implication for matrix §4.13

The current matrix:

| § | Layer | Decision |
|---|---|---|
| 4.13a | `primitive_engine_v2` + `contradiction_engine` + `layer_arbitrator` | RESCUE v2 |
| 4.13b | `primitive_engine` (v1) | FREEZE → DELETE after trace audit confirms v2 fully replaces it |

**Update required**:

| § | Layer | Decision (updated) |
|---|---|---|
| 4.13a | `primitive_engine_v2` + `contradiction_engine` + `layer_arbitrator` | RESCUE as the rescoring + arbitration layer |
| 4.13b | `primitive_engine` (v1) | **RESCUE as-is — intentional v1 layer beneath v2 + direct caller in signature narrative; not legacy redundancy** |

The "Don't keep two primitive engines" rationale in the original §4.13b
was based on the assumption that v2 was a full replacement. It isn't. v1
is the primitive *generator*; v2 is the primitive *rescorer*. Both stay.

## Risk notes

### Risk 1 — false redundancy assumption

The naming convention (`_v2` suffix) suggested replacement. Trace
revealed layering. This is a generic risk for any future "v2 audit": the
suffix does not imply replacement.

### Risk 2 — divergent consumers may drift

Two different consumers eat two different outputs:
- signature narrative eats v1's `primitive_hits`
- public payload carries v2's `primitive_scores_v2`

If v1's output schema or v2's rescoring logic drifts independently, the
two surfaces could disagree about what counts as a strong primitive.
This is not a delete-or-rescue question, but worth noting as a separate
"output divergence" concern for a future audit.

### Risk 3 — signature narrative bypasses v2's rescoring

The signature narrative renderer (`profile_narrative_engine_signature.py`)
consumes v1's raw hits without v2's feature-graph support. That's
intentional today (signature narrative has its own scoring inside), but
if signature narrative ever wants v2's feature support, it would need to
switch to `build_primitives_v2(...)`. Not action-required now, just
visible.

## Recommendation

Update matrix §4.13b to **RESCUE-as-is**. Do not freeze, do not delete.

Document the layering in the matrix rationale so future readers don't
re-open this question.

No code change. No structural action. Audit closes.

## Next action

Matrix §4.13 row updated to reflect "intentional layering" decision.
S3 marked DONE.

S4 (Phase-4 hidden/private → phrase_lib_tr_profile migration) is the
natural next bounded request.
