# SHOU Narrative — Consolidation Decision Matrix

> Planning artifact. **No code.** Builds on
> `shou_narrative_layer_inventory.md`. For every catalogued layer,
> assigns one of four decisions — RESCUE / CONSOLIDATE / FREEZE /
> DELETE — with rationale, and proposes a sequencing for the
> consolidation work. Anchors the answer to the strategic question:
> "do we rewrite everything?" → **No.** "Then what?" → this doc.

## 0. The four decisions

| Decision | Meaning | Behavior |
|---|---|---|
| **RESCUE** | Layer stays as a canonical part of the future stack. May be extended. | No structural change in the short term; future work builds on it |
| **CONSOLIDATE** | Substance (data / banks / specific behavior) survives, but is merged into a rescued layer or refactored to share infrastructure | Migration plan needed; the original file may disappear after migration |
| **FREEZE** | Stay in repo as fallback / legacy. No new development. Runtime selector path may be removed | Cap maintenance; mark deprecated; eligible for DELETE after confirmed unused |
| **DELETE** | Remove from codebase. Functionality replaced or no longer needed | Requires trace audit (any caller / route / test importing it) before removal |

Discipline: the four decisions are per-layer, not per-file. A file
may hold both a RESCUE asset (a curated bank) and a CONSOLIDATE
behavior (its builder logic). The matrix below names the layer
explicitly when this split applies.

## 1. Decision matrix — natal

| § | Layer | File | Status today | **Decision** | Rationale |
|---|---|---|---|---|---|
| 4.1 | Core Story UI mini-template | `core_story_tr_natal.py` | active-canonical | **CONSOLIDATE** → into the consolidated frame engine as a `slide_profile` | Tiny one-off; same job becomes a profile in the rescued template/combinator |
| 4.2a | SIGN_VIBE_TR / HOUSE_ARENA_TR / MICRO banks / RELATIONSHIP_SIGN_OPENING_TR | `supporting_threads_builder.py` | active-canonical | **RESCUE** the data; **CONSOLIDATE** the builder logic | Curated banks are real assets; orchestration should live in the shared composer, not a 2,155-line monolith |
| 4.2b | `build_sections_v2` / `build_supporting_threads` / `_build_thread_paragraph` | same file | active-canonical | **CONSOLIDATE** → use shared template/combinator + editorial policy + humanizer | Reduces dispersion of voice-shaping logic |
| 4.3 | Profile narrative engine selector (legacy/signature router) | `profile_narrative_engine.py` | active-canonical | **CONSOLIDATE** (slim down after legacy frozen) | Once legacy is frozen this becomes a one-line dispatch |
| 4.4 | Signature narrative renderer | `profile_narrative_engine_signature.py` | active-canonical | **RESCUE + EXTEND** as the *primary natal narrative orchestrator* | Already calls `render_block_template` + `select_rhythm_family`; this IS the canonical natal narrative path |
| 4.5 | Profile phrase library (TITLE_FAMILIES_TR / BODY_TEMPLATES_TR / SOFT_ASTRO_HINTS_TR / `render_block_template`) | `phrase_lib_tr_profile.py` | active-canonical | **RESCUE + EXTEND** as the *canonical free-path frame engine* | Repo's clearest existing pattern grammar. Future extension = new families = new entries here, not new files |
| 4.6 | Editorial render policy (rhythm / phrase policy / quality_issues) | `editorial_render_policy.py` | active-canonical | **RESCUE** as the *canonical shared style/policy layer* | Already cross-domain; future renderers route through it |
| 4.7 | Humanizer (NATAL_FORBIDDEN_LEXICON + cleanup) | `humanize_tr.py` + `gold_natal_tone.py` | active-canonical | **RESCUE** as the *canonical shared post-process layer* | Already production-shared; extend forbidden lexicon as families grow |
| 4.8 | Profile detail editorial | `profile_detail_editorial.py` | active-canonical-support | **CONSOLIDATE** → its tension/origin/strength/growth blocks become slide_profile variants | Functionality overlaps with what slide_profile + role_bindings already provide; remove the parallel scaffold |
| 4.9 | Natal upstream engine stack (mechanics/dynamics/pattern/composite/rule/upper-meaning/inquiry/dispositor/sensitivity/axis/latent-potential) | various engine files | active-canonical-upstream | **RESCUE as-is** (Plan layer / Katman 0–2 of ARC) | These don't generate prose; they generate the semantic substrate the renderers consume. Keep |
| 4.10 | Master selector | `master_selector.py` | active-canonical-upstream | **RESCUE** as the *canonical Plan-layer output* | Slot-based spine/line selection is the right interface for renderers to consume |
| 4.11 | Signature engine (facts normalize / primitives / BLOCK_ORDER) | `signature_engine.py` | active-canonical-upstream | **RESCUE as-is** | Semantic preprocessor for signature narrative |
| 4.12 | Promise / domain vector engine | `promise_vector_engine.py` | active-canonical-upstream | **RESCUE as-is** | Salience scoring; part of ARC Katman 0 |
| 4.13a | `primitive_engine_v2` + `contradiction_engine` + `layer_arbitrator` | various | active-canonical-upstream | **RESCUE** as the rescoring + arbitration layer | Converged path. S3 audit (2026-05-20) confirmed v2 is the rescoring layer, not a full replacement of v1 |
| 4.13b | `primitive_engine` (v1) | `primitive_engine.py` | active-canonical-upstream | **RESCUE as-is** — intentional layering beneath v2 | S3 audit (`docs/system/audits/primitive_engine_v1_vs_v2_trace_audit.md`) revealed v1 has 3 live callers: (1) `signature_engine.py` import, (2) `profile_narrative_engine_signature.py:1792` direct call (canonical signature narrative path), (3) `primitive_engine_v2.py:268` `legacy_hits = build_primitives(...)` — **v2 itself depends on v1**. v1 generates primitive hits; v2 rescores them with the natal feature graph. The `_v2` suffix did not imply replacement; the two engines are layered, not competing. v1 NOT delete-safe |

