# NatalPromiseClusterPlanV1 — Milestone Handoff

## Scope frozen here

NatalPromiseClusterPlanV1 end-to-end, including:
- v0.3 archetype registry overlay (Virgo / Libra / Mercury–Venus / Pluto / Mars–Uranus coverage)
- domain-fit selection guards
- aux anchor-bleed filter
- v8 identity_axis identity-family preference
- four copy-polish items (career opener, Venus-Pluto opener, community chip, dangling numbered-house clip)
- P0 renderer guards from earlier rounds (aux-mirror suppression, headline length guard, smart-clip, post-colon Turkish capitalization, `chart_facts_match` annotation)

## Changed files

### Source (5)

| Path | Status |
|---|---|
| `backend/app/natal/natal_promise_cluster_plan.py` | new |
| `backend/app/natal/natal_promise_packets.py` | new |
| `backend/app/natal/promise_archetype_registry_sprint1.py` | new |
| `backend/app/natal/public_builder.py` | modified |
| `backend/app/meaning/projection_shadow_v1_builder.py` | new (whole `backend/app/meaning/` package new) |

### Tests (4)

| Path | Status |
|---|---|
| `backend/tests/test_natal_promise_cluster_plan.py` | new |
| `backend/tests/test_natal_promise_packets.py` | new |
| `backend/tests/test_projection_shadow_v1_builder.py` | new |
| `backend/tests/test_natal_public_builder.py` | modified |

### Tooling (1)

| Path | Status |
|---|---|
| `backend/scripts/audit_regen_projection.py` | new |

### Golden fixtures (1 new + 1 existing)

| Path | Status |
|---|---|
| `backend/tests/_artifacts/natal_interpret_full_1996-12-28_07-10_istanbul_user_compact_debug.json` | existing |
| `backend/tests/_artifacts/natal_interpret_full_1998-09-12_07-30_adana_user_compact_debug.json` | new |

### Audit docs

`docs/system/istanbul_cluster_plan_audit*.md`, `docs/system/adana_cluster_plan_audit*.md`, plus this handoff. All additive.

## Flags

| Flag | Default | Behavior when on | Behavior when off |
|---|---|---|---|
| `ENABLE_NATAL_PROMISE_PROJECTION_V1` | off | `source_graph = "natal_promise_cluster_plan_v1"`; ClusterPlan-driven projection with cluster → packet → legacy graph fallback chain | `source_graph = "meaning_graph_v1_1"`; legacy meaning-graph projection unchanged |
| `ENABLE_NATAL_PROMISE_PACKET_DEBUG` | off | adds `natal_promise_packets_v1` and `natal_promise_cluster_plan_v1` debug fields to the projection payload | omits both fields; public schema unchanged |

Flag gating verified: with both flags off, projection still renders 4 core + N extra blocks for both charts, no banned phrases leak, no cluster plan exposed in public schema.

## New architecture pieces

- `NatalPromiseClusterPlanV1` — internal planning layer over `NatalPromisePacketV1`. Holds `focus_map`, `clusters`, `surface_plan`, `suppressed_packets`, `anchor_usage`. Never surfaces in public schema unless debug flag is on.
- Packet candidate-inventory mode (`mode="candidate_inventory"` vs `mode="selected"`).
- Chart-signature variant packets (`*_chart_exact` suffix) with `chart_facts_match: bool` annotation gated by `_CHART_FACT_VALIDATORS`.
- Domain-family registry: `_DOMAIN_FAMILY_MAP` + `_registry_domain_families` + gated `_resolve_domain` — prevents cross-family domain misassignment (e.g. emotional_world bleeding into relationship).
- Aux domain-compatibility filter: `_filter_aux_for_domain_compatibility` + `aux_should_suppress_from_public` — prevents aux variants from inheriting anchors/body from a section whose domain family conflicts with the packet's resolved family.
- Selection precedence: cluster plan path → packet-only path → legacy graph path. Hybrid fallback when `usable_public_main < 3`.
- v8 identity_axis preference: `identity_identity_like_*` → other identity-family → mind-family fallback (only when no identity-family cluster exists at any tier). Hero / identity_axis cluster non-overlap enforced.
- Renderer guards: `_clip_to_headline`, `_smart_clip` (with `_is_numbered_house_period`), `_localize_public_copy_tr`, post-colon Turkish capitalization (precomposed `İ`).

## Current registry authority

`v0.1_plus_manual_delta_v0_2_plus_v0_3` (literal string in `backend/app/natal/promise_archetype_registry_sprint1.py`).

Authority chain: NPAL v0.1 base + v0.2 addendum + v0.3 Virgo/Libra/Adana overlay. Additive only — v0.3 never replaces v0.1/v0.2 archetypes; it adds 18 new ones plus chart-signature variant guards.

## Golden fixtures covered

