# v0.6 Discovery Metrics Report

Methodology:
- Metrics are from the live current pipeline with `ENABLE_NATAL_PROMISE_PROJECTION_V1=true` and `ENABLE_NATAL_PROMISE_PACKET_DEBUG=true`.
- Mixed normal-case charts use live route-equivalent output compared against the pre-v0.6 snapshots in `/tmp/normal_case_cluster_audits/` for public stability.
- Accepted goldens are marked `stayed stable` based on the passing golden regression suite, because the stored embedded public payloads are older copy-polish snapshots and are not a clean v0.6 comparison baseline.

## Accepted Goldens

### Istanbul 1996
- `candidate_packet_count`: 11
- `unique_candidate_packet_count`: 11
- `public_main/support/detail`: 5 / 0 / 3
- `coverage_warnings`: generic_fallback_public_main
- `missing_domain_flags`: none
- `fallback_public_main_count`: 1
- `non_public_discovery_packet_count`: 0
- `top_discovery_gaps`: none
- `health_score`: 94
- `public output`: stayed stable

### Adana 1998
- `candidate_packet_count`: 22
- `unique_candidate_packet_count`: 22
- `public_main/support/detail`: 5 / 0 / 14
- `coverage_warnings`: generic_fallback_public_main
- `missing_domain_flags`: none
- `fallback_public_main_count`: 5
- `non_public_discovery_packet_count`: 0
- `top_discovery_gaps`: none
- `health_score`: 74
- `public output`: stayed stable

### Istanbul 2020
- `candidate_packet_count`: 13
- `unique_candidate_packet_count`: 13
- `public_main/support/detail`: 4 / 0 / 6
- `coverage_warnings`: generic_fallback_public_main
- `missing_domain_flags`: none
- `fallback_public_main_count`: 3
- `non_public_discovery_packet_count`: 0
- `top_discovery_gaps`: none
- `health_score`: 74
- `public output`: stayed stable

### Izmir 1996
- `candidate_packet_count`: 17
- `unique_candidate_packet_count`: 17
- `public_main/support/detail`: 5 / 0 / 7
- `coverage_warnings`: none
- `missing_domain_flags`: none
- `fallback_public_main_count`: 0
- `non_public_discovery_packet_count`: 0
- `top_discovery_gaps`: none
- `health_score`: 100
- `public output`: stayed stable

### Istanbul 1994
- `candidate_packet_count`: 14
- `unique_candidate_packet_count`: 14
- `public_main/support/detail`: 6 / 2 / 4
- `coverage_warnings`: none
- `missing_domain_flags`: none
- `fallback_public_main_count`: 0
- `non_public_discovery_packet_count`: 0
- `top_discovery_gaps`: none
- `health_score`: 100
- `public output`: stayed stable

### Istanbul 1997
- `candidate_packet_count`: 22
- `unique_candidate_packet_count`: 22
- `public_main/support/detail`: 6 / 6 / 4
- `coverage_warnings`: none
- `missing_domain_flags`: none
- `fallback_public_main_count`: 0
- `non_public_discovery_packet_count`: 0
- `top_discovery_gaps`: none
- `health_score`: 96
- `public output`: stayed stable

## Mixed Normal-Case Batch

### Kutahya 1959
- `candidate_packet_count`: 15
- `unique_candidate_packet_count`: 15
- `public_main/support/detail`: 4 / 0 / 0
- `coverage_warnings`: support_detail_empty, generic_fallback_public_main, mixed_chart_undercovered
- `missing_domain_flags`: none
- `fallback_public_main_count`: 4
- `non_public_discovery_packet_count`: 5
- `top_discovery_gaps`: `axis_2h_8h` (`discovery_axis_2h_8h_gap`)
- `health_score`: 64
- `public output`: stayed stable

