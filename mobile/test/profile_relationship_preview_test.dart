import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:mobile/app/api/api_client.dart';
import 'package:mobile/app/tabs/profile_relationship_preview.dart';
import 'package:mobile/app/timing/transit_repositories.dart';
import 'package:mobile/app/timing/turkish_text.dart';

String tr(String value) => normalizeTurkishText(value);

String trUpper(String value) => turkishToUpper(tr(value));

void main() {
  const fakeProfile = <String, dynamic>{
    'birth_date': '1996-12-28',
    'birth_time': '07:10',
    'city': 'Istanbul',
    'country': 'TR',
    'timezone': 'Europe/Istanbul',
  };

  testWidgets(
    'relationship preview renders flowing narrative and prioritizes relationship-heavy long period events',
    (tester) async {
      final repository = _FakeNarrativeRepository(
        _relationshipNarrativePayload(),
      );

      await _pumpHarness(
        tester,
        child: Scaffold(
          body: ProfileRelationshipPreview(
            profile: fakeProfile,
            narrativeRepository: repository,
            selectedDate: DateTime(2026, 4, 3),
          ),
        ),
      );

      await tester.pumpAndSettle();

      expect(repository.lastLens, 'relationship');
      expect(repository.lastFocusedRange, isTrue);
      expect(repository.lastIncludeBestTimes, isFalse);
      expect(repository.lastResponseMode, 'public_only');
      expect(
        repository.lastPayloadProfile,
        TransitPayloadProfile.relationshipPreview,
      );
      expect(
        repository.lastReceiveTimeout,
        ApiClient.timeoutFor(ApiRequestSla.background),
      );

      expect(find.text(trUpper('Bugünü kuran etkiler')), findsOneWidget);
      expect(find.text(trUpper('Altta çalışan dönem')), findsOneWidget);
      expect(find.text(trUpper('Bugünün üst anlamı')), findsOneWidget);

      expect(
        find.textContaining(
          tr(
            'Birine karsi yumusama, yaklasma istegi ve temas etme ihtimali var.',
          ),
        ),
        findsOneWidget,
      );
      expect(
        find.textContaining(
          tr('Yani gunun ozeti: yakinlasma var, ama kesinlik yok.'),
        ),
        findsOneWidget,
      );
      expect(
        find.textContaining(
          tr(
            'Mesaj atma enerjisi var; sonra bir kosede onun analizini yapma enerjisi de var.',
          ),
        ),
        findsOneWidget,
      );
      expect(
        find.text(
          tr(
            'Gunes-Venus ucgeni orta vadeli bir akis ve bugun en guclu yerinde. Birini daha cok dusunmek, mesaj atmanin kolaylasmasi ya da kucuk bir temasin sende daha fazla etki birakmasi gibi calisabilir. Bu haritada yakinlik once icte hissedilir; o yuzden her sey disaridan buyuk gorunmese de his gercek olabilir.',
          ),
        ),
        findsOneWidget,
      );
      expect(
        find.text(
          tr(
            'Jupiter-Merkur karsitligi orta vadeli bir karsitlik ve simdi yukseliyor. Bir yandan konusmak istersin, bir yandan da yanlis anlasilmamak icin kendini tutarsin. Bu kararsizlik degil; ayni anda iki ihtiyacin calistigini gosteriyor.',
          ),
        ),
        findsOneWidget,
      );
      expect(
        find.text(
          tr(
            'Saturn-DSC karesi iliskiyi ciddiyet ve dayanma gucu tarafindan siniyor. Sicaklik varsa bile bunun emek, sureklilik ve sorumluluk tasiyip tasimadigina bakiyorsun. Bu da his yetiyor mu sorusunu daha onemli hale getiriyor.',
          ),
        ),
        findsOneWidget,
      );
      expect(
        find.textContaining(
          tr('Kalp tarafi aciliyor, ama zihnin hemen teslim olmuyor.'),
        ),
        findsOneWidget,
      );

      expect(find.textContaining(tr('Anlami:')), findsNothing);
      expect(find.textContaining(tr('Sende nasil calisiyor:')), findsNothing);
      expect(find.textContaining('arandaki ton'), findsNothing);
      expect(find.textContaining(tr('iliskisel alan')), findsNothing);
      expect(find.textContaining(tr('yer acma')), findsNothing);
      expect(
        find.textContaining(
          tr(
            'Yakinlik istedigin yer ile kendini korudugun yer ayni anda hareket ediyor.',
          ),
        ),
        findsNothing,
      );

      await tester.tap(find.text('Neden bu önemli?'));
      await tester.pumpAndSettle();

      expect(
        find.text(
          tr(
            'Gunes-Venus ucgeni ve Venus-DSC sekstili bugunun ana kisa ve orta vade hattini kuruyor.',
          ),
        ),
        findsOneWidget,
      );
      expect(
        find.text(
          tr(
            'Saturn-DSC karesi ise altta daha uzun sure calisan donemi tasiyor.',
          ),
        ),
        findsOneWidget,
      );
    },
  );

  testWidgets(
    'relationship preview does not inject a playful line on heavy Neptune-Saturn days',
    (tester) async {
      final repository = _FakeNarrativeRepository(_heavyRelationshipPayload());

      await _pumpHarness(
        tester,
        child: Scaffold(
          body: ProfileRelationshipPreview(
            profile: fakeProfile,
            narrativeRepository: repository,
            selectedDate: DateTime(2026, 3, 2),
          ),
        ),
      );

      await tester.pumpAndSettle();

      expect(
        find.text(
          tr(
            'Mesaj atma enerjisi var; sonra bir kosede onun analizini yapma enerjisi de var.',
          ),
        ),
        findsNothing,
      );
      expect(
        find.textContaining(
          tr(
            'Bir sey hissetmek kolay; onu fazla dusunmemek o kadar kolay degil.',
          ),
        ),
        findsNothing,
      );
      expect(find.textContaining(tr('Neptun-DSC karesi')), findsWidgets);
      expect(find.textContaining(tr('Saturn-DSC karesi')), findsWidgets);
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

class _FakeNarrativeRepository extends NarrativeRepository {
  _FakeNarrativeRepository(this.payload);

  final Map<String, dynamic> payload;

  String? lastLens;
  bool? lastFocusedRange;
  bool? lastIncludeBestTimes;
  String? lastResponseMode;
  TransitPayloadProfile? lastPayloadProfile;
  Duration? lastReceiveTimeout;

  @override
  Future<Map<String, dynamic>> fetchDailyNarrative({
    required Map<String, dynamic> profile,
    required DateTime selectedDate,
    String lens = 'general',
    bool focusedRange = false,
    bool includeBestTimes = true,
    String responseMode = 'full',
    String locale = 'tr',
    TransitPayloadProfile payloadProfile = TransitPayloadProfile.full,
    SubscriptionTier? subscriptionTier,
    int? visibleDaysLimit,
    Duration? receiveTimeout,
    ApiRequestSla requestSla = ApiRequestSla.interactive,
  }) async {
    lastLens = lens;
    lastFocusedRange = focusedRange;
    lastIncludeBestTimes = includeBestTimes;
    lastResponseMode = responseMode;
    lastPayloadProfile = payloadProfile;
    lastReceiveTimeout = receiveTimeout;
    return payload;
  }
}

Map<String, dynamic> _relationshipNarrativePayload() {
  return <String, dynamic>{
    'public': <String, dynamic>{
      'daily_event_cards': <Map<String, dynamic>>[
        _card(
          eventId: 'sun-venus',
          feltLineTr: 'Yakinlik su an daha cok icte buyuyor bugun.',
          whyItFeelsThisWayTr:
              'Bunu en cok konusma, mesajlasma ya da niyetini soyleme tarafinda hissedebilirsin.',
          guidanceMicroTr:
              'Yumusayan seyi hemen buyuk bir sonuca cevirmeye calisma.',
          timeHintTr: '3 Nisan civari',
          phase: 'exactish',
          aspect: 'trine',
          transitBody: 'Sun',
          natalPoint: 'Venus',
          bucket: 'medium',
          horizon: 'daily',
          houseTouchpointTr: 'icine cekildigin yerler',
          houseTouchpointHintTr:
              'Tema 12. evde calistigi icin hislerini daha cok icte yasayabilirsin.',
          semanticCore: <String, dynamic>{
            'aspect_mode': 'flow',
            'source_house': 3,
            'source_house_domain': 'mind',
            'target_house': 12,
            'target_house_domain': 'inner',
          },
          domainScores: <String, dynamic>{'relationships': 0.94, 'inner': 0.30},
          lensProjection: <String, dynamic>{
            'lens': 'relationship',
            'primary_domain': 'relationships',
            'projected_scores': <String, dynamic>{'relationships': 1.09},
          },
          timing: <String, dynamic>{
            'entry_date_utc': '2026-03-29',
            'peak_date_utc': '2026-04-03',
            'exit_date_utc': '2026-04-10',
            'timing_note': 'bugun en guclu yerinde',
          },
        ),
        _card(
          eventId: 'jupiter-mercury',
          feltLineTr:
              'Iliskide acilmak isterken ayni anda kendini korumak da isteyebilirsin bugun.',
          whyItFeelsThisWayTr:
              'Karsi tarafin sozu, beklentisi ya da varligi bunu daha gorunur kiliyor.',
          guidanceMicroTr: 'Ilk tepkiyi nihai karar sanma.',
          timeHintTr: '18 Nisan tepesine gidiyor',
          phase: 'applying',
          aspect: 'opposition',
          transitBody: 'Jupiter',
          natalPoint: 'Mercury',
          bucket: 'medium',
          horizon: 'daily',
          houseTouchpointTr: 'kendini ortaya koyma bicimin',
          semanticCore: <String, dynamic>{
            'aspect_mode': 'polarity',
            'source_house': 7,
            'source_house_domain': 'relationships',
            'target_house': 1,
            'target_house_domain': 'identity',
          },
          domainScores: <String, dynamic>{'relationships': 0.36, 'mind': 0.75},
          lensProjection: <String, dynamic>{
            'lens': 'relationship',
            'primary_domain': 'relationships',
            'projected_scores': <String, dynamic>{'relationships': 0.36},
          },
          timing: <String, dynamic>{
            'entry_date_utc': '2026-02-02',
            'peak_date_utc': '2026-04-18',
            'exit_date_utc': '2026-05-28',
            'timing_note': 'simdi yukseliyor',
          },
        ),
      ],
      'period_event_cards': <Map<String, dynamic>>[
        _card(
          eventId: 'generic-period',
          feltLineTr: 'Iliskide kendini yeniden ayarliyorsun.',
          whyItFeelsThisWayTr:
              'Bu donem karsi tarafla yakinlik kurarken kendi sinirlarini da yeniden kuruyorsun.',
          guidanceMicroTr: 'Yeni ayarin nasil oturduguna bak.',
          timeHintTr: 'Nisan boyu aktif',
          phase: 'applying',
          aspect: 'square',
          transitBody: 'Neptune',
          natalPoint: 'Sun',
          bucket: 'long',
          horizon: 'period',
          semanticCore: <String, dynamic>{
            'aspect_mode': 'friction',
            'source_house': 3,
            'source_house_domain': 'mind',
            'target_house': 1,
            'target_house_domain': 'identity',
          },
          domainScores: <String, dynamic>{'relationships': 0.14},
          lensProjection: <String, dynamic>{
            'lens': 'relationship',
            'primary_domain': 'identity',
            'projected_scores': <String, dynamic>{'relationships': 0.14},
          },
        ),
      ],
      'event_cards': <Map<String, dynamic>>[
        _card(
          eventId: 'venus-dsc',
          feltLineTr: 'Iliskide kucuk ama gercek bir alan aciliyor bugun.',
          whyItFeelsThisWayTr:
              'Bunu en cok konusma, mesajlasma ya da niyetini soyleme tarafinda hissedebilirsin.',
          guidanceMicroTr:
              'Yumusayan seyi hemen buyuk bir sonuca cevirmeye calisma.',
          timeHintTr: '3-6 Nisan arasi',
          phase: 'applying',
          aspect: 'sextile',
          transitBody: 'Venus',
          natalPoint: 'Descendant',
          bucket: 'medium',
          horizon: 'daily',
          semanticCore: <String, dynamic>{
            'aspect_mode': 'opening',
            'source_house': 3,
            'source_house_domain': 'mind',
            'target_house': 7,
            'target_house_domain': 'relationships',
          },
          domainScores: <String, dynamic>{'relationships': 1.0},
          lensProjection: <String, dynamic>{
            'lens': 'relationship',
            'primary_domain': 'relationships',
            'projected_scores': <String, dynamic>{'relationships': 1.0},
          },
          timing: <String, dynamic>{'timing_note': 'simdi yukseliyor'},
        ),
        _card(
          eventId: 'saturn-dsc',
          feltLineTr: 'Iliskide temas ve sinir ayni anda surtebilir bugun.',
          whyItFeelsThisWayTr:
              'Karsi tarafla kurdugun denge ciddi bir testten geciyor.',
          guidanceMicroTr: 'Sicaklik kadar tasinabilir olup olmadigina da bak.',
          timeHintTr: 'Nisan boyunca aktif',
          phase: 'separating',
          aspect: 'square',
          transitBody: 'Saturn',
          natalPoint: 'Descendant',
          bucket: 'long',
          horizon: 'period',
          semanticCore: <String, dynamic>{
            'aspect_mode': 'friction',
            'source_house': 3,
            'source_house_domain': 'mind',
            'target_house': 7,
            'target_house_domain': 'relationships',
          },
          domainScores: <String, dynamic>{'relationships': 0.86},
          lensProjection: <String, dynamic>{
            'lens': 'relationship',
            'primary_domain': 'relationships',
            'projected_scores': <String, dynamic>{'relationships': 0.86},
          },
        ),
        _card(
          eventId: 'neptune-dsc',
          feltLineTr: 'Iliskide temas ve sinir ayni anda surtebilir bugun.',
          whyItFeelsThisWayTr:
              'Karsi tarafin niyetini tam okumak kolay olmayabilir.',
          guidanceMicroTr: 'Temasi ve siniri ayni cumlede tutmaya calis.',
          timeHintTr: 'Uzun suredir aktif',
          phase: 'separating',
          aspect: 'square',
          transitBody: 'Neptune',
          natalPoint: 'Descendant',
          bucket: 'long',
          horizon: 'period',
          semanticCore: <String, dynamic>{
            'aspect_mode': 'friction',
            'source_house': 3,
            'source_house_domain': 'mind',
            'target_house': 7,
            'target_house_domain': 'relationships',
          },
          domainScores: <String, dynamic>{'relationships': 0.78},
          lensProjection: <String, dynamic>{
            'lens': 'relationship',
            'primary_domain': 'relationships',
            'projected_scores': <String, dynamic>{'relationships': 0.78},
          },
        ),
        _card(
          eventId: 'southnode-venus',
          feltLineTr: 'Iliskide temas ve sinir ayni anda surtebilir bugun.',
          whyItFeelsThisWayTr: 'Eski kaliplar tekrar gorunur olabilir.',
          guidanceMicroTr: 'Tanik geleni otomatik olarak guvenli sanma.',
          timeHintTr: 'Nisan ortasina kadar aktif',
          phase: 'separating',
          aspect: 'square',
          transitBody: 'South Node',
          natalPoint: 'Venus',
          bucket: 'long',
          horizon: 'period',
          semanticCore: <String, dynamic>{
            'aspect_mode': 'friction',
            'source_house': 3,
            'source_house_domain': 'mind',
            'target_house': 12,
            'target_house_domain': 'inner',
          },
          domainScores: <String, dynamic>{'relationships': 0.32},
          lensProjection: <String, dynamic>{
            'lens': 'relationship',
            'primary_domain': 'relationships',
            'projected_scores': <String, dynamic>{'relationships': 0.32},
          },
        ),
      ],
      'period_core': <String, dynamic>{
        'title': 'Iliski ekseni yeniden kuruyor',
        'core_story':
            'Yakinlik istedigin yer ile kendini korudugun yer ayni anda hareket ediyor.',
        'upper_meaning':
            'Burada asil degisim, iliski icinde kendini nasil konumladigin.',
        'big_picture':
            'Zamanla daha net, daha sakin ve daha dogru bir iliski ayarina gidiyor.',
      },
    },
  };
}

Map<String, dynamic> _heavyRelationshipPayload() {
  return <String, dynamic>{
    'public': <String, dynamic>{
      'daily_event_cards': <Map<String, dynamic>>[
        _card(
          eventId: 'neptune-dsc-daily',
          feltLineTr: 'Iliskide temas ve sinir ayni anda surtebilir bugun.',
          whyItFeelsThisWayTr:
              'Karsi tarafin niyetini tam okumak kolay olmayabilir.',
          guidanceMicroTr: 'Temasi ve siniri ayni cumlede tutmaya calis.',
          timeHintTr: 'Uzun suredir aktif',
          phase: 'separating',
          aspect: 'square',
          transitBody: 'Neptune',
          natalPoint: 'Descendant',
          bucket: 'long',
          horizon: 'daily',
          semanticCore: <String, dynamic>{
            'aspect_mode': 'friction',
            'source_house': 3,
            'source_house_domain': 'mind',
            'target_house': 7,
            'target_house_domain': 'relationships',
          },
          domainScores: <String, dynamic>{'relationships': 0.88},
          lensProjection: <String, dynamic>{
            'lens': 'relationship',
            'primary_domain': 'relationships',
            'projected_scores': <String, dynamic>{'relationships': 0.88},
          },
        ),
      ],
      'period_event_cards': <Map<String, dynamic>>[
        _card(
          eventId: 'saturn-dsc-heavy',
          feltLineTr: 'Iliskide temas ve sinir ayni anda surtebilir bugun.',
          whyItFeelsThisWayTr:
              'Bu donem sicaklik kadar sureklilik de test ediliyor.',
          guidanceMicroTr: 'Tasiyacak omurgaya bak.',
          timeHintTr: 'Nisan boyunca aktif',
          phase: 'separating',
          aspect: 'square',
          transitBody: 'Saturn',
          natalPoint: 'Descendant',
          bucket: 'long',
          horizon: 'period',
          semanticCore: <String, dynamic>{
            'aspect_mode': 'friction',
            'source_house': 3,
            'source_house_domain': 'mind',
            'target_house': 7,
            'target_house_domain': 'relationships',
          },
          domainScores: <String, dynamic>{'relationships': 0.84},
          lensProjection: <String, dynamic>{
            'lens': 'relationship',
            'primary_domain': 'relationships',
            'projected_scores': <String, dynamic>{'relationships': 0.84},
          },
        ),
      ],
      'event_cards': <Map<String, dynamic>>[
        _card(
          eventId: 'neptune-dsc-raw',
          feltLineTr: 'Iliskide temas ve sinir ayni anda surtebilir bugun.',
          whyItFeelsThisWayTr:
              'Karsi tarafin niyetini tam okumak kolay olmayabilir.',
          guidanceMicroTr: 'Temasi ve siniri ayni cumlede tutmaya calis.',
          timeHintTr: 'Uzun suredir aktif',
          phase: 'separating',
          aspect: 'square',
          transitBody: 'Neptune',
          natalPoint: 'Descendant',
          bucket: 'long',
          horizon: 'period',
          semanticCore: <String, dynamic>{
            'aspect_mode': 'friction',
            'source_house': 3,
            'source_house_domain': 'mind',
            'target_house': 7,
            'target_house_domain': 'relationships',
          },
          domainScores: <String, dynamic>{'relationships': 0.88},
          lensProjection: <String, dynamic>{
            'lens': 'relationship',
            'primary_domain': 'relationships',
            'projected_scores': <String, dynamic>{'relationships': 0.88},
          },
        ),
        _card(
          eventId: 'saturn-dsc-raw',
          feltLineTr: 'Iliskide temas ve sinir ayni anda surtebilir bugun.',
          whyItFeelsThisWayTr:
              'Bu donem sicaklik kadar sureklilik de test ediliyor.',
          guidanceMicroTr: 'Tasiyacak omurgaya bak.',
          timeHintTr: 'Nisan boyunca aktif',
          phase: 'separating',
          aspect: 'square',
          transitBody: 'Saturn',
          natalPoint: 'Descendant',
          bucket: 'long',
          horizon: 'period',
          semanticCore: <String, dynamic>{
            'aspect_mode': 'friction',
            'source_house': 3,
            'source_house_domain': 'mind',
            'target_house': 7,
            'target_house_domain': 'relationships',
          },
          domainScores: <String, dynamic>{'relationships': 0.84},
          lensProjection: <String, dynamic>{
            'lens': 'relationship',
            'primary_domain': 'relationships',
            'projected_scores': <String, dynamic>{'relationships': 0.84},
          },
        ),
      ],
      'period_core': <String, dynamic>{
        'core_story':
            'Bu donem iliski tarafinda netlik, sinir ve dayaniklilik ayni anda test ediliyor.',
      },
    },
  };
}

Map<String, dynamic> _card({
  required String eventId,
  required String feltLineTr,
  required String whyItFeelsThisWayTr,
  required String guidanceMicroTr,
  required String timeHintTr,
  required String phase,
  required String aspect,
  required String transitBody,
  required String natalPoint,
  required String bucket,
  required String horizon,
  Map<String, dynamic>? semanticCore,
  Map<String, dynamic>? domainScores,
  Map<String, dynamic>? lensProjection,
  Map<String, dynamic>? timing,
  String houseTouchpointTr = '',
  String houseTouchpointHintTr = '',
}) {
  return <String, dynamic>{
    'event_id': eventId,
    'title': feltLineTr,
    'felt_line_tr': feltLineTr,
    'why_it_feels_this_way_tr': whyItFeelsThisWayTr,
    'guidance_micro_tr': guidanceMicroTr,
    'time_hint_tr': timeHintTr,
    'phase': phase,
    'aspect': aspect,
    'transit_body': transitBody,
    'natal_point': natalPoint,
    'bucket': bucket,
    'horizon': horizon,
    'house_touchpoint_tr': houseTouchpointTr,
    'house_touchpoint_hint_tr': houseTouchpointHintTr,
    'semantic_core': semanticCore ?? <String, dynamic>{},
    'domain_scores': domainScores ?? <String, dynamic>{},
    'lens_projection': lensProjection ?? <String, dynamic>{},
    'timing': timing ?? <String, dynamic>{},
  };
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
