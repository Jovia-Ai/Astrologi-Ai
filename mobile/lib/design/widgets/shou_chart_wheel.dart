import 'dart:math' as math;

import 'package:flutter/material.dart';

import 'package:mobile/app/chart/chart_wheel_data.dart';
import 'package:mobile/design/theme/profile_theme_extension.dart';

enum ChartWheelMode { profilePreview, homePreview, fullDetail }

class ShouChartWheel extends StatelessWidget {
  const ShouChartWheel({
    super.key,
    required this.data,
    this.mode = ChartWheelMode.profilePreview,
  });

  final ChartWheelData data;
  final ChartWheelMode mode;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final colors = profile.colors;
    final palette = _ChartWheelPalette(
      background: Color.alphaBlend(
        colors.lavender.withValues(alpha: 0.18),
        colors.surface,
      ),
      ring: Color.alphaBlend(
        colors.strokeSoft.withValues(alpha: 0.9),
        colors.surface,
      ),
      ringSoft: colors.separator.withValues(alpha: 0.9),
      glow: Color.alphaBlend(
        colors.primary.withValues(alpha: 0.2),
        colors.surface,
      ),
      accent: colors.brandLime,
      accentSoft: colors.brandLime.withValues(alpha: 0.18),
      warmAccent: colors.brandBlush.withValues(alpha: 0.82),
      text: colors.text,
      muted: colors.muted,
      marker: colors.neonPink.withValues(alpha: 0.9),
    );

    return LayoutBuilder(
      builder: (context, constraints) {
        final finiteWidth = constraints.maxWidth.isFinite;
        final finiteHeight = constraints.maxHeight.isFinite;
        final fallbackSize = mode == ChartWheelMode.fullDetail ? 320.0 : 220.0;
        final size = [
          if (finiteWidth) constraints.maxWidth,
          if (finiteHeight) constraints.maxHeight,
          fallbackSize,
        ].reduce(math.min);

        return SizedBox.square(
          dimension: size,
          child: RepaintBoundary(
            child: CustomPaint(
              painter: _ShouChartWheelPainter(
                data: data,
                mode: mode,
                palette: palette,
                labelStyle: profile.typography.chipLabel,
                metaStyle: profile.typography.meta,
              ),
            ),
          ),
        );
      },
    );
  }
}

class _ShouChartWheelPainter extends CustomPainter {
  const _ShouChartWheelPainter({
    required this.data,
    required this.mode,
    required this.palette,
    required this.labelStyle,
    required this.metaStyle,
  });

  final ChartWheelData data;
  final ChartWheelMode mode;
  final _ChartWheelPalette palette;
  final TextStyle labelStyle;
  final TextStyle metaStyle;

  @override
  void paint(Canvas canvas, Size size) {
    final center = size.center(Offset.zero);
    final metrics = _WheelMetrics.fromSize(size, mode);

    _paintGlow(canvas, center, metrics);
    _paintRings(canvas, center, metrics);
    _paintZodiac(canvas, center, metrics);
    _paintHouses(canvas, center, metrics);
    _paintMarkers(canvas, center, metrics);
    _paintPlanets(canvas, center, metrics);
    _paintCenter(canvas, center, metrics);
  }

  void _paintGlow(Canvas canvas, Offset center, _WheelMetrics metrics) {
    final rect = Rect.fromCircle(
      center: center,
      radius: metrics.outerRadius * 1.06,
    );
    final glow = Paint()
      ..shader = RadialGradient(
        colors: [
          palette.glow.withValues(alpha: 0.26),
          palette.glow.withValues(alpha: 0.08),
          Colors.transparent,
        ],
        stops: const [0.0, 0.58, 1.0],
      ).createShader(rect);
    canvas.drawCircle(center, metrics.outerRadius * 1.06, glow);
  }

