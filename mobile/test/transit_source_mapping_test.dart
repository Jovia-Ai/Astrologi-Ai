import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/app/timing/narrative_dtos.dart';
import 'package:mobile/app/timing/source_guards.dart';

void main() {
  group('Transit source-of-truth mapping', () {
    test('Daily narrative reads only event cards from narrative contract', () {
      final narrative = NarrativeResponse.fromMap({
        'public': {
          'event_cards': [
            {
              'event_id': 'evt_1',
              'title': 'Neptune square ASC',
              'signature': 'signature',
              'teaser': 'daily teaser',
              'horizon': 'day',
              'why_now': 'why now',
              'upper': 'upper',
              'tags': {'phase': 'peak'},
            },
            {
              'event_id': 'evt_period',
              'title': 'Period card',
              'signature': 'period signature',
              'teaser': 'period teaser',
              'horizon': 'period',
              'tags': {'phase': 'peak'},
            },
          ],
          'period_core': {
            'title': 'Period theme',
            'core_story': 'period story',
            'upper_meaning': 'upper meaning',
            'tags': [],
          },
        },
      });

      expect(narrative.eventCards, hasLength(2));
      final dailyCards = pickDailyEventCards(narrative.eventCards);
      expect(dailyCards, hasLength(1));
      expect(dailyCards.first.signature, 'signature');
      expect(assertDailySource(dailyCards.first), isTrue);
    });

    test('Period narrative reads only period event cards', () {
      final narrative = NarrativeResponse.fromMap({
        'public': {
          'period_core': {
            'title': 'Ana Tema',
            'core_story': 'Uzun dönem hikayesi',
            'upper_meaning': 'Daha büyük çerçeve',
            'tags': [],
          },
          'event_cards': [
            {
              'event_id': 'evt_daily',
              'title': 'Daily only',
              'signature_tr': 'Gunluk imza',
              'teaser': 'Gunluk teaser',
              'horizon': 'day',
              'tags': {'phase': 'peak'},
            },
            {
              'event_id': 'evt_period',
              'title': 'Sis Perdesi',
              'signature_tr': 'Ince ayar',
              'teaser': 'Uzun metin teaser',
              'why_now': 'Neden simdi',
              'upper': 'Ust anlam',
              'horizon': 'period',
              'tags': {'phase': 'peak'},
            },
          ],
        },
      });

      final periodCards = pickPeriodEventCards(narrative.eventCards);
      expect(narrative.periodCore?.title, 'Ana Tema');
      expect(periodCards, hasLength(1));
      expect(periodCards.first.title, 'Sis Perdesi');
      expect(PeriodCardDto.fromEventCard(eventCard: periodCards.first, index: 0).timeHint, 'Ince ayar');
    });

    test('Period calendar keeps markers as support source', () {
      final period = PeriodCalendarDto.fromMap({
        'period_core': {
          'title': 'Ana Tema',
          'core_story': 'Uzun dönem hikayesi',
          'upper_meaning': 'Daha büyük çerçeve',
          'tags': [],
        },
        'markers': [
          {
            'id': 'mk_1',
            'title': 'Hareket ve dönüşüm',
            'summary': 'Marker özeti',
            'time_hint': '3-10 Mart',
          },
        ],
      });

      expect(period.periodCore?.title, 'Ana Tema');
      expect(period.markers, hasLength(1));
      expect(assertPeriodSource(period.markers.first), isTrue);
    });

    test('Profile/Home period parsing refuses daily event cards as period source', () {
      final period = PeriodCalendarDto.fromMap({
        'event_cards': [
          {
            'event_id': 'evt_daily',
            'title': 'Daily only',
            'signature': 'sig',
            'teaser': 'teaser',
            'tags': {'phase': 'peak'},
          },
        ],
      });

      expect(period.cards, isEmpty);
      expect(period.hasWrongSource, isTrue);
    });

    test('Home period cards can fallback from themes and intent summary', () {
      final fromThemes = PeriodCalendarDto.fromMap({
        'themes': [
          {
            'theme_id': 'theme_1',
            'label': 'Yapı',
            'summary': 'Uzun dönem yapı teması',
            'time_hint': 'Bu ay',
          },
        ],
      });
      final fromIntent = PeriodCalendarDto.fromMap({
        'intent_summary': {
          'relationship': {
            'by_date': {
              '2026-03-10': {'score': 0.9, 'rating': 3},
              '2026-03-12': {'score': 0.7, 'rating': 2},
            },
          },
        },
      });

      expect(fromThemes.cards, isNotEmpty);
      expect(fromThemes.cards.first.title, 'Yapı');
      expect(fromIntent.cards, isNotEmpty);
      expect(fromIntent.cards.first.title, 'Iliski ve Uyum');
    });

    test('Source guards reject swapped DTOs', () {
      final periodCard = PeriodCardDto(
        id: 'p1',
        title: 'Period',
        subtitle: 'subtitle',
        timeHint: 'time',
      );

      expect(assertDailySource(periodCard, context: 'test'), isFalse);
      expect(assertPeriodSource('wrong', context: 'test'), isFalse);
    });
  });
}
