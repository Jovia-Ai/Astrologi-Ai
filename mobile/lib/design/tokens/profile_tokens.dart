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

  static const ProfileColors light = ProfileColors(
    bg: Color(0xFFFFF1EB),
    surface: Color(0xFFFFFFFF),
    text: Color(0xFF201A35),
    muted: Color(0xFF615B74),
    textLight: Color(0xFF8B84A0),
    primary: Color(0xFF715CFF),
    lime: Color(0xFFB7E85C),
    lavender: Color(0xFFC2A8FF),
    border: Color(0x1F715CFF),
    strokeSoft: Color(0x1F715CFF),
    separator: Color(0x29715CFF),
    auraStops: <Color>[Color(0xFF715CFF), Color(0xFFFF6FD8), Color(0xFF59E7FF)],
    chipBg: Color(0xFFFFFFFF),
    chipBorder: Color(0x24715CFF),
    warmAccent: Color(0xFFFFB84D),
    heroText: Color(0xFFFFFFFF),
    heroBase: Color(0xFF201A55),
    neonPink: Color(0xFFFF6FD8),
    neonCyan: Color(0xFF59E7FF),
  );
}

@immutable
class ProfileRadii {
  const ProfileRadii({required this.cardRadius, required this.pillRadius});

  final double cardRadius;
  final double pillRadius;

  static const ProfileRadii standard = ProfileRadii(
    cardRadius: 24,
    pillRadius: 999,
  );
}

@immutable
class ProfileSpacing {
  const ProfileSpacing({
    required this.xxs,
    required this.xs,
    required this.sm,
    required this.md,
    required this.lg,
    required this.xl,
    required this.xxl,
    required this.xxxl,
  });

  final double xxs;
  final double xs;
  final double sm;
  final double md;
  final double lg;
  final double xl;
  final double xxl;
  final double xxxl;

  double get s4 => xxs;
  double get s8 => xs;
  double get s12 => sm;
  double get s16 => md;
  double get s20 => lg;
  double get s24 => xl;
  double get s32 => xxl;
  double get s40 => xxxl;

  static const ProfileSpacing standard = ProfileSpacing(
    xxs: 4,
    xs: 8,
    sm: 12,
    md: 16,
    lg: 20,
    xl: 24,
    xxl: 32,
    xxxl: 40,
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
      color: Color(0x127360F9),
      blurRadius: 20,
      offset: Offset(0, 8),
      spreadRadius: -10,
    ),
    floatingShadow: BoxShadow(
      color: Color(0x147360F9),
      blurRadius: 24,
      offset: Offset(0, 10),
      spreadRadius: -10,
    ),
  );
}
