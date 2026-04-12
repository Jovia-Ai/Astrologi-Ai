import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:purchases_flutter/purchases_flutter.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

class RevenueCatService {
  RevenueCatService();

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
      ...await Purchases.getProducts(<String>[
        q1ProductId,
        q5ProductId,
        q15ProductId,
      ], productCategory: ProductCategory.nonSubscription),
      ...await Purchases.getProducts(<String>[proMonthlyProductId]),
    ];
    return <String, StoreProduct>{
      for (final product in products) product.identifier: product,
    };
  }

  Future<void> purchase(StoreProduct product) async {
    await _ensureConfigured();
    await Purchases.purchase(PurchaseParams.storeProduct(product));
    await Purchases.syncPurchases();
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
    if (!isSupportedPlatform) {
      throw StateError(
        'RevenueCat purchases are only supported on iOS and Android.',
      );
    }

    final apiKey = _apiKeyForCurrentPlatform;
    if (apiKey.isEmpty) {
      throw StateError('RevenueCat public SDK key is missing.');
    }

    final currentUserId = Supabase.instance.client.auth.currentUser?.id;
    final isConfigured = await Purchases.isConfigured;
    if (!isConfigured) {
      final configuration = PurchasesConfiguration(apiKey);
      if (currentUserId != null && currentUserId.isNotEmpty) {
        configuration.appUserID = currentUserId;
      }
      await Purchases.configure(configuration);
      return;
    }

    if (currentUserId != null && currentUserId.isNotEmpty) {
      final currentAppUserId = await Purchases.appUserID;
      if (currentAppUserId != currentUserId) {
        await Purchases.logIn(currentUserId);
      }
    }
  }

  String get _apiKeyForCurrentPlatform {
    return switch (defaultTargetPlatform) {
      TargetPlatform.iOS => _appleApiKey,
      TargetPlatform.android => _googleApiKey,
      _ => '',
    };
  }
}
