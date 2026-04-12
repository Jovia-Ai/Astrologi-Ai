import 'dart:math' as math;

import 'package:flutter/material.dart';

import 'package:mobile/design/theme/profile_theme_extension.dart';

List<String> joviaHighlightLinesFromText(
  String text, {
  int maxLines = 2,
  int minLength = 14,
  int maxLength = 72,
}) {
  final normalized = text
      .replaceAll('\n', ' ')
      .replaceAll(RegExp(r'\s+'), ' ')
      .trim();
  if (normalized.isEmpty) {
    return const <String>[];
  }

  final parts = normalized
      .split(RegExp(r'(?<=[.!?;:])\s+'))
      .expand((item) => item.split(RegExp(r'\s*[,•]\s*')))
      .map((item) => item.trim())
      .where((item) => item.isNotEmpty)
      .toList(growable: false);

  final seen = <String>{};
  final lines = <String>[];
  for (final part in parts) {
    final compact = part.replaceAll(RegExp(r'\s+'), ' ').trim();
    if (compact.length < minLength) {
      continue;
    }
    final normalizedKey = compact.toLowerCase();
    if (!seen.add(normalizedKey)) {
      continue;
    }
    if (compact.length <= maxLength) {
      lines.add(compact);
    } else {
      lines.add(_trimHighlightLine(compact, maxLength));
    }
    if (lines.length == maxLines) {
      return lines;
    }
  }

  if (lines.isNotEmpty) {
    return lines;
  }
  return <String>[_trimHighlightLine(normalized, maxLength)];
}

String _trimHighlightLine(String text, int maxLength) {
  if (text.length <= maxLength) {
    return text;
  }
  final truncated = text.substring(0, maxLength);
  final boundary = truncated.lastIndexOf(' ');
  if (boundary > maxLength * 0.55) {
    return truncated.substring(0, boundary).trim();
  }
  return truncated.trim();
}

class JoviaSentenceBubbleStack extends StatelessWidget {
  const JoviaSentenceBubbleStack({
    super.key,
    required this.lines,
    this.accents = const <Color>[],
    this.centered = false,
    this.compact = false,
  });

  final List<String> lines;
  final List<Color> accents;
  final bool centered;
  final bool compact;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final resolvedLines = lines
        .map((item) => item.trim())
        .where((item) => item.isNotEmpty)
        .take(3)
        .toList(growable: false);
    if (resolvedLines.isEmpty) {
      return const SizedBox.shrink();
    }

    final palette = accents.isNotEmpty
        ? accents
        : <Color>[
            profile.colors.primary,
            profile.colors.warmAccent,
            profile.colors.lavender,
          ];
    final offsets = centered
        ? const <double>[0, 10, -6]
        : const <double>[0, 14, 6];

    return Column(
      crossAxisAlignment: centered
          ? CrossAxisAlignment.center
          : CrossAxisAlignment.start,
      children: [
        for (var index = 0; index < resolvedLines.length; index++) ...[
          Padding(
            padding: EdgeInsets.only(left: offsets[index % offsets.length]),
            child: _JoviaSentenceBubble(
              text: resolvedLines[index],
              accent: palette[index % palette.length],
              compact: compact,
              showTail: index == 0,
              isDark: isDark,
            ),
          ),
          if (index != resolvedLines.length - 1)
            SizedBox(height: compact ? 8 : 10),
        ],
      ],
    );
  }
}

class _JoviaSentenceBubble extends StatelessWidget {
  const _JoviaSentenceBubble({
    required this.text,
    required this.accent,
    required this.compact,
    required this.showTail,
    required this.isDark,
  });

  final String text;
  final Color accent;
  final bool compact;
  final bool showTail;
  final bool isDark;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final bubble = Color.alphaBlend(
      accent.withValues(alpha: isDark ? 0.18 : 0.22),
      isDark
          ? profile.colors.panelSoft.withValues(alpha: 0.96)
          : Colors.white.withValues(alpha: 0.92),
    );
    final border = Color.alphaBlend(
      accent.withValues(alpha: isDark ? 0.24 : 0.14),
      profile.colors.strokeSoft,
    );
    final radius = compact ? 16.0 : 18.0;

