import 'dart:math' as math;

import 'package:flutter/material.dart';

import 'astro_theme_extension.dart';
import 'element_scores.dart';

const _bgCream = Color(0xFFFFF1EB);
const _surface = Color(0xFFFFFFFF);
const _text = Color(0xFF1F1F24);
const _muted = Color(0xFF5C5F66);
const _border = Color(0x297360F9);
const _brandPurple = Color(0xFF7360F9);

const Map<AstroElement, Color> _elementAnchors = <AstroElement, Color>{
  AstroElement.fire: Color(0xFFFF6D8A),
  AstroElement.water: Color(0xFF57D6F5),
  AstroElement.earth: Color(0xFFB9D440),
  AstroElement.air: Color(0xFFBC9BF3),
};

AstroTheme astroThemeFromElementScores(ElementScores rawScores) {
  final scores = rawScores.normalize();
  final ordered = <({AstroElement element, double weight})>[
    (element: AstroElement.fire, weight: scores.fire),
    (element: AstroElement.water, weight: scores.water),
    (element: AstroElement.earth, weight: scores.earth),
    (element: AstroElement.air, weight: scores.air),
  ]..sort((a, b) => b.weight.compareTo(a.weight));

  final top = ordered.first;
  final second = ordered[1];
  final topTwoSum = top.weight + second.weight;
  final isBalanced =
      top.weight < 0.38 && (top.weight - ordered.last.weight) < 0.12;
  final auraStops = _buildAuraStops(
    top: top,
    second: second,
    ordered: ordered,
    topTwoSum: topTwoSum,
    isBalanced: isBalanced,
  );

  final accent = _accentFor(top.element, strength: top.weight);
  final highlight = _accentFor(
    second.element,
    strength: second.weight,
    fallback: _brandPurple,
  );

  return AstroTheme(
    bg: _bgCream,
    surface: _surface,
    text: _text,
    muted: _muted,
    border: _border,
    auraStops: auraStops,
    blobStyle: _blobStyleFor(top.element),
    shapeFamily: _shapeFamilyFor(top.element),
    motionIntensity: _motionIntensity(top.weight),
    radiusScale: _radiusScale(top.element),
    accent: accent,
    highlight: highlight,
    grainOpacity: isBalanced ? 0.035 : 0.02,
  );
}

List<Color> _buildAuraStops({
  required ({AstroElement element, double weight}) top,
  required ({AstroElement element, double weight}) second,
  required List<({AstroElement element, double weight})> ordered,
  required double topTwoSum,
  required bool isBalanced,
}) {
  if (top.weight >= 0.45) {
    return <Color>[
      _bgCream,
      _softAnchor(top.element, 0.64),
      _softColor(_brandPurple, 0.7),
    ];
  }

  if (topTwoSum >= 0.70) {
    return <Color>[
      _bgCream,
      _softAnchor(top.element, 0.62),
      _softAnchor(second.element, 0.6),
      _softColor(_brandPurple, 0.72),
    ];
  }

  if (isBalanced) {
    return <Color>[
      _bgCream,
      _softAnchor(ordered[0].element, 0.54),
      _softAnchor(ordered[1].element, 0.52),
      _softAnchor(ordered[2].element, 0.5),
      _softColor(_brandPurple, 0.62),
    ];
  }

  return <Color>[
    _bgCream,
    _softAnchor(top.element, 0.58),
    _softAnchor(second.element, 0.54),
    _softColor(_brandPurple, 0.68),
  ];
}

Color _softAnchor(AstroElement element, double amount) {
  return _softColor(_elementAnchors[element]!, amount);
}

Color _softColor(Color base, double amount) {
  final hsl = HSLColor.fromColor(base);
  final softened = hsl
      .withSaturation(_clamp(hsl.saturation * 0.72, 0.18, 0.64))
      .withLightness(_clamp(0.72 + amount * 0.16, 0.72, 0.88));
  return Color.alphaBlend(
    _bgCream.withValues(alpha: _clamp(0.36 - amount * 0.12, 0.18, 0.36)),
    softened.toColor(),
  );
}

Color _accentFor(
  AstroElement element, {
  required double strength,
  Color? fallback,
}) {
  final base = _elementAnchors[element] ?? fallback ?? _brandPurple;
  final hsl = HSLColor.fromColor(base);
  return hsl
      .withSaturation(_clamp(hsl.saturation * 0.9, 0.4, 0.78))
      .withLightness(_clamp(0.56 + strength * 0.08, 0.54, 0.64))
      .toColor();
}

double _motionIntensity(double dominantWeight) {
  return _clamp(0.38 + dominantWeight * 0.72, 0.38, 0.86);
}

double _radiusScale(AstroElement element) {
  return switch (element) {
    AstroElement.fire => 0.92,
    AstroElement.water => 1.08,
    AstroElement.earth => 0.88,
    AstroElement.air => 1.14,
  };
}

BlobStyle _blobStyleFor(AstroElement element) {
  return switch (element) {
    AstroElement.fire => BlobStyle.sharp,
    AstroElement.water => BlobStyle.liquid,
    AstroElement.earth => BlobStyle.solid,
    AstroElement.air => BlobStyle.airy,
  };
}

ShapeFamily _shapeFamilyFor(AstroElement element) {
  return switch (element) {
    AstroElement.fire => ShapeFamily.fire,
    AstroElement.water => ShapeFamily.water,
    AstroElement.earth => ShapeFamily.earth,
    AstroElement.air => ShapeFamily.air,
  };
}

double _clamp(double value, double min, double max) {
  return math.max(min, math.min(max, value));
}
