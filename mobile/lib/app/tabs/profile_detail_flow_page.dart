import 'package:flutter/material.dart';

import 'package:mobile/app/profile/proof_chip.dart';
import 'package:mobile/app/timing/turkish_text.dart';
import 'package:mobile/design/theme/profile_theme_extension.dart';
import 'package:mobile/design/widgets/jovia_editorial.dart';
import 'package:mobile/design/widgets/jovia_premium_accents.dart';
import 'package:mobile/l10n/current_localizations.dart';
import 'package:mobile/l10n/l10n.dart';

const Duration _kDetailPlaybackAutoplay = Duration(seconds: 7);
const Duration _kDetailPlaybackPageTurn = Duration(milliseconds: 280);

class ProfileDetailTone {
  const ProfileDetailTone({
    required this.background,
    required this.surface,
    required this.surfaceStrong,
    required this.accent,
    required this.accentSoft,
    required this.stroke,
    required this.glow,
    required this.mutedText,
  });

  final Color background;
  final Color surface;
  final Color surfaceStrong;
  final Color accent;
  final Color accentSoft;
  final Color stroke;
  final Color glow;
  final Color mutedText;
}

const ProfileDetailTone _kDefaultProfileDetailTone = ProfileDetailTone(
  background: Color(0xFF08070B),
  surface: Color(0xFF12101A),
  surfaceStrong: Color(0xFF1A1524),
  accent: Color(0xFFB58DFF),
  accentSoft: Color(0xFF9EF0E7),
  stroke: Color(0x3DB58DFF),
  glow: Color(0x33B58DFF),
  mutedText: Color(0xFFD3CBDD),
);

ProfileDetailTone _detailToneForPlaybackPage(
  _ProfileDetailPlaybackPageData page,
) {
  return profileDetailToneForSignature(
    title: page.title,
    summary: '${page.intro} ${page.bodyBlocks.join(' ')} ${page.whyText}',
    eyebrow: page.eyebrow,
  );
}

Color _detailPageBackground(BuildContext context, ProfileDetailTone tone) {
  final profile = context.profileTheme;
  return Color.alphaBlend(
    tone.accent.withValues(
      alpha: Theme.of(context).brightness == Brightness.dark ? 0.18 : 0.08,
    ),
    profile.colors.bg,
  );
}

Color _detailCardBackground(
  BuildContext context,
  ProfileDetailTone tone, {
  bool emphasized = false,
}) {
  final profile = context.profileTheme;
  final isDark = Theme.of(context).brightness == Brightness.dark;
  if (isDark) {
    final base = Color.alphaBlend(
      tone.accent.withValues(alpha: emphasized ? 0.1 : 0.06),
      profile.colors.surface,
    );
    return Color.alphaBlend(
      tone.accentSoft.withValues(alpha: emphasized ? 0.08 : 0.04),
      base,
    );
  }
  final base = Color.alphaBlend(
    Colors.white.withValues(alpha: emphasized ? 0.9 : 0.82),
    profile.colors.surface,
  );
  final violetWash = Color.alphaBlend(
    tone.accent.withValues(alpha: emphasized ? 0.12 : 0.08),
    base,
  );
  return Color.alphaBlend(
    const Color(0xFFF1EAFF).withValues(alpha: emphasized ? 0.28 : 0.18),
    violetWash,
  );
}

Color _detailInsetBackground(
  BuildContext context,
  ProfileDetailTone tone, {
  bool highlighted = false,
}) {
  final profile = context.profileTheme;
  final isDark = Theme.of(context).brightness == Brightness.dark;
  if (isDark) {
    return Color.alphaBlend(
      (highlighted ? tone.accent : tone.accentSoft).withValues(
        alpha: highlighted ? 0.16 : 0.08,
      ),
      profile.colors.panelSoft,
    );
  }
  final base = Color.alphaBlend(
    Colors.white.withValues(alpha: highlighted ? 0.72 : 0.62),
    profile.colors.panelSoft,
  );
  return Color.alphaBlend(
    tone.accent.withValues(alpha: highlighted ? 0.1 : 0.07),
    base,
  );
}

Color _detailStrokeColor(BuildContext context, ProfileDetailTone tone) {
  final isDark = Theme.of(context).brightness == Brightness.dark;
  if (isDark) {
    return Color.alphaBlend(
      tone.accent.withValues(alpha: 0.16),
      context.profileTheme.colors.strokeSoft,
    );
  }
  return Color.alphaBlend(
    tone.accent.withValues(alpha: 0.045),
    context.profileTheme.colors.strokeSoft,
  );
}

Color _detailLabelTextColor(BuildContext context, ProfileDetailTone tone) {
  if (Theme.of(context).brightness == Brightness.dark) {
    return tone.accent;
  }
  return Color.alphaBlend(Colors.white.withValues(alpha: 0.12), tone.accent);
}

Color _detailIntroTextColor(BuildContext context) {
  final profile = context.profileTheme;
  if (Theme.of(context).brightness == Brightness.dark) {
    return profile.colors.text.withValues(alpha: 0.9);
  }
  return profile.colors.text.withValues(alpha: 0.8);
}

Color _detailBodyTextColor(BuildContext context) {
  final profile = context.profileTheme;
  if (Theme.of(context).brightness == Brightness.dark) {
    return profile.colors.text.withValues(alpha: 0.96);
  }
  return profile.colors.text.withValues(alpha: 0.9);
}

Color _detailMutedTextColor(BuildContext context) {
  final profile = context.profileTheme;
  if (Theme.of(context).brightness == Brightness.dark) {
    return profile.colors.text.withValues(alpha: 0.68);
  }
  return profile.colors.text.withValues(alpha: 0.58);
}

Color _detailChipTextColor(BuildContext context) {
  final profile = context.profileTheme;
  if (Theme.of(context).brightness == Brightness.dark) {
    return profile.colors.text.withValues(alpha: 0.78);
  }
  return profile.colors.text.withValues(alpha: 0.68);
}

Color _detailInfluenceTextColor(BuildContext context) {
  final profile = context.profileTheme;
  if (Theme.of(context).brightness == Brightness.dark) {
    return profile.colors.text.withValues(alpha: 0.82);
  }
  return profile.colors.text.withValues(alpha: 0.78);
}

String _detailInfluenceLabel(BuildContext context) {
  return context.l10n.profileDetailInfluences;
}

List<String> _detailHighlightLines(
  _ProfileDetailPlaybackPageData page, {
  int maxLines = 2,
}) {
  final source = <String>[
    page.intro.trim(),
    if (page.bodyBlocks.isNotEmpty) page.bodyBlocks.first.trim(),
    page.whyText.trim(),
  ].firstWhere((item) => item.isNotEmpty, orElse: () => '');
  return joviaHighlightLinesFromText(source, maxLines: maxLines, maxLength: 62);
}

ProfileDetailTone profileDetailToneForSignature({
  required String title,
  String summary = '',
  String family = '',
  String eyebrow = '',
}) {
  final haystack = '$title $summary $family $eyebrow'.toLowerCase();

  bool matches(List<String> values) {
    return values.any((value) {
      final needle = value.toLowerCase();
      if (needle.contains(' ') || needle.contains('_')) {
        return haystack.contains(needle);
      }
      return RegExp(
        '(^|[^a-zçğıöşü])${RegExp.escape(needle)}([^a-zçğıöşü]|\$)',
      ).hasMatch(haystack);
    });
  }

  if (matches(const ['güneş', 'gunes', 'sun', 'solar'])) {
    return const ProfileDetailTone(
      background: Color(0xFF120A04),
      surface: Color(0xFF1E120A),
      surfaceStrong: Color(0xFF2A180D),
      accent: Color(0xFFFF9B47),
      accentSoft: Color(0xFFFFD07A),
      stroke: Color(0x40FF9B47),
      glow: Color(0x33FF9B47),
      mutedText: Color(0xFFE6D1BE),
    );
  }
  if (matches(const ['ay', 'moon', 'luna'])) {
    return const ProfileDetailTone(
      background: Color(0xFF071018),
      surface: Color(0xFF101A25),
      surfaceStrong: Color(0xFF162334),
      accent: Color(0xFF8CB8FF),
      accentSoft: Color(0xFFD8E7FF),
      stroke: Color(0x408CB8FF),
      glow: Color(0x338CB8FF),
      mutedText: Color(0xFFD3DDF0),
    );
  }
  if (matches(const ['merkür', 'merkur', 'mercury'])) {
    return const ProfileDetailTone(
      background: Color(0xFF061315),
      surface: Color(0xFF0F2023),
      surfaceStrong: Color(0xFF173036),
      accent: Color(0xFF69E3E2),
      accentSoft: Color(0xFFB2F3F0),
      stroke: Color(0x4069E3E2),
      glow: Color(0x3369E3E2),
      mutedText: Color(0xFFCDE5E3),
    );
  }
  if (matches(const ['venüs', 'venus', 'ask', 'sevgi'])) {
    return const ProfileDetailTone(
      background: Color(0xFF170A11),
      surface: Color(0xFF24101B),
      surfaceStrong: Color(0xFF311625),
      accent: Color(0xFFFF8CC6),
      accentSoft: Color(0xFFFFC6E1),
      stroke: Color(0x40FF8CC6),
      glow: Color(0x33FF8CC6),
      mutedText: Color(0xFFE9CBD9),
    );
  }
  if (matches(const ['mars', 'kavga', 'ates'])) {
    return const ProfileDetailTone(
      background: Color(0xFF170805),
      surface: Color(0xFF25110D),
      surfaceStrong: Color(0xFF341713),
      accent: Color(0xFFFF7A59),
      accentSoft: Color(0xFFFFB18E),
      stroke: Color(0x40FF7A59),
      glow: Color(0x33FF7A59),
      mutedText: Color(0xFFE6CCC3),
    );
  }
  if (matches(const ['jüpiter', 'jupiter'])) {
    return const ProfileDetailTone(
      background: Color(0xFF140E04),
      surface: Color(0xFF221909),
      surfaceStrong: Color(0xFF31230D),
      accent: Color(0xFFF2B84A),
      accentSoft: Color(0xFFFFE39A),
      stroke: Color(0x40F2B84A),
      glow: Color(0x33F2B84A),
      mutedText: Color(0xFFE4D7B8),
    );
  }
  if (matches(const ['satürn', 'saturn'])) {
    return const ProfileDetailTone(
      background: Color(0xFF100D0A),
      surface: Color(0xFF1A1612),
      surfaceStrong: Color(0xFF252018),
      accent: Color(0xFFC7A97B),
      accentSoft: Color(0xFFE4D3B8),
      stroke: Color(0x40C7A97B),
      glow: Color(0x33C7A97B),
      mutedText: Color(0xFFD8CFC2),
    );
  }
  if (matches(const ['uranüs', 'uranus'])) {
    return const ProfileDetailTone(
      background: Color(0xFF071510),
      surface: Color(0xFF10231D),
      surfaceStrong: Color(0xFF163229),
      accent: Color(0xFF5DE6B4),
      accentSoft: Color(0xFFB4F5DB),
      stroke: Color(0x405DE6B4),
      glow: Color(0x335DE6B4),
      mutedText: Color(0xFFCBE6DA),
    );
  }
  if (matches(const ['neptün', 'neptun', 'neptune'])) {
    return const ProfileDetailTone(
      background: Color(0xFF070D19),
      surface: Color(0xFF111A2D),
      surfaceStrong: Color(0xFF162541),
      accent: Color(0xFF7FA7FF),
      accentSoft: Color(0xFF79E7FF),
      stroke: Color(0x407FA7FF),
      glow: Color(0x337FA7FF),
      mutedText: Color(0xFFD0DBF7),
    );
  }
  if (matches(const ['plüto', 'pluto'])) {
    return const ProfileDetailTone(
      background: Color(0xFF14070F),
      surface: Color(0xFF220F1B),
      surfaceStrong: Color(0xFF31152B),
      accent: Color(0xFFE46AB6),
      accentSoft: Color(0xFFF3A4D5),
      stroke: Color(0x40E46AB6),
      glow: Color(0x33E46AB6),
      mutedText: Color(0xFFE4C8D7),
    );
  }
  if (matches(const [
    'açı',
    'aci',
    'contradiction',
    'kare',
    'karşıt',
    'karsit',
  ])) {
    return const ProfileDetailTone(
      background: Color(0xFF140908),
      surface: Color(0xFF221210),
      surfaceStrong: Color(0xFF311915),
      accent: Color(0xFFFF8D6B),
      accentSoft: Color(0xFFFFC3A8),
      stroke: Color(0x40FF8D6B),
      glow: Color(0x33FF8D6B),
      mutedText: Color(0xFFE5CEC7),
    );
  }
  if (matches(const ['burç', 'burc', 'tone_signature'])) {
    return const ProfileDetailTone(
      background: Color(0xFF07140E),
      surface: Color(0xFF102018),
      surfaceStrong: Color(0xFF173024),
      accent: Color(0xFF72D6A4),
      accentSoft: Color(0xFFB7F0CB),
      stroke: Color(0x4072D6A4),
      glow: Color(0x3372D6A4),
      mutedText: Color(0xFFCDE4D7),
    );
  }
  return _kDefaultProfileDetailTone;
}

