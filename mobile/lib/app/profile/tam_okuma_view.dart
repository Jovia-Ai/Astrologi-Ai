import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';

import 'package:mobile/app/profile/layered_kart.dart';
import 'package:mobile/app/profile/profile_v9_adapter.dart';

class TamOkumaView extends StatefulWidget {
  const TamOkumaView({
    super.key,
    this.profile,
    this.payload,
    this.displayName,
    this.data,
    this.onCardTap,
    this.embedded = false,
  });

  final Map<String, dynamic>? profile;
  final Map<String, dynamic>? payload;
  final String? displayName;

  /// Adapter çıktısı — null ise mock veri kullanılır.
  final ProfileV9TamOkumaData? data;

  /// Karta tıklanınca çağrılır — null değilse kart tıklanabilir olur.
  final void Function(LayeredKartData card)? onCardTap;

  /// `true` ise dış rounded-card + iç top header gizlenir (Profil tab'ı
  /// gibi başka bir surface içinde gömülü kullanım için).
  final bool embedded;

  @override
  State<TamOkumaView> createState() => _TamOkumaViewState();
}

class _TamOkumaViewState extends State<TamOkumaView> {
  int _axis = 0;

  static const List<_Axis> _axes = [
    _Axis(eye: '01', label: 'Kimlik', headerEye: 'Kimlik ekseni'),
    _Axis(eye: '02', label: 'İlişki', headerEye: 'İlişki ekseni'),
    _Axis(eye: '03', label: 'Kariyer', headerEye: 'Kariyer ekseni'),
    _Axis(eye: '04', label: 'Gölge', headerEye: 'Gölge ekseni'),
  ];

  @override
  Widget build(BuildContext context) {
    final usingRealData = widget.data != null;
    final realCards = usingRealData
        ? widget.data!.cardsByAxis[_axisFromIndex(_axis)] ?? const []
        : null;
    final mockCards = usingRealData ? null : _mockCardsForAxis(_axis);
    final cardCount = usingRealData ? realCards!.length : mockCards!.length;

    final intro = _resolveIntro(usingRealData: usingRealData);
    final next = _axes[(_axis + 1) % _axes.length];
    final displayName = widget.displayName ?? 'Sahra Özdoğan';

    final body = Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        if (!widget.embedded)
          _HeaderBlock(
            displayName: displayName,
            axes: _axes,
            currentAxis: _axis,
            onAxisChanged: (i) => setState(() => _axis = i),
          ),
        if (widget.embedded)
          _AxisTabBar(
            axes: _axes,
            currentAxis: _axis,
            onAxisChanged: (i) => setState(() => _axis = i),
          ),
        _GalleryIntro(
          eyebrow: intro.eyebrow,
          quote: intro.quoteHead,
          quoteEm: intro.quoteTailItalic,
          sub: intro.subtitle,
        ),
        Padding(
          padding: const EdgeInsets.fromLTRB(14, 16, 14, 22),
          child: Column(
            children: [
              for (var i = 0; i < cardCount; i++) ...[
                if (i > 0) const SizedBox(height: 12),
                if (usingRealData)
                  _Kart(
                    card: _kartDataFromLayered(realCards![i], i),
                    onTap: () => widget.onCardTap?.call(realCards[i]),
                  )
                else
                  _Kart(
                    card: mockCards![i],
                    onTap: () {},
                  ),
              ],
              if (cardCount == 0) const _EmptyAxisNote(),
            ],
          ),
        ),
        _GalleryFooter(
          axisLabel: _axes[_axis].label,
          cardCount: cardCount,
          currentIndex: _axis,
          total: _axes.length,
          nextEye: next.eye,
          nextLabel: next.label,
          nextTagline: _mockNextTagline(next.label),
          onNext: () =>
              setState(() => _axis = (_axis + 1) % _axes.length),
        ),
      ],
    );

    if (widget.embedded) {
      return body; // Profile tab içinde — dış kart yok, padding yok.
    }

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Container(
        clipBehavior: Clip.antiAlias,
        decoration: BoxDecoration(
          color: _ToColors.paperPure,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: _ToColors.hairline),
        ),
        child: body,
      ),
    );
  }

  TamOkumaAxis _axisFromIndex(int i) {
    switch (i) {
      case 0:
        return TamOkumaAxis.kimlik;
      case 1:
        return TamOkumaAxis.iliski;
      case 2:
        return TamOkumaAxis.kariyer;
      default:
        return TamOkumaAxis.golge;
    }
  }

  V9TamOkumaIntro _resolveIntro({required bool usingRealData}) {
    if (usingRealData && widget.data != null) {
      final intro = widget.data!.introByAxis[_axisFromIndex(_axis)];
      if (intro != null) return intro;
    }
    final mock = _mockIntroForAxis(_axis);
    return V9TamOkumaIntro(
      eyebrow: _axes[_axis].headerEye.toUpperCase(),
      quoteHead: mock.quote,
      quoteTailItalic: mock.quoteEm,
      subtitle: mock.sub,
    );
  }

}

