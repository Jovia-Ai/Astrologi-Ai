# System Consolidation Audit

**Date:** 2026-04-29  
**Scope:** Natal meaning / projection / voice / surface / chart-wheel consolidation status after recent work.  
**Constraint:** No code changes.

## 0. Executive Summary

The system is materially better organized than before, but it is **not consolidated yet**.

What is genuinely stronger now:

- `meaning_graph_v1_1` exists, validates cleanly, and is emitted in public payloads.
- projection shadow outputs exist and have strong traceability.
- selection/ranking/dedup guardrails improved sharply, especially for projection selection integrity.
- Voice Sprint 1 cleaned the worst phrase-level coaching/jargon regressions.
- Home/Profile surface audits exist and some P0 cleanup has already landed in code.
- Profile chart wheel integration is live and payload precedence in `chart_wheel_repository.dart` is fixed.

What is still unresolved:

- semantic authority is still duplicated across `meaning_graph`, `meaning_graph_v1_1`, `profile_narrative`, `sections_v2`, `supporting_threads`, `profile_v8`, and `full_map_v8`
- projection outputs are good enough for shadow QA, not for UI replacement
- `include_full_profile=false` already prunes some heavy work, but several expensive branches still run because they remain semantic roots or parity artifacts
- voice still needs pattern-level and surface-mode work
- Home V2 is only **partially** cleaned; Profile chart wheel exists, but Home still renders its old chart wheel section

Bottom line:

- **Semantic source:** improved but not fully adopted
- **Projection:** improved but not ready for migration
- **Selection/ranking/dedup:** strong enough to stop rewriting for now
- **Voice:** phrase-level improved; pattern-level still open
- **Surface/UI:** partially cleaned; not yet orchestration-clean
- **Chart wheel:** profile integration improved; data-source/privacy hardening still needed

## 1. Current State By Area

| Area | Status | Why |
|---|---|---|
| Semantic source | `improved but not done` | `meaning_graph_v1_1` is live and validated, but legacy semantic/render branches still carry authority in practice |
| Projection | `improved but not done` | projection shadow branches exist and trace cleanly, but parity audits still show structural/editorial gaps |
| Selection/ranking/dedup | `fixed` | current blocker has shifted away from selection integrity toward voice/render quality |
| Voice Sprint 1 | `fixed` | phrase-level cleanup landed, lint guard exists, no rollback recommended |
| Surface mapping | `improved but not done` | audits are clear and some Home/Profile P0 work landed, but orchestration mismatch remains |
| Chart wheel | `improved but not done` | Profile integration exists and payload precedence is fixed in current code, but Home duplication and endpoint/privacy issues remain |

## 2. What Is Now Fixed

## 2.1 Semantic source

Fixed:

- `meaning_graph_v1_1` is a real emitted artifact, not just a plan.
- Validation confirms stable coverage of the 4 intended source families:
  - `core_story_ui`
  - `user_compact`
  - `personality_imprint`
  - `supporting_threads`
- The builder includes:
  - multi-layer support via `layers[]`
  - `primary_layer`
  - `node_type`
  - `projection_hints`
  - `dedupe_fingerprint`

Cross-check in code:

- [public_builder.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/natal/public_builder.py:117)
- [meaning_graph_v1_1_builder.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/meaning/meaning_graph_v1_1_builder.py:166)
- [meaning_graph_v1_1_builder.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/meaning/meaning_graph_v1_1_builder.py:764)

Not yet fixed:

- consumers are not graph-first in UI
- `meaning_graph` v1 still co-exists
- several render packs still reconstruct meaning independently

Classification: `improved but not done`

## 2.2 Projection

Fixed:

- projection shadow artifacts are emitted in public payloads:
  - `profile_narrative_projection_v1`
  - `profile_v8_projection_v1`
- node/evidence traceability is strong and deterministic
- selection guardrails for projection branches are implemented, including:
  - duplicate fingerprint prevention
  - near-duplicate suppression
  - domain/layer caps
  - V8 shadow cap/floor controls

