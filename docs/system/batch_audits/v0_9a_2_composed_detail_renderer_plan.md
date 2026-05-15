# v0.9a.2 Composed Detail Renderer Plan

## Scope

This document plans the next safe step after the `v0.9a.1` visibility guard:

- `career_route` only
- subtype `public_voice` only
- `detail cards` only

Still out of scope:

- `public_support`
- `public_main`
- `creative_visibility`
- `authority_responsibility`
- `action_initiative`
- `invisible_preparation_before_visibility`
- `identity_route`
- `relationship_route`
- `moon_signature`
- registry additions
- selection changes

This is a planning document only.

## Current State

After `v0.9a.1`, composed `public_voice` candidates are in the correct holding state:

- semantically available
- `detail_eligible=true`
- `keep_for=["detail", "debug"]`
- not user-visible by default because `ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL=false`

This is the correct pause point.

The next job is not more scoring. The next job is controlled rendering:

- a dedicated composed detail renderer
- or an explicit detail-card route

The renderer must turn composed semantic ingredients into SHOU-quality lived recognition, not leak debug/spec prose.

---

## 1. Where should composed detail rendering happen?

### Option A: `projection_shadow_v1_builder.py`

Pros:

- already owns `profile_narrative_projection_v1`
- already owns `profile_v8_projection_v1`
- already converts packet/cluster payloads into user-facing projection nodes
- already has the right insertion point for a render guard

Cons:

- it is currently doing both selection-side shaping and surface rendering
- mixing composed semantic copy-building directly into the same generic packet-node path risks reintroducing debug/spec leakage
- if composed detail rendering is embedded too loosely here, it becomes hard to keep SHOU-quality constraints separate from legacy packet rendering

Verdict:

- good integration point
- not ideal as the only place where composed detail copy logic lives

### Option B: `natal_promise_cluster_plan.py`

Pros:

- owns suppression and surface-role routing
- already knows `detail_eligible`, `keep_for`, and `source_type`

Cons:

- this is the wrong layer for public prose
- ClusterPlan should decide *whether* something is detail-eligible, not *how* it should sound
- putting public card rendering here would blur semantic selection and copy rendering

Verdict:

- not recommended for copy generation
- keep it as routing/eligibility only

### Option C: new `composed_detail_renderer` module

Pros:

- clean separation of concerns
- can accept composed candidates as semantic ingredients and output a controlled public detail-card contract
- can enforce SHOU-only rendering rules for composed semantics
- can stay very narrow at first:
  - `career_route`
  - `public_voice`
  - `detail-only`

Cons:

- one more module to maintain
- requires explicit handoff wiring from projection builder

Verdict:

- recommended

### Option D: `public_builder.py`

Pros:

- top-level public payload owner
- could theoretically compose final cards centrally

Cons:

- too high-level
- would make `public_builder.py` absorb route-specific narrative logic that belongs lower
- weak fit for chart-family-specific detail copy shaping

Verdict:

- not recommended for the rendering logic itself
- only appropriate as orchestration/wiring

### Recommended architecture

Best split:

1. `natal_promise_cluster_plan.py`
- continues to own eligibility and suppression

2. new composed detail renderer module
- owns composed detail-card transformation
- example future location:
  - `backend/app/meaning/composed_detail_renderer.py`

3. `projection_shadow_v1_builder.py`
- calls the composed detail renderer when:
  - `source_type == composed_semantic`
  - subtype is supported
  - `detail_eligible == true`
  - `ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL=true`
- inserts returned cards only into detail surfaces

4. `public_builder.py`
- unchanged except for existing orchestration

Short answer:

- rendering should happen in a new composed-detail renderer module
- projection builder should only decide when to call it and where to place its result

---

## 2. Composed detail card contract

Recommended contract for a public-facing composed detail card:

### Required public fields

- `headline`
- `teaser`
- `body`
- `chips`

### Required traceability fields

- `evidence_summary`
- `source_type`
- `source_candidate_id`
- `public_job`
- `source_anchor_trace`

### Proposed shape