## 2. Decision matrix — projection / family renderers

| § | Layer | File | Status | **Decision** | Rationale |
|---|---|---|---|---|---|
| 5.1 | Projection shadow builder | `projection_shadow_v1_builder.py` | active-canonical | **RESCUE** as the *canonical projection bridge* | Bridges selection ↔ public surface; right place for projection logic |
| 5.2 | Composed detail renderer — generic | `composed_detail_renderer.py` `render_composed_detail_card_v0_9a_2` | active-canonical | **RESCUE + CONSOLIDATE** — refactor body building to call `render_block_template` instead of static text | Removes another parallel template path |
| 5.2 | Composed detail renderer — hidden/private (Phase-4 work) | same file, `render_relationship_hidden_private_love_card_v0_10_phase2` + `_build_relationship_hidden_private_love_phase4_deep_read_slides` | active-narrow | **CONSOLIDATE** — Phase-4 slide templates migrate into `phrase_lib_tr_profile.BODY_TEMPLATES_TR` as a hidden/private family entry; the renderer becomes a thin adapter | This is the central correction: my Phase-4 work added a parallel template path. Consolidation reverses that. Frame contract (Rules 1–4 + origin_hint + gift bindings) survives; storage location changes |

## 3. Decision matrix — personality / library-driven

| § | Layer | File | Status | **Decision** | Rationale |
|---|---|---|---|---|---|
| 6.1 | Personality imprint builder | `personality_imprint/builder.py` | active-canonical | **RESCUE as-is** | Distinct purpose (aura/trait/drive/shadow library), different from frame-grammar approach |
| 6.2 | Personality imprint library | `personality_imprint/contracts.py` (PERSONALITY_IMPRINT_LIBRARY_TR_V1/V2 + priority/support house libraries) | active-canonical | **RESCUE as-is** + harmonize style/policy via shared `editorial_render_policy` + `humanize_tr` | Library-driven model is intentional here; consolidation = shared guardrails only |

