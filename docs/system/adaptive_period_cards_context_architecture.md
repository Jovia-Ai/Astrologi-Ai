# Adaptive Period Cards Context Architecture

## 1. Purpose of This Plan

Adaptive expandable period cards need context contracts before any rendering work starts.

Without contracts:

- cards may read too many raw fields and quietly become a second interpretation engine
- cards may rely too heavily on `period_reading_v1` and lose evidence richness
- cards may drift into natal/profile reading if they pull from `profile_v8`, `personality_imprint`, or projection surfaces
- cards may overfit to old UI-era surfaces like `blocks[]`, `daily_energy`, or `core_theme`

The solution is to create two narrow contracts:

- `PeriodCardContext / PeriodEvidenceContext`
- `NatalContextForPeriodCards`

Then the future chain becomes:

`active_life_chapter`
→ `semantic_focus_result`
→ `chapter_priority gate`
→ `composer_plan`
→ `period_reading_v1`
→ `PeriodCardContext / PeriodEvidenceContext`
→ `NatalContextForPeriodCards`
→ `period_signal_lines_v1 / adaptive expandable cards`

These contracts must organize meaning that already exists. They must not create new meaning authority.

### Voice owner note

- `docs/voice/SHOU_VOICE_VNEXT.md` remains the canonical SHOU voice doctrine and owner.
- This file is a product/architecture plan for adaptive period cards, not a replacement voice doctrine.
- The adaptive card examples here are surface-specific references, not a new authority layer.
- If an example in this plan conflicts with `SHOU_VOICE_VNEXT.md`, `SHOU_VOICE_VNEXT.md` wins.
- Final sample quality for adaptive cards should be governed by `docs/voice/adaptive_period_cards_voice_reference.md`.
- `docs/voice/handcrafted_period_validation_v4_final.md` remains the long-form period target reference.
- `docs/voice/voice_spec.md`, UX contract docs, and `docs/voice/share_line_playbook.md` remain earlier voice DNA inputs, not new authority.

## 2. Authority Chain

### Strict authority chain

- `semantic_focus_result` owns period meaning
- `chapter_priority` can mark chapter-first ownership
- `period_reading_v1` is the main public synthesis
- `PeriodCardContext` organizes period evidence and framing
- `NatalContextForPeriodCards` personalizes the selected meaning through canonical natal structure
- `period_signal_lines_v1` renders adaptive cards

### Forbidden

- cards selecting their own main meaning
- cards contradicting `semantic_focus_result`
- cards using event score alone as meaning
- cards using `daily_synthesis.body` as source
- cards using old `blocks[]` / assembler copy
- cards using `profile_v8` / `personality_imprint` as authority
- cards sounding like a second natal reading

### Core rule

Cards must project already-selected meaning and evidence into lived, user-facing expandable cards.

## 3. PeriodCardContext / PeriodEvidenceContext Design

`PeriodCardContext` is the period-side organizer.

It does not decide meaning.  
It arranges:

- who owns the current period meaning
- what evidence supports that meaning
- where it is likely to show up
- which period-side tensions, scenes, and timing hints are available for card generation

### Required inputs

- `period_core.semantic_focus`
- `period_core.chapter_priority`
- `period_core.canonical_period_spine`
- `period_core.natal_activation_context`
- `period_core.featured_events[]`
- `featured_events[].derived_context`
- `featured_events[].chapter_role`
- `featured_events[].story_score`
- `featured_events[].timing`
- `featured_events[].phase`
- `featured_events[].bucket`
- `manifestation_context`
- `suppressed_meanings`
- `period_reading_v1`
- `composer_plan`

### Important structural rule

`period_reading_v1` and `composer_plan` are **framing-only, not primary evidence**.

Authority stays structurally above them:

- `semantic_focus`
- `chapter_priority`
- `canonical_period_spine`
- `featured_events`
- `manifestation_context`

Cards can use `period_reading_v1` and `composer_plan` to keep rhythm, tone, and framing consistent with the public period reading. They must not use them to invent a different story.

### Blocked inputs

- old top-level `blocks[]`
- `daily_synthesis.body`
- raw `heat` / `rating` as meaning
- `best_times.score_by_intent` as meaning
- profile/rendered natal surfaces

### Proposed contract

```python
PeriodCardContext = {
    "version": "period_card_context_v1",
    "owner_ref": {
        "semantic_focus_source": str,
        "selected_meaning": str,
        "meaning_family": str | None,
        "confidence": float,
    },
    "primary_meaning": {
        "label": str,
        "primary_domain": str | None,
        "secondary_domains": list[str],
        "suppressed_meanings": list[str],
    },
    "source_owner": {
        "chapter_priority_applied": bool,
        "chapter_type": str | None,
        "event_cards_role": str | None,
    },
    "chapter_priority": dict,
    "main_domains": list[str],
    "suppressed_meanings": list[str],
    "period_reading_ref": {
        "version": str,
        "full_text": str,
        "block_roles": list[str],
    },
    "composer_frame": {
        "semantic_mode": str | None,
        "hook": str | None,
        "scene_anchor": str | None,
        "core_contrast": str | None,
        "mechanism": str | None,
        "growth_edge": str | None,
        "what_it_builds": str | None,
    },
    "manifestation_scenes": list[dict],
    "timing_hints": list[dict],
    "evidence_items": list["PeriodEvidenceItem"],
    "debug": dict,
}
```

