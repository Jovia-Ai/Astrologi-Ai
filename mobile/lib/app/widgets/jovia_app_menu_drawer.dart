import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import 'package:mobile/app/people/people_providers.dart';
import 'package:mobile/app/preferences/jovia_app_preferences_provider.dart';
import 'package:mobile/app/profile/profile_providers.dart';
import 'package:mobile/app/theme/app_theme_mode_provider.dart';
import 'package:mobile/design/theme/profile_theme_extension.dart';
import 'package:mobile/design/widgets/jovia_editorial.dart';
import 'package:mobile/l10n/l10n.dart';

typedef JoviaAppMenuAction =
    Future<void> Function(BuildContext context, Map<String, dynamic>? profile);

class JoviaAppMenuDrawer extends ConsumerWidget {
  const JoviaAppMenuDrawer({
    super.key,
    this.onEditProfile,
    this.onOpenPeople,
    this.onOpenCalendar,
    this.onOpenArchetype,
  });

  final JoviaAppMenuAction? onEditProfile;
  final JoviaAppMenuAction? onOpenPeople;
  final JoviaAppMenuAction? onOpenCalendar;
  final JoviaAppMenuAction? onOpenArchetype;

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

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final profile = context.profileTheme;
    final l10n = context.l10n;
    final authUser = Supabase.instance.client.auth.currentUser;
    final profileMap = ref.watch(userProfileProvider).valueOrNull;
    final peopleCount = ref.watch(peopleListProvider).valueOrNull?.length ?? 0;
    final prefs = ref.watch(joviaAppPreferencesProvider);
    final themeMode = ref.watch(joviaThemeModeProvider);
    final hasBirthData = _hasBirthData(profileMap);
    final displayName = _displayName(profileMap, authUser);
    final username = _displayUsername(profileMap, authUser);
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final drawerWidth = (MediaQuery.sizeOf(context).width * 0.86)
        .clamp(312.0, 382.0)
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
          padding: const EdgeInsets.fromLTRB(10, 10, 14, 10),
          child: DecoratedBox(
            decoration: BoxDecoration(
              color: shellColor,
              borderRadius: BorderRadius.circular(32),
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
              padding: const EdgeInsets.fromLTRB(16, 14, 16, 16),
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
                  _JoviaAppMenuIdentityCard(
                    displayName: displayName,
                    username: username,
                    peopleCount: peopleCount,
                    hasBirthData: hasBirthData,
                  ),
                  const SizedBox(height: 18),
                  Expanded(
                    child: SingleChildScrollView(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          _JoviaAppMenuSectionLabel(
                            label: l10n.menuQuickAccess,
                          ),
                          const SizedBox(height: 8),
                          if (onEditProfile != null)
                            _JoviaAppMenuActionTile(
                              title: l10n.menuEditProfile,
                              subtitle: l10n.menuEditProfileSubtitle,
                              iconAsset: JoviaUiAsset.settingsRings,
                              onTap: () => closeThenRun(
                                context,
                                onEditProfile,
                                profile: profileMap,
                              ),
                            ),
                          if (onEditProfile != null) const SizedBox(height: 10),
                          if (onOpenPeople != null)
                            _JoviaAppMenuActionTile(
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
                          if (onOpenPeople != null) const SizedBox(height: 10),
                          if (onOpenCalendar != null)
                            _JoviaAppMenuActionTile(
                              title: l10n.menuCalendar,
                              subtitle: l10n.menuCalendarSubtitle,
                              iconAsset: JoviaUiAsset.calendarLunar,
                              onTap: () => closeThenRun(
                                context,
                                onOpenCalendar,
                                profile: profileMap,
                              ),
                            ),
                          if (onOpenCalendar != null)
                            const SizedBox(height: 10),
                          if (onOpenArchetype != null)
                            _JoviaAppMenuActionTile(
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
                          const SizedBox(height: 18),
                          _JoviaAppMenuSectionLabel(
                            label: l10n.menuPreferences,
                          ),
                          const SizedBox(height: 8),
                          JoviaSurfaceCard(
                            radius: 24,
                            padding: const EdgeInsets.fromLTRB(14, 14, 14, 14),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  l10n.menuThemeMode,
                                  style: profile.typography.cardTitle.copyWith(
                                    color: profile.colors.text,
                                    fontSize: 14,
                                  ),
                                ),
                                const SizedBox(height: 10),
                                JoviaModeSwitch<JoviaThemeMode>(
                                  value: themeMode,
                                  leadingValue: JoviaThemeMode.dark,
                                  leadingLabel: l10n.themeModeDark,
                                  trailingValue: JoviaThemeMode.light,
                                  trailingLabel: l10n.themeModeLight,
                                  onChanged: (mode) {
                                    ref
                                        .read(joviaThemeModeProvider.notifier)
                                        .setMode(mode);
                                  },
                                ),
                                const SizedBox(height: 14),
                                Text(
                                  l10n.menuLanguage,
                                  style: profile.typography.cardTitle.copyWith(
                                    color: profile.colors.text,
                                    fontSize: 14,
                                  ),
                                ),
                                const SizedBox(height: 10),
                                JoviaModeSwitch<JoviaAppLocale>(
                                  value: prefs.locale,
                                  leadingValue: JoviaAppLocale.tr,
                                  leadingLabel: JoviaAppLocale.tr.label,
                                  trailingValue: JoviaAppLocale.en,
                                  trailingLabel: JoviaAppLocale.en.label,
                                  onChanged: (value) {
                                    ref
                                        .read(
                                          joviaAppPreferencesProvider.notifier,
                                        )
                                        .setLocale(value);
                                  },
                                ),
                                const SizedBox(height: 14),
                                Text(
                                  l10n.menuNotificationPreferences,
                                  style: profile.typography.cardTitle.copyWith(
                                    color: profile.colors.text,
                                    fontSize: 14,
                                  ),
                                ),
                                const SizedBox(height: 10),
                                _JoviaAppMenuToggleTile(
                                  title: l10n.menuDailySummary,
                                  subtitle: l10n.menuDailySummarySubtitle,
                                  value: prefs.dailyBriefEnabled,
                                  onChanged: (value) {
                                    ref
                                        .read(
                                          joviaAppPreferencesProvider.notifier,
                                        )
                                        .setDailyBriefEnabled(value);
                                  },
                                ),
                                const SizedBox(height: 8),
                                _JoviaAppMenuToggleTile(
                                  title: l10n.menuSkyEvents,
                                  subtitle: l10n.menuSkyEventsSubtitle,
                                  value: prefs.skyAlertsEnabled,
                                  onChanged: (value) {
                                    ref
                                        .read(
                                          joviaAppPreferencesProvider.notifier,
                                        )
                                        .setSkyAlertsEnabled(value);
                                  },
                                ),
                                const SizedBox(height: 8),
                                _JoviaAppMenuToggleTile(
                                  title: l10n.menuSocialActivity,
                                  subtitle: l10n.menuSocialActivitySubtitle,
                                  value: prefs.socialAlertsEnabled,
                                  onChanged: (value) {
                                    ref
                                        .read(
                                          joviaAppPreferencesProvider.notifier,
                                        )
                                        .setSocialAlertsEnabled(value);
                                  },
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(height: 18),
                          _JoviaAppMenuSectionLabel(label: l10n.menuMembership),
                          const SizedBox(height: 8),
                          _JoviaAppMenuActionTile(
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
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 14),
                  _JoviaAppMenuActionTile(
                    title: l10n.menuSignOut,
                    subtitle: l10n.menuSignOutSubtitle,
                    iconAsset: JoviaUiAsset.logoutArc,
                    danger: true,
                    onTap: () async {
                      Navigator.of(context).pop();
                      await Future<void>.delayed(
                        const Duration(milliseconds: 180),
                      );
                      await Supabase.instance.client.auth.signOut();
                    },
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

class _JoviaAppMenuIdentityCard extends StatelessWidget {
  const _JoviaAppMenuIdentityCard({
    required this.displayName,
    required this.username,
    required this.peopleCount,
    required this.hasBirthData,
  });

  final String displayName;
  final String username;
  final int peopleCount;
  final bool hasBirthData;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final l10n = context.l10n;
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.fromLTRB(14, 14, 14, 14),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: profile.colors.strokeSoft),
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            Colors.white.withValues(
              alpha: Theme.of(context).brightness == Brightness.dark
                  ? 0.06
                  : 0.92,
            ),
            profile.colors.panelSoft,
          ],
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            displayName,
            style: profile.typography.cardTitle.copyWith(
              color: profile.colors.text,
              fontSize: 16,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            username,
            style: profile.typography.meta.copyWith(
              color: profile.colors.textLight,
              fontSize: 11.5,
            ),
          ),
          const SizedBox(height: 10),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              if (peopleCount > 0)
                JoviaMetaPill(label: l10n.menuPeopleCount(peopleCount)),
              JoviaMetaPill(
                label: hasBirthData
                    ? l10n.menuArchetypeReady
                    : l10n.menuBirthDataMissing,
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _JoviaAppMenuSectionLabel extends StatelessWidget {
  const _JoviaAppMenuSectionLabel({required this.label});

  final String label;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Text(
      label,
      style: profile.typography.eyebrow.copyWith(
        color: profile.colors.textLight,
        fontSize: 10.5,
        fontWeight: FontWeight.w700,
        letterSpacing: 1.3,
      ),
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
    final profile = context.profileTheme;
    final surface = danger
        ? Color.alphaBlend(
            profile.colors.warmAccent.withValues(alpha: 0.08),
            profile.colors.panelSoft,
          )
        : profile.colors.panelSoft;
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(22),
        child: Ink(
          padding: const EdgeInsets.fromLTRB(12, 12, 12, 12),
          decoration: BoxDecoration(
            color: surface,
            borderRadius: BorderRadius.circular(22),
            border: Border.all(color: profile.colors.strokeSoft),
          ),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                width: 38,
                height: 38,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: Colors.white.withValues(alpha: 0.68),
                  border: Border.all(color: profile.colors.strokeSoft),
                ),
                child: Center(
                  child: JoviaUiIcon(
                    asset: iconAsset,
                    size: 16,
                    color: profile.colors.text,
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            title,
                            style: profile.typography.cardTitle.copyWith(
                              color: profile.colors.text,
                              fontSize: 14,
                            ),
                          ),
                        ),
                        if ((trailingLabel ?? '').trim().isNotEmpty)
                          Padding(
                            padding: const EdgeInsets.only(left: 8),
                            child: JoviaMetaPill(label: trailingLabel!.trim()),
                          ),
                      ],
                    ),
                    const SizedBox(height: 3),
                    Text(
                      subtitle,
                      style: profile.typography.bodyCompact.copyWith(
                        color: profile.colors.textLight,
                        fontSize: 11.5,
                        height: 1.3,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 10),
              JoviaUiIcon(
                asset: JoviaUiAsset.chevronRight,
                size: 15,
                color: profile.colors.textLight,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _JoviaAppMenuToggleTile extends StatelessWidget {
  const _JoviaAppMenuToggleTile({
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
    final profile = context.profileTheme;
    return Container(
      padding: const EdgeInsets.fromLTRB(12, 10, 12, 10),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: profile.colors.strokeSoft),
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: profile.typography.body.copyWith(
                    color: profile.colors.text,
                    fontSize: 13.5,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  subtitle,
                  style: profile.typography.meta.copyWith(
                    color: profile.colors.textLight,
                    fontSize: 11,
                  ),
                ),
              ],
            ),
          ),
          Switch.adaptive(value: value, onChanged: onChanged),
        ],
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
