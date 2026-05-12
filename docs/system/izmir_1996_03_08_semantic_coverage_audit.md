# Izmir 1996-03-08 08:30 Semantic Coverage Audit Packet

- Generated: 2026-05-12
- Chart: `1996-03-08 08:30 Izmir, TR`
- Coordinates used: `38.4237, 27.1428`
- Timezone used: `Europe/Istanbul`
- Projection flags: `ENABLE_NATAL_PROMISE_PROJECTION_V1=true`, `ENABLE_NATAL_PROMISE_PACKET_DEBUG=true`
- Scope: semantic coverage review only. No new semantic implementation in this pass.

## 1. Raw Chart Signature

### Planet Positions

All bodies from the raw natal chart engine:

| Body | Sign | House | Degree |
|---|---|---:|---|
| Venus | Taurus | 12 | 2°26' |
| Vertex | Taurus | 12 | 2°26' |
| Lilith | Cancer | 3 | 18°02' |
| Chiron | Libra | 6 | 12°55' |
| North Node | Libra | 6 | 17°17' |
| Moon | Libra | 6 | 22°00' |
| Pluto | Sagittarius | 7 | 3°07' Rx |
| Fortune | Sagittarius | 8 | 7°23' |
| Jupiter | Capricorn | 9 | 12°54' |
| Neptune | Capricorn | 10 | 27°02' |
| Uranus | Aquarius | 10 | 3°05' |
| Juno | Aquarius | 11 | 23°21' |
| Mercury | Pisces | 11 | 1°16' |
| Mars | Pisces | 12 | 17°11' |
| Sun | Pisces | 12 | 17°58' |
| Saturn | Pisces | 12 | 26°18' |

### ASC / MC / House Cusps

- ASC: `Taurus` at `33.3518°`
- DSC: `Scorpio` at `213.3518°`
- MC: `Capricorn` at `289.2958°`
- IC: `Cancer` at `109.2958°`

House cusps:

| House | Sign | Longitude |
|---|---|---|
| 1 | Taurus | `33.3518°` |
| 2 | Gemini | `64.7123°` |
| 3 | Gemini | `87.7843°` |
| 4 | Cancer | `109.2958°` |
| 5 | Leo | `133.8397°` |
| 6 | Virgo | `167.1702°` |
| 7 | Scorpio | `213.3518°` |
| 8 | Sagittarius | `244.7123°` |
| 9 | Sagittarius | `267.7843°` |
| 10 | Capricorn | `289.2958°` |
| 11 | Aquarius | `313.8397°` |
| 12 | Pisces | `347.1702°` |

### Angle / House Rulers

- Chart ruler:
  - ASC sign `Taurus`
  - ruler `Venus`
  - ruler placement: `Taurus 12H`

- DSC ruler:
  - DSC sign `Scorpio`
  - primary ruler `Mars`
  - primary ruler placement: `Pisces 12H`
  - secondary ruler `Pluto`
  - secondary ruler placement: `Sagittarius 7H`

- MC ruler:
  - MC sign `Capricorn`
  - ruler `Saturn`
  - ruler placement: `Pisces 12H`

- 4H ruler:
  - 4H sign `Cancer`
  - ruler `Moon`
  - ruler placement: `Libra 6H`

### Tight Aspects Under 5°

Planet-to-planet and planet-to-angle aspects within `<= 5°` orb:

- Sun conjunct Mars `0.78°`
- Sun trine Lilith `0.06°`
- Sun sextile MC `1.33°`
- Sun trine IC `1.33°`
- Moon conjunct North Node `4.72°`
- Moon square Lilith `3.97°`
- Moon trine Juno `1.34°`
- Moon square MC `2.70°`
- Moon square IC `2.70°`
- Mercury sextile Venus `1.17°`
- Mercury square Pluto `1.85°`
- Mercury sextile Vertex `1.17°`
- Mercury sextile ASC `2.09°`
- Mercury trine DSC `2.09°`
- Venus square Uranus `0.66°`
- Venus conjunct ASC `0.92°`
- Venus opposite DSC `0.92°`
- Mars sextile Jupiter `4.28°`
- Mars trine Lilith `0.84°`
- Mars sextile MC `2.11°`
- Mars trine IC `2.11°`
- Jupiter square North Node `4.37°`
- Jupiter square Chiron `0.01°`
- Saturn sextile Neptune `0.74°`
- Uranus sextile Pluto `0.02°`
- Uranus square Vertex `0.66°`
- Uranus sextile Fortune `4.29°`
- Uranus square ASC `0.26°`
- Uranus square DSC `0.26°`
- Pluto conjunct Fortune `4.27°`
- North Node square Lilith `0.75°`
- North Node conjunct Chiron `4.36°`
- North Node square MC `2.02°`
- North Node square IC `2.02°`
- Lilith opposite MC `1.27°`
- Lilith conjunct IC `1.27°`
- Vertex conjunct ASC `0.92°`
- Vertex opposite DSC `0.92°`

### Angular Aspects

Tight aspects involving ASC / DSC / MC / IC:

- Sun sextile MC `1.33°`
- Sun trine IC `1.33°`
- Moon square MC `2.70°`
- Moon square IC `2.70°`
- Mercury sextile ASC `2.09°`
- Mercury trine DSC `2.09°`
- Venus conjunct ASC `0.92°`
- Venus opposite DSC `0.92°`
- Mars sextile MC `2.11°`
- Mars trine IC `2.11°`
- Uranus square ASC `0.26°`
- Uranus square DSC `0.26°`
- North Node square MC `2.02°`
- North Node square IC `2.02°`
- Lilith opposite MC `1.27°`
- Lilith conjunct IC `1.27°`
- Vertex conjunct ASC `0.92°`
- Vertex opposite DSC `0.92°`

### Ruler Chains

Using the repo’s current traditional-primary dispositor logic:

- ASC ruler chain
  - start: `Venus in Taurus 12H`
  - chain: `Venus`
  - termination: `domicile`

- DSC ruler chain
  - start: `Mars in Pisces 12H`
  - chain: `Jupiter -> Saturn -> Jupiter`
  - secondary echoes: `Neptune`
  - termination: `loop_detected`

- MC ruler chain
  - start: `Saturn in Pisces 12H`
  - chain: `Jupiter -> Saturn -> Jupiter`
  - secondary echoes: `Neptune`
  - termination: `loop_detected`

- Sun ruler chain
  - start: `Sun in Pisces 12H`
  - chain: `Jupiter -> Saturn -> Jupiter`
  - secondary echoes: `Neptune`
  - termination: `loop_detected`

- Moon ruler chain
  - start: `Moon in Libra 6H`
  - chain: `Venus`
  - termination: `domicile`

### Raw Signature Summary

The strongest raw structural signature is not generic `mind`. It is:

- **very strong 12H emphasis**
  - `Sun 12H Pisces`
  - `Mars 12H Pisces`
  - `Saturn 12H Pisces`
  - `Venus 12H Taurus`
- **Taurus ASC with Venus conjunct ASC from 12H**
- **MC Capricorn with MC ruler Saturn in 12H Pisces**
- **DSC Scorpio with ruler Mars in 12H Pisces**
- **Mercury Pisces 11H square Pluto**

This is a chart of private saturation, invisible preparation, soft-but-intense
relating, and a mind that is both porous and penetrating.

## 2. Current ClusterPlan State

### Candidate Inventory Full List

Current payload count: `10`

Important note:

- this count is inflated by duplicate `_aux` variants
- effective unique debug packet ids are only `7`

Candidate inventory:

1. `career_career_visibility`
   - domain: `career`
   - promise_type: `career_signature`
   - strength: `1.0`
   - anchors: `Satürn · 12. ev · Balık`, `MC Oğlak`, `Satürn 12. ev`
   - direct_meaning: `Perde açılmadan önce içeride uzun bir son prova olur.`