```python
PeriodEvidenceItem = {
    "event_id": str,
    "evidence_role": str,
    "rank": int,
    "transit_body": str | None,
    "natal_point": str | None,
    "aspect": str | None,
    "public_event_type": str | None,
    "domain": str | None,
    "house_scene": str | None,
    "derived_context_summary": dict,
    "natal_target_summary": dict,
    "timing_phase": str | None,
    "timing_bucket": str | None,
    "chapter_role": dict | None,
    "story_score": float | None,
    "semantic_owner": str | None,
    "debug_refs": dict,
}
```

### Explicit source tiers

#### Tier A — safe primary period inputs

- `semantic_focus`
- `chapter_priority`
- `canonical_period_spine`
- `natal_activation_context`
- `featured_events[].derived_context`
- `featured_events[].chapter_role`
- `manifestation_context`
- `suppressed_meanings`

#### Tier B — support / framing inputs

- `featured_events[].timing`
- `featured_events[].phase`
- `featured_events[].bucket`
- `featured_events[].story_score`
- `period_reading_v1`
- `composer_plan`
- event tags/domains

#### Tier C — blocked as authority

- raw `story_score` alone
- `daily_synthesis.body`
- `best_times.score_by_intent`
- `story_tracks`
- `_event_story_map`
- old `blocks[]`
- raw `heat` / `rating`

## 4. NatalContextForPeriodCards Design

`NatalContextForPeriodCards` is the personalization projection.

It should translate canonical natal structure into period-relevant personalization hooks without starting a separate natal reading.

### Allowed sources

- `CanonicalNatalStateV1`
- `core_promises`
- `contradictions`
- `chart_spine`
- `meaning_graph.activation_hooks`
- `structural_state.dispositor_routes`
- `structural_state.house_ruler_routes`
- canonical natal activation outputs
- event `derived_context`
- event `natal_promise` when available
- `active_life_chapter.renderer_handoff`
- `active_life_chapter.natal_architecture_anchor`

### Blocked as authority

- `personality_imprint`
- `profile_v8`
- `full_map_v8`
- `meaning_graph_v1_1`
- projection outputs

### Proposed contract

```python
NatalContextForPeriodCards = {
    "version": "natal_context_for_period_cards_v1",
    "semantic_owner_ref": {
        "selected_meaning": str,
        "meaning_family": str | None,
        "semantic_focus_source": str,
    },
    "activated_promises": list[dict],
    "activated_contradictions": list[dict],
    "chart_spine_refs": list[dict],
    "activation_hooks": list[dict],
    "dispositor_route_hints": list[dict],
    "house_ruler_route_hints": list[dict],
    "natal_personalization_lines": list[dict],
    "suppressed_identity_claims": list[str],
    "life_chapter_natal_bridge": {
        "renderer_handoff": dict | None,
        "natal_architecture_anchor": dict | None,
    },
    "debug": dict,
}
```

### Good vs bad

Good:

> “Sen zaten sözünü kolay harcamayan birisin; bu dönem o ölçülü tarafın daha seçilmiş bir cümleye dönüşüyor.”

Bad:

> “Sen derin, kontrollü, mesafeli bir insansın.”

### Explicit source tiers

#### Tier A — safe canonical/evidence sources

- `CanonicalNatalStateV1`
- `core_promises`
- `contradictions`
- `chart_spine`
- `activation_hooks`
- `dispositor_routes`
- `house_ruler_routes`
- canonical activation outputs
- event `derived_context`
- event `natal_promise`
- life chapter natal anchor/handoff

#### Tier B — support-only, later optional

- editorialized short language atoms extracted from canonical nodes
- humanized route summaries derived from canonical structure

#### Tier C — blocked as authority

- `personality_imprint`
- `profile_v8`
- `full_map_v8`
- `meaning_graph_v1_1`
- projection outputs

## 5. How Period + Natal Contexts Combine

The merge target is:

`PeriodCardContext`
`+`
`NatalContextForPeriodCards`
`→ CardCandidateContext[]`

### Proposed merged candidate

```python
CardCandidateContext = {
    "card_id": str,
    "selected_meaning_ref": dict,
    "evidence_source": dict,
    "natal_personalization_hook": dict | None,
    "manifestation_scene": dict | None,
    "narrative_move_candidates": list[str],
    "theme_palette": str | None,
    "domain_palette": str | None,
    "suppression_list": list[str],
    "trace_refs": dict,
}
```

Each candidate must have:

