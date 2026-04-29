// ignore_for_file: unused_field, unused_element
//
// Home v12 bölüm-bölüm kuruluyor; palet ve enum değerleri sonraki
// fazlarda devreye girecek — bilerek şimdiden tanımlı.

import 'dart:math' as math;

import 'package:dio/dio.dart' show DioException;
import 'package:flutter/foundation.dart' show kDebugMode;
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';

import 'package:mobile/app/api/api_environment.dart';
import 'package:mobile/app/tabs/home_v2_natal.dart';
import 'package:mobile/app/tabs/home_v2_providers.dart';
import 'package:mobile/design/widgets/shou_topbar.dart';

/// SHOU Home v12 — yeni tasarım.
///
/// Canlı data bağlı legacy [HomePage] duruyor; bu sayfa mock veriyle
/// bölüm-bölüm kuruluyor, son aşamada provider'lara bağlanacak.

/// Bond / Friends Lattice feature flag.
///
/// `_NearSection` (friend avatar rail) and `_FeedSection` (friends'
/// transit posts) are gated behind this flag because the underlying
/// Bond/Synastry partner-data infrastructure is not in production yet.
/// While `false`, both sections render nothing — see P0-A cleanup plan
/// (docs/system/home_profile_surface_cleanup_plan.md). Flipping this to
/// `true` will require a live `bondPartnersProvider` data source.
const bool kHomeBondFeatureEnabled = false;
class HomePageV2 extends ConsumerStatefulWidget {
  const HomePageV2({super.key});

  @override
  ConsumerState<HomePageV2> createState() => _HomePageV2State();
}

class _HomePageV2State extends ConsumerState<HomePageV2> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _HomeV2Palette.paper,
      body: SafeArea(
        bottom: false,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            ShouTopBar(
              label: 'BUGÜN',
              variant: ShouTopBarVariant.light,
              onSearch: () {},
              onMenu: () {},
            ),
            const _DevDataStatusChip(),
            const Expanded(
              child: SingleChildScrollView(
                physics: BouncingScrollPhysics(),
                padding: EdgeInsets.only(bottom: 120),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    _ManifestoSection(),
                    _DividerGlyph(style: _DividerStyle.spark),
                    _SkySection(),
                    _AskewBanner(),
                    _NearSection(),
                    _DividerGlyph(style: _DividerStyle.dot),
                    _FeedSection(),
                    _ChartWheelSection(),
                    _PullQuoteSection(),
                    _StickerGridSection(),
                    _ForumSection(),
                    _WeekSection(),
                    _Endpiece(),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Dev-only: provider durumunu üstte gösteren mini chip. Sadece
/// `kDebugMode` aktifken görünür — release build'de tamamen gizli.
class _DevDataStatusChip extends ConsumerWidget {
  const _DevDataStatusChip();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (!kDebugMode) return const SizedBox.shrink();
    final snap = ref.watch(homeV2SnapshotProvider);
    final sky = ref.watch(homeV2SkyNowProvider);
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        _chip(
          bg: _HomeV2Palette.ink,
          fg: _HomeV2Palette.lime,
          text: 'DEV · API = ${ApiEnvironment.apiBaseUrl}',
        ),
        snap.when(
          data: (s) => _chip(
            bg: const Color(0xFFEAFFB8),
            fg: _HomeV2Palette.limeText,
            text: s == null
                ? 'DEV · NARRATIVE · PROFİL YOK (mock)'
                : 'DEV · NARRATIVE · ${s.displayName} · '
                      '${s.narrative.dailyEventCards.length} daily · '
                      '${s.narrative.periodEventCards.length} period · '
                      '${s.narrative.calendarDays.length} day',
          ),
          loading: () => _chip(
            bg: _HomeV2Palette.cream,
            fg: _HomeV2Palette.fog,
            text: 'DEV · NARRATIVE · yükleniyor…',
          ),
          error: (err, _) => _chip(
            bg: const Color(0xFFFDE4F2),
            fg: _HomeV2Palette.blushDeep,
            text: 'DEV · NARRATIVE HATA · ${_formatError(err)}',
          ),
        ),
        sky.when(
          data: (s) => _chip(
            bg: const Color(0xFFF0EEFF),
            fg: _HomeV2Palette.lavenderDeep,
            text: s == null
                ? 'DEV · SKY/NOW · null (mock banner)'
                : 'DEV · SKY/NOW · ${s.items.length} item · '
                      'hero="${s.items.isNotEmpty ? s.items.first.shortTitle : "—"}"',
          ),
          loading: () => _chip(
            bg: _HomeV2Palette.cream,
            fg: _HomeV2Palette.fog,
            text: 'DEV · SKY/NOW · yükleniyor…',
          ),
          error: (err, _) => _chip(
            bg: const Color(0xFFFDE4F2),
            fg: _HomeV2Palette.blushDeep,
            text: 'DEV · SKY HATA · ${_formatError(err)}',
          ),
        ),
        ref
            .watch(homeV2NatalProvider)
            .when(
              data: (s) => _chip(
                bg: const Color(0xFFFDE4F2),
                fg: _HomeV2Palette.blushDeep,
                text: s == null
                    ? 'DEV · NATAL · null (mock planets)'
                    : 'DEV · NATAL · ${s.planets.length} gezegen · '
                          'Asc=${s.angles.ascendantSign} · '
                          'Moon=${s.findPlanet("Moon")?.sign ?? "—"}',
              ),
              loading: () => _chip(
                bg: _HomeV2Palette.cream,
                fg: _HomeV2Palette.fog,
                text: 'DEV · NATAL · yükleniyor…',
              ),
              error: (err, _) => _chip(
                bg: const Color(0xFFFDE4F2),
                fg: _HomeV2Palette.blushDeep,
                text: 'DEV · NATAL HATA · ${_formatError(err)}',
              ),
            ),
      ],
    );
  }

  String _formatError(Object err) {
    if (err is DioException) {
      final status = err.response?.statusCode;
      final body = err.response?.data;
      final bodyStr = body == null ? '' : body.toString();
      final trimmed = bodyStr.length > 200
          ? '${bodyStr.substring(0, 200)}…'
          : bodyStr;
      return 'HTTP ${status ?? "?"} · ${err.type.name}'
          '${trimmed.isNotEmpty ? " · $trimmed" : ""}';
    }
    final s = err.toString();
    return s.length > 240 ? '${s.substring(0, 240)}…' : s;
  }

  Widget _chip({required Color bg, required Color fg, required String text}) {
    return Container(
      width: double.infinity,
      color: bg,
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
      child: SelectableText(
        text,
        style: GoogleFonts.jetBrainsMono(
          textStyle: TextStyle(
            fontSize: 9.5,
            letterSpacing: 0.6,
            color: fg,
            fontWeight: FontWeight.w500,
          ),
        ),
      ),
    );
  }
}

/// Paletin ortak referansı — v12 HTML'indeki CSS değişkenleriyle birebir.
class _HomeV2Palette {
  const _HomeV2Palette._();

  static const Color ink = Color(0xFF111111);
  static const Color graphite = Color(0xFF222222);
  static const Color fog = Color(0xFF444444);
  static const Color mist = Color(0xFF777777);
  static const Color silver = Color(0xFFAAAAAA);
  static const Color cloud = Color(0xFFCCCCCC);
  static const Color hairline = Color(0x14000000); // rgba(0,0,0,.08)
  static const Color paper = Color(0xFFFAFAF7);
  static const Color cream = Color(0xFFF5F3EE);
  static const Color lime = Color(0xFFCAFF4D);
  static const Color limeText = Color(0xFF1A3300);
  static const Color lavender = Color(0xFF7F77DD);
  static const Color lavenderDeep = Color(0xFF534AB7);
  static const Color lavenderBg = Color(0xFFF0EEFF);
  static const Color blush = Color(0xFFF9A8D4);
  static const Color blushDeep = Color(0xFFC76FA0);
  static const Color blushBg = Color(0xFFFDE4F2);
  static const Color white = Color(0xFFFFFFFF);
}

// ─────────────────────────────────────────────────────────────
// MANIFESTO SECTION
// ─────────────────────────────────────────────────────────────

class _ManifestoSection extends ConsumerWidget {
  const _ManifestoSection();

  /// Backend-driven manifesto hook. Maps to the existing live narrative
  /// payload — no new schema field. Tries `periodCore.upperMeaning`
  /// first (typically a single editorial sentence), falls back to the
  /// first sentence of `periodCore.coreStory`. Returns `null` when
  /// neither is available so the UI hides the title area instead of
  /// falling back to a hardcoded mock. Inlined here (rather than as a
  /// provider getter) to keep `home_v2_providers.dart` untouched.
  static String? _coreStoryHeadline(HomeV2Snapshot? snapshot) {
    final core = snapshot?.narrative.periodCore;
    if (core == null) return null;

    final upper = core.upperMeaning.trim();
    if (upper.isNotEmpty) return upper;

    final story = core.coreStory.trim();
    if (story.isEmpty) return null;
    final firstSentenceEnd = story.indexOf(RegExp(r'[.!?](\s|$)'));
    if (firstSentenceEnd < 0) return story;
    return story.substring(0, firstSentenceEnd + 1).trim();
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final snapshot = ref.watch(homeV2SnapshotProvider).value;
    // Backend-driven manifesto hook. When live data is missing the title
    // area (and its surrounding spacing) collapses entirely instead of
    // falling back to a hardcoded mock — see P0-A cleanup plan.
    final headline = _coreStoryHeadline(snapshot)?.trim();
    final hasHeadline = headline != null && headline.isNotEmpty;
    return Padding(
      padding: const EdgeInsets.fromLTRB(28, 42, 28, 48),
      child: Column(
        children: [
          _ManifestoGreeting(
            name: snapshot?.displayName ?? 'Sahra',
            dateLabel: snapshot?.formattedDate ?? '17 Nisan Cuma',
            moonSign: snapshot?.moonSignLabel ?? 'Aslan burcunda',
            salutation: snapshot?.salutation ?? greetingForHour(DateTime.now().hour),
          ),
          if (hasHeadline) const SizedBox(height: 32),
          if (hasHeadline) _ManifestoTitle(headline: headline),
          const SizedBox(height: 36),
          const _OrbitEmblem(),
          const SizedBox(height: 26),
          const _ManifestoOpenLink(),
          const SizedBox(height: 30),
          const _ManifestoMetaRow(),
        ],
      ),
    );
  }
}

/// "Tünaydın, Sahra. Bugün 17 Nisan Cuma ve gökyüzünde Ay Aslan burcunda."
/// İsim ve tarih ince underline, burç adı lime altı çizili.
class _ManifestoGreeting extends StatelessWidget {
  const _ManifestoGreeting({
    required this.salutation,
    required this.name,
    required this.dateLabel,
    required this.moonSign,
  });

  final String salutation;
  final String name;
  final String dateLabel;
  final String moonSign;

  @override
  Widget build(BuildContext context) {
    const baseStyle = TextStyle(
      fontSize: 12.5,
      height: 1.65,
      letterSpacing: -0.1,
      color: _HomeV2Palette.fog,
      fontWeight: FontWeight.w400,
    );
    final base = GoogleFonts.inter(textStyle: baseStyle);
    final inkUnderlined = base.copyWith(
      color: _HomeV2Palette.ink,
      decoration: TextDecoration.underline,
      decorationColor: const Color(0x4D000000),
      decorationThickness: 0.5,
    );
    final limeUnderlined = base.copyWith(
      color: _HomeV2Palette.ink,
      decoration: TextDecoration.underline,
      decorationColor: _HomeV2Palette.lime,
      decorationThickness: 2,
    );

    return ConstrainedBox(
      constraints: const BoxConstraints(maxWidth: 280),
      child: Text.rich(
        TextSpan(
          style: base,
          children: [
            TextSpan(text: '$salutation, '),
            TextSpan(text: name, style: inkUnderlined),
            const TextSpan(text: '. Bugün '),
            TextSpan(text: dateLabel, style: inkUnderlined),
            const TextSpan(text: ' ve gökyüzünde Ay '),
            TextSpan(text: moonSign, style: limeUnderlined),
            const TextSpan(text: '. Günün tek cümlesi:'),
          ],
        ),
        textAlign: TextAlign.center,
      ),
    );
  }
}

/// Manifesto title — backend-driven. Receives a live editorial hook from
/// `HomeV2Snapshot.coreStoryHeadline` (period upper meaning / first
/// sentence of core story). Caller is responsible for hiding this widget
/// when the headline is empty; here we always assume non-empty input.
///
/// Styling kept editorial (Inter base + Fraunces italic accent) but the
/// dynamic copy means we no longer hand-place the lime highlight on
/// specific words — that was a static-copy affordance.
class _ManifestoTitle extends StatelessWidget {
  const _ManifestoTitle({required this.headline});

  final String headline;

  @override
  Widget build(BuildContext context) {
    final base = GoogleFonts.fraunces(
      textStyle: const TextStyle(
        fontSize: 24,
        height: 1.28,
        letterSpacing: -0.4,
        color: _HomeV2Palette.ink,
        fontStyle: FontStyle.italic,
        fontWeight: FontWeight.w400,
      ),
    );

    return ConstrainedBox(
      constraints: const BoxConstraints(maxWidth: 320),
      child: Text(
        headline,
        style: base,
        textAlign: TextAlign.center,
      ),
    );
  }
}

/// Logo orbit centerpiece — iki halka yavaş dönüyor, üstte lime sinyal
/// noktası nabız atıyor, köşelerde iki kıvılcım parlıyor.
class _OrbitEmblem extends StatefulWidget {
  const _OrbitEmblem();

  @override
  State<_OrbitEmblem> createState() => _OrbitEmblemState();
}

class _OrbitEmblemState extends State<_OrbitEmblem>
    with TickerProviderStateMixin {
  late final AnimationController _outer;
  late final AnimationController _inner;
  late final AnimationController _pulse;

  @override
  void initState() {
    super.initState();
    _outer = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 120),
    )..repeat();
    _inner = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 80),
    )..repeat(reverse: false);
    _pulse = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 3),
    )..repeat(reverse: true);
  }

  @override
  void dispose() {
    _outer.dispose();
    _inner.dispose();
    _pulse.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 108,
      height: 108,
      child: AnimatedBuilder(
        animation: Listenable.merge([_outer, _inner, _pulse]),
        builder: (context, _) {
          return CustomPaint(
            painter: _OrbitEmblemPainter(
              outerT: _outer.value,
              innerT: -_inner.value, // reverse
              pulseT: _pulse.value,
            ),
          );
        },
      ),
    );
  }
}

class _OrbitEmblemPainter extends CustomPainter {
  _OrbitEmblemPainter({
    required this.outerT,
    required this.innerT,
    required this.pulseT,
  });

  final double outerT;
  final double innerT;
  final double pulseT;

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    // HTML viewBox 108, r=44 (outer) r=24 (inner)
    final rOuter = size.width * 44 / 108;
    final rInner = size.width * 24 / 108;

