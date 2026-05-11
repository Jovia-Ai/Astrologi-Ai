import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'package:mobile/app/timing/turkish_text.dart';
import 'package:mobile/design/widgets/jovia_assets.dart';

/// Library shadow cümleleri tipik markerlar ile başlar:
///   "Bazen…", "Gerilim yükseldiğinde…", "Denge bozulduğunda…",
///   "Bozulduğunda…", "Zorlandığında…"
///
/// Bu marker'lardan başlayan cümle BODY'NİN GERİSİNİ shadow olarak
/// ayırır. Hero/Mechanism slide'da gösterilen body bu marker'a kadar
/// olan kısım. Sonrası "Aynadaki halin" reframe slide'ında.
const List<String> _shadowMarkers = <String>[
  'Bazen ',
  'Bazen,',
  'Bazen.',
  'Gerilim ',
  'Denge ',
  'Bozulduğunda',
  'Zorlandığında',
  'Sıkıştığında',
  'Stres ',
];

/// Body'yi (mainBody, shadowText) olarak böler.
/// shadowText boş ise body'de shadow marker'ı yok demektir.
({String mainBody, String shadowText}) _splitBodyShadow(String body) {
  final trimmed = body.trim();
  if (trimmed.isEmpty) return (mainBody: '', shadowText: '');

  // Cümle bazında tara — Bir cümle marker ile başlıyorsa o cümle ve
  // sonrası shadow.
  final sentences = trimmed.split(RegExp(r'(?<=[.!?…])\s+'));
  for (var i = 0; i < sentences.length; i++) {
    final s = sentences[i].trimLeft();
    for (final marker in _shadowMarkers) {
      if (s.startsWith(marker)) {
        final main = sentences.sublist(0, i).join(' ').trim();
        final shadow = sentences.sublist(i).join(' ').trim();
        return (mainBody: main, shadowText: shadow);
      }
    }
  }
  return (mainBody: trimmed, shadowText: '');
}

/// Main body'yi cümle bazlı slide-paragraflarına böler.
///
/// Backend tipik olarak `aura + trait + drive + gift` cümlelerini tek
/// paragraf string olarak gönderiyor. Story-style slide deneyimi için her
/// cümle kendi slide'ında — kullanıcı az şey, derin şey okur.
///
/// Sadece çok kısa cümleleri (<35 char) sonrakine ekler — çoğu cümle kendi
/// slide'ında kalır. Story-post deneyimi: her slide'da bir an, bir his.
List<String> _splitBodyIntoSlides(String body) {
  final trimmed = body.trim();
  if (trimmed.isEmpty) return const [];
  final raw = trimmed
      .split(RegExp(r'(?<=[.!?…])\s+'))
      .where((s) => s.trim().isNotEmpty)
      .map((s) => s.trim())
      .toList();
  if (raw.isEmpty) return const [];

  final groups = <String>[];
  var buffer = '';
  for (final sentence in raw) {
    if (buffer.isEmpty) {
      buffer = sentence;
    } else if (buffer.length < 35) {
      buffer = '$buffer $sentence';
    } else {
      groups.add(buffer);
      buffer = sentence;
    }
  }
  if (buffer.isNotEmpty) groups.add(buffer);
  return groups;
}

/// Slayt tonu — her slide kendi accent'ten türetilen pastel zeminle gelir,
/// tipi (hero / body / shadow / growth / context) zemin yoğunluğunu etkiler.
enum _SlideKind { hero, body, mechanism, layer, shadow, growth, context }

Color _slideBg(Color accent, _SlideKind kind) {
  switch (kind) {
    case _SlideKind.hero:
      return accent.withValues(alpha: 0.16);
    case _SlideKind.body:
      return accent.withValues(alpha: 0.10);
    case _SlideKind.mechanism:
      return accent.withValues(alpha: 0.08);
    case _SlideKind.layer:
      return accent.withValues(alpha: 0.07);
    case _SlideKind.shadow:
      // Shadow ayrı tonda — accent'in soğuk gri-mavi karışımı, daha mahrem his.
      return const Color(0xFFEFEDF2);
    case _SlideKind.growth:
      return const Color(0xFFFAFFEC); // çok hafif lime
    case _SlideKind.context:
      return const Color(0xFFF7F7F4);
  }
}

