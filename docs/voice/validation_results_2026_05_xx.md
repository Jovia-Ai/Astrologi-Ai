# SHOU Voice vNext — Validation Results 2026-05-XX

## Status

Bu cycle'da insan blind validation çalıştırılmadı.

- Decision date: `2026-05-04`
- Decision authority: `Sahra`
- Reason: `v4 prose target reference directly approved; validation cycle skipped`
- Active reference: [handcrafted_period_validation_v4_final.md](/Users/sahradenizozdogan/Astrologi-Ai/docs/voice/handcrafted_period_validation_v4_final.md)
- Active handoff: [codex_prompt_pr4_renderer_migration.md](/Users/sahradenizozdogan/Astrologi-Ai/docs/voice/codex_prompt_pr4_renderer_migration.md)

Bu dosya artık sonuç girişi bekleyen aktif bir template değil. Arşiv olarak tutulur; ileride başka bir blind validation cycle açılırsa yeniden kullanılabilir.

## Meta

- Historical validation pack source: `removed from active docs/voice cleanup`
- Historical answer key source: `removed from active docs/voice cleanup`
- Decision authority: **Sahra**
- Reviewer count:
- Usable period charts:
- Surface: `period_only_single_variant`

## Reviewer Pack Note

- Reviewer-facing charts are single-variant.
- Reviewer-facing chart labels are neutral (`Chart 1` ... `Chart 5`).
- This template is archived because the blind reviewer cycle was skipped before execution.

## Rating Fields

Per-chart fields:

- `beni_goruyor_score` (`1–5`)
- `generic_horoscope_score` (`1–5`)
- `arkadasa_gonderir_miydin` (`evet / hayır / belki`)
- `akilda_kalan_cumle` (free text)

Skor yönü:

- `beni_goruyor_score`: yüksek daha iyi
- `generic_horoscope_score`: düşük daha iyi

## Minimum Threshold Check

- Minimum reviewer: `5`
- Minimum usable period charts: `4`

Durum:

- Reviewer threshold met:
- Period chart threshold met:

## Decision Thresholds

- Pack succeeds if average `beni_goruyor_score` is strong across charts and `generic_horoscope_score` remains low.
- Secondary signal: `arkadasa_gonderir_miydin = evet/belki` share should be meaningfully above `hayır`.
- Qualitative signal: memorable sentences should cluster around chart-specific lines, not generic mood language.

## Period Summary

### Aggregate

| chart | avg_beni_goruyor | avg_generic_horoscope | evet_share | belki_share | hayir_share | memorable_line_theme |
|---|---:|---:|---:|---:|---:|---|
| Chart 1 |  |  |  |  |  |  |
| Chart 2 |  |  |  |  |  |  |
| Chart 3 |  |  |  |  |  |  |
| Chart 4 |  |  |  |  |  |  |
| Chart 5 |  |  |  |  |  |  |

### Chart-by-Chart Notes

#### Chart 1

- Seen score summary:
- Generic score summary:
- Share intent summary:
- Memorable lines:
- Notes:

#### Chart 2

- Seen score summary:
- Generic score summary:
- Share intent summary:
- Memorable lines:
- Notes:

#### Chart 3

- Seen score summary:
- Generic score summary:
- Share intent summary:
- Memorable lines:
- Notes:

#### Chart 4

- Seen score summary:
- Generic score summary:
- Share intent summary:
- Memorable lines:
- Notes:

#### Chart 5

- Seen score summary:
- Generic score summary:
- Share intent summary:
- Memorable lines:
- Notes:

## Qualitative Findings

### What felt most “This sees me”

- 

### What still felt generic or distant

- 

### Which chart register worked best

- `maturation`
- `release`
- `recognition`
- `dense integration`
- `momentum / self-other`

Notes:

- 

## Scenario Assignment

- Scenario:
- Reason:

Scenarios:

- `A`: Period voice clearly lands; renderer migration can proceed.
- `B`: Meaning is directionally right but prose still fails to land consistently.
- `C`: reserved for later broader validation
- `D`: target voice does not outperform baseline expectations; rescue/rethink needed.
- `E`: mixed by register; some voice families work, others need redesign.

## Final Decision

- Approved by:
- Date:
- Next PR:

## Archive Note

- v3 blind-reviewer flow repo içinde template olarak kalır.
- Bu cycle için reviewer recruitment, facilitation ve synthesis adımları kapatılmıştır.
