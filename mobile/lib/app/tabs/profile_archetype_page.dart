import 'dart:async';
import 'dart:math' as math;

import 'package:flutter/material.dart';

import 'package:mobile/app/api/api_client.dart';
import 'package:mobile/app/profile/explainability_panel.dart';
import 'package:mobile/design/theme/profile_theme_extension.dart';
import 'package:mobile/design/widgets/jovia_editorial.dart';

class ProfileArchetypeExperiencePage extends StatefulWidget {
  const ProfileArchetypeExperiencePage({
    super.key,
    required this.displayName,
    required this.requestPayload,
    this.baseUrl,
    this.initialPayload,
  });

  final String displayName;
  final Map<String, dynamic> requestPayload;
  final String? baseUrl;
  final Map<String, dynamic>? initialPayload;

  @override
  State<ProfileArchetypeExperiencePage> createState() =>
      _ProfileArchetypeExperiencePageState();
}

class _ProfileArchetypeExperiencePageState
    extends State<ProfileArchetypeExperiencePage>
    with SingleTickerProviderStateMixin {
  static const _minimumLoading = Duration(milliseconds: 2600);
  static const _loadingSteps = <String>[
    'Kimlik omurgasi taraniyor',
    'Koruyucu hatlar ayiklaniyor',
    'Ic gerilim cizgisi cozuluyor',
    'Arketip haritasi aciliyor',
  ];

  late final AnimationController _orbController;
  Timer? _stepTimer;
  int _activeStep = 0;
  bool _isLoading = true;
  String? _error;
  Map<String, dynamic> _payload = const <String, dynamic>{};

  @override
  void initState() {
    super.initState();
    final seededPayload = widget.initialPayload;
    if (seededPayload != null && seededPayload.isNotEmpty) {
      _payload = Map<String, dynamic>.from(seededPayload);
      _isLoading = false;
    }
    _orbController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 3600),
    )..repeat();
    _stepTimer = Timer.periodic(const Duration(milliseconds: 950), (_) {
      if (!mounted || !_isLoading) {
        return;
      }
      setState(() {
        _activeStep = (_activeStep + 1) % _loadingSteps.length;
      });
    });
    if (_isLoading) {
      unawaited(_load());
    }
  }

  @override
  void dispose() {
    _stepTimer?.cancel();
    _orbController.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    final startedAt = DateTime.now();
    try {
      final client = ApiClient(baseUrl: widget.baseUrl);
      final response = await client.post(
        '/profile/archetype?persist=true',
        data: widget.requestPayload,
      );
      final data = _asMap(response.data);
      if (data.isEmpty) {
        throw Exception('Arketip payload bos geldi.');
      }
      final elapsed = DateTime.now().difference(startedAt);
      if (elapsed < _minimumLoading) {
        await Future<void>.delayed(_minimumLoading - elapsed);
      }
      if (!mounted) {
        return;
      }
      setState(() {
        _payload = data;
        _isLoading = false;
        _error = null;
      });
    } catch (error) {
      final elapsed = DateTime.now().difference(startedAt);
      if (elapsed < _minimumLoading) {
        await Future<void>.delayed(_minimumLoading - elapsed);
      }
      if (!mounted) {
        return;
      }
      setState(() {
        _error = 'Arketip akisi acilamadi: $error';
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final spacing = profile.spacing;
    final resultTop = _asListOfMaps(_payload['top_archetypes']);
    final chartOnly = _asListOfMaps(_payload['test_scores']).isEmpty;

    return Scaffold(
      backgroundColor: profile.colors.bg,
      body: JoviaPageScaffold(
        padding: EdgeInsets.fromLTRB(
          spacing.pageHorizontal,
          spacing.xs,
          spacing.pageHorizontal,
          spacing.lg,
        ),
        child: AnimatedSwitcher(
          duration: const Duration(milliseconds: 650),
          switchInCurve: Curves.easeOutCubic,
          switchOutCurve: Curves.easeInCubic,
          child: _isLoading
              ? _ArchetypeLoadingView(
                  key: const ValueKey<String>('loading'),
                  displayName: widget.displayName,
                  activeStep: _activeStep,
                  steps: _loadingSteps,
                  animation: _orbController,
                )
              : _error != null
              ? _ArchetypeErrorView(
                  key: const ValueKey<String>('error'),
                  error: _error!,
                  onRetry: () {
                    setState(() {
                      _isLoading = true;
                      _error = null;
                      _activeStep = 0;
                    });
                    unawaited(_load());
                  },
                )
              : _ArchetypeResultView(
                  key: ValueKey<String>(
                    'result:${resultTop.isEmpty ? 'empty' : resultTop.first['id'] ?? 'top'}',
                  ),
                  displayName: widget.displayName,
                  payload: _payload,
                  chartOnly: chartOnly,
                  onClose: () => Navigator.of(context).maybePop(),
                  monoStyle: profile.typography.monoEyebrow,
                ),
        ),
      ),
    );
  }
}

class _ArchetypeLoadingView extends StatelessWidget {
  const _ArchetypeLoadingView({
    super.key,
    required this.displayName,
    required this.activeStep,
    required this.steps,
    required this.animation,
  });

  final String displayName;
  final int activeStep;
  final List<String> steps;
  final Animation<double> animation;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final spacing = profile.spacing;
    return ListView(
      padding: EdgeInsets.zero,
      children: [
        const JoviaProfileTopBar(
          label: 'Arketip',
          centerText: 'Kimlik haritasi',
          reserveTrailingSpace: true,
        ),
        SizedBox(height: spacing.s24),
        JoviaEditorialHeroBlock(
          label: 'Arketip akisi',
          title: 'Arketip alanin aciliyor',
          body:
              '$displayName icin kimlik, koruma ve gerilim cizgileri tek bir akista toparlaniyor.',
          large: true,
          bodyMaxLines: 8,
          glyph: const JoviaUiIcon(asset: JoviaUiAsset.orbitPlanet, size: 18),
          footer: Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              const JoviaMetaPill(label: 'Canli analiz'),
              JoviaMetaPill(label: steps[activeStep]),
            ],
          ),
        ),
        SizedBox(height: spacing.s20),
        JoviaSurfaceCard(
          radius: 32,
          child: Column(
            children: [
              Center(child: _ArchetypeLoadingOrb(animation: animation)),
              const SizedBox(height: 18),
              Text(
                steps[activeStep],
                textAlign: TextAlign.center,
                style: profile.typography.section.copyWith(
                  color: profile.colors.text,
                  fontSize: 24,
                  height: 1.08,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'Katmanlar birbiriyle eslesirken sonuc kartlari hazirlaniyor.',
                textAlign: TextAlign.center,
                style: profile.typography.bodyCompact.copyWith(
                  color: profile.colors.textLight,
                  height: 1.56,
                ),
              ),
            ],
          ),
        ),
        SizedBox(height: spacing.s16),
        JoviaSurfaceCard(
          child: Column(
            children: [
              for (var index = 0; index < steps.length; index++) ...[
                _ArchetypeLoadingStep(
                  label: steps[index],
                  isActive: index == activeStep,
                  isPassed: index < activeStep,
                ),
                if (index != steps.length - 1) const SizedBox(height: 12),
              ],
            ],
          ),
        ),
      ],
    );
  }
}