@immutable
class ProfileSheetLayer {
  const ProfileSheetLayer({
    required this.placement,
    required this.headline,
    this.body = '',
    this.highlight = '',
  });

  final String placement;
  final String headline;
  final String body;
  final String highlight;
}

@immutable
class ProfileDetailSheetData {
  const ProfileDetailSheetData({
    required this.eyebrow,
    required this.headline,
    this.body = '',
    this.placement = '',
    this.accent = const Color(0xFFCAFF4D),
    this.accentInk = const Color(0xFF1A3300),
    this.highlight = '',
    this.chips = const <String>[],
    this.details = const <String>[],
    this.extraLayers = const <ProfileSheetLayer>[],
    this.extraLayersTitle = 'DAHA DA GEÇMİŞE',
    this.growthNote = '',
    this.ctaLabel,
    this.onCta,
    this.illustration,
  });

  final String eyebrow;
  final String headline;
  final String body;
  final String placement;
  final Color accent;
  final Color accentInk;
  final String highlight;
  final List<String> chips;
  final List<String> details;
  final List<ProfileSheetLayer> extraLayers;
  final String extraLayersTitle;
  final String growthNote;
  final String? ctaLabel;
  final VoidCallback? onCta;

  /// Hero slide üstünde gösterilen pastel banddaki illüstrasyon.
  /// `null` ise illüstrasyon band gizlenir (geriye dönük uyumluluk).
  final JoviaIllustrationAsset? illustration;
}

Future<void> showProfileDetailSheet(
  BuildContext context,
  ProfileDetailSheetData data,
) {
  HapticFeedback.selectionClick();
  return Navigator.of(context).push(
    PageRouteBuilder<void>(
      opaque: false,
      barrierColor: Colors.black54,
      transitionDuration: const Duration(milliseconds: 320),
      reverseTransitionDuration: const Duration(milliseconds: 240),
      pageBuilder: (_, a, b) => _ProfileDetailPage(data: data),
      transitionsBuilder: (_, animation, b, child) {
        final curved = CurvedAnimation(
          parent: animation,
          curve: Curves.easeOutCubic,
          reverseCurve: Curves.easeInCubic,
        );
        final offset = Tween<Offset>(
          begin: const Offset(0, 0.06),
          end: Offset.zero,
        ).animate(curved);
        return FadeTransition(
          opacity: curved,
          child: SlideTransition(position: offset, child: child),
        );
      },
    ),
  );
}

class _ProfileDetailPage extends StatefulWidget {
  const _ProfileDetailPage({required this.data});

  final ProfileDetailSheetData data;

  @override
  State<_ProfileDetailPage> createState() => _ProfileDetailPageState();
}