    // Çok soluk dolgu halka
    final fill = Paint()..color = const Color(0x04000000);
    canvas.drawCircle(center, rOuter, fill);

    // Outer ring + rotating lime signal dot
    final ringPaint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1
      ..color = _HomeV2Palette.ink;
    canvas.drawCircle(center, rOuter, ringPaint);

    canvas.save();
    canvas.translate(center.dx, center.dy);
    canvas.rotate(outerT * 2 * 3.1415926535);
    final pulseScale = 0.9 + 0.2 * (1 - (pulseT * 2 - 1).abs()); // 0.9..1.1
    final pulseOpacity = 0.55 + 0.45 * (1 - (pulseT * 2 - 1).abs());
    final topDotPaint = Paint()
      ..color = _HomeV2Palette.lime.withValues(alpha: pulseOpacity);
    canvas.drawCircle(
      Offset(0, -rOuter), // top of ring
      3.5 * pulseScale,
      topDotPaint,
    );
    canvas.restore();

    // Inner dashed ring + rotating small black dot
    _drawDashedCircle(
      canvas,
      center,
      rInner,
      const Color(0xFF111111),
      dashLength: 2,
      gapLength: 4,
      strokeWidth: 1,
    );
    canvas.save();
    canvas.translate(center.dx, center.dy);
    canvas.rotate(innerT * 2 * 3.1415926535);
    final innerDot = Paint()..color = _HomeV2Palette.ink;
    canvas.drawCircle(Offset(rInner, 0), 1.8, innerDot);
    canvas.restore();

    // Merkez nokta
    canvas.drawCircle(center, 3.5, Paint()..color = _HomeV2Palette.ink);

    // İki küçük sparkle (statik, hafif opaklık)
    _drawSparkle(
      canvas,
      offset: Offset(size.width * 82 / 108, size.height * 23 / 108),
      size: 3.5,
      color: _HomeV2Palette.lime.withValues(alpha: 0.6),
    );
    _drawSparkle(
      canvas,
      offset: Offset(size.width * 22 / 108, size.height * 84 / 108),
      size: 2.5,
      color: _HomeV2Palette.lavender.withValues(alpha: 0.55),
    );
  }

  void _drawDashedCircle(
    Canvas canvas,
    Offset center,
    double radius,
    Color color, {
    required double dashLength,
    required double gapLength,
    required double strokeWidth,
  }) {
    final paint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth
      ..color = color;
    final circumference = 2 * 3.1415926535 * radius;
    final dashCount = (circumference / (dashLength + gapLength)).floor();
    final anglePerStep = 2 * 3.1415926535 / dashCount;
    final dashAngle = (dashLength / circumference) * 2 * 3.1415926535;

    final rect = Rect.fromCircle(center: center, radius: radius);
    for (var i = 0; i < dashCount; i++) {
      final start = i * anglePerStep;
      final path = Path()..addArc(rect, start, dashAngle);
      canvas.drawPath(path, paint);
    }
  }

  void _drawSparkle(
    Canvas canvas, {
    required Offset offset,
    required double size,
    required Color color,
  }) {
    final path = Path()
      ..moveTo(offset.dx, offset.dy - size)
      ..lineTo(offset.dx + size * 0.3, offset.dy - size * 0.3)
      ..lineTo(offset.dx + size, offset.dy)
      ..lineTo(offset.dx + size * 0.3, offset.dy + size * 0.3)
      ..lineTo(offset.dx, offset.dy + size)
      ..lineTo(offset.dx - size * 0.3, offset.dy + size * 0.3)
      ..lineTo(offset.dx - size, offset.dy)
      ..lineTo(offset.dx - size * 0.3, offset.dy - size * 0.3)
      ..close();
    canvas.drawPath(path, Paint()..color = color);
  }

  @override
  bool shouldRepaint(covariant _OrbitEmblemPainter old) =>
      old.outerT != outerT || old.innerT != innerT || old.pulseT != pulseT;
}

/// "GÜNÜ AÇ →" — letterspaced uppercase link, ince underline.
class _ManifestoOpenLink extends StatelessWidget {
  const _ManifestoOpenLink();

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: () {
        // TODO: Profil Detay (profile_detail_flow) açılacak.
      },
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 4),
        child: Text(
          'GÜNÜ AÇ  →',
          style: GoogleFonts.inter(
            textStyle: const TextStyle(
              fontSize: 10.5,
              letterSpacing: 2.5,
              color: _HomeV2Palette.ink,
              fontWeight: FontWeight.w400,
              decoration: TextDecoration.underline,
              decorationThickness: 0.5,
              decorationColor: _HomeV2Palette.ink,
            ),
          ),
        ),
      ),
    );
  }
}

/// Alt meta satırı: aktif Ay burcu lime bg, yumuşak dimmed Güneş/Venüs.
class _ManifestoMetaRow extends StatelessWidget {
  const _ManifestoMetaRow();

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        _MetaChip(label: '☽ Aslan', active: true),
        SizedBox(width: 22),
        _MetaChip(label: '☉ Koç'),
        SizedBox(width: 14),
        _MetaDot(),
        SizedBox(width: 14),
        _MetaChip(label: '♀ Boğa'),
      ],
    );
  }
}

class _MetaChip extends StatelessWidget {
  const _MetaChip({required this.label, this.active = false});
  final String label;
  final bool active;

  @override
  Widget build(BuildContext context) {
    final style = GoogleFonts.inter(
      textStyle: TextStyle(
        fontSize: 8.5,
        letterSpacing: 1.4,
        color: active ? _HomeV2Palette.limeText : _HomeV2Palette.silver,
        fontWeight: FontWeight.w400,
      ),
    );
    final text = Text(label.toUpperCase(), style: style);
    if (!active) return text;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: _HomeV2Palette.lime,
        borderRadius: BorderRadius.circular(3),
      ),
      child: text,
    );
  }
}

class _MetaDot extends StatelessWidget {
  const _MetaDot();
  @override
  Widget build(BuildContext context) {
    return Container(
      width: 3,
      height: 3,
      decoration: const BoxDecoration(
        color: _HomeV2Palette.cloud,
        shape: BoxShape.circle,
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────
// DIVIDER GLYPH (section separator)
// ─────────────────────────────────────────────────────────────

enum _DividerStyle { spark, dot }

class _DividerGlyph extends StatelessWidget {
  const _DividerGlyph({this.style = _DividerStyle.spark});
  final _DividerStyle style;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(0, 28, 0, 20),
      child: Row(
        children: [
          const Expanded(child: _HairlineRule()),
          SizedBox(
            width: 14,
            height: 14,
            child: CustomPaint(
              painter: style == _DividerStyle.spark
                  ? _SparkGlyphPainter()
                  : _DotGlyphPainter(),
            ),
          ),
          const Expanded(child: _HairlineRule()),
        ],
      ),
    );
  }
}

class _HairlineRule extends StatelessWidget {
  const _HairlineRule();
  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 18),
      child: Container(height: 0.5, color: _HomeV2Palette.hairline),
    );
  }
}

class _SparkGlyphPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    // 12x12 viewBox sparkle → scale to 14x14
    final scale = size.width / 12;
    final path = Path()
      ..moveTo(6 * scale, 1 * scale)
      ..lineTo(6.4 * scale, 5.3 * scale)
      ..lineTo(11 * scale, 6 * scale)
      ..lineTo(6.4 * scale, 6.7 * scale)
      ..lineTo(6 * scale, 11 * scale)
      ..lineTo(5.6 * scale, 6.7 * scale)
      ..lineTo(1 * scale, 6 * scale)
      ..lineTo(5.6 * scale, 5.3 * scale)
      ..close();
    canvas.drawPath(
      path,
      Paint()..color = _HomeV2Palette.mist.withValues(alpha: 0.55),
    );
  }

  @override
  bool shouldRepaint(covariant CustomPainter old) => false;
}

class _DotGlyphPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final ring = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 0.5
      ..color = _HomeV2Palette.mist;
    canvas.drawCircle(center, size.width / 2 - 1, ring);
    canvas.drawCircle(center, 1.5, Paint()..color = _HomeV2Palette.mist);
  }

  @override
  bool shouldRepaint(covariant CustomPainter old) => false;
}

// ─────────────────────────────────────────────────────────────
// SKY SECTION — eyebrow + quote + yatay 5 transit kartı
// ─────────────────────────────────────────────────────────────

class _SkySection extends StatelessWidget {
  const _SkySection();

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(0, 14, 0, 48),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: const [
          _SkyHead(),
          SizedBox(height: 24),
          _SkyRail(),
        ],
      ),
    );
  }
}

class _SkyHead extends StatelessWidget {
  const _SkyHead();

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 28),
      child: Column(
        children: [
          Text(
            'GÖKYÜZÜ · ŞU AN',
            style: GoogleFonts.inter(
              textStyle: const TextStyle(
                fontSize: 8.5,
                letterSpacing: 2.4,
                color: _HomeV2Palette.silver,
                fontWeight: FontWeight.w400,
              ),
            ),
          ),
          // Central editorial sky-quote dropped in P0-A cleanup: previous
          // copy was hardcoded editorial text and no backend field exists
          // for a sky-now hook today. Section keeps the eyebrow + the
          // horizontal sky rail; the quote returns once a dedicated
          // `narrative.sky_now_quote` field ships (Sprint 3).
        ],
      ),
    );
  }
}

// `_SkyQuote` widget removed in P0-A cleanup. Previous central sky-quote
// was hardcoded editorial copy with no backend hook; live data only
// covers the horizontal sky rail (HomeV2SkyCard list). When a dedicated
// `narrative.sky_now_quote` field ships (deferred to Sprint 3), the
// central quote can return as a backend-driven widget.
//
// `_LimeUnderlay` (defined below) was used by `_SkyQuote` for the gradient
// underline effect — kept for now in case other future widgets need it,
// but currently has no callers in this file.

/// Metnin altında ~%26 yüksekliğinde lime band — HTML'deki linear-gradient
/// underline efektinin basitleştirilmiş versiyonu.
class _LimeUnderlay extends StatelessWidget {
  const _LimeUnderlay({required this.child});
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Stack(
      alignment: Alignment.bottomCenter,
      children: [
        Positioned(
          left: -2,
          right: -2,
          bottom: 1,
          height: 7,
          child: Container(color: _HomeV2Palette.lime),
        ),
        child,
      ],
    );
  }
}

class _SkyRail extends ConsumerWidget {
  const _SkyRail();

  static const _mockCards = <_SkyCardData>[
    _SkyCardData(
      tone: _SkyCardTone.now,
      when: 'Şimdi',
      glyph: _PlanetKind.moon,
      titlePrefix: 'Ay · Aslan\'da',
      sub: 'Duygular sahne arar. Gösterme değil — paylaşma.',
      affMeta: '14°23′ · AÇ',
    ),
    _SkyCardData(
      tone: _SkyCardTone.blush,
      when: 'Bu akşam · 21:47',
      glyph: _PlanetKind.venus,
      titlePrefix: 'Venüs, Nodlara ',
      titleItalic: 'kare',
      sub: 'Eski bir bağ çağırabilir. Cevap vermeden önce dinle.',
      affMeta: '♀ □ ☊ · 5 SLAYT',
    ),
    _SkyCardData(
      tone: _SkyCardTone.neutral,
      when: 'Yarın · 06:12',
      glyph: _PlanetKind.moon,
      titlePrefix: 'Ay, ',
      titleItalic: 'Başak\'a',
      titleSuffix: ' geçer',
      sub: 'Toparlan, topraklan. Detaylara ve düzene dön.',
      affMeta: '☽ → ♍ · 4 SLAYT',
    ),
    _SkyCardData(
      tone: _SkyCardTone.lavender,
      when: '22 Nisan · Sal',
      glyph: _PlanetKind.moon,
      titlePrefix: 'Yeni Ay ',
      titleItalic: 'Boğa\'da',
      sub: 'Niyet dile. Ağırdan al, köklendir. Tohum haftası.',
      affMeta: '6 SLAYT · AÇ',
    ),
    _SkyCardData(
      tone: _SkyCardTone.neutral,
      when: '29 Nisan · Sal',
      glyph: _PlanetKind.mercury,
      titlePrefix: 'Merkür, ',
      titleItalic: 'Boğa\'ya',
      titleSuffix: ' geçer',
      sub: 'Düşünce yavaşlar, sözler ağırlaşır. Kalıcı sohbetler.',
      affMeta: '☿ → ♉ · 4 SLAYT',
    ),
  ];

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final snapshot = ref.watch(homeV2SnapshotProvider).value;
    final live = snapshot?.skyCards ?? const <HomeV2SkyCard>[];
    final cards = live.isNotEmpty
        ? live.map(_fromLive).toList(growable: false)
        : _mockCards;
    return SizedBox(
      height: 250,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        physics: const BouncingScrollPhysics(),
        padding: const EdgeInsets.fromLTRB(24, 0, 24, 8),
        itemCount: cards.length,
        separatorBuilder: (_, _) => const SizedBox(width: 10),
        itemBuilder: (context, i) => _SkyCard(data: cards[i]),
      ),
    );
  }

  static _SkyCardData _fromLive(HomeV2SkyCard c) {
    return _SkyCardData(
      tone: switch (c.tone) {
        HomeV2SkyTone.now => _SkyCardTone.now,
        HomeV2SkyTone.blush => _SkyCardTone.blush,
        HomeV2SkyTone.lavender => _SkyCardTone.lavender,
        HomeV2SkyTone.neutral => _SkyCardTone.neutral,
      },
      when: c.when,
      glyph: switch (c.planet) {
        HomeV2Planet.sun => _PlanetKind.sun,
        HomeV2Planet.moon => _PlanetKind.moon,
        HomeV2Planet.mercury => _PlanetKind.mercury,
        HomeV2Planet.venus => _PlanetKind.venus,
        HomeV2Planet.mars => _PlanetKind.mars,
        HomeV2Planet.saturn => _PlanetKind.saturn,
        HomeV2Planet.unknown => _PlanetKind.moon,
      },
      titlePrefix: c.title,
      titleItalic: c.italic,
      titleSuffix: c.suffix,
      sub: c.sub,
      affMeta: c.meta,
    );
  }
}

enum _SkyCardTone { now, neutral, blush, lavender }

class _SkyCardData {
  const _SkyCardData({
    required this.tone,
    required this.when,
    required this.glyph,
    required this.titlePrefix,
    this.titleItalic,
    this.titleSuffix,
    required this.sub,
    required this.affMeta,
  });

  final _SkyCardTone tone;
  final String when;
  final _PlanetKind glyph;
  final String titlePrefix;
  final String? titleItalic;
  final String? titleSuffix;
  final String sub;
  final String affMeta;
}

class _SkyCard extends StatelessWidget {
  const _SkyCard({required this.data});
  final _SkyCardData data;

