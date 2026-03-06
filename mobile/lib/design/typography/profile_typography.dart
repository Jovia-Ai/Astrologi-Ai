import 'package:flutter/material.dart';

@immutable
class ProfileTypography {
  const ProfileTypography({
    required this.hero,
    required this.section,
    required this.card,
    required this.body,
    required this.meta,
  });

  final TextStyle hero;
  final TextStyle section;
  final TextStyle card;
  final TextStyle body;
  final TextStyle meta;

  TextStyle get h1 => hero;
  TextStyle get h2 => section;
  TextStyle get micro => meta;
  TextStyle get heroTitle => hero;
  TextStyle get sectionTitle => section;
  TextStyle get cardTitle => card;

  static List<String> get _fallbackFamily => const <String>[
    'Plus Jakarta Sans',
    '.SF Pro Text',
    'Inter',
    'Segoe UI',
    'Roboto',
  ];

  factory ProfileTypography.fromColor(Color textColor, Color mutedColor) {
    return ProfileTypography(
      hero: TextStyle(
        fontSize: 28,
        height: 1.2,
        fontWeight: FontWeight.w700,
        color: textColor,
        letterSpacing: -0.4,
        fontFamilyFallback: _fallbackFamily,
      ),
      section: TextStyle(
        fontSize: 22,
        height: 1.3,
        fontWeight: FontWeight.w700,
        color: textColor,
        letterSpacing: -0.35,
        fontFamilyFallback: _fallbackFamily,
      ),
      card: TextStyle(
        fontSize: 18,
        height: 1.28,
        fontWeight: FontWeight.w600,
        color: textColor,
        letterSpacing: -0.2,
        fontFamilyFallback: _fallbackFamily,
      ),
      body: TextStyle(
        fontSize: 15,
        height: 1.45,
        fontWeight: FontWeight.w400,
        color: textColor,
        letterSpacing: 0,
        fontFamilyFallback: _fallbackFamily,
      ),
      meta: TextStyle(
        fontSize: 13,
        height: 1.35,
        fontWeight: FontWeight.w500,
        color: mutedColor,
        letterSpacing: 0.08,
        fontFamilyFallback: _fallbackFamily,
      ),
    );
  }
}
