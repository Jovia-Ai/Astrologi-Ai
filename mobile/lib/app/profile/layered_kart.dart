// Buzdağı modeli için paylaşılan kart bileşeni.
//
// Hem Profile yüzeyindeki "Seni farklı kılan" differentiator'larında
// hem de Tam Okuma derinliğindeki kart galerisinde aynı görsel pattern
// kullanılıyor: 16:9 pastel zemin + tap scale animasyonu + opsiyonel
// el-çizimi illüstrasyon. F2'de Tam Okuma da bu shell'e geçecek; şu an
// önce Profile yüzeyi kullanıyor.

import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';

// ─────────────────────────────────────────────────────────────────
// Tones — pastel arkaplan varyantları + her birinin metin/illüst rengi.
// ─────────────────────────────────────────────────────────────────

enum LayeredKartTone { grey, lav, lime, peach, blush, limeFull }

class LayeredKartTonePalette {
  const LayeredKartTonePalette({
    required this.bg,
    required this.strong,
    required this.label,
    required this.meta,
    required this.body,
    required this.illust,
  });

  final Color bg;
  final Color strong; // start-of-card label color (e.g. "01 stellium")
  final Color label; // muted small label
  final Color meta; // top-right meta
  final Color body; // body text color
  final Color illust; // illustration tint
}

const _ink = Color(0xFF0E0E10);
const _mist = Color(0xFF888888);

LayeredKartTonePalette layeredKartPalette(LayeredKartTone tone) {
  switch (tone) {
    case LayeredKartTone.lav:
      return const LayeredKartTonePalette(
        bg: Color(0xFFE0DCF5),
        strong: Color(0xFF534AB7),
        label: _mist,
        meta: _mist,
        body: _ink,
        illust: Color(0xFF534AB7),
      );
    case LayeredKartTone.lime:
      return const LayeredKartTonePalette(
        bg: Color(0xFFE8F5C4),
        strong: Color(0xFF5A8E10),
        label: _mist,
        meta: _mist,
        body: _ink,
        illust: Color(0xFF5A8E10),
      );
    case LayeredKartTone.peach:
      return const LayeredKartTonePalette(
        bg: Color(0xFFFADBB8),
        strong: Color(0xFFC97A2E),
        label: _mist,
        meta: _mist,
        body: _ink,
        illust: Color(0xFFC97A2E),
      );
    case LayeredKartTone.blush:
      return const LayeredKartTonePalette(
        bg: Color(0xFFFADCEC),
        strong: Color(0xFFC76FA0),
        label: _mist,
        meta: _mist,
        body: _ink,
        illust: Color(0xFFC76FA0),
      );
    case LayeredKartTone.limeFull:
      return const LayeredKartTonePalette(
        bg: Color(0xFFCAFF4D),
        strong: Color(0xFF1A3300),
        label: Color(0xA61A3300),
        meta: Color(0x8C1A3300),
        body: Color(0xFF1A3300),
        illust: Color(0xFF1A3300),
      );
    case LayeredKartTone.grey:
      return const LayeredKartTonePalette(
        bg: Color(0xFFECECEA),
        strong: _ink,
        label: _mist,
        meta: _mist,
        body: _ink,
        illust: _ink,
      );
  }
}

// ─────────────────────────────────────────────────────────────────
// Hand-drawn illustrations (SVG) — Tam Okuma v2 referansından 1:1.
// ─────────────────────────────────────────────────────────────────

enum LayeredKartIllust { stellium, square, conj, past, nn, opening }

/// Backend `detail_cards[]` → mobil 3-katmanlı kart için veri kabuğu.
///
/// Üç katman:
///   - **label** (etiket / jargon) — `astro_sources.join(' · ')` veya `chips`
///   - **core** (çekirdek başlık) — Fraunces italik, `title`
///   - **body** + **detailBlocks** (yorum gövdesi) — açılır sayfada gösterilir
class LayeredKartData {
  const LayeredKartData({
    required this.id,
    required this.tone,
    required this.illust,
    required this.label,
    required this.core,
    this.eyebrow,
    this.summary,
    this.body,
    this.detailBlocks = const [],
    this.chips = const [],
    this.astroSources = const [],
    this.family,
    this.surfaceLink,
  });

  /// `card_key` veya `id` — kalıcı kimlik (deep link / surface↔depth link için).
  final String id;
  final LayeredKartTone tone;
  final LayeredKartIllust illust;

  /// Layer 1 — jargon/orb satırı (mono, küçük caps).
  final String label;

  /// Layer 2 — editöryal başlık cümlesi (Fraunces italic).
  final String core;

  /// Backend `eyebrow` (varsa) — başlık üstü mini etiket.
  final String? eyebrow;

  /// Kapalı kart teaser (max ~140c).
  final String? summary;

  /// Açılır sayfada lead paragrafı (max ~520c).
  final String? body;

  /// Açılır sayfada gövde paragrafları (her biri max ~320c, max 7 adet).
  final List<String> detailBlocks;

  /// Kart altında küçük tag'ler.
  final List<String> chips;

  /// Astrolojik kaynaklar (gezegen, açı, ev). Layer 1'i besler.
  final List<String> astroSources;

  /// Backend `family` — eksen ataması ve tone/illust seçimi için.
  final String? family;

  /// Profile yüzeyindeki teaser referansı (varsa) — örn. "differentiators[0]".
  final String? surfaceLink;
}