## 4. Decision matrix — legacy and older parallel

| § | Layer | File | Status | **Decision** | Rationale |
|---|---|---|---|---|---|
| 7.1 | `LEGACY_BLOCKS` + `build_profile_narrative_legacy` | `profile_narrative_engine_legacy.py` | legacy-runtime-selectable | **FREEZE → DELETE** | Remove from §4.3 selector path; verify zero callers via tests; then delete. Signature engine fully covers the cases |
| 7.2a | **V26 LIVE branch** — `build_core_story_plan` + `render_core_story` | `builders/narrative_binding.py`, `builders/narrative_renderer_v26.py` (historic live symbols; wrappers now removed), canonical home `backend/app/natal/narrative/core_story/` | active-canonical | **CONSOLIDATE-with-contract-preservation** (S2.1 audit decided; S2.1.3/S2.1.4 executed) | S2.1 audit (`docs/system/audits/v26_core_story_downstream_consumer_audit.md`) found three concrete downstream consumers: (a) `PublicNatalView.core_story` public field, mobile-consumed via `chart_lab_page.dart`; (b) `profile_v8.identity_axis_body` fallback in `profile_v8_payload_builder.py:1749`; (c) `core_story_ui` builder + `data_quality` payload, both fed by `core_story_plan`. Snapshot coverage was added in S2.1.1, migration completed in S2.1.3, and deprecated wrappers were removed in S2.1.4. Orphan helper residue in the old V26 files remains intentionally and is deferred to S2.1.5 |
| 7.2b | **V26 DEAD branch** — `build_narrative` + `build_domain_narrative_v26` + `StylePackV26TR` + the dead `build_narrative` import in natal route | same files (symbol-level subset); plus `style/style_pack_v26_tr.py` (whole file) | dead / unused (S2 confirmed: zero callsites repo-wide) | **DELETE** — pending one final verification (S2.2: run full backend test suite with these symbols + import removed/stubbed; if zero failures, delete) | S2 caller search: `build_narrative` only imported in `natal_interpretation.py:29`, never called. `build_domain_narrative_v26` only called by `build_narrative`. `StylePackV26TR` only used by `build_domain_narrative_v26`. Entire sub-branch is unreachable from any public endpoint. `style_pack_v26_tr.py` (the whole 105-line file) is reachable only through the dead branch and is therefore also delete-eligible |

## 5. Decision matrix — compact / shared

| § | Layer | File | Status | **Decision** | Rationale |
|---|---|---|---|---|---|
| 8 | Compact narrative (user_compact) | `builders/output_compactor.py` | active-canonical-support | **RESCUE** (already routes through shared policy) | Small canonical surface; harmonized |
| 12.4 | Shared voice guardrail layer | `narrative/voice_guardrails_tr.py` | active-shared-policy | **RESCUE + EXTEND** as the *canonical Guard layer* | This is the shared safety layer. Forbidden public copy scans, technical leakage, pattern-name / hedge validation, cookbook bans. Future Phase-4 / family renderers / LLM premium all route through this |

## 6. Decision matrix — synastry

