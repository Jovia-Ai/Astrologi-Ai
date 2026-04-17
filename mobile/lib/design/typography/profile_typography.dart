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
  TextStyle get heroName => heroEditorial.copyWith(
    fontSize: 28,
    height: 1.04,
    fontWeight: FontWeight.w500,
    letterSpacing: -0.56,
  );
  TextStyle get editorialHeadline => heroEditorial.copyWith(
    fontSize: 38,
    height: 1.06,
    fontWeight: FontWeight.w400,
    letterSpacing: -0.96,
  );
  TextStyle get monoEyebrow =>
      sectionLabel.copyWith(fontWeight: FontWeight.w500, letterSpacing: 2.35);
  TextStyle get bodyReading =>
      bodyLarge.copyWith(fontSize: 15.5, height: 1.74, letterSpacing: -0.08);
  TextStyle get buttonLabel => chipLabel.copyWith(
    fontSize: 12.5,
    height: 16 / 12.5,
    fontWeight: FontWeight.w500,
    letterSpacing: 0.04,
  );
  TextStyle get metaSoft => meta.copyWith(
    fontSize: 12.5,
    height: 18 / 12.5,
    fontWeight: FontWeight.w500,
    letterSpacing: 0.02,
  );

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
      fontSize: 11.5,
      height: 15 / 11.5,
      fontWeight: FontWeight.w500,
      letterSpacing: 1.35,
    );
  }

  TextStyle navigationMeta({Color? color}) {
    return meta.copyWith(
      color: color ?? meta.color,
      fontSize: 13,
      height: 18 / 13,
      fontWeight: FontWeight.w500,
      letterSpacing: 0,
    );
  }

  TextStyle navigationAction({Color? color}) {
    return cardTitle.copyWith(
      color: color ?? pageTitle.color,
      fontSize: 17,
      height: 22 / 17,
      fontWeight: FontWeight.w500,
      letterSpacing: -0.18,
    );
  }

  bool prefersEditorialSerif(String text) {
    final normalized = text.trim();
    if (normalized.isEmpty) {
      return false;
    }
    final wordCount = normalized.split(RegExp(r'\s+')).length;
    return normalized.length <= 34 && wordCount <= 5;
  }

  TextStyle headlineFor(String text, {Color? color}) {
    final base = prefersEditorialSerif(text) ? heroEditorial : pageTitle;
    return color == null ? base : base.copyWith(color: color);
  }

  factory ProfileTypography.fromColors({
    required Color textColor,
    required Color secondaryColor,
    required Color mutedLabelColor,
    TextStyle Function(TextStyle base)? display,
    TextStyle Function(TextStyle base)? body,
    TextStyle Function(TextStyle base)? mono,
  }) {
    TextStyle apply(
      TextStyle Function(TextStyle base)? wrap,
      TextStyle base,
    ) => wrap != null ? wrap(base) : base;

    return ProfileTypography(
      sectionLabel: apply(
        mono,
        TextStyle(
          fontSize: 11,
          height: 15 / 11,
          fontWeight: FontWeight.w500,
          color: mutedLabelColor,
          letterSpacing: 1.7,
        ),
      ),
      pageTitle: apply(
        body,
        TextStyle(
          fontSize: 36,
          height: 40 / 36,
          fontWeight: FontWeight.w400,
          color: textColor,
          letterSpacing: -1.24,
        ),
      ),
      sectionTitle: apply(
        body,
        TextStyle(
          fontSize: 30,
          height: 34 / 30,
          fontWeight: FontWeight.w400,
          color: textColor,
          letterSpacing: -0.9,
        ),
      ),
      cardTitle: apply(
        body,
        TextStyle(
          fontSize: 18,
          height: 24 / 18,
          fontWeight: FontWeight.w500,
          color: textColor,
          letterSpacing: -0.22,
        ),
      ),
      bodyLarge: apply(
        body,
        TextStyle(
          fontSize: 15.5,
          height: 26 / 15.5,
          fontWeight: FontWeight.w400,
          color: textColor,
          letterSpacing: -0.08,
        ),
      ),
      bodyCompact: apply(
        body,
        TextStyle(
          fontSize: 14.5,
          height: 22 / 14.5,
          fontWeight: FontWeight.w400,
          color: textColor,
          letterSpacing: -0.05,
        ),
      ),
      meta: apply(
        body,
        TextStyle(
          fontSize: 13,
          height: 18 / 13,
          fontWeight: FontWeight.w400,
          color: secondaryColor,
          letterSpacing: 0.01,
        ),
      ),
      chipLabel: apply(
        body,
        TextStyle(
          fontSize: 12.5,
          height: 16 / 12.5,
          fontWeight: FontWeight.w500,
          color: textColor,
          letterSpacing: 0.02,
        ),
      ),
      heroEditorial: apply(
        body,
        TextStyle(
          fontSize: 52,
          height: 54 / 52,
          fontWeight: FontWeight.w400,
          color: textColor,
          letterSpacing: -1.72,
        ),
      ),
    );
  }
}