- selected period meaning link
- evidence source
- natal personalization hook
- manifestation scene
- narrative move candidate
- theme palette
- domain palette
- suppression list
- trace/debug refs

Every emitted card must be explainable as:

> “This card says X because the selected period meaning is Y, supported by period evidence Z, landing in natal architecture W.”

If that sentence cannot be completed, the card should be dropped.

## 6. Theme Palettes

Theme palettes control:

- vocabulary
- rhythm
- sentence length
- metaphor level
- temporal feeling
- emotional register
- title style
- preview style
- body style

### Initial palette set

- `saturn_maturation`
- `chiron_old_sensitivity`
- `neptune_blur_or_sensitivity`
- `pluto_depth`
- `mars_action`
- `venus_value_closeness`
- `mercury_message_mind`
- `jupiter_growth`
- `node_direction`
- `eclipse_threshold`
- `uranus_change`
- `moon_emotional_rhythm`
- `sun_visibility`

### Palette definitions

#### `saturn_maturation`

- Applies when:
  - Saturn return / Saturn-heavy ownership / high responsibility line
- Preferred words:
  - yerleşmek, taşımak, seçmek, ağırlaşmak, oturmak, sorumluluk, cümle, duruş
- Avoid:
  - yüklenmek as default, kader, cezalandırma, generic burden language
- Good phrases:
  - “sözün daha ağır geliyor”
  - “rolünü saklamadan taşımak”
  - “ilk tepkiyi son söz yapmamak”
- Bad phrases:
  - “yapı kuruluyor”
  - “mekanizma çalışıyor”
  - “süreç inşa ediyor”
- Sample title:
  - `Sözün daha ağır geliyor`
- Sample preview:
  - `Hızlı söylediğin bir şey bu dönem düşündüğünden daha kalıcı yankı bırakabilir.`
- Sample body fragment:
  - `Burada mesele daha çok konuşmak değil; neyi gerçekten sahiplenerek söyleyeceğini seçmek.`

#### `chiron_old_sensitivity`

- Applies when:
  - Chiron is core evidence or strong support
- Preferred words:
  - eski yara, eski hassasiyet, kolay tetiklenen yer, daha önce de tanıdığın bir hassasiyet, korumaya alıştığın yer
- Avoid:
  - şifa, iyileşme vaadi, adını koyunca yumuşayan şey, generic wound-healing trope
- Good phrases:
  - `eski bir hassasiyet tetikleniyor`
  - `daha önce de tanıdığın bir yer`
- Bad phrases:
  - `şifa kapısı açılıyor`
  - `yaranı sarıyorsun`
- Sample title:
  - `Eski bir hassasiyet tetikleniyor`
- Sample preview:
  - `Daha önce de tanıdığın bir yer bu dönem daha kolay sızlayabilir.`
- Sample body fragment:
  - `Bir söz ya da küçük bir mesafe, bugünkü olaydan büyük bir yere dokunabilir.`

#### `neptune_blur_or_sensitivity`

- Applies when:
  - Neptune dominates period evidence
- Preferred words:
  - buğulanmak, belirsizlik, varsayım, sezgi, karışmak, netlik aramak
- Avoid:
  - sis metaphors repeated mechanically, mistik akış, surrender cliché
- Good phrases:
  - `boşlukları varsayımla doldurmak`
  - `netlik azaldığında`
- Bad phrases:
  - `geçirgen`
  - `üst anlam`
- Sample title:
  - `Belirsizlik hemen dolmak istiyor`
- Sample preview:
  - `Net olmayan bir şeyi erkenden anlamlandırmak isteyebilirsin.`
- Sample body fragment:
  - `Burada mesele her şeyi çözmek değil; gerçekten neyi bildiğini neyi hissettiğini ayırabilmek.`

#### `pluto_depth`

- Applies when:
  - Pluto / high-depth transformation signals are central
- Preferred words:
  - derinleşmek, altı oyulmak, bırakmamak, güç, kontrol, iç basınç
- Avoid:
  - kriz pornosu, yok oluş dili, therapy diagnosis
- Sample title:
  - `Kolay bırakamadığın bir yer açılıyor`

#### `mars_action`

- Applies when:
  - Mars is central
- Preferred words:
  - ilk tepki, harekete geçmek, hızlanmak, karşılık vermek, keskinleşmek
- Avoid:
  - aggression cliché, savaşçı branding
- Sample title:
  - `İlk tepkin daha hızlı geliyor`

#### `venus_value_closeness`

- Applies when:
  - Venus, value, closeness, aesthetics, relation-value lines
- Preferred words:
  - sıcaklık, değer, güzellik, yaklaşmak, hoşuna gitmek, yumuşaklık
- Avoid:
  - sweet generic romance copy
- Sample title:
  - `İstediğin şey daha görünür oluyor`

#### `mercury_message_mind`

- Applies when:
  - Mercury / 3rd / 9th / communication-learning lines
- Preferred words:
  - cümle, mesaj, ton, açıklamak, duymak, yazmak, küçük konuşma
