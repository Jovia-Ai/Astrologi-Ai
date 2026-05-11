# Life Chapter Signal Registry

Date: 2026-05-05  
Status: readonly registry  
Scope: current major-cycle signal inventory before `LifeChapterDetector`

## Purpose

Bu doküman mevcut repoda zaten bulunan veya henüz eksik olan life-chapter sinyallerini tek yerde toplar.

Önemli ayrım:

- `signal exists`
- `signal influences scoring`
- `signal is top-level chapter owner`

Bugün hiçbir signal top-level chapter owner değildir.

## Current Signals

| Signal | Status | Current role | Influences scoring? | Is top-level chapter owner? | Notes |
|---|---|---|---|---|---|
| `saturn_return` | `live` | `selection_input` | `yes` | `no` | `astro_event_v2.py` içinde detect ediliyor; structural/chapter rail olarak akıyor. `LifeChapterDetector` bunu artık Tier-1 active chapter adayı olarak emit edebiliyor, ama selection owner hâlâ değil |
| `jupiter_return` | `live` | `selection_input` | `yes` | `no` | return subtype live, period owner değil |
| `nodal_return` | `live` | `selection_input` | `yes` | `no` | subtype live; `LifeChapterDetector` bunu Tier-1 active chapter olarak emit edebiliyor, ama chapter owner değil |
| `nodal_activation` | `partial` | `selection_input` | `partial` | `no` | node-related signals ve overlaps var; `nodal_opposition` ve overlap rail’leri detector içinde Tier-1 activation chapter’a maplenebiliyor |
| `solar_year_frame` | `live` | `payload_side_rail` | `partial` | `no` | annual frame payload’da var, selection owner değil |
| `eclipse_activation` | `live` | `selection_input` | `yes` | `no` | `eclipse_trigger` family üzerinden geliyor |
| `station` | `live` | `selection_input` | `yes` | `no` | station/retro markers scoring’e giriyor |
| `house_ingress` | `live` | `payload_side_rail` | `partial` | `no` | slow-body ingress structural rail’de var |
| `outer_planet_angle_hit` | `partial` | `selection_input` | `partial` | `no` | angle-related weighting ve milestone subtype parçalı olarak var |
| `major_transit_chapter` | `partial` | `selection_input` | `partial` | `no` | milestone-style events var, unified chapter contract yok |
| `structural_natal_pattern` | `partial` | `debug_only` | `no` | `no` | T-square gibi natal structural pattern period owner olarak sınıflanmıyor; future derived source. Bu signal ileride `chapter_type=structural_natal_chapter` üretebilir. Mevcut karar: `excluded_from_PR_D_v1`, future candidate `PR-C.4` |

## Missing Future Sources

| Future source | Status | Current role | Notes |
|---|---|---|---|
| `profection_year` | `missing` | `not_implemented` | annual profection / time-lord logic yok |
| `time_lord` | `missing` | `not_implemented` | profection’e bağlı owner signal yok |
| `progressed_moon` | `missing` | `not_implemented` | progressed Moon period owner olarak yok |
| `progressed_lunation` | `missing` | `not_implemented` | secondary progression / lunation phase yok |
| `solar_return_as_owner` | `missing` | `not_implemented` | `solar_year_frame` var ama chapter owner değil |

## Interpretation Notes

### `live`

Signal runtime’da mevcut ve payload/scoring zincirine bir şekilde giriyor.

### `partial`

Signal’in bazı parçaları var ama henüz:

- unified contract yok
- owner semantics yok
- selection priority yok

### `missing`

Repo search seviyesinde isim/kavram bulunabilir ama transit period reasoning içinde çalışan implementation yok.

## Decision Record

- Bu registry implementation değildir.
- Bu registry priority vermez.
- Bu registry `LifeChapterDetector` yerine geçmez.
- `LifeChapterDetector` artık Tier-1 (`saturn_return`, `nodal_return`, `nodal_activation`) active chapter emission yapabilir.
- Bir sonraki adım selection override değil; daha zengin Tier-1 reasoning ve sonra feature-flag arkasında period-core integration’dır.
- `PR-D v1` planlanırsa scope yalnız Tier-1 owner-ready chapter family’leriyle sınırlı tutulmalıdır:
  - `saturn_return`
  - `nodal_return`
  - `nodal_activation`
- `PR-D v1` scope dışı:
  - `structural_natal_chapter`
  - `profection_year`
  - `progressed_lunation`
  - `solar_return_theme` as owner
  - `outer_planet_angle_hit` until explicitly promoted later
