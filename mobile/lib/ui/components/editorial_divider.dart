import 'package:flutter/material.dart';

import 'package:mobile/design/theme/profile_theme_extension.dart';

class EditorialDivider extends StatelessWidget {
  const EditorialDivider({
    super.key,
    this.symbol = '✦',
    this.iconData,
    this.iconSize = 16,
    this.lineColor,
    this.iconColor,
    this.lineOpacity = 0.22,
    this.thickness = 1,
    this.padding = const EdgeInsets.symmetric(vertical: 12),
    this.gap = 12,
  });

  final String? symbol;
  final IconData? iconData;
  final double iconSize;
  final Color? lineColor;
  final Color? iconColor;
  final double lineOpacity;
  final double thickness;
  final EdgeInsets padding;
  final double gap;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final resolvedLineColor = (lineColor ?? profile.colors.strokeSoft).withValues(
      alpha: lineOpacity,
    );
    final resolvedIconColor =
        (iconColor ?? profile.colors.primary).withValues(alpha: 0.6);
    final glyph = (symbol == null || symbol!.trim().isEmpty) ? '✦' : symbol!;

    return Padding(
      padding: padding,
      child: SizedBox(
        height: 24,
        child: Row(
          children: [
            Expanded(
              child: Container(height: thickness, color: resolvedLineColor),
            ),
            SizedBox(width: gap),
            if (iconData != null)
              Icon(iconData, size: iconSize, color: resolvedIconColor)
            else
              Text(
                glyph,
                style: TextStyle(
                  fontSize: iconSize,
                  height: 1,
                  color: resolvedIconColor,
                  fontWeight: FontWeight.w500,
                ),
              ),
            SizedBox(width: gap),
            Expanded(
              child: Container(height: thickness, color: resolvedLineColor),
            ),
          ],
        ),
      ),
    );
  }
}

class WavyDivider extends StatelessWidget {
  const WavyDivider({
    super.key,
    this.color,
    this.opacity = 0.35,
    this.strokeWidth = 1,
    this.padding = const EdgeInsets.symmetric(vertical: 12),
    this.height = 24,
  });

  final Color? color;
  final double opacity;
  final double strokeWidth;
  final EdgeInsets padding;
  final double height;

  @override
  Widget build(BuildContext context) {
    final resolvedColor = (color ?? context.profileTheme.colors.strokeSoft)
        .withValues(
      alpha: opacity,
    );

    return Padding(
      padding: padding,
      child: SizedBox(
        height: height,
        width: double.infinity,
        child: CustomPaint(
          painter: _WavyDividerPainter(
            color: resolvedColor,
            strokeWidth: strokeWidth,
          ),
        ),
      ),
    );
  }
}

class _WavyDividerPainter extends CustomPainter {
  const _WavyDividerPainter({required this.color, required this.strokeWidth});

  final Color color;
  final double strokeWidth;

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..strokeWidth = strokeWidth
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;

    final path = Path();
    final centerY = size.height / 2;
    final waveHeight = size.height * 0.12;
    const waveCount = 4;
    final segment = size.width / waveCount;

    path.moveTo(0, centerY);
    for (var i = 0; i < waveCount; i++) {
      final x0 = i * segment;
      final x1 = x0 + segment / 2;
      final x2 = x0 + segment;
      path.quadraticBezierTo(x1, centerY - waveHeight, x2, centerY);
    }

    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant _WavyDividerPainter oldDelegate) {
    return oldDelegate.color != color || oldDelegate.strokeWidth != strokeWidth;
  }
}
