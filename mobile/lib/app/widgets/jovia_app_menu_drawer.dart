import 'package:flutter/foundation.dart' show kDebugMode;
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import 'package:mobile/app/tabs/profile_page_v9.dart';

import 'package:mobile/app/ai/revenuecat_service.dart';
import 'package:mobile/app/auth/account_service.dart';
import 'package:mobile/app/legal/external_link_service.dart';
import 'package:mobile/app/people/people_providers.dart';
import 'package:mobile/app/preferences/jovia_app_preferences_provider.dart';
import 'package:mobile/app/profile/profile_providers.dart';
import 'package:mobile/app/theme/app_theme_mode_provider.dart';
import 'package:mobile/design/theme/profile_theme_extension.dart';
import 'package:mobile/design/widgets/jovia_editorial.dart';
import 'package:mobile/l10n/app_localizations.dart';
import 'package:mobile/l10n/l10n.dart';

typedef JoviaAppMenuAction =
    Future<void> Function(BuildContext context, Map<String, dynamic>? profile);

/// Drawer'da kullanılan home v12 palet değerleri — home_page_v2.dart'taki
/// `_HomeV2Palette` ile birebir aynı. Ortak paleti lib/design'e taşıma
/// ihtiyacı doğarsa ikisini de tek kaynaktan besleyeceğiz.
class _HomeV2Ink {
  const _HomeV2Ink._();
  static const Color ink = Color(0xFF111111);
  static const Color fog = Color(0xFF444444);
  static const Color mist = Color(0xFF777777);
  static const Color silver = Color(0xFFAAAAAA);
  static const Color hairline = Color(0x14000000);
  static const Color paper = Color(0xFFFAFAF7);
  static const Color lime = Color(0xFFCAFF4D);
  static const Color limeText = Color(0xFF1A3300);
  static const Color blushDeep = Color(0xFFC76FA0);
}

String _notificationsSubtitle(AppLocalizations l10n, JoviaAppPreferences prefs) {
  final on = <String>[
    if (prefs.dailyBriefEnabled) l10n.menuDailySummary,
    if (prefs.skyAlertsEnabled) l10n.menuSkyEvents,
    if (prefs.socialAlertsEnabled) l10n.menuSocialActivity,
  ];
  if (on.isEmpty) return 'Tümü kapalı';
  return on.join(' · ');
}

class JoviaAppMenuDrawer extends ConsumerWidget {
  JoviaAppMenuDrawer({
    super.key,
    this.onEditProfile,
    this.onOpenPeople,
    this.onOpenCalendar,
    this.onOpenArchetype,
    this.currentUser,
    ExternalLinkService? externalLinkService,
    RevenueCatService? revenueCatService,
    AccountService? accountService,
    Future<void> Function()? onSignOut,
  }) : _externalLinkService =
           externalLinkService ?? const ExternalLinkService(),
       _revenueCatService = revenueCatService ?? RevenueCatService(),
       _accountService = accountService ?? AccountService(),
       _onSignOut = onSignOut;

  final JoviaAppMenuAction? onEditProfile;
  final JoviaAppMenuAction? onOpenPeople;
  final JoviaAppMenuAction? onOpenCalendar;
  final JoviaAppMenuAction? onOpenArchetype;
  final User? currentUser;
  final ExternalLinkService _externalLinkService;
  final RevenueCatService _revenueCatService;
  final AccountService _accountService;
  final Future<void> Function()? _onSignOut;

  static Future<void> closeThenRun(
    BuildContext context,
    JoviaAppMenuAction? action, {
    Map<String, dynamic>? profile,
  }) async {
    if (action == null) {
      return;
    }
    Navigator.of(context).pop();
    await Future<void>.delayed(const Duration(milliseconds: 180));
    if (!context.mounted) {
      return;
    }
    await action(context, profile);
  }

  Future<void> _restorePurchases(BuildContext context) async {
    Navigator.of(context).pop();
    await Future<void>.delayed(const Duration(milliseconds: 180));
    if (!context.mounted) {
      return;
    }

    final result = await _revenueCatService.restorePurchases();
    if (!context.mounted) {
      return;
    }

    final messenger = ScaffoldMessenger.of(context);
    switch (result.status) {
      case RestorePurchasesStatus.restored:
        messenger.showSnackBar(
          SnackBar(content: Text(context.l10n.restorePurchasesSuccess)),
        );
        break;
      case RestorePurchasesStatus.noActivePurchases:
        messenger.showSnackBar(
          SnackBar(content: Text(context.l10n.restorePurchasesNoActive)),
        );
        break;
      case RestorePurchasesStatus.failed:
        final errorMessage = (result.errorMessage ?? '').trim();
        messenger.showSnackBar(
          SnackBar(
            content: Text(
              errorMessage.isNotEmpty
                  ? errorMessage
                  : context.l10n.restorePurchasesError,
            ),
          ),
        );
        break;
    }
  }

