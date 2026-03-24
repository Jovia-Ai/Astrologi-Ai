import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:mobile/app/api/api_client.dart';
import 'package:mobile/app/profile/profile_models.dart';
import 'package:mobile/app/profile/profile_providers.dart';
import 'package:mobile/app/tabs/bond_page.dart';
import 'package:mobile/app/tabs/home_page.dart';
import 'package:mobile/design/theme/profile_theme_extension.dart';
import 'package:mobile/design/widgets/jovia_assets.dart';
import 'package:mobile/design/widgets/jovia_editorial.dart';

class StoryStudioPage extends ConsumerStatefulWidget {
  const StoryStudioPage({super.key});

  @override
  ConsumerState<StoryStudioPage> createState() => _StoryStudioPageState();
}

enum _StudioFamily { identity, moment }

class _StoryStudioPageState extends ConsumerState<StoryStudioPage> {
  final PageController _pageController = PageController(viewportFraction: 0.8);

  bool _isLoading = false;
  String? _error;
  String? _lastKey;
  PersonalityImprintProfile? _imprintProfile;
  int _activeIndex = 0;
  _StudioFamily _family = _StudioFamily.identity;

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = context.profileTheme;
    final spacing = theme.spacing;
    final palette = _StoryStudioReferencePalette.of(context);
    final profileAsync = ref.watch(userProfileProvider);
    final profile = profileAsync.valueOrNull;

    if (profile != null) {
      _maybeLoadImprint(profile);
    }

