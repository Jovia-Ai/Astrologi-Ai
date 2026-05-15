# v0.9a.3 Phase B Public Detail Lane — Post-Implementation Audit

> Phase B of the v0.9a.3 plan landed: a dedicated, flag-gated public
> field `profile_public.composed_detail_cards` that promotes
> already-rendered composed detail cards into a user-facing lane, while
> keeping every other public surface untouched. This document is the
> shipping audit.

## 1. Changed Files (Phase B scope)

Only the files below were touched in service of Phase B. Other dirty
working-tree files visible in `git status` belong to unrelated, earlier
work (promise packets, cluster plan, sprint registry, etc.) and are out
of scope for this audit.

| File | Role | Change kind |
|---|---|---|
| [backend/app/meaning/composed_detail_renderer.py](backend/app/meaning/composed_detail_renderer.py) | Renderer + Phase B promotion helper | new helpers added (`project_composed_detail_cards_to_public_lane`, `public_detail_lane_enabled`, `_PUBLIC_DETAIL_LANE_VARIANT_ALLOWLIST`, `_PUBLIC_DETAIL_LANE_VISIBLE_FIELDS`, `_strip_to_public_visible`, `_variant_from_card_id`) |
| [backend/app/meaning/projection_shadow_v1_builder.py](backend/app/meaning/projection_shadow_v1_builder.py) | Projection builder for `profile_narrative_projection_v1` and `profile_v8_projection_v1` | renamed `_render_composed_detail_cards_debug` → `_render_composed_detail_cards` and dropped `include_packet_debug` param (render is now decided purely by `RENDER_DETAIL`; trace and lane emission still gated downstream); wired `public_composed_detail_cards` into `profile_public` conditionally (omitted when empty) |
| [backend/app/api/routes/natal_interpretation.py](backend/app/api/routes/natal_interpretation.py) | UI interpretation route + cache | added `v09_public_detail_lane:<value>` segment to `composed_semantic_flag_signature` so the new flag invalidates the cache when toggled |
| [backend/tests/test_composed_detail_renderer.py](backend/tests/test_composed_detail_renderer.py) | Unit tests | 7 new tests for promotion helper (flag matrix, trace stripping, allowlist gate, copy QA, empty/None input) |
| [backend/tests/test_natal_public_builder.py](backend/tests/test_natal_public_builder.py) | Integration tests | 7 new tests at projection level (flag-off, render-on/lane-off, render-off/lane-on, both-on target, non-target charts, non-leakage into other surfaces, public-card copy QA) |

---

## 2. Final Flag Matrix

| `RENDER_DETAIL` | `PUBLIC_DETAIL_LANE` | `traceability.composed_detail_cards_v0_9a_2` | `profile_public.composed_detail_cards` |
|---|---|---|---|
| off | off | absent | absent |
| on  | off | present (when `include_packet_debug=true`) | absent |
| off | on  | absent | absent |
| on  | on  | present (when `include_packet_debug=true`) | present **for allowlisted variants only** (`fix04_h10_career_stellium`, `tokyo_1998_06_21`, `toronto_1976_06_26`) |

Notes:

- `PUBLIC_DETAIL_LANE` is a **promotion gate** layered on top of
  `RENDER_DETAIL`. It cannot conjure a card without an underlying
  rendered trace card.
- Both flags default to `false`.
- The lane field is **omitted entirely** when no card qualifies (no
  `composed_detail_cards: []` sentinel is emitted).

---

## 3. Target Chart Payload Excerpt (`fix04_h10_career_stellium`)

Run conditions:

- `RENDER_DETAIL=true`, `PUBLIC_DETAIL_LANE=true`
- `include_packet_debug=true` (interpretation route default for
  `include_debug=true` callers)

### `profile_narrative_projection_v1.profile_public.composed_detail_cards`

