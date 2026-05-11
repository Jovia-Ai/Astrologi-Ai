# Period Semantic Focus v1

## Why this layer exists

`PeriodSemanticFocusResolver` makes period meaning ownership explicit before prose is written.

Current period runtime still contains legacy event-first selection and voice-policy seeds. This layer gathers the already-available signals into one compact contract so the renderer can see:

- which meaning won
- why it won
- which evidence anchors support it
- which shallow alternatives were suppressed

## What it owns

- `selected_meaning`
- `meaning_family`
- `primary_domain`
- `secondary_domains`
- `why_this_meaning`
- `evidence`
- `suppressed_meanings`
- `confidence`
- semantic source attribution

## What it does not own

- event selection
- LifeChapter priority override
- final prose wording
- daily reasoning
- timing / best-times logic

## Relationship to LifeChapter

When a high-confidence `active_life_chapter` is present, semantic focus should prefer it as `source="life_chapter"`.

This does **not** make LifeChapter the global period owner yet. It only lets the strongest existing semantic contract participate in the period meaning handoff.

## Relationship to PeriodVoicePolicy

`PeriodVoicePolicy` frames meaning.

`PeriodSemanticFocusResolver` selects meaning.

During PR-SF1, policy still exists for backward compatibility, but it should no longer be the only holder of `meaning_intent`-like ownership.

## Relationship to the renderer

`AstrologNarrativeEngine` should compose from semantic focus when it exists, rather than inventing alternative readings from thin policy or event hints.

PR-SF1 only adds a minimal preference and debug rail. It does not rewrite the renderer.

## Why PR-D waits for this

PR-D changes runtime ownership pressure by letting LifeChapter compete with generic transit period selection.

That should not happen until period runtime has one visible semantic contract connecting:

- chapter / spine / policy signals
- selected meaning ownership
- renderer consumption