  Future<void> _openExternalLink(
    BuildContext context,
    Future<void> Function() openLink,
  ) async {
    Navigator.of(context).pop();
    await Future<void>.delayed(const Duration(milliseconds: 180));
    if (!context.mounted) {
      return;
    }
    try {
      await openLink();
    } catch (_) {
      if (!context.mounted) {
        return;
      }
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(context.l10n.externalLinkOpenFailed)),
      );
    }
  }

  Future<void> _confirmDeleteAccount(BuildContext context) async {
    Navigator.of(context).pop();
    await Future<void>.delayed(const Duration(milliseconds: 180));
    if (!context.mounted) {
      return;
    }

    final confirmed = await showDialog<bool>(
      context: context,
      builder: (dialogContext) {
        final l10n = dialogContext.l10n;
        return AlertDialog(
          title: Text(l10n.deleteAccountDialogTitle),
          content: Text(
            '${l10n.deleteAccountDialogBody}\n\n${l10n.deleteAccountSubscriptionNote}',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(dialogContext).pop(false),
              child: Text(l10n.deleteAccountCancel),
            ),
            FilledButton(
              onPressed: () => Navigator.of(dialogContext).pop(true),
              child: Text(l10n.deleteAccountConfirm),
            ),
          ],
        );
      },
    );
    if (confirmed != true || !context.mounted) {
      return;
    }

    _showAccountDeletionProgress(context);
    try {
      await _accountService.deleteCurrentAccount();
      if (context.mounted) {
        Navigator.of(context, rootNavigator: true).pop();
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(context.l10n.deleteAccountSuccess)),
        );
      }
      try {
        await _signOut();
      } catch (_) {
        // The backend may already have invalidated the remote session.
      }
    } on AccountDeletionException catch (error) {
      if (context.mounted) {
        Navigator.of(context, rootNavigator: true).pop();
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              error.message.trim().isEmpty
                  ? context.l10n.deleteAccountError
                  : error.message,
            ),
          ),
        );
      }
    } catch (_) {
      if (context.mounted) {
        Navigator.of(context, rootNavigator: true).pop();
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(context.l10n.deleteAccountError)),
        );
      }
    }
  }

  void _showAccountDeletionProgress(BuildContext context) {
    showDialog<void>(
      context: context,
      barrierDismissible: false,
      builder: (dialogContext) {
        return AlertDialog(
          content: Row(
            children: [
              const SizedBox(
                width: 20,
                height: 20,
                child: CircularProgressIndicator(strokeWidth: 2),
              ),
              const SizedBox(width: 16),
              Expanded(child: Text(dialogContext.l10n.deleteAccountProgress)),
            ],
          ),
        );
      },
    );
  }

  Future<void> _signOut() async {
    if (_onSignOut != null) {
      await _onSignOut();
      return;
    }
    await Supabase.instance.client.auth.signOut();
  }

  Future<void> _showThemeSheet(BuildContext context, WidgetRef ref) async {
    final l10n = context.l10n;
    await _showEditSheet(
      context: context,
      title: l10n.menuThemeMode,
      builder: (sheetContext) {
        return Consumer(
          builder: (context, ref, _) {
            final mode = ref.watch(joviaThemeModeProvider);
            return Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              mainAxisSize: MainAxisSize.min,
              children: [
                _DrawerRadioRow(
                  label: l10n.themeModeLight,
                  selected: mode == JoviaThemeMode.light,
                  onTap: () => ref
                      .read(joviaThemeModeProvider.notifier)
                      .setMode(JoviaThemeMode.light),
                ),
                _DrawerRadioRow(
                  label: l10n.themeModeDark,
                  selected: mode == JoviaThemeMode.dark,
                  onTap: () => ref
                      .read(joviaThemeModeProvider.notifier)
                      .setMode(JoviaThemeMode.dark),
                ),
              ],
            );
          },
        );
      },
    );
  }

  Future<void> _showLanguageSheet(BuildContext context, WidgetRef ref) async {
    final l10n = context.l10n;
    await _showEditSheet(
      context: context,
      title: l10n.menuLanguage,
      builder: (sheetContext) {
        return Consumer(
          builder: (context, ref, _) {
            final locale = ref.watch(joviaAppPreferencesProvider).locale;
            return Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              mainAxisSize: MainAxisSize.min,
              children: [
                _DrawerRadioRow(
                  label: JoviaAppLocale.tr.label,
                  selected: locale == JoviaAppLocale.tr,
                  onTap: () => ref
                      .read(joviaAppPreferencesProvider.notifier)
                      .setLocale(JoviaAppLocale.tr),
                ),
                _DrawerRadioRow(
                  label: JoviaAppLocale.en.label,
                  selected: locale == JoviaAppLocale.en,
                  onTap: () => ref
                      .read(joviaAppPreferencesProvider.notifier)
                      .setLocale(JoviaAppLocale.en),
                ),
              ],
            );
          },
        );
      },
    );
  }

  Future<void> _showNotificationsSheet(
    BuildContext context,
    WidgetRef ref,
  ) async {
    final l10n = context.l10n;
    await _showEditSheet(
      context: context,
      title: l10n.menuNotificationPreferences,
      builder: (sheetContext) {
        return Consumer(
          builder: (context, ref, _) {
            final prefs = ref.watch(joviaAppPreferencesProvider);
            final notifier = ref.read(joviaAppPreferencesProvider.notifier);
            return Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              mainAxisSize: MainAxisSize.min,
              children: [
                _DrawerToggleRow(
                  title: l10n.menuDailySummary,
                  subtitle: l10n.menuDailySummarySubtitle,
                  value: prefs.dailyBriefEnabled,
                  onChanged: notifier.setDailyBriefEnabled,
                ),
                _DrawerToggleRow(
                  title: l10n.menuSkyEvents,
                  subtitle: l10n.menuSkyEventsSubtitle,
                  value: prefs.skyAlertsEnabled,
                  onChanged: notifier.setSkyAlertsEnabled,
                ),
                _DrawerToggleRow(
                  title: l10n.menuSocialActivity,
                  subtitle: l10n.menuSocialActivitySubtitle,
                  value: prefs.socialAlertsEnabled,
                  onChanged: notifier.setSocialAlertsEnabled,
                ),
              ],
            );
          },
        );
      },
    );
  }

  Future<void> _showEditSheet({
    required BuildContext context,
    required String title,
    required WidgetBuilder builder,
  }) async {
    await showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (sheetContext) {
        return SafeArea(
          top: false,
          child: Padding(
            padding: EdgeInsets.only(
              left: 12,
              right: 12,
              bottom: MediaQuery.of(sheetContext).viewInsets.bottom + 12,
              top: 12,
            ),
            child: Container(
              decoration: const BoxDecoration(
                color: _HomeV2Ink.paper,
                borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
              ),
              padding: const EdgeInsets.fromLTRB(24, 20, 24, 28),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          title,
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.w500,
                            color: _HomeV2Ink.ink,
                            letterSpacing: -0.3,
                          ),
                        ),
                      ),
                      InkWell(
                        onTap: () => Navigator.of(sheetContext).pop(),
                        customBorder: const CircleBorder(),
                        child: const Padding(
                          padding: EdgeInsets.all(4),
                          child: Icon(
                            Icons.close,
                            size: 20,
                            color: _HomeV2Ink.mist,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Container(height: 0.5, color: _HomeV2Ink.hairline),
                  const SizedBox(height: 4),
                  builder(sheetContext),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final profile = context.profileTheme;
    final l10n = context.l10n;
    final authUser = currentUser ?? Supabase.instance.client.auth.currentUser;
    final profileMap = ref.watch(userProfileProvider).asData?.value;
    final peopleCount = ref.watch(peopleListProvider).asData?.value.length ?? 0;
    final prefs = ref.watch(joviaAppPreferencesProvider);
    final themeMode = ref.watch(joviaThemeModeProvider);
    final hasBirthData = _hasBirthData(profileMap);
    final displayName = _displayName(profileMap, authUser);
    final username = _displayUsername(profileMap, authUser);
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final drawerWidth = (MediaQuery.sizeOf(context).width * 0.82)
        .clamp(304.0, 368.0)
        .toDouble();
    final shellColor = isDark
        ? const Color(0xFF11131A)
        : Color.alphaBlend(
            profile.colors.surface.withValues(alpha: 0.97),
            Colors.white,
          );
    final shellBorder = isDark
        ? Colors.white.withValues(alpha: 0.08)
        : profile.colors.borderSubtle.withValues(alpha: 0.94);

    return Drawer(
      width: drawerWidth,
      elevation: 0,
      backgroundColor: Colors.transparent,
      surfaceTintColor: Colors.transparent,
      shadowColor: Colors.black.withValues(alpha: 0.2),
      child: SafeArea(
        left: false,
        child: Padding(
          padding: const EdgeInsets.fromLTRB(12, 12, 14, 12),
          child: DecoratedBox(
            decoration: BoxDecoration(
              color: shellColor,
              borderRadius: BorderRadius.circular(30),
              border: Border.all(color: shellBorder),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withValues(alpha: isDark ? 0.3 : 0.1),
                  blurRadius: 32,
                  offset: const Offset(-10, 14),
                  spreadRadius: -22,
                ),
              ],
            ),
            child: Padding(
              padding: const EdgeInsets.fromLTRB(16, 16, 16, 16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      JoviaBrandMark(width: 54, opacity: isDark ? 0.84 : 0.9),
                      const Spacer(),
                      JoviaGlassIconButton(
                        onTap: () => Navigator.of(context).pop(),
                        size: 40,
                        child: Icon(
                          Icons.close_rounded,
                          size: 18,
                          color: profile.colors.text,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  JoviaReveal(
                    delay: const Duration(milliseconds: 40),
                    child: _JoviaAppMenuIdentityCard(
                      displayName: displayName,
                      username: username,
                    ),
                  ),
                  const SizedBox(height: 18),
                  Expanded(
                    child: SingleChildScrollView(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          JoviaReveal(
                            delay: const Duration(milliseconds: 80),
                            child: _JoviaAppMenuSectionLabel(
                              label: l10n.menuQuickAccess,
                            ),
                          ),
                          const SizedBox(height: 8),
                          if (onEditProfile != null)
                            JoviaReveal(
                              delay: const Duration(milliseconds: 110),
                              child: _JoviaAppMenuActionTile(
                                title: l10n.menuEditProfile,
                                subtitle: l10n.menuEditProfileSubtitle,
                                iconAsset: JoviaUiAsset.settingsRings,
                                onTap: () => closeThenRun(
                                  context,
                                  onEditProfile,
                                  profile: profileMap,
                                ),
                              ),
                            ),
                          if (onEditProfile != null) const SizedBox(height: 10),
                          if (kDebugMode) ...[
                            JoviaReveal(
                              delay: const Duration(milliseconds: 130),
                              child: _JoviaAppMenuActionTile(
                                title: 'Profil v9 (yeni)',
                                subtitle:
                                    'Paralel "iceberg" tasarımı — yüzey + Haritam + Tam Okuma',
                                iconAsset: JoviaUiAsset.orbitPlanet,
                                trailingLabel: 'DEV',
                                onTap: () async {
                                  // Drawer dışındaki rootNavigator'ı pop'tan
                                  // ÖNCE yakala (drawer kapanınca bu context
                                  // dispose olur). GoRouter'ı by-pass edip
                                  // doğrudan MaterialPageRoute push ediyoruz —
                                  // dev sayfası için route reload gerekmez.
                                  final navigator = Navigator.of(
                                    context,
                                    rootNavigator: true,
                                  );
                                  Navigator.of(context).pop();
                                  await Future<void>.delayed(
                                    const Duration(milliseconds: 180),
                                  );
                                  navigator.push(
                                    MaterialPageRoute<void>(
                                      builder: (_) => const ProfilePageV9(),
                                    ),
                                  );
                                },
                              ),
                            ),
                            const SizedBox(height: 10),
                          ],
                          if (onOpenPeople != null)
                            JoviaReveal(
                              delay: const Duration(milliseconds: 150),
                              child: _JoviaAppMenuActionTile(
                                title: peopleCount > 0
                                    ? l10n.menuManagePeople
                                    : l10n.menuAddPerson,
                                subtitle: l10n.menuPeopleSubtitle,
                                iconAsset: JoviaUiAsset.connectionsTwins,
                                onTap: () => closeThenRun(
                                  context,
                                  onOpenPeople,
                                  profile: profileMap,
                                ),
                              ),
                            ),
                          if (onOpenPeople != null) const SizedBox(height: 10),
                          if (onOpenCalendar != null)
                            JoviaReveal(
                              delay: const Duration(milliseconds: 190),
                              child: _JoviaAppMenuActionTile(
                                title: l10n.menuCalendar,
                                subtitle: l10n.menuCalendarSubtitle,
                                iconAsset: JoviaUiAsset.calendarLunar,
                                onTap: () => closeThenRun(
                                  context,
                                  onOpenCalendar,
                                  profile: profileMap,
                                ),
                              ),
                            ),
                          if (onOpenCalendar != null)
                            const SizedBox(height: 10),
                          if (onOpenArchetype != null)
                            JoviaReveal(
                              delay: const Duration(milliseconds: 230),
                              child: _JoviaAppMenuActionTile(
                                title: hasBirthData
                                    ? l10n.menuArchetypeExperience
                                    : l10n.menuCompleteBirthData,
                                subtitle: hasBirthData
                                    ? l10n.menuArchetypeSubtitle
                                    : l10n.menuCompleteBirthDataSubtitle,
                                iconAsset: hasBirthData
                                    ? JoviaUiAsset.orbitPlanet
                                    : JoviaUiAsset.editPen,
                                onTap: () => closeThenRun(
                                  context,
                                  onOpenArchetype,
                                  profile: profileMap,
                                ),
                              ),
                            ),
                          const SizedBox(height: 18),
                          JoviaReveal(
                            delay: const Duration(milliseconds: 270),
                            child: _JoviaAppMenuSectionLabel(
                              label: l10n.menuPreferences,
                            ),
                          ),
                          const SizedBox(height: 8),
                          JoviaReveal(
                            delay: const Duration(milliseconds: 310),
                            child: _JoviaAppMenuActionTile(
                              title: l10n.menuThemeMode,
                              subtitle: themeMode == JoviaThemeMode.dark
                                  ? l10n.themeModeDark
                                  : l10n.themeModeLight,
                              iconAsset: JoviaUiAsset.settingsRings,
                              onTap: () => _showThemeSheet(context, ref),
                            ),
                          ),
                          JoviaReveal(
                            delay: const Duration(milliseconds: 330),
                            child: _JoviaAppMenuActionTile(
                              title: l10n.menuLanguage,
                              subtitle: prefs.locale.label,
                              iconAsset: JoviaUiAsset.editPen,
                              onTap: () => _showLanguageSheet(context, ref),
                            ),
                          ),
                          JoviaReveal(
                            delay: const Duration(milliseconds: 350),
                            child: _JoviaAppMenuActionTile(
                              title: l10n.menuNotificationPreferences,
                              subtitle: _notificationsSubtitle(l10n, prefs),
                              iconAsset: JoviaUiAsset.settingsRings,
                              onTap: () =>
                                  _showNotificationsSheet(context, ref),
                            ),
                          ),
                          const SizedBox(height: 18),
                          JoviaReveal(
                            delay: const Duration(milliseconds: 360),
                            child: _JoviaAppMenuSectionLabel(
                              label: l10n.menuMembership,
                            ),
                          ),
                          const SizedBox(height: 8),
                          JoviaReveal(
                            delay: const Duration(milliseconds: 390),
                            child: _JoviaAppMenuActionTile(
                              title: l10n.menuPremiumSubscription,
                              subtitle: prefs.premiumInterest
                                  ? l10n.menuPremiumInterestSubtitle
                                  : l10n.menuPremiumDefaultSubtitle,
                              iconAsset: JoviaUiAsset.orbitPlanet,
                              trailingLabel: prefs.premiumInterest
                                  ? l10n.menuInList
                                  : l10n.menuSoon,
                              onTap: () => _showPremiumSheet(context, ref),
                            ),
                          ),
                          const SizedBox(height: 10),
                          JoviaReveal(
                            delay: const Duration(milliseconds: 410),
                            child: _JoviaAppMenuActionTile(
                              title: l10n.restorePurchasesTitle,
                              subtitle: l10n.restorePurchasesDescription,
                              iconAsset: JoviaUiAsset.checkSeal,
                              onTap: () => _restorePurchases(context),
                            ),
                          ),
                          const SizedBox(height: 18),
                          JoviaReveal(
                            delay: const Duration(milliseconds: 430),
                            child: _JoviaAppMenuSectionLabel(
                              label: l10n.menuInfoAndSupport,
                            ),
                          ),
                          const SizedBox(height: 8),
                          JoviaReveal(
                            delay: const Duration(milliseconds: 450),
                            child: _JoviaAppMenuActionTile(
                              title: l10n.privacyPolicyTitle,
                              subtitle: l10n.privacyPolicyDescription,
                              iconAsset: JoviaUiAsset.settingsRings,
                              onTap: () => _openExternalLink(
                                context,
                                _externalLinkService.openPrivacyPolicy,
                              ),
                            ),
                          ),
                          const SizedBox(height: 10),
                          JoviaReveal(
                            delay: const Duration(milliseconds: 470),
                            child: _JoviaAppMenuActionTile(
                              title: l10n.termsOfUseTitle,
                              subtitle: l10n.termsOfUseDescription,
                              iconAsset: JoviaUiAsset.editPen,
                              onTap: () => _openExternalLink(
                                context,
                                _externalLinkService.openTermsOfUse,
                              ),
                            ),
                          ),
                          const SizedBox(height: 10),
                          JoviaReveal(
                            delay: const Duration(milliseconds: 490),
                            child: _JoviaAppMenuActionTile(
                              title: l10n.supportTitle,
                              subtitle: l10n.supportDescription,
                              iconAsset: JoviaUiAsset.connectionsTwins,
                              onTap: () => _openExternalLink(
                                context,
                                _externalLinkService.openSupport,
                              ),
                            ),
                          ),
                          const SizedBox(height: 18),
                          JoviaReveal(
                            delay: const Duration(milliseconds: 510),
                            child: _JoviaAppMenuSectionLabel(
                              label: l10n.menuAccount,
                            ),
                          ),
                          const SizedBox(height: 8),
                          JoviaReveal(
                            delay: const Duration(milliseconds: 530),
                            child: _JoviaAppMenuActionTile(
                              title: l10n.deleteAccountTitle,
                              subtitle: l10n.deleteAccountDescription,
                              iconAsset: JoviaUiAsset.logoutArc,
                              danger: true,
                              onTap: () => _confirmDeleteAccount(context),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 14),
                  JoviaReveal(
                    delay: const Duration(milliseconds: 560),
                    child: _JoviaAppMenuActionTile(
                      title: l10n.menuSignOut,
                      subtitle: l10n.menuSignOutSubtitle,
                      iconAsset: JoviaUiAsset.logoutArc,
                      danger: true,
                      onTap: () async {
                        Navigator.of(context).pop();
                        await Future<void>.delayed(
                          const Duration(milliseconds: 180),
                        );
                        await _signOut();
                      },
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Future<void> _showPremiumSheet(BuildContext context, WidgetRef ref) async {
    final profile = context.profileTheme;
    final l10n = context.l10n;
    await showModalBottomSheet<void>(
      context: context,
      backgroundColor: Colors.transparent,
      isScrollControlled: true,
      builder: (sheetContext) {
        return Consumer(
          builder: (context, ref, _) {
            final prefs = ref.watch(joviaAppPreferencesProvider);
            return Padding(
              padding: EdgeInsets.fromLTRB(
                14,
                14,
                14,
                MediaQuery.of(sheetContext).viewInsets.bottom + 14,
              ),
              child: JoviaSurfaceCard(
                radius: 30,
                padding: const EdgeInsets.fromLTRB(18, 18, 18, 18),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      l10n.premiumSheetTitle,
                      style: profile.typography.h2.copyWith(fontSize: 24),
                    ),
                    const SizedBox(height: 10),
                    Text(
                      l10n.premiumSheetBody,
                      style: profile.typography.bodyCompact.copyWith(
                        color: profile.colors.textLight,
                      ),
                    ),
                    const SizedBox(height: 14),
                    _JoviaAppMenuBullet(text: l10n.premiumBulletIdentity),
                    const SizedBox(height: 8),
                    _JoviaAppMenuBullet(text: l10n.premiumBulletTiming),
                    const SizedBox(height: 8),
                    _JoviaAppMenuBullet(text: l10n.premiumBulletEarlyAccess),
                    const SizedBox(height: 16),
                    SizedBox(
                      width: double.infinity,
                      child: JoviaPrimaryButton(
                        label: prefs.premiumInterest
                            ? l10n.premiumAlreadyInList
                            : l10n.premiumNotifyMe,
                        onTap: () async {
                          await ref
                              .read(joviaAppPreferencesProvider.notifier)
                              .setPremiumInterest(true);
                          if (!sheetContext.mounted) {
                            return;
                          }
                          Navigator.of(sheetContext).pop();
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(content: Text(l10n.premiumNotifySnackbar)),
                          );
                        },
                      ),
                    ),
                  ],
                ),
              ),
            );
          },
        );
      },
    );
  }
}

/// Home v12 tonunda sade kimlik başlığı — sadece isim + handle.
/// Önceki versiyondaki "Arketip hazır / 10 kişi" çip yığını kaldırıldı;
/// o bilgiler artık ilgili liste satırlarının alt metninde.
class _JoviaAppMenuIdentityCard extends StatelessWidget {
  const _JoviaAppMenuIdentityCard({
    required this.displayName,
    required this.username,
  });

  final String displayName;
  final String username;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(4, 4, 4, 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            displayName,
            style: const TextStyle(
              fontSize: 22,
              fontWeight: FontWeight.w500,
              color: _HomeV2Ink.ink,
              letterSpacing: -0.4,
              height: 1.2,
            ),
          ),
          const SizedBox(height: 6),
          Text(
            username,
            style: const TextStyle(
              fontSize: 12,
              color: _HomeV2Ink.mist,
              letterSpacing: 0.1,
              height: 1.2,
            ),
          ),
        ],
      ),
    );
  }
}

/// Home v12 mono uppercase eyebrow — altında hairline ayırıcı.
class _JoviaAppMenuSectionLabel extends StatelessWidget {
  const _JoviaAppMenuSectionLabel({required this.label});

  final String label;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text(
          label.toUpperCase(),
          style: const TextStyle(
            fontSize: 8.5,
            letterSpacing: 2.4,
            color: _HomeV2Ink.silver,
            fontWeight: FontWeight.w400,
          ),
        ),
        const SizedBox(height: 6),
        Container(height: 0.5, color: _HomeV2Ink.hairline),
      ],
    );
  }
}

class _JoviaAppMenuActionTile extends StatelessWidget {
  const _JoviaAppMenuActionTile({
    required this.title,
    required this.subtitle,
    required this.iconAsset,
    required this.onTap,
    this.trailingLabel,
    this.danger = false,
  });

  final String title;
  final String subtitle;
  final JoviaUiAsset iconAsset;
  final VoidCallback onTap;
  final String? trailingLabel;
  final bool danger;

  @override
  Widget build(BuildContext context) {
    final titleColor = danger ? _HomeV2Ink.blushDeep : _HomeV2Ink.ink;
    return InkWell(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 16),
        decoration: const BoxDecoration(
          border: Border(
            bottom: BorderSide(color: _HomeV2Ink.hairline, width: 0.5),
          ),
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          title,
                          style: TextStyle(
                            fontSize: 15,
                            fontWeight: FontWeight.w500,
                            color: titleColor,
                            letterSpacing: -0.2,
                            height: 1.2,
                          ),
                        ),
                      ),
                      if ((trailingLabel ?? '').trim().isNotEmpty)
                        Padding(
                          padding: const EdgeInsets.only(left: 8),
                          child: Text(
                            (trailingLabel ?? '').trim().toUpperCase(),
                            style: const TextStyle(
                              fontSize: 9,
                              letterSpacing: 1.4,
                              color: _HomeV2Ink.silver,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(
                    subtitle,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      fontSize: 11.5,
                      color: _HomeV2Ink.mist,
                      height: 1.35,
                      letterSpacing: -0.05,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(width: 12),
            Padding(
              padding: const EdgeInsets.only(top: 2),
              child: Icon(
                Icons.arrow_forward,
                size: 14,
                color: _HomeV2Ink.silver,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _JoviaAppMenuBullet extends StatelessWidget {
  const _JoviaAppMenuBullet({required this.text});

  final String text;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.only(top: 4),
          child: Container(
            width: 6,
            height: 6,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: profile.colors.warmAccent,
            ),
          ),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: Text(
            text,
            style: profile.typography.bodyCompact.copyWith(
              color: profile.colors.textLight,
            ),
          ),
        ),
      ],
    );
  }
}

bool _hasBirthData(Map<String, dynamic>? profile) {
  if (profile == null) {
    return false;
  }
  final birthDate = (profile['birth_date'] ?? '').toString().trim();
  final birthTime = (profile['birth_time'] ?? '').toString().trim();
  final city = (profile['city'] ?? '').toString().trim();
  final country = (profile['country'] ?? '').toString().trim();
  final place = (profile['place'] ?? '').toString().trim();
  return birthDate.isNotEmpty &&
      birthTime.isNotEmpty &&
      (place.isNotEmpty || city.isNotEmpty || country.isNotEmpty);
}

String _displayName(Map<String, dynamic>? profile, User? user) {
  final fromProfile = (profile?['full_name'] ?? profile?['name'] ?? '')
      .toString()
      .trim();
  if (fromProfile.isNotEmpty) {
    return fromProfile;
  }
  final fromMail = (user?.email ?? '').split('@').first.trim();
  if (fromMail.isNotEmpty) {
    return fromMail;
  }
  return 'Profil';
}

String _displayUsername(Map<String, dynamic>? profile, User? user) {
  final candidate =
      [profile?['username'], profile?['handle'], user?.email?.split('@').first]
          .map((item) => (item ?? '').toString().trim())
          .firstWhere((item) => item.isNotEmpty, orElse: () => 'profil');
  return candidate.startsWith('@') ? candidate : '@$candidate';
}

/// Bottom-sheet tek seçimli satır (tema, dil gibi).
class _DrawerRadioRow extends StatelessWidget {
  const _DrawerRadioRow({
    required this.label,
    required this.selected,
    required this.onTap,
  });

  final String label;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: () {
        onTap();
        Navigator.of(context).maybePop();
      },
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 16),
        decoration: const BoxDecoration(
          border: Border(
            bottom: BorderSide(color: _HomeV2Ink.hairline, width: 0.5),
          ),
        ),
        child: Row(
          children: [
            Expanded(
              child: Text(
                label,
                style: TextStyle(
                  fontSize: 15,
                  fontWeight: selected ? FontWeight.w500 : FontWeight.w400,
                  color: selected ? _HomeV2Ink.ink : _HomeV2Ink.fog,
                  letterSpacing: -0.2,
                ),
              ),
            ),
            if (selected)
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 8,
                  vertical: 3,
                ),
                decoration: BoxDecoration(
                  color: _HomeV2Ink.lime,
                  borderRadius: BorderRadius.circular(3),
                ),
                child: const Text(
                  'SEÇİLİ',
                  style: TextStyle(
                    fontSize: 8.5,
                    letterSpacing: 1.8,
                    color: _HomeV2Ink.limeText,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}

/// Bottom-sheet içinde bireysel bildirim toggle satırı.
class _DrawerToggleRow extends StatelessWidget {
  const _DrawerToggleRow({
    required this.title,
    required this.subtitle,
    required this.value,
    required this.onChanged,
  });

  final String title;
  final String subtitle;
  final bool value;
  final ValueChanged<bool> onChanged;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 14),
      decoration: const BoxDecoration(
        border: Border(
          bottom: BorderSide(color: _HomeV2Ink.hairline, width: 0.5),
        ),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.w500,
                    color: _HomeV2Ink.ink,
                    letterSpacing: -0.2,
                  ),
                ),
                const SizedBox(height: 3),
                Text(
                  subtitle,
                  style: const TextStyle(
                    fontSize: 11.5,
                    color: _HomeV2Ink.mist,
                    height: 1.35,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 12),
          Transform.scale(
            scale: 0.8,
            child: CupertinoSwitchFallback(
              value: value,
              onChanged: onChanged,
              activeColor: _HomeV2Ink.lime,
            ),
          ),
        ],
      ),
    );
  }
}

/// Switch için `Switch.adaptive` kullanılır; CupertinoSwitch gerekmesin.
class CupertinoSwitchFallback extends StatelessWidget {
  const CupertinoSwitchFallback({
    super.key,
    required this.value,
    required this.onChanged,
    required this.activeColor,
  });

  final bool value;
  final ValueChanged<bool> onChanged;
  final Color activeColor;

  @override
  Widget build(BuildContext context) {
    return Switch.adaptive(
      value: value,
      onChanged: onChanged,
      activeThumbColor: Colors.white,
      activeTrackColor: activeColor,
      inactiveTrackColor: _HomeV2Ink.hairline,
      inactiveThumbColor: Colors.white,
    );
  }
}
