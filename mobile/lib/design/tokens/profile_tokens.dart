import 'package:flutter/material.dart';

@immutable
class ProfileColors {
  const ProfileColors({
    required this.bg,
    required this.surface,
    required this.text,
    required this.muted,
    required this.textLight,
    required this.primary,
    required this.lime,
    required this.lavender,
    required this.border,
    required this.strokeSoft,
    required this.separator,
    required this.auraStops,
    required this.chipBg,
    required this.chipBorder,
    required this.warmAccent,
    required this.heroText,
    required this.heroBase,
    required this.neonPink,
    required this.neonCyan,
  });

  final Color bg;
  final Color surface;
  final Color text;
  final Color muted;
  final Color textLight;
  final Color primary;
  final Color lime;
  final Color lavender;
  final Color border;
  final Color strokeSoft;
  final Color separator;
  final List<Color> auraStops;
  final Color chipBg;
  final Color chipBorder;
  final Color warmAccent;
  final Color heroText;
  final Color heroBase;
  final Color neonPink;
  final Color neonCyan;

  Color get canvas => bg;
  Color get canvasAlt => heroBase;
  Color get heroBand =>
      Color.alphaBlend(primary.withValues(alpha: 0.14), heroBase);
  Color get panelSoft =>
      Color.alphaBlend(strokeSoft.withValues(alpha: 0.18), surface);
  Color get panelStrong =>
      Color.alphaBlend(border.withValues(alpha: 0.22), heroBase);
  Color get pillIdle => chipBg;
  Color get pillActive =>
      Color.alphaBlend(warmAccent.withValues(alpha: 0.12), panelStrong);
  Color get buttonPrimary => warmAccent;
  Color get buttonSecondary => panelStrong;
  Color get hairline => separator;
  Color get shadowSoft => const Color(0x1F0E1620);
  Color get shadowLift => const Color(0x33202A33);

  Color get bgBase => bg;
  Color get surfaceCard => surface;
  Color get brandPurple => primary;
  Color get brandLime => lime;
  Color get brandLavender => lavender;
  Color get strokeDivider => separator;
  Color get bgPrimary => bg;
  Color get bgSecondary => heroBase;
  Color get surfacePrimary => surface;
  Color get surfaceSoft => heroBase;
  Color get textPrimary => text;
  Color get textSecondary => muted;
  Color get textMuted => textLight;
  Color get borderSubtle => strokeSoft;
  Color get accentPrimary => primary;
  Color get accentSoft => lavender;
  Color get successSoft => const Color(0xFFE8F5E4);
  Color get warningSoft => const Color(0xFFFFE8D5);
  Color get statusApproaching => const Color(0xFF8D7CFF);
  Color get statusPeak => warmAccent;
  Color get statusReceding => const Color(0xFF8FA1B5);

  static const ProfileColors light = ProfileColors(
    bg: Color(0xFFEFF3F6),
    surface: Color(0xFFF8FBFD),
    text: Color(0xFF182028),
    muted: Color(0xFF667480),
    textLight: Color(0xFF95A3AE),
    primary: Color(0xFFAABAC7),
    lime: Color(0xFFF1F5F8),
    lavender: Color(0xFFE9EFF4),
    border: Color(0x2A8EA0AF),
    strokeSoft: Color(0x1F8EA0AF),
    separator: Color(0x1A8EA0AF),
    auraStops: <Color>[Color(0xFFEFF3F6), Color(0xFFF5F8FB), Color(0xFFF8FBFD)],
    chipBg: Color(0xE6F7FAFC),
    chipBorder: Color(0x339EAFBD),
    warmAccent: Color(0xFFB8C7D4),
    heroText: Color(0xFF182028),
    heroBase: Color(0xFFE7EDF2),
    neonPink: Color(0xFFDDE6F2),
    neonCyan: Color(0xFFDDE8EC),
  );