  void _paintRings(Canvas canvas, Offset center, _WheelMetrics metrics) {
    final fill = Paint()
      ..style = PaintingStyle.fill
      ..color = palette.background;
    final ring = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = metrics.lineWidth
      ..color = palette.ring;
    final softRing = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = metrics.lineWidth * 0.9
      ..color = palette.ringSoft;

    canvas.drawCircle(center, metrics.outerRadius, fill);
    canvas.drawCircle(center, metrics.outerRadius, ring);
    canvas.drawCircle(center, metrics.zodiacInnerRadius, ring);
    canvas.drawCircle(center, metrics.houseRadius, softRing);
    canvas.drawCircle(center, metrics.innerRadius, softRing);
  }

  void _paintZodiac(Canvas canvas, Offset center, _WheelMetrics metrics) {
    final divider = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = metrics.lineWidth * 0.8
      ..color = palette.ringSoft.withValues(alpha: 0.95);
    for (var index = 0; index < 12; index++) {
      final startAngle = _angleForLongitude(index * 30.0);
      final inner = _polar(center, metrics.zodiacInnerRadius, startAngle);
      final outer = _polar(center, metrics.outerRadius, startAngle);
      canvas.drawLine(inner, outer, divider);

      final labelAngle = _angleForLongitude(index * 30.0 + 15.0);
      final labelOffset = _polar(center, metrics.signLabelRadius, labelAngle);
      _drawText(
        canvas,
        _zodiacShort[index],
        labelOffset,
        metaStyle.copyWith(
          color: palette.muted.withValues(alpha: 0.94),
          fontSize: metrics.signFontSize,
          fontWeight: FontWeight.w600,
          letterSpacing: 0.8,
        ),
      );
    }
  }

  void _paintHouses(Canvas canvas, Offset center, _WheelMetrics metrics) {
    final spokes = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = metrics.lineWidth * 0.8
      ..color = palette.ring.withValues(alpha: 0.74);

    for (var index = 0; index < data.houseCusps.length; index++) {
      final angle = _angleForLongitude(data.houseCusps[index]);
      canvas.drawLine(
        _polar(center, metrics.innerRadius, angle),
        _polar(center, metrics.houseRadius, angle),
        spokes,
      );

      if (mode != ChartWheelMode.fullDetail) {
        continue;
      }
      final next = data.houseCusps[(index + 1) % data.houseCusps.length];
      final delta = ((next - data.houseCusps[index]) + 360) % 360;
      final midLongitude = data.houseCusps[index] + (delta / 2);
      _drawText(
        canvas,
        '${index + 1}',
        _polar(
          center,
          metrics.houseNumberRadius,
          _angleForLongitude(midLongitude),
        ),
        metaStyle.copyWith(
          color: palette.muted,
          fontSize: metrics.houseFontSize,
          fontWeight: FontWeight.w600,
        ),
      );
    }
  }

  void _paintMarkers(Canvas canvas, Offset center, _WheelMetrics metrics) {
    _paintAxisMarker(
      canvas,
      center,
      metrics,
      longitude: data.ascDegree,
      label: 'ASC',
      color: palette.accent,
    );
    _paintAxisMarker(
      canvas,
      center,
      metrics,
      longitude: data.mcDegree,
      label: 'MC',
      color: palette.marker,
    );
  }

  void _paintAxisMarker(
    Canvas canvas,
    Offset center,
    _WheelMetrics metrics, {
    required double longitude,
    required String label,
    required Color color,
  }) {
    final angle = _angleForLongitude(longitude);
    final tip = _polar(
      center,
      metrics.outerRadius + metrics.markerInset,
      angle,
    );
    final base = _polar(
      center,
      metrics.outerRadius - metrics.markerTail,
      angle,
    );
    final tangent = Offset(-math.sin(angle), math.cos(angle));
    final normal = Offset(math.cos(angle), math.sin(angle));

    final path = Path()
      ..moveTo(tip.dx, tip.dy)
      ..lineTo(
        base.dx + tangent.dx * metrics.markerWidth,
        base.dy + tangent.dy * metrics.markerWidth,
      )
      ..lineTo(
        base.dx - tangent.dx * metrics.markerWidth,
        base.dy - tangent.dy * metrics.markerWidth,
      )
      ..close();
    canvas.drawPath(path, Paint()..color = color.withValues(alpha: 0.96));

    final labelOffset = Offset(
      tip.dx + normal.dx * metrics.markerLabelGap,
      tip.dy + normal.dy * metrics.markerLabelGap,
    );
    _drawText(
      canvas,
      label,
      labelOffset,
      labelStyle.copyWith(
        color: color,
        fontSize: metrics.markerFontSize,
        fontWeight: FontWeight.w700,
        letterSpacing: 0.7,
      ),
    );
  }