2. `career_career_visibility_aux`
   - domain: `career`
   - promise_type: `career_signature`
   - strength: `1.0`
   - same anchors / same meaning

3. `career_career_visibility_aux`
   - duplicate aux variant

4. `mind_mind_system`
   - domain: `mind`
   - promise_type: `mind_style`
   - strength: `1.0`
   - anchors: `Venüs · 12. ev · Boğa`, `Yükselen Boğa`, `Venüs 12. ev`
   - direct_meaning: `Ne yapacağını bildiğin an tempo kendiliğinden yükselir.`

5. `mind_mind_system_aux`
   - domain: `mind`
   - promise_type: `mind_style`
   - strength: `1.0`

6. `mind_mind_system_aux`
   - duplicate aux variant

7. `relationship_relationships`
   - domain: `relationship`
   - promise_type: `love_style`
   - strength: `1.0`
   - anchors: `Mars · 12. ev · Balık`, `7. ev Akrep`, `Mars 12. ev`
   - direct_meaning: `İnsanlar sende sıcaklıktan önce güven eşiğini hisseder.`

8. `relationship_relationships_aux`
   - domain: `relationship`
   - promise_type: `love_style`
   - strength: `1.0`

9. `relationship_relationships_aux`
   - duplicate aux variant

10. `mercury_square_pluto_deep_mind_pressure_chart_exact`
   - domain: `mind`
   - promise_type: `wound_to_gift`
   - strength: `0.9536`
   - anchors: `Merkür kare Plüton`, `Derin düşünce`
   - direct_meaning: `Zihin yüzeyde kalmak istemez; bir şeyi anlamak istediğinde köküne inene kadar bırakmak zor olabilir.`

### Selected Packets

Selected packet ids:

- `career_career_visibility`
- `mind_mind_system`
- `relationship_relationships`

Selected-set conclusion:

- selected path is still stuck at `3`
- selection is broad-domain minimal, not semantically layered

### Focus Map

| Domain | Score | Tier | Notes |
|---|---:|---|---|
| career | `1.0` | `strong` | boosted by repeated generic career packet family |
| relationship | `1.0` | `strong` | boosted by repeated generic relationship packet family |
| mind | `0.9726` | `strong` | main generic mind packet + Mercury/Pluto detail packet |

What is missing:

- `identity` absent
- `inner_world` / `private_life` / `hidden_maturation` not split out
- `action` absent despite Mars/Sun/Saturn 12H

### Clusters

1. `career_career_like_career_career_visibility`
   - domain: `career`
   - strength: `0.7953`
   - target: `public_main`
   - main_packet_id: `career_career_visibility`
   - members:
     - `career_career_visibility` as `primary_anchor`
     - `career_career_visibility_aux` as `modifier`

2. `mind_mind_like_mind_mind_system`
   - domain: `mind`
   - strength: `0.7893`
   - target: `public_main`
   - main_packet_id: `mind_mind_system`
   - members:
     - `mind_mind_system` as `primary_anchor`
     - `mind_mind_system_aux` as `modifier`

3. `relationship_love_like_relationship_relationships`
   - domain: `relationship`
   - strength: `0.7953`
   - target: `public_main`
   - main_packet_id: `relationship_relationships`
   - members:
     - `relationship_relationships` as `primary_anchor`
     - `relationship_relationships_aux` as `modifier`

4. `mind_wound_like_mercury_square_pluto_deep_mind_pressure_chart_exact`
   - domain: `mind`
   - strength: `0.6426`
   - target: `detail`
   - main_packet_id: `mercury_square_pluto_deep_mind_pressure_chart_exact`

### Public Main / Support / Detail

- public_main:
  - `career_career_like_career_career_visibility`
  - `relationship_love_like_relationship_relationships`
  - `mind_mind_like_mind_mind_system`

- public_support:
  - none

- detail:
  - `mind_wound_like_mercury_square_pluto_deep_mind_pressure_chart_exact`

### Suppressed Packets

Suppressed from main but kept for detail/debug/transit:

- `career_career_visibility_aux`
- `relationship_relationships_aux`
- `mind_mind_system_aux`

### V8 Snapshot

#### hero

- node_id: `promise::mind_mind_system`
- headline: `Ne yapacağını bildiğin an tempo kendiliğinden yükselir.`

#### identity_axis

- eyebrow: `Öne Çıkan Hat`
- node_id: `promise::relationship_relationships`
- headline: `Sen ilişkide yüzeysel bir sıcaklıktan çok, içine oturan bir güven arıyorsun.`

#### insight_strip

1. `Kariyer` → `promise::career_career_visibility`
2. `Zihin` → `promise::mind_mind_system_aux`
3. `İlişki` → `promise::relationship_relationships_aux`

#### differentiators

1. `career_career_visibility_aux`
2. `mercury_square_pluto_deep_mind_pressure_chart_exact`
3. `mind_mind_system`

## 3. Missing Signatures

Below is the gap analysis between the raw chart signature and the current
packet / cluster state.

### A. Taurus ASC + Venus 12H identity / hidden value

Raw chart evidence:

- ASC `Taurus`
- chart ruler `Venus`
- Venus `Taurus 12H`
- Venus conjunct ASC `0.92°`

Current state:

- **under-read / misfiled**
- this signature is being absorbed into `mind_mind_system`
- no identity-family packet or cluster exists

Why this matters:

- this is one of the chart’s clearest signatures
- it should read as identity / magnetism / guarded softness / hidden value
- current system misroutes it as `mind`

### B. Venus Taurus 12H private love / inner beauty / self-worth

Raw chart evidence:

- Venus in domicile
- Venus `12H`
- Venus conjunct ASC
- strong Taurus / private value tone

Current state:

- **missing**
- no dedicated Venus Taurus 12H love/self-worth packet
- no relationship subtype for private affection / hidden tenderness
- no identity subtype for quiet magnetism / inner beauty

### C. MC Capricorn + Saturn Pisces 12H career invisible preparation

Raw chart evidence:

- MC `Capricorn`
- MC ruler `Saturn`
- Saturn `Pisces 12H`
- Sun sextile MC `1.33°`
- Mars sextile MC `2.11°`

Current state:

- **partially read**
- `career_career_visibility` correctly points toward backstage preparation
- but it is still generic and does not fully express:
  - invisible preparation
  - private maturity
  - delayed visibility
  - hidden labor behind authority

### D. Saturn Pisces 12H private maturity / boundary sensitivity

Raw chart evidence:

- Saturn `Pisces 12H`
- MC ruler in 12H
- Saturn sextile Neptune `0.74°`

Current state:

- **missing**
- career packet mentions preparation, but Saturn Pisces 12H itself is not
  surfaced as a semantic line
- no boundary-sensitivity / private burden / silent maturity packet exists

### E. 7H Scorpio + Mars Pisces 12H relationship trust / silent desire / emotional intensity

Raw chart evidence:

- DSC `Scorpio`
- primary ruler `Mars Pisces 12H`
- secondary ruler `Pluto Sagittarius 7H`
- Venus opposite DSC `0.92°`
- strong 12H + Scorpio relating tone

Current state:

- **partially read**
- generic relationship packet does capture `trust threshold`
- but the signature is still under-specified

What is missing semantically:

- silent desire
- private longing
- emotional intensity under softness
- trust-before-exposure architecture
- protective withdrawal when not safe

### F. Mars Pisces 12H hidden action / soft drive

Raw chart evidence:

- Mars `Pisces 12H`
- Sun conjunct Mars `0.78°`
- Mars sextile MC `2.11°`

Current state:

- **missing**
- action/drive is not surfaced as its own packet
- it only appears indirectly inside relationship or career background material

### G. Mercury square Pluto deep mind

Raw chart evidence:

- Mercury `Pisces 11H`
- Pluto `Sagittarius 7H`
- Mercury square Pluto `1.85°`

Current state:

- **present but under-promoted**
- currently only detail:
  - `mercury_square_pluto_deep_mind_pressure_chart_exact`
