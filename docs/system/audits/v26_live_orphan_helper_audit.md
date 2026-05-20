# S2.1.5 — V26 LIVE Orphan Helper Audit

## Scope

This is an audit-only artifact.

No code.
No runtime change.
No deletion.
No refactor.

Target files:

- `backend/app/builders/narrative_binding.py`
- `backend/app/builders/narrative_renderer_v26.py`

Question:

After S2.1.3 migrated live `core_story` into
`backend/app/natal/narrative/core_story/` and S2.1.4 removed the old
wrappers, what residue remains in the former V26 live files, and is any
of it still reachable from canonical runtime?

This audit starts from the S2.1.3 Step 0.5 partition:

- `docs/system/audits/v26_live_core_story_helper_dependency_audit.md`

and re-verifies it post-migration / post-wrapper-removal.

## Executive verdict

The old V26 live files are no longer on any canonical natal, synastry, or
transit runtime path.

### Main result

- **No canonical public endpoint reaches the residue**
- **No current natal/synastry/transit public builder imports these files**
- Remaining symbols partition cleanly into:
  - **dead-truly**
  - **locally-residue-only**
  - **test-only stale legacy references** outside the canonical backend
- **No unexpected-live caller was found**

### File-level recommendation

- `backend/app/builders/narrative_binding.py` → **FREEZE-only**
- `backend/app/builders/narrative_renderer_v26.py` → **FREEZE-only**

Reason:

- runtime is already off these files
- but residue cleanup should still be a separate bounded PR
- `tests/engine/*` still contains stale legacy imports of
  `build_narrative`, so file-level deletion is not yet the right
  recommendation from this audit alone

### Recommendation label

**FREEZE-only**

Not `MIGRATE-callers-first`:

- because no live caller remains to migrate

Not `DELETE-safe`:

- because residue still needs symbol-level cleanup, and stale non-canonical
  test imports still exist in the repo

## 1. Call chain evidence

### 1.1 Canonical live chain today

The canonical natal route now imports only the new package:

- [backend/app/api/routes/natal_interpretation.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/api/routes/natal_interpretation.py:29)
  - `from app.natal.narrative.core_story import build_core_story_plan, render_core_story`
- [backend/app/api/routes/natal_interpretation.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/api/routes/natal_interpretation.py:2580)
  - `response["core_story_plan"] = build_core_story_plan(...)`
- [backend/app/api/routes/natal_interpretation.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/api/routes/natal_interpretation.py:2588)
  - `response["core_story"] = render_core_story(...)`

Live package entrypoint:

- [backend/app/natal/narrative/core_story/__init__.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/natal/narrative/core_story/__init__.py:1)

### 1.2 Current reachability result

Repo-wide import/caller trace for:

- `app.builders.narrative_binding`
- `app.builders.narrative_renderer_v26`
- `build_core_story_plan`
- `render_core_story`

found:

- canonical runtime imports only the new `core_story/` package
- no current synastry or transit public path imports the former V26 live
  files
- no `backend/app/*` public builder path imports the old V26 live modules

### 1.3 Non-canonical stale references

Two root-level legacy tests still reference removed dead-branch symbols:

- [tests/engine/test_narrative_binding.py](/Users/sahradenizozdogan/Astrologi-Ai/tests/engine/test_narrative_binding.py:12)
- [tests/engine/test_narrative_voice_invariants.py](/Users/sahradenizozdogan/Astrologi-Ai/tests/engine/test_narrative_voice_invariants.py:12)

These are not canonical backend runtime callers. They are stale test-only
legacy references and are one reason this audit stops at `FREEZE-only`
rather than file-level `DELETE-safe`.

## 2. Caller table

| Symbol / file | Current caller class | Evidence | Verdict |
|---|---|---|---|
| `app.builders.narrative_binding` | test-only stale legacy reference | `tests/engine/test_narrative_binding.py`, `tests/engine/test_narrative_voice_invariants.py` import removed `build_narrative` | non-canonical / stale |
| `app.builders.narrative_renderer_v26` | none found | no repo import/caller of the module path remained | no caller |
| `build_core_story_plan` old path | none | canonical route imports package path only | no caller |
| `render_core_story` old path | none | canonical route imports package path only | no caller |
| residue helpers / constants / classes | none external by module path | no external imports of private residue symbols found | file-local only |

Important note:

Same-name functions elsewhere in the repo are **not** treated as callers.
For example, `_join_sentences`, `_fingerprint_text`, or `_clamp` appear in
other modules, but those are independent definitions, not imports of this
residue.

## 3. Post-S0.5 partition

