// FREE-PROFILE-R4B — narrow Free editorial profile adapter + surface tests.
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/app/profile/free_editorial_profile_adapter.dart';
import 'package:mobile/app/profile/free_editorial_profile_view.dart';

Map<String, dynamic> _card({
  required int ordinal,
  required String domain,
  required String planet,
  required String placementType,
  required String primaryKey,
  required String title,
  String summary = 'özet',
  bool withGift = false,
}) {
  return <String, dynamic>{
    'card_id':
        'free.$planet.${placementType == 'planet_sign' ? 'sign' : 'house'}.$primaryKey',
    'ordinal': ordinal,
    'domain': domain,
    'planet': planet,
    'placement_type': placementType,
    'primary_key': primaryKey,
    'asset_id': 'editorial.$planet.x.tr.v1',
    'title': title,
    'summary': summary,
    'content_blocks': <Map<String, dynamic>>[
      {'role': 'recognition', 'text': 'tanıma', 'source_field': 'trait'},
      {'role': 'mechanism', 'text': 'mekanizma', 'source_field': 'drive'},
      {'role': 'tension', 'text': 'gerilim', 'source_field': 'shadow'},
      if (withGift)
        {'role': 'capacity', 'text': 'kapasite', 'source_field': 'gift'},
    ],
    'chips': <Map<String, dynamic>>[
      {'label': planet, 'source': primaryKey},
      {'label': 'X', 'source': primaryKey},
    ],
    'ownership': <String, dynamic>{
      'meaning_owner': 'natal_placement:$primaryKey',
      'expression_owner': 'editorial.$planet.x.tr.v1',
      'presentation_owner': 'free_editorial_profile_v1',
      'status': 'aligned',
    },
  };
}

Map<String, dynamic> _fixtureA() => <String, dynamic>{
  'editorial_profile': {
    'version': 'free_editorial_profile_v1',
    'locale': 'tr-TR',
    'cards': <Map<String, dynamic>>[
      _card(
        ordinal: 0,
        domain: 'identity',
        planet: 'sun',
        placementType: 'planet_sign',
        primaryKey: 'sun_leo',
        title: 'Güneş Aslan',
      ),
      _card(
        ordinal: 1,
        domain: 'identity',
        planet: 'sun',
        placementType: 'planet_house',
        primaryKey: 'sun_house_4',
        title: 'Güneş 4. Ev',
        withGift: true,
      ),
      _card(
        ordinal: 2,
        domain: 'emotion',
        planet: 'moon',
        placementType: 'planet_sign',
        primaryKey: 'moon_gemini',
        title: 'Ay İkizler',
      ),
      _card(
        ordinal: 4,
        domain: 'mind',
        planet: 'mercury',
        placementType: 'planet_sign',
        primaryKey: 'mercury_virgo',
        title: 'Merkür Başak',
      ),
      _card(
        ordinal: 8,
        domain: 'action',
        planet: 'mars',
        placementType: 'planet_sign',
        primaryKey: 'mars_sagittarius',
        title: 'Mars Yay',
      ),
    ],
    'diagnostics': {'missing_keys': <dynamic>[], 'fallback_used': false},
  },
};

Map<String, dynamic> _fixtureBAction() => <String, dynamic>{
  'editorial_profile': {
    'version': 'free_editorial_profile_v1',
    'locale': 'tr-TR',
    'cards': <Map<String, dynamic>>[
      _card(
        ordinal: 8,
        domain: 'action',
        planet: 'mars',
        placementType: 'planet_sign',
        primaryKey: 'mars_virgo',
        title: 'Mars Başak',
      ),
    ],
    'diagnostics': {
      'missing_keys': <dynamic>[
        {'primary_key': 'mars_house_9', 'reason': 'ASSET_NOT_FOUND'},
      ],
      'fallback_used': false,
    },
  },
};

const _adapter = FreeEditorialProfileAdapter();

/// File contents with comment-only lines removed, so source-level token checks
/// test actual code rather than explanatory comments.
String _codeOf(String path) {
  return File(
    path,
  ).readAsLinesSync().where((l) => !l.trimLeft().startsWith('//')).join('\n');
}

