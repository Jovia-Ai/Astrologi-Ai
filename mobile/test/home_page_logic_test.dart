import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/app/tabs/home_page.dart';
import 'package:mobile/app/timing/narrative_dtos.dart';
import 'package:mobile/app/timing/turkish_text.dart';

String tr(String value) => normalizeTurkishText(value);

void main() {
  group('Home transit logic', () {
    test(
      'buildHomeTransitSnapshot uses period_event_cards and promotes transit fallback for home hero',
      () {
        final narrative = NarrativeResponse.fromMap({
          'calendar': {
            'days': [
              {
                'date': '2026-04-02',
                'rating': 2,
                'heat': 2,
                'event_count': 0,
                'signals_count': 1,
                'has_signals': true,
                'is_critical': false,
                'labels': const <String>[],
                'critical_reasons': const <String>[],
                'signal_label_tr': 'Bugün öne çıkan tema bu.',
                'tone_label_tr': 'akiskan',
                'micro_summary_tr': 'Bugün transit teması belirgin.',
              },
            ],
          },
          'public': {
            'period_core': {
              'title': 'Transit Donemi',
              'core_story': 'Transit ana hikayesi',
              'upper_meaning': 'Buyuk akis',
              'big_picture': 'Transit buyuk resmi',
              'mechanism': 'Transit mekanizmasi',
              'tags': [],
            },
            'event_cards': [],
            'daily_event_cards': [],
            'period_event_cards': [
              {
                'event_id': 'evt_period',
                'headline': 'Transit Baslik',
                'opening': 'Transit acilisi',
                'essence': 'Transit ozeti',
                'what_it_builds': 'Transit yonu',
                'signature_tr': 'Transit imza',
                'time_hint_tr': 'Bu hafta',
                'horizon': 'period',
                'tags': {
                  'phase': 'peak',
                  'duration': 'weeks',
                  'domain': 'general',
                },
              },
            ],
          },
        });

        final snapshot = buildHomeTransitSnapshot(
          narrative: narrative,
          today: DateTime(2026, 4, 2),
        );

        expect(snapshot.periodCore?.title, tr('Transit Donemi'));
        expect(snapshot.periodCards, hasLength(1));
        expect(snapshot.periodCards.first.title, tr('Transit Baslik'));
        expect(snapshot.dailyCards, hasLength(1));
        expect(snapshot.dailyCards.first.horizon, 'daily');
        expect(snapshot.dailyCards.first.feltLineTr, tr('Transit Baslik'));
        expect(
          snapshot.dailyCards.first.whyItFeelsThisWayTr,
          tr('Transit acilisi'),
        );
      },
    );

    test(
      'buildHomeDefaultHeroBody prefers transit copy over natal summary',
      () {
        final dailyCard = EventCardDto.fromMap({
          'event_id': 'evt_daily',
          'headline': 'Gunluk Baslik',
          'opening': 'Transit acilisi',
          'essence': 'Transit ozeti',
          'horizon': 'day',
          'tags': {'phase': 'peak'},
        });

        final bodyFromDaily = buildHomeDefaultHeroBody(
          todayDailyCard: dailyCard,
          activeCard: null,
          periodCore: null,
          natalSummary: 'Natal yorum',
          loading: false,
        );

        final bodyFromPeriodCore = buildHomeDefaultHeroBody(
          todayDailyCard: null,
          activeCard: null,
          periodCore: PeriodCoreDto.fromMap({
            'title': 'Donem',
            'core_story': 'Transit donem hikayesi',
            'upper_meaning': 'Yukari',
            'big_picture': 'Buyuk resim',
            'mechanism': 'Mekanizma',
            'tags': [],
          }),
          natalSummary: 'Natal yorum',
          loading: false,
        );

        expect(bodyFromDaily, tr('Transit acilisi'));
        expect(bodyFromPeriodCore, tr('Transit donem hikayesi'));
      },
    );
  });
}
