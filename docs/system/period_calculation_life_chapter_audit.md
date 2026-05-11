# Period Calculation + Life Chapter Audit

**For:** Sahra  
**Date:** 2026-05-04  
**Type:** Audit only  
**Runtime change:** none  
**Deliverable goal:** decide whether period is already life-chapter-aware, or whether a `LifeChapterDetector` layer must be added before period can fully think like an astrolog

## TL;DR

1. **Period şu an nasıl hesaplanıyor?**  
   Period bugün hâlâ esas olarak `120-day transit window -> selected event IDs -> canonical_period_spine -> period_core -> period_voice_policy -> renderer` zinciriyle kuruluyor.

2. **Major-cycle signal'leri var mı, ne kadar live?**  
   Evet, `saturn_return`, `jupiter_return`, `nodal_return`, `solar_year_frame`, `eclipse`, `station`, `house_ingress` gibi sinyaller live; ama bunlar top-level reasoning owner değil, scoring/payload side-rail seviyesinde.

3. **`Saturn return Koç 3. ev + South Node Koç 3. ev` gibi LifeChapter şu an üretilebilir mi?**  
   **Partial only.** Ayrı sinyaller detect ediliyor ama bunları tek bir `LifeChapter` nesnesinde birleştirip ana hikâye olarak period selection’a koyan layer yok.

4. **Eksik en kritik 3 şey:**  
   - explicit `LifeChapter` contract + detector  
   - pass/phase model (`approaching`, `first_pass`, `retrograde_review`, `final_pass`, `integrating`)  
   - chapter-first hierarchy (`life_chapter -> major_period -> thematic_period -> short_wave -> daily_trigger`)

5. **Önerilen ilk PR?**  
   **PR-A:** readonly signal registry + `LifeChapter` contract doc/facade skeleton.  
   Scope: mevcut cycle/return sinyallerini tek shape altında toplamak, ama henüz runtime selection owner yapmamak.

---

## Executive Verdict

En net sonuç şu:

```text
Repo major-cycle ingredient'lara sahip.
Ama current period system henüz major-cycle-led değil.
Hâlâ event-selection-led.
```

Yani sistem bugün şu soruları iyi cevaplıyor:

- hangi transit event'ler önemli?
- bunlardan hangileri period story'ye girecek?
- hangi natal spine aktive oluyor?
- hangi voice register ile yazılacak?

Ama şu soruyu **ilk soru olarak** sormuyor:

```text
Bu kişinin hayatında şu an ana chapter ne?
```

Bu yüzden period güçlüleşmiş olsa da henüz tam astrolog-thinking layer’a çıkmış değil.

---

## 1. Current Period Calculation

## 1.1 Live route trace

Canlı zincir bugün pratikte şöyle:

1. `transits.py` raw transit engine response’u üretir.  
2. `selection.py -> select_event_ids(...)` story-first event seçimi yapar.  
3. `public_builder.py` event cards + `canonical_period_spine` + `period_core` oluşturur.  
4. `deep_archetype_engine.py -> build_period_core(...)` seçilen event’leri tek period gövdesine toplar.  
5. `period_voice_policy.py` framing / meaning-intent / rhetorical-frame / valence-intensity çıkarır.  
6. `astrolog_narrative_engine.py` final prose üretir.  
7. Daily tarafı sonra bunun altına bağlanır: `daily_selection -> daily_synthesis -> today_story_candidate`.

Kritik satırlar:

- route orchestration: `backend/app/api/routes/transits.py`
- event selection: `backend/app/transit/narrative/selection.py`
- period core build: `backend/app/transit/narrative/deep_archetype_engine.py`
- period renderer: `backend/app/transit/narrative/astrolog_narrative_engine.py`

## 1.2 Bir period’u bugün ne yaratıyor?

Bugünkü cevap:

```text
selected transit events create the period
```

Detay:

- route bir transit window kuruyor
- raw events içinden `select_event_ids(...)` ile az sayıda public/story-worthy event seçiliyor
- `period_core` bu seçilmiş event listesi üzerinden kuruluyor
- `canonical_period_spine` bu seçilmiş event card'ların canonical natal activation match’i üzerinden ekleniyor

