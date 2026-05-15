# Istanbul 1994-06-25 10:00 ClusterPlan Audit

- Generated: 2026-05-12
- Birth data: `1994-06-25 10:00`, `Istanbul, TR`
- Ground truth for audit: the user-provided corrected chart signature, cross-checked against the repo's live local chart computation
- Build path used for current-state readout: `compute_natal_chart(...)` plus `interpret_natal_chart_ui(..., include_full_profile=true)` plus `build_public_natal_view(...)`
- Flags: `ENABLE_NATAL_PROMISE_PROJECTION_V1=true`, `ENABLE_NATAL_PROMISE_PACKET_DEBUG=true`
- Scope: analysis only, no code changes

## 1. Raw chart signature

The repo's live local chart computation matches the corrected chart frame closely:

- `ASC Leo 26°17′` (`user target: 26°15′`)
- `MC Taurus 19°37′` (`user target: 19°35′`)
- `DSC Aquarius 26°17′`
- `IC Scorpio 19°37′`

### Planet positions

| Planet | Sign | House | Approx degree in sign |
|---|---|---:|---:|
| Sun | Cancer | 11 | `3°` |
| Mercury | Cancer | 11 | `3°` |
| Moon | Capricorn | 5 | `27°` |
| Venus | Leo | 12 | `11°` |
| Mars | Taurus | 10 | `23°` |
| Jupiter | Scorpio | 3 | `4°` |
| Saturn | Pisces | 7 | `12°` |
| Uranus | Capricorn | 5 | `25°` |
| Neptune | Capricorn | 5 | `22°` |
| Pluto | Scorpio | 4 | `25°` |
| North Node | Scorpio | 4 | `23°` |
| Chiron | Virgo | 1 | `5°` |

### House cusps

| House | Cusp |
|---|---|
| 1 | Leo `26°17′` |
| 2 | Virgo `18°50′` |
| 3 | Libra `16°34′` |
| 4 | Scorpio `19°37′` |
| 5 | Sagittarius `24°58′` |
| 6 | Capricorn `27°48′` |
| 7 | Aquarius `26°17′` |
| 8 | Pisces `18°50′` |
| 9 | Aries `16°34′` |
| 10 | Taurus `19°37′` |
| 11 | Gemini `24°58′` |
| 12 | Cancer `27°48′` |

### Ruler routes

- Chart ruler route: `ASC Leo -> Sun -> Cancer 11H`
- DSC ruler route:
  - classical/main runtime route: `DSC Aquarius -> Saturn -> Pisces 7H`
  - modern modifier: `Aquarius -> Uranus -> Capricorn 5H`
- MC ruler route: `MC Taurus -> Venus -> Leo 12H`
- IC / 4H ruler route:
  - classical route: `IC Scorpio -> Mars -> Taurus 10H`
  - modern/depth route: `IC Scorpio -> Pluto -> Scorpio 4H`

### Tight aspects under 5°

- `Sun conjunct Mercury` `0.18°`
- `Sun trine Jupiter` `1.33°`
- `Sun sextile Chiron` `1.96°`
- `Moon trine Mars` `3.78°`
- `Moon conjunct Uranus` `2.38°`
- `Moon sextile Pluto` `1.87°`
- `Moon sextile North Node` `4.42°`
- `Mercury trine Jupiter` `1.15°`
- `Mercury sextile Chiron` `1.78°`
- `Mars trine Uranus` `1.40°`
- `Mars trine Neptune` `1.34°`
- `Mars opposite Pluto` `1.91°`
- `Mars opposite North Node` `0.64°`
- `Mars square ASC / DSC` `2.48°`
- `Mars conjunct MC / opposite IC` `4.19°`
- `Uranus conjunct Neptune` `2.74°`
- `Uranus sextile Pluto` `0.51°`
- `Uranus sextile North Node` `2.04°`
- `Neptune sextile Pluto` `3.25°`
- `Neptune sextile North Node` `0.70°`
- `Neptune trine MC / sextile IC` `2.85°`
- `Pluto conjunct North Node` `2.55°`
- `Pluto square ASC / DSC` `0.57°`
- `North Node square ASC / DSC` `3.12°`
- `North Node opposite MC / conjunct IC` `3.55°`
- `Jupiter sextile Chiron` `0.63°`