Cross-check in code:

- [public_builder.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/natal/public_builder.py:124)
- [projection_shadow_v1_builder.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/meaning/projection_shadow_v1_builder.py:61)
- [projection_shadow_v1_builder.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/meaning/projection_shadow_v1_builder.py:618)
- [projection_shadow_v1_builder.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/meaning/projection_shadow_v1_builder.py:1238)

Not yet fixed:

- `profile_narrative_projection_v1` still carries editorial template pressure
- `profile_v8_projection_v1` is still structurally incomplete versus legacy `profile_v8`
- UI migration should still not happen

Classification: `improved but not done`

## 2.3 Selection / ranking / dedup

Fixed:

- The main readiness problem is no longer duplicate/near-duplicate selection.
- Current projection selection state is strong enough to stop changing core selection logic and move effort to voice.
- `profile_v8_payload_builder.py` already has a concrete scoring/dedupe layer for legacy V8 selection.

Cross-check in code:

- [projection_shadow_v1_builder.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/meaning/projection_shadow_v1_builder.py:61)
- [projection_shadow_v1_builder.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/meaning/projection_shadow_v1_builder.py:654)
- [profile_v8_payload_builder.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/natal/profile_v8_payload_builder.py:471)
- [profile_v8_payload_builder.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/natal/profile_v8_payload_builder.py:681)
- [profile_v8_payload_builder.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/natal/profile_v8_payload_builder.py:707)

Important nuance:

- the unified ranking policy is still a **documented policy**, not a single implemented cross-surface selector
- but the current practical blocker is no longer ranking correctness

Classification: `fixed`

## 2.4 Voice Sprint 1

Fixed:

- Phrase-level banned/coaching/jargon regressions targeted in Sprint 1 are cleaned.
- Source-level lint guard exists.
- No rollback is recommended by the post-audit.

Cross-check in code:

- [phrase_lib_tr_profile.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/natal/narrative/phrase_lib_tr_profile.py:65)
- [phrase_lib_tr_profile.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/natal/narrative/phrase_lib_tr_profile.py:143)
- [profile_narrative_engine_signature.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/natal/narrative/profile_narrative_engine_signature.py:205)
- [profile_v8_payload_builder.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/natal/profile_v8_payload_builder.py:201)

Still open:

- pattern-level repetition
- surface-mode mismatch
- semantic enrichment

Classification: `fixed`

## 2.5 Surface mapping

Fixed in current code:

- Home manifesto title is no longer hardcoded; it derives from live narrative snapshot.
- Home central sky quote is removed.
- Home Near/Feed mock friend sections are gated off.
- Profile natal chart wheel section is inserted after the profile hero/header and before deeper content.

Cross-check in code:

- [home_page_v2.dart](/Users/sahradenizozdogan/Astrologi-Ai/mobile/lib/app/tabs/home_page_v2.dart:238)
- [home_page_v2.dart](/Users/sahradenizozdogan/Astrologi-Ai/mobile/lib/app/tabs/home_page_v2.dart:785)
- [home_page_v2.dart](/Users/sahradenizozdogan/Astrologi-Ai/mobile/lib/app/tabs/home_page_v2.dart:1385)
- [home_page_v2.dart](/Users/sahradenizozdogan/Astrologi-Ai/mobile/lib/app/tabs/home_page_v2.dart:1669)
- [profile_page.dart](/Users/sahradenizozdogan/Astrologi-Ai/mobile/lib/app/tabs/profile_page.dart:1301)

Not yet fixed:

- Home still renders `_ChartWheelSection`
- Home render order still does not match orchestration target
- Profile UI still consumes legacy `profile_v8`/threads/sections paths, not projection outputs

Classification: `improved but not done`

## 2.6 Chart wheel

Fixed in current code:

- Profile chart wheel component is integrated.
- `ChartWheelRepository` now sends `birth_place` only, not `city`.
- Profile section first tries local payload parse, then endpoint fallback.

