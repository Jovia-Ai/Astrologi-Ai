import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';

class HaritamView extends StatefulWidget {
  const HaritamView({super.key, this.profile, this.payload});

  final Map<String, dynamic>? profile;
  final Map<String, dynamic>? payload;

  @override
  State<HaritamView> createState() => _HaritamViewState();
}

class _HaritamViewState extends State<HaritamView> {
  @override
  Widget build(BuildContext context) {
    final data = _HaritamMockData.fromInputs(
      profile: widget.profile,
      payload: widget.payload,
    );
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Container(
        clipBehavior: Clip.antiAlias,
        decoration: BoxDecoration(
          color: _HaritamColors.paperPure,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: _HaritamColors.hairline),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            _WheelSection(data: data),
            _DistributionBlock(data: data),
            _PlacementsTable(data: data),
            _AspectsTable(data: data),
            _HousesDarkTable(data: data),
            _MetaBlock(data: data),
          ],
        ),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════
// Palette + typography constants — mirrors :root vars from v6 HTML
// ═══════════════════════════════════════════════════════════════════

class _HaritamColors {
  static const ink = Color(0xFF0E0E10);
  static const fog = Color(0xFF444444);
  static const mist = Color(0xFF888888);
  static const silver = Color(0xFFB0B0B0);
  static const hairline = Color(0x1A000000);
  static const hairlineRow = Color(0x12000000);
  static const paper = Color(0xFFFAFAF7);
  static const paperPure = Color(0xFFFFFFFF);
  static const lime = Color(0xFFCAFF4D);
  static const limeText = Color(0xFF1A3300);
  static const limeDeep = Color(0xFF5A8E10);
  static const limeBg = Color(0xFFF5FCDE);
  static const lav = Color(0xFF7F77DD);
  static const lavDeep = Color(0xFF534AB7);
  static const lavSoft = Color(0xFFB5AFE0);
  static const lavBg = Color(0xFFF4F2FA);
  static const blush = Color(0xFFF9A8D4);
  static const blushDeep = Color(0xFFC76FA0);
  static const peach = Color(0xFFF4A261);
  static const peachDeep = Color(0xFFC97A2E);
}

class _HaritamFonts {
  static const display = 'Fraunces';
  static const body = 'Inter';
  static const mono = 'Space Mono';
  static const dot = 'VT323';
}

// ═══════════════════════════════════════════════════════════════════
// Mock data
// ═══════════════════════════════════════════════════════════════════

enum _PlanetKey { sun, moon, mercury, venus, mars, jupiter, saturn, uranus, neptune, pluto, nnode, lilith, chiron, fortune, asc }

enum _AspectKind { conjunction, trine, square, sextile, opposition }

class _Placement {
  const _Placement({
    required this.planet,
    required this.sign,
    required this.degreeText,
    required this.house,
    required this.longitude,
    this.retrograde = false,
    this.stellium = false,
  });

  final _PlanetKey planet;
  final String sign;
  final String degreeText;
  final int house;
  final double longitude;
  final bool retrograde;
  final bool stellium;
}

class _AspectRow {
  const _AspectRow({
    required this.left,
    required this.right,
    required this.kind,
    required this.label,
    required this.orbText,
    this.tight = false,
  });

  final _PlanetKey left;
  final _PlanetKey right;
  final _AspectKind kind;
  final String label;
  final String orbText;
  final bool tight;
}

class _HouseRow {
  const _HouseRow({
    required this.number,
    required this.signCode,
    required this.occupants,
    this.stellium = false,
  });

  final int number;
  final String signCode;
  final List<_PlanetKey> occupants;
  final bool stellium;
}

class _DistEntry {
  const _DistEntry({required this.label, required this.count, this.dominant = false, this.lav = false});

  final String label;
  final int count;
  final bool dominant;
  final bool lav;
}

class _HaritamMockData {
  const _HaritamMockData({
    required this.title,
    required this.fileEye,
    required this.dateLabel,
    required this.locationLabel,
    required this.timeZoneLabel,
    required this.coordinates,
    required this.systemLabel,
    required this.ascSign,
    required this.placements,
    required this.aspects,
    required this.houses,
    required this.elements,
    required this.modalities,
    required this.totalObjects,
    required this.extraPoints,
    required this.extraSextiles,
  });

  final String title;
  final String fileEye;
  final String dateLabel;
  final String locationLabel;
  final String timeZoneLabel;
  final String coordinates;
  final String systemLabel;
  final String ascSign;
  final List<_Placement> placements;
  final List<_AspectRow> aspects;
  final List<_HouseRow> houses;
  final List<_DistEntry> elements;
  final List<_DistEntry> modalities;
  final int totalObjects;
  final int extraPoints;
  final int extraSextiles;