### Izmir 1996 normal chart
- `candidate_packet_count`: 12
- `unique_candidate_packet_count`: 12
- `public_main/support/detail`: 2 / 0 / 0
- `coverage_warnings`: support_detail_empty, generic_fallback_public_main, mixed_chart_undercovered
- `missing_domain_flags`: none
- `fallback_public_main_count`: 2
- `non_public_discovery_packet_count`: 9
- `top_discovery_gaps`: `house_12h` (`discovery_house_12h_concentration_gap`); `house_5h` (`discovery_house_5h_concentration_gap`); `axis_2h_8h` (`discovery_axis_2h_8h_gap`); `tight_aspect_relationship` (`discovery_aspect_moon_conjunction_venus_gap`)
- `health_score`: 68
- `public output`: stayed stable

### Izmir 2007
- `candidate_packet_count`: 20
- `unique_candidate_packet_count`: 20
- `public_main/support/detail`: 4 / 0 / 3
- `coverage_warnings`: generic_fallback_public_main, mixed_chart_undercovered
- `missing_domain_flags`: none
- `fallback_public_main_count`: 4
- `non_public_discovery_packet_count`: 7
- `top_discovery_gaps`: `house_4h_ic` (`discovery_house_4h_ic_concentration_gap`); `house_5h` (`discovery_house_5h_concentration_gap`); `axis_3h_9h` (`discovery_axis_3h_9h_gap`); `tight_aspect_emotional_depth` (`discovery_aspect_moon_square_pluto_gap`)
- `health_score`: 70
- `public output`: stayed stable

### Istanbul 2012
- `candidate_packet_count`: 14
- `unique_candidate_packet_count`: 14
- `public_main/support/detail`: 3 / 0 / 0
- `coverage_warnings`: support_detail_empty, generic_fallback_public_main, mixed_chart_undercovered
- `missing_domain_flags`: none
- `fallback_public_main_count`: 2
- `non_public_discovery_packet_count`: 7
- `top_discovery_gaps`: `house_4h_ic` (`discovery_house_4h_ic_concentration_gap`); `axis_2h_8h` (`discovery_axis_2h_8h_gap`); `axis_3h_9h` (`discovery_axis_3h_9h_gap`)
- `health_score`: 70
- `public output`: stayed stable

## Aggregate

- Most common missing domains: none
- Most common discovery gaps: `axis_2h_8h` x3, `house_5h` x2, `house_4h_ic` x2, `axis_3h_9h` x2, `house_12h` x1, `tight_aspect_relationship` x1, `tight_aspect_emotional_depth` x1
- Lowest health scores: Kutahya 1959 (64), Izmir 1996 normal chart (68), Istanbul 2012 (70), Izmir 2007 (70), Adana 1998 (74)
- Charts where generic fallback still owns public_main: Istanbul 1996, Adana 1998, Istanbul 2020, Kutahya 1959, Izmir 1996 normal chart, Izmir 2007, Istanbul 2012
- Top 10 archetype families to consider writing next:
  - `career_route` x4: MC + ruler + 10H public-role family
  - `moon_signature` x4: Moon sign/house/aspect emotional-rhythm family
  - `identity_route` x3: ASC + chart ruler + Sun identity-route family
  - `relationship_route` x3: DSC + ruler + Venus/Mars/Moon relationship-route family
  - `axis_2h_8h` x3: 2H/8H value-sharing axis family
  - `mercury_signature` x2: Mercury + 3H/9H mind-axis family
  - `house_5h` x2: 5H creativity/romance concentration family
  - `house_4h_ic` x2: 4H/IC home-roots concentration family
  - `axis_3h_9h` x2: 3H/9H learning-belief axis family
  - `house_12h` x1: 12H inner-world saturation family

## Readiness

v0.6 is ready for a 50-chart batch audit.
- The accepted golden set remained regression-safe under the focused suite.
- Mixed normal-case charts now expose meaningful non-public discovery candidates and coverage warnings without changing live public output.
- The main remaining issue is not truthfulness but semantic coverage authoring: generic public-main ownership is still high on ordinary charts, especially Kutahya 1959, Izmir 1996 normal chart, Izmir 2007, and Istanbul 2012.
- For a 50-chart batch, the next useful output will be frequency-ranked discovery-topic clustering, not renderer work.
