import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';

import 'package:mobile/design/theme/profile_theme_extension.dart';
import 'package:mobile/design/widgets/shou_topbar.dart';

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
          children: [
            ShouTopBar(
              label: 'BUGÜN',
              onSearch: () {},
              onMenu: () {},
            ),
            Expanded(
              child: ListView(
                padding: const EdgeInsets.only(bottom: 120),
                children: const [
                  SizedBox(height: 13),
                  _StoryCirclesRow(),
                  SizedBox(height: 32),
                  _HomeV2Placeholder(),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Horizontal "Bugün aktif" story row with tinted rings encoding each
/// friend's state — lime for "active today", lavender for "in your current
/// transit", blush for softer social relevance. Mirrors the Figma
/// `STORY CIRCLES` frame: header eyebrow + "Tümünü gör" link on top of a
/// 70px tall scrollable row of 52×52 rings with a tiny name label.
///
/// Uses hardcoded placeholder entries for now; wired to the friends /
/// people provider in a later step.
class _StoryCirclesRow extends StatelessWidget {
  const _StoryCirclesRow();

  static const _items = <_StoryCircleData>[
    _StoryCircleData(name: 'Sen', tone: _StoryCircleTone.limeActive),
    _StoryCircleData(name: 'Zeynep', tone: _StoryCircleTone.lime),
    _StoryCircleData(name: 'Ceren', tone: _StoryCircleTone.lavender),
    _StoryCircleData(name: 'Alp', tone: _StoryCircleTone.lavender),
    _StoryCircleData(name: 'Bora', tone: _StoryCircleTone.blush),
  ];

  @override
  Widget build(BuildContext context) {
    final theme = context.profileTheme;
    final eyebrowColor = theme.colors.textLight;
    final eyebrowStyle = GoogleFonts.jetBrainsMono(
      textStyle: TextStyle(
        fontSize: 10.5,
        letterSpacing: 1.4,
        color: eyebrowColor,
      ),
    );
    final linkStyle = TextStyle(
      fontSize: 11,
      fontWeight: FontWeight.w500,
      color: theme.colors.brandLavender,
    );

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20),
          child: Row(
            children: [
              Text('Bugün aktif', style: eyebrowStyle),
              const Spacer(),
              Text('Tümünü gör', style: linkStyle),
            ],
          ),
        ),
        const SizedBox(height: 14),
        SizedBox(
          height: 70,
          child: ListView.separated(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 20),
            itemCount: _items.length,
            separatorBuilder: (_, _) => const SizedBox(width: 14),
            itemBuilder: (context, index) =>
                _StoryCircle(data: _items[index]),
          ),
        ),
      ],
    );
  }
}

enum _StoryCircleTone { limeActive, lime, lavender, blush }

class _StoryCircleData {
  const _StoryCircleData({required this.name, required this.tone});
  final String name;
  final _StoryCircleTone tone;
}

class _StoryCircle extends StatelessWidget {
  const _StoryCircle({required this.data});
  final _StoryCircleData data;

  _StoryCirclePalette _palette(BuildContext context) {
    final colors = context.profileTheme.colors;
    switch (data.tone) {
      case _StoryCircleTone.limeActive:
        return _StoryCirclePalette(
          ring: colors.brandLime,
          center: const Color(0xFFEAFFB8),
          avatar: const Color(0xFFD4F088),
        );
      case _StoryCircleTone.lime:
        return _StoryCirclePalette(
          ring: colors.brandLime.withValues(alpha: 0.55),
          center: const Color(0xFFF0FFD4),
          avatar: const Color(0xFFE6F7B8),
        );
      case _StoryCircleTone.lavender:
        return _StoryCirclePalette(
          ring: colors.brandLavender.withValues(alpha: 0.45),
          center: const Color(0xFFEBE8FF),
          avatar: const Color(0xFFD6D0F5),
        );
      case _StoryCircleTone.blush:
        return _StoryCirclePalette(
          ring: const Color(0xFFF5C2DE),
          center: const Color(0xFFFDE4F2),
          avatar: const Color(0xFFF5C2DE),
        );
    }
  }

  @override
  Widget build(BuildContext context) {
    final palette = _palette(context);
    final theme = context.profileTheme;
    return SizedBox(
      width: 52,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 52,
            height: 52,
            decoration: BoxDecoration(
              color: palette.ring,
              shape: BoxShape.circle,
            ),
            child: Padding(
              padding: const EdgeInsets.all(3),
              child: Container(
                decoration: BoxDecoration(
                  color: palette.center,
                  shape: BoxShape.circle,
                  border: Border.all(color: Colors.white, width: 2),
                ),
                child: Center(
                  child: Container(
                    width: 28,
                    height: 28,
                    decoration: BoxDecoration(
                      color: palette.avatar,
                      shape: BoxShape.circle,
                    ),
                  ),
                ),
              ),
            ),
          ),
          const SizedBox(height: 5),
          SizedBox(
            height: 13,
            child: Text(
              data.name,
              style: TextStyle(
                fontSize: 10.5,
                fontWeight: FontWeight.w400,
                color: theme.colors.textLight,
                height: 1,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _StoryCirclePalette {
  const _StoryCirclePalette({
    required this.ring,
    required this.center,
    required this.avatar,
  });

  final Color ring;
  final Color center;
  final Color avatar;
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
