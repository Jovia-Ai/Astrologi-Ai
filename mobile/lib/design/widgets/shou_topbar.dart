import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

enum ShouTopBarVariant { dark, light }

/// SHOU wordmark topbar — ortak marka şeridi.
class ShouTopBar extends StatelessWidget {
  const ShouTopBar({
    super.key,
    required this.label,
    this.onBack,
    this.onSearch,
    this.onMenu,
    this.variant = ShouTopBarVariant.dark,
  });

  final String label;
  final VoidCallback? onBack;
  final VoidCallback? onSearch;
  final VoidCallback? onMenu;
  final ShouTopBarVariant variant;

  @override
  Widget build(BuildContext context) {
    final isLight = variant == ShouTopBarVariant.light;
    final bg = isLight ? const Color(0xFFFAFAF7) : const Color(0xFF0E0D11);
    final eyebrowColor = isLight
        ? const Color(0xFF777777)
        : const Color(0xFF8A8A8A);
    final wordmarkColor = isLight ? const Color(0xFF111111) : Colors.white;
    final iconColor = isLight
        ? const Color(0xFF111111)
        : const Color(0xFFE5E5E5);
    final orbitStroke = isLight ? const Color(0xFF111111) : Colors.white;
    final border = isLight
        ? const Border(
            bottom: BorderSide(color: Color(0x14000000), width: 0.5),
          )
        : null;

    return Container(
      height: 56,
      decoration: BoxDecoration(color: bg, border: border),
      padding: const EdgeInsets.symmetric(horizontal: 20),
      child: Row(
        children: [
          Expanded(
            child: _ShouTopBarLeading(
              label: label,
              onBack: onBack,
              textColor: eyebrowColor,
              iconColor: iconColor,
            ),
          ),
          _ShouWordmarkBeat(
            wordmarkColor: wordmarkColor,
            orbitStroke: orbitStroke,
            isLight: isLight,
          ),
          Expanded(
            child: Align(
              alignment: Alignment.centerRight,
              child: _ShouTopBarActions(
                onSearch: onSearch,
                onMenu: onMenu,
                iconColor: iconColor,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _ShouTopBarLeading extends StatelessWidget {
  const _ShouTopBarLeading({
    required this.label,
    required this.textColor,
    required this.iconColor,
    this.onBack,
  });

  final String label;
  final Color textColor;
  final Color iconColor;
  final VoidCallback? onBack;

  @override
  Widget build(BuildContext context) {
    // Eyebrow ('BUGÜN' gibi kısa uppercase) → geniş letter-spacing.
    // Username ('@sahra' gibi lowercase/handle) → daraltılmış spacing.
    final isEyebrow = label == label.toUpperCase() && label.length <= 10;
    final text = Text(
      label,
      maxLines: 1,
      overflow: TextOverflow.ellipsis,
      style: GoogleFonts.jetBrainsMono(
        textStyle: TextStyle(
          fontSize: isEyebrow ? 10.5 : 11,
          fontWeight: FontWeight.w400,
          color: textColor,
          letterSpacing: isEyebrow ? 2.4 : 0.2,
        ),
      ),
    );

    if (onBack == null) {
      return Align(alignment: Alignment.centerLeft, child: text);
    }

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        _ShouTopBarIcon(
          icon: Icons.arrow_back_ios_new_rounded,
          semanticsLabel: 'Geri',
          onTap: onBack!,
          color: iconColor,
        ),
        const SizedBox(width: 4),
        Flexible(child: text),
      ],
    );
  }
}

class _ShouWordmarkBeat extends StatelessWidget {
  const _ShouWordmarkBeat({
    required this.wordmarkColor,
    required this.orbitStroke,
    required this.isLight,
  });

  final Color wordmarkColor;
  final Color orbitStroke;
  final bool isLight;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        _ShouOrbitMark(size: isLight ? 20 : 22, stroke: orbitStroke),
        SizedBox(width: isLight ? 7 : 9),
        Text(
          'SHOU',
          style: GoogleFonts.fraunces(
            textStyle: TextStyle(
              fontSize: isLight ? 18 : 21,
              fontWeight: isLight ? FontWeight.w300 : FontWeight.w400,
              color: wordmarkColor,
              letterSpacing: isLight ? 1.0 : 2.8,
              height: 1,
            ),
          ),
        ),
      ],
    );
  }
}

class _ShouOrbitMark extends StatelessWidget {
  const _ShouOrbitMark({this.size = 22, required this.stroke});

  final double size;
  final Color stroke;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: size,
      height: size,
      child: CustomPaint(painter: _ShouOrbitPainter(stroke: stroke)),
    );
  }
}

class _ShouOrbitPainter extends CustomPainter {
  _ShouOrbitPainter({required this.stroke});

