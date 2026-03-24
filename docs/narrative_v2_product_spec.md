# Narrative V2 Product Spec

## Section priority matrix

### Natal section priorities

| Section | Primary | Secondary | Contextual |
|---|---|---|---|
| `hook` | `aspect` | `house` | `ruler` |
| `lived_experience` | `aspect + house` | `ruler` | `motif` |
| `mechanism` | `house + ruler` | `aspect` | `dispositor` |
| `reflex` | `aspect` | `ruler` | `house` |
| `gift` | `aspect` | `house` | `ruler` |
| `growth_edge` | `ruler + aspect` | `house` | `motif` |
| `what_it_builds` | `ruler` | `aspect` | `house` |
| `technical_anchor` | `house + ruler + aspect` | `graph` | `derived` |

Short rule:
- `aspect` = recognition, reflex, gift
- `house` = life scene
- `ruler` = organization, development path

## Data contract v2 draft

### Natal source-of-truth

- `hook`
- `lived_experience`
- `mechanism`
- `reflex`
- `gift`
- `growth_edge`
- `what_it_builds`
- `technical_anchor`

### Transit event source-of-truth

- `headline`
- `opening`
- `essence`
- `mechanism`
- `asks`
- `watchout`
- `what_it_builds`
- `technical_note`

### Period source-of-truth

- `period_opening`
- `big_picture`
- `mechanism`
- `growth_edge`
- `relational_or_life_expression`
- `what_it_builds`
- `technical_note`

## Aspect bundle selector spec

### Goal

Do not surface raw natal aspect lists. Select a few high-value bundles that can drive recognition language.

### Bundle families

- `personal_core_bundle`
- `angle_identity_bundle`
- `emotional_regulation_bundle`
- `mental_style_bundle`
- `relational_pattern_bundle`
- `pressure_growth_bundle`
- `soft_capacity_bundle`
- `contradiction_bundle`

### Scoring dimensions

```text
bundle_score =
  exactness * 0.20 +
  planet_importance * 0.20 +
  angle_or_luminary_weight * 0.15 +
  domain_relevance * 0.15 +
  psychological_recognition * 0.15 +
  motif_resonance * 0.10 +
  repetition_support * 0.05
```

### Selection rules

- Max `3` primary bundles for a natal profile
- Max `1` primary + `1` support bundle per rendered section
- `hook`, `reflex`, `gift` require an aspect bundle
- `mechanism` may use only house/ruler if that section is already specific enough

## Hook family spec

### `sharp`
- Use when recognition is high and the internal contradiction is obvious
- Direct and clear, but not judgmental

### `magnetic`
- Use for depth, intensity, attraction, belonging, power, Pluto/Venus/angle signatures
- Should feel weighted, not theatrical

### `soft_striking`
- Use for sensitivity, subtle defenses, Neptunian and lunar openings
- Gentle entry, deep recognition

### `builder`
- Use for Saturn/Mercury/6th/10th house patterns
- Stable, grounded, developmental

## Fallback rules

- Fallback runs only if the source-of-truth field is empty, removed by dedupe, or fails specificity checks
- Fallback order:
  1. event/natal/period specific field
  2. same-object secondary enrichment
  3. safe local rewrite fallback
  4. minimal generic fallback
- Fallback must never:
  - let period text fill event sections
  - let generic risk override a real event-specific risk
  - let supporting thread override natal primary copy
  - run only for variety
- `watchout` may remain empty if there is no real risk sentence

## Migration map

### Natal

| Old | New |
|---|---|
| `core_story` | `lived_experience` + `mechanism` |
| `core_story_ui.headline` | `hook` |
| `upper_meaning` | `growth_edge` or `what_it_builds` |
| `supporting_threads` | `secondary_contexts` |
| `signature_motifs` | `primary_aspect_bundles` or `secondary_contexts` |

### Transit event

| Old | New |
|---|---|
| `title` | `headline` |
| `teaser` | `opening` |
| `big_picture` | `essence` |
| `why_now` | `mechanism` or `technical_note` |
| `upper` | `asks` |
| `guidance` | `what_it_builds` or support |
| `conflict` | `watchout` |
| `shadow` | `watchout` support |

### Period

| Old | New |
|---|---|
| `lead` | `period_opening` |
| `core_story` | `big_picture` |
| `contribution` | `growth_edge` |
| `upper_meaning` | `what_it_builds` |