  factory _HaritamMockData.fromInputs({
    Map<String, dynamic>? profile,
    Map<String, dynamic>? payload,
  }) {
    return const _HaritamMockData(
      title: 'Haritam',
      fileEye: 'FILE · NATAL · S01',
      dateLabel: '28.12.96 · 11:42',
      locationLabel: 'İSTANBUL',
      timeZoneLabel: '11:42 GMT+3',
      coordinates: '41.01°N · 28.97°E',
      systemLabel: 'Placidus · Tropikal',
      ascSign: 'CAP',
      totalObjects: 14,
      extraPoints: 4,
      extraSextiles: 3,
      elements: [
        _DistEntry(label: 'Toprak 6', count: 6, dominant: true),
        _DistEntry(label: 'Hava 2', count: 2),
        _DistEntry(label: 'Ateş 1', count: 1),
        _DistEntry(label: 'Su 1', count: 1),
      ],
      modalities: [
        _DistEntry(label: 'Öncü 6', count: 6, dominant: true, lav: true),
        _DistEntry(label: 'Sabit 2', count: 2),
        _DistEntry(label: 'Değ. 2', count: 2),
      ],
      placements: [
        _Placement(planet: _PlanetKey.sun, sign: 'Oğlak', degreeText: "6°45'", house: 1, longitude: 276.75, stellium: true),
        _Placement(planet: _PlanetKey.mercury, sign: 'Oğlak', degreeText: "17°21'", house: 1, longitude: 287.35, stellium: true, retrograde: true),
        _Placement(planet: _PlanetKey.jupiter, sign: 'Oğlak', degreeText: "24°17'", house: 1, longitude: 294.28, stellium: true),
        _Placement(planet: _PlanetKey.uranus, sign: 'Kova', degreeText: "3°03'", house: 1, longitude: 303.05, stellium: true),
        _Placement(planet: _PlanetKey.neptune, sign: 'Oğlak', degreeText: "26°41'", house: 1, longitude: 296.68, stellium: true),
        _Placement(planet: _PlanetKey.saturn, sign: 'Koç', degreeText: "1°09'", house: 3, longitude: 1.15),
        _Placement(planet: _PlanetKey.moon, sign: 'Aslan', degreeText: "13°56'", house: 8, longitude: 133.93),
        _Placement(planet: _PlanetKey.venus, sign: 'Yay', degreeText: "13°42'", house: 12, longitude: 253.70),
        _Placement(planet: _PlanetKey.mars, sign: 'Başak', degreeText: "27°55'", house: 9, longitude: 177.92),
        _Placement(planet: _PlanetKey.pluto, sign: 'Yay', degreeText: "4°15'", house: 11, longitude: 244.25),
      ],
      aspects: [
        _AspectRow(left: _PlanetKey.asc, right: _PlanetKey.saturn, kind: _AspectKind.square, label: 'Kare', orbText: "0°00'", tight: true),
        _AspectRow(left: _PlanetKey.moon, right: _PlanetKey.venus, kind: _AspectKind.trine, label: 'Trine', orbText: "0°14'", tight: true),
        _AspectRow(left: _PlanetKey.sun, right: _PlanetKey.mercury, kind: _AspectKind.conjunction, label: 'Konj.', orbText: "0°45'"),
        _AspectRow(left: _PlanetKey.mars, right: _PlanetKey.neptune, kind: _AspectKind.trine, label: 'Trine', orbText: "1°14'"),
        _AspectRow(left: _PlanetKey.saturn, right: _PlanetKey.pluto, kind: _AspectKind.trine, label: 'Trine', orbText: "3°05'"),
        _AspectRow(left: _PlanetKey.sun, right: _PlanetKey.mars, kind: _AspectKind.trine, label: 'Trine', orbText: "2°50'"),
      ],
      houses: [
        _HouseRow(number: 1, signCode: 'CAP', occupants: [_PlanetKey.sun, _PlanetKey.mercury, _PlanetKey.jupiter, _PlanetKey.uranus, _PlanetKey.neptune], stellium: true),
        _HouseRow(number: 2, signCode: 'AQU', occupants: []),
        _HouseRow(number: 3, signCode: 'ARI', occupants: [_PlanetKey.saturn]),
        _HouseRow(number: 4, signCode: 'TAU', occupants: []),
        _HouseRow(number: 5, signCode: 'GEM', occupants: []),
        _HouseRow(number: 6, signCode: 'CAN', occupants: []),
        _HouseRow(number: 7, signCode: 'LEO', occupants: []),
        _HouseRow(number: 8, signCode: 'LEO', occupants: [_PlanetKey.moon, _PlanetKey.lilith]),
        _HouseRow(number: 9, signCode: 'VIR', occupants: [_PlanetKey.mars, _PlanetKey.nnode]),
        _HouseRow(number: 10, signCode: 'LIB', occupants: [_PlanetKey.chiron]),
        _HouseRow(number: 11, signCode: 'SCO', occupants: [_PlanetKey.pluto]),
        _HouseRow(number: 12, signCode: 'SAG', occupants: [_PlanetKey.venus]),
      ],
    );
  }
}

// ═══════════════════════════════════════════════════════════════════
// Section 1 — Wheel (CustomPaint) + meta + caption
// ═══════════════════════════════════════════════════════════════════

class _WheelSection extends StatelessWidget {
  const _WheelSection({required this.data});

  final _HaritamMockData data;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(20, 20, 20, 18),
      decoration: const BoxDecoration(
        color: _HaritamColors.paperPure,
        border: Border(bottom: BorderSide(color: _HaritamColors.hairline)),
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text.rich(
                TextSpan(
                  style: const TextStyle(
                    fontFamily: _HaritamFonts.mono,
                    fontSize: 8.5,
                    letterSpacing: 0.3,
                    color: _HaritamColors.mist,
                  ),
                  children: [
                    const TextSpan(
                      text: 'NATAL',
                      style: TextStyle(
                        color: _HaritamColors.ink,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    TextSpan(text: ' · ${data.timeZoneLabel}'),
                  ],
                ),
              ),
              Row(
                children: const [
                  _PulseDot(),
                  SizedBox(width: 5),
                  Text(
                    'HAZIR',
                    style: TextStyle(
                      fontFamily: _HaritamFonts.dot,
                      fontSize: 11,
                      color: _HaritamColors.limeDeep,
                      letterSpacing: 1,
                    ),
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 14),
          AspectRatio(
            aspectRatio: 1,
            child: LayoutBuilder(
              builder: (context, constraints) {
                final size = math.min(constraints.maxWidth, 280.0);
                return Center(
                  child: SizedBox(
                    width: size,
                    height: size,
                    child: CustomPaint(
                      painter: _HaritamWheelPainter(
                        placements: data.placements,
                        ascLongitude: 270, // Capricorn 0°
                        ascSign: data.ascSign,
                      ),
                    ),
                  ),
                );
              },
            ),
          ),
          const SizedBox(height: 8),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              _CaptionDot(color: _HaritamColors.lime, label: 'ASC'),
              const SizedBox(width: 14),
              _CaptionDot(color: _HaritamColors.blush, label: 'MC'),
              const SizedBox(width: 14),
              Text(
                '· ${data.totalObjects} obj · 12 ev',
                style: const TextStyle(
                  fontFamily: _HaritamFonts.mono,
                  fontSize: 8.5,
                  color: _HaritamColors.mist,
                  letterSpacing: 0.3,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _PulseDot extends StatefulWidget {
  const _PulseDot();
  @override
  State<_PulseDot> createState() => _PulseDotState();
}

class _PulseDotState extends State<_PulseDot> with SingleTickerProviderStateMixin {
  late final AnimationController _ctrl;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1600),
    )..repeat(reverse: true);
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _ctrl,
      builder: (context, _) {
        final t = _ctrl.value;
        final scale = 1.0 - 0.15 * t;
        final opacity = 1.0 - 0.6 * t;
        return Opacity(
          opacity: opacity,
          child: Transform.scale(
            scale: scale,
            child: Container(
              width: 5,
              height: 5,
              decoration: const BoxDecoration(
                color: _HaritamColors.limeDeep,
                shape: BoxShape.circle,
              ),
            ),
          ),
        );
      },
    );
  }
}

class _CaptionDot extends StatelessWidget {
  const _CaptionDot({required this.color, required this.label});
  final Color color;
  final String label;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Container(
          width: 6,
          height: 6,
          decoration: BoxDecoration(color: color, shape: BoxShape.circle),
        ),
        const SizedBox(width: 4),
        Text(
          label,
          style: const TextStyle(
            fontFamily: _HaritamFonts.mono,
            fontSize: 8.5,
            color: _HaritamColors.mist,
            letterSpacing: 0.3,
          ),
        ),
      ],
    );
  }
}

class _HaritamWheelPainter extends CustomPainter {
  _HaritamWheelPainter({
    required this.placements,
    required this.ascLongitude,
    required this.ascSign,
  });

  final List<_Placement> placements;
  final double ascLongitude;
  final String ascSign;

