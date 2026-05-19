# SHOU Voice Reconciliation Spec (v0.1)

> Planning artifact. No code, runtime, renderer, scoring, gold, or
> public-output changes. Purpose: stop the voice layer from forking
> into a third taxonomy. Binds the THREE existing committed assets into
> ONE chain, folds the two genuinely-new chat contributions as explicit
> contract fields, and re-renders 1985 in TR using the **committed**
> tone-aware machinery (not a new system). Bounded exactly like §10.3:
> validate blind on one chart, then 2–3, before any code.

## 0. The three assets being reconciled (do not duplicate)

1. `config/ontology/themes.yaml` — 13 orthogonal **tension themes**
   (psychological territory + question + share_weight + caps).
2. `docs/system/shou_tone_aware_composition_plan.md` — `valence_frame`,
   §6 strategy matrix, §7 eight sentence strategies, §9 adaptive slide
   profiles, §4.2 length budgets, §8 editorial constraint library.
3. `docs/system/shou_semantic_role_and_voice_mode_map.md` — semantic
   role → voice_mode map + `missing_needed` contract gaps.

The chat-proposed "12 theme families + 12 voice_modes" is **not
adopted**. It is a re-spec of assets 1–2 and would create the drift
asset 3 §4 explicitly warns about.

## 1. The single canonical chain

```
themes.yaml.theme            (WHICH psychological territory)
  → valence_frame            (HOW it is energetically shaped; tone_aware §6.1)
  → slide_profile            (adaptive slide arc;            tone_aware §9.1)
  → sentence_strategy        (per-slide line construction;   tone_aware §7)
  → voice_mode / role        (semantic_role_voice_mode_map)
  → map_trace + deselected_trace   (NEW — §3 of this spec)
  → UI surface + length budget     (tone_aware §4.2)
```

Rule: `theme` answers *what*; `valence_frame` answers *how*. They are
orthogonal axes (this is why "gift" / "friction" are NOT themes — they
are valence; tone_aware §6.1 already separates them). A single theme
(e.g. `intimacy_trust`) renders completely differently under
`valence_frame=gift` vs `=friction`. Voice is a function of
`(theme × valence_frame × dignity-strength × domain)`, deterministic,
config-owned, never an LLM choice (tone_aware §11).

## 2. Mapping table (binding, not new vocabulary)

| Layer | Source of truth | Owner | Determinism |
|---|---|---|---|
| theme | `themes.yaml` | ontology | deterministic |
| valence_frame | tone_aware §6.1 set | ontology/config | deterministic from aspect-valence + dignity |
| slide_profile | tone_aware §9.1 | config | deterministic from valence_frame + domain |
| sentence_strategy | tone_aware §7 (8) | composition | matrix-derived (§6.2) |
| voice_mode | semantic_role_map | composition | from role |
| map_trace / deselected_trace | **NEW (§3)** | semantic source | deterministic from ARC anchors |

## 3. Two NEW contract fields (the real chat contribution)

These do not exist in any of the three assets and are the only genuine
additions. They are added the same way semantic_role_map already lists
`pattern_name` / `share_line` / `proof_line` as `missing_needed`.

### 3.1 `map_trace`

Light, human-facing anchor list shown as a separate layer (NOT in the
main narrative; main narrative stays jargon-free per tone_aware §8).
Names the placements the card was built from, one short line each.

### 3.2 `deselected_trace`  *(brand-defining)*

Human-language statement of **what was deliberately NOT led with, and
why** — sourced directly from ARC's `must_not` (salience-kind) +
residual `false_emphasis`. Converts the §10.3 residual-FE finding
(scorer flags Neptune–Pluto via member-max attribution) into a user
trust signal. Co-Star/Pattern hide reasoning; SHOU showing "what we
chose not to make your headline" is a differentiator.

Proposed for `semantic_role_voice_mode_map.md` → `missing_needed`:
`deselected_trace` (status: missing_needed, voice mode:
`honesty_trace_mode`, surface: profile deep + explainability).

## 4. Recorded gaps — PROPOSED, pending tone_aware §13.2 review

Surfaced by reconciling 1985; **not silently added** (no fork):

1. **themes.yaml has no clean "emotional-base / inner anchor" tension.**
   1985 rank-1 (Moon Cancer 9 domicile, final dispositor) maps only
   approximately to `security` + `meaning_belief`. Proposed review
   item: evaluate an `emotional_base` theme OR confirm it is a domain,
   not a tension. Requires §13.2 authoring packet before any add.
2. **tone_aware §9.1 has no identity/first-impression slide_profile.**
   1985 is persona-vs-core, not gift/friction/hidden/etc. Proposed
   profile `identity_polarity`:
   `surface_persona → drive_nuance → emotional_core → relational_asset
   → integrated_shape`. Flagged proposed-not-committed; the 1985 render
   below uses it explicitly labelled as such.

