import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/app/auth/auth_gate.dart';

void main() {
  test('routes to tabs when birth data is complete', () async {
    final decision = await loadBirthDataGateDecision(
      userId: 'user-1',
      profileLoader: (_) async => <String, dynamic>{
        'birth_date': '1996-07-27',
        'place': 'Istanbul, Turkiye',
      },
    );

    expect(decision.target, BirthDataGateTarget.tabs);
  });

  test('routes to onboarding when birth data is missing', () async {
    final decision = await loadBirthDataGateDecision(
      userId: 'user-2',
      profileLoader: (_) async => <String, dynamic>{
        'birth_date': null,
        'place': '',
      },
    );

    expect(decision.target, BirthDataGateTarget.onboarding);
  });

  test('routes to retry when profile loading throws', () async {
    final error = Exception('Failed host lookup');
    final decision = await loadBirthDataGateDecision(
      userId: 'user-3',
      profileLoader: (_) async => throw error,
    );

    expect(decision.target, BirthDataGateTarget.retry);
    expect(decision.error, same(error));
  });
}