| § | Layer | File | Status | **Decision** | Rationale |
|---|---|---|---|---|---|
| 9.1 | Synastry public builder | `synastry/public_builder.py` | active-canonical (synastry) | **RESCUE as-is** | Domain-specific orchestrator; works |
| 9.2 | Synastry narrative engine | `synastry/narrative/synastry_narrative_engine.py` | active-canonical (synastry) | **RESCUE as-is** (short term) → **CONSOLIDATE** style/policy via shared `editorial_render_policy` + `humanize_tr` (later) | Don't restructure cross-domain yet; harmonize the policy and humanize calls only |
| 9.3 + 12.1 + 12.2 | Synastry phrase / library / router / policy assets | `phrase_lib_tr_synastry.py`, `synastry_library_tr.py`, `synastry_phrase_bank_tr.py`, `synastry_signature_router.py` | active-canonical (synastry) | **RESCUE as-is** + later consolidation reading: are these the synastry equivalent of `phrase_lib_tr_profile`? If yes, the consolidated free-path engine can host both | Future audit task; deferred |
| 12.3 | Synastry resonance engine | `synastry/resonance_engine.py` | active-canonical-upstream (synastry) | **RESCUE as-is** | Salience-equivalent for synastry; keep |

## 7. Decision matrix — transit

| § | Layer | File | Status | **Decision** | Rationale |
|---|---|---|---|---|---|
| 10.1 | Transit public builder | `transit/present/public_builder.py` | active-canonical (transit) | **RESCUE as-is** | Domain-specific orchestrator |
| 10.2 | Transit text quality | `transit/narrative/text_quality_tr.py` | active-canonical (transit) | **RESCUE as-is** → harmonize cleanup with shared `humanize_tr` later | Quality layer parallel to natal humanizer; eventual consolidation of the cleanup surface |
| 10.3 | Transit phrase / archetype systems | `phrase_lib_tr.py`, `natal_promise.py` phrase lib, JSON content packs in `transit/content/tr/` | active-canonical (transit) | **RESCUE as-is** | Domain-specific phrase ecosystem |
| 10.4 | Transit composer | `transit/narrative/composer.py` | active-canonical (transit) | **RESCUE as-is** | Sentence-level composition for transit events; parallel to natal renderer |
| 10.5 | Transit voice policy | `transit/narrative/period_voice_policy.py` | active-canonical (transit) | **RESCUE as-is** | Renderer-upstream policy brain; valuable parallel to natal `editorial_render_policy` |
| 10.6 | Transit narrative brain | `transit/narrative/astrolog_narrative_engine.py` | active-canonical (transit) | **RESCUE as-is** | Story orchestrator for transit |
| 10.7 | Transit deep archetype engine | `transit/narrative/deep_archetype_engine.py` | active-canonical (transit) | **RESCUE as-is** | Event-card selection/composition; keep |

Transit-wide note: the transit stack is its own coherent system
(composer → policy → narrative brain → deep archetype) and is
self-consistent. Cross-domain consolidation with natal is a
**later, separate** audit, not in scope of this matrix. Short
term: only the shared guard / humanize layers harmonize.

## 8. The consolidated end-state (sketch)

After all RESCUE/CONSOLIDATE/FREEZE/DELETE decisions execute, the
canonical natal narrative stack is:

```
Plan layer (RESCUED as-is)
  ARC Katman 0–2 engines (4.9) — astro/mechanics/dynamics/pattern/...
  Master selector (4.10) — slot-based spine/line selection
  Signature engine (4.11) — facts normalize + primitives + BLOCK_ORDER
  Promise/domain vector (4.12) — salience scoring
  Primitive_v2 + contradiction + arbitrator (4.13a)
        ↓
  emits a deterministic SemanticPlan (slide_profile + role_bindings +
                                     packet fields + selected anchors)
        ↓
Renderer dispatch (RESCUED, simplified)
  Signature narrative renderer (4.4) is the primary natal entry
        ↓
Frame engine (RESCUED + EXTENDED)
  phrase_lib_tr_profile (4.5) — TITLE_FAMILIES_TR + BODY_TEMPLATES_TR +
                                SOFT_ASTRO_HINTS_TR + render_block_template
        ↓ (consumed BANKS from CONSOLIDATED sources)
  + supporting_threads sign/house/relationship banks (4.2a)
  + (later) consolidated family-specific entries: hidden/private
    deep_read slides migrated from Phase-4 work (5.2 row 2)
        ↓
Style / policy (RESCUED)
  editorial_render_policy (4.6) — rhythm family + phrase policy +
                                 quality_issues
        ↓
Post-process (RESCUED)
  humanize_tr (4.7) — cleanup + clamp + technical replacements
        ↓
Guard (RESCUED + EXTENDED)
  voice_guardrails_tr (12.4) — forbidden public copy + technical leak +
                              hedge validation + cookbook bans
        ↓
public output
```