    return Stack(
      clipBehavior: Clip.none,
      children: [
        Container(
          padding: EdgeInsets.symmetric(
            horizontal: compact ? 12 : 14,
            vertical: compact ? 8 : 10,
          ),
          decoration: BoxDecoration(
            color: bubble,
            borderRadius: BorderRadius.circular(radius),
            border: Border.all(color: border),
            boxShadow: [
              BoxShadow(
                color: accent.withValues(alpha: isDark ? 0.08 : 0.12),
                blurRadius: 16,
                offset: const Offset(0, 8),
                spreadRadius: -14,
              ),
            ],
          ),
          child: Text(
            text,
            style: context.profileTheme.typography.bodyCompact.copyWith(
              color: profile.colors.text,
              fontSize: compact ? 12.8 : 13.6,
              fontWeight: FontWeight.w600,
              height: compact ? 1.28 : 1.32,
            ),
          ),
        ),
        if (showTail)
          Positioned(
            left: compact ? 14 : 16,
            bottom: -4,
            child: Transform.rotate(
              angle: math.pi / 4,
              child: Container(
                width: compact ? 10 : 12,
                height: compact ? 10 : 12,
                decoration: BoxDecoration(
                  color: bubble,
                  borderRadius: BorderRadius.circular(3),
                  border: Border.all(color: border),
                ),
              ),
            ),
          ),
      ],
    );
  }
}

enum JoviaMoodStickerShape { orb, rounded, gem }

enum JoviaMoodStickerMood { smile, blink, wink }

class JoviaMoodSticker extends StatelessWidget {
  const JoviaMoodSticker({
    super.key,
    required this.primaryColor,
    required this.secondaryColor,
    this.size = 42,
    this.shape = JoviaMoodStickerShape.orb,
    this.mood = JoviaMoodStickerMood.smile,
    this.rotation = 0,
  });

  final Color primaryColor;
  final Color secondaryColor;
  final double size;
  final JoviaMoodStickerShape shape;
  final JoviaMoodStickerMood mood;
  final double rotation;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final faceColor = profile.colors.text.withValues(alpha: 0.86);
    final border = Color.alphaBlend(
      primaryColor.withValues(alpha: 0.14),
      profile.colors.strokeSoft,
    );

    Widget base = Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        shape: shape == JoviaMoodStickerShape.orb
            ? BoxShape.circle
            : BoxShape.rectangle,
        borderRadius: shape == JoviaMoodStickerShape.orb
            ? null
            : BorderRadius.circular(
                shape == JoviaMoodStickerShape.rounded
                    ? size * 0.3
                    : size * 0.2,
              ),
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            primaryColor.withValues(alpha: 0.92),
            secondaryColor.withValues(alpha: 0.92),
            Colors.white.withValues(alpha: 0.78),
          ],
        ),
        border: Border.all(color: border),
        boxShadow: [
          BoxShadow(
            color: primaryColor.withValues(alpha: 0.16),
            blurRadius: size * 0.34,
            offset: Offset(0, size * 0.14),
            spreadRadius: -size * 0.22,
          ),
        ],
      ),
    );

    if (shape == JoviaMoodStickerShape.gem) {
      base = Transform.rotate(angle: math.pi / 4, child: base);
    }

    return Transform.rotate(
      angle: rotation,
      child: SizedBox(
        width: size,
        height: size,
        child: Stack(
          alignment: Alignment.center,
          children: [
            base,
            if (shape == JoviaMoodStickerShape.gem)
              Transform.rotate(
                angle: -math.pi / 4,
                child: _JoviaMoodFace(size: size, mood: mood, color: faceColor),
              )
            else
              _JoviaMoodFace(size: size, mood: mood, color: faceColor),
          ],
        ),
      ),
    );
  }
}

class JoviaMoodStickerCluster extends StatelessWidget {
  const JoviaMoodStickerCluster({
    super.key,
    this.size = 28,
    this.colors = const <Color>[],
  });