S2.1.3 Step 0.5 already split symbols into `move-with` and
`orphan-later`. After S2.1.3 and S2.1.4:

- the `move-with` sets now live in `backend/app/natal/narrative/core_story/`
- the old files contain only residue

This audit tightens residue into:

- `dead-truly`
- `locally-residue-only`
- `unexpected-live`

Result:

- `unexpected-live` = **none**

## 4. `narrative_binding.py` residue

### 4.1 Dead-truly

These symbols are not used by canonical runtime and are not even used
locally by the remaining residue root graph:

- [CORE_STORY_SECTIONS](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_binding.py:26)
- [render_identity_v26](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_binding.py:1606)

Dead-import candidates:

- `build_claim`
- `default_phrase_map_config`

These imports are no longer loaded by any reachable live behavior in the
file.

### 4.2 Locally-residue-only

These are still internally referenced by other residue in the same file,
but no canonical runtime reaches them anymore:

- `_domain_order`
- `_domain_slots`
- `_build_recognition`
- `_build_experienced`
- `_build_potential`
- `_build_shadow`
- `_build_upper`
- `_selected_text`
- `_resolve_tone_profile`
- `_apply_tone_safe`
- `_domain_title`
- `_domain_title_from_focus`
- `_style_pack`
- `_SafeDict`
- `_render_template_paragraphs`
- `_join_paragraphs`
- `_plan_tokens`
- `normalize_text`
- `_dedup_slots`
- `_apply_slot_budget`
- `_cast_fragment`
- `_fragment_signature`
- `_rule_group`
- `_compute_salience`
- `_orb_strength`
- `_find_orb`
- `_dominance_score`
- `_axis_weight`
- `_house_weight`
- `_pattern_bonus`
- `_domain_priority`
- `_resolve_house`
- `_axis_for_house`
- `_normalize_planet`
- `_slot_ratios`
- `_clean_text`
- `_safe_float`
- `_clamp`
- `_apply_meta_tone`
- `_limit_paragraph_sentences`
- `_rewrite_repeated_verbs`
- `_normalize_paragraphs`
- `_normalize_paragraph`
- `_limit_word_count`
- `_micro_insight_text`
- `_mechanism_to_lived`
- `_mechanism_phrase`
- `_contains_any`
- `_top_intent_pairs`
- `_intent_phrase`
- `_inner_question`
- `_potential_growth_sentence`
- `_shadow_risk_sentence`
- `_mechanism_inner_voice`
- `_mechanism_conflict_line`
- `_dedupe_lines`
- `_collect_slot_texts`
- `_core_style_from_text`
- `_outer_perception`
- `_inner_counterforce`
- `_apply_genelde_rule`
- `_apply_softener_rule`
- `_normalize_sections`
- `_drop_forbidden_sections`
- `_drop_forbidden_sentences`
- `_contains_forbidden`
- `_tokenize_words`
- `_top_intents`
- `_identity_sections_from_payload`
- `_build_style_context`
- `_select_focus_claims`
- `_section_from_paragraphs`
- `_apply_section_tone`
- `_norm_space`
- `_cap_sentences`
- `_join_sentences`
- `_pick_top_intents`

### 4.3 Imports still locally used

Imports still used by residue:

- `hashlib`
- `json`
- `re`
- `string`
- `apply_tone`
- `ToneProfile`
- `canon_domain`
- `normalize_node_alias`
- `normalize_planet_key`
- `Claim`
- `STYLE_PACK_TR_V26`
- `pick_identity_plan_tokens`

## 5. `narrative_renderer_v26.py` residue

### 5.1 Dead-truly

No top-level dead-truly function cluster was found beyond the already
known shadowed duplicate and dead-import candidates.

Shadowed duplicate:

- earlier [_build_fragment_index](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:68)

The later runtime-effective version had already been moved to the new
package during S2.1.3. The earlier version is now pure residue.

Dead-import candidates:

- `dataclass`
- `Iterable`

### 5.2 Locally-residue-only

Still internally referenced by same-file residue, but not reachable from
canonical runtime:

- `CORE_STORY_SLOT_ORDER`
- `_select_focus_claims`
- `_section`
- `_join_sections`
- `_resolve_tone_profile`
- `_apply_tone_safe`
- `_build_fragment_id_map`
- `_build_fragment_id_text_map`
- `_build_id_to_text`
- `_plan_section_map`
- `_pick_sentences`
- `_resolve_slot_text`
- `_extend_from_section`
- `_ensure_min_sentences`
- `_join_sentences`
- `_fingerprint_text`
- `_insert_micro_transition`
- `_build_spine_index`
- `_build_insight_index`
- `_build_meaning_index`
- `_headline_ref`
- `_find_composite_ref`
- `_pick_spine_ref`
- later `_build_fragment_index`
- `_resolve_fragment_text`
- `_split_sentences`
- `_capitalize_turkish_initial`
- `_normalize_sentence`
- `_sentence_key`
- `_dedupe_sentences`
- `_cap_connector_usage`
- `_soften_shadow`
- `_is_enum_like`
- `_wrap_shadow`
- `_fix_duplicate_tokens`
- `_clean_sentence`
- `_CORE_STORY_STOPWORDS`
- `_core_story_tokens`
- `_core_story_overlap`
- `_polish_core_story_sentence`
- `_polish_core_story_paragraph`
- `_bridge_inner_outer`
- `_collapse_repeated_leads`
- `_resolve_sentence_role`
- `_needs_connector`
- `_pick_connector`
- `_join_with_connector`
- `_has_leading_connector`
- `_dedupe_within_paragraph`
- `_add_connectors_with_cap`
- `_merge_sentence`
- `_merge_adjacent_sentences`
- `_normalize_clause`
- `_ensure_terminal_punctuation`
- `_section_entries`
- `_slot_texts`
- `_first_text`
- `_synthesize_paragraph`
- `_ensure_min_sentences_payload`
- `_extract_need`
- `_link_shadow`
- `_render_upper_meaning`
- `_render_section_sentences`
- `_append_unique_sentence`
- `_render_role_sentence`
- `SLOT_CONNECTORS`
- `CONNECTOR_TOKENS`
- `_apply_connector`
- `_limit_sentences`
- `_ensure_spine_fallback`
- `_ensure_min_sentences_count`
- `_build_composite_lookup`
- `_plan_composite_selected`
- `_insert_composite_headline`
- `_insert_composite_explain`
- `_insert_spines`
- `_select_spine_links`
- `_insert_link_connector`
- `_insert_shadow_from_spines`
- `_build_fallback_pool`
- `_normalize_sentence_start`
- `_select_paragraph_fragments_from_plan`
- `_select_from_plan`
- `_pad_with_fragment_map`
- `_select_supporting_fact`
- `_compose_paragraph`
- `_clean_fragment_text`
- `_stable_pick`

### 5.3 Imports still locally used

Imports still used by residue:

- `re`
- `Claim`
- `apply_tone`
- `ToneProfile`

## 6. Public endpoint reachability

### Natal

Canonical natal route uses only:

- `backend/app/natal/narrative/core_story/`

No residual dependency on the old V26 live files was found.

### Synastry

No current synastry public builder or route reaches the former V26 live
files.

### Transit

No current transit public builder or route reaches the former V26 live
files.

### Public payload consequence

The following invariants are therefore unaffected by residue presence:

- `response["core_story"]`
- `response["core_story_plan"]`
- `PublicNatalView.core_story`
- `profile_v8.identity_axis_body` fallback
- `core_story_ui`

## 7. Risk notes

### Risk 1 — file-level delete is broader than residue delete

Even though canonical runtime is clean, deleting the whole old files now
would mix:

- dead-truly residue
- locally-residue-only clusters
- stale legacy test fallout

That is a different risk class from symbol-level cleanup.

### Risk 2 — same-name false positives

Several helper names exist elsewhere in the repo. Grep alone can make
them look externally referenced. This audit treats only **real imports /
module-path callers** as callers.

### Risk 3 — shadowed duplicate trap remains in residue

`narrative_renderer_v26.py` still contains the earlier shadowed
`_build_fragment_index(...)`. Any future cleanup PR must delete the dead
earlier definition consciously, not mistake it for the moved live helper.

### Risk 4 — dead-import cleanup should not widen into refactor

Dead imports are now visible, but removing them should happen together
with residue cleanup only, not as an opportunistic style pass.

## 8. Recommendation

### Recommendation

**FREEZE-only**

### Why

- canonical runtime is already off the old files
- no live caller remains to migrate
- residue cleanup is now mostly mechanical but still deserves its own
  bounded PR
- stale legacy test imports mean file-level deletion is not the right next
  step yet

### Next action

Prepare a separate, narrow implementation request that:

1. deletes only `dead-truly` residue first, or
2. deletes `dead-truly + locally-residue-only` clusters from one file at a
   time, with compile + regression gates

Required regression set for that later PR:

- `backend/tests/test_natal_public_builder.py`
- `backend/tests/test_composed_detail_renderer.py`

## Final verdict

S2.1.5 confirms that the former V26 live files are no longer part of any
canonical runtime path.

The correct next step is **bounded residue cleanup**, not more migration.

The recommendation is **FREEZE-only now, cleanup in a separate PR**.