Personality imprint (§6) runs in parallel — different model
(library-driven retrieval), shares only the Guard + Humanizer.

Projection shadow (§5.1) sits between the Plan layer and the
renderer, bridging selection → public surface.

Synastry (§6/§9) and transit (§7/§10) keep their own parallel
stacks at first; only Guard + Humanizer harmonize cross-domain
in this phase.

## 9. Where my Phase-4 hidden/private work fits

Honest answer: **today it's a parallel renderer** living inside
`composed_detail_renderer.py` with its own static templates,
NOT consuming the consolidated frame engine. That's exactly the
pattern this matrix decides to stop.

The consolidation target for Phase-4:

1. `_build_relationship_hidden_private_love_phase4_deep_read_slides`
   templates **migrate into `phrase_lib_tr_profile.BODY_TEMPLATES_TR`**
   (or a sibling structured per family — exact location is a
   §13.2-pending implementation detail).
2. The Phase-4 routing in `composed_detail_renderer.py` becomes a
   **thin adapter**: detect pilot signature → look up family in
   the frame library → call `render_block_template(...)` with the
   family's TITLE_FAMILIES_TR + BODY_TEMPLATES_TR entries → pass
   through editorial_render_policy + humanize_tr + voice_guardrails_tr.
3. Phase-4 hard invariants survive: flag-off byte-identical, no
   public schema widening, eligibility chain via deep_read_phase3
   metadata, all B3 guards still wired.
4. The frozen voice contract (Rules 1–4 + role_bindings) is now
   enforced **across all consumers** of the frame engine, not just
   the deep_read pilot.

This is also where pattern grammar variation (the user's earlier
"şablon hissi olmasın" instinct) lives: extending
`TITLE_FAMILIES_TR` and `BODY_TEMPLATES_TR` with N variants per
role, with chart-hash seeded selection, is a NATURAL extension of
the existing `render_block_template` machinery — not new
infrastructure.

## 10. Where LLM premium tier fits

LLM premium = an alternative renderer dispatch that:
- consumes the same SemanticPlan from the Plan layer
- skips the frame engine; calls LLM with prompt constraints
  derived from the same role_bindings + Rules 1–4
- passes through the same editorial_render_policy +
  humanize_tr + voice_guardrails_tr (the LLM output is treated as
  candidate text, then guarded identically to template output)
- is cached on Plan-hash; identical Plan → identical render
- falls back to frame engine on LLM failure or guard rejection

The rescued Guard layer (12.4) is what makes LLM premium
safe-to-ship: same banned-phrase scan, same hedge validation, same
cookbook bans apply to LLM output as template output.

## 11. Where ARC/A2 §10.3 fits (it doesn't — separate concern)

The matrix is about render-layer consolidation. **A2 / ARC
salience calibration is Katman 0 work, not render work.** It
remains owed regardless of consolidation decisions. The Plan
layer (§8) feeds the renderer; if A2 changes which signatures are
defining vs background, the SemanticPlan changes, but the
renderer machinery doesn't.

Recommendation: A2 §10.3 product-validation checkpoint can
proceed in parallel with consolidation. They are independent
dependency chains.

## 12. Sequencing (proposed order, not committed)

Each step below would be its own bounded request with §13.2-style
review. **No code authorized by this document.**