String layeredKartIllustSvg(LayeredKartIllust kind) {
  switch (kind) {
    case LayeredKartIllust.stellium:
      return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 60">'
          '<g stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round">'
          '<circle cx="40" cy="22" r="3.5" fill="currentColor"/>'
          '<circle cx="28" cy="32" r="3" fill="currentColor"/>'
          '<circle cx="52" cy="32" r="3" fill="currentColor"/>'
          '<circle cx="34" cy="42" r="2.5" fill="currentColor"/>'
          '<circle cx="46" cy="42" r="2.5" fill="currentColor"/>'
          '<path d="M40 16 Q35 14 33 18" fill="none"/>'
          '<path d="M40 16 Q45 14 47 18" fill="none"/>'
          '<path d="M22 32 Q19 30 17 33" fill="none"/>'
          '<path d="M58 32 Q61 30 63 33" fill="none"/>'
          '</g></svg>';
    case LayeredKartIllust.square:
      return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 60">'
          '<g stroke="currentColor" stroke-width="2.2" fill="none" stroke-linecap="round" stroke-linejoin="round">'
          '<path d="M22 14 Q20 14 20 16 L20 44 Q20 46 22 46 L58 46 Q60 46 60 44 L60 16 Q60 14 58 14 Z"/>'
          '<path d="M28 22 L52 38"/>'
          '<path d="M52 22 L28 38"/>'
          '</g></svg>';
    case LayeredKartIllust.conj:
      return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 60">'
          '<g stroke="currentColor" stroke-width="2.2" fill="none" stroke-linecap="round">'
          '<circle cx="32" cy="30" r="14"/>'
          '<circle cx="48" cy="30" r="14"/>'
          '<circle cx="40" cy="30" r="2.5" fill="currentColor"/>'
          '</g></svg>';
    case LayeredKartIllust.past:
      return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 60">'
          '<g stroke="currentColor" stroke-width="2.2" fill="none" stroke-linecap="round" stroke-linejoin="round">'
          '<path d="M58 18 Q30 14 24 30 Q22 44 38 46 Q52 46 52 36 Q52 28 44 28"/>'
          '<path d="M55 14 L58 18 L54 22"/>'
          '</g></svg>';
    case LayeredKartIllust.nn:
      return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 60">'
          '<g stroke="currentColor" stroke-width="2.2" fill="none" stroke-linecap="round" stroke-linejoin="round">'
          '<path d="M16 44 Q16 18 40 18 Q64 18 64 44"/>'
          '<circle cx="16" cy="46" r="3"/>'
          '<circle cx="64" cy="46" r="3"/>'
          '<path d="M40 18 L40 12"/>'
          '<path d="M36 14 L40 12 L44 14"/>'
          '</g></svg>';
    case LayeredKartIllust.opening:
      return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 60">'
          '<g stroke="currentColor" stroke-width="2.2" fill="none" stroke-linecap="round" stroke-linejoin="round">'
          '<path d="M28 14 L28 46 L48 46 L48 14 Z"/>'
          '<path d="M48 14 L62 20 L62 40 L48 46"/>'
          '<circle cx="44" cy="30" r="1.5" fill="currentColor"/>'
          '</g></svg>';
  }
}

class LayeredKartIllustration extends StatelessWidget {
  const LayeredKartIllustration({
    super.key,
    required this.kind,
    required this.color,
    this.width = 92,
    this.height = 68,
    this.opacity = 1.0,
  });

  final LayeredKartIllust kind;
  final Color color;
  final double width;
  final double height;
  final double opacity;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: width,
      height: height,
      child: Opacity(
        opacity: opacity,
        child: SvgPicture.string(
          layeredKartIllustSvg(kind),
          colorFilter: ColorFilter.mode(color, BlendMode.srcIn),
          fit: BoxFit.contain,
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────
// Press-kart shell — 16:9 (varsayılan) pastel kart, tap'te scale 0.97
// + 1px translate-y (CLAUDE.md animasyon standardı: 150ms easeOutCubic).
// İçerik build'i caller'a bırakılır → Tam Okuma ve Profil farklı içerik
// yerleşimleri kullanır ama aynı kabuğu paylaşır.
// ─────────────────────────────────────────────────────────────────

class LayeredKartShell extends StatefulWidget {
  const LayeredKartShell({
    super.key,
    required this.tone,
    required this.onTap,
    required this.builder,
    this.aspectRatio = 16 / 9,
    this.padding = const EdgeInsets.fromLTRB(18, 14, 18, 14),
    this.borderRadius = 22,
  });

  final LayeredKartTone tone;
  final VoidCallback onTap;
  final Widget Function(BuildContext context, LayeredKartTonePalette palette)
  builder;
  final double aspectRatio;
  final EdgeInsets padding;
  final double borderRadius;

  @override
  State<LayeredKartShell> createState() => _LayeredKartShellState();
}

class _LayeredKartShellState extends State<LayeredKartShell> {
  bool _pressed = false;

  @override
  Widget build(BuildContext context) {
    final palette = layeredKartPalette(widget.tone);
    return GestureDetector(
      behavior: HitTestBehavior.opaque,
      onTapDown: (_) => setState(() => _pressed = true),
      onTapUp: (_) => setState(() => _pressed = false),
      onTapCancel: () => setState(() => _pressed = false),
      onTap: widget.onTap,
      child: AnimatedScale(
        scale: _pressed ? 0.97 : 1.0,
        duration: const Duration(milliseconds: 150),
        curve: Curves.easeOutCubic,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 150),
          curve: Curves.easeOutCubic,
          transform: Matrix4.translationValues(0, _pressed ? 1 : 0, 0),
          child: AspectRatio(
            aspectRatio: widget.aspectRatio,
            child: Container(
              clipBehavior: Clip.antiAlias,
              decoration: BoxDecoration(
                color: palette.bg,
                borderRadius: BorderRadius.circular(widget.borderRadius),
              ),
              padding: widget.padding,
              child: widget.builder(context, palette),
            ),
          ),
        ),
      ),
    );
  }
}
