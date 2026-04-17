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
    this.brandLime = const Color(0xFFCAFF4D),
    this.brandLavender = const Color(0xFF7F77DD),
    this.brandBlush = const Color(0xFFF9A8D4),
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
  final Color brandLime;
  final Color brandLavender;
  final Color brandBlush;

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
    bg: Color(0xFFFAF8F3),
    surface: Color(0xFFFFFFFF),
    text: Color(0xFF0A0A0A),
    muted: Color(0xFF444444),
    textLight: Color(0xFF777777),
    primary: Color(0xFFDCCEFF),
    lime: Color(0xFFE9FFC5),
    lavender: Color(0xFFF3EEFF),
    border: Color(0x14000000),
    strokeSoft: Color(0x12000000),
    separator: Color(0x0A000000),
    auraStops: <Color>[Color(0xFFFAF8F3), Color(0xFFF5F3EE), Color(0xFFFAF8F3)],
    chipBg: Color(0xFFFFFFFF),
    chipBorder: Color(0x14000000),
    warmAccent: Color(0xFFD8FF72),
    heroText: Color(0xFF0A0A0A),
    heroBase: Color(0xFFF5F3EE),
    neonPink: Color(0xFFF8EFFF),
    neonCyan: Color(0xFFEFFFF4),
  );

  static const ProfileColors dark = ProfileColors(
    bg: Color(0xFF111111),
    surface: Color(0xFF1A1A1A),
    text: Color(0xFFFFFFFF),
    muted: Color(0xFFC8D0D7),
    textLight: Color(0xFF93A1AE),
    primary: Color(0xFFAAB7C3),
    lime: Color(0xFF11181F),
    lavender: Color(0xFF161D24),
    border: Color(0x337D8D9C),
    strokeSoft: Color(0x268595A4),
    separator: Color(0x1F8A99A8),
    auraStops: <Color>[Color(0xFF111111), Color(0xFF1A1A1A), Color(0xFF111111)],
    chipBg: Color(0xCC1A1A1A),
    chipBorder: Color(0x338899A8),
    warmAccent: Color(0xFFC7D6E2),
    heroText: Color(0xFF0A0A0A),
    heroBase: Color(0xFF0A0A0A),
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
    small: 16,
    medium: 28,
    large: 36,
    pillRadius: 20,
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
    step20: 24,
    lg: 28,
    xl: 36,
    xxl: 44,
    xxxl: 56,
    heroGap: 68,
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
      color: Color(0x140F151A),
      blurRadius: 26,
      offset: Offset(0, 14),
      spreadRadius: -18,
    ),
    floatingShadow: BoxShadow(
      color: Color(0x1A0F151A),
      blurRadius: 36,
      offset: Offset(0, 20),
      spreadRadius: -22,
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
