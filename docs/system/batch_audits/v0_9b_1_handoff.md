# v0.9b.1 Handoff — Moon Home-Security Composed Detail Lane

> Final implementation handoff. v0.9b.1 ships a single subtype
> (`moon_signature.home_inner_security`) into the existing Phase B
> `profile_public.composed_detail_cards` lane behind a new
> default-`false` flag and a 3-chart allowlist. The accompanying
> chain — v0.9a.3 P0 truthfulness fix, v0.9b.0 debug-only families,
> v0.9b.0.1 calibration — also ships in the same commit.

---

## Changed Files

| File | Role |
|---|---|
| [backend/app/meaning/composed_detail_renderer.py](backend/app/meaning/composed_detail_renderer.py) | Career Phase B renderer + Moon variant matcher (`_match_supported_moon_home_inner_security_variant`), Moon render helper (`render_moon_home_inner_security_card_v0_9b_1`), bespoke TR copy for 3 charts, banned-phrase + required-vocabulary guards, lane projection helper. |
| [backend/app/meaning/projection_shadow_v1_builder.py](backend/app/meaning/projection_shadow_v1_builder.py) | Wires `project_moon_home_inner_security_to_public_lane` into `profile_public.composed_detail_cards` — career cards first, Moon cards appended; lane field omitted entirely when empty. |
| [backend/app/api/routes/natal_interpretation.py](backend/app/api/routes/natal_interpretation.py) | Cache key gains the v0.9b family flags plus `v09b_moon_hi_lane`. |
| [backend/app/natal/natal_promise_packets.py](backend/app/natal/natal_promise_packets.py) | `_build_relationship_route_candidates`, `_build_moon_signature_candidates`, calibrated default-fallback penalties, cross-family Moon-ownership post-pass; P0 fix for the `"olması de"` template via `_vowel_harmonized_de_particle`; `_normalize_packet_field_text` connector-aware boundary. |
| [backend/app/natal/natal_promise_cluster_plan.py](backend/app/natal/natal_promise_cluster_plan.py) | Ledger metrics: `composed_candidate_subtype_distribution`, `composed_v0_9b_confidence_distribution`, `composed_cross_family_overlap_count`, `composed_default_fallback_count`, `cross_family_moon_ownership_count`, `relationship_candidates_blocked_by_moon_ownership`, `composed_v0_9b_opportunity_severity`. |
| [backend/tests/test_composed_detail_renderer.py](backend/tests/test_composed_detail_renderer.py) | Renderer unit tests for v0.9a.2 + Phase B + v0.9b.1 (full flag matrix, allowlist gate, strip-to-visible, semantic direction, P0). |
| [backend/tests/test_natal_public_builder.py](backend/tests/test_natal_public_builder.py) | Integration tests covering Phase B, v0.9b.0, v0.9b.0.1, v0.9b.1 across the live UI route. |
| [backend/tests/test_natal_promise_packets.py](backend/tests/test_natal_promise_packets.py) | Unit tests for both families (flag matrix, subtype routing, default-fallback penalty, cross-family ownership). |
| [backend/tests/test_natal_promise_cluster_plan.py](backend/tests/test_natal_promise_cluster_plan.py) | Cluster-plan trace tests for v0.9b debug-only behavior. |

Planning + audit docs added under `docs/system/batch_audits/` and
`docs/system/`:

- `v0_9a_2_composed_detail_renderer_post_implementation_review.md` (updated with v0.9a.2 follow-up section)
- `v0_9a_3_dedicated_composed_detail_lane_plan.md`
- `v0_9a_3_phase_b_public_detail_lane_audit.md`
- `post_v0_9a_3_system_health_audit.md`
- `natal_compositional_grammar_v0_9b_relationship_moon_plan.md`
- `v0_9b_0_scoring_subtype_calibration_review.md`
- `v0_9b_1_moon_home_inner_security_detail_rollout_plan.md`
- `v0_9b_1_handoff.md` (this document)

---

## Flag Matrix