/// Backend `LayeredKartData` → mock kart visual layout'una uyumlu `_KartData`
/// dönüşümü. Mock kartlardaki gibi 5 slot kullanılır:
///   • top-l strong  : "01 stellium" (axis index + family kısa adı)
///   • top-l subtitle: 3-4 kelimelik kısa tema (overflow olmaz)
///   • top-r meta    : astro kaynak ilk 2 öğe — kısa
///   • illust        : merkezde (mock ile aynı)
///   • bot-l         : family-tr context label ("tek evde 5", "tam kare", ...)
///   • bot-r         : chips ilk öğesi veya house/sign hint
///
/// Detayl içerik (body, detail_blocks) detail sayfasında — kart üstünde değil.
_KartData _kartDataFromLayered(LayeredKartData k, int axisIndex) {
  final indexLabel =
      '${(axisIndex + 1).toString().padLeft(2, '0')} ${_familyShortLabel(k.family)}';
  return _KartData(
    indexEye: k.id,
    title: indexLabel.trim(),
    subtitle: _shortSubtitle(k),
    topRight: _topRightMeta(k),
    botLeft: _bottomLeftContext(k),
    botRight: _bottomRightMeta(k),
    illust: _toInternalIllust(k.illust),
    tone: _toInternalTone(k.tone),
  );
}

/// Çekirdek cümlenin ilk 3-4 kelimesi — kart üstünde subtitle slot'una sığar.
String _shortSubtitle(LayeredKartData k) {
  final core = k.core.trim();
  if (core.isEmpty) {
    return (k.eyebrow ?? '').trim();
  }
  final words = core.split(RegExp(r'\s+'));
  final clipped = words.take(4).join(' ');
  // Sondaki noktalama işaretini at
  final cleaned = clipped.replaceAll(RegExp(r'[.,;:]+$'), '');
  if (cleaned.length > 28) {
    return '${cleaned.substring(0, 25)}…';
  }
  return cleaned;
}

/// Astro kaynak ilk 2 öğesi (kısa) — top-right slot'una sığar.
/// Backend'in astro_sources tipik formatı: ["Saturn", "0.03°", "Ascendant"].
/// İlk iki öğeyi joinleriz; orb varsa ikinci satırda kalır.
String _topRightMeta(LayeredKartData k) {
  final src = k.astroSources.where((s) => s.trim().isNotEmpty).toList();
  if (src.isEmpty) return '';
  if (src.length == 1) return src.first;
  // En fazla 2 öğe; orb gibi metric varsa ikinci satıra kıralım
  final first = src[0];
  final second = src[1];
  // Hangi öğe orb (içinde ° vb. var) — orb'u alta koy
  final hasOrb = second.contains('°') || RegExp(r'\d').hasMatch(second);
  if (hasOrb && !first.contains('°')) {
    return '$first\n$second';
  }
  return '$first · $second';
}

/// Family'ye göre semantik kısa context — bottom-left slot.
/// Mock cards'taki "tek evde 5", "tam kare", "kavuşum" gibi etiketler.
String _bottomLeftContext(LayeredKartData k) {
  switch (k.family) {
    case 'self_definition':
      return 'kimlik';
    case 'mind_mechanics':
      return 'kavuşum';
    case 'outer_inner_split':
      return 'iç/dış';
    case 'contradiction_core':
      return 'tam kare';
    case 'tone_signature':
      return 'ton';
    case 'placement_signature':
      return 'yerleşim';
    case 'intimacy_guard':
      return 'yakınlık';
    case 'desire_style':
      return 'arzu';
    case 'relational_pattern_bundle':
      return 'ilişki';
    case 'visible_power':
      return 'görünür';
    case 'creative_channel':
      return 'yaratım';
    case 'protection_pattern':
      return 'savunma';
    case 'retreat_recharge':
      return 'çekilme';
    case 'control_vs_flow':
      return 'kontrol';
    default:
      return '';
  }
}

/// Bottom-right meta — chips ilki, yoksa astro kaynağın son öğesi.
String _bottomRightMeta(LayeredKartData k) {
  for (final c in k.chips) {
    if (c.trim().isNotEmpty && c.length <= 18) return c.trim();
  }
  if (k.astroSources.length >= 3) {
    final last = k.astroSources.last.trim();
    if (last.isNotEmpty && last.length <= 18) return last;
  }
  return '';
}

String _familyShortLabel(String? family) {
  switch (family) {
    case 'self_definition':
      return 'kimlik';
    case 'mind_mechanics':
      return 'zihin';
    case 'outer_inner_split':
      return 'eksen';
    case 'contradiction_core':
      return 'gerilim';
    case 'tone_signature':
      return 'ton';
    case 'placement_signature':
      return 'yerleşim';
    case 'intimacy_guard':
      return 'yakınlık';
    case 'desire_style':
      return 'arzu';
    case 'relational_pattern_bundle':
      return 'ilişki';
    case 'visible_power':
      return 'görünür';
    case 'creative_channel':
      return 'yaratım';
    case 'protection_pattern':
      return 'savunma';
    case 'retreat_recharge':
      return 'çekilme';
    case 'control_vs_flow':
      return 'kontrol';
    default:
      return 'kart';
  }
}