Yani bugünkü owner:

```text
event aggregation + selection score
```

owner değil:

```text
major cycle / life chapter
```

## 1.3 Hangi time window kullanılıyor?

Route-level period window bugün açıkça sabitlerle kuruluyor:

- `DEFAULT_PERIOD_DAYS = 120`
- `DEFAULT_PERIOD_STEP_HOURS = 24`
- `DEFAULT_PERIOD_MAX_EVENTS = 20`

Kaynak: `backend/app/api/routes/transits.py`

Bu da şu anki period’ün:

- transit-window-based
- medium/long bucket aware
- ama independent chapter timeline owner olmayan

bir yapı olduğunu doğruluyor.

## 1.4 Selected event IDs üzerinden mi kuruluyor?

Evet.

`build_period_core(...)` doğrudan `event_cards` içindeki `event_id` listesinden seçilmiş raw event’leri geri bulup period gövdesini onlardan inşa ediyor.

Bu çok kritik çünkü bugünkü reasoning sırası fiilen şu:

```text
important events chosen first
then period meaning is built from those events
```

Henüz şu değil:

```text
main chapter chosen first
then events are subordinated under that chapter
```

## 1.5 Event score dışında priority level var mı?

**Partial.**

Event selection yalnız düz strength ile çalışmıyor; şu tür sinyaller var:

- `structurality`
- `lasting_change`
- `chapter_opening`
- `root_cause_weight`
- `chapter_role`
- bucket weighting (`long / medium / short`)

Bunlar `selection.py`, `event_feature_vector.py`, `chapter_role_engine.py` içinde var.

Ama bunlar hâlâ:

```text
weighted event-scoring features
```

top-level hierarchy değil.

## 1.6 Period selection Saturn return / nodal return / profection / progression / solar return’den haberdar mı?

Bugünkü ayrım:

### Haberdar olduğu şeyler

- `saturn_return`
- `jupiter_return`
- `nodal_return`
- `nodal_opposition`
- `chiron_return`
- `eclipse`
- `station`
- `house_ingress`
- `solar_year_frame`

### Haberdar olmadığı şeyler

- profection year
- time lord
- progressed Moon
- progressed lunation phase
- secondary progression engine as period owner

Ama haberdar olduğu signal’leri de period selection şu anda:

```text
life chapter first-class owner
```

olarak kullanmıyor.

---

## 2. Existing Major-Cycle Support

## 2.1 Catalog

| Signal / module | File | Role now | Live or dead | Implemented or placeholder | Used in period selection or only side rail |
|---|---|---|---|---|---|
| `saturn_return`, `jupiter_return`, `nodal_return`, `nodal_opposition`, `chiron_return` | `backend/app/transit/astro_event_v2.py` | cycle event detector | live | implemented | indirect: affects selection via event features, but not top-level owner |
| `solar_year_frame` | `backend/app/transit/astro_event_v2.py` | annual frame builder | live | implemented | payload/side rail, not period owner |
| `solar_year_frame` route plumbing | `backend/app/api/routes/transits.py` | attaches annual frame to payload | live | implemented | payload only |
| `structural_chapter_rail` | `backend/app/transit/astro_event_v2.py` + `public_builder.py` | chapter-like rail exposure | live | implemented | side rail only |
| `eclipse_trigger` | `astro_event_v2.py`, `daily_selection.py`, `event_feature_vector.py` | structural/transient event family | live | implemented | yes, as scored event family |
| `station_event` | `calendar_builder.py`, `astro_event_v2.py`, `daily_selection.py` | phase marker + event family | live | implemented | yes, as scored event family |
| `house_ingress_event` | `astro_event_v2.py` | slow-body ingress chapter-like event | live | implemented | indirect only |
| `chart_ruler` | natal graph + transit helper layers | natal importance context | live | implemented | context/scoring, not chapter owner |
| `dispositor` | `hybrid_context.py` | event enrichment | live | implemented | not chapter owner |
| `profection`, `time_lord` | repo search | none | missing | no runtime impl | no |
| `progressed_moon`, `progression`, `progressed_lunation` | repo search + model literals | partial naming only | mostly dead/placeholder | not period-live | no |
| `solar_return` | `build_solar_year_theme` / `_solar_return_datetime` | annual frame math | live | implemented | not period owner |
| `sect`, `essential dignity` | repo search | not in transit period path | partial elsewhere at best | not period-live | no |

