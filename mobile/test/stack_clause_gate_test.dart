import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/app/timing/narrative_dtos.dart';
import 'package:mobile/app/timing/stack_clause_gate.dart';

const String _clause =
    'Bu hat bugun tek basina degil; birkac konu ayni anda calisiyor.';

void main() {
  group('stackClauseShouldShow', () {
    test('empty clause returns false regardless of cooldown state', () {
      final result = stackClauseShouldShow(
        stackClauseTr: '',
        lastShownMs: null,
        nowMs: 1_700_000_000_000,
        featureEnabled: true,
      );
      expect(result, isFalse);
    });

    test('fresh cooldown (never shown) returns true for non-empty clause', () {
      final result = stackClauseShouldShow(
        stackClauseTr: _clause,
        lastShownMs: null,
        nowMs: 1_700_000_000_000,
        featureEnabled: true,
      );
      expect(result, isTrue);
    });

    test('active cooldown (3 days ago) returns false', () {
      final now = 1_700_000_000_000;
      final threeDaysAgo = now - (3 * 24 * 60 * 60 * 1000);
      final result = stackClauseShouldShow(
        stackClauseTr: _clause,
        lastShownMs: threeDaysAgo,
        nowMs: now,
        featureEnabled: true,
      );
      expect(result, isFalse);
    });

    test('boundary: exactly 7 days ago returns true', () {
      final now = 1_700_000_000_000;
      final exactlySevenDaysAgo = now - kStackClauseCooldownMs;
      final result = stackClauseShouldShow(
        stackClauseTr: _clause,
        lastShownMs: exactlySevenDaysAgo,
        nowMs: now,
        featureEnabled: true,
      );
      expect(result, isTrue);
    });

    test('boundary minus 1 ms still under cooldown (returns false)', () {
      final now = 1_700_000_000_000;
      final justShyOfSeven = now - kStackClauseCooldownMs + 1;
      final result = stackClauseShouldShow(
        stackClauseTr: _clause,
        lastShownMs: justShyOfSeven,
        nowMs: now,
        featureEnabled: true,
      );
      expect(result, isFalse);
    });

    test('feature flag off suppresses clause even on fresh cooldown', () {
      final result = stackClauseShouldShow(
        stackClauseTr: _clause,
        lastShownMs: null,
        nowMs: 1_700_000_000_000,
        featureEnabled: false,
      );
      expect(result, isFalse);
    });

    test('14 days later (long absence) returns true', () {
      final now = 1_700_000_000_000;
      final fourteenDaysAgo = now - (14 * 24 * 60 * 60 * 1000);
      final result = stackClauseShouldShow(
        stackClauseTr: _clause,
        lastShownMs: fourteenDaysAgo,
        nowMs: now,
        featureEnabled: true,
      );
      expect(result, isTrue);
    });
  });

  group('stackClauseComposeLine', () {
    test('show=false returns baseText unchanged', () {
      final result = stackClauseComposeLine(
        baseText: 'Etki su anda zirveye.',
        stackClauseTr: _clause,
        showStackClause: false,
      );
      expect(result, 'Etki su anda zirveye.');
    });

    test('show=true concatenates with single space', () {
      final result = stackClauseComposeLine(
        baseText: 'Etki su anda zirveye.',
        stackClauseTr: _clause,
        showStackClause: true,
      );
      expect(result, 'Etki su anda zirveye. $_clause');
    });

    test('show=true but empty clause returns baseText unchanged', () {
      final result = stackClauseComposeLine(
        baseText: 'Etki su anda zirveye.',
        stackClauseTr: '',
        showStackClause: true,
      );
      expect(result, 'Etki su anda zirveye.');
    });

    test('empty baseText + show=true returns just clause', () {
      final result = stackClauseComposeLine(
        baseText: '',
        stackClauseTr: _clause,
        showStackClause: true,
      );
      expect(result, _clause);
    });
  });

  group('EventCardDto deserialization with stack_clause_tr', () {
    test('reads stack_clause_tr when present', () {
      final card = EventCardDto.fromMap({
        'event_id': 'evt_x',
        'why_now': 'Etki su anda zirveye.',
        'stack_clause_tr': _clause,
      });
      expect(card.stackClauseTr, _clause);
    });

    test('defaults to empty string when field absent', () {
      final card = EventCardDto.fromMap({
        'event_id': 'evt_x',
        'why_now': 'Etki su anda zirveye.',
      });
      expect(card.stackClauseTr, '');
    });

    test('tolerates empty string (non-top-member of a stack)', () {
      final card = EventCardDto.fromMap({
        'event_id': 'evt_x',
        'why_now': 'Etki su anda zirveye.',
        'stack_clause_tr': '',
      });
      expect(card.stackClauseTr, '');
    });
  });
}