- Avoid:
  - zihinsel süreçler abstraction overload
- Sample title:
  - `Bir cümle daha fazla ağırlık taşıyor`

#### `jupiter_growth`

- Applies when:
  - Jupiter / expansion / belief / meaning lines
- Preferred words:
  - büyümek, ufuk, genişlemek, daha fazla yer kaplamak, güvenmek
- Avoid:
  - guaranteed success, abundance cliché
- Sample title:
  - `Yer açılan tarafın büyüyor`

#### `node_direction`

- Applies when:
  - nodal return / nodal activation / direction line
- Preferred words:
  - yön, çizgi, ayarlamak, onay, kendi sözün, birlikte ama kaybolmadan
- Avoid:
  - generic self/other balance
- Sample title:
  - `Yönünü daha açık söylemek`

#### `eclipse_threshold`

- Applies when:
  - eclipse-triggered threshold periods
- Preferred words:
  - eşik, görünür olmak, perde kalkmak, keskinleşmek
- Avoid:
  - fate theater
- Sample title:
  - `Bir eşik görünür hale geliyor`

#### `uranus_change`

- Applies when:
  - Uranus / disruption / release / rewire
- Preferred words:
  - yerinden oynatmak, ani, farklı yol, alışkanlığı bozmak
- Avoid:
  - chaos-only language
- Sample title:
  - `Aynı yoldan gitmek zorunda hissetmiyorsun`

#### `moon_emotional_rhythm`

- Applies when:
  - Moon / regulation / body-rhythm / sensitivity
- Preferred words:
  - iç tempo, dalga, yakın his, rahatlama, taşma
- Avoid:
  - generic moodiness
- Sample title:
  - `İç ritmin daha görünür`

#### `sun_visibility`

- Applies when:
  - Sun / identity / visibility / center-stage
- Preferred words:
  - görünmek, duruş, isim, merkez, dikkat
- Avoid:
  - spotlight cliché
- Sample title:
  - `Duruşun daha fazla fark ediliyor`

## 7. Domain Palettes

### creativity / project / production

- Lived scenes:
  - yarım kalan fikir, taslak, not, dosya, deneme, görünür kılmak
- Preferred words:
  - taslak, form vermek, üslup, küçük deneme, görünür yapmak
- Avoid:
  - üretkenlik teması, yaratıcılık alanı
- Possible titles:
  - `Yarım kalan fikir geri dönüyor`
  - `Bir şeye küçük bir form vermek`

### work / career / visibility

- Lived scenes:
  - toplantı, rol, sorumluluk, teslim, görünürlük, emeği saklamamak
- Preferred words:
  - rol, emek, duruş, görünür olmak, sorumluluk
- Avoid:
  - başarı geliyor, kariyer alanı öne çıkıyor
- Possible titles:
  - `Rolünü saklamadan taşımak`
  - `Emeğin daha görünür oluyor`

### relationship / intimacy / agreements

- Lived scenes:
  - yan yana durmak, aynı masada kalmak, güven, kendini silmemek, anlaşma
- Preferred words:
  - yakınlık, güven, sınır, birlikte, aynı masada
- Avoid:
  - fated relationship drama, generic ilişki dengesi
- Possible titles:
  - `Yan yana dururken kendini kısmamak`
  - `Yakınlıkta kendini kaybetmemek`

### money / self-worth / resources

- Lived scenes:
  - emeğin karşılığı, değerin, ortak kaynak, tutmak-bırakmak
- Preferred words:
  - değer, karşılık, kaynak, elinde tutmak, hak etmek
- Avoid:
  - bolluk vaadi, manifest prosperity tone
- Possible titles:
  - `Karşılığını daha dikkatli ölçüyorsun`

### home / family / inner security

- Lived scenes:
  - evde, yalnız kaldığında, iç düzen, güvende hissetmek, dışarıdaki duruşa taşımak
- Preferred words:
  - evde, iç güvenlik, yalnız kaldığında, iç düzen, sana ait alan
- Avoid:
  - duygusal alan, iç dünya as empty abstraction
- Possible titles:
  - `Sana ait alan daha görünür`
  - `İçerideki düzen dışarıya taşıyor`

### mind / communication / learning

- Lived scenes:
  - mesaj, kısa konuşma, ton ayarı, açıklamak, yanlış anlamak, öğrenmek
- Preferred words:
  - cümle, mesaj, küçük konuşma, ton, anlatmak
- Avoid:
  - iletişim teması, zihinsel süreç
- Possible titles:
  - `Bir cümle beklediğinden ağır düşüyor`

### body / daily rhythm / routine

- Lived scenes:
  - sabah düzeni, enerji düşüşü, tekrar eden alışkanlık, tempo
- Preferred words:
  - ritim, düzen, tempo, dayanmak, sürdürebilmek
- Avoid:
  - wellness coaching
- Possible titles:
  - `Ritmini neyin bozduğunu görüyorsun`

### social / friends / community