  final double size;
  final List<Color> colors;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final palette = colors.isNotEmpty
        ? colors
        : <Color>[
            profile.colors.primary,
            profile.colors.warmAccent,
            profile.colors.lavender,
          ];
    return SizedBox(
      width: size * 2.3,
      height: size * 1.8,
      child: Stack(
        clipBehavior: Clip.none,
        children: [
          Positioned(
            left: 0,
            top: size * 0.42,
            child: JoviaMoodSticker(
              size: size * 1.1,
              primaryColor: palette[0 % palette.length],
              secondaryColor: Colors.white,
              shape: JoviaMoodStickerShape.orb,
              mood: JoviaMoodStickerMood.smile,
              rotation: -0.18,
            ),
          ),
          Positioned(
            left: size * 0.72,
            top: 0,
            child: JoviaMoodSticker(
              size: size,
              primaryColor: palette[1 % palette.length],
              secondaryColor: palette[0 % palette.length].withValues(
                alpha: 0.82,
              ),
              shape: JoviaMoodStickerShape.rounded,
              mood: JoviaMoodStickerMood.blink,
              rotation: 0.12,
            ),
          ),
          Positioned(
            right: 0,
            bottom: 0,
            child: JoviaMoodSticker(
              size: size * 0.88,
              primaryColor: palette[2 % palette.length],
              secondaryColor: palette[1 % palette.length].withValues(
                alpha: 0.8,
              ),
              shape: JoviaMoodStickerShape.gem,
              mood: JoviaMoodStickerMood.wink,
              rotation: -0.08,
            ),
          ),
        ],
      ),
    );
  }
}

class _JoviaMoodFace extends StatelessWidget {
  const _JoviaMoodFace({
    required this.size,
    required this.mood,
    required this.color,
  });

  final double size;
  final JoviaMoodStickerMood mood;
  final Color color;

  @override
  Widget build(BuildContext context) {
    final eyeSize = size * 0.085;
    return SizedBox(
      width: size,
      height: size,
      child: Stack(
        children: [
          Positioned(
            top: size * 0.38,
            left: size * 0.28,
            child: _JoviaEye(
              size: eyeSize,
              color: color,
              closed: mood == JoviaMoodStickerMood.blink,
            ),
          ),
          Positioned(
            top: size * 0.38,
            right: size * 0.28,
            child: _JoviaEye(
              size: eyeSize,
              color: color,
              closed: mood != JoviaMoodStickerMood.smile,
              winkTilt: mood == JoviaMoodStickerMood.wink,
            ),
          ),
          Positioned(
            left: size * 0.31,
            right: size * 0.31,
            bottom: size * 0.28,
            child: SizedBox(
              height: size * 0.16,
              child: CustomPaint(painter: _JoviaSmilePainter(color: color)),
            ),
          ),
        ],
      ),
    );
  }
}

class _JoviaEye extends StatelessWidget {
  const _JoviaEye({
    required this.size,
    required this.color,
    this.closed = false,
    this.winkTilt = false,
  });

  final double size;
  final Color color;
  final bool closed;
  final bool winkTilt;

  @override
  Widget build(BuildContext context) {
    if (!closed) {
      return Container(
        width: size,
        height: size,
        decoration: BoxDecoration(color: color, shape: BoxShape.circle),
      );
    }
    return Transform.rotate(
      angle: winkTilt ? -0.26 : 0,
      child: Container(
        width: size * 1.6,
        height: size * 0.36,
        decoration: BoxDecoration(
          color: color,
          borderRadius: BorderRadius.circular(size),
        ),
      ),
    );
  }
}

class _JoviaSmilePainter extends CustomPainter {
  const _JoviaSmilePainter({required this.color});

  final Color color;

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = math.max(1.2, size.height * 0.18)
      ..strokeCap = StrokeCap.round;
    final path = Path()
      ..moveTo(size.width * 0.1, size.height * 0.36)
      ..quadraticBezierTo(
        size.width * 0.5,
        size.height * 0.88,
        size.width * 0.9,
        size.height * 0.36,
      );
    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant _JoviaSmilePainter oldDelegate) {
    return oldDelegate.color != color;
  }
}