  @override
  Widget build(BuildContext context) {
    final isNow = data.tone == _SkyCardTone.now;
    final bg = isNow ? _HomeV2Palette.cream : _HomeV2Palette.white;
    final borderColor = isNow
        ? _HomeV2Palette.lime.withValues(alpha: 0.4)
        : _HomeV2Palette.hairline;

    Color glyphColor() {
      switch (data.tone) {
        case _SkyCardTone.now:
          return _HomeV2Palette.ink;
        case _SkyCardTone.lavender:
          return _HomeV2Palette.lavenderDeep;
        case _SkyCardTone.blush:
          return _HomeV2Palette.blushDeep;
        case _SkyCardTone.neutral:
          return _HomeV2Palette.silver;
      }
    }

    return InkWell(
      onTap: () {
        // TODO: 6 slaytlık detay overlay açılacak (sonraki faz).
      },
      child: Stack(
        children: [
          Container(
            width: 176,
            decoration: BoxDecoration(
              color: bg,
              border: Border.all(color: borderColor, width: 0.5),
              borderRadius: BorderRadius.circular(2),
            ),
            padding: const EdgeInsets.fromLTRB(16, 16, 16, 14),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _SkyCardWhen(label: data.when, isNow: isNow),
                    const SizedBox(height: 16),
                    SizedBox(
                      width: 32,
                      height: 32,
                      child: CustomPaint(
                        painter: _SkyGlyphPainter(
                          kind: data.glyph,
                          color: glyphColor(),
                        ),
                      ),
                    ),
                    const SizedBox(height: 16),
                    _SkyCardTitle(data: data),
                    const SizedBox(height: 6),
                    Text(
                      data.sub,
                      maxLines: 4,
                      overflow: TextOverflow.ellipsis,
                      style: GoogleFonts.inter(
                        textStyle: const TextStyle(
                          fontSize: 10,
                          height: 1.4,
                          letterSpacing: -0.1,
                          color: _HomeV2Palette.mist,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 10),
                _SkyCardAffordance(meta: data.affMeta, isNow: isNow),
              ],
            ),
          ),
          if (isNow)
            Positioned(
              top: 0,
              left: 16,
              child: Container(
                width: 24,
                height: 2,
                decoration: const BoxDecoration(
                  color: _HomeV2Palette.lime,
                  borderRadius: BorderRadius.vertical(
                    bottom: Radius.circular(1),
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }
}

class _SkyCardWhen extends StatelessWidget {
  const _SkyCardWhen({required this.label, required this.isNow});
  final String label;
  final bool isNow;

  @override
  Widget build(BuildContext context) {
    final text = Text(
      label.toUpperCase(),
      style: GoogleFonts.inter(
        textStyle: TextStyle(
          fontSize: 8,
          letterSpacing: 1.8,
          color: isNow ? _HomeV2Palette.limeText : _HomeV2Palette.mist,
          fontWeight: FontWeight.w500,
        ),
      ),
    );
    if (!isNow) return text;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: _HomeV2Palette.lime,
        borderRadius: BorderRadius.circular(3),
      ),
      child: text,
    );
  }
}

class _SkyCardTitle extends StatelessWidget {
  const _SkyCardTitle({required this.data});
  final _SkyCardData data;

  @override
  Widget build(BuildContext context) {
    final body = GoogleFonts.inter(
      textStyle: const TextStyle(
        fontSize: 14,
        height: 1.3,
        letterSpacing: -0.25,
        color: _HomeV2Palette.ink,
        fontWeight: FontWeight.w500,
      ),
    );
    final italic = GoogleFonts.fraunces(
      textStyle: const TextStyle(
        fontSize: 14,
        height: 1.3,
        letterSpacing: -0.25,
        color: _HomeV2Palette.ink,
        fontStyle: FontStyle.italic,
        fontWeight: FontWeight.w400,
      ),
    );

    return Text.rich(
      TextSpan(
        style: body,
        children: [
          TextSpan(text: data.titlePrefix),
          if (data.titleItalic != null)
            TextSpan(text: data.titleItalic, style: italic),
          if (data.titleSuffix != null) TextSpan(text: data.titleSuffix),
        ],
      ),
      maxLines: 3,
      overflow: TextOverflow.ellipsis,
    );
  }
}

class _SkyCardAffordance extends StatelessWidget {
  const _SkyCardAffordance({required this.meta, required this.isNow});
  final String meta;
  final bool isNow;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.only(top: 10),
      decoration: const BoxDecoration(
        border: Border(
          top: BorderSide(color: _HomeV2Palette.hairline, width: 0.5),
        ),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          Expanded(
            child: Text(
              meta,
              overflow: TextOverflow.ellipsis,
              style: GoogleFonts.inter(
                textStyle: TextStyle(
                  fontSize: 9,
                  letterSpacing: 1.4,
                  color: isNow
                      ? _HomeV2Palette.limeText
                      : _HomeV2Palette.silver,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
          ),
          const SizedBox(width: 8),
          Container(
            width: 22,
            height: 22,
            decoration: BoxDecoration(
              color: isNow ? _HomeV2Palette.lime : _HomeV2Palette.cream,
              shape: BoxShape.circle,
              border: isNow
                  ? null
                  : Border.all(
                      color: _HomeV2Palette.hairline,
                      width: 0.5,
                    ),
            ),
            child: const Icon(
              Icons.arrow_forward,
              size: 11,
              color: _HomeV2Palette.ink,
            ),
          ),
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────
// ASKEW BANNER — "22.04 Yeni Ay Boğa'da" diyagonal lime şeritli
// ─────────────────────────────────────────────────────────────

class _AskewBanner extends ConsumerWidget {
  const _AskewBanner();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Öncelik: /sky/now hero → narrative periodCard → mock
    final sky = ref.watch(homeV2SkyNowProvider).value;
    final skyHero = (sky?.items.isNotEmpty ?? false) ? sky!.items.first : null;
    final skyBanner = homeV2AskewFromSkyHero(skyHero);
    final snapshot = ref.watch(homeV2SnapshotProvider).value;
    final live = skyBanner ?? snapshot?.askewBanner;
    final eyebrow = live?.eyebrow ?? '5 GÜN SONRA · BÜYÜK GEÇİŞ';
    final date = live?.date ?? '22.04';
    final name = live?.name ?? 'Yeni Ay Boğa\'da';
    final sub = live?.sub ??
        'Yılın en sakin niyet kapısı. Boğa\'da yeni ay — '
            'köklendir, beden konuşsun.';
    return ClipRect(
      child: Stack(
        children: [
          Positioned.fill(
            child: CustomPaint(painter: _AskewBackgroundPainter()),
          ),
          Positioned(
            top: 0,
            bottom: 0,
            left: -40,
            right: -40,
            child: Align(
              alignment: Alignment.center,
              child: Transform.rotate(
                angle: -0.0436,
                child: Container(
                  height: 38,
                  color: _HomeV2Palette.lime.withValues(alpha: 0.95),
                ),
              ),
            ),
          ),
          Padding(
            padding: const EdgeInsets.fromLTRB(28, 36, 28, 38),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  eyebrow,
                  style: GoogleFonts.inter(
                    textStyle: const TextStyle(
                      fontSize: 8,
                      letterSpacing: 2.4,
                      color: Color(0x80FFFFFF),
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  date,
                  style: GoogleFonts.fraunces(
                    textStyle: const TextStyle(
                      fontSize: 54,
                      fontStyle: FontStyle.italic,
                      fontWeight: FontWeight.w300,
                      letterSpacing: -1.6,
                      height: 0.95,
                      color: Colors.white,
                    ),
                  ),
                ),
                const SizedBox(height: 2),
                Transform.rotate(
                  angle: -0.0262,
                  child: Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 10,
                      vertical: 4,
                    ),
                    color: _HomeV2Palette.lime,
                    child: Text(
                      name,
                      style: GoogleFonts.inter(
                        textStyle: const TextStyle(
                          fontSize: 22,
                          fontWeight: FontWeight.w500,
                          letterSpacing: -0.3,
                          color: _HomeV2Palette.limeText,
                        ),
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 12),
                ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 260),
                  child: Text(
                    sub,
                    style: GoogleFonts.inter(
                      textStyle: const TextStyle(
                        fontSize: 13,
                        height: 1.5,
                        letterSpacing: -0.1,
                        color: Color(0xB3FFFFFF),
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                InkWell(
                  onTap: () {
                    // TODO: Hatırlatıcı oluşturma.
                  },
                  child: Text(
                    'HATIRLAT  →',
                    style: GoogleFonts.inter(
                      textStyle: const TextStyle(
                        fontSize: 10,
                        letterSpacing: 2.5,
                        color: Colors.white,
                        fontWeight: FontWeight.w400,
                        decoration: TextDecoration.underline,
                        decorationColor: _HomeV2Palette.lime,
                        decorationThickness: 0.5,
                      ),
                    ),
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

/// Ink zemin + eğik hafif lime çizgili stripe deseni (HTML ::before).
class _AskewBackgroundPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    canvas.drawRect(
      Rect.fromLTWH(0, 0, size.width, size.height),
      Paint()..color = _HomeV2Palette.ink,
    );

    // -6° eğimde 45px aralıklı hafif lime çizgiler
    canvas.save();
    canvas.translate(size.width / 2, size.height / 2);
    canvas.rotate(-0.1047); // -6°
    final stripePaint = Paint()
      ..color = _HomeV2Palette.lime.withValues(alpha: 0.04)
      ..strokeWidth = 1;
    final diag = (size.width + size.height);
    for (double x = -diag; x < diag; x += 45) {
      canvas.drawLine(Offset(x, -diag), Offset(x, diag), stripePaint);
    }
    canvas.restore();
  }

  @override
  bool shouldRepaint(covariant CustomPainter old) => false;
}

// ─────────────────────────────────────────────────────────────
// YAKINDAKİLER — "Gökyüzü herkese aynı söylemiyor" + 6 arkadaş avatarı
// ─────────────────────────────────────────────────────────────

class _NearSection extends StatelessWidget {
  const _NearSection();

  @override
  Widget build(BuildContext context) {
    // Bond feature gate (P0-A cleanup): until partner-data infra ships,
    // this section would only render hardcoded mock friends, which is
    // unacceptable for production. Returning empty collapses the section
    // (parent Column tolerates SizedBox.shrink without spacing artifacts
    // because the surrounding sections have their own vertical padding).
    if (!kHomeBondFeatureEnabled) return const SizedBox.shrink();
    return Padding(
      padding: const EdgeInsets.fromLTRB(0, 8, 0, 44),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: const [
          _NearHead(),
          SizedBox(height: 28),
          _NearRail(),
        ],
      ),
    );
  }
}

class _NearHead extends StatelessWidget {
  const _NearHead();

  @override
  Widget build(BuildContext context) {
    final eyebrow = GoogleFonts.inter(
      textStyle: const TextStyle(
        fontSize: 8.5,
        letterSpacing: 2.4,
        color: _HomeV2Palette.silver,
        fontWeight: FontWeight.w400,
      ),
    );
    final titleBody = GoogleFonts.inter(
      textStyle: const TextStyle(
        fontSize: 22,
        fontWeight: FontWeight.w500,
        color: _HomeV2Palette.ink,
        letterSpacing: -0.4,
        height: 1.25,
      ),
    );
    final titleItalic = GoogleFonts.fraunces(
      textStyle: const TextStyle(
        fontSize: 22,
        fontWeight: FontWeight.w400,
        fontStyle: FontStyle.italic,
        color: _HomeV2Palette.ink,
        letterSpacing: -0.4,
        height: 1.25,
      ),
    );

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 28),
      child: Column(
        children: [
          Text('BUGÜN YAKININDA', style: eyebrow),
          const SizedBox(height: 10),
          Text.rich(
            TextSpan(
              style: titleBody,
              children: [
                const TextSpan(text: 'Gökyüzü herkese '),
                TextSpan(text: 'aynı', style: titleItalic),
                const TextSpan(text: ' söylemiyor.'),
              ],
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}

enum _FriendTone { me, lime, lavender, blush, plain }

class _FriendAviData {
  const _FriendAviData({
    required this.name,
    required this.meta,
    required this.initial,
    required this.tone,
  });
  final String name;
  final String meta;
  final String initial;
  final _FriendTone tone;
}

class _NearRail extends StatelessWidget {
  const _NearRail();

  // Mock friend data removed in P0-A cleanup. Once the Bond feature ships
  // a `bondPartnersProvider`, the rail will be populated from that live
  // source. Until then `_NearSection` is gated behind
  // `kHomeBondFeatureEnabled = false` and never renders.
  static const _friends = <_FriendAviData>[];

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 90,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        physics: const BouncingScrollPhysics(),
        padding: const EdgeInsets.symmetric(horizontal: 28),
        itemCount: _friends.length,
        separatorBuilder: (_, _) => const SizedBox(width: 16),
        itemBuilder: (context, i) => _FriendAvatar(data: _friends[i]),
      ),
    );
  }
}

class _FriendAvatar extends StatelessWidget {
  const _FriendAvatar({required this.data});
  final _FriendAviData data;

  @override
  Widget build(BuildContext context) {
    late Color bg;
    late Color border;
    late Color letter;
    late bool dashedBorder;
    late bool useBodyFont;

    switch (data.tone) {
      case _FriendTone.me:
        bg = Colors.transparent;
        border = _HomeV2Palette.cloud;
        letter = _HomeV2Palette.mist;
        dashedBorder = true;
        useBodyFont = true;
        break;
      case _FriendTone.lime:
        bg = _HomeV2Palette.lime.withValues(alpha: 0.18);
        border = _HomeV2Palette.lime.withValues(alpha: 0.5);
        letter = _HomeV2Palette.limeText;
        dashedBorder = false;
        useBodyFont = false;
        break;
      case _FriendTone.lavender:
        bg = _HomeV2Palette.lavenderBg;
        border = _HomeV2Palette.lavender.withValues(alpha: 0.28);
        letter = _HomeV2Palette.lavenderDeep;
        dashedBorder = false;
        useBodyFont = false;
        break;
      case _FriendTone.blush:
        bg = _HomeV2Palette.blushBg;
        border = _HomeV2Palette.blush.withValues(alpha: 0.35);
        letter = _HomeV2Palette.blushDeep;
        dashedBorder = false;
        useBodyFont = false;
        break;
      case _FriendTone.plain:
        bg = const Color(0xFFF5F5F8);
        border = _HomeV2Palette.hairline;
        letter = _HomeV2Palette.fog;
        dashedBorder = false;
        useBodyFont = false;
        break;
    }

    final letterStyle = useBodyFont
        ? GoogleFonts.inter(
            textStyle: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w300,
              color: letter,
              height: 1,
            ),
          )
        : GoogleFonts.fraunces(
            textStyle: TextStyle(
              fontSize: 17,
              fontStyle: FontStyle.italic,
              fontWeight: FontWeight.w400,
              color: letter,
              height: 1,
            ),
          );

    return SizedBox(
      width: 62,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          SizedBox(
            width: 52,
            height: 52,
            child: CustomPaint(
              painter: _FriendAviPainter(
                bg: bg,
                border: border,
                dashed: dashedBorder,
              ),
              child: Center(child: Text(data.initial, style: letterStyle)),
            ),
          ),
          const SizedBox(height: 8),
          Text(
            data.name,
            style: GoogleFonts.inter(
              textStyle: const TextStyle(
                fontSize: 10,
                color: _HomeV2Palette.ink,
                letterSpacing: -0.1,
                fontWeight: FontWeight.w400,
              ),
            ),
          ),
          const SizedBox(height: 2),
          Text(
            data.meta,
            style: GoogleFonts.inter(
              textStyle: const TextStyle(
                fontSize: 7.5,
                color: _HomeV2Palette.silver,
                letterSpacing: 1.4,
                fontWeight: FontWeight.w400,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _FriendAviPainter extends CustomPainter {
  _FriendAviPainter({
    required this.bg,
    required this.border,
    required this.dashed,
  });

  final Color bg;
  final Color border;
  final bool dashed;

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width / 2 - 0.5;
    if (bg.a > 0) {
      canvas.drawCircle(center, radius, Paint()..color = bg);
    }
    final stroke = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 0.8
      ..color = border;
    if (!dashed) {
      canvas.drawCircle(center, radius, stroke);
      return;
    }
    // dashed
    final circumference = 2 * 3.1415926535 * radius;
    const dashLen = 3.0;
    const gapLen = 3.0;
    final dashes = (circumference / (dashLen + gapLen)).floor();
    final step = 2 * 3.1415926535 / dashes;
    final dashAngle = (dashLen / circumference) * 2 * 3.1415926535;
    final rect = Rect.fromCircle(center: center, radius: radius);
    for (var i = 0; i < dashes; i++) {
      final path = Path()..addArc(rect, i * step, dashAngle);
      canvas.drawPath(path, stroke);
    }
  }

  @override
  bool shouldRepaint(covariant _FriendAviPainter old) =>
      old.bg != bg || old.border != border || old.dashed != dashed;
}

// ─────────────────────────────────────────────────────────────
// FEED — "Gökyüzü onlara ne söyledi?" + 4 arkadaş post'u
// ─────────────────────────────────────────────────────────────

class _FeedSection extends StatelessWidget {
  const _FeedSection();

  @override
  Widget build(BuildContext context) {
    // Bond feature gate (P0-A cleanup): the four `_FeedPost*` posts
    // below are hardcoded "friend transit" editorial mocks. They must
    // never reach production. Until live data exists, render nothing.
    if (!kHomeBondFeatureEnabled) return const SizedBox.shrink();
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: const [
        _FeedHead(),
        SizedBox(height: 28),
        Padding(
          padding: EdgeInsets.fromLTRB(28, 0, 28, 48),
          child: Column(
            children: [
              _FeedPostMira(),
              SizedBox(height: 34),
              _FeedPostEla(),
              SizedBox(height: 34),
              _FeedPostBurak(),
              SizedBox(height: 34),
              _FeedPostDeniz(),
            ],
          ),
        ),
      ],
    );
  }
}

class _FeedHead extends StatelessWidget {
  const _FeedHead();

  @override
  Widget build(BuildContext context) {
    final eyebrow = GoogleFonts.inter(
      textStyle: const TextStyle(
        fontSize: 8.5,
        letterSpacing: 2.4,
        color: _HomeV2Palette.silver,
        fontWeight: FontWeight.w400,
      ),
    );
    final titleBody = GoogleFonts.inter(
      textStyle: const TextStyle(
        fontSize: 22,
        fontWeight: FontWeight.w500,
        color: _HomeV2Palette.ink,
        letterSpacing: -0.4,
        height: 1.2,
      ),
    );
    final titleItalic = GoogleFonts.fraunces(
      textStyle: const TextStyle(
        fontSize: 22,
        fontWeight: FontWeight.w400,
        fontStyle: FontStyle.italic,
        color: _HomeV2Palette.ink,
        letterSpacing: -0.4,
        height: 1.2,
      ),
    );
    final sub = GoogleFonts.inter(
      textStyle: const TextStyle(
        fontSize: 11.5,
        color: _HomeV2Palette.mist,
        height: 1.5,
        fontWeight: FontWeight.w400,
      ),
    );

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 28),
      child: Column(
        children: [
          Text('BUGÜN YAKINLARINDA', style: eyebrow),
          const SizedBox(height: 10),
          Text.rich(
            TextSpan(
              style: titleBody,
              children: [
                const TextSpan(text: 'Gökyüzü onlara ne '),
                TextSpan(text: 'söyledi', style: titleItalic),
                const TextSpan(text: '?'),
              ],
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 6),
          ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 280),
            child: Text(
              'Herkesin bugünü farklı bir pencereden açılıyor.',
              textAlign: TextAlign.center,
              style: sub,
            ),
          ),
        ],
      ),
    );
  }
}

// ── Shared post shell ─────────────────────────────────────

class _FeedPost extends StatelessWidget {
  const _FeedPost({
    required this.meta,
    required this.body,
    required this.actionLeft,
    required this.actionRight,
    required this.deeperText,
    required this.deeperCount,
  });

  final List<InlineSpan> meta;
  final InlineSpan body;
  final _FeedAction actionLeft;
  final _FeedAction actionRight;
  final String deeperText;
  final String deeperCount;

  @override
  Widget build(BuildContext context) {
    final bodyStyle = GoogleFonts.inter(
      textStyle: const TextStyle(
        fontSize: 17,
        height: 1.45,
        letterSpacing: -0.3,
        color: _HomeV2Palette.ink,
        fontWeight: FontWeight.w400,
      ),
    );

    return Column(
      children: [
        // meta row
        Wrap(
          alignment: WrapAlignment.center,
          crossAxisAlignment: WrapCrossAlignment.center,
          spacing: 8,
          runSpacing: 4,
          children: meta.map<Widget>(_metaSpanToWidget).toList(),
        ),
        const SizedBox(height: 14),
        ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 310),
          child: Text.rich(
            TextSpan(style: bodyStyle, children: [body]),
            textAlign: TextAlign.center,
          ),
        ),
        const SizedBox(height: 16),
        // actions
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            _FeedActionChip(action: actionLeft),
            const SizedBox(width: 22),
            _FeedActionChip(action: actionRight),
          ],
        ),
        const SizedBox(height: 14),
        _PostDeeper(text: deeperText, count: deeperCount),
      ],
    );
  }

  static Widget _metaSpanToWidget(InlineSpan span) {
    if (span is WidgetSpan) return span.child;
    return Text.rich(span);
  }
}

enum _MetaTone { author, neutral, lime, blush, lavender, stone }

class _FeedMetaChip extends StatelessWidget {
  const _FeedMetaChip({required this.label, required this.tone});
  final String label;
  final _MetaTone tone;

  @override
  Widget build(BuildContext context) {
    Color textColor;
    Color? bg;
    switch (tone) {
      case _MetaTone.author:
        textColor = _HomeV2Palette.ink;
        bg = null;
        break;
      case _MetaTone.neutral:
        textColor = _HomeV2Palette.mist;
        bg = null;
        break;
      case _MetaTone.lime:
        textColor = _HomeV2Palette.limeText;
        bg = _HomeV2Palette.lime;
        break;
      case _MetaTone.blush:
        textColor = _HomeV2Palette.blushDeep;
        bg = _HomeV2Palette.blushBg;
        break;
      case _MetaTone.lavender:
        textColor = _HomeV2Palette.lavenderDeep;
        bg = _HomeV2Palette.lavenderBg;
        break;
      case _MetaTone.stone:
        textColor = _HomeV2Palette.fog;
        bg = const Color(0xFFF0EDE6);
        break;
    }
    final child = Text(
      label.toUpperCase(),
      style: GoogleFonts.inter(
        textStyle: TextStyle(
          fontSize: 8.5,
          letterSpacing: 1.8,
          color: textColor,
          fontWeight: tone == _MetaTone.author
              ? FontWeight.w500
              : FontWeight.w400,
        ),
      ),
    );
    if (bg == null) return child;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(3),
      ),
      child: child,
    );
  }
}

class _FeedMetaDot extends StatelessWidget {
  const _FeedMetaDot();
  @override
  Widget build(BuildContext context) {
    return Container(
      width: 3,
      height: 3,
      decoration: const BoxDecoration(
        color: _HomeV2Palette.cloud,
        shape: BoxShape.circle,
      ),
    );
  }
}

class _FeedAction {
  const _FeedAction({
    required this.icon,
    required this.label,
    required this.color,
  });
  final IconData icon;
  final String label;
  final Color color;
}

class _FeedActionChip extends StatelessWidget {
  const _FeedActionChip({required this.action});
  final _FeedAction action;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(action.icon, size: 13, color: action.color),
        const SizedBox(width: 5),
        Text(
          action.label,
          style: GoogleFonts.inter(
            textStyle: TextStyle(
              fontSize: 10,
              letterSpacing: 0.3,
              color: action.color,
              fontWeight: FontWeight.w400,
            ),
          ),
        ),
      ],
    );
  }
}

class _PostDeeper extends StatelessWidget {
  const _PostDeeper({required this.text, required this.count});
  final String text;
  final String count;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: () {
        // TODO: Slide overlay açılacak.
      },
      child: Container(
        padding: const EdgeInsets.only(top: 10),
        decoration: const BoxDecoration(
          border: Border(
            top: BorderSide(
              color: _HomeV2Palette.hairline,
              width: 0.5,
              style: BorderStyle.solid,
            ),
          ),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text.rich(
              TextSpan(
                style: GoogleFonts.inter(
                  textStyle: const TextStyle(
                    fontSize: 9.5,
                    letterSpacing: 1.6,
                    color: _HomeV2Palette.mist,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                children: [
                  TextSpan(text: '${text.toUpperCase()} · '),
                  TextSpan(
                    text: count.toUpperCase(),
                    style: const TextStyle(color: _HomeV2Palette.ink),
                  ),
                ],
              ),
            ),
            const SizedBox(width: 8),
            Container(
              width: 22,
              height: 22,
              decoration: BoxDecoration(
                color: _HomeV2Palette.white,
                shape: BoxShape.circle,
                border: Border.all(
                  color: _HomeV2Palette.cloud,
                  width: 0.5,
                ),
              ),
              child: const Icon(
                Icons.arrow_forward,
                size: 11,
                color: _HomeV2Palette.ink,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ── Individual posts ─────────────────────────────────────
//
// All four `_FeedPost*` widgets previously contained hardcoded "friend
// transit" editorial copy (Mira / Ela / Burak / Deniz with fictional
// chart data). Removed in P0-A cleanup so no mock copy lives in source.
// `_FeedSection` is gated behind `kHomeBondFeatureEnabled` and never
// renders these placeholders, but they remain as named widgets so call
// sites in `_FeedSection` continue to compile until the section is
// rewritten with a live `bondFeedProvider`.

class _FeedPostMira extends StatelessWidget {
  const _FeedPostMira();
  @override
  Widget build(BuildContext context) => const SizedBox.shrink();
}

class _FeedPostEla extends StatelessWidget {
  const _FeedPostEla();
  @override
  Widget build(BuildContext context) => const SizedBox.shrink();
}

class _FeedPostBurak extends StatelessWidget {
  const _FeedPostBurak();
  @override
  Widget build(BuildContext context) => const SizedBox.shrink();
}

class _FeedPostDeniz extends StatelessWidget {
  const _FeedPostDeniz();
  @override
  Widget build(BuildContext context) => const SizedBox.shrink();
}

// ─────────────────────────────────────────────────────────────
// CHART WHEEL — "Gezegenler şu an böyle duruyor" dönen natal chart
// ─────────────────────────────────────────────────────────────

class _ChartWheelSection extends StatelessWidget {
  const _ChartWheelSection();

  @override
  Widget build(BuildContext context) {
    final eyebrow = GoogleFonts.inter(
      textStyle: const TextStyle(
        fontSize: 8.5,
        letterSpacing: 2.4,
        color: _HomeV2Palette.silver,
        fontWeight: FontWeight.w400,
      ),
    );
    final titleBody = GoogleFonts.inter(
      textStyle: const TextStyle(
        fontSize: 17,
        fontWeight: FontWeight.w500,
        color: _HomeV2Palette.ink,
        letterSpacing: -0.3,
        height: 1.3,
      ),
    );
    final titleItalic = GoogleFonts.fraunces(
      textStyle: const TextStyle(
        fontSize: 17,
        fontWeight: FontWeight.w400,
        fontStyle: FontStyle.italic,
        color: _HomeV2Palette.ink,
        letterSpacing: -0.3,
        height: 1.3,
      ),
    );
    final meta = GoogleFonts.inter(
      textStyle: const TextStyle(
        fontSize: 9,
        letterSpacing: 1.2,
        color: _HomeV2Palette.mist,
        fontWeight: FontWeight.w400,
      ),
    );
    final metaStrong = GoogleFonts.inter(
      textStyle: const TextStyle(
        fontSize: 9,
        letterSpacing: 1.2,
        color: _HomeV2Palette.ink,
        fontWeight: FontWeight.w500,
      ),
    );

    return Container(
      color: _HomeV2Palette.cream,
      padding: const EdgeInsets.fromLTRB(28, 36, 28, 44),
      foregroundDecoration: const BoxDecoration(
        border: Border(
          top: BorderSide(color: _HomeV2Palette.hairline, width: 0.5),
          bottom: BorderSide(color: _HomeV2Palette.hairline, width: 0.5),
        ),
      ),
      child: Column(
        children: [
          Text('GÖKYÜZÜ · CANLI', style: eyebrow),
          const SizedBox(height: 6),
          Text.rich(
            TextSpan(
              style: titleBody,
              children: [
                const TextSpan(text: 'Gezegenler şu an '),
                TextSpan(text: 'böyle', style: titleItalic),
                const TextSpan(text: ' duruyor'),
              ],
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 22),
          const _ChartWheel(),
          const SizedBox(height: 20),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              Text.rich(
                TextSpan(
                  style: meta,
                  children: [
                    TextSpan(text: '9 ', style: metaStrong),
                    const TextSpan(text: 'GEZEGEN'),
                  ],
                ),
              ),
              Text('   ·   ', style: meta),
              Text.rich(
                TextSpan(
                  style: meta,
                  children: [
                    TextSpan(text: '3 ', style: metaStrong),
                    const TextSpan(text: 'AKTİF ASPECT'),
                  ],
                ),
              ),
              Text('   ·   ', style: meta),
              Text('GÖBEKLİ TEPE SAAT', style: meta),
            ],
          ),
        ],
      ),
    );
  }
}

class _ChartWheel extends ConsumerStatefulWidget {
  const _ChartWheel();

  @override
  ConsumerState<_ChartWheel> createState() => _ChartWheelState();
}

class _ChartWheelState extends ConsumerState<_ChartWheel>
    with SingleTickerProviderStateMixin {
  late final AnimationController _spin;

  @override
  void initState() {
    super.initState();
    _spin = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 180),
    )..repeat();
  }

  @override
  void dispose() {
    _spin.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final natal = ref.watch(homeV2NatalProvider).value;
    final placements = natal != null
        ? _placementsFromNatal(natal)
        : _mockPlanetPlacements;
    final isLive = natal != null;

    return SizedBox(
      width: 220,
      height: 220,
      child: Stack(
        alignment: Alignment.center,
        children: [
          AnimatedBuilder(
            animation: _spin,
            builder: (context, _) {
              return Transform.rotate(
                angle: _spin.value * 2 * 3.1415926535,
                child: SizedBox(
                  width: 220,
                  height: 220,
                  child: CustomPaint(
                    painter: _ChartWheelPainter(
                      planets: placements,
                      ascendantLon: natal?.angles.ascendantLon,
                    ),
                  ),
                ),
              );
            },
          ),
          Transform.rotate(
            angle: -0.0698,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              color: _HomeV2Palette.ink,
              child: Text.rich(
                TextSpan(
                  style: GoogleFonts.inter(
                    textStyle: const TextStyle(
                      fontSize: 9.5,
                      letterSpacing: 2,
                      color: Colors.white,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  children: [
                    TextSpan(text: isLive ? 'NATAL · ' : '17 NİS · '),
                    TextSpan(
                      text: isLive ? 'SAHRA' : 'CANLI',
                      style: const TextStyle(color: _HomeV2Palette.lime),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

enum _PlanetKind { sun, moon, mercury, venus, mars, saturn }

/// Chart wheel'de bir gezegenin nasıl çizileceğini tarif eder.
class _PlanetPlacement {
  const _PlanetPlacement({
    required this.kind,
    required this.lonDeg,
    required this.discRadius,
    required this.bg,
    required this.fg,
  });

  final _PlanetKind kind;
  final double lonDeg; // 0..360 — Aries 0° = 12 o'clock, clockwise
  final double discRadius; // SVG 220 viewport unit (painter _k scale'er)
  final Color bg;
  final Color fg;
}

/// Natal verisi gelmediğinde kullanılan örnek yerleşim — HTML mock'u ile
/// uyumlu. Longitude değerleri, mock'taki hardcoded (x,y) koordinatlarını
/// inner-ring radius 82 üzerinde yeniden üretir.
const List<_PlanetPlacement> _mockPlanetPlacements = [
  _PlanetPlacement(
    kind: _PlanetKind.moon,
    lonDeg: 134,
    discRadius: 9,
    bg: _HomeV2Palette.lime,
    fg: _HomeV2Palette.limeText,
  ),
  _PlanetPlacement(
    kind: _PlanetKind.sun,
    lonDeg: 0,
    discRadius: 7,
    bg: _HomeV2Palette.ink,
    fg: Colors.white,
  ),
  _PlanetPlacement(
    kind: _PlanetKind.venus,
    lonDeg: 28,
    discRadius: 6.5,
    bg: _HomeV2Palette.lavender,
    fg: Colors.white,
  ),
  _PlanetPlacement(
    kind: _PlanetKind.mercury,
    lonDeg: 12,
    discRadius: 6,
    bg: _HomeV2Palette.blush,
    fg: _HomeV2Palette.ink,
  ),
  _PlanetPlacement(
    kind: _PlanetKind.mars,
    lonDeg: 70,
    discRadius: 6.5,
    bg: _HomeV2Palette.ink,
    fg: Colors.white,
  ),
  _PlanetPlacement(
    kind: _PlanetKind.saturn,
    lonDeg: 320,
    discRadius: 6.5,
    bg: _HomeV2Palette.ink,
    fg: Colors.white,
  ),
];

const Map<String, _PlanetKind> _planetKindByName = {
  'Sun': _PlanetKind.sun,
  'Moon': _PlanetKind.moon,
  'Mercury': _PlanetKind.mercury,
  'Venus': _PlanetKind.venus,
  'Mars': _PlanetKind.mars,
  'Saturn': _PlanetKind.saturn,
};

/// Sahra'nın natal haritasını chart wheel'in beklediği yerleşim listesine
/// çevirir. Sadece 6 ana gezegen (diğerleri tasarımı kalabalıklaştırır).
List<_PlanetPlacement> _placementsFromNatal(HomeV2NatalSnapshot natal) {
  final result = <_PlanetPlacement>[];
  for (final entry in _planetKindByName.entries) {
    final p = natal.findPlanet(entry.key);
    if (p == null) continue;
    final kind = entry.value;
    result.add(
      _PlanetPlacement(
        kind: kind,
        lonDeg: p.longitude,
        discRadius: kind == _PlanetKind.moon ? 9 : 6.5,
        bg: _planetBg(kind),
        fg: _planetFg(kind),
      ),
    );
  }
  return result;
}

Color _planetBg(_PlanetKind kind) {
  switch (kind) {
    case _PlanetKind.moon:
      return _HomeV2Palette.lime;
    case _PlanetKind.venus:
      return _HomeV2Palette.lavender;
    case _PlanetKind.mercury:
      return _HomeV2Palette.blush;
    case _PlanetKind.sun:
    case _PlanetKind.mars:
    case _PlanetKind.saturn:
      return _HomeV2Palette.ink;
  }
}

Color _planetFg(_PlanetKind kind) {
  switch (kind) {
    case _PlanetKind.moon:
      return _HomeV2Palette.limeText;
    case _PlanetKind.mercury:
      return _HomeV2Palette.ink;
    case _PlanetKind.sun:
    case _PlanetKind.venus:
    case _PlanetKind.mars:
    case _PlanetKind.saturn:
      return Colors.white;
  }
}

enum _ZodiacSign {
  aries,
  taurus,
  gemini,
  cancer,
  leo,
  virgo,
  libra,
  scorpio,
  sagittarius,
  capricorn,
  aquarius,
  pisces,
}

class _ChartWheelPainter extends CustomPainter {
  const _ChartWheelPainter({required this.planets, this.ascendantLon});

  final List<_PlanetPlacement> planets;
  final double? ascendantLon;

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    // HTML viewBox 220; oranlar korunuyor
    double k(double v) => v / 220 * size.width;

    final ring = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1
      ..color = _HomeV2Palette.ink;
    canvas.drawCircle(center, k(100), ring);

    _drawDashedCircle(
      canvas,
      center,
      k(68),
      _HomeV2Palette.ink,
      dashLength: 2,
      gapLength: 4,
      strokeWidth: 0.5,
    );

    final innerRing = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 0.5
      ..color = _HomeV2Palette.ink;
    canvas.drawCircle(center, k(36), innerRing);

    // 12 ev çizgisi — HTML koordinatları (oran üzerinden)
    final spokes = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 0.4
      ..color = _HomeV2Palette.ink.withValues(alpha: 0.4);
    const segs = <List<double>>[
      [110, 10, 110, 42],
      [162, 38, 143, 62],
      [198, 75, 166, 90],
      [210, 110, 178, 110],
      [198, 145, 166, 130],
      [162, 182, 143, 158],
      [110, 210, 110, 178],
      [58, 182, 77, 158],
      [22, 145, 54, 130],
      [10, 110, 42, 110],
      [22, 75, 54, 90],
      [58, 38, 77, 62],
    ];
    for (final s in segs) {
      canvas.drawLine(Offset(k(s[0]), k(s[1])), Offset(k(s[2]), k(s[3])), spokes);
    }

    // Zodiac glyphs (outer ring) — her biri vektör path olarak çiziliyor.
    const zodiac = <List<dynamic>>[
      [_ZodiacSign.aries, 110, 26],
      [_ZodiacSign.taurus, 158, 46],
      [_ZodiacSign.gemini, 192, 80],
      [_ZodiacSign.cancer, 202, 115],
      [_ZodiacSign.leo, 192, 148],
      [_ZodiacSign.virgo, 158, 180],
      [_ZodiacSign.libra, 110, 200],
      [_ZodiacSign.scorpio, 58, 180],
      [_ZodiacSign.sagittarius, 24, 148],
      [_ZodiacSign.capricorn, 14, 115],
      [_ZodiacSign.aquarius, 24, 80],
      [_ZodiacSign.pisces, 58, 46],
    ];
    for (final z in zodiac) {
      _drawZodiacGlyph(
        canvas,
        center: Offset(k(z[1].toDouble()), k(z[2].toDouble())),
        radius: k(7),
        color: const Color(0xFF555555),
        sign: z[0] as _ZodiacSign,
      );
    }

    // Gezegen yerleşimleri — longitude'a göre ring (r=82) üzerinde.
    // Aries 0° = 12 o'clock (üst), saat yönünde artar.
    const double planetRingLon = 82; // SVG unit
    for (final p in planets) {
      final angleRad = p.lonDeg * math.pi / 180;
      final cx = 110 + planetRingLon * math.sin(angleRad);
      final cy = 110 - planetRingLon * math.cos(angleRad);
      _drawPlanet(
        canvas,
        center: Offset(k(cx), k(cy)),
        radius: k(p.discRadius),
        bg: p.bg,
        fg: p.fg,
        kind: p.kind,
      );
    }

    // Ascendant işareti — dış halkada küçük üçgen + "AC" metni.
    if (ascendantLon != null) {
      final angleRad = ascendantLon! * math.pi / 180;
      const double r = 105;
      final tipX = 110 + r * math.sin(angleRad);
      final tipY = 110 - r * math.cos(angleRad);
      final acPaint = Paint()..color = _HomeV2Palette.lime;
      final path = Path()
        ..moveTo(k(tipX), k(tipY))
        ..lineTo(
          k(tipX - 3 * math.cos(angleRad)),
          k(tipY - 3 * math.sin(angleRad)),
        )
        ..lineTo(
          k(tipX + 3 * math.cos(angleRad)),
          k(tipY + 3 * math.sin(angleRad)),
        )
        ..close();
      canvas.drawPath(path, acPaint);
    }

    // Center sparkle (lime)
    _drawSparkle(
      canvas,
      offset: Offset(k(110), k(110)),
      size: k(10),
      color: _HomeV2Palette.lime.withValues(alpha: 0.8),
    );
  }

  void _drawPlanet(
    Canvas canvas, {
    required Offset center,
    required double radius,
    required Color bg,
    required Color fg,
    required _PlanetKind kind,
  }) {
    canvas.drawCircle(center, radius, Paint()..color = bg);
    final stroke = Paint()
      ..color = fg
      ..style = PaintingStyle.stroke
      ..strokeWidth = radius * 0.18
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;
    final fill = Paint()..color = fg;

    canvas.save();
    canvas.translate(center.dx, center.dy);

    switch (kind) {
      case _PlanetKind.sun:
        canvas.drawCircle(Offset.zero, radius * 0.28, fill);
        break;
      case _PlanetKind.moon:
        // Crescent — içi boşaltılmış çift daire
        final outer = Path()
          ..addOval(
            Rect.fromCircle(center: Offset.zero, radius: radius * 0.65),
          );
        final inner = Path()
          ..addOval(
            Rect.fromCircle(
              center: Offset(radius * 0.25, 0),
              radius: radius * 0.55,
            ),
          );
        final crescent = Path.combine(PathOperation.difference, outer, inner);
        canvas.drawPath(crescent, fill);
        break;
      case _PlanetKind.venus:
        canvas.drawCircle(
          Offset(0, -radius * 0.22),
          radius * 0.32,
          stroke,
        );
        canvas.drawLine(
          Offset(0, radius * 0.15),
          Offset(0, radius * 0.75),
          stroke,
        );
        canvas.drawLine(
          Offset(-radius * 0.28, radius * 0.45),
          Offset(radius * 0.28, radius * 0.45),
          stroke,
        );
        break;
      case _PlanetKind.mars:
        canvas.drawCircle(
          Offset(-radius * 0.12, radius * 0.12),
          radius * 0.38,
          stroke,
        );
        final tip = Offset(radius * 0.68, -radius * 0.68);
        canvas.drawLine(Offset(radius * 0.22, -radius * 0.22), tip, stroke);
        canvas.drawLine(tip, Offset(radius * 0.38, -radius * 0.68), stroke);
        canvas.drawLine(tip, Offset(radius * 0.68, -radius * 0.38), stroke);
        break;
      case _PlanetKind.mercury:
        // Üstte açık ay boynuzları, ortada daire, altında haç
        canvas.drawArc(
          Rect.fromCircle(
            center: Offset(0, -radius * 0.55),
            radius: radius * 0.3,
          ),
          0,
          3.1415926535,
          false,
          stroke,
        );
        canvas.drawCircle(Offset(0, -radius * 0.1), radius * 0.28, stroke);
        canvas.drawLine(
          Offset(0, radius * 0.2),
          Offset(0, radius * 0.75),
          stroke,
        );
        canvas.drawLine(
          Offset(-radius * 0.22, radius * 0.48),
          Offset(radius * 0.22, radius * 0.48),
          stroke,
        );
        break;
      case _PlanetKind.saturn:
        // h + alt kanca (scythe)
        // üst yatay çizgi
        canvas.drawLine(
          Offset(-radius * 0.5, -radius * 0.7),
          Offset(radius * 0.05, -radius * 0.7),
          stroke,
        );
        // dikey
        canvas.drawLine(
          Offset(-radius * 0.25, -radius * 0.7),
          Offset(-radius * 0.25, radius * 0.35),
          stroke,
        );
        // alt kanca
        canvas.drawArc(
          Rect.fromLTRB(
            -radius * 0.25,
            radius * 0.05,
            radius * 0.55,
            radius * 0.85,
          ),
          3.1415926535,
          1.7,
          false,
          stroke,
        );
        break;
    }
    canvas.restore();
  }

  void _drawZodiacGlyph(
    Canvas canvas, {
    required Offset center,
    required double radius,
    required Color color,
    required _ZodiacSign sign,
  }) {
    final stroke = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = radius * 0.14
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;

    canvas.save();
    canvas.translate(center.dx, center.dy);

    switch (sign) {
      case _ZodiacSign.aries:
        // İki kıvrık boynuz (V şeklinde)
        final p = Path()
          ..moveTo(-radius * 0.6, radius * 0.35)
          ..quadraticBezierTo(
            -radius * 0.6, -radius * 0.3,
            -radius * 0.2, -radius * 0.15,
          )
          ..lineTo(0, radius * 0.6)
          ..lineTo(radius * 0.2, -radius * 0.15)
          ..quadraticBezierTo(
            radius * 0.6, -radius * 0.3,
            radius * 0.6, radius * 0.35,
          );
        canvas.drawPath(p, stroke);
        break;
      case _ZodiacSign.taurus:
        // Daire + üstünde hilal
        canvas.drawCircle(
          Offset(0, radius * 0.2),
          radius * 0.32,
          stroke,
        );
        canvas.drawArc(
          Rect.fromCircle(
            center: Offset(0, -radius * 0.3),
            radius: radius * 0.35,
          ),
          3.6,
          2.08,
          false,
          stroke,
        );
        break;
      case _ZodiacSign.gemini:
        // || ikizler — iki dikey + iki yatay kapak
        canvas.drawLine(
          Offset(-radius * 0.3, -radius * 0.55),
          Offset(-radius * 0.3, radius * 0.55),
          stroke,
        );
        canvas.drawLine(
          Offset(radius * 0.3, -radius * 0.55),
          Offset(radius * 0.3, radius * 0.55),
          stroke,
        );
        canvas.drawLine(
          Offset(-radius * 0.55, -radius * 0.55),
          Offset(radius * 0.55, -radius * 0.55),
          stroke,
        );
        canvas.drawLine(
          Offset(-radius * 0.55, radius * 0.55),
          Offset(radius * 0.55, radius * 0.55),
          stroke,
        );
        break;
      case _ZodiacSign.cancer:
        // 69 şeklinde iki daire, biri üstte biri altta
        canvas.drawCircle(
          Offset(-radius * 0.3, -radius * 0.22),
          radius * 0.2,
          Paint()..color = color,
        );
        canvas.drawCircle(
          Offset(radius * 0.3, radius * 0.22),
          radius * 0.2,
          Paint()..color = color,
        );
        canvas.drawArc(
          Rect.fromLTRB(
            -radius * 0.6,
            -radius * 0.3,
            radius * 0.35,
            radius * 0.4,
          ),
          3.3,
          1.9,
          false,
          stroke,
        );
        canvas.drawArc(
          Rect.fromLTRB(
            -radius * 0.35,
            -radius * 0.4,
            radius * 0.6,
            radius * 0.3,
          ),
          0.15,
          1.9,
          false,
          stroke,
        );
        break;
      case _ZodiacSign.leo:
        // Daire + kıvrılan kuyruk
        canvas.drawCircle(
          Offset(-radius * 0.15, -radius * 0.1),
          radius * 0.25,
          stroke,
        );
        final tail = Path()
          ..moveTo(radius * 0.1, -radius * 0.1)
          ..quadraticBezierTo(
            radius * 0.6, radius * 0.1,
            radius * 0.4, radius * 0.5,
          )
          ..quadraticBezierTo(
            radius * 0.2, radius * 0.8,
            radius * 0.5, radius * 0.75,
          );
        canvas.drawPath(tail, stroke);
        break;
      case _ZodiacSign.virgo:
        // M şeklinde üç dikey + kıvrılan kuyruk
        canvas.drawLine(
          Offset(-radius * 0.55, -radius * 0.4),
          Offset(-radius * 0.55, radius * 0.55),
          stroke,
        );
        canvas.drawLine(
          Offset(-radius * 0.55, -radius * 0.4),
          Offset(-radius * 0.2, radius * 0.55),
          stroke,
        );
        canvas.drawLine(
          Offset(-radius * 0.2, -radius * 0.4),
          Offset(-radius * 0.2, radius * 0.55),
          stroke,
        );
        canvas.drawLine(
          Offset(-radius * 0.2, -radius * 0.4),
          Offset(radius * 0.15, radius * 0.55),
          stroke,
        );
        canvas.drawLine(
          Offset(radius * 0.15, -radius * 0.4),
          Offset(radius * 0.15, radius * 0.55),
          stroke,
        );
        // kuyruk
        canvas.drawArc(
          Rect.fromLTRB(
            -radius * 0.15,
            radius * 0.1,
            radius * 0.55,
            radius * 0.8,
          ),
          4.8,
          2.4,
          false,
          stroke,
        );
        break;
      case _ZodiacSign.libra:
        // İki çizgi + üstte tepeli kemer
        canvas.drawLine(
          Offset(-radius * 0.6, radius * 0.45),
          Offset(radius * 0.6, radius * 0.45),
          stroke,
        );
        canvas.drawLine(
          Offset(-radius * 0.5, radius * 0.15),
          Offset(-radius * 0.15, radius * 0.15),
          stroke,
        );
        canvas.drawLine(
          Offset(radius * 0.15, radius * 0.15),
          Offset(radius * 0.5, radius * 0.15),
          stroke,
        );
        canvas.drawArc(
          Rect.fromLTRB(
            -radius * 0.3,
            -radius * 0.5,
            radius * 0.3,
            radius * 0.25,
          ),
          3.1415,
          3.1415,
          false,
          stroke,
        );
        break;
      case _ZodiacSign.scorpio:
        // M + kuyrukta ok
        canvas.drawLine(
          Offset(-radius * 0.55, radius * 0.55),
          Offset(-radius * 0.55, -radius * 0.4),
          stroke,
        );
        canvas.drawLine(
          Offset(-radius * 0.55, -radius * 0.4),
          Offset(-radius * 0.25, radius * 0.55),
          stroke,
        );
        canvas.drawLine(
          Offset(-radius * 0.25, radius * 0.55),
          Offset(-radius * 0.25, -radius * 0.4),
          stroke,
        );
        canvas.drawLine(
          Offset(-radius * 0.25, -radius * 0.4),
          Offset(radius * 0.05, radius * 0.55),
          stroke,
        );
        canvas.drawLine(
          Offset(radius * 0.05, radius * 0.55),
          Offset(radius * 0.05, -radius * 0.1),
          stroke,
        );
        // ok ucu
        final arrow = Offset(radius * 0.55, -radius * 0.55);
        canvas.drawLine(
          Offset(radius * 0.05, -radius * 0.1),
          arrow,
          stroke,
        );
        canvas.drawLine(arrow, Offset(radius * 0.3, -radius * 0.55), stroke);
        canvas.drawLine(arrow, Offset(radius * 0.55, -radius * 0.3), stroke);
        break;
      case _ZodiacSign.sagittarius:
        // Ok (diyagonal) + sap ortasında çapraz
        final arrowTip = Offset(radius * 0.6, -radius * 0.6);
        canvas.drawLine(
          Offset(-radius * 0.6, radius * 0.6),
          arrowTip,
          stroke,
        );
        canvas.drawLine(arrowTip, Offset(radius * 0.3, -radius * 0.6), stroke);
        canvas.drawLine(arrowTip, Offset(radius * 0.6, -radius * 0.3), stroke);
        // çapraz çizgi (ok sapında)
        canvas.drawLine(
          Offset(-radius * 0.35, -radius * 0.1),
          Offset(radius * 0.1, radius * 0.35),
          stroke,
        );
        break;
      case _ZodiacSign.capricorn:
        // V (üstte) + kancalı daire (altta)
        canvas.drawLine(
          Offset(-radius * 0.55, -radius * 0.4),
          Offset(-radius * 0.25, radius * 0.2),
          stroke,
        );
        canvas.drawLine(
          Offset(-radius * 0.25, radius * 0.2),
          Offset(radius * 0.05, -radius * 0.3),
          stroke,
        );
        canvas.drawLine(
          Offset(radius * 0.05, -radius * 0.3),
          Offset(radius * 0.25, radius * 0.2),
          stroke,
        );
        // alt kanca
        canvas.drawArc(
          Rect.fromLTRB(
            radius * 0.05,
            radius * 0.1,
            radius * 0.6,
            radius * 0.7,
          ),
          3.4,
          3.0,
          false,
          stroke,
        );
        break;
      case _ZodiacSign.aquarius:
        // İki dalga çizgisi
        for (var row = 0; row < 2; row++) {
          final y = row == 0 ? -radius * 0.2 : radius * 0.25;
          final wave = Path()
            ..moveTo(-radius * 0.6, y)
            ..lineTo(-radius * 0.35, y - radius * 0.18)
            ..lineTo(-radius * 0.1, y + radius * 0.05)
            ..lineTo(radius * 0.15, y - radius * 0.18)
            ..lineTo(radius * 0.4, y + radius * 0.05)
            ..lineTo(radius * 0.6, y - radius * 0.1);
          canvas.drawPath(wave, stroke);
        }
        break;
      case _ZodiacSign.pisces:
        // İki dışa bakan C (araya düz çizgi)
        canvas.drawArc(
          Rect.fromLTRB(
            -radius * 0.7,
            -radius * 0.5,
            -radius * 0.1,
            radius * 0.5,
          ),
          -1.7,
          3.0,
          false,
          stroke,
        );
        canvas.drawArc(
          Rect.fromLTRB(
            radius * 0.1,
            -radius * 0.5,
            radius * 0.7,
            radius * 0.5,
          ),
          1.4,
          3.0,
          false,
          stroke,
        );
        canvas.drawLine(
          Offset(-radius * 0.45, 0),
          Offset(radius * 0.45, 0),
          stroke,
        );
        break;
    }
    canvas.restore();
  }

  void _drawDashedCircle(
    Canvas canvas,
    Offset center,
    double radius,
    Color color, {
    required double dashLength,
    required double gapLength,
    required double strokeWidth,
  }) {
    final paint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth
      ..color = color;
    final circumference = 2 * 3.1415926535 * radius;
    final dashes = (circumference / (dashLength + gapLength)).floor();
    final step = 2 * 3.1415926535 / dashes;
    final dashAngle = (dashLength / circumference) * 2 * 3.1415926535;
    final rect = Rect.fromCircle(center: center, radius: radius);
    for (var i = 0; i < dashes; i++) {
      final path = Path()..addArc(rect, i * step, dashAngle);
      canvas.drawPath(path, paint);
    }
  }

  void _drawSparkle(
    Canvas canvas, {
    required Offset offset,
    required double size,
    required Color color,
  }) {
    final path = Path()
      ..moveTo(offset.dx, offset.dy - size * 0.9)
      ..lineTo(offset.dx + size * 0.15, offset.dy - size * 0.15)
      ..lineTo(offset.dx + size * 0.9, offset.dy)
      ..lineTo(offset.dx + size * 0.15, offset.dy + size * 0.15)
      ..lineTo(offset.dx, offset.dy + size * 0.9)
      ..lineTo(offset.dx - size * 0.15, offset.dy + size * 0.15)
      ..lineTo(offset.dx - size * 0.9, offset.dy)
      ..lineTo(offset.dx - size * 0.15, offset.dy - size * 0.15)
      ..close();
    canvas.drawPath(path, Paint()..color = color);
  }

  @override
  bool shouldRepaint(covariant _ChartWheelPainter old) =>
      old.planets != planets || old.ascendantLon != ascendantLon;
}

// ─────────────────────────────────────────────────────────────
// PULL QUOTE — "Ay Aslan'da parladığında…" editorial essay insert
// ─────────────────────────────────────────────────────────────

class _PullQuoteSection extends ConsumerWidget {
  const _PullQuoteSection();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Canlı kaynak öncelik: narrative periodCore.upperMeaning → periodCore.coreStory.
    // İkisi de yoksa mock cümle.
    final snapshot = ref.watch(homeV2SnapshotProvider).value;
    final periodCore = snapshot?.narrative.periodCore;
    final liveQuote = [
      periodCore?.upperMeaning,
      periodCore?.coreStory,
    ].firstWhere(
      (s) => (s ?? '').trim().isNotEmpty,
      orElse: () => null,
    );

    final body = GoogleFonts.inter(
      textStyle: const TextStyle(
        fontSize: 15,
        height: 1.5,
        letterSpacing: -0.2,
        color: _HomeV2Palette.ink,
        fontWeight: FontWeight.w400,
      ),
    );
    final italic = GoogleFonts.fraunces(
      textStyle: const TextStyle(
        fontSize: 15,
        height: 1.5,
        letterSpacing: -0.2,
        color: _HomeV2Palette.ink,
        fontStyle: FontStyle.italic,
        fontWeight: FontWeight.w400,
      ),
    );
    final credit = GoogleFonts.inter(
      textStyle: const TextStyle(
        fontSize: 8.5,
        letterSpacing: 2,
        color: _HomeV2Palette.mist,
        fontWeight: FontWeight.w400,
      ),
    );
    final creditStrong = GoogleFonts.inter(
      textStyle: const TextStyle(
        fontSize: 8.5,
        letterSpacing: 2,
        color: _HomeV2Palette.ink,
        fontWeight: FontWeight.w500,
      ),
    );

    final quoteBody = liveQuote != null
        ? Text(liveQuote.trim(), style: body)
        : Text.rich(
            TextSpan(
              style: body,
              children: [
                const TextSpan(text: 'Ay Aslan\'da parladığında, '),
                TextSpan(text: 'en sessiz', style: italic),
                const TextSpan(
                  text: ' olanlar bile bir cümle kurar. Soru şu: o cümle ',
                ),
                TextSpan(text: 'kime', style: italic),
                const TextSpan(text: '?'),
              ],
            ),
          );

    return Container(
      color: _HomeV2Palette.paper,
      padding: const EdgeInsets.fromLTRB(28, 38, 28, 36),
      foregroundDecoration: const BoxDecoration(
        border: Border(
          top: BorderSide(color: _HomeV2Palette.hairline, width: 0.5),
          bottom: BorderSide(color: _HomeV2Palette.hairline, width: 0.5),
        ),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.only(top: 4, right: 18),
            child: Text(
              '"',
              style: GoogleFonts.fraunces(
                textStyle: const TextStyle(
                  fontSize: 72,
                  height: 0.7,
                  fontStyle: FontStyle.italic,
                  fontWeight: FontWeight.w300,
                  color: _HomeV2Palette.lime,
                ),
              ),
            ),
          ),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                quoteBody,
                const SizedBox(height: 12),
                Text.rich(
                  TextSpan(
                    style: credit,
                    children: [
                      const TextSpan(text: 'SHOU · '),
                      TextSpan(text: 'BUGÜNÜN NOTU', style: creditStrong),
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

// ─────────────────────────────────────────────────────────────
// WEEK STRIP — 7 günlük grid + "yoğun gün" highlight kutusu
// ─────────────────────────────────────────────────────────────

class _WeekSection extends StatelessWidget {
  const _WeekSection();

  @override
  Widget build(BuildContext context) {
    final eyebrow = GoogleFonts.inter(
      textStyle: const TextStyle(
        fontSize: 8.5,
        letterSpacing: 2.4,
        color: _HomeV2Palette.silver,
        fontWeight: FontWeight.w400,
      ),
    );
    final titleBody = GoogleFonts.inter(
      textStyle: const TextStyle(
        fontSize: 20,
        fontWeight: FontWeight.w500,
        color: _HomeV2Palette.ink,
        letterSpacing: -0.4,
        height: 1.2,
      ),
    );
    final titleItalic = GoogleFonts.fraunces(
      textStyle: const TextStyle(
        fontSize: 20,
        fontWeight: FontWeight.w400,
        fontStyle: FontStyle.italic,
        color: _HomeV2Palette.ink,
        letterSpacing: -0.4,
        height: 1.2,
      ),
    );
    final intro = GoogleFonts.inter(
      textStyle: const TextStyle(
        fontSize: 11.5,
        color: _HomeV2Palette.mist,
        height: 1.5,
        fontWeight: FontWeight.w400,
      ),
    );

    return Padding(
      padding: const EdgeInsets.fromLTRB(28, 38, 28, 40),
      child: Column(
        children: [
          Text('BU HAFTA', style: eyebrow),
          const SizedBox(height: 10),
          Text.rich(
            TextSpan(
              style: titleBody,
              children: [
                const TextSpan(text: 'Akışın '),
                TextSpan(text: 'haftalık', style: titleItalic),
                const TextSpan(text: ' görüntüsü'),
              ],
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 4),
          ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 280),
            child: Text(
              'Gökyüzü hafta boyunca farklı pencereler açar — biri yoğun, biri sessiz.',
              textAlign: TextAlign.center,
              style: intro,
            ),
          ),
          const SizedBox(height: 26),
          const _WeekDays(),
          const SizedBox(height: 24),
          const _WeekNextCard(),
        ],
      ),
    );
  }
}

enum _WeekDayTone { idle, active, blushDay, lavDay }

class _WeekDayData {
  const _WeekDayData({
    required this.num,
    required this.name,
    required this.tone,
  });
  final String num;
  final String name;
  final _WeekDayTone tone;
}

class _WeekDays extends ConsumerWidget {
  const _WeekDays();

  static const _mockDays = <_WeekDayData>[
    _WeekDayData(num: '17', name: 'CUM', tone: _WeekDayTone.active),
    _WeekDayData(num: '18', name: 'CMT', tone: _WeekDayTone.idle),
    _WeekDayData(num: '19', name: 'PAZ', tone: _WeekDayTone.blushDay),
    _WeekDayData(num: '20', name: 'PZT', tone: _WeekDayTone.idle),
    _WeekDayData(num: '21', name: 'SAL', tone: _WeekDayTone.idle),
    _WeekDayData(num: '22', name: 'ÇAR', tone: _WeekDayTone.lavDay),
    _WeekDayData(num: '23', name: 'PER', tone: _WeekDayTone.idle),
  ];

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final snapshot = ref.watch(homeV2SnapshotProvider).value;
    final live = snapshot?.weekDays ?? const <HomeV2WeekDay>[];
    final days = live.isNotEmpty
        ? live
              .map(
                (d) => _WeekDayData(
                  num: d.numLabel,
                  name: d.nameLabel,
                  tone: switch (d.tone) {
                    HomeV2WeekDayTone.idle => _WeekDayTone.idle,
                    HomeV2WeekDayTone.active => _WeekDayTone.active,
                    HomeV2WeekDayTone.blushDay => _WeekDayTone.blushDay,
                    HomeV2WeekDayTone.lavDay => _WeekDayTone.lavDay,
                  },
                ),
              )
              .toList(growable: false)
        : _mockDays;

    return Stack(
      alignment: Alignment.topCenter,
      children: [
        Positioned(
          top: 28,
          left: 12,
          right: 12,
          child: Container(height: 0.5, color: _HomeV2Palette.hairline),
        ),
        Padding(
          padding: const EdgeInsets.symmetric(vertical: 6),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              for (final d in days) Expanded(child: _WeekDayCell(data: d)),
            ],
          ),
        ),
      ],
    );
  }
}

class _WeekDayCell extends StatelessWidget {
  const _WeekDayCell({required this.data});
  final _WeekDayData data;

  @override
  Widget build(BuildContext context) {
    final isActive = data.tone == _WeekDayTone.active;
    final numStyle = GoogleFonts.fraunces(
      textStyle: TextStyle(
        fontSize: 16,
        fontWeight: FontWeight.w300,
        height: 1,
        letterSpacing: -0.3,
        color: isActive ? _HomeV2Palette.ink : _HomeV2Palette.silver,
      ),
    );
    final nameStyle = GoogleFonts.inter(
      textStyle: const TextStyle(
        fontSize: 8,
        letterSpacing: 1.2,
        color: _HomeV2Palette.silver,
        fontWeight: FontWeight.w400,
      ),
    );

    Color dotColor;
    Color dotBorder;
    switch (data.tone) {
      case _WeekDayTone.active:
        dotColor = _HomeV2Palette.lime;
        dotBorder = _HomeV2Palette.lime;
        break;
      case _WeekDayTone.blushDay:
        dotColor = _HomeV2Palette.blush;
        dotBorder = _HomeV2Palette.blush;
        break;
      case _WeekDayTone.lavDay:
        dotColor = _HomeV2Palette.lavender;
        dotBorder = _HomeV2Palette.lavender;
        break;
      case _WeekDayTone.idle:
        dotColor = _HomeV2Palette.paper;
        dotBorder = _HomeV2Palette.cloud;
        break;
    }

    return Column(
      children: [
        Text(data.num, style: numStyle),
        const SizedBox(height: 8),
        Container(
          width: 8,
          height: 8,
          decoration: BoxDecoration(
            color: dotColor,
            shape: BoxShape.circle,
            border: Border.all(color: dotBorder, width: 0.5),
            boxShadow: isActive
                ? [
                    BoxShadow(
                      color: _HomeV2Palette.lime.withValues(alpha: 0.3),
                      blurRadius: 0,
                      spreadRadius: 3,
                    ),
                  ]
                : null,
          ),
        ),
        const SizedBox(height: 6),
        Text(data.name, style: nameStyle),
      ],
    );
  }
}

class _WeekNextCard extends StatelessWidget {
  const _WeekNextCard();

  @override
  Widget build(BuildContext context) {
    final dateStyle = GoogleFonts.fraunces(
      textStyle: const TextStyle(
        fontSize: 11,
        fontStyle: FontStyle.italic,
        color: _HomeV2Palette.lavenderDeep,
        letterSpacing: 0.5,
        height: 1.3,
      ),
    );
    final labelStyle = GoogleFonts.inter(
      textStyle: const TextStyle(
        fontSize: 8,
        letterSpacing: 1.8,
        color: _HomeV2Palette.lavenderDeep,
        fontWeight: FontWeight.w500,
      ),
    );
    final bodyStyle = GoogleFonts.fraunces(
      textStyle: const TextStyle(
        fontSize: 13.5,
        height: 1.4,
        letterSpacing: -0.1,
        color: _HomeV2Palette.ink,
        fontWeight: FontWeight.w400,
      ),
    );
    final bodyItalic = GoogleFonts.fraunces(
      textStyle: const TextStyle(
        fontSize: 13.5,
        height: 1.4,
        letterSpacing: -0.1,
        color: _HomeV2Palette.fog,
        fontStyle: FontStyle.italic,
        fontWeight: FontWeight.w400,
      ),
    );

    // Sol 2px lav accent + sağı yuvarlak beyaz kutu. Mixed-color border +
    // borderRadius Flutter'da hatalı; onun yerine Row + ayrık container'lar.
    return ClipRRect(
      borderRadius: const BorderRadius.only(
        topRight: Radius.circular(8),
        bottomRight: Radius.circular(8),
      ),
      child: IntrinsicHeight(
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Container(width: 2, color: _HomeV2Palette.lavender),
            Expanded(
              child: Container(
                padding: const EdgeInsets.fromLTRB(14, 16, 18, 16),
                color: _HomeV2Palette.white,
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    SizedBox(
                      width: 56,
                      child: Text('22 Nis\nÇar', style: dateStyle),
                    ),
                    const SizedBox(width: 14),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('YOĞUN GÜN', style: labelStyle),
                          const SizedBox(height: 5),
                          Text.rich(
                            TextSpan(
                              style: bodyStyle,
                              children: [
                                const TextSpan(text: 'Yeni Ay '),
                                TextSpan(text: 'Boğa\'da', style: bodyItalic),
                                const TextSpan(
                                  text:
                                      '. Niyet dilemek için yıl içindeki en sakin kapı.',
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────
// STICKER GRID — 3x3 hızlı keşfet karoları, vektör glyph'ler
// ─────────────────────────────────────────────────────────────

enum _StickerTone { light, lime, ink, lavender, blush, cream }

enum _StickerGlyph {
  moon,
  venus,
  mercury,
  saturn,
  mars,
  sextile,
  flower,
  sun,
  fullMoon,
  plus,
}

class _StickerData {
  const _StickerData({
    required this.index,
    required this.label,
    required this.glyph,
    required this.tone,
  });
  final String index;
  final String label;
  final _StickerGlyph glyph;
  final _StickerTone tone;
}

class _StickerGridSection extends StatelessWidget {
  const _StickerGridSection();

  static const _items = <_StickerData>[
    _StickerData(
      index: '01',
      label: 'Ay Durumu',
      glyph: _StickerGlyph.moon,
      tone: _StickerTone.lime,
    ),
    _StickerData(
      index: '02',
      label: 'Aşk · Sinastri',
      glyph: _StickerGlyph.venus,
      tone: _StickerTone.ink,
    ),
    _StickerData(
      index: '03',
      label: 'İletişim',
      glyph: _StickerGlyph.mercury,
      tone: _StickerTone.light,
    ),
    _StickerData(
      index: '04',
      label: 'Dönem Transit',
      glyph: _StickerGlyph.saturn,
      tone: _StickerTone.lavender,
    ),
    _StickerData(
      index: '05',
      label: 'Açılar',
      glyph: _StickerGlyph.sextile,
      tone: _StickerTone.cream,
    ),
    _StickerData(
      index: '06',
      label: 'Retrograd',
      glyph: _StickerGlyph.flower,
      tone: _StickerTone.blush,
    ),
    _StickerData(
      index: '07',
      label: 'Güneş Dönüşü',
      glyph: _StickerGlyph.sun,
      tone: _StickerTone.light,
    ),
    _StickerData(
      index: '08',
      label: 'Yeni · Dolunay',
      glyph: _StickerGlyph.fullMoon,
      tone: _StickerTone.lime,
    ),
    _StickerData(
      index: '09',
      label: 'Tüm Araçlar',
      glyph: _StickerGlyph.plus,
      tone: _StickerTone.ink,
    ),
  ];

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 32, 20, 40),
      child: Column(
        children: [
          Text(
            'HIZLICA KEŞFET',
            style: GoogleFonts.inter(
              textStyle: const TextStyle(
                fontSize: 8.5,
                letterSpacing: 2.4,
                color: _HomeV2Palette.silver,
                fontWeight: FontWeight.w400,
              ),
            ),
          ),
          const SizedBox(height: 16),
          GridView.count(
            crossAxisCount: 3,
            crossAxisSpacing: 8,
            mainAxisSpacing: 8,
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            children: [for (final s in _items) _StickerTile(data: s)],
          ),
        ],
      ),
    );
  }
}

class _StickerTile extends StatelessWidget {
  const _StickerTile({required this.data});
  final _StickerData data;

  @override
  Widget build(BuildContext context) {
    late Color bg;
    late Color fg;
    late Color labelColor;
    late Color cornerColor;
    late bool hasBorder;

    switch (data.tone) {
      case _StickerTone.light:
        bg = _HomeV2Palette.white;
        fg = _HomeV2Palette.ink;
        labelColor = _HomeV2Palette.mist;
        cornerColor = _HomeV2Palette.silver;
        hasBorder = true;
        break;
      case _StickerTone.lime:
        bg = _HomeV2Palette.lime;
        fg = _HomeV2Palette.limeText;
        labelColor = _HomeV2Palette.limeText;
        cornerColor = const Color(0x4D000000);
        hasBorder = false;
        break;
      case _StickerTone.ink:
        bg = _HomeV2Palette.ink;
        fg = Colors.white;
        labelColor = const Color(0x99FFFFFF);
        cornerColor = const Color(0x59FFFFFF);
        hasBorder = false;
        break;
      case _StickerTone.lavender:
        bg = _HomeV2Palette.lavenderBg;
        fg = _HomeV2Palette.lavenderDeep;
        labelColor = _HomeV2Palette.lavenderDeep;
        cornerColor = _HomeV2Palette.silver;
        hasBorder = false;
        break;
      case _StickerTone.blush:
        bg = _HomeV2Palette.blushBg;
        fg = _HomeV2Palette.blushDeep;
        labelColor = _HomeV2Palette.blushDeep;
        cornerColor = _HomeV2Palette.silver;
        hasBorder = false;
        break;
      case _StickerTone.cream:
        bg = _HomeV2Palette.cream;
        fg = _HomeV2Palette.ink;
        labelColor = _HomeV2Palette.mist;
        cornerColor = _HomeV2Palette.silver;
        hasBorder = true;
        break;
    }

    return AspectRatio(
      aspectRatio: 1,
      child: Container(
        decoration: BoxDecoration(
          color: bg,
          borderRadius: BorderRadius.circular(2),
          border: hasBorder
              ? Border.all(color: _HomeV2Palette.hairline, width: 0.5)
              : null,
        ),
        child: Stack(
          children: [
            Positioned(
              top: 6,
              right: 8,
              child: Text(
                data.index,
                style: GoogleFonts.inter(
                  textStyle: TextStyle(
                    fontSize: 7,
                    letterSpacing: 0.6,
                    color: cornerColor,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
            ),
            Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  SizedBox(
                    width: 32,
                    height: 32,
                    child: CustomPaint(
                      painter: _StickerGlyphPainter(
                        glyph: data.glyph,
                        color: fg,
                      ),
                    ),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    data.label.toUpperCase(),
                    textAlign: TextAlign.center,
                    style: GoogleFonts.inter(
                      textStyle: TextStyle(
                        fontSize: 9,
                        letterSpacing: 1.2,
                        color: labelColor,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Sky rail kartlarındaki gezegen glyph'i — _StickerGlyphPainter'ı gezegen
/// enum'u üzerinden kullanır.
class _SkyGlyphPainter extends CustomPainter {
  _SkyGlyphPainter({required this.kind, required this.color});
  final _PlanetKind kind;
  final Color color;

  @override
  void paint(Canvas canvas, Size size) {
    final glyph = switch (kind) {
      _PlanetKind.sun => _StickerGlyph.sun,
      _PlanetKind.moon => _StickerGlyph.moon,
      _PlanetKind.mercury => _StickerGlyph.mercury,
      _PlanetKind.venus => _StickerGlyph.venus,
      _PlanetKind.mars => _StickerGlyph.mars,
      _PlanetKind.saturn => _StickerGlyph.saturn,
    };
    _StickerGlyphPainter(glyph: glyph, color: color).paint(canvas, size);
  }

  @override
  bool shouldRepaint(covariant _SkyGlyphPainter old) =>
      old.kind != kind || old.color != color;
}

class _StickerGlyphPainter extends CustomPainter {
  _StickerGlyphPainter({required this.glyph, required this.color});

  final _StickerGlyph glyph;
  final Color color;

  @override
  void paint(Canvas canvas, Size size) {
    final r = size.width / 2;
    final stroke = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = r * 0.14
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;
    final fill = Paint()..color = color;

    canvas.save();
    canvas.translate(size.width / 2, size.height / 2);

    switch (glyph) {
      case _StickerGlyph.moon:
        final outer = Path()
          ..addOval(Rect.fromCircle(center: Offset.zero, radius: r * 0.8));
        final inner = Path()
          ..addOval(
            Rect.fromCircle(
              center: Offset(r * 0.25, 0),
              radius: r * 0.7,
            ),
          );
        canvas.drawPath(
          Path.combine(PathOperation.difference, outer, inner),
          fill,
        );
        break;
      case _StickerGlyph.sun:
        canvas.drawCircle(Offset.zero, r * 0.6, stroke);
        canvas.drawCircle(Offset.zero, r * 0.15, fill);
        break;
      case _StickerGlyph.venus:
        canvas.drawCircle(Offset(0, -r * 0.25), r * 0.35, stroke);
        canvas.drawLine(Offset(0, r * 0.1), Offset(0, r * 0.8), stroke);
        canvas.drawLine(
          Offset(-r * 0.3, r * 0.45),
          Offset(r * 0.3, r * 0.45),
          stroke,
        );
        break;
      case _StickerGlyph.mercury:
        canvas.drawArc(
          Rect.fromCircle(
            center: Offset(0, -r * 0.55),
            radius: r * 0.3,
          ),
          0,
          3.1415926535,
          false,
          stroke,
        );
        canvas.drawCircle(Offset(0, -r * 0.1), r * 0.3, stroke);
        canvas.drawLine(Offset(0, r * 0.25), Offset(0, r * 0.8), stroke);
        canvas.drawLine(
          Offset(-r * 0.25, r * 0.52),
          Offset(r * 0.25, r * 0.52),
          stroke,
        );
        break;
      case _StickerGlyph.saturn:
        canvas.drawLine(
          Offset(-r * 0.5, -r * 0.7),
          Offset(r * 0.1, -r * 0.7),
          stroke,
        );
        canvas.drawLine(
          Offset(-r * 0.2, -r * 0.7),
          Offset(-r * 0.2, r * 0.35),
          stroke,
        );
        canvas.drawArc(
          Rect.fromLTRB(-r * 0.2, r * 0.05, r * 0.55, r * 0.85),
          3.1415926535,
          1.7,
          false,
          stroke,
        );
        break;
      case _StickerGlyph.mars:
        canvas.drawCircle(
          Offset(-r * 0.12, r * 0.12),
          r * 0.38,
          stroke,
        );
        final tip = Offset(r * 0.68, -r * 0.68);
        canvas.drawLine(Offset(r * 0.22, -r * 0.22), tip, stroke);
        canvas.drawLine(tip, Offset(r * 0.38, -r * 0.68), stroke);
        canvas.drawLine(tip, Offset(r * 0.68, -r * 0.38), stroke);
        break;
      case _StickerGlyph.sextile:
        // 6-point star (iki üçgen üst üste)
        for (var rot = 0; rot < 2; rot++) {
          final angleOffset = rot * 3.1415926535 / 3;
          final tri = Path();
          for (var i = 0; i < 3; i++) {
            final a = angleOffset + i * 2 * 3.1415926535 / 3 - 3.1415926535 / 2;
            final p = Offset(r * 0.7 * _cosd(a), r * 0.7 * _sind(a));
            if (i == 0) {
              tri.moveTo(p.dx, p.dy);
            } else {
              tri.lineTo(p.dx, p.dy);
            }
          }
          tri.close();
          canvas.drawPath(tri, stroke);
        }
        break;
      case _StickerGlyph.flower:
        // 6 yapraklı çiçek — retrograd / Rx sembolü yerine
        for (var i = 0; i < 6; i++) {
          final a = i * 3.1415926535 / 3;
          final cx = r * 0.45 * _cosd(a);
          final cy = r * 0.45 * _sind(a);
          canvas.drawCircle(Offset(cx, cy), r * 0.22, stroke);
        }
        canvas.drawCircle(Offset.zero, r * 0.1, fill);
        break;
      case _StickerGlyph.fullMoon:
        canvas.drawCircle(Offset.zero, r * 0.55, fill);
        break;
      case _StickerGlyph.plus:
        canvas.drawLine(
          Offset(0, -r * 0.6),
          Offset(0, r * 0.6),
          stroke,
        );
        canvas.drawLine(
          Offset(-r * 0.6, 0),
          Offset(r * 0.6, 0),
          stroke,
        );
        break;
    }
    canvas.restore();
  }

  double _cosd(double rad) => math.cos(rad);
  double _sind(double rad) => math.sin(rad);

  @override
  bool shouldRepaint(covariant _StickerGlyphPainter old) =>
      old.glyph != glyph || old.color != color;
}

// ─────────────────────────────────────────────────────────────
// FORUM SECTION — kolektif thread preview'u
// ─────────────────────────────────────────────────────────────

class _ForumSection extends StatefulWidget {
  const _ForumSection();

  @override
  State<_ForumSection> createState() => _ForumSectionState();
}

class _ForumSectionState extends State<_ForumSection>
    with SingleTickerProviderStateMixin {
  late final AnimationController _pulse;

  @override
  void initState() {
    super.initState();
    _pulse = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 3),
    )..repeat(reverse: true);
  }

  @override
  void dispose() {
    _pulse.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [
            _HomeV2Palette.lavenderBg,
            _HomeV2Palette.lavenderBg.withValues(alpha: 0),
          ],
          stops: const [0, 0.85],
        ),
        border: const Border(
          top: BorderSide(color: _HomeV2Palette.hairline, width: 0.5),
          bottom: BorderSide(color: _HomeV2Palette.hairline, width: 0.5),
        ),
      ),
      padding: const EdgeInsets.fromLTRB(28, 32, 28, 48),
      child: Column(
        children: [
          _ForumEyebrow(pulse: _pulse),
          const SizedBox(height: 18),
          _ForumTitle(),
          const SizedBox(height: 6),
          _ForumSub(),
          const SizedBox(height: 28),
          const _ForumThreads(),
          const SizedBox(height: 30),
          _ForumCta(),
        ],
      ),
    );
  }
}

class _ForumEyebrow extends StatelessWidget {
  const _ForumEyebrow({required this.pulse});
  final Animation<double> pulse;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        AnimatedBuilder(
          animation: pulse,
          builder: (context, _) {
            final t = 1 - (pulse.value * 2 - 1).abs();
            return Container(
              width: 5,
              height: 5,
              decoration: BoxDecoration(
                color: _HomeV2Palette.lime.withValues(
                  alpha: 0.5 + 0.5 * t,
                ),
                shape: BoxShape.circle,
              ),
            );
          },
        ),
        const SizedBox(width: 8),
        Text(
          'KOLEKTİF — 127 KİŞİ ÇEVRİMİÇİ',
          style: GoogleFonts.inter(
            textStyle: const TextStyle(
              fontSize: 8.5,
              letterSpacing: 2.4,
              color: _HomeV2Palette.lavenderDeep,
              fontWeight: FontWeight.w400,
            ),
          ),
        ),
      ],
    );
  }
}

class _ForumTitle extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final body = GoogleFonts.inter(
      textStyle: const TextStyle(
        fontSize: 22,
        fontWeight: FontWeight.w500,
        color: _HomeV2Palette.ink,
        letterSpacing: -0.4,
        height: 1.2,
      ),
    );
    final italic = GoogleFonts.fraunces(
      textStyle: const TextStyle(
        fontSize: 22,
        fontWeight: FontWeight.w400,
        fontStyle: FontStyle.italic,
        color: _HomeV2Palette.ink,
        letterSpacing: -0.4,
        height: 1.2,
      ),
    );
    return Text.rich(
      TextSpan(
        style: body,
        children: [
          TextSpan(text: 'Gökyüzü', style: italic),
          const TextSpan(text: ' hakkında konuşulanlar'),
        ],
      ),
      textAlign: TextAlign.center,
    );
  }
}

class _ForumSub extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Text(
      'Benzer transit geçen başka biri nasıl hissediyor?',
      textAlign: TextAlign.center,
      style: GoogleFonts.inter(
        textStyle: const TextStyle(
          fontSize: 11.5,
          color: _HomeV2Palette.mist,
          letterSpacing: -0.1,
          fontWeight: FontWeight.w400,
        ),
      ),
    );
  }
}

enum _ThreadTone { lavender, lime, blush }

class _ForumThreads extends StatelessWidget {
  const _ForumThreads();

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: const [
        _ForumThread(
          tone: _ThreadTone.lavender,
          glyph: _StickerGlyph.venus,
          topic: 'Venüs Retro · Genel',
          question:
              'Eski bir sevgili tekrar yazdı — #retro etkisi# mi yoksa tesadüf mü?',
          replies: '42 yanıt · 8 dk önce',
          avatarColors: [
            Color(0xFFDDD8FC),
            Color(0xFFEAFFB8),
            Color(0xFFFDE4F2),
          ],
        ),
        SizedBox(height: 22),
        _ForumThread(
          tone: _ThreadTone.lime,
          glyph: _StickerGlyph.moon,
          topic: 'Ay Aslan · Bugün',
          question:
              'Bugün #sahnede olma hissi# herkeste var mı, yoksa bir tek bende mi?',
          replies: '18 yanıt · 24 dk önce',
          avatarColors: [Color(0xFFEAFFB8), Color(0xFFF0EDE6)],
        ),
        SizedBox(height: 22),
        _ForumThread(
          tone: _ThreadTone.blush,
          glyph: _StickerGlyph.sextile,
          topic: 'Sinastri · İlişki',
          question:
              'Ay-Venüs #kavuşumu# olan çiftler — bu aspect günlük yaşamınızda nasıl geçiyor?',
          replies: '73 yanıt · 1sa önce',
          avatarColors: [
            Color(0xFFFDE4F2),
            Color(0xFFDDD8FC),
            Color(0xFFEAFFB8),
          ],
        ),
      ],
    );
  }
}

class _ForumThread extends StatelessWidget {
  const _ForumThread({
    required this.tone,
    required this.glyph,
    required this.topic,
    required this.question,
    required this.replies,
    required this.avatarColors,
  });

  final _ThreadTone tone;
  final _StickerGlyph glyph;
  final String topic;
  final String question;
  final String replies;
  final List<Color> avatarColors;

  @override
  Widget build(BuildContext context) {
    Color glyphColor;
    switch (tone) {
      case _ThreadTone.lavender:
        glyphColor = _HomeV2Palette.lavenderDeep;
        break;
      case _ThreadTone.lime:
        glyphColor = _HomeV2Palette.limeText;
        break;
      case _ThreadTone.blush:
        glyphColor = _HomeV2Palette.blushDeep;
        break;
    }

    final questionBody = GoogleFonts.inter(
      textStyle: const TextStyle(
        fontSize: 14.5,
        height: 1.4,
        letterSpacing: -0.2,
        color: _HomeV2Palette.ink,
        fontWeight: FontWeight.w400,
      ),
    );
    final questionItalic = GoogleFonts.fraunces(
      textStyle: const TextStyle(
        fontSize: 14.5,
        height: 1.4,
        letterSpacing: -0.2,
        color: _HomeV2Palette.ink,
        fontStyle: FontStyle.italic,
        fontWeight: FontWeight.w400,
      ),
    );

    // Parse #word# spans for italic
    final spans = <InlineSpan>[];
    final parts = question.split('#');
    for (var i = 0; i < parts.length; i++) {
      if (parts[i].isEmpty) continue;
      spans.add(
        TextSpan(
          text: parts[i],
          style: i.isOdd ? questionItalic : null,
        ),
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Topic row with glyph
        Row(
          children: [
            SizedBox(
              width: 14,
              height: 14,
              child: CustomPaint(
                painter: _StickerGlyphPainter(
                  glyph: glyph,
                  color: glyphColor,
                ),
              ),
            ),
            const SizedBox(width: 8),
            Text(
              topic.toUpperCase(),
              style: GoogleFonts.inter(
                textStyle: const TextStyle(
                  fontSize: 8,
                  letterSpacing: 1.8,
                  color: _HomeV2Palette.mist,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 7),
        Text.rich(
          TextSpan(style: questionBody, children: spans),
        ),
        const SizedBox(height: 8),
        Row(
          children: [
            for (var i = 0; i < avatarColors.length; i++)
              Transform.translate(
                offset: Offset(-4.0 * i, 0),
                child: Container(
                  width: 14,
                  height: 14,
                  decoration: BoxDecoration(
                    color: avatarColors[i],
                    shape: BoxShape.circle,
                    border: Border.all(
                      color: _HomeV2Palette.paper,
                      width: 1.5,
                    ),
                  ),
                ),
              ),
            const SizedBox(width: 12),
            Text(
              replies,
              style: GoogleFonts.inter(
                textStyle: const TextStyle(
                  fontSize: 9,
                  letterSpacing: 0.3,
                  color: _HomeV2Palette.mist,
                ),
              ),
            ),
          ],
        ),
      ],
    );
  }
}

class _ForumCta extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: () {
        // TODO: Forum tab'ına git veya soru yaz sayfasına.
      },
      child: Text(
        'SORU SOR  →',
        style: GoogleFonts.inter(
          textStyle: const TextStyle(
            fontSize: 10,
            letterSpacing: 2.5,
            color: _HomeV2Palette.ink,
            fontWeight: FontWeight.w400,
            decoration: TextDecoration.underline,
            decorationColor: _HomeV2Palette.lime,
            decorationThickness: 2,
          ),
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────
// ENDPIECE — sayfanın imzası
// ─────────────────────────────────────────────────────────────

class _Endpiece extends StatelessWidget {
  const _Endpiece();

  @override
  Widget build(BuildContext context) {
    final body = GoogleFonts.fraunces(
      textStyle: const TextStyle(
        fontSize: 15,
        fontStyle: FontStyle.italic,
        fontWeight: FontWeight.w300,
        color: _HomeV2Palette.fog,
        height: 1.4,
        letterSpacing: -0.005,
      ),
    );
    final bodyInk = GoogleFonts.fraunces(
      textStyle: const TextStyle(
        fontSize: 15,
        fontStyle: FontStyle.italic,
        fontWeight: FontWeight.w300,
        color: _HomeV2Palette.ink,
        height: 1.4,
        letterSpacing: -0.005,
      ),
    );

    return Container(
      color: _HomeV2Palette.cream,
      padding: const EdgeInsets.fromLTRB(32, 44, 32, 32),
      foregroundDecoration: const BoxDecoration(
        border: Border(
          top: BorderSide(color: _HomeV2Palette.hairline, width: 0.5),
        ),
      ),
      child: Column(
        children: [
          Text.rich(
            TextSpan(
              style: body,
              children: [
                const TextSpan(text: '"Gökyüzü bugün '),
                TextSpan(text: 'burada', style: bodyInk),
                const TextSpan(text: '.\nKalbin nerede?"'),
              ],
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 14),
          Text(
            'SHOU · ASTROLOJİK NOT DEFTERİ',
            style: GoogleFonts.inter(
              textStyle: const TextStyle(
                fontSize: 8.5,
                letterSpacing: 2.5,
                color: _HomeV2Palette.silver,
                fontWeight: FontWeight.w400,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