class ProfileDetailCatalogItem {
  const ProfileDetailCatalogItem({
    required this.id,
    required this.eyebrow,
    required this.title,
    required this.subtitle,
    required this.illustrationAsset,
    this.tone = _kDefaultProfileDetailTone,
  });

  final String id;
  final String eyebrow;
  final String title;
  final String subtitle;
  final JoviaIllustrationAsset illustrationAsset;
  final ProfileDetailTone tone;
}

enum ProfileDetailSceneVariant {
  glance,
  posterScene,
  structuredInsight,
  split,
  symbol,
  portal,
}

class ProfileDetailSceneData {
  const ProfileDetailSceneData({
    required this.id,
    required this.eyebrow,
    required this.title,
    required this.intro,
    required this.bodyBlocks,
    required this.chips,
    required this.astroSources,
    required this.whyText,
    required this.illustrationAsset,
    required this.variant,
    this.nextTitle = '',
    this.proofRaw = '',
  });

  final String id;
  final String eyebrow;
  final String title;
  final String intro;
  final List<String> bodyBlocks;
  final List<String> chips;
  final List<String> astroSources;
  final String whyText;
  final JoviaIllustrationAsset illustrationAsset;
  final ProfileDetailSceneVariant variant;
  final String nextTitle;

  /// Thread-level astrological credit line (voice spec v2.1 §11.4).
  /// Flows from _SupportingThreadItem.proofRaw → _sceneFromThread.
  /// Card / insight / identity scenes default empty.
  final String proofRaw;

  ProfileDetailSceneData copyWith({
    String? nextTitle,
    ProfileDetailSceneVariant? variant,
  }) {
    return ProfileDetailSceneData(
      id: id,
      eyebrow: eyebrow,
      title: title,
      intro: intro,
      bodyBlocks: bodyBlocks,
      chips: chips,
      astroSources: astroSources,
      whyText: whyText,
      illustrationAsset: illustrationAsset,
      variant: variant ?? this.variant,
      nextTitle: nextTitle ?? this.nextTitle,
      proofRaw: proofRaw,
    );
  }
}

class ProfileDetailPage extends StatelessWidget {
  const ProfileDetailPage({
    super.key,
    required this.flowTitle,
    required this.flowSubtitle,
    required this.scenes,
    this.tone = _kDefaultProfileDetailTone,
  });