class _ArchetypeResultView extends StatelessWidget {
  const _ArchetypeResultView({
    super.key,
    required this.displayName,
    required this.payload,
    required this.chartOnly,
    required this.onClose,
    required this.monoStyle,
  });

  final String displayName;
  final Map<String, dynamic> payload;
  final bool chartOnly;
  final VoidCallback onClose;
  final TextStyle monoStyle;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final spacing = profile.spacing;
    final topArchetypes = _asListOfMaps(payload['top_archetypes']);
    final shadow = _asMap(payload['shadow_archetype']);
    final contradiction = _asMap(payload['primary_contradiction']);
    final confidence = _asMap(payload['confidence']);
    final slots = _asMap(payload['slots']);
    final chartPrior = _asMap(payload['chart_prior']);
    final priorItems = _asListOfMaps(chartPrior['items']);
    final lookup = <String, String>{
      for (final item in <Map<String, dynamic>>[
        ...topArchetypes,
        ...priorItems,
        if (shadow.isNotEmpty) shadow,
      ])
        if (_readString(item['id']).isNotEmpty)
          _readString(item['id']): _readString(item['label']),
    };
    final primary = topArchetypes.isNotEmpty
        ? topArchetypes.first
        : const <String, dynamic>{};
    final secondary = topArchetypes.length > 1
        ? topArchetypes[1]
        : const <String, dynamic>{};

