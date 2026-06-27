// FREE-PROFILE-R4C — host decision + wiring tests.
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/app/profile/free_editorial_profile_host.dart';

Map<String, dynamic> _cardMap(
  int ord,
  String domain,
  String planet,
  String type,
  String key,
  String title,
) => <String, dynamic>{
  'card_id': 'free.$planet.${type == 'planet_sign' ? 'sign' : 'house'}.$key',
  'ordinal': ord,
  'domain': domain,
  'planet': planet,
  'placement_type': type,
  'primary_key': key,
  'asset_id': 'editorial.$planet.x.tr.v1',
  'title': title,
  'summary': 'özet',
  'content_blocks': <Map<String, dynamic>>[
    {'role': 'recognition', 'text': 'r', 'source_field': 'trait'},
    {'role': 'mechanism', 'text': 'm', 'source_field': 'drive'},
  ],
  'chips': <Map<String, dynamic>>[
    {'label': planet, 'source': key},
  ],
  'ownership': <String, dynamic>{
    'meaning_owner': 'natal_placement:$key',
    'expression_owner': 'editorial.$planet.x.tr.v1',
    'presentation_owner': 'free_editorial_profile_v1',
    'status': 'aligned',
  },
};

Map<String, dynamic> _payloadA() => <String, dynamic>{
  'core_story': 'legacy',
  'profile_v8': {'legacy': true},
  'editorial_profile': {
    'version': 'free_editorial_profile_v1',
    'locale': 'tr-TR',
    'cards': <Map<String, dynamic>>[
      _cardMap(0, 'identity', 'sun', 'planet_sign', 'sun_leo', 'Güneş Aslan'),
      _cardMap(
        1,
        'identity',
        'sun',
        'planet_house',
        'sun_house_4',
        'Güneş 4. Ev',
      ),
      _cardMap(
        2,
        'emotion',
        'moon',
        'planet_sign',
        'moon_gemini',
        'Ay İkizler',
      ),
    ],
    'diagnostics': {'missing_keys': <dynamic>[], 'fallback_used': false},
  },
};

Map<String, dynamic> _payloadB() => <String, dynamic>{
  'editorial_profile': {
    'version': 'free_editorial_profile_v1',
    'locale': 'tr-TR',
    'cards': <Map<String, dynamic>>[
      _cardMap(
        0,
        'identity',
        'sun',
        'planet_sign',
        'sun_capricorn',
        'Güneş Oğlak',
      ),
    ],
    'diagnostics': {'missing_keys': <dynamic>[], 'fallback_used': false},
  },
};

Map<String, dynamic> _interpretUiEnvelope() => <String, dynamic>{
  'public': _payloadB(),
};

String _codeOf(String path) => File(
  path,
).readAsLinesSync().where((l) => !l.trimLeft().startsWith('//')).join('\n');