  final String flowTitle;
  final String flowSubtitle;
  final List<ProfileDetailSceneData> scenes;
  final ProfileDetailTone tone;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final firstScene = scenes.isNotEmpty ? scenes.first : null;
    final topBarLabel = (firstScene?.eyebrow ?? '').trim().isNotEmpty
        ? (firstScene?.eyebrow ?? flowTitle)
        : flowTitle;
    final topBarCenterText =
        firstScene == null ||
            firstScene.title.trim().isEmpty ||
            firstScene.title.trim() == flowTitle.trim()
        ? null
        : flowTitle;
    return Scaffold(
      backgroundColor: profile.colors.bg,
      body: ColoredBox(
        color: profile.colors.bg,
        child: SafeArea(
          bottom: false,
          child: JoviaPageScaffold(
            padding: const EdgeInsets.fromLTRB(16, 12, 16, 28),
            child: ListView(
              padding: EdgeInsets.zero,
              children: [
                JoviaProfileTopBar(
                  label: topBarLabel,
                  centerText: topBarCenterText,
                  onBackTap: () => Navigator.of(context).maybePop(),
                  reserveTrailingSpace: true,
                ),
                const SizedBox(height: 20),
                for (var index = 0; index < scenes.length; index++) ...[
                  _ProfileDetailPinnedSceneCard(
                    scene: scenes[index],
                    index: index,
                    total: scenes.length,
                    tone: tone,
                  ),
                  SizedBox(height: profile.spacing.s16),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _ProfileDetailPinnedSceneCard extends StatelessWidget {
  const _ProfileDetailPinnedSceneCard({
    required this.scene,
    required this.index,
    required this.total,
    required this.tone,
  });

  final ProfileDetailSceneData scene;
  final int index;
  final int total;
  final ProfileDetailTone tone;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final hasIntro = scene.intro.trim().isNotEmpty;
    final pages = _buildPinnedScenePages(scene);
    return JoviaSurfaceCard(
      radius: 28,
      padding: EdgeInsets.zero,
      backgroundColor: _detailCardBackground(context, tone, emphasized: true),
      borderColor: _detailStrokeColor(context, tone),
      child: Stack(
        children: [
          Positioned(
            right: -18,
            top: -18,
            child: DecoratedBox(
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: RadialGradient(
                  colors: [
                    tone.accent.withValues(alpha: 0.24),
                    Colors.transparent,
                  ],
                ),
              ),
              child: const SizedBox(width: 120, height: 120),
            ),
          ),
          Positioned(
            right: 14,
            bottom: 12,
            child: JoviaIllustrationAccent(
              asset: scene.illustrationAsset,
              width: 84,
              height: 84,
              opacity: 0.14,
            ),
          ),
          Padding(
            padding: const EdgeInsets.fromLTRB(18, 18, 18, 18),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            scene.eyebrow.isNotEmpty
                                ? scene.eyebrow
                                : currentL10n().profileDetailDefaultEyebrow,
                            style: profile.typography.monoEyebrow.copyWith(
                              color: tone.accent,
                              fontSize: 11.5,
                              letterSpacing: 1.7,
                            ),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            scene.title,
                            style: profile.typography.section.copyWith(
                              color: profile.colors.text,
                              fontSize: 28,
                              height: 1.08,
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(width: 12),
                    JoviaIllustrationAccent(
                      asset: scene.illustrationAsset,
                      width: 38,
                      height: 38,
                      opacity: 0.92,
                    ),
                  ],
                ),
                if (hasIntro) ...[
                  const SizedBox(height: 12),
                  Text(
                    scene.intro,
                    style: profile.typography.bodyReading.copyWith(
                      color: tone.mutedText,
                      height: 1.58,
                    ),
                  ),
                ],
                if (scene.chips.isNotEmpty) ...[
                  const SizedBox(height: 16),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: [
                      for (final chip in scene.chips.take(4))
                        _ProfileDetailThemeChip(label: chip, tone: tone),
                    ],
                  ),
                ],
                if (pages.isNotEmpty) ...[
                  const SizedBox(height: 20),
                  _ProfileDetailPinnedTextPager(
                    sceneId: scene.id,
                    pages: pages,
                    tone: tone,
                  ),
                ],
                if (index < total - 1 && scene.nextTitle.trim().isNotEmpty) ...[
                  const SizedBox(height: 16),
                  Text(
                    currentL10n().profileDetailNextLabel(scene.nextTitle),
                    style: profile.typography.meta.copyWith(
                      color: tone.mutedText.withValues(alpha: 0.82),
                    ),
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _ProfileDetailPinnedPageData {
  const _ProfileDetailPinnedPageData({required this.text, this.label = ''});

  final String text;
  final String label;
}

List<_ProfileDetailPinnedPageData> _buildPinnedScenePages(
  ProfileDetailSceneData scene,
) {
  final pages = <_ProfileDetailPinnedPageData>[
    for (final block
        in scene.bodyBlocks
            .map((item) => item.trim())
            .where((item) => item.isNotEmpty))
      _ProfileDetailPinnedPageData(text: block),
  ];
  final whyText = scene.whyText.trim();
  if (whyText.isNotEmpty) {
    pages.add(
      _ProfileDetailPinnedPageData(
        text: whyText,
        label: currentL10n().profileDetailWhyHere,
      ),
    );
  }
  if (pages.isNotEmpty) {
    return pages;
  }
  final fallback = scene.intro.trim();
  if (fallback.isEmpty) {
    return const <_ProfileDetailPinnedPageData>[];
  }
  return <_ProfileDetailPinnedPageData>[
    _ProfileDetailPinnedPageData(text: fallback),
  ];
}

class _ProfileDetailThemeChip extends StatelessWidget {
  const _ProfileDetailThemeChip({required this.label, required this.tone});

  final String label;
  final ProfileDetailTone tone;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 7),
      decoration: BoxDecoration(
        color: tone.accent.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: tone.stroke),
      ),
      child: Text(
        label,
        style: profile.typography.buttonLabel.copyWith(
          color: profile.colors.text,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }
}

class _ProfileDetailPinnedTextPager extends StatefulWidget {
  const _ProfileDetailPinnedTextPager({
    required this.sceneId,
    required this.pages,
    required this.tone,
  });

  final String sceneId;
  final List<_ProfileDetailPinnedPageData> pages;
  final ProfileDetailTone tone;

  @override
  State<_ProfileDetailPinnedTextPager> createState() =>
      _ProfileDetailPinnedTextPagerState();
}

class _ProfileDetailPinnedTextPagerState
    extends State<_ProfileDetailPinnedTextPager> {
  late final PageController _pageController;
  int _activeIndex = 0;

  @override
  void initState() {
    super.initState();
    _pageController = PageController();
  }

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(
          height: 316,
          child: PageView.builder(
            key: ValueKey<String>('profileDetailTextPager_${widget.sceneId}'),
            controller: _pageController,
            physics: const BouncingScrollPhysics(),
            itemCount: widget.pages.length,
            onPageChanged: (index) {
              if (_activeIndex == index) {
                return;
              }
              setState(() => _activeIndex = index);
            },
            itemBuilder: (context, index) {
              return AnimatedBuilder(
                animation: _pageController,
                builder: (context, child) {
                  final page = _pageController.hasClients
                      ? (_pageController.page ?? _activeIndex.toDouble())
                      : _activeIndex.toDouble();
                  final distance = (page - index).clamp(-1.0, 1.0);
                  final emphasis = (1 - distance.abs()).clamp(0.0, 1.0);
                  final eased = Curves.easeOutCubic.transform(emphasis);
                  final pageData = widget.pages[index];
                  return Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 2),
                    child: ClipRect(
                      child: Transform.translate(
                        offset: Offset(distance * -28, 0),
                        child: Opacity(
                          opacity: 0.46 + (0.54 * eased),
                          child: Align(
                            alignment: Alignment.topLeft,
                            child: KeyedSubtree(
                              key: ValueKey<String>(
                                'profileDetailTextPage_${widget.sceneId}_$index',
                              ),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  if (pageData.label.isNotEmpty) ...[
                                    Text(
                                      pageData.label,
                                      style: profile.typography.buttonLabel
                                          .copyWith(
                                            color: widget.tone.accent,
                                            fontWeight: FontWeight.w700,
                                          ),
                                    ),
                                    const SizedBox(height: 10),
                                  ],
                                  Expanded(
                                    child: SingleChildScrollView(
                                      physics: const BouncingScrollPhysics(),
                                      child: Text(
                                        pageData.text,
                                        style: profile.typography.bodyReading
                                            .copyWith(
                                              color: pageData.label.isNotEmpty
                                                  ? profile.colors.text
                                                  : profile.colors.textLight,
                                              fontSize: 16.4,
                                              height: 1.68,
                                            ),
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                        ),
                      ),
                    ),
                  );
                },
              );
            },
          ),
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 7),
              decoration: BoxDecoration(
                color: widget.tone.accent.withValues(alpha: 0.08),
                borderRadius: BorderRadius.circular(999),
                border: Border.all(color: widget.tone.stroke),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    Icons.swipe_rounded,
                    size: 14,
                    color: widget.tone.accent,
                  ),
                  const SizedBox(width: 6),
                  Text(
                    '${_activeIndex + 1}/${widget.pages.length}',
                    style: profile.typography.metaSoft.copyWith(
                      color: profile.colors.text,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ],
              ),
            ),
            const Spacer(),
            Row(
              children: [
                for (var index = 0; index < widget.pages.length; index++) ...[
                  AnimatedContainer(
                    duration: const Duration(milliseconds: 220),
                    curve: Curves.easeOutCubic,
                    width: index == _activeIndex ? 20 : 8,
                    height: 8,
                    decoration: BoxDecoration(
                      color: index == _activeIndex
                          ? widget.tone.accent
                          : context.profileTheme.colors.strokeSoft,
                      borderRadius: BorderRadius.circular(999),
                    ),
                  ),
                  if (index != widget.pages.length - 1)
                    const SizedBox(width: 6),
                ],
              ],
            ),
          ],
        ),
      ],
    );
  }
}

class ProfileDetailCatalogPage extends StatelessWidget {
  const ProfileDetailCatalogPage({
    super.key,
    required this.title,
    required this.subtitle,
    required this.items,
    required this.onOpenItem,
  });

  final String title;
  final String subtitle;
  final List<ProfileDetailCatalogItem> items;
  final ValueChanged<ProfileDetailCatalogItem> onOpenItem;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final pageTone = items.isNotEmpty
        ? items.first.tone
        : _kDefaultProfileDetailTone;
    return Scaffold(
      backgroundColor: profile.colors.bg,
      body: ColoredBox(
        color: profile.colors.bg,
        child: SafeArea(
          bottom: false,
          child: JoviaPageScaffold(
            padding: const EdgeInsets.fromLTRB(16, 12, 16, 28),
            child: ListView(
              padding: EdgeInsets.zero,
              children: [
                JoviaProfileTopBar(
                  label: title,
                  centerText: context.l10n.profileDetailAllCards,
                  onBackTap: () => Navigator.of(context).maybePop(),
                  reserveTrailingSpace: true,
                ),
                const SizedBox(height: 18),
                JoviaSurfaceCard(
                  radius: 28,
                  backgroundColor: _detailCardBackground(
                    context,
                    pageTone,
                    emphasized: true,
                  ),
                  borderColor: _detailStrokeColor(context, pageTone),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        turkishToUpper(title),
                        style: profile.typography.monoEyebrow.copyWith(
                          color: pageTone.accent,
                          fontSize: 11.5,
                          letterSpacing: 1.8,
                        ),
                      ),
                      const SizedBox(height: 10),
                      Text(
                        context.l10n.profileDetailSignatureCardsTitle,
                        style: profile.typography.section.copyWith(
                          color: profile.colors.text,
                          fontSize: 24,
                          height: 1.08,
                        ),
                      ),
                      if (subtitle.trim().isNotEmpty) ...[
                        const SizedBox(height: 10),
                        Text(
                          subtitle,
                          style: profile.typography.bodyCompact.copyWith(
                            color: pageTone.mutedText,
                            height: 1.56,
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
                const SizedBox(height: 18),
                for (var index = 0; index < items.length; index++) ...[
                  _ProfileDetailCatalogCard(
                    item: items[index],
                    onTap: () => onOpenItem(items[index]),
                  ),
                  if (index != items.length - 1) const SizedBox(height: 14),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _ProfileDetailCatalogCard extends StatelessWidget {
  const _ProfileDetailCatalogCard({required this.item, required this.onTap});

  final ProfileDetailCatalogItem item;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return JoviaPressable(
      onTap: onTap,
      borderRadius: BorderRadius.circular(24),
      child: JoviaSurfaceCard(
        radius: 24,
        backgroundColor: _detailCardBackground(context, item.tone),
        borderColor: _detailStrokeColor(context, item.tone),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              width: 72,
              height: 72,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(18),
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [
                    item.tone.accent.withValues(alpha: 0.32),
                    item.tone.accentSoft.withValues(alpha: 0.18),
                    item.tone.surfaceStrong,
                  ],
                ),
              ),
              child: Center(
                child: JoviaIllustrationAccent(
                  asset: item.illustrationAsset,
                  width: 44,
                  height: 44,
                  opacity: 0.92,
                ),
              ),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (item.eyebrow.trim().isNotEmpty) ...[
                    Text(
                      turkishToUpper(item.eyebrow),
                      style: profile.typography.monoEyebrow.copyWith(
                        color: item.tone.accent,
                        fontSize: 11.0,
                        letterSpacing: 1.6,
                      ),
                    ),
                    const SizedBox(height: 6),
                  ],
                  Text(
                    item.title,
                    style: profile.typography.card.copyWith(
                      color: profile.colors.text,
                      fontWeight: FontWeight.w700,
                      fontSize: 18,
                      height: 1.22,
                    ),
                  ),
                  if (item.subtitle.trim().isNotEmpty) ...[
                    const SizedBox(height: 8),
                    Text(
                      item.subtitle,
                      maxLines: 3,
                      overflow: TextOverflow.ellipsis,
                      style: profile.typography.metaSoft.copyWith(
                        color: item.tone.mutedText,
                        height: 1.5,
                      ),
                    ),
                  ],
                ],
              ),
            ),
            const SizedBox(width: 10),
            Icon(
              Icons.arrow_forward_rounded,
              color: item.tone.accent,
              size: 20,
            ),
          ],
        ),
      ),
    );
  }
}

class ProfileDetailFlowPage extends StatefulWidget {
  const ProfileDetailFlowPage({
    super.key,
    required this.flowTitle,
    required this.flowSubtitle,
    required this.scenes,
  });

  final String flowTitle;
  final String flowSubtitle;
  final List<ProfileDetailSceneData> scenes;

  @override
  State<ProfileDetailFlowPage> createState() => _ProfileDetailFlowPageState();
}

class _ProfileDetailFlowPageState extends State<ProfileDetailFlowPage>
    with SingleTickerProviderStateMixin, WidgetsBindingObserver {
  late final PageController _pageController;
  late final AnimationController _autoplayController;
  late List<_ProfileDetailPlaybackSceneGroup> _sceneGroups;
  late List<_ProfileDetailPlaybackPageData> _pages;
  final Map<int, PageController> _scenePageControllers = {};
  final Map<int, int> _activePageByScene = {};

  int _activeSceneIndex = 0;
  bool _isHolding = false;
  bool _isDragging = false;
  bool _isInactive = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _pageController = PageController();
    _autoplayController = AnimationController(
      vsync: this,
      duration: _kDetailPlaybackAutoplay,
    )..addStatusListener(_handleAutoplayStatus);
    _configurePlayback(widget.scenes);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) {
        return;
      }
      _restartAutoplay();
    });
  }

  @override
  void didUpdateWidget(covariant ProfileDetailFlowPage oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.scenes == widget.scenes &&
        oldWidget.flowTitle == widget.flowTitle &&
        oldWidget.flowSubtitle == widget.flowSubtitle) {
      return;
    }
    _configurePlayback(widget.scenes);
    if (_pageController.hasClients) {
      _pageController.jumpToPage(0);
    }
    _restartAutoplay();
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _autoplayController
      ..removeStatusListener(_handleAutoplayStatus)
      ..dispose();
    _disposeScenePageControllers();
    _pageController.dispose();
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    final inactive =
        state == AppLifecycleState.inactive ||
        state == AppLifecycleState.paused ||
        state == AppLifecycleState.hidden ||
        state == AppLifecycleState.detached;
    if (_isInactive == inactive) {
      return;
    }
    _isInactive = inactive;
    if (inactive) {
      _pauseAutoplay();
    } else {
      _resumeAutoplay();
    }
  }

  _ProfileDetailPlaybackSceneGroup get _currentSceneGroup =>
      _sceneGroups[_activeSceneIndex.clamp(0, _sceneGroups.length - 1)];

  int get _currentScenePageIndex {
    final pageIndex = _activePageByScene[_activeSceneIndex] ?? 0;
    return pageIndex.clamp(0, _currentSceneGroup.pages.length - 1);
  }

  int get _activeFlatIndex =>
      (_currentSceneGroup.flatStartIndex + _currentScenePageIndex).clamp(
        0,
        _pages.length - 1,
      );

  _ProfileDetailPlaybackPageData get _currentPage =>
      _currentSceneGroup.pages[_currentScenePageIndex];

  @override
  Widget build(BuildContext context) {
    final activePage = _currentPage;
    final activeTone = _detailToneForPlaybackPage(activePage);
    final background = _detailPageBackground(context, activeTone);
    return Scaffold(
      backgroundColor: background,
      body: ColoredBox(
        color: background,
        child: Stack(
          children: [
            _DetailFlowBackdrop(tone: activeTone),
            NotificationListener<ScrollNotification>(
              onNotification: (notification) {
                if (notification is ScrollStartNotification &&
                    notification.dragDetails != null) {
                  _isDragging = true;
                  _pauseAutoplay();
                } else if (notification is ScrollEndNotification &&
                    _isDragging) {
                  _isDragging = false;
                  _resumeAutoplay();
                }
                return false;
              },
              child: Listener(
                behavior: HitTestBehavior.translucent,
                onPointerDown: (_) {
                  _isHolding = true;
                  _pauseAutoplay();
                },
                onPointerUp: (_) {
                  _isHolding = false;
                  _resumeAutoplay();
                },
                onPointerCancel: (_) {
                  _isHolding = false;
                  _resumeAutoplay();
                },
                child: PageView.builder(
                  key: const Key('profileDetailPageView'),
                  controller: _pageController,
                  scrollDirection: Axis.vertical,
                  itemCount: _sceneGroups.length,
                  onPageChanged: _handleSceneChanged,
                  itemBuilder: (context, index) {
                    final sceneGroup = _sceneGroups[index];
                    return _DetailPlaybackSceneGroupView(
                      group: sceneGroup,
                      controller: sceneGroup.pages.length > 1
                          ? _controllerForScene(index)
                          : null,
                      onPageChanged: (pageIndex) =>
                          _handleScenePageChanged(index, pageIndex),
                      totalPageCount: _pages.length,
                    );
                  },
                ),
              ),
            ),
            Positioned.fill(
              top: 96,
              child: IgnorePointer(
                ignoring: false,
                child: Row(
                  children: [
                    Expanded(
                      child: GestureDetector(
                        key: const Key('profileDetailTapPrev'),
                        behavior: HitTestBehavior.translucent,
                        onTapDown: (_) {
                          _isHolding = true;
                          _pauseAutoplay();
                        },
                        onTapCancel: () {
                          _isHolding = false;
                          _resumeAutoplay();
                        },
                        onTapUp: (_) {
                          _isHolding = false;
                          _goPrevious();
                        },
                      ),
                    ),
                    Expanded(
                      child: GestureDetector(
                        key: const Key('profileDetailTapNext'),
                        behavior: HitTestBehavior.translucent,
                        onTapDown: (_) {
                          _isHolding = true;
                          _pauseAutoplay();
                        },
                        onTapCancel: () {
                          _isHolding = false;
                          _resumeAutoplay();
                        },
                        onTapUp: (_) {
                          _isHolding = false;
                          _goNext();
                        },
                      ),
                    ),
                  ],
                ),
              ),
            ),
            SafeArea(
              bottom: false,
              child: Padding(
                padding: const EdgeInsets.fromLTRB(12, 10, 12, 0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    AnimatedBuilder(
                      animation: _autoplayController,
                      builder: (context, _) {
                        return _DetailPlaybackProgress(
                          count: _pages.length,
                          activeIndex: _activeFlatIndex,
                          progress: _canAutoplayCurrentPage()
                              ? _autoplayController.value
                              : 1,
                        );
                      },
                    ),
                    const SizedBox(height: 10),
                    _DetailPlaybackTopBar(
                      flowTitle: widget.flowTitle,
                      sceneTitle: activePage.overlayTitle,
                      sceneMeta: activePage.pageCountInScene > 1
                          ? '${activePage.pageIndexInScene + 1}/${activePage.pageCountInScene}'
                          : '',
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

  void _handleAutoplayStatus(AnimationStatus status) {
    if (status != AnimationStatus.completed || !mounted) {
      return;
    }
    _goNext();
  }

  void _handleSceneChanged(int index) {
    if (!mounted) {
      return;
    }
    setState(() => _activeSceneIndex = index);
    _restartAutoplay();
  }

  void _handleScenePageChanged(int sceneIndex, int pageIndex) {
    if (!mounted) {
      return;
    }
    final current = _activePageByScene[sceneIndex] ?? 0;
    if (current == pageIndex) {
      return;
    }
    _activePageByScene[sceneIndex] = pageIndex;
    if (sceneIndex != _activeSceneIndex) {
      return;
    }
    setState(() {});
    _restartAutoplay();
  }

  void _goNext() {
    final sceneGroup = _currentSceneGroup;
    final scenePageIndex = _currentScenePageIndex;
    if (scenePageIndex < sceneGroup.pages.length - 1) {
      _goToScenePage(_activeSceneIndex, scenePageIndex + 1);
      return;
    }
    _goToScene(_activeSceneIndex + 1, targetPageIndex: 0);
  }

  void _goPrevious() {
    final scenePageIndex = _currentScenePageIndex;
    if (scenePageIndex > 0) {
      _goToScenePage(_activeSceneIndex, scenePageIndex - 1);
      return;
    }
    if (_activeSceneIndex <= 0) {
      _restartAutoplay();
      return;
    }
    final previousSceneIndex = _activeSceneIndex - 1;
    final previousScene = _sceneGroups[previousSceneIndex];
    _goToScene(
      previousSceneIndex,
      targetPageIndex: previousScene.pages.length - 1,
    );
  }

  void _goToScene(int sceneIndex, {required int targetPageIndex}) {
    final clampedScene = sceneIndex.clamp(0, _sceneGroups.length - 1);
    final targetScene = _sceneGroups[clampedScene];
    final clampedPage = targetPageIndex.clamp(0, targetScene.pages.length - 1);
    _activePageByScene[clampedScene] = clampedPage;
    final nestedController = _scenePageControllers[clampedScene];
    if (nestedController != null && nestedController.hasClients) {
      nestedController.jumpToPage(clampedPage);
    }
    if (clampedScene == _activeSceneIndex) {
      _goToScenePage(clampedScene, clampedPage);
      return;
    }
    _pauseAutoplay(reset: true);
    if (_pageController.hasClients) {
      _pageController.animateToPage(
        clampedScene,
        duration: _kDetailPlaybackPageTurn,
        curve: Curves.easeOutCubic,
      );
      return;
    }
    setState(() => _activeSceneIndex = clampedScene);
    _restartAutoplay();
  }

  void _goToScenePage(int sceneIndex, int pageIndex) {
    final sceneGroup = _sceneGroups[sceneIndex];
    final clampedPage = pageIndex.clamp(0, sceneGroup.pages.length - 1);
    if (sceneIndex != _activeSceneIndex) {
      _activePageByScene[sceneIndex] = clampedPage;
      return;
    }
    if (clampedPage == _currentScenePageIndex) {
      _restartAutoplay();
      return;
    }
    _pauseAutoplay(reset: true);
    final controller = _controllerForScene(sceneIndex);
    if (controller.hasClients) {
      controller.animateToPage(
        clampedPage,
        duration: _kDetailPlaybackPageTurn,
        curve: Curves.easeOutCubic,
      );
      return;
    }
    _activePageByScene[sceneIndex] = clampedPage;
    setState(() {});
    _restartAutoplay();
  }

  void _restartAutoplay() {
    _autoplayController
      ..stop()
      ..value = 0;
    if (!_canAutoplayCurrentPage()) {
      return;
    }
    _autoplayController.forward();
  }

  void _pauseAutoplay({bool reset = false}) {
    _autoplayController.stop();
    if (reset) {
      _autoplayController.value = 0;
    }
  }

  void _resumeAutoplay() {
    if (!_canAutoplayCurrentPage()) {
      return;
    }
    if (_autoplayController.isAnimating) {
      return;
    }
    if (_autoplayController.value >= 1) {
      _autoplayController.value = 0;
    }
    _autoplayController.forward();
  }

  bool _canAutoplayCurrentPage() {
    final page = _currentPage;
    return page.allowAutoAdvance &&
        !page.requiresOverflowScroll &&
        !_isHolding &&
        !_isDragging &&
        !_isInactive;
  }

  PageController _controllerForScene(int sceneIndex) {
    return _scenePageControllers.putIfAbsent(
      sceneIndex,
      () => PageController(initialPage: _activePageByScene[sceneIndex] ?? 0),
    );
  }

  void _configurePlayback(List<ProfileDetailSceneData> scenes) {
    _disposeScenePageControllers();
    _sceneGroups = _buildSceneGroups(_resolvedScenes(scenes));
    _pages = [for (final sceneGroup in _sceneGroups) ...sceneGroup.pages];
    _activePageByScene
      ..clear()
      ..addEntries([
        for (var index = 0; index < _sceneGroups.length; index++)
          MapEntry(index, 0),
      ]);
    _activeSceneIndex = 0;
  }

  void _disposeScenePageControllers() {
    for (final controller in _scenePageControllers.values) {
      controller.dispose();
    }
    _scenePageControllers.clear();
  }
}

class _ProfileDetailPlaybackPageData {
  const _ProfileDetailPlaybackPageData({
    required this.sceneId,
    required this.playbackId,
    required this.variant,
    required this.eyebrow,
    required this.title,
    required this.intro,
    required this.bodyBlocks,
    required this.chips,
    required this.astroSources,
    required this.whyText,
    required this.illustrationAsset,
    required this.nextTitle,
    required this.pageIndexInScene,
    required this.pageCountInScene,
    required this.isContinuation,
    required this.allowAutoAdvance,
    required this.requiresOverflowScroll,
    this.proofRaw = '',
  });

  final String sceneId;
  final String playbackId;
  final ProfileDetailSceneVariant variant;
  final String eyebrow;
  final String title;
  final String intro;
  final List<String> bodyBlocks;
  final List<String> chips;
  final List<String> astroSources;
  final String whyText;
  final JoviaIllustrationAsset illustrationAsset;
  final String nextTitle;
  final int pageIndexInScene;
  final int pageCountInScene;
  final bool isContinuation;
  final bool allowAutoAdvance;
  final bool requiresOverflowScroll;

  /// Thread-level proof chip content (voice spec v2.1 §11.4).
  /// Only non-empty on primary scene page; continuation pages always '' —
  /// "sessiz imza" appears once per thread, not on every chunk.
  final String proofRaw;

  String get overlayTitle => isContinuation && pageCountInScene > 1
      ? currentL10n().profileDetailContinuationTitle(title)
      : title;

  List<String> get influenceLabels {
    if (astroSources.isNotEmpty) {
      return astroSources;
    }
    return chips.take(3).toList(growable: false);
  }

  _ProfileDetailPlaybackPageData copyWith({
    String? nextTitle,
    int? pageIndexInScene,
    int? pageCountInScene,
    bool? allowAutoAdvance,
    bool? requiresOverflowScroll,
    String? whyText,
  }) {
    return _ProfileDetailPlaybackPageData(
      sceneId: sceneId,
      playbackId: playbackId,
      variant: variant,
      eyebrow: eyebrow,
      title: title,
      intro: intro,
      bodyBlocks: bodyBlocks,
      chips: chips,
      astroSources: astroSources,
      whyText: whyText ?? this.whyText,
      illustrationAsset: illustrationAsset,
      nextTitle: nextTitle ?? this.nextTitle,
      pageIndexInScene: pageIndexInScene ?? this.pageIndexInScene,
      pageCountInScene: pageCountInScene ?? this.pageCountInScene,
      isContinuation: isContinuation,
      allowAutoAdvance: allowAutoAdvance ?? this.allowAutoAdvance,
      requiresOverflowScroll:
          requiresOverflowScroll ?? this.requiresOverflowScroll,
      proofRaw: proofRaw,
    );
  }
}

class _ProfileDetailPlaybackSceneGroup {
  const _ProfileDetailPlaybackSceneGroup({
    required this.sceneId,
    required this.pages,
    required this.flatStartIndex,
  });

  final String sceneId;
  final List<_ProfileDetailPlaybackPageData> pages;
  final int flatStartIndex;
}

List<ProfileDetailSceneData> _resolvedScenes(
  List<ProfileDetailSceneData> scenes,
) {
  if (scenes.isNotEmpty) {
    return scenes;
  }
  final l10n = currentL10n();
  return <ProfileDetailSceneData>[
    ProfileDetailSceneData(
      id: 'empty',
      eyebrow: l10n.profileDetailFallbackEyebrow,
      title: l10n.profileDetailFallbackTitle,
      intro: l10n.profileDetailFallbackIntro,
      bodyBlocks: <String>[l10n.profileDetailFallbackBody],
      chips: <String>[],
      astroSources: <String>[],
      whyText: '',
      illustrationAsset: JoviaIllustrationAsset.planet,
      variant: ProfileDetailSceneVariant.glance,
    ),
  ];
}

List<_ProfileDetailPlaybackSceneGroup> _buildSceneGroups(
  List<ProfileDetailSceneData> scenes,
) {
  final groups = <_ProfileDetailPlaybackSceneGroup>[];
  var flatStartIndex = 0;
  for (final scene in scenes) {
    final scenePages = _splitSceneToPlaybackPages(scene);
    if (scenePages.isEmpty) {
      continue;
    }
    final resolvedPages = <_ProfileDetailPlaybackPageData>[
      for (var index = 0; index < scenePages.length; index++)
        scenePages[index].copyWith(
          nextTitle: index == scenePages.length - 1
              ? scene.nextTitle.trim()
              : '',
          pageIndexInScene: index,
          pageCountInScene: scenePages.length,
        ),
    ];
    groups.add(
      _ProfileDetailPlaybackSceneGroup(
        sceneId: scene.id,
        pages: resolvedPages,
        flatStartIndex: flatStartIndex,
      ),
    );
    flatStartIndex += resolvedPages.length;
  }
  if (groups.isEmpty) {
    return _buildSceneGroups(_resolvedScenes(const <ProfileDetailSceneData>[]));
  }
  final lastGroup = groups.last;
  final lastPages = [...lastGroup.pages];
  lastPages[lastPages.length - 1] = lastPages.last.copyWith(
    allowAutoAdvance: false,
  );
  groups[groups.length - 1] = _ProfileDetailPlaybackSceneGroup(
    sceneId: lastGroup.sceneId,
    pages: lastPages,
    flatStartIndex: lastGroup.flatStartIndex,
  );
  return groups;
}

List<_ProfileDetailPlaybackPageData> _buildPlaybackPages(
  List<ProfileDetailSceneData> scenes,
) {
  return [
    for (final sceneGroup in _buildSceneGroups(scenes)) ...sceneGroup.pages,
  ];
}

@visibleForTesting
List<ProfileDetailPlaybackDebugPage> debugBuildProfileDetailPlaybackPages(
  List<ProfileDetailSceneData> scenes,
) {
  return _buildPlaybackPages(_resolvedScenes(scenes))
      .map(
        (item) => ProfileDetailPlaybackDebugPage(
          playbackId: item.playbackId,
          title: item.title,
          bodyBlocks: item.bodyBlocks,
          whyText: item.whyText,
          nextTitle: item.nextTitle,
          pageIndexInScene: item.pageIndexInScene,
          pageCountInScene: item.pageCountInScene,
          allowAutoAdvance: item.allowAutoAdvance,
          isContinuation: item.isContinuation,
          proofRaw: item.proofRaw,
        ),
      )
      .toList(growable: false);
}

class ProfileDetailPlaybackDebugPage {
  const ProfileDetailPlaybackDebugPage({
    required this.playbackId,
    required this.title,
    required this.bodyBlocks,
    required this.whyText,
    required this.nextTitle,
    required this.pageIndexInScene,
    required this.pageCountInScene,
    required this.allowAutoAdvance,
    this.isContinuation = false,
    this.proofRaw = '',
  });

  final String playbackId;
  final String title;
  final List<String> bodyBlocks;
  final String whyText;
  final String nextTitle;
  final int pageIndexInScene;
  final int pageCountInScene;
  final bool allowAutoAdvance;

  /// Whether this debug page represents a continuation chunk (not the
  /// primary scene page). Voice spec v2.1 §11.4 — proof_raw only on primary.
  final bool isContinuation;

  /// Thread-level astrological credit line (voice spec v2.1 §11.4).
  /// Empty on continuation pages or when scene is non-thread sourced.
  final String proofRaw;
}

List<_ProfileDetailPlaybackPageData> _splitSceneToPlaybackPages(
  ProfileDetailSceneData scene,
) {
  final blocks = scene.bodyBlocks
      .map((item) => item.trim())
      .where((item) => item.isNotEmpty)
      .toList(growable: false);
  final intro = scene.intro.trim();
  final why = scene.whyText.trim();
  final chips = scene.chips
      .map((item) => item.trim())
      .where((item) => item.isNotEmpty)
      .take(3)
      .toList(growable: false);
  final astroSources = scene.astroSources
      .map((item) => item.trim())
      .where((item) => item.isNotEmpty)
      .take(3)
      .toList(growable: false);

  final blocksPerPage = _blocksPerPlaybackPage(scene.variant);
  final playbackPages = <_ProfileDetailPlaybackPageData>[];
  final leadingBlocks = blocks.take(blocksPerPage).toList(growable: false);
  final remainingBlocks = blocks.skip(blocksPerPage).toList(growable: false);

  playbackPages.add(
    _ProfileDetailPlaybackPageData(
      sceneId: scene.id,
      playbackId: '${scene.id}_0',
      variant: scene.variant,
      eyebrow: scene.eyebrow.trim().isNotEmpty
          ? scene.eyebrow
          : currentL10n().profileDetailDefaultEyebrow,
      title: scene.title.trim().isNotEmpty
          ? scene.title
          : currentL10n().profileDetailDefaultTitle,
      intro: intro,
      bodyBlocks: leadingBlocks,
      chips: chips,
      astroSources: astroSources,
      whyText: '',
      illustrationAsset: scene.illustrationAsset,
      nextTitle: '',
      pageIndexInScene: 0,
      pageCountInScene: 1,
      isContinuation: false,
      allowAutoAdvance: true,
      requiresOverflowScroll: _requiresOverflowScroll(
        title: scene.title,
        intro: intro,
        bodyBlocks: leadingBlocks,
        whyText: '',
      ),
      // Voice spec v2.1 §11.4 — proof chip appears on primary page only.
      proofRaw: scene.proofRaw,
    ),
  );

  var continuationIndex = 1;
  for (var index = 0; index < remainingBlocks.length; index += blocksPerPage) {
    final chunk = remainingBlocks.skip(index).take(blocksPerPage).toList();
    playbackPages.add(
      _ProfileDetailPlaybackPageData(
        sceneId: scene.id,
        playbackId: '${scene.id}_$continuationIndex',
        variant: _continuationVariantFor(scene.variant),
        eyebrow: scene.eyebrow.trim().isNotEmpty
            ? scene.eyebrow
            : currentL10n().profileDetailDefaultEyebrow,
        title: scene.title.trim().isNotEmpty
            ? scene.title
            : currentL10n().profileDetailDefaultTitle,
        intro: '',
        bodyBlocks: chunk,
        chips: const <String>[],
        astroSources: const <String>[],
        whyText: '',
        illustrationAsset: scene.illustrationAsset,
        nextTitle: '',
        pageIndexInScene: continuationIndex,
        pageCountInScene: 1,
        isContinuation: true,
        allowAutoAdvance: true,
        requiresOverflowScroll: _requiresOverflowScroll(
          title: scene.title,
          intro: '',
          bodyBlocks: chunk,
          whyText: '',
        ),
      ),
    );
    continuationIndex += 1;
  }

  if (why.isNotEmpty) {
    final shouldSplitWhy =
        blocks.isNotEmpty || intro.isNotEmpty || playbackPages.length > 1;
    if (shouldSplitWhy) {
      playbackPages.add(
        _ProfileDetailPlaybackPageData(
          sceneId: scene.id,
          playbackId: '${scene.id}_$continuationIndex',
          variant: ProfileDetailSceneVariant.glance,
          eyebrow: currentL10n().profileDetailWhyHere,
          title: scene.title.trim().isNotEmpty
              ? scene.title
              : currentL10n().profileDetailDefaultTitle,
          intro: '',
          bodyBlocks: const <String>[],
          chips: const <String>[],
          astroSources: const <String>[],
          whyText: why,
          illustrationAsset: scene.illustrationAsset,
          nextTitle: '',
          pageIndexInScene: continuationIndex,
          pageCountInScene: 1,
          isContinuation: true,
          allowAutoAdvance: true,
          requiresOverflowScroll: _requiresOverflowScroll(
            title: scene.title,
            intro: '',
            bodyBlocks: const <String>[],
            whyText: why,
          ),
        ),
      );
    } else {
      playbackPages[0] = playbackPages.first.copyWith(
        whyText: why,
        requiresOverflowScroll: _requiresOverflowScroll(
          title: playbackPages.first.title,
          intro: playbackPages.first.intro,
          bodyBlocks: playbackPages.first.bodyBlocks,
          whyText: why,
        ),
      );
    }
  }

  if (playbackPages.length == 1 &&
      playbackPages.first.bodyBlocks.isEmpty &&
      playbackPages.first.intro.isEmpty &&
      why.isEmpty) {
    return [
      playbackPages.first.copyWith(
        requiresOverflowScroll: _requiresOverflowScroll(
          title: playbackPages.first.title,
          intro: playbackPages.first.intro,
          bodyBlocks: playbackPages.first.bodyBlocks,
          whyText: playbackPages.first.whyText,
        ),
      ),
    ];
  }

  return playbackPages;
}

int _blocksPerPlaybackPage(ProfileDetailSceneVariant variant) {
  return switch (variant) {
    ProfileDetailSceneVariant.glance => 1,
    ProfileDetailSceneVariant.symbol => 1,
    ProfileDetailSceneVariant.portal => 1,
    ProfileDetailSceneVariant.posterScene => 2,
    ProfileDetailSceneVariant.split => 2,
    ProfileDetailSceneVariant.structuredInsight => 3,
  };
}

ProfileDetailSceneVariant _continuationVariantFor(
  ProfileDetailSceneVariant variant,
) {
  return switch (variant) {
    ProfileDetailSceneVariant.posterScene =>
      ProfileDetailSceneVariant.structuredInsight,
    ProfileDetailSceneVariant.glance => ProfileDetailSceneVariant.posterScene,
    ProfileDetailSceneVariant.symbol => ProfileDetailSceneVariant.glance,
    ProfileDetailSceneVariant.portal => ProfileDetailSceneVariant.glance,
    _ => variant,
  };
}

bool _requiresOverflowScroll({
  required String title,
  required String intro,
  required List<String> bodyBlocks,
  required String whyText,
}) {
  final longestBlock = bodyBlocks.fold<int>(
    0,
    (current, item) => item.length > current ? item.length : current,
  );
  return title.length > 88 ||
      intro.length > 260 ||
      longestBlock > 420 ||
      whyText.length > 360;
}

class _DetailPlaybackProgress extends StatelessWidget {
  const _DetailPlaybackProgress({
    required this.count,
    required this.activeIndex,
    required this.progress,
  });

  final int count;
  final int activeIndex;
  final double progress;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Row(
      children: [
        for (var index = 0; index < count; index++) ...[
          Expanded(
            child: Container(
              height: 3,
              decoration: BoxDecoration(
                color: profile.colors.hairline,
                borderRadius: BorderRadius.circular(999),
              ),
              clipBehavior: Clip.antiAlias,
              child: Align(
                alignment: Alignment.centerLeft,
                child: FractionallySizedBox(
                  widthFactor: index < activeIndex
                      ? 1
                      : index == activeIndex
                      ? progress.clamp(0, 1)
                      : 0,
                  child: Container(color: profile.colors.text),
                ),
              ),
            ),
          ),
          if (index != count - 1) const SizedBox(width: 4),
        ],
      ],
    );
  }
}

class _DetailPlaybackTopBar extends StatelessWidget {
  const _DetailPlaybackTopBar({
    required this.flowTitle,
    required this.sceneTitle,
    required this.sceneMeta,
  });

  final String flowTitle;
  final String sceneTitle;
  final String sceneMeta;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        JoviaGlassIconButton(
          onTap: () => Navigator.of(context).maybePop(),
          size: 42,
          child: const JoviaUiIcon(asset: JoviaUiAsset.back, size: 18),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                turkishToUpper(flowTitle),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: profile.typography.monoEyebrow.copyWith(
                  color: profile.colors.textLight,
                  fontSize: 11.5,
                  letterSpacing: 1.8,
                ),
              ),
              const SizedBox(height: 2),
              Text(
                sceneTitle,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: profile.typography.metaSoft.copyWith(
                  color: profile.colors.text,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ],
          ),
        ),
        if (sceneMeta.isNotEmpty)
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
            decoration: BoxDecoration(
              color: profile.colors.panelStrong,
              borderRadius: BorderRadius.circular(999),
              border: Border.all(color: profile.colors.hairline),
            ),
            child: Text(
              sceneMeta,
              style: profile.typography.buttonLabel.copyWith(
                color: profile.colors.text,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
      ],
    );
  }
}

class _DetailPlaybackSceneGroupView extends StatelessWidget {
  const _DetailPlaybackSceneGroupView({
    required this.group,
    required this.controller,
    required this.onPageChanged,
    required this.totalPageCount,
  });

  final _ProfileDetailPlaybackSceneGroup group;
  final PageController? controller;
  final ValueChanged<int> onPageChanged;
  final int totalPageCount;

  @override
  Widget build(BuildContext context) {
    if (group.pages.length <= 1) {
      return _DetailPlaybackPage(
        page: group.pages.first,
        isLastOverallPage: group.flatStartIndex == totalPageCount - 1,
      );
    }
    return PageView.builder(
      key: ValueKey<String>('detailScenePager_${group.sceneId}'),
      controller: controller,
      scrollDirection: Axis.horizontal,
      itemCount: group.pages.length,
      onPageChanged: onPageChanged,
      itemBuilder: (context, index) {
        return _DetailPlaybackPage(
          page: group.pages[index],
          isLastOverallPage: group.flatStartIndex + index == totalPageCount - 1,
        );
      },
    );
  }
}

class _DetailPlaybackPage extends StatelessWidget {
  const _DetailPlaybackPage({
    required this.page,
    required this.isLastOverallPage,
  });

  final _ProfileDetailPlaybackPageData page;
  final bool isLastOverallPage;

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      bottom: false,
      child: LayoutBuilder(
        builder: (context, constraints) {
          return Padding(
            key: ValueKey<String>('detailPlaybackPage_${page.playbackId}'),
            padding: const EdgeInsets.fromLTRB(16, 88, 16, 18),
            child: ConstrainedBox(
              constraints: BoxConstraints(
                minHeight: constraints.maxHeight - 106,
              ),
              child: _DetailVariantSurface(
                page: page,
                isLastOverallPage: isLastOverallPage,
              ),
            ),
          );
        },
      ),
    );
  }
}

class _DetailPageFill extends StatelessWidget {
  const _DetailPageFill({required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context) {
    return SizedBox.expand(
      child: ConstrainedBox(
        constraints: const BoxConstraints.expand(),
        child: child,
      ),
    );
  }
}

class _DetailScrollableFill extends StatelessWidget {
  const _DetailScrollableFill({required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        return SingleChildScrollView(
          child: ConstrainedBox(
            constraints: BoxConstraints(minHeight: constraints.maxHeight),
            child: child,
          ),
        );
      },
    );
  }
}

class _DetailVariantSurface extends StatelessWidget {
  const _DetailVariantSurface({
    required this.page,
    required this.isLastOverallPage,
  });

  final _ProfileDetailPlaybackPageData page;
  final bool isLastOverallPage;

  @override
  Widget build(BuildContext context) {
    return switch (page.variant) {
      ProfileDetailSceneVariant.glance => _DetailGlancePlaybackCard(
        page: page,
        isLastOverallPage: isLastOverallPage,
      ),
      ProfileDetailSceneVariant.posterScene => _DetailPosterPlaybackCard(
        page: page,
        isLastOverallPage: isLastOverallPage,
      ),
      ProfileDetailSceneVariant.structuredInsight =>
        _DetailStructuredPlaybackCard(
          page: page,
          isLastOverallPage: isLastOverallPage,
        ),
      ProfileDetailSceneVariant.split => _DetailSplitPlaybackCard(
        page: page,
        isLastOverallPage: isLastOverallPage,
      ),
      ProfileDetailSceneVariant.symbol => _DetailSymbolPlaybackCard(
        page: page,
        isLastOverallPage: isLastOverallPage,
      ),
      ProfileDetailSceneVariant.portal => _DetailPortalPlaybackCard(
        page: page,
        isLastOverallPage: isLastOverallPage,
      ),
    };
  }
}

class _DetailFlowBackdrop extends StatelessWidget {
  const _DetailFlowBackdrop({required this.tone});

  final ProfileDetailTone tone;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return IgnorePointer(
      child: Stack(
        fit: StackFit.expand,
        children: [
          DecoratedBox(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  _detailPageBackground(context, tone),
                  profile.colors.bg,
                  Color.alphaBlend(
                    tone.accentSoft.withValues(alpha: 0.08),
                    profile.colors.bg,
                  ),
                ],
              ),
            ),
          ),
          Positioned(
            top: -110,
            right: -72,
            child: Container(
              width: 240,
              height: 240,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: RadialGradient(
                  colors: [
                    tone.accent.withValues(alpha: 0.18),
                    Colors.transparent,
                  ],
                ),
              ),
            ),
          ),
          Positioned(
            left: -92,
            bottom: -128,
            child: Container(
              width: 260,
              height: 260,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: RadialGradient(
                  colors: [
                    tone.accentSoft.withValues(alpha: 0.16),
                    Colors.transparent,
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

class _DetailSurfaceCard extends StatelessWidget {
  const _DetailSurfaceCard({
    required this.child,
    required this.tone,
    this.padding = const EdgeInsets.all(20),
    this.radius = 30,
  });

  final Widget child;
  final ProfileDetailTone tone;
  final EdgeInsetsGeometry padding;
  final double radius;

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return JoviaSurfaceCard(
      radius: radius,
      padding: EdgeInsets.zero,
      backgroundColor: _detailCardBackground(context, tone, emphasized: true),
      borderColor: _detailStrokeColor(context, tone),
      child: Stack(
        children: [
          Positioned(
            right: -20,
            top: -24,
            child: Container(
              width: 120,
              height: 120,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: RadialGradient(
                  colors: [
                    tone.accent.withValues(alpha: isDark ? 0.16 : 0.22),
                    Colors.transparent,
                  ],
                ),
              ),
            ),
          ),
          Positioned(
            right: 16,
            top: 16,
            child: IgnorePointer(
              child: Opacity(
                opacity: isDark ? 0.76 : 0.92,
                child: JoviaMoodStickerCluster(
                  size: 18,
                  colors: <Color>[
                    tone.accent,
                    tone.accentSoft,
                    tone.accent.withValues(alpha: 0.86),
                  ],
                ),
              ),
            ),
          ),
          Positioned(
            left: -30,
            bottom: -38,
            child: Container(
              width: 138,
              height: 138,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: RadialGradient(
                  colors: [
                    tone.accent.withValues(alpha: isDark ? 0.1 : 0.14),
                    Colors.transparent,
                  ],
                ),
              ),
            ),
          ),
          Padding(padding: padding, child: child),
        ],
      ),
    );
  }
}

class _DetailInfluenceCorner extends StatelessWidget {
  const _DetailInfluenceCorner({
    required this.sources,
    required this.tone,
    this.maxWidth = 164,
  });

  final List<String> sources;
  final ProfileDetailTone tone;
  final double maxWidth;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    if (sources.isEmpty) {
      return const SizedBox.shrink();
    }
    final visible = sources.take(2).toList(growable: false);
    final remainder = sources.length - visible.length;
    final textLines = <String>[...visible, if (remainder > 0) '+$remainder'];
    return ConstrainedBox(
      constraints: BoxConstraints(maxWidth: maxWidth),
      child: Container(
        padding: const EdgeInsets.fromLTRB(12, 10, 12, 10),
        decoration: BoxDecoration(
          color: _detailInsetBackground(context, tone, highlighted: true),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: _detailStrokeColor(context, tone)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              _detailInfluenceLabel(context),
              style: profile.typography.meta.copyWith(
                color: _detailLabelTextColor(
                  context,
                  tone,
                ).withValues(alpha: 0.92),
                fontSize: 11.5,
                fontWeight: FontWeight.w700,
                letterSpacing: 0.24,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              textLines.join('\n'),
              maxLines: 3,
              overflow: TextOverflow.ellipsis,
              style: profile.typography.metaSoft.copyWith(
                color: _detailInfluenceTextColor(context),
                fontSize: 12.2,
                fontWeight: FontWeight.w600,
                height: 1.35,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _DetailGlancePlaybackCard extends StatelessWidget {
  const _DetailGlancePlaybackCard({
    required this.page,
    required this.isLastOverallPage,
  });

  final _ProfileDetailPlaybackPageData page;
  final bool isLastOverallPage;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final tone = _detailToneForPlaybackPage(page);
    final bodyText = page.bodyBlocks.isNotEmpty
        ? page.bodyBlocks.first
        : page.intro.trim();
    final highlightLines = _detailHighlightLines(page, maxLines: 1);
    return _DetailPageFill(
      child: _DetailSurfaceCard(
        tone: tone,
        radius: 30,
        padding: const EdgeInsets.fromLTRB(24, 24, 24, 22),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            Align(
              alignment: Alignment.centerLeft,
              child: Text(
                turkishToUpper(page.eyebrow),
                style: profile.typography.monoEyebrow.copyWith(
                  color: profile.colors.warmAccent,
                  fontSize: 11.5,
                  letterSpacing: 1.8,
                ),
              ),
            ),
            if (page.influenceLabels.isNotEmpty) ...[
              const SizedBox(height: 10),
              Align(
                alignment: Alignment.centerRight,
                child: _DetailInfluenceCorner(
                  sources: page.influenceLabels,
                  tone: tone,
                  maxWidth: 188,
                ),
              ),
            ],
            const Spacer(),
            JoviaIllustrationAccent(
              asset: page.illustrationAsset,
              width: 162,
              height: 162,
              opacity: 0.96,
            ),
            const SizedBox(height: 18),
            Text(
              page.title,
              textAlign: TextAlign.center,
              style: profile.typography.editorialHeadline.copyWith(
                color: profile.colors.text,
                fontSize: 28,
                height: 1.06,
              ),
            ),
            if (highlightLines.isNotEmpty) ...[
              const SizedBox(height: 14),
              JoviaSentenceBubbleStack(
                lines: highlightLines,
                centered: true,
                compact: true,
                accents: <Color>[tone.accent, tone.accentSoft],
              ),
            ],
            if (bodyText.isNotEmpty) ...[
              const SizedBox(height: 12),
              Text(
                bodyText,
                textAlign: TextAlign.center,
                maxLines: page.requiresOverflowScroll ? null : 3,
                overflow: page.requiresOverflowScroll
                    ? TextOverflow.visible
                    : TextOverflow.ellipsis,
                style: profile.typography.bodyReading.copyWith(
                  color: _detailBodyTextColor(context),
                  fontSize: 14.8,
                  height: 1.52,
                ),
              ),
            ],
            const Spacer(),
            Align(
              alignment: Alignment.centerLeft,
              child: _DetailPageFooter(
                page: page,
                isLastOverallPage: isLastOverallPage,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _DetailPosterPlaybackCard extends StatelessWidget {
  const _DetailPosterPlaybackCard({
    required this.page,
    required this.isLastOverallPage,
  });

  final _ProfileDetailPlaybackPageData page;
  final bool isLastOverallPage;

  @override
  Widget build(BuildContext context) {
    final tone = _detailToneForPlaybackPage(page);
    final content = _DetailTextSection(
      page: page,
      tone: tone,
      titleSize: 34,
      isLastOverallPage: isLastOverallPage,
      scrollable: page.requiresOverflowScroll,
    );
    return _DetailPageFill(
      child: _DetailSurfaceCard(
        tone: tone,
        radius: 32,
        padding: EdgeInsets.zero,
        child: Stack(
          children: [
            if (page.influenceLabels.isNotEmpty)
              Positioned(
                top: 18,
                right: 18,
                child: _DetailInfluenceCorner(
                  sources: page.influenceLabels,
                  tone: tone,
                  maxWidth: 176,
                ),
              ),
            Positioned(
              right: 0,
              bottom: 10,
              child: JoviaIllustrationAccent(
                asset: page.illustrationAsset,
                width: 148,
                height: 148,
                opacity: 0.94,
              ),
            ),
            Padding(
              padding: const EdgeInsets.fromLTRB(22, 24, 22, 22),
              child: page.requiresOverflowScroll
                  ? _DetailScrollableFill(
                      child: Padding(
                        padding: const EdgeInsets.only(right: 96),
                        child: content,
                      ),
                    )
                  : Padding(
                      padding: const EdgeInsets.only(right: 96),
                      child: content,
                    ),
            ),
          ],
        ),
      ),
    );
  }
}

class _DetailStructuredPlaybackCard extends StatelessWidget {
  const _DetailStructuredPlaybackCard({
    required this.page,
    required this.isLastOverallPage,
  });

  final _ProfileDetailPlaybackPageData page;
  final bool isLastOverallPage;

  @override
  Widget build(BuildContext context) {
    final tone = _detailToneForPlaybackPage(page);
    return _DetailPageFill(
      child: _DetailSurfaceCard(
        tone: tone,
        radius: 30,
        padding: const EdgeInsets.fromLTRB(20, 20, 20, 20),
        child: page.requiresOverflowScroll
            ? _DetailScrollableFill(
                child: _DetailStructuredBody(
                  page: page,
                  tone: tone,
                  isLastOverallPage: isLastOverallPage,
                ),
              )
            : _DetailStructuredBody(
                page: page,
                tone: tone,
                isLastOverallPage: isLastOverallPage,
              ),
      ),
    );
  }
}

class _DetailStructuredBody extends StatelessWidget {
  const _DetailStructuredBody({
    required this.page,
    required this.tone,
    required this.isLastOverallPage,
  });

  final _ProfileDetailPlaybackPageData page;
  final ProfileDetailTone tone;
  final bool isLastOverallPage;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final highlightLines = _detailHighlightLines(page, maxLines: 1);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              width: 3,
              height: 74,
              decoration: BoxDecoration(
                color: tone.accent,
                borderRadius: BorderRadius.circular(999),
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    turkishToUpper(page.eyebrow),
                    style: profile.typography.monoEyebrow.copyWith(
                      color: _detailLabelTextColor(context, tone),
                      fontSize: 11.5,
                      letterSpacing: 1.7,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    page.title,
                    style: profile.typography.section.copyWith(
                      color: profile.colors.text,
                      fontSize: 24,
                      height: 1.08,
                    ),
                  ),
                  if (page.intro.trim().isNotEmpty) ...[
                    const SizedBox(height: 10),
                    Text(
                      page.intro,
                      style: profile.typography.bodyReading.copyWith(
                        color: _detailIntroTextColor(context),
                        fontSize: 14.6,
                        height: 1.5,
                      ),
                    ),
                  ],
                ],
              ),
            ),
            const SizedBox(width: 12),
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                if (page.influenceLabels.isNotEmpty) ...[
                  _DetailInfluenceCorner(
                    sources: page.influenceLabels,
                    tone: tone,
                    maxWidth: 156,
                  ),
                  const SizedBox(height: 10),
                ],
                JoviaIllustrationAccent(
                  asset: page.illustrationAsset,
                  width: 62,
                  height: 62,
                  opacity: 0.88,
                ),
              ],
            ),
          ],
        ),
        if (highlightLines.isNotEmpty) ...[
          const SizedBox(height: 14),
          JoviaSentenceBubbleStack(
            lines: highlightLines,
            compact: true,
            accents: <Color>[tone.accent, tone.accentSoft],
          ),
        ],
        if (page.bodyBlocks.isNotEmpty) ...[
          const SizedBox(height: 18),
          for (var index = 0; index < page.bodyBlocks.length; index++) ...[
            Container(
              width: double.infinity,
              padding: const EdgeInsets.fromLTRB(14, 12, 14, 12),
              decoration: BoxDecoration(
                color: _detailInsetBackground(context, tone),
                borderRadius: BorderRadius.circular(18),
                border: Border.all(color: _detailStrokeColor(context, tone)),
              ),
              child: Text(
                page.bodyBlocks[index],
                style: profile.typography.bodyReading.copyWith(
                  color: _detailBodyTextColor(context),
                  fontSize: 14.4,
                  height: 1.52,
                ),
              ),
            ),
            if (index != page.bodyBlocks.length - 1) const SizedBox(height: 10),
          ],
        ],
        if (page.chips.isNotEmpty) ...[
          const SizedBox(height: 14),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: page.chips
                .map((chip) => _DetailChip(label: chip, tone: tone))
                .toList(),
          ),
        ],
        if (page.whyText.trim().isNotEmpty) ...[
          const SizedBox(height: 16),
          _DetailWhyBlock(text: page.whyText, tone: tone),
        ],
        const SizedBox(height: 16),
        _DetailPageFooter(page: page, isLastOverallPage: isLastOverallPage),
      ],
    );
  }
}

class _DetailSplitPlaybackCard extends StatelessWidget {
  const _DetailSplitPlaybackCard({
    required this.page,
    required this.isLastOverallPage,
  });

  final _ProfileDetailPlaybackPageData page;
  final bool isLastOverallPage;

  @override
  Widget build(BuildContext context) {
    final tone = _detailToneForPlaybackPage(page);
    final leftText = page.bodyBlocks.isNotEmpty
        ? page.bodyBlocks.first
        : page.intro;
    final rightText = page.bodyBlocks.length > 1
        ? page.bodyBlocks[1]
        : (page.whyText.trim().isNotEmpty ? page.whyText : '');
    final extraBlocks = page.bodyBlocks.length > 2
        ? page.bodyBlocks.skip(2).toList(growable: false)
        : const <String>[];
    return _DetailPageFill(
      child: _DetailSurfaceCard(
        tone: tone,
        radius: 30,
        padding: const EdgeInsets.fromLTRB(20, 20, 20, 20),
        child: page.requiresOverflowScroll
            ? _DetailScrollableFill(
                child: _DetailSplitBody(
                  page: page,
                  tone: tone,
                  leftText: leftText,
                  rightText: rightText,
                  extraBlocks: extraBlocks,
                  isLastOverallPage: isLastOverallPage,
                ),
              )
            : _DetailSplitBody(
                page: page,
                tone: tone,
                leftText: leftText,
                rightText: rightText,
                extraBlocks: extraBlocks,
                isLastOverallPage: isLastOverallPage,
              ),
      ),
    );
  }
}

class _DetailSplitBody extends StatelessWidget {
  const _DetailSplitBody({
    required this.page,
    required this.tone,
    required this.leftText,
    required this.rightText,
    required this.extraBlocks,
    required this.isLastOverallPage,
  });

  final _ProfileDetailPlaybackPageData page;
  final ProfileDetailTone tone;
  final String leftText;
  final String rightText;
  final List<String> extraBlocks;
  final bool isLastOverallPage;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final highlightLines = _detailHighlightLines(page, maxLines: 1);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          turkishToUpper(page.eyebrow),
          style: profile.typography.monoEyebrow.copyWith(
            color: _detailLabelTextColor(context, tone),
            fontSize: 11.5,
            letterSpacing: 1.8,
          ),
        ),
        const SizedBox(height: 10),
        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Expanded(
              child: Text(
                page.title,
                style: profile.typography.editorialHeadline.copyWith(
                  color: profile.colors.text,
                  fontSize: 27,
                  height: 1.06,
                ),
              ),
            ),
            const SizedBox(width: 12),
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                if (page.influenceLabels.isNotEmpty) ...[
                  _DetailInfluenceCorner(
                    sources: page.influenceLabels,
                    tone: tone,
                    maxWidth: 156,
                  ),
                  const SizedBox(height: 10),
                ],
                JoviaIllustrationAccent(
                  asset: page.illustrationAsset,
                  width: 74,
                  height: 74,
                  opacity: 0.92,
                ),
              ],
            ),
          ],
        ),
        if (highlightLines.isNotEmpty) ...[
          const SizedBox(height: 14),
          JoviaSentenceBubbleStack(
            lines: highlightLines,
            compact: true,
            accents: <Color>[tone.accentSoft, tone.accent],
          ),
        ],
        const SizedBox(height: 18),
        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Expanded(
              child: _DetailSplitPane(
                title: context.l10n.profileDetailSideA,
                body: leftText,
                tone: tone,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _DetailSplitPane(
                title: context.l10n.profileDetailSideB,
                body: rightText.isNotEmpty ? rightText : page.intro,
                highlighted: true,
                tone: tone,
              ),
            ),
          ],
        ),
        if (extraBlocks.isNotEmpty) ...[
          const SizedBox(height: 14),
          for (final block in extraBlocks) ...[
            Text(
              block,
              style: profile.typography.bodyReading.copyWith(
                color: _detailBodyTextColor(context),
                fontSize: 14.2,
                height: 1.5,
              ),
            ),
            const SizedBox(height: 10),
          ],
        ],
        if (page.chips.isNotEmpty) ...[
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: page.chips
                .map((chip) => _DetailChip(label: chip, tone: tone))
                .toList(),
          ),
        ],
        const SizedBox(height: 16),
        _DetailPageFooter(page: page, isLastOverallPage: isLastOverallPage),
      ],
    );
  }
}

class _DetailSplitPane extends StatelessWidget {
  const _DetailSplitPane({
    required this.title,
    required this.body,
    required this.tone,
    this.highlighted = false,
  });

  final String title;
  final String body;
  final ProfileDetailTone tone;
  final bool highlighted;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Container(
      padding: const EdgeInsets.fromLTRB(14, 14, 14, 14),
      decoration: BoxDecoration(
        color: _detailInsetBackground(context, tone, highlighted: highlighted),
        borderRadius: BorderRadius.circular(18),
        border: Border.all(
          color: highlighted
              ? _detailStrokeColor(context, tone)
              : _detailStrokeColor(context, tone),
        ),
      ),
      child: Column(
        children: [
          Text(
            title,
            style: profile.typography.buttonLabel.copyWith(
              color: highlighted
                  ? _detailLabelTextColor(context, tone)
                  : _detailBodyTextColor(context),
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            body,
            style: profile.typography.bodyReading.copyWith(
              color: profile.colors.text,
              fontSize: 14.2,
              height: 1.48,
            ),
          ),
        ],
      ),
    );
  }
}

class _DetailSymbolPlaybackCard extends StatelessWidget {
  const _DetailSymbolPlaybackCard({
    required this.page,
    required this.isLastOverallPage,
  });

  final _ProfileDetailPlaybackPageData page;
  final bool isLastOverallPage;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final tone = _detailToneForPlaybackPage(page);
    final highlightLines = _detailHighlightLines(page, maxLines: 1);
    return _DetailPageFill(
      child: _DetailSurfaceCard(
        tone: tone,
        radius: 30,
        padding: const EdgeInsets.fromLTRB(22, 22, 22, 22),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            Align(
              alignment: Alignment.centerLeft,
              child: Text(
                turkishToUpper(page.eyebrow),
                style: profile.typography.monoEyebrow.copyWith(
                  color: _detailLabelTextColor(context, tone),
                  fontSize: 11.5,
                  letterSpacing: 1.7,
                ),
              ),
            ),
            if (page.influenceLabels.isNotEmpty) ...[
              const SizedBox(height: 10),
              Align(
                alignment: Alignment.centerRight,
                child: _DetailInfluenceCorner(
                  sources: page.influenceLabels,
                  tone: tone,
                  maxWidth: 188,
                ),
              ),
            ],
            const Spacer(),
            JoviaIllustrationAccent(
              asset: page.illustrationAsset,
              width: 170,
              height: 170,
              opacity: 0.96,
            ),
            const SizedBox(height: 16),
            Text(
              page.title,
              textAlign: TextAlign.center,
              style: profile.typography.section.copyWith(
                color: profile.colors.text,
                fontSize: 23,
                height: 1.1,
              ),
            ),
            if (highlightLines.isNotEmpty) ...[
              const SizedBox(height: 12),
              JoviaSentenceBubbleStack(
                lines: highlightLines,
                centered: true,
                compact: true,
                accents: <Color>[tone.accentSoft, tone.accent],
              ),
            ],
            if (page.intro.trim().isNotEmpty || page.bodyBlocks.isNotEmpty) ...[
              const SizedBox(height: 12),
              Text(
                page.intro.trim().isNotEmpty
                    ? page.intro
                    : page.bodyBlocks.first,
                textAlign: TextAlign.center,
                style: profile.typography.bodyReading.copyWith(
                  color: _detailBodyTextColor(context),
                  fontSize: 14.4,
                  height: 1.46,
                ),
              ),
            ],
            const Spacer(),
            Align(
              alignment: Alignment.centerLeft,
              child: _DetailPageFooter(
                page: page,
                isLastOverallPage: isLastOverallPage,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _DetailPortalPlaybackCard extends StatelessWidget {
  const _DetailPortalPlaybackCard({
    required this.page,
    required this.isLastOverallPage,
  });

  final _ProfileDetailPlaybackPageData page;
  final bool isLastOverallPage;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final tone = _detailToneForPlaybackPage(page);
    final highlightLines = _detailHighlightLines(page, maxLines: 1);
    return _DetailPageFill(
      child: _DetailSurfaceCard(
        tone: tone,
        radius: 30,
        padding: const EdgeInsets.fromLTRB(22, 22, 22, 22),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              turkishToUpper(page.eyebrow),
              style: profile.typography.monoEyebrow.copyWith(
                color: _detailLabelTextColor(context, tone),
                fontSize: 11.5,
                letterSpacing: 1.8,
              ),
            ),
            if (page.influenceLabels.isNotEmpty) ...[
              const SizedBox(height: 12),
              Align(
                alignment: Alignment.centerRight,
                child: _DetailInfluenceCorner(
                  sources: page.influenceLabels,
                  tone: tone,
                  maxWidth: 188,
                ),
              ),
            ],
            const Spacer(),
            Text(
              page.title,
              style: profile.typography.editorialHeadline.copyWith(
                color: profile.colors.text,
                fontSize: 27,
                height: 1.06,
              ),
            ),
            if (highlightLines.isNotEmpty) ...[
              const SizedBox(height: 14),
              JoviaSentenceBubbleStack(
                lines: highlightLines,
                compact: true,
                accents: <Color>[tone.accent, tone.accentSoft],
              ),
            ],
            if (page.intro.trim().isNotEmpty) ...[
              const SizedBox(height: 12),
              Text(
                page.intro,
                style: profile.typography.bodyReading.copyWith(
                  color: _detailBodyTextColor(context),
                  fontSize: 14.8,
                  height: 1.5,
                ),
              ),
            ],
            const SizedBox(height: 18),
            IgnorePointer(
              child: MinimalCTAButton(
                label: page.nextTitle.trim().isNotEmpty
                    ? context.l10n.profileDetailContinueFlow
                    : context.l10n.profileDetailContinueFromHere,
                emphasized: true,
                onTap: null,
              ),
            ),
            const Spacer(),
            _DetailPageFooter(page: page, isLastOverallPage: isLastOverallPage),
          ],
        ),
      ),
    );
  }
}

class _DetailTextSection extends StatelessWidget {
  const _DetailTextSection({
    required this.page,
    required this.tone,
    required this.titleSize,
    required this.isLastOverallPage,
    this.scrollable = false,
  });

  final _ProfileDetailPlaybackPageData page;
  final ProfileDetailTone tone;
  final double titleSize;
  final bool isLastOverallPage;
  final bool scrollable;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final highlightLines = _detailHighlightLines(page, maxLines: 1);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          turkishToUpper(page.eyebrow),
          style: profile.typography.monoEyebrow.copyWith(
            color: _detailLabelTextColor(context, tone),
            fontSize: 11.5,
            letterSpacing: 1.8,
          ),
        ),
        const SizedBox(height: 10),
        Text(
          page.title,
          style: profile.typography.section.copyWith(
            color: profile.colors.text,
            fontSize: titleSize - 3,
            height: 1.1,
          ),
        ),
        if (page.intro.trim().isNotEmpty) ...[
          const SizedBox(height: 10),
          Text(
            page.intro,
            style: profile.typography.bodyReading.copyWith(
              color: _detailIntroTextColor(context),
              fontSize: 14.6,
              height: 1.5,
            ),
          ),
        ],
        if (highlightLines.isNotEmpty) ...[
          const SizedBox(height: 14),
          JoviaSentenceBubbleStack(
            lines: highlightLines,
            compact: true,
            accents: <Color>[tone.accentSoft, tone.accent],
          ),
        ],
        if (page.bodyBlocks.isNotEmpty) ...[
          const SizedBox(height: 16),
          for (var index = 0; index < page.bodyBlocks.length; index++) ...[
            Text(
              page.bodyBlocks[index],
              style: profile.typography.bodyReading.copyWith(
                color: _detailBodyTextColor(context),
                fontSize: 14.3,
                height: 1.52,
              ),
            ),
            if (index != page.bodyBlocks.length - 1) const SizedBox(height: 14),
          ],
        ],
        // Voice spec v2.1 §13.4 — sessiz astrolojik künye, paragraph altı,
        // chip'lerden önce. Empty → SizedBox.shrink; non-TR locale → shrink.
        ProfileProofChip(proofRaw: page.proofRaw),
        if (page.chips.isNotEmpty) ...[
          const SizedBox(height: 16),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: page.chips
                .map((chip) => _DetailChip(label: chip, tone: tone))
                .toList(),
          ),
        ],
        if ((page.bodyBlocks.isEmpty && page.intro.trim().isEmpty) &&
            page.whyText.trim().isNotEmpty) ...[
          const SizedBox(height: 18),
          _DetailWhyBlock(text: page.whyText, tone: tone),
        ],
        if (scrollable) const SizedBox(height: 18) else const Spacer(),
        _DetailPageFooter(page: page, isLastOverallPage: isLastOverallPage),
      ],
    );
  }
}