    final cards = _storyStudioCards(_imprintProfile);
    final isIdentityFamily = _family == _StudioFamily.identity;
    return Scaffold(
      backgroundColor: palette.canvas,
      body: DecoratedBox(
        decoration: BoxDecoration(
          color: palette.canvas,
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [palette.canvas, palette.canvas, palette.lowerGlow],
            stops: const [0, 0.34, 1],
          ),
        ),
        child: Stack(
          children: [
            Positioned(
              top: -32,
              right: -24,
              child: IgnorePointer(
                child: SizedBox(
                  width: 220,
                  height: 220,
                  child: JoviaColorWash(
                    asset: JoviaColorAsset.wash11,
                    opacity: Theme.of(context).brightness == Brightness.dark
                        ? 0.14
                        : 0.18,
                    fit: BoxFit.cover,
                  ),
                ),
              ),
            ),
            JoviaPageScaffold(
              child: profile == null
                  ? _StoryStudioStateBlock(
                      title: 'Story Studio',
                      body:
                          'Profil bilgileri yuklenirken kartlar hazirlaniyor.',
                      child: const Padding(
                        padding: EdgeInsets.only(top: 18),
                        child: Center(child: CircularProgressIndicator()),
                      ),
                    )
                  : !_hasBirthData(profile)
                  ? const _StoryStudioStateBlock(
                      title: 'Story Studio',
                      body:
                          'Bu alanda kisilik imzasi kartlari gormek icin dogum tarihi, saat ve yer bilgisi gerekiyor.',
                    )
                  : SingleChildScrollView(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const JoviaProfileTopBar(
                            label: 'Studio',
                            centerText: 'story studio',
                            reserveTrailingSpace: true,
                          ),
                          SizedBox(height: spacing.s20),
                          const _StoryStudioReferenceHero(title: '', body: ''),
                          SizedBox(height: spacing.s20),
                          _StoryStudioSectionLead(
                            title: isIdentityFamily
                                ? 'Kişilik imzalarını aç'
                                : 'Akışlardan bir an seç',
                            body: isIdentityFamily
                                ? 'Identity Studio dominant ve destek katmanları daha collectible kartlara çevirir.'
                                : 'Moment Studio Home ve Bond akışlarındaki anlık yüzeylere köprü olur.',
                          ),
                          SizedBox(height: spacing.sectionToContent),
                          JoviaSegmentedControl<_StudioFamily>(
                            value: _family,
                            options: _StudioFamily.values,
                            labelBuilder: (value) => switch (value) {
                              _StudioFamily.identity => 'Identity Studio',
                              _StudioFamily.moment => 'Moment Studio',
                            },
                            onChanged: (value) {
                              if (value == _family) {
                                return;
                              }
                              setState(() => _family = value);
                            },
                          ),
                          SizedBox(height: spacing.majorSectionGap),
                          if (!isIdentityFamily)
                            _StoryStudioMomentBlock(
                              onOpenHome: () {
                                Navigator.of(context).push(
                                  MaterialPageRoute<void>(
                                    builder: (_) => const HomePage(),
                                  ),
                                );
                              },
                              onOpenBond: () {
                                Navigator.of(context).push(
                                  MaterialPageRoute<void>(
                                    builder: (_) => const BondPage(),
                                  ),
                                );
                              },
                            )
                          else if (_error != null && cards.isEmpty)
                            _StoryStudioStateBlock(
                              title: 'Kartlar yuklenemedi',
                              body: _error!,
                              child: Padding(
                                padding: const EdgeInsets.only(top: 18),
                                child: JoviaPressable(
                                  onTap: () => _loadImprint(profile),
                                  borderRadius: BorderRadius.circular(999),
                                  child: Container(
                                    padding: const EdgeInsets.symmetric(
                                      horizontal: 18,
                                      vertical: 12,
                                    ),
                                    decoration: BoxDecoration(
                                      color: const Color(0xFF6D5CF6),
                                      borderRadius: BorderRadius.circular(999),
                                    ),
                                    child: const Text(
                                      'Tekrar dene',
                                      style: TextStyle(
                                        color: Colors.white,
                                        fontWeight: FontWeight.w700,
                                      ),
                                    ),
                                  ),
                                ),
                              ),
                            )
                          else if (_isLoading && cards.isEmpty)
                            const _StoryStudioStateBlock(
                              title: 'Kartlar hazirlaniyor',
                              body:
                                  'Kisilik imzandaki dominant ve destek katmanlar toplanıyor.',
                              child: Padding(
                                padding: EdgeInsets.only(top: 18),
                                child: Center(
                                  child: CircularProgressIndicator(),
                                ),
                              ),
                            )
                          else if (cards.isEmpty)
                            const _StoryStudioStateBlock(
                              title: 'Kart bulunmadi',
                              body:
                                  'Kisilik imzasi kartlari su an olusmamis gorunuyor.',
                            )
                          else ...[
                            SizedBox(height: spacing.s8),
                            SizedBox(
                              height: 528,
                              child: PageView.builder(
                                controller: _pageController,
                                itemCount: cards.length,
                                clipBehavior: Clip.none,
                                onPageChanged: (value) {
                                  setState(() => _activeIndex = value);
                                },
                                itemBuilder: (context, index) {
                                  return AnimatedBuilder(
                                    animation: _pageController,
                                    builder: (context, child) {
                                      final page = _pageController.hasClients
                                          ? (_pageController.page ??
                                                _activeIndex.toDouble())
                                          : _activeIndex.toDouble();
                                      final delta = page - index;
                                      return _StoryStudioSceneCard(
                                        data: cards[index],
                                        delta: delta,
                                        isActive: index == _activeIndex,
                                        indexLabel:
                                            '${index + 1}/${cards.length}',
                                        onTap: () {
                                          setState(() {
                                            _activeIndex = index;
                                          });
                                          _openCard(cards[index]);
                                        },
                                      );
                                    },
                                  );
                                },
                              ),
                            ),
                            const SizedBox(height: 18),
                            Center(
                              child: Wrap(
                                spacing: 8,
                                children: [
                                  for (
                                    var index = 0;
                                    index < cards.length;
                                    index++
                                  )
                                    AnimatedContainer(
                                      duration: theme.motion.normal,
                                      curve: theme.motion.curve,
                                      width: index == _activeIndex ? 20 : 7,
                                      height: 7,
                                      decoration: BoxDecoration(
                                        color: index == _activeIndex
                                            ? palette.edge
                                            : palette.softFill,
                                        borderRadius: BorderRadius.circular(
                                          999,
                                        ),
                                      ),
                                    ),
                                ],
                              ),
                            ),
                          ],
                          const SizedBox(height: 24),
                        ],
                      ),
                    ),
            ),
          ],
        ),
      ),
    );
  }

  void _maybeLoadImprint(Map<String, dynamic> profile) {
    final key = _profileKey(profile);
    if (key.isEmpty || key == _lastKey) {
      return;
    }
    _lastKey = key;
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) {
        return;
      }
      _loadImprint(profile);
    });
  }

  Future<void> _loadImprint(Map<String, dynamic> profile) async {
    final payload = <String, dynamic>{
      'birth_date': (profile['birth_date'] ?? '').toString().trim(),
      'birth_time': _normalizeBirthTime(
        (profile['birth_time'] ?? '').toString(),
      ),
      'birth_place': _birthPlace(profile),
      'locale': 'tr',
    };

    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final client = ApiClient();
      final response = await client.post('/interpret', data: payload);
      final parsed = _extractPersonalityImprint(_asMap(response.data));
      if (!mounted) {
        return;
      }
      setState(() {
        _imprintProfile = parsed;
        _activeIndex = 0;
        _isLoading = false;
      });
    } catch (error) {
      if (!mounted) {
        return;
      }
      setState(() {
        _isLoading = false;
        _error = 'Kisilik imzasi su an alinmadi: $error';
      });
    }
  }

  Future<void> _openCard(_StoryStudioCardData card) {
    return Navigator.of(context).push(
      PageRouteBuilder<void>(
        transitionDuration: const Duration(milliseconds: 260),
        reverseTransitionDuration: const Duration(milliseconds: 220),
        pageBuilder: (context, animation, secondaryAnimation) =>
            _StoryStudioFullViewPage(card: card, isLoading: _isLoading),
        transitionsBuilder: (context, animation, secondaryAnimation, child) {
          final curved = CurvedAnimation(
            parent: animation,
            curve: Curves.easeOutCubic,
            reverseCurve: Curves.easeOutCubic,
          );
          return SlideTransition(
            position: Tween<Offset>(
              begin: const Offset(0, 0.04),
              end: Offset.zero,
            ).animate(curved),
            child: ScaleTransition(
              scale: Tween<double>(begin: 0.965, end: 1).animate(curved),
              child: child,
            ),
          );
        },
      ),
    );
  }
}

