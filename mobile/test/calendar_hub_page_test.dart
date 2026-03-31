import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:mobile/app/tabs/calendar_hub_page.dart';

void main() {
  const fakeProfile = <String, dynamic>{
    'birth_date': '1996-12-28',
    'birth_time': '07:10',
    'city': 'Istanbul',
    'country': 'TR',
    'timezone': 'Europe/Istanbul',
  };

  testWidgets('calendar hub opens the selected day page from month cells', (
    tester,
  ) async {
    final dayCell = find.byKey(
      const ValueKey<String>('calendarDayCell_2026-03-16'),
    );
    await _pumpHarness(
      tester,
      child: CalendarHubPage(
        profileOverride: fakeProfile,
        dataSource: _FakeCalendarDataSource(),
        initialSelectedDay: DateTime(2026, 3, 15),
      ),
    );

    await tester.pumpAndSettle();

    await tester.ensureVisible(dayCell);
    await tester.tap(dayCell, warnIfMissed: false);
    await tester.pumpAndSettle();

    expect(find.text('Kart 16'), findsWidgets);
    expect(
      find.byKey(const ValueKey<String>('calendarDayBack')),
      findsOneWidget,
    );
  });

  testWidgets(
    'day page swipe returns the final selected day back to calendar',
    (tester) async {
      final initialCell = find.byKey(
        const ValueKey<String>('calendarDayCell_2026-03-15'),
      );
      await _pumpHarness(
        tester,
        child: CalendarHubPage(
          profileOverride: fakeProfile,
          dataSource: _FakeCalendarDataSource(),
          initialSelectedDay: DateTime(2026, 3, 15),
        ),
      );

      await tester.pumpAndSettle();

      await tester.ensureVisible(initialCell);
      await tester.tap(initialCell, warnIfMissed: false);
      await tester.pumpAndSettle();

      await tester.fling(find.byType(PageView), const Offset(-1000, 0), 1800);
      await tester.pumpAndSettle();

      expect(find.text('Kart 16'), findsWidgets);

      await tester.tap(find.byKey(const ValueKey<String>('calendarDayBack')));
      await tester.pumpAndSettle();

      expect(find.text('Kart 16'), findsOneWidget);
    },
  );

  testWidgets('profile preview strip selects a day, then opens via CTA', (
    tester,
  ) async {
    await _pumpHarness(
      tester,
      child: Scaffold(
        body: ProfileCalendarPreviewStrip(
          profileOverride: fakeProfile,
          dataSource: _FakeCalendarDataSource(),
          initialDate: DateTime(2026, 3, 15),
        ),
      ),
    );

    await tester.pumpAndSettle();

    await tester.tap(
      find.byKey(const ValueKey<String>('profilePreviewDay_2026-03-17')),
    );
    await tester.pumpAndSettle();

    expect(find.text('Kart 17'), findsWidgets);
    expect(find.byKey(const ValueKey<String>('calendarDayBack')), findsNothing);

    await tester.tap(find.text('Gunu ac').first);
    await tester.pumpAndSettle();

    expect(
      find.byKey(const ValueKey<String>('calendarDayBack')),
      findsOneWidget,
    );
    expect(find.text('Kart 17'), findsWidgets);
  });

  testWidgets(
    'calendar hub switches between month and week while preserving selected day',
    (tester) async {
      await _pumpHarness(
        tester,
        child: CalendarHubPage(
          profileOverride: fakeProfile,
          dataSource: _FakeCalendarDataSource(),
          initialSelectedDay: DateTime(2026, 3, 15),
        ),
      );

      await tester.pumpAndSettle();

      expect(
        find.byKey(const ValueKey<String>('calendarDayCell_2026-03-16')),
        findsOneWidget,
      );

      await tester.tap(find.text('Hafta'));
      await tester.pumpAndSettle();

      expect(
        find.byKey(const ValueKey<String>('calendarDayCell_2026-03-15')),
        findsOneWidget,
      );
      expect(
        find
            .byKey(const ValueKey<String>('calendarDayCell_2026-03-16'))
            .hitTestable(),
        findsNothing,
      );

      await tester.tap(find.text('Ay'));
      await tester.pumpAndSettle();

      expect(
        find.byKey(const ValueKey<String>('calendarDayCell_2026-03-16')),
        findsOneWidget,
      );
    },
  );
}

Future<void> _pumpHarness(WidgetTester tester, {required Widget child}) async {
  tester.view.devicePixelRatio = 1;
  tester.view.physicalSize = const Size(1179, 2556);
  addTearDown(() {
    tester.view.resetPhysicalSize();
    tester.view.resetDevicePixelRatio();
  });
  await tester.pumpWidget(
    DefaultAssetBundle(
      bundle: _FakeSvgAssetBundle(),
      child: MaterialApp(home: child),
    ),
  );
  await tester.pump();
}

