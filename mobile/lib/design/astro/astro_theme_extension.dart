import 'dart:ui' show lerpDouble;

import 'package:flutter/material.dart';

enum BlobStyle { liquid, sharp, airy, solid }

enum ShapeFamily { fire, water, earth, air }

@immutable
class AstroTheme extends ThemeExtension<AstroTheme> {
  const AstroTheme({
    required this.bg,
    required this.surface,
    required this.text,
    required this.muted,
    required this.border,
    required this.auraStops,
    required this.blobStyle,
    required this.shapeFamily,
    required this.motionIntensity,
    required this.radiusScale,
    required this.accent,
    required this.highlight,
    this.grainOpacity = 0,
  });

  final Color bg;
  final Color surface;
  final Color text;
  final Color muted;
  final Color border;
  final List<Color> auraStops;
  final BlobStyle blobStyle;
  final ShapeFamily shapeFamily;
  final double motionIntensity;
  final double radiusScale;
  final Color accent;
  final Color highlight;
  final double grainOpacity;

  static const AstroTheme fallback = AstroTheme(
    bg: Color(0xFFF7F3FC),
    surface: Color(0xF2FFFFFF),
    text: Color(0xFF241C33),
    muted: Color(0xFF756D88),
    border: Color(0x33A895C8),
    auraStops: <Color>[Color(0xFF5E2C93), Color(0xFFA26FE3), Color(0xFFF2B5D4)],
    blobStyle: BlobStyle.liquid,
    shapeFamily: ShapeFamily.air,
    motionIntensity: 0.45,
    radiusScale: 1.0,
    accent: Color(0xFF8D58DA),
    highlight: Color(0xFFC293FF),
    grainOpacity: 0.02,
  );

  @override
  AstroTheme copyWith({
    Color? bg,
    Color? surface,
    Color? text,
    Color? muted,
    Color? border,
    List<Color>? auraStops,
    BlobStyle? blobStyle,
    ShapeFamily? shapeFamily,
    double? motionIntensity,
    double? radiusScale,
    Color? accent,
    Color? highlight,
    double? grainOpacity,
  }) {
    return AstroTheme(
      bg: bg ?? this.bg,
      surface: surface ?? this.surface,
      text: text ?? this.text,
      muted: muted ?? this.muted,
      border: border ?? this.border,
      auraStops: auraStops ?? this.auraStops,
      blobStyle: blobStyle ?? this.blobStyle,
      shapeFamily: shapeFamily ?? this.shapeFamily,
      motionIntensity: motionIntensity ?? this.motionIntensity,
      radiusScale: radiusScale ?? this.radiusScale,
      accent: accent ?? this.accent,
      highlight: highlight ?? this.highlight,
      grainOpacity: grainOpacity ?? this.grainOpacity,
    );
  }

  @override
  AstroTheme lerp(covariant ThemeExtension<AstroTheme>? other, double t) {
    if (other is! AstroTheme) {
      return this;
    }
    return AstroTheme(
      bg: Color.lerp(bg, other.bg, t) ?? bg,
      surface: Color.lerp(surface, other.surface, t) ?? surface,
      text: Color.lerp(text, other.text, t) ?? text,
      muted: Color.lerp(muted, other.muted, t) ?? muted,
      border: Color.lerp(border, other.border, t) ?? border,
      auraStops: List<Color>.generate(auraStops.length, (index) {
        final start = auraStops[index];
        final end = index < other.auraStops.length
            ? other.auraStops[index]
            : other.auraStops.last;
        return Color.lerp(start, end, t) ?? start;
      }),
      blobStyle: t < 0.5 ? blobStyle : other.blobStyle,
      shapeFamily: t < 0.5 ? shapeFamily : other.shapeFamily,
      motionIntensity:
          lerpDouble(motionIntensity, other.motionIntensity, t) ??
          motionIntensity,
      radiusScale: lerpDouble(radiusScale, other.radiusScale, t) ?? radiusScale,
      accent: Color.lerp(accent, other.accent, t) ?? accent,
      highlight: Color.lerp(highlight, other.highlight, t) ?? highlight,
      grainOpacity:
          lerpDouble(grainOpacity, other.grainOpacity, t) ?? grainOpacity,
    );
  }
}

ThemeData withAstroTheme(ThemeData base, {AstroTheme? astroTheme}) {
  final resolved = astroTheme ?? AstroTheme.fallback;
  final extensions = List<ThemeExtension<dynamic>>.from(base.extensions.values);
  extensions.removeWhere((ext) => ext is AstroTheme);
  extensions.add(resolved);
  return base.copyWith(extensions: extensions);
}

extension AstroThemeBuildContextX on BuildContext {
  AstroTheme get astroTheme =>
      Theme.of(this).extension<AstroTheme>() ?? AstroTheme.fallback;
}