void main() {
  test('1. adapter preserves backend order', () {
    final m = _adapter.parse(_fixtureA());
    expect(m.cards.map((c) => c.primaryKey).toList(), [
      'sun_leo',
      'sun_house_4',
      'moon_gemini',
      'mercury_virgo',
      'mars_sagittarius',
    ]);
  });

  test('1b. adapter accepts /interpret/ui public envelope', () {
    final m = _adapter.parse(<String, dynamic>{'public': _fixtureBAction()});
    expect(m.isValid, true);
    expect(m.cards.single.primaryKey, 'mars_virgo');
    expect(m.missingKeys.map((o) => o.primaryKey).toList(), ['mars_house_9']);
  });

  test('2. adapter does not consult legacy fallback fields', () {
    // payload has NO profile_v8 / sections_v2 / supporting_threads
    final m = _adapter.parse(_fixtureA());
    expect(m.isValid, true);
    final src = _codeOf('lib/app/profile/free_editorial_profile_adapter.dart');
    for (final forbidden in [
      'profile_v8',
      'sections_v2',
      'supporting_thread',
      'mock',
    ]) {
      expect(
        src.contains(forbidden),
        false,
        reason: 'adapter must not reference $forbidden',
      );
    }
  });

  test('3. chips stay with their card (no cross-card merge)', () {
    final m = _adapter.parse(_fixtureA());
    for (final c in m.cards) {
      for (final chip in c.chips) {
        expect(chip.source, c.primaryKey);
      }
    }
  });

  test('4. domains contain at most two cards', () {
    final m = _adapter.parse(_fixtureA());
    for (final d in kFreeEditorialDomainOrder) {
      expect(m.cardsForDomain(d).length <= 2, true);
    }
  });

  test('5. missing house card is omitted (no substitute)', () {
    final m = _adapter.parse(_fixtureBAction());
    final action = m.cardsForDomain('action');
    expect(action.length, 1);
    expect(action.first.primaryKey, 'mars_virgo');
    expect(m.missingKeys.map((o) => o.primaryKey).toList(), ['mars_house_9']);
  });

  test('6. no aura badge / no Koruyucu dalga in narrow surface', () {
    final src = _codeOf('lib/app/profile/free_editorial_profile_view.dart');
    expect(src.contains('Koruyucu dalga'), false);
    expect(src.contains('jovia_aura'), false);
    expect(src.contains('JoviaAura'), false);
  });

  test('7. no _splitBodyIntoSlides in narrow surface', () {
    final src = _codeOf('lib/app/profile/free_editorial_profile_view.dart');
    expect(src.contains('_splitBodyIntoSlides'), false);
    expect(src.contains('PageView'), false);
  });

  test('8. detail blocks preserve structured role order', () {
    final m = _adapter.parse(_fixtureA());
    final house = m.cards.firstWhere((c) => c.primaryKey == 'sun_house_4');
    expect(house.orderedBlocks().map((b) => b.role).toList(), [
      'recognition',
      'mechanism',
      'tension',
      'capacity',
    ]);
    final sign = m.cards.firstWhere((c) => c.primaryKey == 'sun_leo');
    expect(sign.orderedBlocks().map((b) => b.role).toList(), [
      'recognition',
      'mechanism',
      'tension',
    ]); // no gift -> no capacity
  });

  test('9. invalid payload produces safe empty state', () {
    expect(_adapter.parse(null).isValid, false);
    expect(_adapter.parse(<String, dynamic>{}).isValid, false);
    expect(
      _adapter.parse(<String, dynamic>{'editorial_profile': 'oops'}).isValid,
      false,
    );
  });

  test('10. adapter exposes no mobile feature flag', () {
    final src = _codeOf('lib/app/profile/free_editorial_profile_adapter.dart');
    expect(src.contains('FREE_EDITORIAL_PROFILE_ENABLED'), false);
    expect(src.contains('kFreeEditorialProfileEnabled'), false);
  });

  testWidgets('widget: renders domains, max two cards, no Koruyucu dalga', (
    tester,
  ) async {
    final m = _adapter.parse(_fixtureA());
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(body: FreeEditorialProfileView(profile: m)),
      ),
    );
    expect(find.text('Güneş Aslan'), findsOneWidget);
    expect(find.text('KİMLİK'), findsOneWidget);
    expect(find.textContaining('Koruyucu dalga'), findsNothing);
    expect(find.text('Detayı aç'), findsWidgets);
  });

  testWidgets('widget: invalid model shows empty state', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: FreeEditorialProfileView(
            profile: FreeEditorialProfileModel.empty,
          ),
        ),
      ),
    );
    expect(find.text('Profil hazırlanıyor.'), findsOneWidget);
  });

  testWidgets('widget: detail renders blocks in order, no page counter', (
    tester,
  ) async {
    final m = _adapter.parse(_fixtureA());
    final house = m.cards.firstWhere((c) => c.primaryKey == 'sun_house_4');
    await tester.pumpWidget(
      MaterialApp(home: FreeEditorialDetailPage(card: house)),
    );
    expect(
      find.byKey(const Key('free-editorial-block-recognition')),
      findsOneWidget,
    );
    expect(
      find.byKey(const Key('free-editorial-block-capacity')),
      findsOneWidget,
    );
    expect(find.textContaining('01/'), findsNothing);
    expect(find.textContaining('02/'), findsNothing);
  });
}