- Lived scenes:
  - arkadaş çevresi, bir grubun içinde durmak, birlikte üretmek, görünür olmak
- Preferred words:
  - çevre, birlikte, ait olmak, paylaşmak
- Avoid:
  - sosyal alan aktivasyonu
- Possible titles:
  - `Birlikte olduğun yer seni değiştiriyor`

### inner work / solitude / spirituality

- Lived scenes:
  - çekilmek, yalnız kalmak, içerde çözmek, sessizlik
- Preferred words:
  - geri çekilmek, içeride kalmak, çözülmek, susmak
- Avoid:
  - spiritüel açılım, ruhsal aktivasyon
- Possible titles:
  - `Sessizlikte daha çok şey duyuluyor`

## 8. Adaptive Narrative Moves

These are internal only:

- `scene`
- `inner_state`
- `construction`
- `clarification`
- `pressure`
- `support`
- `threshold`
- `integration`
- `repair`
- `visibility`
- `choice`
- `boundary`
- `softening`
- `embodiment`
- `relationship_mirror`
- `creative_form`
- `work_visibility`
- `value_check`
- `home_inner_safety`
- `communication_reflex`
- `timing_peak`
- `timing_release`

Rules:

- moves are internal/debug only
- public title is generated, not equal to move name
- no move is mandatory
- no fixed move order
- card count `0–8`, typically `3–6`
- no padding
- evidence decides which moves fire

Not every period has release.  
Not every period has learning.  
Some are construction.  
Some are clarification.  
Some are pressure.  
Some are support.

## 9. Copy Style: Lived Recognition

This is the most important voice rule.

Cards must not read like analysis summaries.

Detailed surface-quality examples live in `docs/voice/adaptive_period_cards_voice_reference.md`.
This section defines architecture-level voice constraints, not the full example pack.

### Core formula

`Data → analysis değil.`  
`Data → lived recognition.`

Cards should feel like:

> “a small page from the user’s life”

not:

> “a categorized astrology analysis”

### Every card should answer

- Where might this show up?
- What might the user feel or do?
- What tension is underneath?
- What becomes possible if they notice it?

### Translation rule

Raw astrologer analysis may contain technical explanation.

Adaptive cards must translate that analysis into lived cards.

- do not expose technical astrology in the public card body
- use technical evidence only in `context_used`, debug traces, or optional human evidence expansion
- if a sentence still sounds like explanation-of-data, it has not finished translating into SHOU card language

### Prefer

- lived scenes
- concrete objects/actions
- relational moments
- small moments that reveal the larger pattern
- second-person recognition
- one emotional tension per card
- one memorable line per card

### Creative Freedom vs Hard Guardrails

The goal is not rule-compliant copy.

The goal is precise, alive, emotionally recognizable copy that still respects semantic authority.

#### Hard guardrails

Hard bans are only:

- outcome / prediction claims
- therapy / diagnosis language
- technical astrology leakage in public body
- semantic contradiction with `semantic_focus` / `suppressed_meanings`
- new meaning authority
- generic domain-label prose as final output

These are blocking failures.

#### Creative guidance

Everything else should be treated as:

- avoid overuse
- avoid default template
- use only if the sentence feels alive and clear

Clarifications:

- `Bu dönem` is not globally banned, but cannot become the default opening.
- `Olabilir / gelebilir` is not globally banned, but supportive/opening cards should not over-soften by default.
- `Öğreniyorsun / fark ediyorsun` is not globally banned, but cards should prefer lived moments when possible.
- Metaphor is allowed if it makes the experience more concrete, not more abstract.
- Some abstract personification is allowed if it sounds alive in Turkish and does not obscure meaning.

Permissions:

- You may write bold recognition lines.
- You may use sensory detail.
- You may use short poetic turns.
- You may use strong but non-predictive sentences.
- You may let supportive aspects feel warm, bright, and alive.
- You may let hard aspects feel dense without making them scary.
- You may write a sentence that feels like a person noticing themselves, not a system explaining them.

### Watchlist vocabulary / constructions

#### Translation-smell and mechanical nouns

- geçirgen
- üst anlam
- bütünlüklü yön
- yön duygusu
- aktivasyon
- mekanizma
- proses

#### Parallel-philosophy patterns

- `X yapmakla Y aynı şey değil`
- `aynı şey değil`
- `aynı yerde durmuyor`
- `arasındaki farkı kaçırma`

#### Anthropomorphic abstract subjects

Avoid overusing constructions where abstraction becomes a speaking/wanting agent:

- `ihtiyaç aynı anda söz istiyor`
- `sürtünme konuşuyor`
- `yakınlık senden bir şey istiyor`
- `yön duygusu arıyor`

A small amount of personification is acceptable if the sentence stays clear, alive, and emotionally legible in Turkish.

#### Segment-announcing connectors

- `Bu en çok... görünür`
- `Risk:`
- `Bu dönem sende... kasını`
- `Bunun altında şu fark çalışıyor`

#### Heavy gravitas drift

