import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/app/timing/narrative_dtos.dart';
import 'package:mobile/app/timing/source_guards.dart';
import 'package:mobile/app/timing/turkish_text.dart';

String tr(String value) => normalizeTurkishText(value);

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
        tr('Sozlerin tonda kayma yarattigi bir donem.'),
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
      expect(periodCards.first.title, tr('Donem karti'));
    });

    test('Daily synthesis parses additive narrative contract fields', () {
      final narrative = NarrativeResponse.fromMap({
        'public': {
          'daily_synthesis': {
            'theme': 'communication_clarity_tension',
            'theme_description':
                'Bugunun agirligi ifade, netlik ve zihinsel akis tarafina dusuyor.',
            'headline': 'Bugun mesele zihnin ve konusma halin.',
            'body':
                'Bugun soylediklerinin tonu daha cabuk buyuyebilir.\n\nSenin yapinda bu tema en hizli zihnin ve konusma halin uzerinden calisiyor.\n\nBu, daha buyuk bir donemin bugune inen yuzu.',
            'guidance': 'Bugun en saglikli yaklasim su: ilk cumleyi netlestir.',
            'sources': {
              'daily': ['evt_1'],
              'period': ['period_core'],
              'natal': ['house_3', 'natal_point_sun'],
            },
          },
        },
      });

      expect(narrative.dailySynthesis, isNotNull);
      expect(
        narrative.dailySynthesis?.theme,
        'communication_clarity_tension',
      );
      expect(
        narrative.dailySynthesis?.headline,
        tr('Bugun mesele zihnin ve konusma halin.'),
      );
      expect(narrative.dailySynthesis?.sources.daily, ['evt_1']);
      expect(narrative.dailySynthesis?.sources.period, ['period_core']);
      expect(
        narrative.dailySynthesis?.sources.natal,
        ['house_3', 'natal_point_sun'],
      );
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
      expect(fromIntent.cards.first.title, tr('Iliski ve Uyum'));
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
        'semantic_core': {
          'target_affinity': 'relationships',
          'target_house_domain': 'inner',
        },
        'domain_scores': {'relationships': 0.81, 'inner': 0.77},
        'lens_projection': {
          'lens': 'relationships',
          'primary_domain': 'relationships',
        },
        'tags': {
          'phase': 'peak',
          'duration': 'months',
          'domain': 'relationships',
        },
      });

      expect(card.title, tr('Netlik Cizgisi'));
      expect(
        card.opening,
        tr('Dogru cumle dogru anda daha cok onem kazaniyor.'),
      );
      expect(
        card.essence,
        tr('Mesele sadece ne soyledigin degil, neyin acik kaldigi.'),
      );
      expect(card.asks, tr('Daha acik ve sakin kurmani istiyor.'));
      expect(card.watchout, tr('Imayla ilerlemek yanlis okumayi artirabilir.'));
      expect(
        card.whatItBuilds,
        tr('Bu donem sende net ifade kasini gelistiriyor.'),
      );
      expect(card.technicalNote, '3. evden 7. eve kare.');
      expect(card.semanticCore['target_affinity'], 'relationships');
      expect(card.domainScores['relationships'], 0.81);
      expect(card.lensProjection['primary_domain'], 'relationships');
    });

    test(
      'NarrativeResponse dedupes repeated transit cards in the same payload',
      () {
        final narrative = NarrativeResponse.fromMap({
          'public': {
            'daily_event_cards': [
              {
                'event_id': 'evt_daily_a',
                'headline': 'Ic ses aciliyor',
                'opening': 'Ayni tema bugunde daha cok hissediliyor.',
                'signature_tr': 'Gunluk vurgu',
                'horizon': 'day',
                'tags': {'phase': 'peak'},
              },
              {
                'event_id': 'evt_daily_b',
                'headline': 'Ic ses aciliyor',
                'opening': 'Ayni tema bugunde daha cok hissediliyor.',
                'signature_tr': 'Gunluk vurgu',
                'horizon': 'day',
                'tags': {'phase': 'peak'},
              },
            ],
            'period_event_cards': [
              {
                'event_id': 'evt_period_a',
                'headline': 'Uzun tema',
                'opening': 'Ayni donem vurgusu burada tekrar ediyor.',
                'signature_tr': 'Donem',
                'horizon': 'period',
                'tags': {'phase': 'peak'},
              },
              {
                'event_id': 'evt_period_b',
                'headline': 'Uzun tema',
                'opening': 'Ayni donem vurgusu burada tekrar ediyor.',
                'signature_tr': 'Donem',
                'horizon': 'period',
                'tags': {'phase': 'peak'},
              },
            ],
            'event_cards': [
              {
                'event_id': 'evt_public_a',
                'headline': 'Ana akis',
                'opening': 'Bu metin listede iki kez donmemeli.',
                'signature_tr': 'Ana vurgu',
                'horizon': 'day',
                'tags': {'phase': 'peak'},
              },
              {
                'event_id': 'evt_public_b',
                'headline': 'Ana akis',
                'opening': 'Bu metin listede iki kez donmemeli.',
                'signature_tr': 'Ana vurgu',
                'horizon': 'day',
                'tags': {'phase': 'peak'},
              },
            ],
          },
        });

        expect(narrative.dailyEventCards, hasLength(1));
        expect(narrative.periodEventCards, hasLength(1));
        expect(narrative.eventCards, hasLength(1));
      },
    );

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
      expect(detail.umbrellaBody, contains(tr('buyuk donem')));
      expect(
        detail.sections
            .firstWhere((section) => section.title == tr('Bu donemin ozu'))
            .body,
        eventCard.essence,
      );
      expect(
        detail.sections
            .firstWhere((section) => section.title == tr('Nasil calisiyor'))
            .body,
        eventCard.mechanism,
      );
      expect(
        detail.sections
            .firstWhere((section) => section.title == tr('Senden ne istiyor'))
            .body,
        eventCard.asks,
      );
      expect(
        detail.sections
            .firstWhere(
              (section) => section.title == tr('Dikkat edilmesi gereken'),
            )
            .body,
        eventCard.watchout,
      );
      expect(
        detail.sections
            .firstWhere(
              (section) => section.title == tr('Sende neyi gelistiriyor'),
            )
            .body,
        tr('Bu donem sende yakin baglarda net kalabilme kasini gelistiriyor.'),
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

    test('Period detail does not repeat timing note in technical rows', () {
      final eventCard = EventCardDto.fromMap({
        'event_id': 'evt_timing_repeat',
        'headline': 'Ton Ayari',
        'opening': 'Iliski tonunda ince ayar gereken bir donem.',
        'essence': 'Mesele ne dediginden cok nasil duyuldugunda aciliyor.',
        'mechanism': 'Yuzeyde kucuk ton farklari buyuyebiliyor.',
        'asks': 'Cumleyi daha acik ve yumusak kurmani istiyor.',
        'watchout': 'Imaya yaslanmak yanlis okumayi buyutebilir.',
        'what_it_builds': 'net ve sakin ifade kasini',
        'technical_note': '3. evden 7. eve kare.',
        'signature_tr': 'Ince ayar',
        'time_hint_tr': 'Mart boyunca',
        'tags': {
          'phase': 'applying',
          'duration': 'months',
          'domain': 'relationships',
        },
      });

      final detail = PeriodCardDto.fromEventCard(
        eventCard: eventCard,
        index: 0,
      ).buildDetailNarrative(periodCore: null, routeSource: 'test');

      expect(detail.timingNote, 'Mart boyunca');
      expect(detail.metaRows.where((row) => row.label == 'Zaman'), isEmpty);
    });
  });
}