### Angular aspects

- `Mars conjunct MC`
- `Mars opposite IC`
- `Neptune trine MC`
- `Neptune sextile IC`
- `Pluto conjunct IC` by sign/house emphasis, plus `Node conjunct IC` by orb
- `Pluto / Node square ASC`
- `Mars square ASC`

### Strongest repeated chart signatures

1. `Leo ASC -> Sun Cancer 11H`
   - warm outer signal, belonging, social-emotional visibility, identity through group context
2. `MC Taurus + Mars Taurus 10H`
   - visible action, steady public drive, controlled but forceful vocational push
3. `Pluto + North Node Scorpio 4H`
   - roots, home, inner security, deep emotional inheritance and transformation
4. `Moon Capricorn 5H + Uranus/Neptune 5H`
   - structured feeling, controlled creativity, emotionally defended imagination, unusual/private expressive life
5. `Venus Leo 12H + MC ruler in 12H`
   - hidden value, private pride, backstage artistry, unseen romantic or aesthetic signature
6. `Aquarius DSC + Saturn Pisces 7H`
   - relationship needs mixing freedom, boundary sensitivity, seriousness and soft permeability
7. `Mars opposite Pluto` plus `ASC/IC/MC involvement`
   - public power tension, control vs action, pressure carrying into visibility and roots

## 2. Current ClusterPlan state

### Candidate inventory

Current candidate inventory count: **9**. It is entirely generic.

1. `career_career_visibility`
2. `career_career_visibility_aux`
3. `career_career_visibility_aux`
4. `mind_mind_system`
5. `mind_mind_system_aux`
6. `mind_mind_system_aux`
7. `relationship_relationships`
8. `relationship_relationships_aux`
9. `relationship_relationships_aux`

Read:

- No chart-exact packet fired.
- No v0.4/v0.5 archetype-style packet fired.
- The system is reading only generic section/thread packets.

### Selected packets

Selected count: **3**

1. `career_career_visibility`
2. `mind_mind_system`
3. `relationship_relationships`

### Focus map

| domain | score | tier | read |
|---|---:|---|---|
| `mind` | `1.0000` | `strong` | driven only by generic `mind_mind_system` |
| `relationship` | `1.0000` | `strong` | driven only by generic `relationship_relationships` |
| `career` | `0.9727` | `strong` | driven only by generic `career_career_visibility` |

Notably absent:

- `identity`
- `inner_world`
- `home`
- `creativity`
- `emotion`

### Clusters

#### `public_main`

1. `mind_mind_like_mind_mind_system`
   - main packet: `mind_mind_system`
2. `relationship_love_like_relationship_relationships`
   - main packet: `relationship_relationships`
3. `career_wound_like_career_career_visibility`
   - main packet: `career_career_visibility`

#### `public_support`

- none

#### `detail`

- none

### Suppressed packets

1. `mind_mind_system_aux`
   - suppressed as weaker duplicate of `mind_mind_system`
2. `relationship_relationships_aux`
   - suppressed as weaker duplicate of `relationship_relationships`
3. `career_career_visibility_aux`
   - suppressed as weaker duplicate of `career_career_visibility`

### Public surfaces

#### `profile_narrative_projection_v1` core

1. `promise::mind_mind_system`
   - headline: `Yükselen.`
2. `promise::relationship_relationships`
   - headline: `Sen ilişkide yüzeysel bir sıcaklıktan çok, içine oturan bir güven arıyorsun.`
3. `promise::career_career_visibility`
   - headline: `İçinde yerine oturmayan şeyi dışarı taşımak istemezsin.`