class _ProfileDetailPageState extends State<_ProfileDetailPage> {
  late final PageController _controller = PageController();
  int _index = 0;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  List<Widget> _buildSlides() {
    final data = widget.data;
    final shadowSplit = _splitBodyShadow(data.body);
    final mainSentences = _splitBodyIntoSlides(shadowSplit.mainBody);

    // İlk cümle Hero'da kalır (illüstrasyon + headline ile birlikte).
    // Geri kalan cümleler her biri kendi slide'ında — story-post mantığı.
    final leadSentence = mainSentences.isNotEmpty ? mainSentences.first : '';
    final remainingSentences = mainSentences.length > 1
        ? mainSentences.sublist(1)
        : const <String>[];

    final slides = <Widget>[
      _HeroSlide(data: data, leadSentence: leadSentence),
    ];

    // Body cümleleri — her biri kendi slide'ı. Eyebrow yumuşak ("İÇERİDE",
    // "ALTINDAKİ" gibi) — kullanıcı kart başlığı + her bir his/an arasında
    // dolaşır. Hero ile aynı accent ile.
    for (var i = 0; i < remainingSentences.length; i++) {
      slides.add(
        _BodySlide(
          data: data,
          text: remainingSentences[i],
          slideIndex: i,
          totalSlides: remainingSentences.length,
        ),
      );
    }

    // Backend bullet listesi (rare — affects_you'da rows[]) ayrıca slide.
    if (data.details.isNotEmpty) {
      slides.add(_MechanismSlide(data: data));
    }
    for (final layer in data.extraLayers) {
      slides.add(
        _LayerSlide(
          data: data,
          layer: layer,
          eyebrow: data.extraLayersTitle,
        ),
      );
    }
    // Shadow ayrı slide — body'de marker bulduysa "Aynadaki halin" olarak
    // göster. Profile yüzeyinde direkt görünmez, kullanıcı tap'leyip slide
    // içinden geçince görür. Reframe note ile yumuşatılır.
    if (shadowSplit.shadowText.isNotEmpty) {
      slides.add(_ShadowMirrorSlide(data: data, shadowText: shadowSplit.shadowText));
    }
    if (data.growthNote.trim().isNotEmpty) {
      slides.add(_GrowthSlide(data: data));
    }
    if (data.chips.isNotEmpty || (data.ctaLabel ?? '').trim().isNotEmpty) {
      slides.add(_ContextSlide(data: data));
    }
    return slides;
  }

  @override
  Widget build(BuildContext context) {
    final slides = _buildSlides();
    final showIndicator = slides.length > 1;
    return Scaffold(
      backgroundColor: Colors.white,
      body: Stack(
        children: [
          // Full-bleed PageView — her slayt kendi tonunu taşır.
          PageView.builder(
            controller: _controller,
            itemCount: slides.length,
            onPageChanged: (value) {
              HapticFeedback.selectionClick();
              setState(() => _index = value);
            },
            physics: const PageScrollPhysics(parent: BouncingScrollPhysics()),
            itemBuilder: (_, index) => slides[index],
          ),
          // Top bar: close + eyebrow + sayaç
          Positioned(
            top: MediaQuery.of(context).padding.top + 8,
            left: 16,
            right: 16,
            child: Row(
              children: [
                _CloseButton(onTap: () => Navigator.of(context).maybePop()),
                const Spacer(),
                _SheetEyebrow(data: widget.data),
                if (showIndicator) ...[
                  const SizedBox(width: 14),
                  _PageCounter(
                    index: _index,
                    count: slides.length,
                    accent: widget.data.accent,
                  ),
                ],
              ],
            ),
          ),
          // Alt: ince progress bar — story-post hissi
          if (showIndicator)
            Positioned(
              left: 24,
              right: 24,
              bottom: MediaQuery.of(context).padding.bottom + 24,
              child: _SlideProgressBar(
                count: slides.length,
                index: _index,
                accent: widget.data.accent,
              ),
            ),
        ],
      ),
    );
  }
}

class _SheetEyebrow extends StatelessWidget {
  const _SheetEyebrow({required this.data});

  final ProfileDetailSheetData data;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 6,
          height: 6,
          decoration: BoxDecoration(color: data.accent, shape: BoxShape.circle),
        ),
        const SizedBox(width: 8),
        Text(
          turkishToUpper(data.eyebrow),
          style: const TextStyle(
            color: Color(0xFF9A9A9A),
            fontSize: 9,
            letterSpacing: 0.9,
            fontWeight: FontWeight.w500,
          ),
        ),
      ],
    );
  }
}

/// Top-right "01 / 05" sayacı — hangi slayt'ta olduğunu net gösterir.
class _PageCounter extends StatelessWidget {
  const _PageCounter({
    required this.index,
    required this.count,
    required this.accent,
  });

  final int index;
  final int count;
  final Color accent;