  static const _signCodes = [
    'CAP', 'AQU', 'PIS', 'ARI', 'TAU', 'GEM',
    'CAN', 'LEO', 'VIR', 'LIB', 'SCO', 'SAG',
  ];

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final outer = math.min(size.width, size.height) / 2 - 4;
    final mid = outer * (148 / 170);
    final inner = outer * (100 / 170);

    final inkStroke = Paint()
      ..style = PaintingStyle.stroke
      ..color = _HaritamColors.ink
      ..strokeWidth = 0.8;
    canvas.drawCircle(center, outer, inkStroke);

    final midStroke = Paint()
      ..style = PaintingStyle.stroke
      ..color = _HaritamColors.ink.withValues(alpha:0.7)
      ..strokeWidth = 0.5;
    canvas.drawCircle(center, mid, midStroke);

    // 12 zodiac segment ticks (between outer and mid ring)
    final tickStroke = Paint()
      ..style = PaintingStyle.stroke
      ..color = _HaritamColors.ink.withValues(alpha:0.5)
      ..strokeWidth = 0.4;
    for (var i = 0; i < 12; i++) {
      final lon = i * 30.0;
      final ang = _angleFor(lon);
      final p1 = _pointAt(center, outer, ang);
      final p2 = _pointAt(center, mid, ang);
      canvas.drawLine(p1, p2, tickStroke);
    }

    // Sign labels (mono, 7px) at middle of each segment
    for (var i = 0; i < 12; i++) {
      final code = _signCodes[i];
      // signCodes[0] = CAP corresponds to ecliptic longitude 270.
      final ecliptic = (270.0 + i * 30.0 + 15.0) % 360.0;
      final ang = _angleFor(ecliptic);
      final pos = _pointAt(center, (outer + mid) / 2, ang);
      _drawText(
        canvas,
        code,
        pos,
        const TextStyle(
          fontFamily: _HaritamFonts.mono,
          fontSize: 9,
          color: Color(0xFFAAAAAA),
          letterSpacing: 0.4,
        ),
        center: true,
      );
    }

    // Inner ring for houses (light)
    final innerStroke = Paint()
      ..style = PaintingStyle.stroke
      ..color = _HaritamColors.ink.withValues(alpha:0.2)
      ..strokeWidth = 0.4;
    canvas.drawCircle(center, inner, innerStroke);

    // House numbers — equal-house mock starting from ASC
    for (var i = 0; i < 12; i++) {
      final houseMid = (ascLongitude + i * 30.0 + 15.0) % 360.0;
      final ang = _angleFor(houseMid);
      final pos = _pointAt(center, (mid + inner) / 2, ang);
      _drawText(
        canvas,
        '${i + 1}',
        pos,
        const TextStyle(
          fontFamily: _HaritamFonts.display,
          fontStyle: FontStyle.italic,
          fontSize: 11,
          color: Color(0xFF777777),
          fontWeight: FontWeight.w400,
        ),
        center: true,
      );
    }

    // Decorative aspect lines (a few sample)
    final softGreen = Paint()
      ..style = PaintingStyle.stroke
      ..color = _HaritamColors.limeDeep.withValues(alpha:0.5)
      ..strokeWidth = 0.5;
    final softLav = Paint()
      ..style = PaintingStyle.stroke
      ..color = _HaritamColors.lav.withValues(alpha:0.5)
      ..strokeWidth = 0.5;
    final softPeach = Paint()
      ..style = PaintingStyle.stroke
      ..color = _HaritamColors.peachDeep.withValues(alpha:0.4)
      ..strokeWidth = 0.5;

    final moon = _findPlanet(_PlanetKey.moon);
    final venus = _findPlanet(_PlanetKey.venus);
    final saturn = _findPlanet(_PlanetKey.saturn);
    final mars = _findPlanet(_PlanetKey.mars);
    final neptune = _findPlanet(_PlanetKey.neptune);

    if (moon != null && venus != null) {
      final r = inner - 10;
      canvas.drawLine(
        _pointAt(center, r, _angleFor(moon.longitude)),
        _pointAt(center, r, _angleFor(venus.longitude)),
        softGreen,
      );
    }
    if (saturn != null && neptune != null) {
      final r = inner - 14;
      canvas.drawLine(
        _pointAt(center, r, _angleFor(saturn.longitude)),
        _pointAt(center, r, _angleFor(neptune.longitude)),
        softLav,
      );
    }
    if (mars != null && venus != null) {
      final r = inner - 6;
      canvas.drawLine(
        _pointAt(center, r, _angleFor(mars.longitude)),
        _pointAt(center, r, _angleFor(venus.longitude)),
        softPeach,
      );
    }

    // Center disc with ASC label
    final centerR = outer * (26 / 170);
    final centerFill = Paint()..color = _HaritamColors.paper;
    canvas.drawCircle(center, centerR, centerFill);
    canvas.drawCircle(
      center,
      centerR,
      Paint()
        ..style = PaintingStyle.stroke
        ..color = _HaritamColors.ink
        ..strokeWidth = 0.5,
    );
    _drawText(
      canvas,
      'ASC',
      Offset(center.dx, center.dy - centerR * 0.25),
      const TextStyle(
        fontFamily: _HaritamFonts.body,
        fontSize: 7,
        letterSpacing: 1,
        color: Color(0xFF777777),
        fontWeight: FontWeight.w500,
      ),
      center: true,
    );
    _drawText(
      canvas,
      ascSign,
      Offset(center.dx, center.dy + centerR * 0.3),
      const TextStyle(
        fontFamily: _HaritamFonts.mono,
        fontSize: 8,
        color: _HaritamColors.ink,
        letterSpacing: 0.5,
        fontWeight: FontWeight.w500,
      ),
      center: true,
    );

    // ASC marker (lime triangle) at left
    final ascAng = _angleFor(ascLongitude);
    final ascTip = _pointAt(center, outer - 0, ascAng);
    final ascBack = _pointAt(center, outer + 8, ascAng);
    _drawArrow(canvas, ascTip, ascBack, _HaritamColors.lime);
    // MC marker (blush) at top — MC ≈ ASC + 90 (roughly)
    final mcAng = _angleFor((ascLongitude + 90) % 360);
    final mcTip = _pointAt(center, outer - 0, mcAng);
    final mcBack = _pointAt(center, outer + 8, mcAng);
    _drawArrow(canvas, mcTip, mcBack, _HaritamColors.blush);

    // Planets — colored disc + 2-letter monogram
    final planetRadius = (mid + inner) / 2 + 6;
    for (final p in placements) {
      _drawPlanetDisc(canvas, center, planetRadius, p);
    }
  }

  _Placement? _findPlanet(_PlanetKey k) {
    for (final p in placements) {
      if (p.planet == k) return p;
    }
    return null;
  }