There are **no extra blocks**.

#### `profile_v8_projection_v1`

- hero:
  - node: `promise::mind_mind_system`
  - headline: `Yükselen.`
- identity_axis:
  - eyebrow: `Öne Çıkan Hat`
  - node: `promise::relationship_relationships`
  - headline: `Sen ilişkide yüzeysel bir sıcaklıktan çok, içine oturan bir güven arıyorsun.`
- insight_strip:
  1. `career_career_visibility`
  2. `relationship_relationships_aux`
  3. `mind_mind_system_aux`
- differentiators:
  1. `career_career_visibility_aux`
  2. `mind_mind_system`
  3. `relationship_relationships`

## 3. Missing or under-read signatures

Status key:

- `MISSING`: not surfaced at packet or cluster level
- `UNDER-READ`: partially touched but only through generic fallback
- `PRESENT`: clearly surfaced

### 3.1 Leo ASC + Sun Cancer 11H identity / warm visibility + belonging

Status: **MISSING**

- This should be one of the chart's main identity signatures.
- Instead of identity-family coverage, the system routes `Sun Cancer 11H + Leo ASC` into generic `mind_mind_system`.
- No identity cluster appears anywhere in focus_map or surface plan.

Before-needed note:
- The chart ruler route is loud and central.

After-needed note:
- A future addendum should let this become either `public_main` identity or at minimum support/detail.

### 3.2 Sun-Mercury Cancer 11H social-emotional intelligence

Status: **UNDER-READ**

- The current system notices a generic mind line.
- It does not read `Sun conjunct Mercury` in Cancer/11H as social-emotional intelligence, belonging speech, or feeling-informed group thinking.
- No chart-specific packet exists for this line in current inventory.

### 3.3 Pluto + North Node Scorpio 4H roots / inner security transformation

Status: **MISSING**

- One of the strongest repeated signatures in the chart.
- Completely absent from packets, focus_map and surfaces.
- No `home`, `inner_world`, `roots`, `security`, `family depth`, or transformation cluster exists.

### 3.4 Moon Capricorn 5H + Uranus/Neptune 5H structured imagination / creative-emotional control

Status: **MISSING**

- The chart has a strong `creativity + emotion + control + unusual imagination` pattern.
- Nothing in current ClusterPlan surfaces `5H Capricorn Moon/Uranus/Neptune`.
- No creativity domain exists in current readout.

### 3.5 MC Taurus + Mars Taurus 10H visible drive / steady public action

Status: **UNDER-READ**

- Career is present, but only through generic `career_career_visibility`.
- The strongest chart fact here is not Venus 12H alone; it is `MC Taurus + Mars Taurus 10H near MC`, with visible controlled drive.
- Current career copy does not center Mars near MC at all.

### 3.6 Mars opposite Pluto public power tension

Status: **MISSING**

- This is one of the chart's clearest friction signatures.
- No contradiction/power/control packet appears.
- Neither career nor identity nor home layers carry it.

### 3.7 Aquarius DSC + Saturn Pisces 7H relationship freedom + responsibility + sensitivity

Status: **UNDER-READ**

- The relationship card is fact-correct at anchor level: `Saturn 7H Pisces`, `7H Aquarius`.
- But it remains a generic fallback.
- It does not distinguish:
  - Aquarius-style distance/freedom
  - Saturn/Pisces responsibility + softness
  - trust/sensitivity boundary tension

### 3.8 Venus Leo 12H hidden romantic pride / private love

Status: **MISSING**

- This is central to both love style and the MC ruler route.
- Current system only leaks it sideways into a generic career opener.
- No private-love, hidden pride, backstage heart, or hidden value packet appears.

### 3.9 Jupiter Scorpio 3H deep speech / psychological learning

Status: **MISSING**

- Neither mind nor speech layer reads this.
- The system does not capture deep speech, investigative learning, or emotionally charged cognition.