  final Color stroke;
  static const Color _lime = Color(0xFFCAFF4D);

  @override
  void paint(Canvas canvas, Size size) {
    final centre = Offset(size.width / 2, size.height / 2);
    final outerRadius = size.width * 0.42;
    final innerRadius = size.width * 0.22;

    final strokePaint = Paint()
      ..color = stroke
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.2
      ..isAntiAlias = true;
    canvas.drawCircle(centre, outerRadius, strokePaint);

    final innerPaint = Paint()
      ..color = stroke.withValues(alpha: 0.45)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1
      ..isAntiAlias = true;
    canvas.drawCircle(centre, innerRadius, innerPaint);

    final topDotCentre = Offset(size.width / 2, size.height * 0.08);
    final lineStart = Offset(
      topDotCentre.dx,
      topDotCentre.dy + size.width * 0.045,
    );
    final lineEnd = Offset(centre.dx, centre.dy - outerRadius);
    final linePaint = Paint()
      ..color = stroke
      ..strokeWidth = 1
      ..strokeCap = StrokeCap.round
      ..isAntiAlias = true;
    canvas.drawLine(lineStart, lineEnd, linePaint);

    final dotPaint = Paint()
      ..color = _lime
      ..isAntiAlias = true;
    canvas.drawCircle(centre, size.width * 0.08, dotPaint);
    canvas.drawCircle(topDotCentre, size.width * 0.095, dotPaint);
  }

  @override
  bool shouldRepaint(covariant _ShouOrbitPainter oldDelegate) =>
      oldDelegate.stroke != stroke;
}

class _ShouTopBarActions extends StatelessWidget {
  const _ShouTopBarActions({
    required this.iconColor,
    this.onSearch,
    this.onMenu,
  });

  final VoidCallback? onSearch;
  final VoidCallback? onMenu;
  final Color iconColor;

  @override
  Widget build(BuildContext context) {
    final children = <Widget>[];
    if (onSearch != null) {
      children.add(
        _ShouTopBarIcon(
          icon: Icons.search,
          semanticsLabel: 'Ara',
          onTap: onSearch!,
          color: iconColor,
        ),
      );
    }
    if (onMenu != null) {
      if (children.isNotEmpty) {
        children.add(const SizedBox(width: 2));
      }
      children.add(
        _ShouTopBarIcon(
          icon: Icons.menu,
          semanticsLabel: 'Menü',
          onTap: onMenu!,
          color: iconColor,
        ),
      );
    }
    if (children.isEmpty) {
      return const SizedBox.shrink();
    }
    return Row(mainAxisSize: MainAxisSize.min, children: children);
  }
}

class _ShouTopBarIcon extends StatelessWidget {
  const _ShouTopBarIcon({
    required this.icon,
    required this.onTap,
    required this.semanticsLabel,
    required this.color,
  });

  final IconData icon;
  final VoidCallback onTap;
  final String semanticsLabel;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return IconButton(
      onPressed: onTap,
      splashRadius: 22,
      icon: Icon(icon, size: 20, color: color),
      tooltip: semanticsLabel,
      padding: const EdgeInsets.all(8),
      constraints: const BoxConstraints(minWidth: 36, minHeight: 36),
    );
  }
}