| Flag | Default | Role |
|---|---|---|
| `ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9` | false | base composed semantics |
| `ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_ROUTE_V0_9B` | false | produce `relationship_route` composed candidates (debug-only) |
| `ENABLE_NATAL_COMPOSED_SEMANTICS_MOON_SIGNATURE_V0_9B` | false | produce `moon_signature` composed candidates (debug-only) |
| `ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9B_DETAIL_SUPPORT` | false | mark v0.9b candidates `detail_eligible` when conf ≥ 0.70 |
| `ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL` | false | render eligible cards into trace lane |
| `ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_DETAIL_LANE` | false | open `profile_public.composed_detail_cards` (career allowlist) |
| `ENABLE_NATAL_COMPOSED_SEMANTICS_MOON_HOME_INNER_SECURITY_PUBLIC_DETAIL_LANE` | **false** | **NEW** — promote moon `home_inner_security` cards into the same public lane |
| `ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_MAIN` | false (load-bearing) | hard gate against public_main routing |

### Activation Matrix (Moon detail lane)

| `RENDER_DETAIL` | `PUBLIC_DETAIL_LANE` | `MOON_HOME_INNER_SECURITY_PUBLIC_DETAIL_LANE` | Moon card visible? |
|---|---|---|---|
| off | * | * | no |
| on | off | * | no |
| on | on | off | no |
| on | on | on (chart in allowlist + signature match + conf ≥ 0.80 + not Moon-owned-elsewhere) | **yes (target charts only)** |

`public_main_eligible` and `public_support_eligible` stay hard-coded
`False` for every moon_signature candidate under every flag combo.

---

## Target Chart Allowlist

The renderer's `_match_supported_moon_home_inner_security_variant`
recognizes three primitive-fact signatures:

| Variant id | Chart | Signature | Confidence |
|---|---|---|---|
| `trabzon_2001_09_14_moon_home_inner_security` | `trabzon_2001_09_14` | Moon Leo 4H + IC Leo + Sun Virgo 5H | 0.88 |
| `fix08_cancer_capricorn_nodes_moon_home_inner_security` | `fix08_cancer_capricorn_nodes` | Moon Libra 4H + IC Libra + Venus Capricorn 7H | 0.85 |
| `cairo_1991_01_15_moon_home_inner_security` | `cairo_1991_01_15` | Moon Capricorn 4H + Saturn Capricorn 4H + IC Capricorn | 0.81 |

No other chart can render to the lane — the matcher returns `None`
and the renderer short-circuits.

---

## Public Payload Contract

The lane sits at `profile_narrative_projection_v1.profile_public.composed_detail_cards`
(the existing Phase B field, now also carrying Moon cards on the 3
target charts). The field is omitted entirely when empty.

### Visible fields (strict subset)

```
{ id, node_id, headline, teaser, body, chips, family, emphasis, origin }
```

Stripped before public emission and observable only in the
traceability lane (`source_anchor_trace`):

```
source_type, source_candidate_id, public_job,
source_anchor_trace, detail_items, evidence_summary, avoid_readings
```

### Live sample — `cairo_1991_01_15`

```json
{
  "id": "composed_detail::composed_moon_signature_v0_9b::cairo_1991_01_15_moon_home_inner_security",
  "node_id": "promise::composed_moon_signature_v0_9b",
  "headline": "Duygusal güvenliğin sağlam bir yapı üzerinden taşınıyor.",
  "teaser": "İç zemininde kurulu bir omurga olduğunda kendini düzenleyebiliyorsun; o yapı zayıfladığında dış ritm de hızlıca sertleşebiliyor.",
  "body": "Duygusal güvenliği bir gevşeklik üzerinden değil, içeride kurduğun sağlam bir yapı ve çerçeve üzerinden topluyorsun. Bu iç omurga yerindeyken kendini düzenleyebiliyorsun; sarsıldığında dış dünyadaki ritm çabuk gerginleşiyor ve kontrol ihtiyacı öne çıkıyor. Bu hattın armağanı dayanıklılık, duygusal hafıza ve koruma kapasitesi; sürtüşmesi ise iç güveni yalnız dış zeminden bekleme ya da çevreye fazla tutunma. Büyüme yönü, içeride taşınan bir güveni dışarıdan gelen onaya bağlamadan kurabilmek.",
  "chips": ["İç güven", "Sağlam zemin", "Düzenleme"],
  "family": "moon_home_inner_security",
  "emphasis": "detail",
  "origin": "composed_detail_renderer_v0_9b_1"
}
```

