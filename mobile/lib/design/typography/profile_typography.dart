import 'package:flutter/material.dart';

@immutable
class ProfileTypography {
  const ProfileTypography({
    required this.sectionLabel,
    required this.pageTitle,
    required this.sectionTitle,
    required this.cardTitle,
    required this.bodyLarge,
    required this.bodyCompact,
    required this.meta,
    required this.chipLabel,
    required this.heroEditorial,
  });

  final TextStyle sectionLabel;
  final TextStyle pageTitle;
  final TextStyle sectionTitle;
  final TextStyle cardTitle;
  final TextStyle bodyLarge;
  final TextStyle bodyCompact;
  final TextStyle meta;
  final TextStyle chipLabel;
  final TextStyle heroEditorial;

  TextStyle get overline => sectionLabel;
  TextStyle get display => pageTitle;
  TextStyle get hero => heroEditorial;
  TextStyle get section => sectionTitle;
  TextStyle get card => cardTitle;
  TextStyle get body => bodyLarge;
  TextStyle get label => chipLabel;

  TextStyle get h1 => heroEditorial;
  TextStyle get h2 => sectionTitle;
  TextStyle get micro => meta;
  TextStyle get heroTitle => heroEditorial;
  TextStyle get eyebrow => sectionLabel;
  TextStyle get displayTitle => pageTitle;
  TextStyle get uiLabel => chipLabel;

  TextStyle navigationLabel({Color? color}) {
    return sectionLabel.copyWith(
      color: color ?? sectionLabel.color,
      fontSize: 12,
      height: 16 / 12,
      fontWeight: FontWeight.w600,
      letterSpacing: 1.8,
    );
  }

  TextStyle navigationMeta({Color? color}) {
    return meta.copyWith(
      color: color ?? meta.color,
      fontSize: 13,
      height: 18 / 13,
      fontWeight: FontWeight.w500,
    );
  }

  TextStyle navigationAction({Color? color}) {
    return pageTitle.copyWith(
      color: color ?? pageTitle.color,
      fontSize: 18,
      height: 24 / 18,
      fontWeight: FontWeight.w600,
      letterSpacing: 1.1,
    );
  }

  static const String _sansFamily = 'Inter';
  static const String _serifFamily = 'Cormorant Garamond';

  static List<String> get _sansFallbackFamily => const <String>[
    '.SF Pro Text',
    'Segoe UI',
    'Roboto',
  ];

  static List<String> get _serifFallbackFamily => const <String>[
    'Iowan Old Style',
    'Georgia',
    'Times New Roman',
    'Times',
  ];

  bool prefersEditorialSerif(String text) {
    final normalized = text.trim();
    if (normalized.isEmpty) {
      return false;
    }
    final wordCount = normalized.split(RegExp(r'\s+')).length;
    return normalized.length <= 48 && wordCount <= 8;
  }

  TextStyle headlineFor(String text, {Color? color}) {
    final base = prefersEditorialSerif(text) ? heroEditorial : pageTitle;
    return color == null ? base : base.copyWith(color: color);
  }

  factory ProfileTypography.fromColors({
    required Color textColor,
    required Color secondaryColor,
    required Color mutedLabelColor,
  }) {
    return ProfileTypography(
      sectionLabel: TextStyle(
        fontSize: 12,
        height: 16 / 12,
        fontWeight: FontWeight.w600,
        color: mutedLabelColor,
        letterSpacing: 1.8,
        fontFamily: _sansFamily,
        fontFamilyFallback: _sansFallbackFamily,
      ),
      pageTitle: TextStyle(
        fontSize: 30,
        height: 34 / 30,
        fontWeight: FontWeight.w600,
        color: textColor,
        fontFamily: _sansFamily,
        fontFamilyFallback: _sansFallbackFamily,
        letterSpacing: -0.5,
      ),
      sectionTitle: TextStyle(
        fontSize: 21,
        height: 28 / 21,
        fontWeight: FontWeight.w600,
        color: textColor,
        fontFamily: _sansFamily,
        fontFamilyFallback: _sansFallbackFamily,
        letterSpacing: -0.32,
      ),
      cardTitle: TextStyle(
        fontSize: 17,
        height: 24 / 17,
        fontWeight: FontWeight.w600,
        color: textColor,
        fontFamily: _sansFamily,
        fontFamilyFallback: _sansFallbackFamily,
        letterSpacing: -0.22,
      ),
      bodyLarge: TextStyle(
        fontSize: 16,
        height: 27 / 16,
        fontWeight: FontWeight.w400,
        color: textColor,
        fontFamily: _sansFamily,
        fontFamilyFallback: _sansFallbackFamily,
        letterSpacing: -0.06,
      ),
      bodyCompact: TextStyle(
        fontSize: 15,
        height: 24 / 15,
        fontWeight: FontWeight.w400,
        color: textColor,
        fontFamily: _sansFamily,
        fontFamilyFallback: _sansFallbackFamily,
        letterSpacing: -0.04,
      ),
      meta: TextStyle(
        fontSize: 13,
        height: 19 / 13,
        fontWeight: FontWeight.w500,
        color: secondaryColor,
        fontFamily: _sansFamily,
        fontFamilyFallback: _sansFallbackFamily,
        letterSpacing: 0.02,
      ),
      chipLabel: TextStyle(
        fontSize: 12,
        height: 16 / 12,
        fontWeight: FontWeight.w600,
        color: textColor,
        fontFamily: _sansFamily,
        fontFamilyFallback: _sansFallbackFamily,
        letterSpacing: 0.22,
      ),
      heroEditorial: TextStyle(
        fontSize: 46,
        height: 48 / 46,
        fontWeight: FontWeight.w600,
        color: textColor,
        fontFamily: _serifFamily,
        fontFamilyFallback: _serifFallbackFamily,
        letterSpacing: -0.92,
      ),
    );
  }
}