## 2.2 Important nuance

Bu çok önemli:

```text
“signal exists” != “signal owns period reasoning”
```

Repo’da `saturn_return` detection olması, period’in gerçekten:

```text
this is the main chapter
```

dediği anlamına gelmiyor.

Bugünkü durumda daha doğru ifade:

```text
major-cycle signals exist as strong event families
but they do not yet outrank the period selection architecture
```

---

## 3. Saturn Return Detection Capability

Audit reference example:

```text
Saturn return
Koç
3. ev
South Node Koç 3. ev
```

## 3.1 System şu anda neyi detect edebiliyor?

### Detect edebiliyor

- transit Saturn natal Saturn ilişkisini `saturn_return` olarak
- raw event window içinden return-like chapter event çıkarmayı
- sign / house context’in bazı parçalarını event-level olarak
- solar-year resonance eklemeyi
- node body’lerini tanımayı
- canonical natal promise / activation hook eşleşmelerini ayrı katmanda

### Kısmen detect ediyor

- orb/exactness: raw event exactness üzerinden, ama dedicated return-phase contract değil
- natal rulership / dispositor / natal aspect context: event enrichment içinde var
- chart spine / canonical promise bağı: activation context + canonical spine üzerinden dolaylı var

### Detect edemiyor

- `approaching`
- `first_pass`
- `retrograde_review`
- `final_pass`
- `integrating`

Çünkü `_phase_from_now(...)` şu an her durumda `"active"` dönüyor.

## 3.2 South Node overlap’i chapter level’da üretebiliyor mu?

Hayır, birleşik chapter olarak üretemiyor.

Bugün mümkün olan:

- ayrı bir `saturn_return` signal
- ayrı bir node-related context
- ayrı bir canonical activation / natal promise / spine mapping

Ama mümkün olmayan:

```text
LifeChapter {
  chapter_type = saturn_return
  selected_meaning = old reflexive speech patterns maturing
  evidence = [Saturn return, Aries 3rd, South Node overlap, natal promise...]
  suppressed_readings = [...]
}
```

Yani worked example için cevap:

```text
partial, not unified
```

## 3.3 Eksik olan tam olarak ne?

- return-phase model
- chapter merge logic
- overlap weighting (`saturn_return + south_node_same_sign_house`)
- selected meaning chooser
- suppressed reading list
- chapter priority override in period selection

---

## 4. Period Hierarchy

## 4.1 Current system distinguish ediyor mu?

Tam olarak hayır.

Bugünkü sistemde şu seviyeler açıkça ayrılmış değil:

```text
Level 5 life_chapter
Level 4 major_period
Level 3 thematic_period
Level 2 short_wave
Level 1 daily_trigger
```

Onun yerine:

- structural event families
- bucket weighting
- chapter role
- daily trigger selection

var.

Bu, hierarchy-benzeri ama hierarchy-değil.

## 4.2 Recommended hierarchy

### Level 5 — `life_chapter`

Örnek:

- Saturn return
- nodal return
- nodal activation with major natal overlap
- progressed lunation phase
- profection + time lord year
- solar return dominant chapter
- outer planet to luminary/angle/chart ruler milestone

### Level 4 — `major_period`

Örnek:

- Saturn/Jupiter/outer planet exact transit to natal personal planet
- eclipse to natal angle / luminary
- major retro pass over canonical promise line

### Level 3 — `thematic_period`

Örnek:

- Venus retrograde relationship line
- Mars retrograde over natal point
- Mercury retrograde activating 3/6/10 communication-work structure

### Level 2 — `short_wave`

Örnek:

- lunation window
- inner-planet cluster
- station week

### Level 1 — `daily_trigger`

Örnek:

- Moon trigger
- exact daily fast transit
- ingress/station/day delta