### 3.10 Chiron Virgo 1H self-correction / visible sensitivity

Status: **MISSING**

- Completely absent.
- No visible-sensitivity, self-editing, embodied correctness, or self-fixing line is present.

### 3.11 Strong 4H / 5H / 12H / roots-creativity-inner-world architecture

Status: **MISSING**

- The chart is not only mind/relationship/career.
- It has a heavy `home + creativity + inner security + private value` architecture.
- Current ClusterPlan does not recognize those domains at all.

## 4. Public copy issues

### 4.1 Chart-fact leaks

No hard false chart-fact leak was found at the level seen in prior P0 cases like Gemini-on-Taurus or Sagittarius-on-Scorpio.

However:

- the hero headline is broken: `Yükselen.`
- multiple bodies use template joins like:
  - `Yükseleninin Aslan olması de`
  - `Kariyer hattının Boğa'da olması de`
- the copy is chart-thin enough that semantic under-read is a bigger problem than outright fact leakage

### 4.2 Generic fallback public_main

This is the main current failure.

- All three public-main cards are generic fallback packets.
- No chart-exact packet wins.
- The chart reads like a generic `mind + relationship + career` profile rather than this specific configuration.

### 4.3 Missing domains

Missing or effectively absent from public readout:

- identity
- home / roots
- inner_world
- creativity
- emotion

That is too much missing structural material for a golden chart.

### 4.4 Empty support/detail

Current support/detail state:

- `public_support`: empty
- `detail`: empty

For a chart with this much specific material, empty support/detail is a major sign of thin candidate coverage.

### 4.5 v8 hero / identity issues

- hero is generic `mind_mind_system`
- identity_axis does not show an identity packet; it falls back honestly to `Öne Çıkan Hat`
- this is not a collapse bug so much as a semantic vacuum

### 4.6 Duplicate headlines / repeated surfaces

- `mind_mind_system` appears as hero and also as differentiator
- `relationship_relationships` appears as identity_axis and differentiator
- `career_career_visibility` appears as insight and differentiator

This creates visible repetition and makes the surface feel thinner than it already is.

### 4.7 Unnatural template joins

Present examples:

- `Yükseleninin Aslan olması de`
- `Kariyer hattının Boğa'da olması de`
- `Yükselen.` as a headline fragment

These are renderer-quality problems, but they are secondary to the larger semantic gap.

## 5. Verdict

### Accepted golden?

**No.**

This chart is not ready to join the accepted golden set.

### Needs P0 truthfulness fix?

**No immediate P0 truthfulness leak** of the Izmir/Gemini type was found.

The current failure is not mainly false chart facts; it is severe under-reading and generic fallback dominance.

### Needs semantic coverage addendum?

**Yes. Strongly.**

This chart needs a new semantic addendum before tuning selection or polishing copy.

### Needs only copy polish?

**No.**

Copy polish alone would not rescue this chart, because the system is not selecting the right semantic material in the first place.

### Suggested next action

Write a new addendum before any renderer or selection pass.

Priority coverage needed:

1. `Leo ASC + Sun/Mercury Cancer 11H` identity + social-emotional intelligence
2. `MC Taurus + Mars Taurus 10H` visible drive / steady public action
3. `Pluto + North Node Scorpio 4H` roots / inner security transformation
4. `Moon Capricorn 5H + Uranus/Neptune 5H` structured imagination / creative-emotional control
5. `Aquarius DSC + Saturn Pisces 7H` freedom + responsibility + sensitivity in relationship
6. `Venus Leo 12H` hidden romantic pride / private love / backstage value
7. `Jupiter Scorpio 3H` deep speech / psychological learning
8. `Chiron Virgo 1H` visible sensitivity / self-correction
9. `Mars opposite Pluto` public power tension

Suggested call after the addendum:

- rerun candidate inventory
- verify identity/home/inner_world/creativity appear
- verify support/detail is no longer empty
- then decide whether selection tuning or copy polish is needed