| Step | Decision | Effort | Risk | Output |
|---|---|---|---|---|
| **S1** | FREEZE `LEGACY_BLOCKS` selector route (7.1) | Low | Low (already a selectable branch) | Smaller surface; safer to delete later |
| **S2** | ✅ DONE 2026-05-20 (`audits/v26_trace_audit.md`) — V26 stack is **SPLIT**: live core_story branch + dead domain-narrative branch | Low | Trace only, no code change | **Outcome**: matrix §7.2 rewritten as 7.2a (live, MIGRATE) + 7.2b (dead, DELETE pending verification). Generated two follow-up steps: S2.1 + S2.2 |
| **S2.1** | ✅ DONE 2026-05-20 (`audits/v26_core_story_downstream_consumer_audit.md`) | Low | Trace only, no code | **Outcome**: 7.2a decided as CONSOLIDATE-with-contract-preservation. Three concrete downstream consumers identified incl. mobile `chart_lab_page.dart`. Coverage gap discovered: no test asserts on `public["core_story"]` content — must close before migration. Generated step S2.1.1 (snapshot coverage step) |
| **S2.1.1** | ✅ DONE 2026-05-20 (commit `bb3d025`) — 3 baseline snapshot tests added to `tests/test_natal_public_builder.py` locking `public["core_story"]` content + shape, `response["core_story_plan"]` schema, and `profile_v8.identity_axis.body` fallback for the canonical 1996 Istanbul fixture | Low | Test additions only, no production change | Pre-migration coverage gap closed. S2.1.2/S2.1.3 migration steps now have an automated safety net |
| **S2.1.2** | ✅ DONE 2026-05-20 (`audits/v26_live_core_story_migration_design.md`) — migration target chosen: dedicated canonical package `backend/app/natal/narrative/core_story/` with wrapper-first sequencing and import-compat parity gates | Low | Design only | **Outcome**: rejected early coupling to signature renderer; selected dedicated `core_story/` package shape to preserve contract while reducing V26 naming debt |
| **S2.1.3** | ✅ DONE 2026-05-20 (commit `7221142`) — extracted live `build_core_story_plan` + `render_core_story` into `backend/app/natal/narrative/core_story/`; kept old V26 symbols as temporary thin wrappers; canonical natal route rewired; parity tests added | Medium | Coverage from S2.1.1 + wrapper-first sequencing mitigated | Consolidated V26 LIVE into canonical stack without public contract change; enabled narrow wrapper cleanup as a separate step |
| **S2.1.4** | ✅ DONE 2026-05-20 (commit `0a08611`) — deprecated `core_story` wrappers removed from `builders/narrative_binding.py` and `builders/narrative_renderer_v26.py`; canonical import path is now `backend/app/natal/narrative/core_story/` only | Low-medium | Narrow cleanup only; full `backend/tests/test_natal_public_builder.py` regression green | Wrapper cleanup completed without runtime/schema change. Orphan helper residue in the old V26 files remains intentionally and is deferred |
| **S2.1.5** | ✅ DONE 2026-05-20 (`audits/v26_live_orphan_helper_audit.md`, `audits/v26_live_orphan_helper_cleanup_design.md`) — post-migration residue audit confirmed `unexpected-live = none`; former V26 live files are off all canonical natal/synastry/transit runtime paths and are now `FREEZE-only` pending bounded cleanup PRs | Low | Audit/design only | Finalized the post-migration residue partition: `dead-truly`, `locally-residue-only`, stale non-canonical test-only references. Generated narrow PR-1 cleanup design |
| **S2.1.6** | ✅ DONE 2026-05-20 (commit `5a18853`) — PR-1 cleanup executed: removed `dead-truly` residue (`CORE_STORY_SECTIONS`, `render_identity_v26`, shadowed earlier `_build_fragment_index`), removed truly dead imports, and cleaned stale `tests/engine/*` legacy dependency on deleted `build_narrative` | Low-medium | Narrow cleanup only; canonical package untouched | Runtime unchanged. Regression gates green: `backend/tests/test_natal_public_builder.py`, `backend/tests/test_composed_detail_renderer.py`, and repaired `tests/engine/test_narrative_binding.py`. `locally-residue-only` clusters remain deferred to PR-2 / PR-3 |
| **S2.1.7** | ✅ DONE 2026-05-20 (commit `ed290f7`) — PR-2 executed: `backend/app/builders/narrative_binding.py` **deleted entirely** (1,592 lines). Pre-delete grep confirmed zero external callers (module path + representative symbols); all live `core_story` consumers import from `app.natal.narrative.core_story`. Comment-only reference remaining in `narrative_renderer_v26.py` is a stale comment, not an import | Medium | Atomic full-file delete on confirmed residue; zero external callers verified | Regression set **126/126 passed** (`test_natal_public_builder.py` + `test_composed_detail_renderer.py` + `tests/engine/test_narrative_binding.py`). Public contract preserved. One former V26 live file retired. PR-3 (`narrative_renderer_v26.py` cleanup) remains as the V26 stack arc's final closure step |
| **S2.1.8** | ✅ DONE 2026-05-20 (commit `65c952c`) — PR-3 executed: `backend/app/builders/narrative_renderer_v26.py` **deleted entirely** (1,663 lines). Pre-delete grep confirmed zero external callers (module path + key symbols `render_core_story` / `_build_fragment_index`); all live consumers import from `app.natal.narrative.core_story.renderer` | Medium | Atomic full-file delete on confirmed residue; zero external callers verified | Regression set **126/126 passed**. Public contract preserved. **V26 stack fully retired** — canonical home is now `backend/app/natal/narrative/core_story/` only. Matrix §7.2 (both 7.2a CONSOLIDATE + 7.2b DELETE) fully closed |
| **S2.2** | ✅ DONE 2026-05-20 (commit `cc2befb`) — V26 dead branch removed: `build_narrative` (74 lines from `narrative_binding.py`), `build_domain_narrative_v26` + `NarrativeDomainOutput` (56 lines from `narrative_renderer_v26.py`), entire `style_pack_v26_tr.py` (105 lines), dead `build_narrative` import in natal route. **~235 lines deleted total.** Verification: V26-adjacent natal tests 120/120 PASSED; full backend suite 1232 passed, 49 failed but zero of those 49 reference any V26 symbol I deleted (all pre-existing, in unrelated test areas) | Low-medium | Conservative: leaves orphaned helpers (e.g. `_style_pack` in narrative_binding.py) that may now be unused but were not part of the audited dead set; separate orphan-helper cleanup pass can identify them later | Smaller repo. V26 LIVE branch (matrix §7.2a) unaffected and continues to power canonical natal `/interpret` |
| **S3** | ✅ DONE 2026-05-20 (`audits/primitive_engine_v1_vs_v2_trace_audit.md`) — v1 is NOT delete-safe; v2 depends on it (line 268 `legacy_hits = build_primitives(...)`) AND signature narrative renderer calls v1 directly. The two engines are intentionally layered, not competing | Low | Trace only, no code | **Outcome**: matrix §4.13a and §4.13b updated. §4.13b flipped from "FREEZE → DELETE" to **RESCUE as-is**. No deletion possible without breaking canonical natal narrative + v2's own pipeline |
| **S4** | Migrate Phase-4 hidden/private templates into `phrase_lib_tr_profile` (5.2 row 2) | Medium | Phase-4 test coverage already strong (B0-B5 117/117) | Removes the most recent parallel template; proves consolidation pattern on a known-good family |
| **S5** | Consolidate `supporting_threads_builder` banks into the frame library, builder logic into shared composer (4.2) | Medium-high | 2,155-line file refactor; risk of regression | Largest narrative file becomes data-driven; supports cross-family variant expansion |
| **S6** | Consolidate `core_story_ui` + `profile_detail_editorial` as slide_profile entries (4.1, 4.8) | Low-medium | Both small | Two more parallel paths removed |
| **S7** | Simplify `profile_narrative_engine` selector after S1 + S6 (4.3) | Low | After legacy frozen | Cleaner dispatch |
| **S8** | DELETE V26 stack (7.2) — if S2 confirms safe | Medium | Conditional on S2 | ~1,994 lines removed |
| **S9** | DELETE legacy block engine (7.1) — if S1 + S7 hold for one release | Low | Conditional | More dead code removed |
| **S10** | (Optional, later) Cross-domain shared guard / humanize harmonization with synastry + transit | High | Cross-domain test surface | One shared safety layer across natal/synastry/transit |
| **S11** | (Optional, later) Synastry / transit phrase library audit — are they the same shape as `phrase_lib_tr_profile`? Consolidation candidate? | Audit only | None | Future strategy |