- borç
- suçluluk
- yargı
- generic burden language when not evidence-backed

### Do not write analytical summaries

Write lived recognitions.

Cards should feel like:

> “a small page from the user’s life”

not:

> “a categorized astrology analysis.”

Hard avoid:

- outcome claims
- therapy tone
- technical astrology leakage in public body
- generic domain-label prose as final output

Soft avoid as defaults:

- `X alanında Y teması öne çıkıyor`
- `Bu dönem Z dinamiği çalışıyor`
- `Bu süreç sana ... öğretiyor` as default
- `Bu tema...`
- `Bu yapı...`
- `Bu dinamik...`
- domain-label prose
- abstract nouns stacked together
- generic coaching advice

Prefer:

- lived scenes
- concrete objects/actions
- relational moments
- small moments that reveal the larger pattern
- second-person recognition
- one emotional tension per card
- one memorable line per card

Each card should answer:

- Where might this show up?
- What might the user feel or do?
- What tension is underneath?
- What becomes possible if they notice it?

### Core distinction

Bad:

> “Bu dönem yaratıcılık alanında üretim ve görünürlük temaları öne çıkıyor.”

Good:

> “Aklında uzun zamandır duran bir fikir artık sadece içeride dönmek istemiyor. Bir taslak, bir not, bir küçük deneme bile bu dönem ‘beni dışarı çıkar’ diyebilir.”

Bad:

> “İlişkilerde sınır ve yakınlık teması çalışıyor.”

Good:

> “Birine yakın dururken kendini ne kadar geri çektiğini daha net fark ediyorsun. Bu dönem mesele sevmek ya da uzaklaşmak değil; yan yana dururken kendini kaybetmemek.”

Bad:

> “Kariyer alanında sorumluluk ve görünürlük artıyor.”

Good:

> “Dışarıda senden beklenen rol biraz daha ağırlaşabilir. Ama bu sadece yük değil; emeğini saklamadan ‘ben bunu taşıyorum’ diyebileceğin bir sahne de açıyor.”

### Assertive empathy

Cards should be emotionally assertive enough to feel seen.

Avoid overly cautious product-copy language as the default:

- `daha kolay gelebilir`
- `doğal olabilir`
- `alan açılıyor`
- `destekleniyor`
- `mümkün olabilir`
- `öne çıkıyor`
- `tema çalışıyor`

These can appear when uncertainty is genuinely part of the lived experience, but they should not become the default SHOU card voice.

Preferred SHOU mode:

- direct recognition
- second-person present tense
- emotionally specific
- confident but not predictive
- empathic without becoming therapy language

Bad:

> “Yakınlık bu ara daha kolay gelebilir.”

Better:

> “Birinin yanında kendini daha az açıklayarak da sıcak kalabildiğini fark ediyorsun.”

Bad:

> “Yaratıcılık alanında destekleniyorsun.”

Better:

> “Aklında bekleyen fikir artık sadece içeride dönmek istemiyor.”

Bad:

> “Kariyer görünürlüğün artabilir.”

Better:

> “Yaptığın iş saklandığı yerden biraz daha öne çıkıyor.”

### Valence-sensitive voice

Do not make every card cautionary.

Tone must follow:

- `valence_mode`
- `intensity_mode`
- `theme_palette`
- `domain_palette`
- `chapter_role`
- semantic focus voice hints

Support / opening / recognition:

- should feel alive, warm, easier to enter
- not cautionary
- not `be careful` by default
- use small movement / ease / visibility / warmth
- can be warm, bright, and direct without apologizing for themselves

Examples:

- `Bir cümle fazla zorlamadan yerine oturuyor.`
- `Aklında bekleyen fikir artık sadece içeride dönmek istemiyor.`
- `Emeğin saklandığı yerden biraz daha öne çıkıyor.`
- `Birinin yanında kendini daha az açıklayarak da sıcak kalabiliyorsun.`

Tension / pressure:

- should feel grounding, not scary
- show friction, choice, boundary, slowing down
- do not dramatize
- can sound dense or tight without becoming threatening

Maturation:

- construction, responsibility, steadiness
- not punishment / heaviness by default

Release:

- loosening, softening, less gripping
- not forced loss

Recognition:

- being seen
- `this is already there`
- not motivational praise
- should feel like a person noticing themselves, not a system naming a category

Momentum:

- directness, movement, aliveness
- not danger by default

### Not all cards are negative / preventive

Do not write every card as:

- warning
- repair
- old wound
- caution
- slowing down

Some cards should feel like:

- creativity waking up
- a project finding form
- warmth in relationship
- visibility in work
- value becoming easier to claim
- a conversation finding its place
- a small opening in timing

## 10. Adaptive Expandable Card UX

Each card should support:

- title
- preview
- body
- optional `timing_hint`
- optional `evidence_summary`
- optional tone/move indicator for debug only

### Collapsed

- title
- preview

### Expanded

- full body
- optional human “neden?” / “neden önemli?” evidence

### Body length