  static const ProfileColors dark = ProfileColors(
    bg: Color(0xFF06090D),
    surface: Color(0xFF10161C),
    text: Color(0xFFF2F5F8),
    muted: Color(0xFFC8D0D7),
    textLight: Color(0xFF93A1AE),
    primary: Color(0xFFAAB7C3),
    lime: Color(0xFF11181F),
    lavender: Color(0xFF161D24),
    border: Color(0x337D8D9C),
    strokeSoft: Color(0x268595A4),
    separator: Color(0x1F8A99A8),
    auraStops: <Color>[Color(0xFF06090D), Color(0xFF10161C), Color(0xFF06090D)],
    chipBg: Color(0xCC111820),
    chipBorder: Color(0x338899A8),
    warmAccent: Color(0xFFC7D6E2),
    heroText: Color(0xFF0E141A),
    heroBase: Color(0xFF0B1015),
    neonPink: Color(0xFF313E4B),
    neonCyan: Color(0xFF24333C),
  );
}

@immutable
class ProfileRadii {
  const ProfileRadii({
    required this.small,
    required this.medium,
    required this.large,
    required this.pillRadius,
  });

  final double small;
  final double medium;
  final double large;
  final double pillRadius;

  double get cardRadius => medium;
  double get chipRadius => pillRadius;
  double get heroRadius => large;

  static const ProfileRadii standard = ProfileRadii(
    small: 14,
    medium: 22,
    large: 30,
    pillRadius: 18,
  );
}

@immutable
class ProfileSpacing {
  const ProfileSpacing({
    required this.xxs,
    required this.xs,
    required this.sm,
    required this.md,
    required this.step20,
    required this.lg,
    required this.xl,
    required this.xxl,
    required this.xxxl,
    required this.heroGap,
  });

  final double xxs;
  final double xs;
  final double sm;
  final double md;
  final double step20;
  final double lg;
  final double xl;
  final double xxl;
  final double xxxl;
  final double heroGap;

  double get s4 => xxs;
  double get s8 => xs;
  double get s12 => sm;
  double get s16 => md;
  double get s20 => step20;
  double get s24 => lg;
  double get s32 => xl;
  double get s40 => xxl;
  double get s48 => xxxl;
  double get s56 => heroGap;

  double get pageHorizontal => step20;
  double get pageTop => step20;
  double get pageBottom => xl;
  double get sectionToContent => sm;
  double get compactBlockGap => sm;
  double get majorSectionGap => 28;
  double get heroToSectionGap => xxl;
  double get compactUtilityPadding => md;
  double get standardPanelPadding => 18;
  double get largeNarrativePadding => 22;
  double get primaryToSecondaryGap => sm;
  double get iconActionGap => sm;
  double get textActionGap => sm;
  double get sectionGap => xl;
  double get headlineGap => lg;
  double get cardInset => step20;
  double get railGap => sm;
  double get pillHeight => 44;
  double get buttonHeight => 48;
  double get navInset => md;

  static const ProfileSpacing standard = ProfileSpacing(
    xxs: 4,
    xs: 8,
    sm: 12,
    md: 16,
    step20: 20,
    lg: 24,
    xl: 32,
    xxl: 40,
    xxxl: 48,
    heroGap: 56,
  );
}

@immutable
class ProfileShadows {
  const ProfileShadows({
    required this.cardShadow,
    required this.floatingShadow,
  });

  final BoxShadow cardShadow;
  final BoxShadow floatingShadow;

  static const ProfileShadows soft = ProfileShadows(
    cardShadow: BoxShadow(
      color: Color(0x26141F28),
      blurRadius: 30,
      offset: Offset(0, 18),
      spreadRadius: -20,
    ),
    floatingShadow: BoxShadow(
      color: Color(0x33212B35),
      blurRadius: 40,
      offset: Offset(0, 24),
      spreadRadius: -24,
    ),
  );
}

@immutable
class ProfileMotion {
  const ProfileMotion({
    required this.fast,
    required this.normal,
    required this.enter,
    required this.page,
    required this.curve,
  });

  final Duration fast;
  final Duration normal;
  final Duration enter;
  final Duration page;
  final Curve curve;

  static const ProfileMotion soft = ProfileMotion(
    fast: Duration(milliseconds: 120),
    normal: Duration(milliseconds: 180),
    enter: Duration(milliseconds: 240),
    page: Duration(milliseconds: 280),
    curve: Curves.easeOutCubic,
  );
}