    return ListView(
      key: const ValueKey<String>('result-scroll'),
      padding: EdgeInsets.zero,
      children: [
        JoviaProfileTopBar(
          label: 'Arketip',
          centerText: 'Sonucun hazir',
          onBackTap: onClose,
          reserveTrailingSpace: true,
        ),
        SizedBox(height: spacing.s24),
        _ArchetypeHeroCard(
          displayName: displayName,
          primary: primary,
          secondary: secondary,
          chartOnly: chartOnly,
        ),
        if (_hasNarrative(primary)) ...[
          SizedBox(height: spacing.s24),
          const JoviaSectionHeader(
            label: 'Okuma katmani',
            title: 'Bu cizginin dili',
            variant: JoviaSectionHeaderVariant.editorial,
          ),
          SizedBox(height: spacing.sm),
          _ArchetypeNarrativePanel(item: primary),
        ],
        SizedBox(height: spacing.s24),
        const JoviaSectionHeader(
          label: 'Aktif cizgiler',
          title: 'Arketiplerinin agirlik sirasi',
          variant: JoviaSectionHeaderVariant.editorial,
        ),
        SizedBox(height: spacing.sm),
        for (var index = 0; index < topArchetypes.length; index++) ...[
          _ArchetypeRankCard(
            rank: index + 1,
            item: topArchetypes[index],
            chartOnly: chartOnly,
            lunarPhase: _readString(payload['lunar_phase']).isEmpty
                ? null
                : _readString(payload['lunar_phase']),
            dignityBonus: _dignityBonusFor(
              _readString(topArchetypes[index]['id']),
              priorItems,
            ),
          ),
          if (index != topArchetypes.length - 1) const SizedBox(height: 12),
        ],
        if (shadow.isNotEmpty) ...[
          SizedBox(height: spacing.s24),
          _MetaBlock(
            eyebrow: 'KORUYUCU CIZGI',
            title: _readString(shadow['label']),
            body: _readString(shadow['shadow_tr']).isNotEmpty
                ? _readString(shadow['shadow_tr'])
                : 'Stres arttiginda ya da alanini koruman gerektiginde ilk devreye giren savunma dili burada toplanir.',
            score: _readDouble(shadow['score']),
            accent: profile.colors.primary,
            illustrationAsset: JoviaIllustrationAsset.blocks,
          ),
        ],
        if (contradiction.isNotEmpty) ...[
          SizedBox(height: spacing.s16),
          _MetaBlock(
            eyebrow: 'ANA GERILIM',
            title: _readString(contradiction['label']),
            body:
                'Sende ayni anda calisan iki yon buradan okunuyor. Bu alan profilin neden tek renk davranmadigini anlatir.',
            score: _readDouble(contradiction['score']),
            accent: profile.colors.warmAccent,
            illustrationAsset: JoviaIllustrationAsset.planet,
          ),
        ],
        if (slots.isNotEmpty) ...[
          SizedBox(height: spacing.s24),
          const JoviaSectionHeader(
            label: 'Rol dagilimi',
            title: 'Hangi arketip hangi rolde calisiyor',
            variant: JoviaSectionHeaderVariant.editorial,
          ),
          SizedBox(height: spacing.sm),
          Wrap(
            spacing: 10,
            runSpacing: 10,
            children: [
              for (final entry in slots.entries)
                _SlotPill(
                  label: _slotLabel(entry.key),
                  value:
                      lookup[_readString(entry.value)] ??
                      _readString(entry.value),
                ),
            ],
          ),
        ],
        if (confidence.isNotEmpty) ...[
          SizedBox(height: spacing.s24),
          const JoviaSectionHeader(
            label: 'Okuma netligi',
            title: 'Guven skoru',
            variant: JoviaSectionHeaderVariant.editorial,
          ),
          SizedBox(height: spacing.sm),
          JoviaSurfaceCard(
            child: Column(
              children: [
                _ConfidenceBar(
                  label: 'Genel',
                  value: _readDouble(confidence['global']),
                  color: profile.colors.warmAccent,
                ),
                const SizedBox(height: 12),
                _ConfidenceBar(
                  label: 'Harita',
                  value: _readDouble(confidence['chart']),
                  color: profile.colors.primary,
                ),
                if (!chartOnly) ...[
                  const SizedBox(height: 12),
                  _ConfidenceBar(
                    label: 'Test',
                    value: _readDouble(confidence['test']),
                    color: profile.colors.lime,
                  ),
                ],
              ],
            ),
          ),
        ],
      ],
    );
  }
}

class _ArchetypeHeroCard extends StatelessWidget {
  const _ArchetypeHeroCard({
    required this.displayName,
    required this.primary,
    required this.secondary,
    required this.chartOnly,
  });

  final String displayName;
  final Map<String, dynamic> primary;
  final Map<String, dynamic> secondary;
  final bool chartOnly;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final primaryLabel = _readString(primary['label']).isNotEmpty
        ? _readString(primary['label'])
        : 'Arketip cizgisi';
    final secondaryLabel = _readString(secondary['label']);
    final softenedSubprofile = primary['subprofile_is_softened'] == true;
    final visibleSubprofileLabel =
        _readString(primary['subprofile_display_label_tr']).isNotEmpty
        ? _readString(primary['subprofile_display_label_tr'])
        : (softenedSubprofile ? '' : _readString(primary['subprofile_label_tr']));
    final score = _readDouble(primary['score']);
    final motto = _copyField(primary, 'motto_tr');
    final plainSummary = _copyField(primary, 'plain_summary_tr');
    final portrait = _copyField(primary, 'portrait_tr');
    final flavor = _copyField(primary, 'flavor_tr');
    final differentiators = _readStringList(primary['differentiators']);
    final accent = profile.colors.warmAccent;
    final headline = visibleSubprofileLabel.isNotEmpty
        ? '$primaryLabel / $visibleSubprofileLabel'
        : '$primaryLabel sende one cikiyor';
    final chips = <String>[
      if (visibleSubprofileLabel.isNotEmpty) visibleSubprofileLabel,
      if (secondaryLabel.isNotEmpty) secondaryLabel,
      ..._mixinLabels(primary).take(2),
      chartOnly ? 'Harita temelli' : 'Fusion profil',
    ];
    final bodyText = plainSummary.isNotEmpty
        ? plainSummary
        : (portrait.isNotEmpty
              ? portrait
              : (flavor.isNotEmpty
                    ? flavor
                    : (differentiators.isNotEmpty
                          ? differentiators.first
                          : '')));

