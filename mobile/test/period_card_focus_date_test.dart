import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/app/timing/narrative_dtos.dart';

void main() {
  test('resolvePeriodCardFocusDate prefers explicit peak date', () {
    final card = PeriodCardDto.fromEventCard(
      eventCard: EventCardDto.fromMap({
        'event_id': 'evt_peak',
        'headline': 'Peak transit',
        'horizon': 'period',
        'timing': {
          'peak_date_utc': '2026-04-11T10:00:00Z',
          'entry_date_utc': '2026-04-09T10:00:00Z',
          'exit_date_utc': '2026-04-14T10:00:00Z',
        },
        'tags': {'phase': 'peak'},
      }),
      index: 0,
    );

    expect(resolvePeriodCardFocusDate(card), DateTime(2026, 4, 11));
  });

  test('resolvePeriodCardFocusDate falls back to exact_in_days', () {
    final card = PeriodCardDto.fromEventCard(
      eventCard: EventCardDto.fromMap({
        'event_id': 'evt_offset',
        'headline': 'Offset transit',
        'horizon': 'period',
        'tags': {'phase': 'applying', 'exact_in_days': 3},
      }),
      index: 0,
    );

    expect(
      resolvePeriodCardFocusDate(
        card,
        fallbackDay: DateTime(2026, 4, 6, 21, 15),
      ),
      DateTime(2026, 4, 9),
    );
  });
}