- `2–6` sentences
- richer periods get richer cards
- equal length must not be forced
- support cards can be shorter
- rich periods can have longer bodies
- preview opens the card; body deepens it
- body should not simply repeat the preview
- consecutive cards should not start with the same rhythm
- rich chapter cards can breathe

### Rhythm note

Because cards are expandable:

- title should be short, alive, and never read like a category label
- preview should usually be `1–2` sentences
- body can vary in length according to evidence density
- one period can contain a short support card beside a longer pressure or integration card
- rhythm variety matters across consecutive cards; repeated opening cadence makes the surface feel mechanical

UI can later render:

- horizontal carousel
- vertical accordion
- stacked expandable cards

Internal move names must not surface in UI.

## 11. Selection Algorithm

Conservative algorithm:

1. Build `PeriodCardContext`.
2. Build `NatalContextForPeriodCards`.
3. Merge into candidate contexts.
4. Assign theme palette.
5. Assign domain palette.
6. Propose narrative moves.
7. Drop unsupported moves.
8. Dedupe by fingerprint.
9. Apply no-contradiction checks.
10. Rank.
11. Emit `0–8` cards.

### Ranking factors

- alignment with semantic focus primary meaning/domain
- chapter-priority evidence if applied
- featured-event chapter role / story score
- domain diversity
- natal activation relevance
- novelty vs `period_reading_v1`
- timing relevance

No evidence, no card.  
No padding.

## 12. Consistency and No-Contradiction Rules

Mandatory:

- card cannot contradict `semantic_focus.suppressed_meanings`
- card cannot promote suppressed readings
- card cannot be more confident than owner
- card cannot state outcome predictions
- card cannot create a different main story
- event-derived cards are support/evidence unless aligned with owner
- if `chapter_priority.applied=true`, cards orbit chapter owner
- if `chapter_priority.applied=false`, cards are evidence-guided but must not pretend to be LifeChapter
- cards must not repeat `period_reading_v1` verbatim unless intentionally linked
- cards must not use old `blocks[]` / daily body as source

Implementation should later include:

- `alignment_check(card, semantic_focus_result)`
- `suppressed_meanings_conflict_check(card)`
- `dedupe_fingerprint(card)`

Cards that fail should be dropped, not softened into vague prose.

## 13. Relation to Old `blocks[]` Surface

The old top-level `blocks[]` surface is legacy.

Do not use it for adaptive cards.

Do not base card copy on:

- `core_theme`
- `daily_energy`
- `event_list_preview`
- `challenge`
- `support`
- `alert`
- old assembler prose

Future:

- deprecate legacy `blocks[]` except `best_time_*` later if still needed
- but not in this PR

## 14. Real Artifact Analysis

This section validates the proposed contracts against real current cases.

### A. 2026-03-04 real route case

Observed:

- `semantic_focus.source = period_voice_policy`
- `selected_meaning = reorientation`
- `primary_domain = küçük cümlelerin ağırlığı`
- `manifestation_context.primary_house = 3`
- top period evidence includes Neptune square Sun, Neptune square DSC, Saturn sextile Uranus
- `chapter_priority.applied = false`
- `period_reading_v1` is rich, but still fallback-guided rather than chapter-owned

Contract validation:

- `PeriodCardContext` can safely organize:
  - reorientation owner
  - communication-weighted scene
  - relationship boundary support
  - identity pressure support
- `NatalContextForPeriodCards` can personalize through:
  - Sun in 1st
  - DSC relationship edge
  - Saturn/Uranus identity structure

What cards this could produce:

- a communication-reflex card
- a relationship-mirror card
- an identity-under-blur support card

What should not be used:

- raw score alone
- generic “iletişim teması”
- daily body copy

### B. 2026-04-22 real route case

Observed:

- `semantic_focus.source = period_voice_policy`
- `selected_meaning = reorientation`
- semantic focus leans communication/near-environment
- top evidence also includes strong identity and 4th-house/home-support signals
- `chapter_priority.applied = false`
- `period_reading_v1` is improved but still thinner than Tier-1 chapter cases

Contract validation:

- This case proves that cards need a narrow evidence organizer.
- The owner stays reorientation.
- Secondary support can still surface:
  - inner safety
  - identity/ASC/Sun
  - 4th-house/home pull

What cards this could produce:

- inner safety to outer stance card
- small-signal / sentence-weight support card
- identity-under-belief-shift support card

What should not happen:

- a new faux-LifeChapter story
- a communication-only monopoly if event evidence is wider
- a home-only override that contradicts selected owner

### C. Cancer 8th Saturn return

Observed:

- `semantic_focus.source = life_chapter`
- `selected_meaning = shared_emotional_territory`
- `primary_domain = trust_transformation`
- chapter handoff fields exist
- suppressed meanings are explicit

Contract validation:

- Chapter-owned cards are safe here.
- `PeriodCardContext` can orbit:
  - shared burden
  - trust boundary
  - what stays private vs what becomes shared
