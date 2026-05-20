# SHOU `deep_read` — §13.2 Review Bundle

> Single human review unit. Planning artifact. **No code.**
> Reviewer cannot be the builder; this bundle exists so the
> author/build side cannot self-clear (§9.5 / §10 discipline).
> Approval here authorizes only what §3 enumerates — nothing more.

## 1. Artifacts under review (one decision, three docs)

The three documents below are reviewed as a single unit. PASS only if
all three are individually acceptable; a REVISE on any one returns
the whole bundle.

| # | Path | Role in the bundle |
|---|---|---|
| 1 | `docs/system/shou_voice_deep_read_authoring_packet.md` | The frozen design contract (Rules 1–4, roles, eligibility, good/bad examples, QA gate split). Reviewer's primary text. |
| 2 | `docs/system/shou_voice_phase3_hidden_private_closure.md` | Confirms Phase-3 internal-metadata pilot is closed (commit `472236e`), flag-gated, public no-op. Reviewer must verify scope and no-op claims. |
| 3 | `docs/system/shou_deep_read_phase4_implementation_task_breakdown.md` | The next-gate planning artifact; flag strategy, file map, QA set, rollback. Cross-references the actual committed Phase-3 schema (§5.3 verbatim shape). |

Supporting context (read-only references; not separately decided):

- `shou_voice_reconciliation_spec.md` (the binding chain + §9 contract, §9.5 stopping condition, §9.6/9.8/9.9 role/profile bindings)
- `shou_voice_deep_read_reference_v4.md` + `shou_voice_deep_read_lock_BLIND.md` (LOCK PASS evidence)
- `shou_voice_deep_read_v4_1_delta.md` (silik fix + origin_hint examples)
- `shou_voice_phase3_implementation_plan.md` (what Phase-3 was scoped to do; the closure realises this plan)

## 2. Out of scope (anti-creep — reviewer must reject if smuggled in)

- any Flutter / mobile change
- any endpoint or router change
- any `config/`, `core/config.py`, `main.py`, or package change
- `public_models.py` public-field shape changes
- any other `deep_read` family (only hidden/private pilot)
- global taxonomy promotion of `pattern_to_gift`
- merging or otherwise authorising ARC scorer / **A2** (Pass-1 closed
  negative; A2 still owes its own §10.3; explicitly NOT decided here)
- `identity_polarity`, `held_plurality`, `emotional_base` (still
  PROPOSED — not under review in this bundle)

## 3. What PASS would authorise (and would NOT)

**Would authorise:**

- adoption of the frozen deep_read contract (Rules 1–4 + origin_hint
  with denylist + gift + integration examples)
- pilot-scoped `pattern_to_gift` exception for hidden/private only
  (NOT global)
- acceptance of the Phase-3 closure as complete (commit `472236e`)
- the Phase-4 breakdown as the **approved plan shape** for a later,
  separate implementation request

**Would NOT authorise:**

- Phase-4 implementation itself (separate "implement Phase-4
  hidden/private pilot" request still required after this PASS)
- any user-visible output change
- any of the §2 out-of-scope items

## 4. Reviewer pass checklist (concrete — so "enough review" is defined)

A reviewer marks each item Y / N / N-A. Bundle is PASS only with **all
Y**; any N is REVISE on that artifact.

### A. Packet (`authoring_packet.md`)
- [ ] §2 four rules internally consistent (no contradiction with §7 worked example)
- [ ] §3 `pattern_to_gift` framed as **pilot-scoped candidate** (NOT self-approved by the packet)
- [ ] §4 origin_hint eligibility has the explicit denylist; rule "allowlist alone is not sufficient" present
- [ ] §5 good examples present for origin_hint, gift, **and integration**
- [ ] §6 bad examples cover: determinist/blame · motivational · clinical · soft-coercion · translation drift · over-specific childhood without opt-out
- [ ] §8 phase split explicit: §13.2 = Phase-3 precondition; §13.3 = Phase-4/public-rollout gate
- [ ] pending items (`identity_polarity`, `held_plurality`, `emotional_base`) clearly still pending
- [ ] ARC/A2 explicitly untouched

### B. Phase-3 closure (`phase3_hidden_private_closure.md`)
- [ ] commit hash (`472236e`) and pinned-hashseed test runs cited
- [ ] flag (`ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_HIDDEN_PRIVATE_LOVE_PHASE3_INTERNAL_METADATA`) named exactly
- [ ] "Public No-Op Guarantees" verifiable: implementation-shape + tests both green
- [ ] scope strictly hidden/private; no other family touched
- [ ] "Next Decision Gate" correctly names Phase-4 design plan as the next required gate

### C. Phase-4 breakdown (`phase4_implementation_task_breakdown.md`)
- [ ] §5.3 `role_bindings` shape matches the committed schema verbatim (`natal_promise_packets.py:277–286` + `composed_detail_renderer.py:559–577`)
- [ ] separate Phase-4 flag, default off, independent of Phase-3 flag
- [ ] §7 3-chart QA purposes non-fungible: 2007 = felt bar, 1996 = code-seam compatibility (no gold, NOT felt), 1975 = overreach contrast
- [ ] §8.3 origin safety tests assert on existing `allow_reasons`/`deny_reasons` telemetry (no parallel safety layer)
- [ ] §8 flag-off no-op tests + regression tests + Phase-4-only fields not leaking to other surfaces
- [ ] §9 non-goals match §2 of this bundle
- [ ] §10 rollback is operationally trivial (flag flip → Phase-3 no-op baseline)
- [ ] §11 approval questions include Phase-3 schema reconciliation confirmation
- [ ] doc itself does not authorise implementation

## 5. Decision form

```
Reviewer: project owner
Date:     2026-05-20
Role:     project owner (not the builder — review-of-record)

A. Packet:                PASS
B. Phase-3 closure:       PASS
C. Phase-4 breakdown:     PASS

Bundle decision: PASS
  (all three A/B/C = PASS)

Notes: PASS authorizes use of this bundle as the §13.2
review-of-record. Does NOT authorize implementation; a separate
bounded "Implement Phase-4 hidden/private pilot renderer" request
follows and requires explicit scope confirmation before code.
```

## 6. After the decision

- **Bundle PASS** → record decision in this file; future Phase-4
  implementation request may cite this bundle as the §13.2 review of
  record. Implementation still requires its own separate approval
  (per packet §9 and breakdown §13).
- **Bundle REVISE** → return the bundle with the per-artifact change
  list; no implementation work proceeds. A subsequent revised bundle
  is reviewed against the same §4 checklist.
- **Bundle REJECT** → design returns to the locked rules and the
  pending §13.2-proposed items; no Phase-4 path until a new design
  cycle is opened.

## 7. Reviewer's hand (what the bundle does for them)

This bundle exists so the reviewer does **not** have to decide what
"enough review" means, reconcile contradictions between artifacts, or
verify schema claims from scratch. §4 lists the conditions; §1–3
fences the scope; §5 is the form; §6 is the post-decision path.
Everything else is in the three artifacts and their supporting
references.
