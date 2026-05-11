import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:mobile/app/chart/chart_wheel_data.dart';
import 'package:mobile/app/chart/chart_wheel_repository.dart';
import 'package:mobile/app/profile/profile_natal_chart_section.dart';
import 'package:mobile/design/theme/profile_theme_extension.dart';
import 'package:mobile/design/widgets/shou_chart_wheel.dart';

void main() {
  test('chart wheel parser returns null on missing geometry', () {
    final data = ChartWheelData.tryFromChartResponse(<String, dynamic>{
      'angles': {'ascendant': 12.4},
      'planets': {
        'Sun': {'longitude': 10.2, 'sign': 'Aries'},
      },
    });

    expect(data, isNull);
  });

  test('chart wheel payload prefers birth_place and omits city override', () {
    final payload = buildChartWheelPayload(<String, dynamic>{
      'birth_date': '1996-12-28',
      'birth_time': '7:10',
      'place': 'Istanbul, TR',
      'city': 'Istanbul',
      'country': 'TR',
      'timezone': 'Europe/Istanbul',
      'latitude': 41.0082,
      'longitude': 28.9784,
    });

    expect(payload['birth_date'], '1996-12-28');
    expect(payload['birth_time'], '07:10');
    expect(payload['birth_place'], 'Istanbul, TR');
    expect(payload.containsKey('city'), isFalse);
    expect(payload['timezone'], 'Europe/Istanbul');
    expect(payload['latitude'], 41.0082);
    expect(payload['longitude'], 28.9784);
  });

  testWidgets('shou chart wheel renders with minimal fixture data', (
    tester,
  ) async {
    final data = ChartWheelData(
      ascDegree: 281.5,
      mcDegree: 210.2,
      houseCusps: const <double>[
        281.5,
        312.3,
        340.0,
        12.1,
        39.8,
        67.4,
        101.5,
        132.3,
        160.0,
        192.1,
        219.8,
        247.4,
      ],
      planets: <ChartPlanetPoint>[
        ChartPlanetPoint(
          id: 'sun',
          longitude: 276.2,
          sign: 'Capricorn',
          house: 12,
          retrograde: false,
        ),
        ChartPlanetPoint(
          id: 'moon',
          longitude: 129.8,
          sign: 'Leo',
          house: 7,
          retrograde: false,
        ),
        ChartPlanetPoint(
          id: 'mercury',
          longitude: 285.1,
          sign: 'Capricorn',
          house: 1,
          retrograde: true,
        ),
      ],
    );

    await tester.pumpWidget(
      MaterialApp(
        theme: withProfileTheme(ThemeData.light()),
        home: Scaffold(
          body: Center(
            child: SizedBox.square(
              dimension: 260,
              child: ShouChartWheel(data: data),
            ),
          ),
        ),
      ),
    );

    await tester.pump();

    expect(find.byType(ShouChartWheel), findsOneWidget);
    expect(
      find.descendant(
        of: find.byType(ShouChartWheel),
        matching: find.byType(CustomPaint),
      ),
      findsOneWidget,
    );
    expect(tester.takeException(), isNull);
  });

  testWidgets(
    'profile natal chart section shows fallback when data is missing',
    (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: withProfileTheme(ThemeData.light()),
          home: const Scaffold(
            body: ProfileNatalChartSection(
              profile: <String, dynamic>{},
              subtitle: '',
            ),
          ),
        ),
      );

      await tester.pump();

      expect(find.text('Haritalarım'), findsOneWidget);
      expect(find.text('Natal Haritan'), findsOneWidget);
      expect(
        find.text(
          'Natal harita için doğum tarihi, saat ve yer bilgisi gerekiyor.',
        ),
        findsOneWidget,
      );
      expect(tester.takeException(), isNull);
    },
  );
}
