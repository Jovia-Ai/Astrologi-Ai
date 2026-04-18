// Faz 2 PR 8b: inline explainability panel widget test coverage.
//
// 1. Phrase helper'ları (pure function) — full matrix
// 2. Panel widget davranışı — collapsed/expanded, data var/yok state
//
// Widget test'leri test_app.dart üzerinden ProfileTheme ile pump edilir;
// gerçek backend çağrısı yok, payload sentetik.

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/app/profile/explainability_panel.dart';

import 'support/test_app.dart';

void main() {
  group('strengthLabel', () {
    test('meets threshold + positive dignity → güçlü oturmuş', () {
      expect(
        strengthLabel(meetsThreshold: true, dignityBonus: 0.15),
        'güçlü oturmuş',
      );
    });

    test('meets threshold + negative dignity → net ama gerilimde', () {
      expect(
        strengthLabel(meetsThreshold: true, dignityBonus: -0.10),
        'net ama gerilimde',
      );
    });

    test('meets threshold + peregrine → net ayrışıyor', () {
      expect(
        strengthLabel(meetsThreshold: true, dignityBonus: 0.0),
        'net ayrışıyor',
      );
    });

    test('below threshold + negative dignity → arka planda', () {
      expect(
        strengthLabel(meetsThreshold: false, dignityBonus: -0.15),
        'arka planda',
      );
    });

    test('below threshold + peregrine → hafif', () {
      expect(
        strengthLabel(meetsThreshold: false, dignityBonus: 0.0),
        'hafif',
      );
    });
  });

  group('dignityChip', () {
    test('builder with high domicile bonus → Satürn güçlü destekli', () {
      expect(
        dignityChip(archetypeId: 'builder', dignityBonus: 0.15),
        'Satürn güçlü destekli',
      );
    });

    test('guardian dual signature → Satürn, Ay güçlü destekli', () {
      expect(
        dignityChip(archetypeId: 'guardian', dignityBonus: 0.30),
        'Satürn, Ay güçlü destekli',
      );
    });

    test('builder fall → Satürn yabancı alanda', () {
      expect(
        dignityChip(archetypeId: 'builder', dignityBonus: -0.15),
        'Satürn yabancı alanda',
      );
    });

    test('light positive → destekli tier', () {
      expect(
        dignityChip(archetypeId: 'analyst', dignityBonus: 0.06),
        'Merkür destekli',
      );
    });

    test('peregrine zone → null chip', () {
      expect(dignityChip(archetypeId: 'builder', dignityBonus: 0.0), isNull);
      expect(dignityChip(archetypeId: 'builder', dignityBonus: 0.04), isNull);
      expect(dignityChip(archetypeId: 'builder', dignityBonus: -0.04), isNull);
    });

    test('unknown archetype → null chip (graceful)', () {
      expect(
        dignityChip(archetypeId: 'mystery', dignityBonus: 0.15),
        isNull,
      );
    });

    test('case-insensitive archetype id', () {
      expect(
        dignityChip(archetypeId: 'BUILDER', dignityBonus: 0.15),
        'Satürn güçlü destekli',
      );
    });
  });

  group('tensionChips', () {
    test('non-zero buckets produce chips, unknown skipped', () {
      final chips = tensionChips({
        'applying': 3,
        'separating': 1,
        'exact': 1,
        'unknown': 5,
      });
      expect(chips, [
        '1 tam aspect',
        '3 yaklaşan gerilim',
        '1 işlenmiş hareket',
      ]);
    });

    test('zero counts produce empty list', () {
      expect(
        tensionChips({'applying': 0, 'separating': 0, 'exact': 0, 'unknown': 0}),
        isEmpty,
      );
    });

    test('null breakdown → empty', () {
      expect(tensionChips(null), isEmpty);
    });

    test('only unknown counts → empty (internal signal hidden)', () {
      expect(tensionChips({'applying': 0, 'unknown': 4}), isEmpty);
    });
  });

  group('lunarPhaseChip', () {
    test('maps known phases', () {
      expect(lunarPhaseChip('new'), 'Yeni ay gecesi');
      expect(lunarPhaseChip('full'), 'Dolunay altında');
      expect(lunarPhaseChip('balsamic'), 'Balsamic an');
    });

    test('null phase → null chip', () {
      expect(lunarPhaseChip(null), isNull);
    });

    test('unknown phase label → null chip (graceful)', () {
      expect(lunarPhaseChip('crescent_doom'), isNull);
    });
  });

  group('hasExplainableContent', () {
    test('empty item, no lunar → false', () {
      expect(
        hasExplainableContent(item: const <String, dynamic>{}, lunarPhase: null),
        isFalse,
      );
    });

    test('non-empty why → true', () {
      expect(
        hasExplainableContent(
          item: const {'why_this_not_that': 'bir şey'},
          lunarPhase: null,
        ),
        isTrue,
      );
    });

    test('lunar phase alone → true', () {
      expect(
        hasExplainableContent(item: const {}, lunarPhase: 'full'),
        isTrue,
      );
    });
  });

  group('ExplainabilityPanel widget', () {
    testWidgets('starts collapsed with toggle visible', (tester) async {
      await _pump(tester, item: _fullItem(), lunarPhase: 'full');
      expect(find.text('Neden bu öne çıktı?'), findsOneWidget);
      // Expanded content should not be visible initially
      expect(find.text('1 tam aspect'), findsNothing);
      expect(find.text('Dolunay altında'), findsNothing);
    });

    testWidgets('tap toggle reveals all four blocks', (tester) async {
      await _pump(tester, item: _fullItem(), lunarPhase: 'full');
      await tester.tap(find.text('Neden bu öne çıktı?'));
      await tester.pumpAndSettle();

      // Block 1: why narrative
      expect(
        find.textContaining('systems_architect', findRichText: true),
        findsOneWidget,
      );
      // Block 2: strength + dignity chips
      expect(find.text('güçlü oturmuş'), findsOneWidget);
      expect(find.text('Satürn güçlü destekli'), findsOneWidget);
      // Block 3: tension chips
      expect(find.text('2 yaklaşan gerilim'), findsOneWidget);
      // Block 4: lunar phase chip
      expect(find.text('Dolunay altında'), findsOneWidget);
    });

    testWidgets('second tap collapses back', (tester) async {
      await _pump(tester, item: _fullItem(), lunarPhase: 'full');
      await tester.tap(find.text('Neden bu öne çıktı?'));
      await tester.pumpAndSettle();
      expect(find.text('Dolunay altında'), findsOneWidget);

      await tester.tap(find.text('Neden bu öne çıktı?'));
      await tester.pumpAndSettle();
      expect(find.text('Dolunay altında'), findsNothing);
    });

    testWidgets(
      'renders nothing when no explainable content present',
      (tester) async {
        await _pump(
          tester,
          item: const <String, dynamic>{},
          lunarPhase: null,
        );
        // Toggle should not render at all
        expect(find.text('Neden bu öne çıktı?'), findsNothing);
      },
    );

    testWidgets('partial data: only why + lunar, no tension/dignity', (tester) async {
      await _pump(
        tester,
        item: const {'why_this_not_that': 'Bu profil öne çıktı.'},
        lunarPhase: 'new',
      );
      await tester.tap(find.text('Neden bu öne çıktı?'));
      await tester.pumpAndSettle();
      expect(find.text('Bu profil öne çıktı.'), findsOneWidget);
      expect(find.text('Yeni ay gecesi'), findsOneWidget);
      // Tension & dignity chips absent
      expect(find.textContaining('yaklaşan'), findsNothing);
      expect(find.textContaining('destekli'), findsNothing);
      // Strength chip still present ("hafif") — threshold false default
      expect(find.text('hafif'), findsOneWidget);
    });

    testWidgets(
      'zero breakdown hides tension block, lunar still renders',
      (tester) async {
        await _pump(
          tester,
          item: const {
            'id': 'builder',
            'score_meets_primary_threshold': true,
            'aspect_direction_breakdown': {
              'applying': 0,
              'separating': 0,
              'exact': 0,
              'unknown': 0,
            },
          },
          lunarPhase: 'first_quarter',
          dignityBonus: 0.15,
        );
        await tester.tap(find.text('Neden bu öne çıktı?'));
        await tester.pumpAndSettle();
        expect(find.text('İlk çeyrek arifesi'), findsOneWidget);
        expect(find.text('güçlü oturmuş'), findsOneWidget);
        // No tension chips
        expect(find.textContaining('yaklaşan gerilim'), findsNothing);
        expect(find.textContaining('tam aspect'), findsNothing);
      },
    );
  });
}

Map<String, dynamic> _fullItem() => {
  'id': 'builder',
  'why_this_not_that':
      'Ayni cekirdekte rebel_designer tonu da mumkundu; ama systems_architect tonu sende daha net ayrisiyor.',
  'score_meets_primary_threshold': true,
  'aspect_direction_breakdown': {
    'applying': 2,
    'separating': 0,
    'exact': 1,
    'unknown': 0,
  },
};

Future<void> _pump(
  WidgetTester tester, {
  required Map<String, dynamic> item,
  String? lunarPhase,
  double dignityBonus = 0.15,
}) async {
  await tester.pumpWidget(
    buildTestApp(
      child: Scaffold(
        body: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: ExplainabilityPanel(
            item: item,
            accent: Colors.black87,
            lunarPhase: lunarPhase,
            dignityBonus: dignityBonus,
          ),
        ),
      ),
    ),
  );
  await tester.pump();
}