```json
{
  "id": "composed_detail::career_route::public_voice::fix04_h10_career_stellium",
  "node_id": "promise::composed_career_route_v0_9a",
  "headline": "...",
  "teaser": "...",
  "body": "...",
  "chips": ["Kariyer", "Söz", "Görünür rol"],
  "detail_items": [],
  "family": "career_public_voice",
  "emphasis": "extra",
  "origin": "composed_detail_renderer_v0_9a_2",
  "evidence_summary": [
    "MC hattı konuşma ve görünür konum alma üzerinden çalışıyor.",
    "Merkür kariyer rotasında görünür bir rol alıyor."
  ],
  "source_type": "composed_semantic",
  "source_candidate_id": "composed_career_route_v0_9a",
  "public_job": "detail_only",
  "source_anchor_trace": {
    "family": "career_route",
    "subtype": "public_voice",
    "domain_reason": ["MC route", "MC ruler involved", "10H planet"],
    "technical_anchors": ["MC Gemini", "Mercury 10H"]
  }
}
```

### Contract rules

- `headline`, `teaser`, `body`, `chips` are public-facing
- `evidence_summary`, `source_type`, `source_candidate_id`, `public_job`, `source_anchor_trace` are traceability/debug-facing
- traceability may remain available in debug payloads even if the visible card is compact

---

## 3. How composed semantic ingredients should map to SHOU copy

### Inputs

The composed detail renderer should start from:

- `domain_reason`
- `lived_scene`
- `lived_scene_atoms`
- `gift`
- `inner_tension`
- `growth_direction`
- `evidence_trace`
- `public_job`

### Core rule

Composed semantic ingredients are not public prose.

They are meaning ingredients that must be transformed into:

- lived recognition
- concrete manifestation
- chart-specific but natural Turkish

### Mapping strategy

#### `headline`

Source priority:

1. `lived_scene`
2. `lived_scene_atoms`
3. re-authored manifestation phrase from `gift + domain_reason`

Target behavior:

- one lived recognition sentence
- no explicit astro mechanics
- no “MC, yöneticisi...” framing

#### `teaser`

Source priority:

1. compressed chart-recognition phrase from `gift`
2. contextualized from `domain_reason + lived_scene`

Target behavior:

- one short sentence
- must sound like “sende bu çizgi şöyle çalışıyor”
- must not sound like debug metadata

#### `body`

Source blend:

- opening from `lived_scene`
- second sentence from `gift`
- tension sentence from `inner_tension`
- close from `growth_direction`

Target behavior:

- 3–4 sentences
- no technical astro in the body
- no `source_type`, `candidate`, `fallback`, `generic`, `MC route`, `debug`, `public_job`
- no mixed-language `public` wording unless intentionally naturalized into Turkish

#### `chips`

Source:

- normalized semantic labels from route family/subtype

For `career_route.public_voice`, preferred chip families:

- `Kariyer`
- `Söz`
- `Görünür rol`
- `İfade`

Avoid:

- `MC`
- `10H`
- `Merkür`
- `composed`
- `debug`

### Hard negative rules

Do not render:

- `MC, yöneticisi...`
- `source_type`
- `debug_only`
- `generic visibility fallback`
- `public job`
- `candidate`
- `composed semantic`
- technical astro sentence structure in the public body

Do not fall back into:

- generic career visibility phrasing
- mixed-language `public` prose
- copy that sounds like a spec

### SHOU standard

The final card should read like:

- “evet, bu bende böyle çalışıyor”

not like:

- “the system detected a career-route public-voice subtype”

---

## 4. Target `public_voice` detail examples

These are target-style examples, not implementation output.

### A. `fix04_h10_career_stellium`

#### Target card

- `headline`:
  - `İnsanlar sende sadece ne yaptığını değil, nasıl söylediğini de fark ediyor.`
- `teaser`:
  - `Dışarıdaki etkin çoğu zaman sözünün tonu ve kurduğun pozisyonla güçleniyor.`
- `body`:
  - `Bir işi yalnız tamamlaman değil, onu nasıl anlattığın da sende görünür rolün parçası oluyor. İnsanlar çoğu zaman önce fikrinin tonunu, sonra o tonun yarattığı etkiyi fark edebilir. Buradaki güç, sesini daha yüksek kullanmakta değil; doğru yerde netleştiğinde dışarıdaki rolün zaten belirginleşmesinde yatıyor.`
- `chips`:
  - `["Kariyer", "Söz", "Görünür rol"]`

#### Why this is better than generic career fallback

- generic fallback only says visibility matters
- this version says *how* visibility happens
- it makes the route speech/position-based rather than generic ambition/visibility prose

### B. `tokyo_1998_06_21`

#### Target card

- `headline`:
  - `Dışarıdaki yerin çoğu zaman kurduğun cümleyle netleşiyor.`
- `teaser`:
  - `Ne söylediğin kadar, onu hangi sakinlik ve yön duygusuyla söylediğin de fark yaratıyor.`