class _StoryStudioStateBlock extends StatelessWidget {
  const _StoryStudioStateBlock({required this.title, this.body, this.child});

  final String title;
  final String? body;
  final Widget? child;

  @override
  Widget build(BuildContext context) {
    final theme = context.profileTheme;
    final palette = _StoryStudioReferencePalette.of(context);
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.fromLTRB(22, 22, 22, 22),
      decoration: BoxDecoration(
        color: palette.panelFill,
        borderRadius: BorderRadius.circular(28),
        border: Border.all(color: palette.edge.withValues(alpha: 0.78)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: theme.typography.sectionTitle.copyWith(color: palette.text),
          ),
          if ((body ?? '').trim().isNotEmpty) ...[
            const SizedBox(height: 12),
            Text(
              body!.trim(),
              style: theme.typography.body.copyWith(color: palette.mutedText),
            ),
          ],
          ...?child == null ? null : <Widget>[child!],
          const SizedBox(height: 18),
          JoviaBrandMark(
            width: 42,
            opacity: 0.72,
            alignment: Alignment.centerRight,
          ),
        ],
      ),
    );
  }
}

class _StoryStudioReferencePalette {
  const _StoryStudioReferencePalette({
    required this.canvas,
    required this.lowerGlow,
    required this.panelFill,
    required this.softFill,
    required this.edge,
    required this.rule,
    required this.text,
    required this.mutedText,
    required this.softText,
  });

  final Color canvas;
  final Color lowerGlow;
  final Color panelFill;
  final Color softFill;
  final Color edge;
  final Color rule;
  final Color text;
  final Color mutedText;
  final Color softText;

  static _StoryStudioReferencePalette of(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return isDark
        ? const _StoryStudioReferencePalette(
            canvas: Color(0xFF080607),
            lowerGlow: Color(0xFF131010),
            panelFill: Color(0xFF100B0C),
            softFill: Color(0xFF1A1414),
            edge: Color(0xFFB97B46),
            rule: Color(0xFF4A3A33),
            text: Color(0xFFF6F1EB),
            mutedText: Color(0xFFC9BEB3),
            softText: Color(0xFFB6A99D),
          )
        : const _StoryStudioReferencePalette(
            canvas: Color(0xFFF5F0E8),
            lowerGlow: Color(0xFFEEE2D6),
            panelFill: Color(0xFFFBF6EF),
            softFill: Color(0xFFF2E7D9),
            edge: Color(0xFFD6945A),
            rule: Color(0xFF7E6959),
            text: Color(0xFF181211),
            mutedText: Color(0xFF6F6156),
            softText: Color(0xFF998474),
          );
  }
}

class _StoryStudioReferenceHero extends StatelessWidget {
  const _StoryStudioReferenceHero({required this.title, required this.body});

  final String title;
  final String body;

  @override
  Widget build(BuildContext context) {
    final theme = context.profileTheme;
    final palette = _StoryStudioReferencePalette.of(context);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (title.trim().isNotEmpty || body.trim().isNotEmpty) ...[
          Text(
            'STUDIO',
            style: theme.typography.eyebrow.copyWith(color: palette.softText),
          ),
          if (title.trim().isNotEmpty) ...[
            const SizedBox(height: 10),
            ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 300),
              child: Text(
                title,
                style: theme.typography.pageTitle.copyWith(
                  color: palette.text,
                  fontSize: 24,
                  height: 1.06,
                ),
              ),
            ),
          ],
          if (body.trim().isNotEmpty) ...[
            const SizedBox(height: 10),
            ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 360),
              child: Text(
                body,
                style: theme.typography.bodyCompact.copyWith(
                  color: palette.mutedText,
                  fontSize: 15,
                  height: 1.54,
                ),
              ),
            ),
          ],
        ],
      ],
    );
  }
}

class _StoryStudioSectionLead extends StatelessWidget {
  const _StoryStudioSectionLead({required this.title, this.body});

  final String title;
  final String? body;

  @override
  Widget build(BuildContext context) {
    final theme = context.profileTheme;
    final palette = _StoryStudioReferencePalette.of(context);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: theme.typography.sectionTitle.copyWith(
            color: palette.text,
            fontSize: 21,
            height: 1.14,
          ),
        ),
        if ((body ?? '').trim().isNotEmpty) ...[
          const SizedBox(height: 10),
          Text(
            body!,
            style: theme.typography.bodyCompact.copyWith(
              color: palette.mutedText,
              fontSize: 15,
            ),
          ),
        ],
      ],
    );
  }
}

