import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/app/timing/transit_repositories.dart';

void main() {
  test(
    'buildNarrativePayload includes known birth and transit coordinates',
    () {
      final profile = <String, dynamic>{
        'birth_date': '1996-12-28',
        'birth_time': '07:10',
        'place': 'Istanbul, Turkey',
        'timezone': 'Europe/Istanbul',
        'latitude': 41.0082,
        'longitude': 28.9784,
      };

      final payload = TransitRequestBuilder.buildNarrativePayload(
        profile: profile,
        selectedDate: DateTime(2026, 4, 6),
        payloadProfile: TransitPayloadProfile.home,
      );

      expect(payload['birth_latitude'], 41.0082);
      expect(payload['birth_longitude'], 28.9784);
      expect(payload['birth_timezone'], 'Europe/Istanbul');
      expect(payload['transit_latitude'], 41.0082);
      expect(payload['transit_longitude'], 28.9784);
      expect(payload['transit_timezone'], 'Europe/Istanbul');
    },
  );

  test('buildCalendarQuery includes known coordinates', () {
    final profile = <String, dynamic>{
      'birth_date': '1996-12-28',
      'birth_time': '07:10',
      'city': 'Istanbul',
      'country': 'Turkey',
      'timezone': 'Europe/Istanbul',
      'latitude': '41.0082',
      'longitude': '28.9784',
    };

    final query = TransitRequestBuilder.buildCalendarQuery(
      profile: profile,
      focusedDate: DateTime(2026, 4, 6),
    );

    expect(query['birth_latitude'], 41.0082);
    expect(query['birth_longitude'], 28.9784);
    expect(query['transit_latitude'], 41.0082);
    expect(query['transit_longitude'], 28.9784);
    expect(query['birth_timezone'], 'Europe/Istanbul');
    expect(query['transit_timezone'], 'Europe/Istanbul');
  });
}