- `body`:
  - `İnsanlar sende yalnızca çalışmanı değil, o çalışmayı nasıl taşıdığını da duyabilir. Bir konuda netleştiğinde sözün dışarıdaki rolünü hızlıca güçlendirebilir. Burada asıl fark, görünür olmak için zorlaman değil; doğru cümle geldiğinde yerinin zaten daha belirgin hale gelmesi olabilir.`
- `chips`:
  - `["Kariyer", "İfade", "Konum"]`

#### Why this is better than generic career fallback

- generic fallback says “visibility gains weight when ready”
- this version identifies speech, tone, and positioning as the actual career mechanism
- it reduces abstract readiness language

### C. `toronto_1976_06_26`

#### Target card

- `headline`:
  - `Görünür olduğunda bunu en çok sözün taşıyor.`
- `teaser`:
  - `Dış dünyadaki etkin, anlatım biçiminle ve insanlarda bıraktığın zihinsel iz ile büyüyebilir.`
- `body`:
  - `Bazı insanlar işini yapar; sende ise işin nasıl konuşulduğu da rolün önemli bir parçası olabilir. Bir cümleyi doğru kurduğunda ya da bir şeyi doğru çerçevelediğinde dışarıdaki ağırlığın daha hızlı hissedilebilir. Bu yüzden kariyer hattın yalnız görünürlük değil, görünürlükle birlikte çalışan bir ifade gücü de taşıyor.`
- `chips`:
  - `["Kariyer", "Söz", "Etki"]`

#### Why this is better than generic career fallback

- generic fallback treats the chart as generic visibility pressure
- this version explicitly recognizes communicative authority as the visible route
- it is more proportional to the chart’s stronger 10H communication stack

---

## 5. Guardrails

These must stay true in `v0.9a.2` planning and later implementation.

- `ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL=false` by default
- no `public_main`
- no `public_support`
- accepted goldens stable
- only `public_voice` subtype
- only when `detail_eligible == true`
- only when `ENABLE_NATAL_COMPOSED_SEMANTICS_RENDER_DETAIL=true`
- never reuse debug/spec prose as public body
- renderer must not expose:
  - raw `domain_reason`
  - raw `source_type`
  - raw `public_job`
  - raw `evidence_trace`

Additional operational guardrails:

- if composed detail renderer is unavailable, do not silently fall back to old debug/spec body
- if composed copy cannot meet quality threshold, keep packet hidden
- do not let composed detail cards leak into `differentiators` unless that is an explicit, separately reviewed decision

---

## 6. Tests to propose

### Visibility gating

- flag off: no public visibility
- flag on: renders only composed `public_voice` detail cards

### Chart targeting

- target charts get detail card:
  - `fix04_h10_career_stellium`
  - `tokyo_1998_06_21`
  - `toronto_1976_06_26`
- non-target charts do not

### Surface protection

- `public_main` unchanged
- `public_support` unchanged
- composed detail cards do not enter hero / identity / insight strip unless explicitly approved later

### Copy quality

- copy has no debug/spec language
- copy has no raw technical body leakage
- no `MC`, `10H`, `source_type`, `debug`, `candidate`, `fallback` language in public body
- no mixed-language `public` wording in public body

### Stability

- accepted goldens stable
- target chart public-main owner unchanged
- exact/chart-specific owner protection remains intact

### Traceability

- card trace still links back to:
  - `source_candidate_id`
  - `source_type=composed_semantic`
  - route family
  - subtype

---

## Recommended rollout shape

### Phase 1

- implement dedicated composed detail renderer
- flag off by default
- render only into a dedicated detail-card lane
- do not reuse `extra_blocks` / `differentiators` as the first public path if avoidable

### Phase 2

- enable only on the three reviewed target charts during audit/dev validation
- compare:
  - current generic career fallback
  - new composed detail card

### Phase 3

- only after copy quality is accepted:
  - consider a broader `public_voice` detail rollout

No phase in `v0.9a.2` should include:

- `public_support`
- `public_main`
- non-`public_voice` subtypes

---

## Final Recommendation

The safest architecture is:

- `natal_promise_cluster_plan.py`: eligibility only
- new composed detail renderer module: SHOU detail-card generation
- `projection_shadow_v1_builder.py`: guarded orchestration and insertion
- `public_builder.py`: unchanged orchestration

The three reviewed charts are strong enough to justify a dedicated composed detail renderer plan.

They are not yet strong enough to justify:

- visible spec/debug prose
- `public_support`
- `public_main`

So `v0.9a.2` should be a rendering-quality plan, not an exposure expansion.