class _DetailWhyBlock extends StatelessWidget {
  const _DetailWhyBlock({required this.text, required this.tone});

  final String text;
  final ProfileDetailTone tone;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Container(
      padding: const EdgeInsets.fromLTRB(14, 12, 14, 12),
      decoration: BoxDecoration(
        color: _detailInsetBackground(context, tone),
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: _detailStrokeColor(context, tone)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            context.l10n.profileDetailWhyHere,
            style: profile.typography.buttonLabel.copyWith(
              color: tone.accent,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 6),
          Text(
            text,
            style: profile.typography.metaSoft.copyWith(
              color: _detailBodyTextColor(context),
              height: 1.5,
            ),
          ),
        ],
      ),
    );
  }
}

class _DetailPageFooter extends StatelessWidget {
  const _DetailPageFooter({
    required this.page,
    required this.isLastOverallPage,
  });

  final _ProfileDetailPlaybackPageData page;
  final bool isLastOverallPage;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final label = switch (_detailFooterKind(page, isLastOverallPage)) {
      _DetailFooterKind.next => context.l10n.profileDetailNextLabel(
        page.nextTitle,
      ),
      _DetailFooterKind.continuation =>
        context.l10n.profileDetailContinuationFooter(
          page.pageIndexInScene + 1,
          page.pageCountInScene,
        ),
      _DetailFooterKind.end => context.l10n.profileDetailFlowEnds,
    };
    return Text(
      label,
      style: profile.typography.metaSoft.copyWith(
        color: _detailMutedTextColor(context),
        fontWeight: FontWeight.w600,
      ),
    );
  }
}

enum _DetailFooterKind { next, continuation, end }

_DetailFooterKind _detailFooterKind(
  _ProfileDetailPlaybackPageData page,
  bool isLastOverallPage,
) {
  if (page.nextTitle.trim().isNotEmpty) {
    return _DetailFooterKind.next;
  }
  if (page.pageIndexInScene < page.pageCountInScene - 1) {
    return _DetailFooterKind.continuation;
  }
  if (isLastOverallPage) {
    return _DetailFooterKind.end;
  }
  return _DetailFooterKind.continuation;
}

class _DetailChip extends StatelessWidget {
  const _DetailChip({required this.label, required this.tone});

  final String label;
  final ProfileDetailTone tone;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 7),
      decoration: BoxDecoration(
        color: _detailInsetBackground(context, tone).withValues(alpha: 0.84),
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: _detailStrokeColor(context, tone)),
      ),
      child: Text(
        label,
        style: profile.typography.buttonLabel.copyWith(
          color: _detailChipTextColor(context),
          fontWeight: FontWeight.w500,
        ),
      ),
    );
  }
}