Cross-check in code:

- [chart_wheel_repository.dart](/Users/sahradenizozdogan/Astrologi-Ai/mobile/lib/app/chart/chart_wheel_repository.dart:35)
- [profile_natal_chart_section.dart](/Users/sahradenizozdogan/Astrologi-Ai/mobile/lib/app/profile/profile_natal_chart_section.dart:25)
- [chart_wheel_data.dart](/Users/sahradenizozdogan/Astrologi-Ai/mobile/lib/app/chart/chart_wheel_data.dart:39)

Not yet fixed:

- Home still has a separate old chart wheel section
- `/api/calculate-natal-chart` is still over-broad and privacy-sensitive for wheel use
- Home natal repository still sends both `birth_place` and `city`

Classification: `improved but not done`

## 3. What Is Still Duplicated

## 3.1 Semantic branches

Still duplicated:

- `meaning_graph` v1
- `meaning_graph_v1_1`
- `core_story_ui`
- `user_compact`
- `personality_imprint`
- `supporting_threads`
- `sections_v2`
- `profile_narrative`

Why it matters:

- semantic authority is still distributed
- render packs still reconstruct meaning from multiple source families

Cross-check in code:

- [public_builder.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/natal/public_builder.py:110)
- [public_builder.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/natal/public_builder.py:117)
- [public_builder.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/natal/public_builder.py:157)

Classification: `risky`

## 3.2 Render packs

Still duplicated:

- `profile_v8`
- `full_map_v8`
- `profile_narrative`
- `sections_v2`
- projection shadows for `profile_narrative_projection_v1` and `profile_v8_projection_v1`

Why it matters:

- editorial value exists in legacy packs
- but compute and payload duplication remain high

Classification: `improved but not done`

## 3.3 `profile_v8` / `profile_narrative` / `sections_v2` / `full_map_v8`

Current truth:

- these are all still alive
- the mobile adapter still leans on legacy branches, not graph-first projection

Cross-check in code:

- [profile_v8_adapter.dart](/Users/sahradenizozdogan/Astrologi-Ai/mobile/lib/app/profile/profile_v8_adapter.dart:224)
- [profile_v8_adapter.dart](/Users/sahradenizozdogan/Astrologi-Ai/mobile/lib/app/profile/profile_v8_adapter.dart:250)
- [profile_page.dart](/Users/sahradenizozdogan/Astrologi-Ai/mobile/lib/app/tabs/profile_page.dart:1692)

Classification: `risky`

## 3.4 v1 vs v1.1

Current truth:

- both `meaning_graph` v1 and `meaning_graph_v1_1` are emitted
- current public builder still includes both

Why:

- migration safety
- backward compatibility
- validation runway

Classification: `deferred`

## 4. What Compute Can Now Be Safely Lazy, Gated, Or Pruned

## 4.1 Current `include_full_profile` behavior

Current code already gates:

- `sections_v2`
- `profile_narrative`
- `profile_v8`
- `full_map_v8`

Current code still always builds:

- `supporting_threads`
- `personality_imprint`
- `meaning_graph` v1
- `meaning_graph_v1_1`
- `profile_narrative_projection_v1`
- `profile_v8_projection_v1`

Cross-check in code:

- [natal_interpretation.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/api/routes/natal_interpretation.py:2068)
- [natal_interpretation.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/api/routes/natal_interpretation.py:2082)
- [natal_interpretation.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/api/routes/natal_interpretation.py:2097)
- [public_builder.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/natal/public_builder.py:89)
- [public_builder.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/natal/public_builder.py:124)

Classification: `fixed`

## 4.2 Heavy branches that are safe to keep lazy

Safe to keep lazy for non-profile consumers:

- `profile_narrative`
- `sections_v2`
- `profile_v8`
- `full_map_v8`

Reason:

- current docs and code agree these are heavy render packs
- lazy/full split already proves semantic roots can survive without them

Classification: `ready for implementation`

