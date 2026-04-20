// Adapter + model passthrough — Voice spec v2.1 §11.4 (S2 Commit 2a).
//
// Invariants:
//   - ProfileV8TextSection.proofRaw field default '' ve constructor preserves.
//   - _normalizeThread raw 'proof_raw' → passthrough; null/whitespace → ''.
//   - _makeSection → proofRawCandidates first-non-empty selection.
//   - fromPayload end-to-end: thread payload proof_raw → section.proofRaw.
//   - Zero UI impact in this commit — body/chips/headline untouched.

import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/app/profile/profile_v8_adapter.dart';

ProfileV8Data _buildFromThreads(List<Map<String, dynamic>> threads) {
  return ProfileV8Adapter.fromPayload(
    payload: null,
    fastPayload: null,
    identityHeadline: '',
    identitySummary: '',
    identityDrivers: const <String>[],
    dominantElementLabel: '',
    narrativeCards: const <Map<String, dynamic>>[],
    insightModules: const <Map<String, dynamic>>[],
    supportingThreads: threads,
  );
}

Map<String, dynamic> _threadMap({
  required String id,
  required String title,
  String oneLiner = '',
  String paragraph = 'Bir içerik.',
  String proofRaw = '',
}) {
  return <String, dynamic>{
    'id': id,
    'title': title,
    'one_liner': oneLiner,
    'paragraph': paragraph,
    'proof_raw': proofRaw,
  };
}

