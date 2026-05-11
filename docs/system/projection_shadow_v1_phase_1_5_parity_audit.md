# Projection Shadow V1 Phase 1.5 Parity Audit

Date: 2026-04-24  
Scope: Post-Phase-1.5 parity check, **no code changes**.

## Method
- Fresh payload generated from local `POST /interpret/ui` with:
  - `birth_date=1996-12-28`
  - `birth_time=07:10`
  - `birth_place=Istanbul, TR`
  - `locale=tr`
  - `include_full_profile=true`
- Payload used: `/tmp/projection_shadow_v1_phase15_payload.json`
- Compared:
  1. `profile_narrative` vs `profile_narrative_projection_v1`
  2. `profile_v8` vs `profile_v8_projection_v1`
- “Before” values are from prior audit:
  - [`docs/system/projection_shadow_v1_parity_audit.md`](/Users/sahradenizozdogan/Astrologi-Ai/docs/system/projection_shadow_v1_parity_audit.md)

## 1) profile_narrative vs profile_narrative_projection_v1

### Before/After Metrics

| Metric | Previous Audit (Projection) | Phase 1.5 (Projection) | Delta | Status |
|---|---:|---:|---:|---|
| Avg body chars | 78.2 | 248.8 | +170.6 | improved |
| Avg detail blocks/card | 3.5 | 3.5 | 0.0 | still weak |
| Unique block ID count | 5 / 10 | 10 / 10 | +5 unique | improved |
| Domain coverage | 2 domains (`general, relationships`) | 6 domains (`emotional, general, identity, life_direction, mind, relationships`) | +4 domains | improved |
| Layer coverage | missing `mechanism` | full graph parity (`effect, mechanism, potential, recognition, shadow`) | restored | improved |
| Traceability ratio | 1.0 | 1.0 | unchanged | improved (stable) |
| Avg sentences/body | ~mostly atomic (qualitative) | 3.1 | richer cadence | improved |
| Signal-only risk | High (previous qualitative) | 0.0 (`<=1 sentence` ratio) | strong reduction | improved |

Legacy reference (same fresh payload):
- Legacy avg body chars: **383.43**
- Projection avg body chars: **248.8**
- Legacy avg detail blocks/card: **6.83**
- Projection avg detail blocks/card: **3.5**

### Over-flattening risk
- **Previous:** High  
- **Current:** **Medium**
- Reason: body cadence improved strongly, but detail depth is still much lower than legacy (3.5 vs 6.83).

### Editorial quality examples

Improved projection examples (now multi-sentence, non-atomic):
- `Merkür 1. Ev Shadow`  
  - “Bazen fazla düşünerek yaşayabilir... Bu tema en çok general alanında shadow katmanında çalışıyor.”
- `Ay 8. Ev Shadow`  
  - “Gerilim yükseldiğinde içe kapanma... Bu tema en çok emotional alanında shadow katmanında çalışıyor.”
- `Micro Insight`  
  - “Kimliğin doğal bir büyüme... Bu tema en çok identity alanında recognition katmanında çalışıyor.”

Still weak:
- Detail expansion remains shallow on some cards (e.g., some `detail_blocks` count = 1).
- Legacy detail-card scaffolding depth is not yet matched.

### Classification
- **improved**
- **still weak**
- **ready for limited canary** (shadow/comparison canary only, not UI switch)

---

## 2) profile_v8 vs profile_v8_projection_v1

### Before/After Metrics

| Metric | Previous Audit (Projection) | Phase 1.5 (Projection) | Delta | Status |
|---|---:|---:|---:|---|
| Profile_v8 completeness ratio | 0.25 | 0.25 | 0.0 | still weak |
| Traceability ratio | 1.0 | 1.0 | unchanged | improved (stable) |
| Domain coverage (projected selected nodes) | not explicitly quantified | `general` only | still narrow | still weak |
| Layer coverage (projected selected nodes) | not explicitly quantified | `potential, recognition, shadow` | partial | still weak |
| Over-flattening risk | High | High | no meaningful change | still weak |
| Signal-only risk | High/Medium (qualitative) | Medium | slight improvement | still weak |

Completeness details (unchanged):
- Legacy present sections: `16/16`
- Projection present sections: `4/16`
- Missing projection sections remain:
  - `past_teaser`, `past_teasers`, `first_impression`, `talents`, `conversation_hooks`,
  - `affects_you`, `defense`, `first_felt`, `intimacy`, `mind`, `mission_preview`, `archetype_portal`

### Editorial quality examples

Still weak example:
- `identity_axis` body length:
  - Legacy: **483 chars**
  - Projection: **67 chars**
- Projection text is traceable but too compressed to match profile_v8 editorial contract.

### Classification
- **still weak**
- **not ready**

---

## 3) Summary Classification

### profile_narrative_projection_v1
- **improved**
- **still weak**
- **ready for limited canary** (shadow parity monitoring only)

### profile_v8_projection_v1
- **still weak**
- **not ready**

No regression detected in requested metrics.

## 4) Final Readiness Decision

Projection quality improved materially for `profile_narrative_projection_v1` (especially body richness, ID integrity, and domain/layer coverage), but `profile_v8_projection_v1` remains structurally incomplete.

UI migration is **not recommended** at this stage.
