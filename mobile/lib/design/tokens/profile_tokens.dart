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
    bg: Color(0xFFF6F0E8),
    surface: Color(0xFFFFFAF4),
    text: Color(0xFF17151F),
    muted: Color(0xFF655B52),
    textLight: Color(0xFF8C7F73),
    primary: Color(0xFFC17E48),
    lime: Color(0xFFF3E7D9),
    lavender: Color(0xFFF8EEE4),
    border: Color(0x1E3B271C),
    strokeSoft: Color(0x163B271C),
    separator: Color(0x223B271C),
    auraStops: <Color>[Color(0xFFF6F0E8), Color(0xFFF7EBDD), Color(0xFFFFFAF4)],
    chipBg: Color(0xFFF6EEE4),
    chipBorder: Color(0x30C17E48),
    warmAccent: Color(0xFFC17E48),
    heroText: Color(0xFF17151F),
    heroBase: Color(0xFFFFF8F1),
    neonPink: Color(0xFFE8C6B1),
    neonCyan: Color(0xFFE7DDD3),
  );

  static const ProfileColors dark = ProfileColors(
    bg: Color(0xFF15110F),
    surface: Color(0xFF241D19),
    text: Color(0xFFF6F0E8),
    muted: Color(0xFFD8CCBF),
    textLight: Color(0xFFB7ABA0),
    primary: Color(0xFFD9C4B0),
    lime: Color(0xFF221C18),
    lavender: Color(0xFF2A221D),
    border: Color(0x36FFFFFF),
    strokeSoft: Color(0x28FFFFFF),
    separator: Color(0x20FFFFFF),
    auraStops: <Color>[Color(0xFF15110F), Color(0xFF201713), Color(0xFF0E0B0A)],
    chipBg: Color(0xFF2C241F),
    chipBorder: Color(0x30FFFFFF),
    warmAccent: Color(0xFFC19773),
    heroText: Color(0xFFF6F0E8),
    heroBase: Color(0xFF100C0A),
    neonPink: Color(0xFF6F5447),
    neonCyan: Color(0xFF574E48),
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
    medium: 20,
    large: 28,
    pillRadius: 14,
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
      color: Color(0x26000000),
      blurRadius: 24,
      offset: Offset(0, 14),
      spreadRadius: -18,
    ),
    floatingShadow: BoxShadow(
      color: Color(0x33000000),
      blurRadius: 34,
      offset: Offset(0, 20),
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