## 4.3 Current code nereye denk geliyor?

Bugünkü codebase daha çok:

- Level 4 / 3 / 2 event scoring
- Level 1 daily trigger

karışımı üzerinde çalışıyor.

Level 5 owner eksik.

---

## 5. Data Contract Proposal

## 5.1 Repo convention recommendation

Transit narrative zinciri bugün büyük ölçüde `Mapping[str, Any]` / dict contract taşıyor.  
Bu yüzden ilk güvenli adım:

```text
plain dict contract + validator helper
```

Pydantic/public schema’ya hemen çıkarmak yerine önce internal detector payload’ı yapmak daha güvenli.

## 5.2 Proposed contract

```python
LifeChapter = {
    "version": "life_chapter_v1",
    "chapter_id": str,
    "chapter_type": str,
    "domain": str,
    "spine_line": str | None,
    "time_window": {
        "start": str,
        "peak": str | None,
        "end": str,
    },
    "phase": str,
    "activated_natal_factors": [
        {
            "type": "planet|angle|node|house|ruler|promise",
            "id": str,
        }
    ],
    "core_question": str,
    "selected_meaning": str,
    "evidence": [
        {
            "factor": str,
            "role": str,
            "explanation": str,
        }
    ],
    "suppressed_readings": [
        {
            "reading": str,
            "reason": str,
        }
    ],
    "priority": "life_chapter|major_period|supporting_period",
    "confidence": "low|medium|high",
    "debug": {
        "source_event_ids": list[str],
        "source_signal_types": list[str],
        "phase_reason": str | None,
        "selection_reason": str,
    },
}
```

## 5.3 Why `evidence[]` and `suppressed_readings[]` are mandatory

Astrolog-thinking layer için sistem sadece bunu dememeli:

```text
selected_meaning = speech maturity
```

Ayrıca şunu da demeli:

- neden bunu seçti?
- neden “sibling conflict” seçmedi?
- neden “generic communication stress” seçmedi?

Bu yüzden `suppressed_readings[]` şart.

## 5.4 Worked example shape

```text
chapter_type: saturn_return
selected_meaning: söz ve zihinsel reflekslerin daha seçilmiş, daha sorumlu bir form kazanması
evidence:
- transit Saturn conjunct natal Saturn
- natal Saturn in Aries / 3rd
- South Node overlap in Aries / 3rd
- canonical promise / communication_learning line support
suppressed_readings:
- generic communication difficulty
- direct sibling conflict prediction
```

---

## 6. Integration Proposal — Pipeline Placement

## 6.1 Proposed future pipeline

```text
CanonicalNatalState
-> LifeChapterDetector
-> ActivePeriodChapter
-> PeriodSemanticFocusResolver
-> PeriodVoicePolicy
-> AstrologNarrativeEngine
-> DailyTrigger / TodayStoryCandidate
```

## 6.2 Current code’ye en doğal oturma noktası

Bugünkü route orchestration’a göre en doğal insertion point:

```text
transits.py
```

özellikle:

- raw event engine response üretildikten sonra
- canonical natal state hazır olduktan sonra
- selected events / period_core’dan önce veya en geç hemen sonra

En güvenli sıralama:

```text
raw event engine response
-> canonical natal state
-> LifeChapterDetector
-> select_event_ids / build_period_core consume active chapter
```

Sebep:

- `LifeChapterDetector` raw event rail’i görmeli
- `selection.py` chapter priority bilgisine sahip olmalı
- `period_core` selected chapter owner ile kurulmalı

## 6.3 `PeriodSemanticFocusResolver` input shape nasıl genişler?

Bugün focus resolver dosyası live değil.  
Plan dokümanı var, runtime file yok.

Bu yüzden ileride input şu olur:

```python
{
  "canonical_natal_state": ...,
  "active_life_chapter": {...} | None,
  "selected_period_events": [...],
  "canonical_period_spine": {...},
  "natal_promise_context": {...},
  "hybrid_context_rows": [...],
}
```

Yani semantic focus resolver artık:

- yalnız selected events’e değil
- active chapter’a da bakar

---

## 7. Relation to PeriodSemanticFocusResolver

