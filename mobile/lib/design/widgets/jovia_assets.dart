import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';

import 'package:mobile/design/assets/divider_asset_resolver.dart';
import 'package:mobile/design/assets/element_asset_resolver.dart';
import 'package:mobile/design/assets/editorial_art_asset_resolver.dart';
import 'package:mobile/design/assets/planet_asset_resolver.dart';
import 'package:mobile/design/theme/profile_theme_extension.dart';

export 'package:mobile/design/assets/divider_asset_resolver.dart';
export 'package:mobile/design/assets/element_asset_resolver.dart';
export 'package:mobile/design/assets/editorial_art_asset_resolver.dart';
export 'package:mobile/design/assets/planet_asset_resolver.dart';

enum JoviaUiAsset {
  homePortal,
  heartOrbit,
  chatOrbit,
  menuStack,
  calendarLunar,
  settingsRings,
  editPen,
  plusCrosshair,
  connectionsTwins,
  profileComet,
  orbitPlanet,
  back,
  chevronRight,
  checkSeal,
  logoutArc,
  search,
}

class JoviaBrandMark extends StatelessWidget {
  const JoviaBrandMark({
    super.key,
    this.width = 54,
    this.opacity = 0.88,
    this.alignment = Alignment.centerLeft,
    this.color,
  });