void main() {
  test('1. valid payload opens narrow without a mobile flag', () {
    final d = decideFreeEditorialHost(payload: _payloadA());
    expect(d.showNarrow, true);
    expect(d.reason.code, 'EDITORIAL_SHOW');
    expect(d.model.cards.length, 3);
  });

  test('2. absent payload never displays mock', () {
    final d = decideFreeEditorialHost(
      payload: <String, dynamic>{'core_story': 'x'},
    );
    expect(d.showNarrow, false);
    expect(d.reason.code, 'EDITORIAL_PAYLOAD_ABSENT');
    expect(d.model.cards, isEmpty);
  });

  test('3. narrow and legacy never render together', () {
    // decision is exclusive: showNarrow implies a valid model; otherwise host keeps legacy.
    final on = decideFreeEditorialHost(payload: _payloadA());
    expect(on.showNarrow && on.model.isValid, true);
    final absent = decideFreeEditorialHost(
      payload: <String, dynamic>{'profile_v8': true},
    );
    expect(absent.showNarrow, false);
    // host wires a single gated branch
    final host = _codeOf('lib/app/tabs/profile_page.dart');
    expect(host.contains('freeEditorialDecision.showNarrow'), true);
    expect(host.contains('FreeEditorialProfileView('), true);
  });

  test('4. card order from backend remains unchanged', () {
    final d = decideFreeEditorialHost(payload: _payloadA());
    expect(d.model.cards.map((c) => c.primaryKey).toList(), [
      'sun_leo',
      'sun_house_4',
      'moon_gemini',
    ]);
  });

  test('5. user/profile change replaces the card set', () {
    final a = decideFreeEditorialHost(payload: _payloadA());
    final b = decideFreeEditorialHost(payload: _payloadB());
    expect(
      a.model.cards.map((c) => c.primaryKey).toList(),
      isNot(equals(b.model.cards.map((c) => c.primaryKey).toList())),
    );
    expect(b.model.cards.single.primaryKey, 'sun_capricorn');
  });

  test('6. stale cards from previous profile are not retained', () {
    // payload nulled on profile change/error -> no prior cards survive
    final cleared = decideFreeEditorialHost(payload: null);
    expect(cleared.showNarrow, false);
    expect(cleared.model.cards, isEmpty);
    expect(cleared.reason.code, 'EDITORIAL_PAYLOAD_ABSENT');
  });

  test('7. malformed payload produces the safe state', () {
    final bad1 = decideFreeEditorialHost(
      payload: <String, dynamic>{'editorial_profile': 'oops'},
    );
    expect(bad1.showNarrow, false);
    expect(bad1.reason.code, 'EDITORIAL_PAYLOAD_INVALID');
    final bad2 = decideFreeEditorialHost(
      payload: <String, dynamic>{
        'editorial_profile': {'version': 'x'},
      },
    );
    expect(bad2.reason.code, 'EDITORIAL_PAYLOAD_INVALID');
    final empty = decideFreeEditorialHost(
      payload: <String, dynamic>{
        'editorial_profile': {'cards': <dynamic>[]},
      },
    );
    expect(empty.reason.code, 'EDITORIAL_CARDS_EMPTY');
    expect(empty.showNarrow, false);
  });

  test('8. Koruyucu dalga absent from narrow path', () {
    for (final f in [
      'lib/app/profile/free_editorial_profile_host.dart',
      'lib/app/profile/free_editorial_profile_view.dart',
      'lib/app/profile/free_editorial_profile_adapter.dart',
    ]) {
      expect(_codeOf(f).contains('Koruyucu dalga'), false);
      expect(_codeOf(f).contains('jovia_aura'), false);
    }
  });

  test('9. Profile V8 / supporting threads not consulted by narrow path', () {
    for (final f in [
      'lib/app/profile/free_editorial_profile_host.dart',
      'lib/app/profile/free_editorial_profile_adapter.dart',
    ]) {
      final src = _codeOf(f);
      for (final forbidden in [
        'profile_v8',
        'sections_v2',
        'supporting_thread',
        'ProfileV8Adapter',
      ]) {
        expect(
          src.contains(forbidden),
          false,
          reason: '$f must not reference $forbidden',
        );
      }
    }
    // decision reads only editorial_profile through the dedicated adapter helper
    expect(
      _codeOf(
            'lib/app/profile/free_editorial_profile_adapter.dart',
          ).contains("'editorial_profile'") &&
          _codeOf(
            'lib/app/profile/free_editorial_profile_host.dart',
          ).contains('editorialProfileRaw'),
      true,
    );
  });

  test('10. Tam Okuma is not embedded in narrow path', () {
    for (final f in [
      'lib/app/profile/free_editorial_profile_host.dart',
      'lib/app/profile/free_editorial_profile_view.dart',
      'lib/app/profile/free_editorial_profile_adapter.dart',
    ]) {
      final src = _codeOf(f).toLowerCase();
      expect(src.contains('tam_okuma'), false);
      expect(src.contains('tamokuma'), false);
    }
  });

  test('11. mobile host has no dart-define flag gate', () {
    final src =
        _codeOf('lib/app/profile/free_editorial_profile_host.dart') +
        _codeOf('lib/app/profile/free_editorial_profile_adapter.dart') +
        _codeOf('lib/app/tabs/profile_page.dart');
    expect(src.contains('FREE_EDITORIAL_PROFILE_ENABLED'), false);
    expect(src.contains('kFreeEditorialProfileEnabled'), false);
    expect(src.contains('flagEnabled'), false);
  });

  test('12. /interpret/ui public envelope selects narrow', () {
    final d = decideFreeEditorialHost(payload: _interpretUiEnvelope());
    expect(d.showNarrow, true);
    expect(d.reason.code, 'EDITORIAL_SHOW');
    expect(d.model.cards.single.primaryKey, 'sun_capricorn');
    expect(d.payloadPresent, true);
    expect(d.editorialFieldPresent, true);
    expect(d.cardCount, 1);
    expect(
      d.diagnosticLine,
      'FREE_EDITORIAL_HOST payload_present=true editorial_field_present=true '
      'card_count=1 decision=narrow reason=null',
    );
  });

  test('13. profile fast cannot overwrite active editorial payload', () {
    final host = _codeOf('lib/app/tabs/profile_page.dart');
    expect(host.contains("_activeProfilePayload = activeMap"), true);
    expect(host.contains("_activeProfilePayload = fastMap"), false);
    expect(host.contains("_applyFastProfileSnapshot(result.data)"), true);
    expect(host.contains("'/interpret/ui'"), true);
    expect(host.contains("'/profile/fast'"), true);
  });

  test('14. diagnostics expose no birth data or card copy', () {
    final d = decideFreeEditorialHost(payload: _interpretUiEnvelope());
    final line = d.diagnosticLine.toLowerCase();
    expect(line.contains('birth'), false);
    expect(line.contains('güneş'), false);
    expect(line.contains('sun_capricorn'), false);
    expect(line.contains('decision=narrow'), true);
  });
}