- this is one of the sharpest exact chart signatures and probably deserves at
  least support-tier status

### H. Strong 12H inner-world signature

Raw chart evidence:

- Sun `12H`
- Mars `12H`
- Saturn `12H`
- Venus `12H`
- DSC ruler `12H`
- MC ruler `12H`

Current state:

- **strongly under-read as a system-level signature**
- current packets distribute it piecemeal:
  - career backstage
  - relationship trust
  - mind tempo
- but there is no packet or cluster that says:
  - intense inner world
  - hidden saturation
  - private processing before expression

## 4. Public Copy Issues

These are secondary to semantic gaps.

### Generic where semantic should be richer

- `career_career_visibility`
  - semantically adjacent but still generic
- `relationship_relationships`
  - closer than before, but still fallback-quality
- `mind_mind_system`
  - semantically misplaced and generic

### Fact-correct but not premium

- current Taurus/Venus mind copy is no longer false, but still reads like a
  fallback template
- examples:
  - `Venüs'ünün 12. evde Boğa'da olması kadar Yükseleninin Boğa olması de...`
  - repeated direct-meaning sentence
  - weak prose cadence

### Repetition / template joins

- `olması de` join bug still exists in current Izmir copy
- direct-meaning line is sometimes repeated twice in the same block
- v8 still reuses main packet families too aggressively

## 5. Proposed v0.5 Needs

Do not implement yet. These are the clearest semantic coverage additions this
chart is asking for.

### Proposed Archetypes / Packets

1. `taurus_asc_venus_12h_hidden_value_identity`
   - identity
   - quiet magnetism, guarded softness, hidden value, slow trust

2. `venus_taurus_12h_private_love_inner_beauty`
   - relationship / identity
   - private affection, inner beauty, love carried inward before expression

3. `mc_capricorn_saturn_12h_invisible_preparation`
   - career
   - backstage authority, invisible rehearsal, maturity before visibility

4. `saturn_pisces_12h_private_maturity_boundary_sensitivity`
   - identity / pressure / resilience
   - quiet burden, porous boundaries, internalized responsibility

5. `scorpio_7h_mars_pisces_12h_trust_threshold`
   - relationship
   - silent desire, protective intensity, trust before full opening

6. `mars_pisces_12h_hidden_action_soft_drive`
   - action / will
   - indirect drive, hidden effort, action after inner saturation

7. `pisces_12h_stellium_inner_world_saturation`
   - identity / inner world / pressure
   - private processing, saturation, psychic permeability

8. `mercury_pisces_11h_social_intuition_mind`
   - mind
   - intuitive social reading, ambient signal pickup, emotional context sensing

9. `venus_conjunct_asc_taurus_soft_presence`
   - identity / social presence
   - warm first impression, understated attractiveness, tactile calm

10. `uranus_square_asc_unsettled_outer_signal`
    - detail / modifier
    - controlled exterior with sudden irregular outer signal

### Expected Focus Map If v0.5 Coverage Lands Well

Expected healthy reading for this chart:

- `identity`: `strong` or high `medium_strong`
- `career`: `medium_strong` to `strong`
- `relationship`: `medium_strong` to `strong`
- `mind`: `medium_strong`
- `inner_world / pressure / hidden_action`: `supporting` or `medium_strong`

### Expected Public Surface Direction

Likely better public-main set after v0.5:

- identity:
  - Taurus ASC + Venus 12H hidden-value signature
- career:
  - MC Capricorn + Saturn 12H invisible preparation
- relationship:
  - 7H Scorpio + Mars Pisces 12H trust-threshold / silent desire
- mind:
  - Mercury Pisces 11H social-intuition mind
- detail/support:
  - Mercury square Pluto deep mind
  - Saturn Pisces 12H private maturity
  - 12H stellium inner-world saturation

## Verdict

This chart is not asking for more tuning on the current generic packets.
It is asking for **new semantic coverage in v0.5**.

The current system can now avoid lying about the chart.
But it still does not really **read** the chart.