### Ordering contract

When the same chart somehow emits both a career Phase B card AND a
Moon v0.9b.1 card (impossible under the current 3+3 disjoint
allowlists, but defensive), career cards take top placement:

1. Phase B career cards
2. v0.9b.1 Moon cards

---

## Cairo Cross-Family Ownership Verification

`cairo_1991_01_15` produces two competing composed candidates:

| Family | Subtype | Confidence |
|---|---|---|
| `moon_signature` | `home_inner_security` | 0.81 |
| `relationship_route` | `intimacy_depth` | 0.71 |

The v0.9b.0.1 cross-family rule triggers (`0.81 - 0.71 = 0.10 ≥ 0.05`):

```
relationship_route candidate:
  meta.moon_evidence_owned_by                  = "moon_signature"
  meta.cross_family_moon_ownership_outcome     = "moon_takes_ownership"
  public_eligibility.future_renderer_eligibility_blocked = True
  public_eligibility.reason_codes              ⊇ {"moon_evidence_owned_elsewhere"}

moon_signature candidate:
  meta.moon_evidence_owned_by                  = "moon_signature"
  (self-owns by default)
```

Public-lane outcome on cairo:

- `composed_detail_cards` carries **exactly one** entry — the Moon
  card.
- No relationship-derived id (`composed_detail::composed_relationship_route_v0_9b::*`)
  appears anywhere in the public payload.

Test: `test_v0_9b_1_cairo_cross_family_block_holds_end_to_end`.

---

## Copy QA Results

Per-chart copy passes both the inherited Phase B
mechanical-quality checks and the new Moon-family semantic
guardrails.

| Check | Result |
|---|---|
| Banned debug tokens (`debug`, `candidate`, `fallback`, `source_type`, `public job`, `mc, yöneticisi`, `mc route`, `10h`) | 0 across all 3 charts |
| Banned generic-family phrases (`Aile önemlidir`, `Ev hayatın güçlüdür`, `Annenle/Babanla ilişkin`, `Ailen senin için her şey`, `kalbinde yer eden aile`) | 0 across all 3 charts |
| Required safety vocabulary (`iç güven`, `duygusal zemin`, `iç zemin`, `kök`, `ait ol`, `düzenle`, `sakinleş`, `toparla`) | ≥ 1 per card (enforced by `_meets_moon_home_inner_security_public_quality`) |
| ASCII Turkish residue (`Insanlar`, `Disaridaki`, `nasil`, `dogru`, `cumle`, `Gorunur`, …) | 0 in public copy |
| Turkish diacritics (`İ`, `ı`, `ş`, `ğ`, `ç`, `ö`, `ü`) | present in every card's `headline`, `teaser`, `body` |
| Body ≥ 18 words (Phase B minimum body length) | satisfied (all 3 bodies ≥ 50 words) |
| P0 dangling connectors (`olması de`, `Bazen de.`, `bazen de.`) | 0 |

---

## Non-Leak Proof (50-chart batch, all flags ON)

```
target_charts_with_moon_card    : 3 / 3   (trabzon, fix08, cairo)
target_charts_missing_moon_card : []
non_target_charts_with_moon_card: []      (0 / 47)

public_leak_total               : 0
  blocks                        : 0
  core_blocks                   : 0
  extra_blocks                  : 0
  detail_cards                  : 0
  profile_v8.differentiators    : 0
  profile_v8.insight_strip      : 0
  profile_v8.hero (composed)    : 0
  profile_v8.identity_axis      : 0

P0 truthfulness scan
  olması de                     : 0
  Bazen de.                     : 0
  bazen de.                     : 0

Accepted golden drift           : 0 / 5
  golden_stable                 : true
```

Surfaces inspected: every `profile_public.*` lane, every
`profile_v8_projection_v1.*` lane, both `hero` and `identity_axis`
node_id, every audited chart × flag-off / flag-on snapshot.

---

