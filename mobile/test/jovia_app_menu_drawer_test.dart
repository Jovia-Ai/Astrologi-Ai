import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import 'package:mobile/app/ai/revenuecat_service.dart';
import 'package:mobile/app/auth/account_service.dart';
import 'package:mobile/app/legal/external_link_service.dart';
import 'package:mobile/app/people/people_providers.dart';
import 'package:mobile/app/people/person_profile.dart';
import 'package:mobile/app/preferences/jovia_app_preferences_provider.dart';
import 'package:mobile/app/profile/profile_providers.dart';
import 'package:mobile/app/theme/app_theme_mode_provider.dart';
import 'package:mobile/app/widgets/jovia_app_menu_drawer.dart';

import 'support/test_app.dart';

void main() {
  testWidgets(
    'drawer renders the new App Store compliance menu items in English',
    (tester) async {
      await _pumpDrawer(tester, locale: const Locale('en'));

      expect(find.text('Restore Purchases'), findsOneWidget);
      expect(find.text('Privacy Policy'), findsOneWidget);
      expect(find.text('Terms of Use'), findsOneWidget);
      expect(find.text('Support'), findsOneWidget);
      expect(find.text('Delete Account'), findsOneWidget);
    },
  );

  testWidgets(
    'drawer renders the new App Store compliance menu items in Turkish',
    (tester) async {
      await _pumpDrawer(tester, locale: const Locale('tr'));

      expect(find.text('Satın Alımları Geri Yükle'), findsOneWidget);
      expect(find.text('Gizlilik Politikası'), findsOneWidget);
      expect(find.text('Kullanım Koşulları'), findsOneWidget);
      expect(find.text('Destek'), findsOneWidget);
      expect(find.text('Hesabı Sil'), findsOneWidget);
    },
  );

  testWidgets(
    'delete account dialog can be cancelled without calling the service',
    (tester) async {
      final accountService = _FakeAccountService();
      await _pumpDrawer(
        tester,
        locale: const Locale('en'),
        accountService: accountService,
      );

      await tester.tap(find.text('Delete Account'));
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 220));

      expect(
        find.text('Are you sure you want to delete your account?'),
        findsOneWidget,
      );
      expect(accountService.deleteCallCount, 0);

      await tester.tap(find.text('Cancel'));
      await tester.pumpAndSettle();

      expect(accountService.deleteCallCount, 0);
      expect(
        find.text('Are you sure you want to delete your account?'),
        findsNothing,
      );
    },
  );

  testWidgets('delete account confirm calls backend deletion and signs out', (
    tester,
  ) async {
    final accountService = _FakeAccountService();
    var signOutCalls = 0;
    await _pumpDrawer(
      tester,
      locale: const Locale('en'),
      accountService: accountService,
      onSignOut: () async {
        signOutCalls += 1;
      },
    );

    await tester.tap(find.text('Delete Account'));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 220));
    await tester.tap(find.text('Delete Account').last);
    await tester.pump();
    await tester.pumpAndSettle();

    expect(accountService.deleteCallCount, 1);
    expect(signOutCalls, 1);
    expect(find.text('Your account has been deleted.'), findsOneWidget);
  });
}

Future<void> _pumpDrawer(
  WidgetTester tester, {
  required Locale locale,
  _FakeAccountService? accountService,
  Future<void> Function()? onSignOut,
}) async {
  await tester.pumpWidget(
    ProviderScope(
      overrides: [
        currentUserIdProvider.overrideWith((ref) => 'user-123'),
        userProfileProvider.overrideWith(
          (ref) async => <String, dynamic>{
            'full_name': 'Ada Lovelace',
            'username': 'adal',
            'birth_date': '1990-01-01',
            'birth_time': '10:00',
            'place': 'Istanbul, Turkiye',
          },
        ),
        peopleListProvider.overrideWith((ref) async => const <PersonProfile>[]),
        joviaAppPreferencesProvider.overrideWith(
          _TestPreferencesController.new,
        ),
        joviaThemeModeProvider.overrideWith(_TestThemeModeController.new),
      ],
      child: buildTestApp(
        locale: locale,
        child: Scaffold(
          endDrawer: JoviaAppMenuDrawer(
            currentUser: const User(
              id: 'user-123',
              appMetadata: <String, dynamic>{},
              userMetadata: <String, dynamic>{},
              aud: 'authenticated',
              email: 'ada@example.com',
              createdAt: '2026-04-13T00:00:00Z',
            ),
            accountService: accountService ?? _FakeAccountService(),
            revenueCatService: _FakeRevenueCatService(),
            externalLinkService: const _FakeExternalLinkService(),
            onSignOut: onSignOut,
          ),
          body: Builder(
            builder: (context) {
              return TextButton(
                onPressed: () => Scaffold.of(context).openEndDrawer(),
                child: const Text('Open'),
              );
            },
          ),
        ),
      ),
    ),
  );

  await tester.tap(find.text('Open'));
  await tester.pumpAndSettle();
}

class _TestPreferencesController extends JoviaAppPreferencesController {
  @override
  JoviaAppPreferences build() {
    return const JoviaAppPreferences(
      locale: JoviaAppLocale.en,
      dailyBriefEnabled: true,
      skyAlertsEnabled: true,
      socialAlertsEnabled: false,
      premiumInterest: false,
    );
  }
}

class _TestThemeModeController extends JoviaThemeModeController {
  @override
  JoviaThemeMode build() => JoviaThemeMode.light;
}

class _FakeRevenueCatService extends RevenueCatService {
  _FakeRevenueCatService();

  @override
  Future<RestorePurchasesResult> restorePurchases() async {
    return const RestorePurchasesResult(
      status: RestorePurchasesStatus.noActivePurchases,
    );
  }
}

class _FakeAccountService extends AccountService {
  int deleteCallCount = 0;

  @override
  Future<void> deleteCurrentAccount() async {
    deleteCallCount += 1;
  }
}

class _FakeExternalLinkService extends ExternalLinkService {
  const _FakeExternalLinkService();

  @override
  Future<void> openPrivacyPolicy() async {}

  @override
  Future<void> openTermsOfUse() async {}

  @override
  Future<void> openSupport() async {}
}