  @override
  Widget build(BuildContext context) {
    final current = (index + 1).toString().padLeft(2, '0');
    final total = count.toString().padLeft(2, '0');
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.65),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFFE1E1E1)),
      ),
      child: Text.rich(
        TextSpan(
          children: [
            TextSpan(
              text: current,
              style: TextStyle(
                color: accent.computeLuminance() > 0.6
                    ? const Color(0xFF1A1A1A)
                    : accent,
                fontSize: 11,
                fontWeight: FontWeight.w600,
                letterSpacing: 0.4,
              ),
            ),
            const TextSpan(
              text: ' / ',
              style: TextStyle(
                color: Color(0xFF9A9A9A),
                fontSize: 11,
                letterSpacing: 0.4,
              ),
            ),
            TextSpan(
              text: total,
              style: const TextStyle(
                color: Color(0xFF9A9A9A),
                fontSize: 11,
                letterSpacing: 0.4,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Alt progress bar — story-post benzeri segmentli ilerleme çizgisi.
class _SlideProgressBar extends StatelessWidget {
  const _SlideProgressBar({
    required this.count,
    required this.index,
    required this.accent,
  });

  final int count;
  final int index;
  final Color accent;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        for (var i = 0; i < count; i++) ...[
          Expanded(
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 280),
              curve: Curves.easeOutCubic,
              height: 3,
              decoration: BoxDecoration(
                color: i <= index
                    ? const Color(0xFF1A1A1A).withValues(alpha: 0.78)
                    : const Color(0xFF1A1A1A).withValues(alpha: 0.14),
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ),
          if (i != count - 1) const SizedBox(width: 4),
        ],
      ],
    );
  }
}

class _CloseButton extends StatelessWidget {
  const _CloseButton({required this.onTap});

  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.white.withValues(alpha: 0.7),
      shape: const CircleBorder(side: BorderSide(color: Color(0xFFE1E1E1))),
      child: InkWell(
        customBorder: const CircleBorder(),
        onTap: onTap,
        child: const SizedBox(
          width: 34,
          height: 34,
          child: Icon(Icons.close_rounded, size: 18, color: Color(0xFF1A1A1A)),
        ),
      ),
    );
  }
}

/// Her slayt full-bleed pastel zemin + iç padding. Pattern-style story-post
/// hissi: tek odak, geniş hava, opsiyonel büyük watermark numarası.
class _SlideShell extends StatelessWidget {
  const _SlideShell({
    required this.child,
    required this.accent,
    required this.kind,
    this.watermark,
  });

  final Widget child;
  final Color accent;
  final _SlideKind kind;

  /// Sağ-üst köşede dev pastel sayı ("01", "02" vb.) — body slide'larda görünür.
  final String? watermark;