class _FakeCalendarDataSource implements CalendarDataSource {
  const _FakeCalendarDataSource();

  @override
  Future<Map<String, dynamic>> fetchBestTimes({
    required Map<String, dynamic> profile,
    required DateTime focusedDate,
  }) async {
    return <String, dynamic>{
      'best_times': <Map<String, dynamic>>[
        <String, dynamic>{'date': '${focusedDate.day} Mart', 'focus': 'Acilis'},
      ],
    };
  }

  @override
  Future<Map<String, dynamic>> fetchCalendar({
    required Map<String, dynamic> profile,
    required DateTime focusedDate,
    String include = 'markers,themes,intent_summary',
  }) async {
    return <String, dynamic>{
      'public': <String, dynamic>{
        'period_core': _periodCoreMap(),
        'markers': <Map<String, dynamic>>[
          <String, dynamic>{
            'id': 'marker-${focusedDate.day}',
            'title': 'Marker ${focusedDate.day}',
            'summary': 'Marker ozeti ${focusedDate.day}',
            'time_hint': 'Aksam',
          },
        ],
      },
    };
  }

  @override
  Future<Map<String, dynamic>> fetchDailyNarrative({
    required Map<String, dynamic> profile,
    required DateTime selectedDate,
  }) async {
    final daysInMonth = DateTime(
      selectedDate.year,
      selectedDate.month + 1,
      0,
    ).day;
    final calendarDays = <Map<String, dynamic>>[
      for (var day = 1; day <= daysInMonth; day++)
        <String, dynamic>{
          'date':
              '${selectedDate.year}-${selectedDate.month.toString().padLeft(2, '0')}-${day.toString().padLeft(2, '0')}',
          'rating': day % 5,
          'heat': day % 3,
          'event_count': 1,
          'signals_count': day.isEven ? 2 : 1,
          'has_signals': true,
          'is_critical': day == 15,
          'labels': <String>['Tema $day', 'Akis $day'],
          'critical_reasons': day == 15
              ? <String>['Yuksek vurgu']
              : const <String>[],
        },
    ];

    return <String, dynamic>{
      'calendar': <String, dynamic>{'days': calendarDays},
      'public': <String, dynamic>{
        'period_core': _periodCoreMap(),
        'timeline': <String, dynamic>{
          'date':
              '${selectedDate.year}-${selectedDate.month.toString().padLeft(2, '0')}-${selectedDate.day.toString().padLeft(2, '0')}',
          'summary': 'Ozet ${selectedDate.day}',
          'lines': <String>['Satir ${selectedDate.day}'],
          'dot_intensity': 2,
        },
        'event_cards': <Map<String, dynamic>>[
          _eventCardMap(selectedDate, horizon: 'day'),
          _eventCardMap(selectedDate, horizon: 'period', prefix: 'Period'),
        ],
      },
    };
  }

  static Map<String, dynamic> _periodCoreMap() {
    return <String, dynamic>{
      'title': 'Uzun donem',
      'core_story': 'Arka planda calisan donem etkisi.',
      'big_picture': 'Buyuk resim aktif.',
      'upper_meaning': 'Ders',
      'mechanism': 'Mekanizma',
      'tags': <Map<String, dynamic>>[],
    };
  }

  static Map<String, dynamic> _eventCardMap(
    DateTime date, {
    required String horizon,
    String prefix = 'Kart',
  }) {
    return <String, dynamic>{
      'event_id': '$horizon-${date.day}',
      'headline': '$prefix ${date.day}',
      'title': '$prefix ${date.day}',
      'opening': 'Acilis ${date.day}',
      'big_picture': 'Buyuk resim ${date.day}',
      'upper': 'Yukari ${date.day}',
      'shadow': 'Golge ${date.day}',
      'what_it_builds': 'Insa ${date.day}',
      'signature_tr': 'Tema ${date.day}',
      'why_now': 'Neden ${date.day}',
      'horizon': horizon,
      'tags': <String, dynamic>{
        'duration': 'Kisa',
        'phase': 'peak',
        'domain': 'genel',
        'intensity': 0.8,
      },
      'timing': <String, dynamic>{},
    };
  }
}

class _FakeSvgAssetBundle extends CachingAssetBundle {
  static const _svg = '''
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">
  <rect width="10" height="10" fill="white"/>
</svg>
''';

  @override
  Future<ByteData> load(String key) async {
    final bytes = Uint8List.fromList(utf8.encode(_svg));
    return ByteData.view(bytes.buffer);
  }
}