    return JoviaSurfaceCard(
      radius: 34,
      padding: const EdgeInsets.fromLTRB(22, 22, 22, 22),
      child: Stack(
        children: [
          Positioned(
            top: -16,
            right: -6,
            child: Opacity(
              opacity: 0.2,
              child: JoviaIllustrationAccent(
                asset: JoviaIllustrationAsset.planet,
                width: 104,
                height: 104,
                opacity: Theme.of(context).brightness == Brightness.dark
                    ? 0.2
                    : 0.28,
              ),
            ),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  _ArchetypeGlyph(accent: accent),
                  const Spacer(),
                  _ScoreBadge(value: score, color: accent),
                ],
              ),
              const SizedBox(height: 20),
              if (motto.isNotEmpty) ...[
                Text(
                  motto,
                  style: profile.typography.monoEyebrow.copyWith(
                    color: accent,
                    fontSize: 11.4,
                    letterSpacing: 1.7,
                  ),
                ),
                const SizedBox(height: 10),
              ],
              Text(
                headline,
                style: profile.typography.editorialHeadline.copyWith(
                  color: profile.colors.text,
                  fontSize: 30,
                  height: 0.98,
                ),
              ),
              const SizedBox(height: 12),
              Text(
                bodyText.isNotEmpty
                    ? bodyText
                    : (chartOnly
                          ? '$displayName icin bu ilk okuma su an sadece haritandaki omurgadan geliyor.'
                          : '$displayName icin harita ve test ayni eksende bulusturuldu; en guclu cizgi burada toplaniyor.'),
                style: profile.typography.bodyReading.copyWith(
                  color: profile.colors.textLight,
                  fontSize: 15.2,
                  height: 1.62,
                ),
              ),
              const SizedBox(height: 12),
              Text(
                chartOnly
                    ? 'Bu yorum simdilik harita omurgasi uzerinden okunuyor.'
                    : 'Bu yorum harita ve test katmaninin birlikte okunmasiyla olustu.',
                style: profile.typography.metaSoft.copyWith(
                  color: profile.colors.textLight,
                  fontSize: 12.8,
                  height: 1.45,
                ),
              ),
              const SizedBox(height: 16),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  for (final chip in chips)
                    _HeroChip(label: chip, color: accent),
                ],
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _ArchetypeRankCard extends StatelessWidget {
  const _ArchetypeRankCard({
    required this.rank,
    required this.item,
    required this.chartOnly,
    this.lunarPhase,
    this.dignityBonus = 0.0,
  });

  final int rank;
  final Map<String, dynamic> item;
  final bool chartOnly;
  final String? lunarPhase;
  final double dignityBonus;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final split = _asMap(item['source_split']);
    final gift = _copyField(item, 'gift_tr');
    final differentiator = _readStringList(item['differentiators']).isNotEmpty
        ? _readStringList(item['differentiators']).first
        : _readString(item['why_this_not_that']);
    final accent = _archetypeRankAccent(context, rank);

    return JoviaSurfaceCard(
      radius: 26,
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 42,
            height: 42,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(16),
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  Colors.white.withValues(alpha: 0.84),
                  _tintedSurface(context, accent, 0.18),
                ],
              ),
              border: Border.all(color: accent.withValues(alpha: 0.22)),
            ),
            child: Center(
              child: Text(
                '$rank',
                style: profile.typography.buttonLabel.copyWith(
                  color: profile.colors.text,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(
                      child: Text(
                        _readString(item['label']),
                        style: profile.typography.section.copyWith(
                          color: profile.colors.text,
                          fontSize: 20,
                          height: 1.08,
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    _ScoreBadge(
                      value: _readDouble(item['score']),
                      color: accent,
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                if (differentiator.isNotEmpty) ...[
                  Text(
                    differentiator,
                    style: profile.typography.metaSoft.copyWith(
                      color: accent,
                      fontSize: 12.2,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  const SizedBox(height: 6),
                ],
                Text(
                  gift.isNotEmpty
                      ? gift
                      : (chartOnly
                            ? 'Su an bu skor haritandaki kimlik ve rol sinyallerinden uretiliyor.'
                            : 'Harita, test ve baglamsal agirliklar tek skorda bulusuyor.'),
                  style: profile.typography.bodyCompact.copyWith(
                    color: profile.colors.textLight,
                    height: 1.54,
                  ),
                ),
                const SizedBox(height: 12),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: [
                    _MiniMetric(
                      label: 'Toplam',
                      value: _readDouble(item['score']),
                      color: accent,
                    ),
                    _MiniMetric(
                      label: 'Harita',
                      value: _readDouble(split['chart_prior']),
                      color: profile.colors.primary,
                    ),
                    if (!chartOnly)
                      _MiniMetric(
                        label: 'Test',
                        value: _readDouble(split['test_score']),
                        color: profile.colors.lime,
                      ),
                  ],
                ),
                // Faz 2 PR 8b: inline explainability panel — tüm accumulative
                // Faz 2 metadata'yı (why_this_not_that / dignity / lunar phase
                // / aspect direction breakdown) editorial bir yüzeyde toplar.
                ExplainabilityPanel(
                  item: item,
                  accent: accent,
                  lunarPhase: lunarPhase,
                  dignityBonus: dignityBonus,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _ArchetypeNarrativePanel extends StatelessWidget {
  const _ArchetypeNarrativePanel({required this.item});

  final Map<String, dynamic> item;

  @override
  Widget build(BuildContext context) {
    final plainSummary = _copyField(item, 'plain_summary_tr');
    final flavor = _copyField(item, 'flavor_tr');
    final gift = _copyField(item, 'gift_tr');
    final fear = _copyField(item, 'fear_tr');
    final shadow = _copyField(item, 'shadow_tr');
    final relationship = _copyField(item, 'relationship_tr');
    final workStyle = _copyField(item, 'work_style_tr');
    final growth = _copyField(item, 'growth_tr');
    final lines = <Widget>[
      if (plainSummary.isNotEmpty)
        _NarrativeLine(
          label: 'NEDEN BU CIKTI',
          body: plainSummary,
          accent: context.profileTheme.colors.warmAccent,
        ),
      if (flavor.isNotEmpty)
        _NarrativeLine(
          label: 'PROFIL TONU',
          body: flavor,
          accent: context.profileTheme.colors.primary,
        ),
      if (gift.isNotEmpty)
        _NarrativeLine(
          label: 'AYIRT EDICI HAT',
          body: gift,
          accent: context.profileTheme.colors.lime,
        ),
      if (fear.isNotEmpty)
        _NarrativeLine(
          label: 'TEMEL KORKU',
          body: fear,
          accent: context.profileTheme.colors.warmAccent,
        ),
      if (shadow.isNotEmpty)
        _NarrativeLine(
          label: 'GOLGEDE',
          body: shadow,
          accent: const Color(0xFFF28B82),
        ),
      if (relationship.isNotEmpty)
        _NarrativeLine(
          label: 'ILISKIDE',
          body: relationship,
          accent: context.profileTheme.colors.primary,
        ),
      if (workStyle.isNotEmpty)
        _NarrativeLine(
          label: 'ISTE',
          body: workStyle,
          accent: context.profileTheme.colors.lime,
        ),
      if (growth.isNotEmpty)
        _NarrativeLine(
          label: 'BUYUME DERSI',
          body: growth,
          accent: context.profileTheme.colors.lavender,
        ),
    ];

    return JoviaSurfaceCard(
      child: Column(
        children: [
          for (var index = 0; index < lines.length; index++) ...[
            lines[index],
            if (index != lines.length - 1) const SizedBox(height: 12),
          ],
        ],
      ),
    );
  }
}

class _NarrativeLine extends StatelessWidget {
  const _NarrativeLine({
    required this.label,
    required this.body,
    required this.accent,
  });

  final String label;
  final String body;
  final Color accent;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.fromLTRB(14, 14, 14, 14),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(22),
        color: accent.withValues(alpha: 0.08),
        border: Border.all(color: accent.withValues(alpha: 0.18)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: profile.typography.monoEyebrow.copyWith(
              color: accent,
              fontSize: 10.9,
              letterSpacing: 1.7,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            body,
            style: profile.typography.bodyCompact.copyWith(
              color: profile.colors.text,
              height: 1.58,
            ),
          ),
        ],
      ),
    );
  }
}

class _MetaBlock extends StatelessWidget {
  const _MetaBlock({
    required this.eyebrow,
    required this.title,
    required this.body,
    required this.score,
    required this.accent,
    required this.illustrationAsset,
  });

  final String eyebrow;
  final String title;
  final String body;
  final double score;
  final Color accent;
  final JoviaIllustrationAsset illustrationAsset;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return JoviaSurfaceCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  eyebrow,
                  style: profile.typography.monoEyebrow.copyWith(
                    color: accent,
                    fontSize: 11.0,
                    letterSpacing: 1.7,
                  ),
                ),
              ),
              _ScoreBadge(value: score, color: accent),
            ],
          ),
          const SizedBox(height: 14),
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                width: 58,
                height: 58,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: accent.withValues(alpha: 0.16),
                ),
                child: Center(
                  child: JoviaIllustrationAccent(
                    asset: illustrationAsset,
                    width: 30,
                    height: 30,
                    opacity: 0.9,
                  ),
                ),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: profile.typography.section.copyWith(
                        color: profile.colors.text,
                        fontSize: 22,
                        height: 1.1,
                      ),
                    ),
                    if (body.trim().isNotEmpty) ...[
                      const SizedBox(height: 10),
                      Text(
                        body,
                        style: profile.typography.bodyCompact.copyWith(
                          color: profile.colors.textLight,
                          height: 1.58,
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _ArchetypeLoadingOrb extends StatelessWidget {
  const _ArchetypeLoadingOrb({required this.animation});

  final Animation<double> animation;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return AnimatedBuilder(
      animation: animation,
      builder: (context, _) {
        final turn = animation.value;
        final pulse = 0.92 + (math.sin(turn * math.pi * 2) * 0.08);
        return SizedBox(
          width: 210,
          height: 210,
          child: Stack(
            alignment: Alignment.center,
            children: [
              Transform.scale(
                scale: pulse,
                child: Container(
                  width: 172,
                  height: 172,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    gradient: RadialGradient(
                      colors: [
                        profile.colors.warmAccent.withValues(alpha: 0.18),
                        profile.colors.primary.withValues(alpha: 0.1),
                        Colors.transparent,
                      ],
                    ),
                  ),
                ),
              ),
              Transform.rotate(
                angle: turn * math.pi * 2,
                child: Container(
                  width: 186,
                  height: 186,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    border: Border.all(color: profile.colors.strokeSoft),
                  ),
                  child: Align(
                    alignment: Alignment.topCenter,
                    child: Container(
                      width: 18,
                      height: 18,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: profile.colors.warmAccent,
                      ),
                    ),
                  ),
                ),
              ),
              Transform.rotate(
                angle: -turn * math.pi * 1.4,
                child: Container(
                  width: 136,
                  height: 136,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    border: Border.all(
                      color: profile.colors.primary.withValues(alpha: 0.55),
                    ),
                  ),
                  child: Align(
                    alignment: Alignment.bottomCenter,
                    child: Container(
                      width: 14,
                      height: 14,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: profile.colors.primary,
                      ),
                    ),
                  ),
                ),
              ),
              Container(
                width: 90,
                height: 90,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: _tintedSurface(context, profile.colors.lavender, 0.08),
                  border: Border.all(color: profile.colors.strokeSoft),
                ),
                child: Center(
                  child: Icon(
                    Icons.auto_awesome_rounded,
                    size: 40,
                    color: Color.alphaBlend(
                      Colors.white.withValues(alpha: 0.16),
                      profile.colors.warmAccent,
                    ),
                  ),
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}

class _ArchetypeLoadingStep extends StatelessWidget {
  const _ArchetypeLoadingStep({
    required this.label,
    required this.isActive,
    required this.isPassed,
  });

  final String label;
  final bool isActive;
  final bool isPassed;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final accent = isPassed
        ? profile.colors.lime
        : isActive
        ? profile.colors.warmAccent
        : profile.colors.textLight.withValues(alpha: 0.4);
    return AnimatedContainer(
      duration: const Duration(milliseconds: 280),
      padding: const EdgeInsets.fromLTRB(14, 12, 14, 12),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(18),
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            Colors.white.withValues(alpha: isActive ? 0.92 : 0.74),
            _tintedSurface(context, accent, isActive ? 0.14 : 0.08),
          ],
        ),
        border: Border.all(color: accent.withValues(alpha: 0.22)),
      ),
      child: Row(
        children: [
          Container(
            width: 12,
            height: 12,
            decoration: BoxDecoration(shape: BoxShape.circle, color: accent),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              label,
              style: profile.typography.buttonLabel.copyWith(
                color: profile.colors.text,
                fontWeight: isActive ? FontWeight.w700 : FontWeight.w600,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _ArchetypeErrorView extends StatelessWidget {
  const _ArchetypeErrorView({
    super.key,
    required this.error,
    required this.onRetry,
  });

  final String error;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final spacing = profile.spacing;
    return ListView(
      padding: EdgeInsets.zero,
      children: [
        const JoviaProfileTopBar(
          label: 'Arketip',
          centerText: 'Akis durdu',
          reserveTrailingSpace: true,
        ),
        SizedBox(height: spacing.s24),
        const JoviaEditorialHeroBlock(
          label: 'Arketip akisi',
          title: 'Akis bir yerde takildi',
          body: 'Ayni analizi yeniden cagirip kartlari tekrar kurabiliriz.',
          large: true,
          glyph: JoviaUiIcon(asset: JoviaUiAsset.orbitPlanet, size: 18),
          footer: Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [JoviaMetaPill(label: 'Tekrar denenebilir')],
          ),
        ),
        SizedBox(height: spacing.s20),
        JoviaSurfaceCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Arketip akisi acilamadi',
                style: profile.typography.section.copyWith(
                  color: profile.colors.text,
                  fontSize: 24,
                ),
              ),
              const SizedBox(height: 12),
              Text(
                error,
                style: profile.typography.bodyCompact.copyWith(
                  color: profile.colors.textLight,
                  height: 1.58,
                ),
              ),
              const SizedBox(height: 18),
              JoviaPrimaryButton(
                label: 'Tekrar dene',
                onTap: onRetry,
                leading: const JoviaUiIcon(
                  asset: JoviaUiAsset.orbitPlanet,
                  size: 16,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _ConfidenceBar extends StatelessWidget {
  const _ConfidenceBar({
    required this.label,
    required this.value,
    required this.color,
  });

  final String label;
  final double value;
  final Color color;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Text(
              label,
              style: profile.typography.buttonLabel.copyWith(
                color: profile.colors.text,
                fontWeight: FontWeight.w700,
              ),
            ),
            const Spacer(),
            Text(
              _scoreText(value),
              style: profile.typography.metaSoft.copyWith(
                color: profile.colors.textLight,
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        ClipRRect(
          borderRadius: BorderRadius.circular(999),
          child: Container(
            height: 12,
            decoration: BoxDecoration(
              color: profile.colors.chipBg,
              border: Border.all(color: profile.colors.strokeSoft),
              borderRadius: BorderRadius.circular(999),
            ),
            child: Align(
              alignment: Alignment.centerLeft,
              child: FractionallySizedBox(
                widthFactor: value.clamp(0.0, 1.0),
                child: Container(
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      begin: Alignment.centerLeft,
                      end: Alignment.centerRight,
                      colors: [color.withValues(alpha: 0.66), color],
                    ),
                    borderRadius: BorderRadius.circular(999),
                  ),
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }
}

class _MiniMetric extends StatelessWidget {
  const _MiniMetric({
    required this.label,
    required this.value,
    required this.color,
  });

  final String label;
  final double value;
  final Color color;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Container(
      padding: const EdgeInsets.fromLTRB(10, 8, 10, 8),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(999),
        color: color.withValues(alpha: 0.1),
        border: Border.all(color: color.withValues(alpha: 0.18)),
      ),
      child: Text(
        '$label ${_scoreText(value)}',
        style: profile.typography.metaSoft.copyWith(
          color: profile.colors.text,
          fontSize: 12.4,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }
}

class _ScoreBadge extends StatelessWidget {
  const _ScoreBadge({required this.value, required this.color});

  final double value;
  final Color color;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Container(
      padding: const EdgeInsets.fromLTRB(12, 8, 12, 8),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(999),
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            Colors.white.withValues(alpha: 0.86),
            color.withValues(alpha: 0.14),
          ],
        ),
        border: Border.all(color: color.withValues(alpha: 0.22)),
      ),
      child: Text(
        _scoreText(value),
        style: profile.typography.buttonLabel.copyWith(
          color: profile.colors.text,
          fontWeight: FontWeight.w700,
        ),
      ),
    );
  }
}

class _HeroChip extends StatelessWidget {
  const _HeroChip({required this.label, required this.color});

  final String label;
  final Color color;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Container(
      padding: const EdgeInsets.fromLTRB(10, 8, 10, 8),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(999),
        color: color.withValues(alpha: 0.1),
        border: Border.all(color: color.withValues(alpha: 0.16)),
      ),
      child: Text(
        label,
        style: profile.typography.metaSoft.copyWith(
          color: profile.colors.text,
          fontSize: 12.2,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }
}

class _SlotPill extends StatelessWidget {
  const _SlotPill({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final accent = _slotAccent(context, label);
    return SizedBox(
      width: 164,
      child: JoviaSurfaceCard(
        radius: 20,
        padding: const EdgeInsets.fromLTRB(14, 12, 14, 12),
        backgroundColor: _tintedSurface(context, accent, 0.07),
        borderColor: accent.withValues(alpha: 0.18),
        shadow: false,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              label,
              style: profile.typography.monoEyebrow.copyWith(
                color: accent,
                fontSize: 10.6,
                letterSpacing: 1.5,
              ),
            ),
            const SizedBox(height: 6),
            Text(
              value,
              style: profile.typography.buttonLabel.copyWith(
                color: profile.colors.text,
                fontSize: 14,
                height: 1.25,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ArchetypeGlyph extends StatelessWidget {
  const _ArchetypeGlyph({required this.accent});

  final Color accent;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 68,
      height: 68,
      child: Stack(
        alignment: Alignment.center,
        children: [
          Container(
            width: 68,
            height: 68,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: accent.withValues(alpha: 0.16),
            ),
          ),
          Container(
            width: 48,
            height: 48,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  Colors.white.withValues(alpha: 0.88),
                  _tintedSurface(context, accent, 0.18),
                ],
              ),
              border: Border.all(color: accent.withValues(alpha: 0.24)),
            ),
            child: const Center(
              child: JoviaUiIcon(asset: JoviaUiAsset.orbitPlanet, size: 22),
            ),
          ),
        ],
      ),
    );
  }
}

Color _archetypeRankAccent(BuildContext context, int rank) {
  final colors = context.profileTheme.colors;
  switch (rank) {
    case 1:
      return colors.warmAccent;
    case 2:
      return colors.primary;
    case 3:
      return colors.lavender;
    default:
      return colors.textLight;
  }
}

Color _slotAccent(BuildContext context, String label) {
  final colors = context.profileTheme.colors;
  final lower = label.toLowerCase();
  if (lower.contains('kimlik')) {
    return colors.warmAccent;
  }
  if (lower.contains('denge') || lower.contains('iliski')) {
    return colors.primary;
  }
  if (lower.contains('koruma')) {
    return colors.lime;
  }
  if (lower.contains('gorunurluk')) {
    return colors.lavender;
  }
  return colors.textLight;
}

Color _tintedSurface(BuildContext context, Color tint, double alpha) {
  return Color.alphaBlend(
    tint.withValues(alpha: alpha),
    context.profileTheme.colors.surface,
  );
}

Map<String, dynamic> _asMap(dynamic value) {
  if (value is Map<String, dynamic>) {
    return value;
  }
  if (value is Map) {
    return Map<String, dynamic>.from(value);
  }
  return <String, dynamic>{};
}

List<Map<String, dynamic>> _asListOfMaps(dynamic value) {
  if (value is! List) {
    return const <Map<String, dynamic>>[];
  }
  return value
      .whereType<Map>()
      .map((item) => Map<String, dynamic>.from(item))
      .toList();
}

bool _hasNarrative(Map<String, dynamic> item) {
  final copyBlocks = _asMap(item['copy_blocks']);
  for (final key in const <String>[
    'plain_summary_tr',
    'reasoning_tr',
    'flavor_tr',
    'motto_tr',
    'portrait_tr',
    'gift_tr',
    'fear_tr',
    'shadow_tr',
    'relationship_tr',
    'work_style_tr',
    'growth_tr',
  ]) {
    if (_readString(copyBlocks[key]).isNotEmpty ||
        _readString(item[key]).isNotEmpty) {
      return true;
    }
  }
  return false;
}

String _readString(dynamic value) => (value ?? '').toString().trim();

List<String> _readStringList(dynamic value) {
  if (value is! List) {
    return const <String>[];
  }
  return value
      .map((item) => _readString(item))
      .where((item) => item.isNotEmpty)
      .toList(growable: false);
}

String _copyField(Map<String, dynamic> item, String key) {
  final copyBlocks = _asMap(item['copy_blocks']);
  final fromBlocks = _readString(copyBlocks[key]);
  if (fromBlocks.isNotEmpty) {
    return fromBlocks;
  }
  return _readString(item[key]);
}

List<String> _mixinLabels(Map<String, dynamic> item) {
  final mixins = _asListOfMaps(item['mixins']);
  return mixins
      .map((mixin) => _readString(mixin['value_label_tr']))
      .where((label) => label.isNotEmpty)
      .toList(growable: false);
}

double _readDouble(dynamic value) {
  if (value is num) {
    return value.toDouble().clamp(0.0, 1.0);
  }
  return 0.0;
}

double _readSignedDouble(dynamic value) {
  if (value is num) return value.toDouble();
  return 0.0;
}

// Faz 2 PR 8b: `chart_prior.items[...].components.dignity_bonus` lookup
// Belirli bir arketip id için. Bulunamazsa 0.0 (peregrine fallback).
double _dignityBonusFor(String archetypeId, List<Map<String, dynamic>> priorItems) {
  if (archetypeId.isEmpty) return 0.0;
  for (final item in priorItems) {
    if (_readString(item['id']) != archetypeId) continue;
    final components = item['components'];
    if (components is Map) {
      return _readSignedDouble(components['dignity_bonus']);
    }
  }
  return 0.0;
}

String _scoreText(double value) => '%${(value.clamp(0.0, 1.0) * 100).round()}';

String _slotLabel(String key) {
  switch (key) {
    case 'primary_identity_spine':
      return 'Ana kimlik';
    case 'secondary_balancing_line':
      return 'Dengeleyici cizgi';
    case 'relational_line':
      return 'Iliskisel rol';
    case 'work_visibility_line':
      return 'Gorunurluk';
    case 'shadow_protection_line':
      return 'Koruma';
    default:
      return key.replaceAll('_', ' ');
  }
}
