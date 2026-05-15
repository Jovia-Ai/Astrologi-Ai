# v0.9a.1 Visibility Guard Review

## Scope

This review covers the visibility guard patch applied after:

- [v0_9a_1_public_voice_detail_visibility_review.md](/Users/sahradenizozdogan/Astrologi-Ai/docs/system/batch_audits/v0_9a_1_public_voice_detail_visibility_review.md)

Goal of the patch:

- keep `public_voice` composed candidates traceable
- keep `detail_eligible=true`
- keep `keep_for=["detail", "debug"]`
- prevent them from rendering into user-visible public surfaces unless an explicit render flag is enabled

New render guard:

- `ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL=false` by default

The guard does **not** change:

- `public_main`
- `public_support`
- renderer wording
- registry ownership
- cluster-plan public-main selection

## Flag Behavior

### Internal rollout flags

Still used:

- `ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9=true`
- `ENABLE_NATAL_COMPOSED_SEMANTICS_DETAIL_SUPPORT=true`
- `ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_VOICE_DETAIL_SUPPORT=true`
- `ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_MAIN=false`

### New visibility guard

- `ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL=false` by default

Result:

- composed `public_voice` career packets can stay detail-eligible internally
- but they do not become rendered public copy unless render-detail is explicitly enabled later

## Before / After Visibility Matrix

The matrix below compares:

- `before_visible`: same rollout flags plus `ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL=true`
- `after_guarded`: same rollout flags with render-detail absent / false

### `fix04_h10_career_stellium`

| Surface | Before Visible | After Guarded |
|---|---:|---:|
| `candidate_inventory` / candidate packet present | yes | yes |
| `detail_eligible` | yes | yes |
| `keep_for` contains `detail` | yes | yes |
| `profile_narrative_projection_v1.extra_blocks` | yes | no |
| `profile_narrative_projection_v1.blocks` | yes | no |
| `profile_v8_projection_v1.differentiators` | yes | no |
| `profile_v8_projection_v1.insight_strip` | no | no |
| `detail_cards` | no | no |

### `tokyo_1998_06_21`

| Surface | Before Visible | After Guarded |
|---|---:|---:|
| `candidate_inventory` / candidate packet present | yes | yes |
| `detail_eligible` | yes | yes |
| `keep_for` contains `detail` | yes | yes |
| `profile_narrative_projection_v1.extra_blocks` | yes | no |
| `profile_narrative_projection_v1.blocks` | yes | no |
| `profile_v8_projection_v1.differentiators` | yes | no |
| `profile_v8_projection_v1.insight_strip` | no | no |
| `detail_cards` | no | no |

### `toronto_1976_06_26`

| Surface | Before Visible | After Guarded |
|---|---:|---:|
| `candidate_inventory` / candidate packet present | yes | yes |
| `detail_eligible` | yes | yes |
| `keep_for` contains `detail` | yes | yes |
| `profile_narrative_projection_v1.extra_blocks` | yes | no |
| `profile_narrative_projection_v1.blocks` | yes | no |
| `profile_v8_projection_v1.differentiators` | yes | no |
| `profile_v8_projection_v1.insight_strip` | no | no |
| `detail_cards` | no | no |

## Internal State Confirmation

For all three target charts, the patch preserves the internal rollout state:

- composed packet id still exists:
  - `composed_career_route_v0_9a`
- `source_type` remains:
  - `composed_semantic`
- `subtype` remains:
  - `public_voice`
- `public_eligibility.detail_eligible` remains:
  - `true`
- `public_eligibility.public_support_eligible` remains:
  - `false`
- `public_eligibility.public_main_eligible` remains:
  - `false`
- suppression state remains:
  - `keep_for=["detail", "debug"]`

So the patch is a visibility guard, not a semantic rollback.

## User-Visible Outcome

With render-detail off, composed `public_voice` packets are no longer rendered into:

- `profile_narrative_projection_v1.extra_blocks`
- `profile_narrative_projection_v1.blocks`
- `profile_v8_projection_v1.differentiators`

This means:

- composed candidates remain analyzable
- composed candidates remain traceable in cluster-plan metadata
- composed candidates do not leak debug-quality copy into SHOU public surfaces

## Public Stability

Confirmed by regression tests:

- accepted goldens remained stable
- no `public_main` behavior changed
- no `public_support` behavior changed
- no renderer copy changed

The visibility guard restores the intended rollout posture:

- internal detail readiness
- no user-facing copy exposure yet

## Debug Metrics

The guard does not remove composed semantics from audit/debug visibility.

Still preserved:

- composed candidate count
- composed family distribution
- composed confidence distribution
- composed public eligibility distribution
- composed-vs-fallback opportunity metrics

So the rollout remains measurable even though it is no longer publicly rendered.

## Test Results

Focused surface regression:

- `backend/tests/test_natal_public_builder.py`: `23 passed`

Broader regression:

- `backend/tests/test_natal_promise_packets.py`
- `backend/tests/test_natal_promise_cluster_plan.py`
- `backend/tests/test_projection_shadow_v1_builder.py`
- combined: `74 passed`

Total validated:

- `97 passed`

## Final Assessment

The visibility guard works as intended.

It fixes the real problem from the prior review:

- semantic candidates were safe enough to exist
- but their rendered copy was not yet SHOU-ready

Now the system holds the correct middle state:

- semantically available
- detail-eligible internally
- not user-visible by default

## Next Required Work

Before any future public display, the next required step is:

- a dedicated composed detail renderer, or
- an explicit detail-card route with copy polishing rules

That future step should happen before:

- re-enabling composed detail rendering by default
- planning `public_support`
- considering any broader composed-semantic visibility rollout
