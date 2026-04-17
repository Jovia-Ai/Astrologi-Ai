import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:purchases_flutter/purchases_flutter.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

enum RestorePurchasesStatus { restored, noActivePurchases, failed }

class RestorePurchasesResult {
  const RestorePurchasesResult({
    required this.status,
    this.errorMessage,
    this.customerInfo,
  });

  final RestorePurchasesStatus status;
  final String? errorMessage;
  final CustomerInfo? customerInfo;
}

abstract class RevenueCatSdk {
  const RevenueCatSdk();

  Future<bool> get isConfigured;

  Future<void> configure(PurchasesConfiguration configuration);

  Future<List<StoreProduct>> getProducts(
    List<String> productIds, {
    ProductCategory productCategory = ProductCategory.subscription,
  });

  Future<void> purchase(StoreProduct product);

  Future<void> syncPurchases();

  Future<CustomerInfo> restorePurchases();

  Future<String> get appUserId;

  Future<void> logIn(String appUserId);
}

class PurchasesRevenueCatSdk implements RevenueCatSdk {
  const PurchasesRevenueCatSdk();

  @override
  Future<bool> get isConfigured => Purchases.isConfigured;

  @override
  Future<void> configure(PurchasesConfiguration configuration) {
    return Purchases.configure(configuration);
  }

  @override
  Future<List<StoreProduct>> getProducts(
    List<String> productIds, {
    ProductCategory productCategory = ProductCategory.subscription,
  }) {
    return Purchases.getProducts(productIds, productCategory: productCategory);
  }

  @override
  Future<void> purchase(StoreProduct product) {
    return Purchases.purchase(PurchaseParams.storeProduct(product));
  }

  @override
  Future<void> syncPurchases() => Purchases.syncPurchases();

  @override
  Future<CustomerInfo> restorePurchases() => Purchases.restorePurchases();

  @override
  Future<String> get appUserId => Purchases.appUserID;

  @override
  Future<void> logIn(String appUserId) => Purchases.logIn(appUserId);
}

class RevenueCatService {
  RevenueCatService({
    RevenueCatSdk? sdk,
    String? appleApiKey,
    String? googleApiKey,
    bool? isSupportedPlatformOverride,
    String? Function()? currentUserIdProvider,
  }) : _sdk = sdk ?? const PurchasesRevenueCatSdk(),
       _appleApiKeyOverride = appleApiKey,
       _googleApiKeyOverride = googleApiKey,
       _isSupportedPlatformOverride = isSupportedPlatformOverride,
       _currentUserIdProvider =
           currentUserIdProvider ??
           (() => Supabase.instance.client.auth.currentUser?.id);

  final RevenueCatSdk _sdk;
  final String? _appleApiKeyOverride;
  final String? _googleApiKeyOverride;
  final bool? _isSupportedPlatformOverride;
  final String? Function() _currentUserIdProvider;

  static const String q1ProductId = 'jovia_q1';
  static const String q5ProductId = 'jovia_q5';
  static const String q15ProductId = 'jovia_q15';
  static const String proMonthlyProductId = 'jovia_pro_monthly';

  static const String _appleApiKey = String.fromEnvironment(
    'REVENUECAT_APPLE_PUBLIC_SDK_KEY',
    defaultValue: '',
  );
  static const String _googleApiKey = String.fromEnvironment(
    'REVENUECAT_GOOGLE_PUBLIC_SDK_KEY',
    defaultValue: '',
  );

  static bool get isSupportedPlatform {
    if (kIsWeb) {
      return false;
    }
    return defaultTargetPlatform == TargetPlatform.iOS ||
        defaultTargetPlatform == TargetPlatform.android;
  }

  Future<Map<String, StoreProduct>> loadProducts() async {
    await _ensureConfigured();
    final products = <StoreProduct>[
      ...await _sdk.getProducts(<String>[
        q1ProductId,
        q5ProductId,
        q15ProductId,
      ], productCategory: ProductCategory.nonSubscription),
      ...await _sdk.getProducts(<String>[proMonthlyProductId]),
    ];
    return <String, StoreProduct>{
      for (final product in products) product.identifier: product,
    };
  }

  Future<void> purchase(StoreProduct product) async {
    await _ensureConfigured();
    await _sdk.purchase(product);
    await _sdk.syncPurchases();
  }

  Future<RestorePurchasesResult> restorePurchases() async {
    try {
      await _ensureConfigured();
      final customerInfo = await _sdk.restorePurchases();
      await _sdk.syncPurchases();
      final hasRestorableAccess = _hasRestorableAccess(customerInfo);
      return RestorePurchasesResult(
        status: hasRestorableAccess
            ? RestorePurchasesStatus.restored
            : RestorePurchasesStatus.noActivePurchases,
        customerInfo: customerInfo,
      );
    } catch (error) {
      return RestorePurchasesResult(
        status: RestorePurchasesStatus.failed,
        errorMessage: errorMessage(error),
      );
    }
  }

  static bool isPurchaseCancelled(Object error) {
    if (error is PlatformException) {
      return PurchasesErrorHelper.getErrorCode(error) ==
          PurchasesErrorCode.purchaseCancelledError;
    }
    return false;
  }

  static String? errorMessage(Object error) {
    if (error is PlatformException) {
      final message = error.message?.trim();
      if (message != null && message.isNotEmpty) {
        return message;
      }
    }
    final text = error.toString().trim();
    return text.isEmpty ? null : text;
  }

  Future<void> _ensureConfigured() async {
    if (!(_isSupportedPlatformOverride ?? isSupportedPlatform)) {
      throw StateError(
        'RevenueCat purchases are only supported on iOS and Android.',
      );
    }

    final apiKey = _apiKeyForCurrentPlatform;
    if (apiKey.isEmpty) {
      throw StateError('RevenueCat public SDK key is missing.');
    }

    final currentUserId = _currentUserIdProvider();
    final configured = await _sdk.isConfigured;
    if (!configured) {
      final configuration = PurchasesConfiguration(apiKey);
      if (currentUserId != null && currentUserId.isNotEmpty) {
        configuration.appUserID = currentUserId;
      }
      await _sdk.configure(configuration);
      return;
    }

    if (currentUserId != null && currentUserId.isNotEmpty) {
      final currentAppUserId = await _sdk.appUserId;
      if (currentAppUserId != currentUserId) {
        await _sdk.logIn(currentUserId);
      }
    }
  }

  bool _hasRestorableAccess(CustomerInfo customerInfo) {
    return customerInfo.entitlements.active.isNotEmpty ||
        customerInfo.activeSubscriptions.isNotEmpty ||
        customerInfo.nonSubscriptionTransactions.isNotEmpty;
  }

  String get _apiKeyForCurrentPlatform {
    return switch (defaultTargetPlatform) {
      TargetPlatform.iOS => _appleApiKeyOverride ?? _appleApiKey,
      TargetPlatform.android => _googleApiKeyOverride ?? _googleApiKey,
      _ => '',
    };
  }
}