## 4.3 Heavy branches that are **not** safe to prune yet

Do not prune yet:

- `supporting_threads`
- `personality_imprint`
- `core_story_ui`
- `user_compact`
- `meaning_graph_v1_1`
- `meaning_graph` v1
- projection shadow outputs

Reason:

- `supporting_threads` is still a graph source family
- `personality_imprint` is a major semantic source
- v1/v1.1 dual emission is still part of parity/migration safety
- projection shadows are still needed for readiness monitoring

Classification: `should not be changed`

## 4.4 Candidates for future lazy/debug gating

Candidates:

- `data_quality_summary`
- `narrative_v2` where bundle teaser UI is not used
- `natal_graph_compact` once profile fallback paths stop leaning on it

Classification: `deferred`

## 5. What Voice Work Remains

## 5.1 Phrase-level complete?

Answer:

- Sprint 1 phrase-level target set is complete
- but voice is **not done overall**

Meaning:

- the obvious banned phrases are cleaned
- this does not remove the deeper template pressure

Classification: `fixed`

## 5.2 Pattern-level remaining?

Yes. Major remaining work:

- block-specific `BODY_TEMPLATES_TR` refactor
- `SOFT_ASTRO_HINTS_TR` contrast/rhythm refactor
- `_BUNDLE_HEADLINES` signature-aware reducer
- `_BALANCE_GIFT_LEADS` / fallback rhythm cleanup

Cross-check in code:

- [phrase_lib_tr_profile.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/natal/narrative/phrase_lib_tr_profile.py:65)
- [phrase_lib_tr_profile.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/natal/narrative/phrase_lib_tr_profile.py:99)
- [profile_v8_payload_builder.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/natal/profile_v8_payload_builder.py:404)

Classification: `ready for implementation`

## 5.3 Surface-mode mismatch?

Yes. Remaining examples:

- past-layer certainty pattern
- overly soft/generic astro-hint filtering for profile surfaces
- some cinematic constructions used too broadly

Classification: `improved but not done`

## 5.4 Semantic enrichment?

Still needed:

- `pattern_name`
- canonical `share_line`
- `proof_line`
- `proof_orb`
- `why_now`
- `emotional_intent`
- typed detail block kinds
- wider trigger coverage for talent/mission/past

Classification: `deferred`

## 6. What UI / Surface Work Remains

## 6.1 Home mock cleanup

Cross-check against docs and current code:

- `ManifestoTitle`: fixed in code
- `SkyQuote`: fixed in code
- `NearSection`: fixed in code via gate
- `FeedSection`: fixed in code via gate
- Home chart wheel removal: **not done**
- Home section reorder: **not done**

So the doc backlog is now only **partially current**.

Classification: `improved but not done`

## 6.2 Profile chart wheel integration

Current code:

- integrated in Profile after hero
- tap opens detail sheet
- same reusable wheel widget exists

Remaining:

- remove old Home wheel duplication
- replace broad backend route with geometry wrapper later

Classification: `improved but not done`

## 6.3 Home/Profile orchestration mismatch

Still mismatched:

- Home still has too many sections for the intended orchestration contract
- Home still contains `_ChartWheelSection`
- Profile is still legacy-pack-driven rather than projection-driven

Classification: `risky`

## 6.4 Spec v2 updates

Still needed:

- differentiators / unique facts
- conversation hooks
- affects-you list role
- explicit first_impression vs first_felt doctrine
- domain card role expansion
- archetype portal CTA role
- Home sky-now expansion
- Bond/Friends lattice surface

Classification: `ready for implementation`

## 7. What Should NOT Be Touched Yet

## 7.1 Legacy branches still needed for parity

Do not remove yet:

- `profile_v8`
- `full_map_v8`
- `profile_narrative`
- `sections_v2`
- `supporting_threads`
- `meaning_graph` v1
- projection shadow outputs

Reason:

- they are still needed for live UI, semantic roots, or parity monitoring

Classification: `should not be changed`