| Chart | Artifact | Cluster plan covers |
|---|---|---|
| Istanbul 1996-12-28 07:10 | `natal_interpret_full_1996-12-28_07-10_istanbul_user_compact_debug.json` | identity, mind, relationship, career — 4 strong domains, 6 public_main / 2 support / 3 detail |
| Adana 1998-09-12 07:30 | `natal_interpret_full_1998-09-12_07-30_adana_user_compact_debug.json` | identity, mind, relationship, career — all `medium_strong` to `strong`, public_main / support / detail filled, identity present via Libra ASC + Venus chart-ruler |

## Tests passing

```
PYTHONPATH=backend backend/venv/bin/pytest \
  backend/tests/test_natal_promise_cluster_plan.py \
  backend/tests/test_natal_promise_packets.py \
  backend/tests/test_natal_public_builder.py \
  backend/tests/test_projection_shadow_v1_builder.py \
  -q
→ 60 passed
```

Extended suite including `test_meaning_graph_v1_1_builder.py`:

```
→ 68 passed
```

## Pre-commit verification (this freeze)

| Check | Result |
|---|---|
| Targeted test suite (4 files) | **60 passed** |
| Extended suite (+ meaning_graph_v1_1) | **68 passed** |
| `py_compile` on 5 source files | **ALL OK** |
| Banned-phrase grep on public copy | **0 hits** across Istanbul + Adana, both flag states. Phrases scanned: `sextile`, `trine`, `square`, `opposition`, `opposite`, `conjunction`, `conjunct`, `midheaven`, `ascendant`, `pressure vs resilience`, `gift_like`, `wound_like`, `cluster_role`, `main_packet`, `aux_should_suppress` |
| Flags OFF → legacy fallback unchanged | `source_graph = "meaning_graph_v1_1"`, projection still renders for both Istanbul + Adana, no cluster plan fields in public payload |
| Flags ON → cluster path active | `source_graph = "natal_promise_cluster_plan_v1"`, Istanbul `core=4 extras=6`, Adana `core=4 extras=6`, debug fields present |

## Known non-blocking follow-ups

1. **Adana core_blocks[2] / extras[5] mid-body content overlap** between two Mars-Leo-11H variants. Both are chart-correct, but the second-rank Mars Leo 11H variant repeats the same "topluluklar içinde görünür olma" mid-body content as the community variant. Polish only; both cards still pass `ready` semantically.
2. **Adana insight_strip[1] title clip** — `"Kariyer hattında anlatmak, açıklamak ve karşı tarafın duygusunu gözetmek birlikte…"` cuts with `…`. Policy-driven length clip rather than upstream overflow; the underlying full headline is intact in `core_blocks[2]`.
3. **Hero summary trailing `…`** — policy-driven hero clipping. Hero `summary` is hard-capped at ~400 chars; longer narrative is intact in the underlying block body.
4. **v0.4 expansion candidates** named in NPAL §14: action/pressure spine packets beyond Mars-Chiron / Saturn-Pluto, additional career-MC archetypes, more wound subtypes. Out of scope for this milestone.

## What not to touch next

- **Istanbul golden cluster plan output** is byte-identical at the cluster level after every round of this milestone. Do not introduce changes that would shift Istanbul `public_main` ordering, `main_packet_id` selection, or block ordering without an explicit user-approved spec.
- **`_CHART_FACT_VALIDATORS` validator registry** — adding entries is safe; removing or relaxing them risks placement-encoded packets firing on charts that don't match.
- **`_DOMAIN_FAMILY_MAP`** — the `emotional_world` → its-own-family mapping (NOT `relationship`) is load-bearing for the Adana domain-fit fix. Do not collapse it back into relationship.
- **Packet aux generation** — the aux domain-compatibility filter is the only thing preventing anchor bleed across domains. Do not bypass it in any new packet path.
- **P0 renderer guards** — `_smart_clip`'s `_is_numbered_house_period`, the post-colon Turkish capitalization, and `_clip_to_headline` are required by golden tests. Do not regress.
- **Cluster plan public-schema exposure** — `natal_promise_cluster_plan_v1` is debug-only. Do not surface it in any normal public top-level field.
- **Public-main saturation rule** — one technical family does not consume more than 1–2 public_main slots. Istanbul's Capricorn/Saturn/Uranus spine and Adana's Virgo stellium currently honor this; new tuning should preserve it.

## Reproduction commands

```bash
# Targeted suite
cd /Users/sahradenizozdogan/Astrologi-Ai
PYTHONPATH=backend backend/venv/bin/pytest \
  backend/tests/test_natal_promise_cluster_plan.py \
  backend/tests/test_natal_promise_packets.py \
  backend/tests/test_natal_public_builder.py \
  backend/tests/test_projection_shadow_v1_builder.py \
  -q

# Audit regen for both charts (writes JSON to stdout)
PYTHONPATH=backend backend/venv/bin/python backend/scripts/audit_regen_projection.py \
  backend/tests/_artifacts/natal_interpret_full_1996-12-28_07-10_istanbul_user_compact_debug.json \
  backend/tests/_artifacts/natal_interpret_full_1998-09-12_07-30_adana_user_compact_debug.json
```
