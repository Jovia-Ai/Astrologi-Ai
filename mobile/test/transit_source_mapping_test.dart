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
              'headline': 'Sis Perdesi',
              'opening': 'Sozlerin tonda kayma yarattigi bir donem.',
              'essence':
                  'Belirsizlik once iletisimde aciliyor, sonra iliskiye yansiyor.',
              'mechanism':
                  'Gundelik konusmalar once karisiyor, sonra beklentiler bulanabiliyor.',
              'asks': 'Ne demek istedigini daha acik kurman gerekiyor.',
              'watchout': 'Varsayimla ilerlemek yanlis anlamayi buyutebilir.',
              'what_it_builds': 'iliski icinde net kalabilme kasini',
              'technical_note': '3. evden 7. eve yansiyan kare.',
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
      expect(
        PeriodCardDto.fromEventCard(
          eventCard: periodCards.first,
          index: 0,
        ).timeHint,
        'Ince ayar',
      );
      expect(
        periodCards.first.opening,
        'Sozlerin tonda kayma yarattigi bir donem.',
      );
    });

    test('Period summary can parse top-level /transits payload directly', () {
      final narrative = NarrativeResponse.fromMap({
        'period_core': {
          'title': 'Ana Tema',
          'core_story': 'Donemin omurgasi',
          'upper_meaning': 'Buyuk resim',
          'tags': [],
        },
        'event_cards': [
          {
            'event_id': 'evt_period',
            'title': 'Donem karti',
            'headline': 'Donem karti',
            'opening': 'Uzun vadeli bir tema aciliyor.',
            'signature_tr': 'Uzun Vade',
            'teaser': 'teaser',
            'why_now': 'simdi',
            'upper': 'ust',
            'horizon': 'period',
            'tags': {'phase': 'peak'},
          },
        ],
      });

      final periodCards = pickPeriodEventCards(narrative.eventCards);
      expect(narrative.periodCore?.title, 'Ana Tema');
      expect(periodCards, hasLength(1));
      expect(periodCards.first.title, 'Donem karti');
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

    test(
      'Profile/Home period parsing refuses daily event cards as period source',
      () {
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
      },
    );

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

    test('EventCardDto prefers source-of-truth narrative fields', () {
      final card = EventCardDto.fromMap({
        'event_id': 'evt_1',
        'headline': 'Netlik Cizgisi',
        'opening': 'Dogru cumle dogru anda daha cok onem kazaniyor.',
        'essence': 'Mesele sadece ne soyledigin degil, neyin acik kaldigi.',
        'mechanism':
            'Once iletisimde basliyor, sonra iliski dengesine vuruyor.',
        'asks': 'Daha acik ve sakin kurmani istiyor.',
        'watchout': 'Imayla ilerlemek yanlis okumayi artirabilir.',
        'what_it_builds': 'Bu donem sende net ifade kasini gelistiriyor.',
        'technical_note': '3. evden 7. eve kare.',
        'title': 'Legacy title',
        'teaser': 'Legacy teaser',
        'big_picture': 'Legacy big picture',
        'upper': 'Legacy upper',
        'shadow': 'Legacy shadow',
        'watch_out': ['Legacy risk'],
        'tags': {
          'phase': 'peak',
          'duration': 'months',
          'domain': 'relationships',
        },
      });

      expect(card.title, 'Netlik Cizgisi');
      expect(card.opening, 'Dogru cumle dogru anda daha cok onem kazaniyor.');
      expect(
        card.essence,
        'Mesele sadece ne soyledigin degil, neyin acik kaldigi.',
      );
      expect(card.asks, 'Daha acik ve sakin kurmani istiyor.');
      expect(card.watchout, 'Imayla ilerlemek yanlis okumayi artirabilir.');
      expect(
        card.whatItBuilds,
        'Bu donem sende net ifade kasini gelistiriyor.',
      );
      expect(card.technicalNote, '3. evden 7. eve kare.');
    });

    test('Period detail narrative keeps event body separate from umbrella story', () {
      final eventCard = EventCardDto.fromMap({
        'event_id': 'evt_neptune_dsc',
        'headline': 'Beklentiyi Netlestiriyorsun',
        'opening':
            'Bu donemde ayni cümle farkli duyulabilir; iliskide ton hassaslasiyor.',
        'essence':
            'Esas kayma, varsayimla degil acik konuşmayla ilerlemek gerektiginde ortaya cikiyor.',
        'mechanism':
            'Belirsizlik once mesajlarda basliyor, sonra iliski dengesine yansiyor.',
        'asks':
            'Ne hissettigini ve ne bekledigini acik isimlendirmeni istiyor.',
        'watchout':
            'Karsi taraf seni anlar diye varsaymak hayal kirikligini buyutebilir.',
        'what_it_builds':
            'Bu donem sende yakin baglarda net kalabilme kasini gelistiriyor.',
        'technical_note': '3. evden 7. eve kare.',
        'signature_tr': 'Neptun kare DSC',
        'time_hint_tr': 'Mart boyunca',
        'why_now': 'Etki iliski hattinda belirgin.',
        'period_story': {
          'title': 'Kimlikte yeniden ayar',
          'lead':
              'Bu buyuk donem disarida nasil gorundugunu da yeniden dusunduruyor.',
          'big_picture': 'Genel temada kimlik cizgisi yeniden ayarlaniyor.',
          'mechanism': 'Genel hikaye iletisimden kimlige uzaniyor.',
          'upper_meaning': 'daha net secim yapma kasini',
        },
        'tags': {
          'phase': 'applying',
          'duration': 'months',
          'domain': 'relationships',
        },
        'watch_out': ['Imayi uzatma'],
      });

      final card = PeriodCardDto.fromEventCard(eventCard: eventCard, index: 0);
      final detail = card.buildDetailNarrative(
        periodCore: PeriodCoreDto.fromMap({
          'title': 'Ana tema',
          'core_story': 'Bu alan detail bodyye girmemeli.',
          'upper_meaning': 'Bu da girmemeli.',
          'big_picture': 'Ana tema buyuk resmi.',
          'mechanism': 'Ana tema mekanizmasi.',
          'tags': [],
        }),
        routeSource: 'test',
      );

      expect(detail.summary, eventCard.opening);
      expect(detail.umbrellaBody, contains('buyuk donem'));
      expect(
        detail.sections
            .firstWhere((section) => section.title == 'Bu donemin ozu')
            .body,
        eventCard.essence,
      );
      expect(
        detail.sections
            .firstWhere((section) => section.title == 'Nasil calisiyor')
            .body,
        eventCard.mechanism,
      );
      expect(
        detail.sections
            .firstWhere((section) => section.title == 'Senden ne istiyor')
            .body,
        eventCard.asks,
      );
      expect(
        detail.sections
            .firstWhere((section) => section.title == 'Dikkat edilmesi gereken')
            .body,
        eventCard.watchout,
      );
      expect(
        detail.sections
            .firstWhere((section) => section.title == 'Sende neyi gelistiriyor')
            .body,
        'Bu donem sende yakin baglarda net kalabilme kasini gelistiriyor.',
      );
      expect(detail.sectionSources['opening'], 'event.opening');
      expect(detail.sectionSources['umbrella'], 'period_story.lead');
      expect(detail.detailRendererVersion, 'period_detail_v3');
      expect(detail.routeSource, 'test');
      expect(
        detail.sections.every(
          (section) =>
              !section.body.contains('Bu alan detail bodyye girmemeli'),
        ),
        isTrue,
      );
    });
  });
}
