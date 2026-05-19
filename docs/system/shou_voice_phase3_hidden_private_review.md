# SHOU Phase-3 Hidden/Private Pilot Review

## Verdict

APPROVE

## Scope Check

- Phase-3 metadata is gated behind `ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_HIDDEN_PRIVATE_LOVE_PHASE3_INTERNAL_METADATA`.
- Implementation is limited to the hidden/private pilot only:
  - `relationship_route.hidden_private_love` candidate metadata
  - hidden/private internal composed-detail card trace metadata
- No renderer copy, endpoint, mobile, taxonomy, ARC/A2, or public schema changes were made.

## Public No-Op Check

- `profile_public.composed_detail_cards` field set remains unchanged.
- Phase-3 metadata is attached only to internal candidate/card structures as `deep_read_phase3`.
- Public promotion still strips this metadata because the public-lane allowlist is unchanged.
- Route-equivalent guard test compares baseline vs Phase-3-flag-on public payload for the Istanbul 1996 hidden/private pilot and asserts:
  - projection snapshot equality
  - exact `profile_public` equality

## Test Coverage

- Internal metadata present when flag is on:
  - candidate meta path
  - renderer internal card path
- Internal metadata absent when flag is off:
  - candidate meta path
  - renderer return object
- Existing Phase-2 hidden/private card behavior unchanged:
  - exact owner emission
  - no leakage to other public surfaces
  - public card shape unchanged
- Public no-op preserved when Phase-3 flag is enabled.

## Relevant Files

- `backend/app/natal/natal_promise_packets.py`
- `backend/app/meaning/composed_detail_renderer.py`
- `backend/tests/test_natal_promise_packets.py`
- `backend/tests/test_composed_detail_renderer.py`
- `backend/tests/test_natal_public_builder.py`

## Notes

- Repository contains unrelated dirty/untracked docs artifacts outside this scope.
- Only the five relevant backend files for the hidden/private Phase-3 pilot should be staged and committed with this change.