  void _paintPlanets(Canvas canvas, Offset center, _WheelMetrics metrics) {
    final layouts = _resolvePlanetLayouts(metrics);
    for (final layout in layouts) {
      final offset = _polar(center, layout.radius, layout.angle);
      final planetColor = _planetColor(layout.point.id);
      final fill = Paint()..color = planetColor;
      final stroke = Paint()
        ..style = PaintingStyle.stroke
        ..strokeWidth = metrics.lineWidth
        ..color = Colors.white.withValues(alpha: 0.2);

      canvas.drawCircle(offset, metrics.planetRadius, fill);
      canvas.drawCircle(offset, metrics.planetRadius, stroke);

      _drawText(
        canvas,
        _planetAbbreviation(layout.point.id),
        offset,
        labelStyle.copyWith(
          color: _planetLabelColor(layout.point.id),
          fontSize: metrics.planetFontSize,
          fontWeight: FontWeight.w700,
          letterSpacing: 0.4,
        ),
      );

      if (mode == ChartWheelMode.fullDetail && layout.point.retrograde) {
        final retroOffset = Offset(
          offset.dx + metrics.planetRadius * 0.95,
          offset.dy - metrics.planetRadius * 0.95,
        );
        _drawText(
          canvas,
          'R',
          retroOffset,
          metaStyle.copyWith(
            color: palette.accent,
            fontSize: metrics.retroFontSize,
            fontWeight: FontWeight.w700,
          ),
        );
      }
    }
  }

  void _paintCenter(Canvas canvas, Offset center, _WheelMetrics metrics) {
    final centerFill = Paint()
      ..color = Color.alphaBlend(
        palette.accentSoft.withValues(alpha: 0.16),
        palette.background,
      );
    final centerStroke = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = metrics.lineWidth
      ..color = palette.ring;
    canvas.drawCircle(center, metrics.innerRadius * 0.7, centerFill);
    canvas.drawCircle(center, metrics.innerRadius * 0.7, centerStroke);

    final primaryText = mode == ChartWheelMode.fullDetail ? 'NATAL' : 'HARITA';
    _drawText(
      canvas,
      primaryText,
      Offset(center.dx, center.dy - metrics.centerTextGap),
      labelStyle.copyWith(
        color: palette.text,
        fontSize: metrics.centerLabelFontSize,
        fontWeight: FontWeight.w700,
        letterSpacing: 1.2,
      ),
    );
    _drawText(
      canvas,
      'ASC ${_signShortForLongitude(data.ascDegree)}',
      Offset(center.dx, center.dy + metrics.centerTextGap),
      metaStyle.copyWith(
        color: palette.muted,
        fontSize: metrics.centerMetaFontSize,
        fontWeight: FontWeight.w600,
        letterSpacing: 0.5,
      ),
    );
  }

  List<_PlanetLayout> _resolvePlanetLayouts(_WheelMetrics metrics) {
    if (data.planets.isEmpty) {
      return const <_PlanetLayout>[];
    }
    final planets =
        data.planets.map((planet) {
            final relative = ((planet.longitude - data.ascDegree) + 360) % 360;
            return _PlanetRelative(point: planet, relativeLongitude: relative);
          }).toList()
          ..sort((a, b) => a.relativeLongitude.compareTo(b.relativeLongitude));

    final clusters = <List<_PlanetRelative>>[];
    final threshold = mode == ChartWheelMode.fullDetail ? 7.0 : 9.0;
    for (final planet in planets) {
      if (clusters.isEmpty) {
        clusters.add(<_PlanetRelative>[planet]);
        continue;
      }
      final current = clusters.last;
      final previous = current.last;
      final gap =
          (planet.relativeLongitude - previous.relativeLongitude + 360) % 360;
      if (gap <= threshold) {
        current.add(planet);
      } else {
        clusters.add(<_PlanetRelative>[planet]);
      }
    }

    if (clusters.length > 1) {
      final first = clusters.first;
      final last = clusters.last;
      final wrapGap =
          ((first.first.relativeLongitude + 360) -
              last.last.relativeLongitude) %
          360;
      if (wrapGap <= threshold) {
        first.insertAll(0, last);
        clusters.removeLast();
      }
    }

    final layouts = <_PlanetLayout>[];
    for (final cluster in clusters) {
      for (var index = 0; index < cluster.length; index++) {
        final item = cluster[index];
        final angle = _angleForLongitude(item.point.longitude);
        final radialStep = metrics.clusterStep * _clusterOffset(index);
        layouts.add(
          _PlanetLayout(
            point: item.point,
            angle: angle,
            radius: metrics.planetOrbitRadius + radialStep,
          ),
        );
      }
    }
    return layouts;
  }

