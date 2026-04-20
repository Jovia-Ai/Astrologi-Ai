// Proof chip widget test — voice spec v2.1 S1 Commit 2.
//
// Invariants under test:
//   - Locale-gated render (voice spec §11.8): sadece TR locale'de görünür.
//   - Empty proofRaw → SizedBox.shrink (voice spec §11.9).
//   - Title Case + Türkçe karakterler korunur (voice spec §11.5).
//   - Accessibility: alpha ≥ 0.60, font ≥ 11px (voice spec §11.6).
//   - Overflow: maxLines 1 + ellipsis.
//   - topSpacing parametresi respect edilir.

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/app/profile/proof_chip.dart';

import 'support/test_app.dart';

Finder _chipText(String content) => find.text(content);

void main() {
  group('ProfileProofChip — render gating', () {
    testWidgets('empty proofRaw → SizedBox.shrink', (tester) async {
      await tester.pumpWidget(
        buildTestApp(
          locale: const Locale('tr'),
          child: const Scaffold(
            body: ProfileProofChip(proofRaw: ''),
          ),
        ),
      );

      expect(find.byType(Container), findsNothing);
      expect(find.byType(Text), findsNothing);
    });

    testWidgets('TR locale + proofRaw present → chip renders', (tester) async {
      await tester.pumpWidget(
        buildTestApp(
          locale: const Locale('tr'),
          child: const Scaffold(
            body: ProfileProofChip(proofRaw: 'Satürn · 3. ev · Oğlak'),
          ),
        ),
      );

      expect(_chipText('Satürn · 3. ev · Oğlak'), findsOneWidget);
    });

    testWidgets('EN locale → SizedBox.shrink (locale-gated)', (tester) async {
      await tester.pumpWidget(
        buildTestApp(
          locale: const Locale('en'),
          child: const Scaffold(
            body: ProfileProofChip(proofRaw: 'Satürn · 3. ev · Oğlak'),
          ),
        ),
      );

      expect(_chipText('Satürn · 3. ev · Oğlak'), findsNothing);
      expect(find.byType(Container), findsNothing);
    });

    testWidgets('Non-supported locale (de) → SizedBox.shrink', (tester) async {
      await tester.pumpWidget(
        buildTestApp(
          locale: const Locale('de'),
          child: const Scaffold(
            body: ProfileProofChip(proofRaw: 'Satürn · 3. ev · Oğlak'),
          ),
        ),
      );

      expect(find.byType(Text), findsNothing);
    });
  });

  group('ProfileProofChip — text rendering', () {
    testWidgets('Türkçe karakterler korunur (İ / ğ / ş / ö / ü)',
        (tester) async {
      await tester.pumpWidget(
        buildTestApp(
          locale: const Locale('tr'),
          child: const Scaffold(
            body: ProfileProofChip(proofRaw: 'Jüpiter · 9. ev · İkizler'),
          ),
        ),
      );

      expect(_chipText('Jüpiter · 9. ev · İkizler'), findsOneWidget);
    });

    testWidgets('Title Case korunur — lowercase transform yok',
        (tester) async {
      await tester.pumpWidget(
        buildTestApp(
          locale: const Locale('tr'),
          child: const Scaffold(
            body: ProfileProofChip(proofRaw: 'Venüs · 11. ev · Balık'),
          ),
        ),
      );

      expect(_chipText('Venüs · 11. ev · Balık'), findsOneWidget);
      expect(_chipText('venüs · 11. ev · balık'), findsNothing);
    });

    testWidgets('maxLines 1 + ellipsis overflow', (tester) async {
      await tester.pumpWidget(
        buildTestApp(
          locale: const Locale('tr'),
          child: const Scaffold(
            body: SizedBox(
              width: 80,
              child: ProfileProofChip(
                proofRaw: 'Çok Uzun Bir Gezegen Adı · 12. ev · Bambaşka',
              ),
            ),
          ),
        ),
      );

      final textWidget = tester.widget<Text>(find.byType(Text));
      expect(textWidget.maxLines, 1);
      expect(textWidget.overflow, TextOverflow.ellipsis);
    });
  });

  group('ProfileProofChip — accessibility invariants (voice spec §11.6)', () {
    testWidgets('alpha ≥ 0.60 on text color', (tester) async {
      await tester.pumpWidget(
        buildTestApp(
          locale: const Locale('tr'),
          child: const Scaffold(
            body: ProfileProofChip(proofRaw: 'Satürn · 3. ev · Oğlak'),
          ),
        ),
      );

      final textWidget = tester.widget<Text>(find.byType(Text));
      final color = textWidget.style?.color;
      expect(color, isNotNull);
      // 0.60 * 255 ≈ 153. Voice spec §11.6 invariant: alpha en az 0.60.
      expect(color!.a, greaterThanOrEqualTo(0.60));
    });

    testWidgets('font size ≥ 11px', (tester) async {
      await tester.pumpWidget(
        buildTestApp(
          locale: const Locale('tr'),
          child: const Scaffold(
            body: ProfileProofChip(proofRaw: 'Satürn · 3. ev · Oğlak'),
          ),
        ),
      );

      final textWidget = tester.widget<Text>(find.byType(Text));
      final fontSize = textWidget.style?.fontSize;
      expect(fontSize, isNotNull);
      // Voice spec §11.6 invariant.
      expect(fontSize!, greaterThanOrEqualTo(11.0));
    });
  });

  group('ProfileProofChip — layout', () {
    testWidgets('default topSpacing = 14', (tester) async {
      await tester.pumpWidget(
        buildTestApp(
          locale: const Locale('tr'),
          child: const Scaffold(
            body: ProfileProofChip(proofRaw: 'Satürn · 3. ev · Oğlak'),
          ),
        ),
      );

      final padding = tester.widget<Padding>(find.byType(Padding).first);
      expect(padding.padding, const EdgeInsets.only(top: 14));
    });

    testWidgets('custom topSpacing respect edilir', (tester) async {
      await tester.pumpWidget(
        buildTestApp(
          locale: const Locale('tr'),
          child: const Scaffold(
            body: ProfileProofChip(
              proofRaw: 'Satürn · 3. ev · Oğlak',
              topSpacing: 24,
            ),
          ),
        ),
      );

      final padding = tester.widget<Padding>(find.byType(Padding).first);
      expect(padding.padding, const EdgeInsets.only(top: 24));
    });

    testWidgets('widget tree contains exactly one Text node', (tester) async {
      await tester.pumpWidget(
        buildTestApp(
          locale: const Locale('tr'),
          child: const Scaffold(
            body: ProfileProofChip(proofRaw: 'Mars · 9. ev · Yay'),
          ),
        ),
      );

      expect(find.byType(Text), findsOneWidget);
    });
  });
}