  double _angleFor(double longitude) {
    // ASC at screen-left (180° = π). Signs go counterclockwise as longitude grows.
    final relative = (longitude - ascLongitude) % 360;
    final degrees = 180.0 - relative;
    return degrees * math.pi / 180;
  }

  Offset _pointAt(Offset center, double radius, double angleRad) {
    return Offset(
      center.dx + radius * math.cos(angleRad),
      center.dy - radius * math.sin(angleRad),
    );
  }

  void _drawText(
    Canvas canvas,
    String text,
    Offset pos,
    TextStyle style, {
    bool center = false,
  }) {
    final tp = TextPainter(
      text: TextSpan(text: text, style: style),
      textDirection: TextDirection.ltr,
    )..layout();
    final offset = center
        ? Offset(pos.dx - tp.width / 2, pos.dy - tp.height / 2)
        : pos;
    tp.paint(canvas, offset);
  }

  void _drawArrow(Canvas canvas, Offset tip, Offset back, Color color) {
    final paint = Paint()..color = color;
    final perp = Offset(-(tip.dy - back.dy), tip.dx - back.dx);
    final length = math.sqrt(perp.dx * perp.dx + perp.dy * perp.dy);
    final unit = length == 0 ? Offset.zero : perp / length;
    final w = 4.0;
    final p1 = back + unit * w;
    final p2 = back - unit * w;
    final path = Path()
      ..moveTo(tip.dx, tip.dy)
      ..lineTo(p1.dx, p1.dy)
      ..lineTo(p2.dx, p2.dy)
      ..close();
    canvas.drawPath(path, paint);
  }

  void _drawPlanetDisc(Canvas canvas, Offset center, double r, _Placement p) {
    final ang = _angleFor(p.longitude);
    final pos = _pointAt(center, r, ang);
    final color = _planetDiscColor(p.planet);
    final glyphColor = _planetGlyphColor(p.planet);
    final radius = 9.0;
    canvas.drawCircle(pos, radius, Paint()..color = color);
    canvas.drawCircle(
      pos,
      radius,
      Paint()
        ..style = PaintingStyle.stroke
        ..color = _HaritamColors.ink
        ..strokeWidth = 0.6,
    );
    _drawText(
      canvas,
      _planetCode(p.planet),
      pos,
      TextStyle(
        fontFamily: _HaritamFonts.mono,
        fontSize: 7.5,
        color: glyphColor,
        fontWeight: FontWeight.w700,
        letterSpacing: 0,
      ),
      center: true,
    );
  }

  Color _planetDiscColor(_PlanetKey k) {
    switch (k) {
      case _PlanetKey.sun:
        return _HaritamColors.lime;
      case _PlanetKey.moon:
        return _HaritamColors.blush;
      case _PlanetKey.venus:
        return const Color(0xFFFDE4F2);
      case _PlanetKey.mars:
        return const Color(0xFFFDECD8);
      case _PlanetKey.jupiter:
        return _HaritamColors.peach;
      case _PlanetKey.saturn:
        return _HaritamColors.lav;
      case _PlanetKey.uranus:
        return _HaritamColors.paperPure;
      case _PlanetKey.neptune:
        return _HaritamColors.lav;
      case _PlanetKey.pluto:
        return _HaritamColors.ink;
      case _PlanetKey.mercury:
        return _HaritamColors.paperPure;
      case _PlanetKey.nnode:
        return _HaritamColors.paperPure;
      default:
        return _HaritamColors.paperPure;
    }
  }

  Color _planetGlyphColor(_PlanetKey k) {
    switch (k) {
      case _PlanetKey.sun:
        return _HaritamColors.ink;
      case _PlanetKey.moon:
        return _HaritamColors.ink;
      case _PlanetKey.venus:
        return _HaritamColors.blushDeep;
      case _PlanetKey.mars:
        return _HaritamColors.peachDeep;
      case _PlanetKey.jupiter:
        return _HaritamColors.paperPure;
      case _PlanetKey.saturn:
        return _HaritamColors.paperPure;
      case _PlanetKey.uranus:
        return _HaritamColors.ink;
      case _PlanetKey.neptune:
        return _HaritamColors.paperPure;
      case _PlanetKey.pluto:
        return _HaritamColors.lime;
      case _PlanetKey.mercury:
        return _HaritamColors.ink;
      case _PlanetKey.nnode:
        return _HaritamColors.ink;
      default:
        return _HaritamColors.ink;
    }
  }

  static String _planetCode(_PlanetKey k) {
    switch (k) {
      case _PlanetKey.sun:
        return 'SU';
      case _PlanetKey.moon:
        return 'MO';
      case _PlanetKey.mercury:
        return 'ME';
      case _PlanetKey.venus:
        return 'VE';
      case _PlanetKey.mars:
        return 'MA';
      case _PlanetKey.jupiter:
        return 'JU';
      case _PlanetKey.saturn:
        return 'SA';
      case _PlanetKey.uranus:
        return 'UR';
      case _PlanetKey.neptune:
        return 'NE';
      case _PlanetKey.pluto:
        return 'PL';
      case _PlanetKey.nnode:
        return 'NN';
      case _PlanetKey.lilith:
        return 'LI';
      case _PlanetKey.chiron:
        return 'CH';
      case _PlanetKey.fortune:
        return 'FO';
      case _PlanetKey.asc:
        return 'AS';
    }
  }

  @override
  bool shouldRepaint(covariant _HaritamWheelPainter oldDelegate) {
    return oldDelegate.placements != placements ||
        oldDelegate.ascLongitude != ascLongitude;
  }
}

// ═══════════════════════════════════════════════════════════════════
// Section 3 — Distribution block (element + modalite pills)
// ═══════════════════════════════════════════════════════════════════

class _DistributionBlock extends StatelessWidget {
  const _DistributionBlock({required this.data});

  final _HaritamMockData data;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(20, 18, 20, 18),
      decoration: const BoxDecoration(
        color: _HaritamColors.paperPure,
        border: Border(bottom: BorderSide(color: _HaritamColors.hairline)),
      ),
      child: Container(
        decoration: BoxDecoration(
          border: Border.all(color: _HaritamColors.hairline),
          borderRadius: BorderRadius.circular(8),
        ),
        clipBehavior: Clip.antiAlias,
        child: Column(
          children: [
            _DistRow(label: 'Element', entries: data.elements),
            const SizedBox(
              height: 1,
              child: ColoredBox(color: _HaritamColors.hairline),
            ),
            _DistRow(label: 'Modalite', entries: data.modalities),
          ],
        ),
      ),
    );
  }
}

class _DistRow extends StatelessWidget {
  const _DistRow({required this.label, required this.entries});

