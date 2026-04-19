import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

/// SHOU wordmark topbar — ortak marka şeridi.
///
/// Figma `TOPBAR` frame'i ile birebir: Night zemin, sol'da mono eyebrow
/// (ya da profil sayfasında `@username`), ortada SHOU orbit lockup,
/// sağda opsiyonel arama + menü ikonları.
///
/// Tab'lar bu widget'ı paylaşır; `label` parametresi bağlamı belirler:
///   - Home: 'BUGÜN' (mono uppercase, brand eyebrow)
///   - Profil: `@username`
///
/// `onBack` verilirse (ör. profil readOnly modu) sol'da geri oku açılır;
/// label geri oku'nun hemen sağında ellipsis'li text olarak gösterilir.
class ShouTopBar extends StatelessWidget {
  const ShouTopBar({
    super.key,
    required this.label,
    this.onBack,
    this.onSearch,
    this.onMenu,
  });

  /// Sol kolon etiketi. Home'da `BUGÜN`, profilde `@username`.
  final String label;

  /// Geri oku callback'i. Null ise ikon görünmez (home modu).
  final VoidCallback? onBack;

  /// Sağ kolon arama ikonu. Null ise ikon görünmez (ör. profil).
  final VoidCallback? onSearch;

  /// Sağ kolon menü ikonu. Null ise ikon görünmez.
  final VoidCallback? onMenu;

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 56,
      color: const Color(0xFF0E0D11),
      padding: const EdgeInsets.symmetric(horizontal: 20),
      child: Row(
        children: [
          Expanded(
            child: _ShouTopBarLeading(label: label, onBack: onBack),
          ),
          const _ShouWordmarkBeat(),
          Expanded(
            child: Align(
              alignment: Alignment.centerRight,
              child: _ShouTopBarActions(onSearch: onSearch, onMenu: onMenu),
            ),
          ),
        ],
      ),
    );
  }
}

class _ShouTopBarLeading extends StatelessWidget {
  const _ShouTopBarLeading({required this.label, this.onBack});

  final String label;
  final VoidCallback? onBack;

  @override
  Widget build(BuildContext context) {
    final text = Text(
      label,
      maxLines: 1,
      overflow: TextOverflow.ellipsis,
      style: GoogleFonts.jetBrainsMono(
        textStyle: const TextStyle(
          fontSize: 10.5,
          fontWeight: FontWeight.w400,
          color: Color(0xFF8A8A8A),
          letterSpacing: 2.4,
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
        ),
        const SizedBox(width: 4),
        Flexible(child: text),
      ],
    );
  }
}

class _ShouWordmarkBeat extends StatelessWidget {
  const _ShouWordmarkBeat();

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        const _ShouOrbitMark(size: 22),
        const SizedBox(width: 9),
        Text(
          'SHOU',
          style: GoogleFonts.fraunces(
            textStyle: const TextStyle(
              fontSize: 21,
              fontWeight: FontWeight.w400,
              color: Colors.white,
              letterSpacing: 2.8,
              height: 1,
            ),
          ),
        ),
      ],
    );
  }
}

/// Minik orbit lockup: dış halka, soluk iç halka, merkez gözlemci noktası
/// ve lime sinyal noktası + bağlantı çizgisi. Figma logo anatomisinden.
class _ShouOrbitMark extends StatelessWidget {
  const _ShouOrbitMark({this.size = 22});

  final double size;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: size,
      height: size,
      child: CustomPaint(painter: _ShouOrbitPainter()),
    );
  }
}

class _ShouOrbitPainter extends CustomPainter {
  static const Color _stroke = Colors.white;
  static const Color _lime = Color(0xFFCAFF4D);

  @override
  void paint(Canvas canvas, Size size) {
    final centre = Offset(size.width / 2, size.height / 2);
    final outerRadius = size.width * 0.42;
    final innerRadius = size.width * 0.22;

    final strokePaint = Paint()
      ..color = _stroke
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.2
      ..isAntiAlias = true;
    canvas.drawCircle(centre, outerRadius, strokePaint);

    final innerPaint = Paint()
      ..color = _stroke.withValues(alpha: 0.45)
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
      ..color = _stroke
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
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

class _ShouTopBarActions extends StatelessWidget {
  const _ShouTopBarActions({this.onSearch, this.onMenu});

  final VoidCallback? onSearch;
  final VoidCallback? onMenu;

  @override
  Widget build(BuildContext context) {
    final children = <Widget>[];
    if (onSearch != null) {
      children.add(
        _ShouTopBarIcon(
          icon: Icons.search,
          semanticsLabel: 'Ara',
          onTap: onSearch!,
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
  });

  final IconData icon;
  final VoidCallback onTap;
  final String semanticsLabel;

  @override
  Widget build(BuildContext context) {
    return IconButton(
      onPressed: onTap,
      splashRadius: 22,
      icon: Icon(icon, size: 20, color: const Color(0xFFE5E5E5)),
      tooltip: semanticsLabel,
      padding: const EdgeInsets.all(8),
      constraints: const BoxConstraints(minWidth: 36, minHeight: 36),
    );
  }
}
