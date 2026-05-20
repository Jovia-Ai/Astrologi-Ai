# S2.1.3 Step 0.5 — V26 LIVE Core Story Helper Dependency Audit

## Scope

This is a trace-only audit artifact.

No code.
No runtime change.
No deletion.
No refactor.

Goal:

- identify which helpers in the live V26 files must move with the live
  symbols
- identify which helpers must stay because they are shared with some
  other live symbol
- identify which helpers are orphaned or belong to dead/non-live paths
  and therefore must **not** be moved during S2.1.3

Target files:

- [backend/app/builders/narrative_binding.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_binding.py:36)
- [backend/app/builders/narrative_renderer_v26.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:22)

Live roots under review:

- `build_core_story_plan(...)`
- `render_core_story(...)`

## Executive verdict

The helper picture is cleaner than it first looks.

### Main result

For the two live roots:

- a clear **move-with** helper set exists in both files
- **no shared-live-stay helper set was found**
- there is a substantial **orphan-later** set in both files that should
  not be moved as part of S2.1.3

### Important implication

The S2.1.3 migration can proceed as:

- move the live roots
- move only the helpers reachable from those roots
- leave the remaining helper residue in place for a later orphan-cleanup
  pass

### Important special case

`narrative_renderer_v26.py` contains **two definitions** of
`_build_fragment_index(...)`:

- earlier definition at
  [narrative_renderer_v26.py:239](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:239)
- later definition at
  [narrative_renderer_v26.py:617](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:617)

The later one shadows the earlier one at runtime. For migration purposes:

- the later definition is the **effective move-with** helper
- the earlier definition is **orphan-later / shadowed residue**

This is exactly the kind of hidden extraction risk Step 0.5 was meant to
catch.

## Method

For each target file:

1. enumerate all top-level function definitions
2. build an internal call graph
3. compute the transitive helper set reachable from the live root
4. search repo-wide callers for top-level exported/live symbols
5. partition helpers into:
   - `move-with`
   - `shared-live-stay`
   - `orphan-later`

Repo-wide caller check result:

- external runtime callers found only for:
  - `build_core_story_plan(...)`
  - `render_core_story(...)`
- no repo callers found for:
  - `render_identity_v26(...)`
  - `normalize_text(...)`
- no external imports of private `_helper(...)` symbols found

## 1. `narrative_binding.py` partition

### 1.1 Live root

- [build_core_story_plan(...)](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_binding.py:36)

### 1.2 Move-with set

These helpers are in the transitive call graph of `build_core_story_plan`
and should move with it:

- [build_core_story_plan](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_binding.py:36)
- [_build_core_story_spines](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_binding.py:143)
- [_map_spine_paragraph](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_binding.py:225)
- [_spines_by_section](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_binding.py:234)
- [_select_composite_meanings](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_binding.py:246)
- [_collect_used_fragments](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_binding.py:265)
- [_headline_ref](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_binding.py:290)
- [_paragraph_spine_refs](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_binding.py:306)
- [_sentence_target](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_binding.py:338)
- [_role_for_slot](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_binding.py:346)
- [_build_section_sentences](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_binding.py:357)
- [_spine_debug](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_binding.py:425)
- [_index_phase2_accepted](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_binding.py:458)
- [_is_better_fragment](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_binding.py:486)
- [_fragment_sort_key](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_binding.py:490)
- [_fill_section_slots](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_binding.py:497)
- [_fallback_from_supporting](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_binding.py:531)
- [_fragment_id_from_fragment](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_binding.py:580)
- [_fallback_fragment_key](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_binding.py:590)
- [_core_story_plan_id](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_binding.py:609)
- [_safe_float](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_binding.py:1144)

### 1.3 Shared-live-stay set

**None found.**

Reason:

- repo-wide external runtime caller exists only for
  `build_core_story_plan(...)`
- no second live symbol in this file currently shares its helper graph in
  a way that would force helper retention outside the move set

### 1.4 Orphan-later set

These symbols should **not** be moved in S2.1.3. They belong to
non-live residue and can be handled in a later cleanup audit/pass.

#### A. Small dead top-level cluster

- [render_identity_v26](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_binding.py:1717)
- its reachable helpers:
  - [_cap_sentences](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_binding.py:1665)
  - [_join_sentences](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_binding.py:1676)
  - [_norm_space](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_binding.py:1659)
  - [_pick_top_intents](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_binding.py:1687)

Repo-wide callers found:

- none

#### B. Self-contained normalizer root

- [normalize_text](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_binding.py:802)

Repo-wide callers found:

- none beyond internal use in dead residue helpers

#### C. Larger legacy residue cluster

Representative orphan-later helpers include:

- [_domain_order](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_binding.py:626)
- [_build_recognition](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_binding.py:646)
- [_build_experienced](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_binding.py:652)
- [_build_potential](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_binding.py:658)
- [_build_shadow](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_binding.py:664)
- [_build_upper](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_binding.py:670)
- [_dedup_slots](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_binding.py:808)
- [_cast_fragment](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_binding.py:913)
- [_compute_salience](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_binding.py:962)
- [_orb_strength](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_binding.py:985)
- [_dominance_score](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_binding.py:1021)
- [_axis_weight](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_binding.py:1047)
- [_house_weight](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_binding.py:1067)
- [_pattern_bonus](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_binding.py:1078)
- [_resolve_house](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_binding.py:1102)
- [_normalize_planet](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_binding.py:1126)