void main() {
  group('ProfileV8TextSection.proofRaw — constructor', () {
    test('default is empty string', () {
      const section = ProfileV8TextSection(
        eyebrow: 'X',
        headline: 'Y',
        body: 'Z',
      );
      expect(section.proofRaw, '');
    });

    test('preserves explicit proofRaw value', () {
      const section = ProfileV8TextSection(
        eyebrow: 'X',
        headline: 'Y',
        body: 'Z',
        proofRaw: 'Satürn · 3. ev · Oğlak',
      );
      expect(section.proofRaw, 'Satürn · 3. ev · Oğlak');
    });

    test('empty proofRaw does not affect hasContent', () {
      const sectionWithProof = ProfileV8TextSection(
        eyebrow: '',
        headline: '',
        body: '',
        proofRaw: 'Satürn · 3. ev · Oğlak',
      );
      // hasContent bases on visible fields; proof_raw alone should not mark
      // section as renderable (belongs to body's credit, not primary content).
      expect(sectionWithProof.hasContent, isFalse);
    });
  });

  group('fromPayload — proof_raw passthrough end-to-end', () {
    test('mind thread carries proof_raw to mindSection.proofRaw', () {
      final data = _buildFromThreads(<Map<String, dynamic>>[
        _threadMap(
          id: 'mind_system',
          title: 'Zihinsel işleyiş',
          oneLiner: 'Düşünmeden konuşmuyorsun.',
          proofRaw: 'Satürn · 3. ev · Oğlak',
        ),
      ]);
      expect(data.mindSection, isNotNull);
      expect(data.mindSection!.proofRaw, 'Satürn · 3. ev · Oğlak');
    });

    test('origin thread carries proof_raw to originSection.proofRaw', () {
      final data = _buildFromThreads(<Map<String, dynamic>>[
        _threadMap(
          id: 'relationships',
          title: 'Bu nereden geliyor olabilir — geçmiş bağ',
          oneLiner: 'Kökten gelen güven ihtiyacın.',
          proofRaw: 'Venüs · 11. ev · Balık',
        ),
      ]);
      expect(data.originSection, isNotNull);
      expect(data.originSection!.proofRaw, 'Venüs · 11. ev · Balık');
    });

    test('conversation thread carries proof_raw to conversationSection', () {
      final data = _buildFromThreads(<Map<String, dynamic>>[
        _threadMap(
          id: 'communication',
          title: 'Nasıl konuşuyorsun — sohbet',
          oneLiner: 'Kelimeyi ölçerek seçiyorsun.',
          proofRaw: 'Merkür · 6. ev · Başak',
        ),
      ]);
      expect(data.conversationSection, isNotNull);
      expect(data.conversationSection!.proofRaw, 'Merkür · 6. ev · Başak');
    });

    test('missing proof_raw falls back to empty string', () {
      final data = _buildFromThreads(<Map<String, dynamic>>[
        <String, dynamic>{
          'id': 'mind_system',
          'title': 'Zihinsel işleyiş',
          'paragraph': 'Düşünmeden konuşmuyorsun.',
          // no proof_raw key
        },
      ]);
      expect(data.mindSection, isNotNull);
      expect(data.mindSection!.proofRaw, '');
    });

    test('whitespace-only proof_raw normalizes to empty', () {
      final data = _buildFromThreads(<Map<String, dynamic>>[
        _threadMap(
          id: 'mind_system',
          title: 'Zihinsel işleyiş',
          oneLiner: 'Düşünmeden konuşmuyorsun.',
          proofRaw: '   ',
        ),
      ]);
      expect(data.mindSection, isNotNull);
      expect(data.mindSection!.proofRaw, '');
    });

    test('null proof_raw normalizes to empty string (no crash)', () {
      final data = _buildFromThreads(<Map<String, dynamic>>[
        <String, dynamic>{
          'id': 'mind_system',
          'title': 'Zihinsel işleyiş',
          'paragraph': 'Bir içerik.',
          'proof_raw': null,
        },
      ]);
      expect(data.mindSection, isNotNull);
      expect(data.mindSection!.proofRaw, '');
    });

    test('non-string proof_raw coerced via safeText (no crash)', () {
      final data = _buildFromThreads(<Map<String, dynamic>>[
        <String, dynamic>{
          'id': 'mind_system',
          'title': 'Zihinsel işleyiş',
          'paragraph': 'Bir içerik.',
          'proof_raw': 12345,
        },
      ]);
      expect(data.mindSection, isNotNull);
      // safeText coerces num/bool to string — voice spec §11.9 invariant:
      // "daima payload'ta, asla null". Not ideal (template üretilmiyor),
      // ama crash yok. Backend source of truth — widget downstream
      // render'ı yine sağlıklı (11px sayı stringi çirkin ama hata değil).
      expect(data.mindSection!.proofRaw, '12345');
    });

    test('multiple live threads each keep their own proof_raw', () {
      final data = _buildFromThreads(<Map<String, dynamic>>[
        _threadMap(
          id: 'mind_system',
          title: 'Zihinsel işleyiş',
          oneLiner: 'Düşünüyorsun.',
          proofRaw: 'Satürn · 3. ev · Oğlak',
        ),
        _threadMap(
          id: 'relationships',
          title: 'Bu nereden geliyor olabilir',
          oneLiner: 'Güven geçmişten.',
          proofRaw: 'Venüs · 11. ev · Balık',
        ),
      ]);
      expect(data.mindSection?.proofRaw, 'Satürn · 3. ev · Oğlak');
      expect(data.originSection?.proofRaw, 'Venüs · 11. ev · Balık');
      // Different sections do not leak each other's proof.
      expect(data.mindSection?.proofRaw, isNot('Venüs · 11. ev · Balık'));
    });
  });

  group('fromPayload — existing fields unaffected (zero-diff)', () {
    test('body/headline/chips still render from thread when proof_raw present',
        () {
      final data = _buildFromThreads(<Map<String, dynamic>>[
        <String, dynamic>{
          'id': 'mind_system',
          'title': 'Zihinsel işleyiş',
          'one_liner': 'Düşünmeden konuşmuyorsun.',
          'paragraph': 'Zihnin içeride bir kez daha tartıyor.',
          'chips': <String>['Satürn', '3. evde', 'Oğlak'],
          'proof_raw': 'Satürn · 3. ev · Oğlak',
        },
      ]);
      final section = data.mindSection!;
      expect(section.headline.isNotEmpty, isTrue);
      expect(section.body.isNotEmpty, isTrue);
      expect(section.chips, contains('Satürn'));
      expect(section.proofRaw, 'Satürn · 3. ev · Oğlak');
    });

    test('thread with empty proof_raw keeps other fields intact', () {
      // Regression guard: adapter değişikliği diğer passthrough'u bozmuyor.
      // Note: _pickThread keyword-less fallback davranışı mevcut sistemde
      // var; bu test "proof_raw yokluğu diğer alanları bozmasın" ile sınırlı.
      final data = _buildFromThreads(<Map<String, dynamic>>[
        _threadMap(
          id: 'mind_system',
          title: 'Zihinsel işleyiş',
          oneLiner: 'Düşünüyorsun.',
          paragraph: 'Zihnin içeride tartıyor.',
          // proofRaw intentionally empty
        ),
      ]);
      final section = data.mindSection!;
      expect(section.proofRaw, '');
      expect(section.body.isNotEmpty, isTrue);
      expect(section.headline.isNotEmpty, isTrue);
    });
  });
}
