import 'package:flutter/material.dart';

import 'package:mobile/app/timing/turkish_text.dart';
import 'package:mobile/design/theme/profile_theme_extension.dart';
import 'package:mobile/design/widgets/jovia_editorial.dart';

const Color _kDetailFlowBg = Color(0xFF0A0A0A);
const Color _kDetailFlowText = Color(0xFFF5F2EE);
const Color _kDetailFlowAccent = Color(0xFFFF8A4C);

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
    required this.whyText,
    required this.illustrationAsset,
    required this.variant,
    this.nextTitle = '',
  });

  final String id;
  final String eyebrow;
  final String title;
  final String intro;
  final List<String> bodyBlocks;
  final List<String> chips;
  final String whyText;
  final JoviaIllustrationAsset illustrationAsset;
  final ProfileDetailSceneVariant variant;
  final String nextTitle;

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
      whyText: whyText,
      illustrationAsset: illustrationAsset,
      variant: variant ?? this.variant,
      nextTitle: nextTitle ?? this.nextTitle,
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
    return Scaffold(
      backgroundColor: tone.background,
      body: ColoredBox(
        color: tone.background,
        child: SafeArea(
          bottom: false,
          child: JoviaPageScaffold(
            padding: const EdgeInsets.fromLTRB(16, 12, 16, 28),
            child: ListView(
              padding: EdgeInsets.zero,
              children: [
                JoviaProfileTopBar(
                  label: flowTitle,
                  centerText: firstScene?.title ?? '',
                  onBackTap: () => Navigator.of(context).maybePop(),
                  reserveTrailingSpace: true,
                ),
                const SizedBox(height: 18),
                JoviaEditorialHeroBlock(
                  label: firstScene?.eyebrow.isNotEmpty == true
                      ? firstScene!.eyebrow
                      : 'Detay',
                  title: flowTitle,
                  body: flowSubtitle,
                  large: true,
                  background: Stack(
                    children: [
                      Positioned(
                        left: -26,
                        bottom: -34,
                        child: Container(
                          width: 170,
                          height: 170,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            gradient: RadialGradient(
                              colors: [
                                tone.accent.withValues(alpha: 0.22),
                                Colors.transparent,
                              ],
                            ),
                          ),
                        ),
                      ),
                      if (firstScene != null)
                        Positioned(
                          right: -8,
                          top: -8,
                          child: JoviaIllustrationAccent(
                            asset: firstScene.illustrationAsset,
                            width: 92,
                            height: 92,
                            opacity: 0.84,
                          ),
                        ),
                    ],
                  ),
                  footer: firstScene == null || firstScene.chips.isEmpty
                      ? null
                      : Wrap(
                          spacing: 8,
                          runSpacing: 8,
                          children: [
                            for (final chip in firstScene.chips.take(3))
                              _ProfileDetailThemeChip(label: chip, tone: tone),
                          ],
                        ),
                ),
                const SizedBox(height: 24),
                for (var index = 0; index < scenes.length; index++) ...[
                  _ProfileDetailSceneCard(
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

class _ProfileDetailSceneCard extends StatelessWidget {
  const _ProfileDetailSceneCard({
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
    final hasWhy = scene.whyText.trim().isNotEmpty;
    return Container(
      decoration: BoxDecoration(
        color: tone.surface,
        borderRadius: BorderRadius.circular(28),
        border: Border.all(color: tone.stroke),
        boxShadow: [
          BoxShadow(
            blurRadius: 26,
            offset: const Offset(0, 18),
            color: tone.glow,
            spreadRadius: -20,
          ),
        ],
      ),
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
                            scene.eyebrow.isNotEmpty ? scene.eyebrow : 'Kart',
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
                              color: _kDetailFlowText,
                              fontSize: 26,
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
                    style: profile.typography.bodyCompact.copyWith(
                      color: tone.mutedText,
                      height: 1.6,
                    ),
                  ),
                ],
                if (scene.bodyBlocks.isNotEmpty) ...[
                  const SizedBox(height: 16),
                  for (final block in scene.bodyBlocks) ...[
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.fromLTRB(14, 12, 14, 12),
                      decoration: BoxDecoration(
                        color: tone.surfaceStrong,
                        borderRadius: BorderRadius.circular(18),
                        border: Border.all(color: tone.stroke),
                      ),
                      child: Text(
                        block,
                        style: profile.typography.bodyCompact.copyWith(
                          color: _kDetailFlowText,
                          height: 1.6,
                        ),
                      ),
                    ),
                    const SizedBox(height: 10),
                  ],
                ],
                if (scene.chips.isNotEmpty) ...[
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: [
                      for (final chip in scene.chips.take(4))
                        _ProfileDetailThemeChip(label: chip, tone: tone),
                    ],
                  ),
                  if (hasWhy) const SizedBox(height: 16),
                ],
                if (hasWhy) ...[
                  Text(
                    'Neden burada',
                    style: profile.typography.eyebrow.copyWith(
                      color: tone.accent,
                      letterSpacing: 1.3,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    scene.whyText,
                    style: profile.typography.bodyCompact.copyWith(
                      color: tone.mutedText,
                      height: 1.56,
                    ),
                  ),
                ],
                if (index < total - 1 && scene.nextTitle.trim().isNotEmpty) ...[
                  const SizedBox(height: 16),
                  Text(
                    'Sonraki: ${scene.nextTitle}',
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
          color: _kDetailFlowText,
          fontWeight: FontWeight.w600,
        ),
      ),
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
      backgroundColor: pageTone.background,
      body: ColoredBox(
        color: pageTone.background,
        child: SafeArea(
          bottom: false,
          child: JoviaPageScaffold(
            padding: const EdgeInsets.fromLTRB(16, 12, 16, 28),
            child: ListView(
              padding: EdgeInsets.zero,
              children: [
                JoviaProfileTopBar(
                  label: title,
                  centerText: 'Tüm Kartlar',
                  onBackTap: () => Navigator.of(context).maybePop(),
                  reserveTrailingSpace: true,
                ),
                const SizedBox(height: 18),
                Container(
                  padding: const EdgeInsets.fromLTRB(18, 18, 18, 18),
                  decoration: BoxDecoration(
                    color: pageTone.surface,
                    borderRadius: BorderRadius.circular(28),
                    border: Border.all(color: pageTone.stroke),
                  ),
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
                        'Kişilik imzası kartları',
                        style: profile.typography.section.copyWith(
                          color: _kDetailFlowText,
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
      child: Container(
        padding: const EdgeInsets.fromLTRB(16, 16, 16, 16),
        decoration: BoxDecoration(
          color: item.tone.surface,
          borderRadius: BorderRadius.circular(24),
          border: Border.all(color: item.tone.stroke),
          boxShadow: [
            BoxShadow(
              color: item.tone.glow,
              blurRadius: 24,
              offset: const Offset(0, 16),
              spreadRadius: -18,
            ),
          ],
        ),
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
                      color: _kDetailFlowText,
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
    return Scaffold(
      backgroundColor: _kDetailFlowBg,
      body: ColoredBox(
        color: _kDetailFlowBg,
        child: Stack(
          children: [
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
    required this.whyText,
    required this.illustrationAsset,
    required this.nextTitle,
    required this.pageIndexInScene,
    required this.pageCountInScene,
    required this.isContinuation,
    required this.allowAutoAdvance,
    required this.requiresOverflowScroll,
  });

  final String sceneId;
  final String playbackId;
  final ProfileDetailSceneVariant variant;
  final String eyebrow;
  final String title;
  final String intro;
  final List<String> bodyBlocks;
  final List<String> chips;
  final String whyText;
  final JoviaIllustrationAsset illustrationAsset;
  final String nextTitle;
  final int pageIndexInScene;
  final int pageCountInScene;
  final bool isContinuation;
  final bool allowAutoAdvance;
  final bool requiresOverflowScroll;

  String get overlayTitle =>
      isContinuation && pageCountInScene > 1 ? '$title · Devam' : title;

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
      whyText: whyText ?? this.whyText,
      illustrationAsset: illustrationAsset,
      nextTitle: nextTitle ?? this.nextTitle,
      pageIndexInScene: pageIndexInScene ?? this.pageIndexInScene,
      pageCountInScene: pageCountInScene ?? this.pageCountInScene,
      isContinuation: isContinuation,
      allowAutoAdvance: allowAutoAdvance ?? this.allowAutoAdvance,
      requiresOverflowScroll:
          requiresOverflowScroll ?? this.requiresOverflowScroll,
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
  return const <ProfileDetailSceneData>[
    ProfileDetailSceneData(
      id: 'empty',
      eyebrow: 'Detay',
      title: 'Detay akışı hazır değil',
      intro: 'Bu bölüm için tam okuma henüz oluşturulmadı.',
      bodyBlocks: <String>[
        'Kürasyon katmanı geldiğinde burada sıralı bir okuma akışı açılacak.',
      ],
      chips: <String>[],
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
  });

  final String playbackId;
  final String title;
  final List<String> bodyBlocks;
  final String whyText;
  final String nextTitle;
  final int pageIndexInScene;
  final int pageCountInScene;
  final bool allowAutoAdvance;
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

  final blocksPerPage = _blocksPerPlaybackPage(scene.variant);
  final playbackPages = <_ProfileDetailPlaybackPageData>[];
  final leadingBlocks = blocks.take(blocksPerPage).toList(growable: false);
  final remainingBlocks = blocks.skip(blocksPerPage).toList(growable: false);

  playbackPages.add(
    _ProfileDetailPlaybackPageData(
      sceneId: scene.id,
      playbackId: '${scene.id}_0',
      variant: scene.variant,
      eyebrow: scene.eyebrow.trim().isNotEmpty ? scene.eyebrow : 'Detay',
      title: scene.title.trim().isNotEmpty ? scene.title : 'Detay akışı',
      intro: intro,
      bodyBlocks: leadingBlocks,
      chips: chips,
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
        eyebrow: scene.eyebrow.trim().isNotEmpty ? scene.eyebrow : 'Detay',
        title: scene.title.trim().isNotEmpty ? scene.title : 'Detay akışı',
        intro: '',
        bodyBlocks: chunk,
        chips: const <String>[],
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
          eyebrow: 'Neden burada',
          title: scene.title.trim().isNotEmpty ? scene.title : 'Detay akışı',
          intro: '',
          bodyBlocks: const <String>[],
          chips: const <String>[],
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
          child: const JoviaUiIcon(
            asset: JoviaUiAsset.back,
            size: 18,
            color: _kDetailFlowText,
          ),
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
      child: Padding(
        key: ValueKey<String>('detailPlaybackPage_${page.playbackId}'),
        padding: const EdgeInsets.fromLTRB(16, 92, 16, 34),
        child: _DetailVariantSurface(
          page: page,
          isLastOverallPage: isLastOverallPage,
        ),
      ),
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
    final bodyText = page.bodyBlocks.isNotEmpty
        ? page.bodyBlocks.first
        : page.intro.trim();
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF050505),
        borderRadius: BorderRadius.circular(30),
        border: Border.all(color: profile.colors.strokeSoft),
      ),
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
          const Spacer(),
          JoviaIllustrationAccent(
            asset: page.illustrationAsset,
            width: 176,
            height: 176,
            opacity: 0.96,
          ),
          const SizedBox(height: 22),
          Text(
            page.title,
            textAlign: TextAlign.center,
            style: profile.typography.editorialHeadline.copyWith(
              color: profile.colors.text,
              fontSize: 32,
              height: 1.04,
            ),
          ),
          if (bodyText.isNotEmpty) ...[
            const SizedBox(height: 14),
            Text(
              bodyText,
              textAlign: TextAlign.center,
              maxLines: page.requiresOverflowScroll ? null : 3,
              overflow: page.requiresOverflowScroll
                  ? TextOverflow.visible
                  : TextOverflow.ellipsis,
              style: profile.typography.bodyReading.copyWith(
                color: profile.colors.textLight,
                fontSize: 15.4,
                height: 1.56,
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
    final profile = context.profileTheme;
    final content = _DetailTextSection(
      page: page,
      titleSize: 34,
      isLastOverallPage: isLastOverallPage,
      scrollable: page.requiresOverflowScroll,
    );
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF050505),
        borderRadius: BorderRadius.circular(32),
        border: Border.all(color: profile.colors.strokeSoft),
      ),
      child: Stack(
        children: [
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
                ? SingleChildScrollView(
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
    final profile = context.profileTheme;
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF050505),
        borderRadius: BorderRadius.circular(30),
        border: Border.all(color: profile.colors.strokeSoft),
      ),
      padding: const EdgeInsets.fromLTRB(20, 20, 20, 20),
      child: page.requiresOverflowScroll
          ? SingleChildScrollView(
              child: _DetailStructuredBody(
                page: page,
                isLastOverallPage: isLastOverallPage,
              ),
            )
          : _DetailStructuredBody(
              page: page,
              isLastOverallPage: isLastOverallPage,
            ),
    );
  }
}

class _DetailStructuredBody extends StatelessWidget {
  const _DetailStructuredBody({
    required this.page,
    required this.isLastOverallPage,
  });

  final _ProfileDetailPlaybackPageData page;
  final bool isLastOverallPage;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
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
                color: _kDetailFlowAccent,
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
                      color: profile.colors.textLight,
                      fontSize: 11.5,
                      letterSpacing: 1.7,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    page.title,
                    style: profile.typography.section.copyWith(
                      color: profile.colors.text,
                      fontSize: 27,
                      height: 1.06,
                    ),
                  ),
                  if (page.intro.trim().isNotEmpty) ...[
                    const SizedBox(height: 10),
                    Text(
                      page.intro,
                      style: profile.typography.bodyReading.copyWith(
                        color: profile.colors.text.withValues(alpha: 0.86),
                        height: 1.52,
                      ),
                    ),
                  ],
                ],
              ),
            ),
            const SizedBox(width: 12),
            JoviaIllustrationAccent(
              asset: page.illustrationAsset,
              width: 62,
              height: 62,
              opacity: 0.88,
            ),
          ],
        ),
        if (page.bodyBlocks.isNotEmpty) ...[
          const SizedBox(height: 18),
          for (var index = 0; index < page.bodyBlocks.length; index++) ...[
            Container(
              width: double.infinity,
              padding: const EdgeInsets.fromLTRB(14, 12, 14, 12),
              decoration: BoxDecoration(
                color: const Color(0xFF0A0908),
                borderRadius: BorderRadius.circular(18),
                border: Border.all(color: profile.colors.strokeSoft),
              ),
              child: Text(
                page.bodyBlocks[index],
                style: profile.typography.bodyReading.copyWith(
                  color: profile.colors.textLight,
                  fontSize: 15,
                  height: 1.56,
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
                .map((chip) => _DetailChip(label: chip))
                .toList(),
          ),
        ],
        if (page.whyText.trim().isNotEmpty) ...[
          const SizedBox(height: 16),
          _DetailWhyBlock(text: page.whyText),
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
    final profile = context.profileTheme;
    final leftText = page.bodyBlocks.isNotEmpty
        ? page.bodyBlocks.first
        : page.intro;
    final rightText = page.bodyBlocks.length > 1
        ? page.bodyBlocks[1]
        : (page.whyText.trim().isNotEmpty ? page.whyText : '');
    final extraBlocks = page.bodyBlocks.length > 2
        ? page.bodyBlocks.skip(2).toList(growable: false)
        : const <String>[];
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF050505),
        borderRadius: BorderRadius.circular(30),
        border: Border.all(color: profile.colors.strokeSoft),
      ),
      padding: const EdgeInsets.fromLTRB(20, 20, 20, 20),
      child: page.requiresOverflowScroll
          ? SingleChildScrollView(
              child: _DetailSplitBody(
                page: page,
                leftText: leftText,
                rightText: rightText,
                extraBlocks: extraBlocks,
                isLastOverallPage: isLastOverallPage,
              ),
            )
          : _DetailSplitBody(
              page: page,
              leftText: leftText,
              rightText: rightText,
              extraBlocks: extraBlocks,
              isLastOverallPage: isLastOverallPage,
            ),
    );
  }
}

class _DetailSplitBody extends StatelessWidget {
  const _DetailSplitBody({
    required this.page,
    required this.leftText,
    required this.rightText,
    required this.extraBlocks,
    required this.isLastOverallPage,
  });

  final _ProfileDetailPlaybackPageData page;
  final String leftText;
  final String rightText;
  final List<String> extraBlocks;
  final bool isLastOverallPage;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          turkishToUpper(page.eyebrow),
          style: profile.typography.monoEyebrow.copyWith(
            color: profile.colors.warmAccent,
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
                  fontSize: 31,
                  height: 1.04,
                ),
              ),
            ),
            const SizedBox(width: 12),
            JoviaIllustrationAccent(
              asset: page.illustrationAsset,
              width: 74,
              height: 74,
              opacity: 0.92,
            ),
          ],
        ),
        const SizedBox(height: 18),
        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Expanded(
              child: _DetailSplitPane(title: 'Bir tarafı', body: leftText),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _DetailSplitPane(
                title: 'Diğer tarafı',
                body: rightText.isNotEmpty ? rightText : page.intro,
                highlighted: true,
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
                color: profile.colors.textLight,
                fontSize: 14.8,
                height: 1.56,
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
                .map((chip) => _DetailChip(label: chip))
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
    this.highlighted = false,
  });

  final String title;
  final String body;
  final bool highlighted;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Container(
      padding: const EdgeInsets.fromLTRB(14, 14, 14, 14),
      decoration: BoxDecoration(
        color: highlighted
            ? Color.alphaBlend(
                profile.colors.warmAccent.withValues(alpha: 0.04),
                const Color(0xFF080706),
              )
            : const Color(0xFF080706),
        borderRadius: BorderRadius.circular(18),
        border: Border.all(
          color: highlighted
              ? profile.colors.warmAccent.withValues(alpha: 0.24)
              : profile.colors.strokeSoft,
        ),
      ),
      child: Column(
        children: [
          Text(
            title,
            style: profile.typography.buttonLabel.copyWith(
              color: highlighted
                  ? profile.colors.warmAccent
                  : profile.colors.textLight,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            body,
            style: profile.typography.bodyReading.copyWith(
              color: profile.colors.text,
              fontSize: 15,
              height: 1.56,
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
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF050505),
        borderRadius: BorderRadius.circular(30),
        border: Border.all(color: profile.colors.strokeSoft),
      ),
      padding: const EdgeInsets.fromLTRB(22, 22, 22, 22),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          Align(
            alignment: Alignment.centerLeft,
            child: Text(
              turkishToUpper(page.eyebrow),
              style: profile.typography.monoEyebrow.copyWith(
                color: profile.colors.textLight,
                fontSize: 11.5,
                letterSpacing: 1.7,
              ),
            ),
          ),
          const Spacer(),
          JoviaIllustrationAccent(
            asset: page.illustrationAsset,
            width: 188,
            height: 188,
            opacity: 0.96,
          ),
          const SizedBox(height: 20),
          Text(
            page.title,
            textAlign: TextAlign.center,
            style: profile.typography.section.copyWith(
              color: profile.colors.text,
              fontSize: 26,
              height: 1.08,
            ),
          ),
          if (page.intro.trim().isNotEmpty || page.bodyBlocks.isNotEmpty) ...[
            const SizedBox(height: 12),
            Text(
              page.intro.trim().isNotEmpty ? page.intro : page.bodyBlocks.first,
              textAlign: TextAlign.center,
              style: profile.typography.bodyReading.copyWith(
                color: profile.colors.textLight,
                fontSize: 15,
                height: 1.5,
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
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF050505),
        borderRadius: BorderRadius.circular(30),
        border: Border.all(color: profile.colors.strokeSoft),
      ),
      padding: const EdgeInsets.fromLTRB(22, 22, 22, 22),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            turkishToUpper(page.eyebrow),
            style: profile.typography.monoEyebrow.copyWith(
              color: profile.colors.warmAccent,
              fontSize: 11.5,
              letterSpacing: 1.8,
            ),
          ),
          const Spacer(),
          Text(
            page.title,
            style: profile.typography.editorialHeadline.copyWith(
              color: profile.colors.text,
              fontSize: 30,
              height: 1.04,
            ),
          ),
          if (page.intro.trim().isNotEmpty) ...[
            const SizedBox(height: 14),
            Text(
              page.intro,
              style: profile.typography.bodyReading.copyWith(
                color: profile.colors.textLight,
                fontSize: 15.4,
                height: 1.56,
              ),
            ),
          ],
          const SizedBox(height: 18),
          IgnorePointer(
            child: MinimalCTAButton(
              label: page.nextTitle.trim().isNotEmpty
                  ? 'Akışı sürdür'
                  : 'Buradan devam et',
              emphasized: true,
              onTap: null,
            ),
          ),
          const Spacer(),
          _DetailPageFooter(page: page, isLastOverallPage: isLastOverallPage),
        ],
      ),
    );
  }
}

class _DetailTextSection extends StatelessWidget {
  const _DetailTextSection({
    required this.page,
    required this.titleSize,
    required this.isLastOverallPage,
    this.scrollable = false,
  });

  final _ProfileDetailPlaybackPageData page;
  final double titleSize;
  final bool isLastOverallPage;
  final bool scrollable;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          turkishToUpper(page.eyebrow),
          style: profile.typography.monoEyebrow.copyWith(
            color: profile.colors.warmAccent,
            fontSize: 11.5,
            letterSpacing: 1.8,
          ),
        ),
        const SizedBox(height: 10),
        Text(
          page.title,
          style: profile.typography.section.copyWith(
            color: profile.colors.text,
            fontSize: titleSize,
            height: 1.08,
          ),
        ),
        if (page.intro.trim().isNotEmpty) ...[
          const SizedBox(height: 10),
          Text(
            page.intro,
            style: profile.typography.bodyReading.copyWith(
              color: profile.colors.text.withValues(alpha: 0.86),
              height: 1.56,
            ),
          ),
        ],
        if (page.bodyBlocks.isNotEmpty) ...[
          const SizedBox(height: 16),
          for (var index = 0; index < page.bodyBlocks.length; index++) ...[
            Text(
              page.bodyBlocks[index],
              style: profile.typography.bodyReading.copyWith(
                color: profile.colors.textLight,
                fontSize: 15,
                height: 1.58,
              ),
            ),
            if (index != page.bodyBlocks.length - 1) const SizedBox(height: 14),
          ],
        ],
        if (page.chips.isNotEmpty) ...[
          const SizedBox(height: 16),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: page.chips
                .map((chip) => _DetailChip(label: chip))
                .toList(),
          ),
        ],
        if ((page.bodyBlocks.isEmpty && page.intro.trim().isEmpty) &&
            page.whyText.trim().isNotEmpty) ...[
          const SizedBox(height: 18),
          _DetailWhyBlock(text: page.whyText),
        ],
        if (scrollable) const SizedBox(height: 18) else const Spacer(),
        _DetailPageFooter(page: page, isLastOverallPage: isLastOverallPage),
      ],
    );
  }
}

class _DetailWhyBlock extends StatelessWidget {
  const _DetailWhyBlock({required this.text});

  final String text;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Container(
      padding: const EdgeInsets.fromLTRB(14, 12, 14, 12),
      decoration: BoxDecoration(
        color: const Color(0xFF0A0908),
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: profile.colors.strokeSoft),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Neden burada',
            style: profile.typography.buttonLabel.copyWith(
              color: profile.colors.warmAccent,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 6),
          Text(
            text,
            style: profile.typography.metaSoft.copyWith(
              color: profile.colors.textLight,
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
      _DetailFooterKind.next => 'Sıradaki: ${page.nextTitle}',
      _DetailFooterKind.continuation =>
        'Devam ${page.pageIndexInScene + 1}/${page.pageCountInScene}',
      _DetailFooterKind.end => 'Akış burada bitiyor',
    };
    return Text(
      label,
      style: profile.typography.metaSoft.copyWith(
        color: profile.colors.text.withValues(alpha: 0.58),
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
  const _DetailChip({required this.label});

  final String label;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 7),
      decoration: BoxDecoration(
        color: const Color(0xFF0E0B09),
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: profile.colors.strokeSoft),
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
