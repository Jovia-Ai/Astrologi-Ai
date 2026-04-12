import 'package:flutter/material.dart';
import 'package:purchases_flutter/purchases_flutter.dart';

import 'package:mobile/app/ai/revenuecat_service.dart';
import 'package:mobile/l10n/app_localizations.dart';
import 'package:mobile/l10n/l10n.dart';

Future<void> showAiPaywallSheet(
  BuildContext context, {
  required VoidCallback onPurchased,
}) {
  return showModalBottomSheet<void>(
    context: context,
    isScrollControlled: true,
    backgroundColor: Colors.transparent,
    builder: (_) => _AiPaywallSheet(onPurchased: onPurchased),
  );
}

class _AiPaywallSheet extends StatefulWidget {
  const _AiPaywallSheet({required this.onPurchased});

  final VoidCallback onPurchased;

  @override
  State<_AiPaywallSheet> createState() => _AiPaywallSheetState();
}

class _AiPaywallSheetState extends State<_AiPaywallSheet> {
  final RevenueCatService _revenueCatService = RevenueCatService();
  bool _loading = true;
  String? _errorMessage;
  String? _busyProductId;
  Map<String, StoreProduct> _productsById = const <String, StoreProduct>{};

  @override
  void initState() {
    super.initState();
    _loadProducts();
  }

  Future<void> _loadProducts() async {
    if (!RevenueCatService.isSupportedPlatform) {
      setState(() {
        _loading = false;
        _errorMessage = 'unsupported';
      });
      return;
    }

    try {
      final products = await _revenueCatService.loadProducts();
      if (!mounted) {
        return;
      }
      setState(() {
        _productsById = products;
        _loading = false;
        _errorMessage = null;
      });
    } catch (error) {
      if (!mounted) {
        return;
      }
      setState(() {
        _loading = false;
        _errorMessage = RevenueCatService.errorMessage(error);
      });
    }
  }

  Future<void> _purchase(_PaywallOption option) async {
    final product = _productsById[option.productId];
    if (product == null) {
      return;
    }

    setState(() => _busyProductId = option.productId);
    try {
      await _revenueCatService.purchase(product);
      if (!mounted) {
        return;
      }
      widget.onPurchased();
      Navigator.of(context).pop();
    } catch (error) {
      if (!mounted) {
        return;
      }
      if (!RevenueCatService.isPurchaseCancelled(error)) {
        final message =
            RevenueCatService.errorMessage(error) ??
            context.l10n.aiPaywallUnavailable;
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text(message)));
      }
    } finally {
      if (mounted) {
        setState(() => _busyProductId = null);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final l10n = context.l10n;
    final options = _paywallOptions(l10n);
    final resolvedError = _errorMessage == 'unsupported'
        ? l10n.aiPurchaseNotSupported
        : _errorMessage;

    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.fromLTRB(16, 16, 16, 24),
        child: DecoratedBox(
          decoration: BoxDecoration(
            color: theme.colorScheme.surface,
            borderRadius: BorderRadius.circular(28),
            border: Border.all(color: theme.colorScheme.outlineVariant),
          ),
          child: SingleChildScrollView(
            child: Padding(
              padding: const EdgeInsets.fromLTRB(20, 20, 20, 24),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    l10n.aiPaywallTitle,
                    style: theme.textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(l10n.aiPaywallBody, style: theme.textTheme.bodyMedium),
                  const SizedBox(height: 16),
                  if (_loading)
                    Padding(
                      padding: const EdgeInsets.symmetric(vertical: 24),
                      child: Row(
                        children: [
                          const SizedBox(
                            width: 18,
                            height: 18,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          ),
                          const SizedBox(width: 12),
                          Text(l10n.aiPaywallLoading),
                        ],
                      ),
                    )
                  else ...[
                    if (resolvedError != null) ...[
                      Text(
                        resolvedError,
                        style: theme.textTheme.bodyMedium?.copyWith(
                          color: theme.colorScheme.error,
                        ),
                      ),
                      const SizedBox(height: 12),
                    ],
                    for (final option in options) ...[
                      _AiPaywallOptionCard(
                        option: option,
                        storeProduct: _productsById[option.productId],
                        busy: _busyProductId == option.productId,
                        enabled: _productsById.containsKey(option.productId),
                        onPressed: () => _purchase(option),
                      ),
                      const SizedBox(height: 12),
                    ],
                    Text(
                      l10n.aiPaywallRestoreHint,
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  List<_PaywallOption> _paywallOptions(AppLocalizations l10n) {
    return <_PaywallOption>[
      _PaywallOption(
        productId: RevenueCatService.q1ProductId,
        title: l10n.aiProductQ1Title,
        subtitle: l10n.aiProductQ1Subtitle,
      ),
      _PaywallOption(
        productId: RevenueCatService.q5ProductId,
        title: l10n.aiProductQ5Title,
        subtitle: l10n.aiProductQ5Subtitle,
      ),
      _PaywallOption(
        productId: RevenueCatService.q15ProductId,
        title: l10n.aiProductQ15Title,
        subtitle: l10n.aiProductQ15Subtitle,
      ),
      _PaywallOption(
        productId: RevenueCatService.proMonthlyProductId,
        title: l10n.aiProductProTitle,
        subtitle: l10n.aiProductProSubtitle,
      ),
    ];
  }
}

class _AiPaywallOptionCard extends StatelessWidget {
  const _AiPaywallOptionCard({
    required this.option,
    required this.storeProduct,
    required this.busy,
    required this.enabled,
    required this.onPressed,
  });

  final _PaywallOption option;
  final StoreProduct? storeProduct;
  final bool busy;
  final bool enabled;
  final VoidCallback onPressed;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final priceLabel =
        storeProduct?.priceString ?? context.l10n.aiStorePriceUnavailable;
    final title = (storeProduct?.title.trim().isNotEmpty ?? false)
        ? storeProduct!.title.trim()
        : option.title;
    return DecoratedBox(
      decoration: BoxDecoration(
        color: theme.colorScheme.surfaceContainerHighest.withValues(alpha: 0.4),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: theme.colorScheme.outlineVariant),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: theme.textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    option.subtitle,
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(width: 12),
            FilledButton(
              onPressed: enabled && !busy ? onPressed : null,
              child: busy
                  ? const SizedBox(
                      width: 18,
                      height: 18,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : Text(priceLabel),
            ),
          ],
        ),
      ),
    );
  }
}

class _PaywallOption {
  const _PaywallOption({
    required this.productId,
    required this.title,
    required this.subtitle,
  });

  final String productId;
  final String title;
  final String subtitle;
}