  double _clusterOffset(int index) {
    if (index == 0) {
      return 0;
    }
    final magnitude = ((index + 1) / 2).floorToDouble();
    return index.isOdd ? magnitude : -magnitude;
  }

  double _angleForLongitude(double longitude) {
    final relative = ((longitude - data.ascDegree) + 360) % 360;
    return (relative + 180) * math.pi / 180;
  }

  Offset _polar(Offset center, double radius, double angle) {
    return Offset(
      center.dx + radius * math.cos(angle),
      center.dy + radius * math.sin(angle),
    );
  }

  void _drawText(Canvas canvas, String text, Offset center, TextStyle style) {
    final painter = TextPainter(
      text: TextSpan(text: text, style: style),
      textDirection: TextDirection.ltr,
      textAlign: TextAlign.center,
    )..layout();
    painter.paint(
      canvas,
      Offset(center.dx - painter.width / 2, center.dy - painter.height / 2),
    );
  }

  Color _planetColor(String id) {
    return switch (id) {
      'sun' => palette.text,
      'moon' => palette.accent,
      'mercury' => palette.warmAccent,
      'venus' => const Color(0xFF8E7FDB),
      'mars' => const Color(0xFFB95B61),
      'jupiter' => const Color(0xFF5B7FA4),
      'saturn' => const Color(0xFF6B6F77),
      'uranus' => const Color(0xFF699A9E),
      'neptune' => const Color(0xFF5670B8),
      'pluto' => const Color(0xFF7C5B7B),
      'north_node' => palette.accent,
      'south_node' => palette.marker,
      'chiron' => palette.warmAccent,
      'lilith' => palette.marker,
      'fortune' => palette.accent,
      'vertex' => palette.text,
      _ => palette.text.withValues(alpha: 0.85),
    };
  }

  Color _planetLabelColor(String id) {
    return switch (id) {
      'moon' || 'north_node' || 'fortune' => const Color(0xFF1A3300),
      _ => Colors.white,
    };
  }

  @override
  bool shouldRepaint(covariant _ShouChartWheelPainter oldDelegate) {
    return oldDelegate.data != data ||
        oldDelegate.mode != mode ||
        oldDelegate.palette != palette ||
        oldDelegate.labelStyle != labelStyle ||
        oldDelegate.metaStyle != metaStyle;
  }
}

class _WheelMetrics {
  const _WheelMetrics({
    required this.outerRadius,
    required this.zodiacInnerRadius,
    required this.houseRadius,
    required this.innerRadius,
    required this.planetOrbitRadius,
    required this.signLabelRadius,
    required this.houseNumberRadius,
    required this.lineWidth,
    required this.planetRadius,
    required this.clusterStep,
    required this.signFontSize,
    required this.houseFontSize,
    required this.planetFontSize,
    required this.markerFontSize,
    required this.markerInset,
    required this.markerTail,
    required this.markerWidth,
    required this.markerLabelGap,
    required this.retroFontSize,
    required this.centerLabelFontSize,
    required this.centerMetaFontSize,
    required this.centerTextGap,
  });