## Tests

```
========================= 173 passed in 43.99s =========================
```

Suite history this session:

| Stage | Tests | Δ |
|---|---|---|
| v0.9a.3 baseline (start of session) | 103 | — |
| v0.9a.2 follow-up (Turkish diacritic + ASCII residue guard) | 106 | +3 |
| v0.9a.3 Phase B (public detail lane) | 120 | +14 |
| v0.9a.3 P0 truthfulness fix | 125 | +5 |
| v0.9b.0 (debug-only relationship + moon families) | 142 | +17 |
| v0.9b.0.1 (penalty bump + Moon ownership) | 150 | +8 |
| **v0.9b.1 (moon home-security detail lane)** | **173** | **+23** |

Focused test command:

```
PYTHONHASHSEED=0 PYTHONPATH=backend python -m pytest \
  backend/tests/test_composed_detail_renderer.py \
  backend/tests/test_natal_public_builder.py \
  backend/tests/test_natal_promise_packets.py \
  backend/tests/test_natal_promise_cluster_plan.py \
  backend/tests/test_projection_shadow_v1_builder.py
```

---

## Known Next Steps

Ordered by readiness and ROI. None of these are in scope for the
v0.9b.1 commit — they are documented for the next planning cycle.

1. **v0.9b.2 — second moon subtype slice.**
   `moon_signature.private_emotional_processing @ conf ≥ 0.80`.
   v0.9b.0.1 audit identified 2 strong candidates
   (`antalya_1999_02_27 @ 0.93`, `rome_1971_02_06 @ 0.84`) plus
   `mersin_1981_08_17 @ 0.785` as a borderline third. Reuses the
   same Phase B-style lane and confidence floor pattern; needs:
   - new variant matcher in the renderer (3 primitive-fact
     signatures)
   - bespoke TR copy following a parallel semantic direction
     (private processing, intuition, withdrawal-to-restore)
   - new flag
     `ENABLE_NATAL_COMPOSED_SEMANTICS_MOON_PRIVATE_EMOTIONAL_PROCESSING_PUBLIC_DETAIL_LANE`

2. **v0.9b.3 — relationship `intimacy_depth` slice (if/when audit allows).**
   The cross-family Moon-ownership rule already filters cairo, madrid,
   antalya, diyarbakir. Remaining candidates (mumbai, antalya
   already gone, cairo already gone, madrid already gone…) need a
   fresh audit pass to see what's left after the Moon block.

3. **50 → 100 chart batch expansion.**
   Single-chart subtypes (`attraction_warmth`, `boundary_conflict`)
   cannot graduate on n=1 evidence — needs more fixture coverage
   before v0.9b.4+.

4. **Phase C mobile detail surface.**
   Still deferred. The lane now carries 3 career charts + 3 moon
   charts = 6 fixtures. Plan §3 in v0.9a.3 required ≥ 6 fixtures
   before mobile work — that threshold is now met. Next planning
   doc can pick up Phase C.

5. **Relationship subtype gap audit.**
   `hidden_private_love` and `wound_to_gift` fire on 0/50 charts.
   Either the detection rules are too strict or the 50-chart batch
   underrepresents the signatures. Re-examine in
   `_build_relationship_route_candidates`.

6. **Transit activation.**
   Orthogonal to this chain; remains independently schedulable.

---

## Risks Left Unmitigated

- **Card copy is hand-authored TR**, not LLM-generated. If a 4th
  chart joins the moon_home_inner_security allowlist later, fresh
  copy must be authored manually following the §6 semantic direction
  in the v0.9b.1 plan.
- **The Moon family renderer takes a different path from career**:
  it operates directly on candidate packets rather than on the v0.9a.2
  trace renderer's output. A future refactor could unify the two paths
  for cleaner separation, but neither path leaks today.
- **Cross-family ownership rule fires only on Moon-anchored
  relationship subtypes** (`emotional_need_affection`, `intimacy_depth`).
  If a future relationship subtype (e.g. `wound_to_gift`) starts
  consuming Moon evidence, the rule's trigger predicate in
  `_apply_v0_9b_cross_family_moon_ownership` will need updating.