class _StoryStudioMomentBlock extends StatelessWidget {
  const _StoryStudioMomentBlock({
    required this.onOpenHome,
    required this.onOpenBond,
  });

  final VoidCallback onOpenHome;
  final VoidCallback onOpenBond;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const _StoryStudioStateBlock(
          title: 'Moment Studio',
          body:
              'Anlik bir donemi ya da iliski vurgusunu secip paylasilabilir bir yone cevirmek icin kaynak akislardan birine don.',
        ),
        const SizedBox(height: 18),
        JoviaActionRail(
          title: 'Kaynak akislara don',
          leading: const JoviaUiIcon(asset: JoviaUiAsset.homePortal, size: 16),
          primaryAction: MinimalCTAButton(
            label: 'Home',
            emphasized: true,
            onTap: onOpenHome,
          ),
          secondaryActions: [
            MinimalCTAButton(label: 'Bond', onTap: onOpenBond),
          ],
        ),
      ],
    );
  }
}

class _StoryStudioSceneCard extends StatelessWidget {
  const _StoryStudioSceneCard({
    required this.data,
    required this.delta,
    required this.isActive,
    required this.indexLabel,
    this.onTap,
  });

  final _StoryStudioCardData data;
  final double delta;
  final bool isActive;
  final String indexLabel;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final theme = context.profileTheme;
    final palette = _storyStudioPaletteFor(data);
    final distance = delta.abs();
    final scale = (1 - (distance * 0.12)).clamp(0.86, 1.0).toDouble();
    final translateX = delta * -20;
    final translateY = distance * 14;
    final opacity = (1 - (distance * 0.34)).clamp(0.56, 1.0).toDouble();
    final relatedPlanet = data.relatedPlanets.isNotEmpty
        ? data.relatedPlanets.first
        : data.entry.labelTr;
    final planetAsset =
        JoviaPlanetAssetResolver.fromNarrativeText(relatedPlanet) ??
        JoviaPlanetAsset.rising;
    final coverText = _firstSentence(
      data.entry.backgroundHint.isNotEmpty
          ? data.entry.backgroundHint
          : data.entry.aura,
    );