  @override
  Widget build(BuildContext context) {
    return Container(
      color: _slideBg(accent, kind),
      child: SafeArea(
        top: false,
        bottom: false,
        child: Stack(
          children: [
            if (watermark != null)
              Positioned(
                top: 78,
                right: 18,
                child: IgnorePointer(
                  child: Text(
                    watermark!,
                    style: TextStyle(
                      color: accent.withValues(alpha: 0.22),
                      fontSize: 130,
                      height: 1,
                      fontWeight: FontWeight.w300,
                      letterSpacing: -4,
                    ),
                  ),
                ),
              ),
            Padding(
              padding: const EdgeInsets.fromLTRB(28, 88, 28, 100),
              child: SingleChildScrollView(
                physics: const BouncingScrollPhysics(),
                child: ConstrainedBox(
                  constraints: BoxConstraints(
                    minHeight: MediaQuery.of(context).size.height - 240,
                  ),
                  child: child,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _HeroSlide extends StatelessWidget {
  const _HeroSlide({required this.data, this.leadSentence = ''});

  final ProfileDetailSheetData data;

  /// Body'nin Hero'da gösterilecek tek cümlesi (intro). Geri kalan cümleler
  /// `_BodySlide`'larda gösterilir.
  final String leadSentence;

  @override
  Widget build(BuildContext context) {
    final highlightVisible =
        data.highlight.trim().isNotEmpty &&
        data.headline.contains(data.highlight);
    final illust = data.illustration;
    return _SlideShell(
      accent: data.accent,
      kind: _SlideKind.hero,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.start,
        children: [
          // Hero illüstrasyonu — daha büyük, ortalı, full-bleed zeminin parçası.
          if (illust != null) ...[
            SizedBox(
              width: double.infinity,
              child: Center(
                child: JoviaIllustrationAccent(
                  asset: illust,
                  height: 124,
                  opacity: 0.95,
                ),
              ),
            ),
            const SizedBox(height: 32),
          ],
          if (data.placement.trim().isNotEmpty) ...[
            Text(
              data.placement,
              style: TextStyle(
                color: data.accent,
                fontSize: 9.5,
                letterSpacing: 0.9,
                fontWeight: FontWeight.w500,
              ),
            ),
            const SizedBox(height: 18),
          ],
          if (highlightVisible)
            _HighlightHeadline(
              text: data.headline,
              highlight: data.highlight,
              accent: data.accent,
              accentInk: data.accentInk,
              fontSize: 30,
            )
          else
            Text(
              data.headline,
              style: const TextStyle(
                color: Color(0xFF111111),
                fontSize: 30,
                height: 1.22,
                letterSpacing: -0.6,
                fontWeight: FontWeight.w400,
              ),
            ),
          if (leadSentence.trim().isNotEmpty) ...[
            const SizedBox(height: 20),
            Text(
              // Hero'da sadece intro cümlesi — geri kalan cümleler ayrı
              // slide'larda. Story-post deneyimi: az şey, derin şey.
              leadSentence,
              style: const TextStyle(
                color: Color(0xFF3F3F3F),
                fontSize: 15.5,
                height: 1.6,
                fontWeight: FontWeight.w400,
              ),
            ),
          ],
        ],
      ),
    );
  }
}

/// Hero'dan sonra her cümle için ayrı slide.
///
/// Eyebrow cümlenin pozisyonuna göre yumuşak ipuçları verir:
///   1. cümle (post-hero) → "İÇERİDE"
///   2. → "ALTINDAKİ"
///   3+ → "DEVAM"
/// — kullanıcı her slide'da yeni bir an okuyor hissi alır.
class _BodySlide extends StatelessWidget {
  const _BodySlide({
    required this.data,
    required this.text,
    required this.slideIndex,
    required this.totalSlides,
  });

  final ProfileDetailSheetData data;
  final String text;
  final int slideIndex;
  final int totalSlides;

  String get _eyebrowLabel {
    if (slideIndex == 0) return 'İÇERİDE';
    if (slideIndex == 1) return 'ALTINDAKİ';
    if (slideIndex == totalSlides - 1) return 'KAPANIŞ';
    return 'DEVAM';
  }

  String get _watermark {
    final n = slideIndex + 2; // hero=01, ilk body=02
    return n.toString().padLeft(2, '0');
  }

  @override
  Widget build(BuildContext context) {
    return _SlideShell(
      accent: data.accent,
      kind: _SlideKind.body,
      watermark: _watermark,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          _SlideTitle(label: _eyebrowLabel, accent: data.accent),
          const SizedBox(height: 28),
          // Cümle ana element — büyük editörel tipografi, slide ortasında durur.
          Text(
            text,
            style: const TextStyle(
              color: Color(0xFF1A1A1A),
              fontSize: 24,
              height: 1.4,
              letterSpacing: -0.4,
              fontWeight: FontWeight.w400,
            ),
          ),
        ],
      ),
    );
  }
}

class _MechanismSlide extends StatelessWidget {
  const _MechanismSlide({required this.data});

  final ProfileDetailSheetData data;

  @override
  Widget build(BuildContext context) {
    return _SlideShell(
      accent: data.accent,
      kind: _SlideKind.mechanism,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _SlideTitle(label: 'NASIL ÇALIŞIYOR', accent: data.accent),
          const SizedBox(height: 18),
          for (var i = 0; i < data.details.length; i++) ...[
            Text(
              data.details[i],
              style: const TextStyle(
                color: Color(0xFF262626),
                fontSize: 16,
                height: 1.6,
                fontWeight: FontWeight.w400,
              ),
            ),
            if (i != data.details.length - 1) const SizedBox(height: 18),
          ],
        ],
      ),
    );
  }
}

class _LayerSlide extends StatelessWidget {
  const _LayerSlide({
    required this.data,
    required this.layer,
    required this.eyebrow,
  });

  final ProfileDetailSheetData data;
  final ProfileSheetLayer layer;
  final String eyebrow;

  @override
  Widget build(BuildContext context) {
    return _SlideShell(
      accent: data.accent,
      kind: _SlideKind.layer,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _SlideTitle(label: eyebrow, accent: data.accent),
          const SizedBox(height: 18),
          if (layer.placement.trim().isNotEmpty) ...[
            Text(
              layer.placement,
              style: TextStyle(
                color: data.accent,
                fontSize: 9.5,
                letterSpacing: 0.9,
                fontWeight: FontWeight.w500,
              ),
            ),
            const SizedBox(height: 12),
          ],
          Text(
            layer.headline,
            style: const TextStyle(
              color: Color(0xFF111111),
              fontSize: 24,
              height: 1.3,
              letterSpacing: -0.4,
              fontWeight: FontWeight.w400,
            ),
          ),
          if (layer.body.trim().isNotEmpty) ...[
            const SizedBox(height: 14),
            Text(
              layer.body,
              style: const TextStyle(
                color: Color(0xFF3F3F3F),
                fontSize: 14.5,
                height: 1.6,
                fontWeight: FontWeight.w400,
              ),
            ),
          ],
        ],
      ),
    );
  }
}

class _GrowthSlide extends StatelessWidget {
  const _GrowthSlide({required this.data});

  final ProfileDetailSheetData data;

  @override
  Widget build(BuildContext context) {
    return _SlideShell(
      accent: data.accent,
      kind: _SlideKind.growth,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _SlideTitle(label: 'AÇILAN KAPI', accent: const Color(0xFFCAFF4D)),
          const SizedBox(height: 18),
          Text(
            data.growthNote,
            style: const TextStyle(
              color: Color(0xFF111111),
              fontSize: 22,
              height: 1.35,
              letterSpacing: -0.3,
              fontWeight: FontWeight.w400,
            ),
          ),
        ],
      ),
    );
  }
}