_Illust _toInternalIllust(LayeredKartIllust k) {
  switch (k) {
    case LayeredKartIllust.stellium:
      return _Illust.stellium;
    case LayeredKartIllust.square:
      return _Illust.square;
    case LayeredKartIllust.conj:
      return _Illust.conj;
    case LayeredKartIllust.past:
      return _Illust.past;
    case LayeredKartIllust.nn:
      return _Illust.nn;
    case LayeredKartIllust.opening:
      return _Illust.opening;
  }
}

_KartTone _toInternalTone(LayeredKartTone t) {
  switch (t) {
    case LayeredKartTone.lav:
      return _KartTone.lav;
    case LayeredKartTone.lime:
      return _KartTone.lime;
    case LayeredKartTone.peach:
      return _KartTone.peach;
    case LayeredKartTone.blush:
      return _KartTone.blush;
    case LayeredKartTone.limeFull:
      return _KartTone.limeFull;
    case LayeredKartTone.grey:
      return _KartTone.grey;
  }
}

/// Embedded mode için ince axis tab şeridi — `_HeaderBlock`'taki dış kart
/// yapısı olmadan sadece 4 eksen tab'ını gösterir.
class _AxisTabBar extends StatelessWidget {
  const _AxisTabBar({
    required this.axes,
    required this.currentAxis,
    required this.onAxisChanged,
  });