```json
[
  {
    "id": "composed_detail::composed_career_route_v0_9a::fix04_h10_career_stellium",
    "node_id": "promise::composed_career_route_v0_9a",
    "headline": "İnsanlar sende sadece ne yaptığını değil, nasıl söylediğini de fark ediyor.",
    "teaser": "Dışarıdaki etkin çoğu zaman sözünün tonu ve kurduğun pozisyonla güçleniyor.",
    "body": "Bir işi yalnız tamamlaman değil, onu nasıl anlattığın da sende görünür rolün parçası oluyor. İnsanlar çoğu zaman önce fikrinin tonunu, sonra o tonun yarattığı etkiyi fark edebilir. Buradaki güç, sesini daha yüksek kullanmakta değil; doğru yerde netleştiğinde dışarıdaki rolün zaten belirginleşmesinde yatıyor.",
    "chips": ["Kariyer", "Söz", "Görünür rol"],
    "family": "career_public_voice",
    "emphasis": "detail",
    "origin": "composed_detail_renderer_v0_9a_2"
  }
]
```

Observed visible-field set, captured from live run:

```
['body', 'chips', 'emphasis', 'family', 'headline', 'id', 'node_id', 'origin', 'teaser']
```

This is exactly the v0.9a.3 visible contract — nothing more, nothing
less.

### `profile_narrative_projection_v1.traceability.composed_detail_cards_v0_9a_2`

Still present, still carries the technical / debug fields that the
public lane intentionally strips:

```json
{
  "source_type": "composed_semantic",
  "source_candidate_id": "composed_career_route_v0_9a",
  "public_job": "detail_only",
  "source_anchor_trace": {
    "family": "career_route",
    "subtype": "public_voice",
    "domain_reason": ["MC route", "MC ruler involved", "10H planet"],
    "technical_anchors": [
      "MC Gemini",
      "Mercury · Cancer · 10. ev",
      "Mercury · 10. ev",
      "Mars · 10. ev"
    ]
  }
}
```

Trace-card observed key set:

```
['body', 'chips', 'detail_items', 'emphasis', 'evidence_summary',
 'family', 'headline', 'id', 'node_id', 'origin',
 'public_job', 'source_anchor_trace', 'source_candidate_id',
 'source_type', 'teaser']
```

So the trace card carries the union (public-visible fields + technical
fields), and the public card carries the strict subset.

---

## 4. Non-Target Chart Payload Excerpt (`izmir_1996_05_20`)

Run conditions: same as above (`RENDER_DETAIL=true`,
`PUBLIC_DETAIL_LANE=true`).

Observed `profile_public` keys:

```
['blocks', 'core_blocks', 'detail_cards', 'extra_blocks', 'schema_version']
```

- `composed_detail_cards` — **absent** from `profile_public`
- `composed_detail_cards_v0_9a_2` — **absent** from `traceability`
  (renderer's `_match_supported_public_voice_variant` returns `None`
  because the chart's placements/angles do not match any of the three
  allowlisted variant signatures, so no card is rendered upstream)

---

## 5. Public Non-Leak Verification

Captured from live runs on **both** target chart
(`fix04_h10_career_stellium`) and non-target chart
(`izmir_1996_05_20`) with both flags ON. Leak counters checked for any
item whose `node_id == "promise::composed_career_route_v0_9a"` or whose
`id` starts with `composed_detail::composed_career_route_v0_9a::`:

| Surface | Target chart leaks | Non-target chart leaks |
|---|---|---|
| `profile_narrative_projection_v1.profile_public.blocks` | 0 | 0 |
| `profile_narrative_projection_v1.profile_public.core_blocks` | 0 | 0 |
| `profile_narrative_projection_v1.profile_public.extra_blocks` | 0 | 0 |
| `profile_narrative_projection_v1.profile_public.detail_cards` | 0 | 0 |
| `profile_v8_projection_v1.differentiators` | 0 | 0 |
| `profile_v8_projection_v1.insight_strip` | 0 | 0 |
| `profile_v8_projection_v1.hero.node_id == composed?` | False | False |
| `profile_v8_projection_v1.identity_axis.node_id == composed?` | False | False |
| `profile_v8_projection_v1.composed_detail_cards` (field existence) | absent | absent |

So:

- composed card is **not** in `blocks`
- composed card is **not** in `core_blocks`
- composed card is **not** in `extra_blocks`
- composed card is **not** in the legacy `detail_cards` lane
- composed card is **not** in `profile_v8.hero`
- composed card is **not** in `profile_v8.identity_axis`
- composed card is **not** in `profile_v8.insight_strip`
- composed card is **not** in `profile_v8.differentiators`
- `profile_v8` does not gain a parallel `composed_detail_cards` field
  (v8 has no `profile_public` container; the lane lives only on
  `profile_narrative_projection_v1`)