## 7.2 Production chart calculation

Do not touch:

- core natal geometry builder
- astrology calculation behavior
- transit engines

Reason:

- chart wheel route hardening should wrap existing builder, not alter math
- transit shares some location machinery and should not be caught in natal cleanup

Classification: `should not be changed`

## 7.3 UI migration to projection

Do not switch UI to:

- `profile_narrative_projection_v1`
- `profile_v8_projection_v1`

Reason:

- readiness docs still place projection at shadow monitoring / voice tuning stage
- mobile adapter is still legacy-driven

Classification: `should not be changed`

## 8. Document Drift To Note

Some referenced docs are now slightly behind current code.

### 8.1 `chart_wheel_data_source_audit.md`

Doc says mobile chart wheel payload still sends both `birth_place` and `city`.

Current code:

- [chart_wheel_repository.dart](/Users/sahradenizozdogan/Astrologi-Ai/mobile/lib/app/chart/chart_wheel_repository.dart:41) sends `birth_place` only

Interpretation:

- the audit is still valid about endpoint breadth/privacy
- but its payload-precedence finding is stale for the Profile chart wheel path

### 8.2 `home_profile_surface_alignment_audit.md` / cleanup plan

Those docs flagged:

- hardcoded manifesto title
- hardcoded sky quote
- mock Near/Feed

Current code shows all four are already addressed.

Interpretation:

- the cleanup plan is still useful
- but current remaining P0 is narrower than the original doc suggests

## 9. Next 5 Implementation Tasks In Safest Order

## 9.1 Task 1

**Finish Home surface cleanup: remove Home chart wheel and reorder Home V2 to the intended short orchestration path.**

Why first:

- user-visible
- additive/risk-contained
- does not depend on projection migration
- cleanup plan already exists

Classification: `ready for implementation`

## 9.2 Task 2

**Harden chart wheel data sourcing: add a minimal geometry-only endpoint wrapper and repoint wheel consumers to it.**

Scope:

- wrap existing natal builder
- do not change chart math
- exclude AI interpretation / formatted extras
- migrate remaining Home natal consumer away from ambiguous raw payload path

Why second:

- current wheel route is over-broad and privacy-sensitive
- profile wheel is live already, so this is now operationally important

Classification: `ready for implementation`

## 9.3 Task 3

**Run Voice Sprint 2 P0: block-specific body templates, soft astro hints rhythm refactor, bundle headline reducer.**

Why third:

- selection is already strong enough
- voice is now the limiting factor before any projection migration
- this improves both legacy/projection perceived quality without schema churn

Classification: `ready for implementation`

## 9.4 Task 4

**Add spec v2 catch-up for surfaces and roles.**

Scope:

- update `shou_surface_orchestration.md`
- document differentiators, conversation hooks, affects-you, domain cards, archetype portal, Bond/Friends lattice, sky-now

Why fourth:

- implementation is already ahead of the spec in several places
- spec drift is starting to obscure what is actually done

Classification: `ready for implementation`

## 9.5 Task 5

**Add telemetry/fallback instrumentation before any compute pruning or projection migration.**

Scope:

- field-read telemetry by surface
- fallback-hit counters in mobile adapters
- payload and render timing by branch

Why fifth:

- this is the safe prerequisite for pruning legacy packs later
- without it, consolidation risks breaking hidden fallback paths

Classification: `ready for implementation`

## 10. Final Recommendation

The safest consolidation strategy is:

1. finish the **surface cleanup that is already partially underway**
2. harden the **chart wheel endpoint contract**
3. spend the next backend iteration on **voice pattern quality**, not on another selection rewrite
4. keep **legacy render packs and dual graph emission** alive until telemetry and parity say otherwise
5. do **not** start UI migration to projection until voice and completeness catch up

This means the system is best described today as:

- **semantic source established**
- **projection infrastructure established**
- **selection stabilized**
- **voice partially stabilized**
- **surfaces partially cleaned**
- **full consolidation still ahead**
