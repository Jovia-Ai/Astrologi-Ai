import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:purchases_flutter/purchases_flutter.dart';

import 'package:mobile/app/ai/revenuecat_service.dart';

void main() {
  test('restorePurchases returns restored when active access exists', () async {
    final service = RevenueCatService(
      sdk: _FakeRevenueCatSdk(
        customerInfo: _customerInfo(activeSubscriptions: const ['shou_pro']),
      ),
      appleApiKey: 'apple-key',
      googleApiKey: 'google-key',
      isSupportedPlatformOverride: true,
      currentUserIdProvider: () => 'user-123',
    );

    final result = await service.restorePurchases();

    expect(result.status, RestorePurchasesStatus.restored);
    expect(result.customerInfo?.activeSubscriptions, ['shou_pro']);
  });

  test(
    'restorePurchases returns noActivePurchases when nothing restorable exists',
    () async {
      final service = RevenueCatService(
        sdk: _FakeRevenueCatSdk(customerInfo: _customerInfo()),
        appleApiKey: 'apple-key',
        googleApiKey: 'google-key',
        isSupportedPlatformOverride: true,
        currentUserIdProvider: () => 'user-123',
      );

      final result = await service.restorePurchases();

      expect(result.status, RestorePurchasesStatus.noActivePurchases);
    },
  );

  test(
    'restorePurchases returns failure and surfaces the platform message',
    () async {
      final service = RevenueCatService(
        sdk: _FakeRevenueCatSdk(
          customerInfo: _customerInfo(),
          restoreError: PlatformException(
            code: 'restore_failed',
            message: 'Could not restore purchases.',
          ),
        ),
        appleApiKey: 'apple-key',
        googleApiKey: 'google-key',
        isSupportedPlatformOverride: true,
        currentUserIdProvider: () => 'user-123',
      );

      final result = await service.restorePurchases();

      expect(result.status, RestorePurchasesStatus.failed);
      expect(result.errorMessage, 'Could not restore purchases.');
    },
  );
}

class _FakeRevenueCatSdk implements RevenueCatSdk {
  _FakeRevenueCatSdk({required this.customerInfo, this.restoreError});

  final CustomerInfo customerInfo;
  final Object? restoreError;
  bool _configured = false;

  @override
  Future<String> get appUserId async => 'user-123';

  @override
  Future<void> configure(PurchasesConfiguration configuration) async {
    _configured = true;
  }

  @override
  Future<List<StoreProduct>> getProducts(
    List<String> productIds, {
    ProductCategory productCategory = ProductCategory.subscription,
  }) async {
    return const <StoreProduct>[];
  }

  @override
  Future<bool> get isConfigured async => _configured;

  @override
  Future<void> logIn(String appUserId) async {}

  @override
  Future<void> purchase(StoreProduct product) async {}

  @override
  Future<CustomerInfo> restorePurchases() async {
    if (restoreError != null) {
      throw restoreError!;
    }
    return customerInfo;
  }

  @override
  Future<void> syncPurchases() async {}
}

CustomerInfo _customerInfo({
  List<String> activeSubscriptions = const <String>[],
  List<StoreTransaction> nonSubscriptionTransactions =
      const <StoreTransaction>[],
}) {
  return CustomerInfo(
    const EntitlementInfos({}, {}),
    const <String, String?>{},
    activeSubscriptions,
    const <String>[],
    nonSubscriptionTransactions,
    '2026-04-13T00:00:00Z',
    'user-123',
    const <String, String?>{},
    '2026-04-13T00:00:00Z',
  );
}