Worked example üzerinden ayrım:

## 7.1 `LifeChapterDetector` der ki

```text
Saturn return in Aries 3rd is the main chapter.
South Node overlap makes speech/reflex/mental independence the karmic emphasis.
```

Bu layer:

- chapter type
- phase
- priority
- selected high-level meaning

seçer.

## 7.2 `PeriodSemanticFocusResolver` der ki

```text
Bu kişide Koç 3. ev + South Node + natal promise + current support cluster
= eski refleksif konuşma biçiminin olgunlaşması
```

Bu layer:

- placement/sign meaning palette içinden final meaning seçer
- alternatif meaning’leri suppress eder
- evidence listesi üretir

## 7.3 `PeriodVoicePolicy` der ki

```text
how should this selected meaning be said?
maturation / dense or medium
```

Bu layer artık:

- `what meaning?` değil
- `how say it?`

katmanıdır.

## 7.4 Design recommendation

En doğru ilişki:

```text
LifeChapter feeds SemanticFocus
SemanticFocus feeds VoicePolicy
```

Parallel two-owners modeli daha riskli olur; çatışan selected meaning üretir.

---

## 8. Missing Pieces

| Capability | Status | Notes |
|---|---|---|
| ephemeris support | `yes` | transit positions, house calc, sky events live |
| return detection | `partial_yes` | return subtype detection live, phase model weak |
| return phase detection | `no` | `_phase_from_now()` only returns `active` |
| solar return builder | `yes` | `build_solar_year_theme()` live |
| solar return as period owner | `no` | payload support only |
| nodal activation detection | `partial_yes` | node events and returns exist; no unified chapter owner |
| house/ruler/dispositor access | `yes` | `hybrid_context.py`, natal graph layers |
| canonical natal promise links | `yes` | `canonical_natal_activation.py`, `natal_promise.py` |
| profection calculator | `no` | no runtime impl found |
| time lord logic | `no` | no runtime impl found |
| progressed chart calculator | `partial_placeholder` | model names exist, no period-live implementation |
| progressed Moon / lunation phase | `no` | no live transit-period implementation |
| chart shape / sect / dignity in period reasoning | `no/partial elsewhere` | not live in period selection chain |

---

## 9. Keep / Refactor / Build New

| Module | Decision | Reason |
|---|---|---|
| `transits.py` | `promote` | best orchestration insertion point for chapter detection |
| `calendar_builder.py` | `keep` | marker/calendar generation, not chapter owner |
| `selection.py` | `refactor` | should consume chapter priority, not remain sole period owner |
| `deep_archetype_engine.py` | `refactor` | should summarize under active chapter instead of only selected events |
| `canonical_natal_activation.py` | `keep/promote` | strong input provider for chapter->promise linking |
| `natal_promise.py` | `keep/promote` | key evidence source for chapter meaning |
| `hybrid_context.py` | `keep` | house/ruler/dispositor enrichment source |
| `period_voice_policy.py` | `demote` | should not decide chapter or semantic owner; only how-to-say |
| `astrolog_narrative_engine.py` | `keep` | renderer consumer, not reasoning owner |
| `today_story_candidate.py` | `keep` | later consume active chapter reference |
| `daily_selection.py` | `keep` | still daily trigger selector, later chapter-aware |
| `period_semantic_focus_resolver.py` | `build new` | runtime file missing; planned facade needed |
| `LifeChapterDetector` | `build new` | missing central owner |

Delete candidate bulunmadı; problem eksik owner, fazla dosya değil.

---

## 10. Recommended Roadmap

## PR-A — Signal registry + contract

Scope:

- readonly catalog of available major-cycle signals
- `LifeChapter` contract
- detector input/output doc

Dependencies:

- none

Blocks:

- chapter integration work

Non-goals:

- no selection change
- no renderer change

## PR-B — `LifeChapterDetector` skeleton

Scope:

- detector facade
- no priority override yet
- returns optional `active_life_chapter`

Dependencies:

- PR-A

Blocks:

- semantic focus integration

Non-goals:

- no profection/progression yet

## PR-C — Saturn return + nodal activation detection