/// Shadow ("gölge") cümlelerini "Aynadaki halin" başlığıyla yeniden çerçeveler.
/// Patolojik teşhis tonu yerine "denge bozulduğu anlarda görünür" şeklinde
/// destek tonlu reframe sunar.
class _ShadowMirrorSlide extends StatelessWidget {
  const _ShadowMirrorSlide({required this.data, required this.shadowText});

  final ProfileDetailSheetData data;
  final String shadowText;

  @override
  Widget build(BuildContext context) {
    return _SlideShell(
      accent: data.accent,
      kind: _SlideKind.shadow,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _SlideTitle(label: 'AYNADAKİ HALİN', accent: data.accent),
          const SizedBox(height: 18),
          Text(
            shadowText,
            style: const TextStyle(
              color: Color(0xFF262626),
              fontSize: 18,
              height: 1.45,
              letterSpacing: -0.3,
              fontWeight: FontWeight.w400,
            ),
          ),
          const SizedBox(height: 22),
          Container(
            width: 28,
            height: 1.5,
            color: data.accent.withValues(alpha: 0.6),
          ),
          const SizedBox(height: 14),
          Text(
            'Bu, denge bozulduğu ya da güvende hissetmediğin anlarda su '
            'yüzüne çıkar — kim olduğunun değil, korumanın hali.',
            style: TextStyle(
              color: const Color(0xFF6F6F6F),
              fontSize: 13.5,
              height: 1.6,
              letterSpacing: -0.05,
              fontStyle: FontStyle.italic,
            ),
          ),
        ],
      ),
    );
  }
}

