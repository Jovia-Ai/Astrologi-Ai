import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';

import 'package:mobile/design/theme/profile_theme_extension.dart';

/// Second generation home page that implements the SHOU v2 Figma design.
///
/// Built in parallel to the legacy [HomePage] so we can ship it behind a
/// compile-time flag, hook section-by-section to real providers and swap the
/// two over once feature parity is reached. The legacy page keeps all its
/// backend wiring untouched while this file grows.
class HomePageV2 extends ConsumerStatefulWidget {
  const HomePageV2({super.key});

  @override
  ConsumerState<HomePageV2> createState() => _HomePageV2State();
}

class _HomePageV2State extends ConsumerState<HomePageV2> {
  @override
  Widget build(BuildContext context) {
    final theme = context.profileTheme;
    return Scaffold(
      backgroundColor: theme.colors.bg,
      body: SafeArea(
        bottom: false,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: const [
            _ShouTopbar(),
            Expanded(child: _HomeV2Placeholder()),
          ],
        ),
      ),
    );
  }
}

/// SHOU wordmark topbar — matches the Figma `TOPBAR` frame.
///
/// Dark Night ground with a mono `BUGÜN` eyebrow on the left, the SHOU
/// orbit-lockup centered, and search + menu affordances on the right.
/// Intentionally no scaffolding / elevation — the dark strip hugs the top
/// safe-area edge and hands off to the cream page body below.
class _ShouTopbar extends StatelessWidget {
  const _ShouTopbar();

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 56,
      color: const Color(0xFF0E0D11),
      padding: const EdgeInsets.symmetric(horizontal: 20),
      child: Row(
        children: [
          Expanded(
            child: Align(
              alignment: Alignment.centerLeft,
              child: Text(
                'BUGÜN',
                style: GoogleFonts.jetBrainsMono(
                  textStyle: const TextStyle(
                    fontSize: 10.5,
                    fontWeight: FontWeight.w400,
                    color: Color(0xFF8A8A8A),
                    letterSpacing: 2.4,
                  ),
                ),
              ),
            ),
          ),
          const _ShouWordmark(),
          const Expanded(
            child: Align(
              alignment: Alignment.centerRight,
              child: _TopbarActions(),
            ),
          ),
        ],
      ),
    );
  }
}

class _ShouWordmark extends StatelessWidget {
  const _ShouWordmark();

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

/// Miniature orbit-lockup: outer circle, faint inner circle, centre dot and
/// signal-lime top dot with its connecting line. Pulled straight from the
/// Figma logo anatomy so the topbar carries the full brand beat.
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

    // Outer orbit.
    canvas.drawCircle(centre, outerRadius, strokePaint);

    // Faint inner orbit.
    final innerPaint = Paint()
      ..color = _stroke.withValues(alpha: 0.45)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1
      ..isAntiAlias = true;
    canvas.drawCircle(centre, innerRadius, innerPaint);

    // Connector from top dot to centre orbit edge.
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

    // Centre observer dot.
    canvas.drawCircle(centre, size.width * 0.08, dotPaint);

    // Top signal dot.
    canvas.drawCircle(topDotCentre, size.width * 0.095, dotPaint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

class _TopbarActions extends StatelessWidget {
  const _TopbarActions();

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        _TopbarIconButton(
          icon: Icons.search,
          semanticsLabel: 'Ara',
          onTap: () {},
        ),
        const SizedBox(width: 2),
        _TopbarIconButton(
          icon: Icons.menu,
          semanticsLabel: 'Menü',
          onTap: () {},
        ),
      ],
    );
  }
}

class _TopbarIconButton extends StatelessWidget {
  const _TopbarIconButton({
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

/// Temporary body shown while the v2 home is still under construction. Lets
/// us wire the route + topbar first and confirm the framing looks right
/// before filling in the story circles / transit / feed sections.
class _HomeV2Placeholder extends StatelessWidget {
  const _HomeV2Placeholder();

  @override
  Widget build(BuildContext context) {
    final theme = context.profileTheme;
    return Center(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              'home v2',
              style: GoogleFonts.jetBrainsMono(
                textStyle: TextStyle(
                  fontSize: 10.5,
                  letterSpacing: 2.2,
                  color: theme.colors.textLight,
                ),
              ),
            ),
            const SizedBox(height: 12),
            Text(
              'Gökyüzü seni bekliyor.',
              textAlign: TextAlign.center,
              style: GoogleFonts.fraunces(
                textStyle: TextStyle(
                  fontSize: 30,
                  height: 1.15,
                  fontWeight: FontWeight.w300,
                  fontStyle: FontStyle.italic,
                  letterSpacing: -0.6,
                  color: theme.colors.text,
                ),
              ),
            ),
            const SizedBox(height: 14),
            Text(
              'Story circles, günlük transit, gökyüzü açıları ve '
              'arkadaşlardan bölümleri sırayla bu ekrana yerleşecek. '
              'Mevcut daily / dönem transit verisi değişmeden yeni '
              'tasarıma bağlanacak.',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 13,
                height: 1.55,
                color: theme.colors.muted,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