  final double width;
  final double opacity;
  final Alignment alignment;
  final Color? color;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final resolvedColor =
        color ?? (isDark ? const Color(0xFFF8F2EC) : profile.colors.text);
    final glyphStart = Color.alphaBlend(
      profile.colors.warmAccent.withValues(alpha: isDark ? 0.34 : 0.76),
      resolvedColor.withValues(alpha: 0.14),
    );
    final glyphEnd = Color.alphaBlend(
      profile.colors.primary.withValues(alpha: isDark ? 0.42 : 0.56),
      resolvedColor.withValues(alpha: 0.08),
    );
    return Align(
      alignment: alignment,
      child: Opacity(
        opacity: opacity,
        child: SizedBox(
          width: width,
          height: width * 0.28,
          child: FittedBox(
            fit: BoxFit.contain,
            alignment: Alignment.centerLeft,
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  width: 18,
                  height: 18,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    gradient: LinearGradient(
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                      colors: [glyphStart, glyphEnd],
                    ),
                    border: Border.all(
                      color: Colors.white.withValues(
                        alpha: isDark ? 0.14 : 0.72,
                      ),
                    ),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withValues(
                          alpha: isDark ? 0.18 : 0.08,
                        ),
                        blurRadius: 12,
                        offset: const Offset(0, 4),
                        spreadRadius: -8,
                      ),
                    ],
                  ),
                  child: Center(
                    child: Container(
                      width: 5,
                      height: 5,
                      decoration: BoxDecoration(
                        color: resolvedColor.withValues(alpha: 0.88),
                        shape: BoxShape.circle,
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                Text(
                  'SHOU',
                  style: TextStyle(
                    fontSize: 34,
                    height: 1,
                    fontWeight: FontWeight.w600,
                    letterSpacing: 4.2,
                    color: resolvedColor,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class JoviaUiIcon extends StatelessWidget {
  const JoviaUiIcon({
    super.key,
    required this.asset,
    this.size = 18,
    this.color,
    this.strokeWidth,
  });

  final JoviaUiAsset asset;
  final double size;
  final Color? color;
  final double? strokeWidth;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final resolvedColor =
        color ?? IconTheme.of(context).color ?? profile.colors.primary;
    return SizedBox.square(
      dimension: size,
      child: CustomPaint(
        painter: _JoviaUiIconPainter(
          asset: asset,
          color: resolvedColor,
          strokeWidth: strokeWidth ?? math.max(1.6, size * 0.1),
        ),
      ),
    );
  }
}

class JoviaColorWash extends StatelessWidget {
  const JoviaColorWash({
    super.key,
    required this.asset,
    this.fit = BoxFit.cover,
    this.opacity = 0.18,
    this.alignment = Alignment.center,
  });

  final JoviaColorAsset asset;
  final BoxFit fit;
  final double opacity;
  final Alignment alignment;

  @override
  Widget build(BuildContext context) {
    return IgnorePointer(
      child: Opacity(
        opacity: opacity,
        child: SvgPicture.asset(asset.path, fit: fit, alignment: alignment),
      ),
    );
  }
}

class JoviaIllustrationAccent extends StatelessWidget {
  const JoviaIllustrationAccent({
    super.key,
    required this.asset,
    this.width,
    this.height,
    this.opacity = 0.9,
    this.fit = BoxFit.contain,
  });

  final JoviaIllustrationAsset asset;
  final double? width;
  final double? height;
  final double opacity;
  final BoxFit fit;

  @override
  Widget build(BuildContext context) {
    return IgnorePointer(
      child: Opacity(
        opacity: opacity,
        child: SvgPicture.asset(
          asset.path,
          width: width,
          height: height,
          fit: fit,
        ),
      ),
    );
  }
}

class JoviaElementArt extends StatelessWidget {
  const JoviaElementArt({
    super.key,
    required this.asset,
    this.width,
    this.height,
    this.opacity = 0.96,
    this.fit = BoxFit.contain,
  });

  final JoviaElementAsset asset;
  final double? width;
  final double? height;
  final double opacity;
  final BoxFit fit;

  @override
  Widget build(BuildContext context) {
    return IgnorePointer(
      child: Opacity(
        opacity: opacity,
        child: SvgPicture.asset(
          asset.path,
          width: width,
          height: height,
          fit: fit,
        ),
      ),
    );
  }
}

class JoviaNarrativeGlyph extends StatelessWidget {
  const JoviaNarrativeGlyph({
    super.key,
    required this.asset,
    this.size = 16,
    this.opacity = 0.92,
  });

  final JoviaNarrativeAsset asset;
  final double size;
  final double opacity;

  @override
  Widget build(BuildContext context) {
    return JoviaIllustrationAccent(
      asset: asset.illustration,
      width: size,
      height: size,
      opacity: opacity,
    );
  }
}

class JoviaDividerAsset extends StatelessWidget {
  const JoviaDividerAsset({
    super.key,
    required this.kind,
    this.width = 132,
    this.color,
    this.opacity = 0.78,
  });

  final JoviaDividerKind kind;
  final double width;
  final Color? color;
  final double opacity;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Center(
      child: Opacity(
        opacity: opacity,
        child: SvgPicture.asset(
          kind.path,
          width: width,
          fit: BoxFit.fitWidth,
          alignment: Alignment.center,
          colorFilter: ColorFilter.mode(
            color ?? profile.colors.primary.withValues(alpha: 0.82),
            BlendMode.srcIn,
          ),
        ),
      ),
    );
  }
}

class JoviaPlanetGlyph extends StatelessWidget {
  const JoviaPlanetGlyph({
    super.key,
    required this.asset,
    this.size = 16,
    this.color,
    this.opacity = 0.92,
  });

  final JoviaPlanetAsset asset;
  final double size;
  final Color? color;
  final double opacity;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final resolvedColor = color ?? profile.colors.primary;
    return SizedBox.square(
      dimension: size,
      child: Opacity(
        opacity: opacity,
        child: SvgPicture.asset(
          asset.path,
          width: size,
          height: size,
          fit: BoxFit.contain,
          colorFilter: asset.tintable
              ? ColorFilter.mode(resolvedColor, BlendMode.srcIn)
              : null,
        ),
      ),
    );
  }
}

class _JoviaUiIconPainter extends CustomPainter {
  const _JoviaUiIconPainter({
    required this.asset,
    required this.color,
    required this.strokeWidth,
  });

  final JoviaUiAsset asset;
  final Color color;
  final double strokeWidth;

  @override
  void paint(Canvas canvas, Size size) {
    final stroke = Paint()
      ..color = color
      ..strokeWidth = strokeWidth
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;
    final fill = Paint()
      ..color = color
      ..style = PaintingStyle.fill;
    switch (asset) {
      case JoviaUiAsset.homePortal:
        _paintHome(canvas, size, stroke);
        break;
      case JoviaUiAsset.heartOrbit:
        _paintHeart(canvas, size, stroke);
        break;
      case JoviaUiAsset.chatOrbit:
        _paintChat(canvas, size, stroke, fill);
        break;
      case JoviaUiAsset.menuStack:
        _paintMenu(canvas, size, stroke);
        break;
      case JoviaUiAsset.calendarLunar:
        _paintCalendar(canvas, size, stroke);
        break;
      case JoviaUiAsset.settingsRings:
        _paintSettings(canvas, size, stroke, fill);
        break;
      case JoviaUiAsset.editPen:
        _paintEdit(canvas, size, stroke, fill);
        break;
      case JoviaUiAsset.plusCrosshair:
        _paintPlus(canvas, size, stroke);
        break;
      case JoviaUiAsset.connectionsTwins:
        _paintConnections(canvas, size, stroke, fill);
        break;
      case JoviaUiAsset.profileComet:
        _paintProfile(canvas, size, stroke, fill);
        break;
      case JoviaUiAsset.orbitPlanet:
        _paintOrbit(canvas, size, stroke, fill);
        break;
      case JoviaUiAsset.back:
        _paintBack(canvas, size, stroke);
        break;
      case JoviaUiAsset.chevronRight:
        _paintChevron(canvas, size, stroke);
        break;
      case JoviaUiAsset.checkSeal:
        _paintCheck(canvas, size, stroke, fill);
        break;
      case JoviaUiAsset.logoutArc:
        _paintLogout(canvas, size, stroke);
        break;
      case JoviaUiAsset.search:
        _paintSearch(canvas, size, stroke);
        break;
    }
  }

  void _paintHome(Canvas canvas, Size size, Paint stroke) {
    final body = RRect.fromRectAndRadius(
      Rect.fromLTWH(
        size.width * 0.2,
        size.height * 0.4,
        size.width * 0.6,
        size.height * 0.34,
      ),
      Radius.circular(size.width * 0.12),
    );
    final roof = Path()
      ..moveTo(size.width * 0.17, size.height * 0.47)
      ..lineTo(size.width * 0.5, size.height * 0.2)
      ..lineTo(size.width * 0.83, size.height * 0.47);
    canvas.drawPath(roof, stroke);
    canvas.drawRRect(body, stroke);
    canvas.drawLine(
      Offset(size.width * 0.46, size.height * 0.74),
      Offset(size.width * 0.46, size.height * 0.55),
      stroke,
    );
    canvas.drawLine(
      Offset(size.width * 0.54, size.height * 0.74),
      Offset(size.width * 0.54, size.height * 0.55),
      stroke,
    );
  }

  void _paintHeart(Canvas canvas, Size size, Paint stroke) {
    final path = Path()
      ..moveTo(size.width * 0.5, size.height * 0.78)
      ..cubicTo(
        size.width * 0.12,
        size.height * 0.53,
        size.width * 0.18,
        size.height * 0.18,
        size.width * 0.42,
        size.height * 0.26,
      )
      ..cubicTo(
        size.width * 0.48,
        size.height * 0.28,
        size.width * 0.5,
        size.height * 0.34,
        size.width * 0.5,
        size.height * 0.34,
      )
      ..cubicTo(
        size.width * 0.5,
        size.height * 0.34,
        size.width * 0.52,
        size.height * 0.28,
        size.width * 0.58,
        size.height * 0.26,
      )
      ..cubicTo(
        size.width * 0.82,
        size.height * 0.18,
        size.width * 0.88,
        size.height * 0.53,
        size.width * 0.5,
        size.height * 0.78,
      );
    canvas.drawPath(path, stroke);
  }

  void _paintChat(Canvas canvas, Size size, Paint stroke, Paint fill) {
    final bubble = RRect.fromRectAndRadius(
      Rect.fromLTWH(
        size.width * 0.14,
        size.height * 0.18,
        size.width * 0.72,
        size.height * 0.5,
      ),
      Radius.circular(size.width * 0.18),
    );
    final tail = Path()
      ..moveTo(size.width * 0.34, size.height * 0.68)
      ..lineTo(size.width * 0.28, size.height * 0.84)
      ..lineTo(size.width * 0.44, size.height * 0.71);
    canvas.drawRRect(bubble, stroke);
    canvas.drawPath(tail, stroke);
    for (final x in <double>[0.35, 0.5, 0.65]) {
      canvas.drawCircle(
        Offset(size.width * x, size.height * 0.43),
        size.width * 0.045,
        fill,
      );
    }
  }

  void _paintMenu(Canvas canvas, Size size, Paint stroke) {
    canvas.drawLine(
      Offset(size.width * 0.2, size.height * 0.28),
      Offset(size.width * 0.72, size.height * 0.28),
      stroke,
    );
    canvas.drawLine(
      Offset(size.width * 0.2, size.height * 0.5),
      Offset(size.width * 0.82, size.height * 0.5),
      stroke,
    );
    canvas.drawLine(
      Offset(size.width * 0.2, size.height * 0.72),
      Offset(size.width * 0.62, size.height * 0.72),
      stroke,
    );
  }

  void _paintCalendar(Canvas canvas, Size size, Paint stroke) {
    final frame = RRect.fromRectAndRadius(
      Rect.fromLTWH(
        size.width * 0.16,
        size.height * 0.2,
        size.width * 0.68,
        size.height * 0.6,
      ),
      Radius.circular(size.width * 0.15),
    );
    canvas.drawRRect(frame, stroke);
    canvas.drawLine(
      Offset(size.width * 0.16, size.height * 0.39),
      Offset(size.width * 0.84, size.height * 0.39),
      stroke,
    );
    canvas.drawLine(
      Offset(size.width * 0.31, size.height * 0.14),
      Offset(size.width * 0.31, size.height * 0.28),
      stroke,
    );
    canvas.drawLine(
      Offset(size.width * 0.69, size.height * 0.14),
      Offset(size.width * 0.69, size.height * 0.28),
      stroke,
    );
    final outerMoon = Rect.fromCircle(
      center: Offset(size.width * 0.49, size.height * 0.58),
      radius: size.width * 0.12,
    );
    final innerMoon = Rect.fromCircle(
      center: Offset(size.width * 0.56, size.height * 0.58),
      radius: size.width * 0.11,
    );
    canvas.drawArc(outerMoon, math.pi * 0.28, math.pi * 1.44, false, stroke);
    canvas.drawArc(innerMoon, math.pi * 0.2, math.pi * 1.44, false, stroke);
  }

  void _paintSettings(Canvas canvas, Size size, Paint stroke, Paint fill) {
    canvas.drawCircle(
      Offset(size.width * 0.5, size.height * 0.5),
      size.width * 0.22,
      stroke,
    );
    canvas.drawCircle(
      Offset(size.width * 0.5, size.height * 0.5),
      size.width * 0.06,
      fill,
    );
    for (final angle in <double>[0, math.pi / 2, math.pi, math.pi * 1.5]) {
      final center = Offset(
        size.width * 0.5 + math.cos(angle) * size.width * 0.31,
        size.height * 0.5 + math.sin(angle) * size.height * 0.31,
      );
      canvas.drawCircle(center, size.width * 0.035, fill);
    }
  }

  void _paintEdit(Canvas canvas, Size size, Paint stroke, Paint fill) {
    final body = Path()
      ..moveTo(size.width * 0.24, size.height * 0.68)
      ..lineTo(size.width * 0.34, size.height * 0.78)
      ..lineTo(size.width * 0.76, size.height * 0.36)
      ..lineTo(size.width * 0.66, size.height * 0.26)
      ..close();
    canvas.drawPath(body, stroke);
    canvas.drawLine(
      Offset(size.width * 0.2, size.height * 0.82),
      Offset(size.width * 0.4, size.height * 0.76),
      stroke,
    );
    canvas.drawCircle(
      Offset(size.width * 0.72, size.height * 0.3),
      size.width * 0.025,
      fill,
    );
  }

  void _paintPlus(Canvas canvas, Size size, Paint stroke) {
    canvas.drawCircle(
      Offset(size.width * 0.5, size.height * 0.5),
      size.width * 0.32,
      Paint()
        ..color = color.withValues(alpha: 0.16)
        ..style = PaintingStyle.fill,
    );
    canvas.drawLine(
      Offset(size.width * 0.5, size.height * 0.24),
      Offset(size.width * 0.5, size.height * 0.76),
      stroke,
    );
    canvas.drawLine(
      Offset(size.width * 0.24, size.height * 0.5),
      Offset(size.width * 0.76, size.height * 0.5),
      stroke,
    );
  }

  void _paintConnections(Canvas canvas, Size size, Paint stroke, Paint fill) {
    final left = Offset(size.width * 0.33, size.height * 0.35);
    final right = Offset(size.width * 0.67, size.height * 0.35);
    canvas.drawCircle(left, size.width * 0.11, stroke);
    canvas.drawCircle(right, size.width * 0.11, stroke);
    final link = Path()
      ..moveTo(size.width * 0.28, size.height * 0.63)
      ..quadraticBezierTo(
        size.width * 0.5,
        size.height * 0.44,
        size.width * 0.72,
        size.height * 0.63,
      );
    canvas.drawPath(link, stroke);
    canvas.drawCircle(
      Offset(size.width * 0.5, size.height * 0.63),
      size.width * 0.035,
      fill,
    );
  }

  void _paintProfile(Canvas canvas, Size size, Paint stroke, Paint fill) {
    canvas.drawCircle(
      Offset(size.width * 0.5, size.height * 0.33),
      size.width * 0.16,
      stroke,
    );
    final body = Path()
      ..moveTo(size.width * 0.24, size.height * 0.76)
      ..quadraticBezierTo(
        size.width * 0.3,
        size.height * 0.54,
        size.width * 0.5,
        size.height * 0.54,
      )
      ..quadraticBezierTo(
        size.width * 0.7,
        size.height * 0.54,
        size.width * 0.76,
        size.height * 0.76,
      );
    canvas.drawPath(body, stroke);
    canvas.drawCircle(
      Offset(size.width * 0.78, size.height * 0.18),
      size.width * 0.04,
      fill,
    );
  }

  void _paintOrbit(Canvas canvas, Size size, Paint stroke, Paint fill) {
    canvas.drawCircle(
      Offset(size.width * 0.48, size.height * 0.5),
      size.width * 0.15,
      stroke,
    );
    final orbit = Rect.fromLTWH(
      size.width * 0.12,
      size.height * 0.27,
      size.width * 0.72,
      size.height * 0.42,
    );
    canvas.drawOval(orbit, stroke);
    canvas.drawCircle(
      Offset(size.width * 0.73, size.height * 0.35),
      size.width * 0.05,
      fill,
    );
  }

  void _paintBack(Canvas canvas, Size size, Paint stroke) {
    final path = Path()
      ..moveTo(size.width * 0.68, size.height * 0.2)
      ..lineTo(size.width * 0.32, size.height * 0.5)
      ..lineTo(size.width * 0.68, size.height * 0.8);
    canvas.drawPath(path, stroke);
  }

  void _paintChevron(Canvas canvas, Size size, Paint stroke) {
    final path = Path()
      ..moveTo(size.width * 0.34, size.height * 0.22)
      ..lineTo(size.width * 0.64, size.height * 0.5)
      ..lineTo(size.width * 0.34, size.height * 0.78);
    canvas.drawPath(path, stroke);
  }

  void _paintSearch(Canvas canvas, Size size, Paint stroke) {
    canvas.drawCircle(
      Offset(size.width * 0.43, size.height * 0.43),
      size.width * 0.2,
      stroke,
    );
    canvas.drawLine(
      Offset(size.width * 0.58, size.height * 0.58),
      Offset(size.width * 0.78, size.height * 0.78),
      stroke,
    );
  }

  void _paintCheck(Canvas canvas, Size size, Paint stroke, Paint fill) {
    canvas.drawCircle(
      Offset(size.width * 0.5, size.height * 0.5),
      size.width * 0.32,
      Paint()
        ..color = color.withValues(alpha: 0.12)
        ..style = PaintingStyle.fill,
    );
    final path = Path()
      ..moveTo(size.width * 0.28, size.height * 0.52)
      ..lineTo(size.width * 0.45, size.height * 0.68)
      ..lineTo(size.width * 0.74, size.height * 0.34);
    canvas.drawPath(path, stroke);
    canvas.drawCircle(
      Offset(size.width * 0.74, size.height * 0.34),
      size.width * 0.02,
      fill,
    );
  }

  void _paintLogout(Canvas canvas, Size size, Paint stroke) {
    canvas.drawArc(
      Rect.fromLTWH(
        size.width * 0.16,
        size.height * 0.18,
        size.width * 0.48,
        size.height * 0.64,
      ),
      math.pi * 0.35,
      math.pi * 1.3,
      false,
      stroke,
    );
    canvas.drawLine(
      Offset(size.width * 0.48, size.height * 0.5),
      Offset(size.width * 0.84, size.height * 0.5),
      stroke,
    );
    final arrow = Path()
      ..moveTo(size.width * 0.68, size.height * 0.34)
      ..lineTo(size.width * 0.84, size.height * 0.5)
      ..lineTo(size.width * 0.68, size.height * 0.66);
    canvas.drawPath(arrow, stroke);
  }

  @override
  bool shouldRepaint(covariant _JoviaUiIconPainter other) {
    return other.asset != asset ||
        other.color != color ||
        other.strokeWidth != strokeWidth;
  }
}