---

## 6. Copy QA on the Public Lane Card

Checks against the public (`profile_public.composed_detail_cards[0]`)
fields for `fix04_h10_career_stellium`:

| Check | Result |
|---|---|
| No `debug` substring in `headline`/`teaser`/`body` (case-insensitive) | pass |
| No `candidate` substring | pass |
| No `fallback` substring | pass |
| No `source_type` substring | pass |
| No `public job` substring | pass |
| No `mc, yöneticisi` substring | pass |
| No `mc route` substring | pass |
| No `10h` substring | pass |
| No `source_anchor_trace` key on public card | pass — observed key set is exactly `{id, node_id, headline, teaser, body, chips, family, emphasis, origin}`; trace fields stripped by `_strip_to_public_visible` |
| No `source_type` / `source_candidate_id` / `public_job` keys on public card | pass — same reason |
| No `detail_items` / `evidence_summary` keys on public card | pass — same reason |
| No ASCII Turkish residue (`Insanlar`, `Disaridaki`, `nasil`, `soyledigini`, `Soz`, `Gorunur`, `dogru`, `cumle`, `Ifade`, `cercevelediginde`, `agirligin` …) in any visible field | pass — enforced both at render time by `_meets_public_quality` and re-checked at lane projection |
| Visible copy contains Turkish diacritics (`İ`, `ı`, `ş`, `ğ`, `ç`, `ö`, `ü`) | pass — observable in headline (`İnsanlar`, `yaptığını`, `söylediğini`), teaser (`Dışarıdaki`, `çoğu`, `güçleniyor`), body (`yalnız`, `görünür`, `parçası`, etc.) |

---

## 7. Cache Key Verification

`_interpret_ui_cache_key` at
[backend/app/api/routes/natal_interpretation.py:452-465](backend/app/api/routes/natal_interpretation.py:452-465)
now hashes `v09_public_detail_lane:<value>` into the cache key.

Live check with identical request and only the lane flag toggled:

```
key when lane=off: interpret_ui:v1:e3914588d850fb2706a731ca830194b907a5fbd4
key when lane=on:  interpret_ui:v1:88a3ce4440a294e62f1c2d9431f0dd5ab61ad871
keys differ: True
```

So flipping `ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_DETAIL_LANE`
between `false` and `true` produces a fresh cache key, meaning a
previously cached response built under one flag value cannot leak into a
request built under the other. Without this, two of the new
`test_natal_public_builder.py` tests would have flaked depending on
which other test ran first.

---

## 8. Tests

Command:

```
PYTHONHASHSEED=0 PYTHONPATH=backend python -m pytest \
  backend/tests/test_composed_detail_renderer.py \
  backend/tests/test_natal_public_builder.py \
  backend/tests/test_natal_promise_packets.py \
  backend/tests/test_natal_promise_cluster_plan.py \
  backend/tests/test_projection_shadow_v1_builder.py
```

Result:

```
============================= 120 passed in 23.35s =============================
```

Suite delta:

- v0.9a.2 follow-up baseline: 106 passed
- v0.9a.3 Phase B: 120 passed (+14)
  - +7 unit tests in `test_composed_detail_renderer.py` for
    `project_composed_detail_cards_to_public_lane`
  - +7 integration tests in `test_natal_public_builder.py` covering the
    full flag matrix, non-target charts, public-surface non-leakage,
    and copy QA on the live lane field

All previously accepted goldens (cluster plan, packets, projection
shadow, public builder) remain stable.

---

## Conclusion

Phase B is shipping in its intended narrow form:

- a dedicated `profile_public.composed_detail_cards` lane exists,
- the new `ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_DETAIL_LANE` flag
  defaults to `false`, so default-production behavior is unchanged,
- when the flag is on, only the three allowlisted target charts emit a
  card, and that card carries only the public-visible field set,
- the traceability lane is untouched and still carries
  `source_anchor_trace`,
- no composed card leaks into any other public surface
  (blocks / core_blocks / extra_blocks / detail_cards / hero /
  identity_axis / insight_strip / differentiators),
- the route-level cache key invalidates correctly when the lane flag
  toggles.

Phase C (mobile-gated detail surface) and Phase D (allowlist relaxation)
remain unimplemented per the v0.9a.3 plan.