## 5. 1985 re-render — TR, committed machinery

Chart `1985-06-20_15-50_istanbul`. Profile: **proposed**
`identity_polarity` (§4.2). Strategies per slide from tone_aware §7.
Length budgets enforced (tone_aware §4.2: parent ≤140c/1–2s, slide body
≤260c/2–3s, share ≤110c/1s). Main text: zero astro jargon (§8). Anchor
names live ONLY in `map_trace`; mechanism ONLY in click `deep_evidence`.

**Parent card** — strategy `paradox_holder`, compressed
> İlk anda yoğun ve kapalı görünürsün. Ama seni asıl taşıyan o sertlik
> değil; içeride daha sessiz, daha dayanıklı bir yer var.

**Slide 1 · "Kolay okunmuyorsun"** — voice_mode `effect_voice`,
strategy `structural_recognition`
> İnsanlar seni hemen çözemez. Yanında bir yoğunluk, bir dikkat hissi
> var; içeri girmek zaman ve güven ister. Bu soğukluk değil — yüzeyde
> kalmayan bir varlık.

**Slide 2 · "Göründüğün kadar sert değilsin"** — strategy
`paradox_holder`
> Dışarıdan kolay etkilenmeyen, hemen savaşan biri gibi durabilirsin.
> Ama içindeki itki daha ölçülü çalışır: ne zaman duracağını, ne zaman
> yaklaşacağını bilirsin. Güç sende saldırı değil, seçim.

**Slide 3 · "Seni taşıyan yer daha yumuşak"** — strategy `inside_lens`
+ `grounded_assertion`
> Asıl dayanıklılığın sertlikten gelmiyor. İçeride koruyan,
> bağlandığını kolay bırakmayan bir merkez var; sevdiğini içten içe
> sahiplenirsin. Sağlamlığın oradan besleniyor.

**Slide 4 · "Yakınlık sende hafif değil"** — strategy
`grounded_assertion` + `paradox_holder` (honors must_not: asset, not
whole)
> Bir bağ ancak güven verince, zamanla oturunca anlam kazanır sende.
> Açıldığında sadakat ve süreklilik ararsın. Ama bu güçlü kapı, evin
> tamamı değil.

**Slide 5 · "Tek bir şey değilsin"** — strategy `evidence_summary` +
`threshold_statement`
> Güçlü bir ilk etki, içeride sessiz ama dayanıklı bir merkez, ve
> derinleşen ama seni tüketmeyen bir yakınlık aynı anda çalışıyor.
> Asıl şekil: görünen güç, içerideki sessiz bağlılıkla taşınıyor.

**Share line** — `share_line_mode`
> Seni sadece yoğun sanan, içindeki sadakati kaçırır.

**map_trace** (separate layer, light)
- İlk etki: Akrep yükselen · Plüton 1. ev
- Görünen güç farkı: Mars (yönetici) hassas
- Duygusal merkez: Ay Yengeç (kendi evinde)
- Yakınlık: Venüs Boğa · 7. ev (kendi evinde)

**deselected_trace** (NEW field, public, honesty)
> Haritandaki en sıkı açı bir Neptün–Plüton (0.27°). Güçlü ama
> nesil-geneli bir iz; seni kişisel olarak anlatan ana hat değil. O
> yüzden bu kartın merkezine koymadık — seni asıl anlatan Ay, Plüton
> ve Venüs hatları.

**deep_evidence** (click-only; technical allowed here ONLY): Moon
Cancer 9 domicile, rank-1, final dispositor, Moon–Saturn trine 0.68 ·
Scorpio Asc + Pluto Scorpio 1 domicile angular, rank-2 · chart ruler
Mars Cancer 9 fall = supporting route (persona > drive) · Venus Taurus
7 domicile, rank-3 + Mercury–Venus sextile 0.30 · core tension central
· deselected: Neptune–Pluto 0.27 sextile (A2 residual FE, demoted).

## 6. What changed vs prior drafts (doc-grounded, not opinion)

- Parent card now obeys tone_aware §4.2 (≤140c/1–2s). Prior version-B
  parent (~5 paragraphs) failed it.
- Main text carries zero mechanism naming (§8 forbidden). Version-B
  ("Mars'ın hassas çalışması … gösteriyor") failed §8 + the user's own
  blind verdict.
