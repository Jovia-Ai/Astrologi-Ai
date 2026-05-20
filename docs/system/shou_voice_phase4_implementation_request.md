# Implement Phase-4 hidden/private pilot renderer — Bounded Request

> Separate bounded authorization request. **No code in this document.**
> Code only begins after the explicit scope-confirmation block at the
> end is signed off. Review-of-record:
> `shou_voice_section_13_2_review_bundle.md` (PASS, project owner,
> 2026-05-20).

## 1. Provenance

- §13.2 review bundle: **PASS** (review-of-record cited above)
- Phase-3 closure: complete (commit `472236e`)
- Source-of-truth plans: `shou_deep_read_phase4_renderer_design_plan.md`,
  `shou_deep_read_phase4_implementation_task_breakdown.md`
- Frozen voice contract: `shou_voice_deep_read_authoring_packet.md`
  (Rules 1–4 + role bindings + eligibility + good/bad examples)
- LOCK reference: `shou_voice_deep_read_lock_BLIND.md` PASS on `2007`

## 2. Confirmed scope (verbatim from owner + operational expansion)

Owner-set scope (must hold throughout implementation):

- hidden/private deep_read **only**
- `pattern_to_gift` pilot profile **only**
- TR-primary
- separate Phase-4 flag (default off)
- current parent/slides public contract **only**
- `share_line` / `map_trace` / `deselected_trace` → **internal or deferred**
- no endpoint / mobile / config / taxonomy
- no ARC/A2 merge
- no public schema widening in first pass

Operational expansion (disciplined defaults; reviewer-set, not new
scope):

- **Default for share_line / map_trace / deselected_trace = INTERNAL**
  (populated on the internal candidate/card payload, NOT emitted in
  the public `/interpret/ui` response). Exposing any of them publicly
  is a separate later request.
- **TR-primary means TR is what ships when flag is on.** EN parallel
  rendering is explicitly **deferred** to a later request — Phase-4
  first pass is TR-only.
- **Pilot identity** = the `relationship_route.hidden_private_love`
  candidate/card path already established by Phase-3 (`472236e`).
- Phase-4 consumes the existing committed `deep_read_phase3` metadata
  shape (authoring packet §3; breakdown §5.3 verbatim shape). No
  parallel naming.

## 3. Phase-4 flag (proposed name, requires owner confirmation)

```
ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_HIDDEN_PRIVATE_LOVE_DEEP_READ_RENDERER
```

- default: **off**
- **independent** from the Phase-3 flag
  (`ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_HIDDEN_PRIVATE_LOVE_PHASE3_INTERNAL_METADATA`)
- Phase-3 flag may be on while Phase-4 flag remains off; Phase-4
  user-visible behavior **must not** activate through Phase-3 flag
  alone

## 4. Hard invariants (Phase-3-style + owner constraints)

1. **Flag-off no-op:** with Phase-4 flag off, public output for every
   chart byte-identical to current (snapshot-tested).
2. **Public contract unchanged in first pass:** no new public fields;
   `profile_public.composed_detail_cards` shape unchanged; the hidden/
   private card's existing slot is the only thing whose **content**
   may differ when the flag is on.
3. **Phase-3 invariants preserved:** all `472236e` no-op + isolation
   guarantees still hold (`route-equivalent payload identical when
   Phase-3 flag toggles`, no leakage to other surfaces).
4. **No leakage to other surfaces** when Phase-4 flag is on
   (regression tests in breakdown §8.6).
5. **Frozen contract honored:** packet Rules 1–4, origin_hint
   allow/deny telemetry assertions (breakdown §8.3), gift drift scan
   (§8.4), trace-surface containment (§8.5).
6. **ARC extraction / Pass-1 §4 guards stay green** (frozen, untouched
   by this work).

## 5. Allowed file touches (anything else = STOP and ASK)

Per breakdown §4 (pre-confirmed):

| File | Allowed use |
|---|---|
| `backend/app/meaning/composed_detail_renderer.py` | primary pilot renderer entrypoint (Phase-4 branch behind flag) |
| `backend/app/meaning/projection_shadow_v1_builder.py` | only as a narrow flag-checked switch (no broader projection rewrite) |
| `backend/app/natal/natal_promise_packets.py` | only if a minimal metadata normalization bug surfaces; **no semantic expansion** |
| `backend/tests/test_composed_detail_renderer.py` | renderer unit tests (flag-off / flag-on / exact-owner / composed-fallback) |
| `backend/tests/test_natal_public_builder.py` | route-equivalent contract tests + no-leakage guards |
| `backend/tests/test_natal_promise_packets.py` | (optional) origin telemetry assertion tests |