These are not in the live `build_core_story_plan(...)` transitive graph and
should stay put for now.

## 2. `narrative_renderer_v26.py` partition

### 2.1 Live root

- [render_core_story(...)](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:22)

### 2.2 Move-with set

These helpers are in the transitive call graph of `render_core_story(...)`
and should move with it:

- [render_core_story](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:22)
- [_resolve_tone_profile](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:216)
- [_apply_tone_safe](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:233)
- effective [_build_fragment_index](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:617)
- [_build_meaning_index](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:508)
- [_headline_ref](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:527)
- [_resolve_fragment_text](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:632)
- [_split_sentences](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:638)
- [_capitalize_turkish_initial](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:646)
- [_normalize_sentence](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:655)
- [_sentence_key](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:666)
- [_dedupe_sentences](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:672)
- [_cap_connector_usage](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:684)
- [_is_enum_like](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:726)
- [_wrap_shadow](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:734)
- [_fix_duplicate_tokens](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:750)
- [_clean_sentence](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:754)
- [_core_story_tokens](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:781)
- [_core_story_overlap](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:790)
- [_polish_core_story_sentence](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:799)
- [_polish_core_story_paragraph](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:820)
- [_bridge_inner_outer](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:833)
- [_collapse_repeated_leads](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:849)
- [_resolve_sentence_role](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:853)
- [_needs_connector](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:866)
- [_pick_connector](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:877)
- [_join_with_connector](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:892)
- [_has_leading_connector](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:899)
- [_dedupe_within_paragraph](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:910)
- [_add_connectors_with_cap](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:926)
- [_merge_adjacent_sentences](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:965)
- [_normalize_clause](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:979)
- [_ensure_terminal_punctuation](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:983)
- [_section_entries](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:992)
- [_slot_texts](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:1006)
- [_first_text](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:1025)
- [_synthesize_paragraph](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:1035)
- [_ensure_min_sentences_payload](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:1190)
- [_extract_need](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:1235)
- [_render_upper_meaning](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:1258)

### 2.3 Shared-live-stay set

**None found.**

Reason:

- the only external runtime caller in this file is `render_core_story(...)`
- no second live exported symbol currently shares this helper graph

### 2.4 Orphan-later set

These symbols should not move during S2.1.3.

#### A. Shadowed duplicate helper

- earlier shadowed [_build_fragment_index](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:239)

This definition is overwritten by the later runtime-effective definition at
line 617.

#### B. Dead alternate composition cluster

Representative orphan-later helpers:

- [_build_fragment_id_map](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:251)
- [_build_fragment_id_text_map](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:275)
- [_build_id_to_text](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:297)
- [_plan_section_map](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:315)
- [_pick_sentences](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:322)
- [_resolve_slot_text](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:362)
- [_extend_from_section](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:381)
- [_ensure_min_sentences](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:422)
- [_fingerprint_text](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:453)
- [_build_spine_index](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:473)
- [_build_insight_index](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:489)
- [_find_composite_ref](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:558)
- [_pick_spine_ref](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:584)
- [_render_section_sentences](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:1280)
- [_append_unique_sentence](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:1326)
- [_render_role_sentence](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:1348)
- [_apply_connector](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:1387)
- [_ensure_spine_fallback](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:1411)
- [_ensure_min_sentences_count](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:1439)
- [_build_composite_lookup](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:1473)
- [_insert_composite_headline](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:1502)
- [_insert_composite_explain](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:1529)
- [_insert_spines](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:1563)
- [_select_spine_links](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:1616)
- [_insert_link_connector](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:1625)
- [_insert_shadow_from_spines](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:1645)
- [_build_fallback_pool](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:1679)
- [_select_paragraph_fragments_from_plan](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:1713)
- [_select_from_plan](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:1749)
- [_pad_with_fragment_map](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:1773)
- [_select_supporting_fact](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:1790)
- [_compose_paragraph](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:1805)
- [_clean_fragment_text](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:1836)
- [_stable_pick](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:1843)

These belong to a dead alternate composition route, not the live
`render_core_story(...)` execution graph.

## 3. Implementation consequence for S2.1.3

The migration plan can now be tightened:

### Move to `core_story_module.py`

- `build_core_story_plan(...)`
- `render_core_story(...)`
- only the move-with helper sets listed above

### Leave in legacy files for now

- all orphan-later helpers
- all dead clusters
- the shadowed duplicate helper definition

### Shared-live-stay action

- none needed at this stage

## 4. Risk notes

### Risk 1 — accidental over-migration

If S2.1.3 moves more than the move-with set, it widens scope and may drag
dead alternate logic into the new module.

### Risk 2 — accidental under-migration

If S2.1.3 forgets one helper from the move-with set, extraction may still
import legacy files indirectly and hide coupling.

### Risk 3 — shadowed helper confusion

The duplicate `_build_fragment_index(...)` in
`narrative_renderer_v26.py` is the sharpest trap.

Migration must move:

- the **effective** line-617 definition

and leave:

- the shadowed line-239 definition

for later cleanup.

## 5. Recommendation

Step 0.5 is now satisfied.

Recommended next action:

- proceed to S2.1.3 using the wrapper-first migration plan
- treat this audit as the authoritative move-with list
- defer orphan cleanup to a separate later pass

## Final verdict

**S2.1.3 can proceed, but only with a helper move set bounded to the
reachable live-root graph documented here.**
