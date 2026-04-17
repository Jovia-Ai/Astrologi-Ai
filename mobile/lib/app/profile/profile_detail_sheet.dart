import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'package:mobile/app/timing/turkish_text.dart';

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
    final slides = <Widget>[
      _HeroSlide(data: data),
    ];
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
      body: SafeArea(
        child: Stack(
          children: [
            PageView.builder(
              controller: _controller,
              itemCount: slides.length,
              onPageChanged: (value) => setState(() => _index = value),
              physics: const BouncingScrollPhysics(),
              itemBuilder: (_, index) => slides[index],
            ),
            Positioned(
              top: 12,
              left: 16,
              child: _CloseButton(
                onTap: () => Navigator.of(context).maybePop(),
              ),
            ),
            Positioned(
              top: 14,
              right: 20,
              child: _SheetEyebrow(data: widget.data),
            ),
            if (showIndicator)
              Positioned(
                left: 0,
                right: 0,
                bottom: 28,
                child: _PageDots(
                  count: slides.length,
                  index: _index,
                  accent: widget.data.accent,
                ),
              ),
          ],
        ),
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

class _PageDots extends StatelessWidget {
  const _PageDots({
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
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        for (var i = 0; i < count; i++)
          AnimatedContainer(
            duration: const Duration(milliseconds: 220),
            curve: Curves.easeOutCubic,
            width: i == index ? 18 : 5,
            height: 5,
            margin: const EdgeInsets.symmetric(horizontal: 3),
            decoration: BoxDecoration(
              color: i == index ? accent : const Color(0xFFE1E1E1),
              borderRadius: BorderRadius.circular(3),
            ),
          ),
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
      color: const Color(0xFFF2F2F2),
      shape: const CircleBorder(),
      child: InkWell(
        customBorder: const CircleBorder(),
        onTap: onTap,
        child: const SizedBox(
          width: 34,
          height: 34,
          child: Icon(Icons.close_rounded, size: 18, color: Color(0xFF555555)),
        ),
      ),
    );
  }
}

class _SlideShell extends StatelessWidget {
  const _SlideShell({required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(24, 70, 24, 72),
      child: SingleChildScrollView(
        physics: const BouncingScrollPhysics(),
        child: ConstrainedBox(
          constraints: BoxConstraints(
            minHeight:
                MediaQuery.of(context).size.height - 220,
          ),
          child: child,
        ),
      ),
    );
  }
}

class _HeroSlide extends StatelessWidget {
  const _HeroSlide({required this.data});

  final ProfileDetailSheetData data;

  @override
  Widget build(BuildContext context) {
    final highlightVisible =
        data.highlight.trim().isNotEmpty &&
        data.headline.contains(data.highlight);
    return _SlideShell(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.start,
        children: [
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
          if (data.body.trim().isNotEmpty) ...[
            const SizedBox(height: 20),
            Text(
              data.body,
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

class _MechanismSlide extends StatelessWidget {
  const _MechanismSlide({required this.data});

  final ProfileDetailSheetData data;

  @override
  Widget build(BuildContext context) {
    return _SlideShell(
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

class _ContextSlide extends StatelessWidget {
  const _ContextSlide({required this.data});

  final ProfileDetailSheetData data;

  @override
  Widget build(BuildContext context) {
    return _SlideShell(
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