    final cardBody = Transform.translate(
      offset: Offset(translateX, translateY),
      child: Transform.scale(
        scale: scale,
        child: Opacity(
          opacity: opacity,
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 6),
            child: Container(
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(36),
                boxShadow: [
                  BoxShadow(
                    color: palette.shadow.withValues(
                      alpha: isActive ? 0.22 : 0.1,
                    ),
                    blurRadius: isActive ? 28 : 18,
                    offset: const Offset(0, 18),
                  ),
                ],
              ),
              child: ClipRRect(
                borderRadius: BorderRadius.circular(36),
                child: Stack(
                  children: [
                    Positioned.fill(
                      child: DecoratedBox(
                        decoration: BoxDecoration(
                          gradient: LinearGradient(
                            begin: Alignment.topLeft,
                            end: Alignment.bottomRight,
                            colors: palette.gradient,
                          ),
                        ),
                      ),
                    ),
                    Positioned.fill(
                      child: Opacity(
                        opacity: 0.88,
                        child: JoviaColorWash(
                          asset: palette.wash,
                          opacity: 0.9,
                          fit: BoxFit.cover,
                        ),
                      ),
                    ),
                    Positioned(
                      top: -18,
                      right: -6,
                      child: JoviaIllustrationAccent(
                        asset: palette.illustration,
                        width: 130,
                        height: 130,
                        opacity: 0.22,
                      ),
                    ),
                    Positioned(
                      top: 74,
                      left: 28,
                      right: 28,
                      child: Center(
                        child: Container(
                          width: 180,
                          height: 180,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            color: Colors.white.withValues(alpha: 0.12),
                          ),
                          child: Center(
                            child: JoviaPlanetGlyph(
                              asset: planetAsset,
                              size: 118,
                              color: Colors.white.withValues(alpha: 0.86),
                            ),
                          ),
                        ),
                      ),
                    ),
                    Positioned.fill(
                      child: DecoratedBox(
                        decoration: BoxDecoration(
                          gradient: LinearGradient(
                            begin: Alignment.topCenter,
                            end: Alignment.bottomCenter,
                            colors: [
                              Colors.transparent,
                              Colors.black.withValues(alpha: 0.08),
                              Colors.black.withValues(alpha: 0.42),
                            ],
                            stops: const [0.35, 0.62, 1],
                          ),
                        ),
                      ),
                    ),
                    Positioned(
                      top: 22,
                      left: 20,
                      child: Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 12,
                          vertical: 7,
                        ),
                        decoration: BoxDecoration(
                          color: Colors.white.withValues(alpha: 0.18),
                          borderRadius: BorderRadius.circular(999),
                        ),
                        child: Text(
                          _storyStudioKindLabel(data.entry.kind),
                          style: theme.typography.meta.copyWith(
                            color: Colors.white.withValues(alpha: 0.92),
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ),
                    ),
                    Positioned(
                      top: 22,
                      right: 20,
                      child: Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 10,
                          vertical: 7,
                        ),
                        decoration: BoxDecoration(
                          color: Colors.white.withValues(alpha: 0.14),
                          borderRadius: BorderRadius.circular(999),
                        ),
                        child: Text(
                          indexLabel,
                          style: theme.typography.meta.copyWith(
                            color: Colors.white.withValues(alpha: 0.82),
                          ),
                        ),
                      ),
                    ),
                    Positioned(
                      left: 22,
                      right: 22,
                      bottom: 24,
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          if (data.entry.tags.isNotEmpty)
                            Wrap(
                              spacing: 8,
                              runSpacing: 8,
                              children: [
                                for (final tag in data.entry.tags.take(3))
                                  Container(
                                    padding: const EdgeInsets.symmetric(
                                      horizontal: 10,
                                      vertical: 6,
                                    ),
                                    decoration: BoxDecoration(
                                      color: Colors.white.withValues(
                                        alpha: 0.12,
                                      ),
                                      borderRadius: BorderRadius.circular(999),
                                    ),
                                    child: Text(
                                      tag,
                                      style: theme.typography.meta.copyWith(
                                        color: Colors.white.withValues(
                                          alpha: 0.86,
                                        ),
                                      ),
                                    ),
                                  ),
                              ],
                            ),
                          const SizedBox(height: 14),
                          Text(
                            data.entry.labelTr,
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                            style: theme.typography.pageTitle.copyWith(
                              color: Colors.white,
                              fontSize: 28,
                              height: 1.08,
                            ),
                          ),
                          const SizedBox(height: 10),
                          Text(
                            coverText,
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                            style: theme.typography.bodyCompact.copyWith(
                              color: Colors.white.withValues(alpha: 0.86),
                              height: 1.45,
                            ),
                          ),
                          const SizedBox(height: 12),
                          JoviaInteractiveSocialBar(
                            seedKey: data.entry.key,
                            title: data.entry.labelTr,
                            initialLikeCount: _storyLikeCount(data),
                            initialCommentCount: _storyCommentCount(data),
                            color: Colors.white.withValues(alpha: 0.88),
                          ),
                        ],
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
    return JoviaPressable(
      onTap: onTap,
      borderRadius: BorderRadius.circular(36),
      child: cardBody,
    );
  }
}

class _StoryStudioFullViewPage extends StatelessWidget {
  const _StoryStudioFullViewPage({required this.card, required this.isLoading});

  final _StoryStudioCardData card;
  final bool isLoading;