  final List<_Axis> axes;
  final int currentAxis;
  final ValueChanged<int> onAxisChanged;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: const BoxDecoration(
        color: _ToColors.paperPure,
        border: Border(bottom: BorderSide(color: _ToColors.hairline)),
      ),
      padding: const EdgeInsets.symmetric(horizontal: 4),
      child: Row(
        children: [
          for (var i = 0; i < axes.length; i++)
            Expanded(
              child: GestureDetector(
                onTap: () => onAxisChanged(i),
                behavior: HitTestBehavior.opaque,
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 180),
                  padding: const EdgeInsets.symmetric(vertical: 10),
                  decoration: BoxDecoration(
                    border: Border(
                      bottom: BorderSide(
                        color: currentAxis == i
                            ? _ToColors.ink
                            : Colors.transparent,
                        width: 2,
                      ),
                    ),
                  ),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        axes[i].eye,
                        style: TextStyle(
                          fontFamily: _ToFonts.mono,
                          fontSize: 7.5,
                          letterSpacing: 0.4,
                          color: currentAxis == i
                              ? _ToColors.limeDeep
                              : _ToColors.silver,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        axes[i].label,
                        style: TextStyle(
                          fontFamily: _ToFonts.body,
                          fontSize: 10.5,
                          letterSpacing: -0.05,
                          color: currentAxis == i
                              ? _ToColors.ink
                              : _ToColors.mist,
                        ),
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

class _EmptyAxisNote extends StatelessWidget {
  const _EmptyAxisNote();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(20, 22, 20, 22),
      decoration: BoxDecoration(
        color: _ToColors.cardGrey.withValues(alpha: 0.4),
        borderRadius: BorderRadius.circular(14),
      ),
      child: const Text(
        'Bu eksende kart henüz hazır değil.',
        textAlign: TextAlign.center,
        style: TextStyle(
          fontFamily: _ToFonts.body,
          fontSize: 12.5,
          color: _ToColors.mist,
          height: 1.5,
        ),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════
// Palette + fonts (mirrors :root vars from tamokuma v2 HTML)
// ═══════════════════════════════════════════════════════════════════

class _ToColors {
  static const ink = Color(0xFF0E0E10);
  static const mist = Color(0xFF888888);
  static const silver = Color(0xFFB0B0B0);
  static const hairline = Color(0x1A000000);
  static const paperPure = Color(0xFFFFFFFF);
  static const cardGrey = Color(0xFFECECEA);
  static const lime = Color(0xFFCAFF4D);
  static const limeText = Color(0xFF1A3300);
  static const limeDeep = Color(0xFF5A8E10);
  static const limeCard = Color(0xFFE8F5C4);
  static const lavDeep = Color(0xFF534AB7);
  static const lavCard = Color(0xFFE0DCF5);
  static const blushDeep = Color(0xFFC76FA0);
  static const blushCard = Color(0xFFFADCEC);
  static const peachDeep = Color(0xFFC97A2E);
  static const peachCard = Color(0xFFFADBB8);
}

class _ToFonts {
  static const display = 'Fraunces';
  static const body = 'Inter';
  static const mono = 'Space Mono';
}

// ═══════════════════════════════════════════════════════════════════
// Models
// ═══════════════════════════════════════════════════════════════════

enum _KartTone { grey, lav, lime, peach, blush, limeFull }

enum _Illust { stellium, square, conj, past, nn, opening }

class _Axis {
  const _Axis({required this.eye, required this.label, required this.headerEye});
  final String eye;
  final String label;
  final String headerEye;
}

class _KartData {
  const _KartData({
    required this.indexEye,
    required this.title,
    required this.subtitle,
    required this.topRight,
    required this.botLeft,
    required this.botRight,
    required this.illust,
    required this.tone,
  });

  final String indexEye; // "01 stellium"
  final String title; // bold strong text
  final String subtitle; // small label below
  final String topRight; // single or multi-line
  final String botLeft;
  final String botRight;
  final _Illust illust;
  final _KartTone tone;
}

class _IntroData {
  const _IntroData({required this.quote, required this.quoteEm, required this.sub});
  final String quote; // first line
  final String quoteEm; // italic line second
  final String sub; // subtitle line
}

// ═══════════════════════════════════════════════════════════════════
// Mock content per axis
// ═══════════════════════════════════════════════════════════════════

_IntroData _mockIntroForAxis(int axis) {
  switch (axis) {
    case 0:
      return const _IntroData(
        quote: 'Taşıyabilirim, dersin.',
        quoteEm: 'Çoğu zaman haklısın.',
        sub: 'Beş gezegen tek evde. Sorumluluk sende bir arzu değil, bir iç ses.',
      );
    case 1:
      return const _IntroData(
        quote: 'Önce güven,',
        quoteEm: 'sonra her şey.',
        sub: 'İlişkide adım atmadan önce zemini ölçersin. Yavaş ama derin.',
      );
    case 2:
      return const _IntroData(
        quote: 'İşin senin için',
        quoteEm: 'bir ifade biçimi.',
        sub: 'Yapıyı kurar, sürdürür, ondan anlam çıkarırsın.',
      );
    default:
      return const _IntroData(
        quote: 'Görmek istemediğin yer,',
        quoteEm: 'sana en çok öğreten yer.',
        sub: 'Gölge — kaçtığın değil, henüz adlandıramadığın güç.',
      );
  }
}

String _mockNextTagline(String label) {
  switch (label) {
    case 'İlişki':
      return 'önce güven';
    case 'Kariyer':
      return 'yapı kurmak';
    case 'Gölge':
      return 'görmediğin güç';
    case 'Kimlik':
    default:
      return 'iç ses';
  }
}

List<_KartData> _mockCardsForAxis(int axis) {
  switch (axis) {
    case 0:
      return const [
        _KartData(
          indexEye: '01 stellium',
          title: '01 stellium',
          subtitle: 'beş gezegen',
          topRight: '1H · CAP',
          botLeft: 'tek evde 5',
          botRight: '2% nadir',
          illust: _Illust.stellium,
          tone: _KartTone.lav,
        ),
        _KartData(
          indexEye: '02 gerilim',
          title: '02 gerilim',
          subtitle: 'içinde sürekli ses',
          topRight: 'ASC □ SAT\n0°00′',
          botLeft: 'tam kare',
          botRight: '1H ↔ 3H',
          illust: _Illust.square,
          tone: _KartTone.lav,
        ),
        _KartData(
          indexEye: '03 zihin',
          title: '03 zihin',
          subtitle: 'düşünmen ve olman',
          topRight: 'SUN ☌ MER\n0°45′',
          botLeft: 'kavuşum',
          botRight: 'CAP · 1H',
          illust: _Illust.conj,
          tone: _KartTone.lime,
        ),
        _KartData(
          indexEye: '04 geçmiş',
          title: '04 geçmiş',
          subtitle: 'konuşmanın bedeli vardı',
          topRight: 'SAT 3H\nSN ARI',
          botLeft: '3 katman',
          botRight: 'cause',
          illust: _Illust.past,
          tone: _KartTone.lav,
        ),
        _KartData(
          indexEye: '05 yönelim',
          title: '05 yönelim',
          subtitle: 'yalnız değil — birlikte',
          topRight: 'NN LIB\n9H · 3°15′',
          botLeft: 'kuzey düğüm',
          botRight: 'anlam',
          illust: _Illust.nn,
          tone: _KartTone.peach,
        ),
        _KartData(
          indexEye: '06 açılan kapı',
          title: '06 açılan kapı',
          subtitle: 'küçültmeden paylaş',
          topRight: '1H → 7TH',
          botLeft: 'potansiyel',
          botRight: 'izin ver',
          illust: _Illust.opening,
          tone: _KartTone.limeFull,
        ),
      ];
    case 1:
      return const [
        _KartData(
          indexEye: '01 yakınlık',
          title: '01 yakınlık',
          subtitle: 'önce duvar, sonra kapı',
          topRight: 'VEN 12H',
          botLeft: 'gizli alan',
          botRight: 'SAG · 12H',
          illust: _Illust.opening,
          tone: _KartTone.blush,
        ),
        _KartData(
          indexEye: '02 zemin',
          title: '02 zemin',
          subtitle: 'güven inşası',
          topRight: 'MOO △ VEN\n0°14′',
          botLeft: 'trine',
          botRight: '8H ↔ 12H',
          illust: _Illust.conj,
          tone: _KartTone.lime,
        ),
        _KartData(
          indexEye: '03 sınır',
          title: '03 sınır',
          subtitle: 'yakınla mesafe arası',
          topRight: 'SAT 3H',
          botLeft: 'ölçü',
          botRight: 'ARI · 3H',
          illust: _Illust.square,
          tone: _KartTone.lav,
        ),
        _KartData(
          indexEye: '04 yönelim',
          title: '04 yönelim',
          subtitle: 'birlikte öğren',
          topRight: 'NN LIB',
          botLeft: 'kuzey düğüm',
          botRight: 'partner',
          illust: _Illust.nn,
          tone: _KartTone.peach,
        ),
      ];
    case 2:
      return const [
        _KartData(
          indexEye: '01 yapı',
          title: '01 yapı',
          subtitle: 'omurga senin işin',
          topRight: 'JUP CAP\n1H',
          botLeft: 'genişleme',
          botRight: '2% stellium',
          illust: _Illust.stellium,
          tone: _KartTone.peach,
        ),
        _KartData(
          indexEye: '02 ifade',
          title: '02 ifade',
          subtitle: 'düşün, kur, paylaş',
          topRight: 'SUN ☌ MER',
          botLeft: 'kavuşum',
          botRight: 'CAP · 1H',
          illust: _Illust.conj,
          tone: _KartTone.lime,
        ),
        _KartData(
          indexEye: '03 disiplin',
          title: '03 disiplin',
          subtitle: 'iç ses, dış sonuç',
          topRight: 'SAT 3H\n△ PLU',
          botLeft: 'trine',
          botRight: '3H ↔ 11H',
          illust: _Illust.past,
          tone: _KartTone.lav,
        ),
        _KartData(
          indexEye: '04 açılım',
          title: '04 açılım',
          subtitle: 'kapı açık',
          topRight: '10H',
          botLeft: 'potansiyel',
          botRight: 'görünür ol',
          illust: _Illust.opening,
          tone: _KartTone.limeFull,
        ),
      ];
    default:
      return const [
        _KartData(
          indexEye: '01 ay',
          title: '01 ay',
          subtitle: 'duyulmamış öfke',
          topRight: 'MOO LEO\n8H',
          botLeft: 'gölge',
          botRight: '8H',
          illust: _Illust.past,
          tone: _KartTone.blush,
        ),
        _KartData(
          indexEye: '02 lilith',
          title: '02 lilith',
          subtitle: 'reddedilen taraf',
          topRight: 'LIL 8H',
          botLeft: 'arkaik',
          botRight: 'sahiplen',
          illust: _Illust.square,
          tone: _KartTone.lav,
        ),
        _KartData(
          indexEye: '03 kapı',
          title: '03 kapı',
          subtitle: 'görmediğin güç',
          topRight: 'PLU 11H',
          botLeft: 'dönüşüm',
          botRight: 'serbest',
          illust: _Illust.opening,
          tone: _KartTone.limeFull,
        ),
      ];
  }
}

// ═══════════════════════════════════════════════════════════════════
// Header (back + title + axis tabs)
// ═══════════════════════════════════════════════════════════════════

class _HeaderBlock extends StatelessWidget {
  const _HeaderBlock({
    required this.displayName,
    required this.axes,
    required this.currentAxis,
    required this.onAxisChanged,
  });

  final String displayName;
  final List<_Axis> axes;
  final int currentAxis;
  final ValueChanged<int> onAxisChanged;

  @override
  Widget build(BuildContext context) {
    final parts = displayName.trim().split(' ');
    final first = parts.isNotEmpty ? parts.first : displayName;
    final rest = parts.length > 1 ? parts.sublist(1).join(' ') : '';

    return Container(
      decoration: const BoxDecoration(
        color: _ToColors.paperPure,
        border: Border(bottom: BorderSide(color: _ToColors.hairline)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(12, 12, 12, 10),
            child: Row(
              children: [
                Container(
                  width: 30,
                  height: 30,
                  alignment: Alignment.center,
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Icon(
                    Icons.chevron_left,
                    size: 18,
                    color: _ToColors.ink,
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'TAM OKUMA',
                        style: TextStyle(
                          fontFamily: _ToFonts.mono,
                          fontSize: 8,
                          color: _ToColors.mist,
                          letterSpacing: 1,
                          height: 1,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text.rich(
                        TextSpan(
                          children: [
                            TextSpan(
                              text: '$first ',
                              style: const TextStyle(
                                fontFamily: _ToFonts.body,
                                fontSize: 14,
                                color: _ToColors.ink,
                                fontWeight: FontWeight.w500,
                                letterSpacing: -0.2,
                                height: 1,
                              ),
                            ),
                            if (rest.isNotEmpty)
                              TextSpan(
                                text: rest,
                                style: const TextStyle(
                                  fontFamily: _ToFonts.display,
                                  fontStyle: FontStyle.italic,
                                  fontSize: 14,
                                  color: _ToColors.ink,
                                  fontWeight: FontWeight.w400,
                                  height: 1,
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
          ),
          Container(
            decoration: const BoxDecoration(
              border: Border(top: BorderSide(color: _ToColors.hairline)),
            ),
            padding: const EdgeInsets.symmetric(horizontal: 4),
            child: Row(
              children: [
                for (var i = 0; i < axes.length; i++)
                  Expanded(
                    child: GestureDetector(
                      onTap: () => onAxisChanged(i),
                      behavior: HitTestBehavior.opaque,
                      child: AnimatedContainer(
                        duration: const Duration(milliseconds: 180),
                        padding: const EdgeInsets.symmetric(vertical: 10),
                        decoration: BoxDecoration(
                          border: Border(
                            bottom: BorderSide(
                              color: currentAxis == i
                                  ? _ToColors.ink
                                  : Colors.transparent,
                              width: 2,
                            ),
                          ),
                        ),
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Text(
                              axes[i].eye,
                              style: TextStyle(
                                fontFamily: _ToFonts.mono,
                                fontSize: 7.5,
                                letterSpacing: 0.4,
                                color: currentAxis == i
                                    ? _ToColors.limeDeep
                                    : _ToColors.silver,
                              ),
                            ),
                            const SizedBox(height: 2),
                            Text(
                              axes[i].label,
                              style: TextStyle(
                                fontFamily: _ToFonts.body,
                                fontSize: 10.5,
                                letterSpacing: -0.05,
                                color: currentAxis == i
                                    ? _ToColors.ink
                                    : _ToColors.mist,
                              ),
                            ),
                          ],
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

// ═══════════════════════════════════════════════════════════════════
// Gallery intro (eyebrow + quote + divider + sub)
// ═══════════════════════════════════════════════════════════════════

class _GalleryIntro extends StatelessWidget {
  const _GalleryIntro({
    required this.eyebrow,
    required this.quote,
    required this.quoteEm,
    required this.sub,
  });

  final String eyebrow;
  final String quote;
  final String quoteEm;
  final String sub;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(20, 26, 20, 22),
      decoration: const BoxDecoration(
        color: _ToColors.paperPure,
        border: Border(bottom: BorderSide(color: _ToColors.hairline)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          Text(
            eyebrow.toUpperCase(),
            style: const TextStyle(
              fontFamily: _ToFonts.mono,
              fontSize: 8.5,
              letterSpacing: 1.2,
              color: _ToColors.mist,
            ),
          ),
          const SizedBox(height: 12),
          Text.rich(
            TextSpan(
              children: [
                TextSpan(
                  text: '$quote\n',
                  style: const TextStyle(
                    fontFamily: _ToFonts.body,
                    fontSize: 24,
                    fontWeight: FontWeight.w400,
                    letterSpacing: -0.5,
                    color: _ToColors.ink,
                    height: 1.2,
                  ),
                ),
                TextSpan(
                  text: quoteEm,
                  style: const TextStyle(
                    fontFamily: _ToFonts.display,
                    fontStyle: FontStyle.italic,
                    fontSize: 24,
                    fontWeight: FontWeight.w400,
                    letterSpacing: -0.5,
                    color: _ToColors.ink,
                    height: 1.2,
                  ),
                ),
              ],
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 12),
          Container(width: 24, height: 1.5, color: _ToColors.ink),
          const SizedBox(height: 10),
          ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 280),
            child: Text(
              sub,
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontFamily: _ToFonts.body,
                fontSize: 11,
                color: _ToColors.mist,
                height: 1.6,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════
// Pressable kart with tap scale animation (translate-y from web→scale on mobile)
// ═══════════════════════════════════════════════════════════════════

class _Kart extends StatefulWidget {
  const _Kart({required this.card, required this.onTap});
  final _KartData card;
  final VoidCallback onTap;

  @override
  State<_Kart> createState() => _KartState();
}

class _KartState extends State<_Kart> {
  bool _pressed = false;

  @override
  Widget build(BuildContext context) {
    final tone = _kartPalette(widget.card.tone);
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
            aspectRatio: 16 / 9,
            child: Container(
              clipBehavior: Clip.antiAlias,
              decoration: BoxDecoration(
                color: tone.bg,
                borderRadius: BorderRadius.circular(22),
              ),
              padding: const EdgeInsets.fromLTRB(18, 14, 18, 14),
              child: Column(
                children: [
                  // top row
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Expanded(
                        child: Text.rich(
                          TextSpan(
                            children: [
                              TextSpan(
                                text: widget.card.title,
                                style: TextStyle(
                                  fontFamily: _ToFonts.mono,
                                  fontSize: 10.5,
                                  fontWeight: FontWeight.w700,
                                  height: 1.35,
                                  color: tone.strong,
                                ),
                              ),
                              const TextSpan(text: '\n'),
                              TextSpan(
                                text: widget.card.subtitle,
                                style: TextStyle(
                                  fontFamily: _ToFonts.mono,
                                  fontSize: 10.5,
                                  height: 1.35,
                                  color: tone.label,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Text(
                        widget.card.topRight,
                        textAlign: TextAlign.right,
                        style: TextStyle(
                          fontFamily: _ToFonts.mono,
                          fontSize: 10,
                          color: tone.meta,
                          letterSpacing: 0.2,
                          height: 1.25,
                        ),
                      ),
                    ],
                  ),
                  // illustration
                  Expanded(
                    child: Padding(
                      padding: const EdgeInsets.symmetric(vertical: 6),
                      child: Center(
                        child: SizedBox(
                          width: 92,
                          height: 68,
                          child: SvgPicture.string(
                            _illustSvg(widget.card.illust),
                            colorFilter: ColorFilter.mode(
                              tone.illust,
                              BlendMode.srcIn,
                            ),
                            fit: BoxFit.contain,
                          ),
                        ),
                      ),
                    ),
                  ),
                  // bottom row
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      Expanded(
                        child: Text(
                          widget.card.botLeft,
                          style: TextStyle(
                            fontFamily: _ToFonts.mono,
                            fontSize: 10.5,
                            color: tone.botLeft,
                          ),
                        ),
                      ),
                      Text(
                        widget.card.botRight,
                        textAlign: TextAlign.right,
                        style: TextStyle(
                          fontFamily: _ToFonts.mono,
                          fontSize: 10,
                          color: tone.meta,
                          letterSpacing: 0.2,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _KartTonePalette {
  const _KartTonePalette({
    required this.bg,
    required this.strong,
    required this.label,
    required this.meta,
    required this.botLeft,
    required this.illust,
  });
  final Color bg;
  final Color strong;
  final Color label;
  final Color meta;
  final Color botLeft;
  final Color illust;
}

_KartTonePalette _kartPalette(_KartTone tone) {
  switch (tone) {
    case _KartTone.lav:
      return const _KartTonePalette(
        bg: _ToColors.lavCard,
        strong: _ToColors.lavDeep,
        label: _ToColors.mist,
        meta: _ToColors.mist,
        botLeft: _ToColors.lavDeep,
        illust: _ToColors.lavDeep,
      );
    case _KartTone.lime:
      return const _KartTonePalette(
        bg: _ToColors.limeCard,
        strong: _ToColors.limeDeep,
        label: _ToColors.mist,
        meta: _ToColors.mist,
        botLeft: _ToColors.limeDeep,
        illust: _ToColors.limeDeep,
      );
    case _KartTone.peach:
      return const _KartTonePalette(
        bg: _ToColors.peachCard,
        strong: _ToColors.peachDeep,
        label: _ToColors.mist,
        meta: _ToColors.mist,
        botLeft: _ToColors.peachDeep,
        illust: _ToColors.peachDeep,
      );
    case _KartTone.blush:
      return const _KartTonePalette(
        bg: _ToColors.blushCard,
        strong: _ToColors.blushDeep,
        label: _ToColors.mist,
        meta: _ToColors.mist,
        botLeft: _ToColors.blushDeep,
        illust: _ToColors.blushDeep,
      );
    case _KartTone.limeFull:
      return const _KartTonePalette(
        bg: _ToColors.lime,
        strong: _ToColors.limeText,
        label: Color(0xA61A3300),
        meta: Color(0x8C1A3300),
        botLeft: _ToColors.limeText,
        illust: _ToColors.limeText,
      );
    case _KartTone.grey:
      return const _KartTonePalette(
        bg: _ToColors.cardGrey,
        strong: _ToColors.lavDeep,
        label: _ToColors.mist,
        meta: _ToColors.mist,
        botLeft: _ToColors.ink,
        illust: _ToColors.ink,
      );
  }
}

// ═══════════════════════════════════════════════════════════════════
// Footer (progress + next CTA)
// ═══════════════════════════════════════════════════════════════════

class _GalleryFooter extends StatelessWidget {
  const _GalleryFooter({
    required this.axisLabel,
    required this.cardCount,
    required this.currentIndex,
    required this.total,
    required this.nextEye,
    required this.nextLabel,
    required this.nextTagline,
    required this.onNext,
  });

  final String axisLabel;
  final int cardCount;
  final int currentIndex;
  final int total;
  final String nextEye;
  final String nextLabel;
  final String nextTagline;
  final VoidCallback onNext;

  @override
  Widget build(BuildContext context) {
    final progress = (currentIndex + 1) / total;
    return Container(
      padding: const EdgeInsets.fromLTRB(20, 18, 20, 22),
      decoration: const BoxDecoration(
        color: _ToColors.paperPure,
        border: Border(top: BorderSide(color: _ToColors.hairline)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text.rich(
                TextSpan(
                  children: [
                    TextSpan(
                      text: axisLabel,
                      style: const TextStyle(
                        fontFamily: _ToFonts.mono,
                        fontSize: 8.5,
                        color: _ToColors.ink,
                        fontWeight: FontWeight.w500,
                        letterSpacing: 0.3,
                      ),
                    ),
                    TextSpan(
                      text: ' · $cardCount kart',
                      style: const TextStyle(
                        fontFamily: _ToFonts.mono,
                        fontSize: 8.5,
                        color: _ToColors.mist,
                        letterSpacing: 0.3,
                      ),
                    ),
                  ],
                ),
              ),
              Text(
                '${(currentIndex + 1).toString().padLeft(2, '0')} / ${total.toString().padLeft(2, '0')}',
                style: const TextStyle(
                  fontFamily: _ToFonts.mono,
                  fontSize: 8.5,
                  color: _ToColors.mist,
                  letterSpacing: 0.3,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          ClipRRect(
            borderRadius: BorderRadius.circular(1),
            child: Stack(
              children: [
                Container(height: 2, color: _ToColors.hairline),
                FractionallySizedBox(
                  widthFactor: progress.clamp(0.05, 1.0),
                  child: Container(height: 2, color: _ToColors.lime),
                ),
              ],
            ),
          ),
          const SizedBox(height: 18),
          GestureDetector(
            onTap: onNext,
            behavior: HitTestBehavior.opaque,
            child: Container(
              padding: const EdgeInsets.fromLTRB(16, 12, 12, 12),
              decoration: BoxDecoration(
                color: _ToColors.ink,
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: _ToColors.ink),
              ),
              child: Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'SIRADAKİ · $nextEye',
                          style: const TextStyle(
                            fontFamily: _ToFonts.mono,
                            fontSize: 8,
                            color: Color(0x80FFFFFF),
                            letterSpacing: 0.5,
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text.rich(
                          TextSpan(
                            children: [
                              TextSpan(
                                text: '$nextLabel ',
                                style: const TextStyle(
                                  fontFamily: _ToFonts.body,
                                  fontSize: 13.5,
                                  color: Colors.white,
                                  letterSpacing: -0.1,
                                  fontWeight: FontWeight.w400,
                                ),
                              ),
                              TextSpan(
                                text: '— ',
                                style: const TextStyle(
                                  fontFamily: _ToFonts.display,
                                  fontStyle: FontStyle.italic,
                                  fontSize: 13.5,
                                  color: _ToColors.lime,
                                ),
                              ),
                              TextSpan(
                                text: nextTagline,
                                style: const TextStyle(
                                  fontFamily: _ToFonts.body,
                                  fontSize: 13.5,
                                  color: Colors.white,
                                  letterSpacing: -0.1,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                  Container(
                    width: 28,
                    height: 28,
                    alignment: Alignment.center,
                    decoration: const BoxDecoration(
                      color: _ToColors.lime,
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(
                      Icons.arrow_forward,
                      size: 14,
                      color: _ToColors.limeText,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════
// Hand-drawn illustration SVGs (extracted 1:1 from tamokuma v2 HTML)
// ═══════════════════════════════════════════════════════════════════

String _illustSvg(_Illust kind) {
  switch (kind) {
    case _Illust.stellium:
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
    case _Illust.square:
      return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 60">'
          '<g stroke="currentColor" stroke-width="2.2" fill="none" stroke-linecap="round" stroke-linejoin="round">'
          '<path d="M22 14 Q20 14 20 16 L20 44 Q20 46 22 46 L58 46 Q60 46 60 44 L60 16 Q60 14 58 14 Z"/>'
          '<path d="M28 22 L52 38"/>'
          '<path d="M52 22 L28 38"/>'
          '</g></svg>';
    case _Illust.conj:
      return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 60">'
          '<g stroke="currentColor" stroke-width="2.2" fill="none" stroke-linecap="round">'
          '<circle cx="32" cy="30" r="14"/>'
          '<circle cx="48" cy="30" r="14"/>'
          '<circle cx="40" cy="30" r="2.5" fill="currentColor"/>'
          '</g></svg>';
    case _Illust.past:
      return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 60">'
          '<g stroke="currentColor" stroke-width="2.2" fill="none" stroke-linecap="round" stroke-linejoin="round">'
          '<path d="M58 18 Q30 14 24 30 Q22 44 38 46 Q52 46 52 36 Q52 28 44 28"/>'
          '<path d="M55 14 L58 18 L54 22"/>'
          '</g></svg>';
    case _Illust.nn:
      return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 60">'
          '<g stroke="currentColor" stroke-width="2.2" fill="none" stroke-linecap="round" stroke-linejoin="round">'
          '<path d="M16 44 Q16 18 40 18 Q64 18 64 44"/>'
          '<circle cx="16" cy="46" r="3"/>'
          '<circle cx="64" cy="46" r="3"/>'
          '<path d="M40 18 L40 12"/>'
          '<path d="M36 14 L40 12 L44 14"/>'
          '</g></svg>';
    case _Illust.opening:
      return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 60">'
          '<g stroke="currentColor" stroke-width="2.2" fill="none" stroke-linecap="round" stroke-linejoin="round">'
          '<path d="M28 14 L28 46 L48 46 L48 14 Z"/>'
          '<path d="M48 14 L62 20 L62 40 L48 46"/>'
          '<circle cx="44" cy="30" r="1.5" fill="currentColor"/>'
          '</g></svg>';
  }
}