Scope:

- Tier 1 chapter types
- overlap weighting
- chapter phase model

Dependencies:

- PR-B

Blocks:

- real astrolog chapter path

Non-goals:

- no annual techniques yet

## PR-D — integrate chapter into `period_core`

Scope:

- chapter outranks generic transit period
- selection consumes active chapter
- period_core stores active chapter reference

Dependencies:

- PR-C

Blocks:

- meaningful semantic focus layering

## PR-E — profection / progressed lunation / solar return expansion

Scope:

- Tier 2 chapter families

Dependencies:

- PR-D

Non-goals:

- not required for first useful chapter-aware period

## PR-F — daily trigger attaches to active chapter

Scope:

- `today_story_candidate`
- `daily_selection`
- daily payload includes active chapter reference

Dependencies:

- PR-D minimum

---

## 11. Tests Recommended

- Saturn return detected when transit Saturn is within configured return threshold of natal Saturn
- Saturn return phase identified as `approaching / first_pass / retrograde_review / final_pass / integrating`
- Saturn return sign/house included in payload
- South Node same sign/house raises relevance or sets overlap flag
- LifeChapter outranks normal transit period in selection priority
- Period without active chapter preserves current behavior
- Daily trigger payload includes active chapter reference
- `selected_meaning` lint guard forbids prediction/outcome claims
- suppressed readings exist when chapter selection is ambiguous

---

## 12. Voice Integration Check Against v4 Reference

## Chart 1 — Capricorn 1st stellium

Could this be `saturn_return`?

- **possible**, if fixture actually carries Saturn-return timing
- **not guaranteed** from the natal signature alone

Interpretation:

- current v4 copy mixes natal structural identity + chapter-like maturation
- this suggests renderer should allow chapter-awareness, but chart alone does not prove `chapter_type = saturn_return`

## Chart 4 — T-square

This is probably **not** a classic life chapter by itself.

More likely:

- structural natal pattern
- activated under a period

Recommended extra taxonomy:

```text
structural_natal_chapter
```

or

```text
persistent_pattern_activation
```

So not every strong period owner must be a time-technique chapter.

## Chart 5 — nodal axis

This likely needs:

- `nodal_return`
- `nodal_activation`

as separate ideas.

Why:

- many important nodal periods are not literal nodal return
- v4 directional reading depends on NN/SN polarity even when return is not exact

Recommended taxonomy addition:

```text
nodal_activation
```

beside `nodal_return`.

---

## PR-4 Relationship — Recommendation

Three paths:

### Path 1 — PR-4 first, LifeChapter later

Pros:

- renderer quality improves immediately
- no delay on voice migration

Cons:

- current chain still misses chapter-first reasoning
- some v4 reference qualities will stay underfed

### Path 2 — LifeChapter first, PR-4 later

Pros:

- cleaner architecture
- renderer receives richer semantic input from day one

Cons:

- much larger delay
- scope explosion risk is real

### Path 3 — Parallel

Pros:

- renderer migration can start on current chain
- chapter work can proceed without blocking voice improvements
- later integration PR can enrich payload without throwing away renderer work

Cons:

- temporary mismatch: renderer becomes better before chapter reasoning catches up

## Technical recommendation

**Recommend Path 3.**

Reason:

```text
PR-4 should proceed as a minimal renderer migration on the current canonical chain,
but it should be implemented in a chapter-ready way.
In parallel, PR-A -> PR-B should start LifeChapter contract/detector work.
Then a later integration PR can feed active chapter into semantic focus and renderer without redoing PR-4.
```

More concretely:

- ship PR-4 against current chain
- do not hardcode assumptions that chapter is absent
- reserve optional `active_life_chapter` slot in future context shape

That is the safest sequencing.

---

## Final Verdict

```text
Period is stronger than before, but still not fully astrolog-thinking at the chapter layer.
The repo has major-cycle signals, but they are side-rail/support signals, not the owner of period reasoning.
The next architecture gap is real: a LifeChapterDetector layer above event selection.
Safest next move is PR-A/PR-B in parallel with PR-4, not instead of PR-4.
```