  @override
  Widget build(BuildContext context) {
    final theme = context.profileTheme;
    final palette = _storyStudioPaletteFor(card);
    final relatedPlanet = card.relatedPlanets.isNotEmpty
        ? card.relatedPlanets.first
        : card.entry.labelTr;
    final planetAsset =
        JoviaPlanetAssetResolver.fromNarrativeText(relatedPlanet) ??
        JoviaPlanetAsset.rising;
    final shadow = _firstSentence(card.entry.shadow);
    final aura = _firstSentence(card.entry.aura);
    final trait = _firstSentence(card.entry.trait);
    final drive = _firstSentence(card.entry.drive);
    final supportLabels = card.supportLabels.take(3).toList(growable: false);

    return Scaffold(
      backgroundColor: Colors.transparent,
      body: DecoratedBox(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: palette.gradient,
          ),
        ),
        child: Stack(
          children: [
            Positioned.fill(
              child: JoviaColorWash(
                asset: palette.wash,
                opacity: 0.92,
                fit: BoxFit.cover,
              ),
            ),
            Positioned(
              top: -24,
              right: -16,
              child: JoviaIllustrationAccent(
                asset: palette.illustration,
                width: 170,
                height: 170,
                opacity: 0.2,
              ),
            ),
            Positioned.fill(
              child: DecoratedBox(
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topCenter,
                    end: Alignment.bottomCenter,
                    colors: [
                      Colors.white.withValues(alpha: 0.06),
                      Colors.black.withValues(alpha: 0.08),
                      Colors.black.withValues(alpha: 0.28),
                    ],
                    stops: const [0, 0.48, 1],
                  ),
                ),
              ),
            ),
            SafeArea(
              child: Column(
                children: [
                  Padding(
                    padding: const EdgeInsets.fromLTRB(18, 10, 18, 0),
                    child: Row(
                      children: [
                        JoviaPressable(
                          onTap: () => Navigator.of(context).maybePop(),
                          borderRadius: BorderRadius.circular(999),
                          child: Container(
                            width: 42,
                            height: 42,
                            decoration: BoxDecoration(
                              color: Colors.white.withValues(alpha: 0.16),
                              borderRadius: BorderRadius.circular(999),
                            ),
                            child: const Center(
                              child: JoviaUiIcon(
                                asset: JoviaUiAsset.back,
                                size: 16,
                                color: Colors.white,
                              ),
                            ),
                          ),
                        ),
                        const Spacer(),
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 12,
                            vertical: 8,
                          ),
                          decoration: BoxDecoration(
                            color: Colors.white.withValues(alpha: 0.16),
                            borderRadius: BorderRadius.circular(999),
                          ),
                          child: Text(
                            _storyStudioKindLabel(card.entry.kind),
                            style: theme.typography.meta.copyWith(
                              color: Colors.white.withValues(alpha: 0.92),
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                  Expanded(
                    child: SingleChildScrollView(
                      padding: const EdgeInsets.fromLTRB(24, 12, 24, 28),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const SizedBox(height: 8),
                          Center(
                            child: Container(
                              width: 128,
                              height: 128,
                              decoration: BoxDecoration(
                                shape: BoxShape.circle,
                                color: Colors.white.withValues(alpha: 0.14),
                                boxShadow: [
                                  BoxShadow(
                                    color: Colors.white.withValues(alpha: 0.08),
                                    blurRadius: 42,
                                    spreadRadius: 8,
                                  ),
                                ],
                              ),
                              child: Center(
                                child: JoviaPlanetGlyph(
                                  asset: planetAsset,
                                  size: 84,
                                  color: Colors.white.withValues(alpha: 0.88),
                                ),
                              ),
                            ),
                          ),
                          const SizedBox(height: 28),
                          if (card.entry.tags.isNotEmpty)
                            Wrap(
                              spacing: 8,
                              runSpacing: 8,
                              children: [
                                for (final tag in card.entry.tags.take(3))
                                  Container(
                                    padding: const EdgeInsets.symmetric(
                                      horizontal: 11,
                                      vertical: 7,
                                    ),
                                    decoration: BoxDecoration(
                                      color: Colors.white.withValues(
                                        alpha: 0.14,
                                      ),
                                      borderRadius: BorderRadius.circular(999),
                                    ),
                                    child: Text(
                                      tag,
                                      style: theme.typography.meta.copyWith(
                                        color: Colors.white.withValues(
                                          alpha: 0.88,
                                        ),
                                      ),
                                    ),
                                  ),
                              ],
                            ),
                          const SizedBox(height: 16),
                          Text(
                            card.entry.labelTr,
                            style: theme.typography.pageTitle.copyWith(
                              color: Colors.white,
                              fontSize: 34,
                              height: 1.02,
                            ),
                          ),
                          if (aura.isNotEmpty) ...[
                            const SizedBox(height: 12),
                            Text(
                              aura,
                              style: theme.typography.body.copyWith(
                                color: Colors.white.withValues(alpha: 0.9),
                                height: 1.5,
                              ),
                            ),
                          ],
                          const SizedBox(height: 14),
                          JoviaInteractiveSocialBar(
                            seedKey: card.entry.key,
                            title: card.entry.labelTr,
                            initialLikeCount: _storyLikeCount(card),
                            initialCommentCount: _storyCommentCount(card),
                            color: Colors.white.withValues(alpha: 0.88),
                          ),
                          const SizedBox(height: 28),
                          if (trait.isNotEmpty) ...[
                            _StoryStudioInlineSection(
                              label: 'OZELLIK',
                              body: trait,
                            ),
                            const SizedBox(height: 18),
                          ],
                          if (drive.isNotEmpty) ...[
                            _StoryStudioInlineSection(
                              label: 'IC MOTOR',
                              body: drive,
                            ),
                            const SizedBox(height: 18),
                          ],
                          if (supportLabels.isNotEmpty)
                            Wrap(
                              spacing: 8,
                              runSpacing: 8,
                              children: [
                                for (final label in supportLabels)
                                  Container(
                                    padding: const EdgeInsets.symmetric(
                                      horizontal: 12,
                                      vertical: 8,
                                    ),
                                    decoration: BoxDecoration(
                                      color: Colors.white.withValues(
                                        alpha: 0.92,
                                      ),
                                      borderRadius: BorderRadius.circular(999),
                                    ),
                                    child: Text(
                                      label,
                                      style: theme.typography.meta.copyWith(
                                        color: const Color(0xFF5E576B),
                                      ),
                                    ),
                                  ),
                              ],
                            ),
                          if (shadow.isNotEmpty) ...[
                            const SizedBox(height: 20),
                            Container(
                              width: double.infinity,
                              padding: const EdgeInsets.fromLTRB(
                                16,
                                14,
                                16,
                                14,
                              ),
                              decoration: BoxDecoration(
                                color: Colors.black.withValues(alpha: 0.22),
                                borderRadius: BorderRadius.circular(22),
                                border: Border.all(
                                  color: Colors.white.withValues(alpha: 0.14),
                                ),
                              ),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    'DOZ ASINCA',
                                    style: theme.typography.meta.copyWith(
                                      color: Colors.white.withValues(
                                        alpha: 0.8,
                                      ),
                                      letterSpacing: 1.25,
                                      fontWeight: FontWeight.w700,
                                    ),
                                  ),
                                  const SizedBox(height: 8),
                                  Text(
                                    shadow,
                                    style: theme.typography.bodyCompact
                                        .copyWith(
                                          color: Colors.white.withValues(
                                            alpha: 0.9,
                                          ),
                                          height: 1.5,
                                        ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                          if (isLoading) ...[
                            const SizedBox(height: 16),
                            Text(
                              'Kartlar yenileniyor...',
                              style: theme.typography.meta.copyWith(
                                color: Colors.white.withValues(alpha: 0.72),
                              ),
                            ),
                          ],
                        ],
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

class _StoryStudioInlineSection extends StatelessWidget {
  const _StoryStudioInlineSection({required this.label, required this.body});

  final String label;
  final String body;

  @override
  Widget build(BuildContext context) {
    final theme = context.profileTheme;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: theme.typography.meta.copyWith(
            color: Colors.white.withValues(alpha: 0.76),
            letterSpacing: 1.4,
            fontWeight: FontWeight.w700,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          body,
          style: theme.typography.bodyCompact.copyWith(
            color: Colors.white.withValues(alpha: 0.92),
            height: 1.55,
          ),
        ),
      ],
    );
  }
}

class _StoryStudioCardData {
  const _StoryStudioCardData({
    required this.entry,
    required this.supportEntries,
    required this.relatedPlanets,
  });

  final PersonalityImprintEntry entry;
  final List<PersonalityImprintEntry> supportEntries;
  final List<String> relatedPlanets;

  List<String> get supportLabels => supportEntries
      .map((item) => item.labelTr.trim())
      .where((item) => item.isNotEmpty)
      .toList(growable: false);
}

class _StoryStudioPalette {
  const _StoryStudioPalette({
    required this.gradient,
    required this.wash,
    required this.illustration,
    required this.shadow,
  });

  final List<Color> gradient;
  final JoviaColorAsset wash;
  final JoviaIllustrationAsset illustration;
  final Color shadow;
}

const List<_StoryStudioPalette> _storyStudioPalettes = [
  _StoryStudioPalette(
    gradient: [Color(0xFF53445E), Color(0xFF866270), Color(0xFFCC9772)],
    wash: JoviaColorAsset.wash03,
    illustration: JoviaIllustrationAsset.dots,
    shadow: Color(0xFF463550),
  ),
  _StoryStudioPalette(
    gradient: [Color(0xFF5A5E72), Color(0xFF8D82C8), Color(0xFFC1B3F7)],
    wash: JoviaColorAsset.wash11,
    illustration: JoviaIllustrationAsset.layers,
    shadow: Color(0xFF464B67),
  ),
  _StoryStudioPalette(
    gradient: [Color(0xFF546253), Color(0xFF7A9067), Color(0xFFCDB988)],
    wash: JoviaColorAsset.wash05,
    illustration: JoviaIllustrationAsset.blocks,
    shadow: Color(0xFF485643),
  ),
  _StoryStudioPalette(
    gradient: [Color(0xFF3F5568), Color(0xFF6D7E9A), Color(0xFFB7C7DB)],
    wash: JoviaColorAsset.wash09,
    illustration: JoviaIllustrationAsset.planet,
    shadow: Color(0xFF384B5C),
  ),
];

_StoryStudioPalette _storyStudioPaletteFor(_StoryStudioCardData data) {
  final seed =
      data.entry.key.hashCode ^
      data.entry.labelTr.hashCode ^
      data.relatedPlanets.join('|').hashCode;
  return _storyStudioPalettes[seed.abs() % _storyStudioPalettes.length];
}

List<_StoryStudioCardData> _storyStudioCards(
  PersonalityImprintProfile? profile,
) {
  if (profile == null) {
    return const <_StoryStudioCardData>[];
  }
  return [
    ..._storyStudioCardsFor(
      entries: profile.entries,
      bundles: profile.bundles,
      supportEntries: profile.supportEntries,
    ),
    ..._storyStudioCardsFor(
      entries: profile.extraEntries,
      bundles: profile.extraBundles,
      supportEntries: profile.supportEntries,
    ),
  ];
}

List<_StoryStudioCardData> _storyStudioCardsFor({
  required List<PersonalityImprintEntry> entries,
  required List<PersonalityImprintBundle> bundles,
  required List<PersonalityImprintEntry> supportEntries,
}) {
  final dominantByKey = <String, PersonalityImprintEntry>{
    for (final entry in entries) entry.key: entry,
  };
  final supportByKey = <String, PersonalityImprintEntry>{
    for (final entry in supportEntries) entry.key: entry,
  };
  final seen = <String>{};
  final cards = <_StoryStudioCardData>[];

  for (final bundle in bundles) {
    final dominant = dominantByKey[bundle.dominantKey];
    if (dominant == null || !seen.add(dominant.key)) {
      continue;
    }
    cards.add(
      _StoryStudioCardData(
        entry: dominant,
        supportEntries: bundle.supportKeys
            .map((key) => supportByKey[key])
            .whereType<PersonalityImprintEntry>()
            .toList(growable: false),
        relatedPlanets: bundle.relatedPlanets,
      ),
    );
  }

  for (final entry in entries) {
    if (!seen.add(entry.key)) {
      continue;
    }
    cards.add(
      _StoryStudioCardData(
        entry: entry,
        supportEntries: entry.supportKeys
            .map((key) => supportByKey[key])
            .whereType<PersonalityImprintEntry>()
            .toList(growable: false),
        relatedPlanets: const <String>[],
      ),
    );
  }

  return cards;
}

String _storyStudioKindLabel(String value) {
  switch (value.trim().toLowerCase()) {
    case 'aspect':
      return 'ACI';
    case 'house_placement':
      return 'EV YERLESIMI';
    case 'sign_placement':
      return 'BURC TONU';
    default:
      return 'KATMAN';
  }
}

bool _hasBirthData(Map<String, dynamic> profile) {
  final birthDate = (profile['birth_date'] ?? '').toString().trim();
  final birthTime = (profile['birth_time'] ?? '').toString().trim();
  final place = _birthPlace(profile);
  return birthDate.isNotEmpty && birthTime.isNotEmpty && place.isNotEmpty;
}

String _profileKey(Map<String, dynamic> profile) {
  final birthDate = (profile['birth_date'] ?? '').toString().trim();
  final birthTime = (profile['birth_time'] ?? '').toString().trim();
  final place = _birthPlace(profile);
  if (birthDate.isEmpty || birthTime.isEmpty || place.isEmpty) {
    return '';
  }
  return '$birthDate|$birthTime|$place|${profile['timezone'] ?? ''}';
}

String _birthPlace(Map<String, dynamic> profile) {
  final city = (profile['city'] ?? '').toString().trim();
  final country = (profile['country'] ?? '').toString().trim();
  final placeRaw = (profile['place'] ?? '').toString().trim();
  if (placeRaw.isNotEmpty) {
    return placeRaw;
  }
  if (city.isEmpty) {
    return country;
  }
  return country.isEmpty ? city : '$city, $country';
}

String _normalizeBirthTime(String raw) {
  final value = raw.trim();
  if (value.isEmpty) {
    return value;
  }
  final parts = value.split(':');
  if (parts.length < 2) {
    return value;
  }
  final hour = parts[0].padLeft(2, '0');
  final minute = parts[1].padLeft(2, '0');
  return '$hour:$minute';
}

Map<String, dynamic> _asMap(dynamic data) {
  if (data is Map<String, dynamic>) {
    return data;
  }
  if (data is Map) {
    return Map<String, dynamic>.from(data);
  }
  return <String, dynamic>{};
}

List<Map<String, dynamic>> _natalScopes(Map<String, dynamic> map) {
  final scopes = <Map<String, dynamic>>[map];
  final public = _asMap(map['public']);
  if (public.isNotEmpty) {
    scopes.add(public);
  }
  final metaInfo = _asMap(map['meta_info']);
  if (metaInfo.isNotEmpty) {
    scopes.add(metaInfo);
  }
  return scopes;
}

PersonalityImprintProfile? _extractPersonalityImprint(
  Map<String, dynamic> map,
) {
  for (final scope in _natalScopes(map)) {
    final raw = scope['personality_imprint'];
    if (raw is! Map) {
      continue;
    }
    final parsed = PersonalityImprintProfile.fromMap(
      Map<String, dynamic>.from(raw),
    );
    if (parsed.hasContent || parsed.hasExtraContent) {
      return parsed;
    }
  }
  return null;
}

int _storyInteractionHash(_StoryStudioCardData data) {
  final hash = data.entry.labelTr.runes.fold<int>(0, (sum, rune) => sum + rune);
  return hash;
}

int _storyLikeCount(_StoryStudioCardData data) {
  return 10 + (_storyInteractionHash(data) % 28);
}

int _storyCommentCount(_StoryStudioCardData data) {
  return 2 + (_storyInteractionHash(data) % 9);
}

String _firstSentence(String text) {
  final normalized = text.trim();
  if (normalized.isEmpty) {
    return '';
  }
  final parts = normalized
      .split(RegExp(r'(?<=[.!?])\s+'))
      .map((item) => item.trim())
      .where((item) => item.isNotEmpty)
      .toList(growable: false);
  if (parts.isEmpty) {
    return normalized;
  }
  return parts.first;
}