- Thesis stated once (slide 5 + share), not 3× (§15 "no restate parent
  on every slide").
- Anchor names isolated to `map_trace`; mechanism to `deep_evidence` —
  matches tone_aware §2 ("technical astrology light, selective").

## 7. Blind verdict (preserve §10.3 discipline)

Builder = this doc (scorer-aware, legitimate). Felt-experience verdict
= a scorer-blind reader, from output only. See blind sheet:
`shou_voice_reconciliation_1985_BLIND.md`. The §6 note here is
explicitly NON-BLIND and is not the verdict.

## 8. Next steps (bounded; == tone_aware §16 Phase 1/2 == §10)

1. Blind verdict on the §5 render (separate sheet).
2. If PASS / minor-REVISE: repeat the *committed-machinery* render +
   blind read on 2007 (12H-heavy) and one no-dominant chart. Same
   profiles/strategies — tests generalization, not per-chart tuning.
3. Only after 2–3 charts hold: §13.2 authoring packets for the two §4
   gap proposals, then the `slides[]` / contract code work
   (tone_aware §16 Phase 3+). No code before that.
4. No new taxonomy. No merge. No production change. Pass-1/§10
   discipline unchanged.

## 9. Surface model: `deep_read` (NEW — added per product UX)

§5 rendered a *scannable* card under tone_aware §4.2 parent budget.
Product clarification: in the app the **glanceable surface is a TITLE
only**; tapping opens a **right-swipe slide flow**. So the long
immersive body is NOT the parent-card surface — it is the tapped,
reflective, high-attention band (tone_aware §4.1). This is a legitimate
distinct surface (`deep_read`), on-benchmark with Chani/Sanctuary-style
immersive reads. It does not replace the scannable model; both exist
for different user states.

### 9.1 `deep_read` contract

| Element | Rule |
|---|---|
| glanceable title | governed by tone_aware §4.2 title budget (≤52–56c); the ONLY thing shown before tap |
| body | swipe slide flow, N slides (not fixed 5); §4.2 *parent/body char budget does NOT apply here* — own budget below |
| slide budget | depth allowed; **one spine per swipe** is the hard rule, not char count |
| thesis | stated **exactly once** (final synthesis slide + share line); intermediate slides must each open a *new face*, never restate the thesis |
| astro terms | permitted in body, but **every term cashed to lived experience in the same breath**; a bare mechanism clause (term + "devreye giriyor/güçlü çalışıyor") is forbidden (tone_aware §8) |
| lived-scene (Rule 3) | every slide carries ≥1 concrete behavioral **scene** (a recognizable moment the person *does/experiences*), not only abstract category nouns; the recurrence carrier must be scenes, not an abstract word-family ("görünmeyen / iç dünya / anlam / güç"); multi-centre charts render centres as a **sequence of entering characters with contrasting tempo**, never a catalogue list |
| rhythm-modulation (Rule 4, CORRECTED) | explanatory **depth is preserved** — long, immersive, explaining slides are good and are NOT the defect. The single variable is **rhythm**, and rhythm is set by the *emotional nature of that slide's content*, varying slide-to-slide and even within a paragraph: inward→calm/unhurried; depth→slow/weighty; discipline→firm/grounded/short clauses; rupture→a sharp short pivot; gift→warm/expansive; shadow→quiet/honest/no drama; synthesis→settling. This is the committed tone_aware §6/§7 strategy matrix + the user's theme-family voice-mode design applied **per slide**. NOT compression, NOT uniform punchline, NOT staccato-everywhere. (v3 over-corrected into compression; rescinded.) |
| map_trace / deselected_trace | unchanged; still separate layers |

### 9.2 Why these two rules survive the length concession

The §4.2 char budget objection is **withdrawn** (surface clarified).
Two rules are length-independent and still binding:
- **one spine per swipe** — this is the real intent of §4.2 "one
  semantic move per slide": a physical swipe must map to one
  retainable idea, regardless of length.
- **thesis once** — in a swipe UX, restating the thesis across slides
  is *worse* (user physically re-encounters the same idea); §15
  "no restate parent on every slide" applies harder here.

### 9.3 Quality reference

The cleaned 2007 deep_read render (A+B applied, Jupiter correctly
8th-house, thesis-once, terms cashed) is the `deep_read` quality
reference, analogous to tone_aware §2's Venus-12H reference — it sets
the depth ceiling. See `shou_voice_deep_read_reference_2007.md`.

### 9.4 Convergence note (why this is NOT a treadmill)

Three independent blind reads (1985 scannable, then 2007 + 1975
deep_read) returned the **same split**: semantic/structure PASS, voice
REVISE, **same reason** ("correct summary, not lived scene"). This
convergence is the opposite of an open loop: the ARC selection +
structure is repeatedly validated, and the failure variable is now
isolated to a single, well-characterised craft axis (abstract-summary
vs lived-scene). Rule 3 is the extraction of that axis. Bounded
expectation: one–two more REVISE→blind cycles close it; this is
zeroing-in, not goalpost drift (§10 / tone_aware §16 discipline
intact).

### 9.5 Stopping condition (anti-treadmill, binding)

Iteration count on the 2 reference cards: v1→v2→v3. Residual is
shrinking and more precisely named each cycle (structure → lived-scene
→ rhythm/shape). This is convergence, but it must not become infinite
hand-polish on 2 charts.

v3 over-corrected (compression/punchline) — builder error: the
diagnosis ("uniform rhythm") was right but the prescription wrongly
discarded the explanatory depth, which was never the defect. Rule 4 is
corrected to **rhythm-modulation, not compression**. v3 is consumed as
the "one more hand cycle maximum".

**v4 is the FINAL hand cycle and the rule-lock. Binding:**
- v4 = the user's preferred long explanatory structure WITH per-slide
  rhythm modulation (corrected Rule 4). Rules 1–4 are now **frozen** as
  the `deep_read` contract regardless of v4's verdict.
- v4 PASS (both) → proceed to §13.2 authoring packets + code
  (tone_aware §16 Phase 3+).
- v4 REVISE → do NOT hand-write v5. The frozen Rules 1–4 are encoded
  as testable automated checks; validation moves to that encoded mode.
  No further hand-polish of these 2 reference cards.

This binds the voice loop the same way §10 / Pass-1 bound the salience
loop.

### 9.6 `origin_hint` — bound to committed `cause_voice` (NEW role, reconciled)

Not a new role: `shou_semantic_role_and_voice_mode_map.md` §2 already
lists `emerging_existing | Cause / Past Layer | cause_voice` (sparse,
not yet a formal contract field). `origin_hint` is its `deep_read`
realization. Promote to `missing_needed` like `deselected_trace`.

Purpose: add the "bu sende neden böyle kurulmuş olabilir" layer — the
learned-reflex / inner-history dimension — *without* deterministic past
claims.

Contract:

```json
{
  "slide_role": "origin_hint",
  "binds_to": "cause_voice / Cause-Past-Layer (semantic_role_map §2)",
  "voice_mode": "softened_interpretive",
  "certainty": "low_to_medium",
  "default_surface": "expandable sub-layer titled \"Nereden geliyor olabilir?\" (opt-in by tap; NOT inline by default)",
  "eligibility": "only on defended / compensatory / withheld signatures (e.g. Saturn 1, 12H carrying, guarded warmth). NOT on neutral or purely-gift signatures. Sparse by design (matches cause_voice = emerging/sparse).",
  "anchor_rule": "MUST attach to the SAME astro signal already anchored in the main reading. It is a register on an existing anchor, never a free-floating psychological story or a new claim.",
  "allowed_language": [
    "öğrenmiş olabilirsin",
    "zamanla böyle kurmuş olabilirsin",
    "erken dönemde ... hissetmiş olabilirsin",
    "bu yüzden bugün ...",
    "herkes için böyle olmak zorunda değil"
  ],
  "forbidden_language": [
    "çocukluğunda kesin ... oldu",
    "ailen / annen / baban sana ... yaptı",
    "travman şudur",
    "bu yüzden böylesin",
    "klinik / tanı sözlüğü"
  ],
  "reversibility_rule": "every origin_hint passage must contain at least one opt-out clause (it MAY be so, not it IS so)."
}
```

This is genuinely on-brand: the user gets "aa ben bunu neden böyle
yapıyorum" — but the consent-by-expansion + probabilistic + anchored
guardrails prevent the single biggest risk (an invasive or fabricated
past-story). It enters the SAME bounded blind discipline; the critical
blind question is *feels-seen vs feels-presumed*.

### 9.7 v4 lexical fix + §9.5 classification

- "silik" (parent) replaced — see v4.1 reference (it carried a
  faded/lesser connotation the user rejected).
- Per §9.5: §9.6 + the lexical fix are **not** a treadmill v5 (not
  re-polishing the locked rhythm axis). Rules 1–4 stay frozen.
  `origin_hint` is additive reconciled scope under its own blind check.

## 10. Blind re-anchor (methodology integrity)

The pending 5-slide Card A/B blind verdicts
(`shou_voice_reconciliation_gen_BLIND.md`) targeted the *scannable*
surface. The design has evolved to `deep_read`. Those 5-slide verdicts
are therefore **superseded by surface change**, not failed. The blind
gate now re-anchors to the `deep_read` surface:

1. Blind verdict on the cleaned 2007 deep_read reference
   (`shou_voice_deep_read_2007_BLIND.md`).
2. Next bounded step: re-render 1975 (no-dominant) on the **same**
   `deep_read` contract + committed §7 strategies (generalization of
   the deep_read profile, not per-chart tuning), blind-verify.
3. Then §13.2 packets + code (tone_aware §16 Phase 3+). No code first.
4. No new taxonomy. No merge. No production change.