- `NatalContextForPeriodCards` can personalize through trust and architecture anchors

### D. Nodal Aries/Libra

Observed:

- `semantic_focus.source = life_chapter`
- `selected_meaning = directional_self_definition`
- `chapter_priority.applied = true`
- suppressed meanings block generic self/other balance

Contract validation:

- Cards can safely orbit direction/self-definition.
- The contract prevents generic relationship-drama drift.

### Why this section matters

These real cases show that the proposed contracts are not theoretical. They map onto real current runtime shapes:

- chapter-owned period cases
- non-LifeChapter fallback cases
- mixed evidence / mixed domain cases

## 15. Sample Outputs

The architecture plan keeps only concise examples.

- These are provisional references, not templates.
- Final sample quality should be governed by `docs/voice/adaptive_period_cards_voice_reference.md`.
- Do not copy sentence structures mechanically.

### Architecture-level examples

#### A. Technical analysis -> lived card

Raw analysis:

> `Saturn return in Aries 3rd with South Node overlap means speech, quick reactions, nearby conversations, and old reflexive communication patterns mature.`

Card direction:

- Title: `Sözün yerini buluyor`
- Preview: `Kelimelerin artık daha seçilmiş bir yere oturuyor.`
- Body move: fast reaction -> chosen sentence -> felt authorship

#### B. Home/identity blur -> lived card

Raw analysis:

> `Neptune square MC/IC dissolves career direction and inner security definitions.`

Card direction:

- Title: `Eski yönler dar geliyor`
- Preview: `“Nereye gidiyorum?” sorusuna eskisi kadar hızlı cevap vermek istemeyebilirsin.`
- Body move: inner safety <-> outer role tension without technical exposition

#### C. Supportive communication -> lived card

Raw analysis:

> `Mercury support helps expression land more clearly.`

Card direction:

- Title: `Bir cümle yerine oturuyor`
- Preview: `Söylemek istediğin şey fazla uzamadan kendini anlatacak kadar netleşiyor.`
- Body move: simple scene -> clearer sentence -> felt position

For full good/bad pairs and polished examples, use the dedicated voice reference doc.

## 16. Implementation Phases

### Phase 0

- finalize contracts
- decide schema names

### Phase 1

- emit `PeriodCardContext / PeriodEvidenceContext`
- emit `NatalContextForPeriodCards`
- no public card copy yet
- tests validate traceability and no-authority drift

### Phase 2

- backend additive `period_signal_lines_v1` card rendering
- no mobile change
- sample review

### Phase 3

- mobile tap-to-expand UI
- carousel or accordion

### Phase 4

- human-readable evidence expansion / “neden?” rail

### Phase 5

- theme/domain palette expansion

## 17. Tests To Propose

### Contract tests

- context exists when period evidence exists
- every card candidate links to semantic owner
- every card candidate has `evidence_refs` / `context_used`
- no candidate from old `blocks[]` / daily body
- no candidate from `profile_v8` / `personality_imprint` as authority

### Card tests

- card count `0–8`
- rich cases usually `3–6`
- every card has title, preview, body
- title is not internal move label
- no duplicate fingerprints
- primary cards align with semantic focus
- chapter cards orbit chapter owner
- no suppressed meaning appears
- no banned phrases
- no outcome claims
- no translation-smell words

### Voice tests

- Chiron cards can use:
  - `eski yara`
  - `eski hassasiyet`
  - `kolay tetiklenen yer`
- Chiron cards do not use:
  - `adını koyunca yumuşayan şey`
- creativity cards mention:
  - project / form / taslak / üslup when evidence supports
- career cards avoid outcome claims
- relationship cards avoid fated relationship drama

### Regression

- `period_reading_v1` unchanged
- daily unchanged
- natal unchanged
- PR-D unchanged

## 18. Open Questions

- final schema name
- sibling surface vs enriched `period_reading_v1.blocks`
- exact v1 palette count
- where `timing_hint` comes from
- carousel vs accordion mobile choice
- whether `evidence_summary` should be public in v1
- whether Phase 1 should emit only contexts before copy cards

## 19. Provisional Voice Reference Warning

The sample language in this plan is provisional.

Before implementation, maintain a dedicated surface-specific examples doc:

- `docs/voice/adaptive_period_cards_voice_reference.md`

That reference doc should contain:

- good/bad pairs
- positive/supportive aspect examples
- tension/pressure examples
- creativity/career/relationship examples
- Chiron old sensitivity examples
- a clear `do not copy mechanically` warning

Do not implement cards until this reference is reviewed by the voice lead.

## Final Recommendation

Do not implement adaptive cards directly from raw runtime fields.

First:

1. finalize `PeriodCardContext / PeriodEvidenceContext`
2. finalize `NatalContextForPeriodCards`
3. validate them against real artifact cases
4. then build `period_signal_lines_v1`

That path preserves semantic ownership, keeps natal personalization canonical, and gives adaptive cards enough evidence to feel alive without becoming a second interpretation engine.