**Must NOT touch** unless explicitly re-approved (STOP and ASK):

- `backend/app/natal/public_models.py`
- `backend/app/natal/public_builder.py`
- any endpoint / router file
- anything under `backend/app/core/` or `backend/app/main.py`
- any Flutter / mobile file
- `config/` / taxonomy / `pubspec.yaml` / `requirements.txt`
- any new Python package
- `backend/ephe/`, `.env`, `config/core/config.py`

This list is **stricter** than CLAUDE.md alone; the additional fences
come from §2 owner scope and §4 invariants.

## 6. Acceptance criteria (Phase-4 first pass = "complete" when)

- All breakdown §8.1 flag-off no-op tests pass.
- All breakdown §8.2 flag-on pilot renderer tests pass.
- Breakdown §8.3 origin safety tests pass — including the telemetry
  assertions (every fired `origin_hint` has empty `deny_reasons`;
  every omitted one has `eligible == false` OR non-empty `deny_reasons`).
- Breakdown §8.4 gift drift scan + §8.5 trace-surface containment
  pass.
- Breakdown §8.6 regression: no other family adopts the Phase-4 path;
  Phase-2 exact-owner precedence intact unless explicitly redesigned;
  no Phase-4-only fields leak to other surfaces.
- Public snapshot diff = 0 with Phase-4 flag off across the existing
  test fixtures.
- §7 3-chart QA set executable (does not require manual sign-off in
  this Phase; manual blind read is a separate Phase-4 → public
  rollout gate, not a Phase-4 first-pass completion gate).
- Phase-4 flag stays default **off**; no enablement decision in this
  pass.

## 7. Stop-and-ask triggers (binding — implementer must halt)

The implementer halts and asks the owner before proceeding if ANY of:

- a needed change falls outside §5 allowed files
- the Phase-3 schema (`role_bindings` shape, carrier names) needs to
  change in any way
- a test requires a config / taxonomy / package addition
- public output diff with Phase-4 flag OFF is anything other than 0
- a new public field would be needed to satisfy a test
- the proposed Phase-4 flag name in §3 needs to differ
- the QA set in breakdown §7 needs to shift (chart added / removed /
  reframed)
- any ARC scorer / A2 path is encountered (must remain untouched)

## 8. Manual QA gate (Phase-4 → public rollout, **NOT** Phase-4 first-pass)

Per breakdown §8.7 + packet §8 phase split, manual blind reading on
the 3-chart QA set is required **before any enablement / public
rollout**, NOT before Phase-4 first-pass completion. First-pass
completion = code + automated tests under flag-off-default. Manual
blind + decision-to-enable is a later, separate gate.

## 9. Rollback (per breakdown §10)

- Primary: disable Phase-4 flag → returns to Phase-3 internal-metadata
  no-op baseline.
- Structural: remove Phase-4 renderer branch only; do **not** unwind
  Phase-3 metadata (which is independent and currently flag-off too).
- Rollback considered safe iff: flag-off path passes Phase-3 no-op
  tests; Phase-2 exact-owner behavior intact; no endpoint/mobile
  contract depends on the Phase-4 branch.

## 10. What scope confirmation here grants vs not

**Confirmation grants:**

- start of Phase-4 implementation under §2–§9 constraints
- single pilot family (hidden/private), TR-primary, default-off flag

**Confirmation does NOT grant:**

- public exposure of `share_line` / `map_trace` / `deselected_trace`
- EN rendering
- enablement / public rollout (separate gate, §8)
- any other deep_read family
- ARC/A2 merge
- any §5 disallowed file touches

## 11. Explicit scope confirmation block (sign-off required before code)

The implementer must NOT begin any code work until the block below is
signed off. Sign-off form:

```
Owner confirmation
==================
Date:        2026-05-20
Owner:       Sahra Deniz / project owner

Confirmed scope (§2):              YES
Confirmed Phase-4 flag name (§3):  YES
Confirmed allowed files (§5):      YES
Confirmed invariants (§4):         YES
Confirmed acceptance (§6):         YES
Confirmed stop-and-ask list (§7):  YES
Confirmed §10 grants/limits:       YES

Overall: GO

Notes:
Approved for Phase-4 hidden/private pilot implementation only.
Scope limited to the existing parent/slides public contract.
share_line / map_trace / deselected_trace remain internal or deferred.
No endpoint, mobile, config, taxonomy, ARC/A2, or public schema
widening is authorized.
```

GO requires all rows YES. Any NO halts the request pending a revised
scope. No code starts under a NO-GO. **GO RECORDED 2026-05-20.**