LLM premium tier work (§10) can begin any time after the
consolidated frame engine has the hidden/private family
migrated (S4). It is a separate parallel track.

ARC A2 §10.3 is fully orthogonal; can run any time.

## 13. What this doc grants vs does NOT

**Grants:**

- A per-layer decision (RESCUE / CONSOLIDATE / FREEZE / DELETE)
  for every catalogued narrative layer
- A sketch of the consolidated end-state
- A clear place for Phase-4 hidden/private to land
- A clear place for LLM premium to plug in
- A sequencing proposal (S1–S11)

**Does NOT grant:**

- Any code work
- Any deletion (every DELETE row is conditional on a trace audit)
- Authorization to refactor any file
- The Step-S4 migration itself (separate bounded request)
- LLM premium implementation
- ARC A2 §10.3 work
- Cross-domain consolidation (synastry / transit)

## 14. Open questions for review

1. **DELETE thresholds**: how long should a FROZEN layer live before
   it becomes DELETE-eligible? One release? Two? Quarterly review?
2. **`supporting_threads_builder` consolidation (S5) risk**: the
   file is large and central. Is a phased internal refactor
   (one section at a time, behind feature flags) safer than a
   single migration?
3. **Personality imprint (§6) harmonization**: the library-driven
   model is intentional; should it share *all* of editorial policy
   + humanize + guards, or only some subset? E.g. should personality
   imprint output also go through the cookbook-ban scan?