class _ContextSlide extends StatelessWidget {
  const _ContextSlide({required this.data});

  final ProfileDetailSheetData data;

  @override
  Widget build(BuildContext context) {
    return _SlideShell(
      accent: data.accent,
      kind: _SlideKind.context,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _SlideTitle(label: 'BU KARTIN İZLERİ', accent: data.accent),
          const SizedBox(height: 18),
          if (data.placement.trim().isNotEmpty) ...[
            Text(
              data.placement,
              style: TextStyle(
                color: data.accent,
                fontSize: 10,
                letterSpacing: 0.9,
                fontWeight: FontWeight.w500,
              ),
            ),
            const SizedBox(height: 14),
          ],
          if (data.chips.isNotEmpty)
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                for (final chip in data.chips)
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 12,
                      vertical: 7,
                    ),
                    decoration: BoxDecoration(
                      color: Colors.transparent,
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(
                        color: data.accent.withValues(alpha: 0.32),
                      ),
                    ),
                    child: Text(
                      chip,
                      style: TextStyle(
                        color: data.accentInk,
                        fontSize: 11,
                        fontWeight: FontWeight.w400,
                      ),
                    ),
                  ),
              ],
            ),
          if ((data.ctaLabel ?? '').trim().isNotEmpty) ...[
            const SizedBox(height: 24),
            _PageCta(
              label: data.ctaLabel!,
              onTap: () {
                final onCta = data.onCta;
                Navigator.of(context).maybePop();
                if (onCta != null) {
                  onCta();
                }
              },
            ),
          ],
        ],
      ),
    );
  }
}

class _SlideTitle extends StatelessWidget {
  const _SlideTitle({required this.label, required this.accent});

  final String label;
  final Color accent;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Container(
          width: 5,
          height: 5,
          decoration: BoxDecoration(color: accent, shape: BoxShape.circle),
        ),
        const SizedBox(width: 8),
        Text(
          label,
          style: const TextStyle(
            color: Color(0xFF9A9A9A),
            fontSize: 9.5,
            letterSpacing: 0.9,
            fontWeight: FontWeight.w500,
          ),
        ),
      ],
    );
  }
}

class _HighlightHeadline extends StatelessWidget {
  const _HighlightHeadline({
    required this.text,
    required this.highlight,
    required this.accent,
    required this.accentInk,
    this.fontSize = 24,
  });

  final String text;
  final String highlight;
  final Color accent;
  final Color accentInk;
  final double fontSize;

  @override
  Widget build(BuildContext context) {
    final index = text.indexOf(highlight);
    final before = index > 0 ? text.substring(0, index) : '';
    final after = text.substring(index + highlight.length);
    return Text.rich(
      TextSpan(
        style: TextStyle(
          color: const Color(0xFF111111),
          fontSize: fontSize,
          height: 1.22,
          letterSpacing: -0.6,
          fontWeight: FontWeight.w400,
        ),
        children: [
          if (before.isNotEmpty) TextSpan(text: before),
          TextSpan(
            text: highlight,
            style: TextStyle(backgroundColor: accent, color: accentInk),
          ),
          if (after.isNotEmpty) TextSpan(text: after),
        ],
      ),
    );
  }
}

class _PageCta extends StatelessWidget {
  const _PageCta({required this.label, required this.onTap});

  final String label;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      child: Material(
        color: const Color(0xFF111111),
        borderRadius: BorderRadius.circular(22),
        child: InkWell(
          borderRadius: BorderRadius.circular(22),
          onTap: onTap,
          child: Container(
            padding: const EdgeInsets.symmetric(vertical: 14),
            alignment: Alignment.center,
            child: Text(
              label,
              style: const TextStyle(
                color: Color(0xFFCAFF4D),
                fontSize: 13,
                fontWeight: FontWeight.w500,
                letterSpacing: 0.2,
              ),
            ),
          ),
        ),
      ),
    );
  }
}