  final double outerRadius;
  final double zodiacInnerRadius;
  final double houseRadius;
  final double innerRadius;
  final double planetOrbitRadius;
  final double signLabelRadius;
  final double houseNumberRadius;
  final double lineWidth;
  final double planetRadius;
  final double clusterStep;
  final double signFontSize;
  final double houseFontSize;
  final double planetFontSize;
  final double markerFontSize;
  final double markerInset;
  final double markerTail;
  final double markerWidth;
  final double markerLabelGap;
  final double retroFontSize;
  final double centerLabelFontSize;
  final double centerMetaFontSize;
  final double centerTextGap;

  factory _WheelMetrics.fromSize(Size size, ChartWheelMode mode) {
    final dimension = math.min(size.width, size.height);
    final detail = mode == ChartWheelMode.fullDetail;
    return _WheelMetrics(
      outerRadius: dimension * 0.47,
      zodiacInnerRadius: dimension * 0.395,
      houseRadius: dimension * 0.34,
      innerRadius: dimension * 0.18,
      planetOrbitRadius: dimension * (detail ? 0.295 : 0.285),
      signLabelRadius: dimension * 0.432,
      houseNumberRadius: dimension * 0.255,
      lineWidth: math.max(1, dimension * 0.0048),
      planetRadius: detail ? dimension * 0.033 : dimension * 0.03,
      clusterStep: detail ? dimension * 0.028 : dimension * 0.024,
      signFontSize: detail ? dimension * 0.027 : dimension * 0.024,
      houseFontSize: dimension * 0.026,
      planetFontSize: detail ? dimension * 0.023 : dimension * 0.021,
      markerFontSize: detail ? dimension * 0.029 : dimension * 0.024,
      markerInset: dimension * 0.03,
      markerTail: dimension * 0.02,
      markerWidth: dimension * 0.014,
      markerLabelGap: dimension * 0.055,
      retroFontSize: dimension * 0.022,
      centerLabelFontSize: detail ? dimension * 0.035 : dimension * 0.03,
      centerMetaFontSize: detail ? dimension * 0.026 : dimension * 0.022,
      centerTextGap: detail ? dimension * 0.034 : dimension * 0.028,
    );
  }
}

class _ChartWheelPalette {
  const _ChartWheelPalette({
    required this.background,
    required this.ring,
    required this.ringSoft,
    required this.glow,
    required this.accent,
    required this.accentSoft,
    required this.warmAccent,
    required this.text,
    required this.muted,
    required this.marker,
  });

  final Color background;
  final Color ring;
  final Color ringSoft;
  final Color glow;
  final Color accent;
  final Color accentSoft;
  final Color warmAccent;
  final Color text;
  final Color muted;
  final Color marker;
}

class _PlanetRelative {
  const _PlanetRelative({required this.point, required this.relativeLongitude});

  final ChartPlanetPoint point;
  final double relativeLongitude;
}

class _PlanetLayout {
  const _PlanetLayout({
    required this.point,
    required this.angle,
    required this.radius,
  });

  final ChartPlanetPoint point;
  final double angle;
  final double radius;
}

const List<String> _zodiacShort = <String>[
  'ARI',
  'TAU',
  'GEM',
  'CAN',
  'LEO',
  'VIR',
  'LIB',
  'SCO',
  'SAG',
  'CAP',
  'AQU',
  'PIS',
];

String _signShortForLongitude(double longitude) {
  final index = ((longitude % 360) ~/ 30) % 12;
  return _zodiacShort[index];
}

String _planetAbbreviation(String id) {
  return switch (id) {
    'sun' => 'SU',
    'moon' => 'MO',
    'mercury' => 'ME',
    'venus' => 'VE',
    'mars' => 'MA',
    'jupiter' => 'JU',
    'saturn' => 'SA',
    'uranus' => 'UR',
    'neptune' => 'NE',
    'pluto' => 'PL',
    'north_node' => 'NN',
    'south_node' => 'SN',
    'chiron' => 'CH',
    'lilith' => 'LI',
    'fortune' => 'FO',
    'vertex' => 'VX',
    _ =>
      id.toUpperCase().replaceAll('_', '').substring(0, math.min(2, id.length)),
  };
}