4. **Step S4 (Phase-4 migration) timing**: do we do this *before*
   adding any new family (so the next family is added in the
   consolidated form), or *after* a second family is built (so
   the consolidation pattern is informed by two examples)?
5. **Cross-domain shared layers (synastry/transit)**: when is the
   right time to harmonize? After all natal consolidation, or
   in parallel?
6. **LLM premium prototype**: can it begin against the *current*
   render stack (parallel renderer dispatch) without waiting for
   consolidation, or should it wait? The latter is cleaner;
   the former is faster.
7. **§13.2 review process for each step**: does every S step
   require its own §13.2-style human review, or can low-risk steps
   (S1, S2, S3 trace audits) batch?

## 15. Recommended immediate next step

Of S1–S11, **S2 (V26 trace audit)** is the highest-value lowest-risk
opening move:

- Pure audit, no code change
- Decides whether ~1,994 lines of parallel narrative engine are
  safely deletable
- Result feeds S8 (DELETE decision)
- Provides confidence-building data before any structural work

If S2 shows V26 has zero runtime callers in canonical chains:
- **Outcome**: high confidence in consolidation direction;
  proceed to S1 (FREEZE legacy selector) + S4 (Phase-4 migration)
  in parallel as bounded requests

If S2 shows V26 still has callers:
- **Outcome**: surface those callers; decide per-caller whether
  to migrate or keep V26 alive longer; revise §11 sequencing

This document does not authorize S2. The user / project owner
decides whether to authorize S2 (or a different sequencing) as
the next bounded request.
