# Izmir 1996-03-08 ClusterPlan Audit After P0 Correctness Guards

- Generated: 2026-05-12
- Source artifact: `backend/tests/_artifacts/natal_interpret_full_1996-03-08_08-30_izmir_user_compact_debug.json`
- Public snapshot: `docs/system/_generated_outputs/fresh_natal_interpret_ui_1996-03-08_08-30_izmir.json`
- Request: `1996-03-08 08:30 Izmir, TR`
- Flags: `ENABLE_NATAL_PROMISE_PROJECTION_V1=true`, `ENABLE_NATAL_PROMISE_PACKET_DEBUG=true`
- Scope: P0 correctness-guard pass only. No new semantic coverage was added.

## 1. What Changed

This pass fixed correctness guards only:

1. Gemini-specific `mind_mind_system` bespoke copy is now chart-guarded.
   It no longer renders on the Izmir chart when packet evidence shows
   `angle:ASC:Taurus` / `Yükselen Boğa`.
2. Generic relationship main copy no longer drifts to `7. ev Yay` when the
   packet evidence says `7. ev Akrep`.
3. `profile_v8_projection_v1.identity_axis` no longer falls back to a mind
   packet under `Kimlik Ekseni` when no identity-family cluster exists. It
   now relabels the slot honestly as `Öne Çıkan Hat`.

## 2. Candidate Inventory

Cluster-plan payload still reports `candidate_packet_count = 10`.

Effective debug packet ids remain:

- `career_career_visibility`
- `career_career_visibility_aux`
- `mercury_square_pluto_deep_mind_pressure_chart_exact`
- `mind_mind_system`
- `mind_mind_system_aux`
- `relationship_relationships`
- `relationship_relationships_aux`

So this pass did not increase semantic breadth. It only removed fact leakage.

## 3. Focus Map

Focus map is unchanged:

### career

- score: `1.0`
- tier: `strong`
- packet_ids:
  - `career_career_visibility`
  - `career_career_visibility_aux`
  - `career_career_visibility_aux`

### relationship

- score: `1.0`
- tier: `strong`
- packet_ids:
  - `relationship_relationships`
  - `relationship_relationships_aux`
  - `relationship_relationships_aux`

### mind

- score: `0.9726`
- tier: `strong`
- packet_ids:
  - `mind_mind_system`
  - `mind_mind_system_aux`
  - `mind_mind_system_aux`
  - `mercury_square_pluto_deep_mind_pressure_chart_exact`

Main takeaway:

- `identity` still does not exist in the focus map
- this pass fixed truthfulness, not selection richness

## 4. Public Blocks

### `profile_narrative_projection_v1.core_blocks`

1. `promise::career_career_visibility`
   - headline: `Perde açılmadan önce içeride uzun bir son prova olur.`
   - body:
     `Satürn'ünün 12. evde Balık'ta olması ve Kariyer hattının Oğlak'ta olması aynı çizgiyi güçlendiriyor...`
   - status:
     semantically still narrow, but not the P0 fact-leak target in this pass

2. `promise::relationship_relationships`
   - headline: `Sen ilişkide yüzeysel bir sıcaklıktan çok, içine oturan bir güven arıyorsun.`
   - body:
     `Mars'ının 12. evde Balık'ta olması ve 7. evinin Akrep olması, ilişkide hem yoğunluk hem de güven aradığını gösteriyor...`
   - P0 outcome:
     `7. ev Yay` drift is gone; body now matches chips/evidence

3. `promise::mind_mind_system`
   - headline: `Ne yapacağını bildiğin an tempo kendiliğinden yükselir.`
   - body:
     `Venüs'ünün 12. evde Boğa'da olması kadar Yükseleninin Boğa olması de bu hattın karakterini belirliyor...`
   - P0 outcome:
     Gemini leak is gone; copy now stays on Taurus/Venus facts
   - remaining issue:
     style/grammar is still rough (`olması de`), but fact correctness is restored

### `profile_narrative_projection_v1.extra_blocks`

1. `promise::mercury_square_pluto_deep_mind_pressure_chart_exact`
   - unchanged detail block
   - still stylistically stiff, but no new chart-fact leak seen in this pass

## 5. V8 Surface

### hero

- node_id: `promise::mind_mind_system`
- headline: `Ne yapacağını bildiğin an tempo kendiliğinden yükselir.`
- summary:
  now Taurus/Venus-coded, not Gemini-coded

### identity_axis

- eyebrow: `Öne Çıkan Hat`
- node_id: `promise::relationship_relationships`
- headline: `Sen ilişkide yüzeysel bir sıcaklıktan çok, içine oturan bir güven arıyorsun.`

This is the intended P0 fallback behavior for this chart state:

- no identity-family cluster exists
- `identity_axis` is no longer mislabeled as `Kimlik Ekseni`
- a distinct non-hero line is surfaced honestly instead

## 6. Exact Grep Checks

Forbidden leaked facts checked against:

- `backend/tests/_artifacts/natal_interpret_full_1996-03-08_08-30_izmir_user_compact_debug.json`
- `docs/system/_generated_outputs/fresh_natal_interpret_ui_1996-03-08_08-30_izmir.json`

Patterns:

- `Yükseleninin İkizler`
- `Yükselenin İkizler`
- `7. ev Yay`
- `7. evinin Yay`

Result:

- no hits

Interpretation:

- Gemini-specific public leak is removed from the route-equivalent output
- relationship sign drift is removed from the route-equivalent output

## 7. Regression Status

Validation run:

```bash
PYTHONPATH=backend backend/venv/bin/pytest \
  backend/tests/test_natal_promise_packets.py \
  backend/tests/test_natal_promise_cluster_plan.py \
  backend/tests/test_natal_public_builder.py \
  backend/tests/test_projection_shadow_v1_builder.py -q
```

Result:

- `73 passed`

Also passed:

```bash
backend/venv/bin/python -m py_compile \
  backend/app/meaning/projection_shadow_v1_builder.py \
  backend/tests/test_natal_public_builder.py \
  backend/tests/test_projection_shadow_v1_builder.py
```

No regressions were observed in:

- Istanbul 1996
- Adana 1998
- Istanbul 2020

## 8. Remaining Non-P0 Issues

This chart is still not an accepted golden.

What remains:

- candidate inventory is still semantically narrow
- `identity` still disappears from the focus map
- mind main copy is fact-correct now, but still stylistically rough
- career/mind/relationship packet set still feels generic
- stored route-equivalent surface and rebuild-from-artifact surface are still not especially rich

So the current verdict is:

- **P0 truthfulness fixed**
- **semantic richness still not fixed**