  final String label;
  final List<_DistEntry> entries;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(14, 11, 14, 11),
      child: Row(
        children: [
          SizedBox(
            width: 56,
            child: Text(
              label.toUpperCase(),
              style: const TextStyle(
                fontFamily: _HaritamFonts.mono,
                fontSize: 8,
                letterSpacing: 0.5,
                color: _HaritamColors.mist,
              ),
            ),
          ),
          const SizedBox(width: 6),
          Expanded(
            child: Wrap(
              spacing: 6,
              runSpacing: 6,
              children: [
                for (final e in entries) _DistPill(entry: e),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _DistPill extends StatelessWidget {
  const _DistPill({required this.entry});
  final _DistEntry entry;

  @override
  Widget build(BuildContext context) {
    final dom = entry.dominant;
    final lav = entry.lav;
    final bg = dom
        ? (lav ? _HaritamColors.lav : _HaritamColors.lime)
        : Colors.transparent;
    final fg = dom
        ? (lav ? Colors.white : _HaritamColors.limeText)
        : _HaritamColors.fog;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(4),
        border: Border.all(
          color: dom ? Colors.transparent : _HaritamColors.hairline,
        ),
      ),
      child: Text(
        entry.label,
        style: TextStyle(
          fontFamily: _HaritamFonts.mono,
          fontSize: 9,
          color: fg,
          fontWeight: dom ? FontWeight.w500 : FontWeight.w400,
          letterSpacing: 0.1,
        ),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════
// Section 4 — Placements table
// ═══════════════════════════════════════════════════════════════════

class _PlacementsTable extends StatelessWidget {
  const _PlacementsTable({required this.data});
  final _HaritamMockData data;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 22, 20, 0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const _SectionHead(eyebrow: 'Yerleşimler', trailing: '10 obj'),
          const SizedBox(height: 10),
          Container(
            decoration: BoxDecoration(
              border: Border.all(color: _HaritamColors.hairline),
              borderRadius: BorderRadius.circular(10),
              color: _HaritamColors.paperPure,
            ),
            clipBehavior: Clip.antiAlias,
            child: Column(
              children: [
                const _PlacementsHeader(),
                for (final p in data.placements) _PlacementsRow(item: p),
                _MoreRow(label: '+ ${data.extraPoints} ek nokta'),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _SectionHead extends StatelessWidget {
  const _SectionHead({required this.eyebrow, this.trailing});
  final String eyebrow;
  final String? trailing;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Text(
          eyebrow.toUpperCase(),
          style: const TextStyle(
            fontFamily: _HaritamFonts.body,
            fontSize: 8,
            letterSpacing: 2,
            color: _HaritamColors.mist,
          ),
        ),
        const SizedBox(width: 10),
        const Expanded(
          child: SizedBox(
            height: 1,
            child: ColoredBox(color: _HaritamColors.hairline),
          ),
        ),
        if (trailing != null) ...[
          const SizedBox(width: 10),
          Text(
            trailing!,
            style: const TextStyle(
              fontFamily: _HaritamFonts.mono,
              fontSize: 8.5,
              color: _HaritamColors.mist,
              letterSpacing: 0.3,
            ),
          ),
        ],
      ],
    );
  }
}

class _PlacementsHeader extends StatelessWidget {
  const _PlacementsHeader();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(14, 9, 14, 9),
      decoration: const BoxDecoration(
        border: Border(bottom: BorderSide(color: _HaritamColors.hairline)),
      ),
      child: const Row(
        children: [
          SizedBox(width: 24),
          Expanded(child: _HeaderCell('Gezegen')),
          SizedBox(width: 64, child: _HeaderCell('Burç')),
          SizedBox(width: 56, child: _HeaderCell('Derece', textAlign: TextAlign.center)),
          SizedBox(width: 26, child: _HeaderCell('Ev', textAlign: TextAlign.right)),
        ],
      ),
    );
  }
}

class _HeaderCell extends StatelessWidget {
  const _HeaderCell(this.text, {this.textAlign = TextAlign.left});
  final String text;
  final TextAlign textAlign;

  @override
  Widget build(BuildContext context) {
    return Text(
      text.toUpperCase(),
      textAlign: textAlign,
      style: const TextStyle(
        fontFamily: _HaritamFonts.mono,
        fontSize: 7.5,
        letterSpacing: 0.6,
        color: _HaritamColors.silver,
      ),
    );
  }
}

class _PlacementsRow extends StatelessWidget {
  const _PlacementsRow({required this.item});
  final _Placement item;

  @override
  Widget build(BuildContext context) {
    final stellium = item.stellium;
    return Container(
      padding: const EdgeInsets.fromLTRB(14, 11, 14, 11),
      decoration: BoxDecoration(
        color: stellium ? const Color(0x0DCAFF4D) : null,
        border: const Border(
          bottom: BorderSide(color: _HaritamColors.hairlineRow),
        ),
      ),
      child: Row(
        children: [
          SizedBox(
            width: 24,
            child: _PlanetGlyph(
              planet: item.planet,
              color: _glyphColor(item.planet),
            ),
          ),
          Expanded(
            child: Padding(
              padding: const EdgeInsets.only(left: 8),
              child: Row(
                children: [
                  Text(
                    _planetTr(item.planet),
                    style: const TextStyle(
                      fontFamily: _HaritamFonts.body,
                      fontSize: 11.5,
                      color: _HaritamColors.ink,
                      letterSpacing: -0.05,
                    ),
                  ),
                  if (item.retrograde) ...[
                    const SizedBox(width: 5),
                    const Text(
                      'R',
                      style: TextStyle(
                        fontFamily: _HaritamFonts.mono,
                        fontSize: 8,
                        color: _HaritamColors.mist,
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ),
          SizedBox(
            width: 64,
            child: Text(
              item.sign,
              style: const TextStyle(
                fontFamily: _HaritamFonts.body,
                fontSize: 11,
                color: _HaritamColors.ink,
                letterSpacing: -0.05,
              ),
            ),
          ),
          SizedBox(
            width: 56,
            child: Text(
              item.degreeText,
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontFamily: _HaritamFonts.mono,
                fontSize: 9.5,
                color: _HaritamColors.mist,
                letterSpacing: -0.1,
              ),
            ),
          ),
          SizedBox(
            width: 26,
            child: Text(
              '${item.house}',
              textAlign: TextAlign.right,
              style: const TextStyle(
                fontFamily: _HaritamFonts.display,
                fontStyle: FontStyle.italic,
                fontSize: 14,
                color: _HaritamColors.ink,
                fontWeight: FontWeight.w400,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Color _glyphColor(_PlanetKey k) {
    switch (k) {
      case _PlanetKey.sun:
        return _HaritamColors.limeDeep;
      case _PlanetKey.jupiter:
        return _HaritamColors.peachDeep;
      case _PlanetKey.neptune:
      case _PlanetKey.saturn:
        return _HaritamColors.lavDeep;
      case _PlanetKey.moon:
      case _PlanetKey.venus:
        return _HaritamColors.blushDeep;
      case _PlanetKey.mars:
        return _HaritamColors.peachDeep;
      default:
        return _HaritamColors.ink;
    }
  }
}

String _planetTr(_PlanetKey k) {
  switch (k) {
    case _PlanetKey.sun:
      return 'Güneş';
    case _PlanetKey.moon:
      return 'Ay';
    case _PlanetKey.mercury:
      return 'Merkür';
    case _PlanetKey.venus:
      return 'Venüs';
    case _PlanetKey.mars:
      return 'Mars';
    case _PlanetKey.jupiter:
      return 'Jüpiter';
    case _PlanetKey.saturn:
      return 'Satürn';
    case _PlanetKey.uranus:
      return 'Uranüs';
    case _PlanetKey.neptune:
      return 'Neptün';
    case _PlanetKey.pluto:
      return 'Plüton';
    case _PlanetKey.nnode:
      return 'K. Düğüm';
    case _PlanetKey.lilith:
      return 'Lilith';
    case _PlanetKey.chiron:
      return 'Şiron';
    case _PlanetKey.fortune:
      return 'Fortuna';
    case _PlanetKey.asc:
      return 'ASC';
  }
}

class _MoreRow extends StatelessWidget {
  const _MoreRow({required this.label});
  final String label;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 11),
      decoration: const BoxDecoration(
        border: Border(top: BorderSide(color: _HaritamColors.hairline)),
        color: _HaritamColors.paperPure,
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(
            label,
            style: const TextStyle(
              fontFamily: _HaritamFonts.mono,
              fontSize: 9,
              color: _HaritamColors.mist,
              letterSpacing: 0.3,
            ),
          ),
        ],
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════
// Section 5 — Tight aspects table
// ═══════════════════════════════════════════════════════════════════

class _AspectsTable extends StatelessWidget {
  const _AspectsTable({required this.data});
  final _HaritamMockData data;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 22, 20, 18),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const _SectionHead(eyebrow: 'Sıkı açılar', trailing: 'orb < 5°'),
          const SizedBox(height: 10),
          Container(
            decoration: BoxDecoration(
              border: Border.all(color: _HaritamColors.hairline),
              borderRadius: BorderRadius.circular(10),
              color: _HaritamColors.paperPure,
            ),
            clipBehavior: Clip.antiAlias,
            child: Column(
              children: [
                _aspectsHeader(),
                for (final a in data.aspects) _AspectsRow(item: a),
                _MoreRow(label: '+ ${data.extraSextiles} sextile'),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _aspectsHeader() {
    return Container(
      padding: const EdgeInsets.fromLTRB(14, 9, 14, 9),
      decoration: const BoxDecoration(
        border: Border(bottom: BorderSide(color: _HaritamColors.hairline)),
      ),
      child: const Row(
        children: [
          Expanded(
            child: _HeaderCell('Açı', textAlign: TextAlign.center),
          ),
          SizedBox(width: 60, child: _HeaderCell('Tip')),
          SizedBox(width: 50, child: _HeaderCell('Orb', textAlign: TextAlign.right)),
        ],
      ),
    );
  }
}

class _AspectsRow extends StatelessWidget {
  const _AspectsRow({required this.item});
  final _AspectRow item;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(14, 11, 14, 11),
      decoration: const BoxDecoration(
        border: Border(bottom: BorderSide(color: _HaritamColors.hairlineRow)),
      ),
      child: Row(
        children: [
          SizedBox(
            width: 22,
            child: _PlanetGlyph(planet: item.left, color: _aspectGlyphColor(item.left), size: 14),
          ),
          SizedBox(
            width: 18,
            child: _AspectGlyph(kind: item.kind, color: _aspectColor(item.kind), size: 11),
          ),
          SizedBox(
            width: 22,
            child: _PlanetGlyph(planet: item.right, color: _aspectGlyphColor(item.right), size: 14),
          ),
          const SizedBox(width: 10),
          Expanded(child: _AspectTypePill(kind: item.kind, label: item.label)),
          SizedBox(
            width: 56,
            child: Text(
              item.orbText,
              textAlign: TextAlign.right,
              style: TextStyle(
                fontFamily: _HaritamFonts.mono,
                fontSize: 10,
                color: item.tight ? _HaritamColors.limeDeep : _HaritamColors.ink,
                letterSpacing: -0.1,
                fontWeight: item.tight ? FontWeight.w700 : FontWeight.w400,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Color _aspectColor(_AspectKind k) {
    switch (k) {
      case _AspectKind.trine:
      case _AspectKind.sextile:
        return _HaritamColors.peachDeep;
      case _AspectKind.square:
      case _AspectKind.opposition:
        return _HaritamColors.lavDeep;
      case _AspectKind.conjunction:
        return _HaritamColors.fog;
    }
  }

  Color _aspectGlyphColor(_PlanetKey k) {
    switch (k) {
      case _PlanetKey.sun:
        return _HaritamColors.limeDeep;
      case _PlanetKey.moon:
      case _PlanetKey.venus:
        return _HaritamColors.blushDeep;
      case _PlanetKey.mars:
      case _PlanetKey.jupiter:
        return _HaritamColors.peachDeep;
      case _PlanetKey.saturn:
      case _PlanetKey.neptune:
        return _HaritamColors.lavDeep;
      case _PlanetKey.asc:
        return _HaritamColors.limeDeep;
      default:
        return _HaritamColors.ink;
    }
  }
}

class _AspectTypePill extends StatelessWidget {
  const _AspectTypePill({required this.kind, required this.label});
  final _AspectKind kind;
  final String label;

  @override
  Widget build(BuildContext context) {
    Color bg;
    Color fg;
    switch (kind) {
      case _AspectKind.trine:
      case _AspectKind.sextile:
        bg = _HaritamColors.limeBg;
        fg = _HaritamColors.limeDeep;
        break;
      case _AspectKind.square:
      case _AspectKind.opposition:
        bg = _HaritamColors.lavBg;
        fg = _HaritamColors.lavDeep;
        break;
      case _AspectKind.conjunction:
        bg = const Color(0xFFF5F5F5);
        fg = _HaritamColors.fog;
        break;
    }
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(3),
      ),
      child: Text(
        label.toUpperCase(),
        style: TextStyle(
          fontFamily: _HaritamFonts.mono,
          fontSize: 7.5,
          letterSpacing: 0.5,
          color: fg,
        ),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════
// Section 6 — 12 houses dark table
// ═══════════════════════════════════════════════════════════════════

class _HousesDarkTable extends StatelessWidget {
  const _HousesDarkTable({required this.data});
  final _HaritamMockData data;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(20, 22, 20, 18),
      decoration: const BoxDecoration(
        color: _HaritamColors.paperPure,
        border: Border(top: BorderSide(color: _HaritamColors.hairline)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const _SectionHead(eyebrow: '12 Ev', trailing: 'stellium · 1'),
          const SizedBox(height: 10),
          Container(
            decoration: BoxDecoration(
              color: _HaritamColors.ink,
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: _HaritamColors.ink),
            ),
            clipBehavior: Clip.antiAlias,
            child: Column(
              children: [
                _housesHeader(),
                for (final h in data.houses) _HousesRow(row: h),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _housesHeader() {
    return Container(
      padding: const EdgeInsets.fromLTRB(14, 9, 14, 9),
      decoration: const BoxDecoration(
        border: Border(bottom: BorderSide(color: Color(0x1AFFFFFF))),
      ),
      child: const Row(
        children: [
          SizedBox(width: 28, child: _DarkHeaderCell('Ev')),
          SizedBox(width: 44, child: _DarkHeaderCell('Burç')),
          Expanded(child: _DarkHeaderCell('İçinde')),
          SizedBox(width: 22, child: _DarkHeaderCell('#', textAlign: TextAlign.right)),
        ],
      ),
    );
  }
}

class _DarkHeaderCell extends StatelessWidget {
  const _DarkHeaderCell(this.text, {this.textAlign = TextAlign.left});
  final String text;
  final TextAlign textAlign;

  @override
  Widget build(BuildContext context) {
    return Text(
      text.toUpperCase(),
      textAlign: textAlign,
      style: const TextStyle(
        fontFamily: _HaritamFonts.mono,
        fontSize: 7.5,
        letterSpacing: 0.6,
        color: Color(0x66FFFFFF),
      ),
    );
  }
}

class _HousesRow extends StatelessWidget {
  const _HousesRow({required this.row});
  final _HouseRow row;

  @override
  Widget build(BuildContext context) {
    final empty = row.occupants.isEmpty;
    return Container(
      padding: const EdgeInsets.fromLTRB(14, 9, 14, 9),
      decoration: BoxDecoration(
        color: row.stellium ? const Color(0x0DCAFF4D) : null,
        border: const Border(bottom: BorderSide(color: Color(0x10FFFFFF))),
      ),
      child: Row(
        children: [
          SizedBox(
            width: 28,
            child: Text(
              '${row.number}',
              style: TextStyle(
                fontFamily: _HaritamFonts.display,
                fontStyle: FontStyle.italic,
                fontSize: 14,
                color: empty ? const Color(0x4DFFFFFF) : _HaritamColors.lime,
              ),
            ),
          ),
          SizedBox(
            width: 44,
            child: Text(
              row.signCode,
              style: const TextStyle(
                fontFamily: _HaritamFonts.mono,
                fontSize: 9,
                color: Color(0x80FFFFFF),
                letterSpacing: 0.5,
              ),
            ),
          ),
          Expanded(
            child: empty
                ? const Text(
                    '—',
                    style: TextStyle(
                      color: Color(0x40FFFFFF),
                      fontSize: 10.5,
                    ),
                  )
                : Wrap(
                    spacing: 5,
                    runSpacing: 4,
                    children: [
                      for (final p in row.occupants)
                        _PlanetGlyph(
                          planet: p,
                          color: _occupantColor(p),
                          size: 11,
                        ),
                    ],
                  ),
          ),
          SizedBox(
            width: 22,
            child: Text(
              empty ? '·' : '${row.occupants.length}',
              textAlign: TextAlign.right,
              style: TextStyle(
                fontFamily: _HaritamFonts.mono,
                fontSize: 9,
                color: empty
                    ? const Color(0x59FFFFFF)
                    : _HaritamColors.lime,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Color _occupantColor(_PlanetKey k) {
    switch (k) {
      case _PlanetKey.sun:
      case _PlanetKey.pluto:
        return _HaritamColors.lime;
      case _PlanetKey.jupiter:
      case _PlanetKey.mars:
        return _HaritamColors.peach;
      case _PlanetKey.moon:
      case _PlanetKey.venus:
        return _HaritamColors.blush;
      case _PlanetKey.saturn:
      case _PlanetKey.neptune:
        return _HaritamColors.lavSoft;
      default:
        return Colors.white;
    }
  }
}

// ═══════════════════════════════════════════════════════════════════
// Section 7 — Meta block (file)
// ═══════════════════════════════════════════════════════════════════

class _MetaBlock extends StatelessWidget {
  const _MetaBlock({required this.data});
  final _HaritamMockData data;

  @override
  Widget build(BuildContext context) {
    final rows = <List<String>>[
      ['Tarih', '28.12.1996'],
      ['Saat · Zone', '11:42 · GMT+3'],
      ['Konum', 'İstanbul'],
      ['Koordinat', data.coordinates],
      ['Sistem · Zodiak', data.systemLabel],
    ];
    return Container(
      padding: const EdgeInsets.fromLTRB(20, 18, 20, 22),
      decoration: const BoxDecoration(
        color: _HaritamColors.paperPure,
        border: Border(top: BorderSide(color: _HaritamColors.hairline)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const _SectionHead(eyebrow: 'Dosya'),
          const SizedBox(height: 10),
          Container(
            decoration: BoxDecoration(
              border: Border.all(color: _HaritamColors.hairline),
              borderRadius: BorderRadius.circular(10),
            ),
            clipBehavior: Clip.antiAlias,
            child: Column(
              children: [
                for (var i = 0; i < rows.length; i++)
                  Container(
                    padding: const EdgeInsets.fromLTRB(14, 10, 14, 10),
                    decoration: BoxDecoration(
                      color: _HaritamColors.paperPure,
                      border: i == rows.length - 1
                          ? null
                          : const Border(
                              bottom: BorderSide(
                                color: _HaritamColors.hairlineRow,
                              ),
                            ),
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          rows[i][0],
                          style: const TextStyle(
                            fontFamily: _HaritamFonts.mono,
                            fontSize: 9.5,
                            color: _HaritamColors.mist,
                            letterSpacing: 0.1,
                          ),
                        ),
                        Text(
                          rows[i][1],
                          style: const TextStyle(
                            fontFamily: _HaritamFonts.mono,
                            fontSize: 9.5,
                            color: _HaritamColors.ink,
                            letterSpacing: 0.1,
                          ),
                        ),
                      ],
                    ),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════
// Glyph helpers — inline SVG via flutter_svg
// ═══════════════════════════════════════════════════════════════════

class _PlanetGlyph extends StatelessWidget {
  const _PlanetGlyph({
    required this.planet,
    required this.color,
    this.size = 16,
  });

  final _PlanetKey planet;
  final Color color;
  final double size;

  @override
  Widget build(BuildContext context) {
    final svg = _planetSvg(planet);
    return SizedBox(
      width: size,
      height: size,
      child: SvgPicture.string(
        svg,
        colorFilter: ColorFilter.mode(color, BlendMode.srcIn),
        fit: BoxFit.contain,
      ),
    );
  }
}

class _AspectGlyph extends StatelessWidget {
  const _AspectGlyph({
    required this.kind,
    required this.color,
    this.size = 11,
  });

  final _AspectKind kind;
  final Color color;
  final double size;

  @override
  Widget build(BuildContext context) {
    final svg = _aspectSvg(kind);
    return SizedBox(
      width: size,
      height: size,
      child: SvgPicture.string(
        svg,
        colorFilter: ColorFilter.mode(color, BlendMode.srcIn),
        fit: BoxFit.contain,
      ),
    );
  }
}

String _planetSvg(_PlanetKey k) {
  switch (k) {
    case _PlanetKey.sun:
      return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><circle cx="8" cy="8" r="6" fill="none" stroke="currentColor" stroke-width="1.2"/><circle cx="8" cy="8" r="1.5" fill="currentColor"/></svg>';
    case _PlanetKey.moon:
      return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><path d="M11.5 3.5 A6 6 0 1 0 11.5 12.5 A4.5 4.5 0 1 1 11.5 3.5 Z" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/></svg>';
    case _PlanetKey.mercury:
      return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><path d="M5 2 A3 3 0 0 0 11 2" fill="none" stroke="currentColor" stroke-width="1.1" stroke-linecap="round"/><circle cx="8" cy="6.5" r="2.5" fill="none" stroke="currentColor" stroke-width="1.2"/><line x1="8" y1="9" x2="8" y2="13.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/><line x1="6" y1="11.5" x2="10" y2="11.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>';
    case _PlanetKey.venus:
      return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><circle cx="8" cy="6" r="3" fill="none" stroke="currentColor" stroke-width="1.2"/><line x1="8" y1="9" x2="8" y2="14" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/><line x1="6" y1="12" x2="10" y2="12" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>';
    case _PlanetKey.mars:
      return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><circle cx="7" cy="9" r="3" fill="none" stroke="currentColor" stroke-width="1.2"/><line x1="9.2" y1="6.8" x2="13" y2="3" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/><polyline points="9.5,3 13,3 13,6.5" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round" stroke-linecap="round"/></svg>';
    case _PlanetKey.jupiter:
      return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><path d="M3 5 Q3 3 5 3 Q7 3 7 5 L7 12.5" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/><line x1="3" y1="9.5" x2="11.5" y2="9.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>';
    case _PlanetKey.saturn:
      return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><line x1="6" y1="2" x2="6" y2="11" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/><line x1="3.5" y1="3.5" x2="8.5" y2="3.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/><path d="M6 9 Q6 13 9 13 Q12 13 12 10.5 Q12 8 10 8" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>';
    case _PlanetKey.uranus:
      return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><line x1="4" y1="3" x2="4" y2="9" stroke="currentColor" stroke-width="1.1" stroke-linecap="round"/><line x1="12" y1="3" x2="12" y2="9" stroke="currentColor" stroke-width="1.1" stroke-linecap="round"/><line x1="4" y1="6" x2="12" y2="6" stroke="currentColor" stroke-width="1.1" stroke-linecap="round"/><line x1="8" y1="9" x2="8" y2="11.5" stroke="currentColor" stroke-width="1.1" stroke-linecap="round"/><circle cx="8" cy="13" r="1.3" fill="none" stroke="currentColor" stroke-width="1.1"/></svg>';
    case _PlanetKey.neptune:
      return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><path d="M3 3 Q3 8 8 8 Q13 8 13 3" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/><line x1="3" y1="3" x2="3" y2="6" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/><line x1="13" y1="3" x2="13" y2="6" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/><line x1="8" y1="3" x2="8" y2="13" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/><line x1="5.5" y1="11" x2="10.5" y2="11" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>';
    case _PlanetKey.pluto:
      return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><path d="M4 4 Q4 7 8 7 Q12 7 12 4" fill="none" stroke="currentColor" stroke-width="1.1" stroke-linecap="round"/><circle cx="8" cy="5" r="1.5" fill="none" stroke="currentColor" stroke-width="1.1"/><line x1="8" y1="7" x2="8" y2="13.5" stroke="currentColor" stroke-width="1.1" stroke-linecap="round"/><line x1="5.5" y1="11" x2="10.5" y2="11" stroke="currentColor" stroke-width="1.1" stroke-linecap="round"/></svg>';
    case _PlanetKey.nnode:
      return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><path d="M3 12 Q3 4 8 4 Q13 4 13 12" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/><circle cx="3" cy="12.5" r="1.2" fill="none" stroke="currentColor" stroke-width="1.1"/><circle cx="13" cy="12.5" r="1.2" fill="none" stroke="currentColor" stroke-width="1.1"/></svg>';
    case _PlanetKey.lilith:
      return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><path d="M11 3 A5 5 0 1 0 11 11 A4 4 0 1 1 11 3 Z" fill="none" stroke="currentColor" stroke-width="1.1" stroke-linejoin="round"/><line x1="8" y1="11" x2="8" y2="14" stroke="currentColor" stroke-width="1.1" stroke-linecap="round"/><line x1="6" y1="12.5" x2="10" y2="12.5" stroke="currentColor" stroke-width="1.1" stroke-linecap="round"/></svg>';
    case _PlanetKey.chiron:
      return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><line x1="6" y1="2" x2="6" y2="11" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/><path d="M6 4 L11 7 L6 9" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round" stroke-linecap="round"/><circle cx="6" cy="13" r="1.5" fill="none" stroke="currentColor" stroke-width="1.2"/></svg>';
    case _PlanetKey.fortune:
      return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><circle cx="8" cy="8" r="6" fill="none" stroke="currentColor" stroke-width="1.2"/><line x1="3.5" y1="3.5" x2="12.5" y2="12.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/><line x1="3.5" y1="12.5" x2="12.5" y2="3.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>';
    case _PlanetKey.asc:
      return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><line x1="2" y1="8" x2="13" y2="8" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/><polyline points="9,4 13,8 9,12" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round" stroke-linecap="round"/></svg>';
  }
}

String _aspectSvg(_AspectKind k) {
  switch (k) {
    case _AspectKind.conjunction:
      return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><circle cx="6" cy="9" r="2.2" fill="none" stroke="currentColor" stroke-width="1.2"/><line x1="7.6" y1="7.4" x2="13" y2="3" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>';
    case _AspectKind.trine:
      return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><polygon points="8,3 13,12 3,12" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/></svg>';
    case _AspectKind.square:
      return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><rect x="3.5" y="3.5" width="9" height="9" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/></svg>';
    case _AspectKind.sextile:
      return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><line x1="3" y1="8" x2="13" y2="8" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/><line x1="8" y1="3" x2="8" y2="13" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/><line x1="4.5" y1="4.5" x2="11.5" y2="11.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/><line x1="11.5" y1="4.5" x2="4.5" y2="11.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>';
    case _AspectKind.opposition:
      return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><line x1="3" y1="8" x2="13" y2="8" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/><circle cx="3" cy="8" r="1.5" fill="none" stroke="currentColor" stroke-width="1.2"/><circle cx="13" cy="8" r="1.5" fill="none" stroke="currentColor" stroke-width="1.2"/></svg>';
  }
}
