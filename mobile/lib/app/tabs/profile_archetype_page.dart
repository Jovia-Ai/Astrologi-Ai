import 'dart:async';
import 'dart:math' as math;

import 'package:flutter/material.dart';

import 'package:mobile/app/api/api_client.dart';
import 'package:mobile/design/theme/profile_theme_extension.dart';
import 'package:mobile/design/widgets/jovia_editorial.dart';

class ProfileArchetypeExperiencePage extends StatefulWidget {
  const ProfileArchetypeExperiencePage({
    super.key,
    required this.displayName,
    required this.requestPayload,
    this.baseUrl,
  });

  final String displayName;
  final Map<String, dynamic> requestPayload;
  final String? baseUrl;

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
    unawaited(_load());
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
    final resultTop = _asListOfMaps(_payload['top_archetypes']);
    final chartOnly = _asListOfMaps(_payload['test_scores']).isEmpty;

    return Scaffold(
      backgroundColor: const Color(0xFF09070D),
      body: DecoratedBox(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: <Color>[
              Color(0xFF09070D),
              Color(0xFF130F1C),
              Color(0xFF0D1218),
            ],
          ),
        ),
        child: Stack(
          children: [
            Positioned(
              top: -80,
              right: -40,
              child: _GlowBlob(color: const Color(0x33FF8A4C), size: 220),
            ),
            Positioned(
              left: -60,
              bottom: 110,
              child: _GlowBlob(color: const Color(0x338FD4FF), size: 200),
            ),
            SafeArea(
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
          ],
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
    return Padding(
      padding: const EdgeInsets.fromLTRB(22, 18, 22, 26),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              MinimalCTAButton(
                label: 'Kapat',
                onTap: () => Navigator.of(context).maybePop(),
                glassy: true,
              ),
              const Spacer(),
              Text(
                'ARKETIP AKISI',
                style: profile.typography.monoEyebrow.copyWith(
                  color: const Color(0xFFD7CFDE),
                  fontSize: 11.2,
                  letterSpacing: 1.8,
                ),
              ),
            ],
          ),
          const Spacer(),
          Center(child: _ArchetypeLoadingOrb(animation: animation)),
          const SizedBox(height: 28),
          Center(
            child: Text(
              'Arketip alanin aciliyor',
              textAlign: TextAlign.center,
              style: profile.typography.editorialHeadline.copyWith(
                color: Colors.white,
                fontSize: 34,
                height: 0.98,
              ),
            ),
          ),
          const SizedBox(height: 12),
          Center(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 320),
              child: Text(
                '$displayName icin kimlik, koruma ve gerilim cizgileri tek bir akista toparlaniyor.',
                textAlign: TextAlign.center,
                style: profile.typography.bodyReading.copyWith(
                  color: const Color(0xFFD5CDDD),
                  fontSize: 15,
                  height: 1.62,
                ),
              ),
            ),
          ),
          const SizedBox(height: 26),
          Container(
            padding: const EdgeInsets.fromLTRB(18, 18, 18, 18),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(28),
              color: Colors.white.withValues(alpha: 0.05),
              border: Border.all(color: Colors.white.withValues(alpha: 0.08)),
            ),
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
          const Spacer(),
        ],
      ),
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
      padding: const EdgeInsets.fromLTRB(22, 18, 22, 28),
      children: [
        Row(
          children: [
            MinimalCTAButton(
              label: 'Profiline don',
              onTap: onClose,
              glassy: true,
            ),
            const Spacer(),
            Text(
              'ARKETIP SONUCU',
              style: monoStyle.copyWith(
                color: const Color(0xFFD7CFDE),
                fontSize: 11.2,
                letterSpacing: 1.8,
              ),
            ),
          ],
        ),
        const SizedBox(height: 22),
        _ArchetypeHeroCard(
          displayName: displayName,
          primary: primary,
          secondary: secondary,
          chartOnly: chartOnly,
        ),
        if (_hasNarrative(primary)) ...[
          const SizedBox(height: 24),
          Text(
            'Bu Cizginin Dili',
            style: profile.typography.section.copyWith(
              color: Colors.white,
              fontSize: 24,
              height: 1.06,
            ),
          ),
          const SizedBox(height: 14),
          _ArchetypeNarrativePanel(item: primary),
        ],
        const SizedBox(height: 26),
        Text(
          'Aktif Arketiplerin',
          style: profile.typography.section.copyWith(
            color: Colors.white,
            fontSize: 24,
            height: 1.06,
          ),
        ),
        const SizedBox(height: 14),
        for (var index = 0; index < topArchetypes.length; index++) ...[
          _ArchetypeRankCard(
            rank: index + 1,
            item: topArchetypes[index],
            chartOnly: chartOnly,
          ),
          if (index != topArchetypes.length - 1) const SizedBox(height: 12),
        ],
        if (shadow.isNotEmpty) ...[
          const SizedBox(height: 24),
          _MetaBlock(
            eyebrow: 'KORUYUCU CIZGI',
            title: _readString(shadow['label']),
            body: _readString(shadow['shadow_tr']).isNotEmpty
                ? _readString(shadow['shadow_tr'])
                : 'Stres arttiginda ya da alanini koruman gerektiginde ilk devreye giren savunma dili burada toplanir.',
            score: _readDouble(shadow['score']),
            accent: const Color(0xFF81D9C8),
            illustrationAsset: JoviaIllustrationAsset.blocks,
          ),
        ],
        if (contradiction.isNotEmpty) ...[
          const SizedBox(height: 18),
          _MetaBlock(
            eyebrow: 'ANA GERILIM',
            title: _readString(contradiction['label']),
            body:
                'Sende ayni anda calisan iki yon buradan okunuyor. Bu alan profilin neden tek renk davranmadigini anlatir.',
            score: _readDouble(contradiction['score']),
            accent: const Color(0xFFFFA06C),
            illustrationAsset: JoviaIllustrationAsset.planet,
          ),
        ],
        if (slots.isNotEmpty) ...[
          const SizedBox(height: 24),
          Text(
            'Rol Dagilimi',
            style: profile.typography.section.copyWith(
              color: Colors.white,
              fontSize: 23,
              height: 1.06,
            ),
          ),
          const SizedBox(height: 12),
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
          const SizedBox(height: 24),
          Text(
            'Guven Skoru',
            style: profile.typography.section.copyWith(
              color: Colors.white,
              fontSize: 23,
              height: 1.06,
            ),
          ),
          const SizedBox(height: 14),
          _ConfidenceBar(
            label: 'Genel',
            value: _readDouble(confidence['global']),
            color: const Color(0xFFFFC165),
          ),
          const SizedBox(height: 10),
          _ConfidenceBar(
            label: 'Harita',
            value: _readDouble(confidence['chart']),
            color: const Color(0xFF8FD4FF),
          ),
          if (!chartOnly) ...[
            const SizedBox(height: 10),
            _ConfidenceBar(
              label: 'Test',
              value: _readDouble(confidence['test']),
              color: const Color(0xFF88E8B0),
            ),
          ],
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
    final score = _readDouble(primary['score']);
    final motto = _readString(primary['motto_tr']);
    final portrait = _readString(primary['portrait_tr']);
    return Container(
      padding: const EdgeInsets.fromLTRB(22, 22, 22, 22),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(34),
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: <Color>[
            Color(0xFF1D1328),
            Color(0xFF26191C),
            Color(0xFF101E24),
          ],
        ),
        border: Border.all(color: Colors.white.withValues(alpha: 0.08)),
        boxShadow: const [
          BoxShadow(
            color: Color(0x3312151F),
            blurRadius: 40,
            offset: Offset(0, 24),
            spreadRadius: -24,
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 64,
                height: 64,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: const Color(0xFFFF8A4C),
                  boxShadow: [
                    BoxShadow(
                      color: const Color(0x66FF8A4C),
                      blurRadius: 28,
                      offset: const Offset(0, 12),
                      spreadRadius: -12,
                    ),
                  ],
                ),
                child: const Center(
                  child: Icon(
                    Icons.auto_awesome_rounded,
                    color: Colors.white,
                    size: 30,
                  ),
                ),
              ),
              const Spacer(),
              _ScoreBadge(value: score),
            ],
          ),
          const SizedBox(height: 20),
          if (motto.isNotEmpty) ...[
            Text(
              motto,
              style: profile.typography.monoEyebrow.copyWith(
                color: const Color(0xFFFFD7B8),
                fontSize: 11.4,
                letterSpacing: 1.6,
              ),
            ),
            const SizedBox(height: 10),
          ],
          Text(
            '$primaryLabel sende one cikiyor',
            style: profile.typography.editorialHeadline.copyWith(
              color: Colors.white,
              fontSize: 31,
              height: 0.98,
            ),
          ),
          const SizedBox(height: 12),
          Text(
            portrait.isNotEmpty
                ? portrait
                : (chartOnly
                      ? '$displayName icin bu ilk okuma su an sadece haritandaki omurgadan geliyor.'
                      : '$displayName icin harita ve test ayni eksende bulusturuldu; en guclu cizgi burada toplaniyor.'),
            style: profile.typography.bodyReading.copyWith(
              color: const Color(0xFFD6CDDD),
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
              color: const Color(0xFFBFB4CB),
              fontSize: 12.8,
              height: 1.45,
            ),
          ),
          if (secondaryLabel.isNotEmpty) ...[
            const SizedBox(height: 16),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                _HeroChip(label: primaryLabel),
                _HeroChip(label: secondaryLabel),
                _HeroChip(
                  label: chartOnly ? 'Harita temelli' : 'Fusion profil',
                ),
              ],
            ),
          ],
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
  });

  final int rank;
  final Map<String, dynamic> item;
  final bool chartOnly;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final split = _asMap(item['source_split']);
    final gift = _readString(item['gift_tr']);
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 16),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(24),
        color: Colors.white.withValues(alpha: 0.05),
        border: Border.all(color: Colors.white.withValues(alpha: 0.08)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 38,
            height: 38,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(14),
              color: const Color(0x1FFF8A4C),
              border: Border.all(color: const Color(0x55FF8A4C)),
            ),
            child: Center(
              child: Text(
                '$rank',
                style: profile.typography.buttonLabel.copyWith(
                  color: Colors.white,
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
                Text(
                  _readString(item['label']),
                  style: profile.typography.section.copyWith(
                    color: Colors.white,
                    fontSize: 20,
                    height: 1.08,
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  gift.isNotEmpty
                      ? gift
                      : (chartOnly
                            ? 'Su an bu skor haritandaki kimlik ve rol sinyallerinden uretiliyor.'
                            : 'Harita, test ve baglamsal agirliklar tek skorda bulusuyor.'),
                  style: profile.typography.metaSoft.copyWith(
                    color: const Color(0xFFCEC4D7),
                    fontSize: 13.4,
                    height: 1.5,
                  ),
                ),
                const SizedBox(height: 10),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: [
                    _MiniMetric(
                      label: 'Toplam',
                      value: _readDouble(item['score']),
                    ),
                    _MiniMetric(
                      label: 'Harita',
                      value: _readDouble(split['chart_prior']),
                    ),
                    if (!chartOnly)
                      _MiniMetric(
                        label: 'Test',
                        value: _readDouble(split['test_score']),
                      ),
                  ],
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
    final fear = _readString(item['fear_tr']);
    final shadow = _readString(item['shadow_tr']);
    final relationship = _readString(item['relationship_tr']);
    final workStyle = _readString(item['work_style_tr']);
    final growth = _readString(item['growth_tr']);

    return Container(
      padding: const EdgeInsets.fromLTRB(18, 18, 18, 18),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(28),
        color: Colors.white.withValues(alpha: 0.05),
        border: Border.all(color: Colors.white.withValues(alpha: 0.08)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (fear.isNotEmpty)
            _NarrativeLine(
              label: 'TEMEL KORKU',
              body: fear,
              accent: const Color(0xFFFFC165),
            ),
          if (shadow.isNotEmpty) ...[
            if (fear.isNotEmpty) const SizedBox(height: 14),
            _NarrativeLine(
              label: 'GOLGEDE',
              body: shadow,
              accent: const Color(0xFFFF9A7A),
            ),
          ],
          if (relationship.isNotEmpty) ...[
            if (fear.isNotEmpty || shadow.isNotEmpty)
              const SizedBox(height: 14),
            _NarrativeLine(
              label: 'ILISKIDE',
              body: relationship,
              accent: const Color(0xFF8FD4FF),
            ),
          ],
          if (workStyle.isNotEmpty) ...[
            if (fear.isNotEmpty || shadow.isNotEmpty || relationship.isNotEmpty)
              const SizedBox(height: 14),
            _NarrativeLine(
              label: 'ISTE',
              body: workStyle,
              accent: const Color(0xFF88E8B0),
            ),
          ],
          if (growth.isNotEmpty) ...[
            if (fear.isNotEmpty ||
                shadow.isNotEmpty ||
                relationship.isNotEmpty ||
                workStyle.isNotEmpty)
              const SizedBox(height: 14),
            _NarrativeLine(
              label: 'BUYUME DERSI',
              body: growth,
              accent: const Color(0xFFFFD89B),
            ),
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
    return Column(
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
          style: profile.typography.bodyReading.copyWith(
            color: const Color(0xFFD2C8DB),
            fontSize: 14.4,
            height: 1.6,
          ),
        ),
      ],
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
    return Container(
      padding: const EdgeInsets.fromLTRB(18, 18, 18, 18),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(28),
        color: Colors.white.withValues(alpha: 0.05),
        border: Border.all(color: Colors.white.withValues(alpha: 0.08)),
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  eyebrow,
                  style: profile.typography.monoEyebrow.copyWith(
                    color: accent,
                    fontSize: 11.0,
                    letterSpacing: 1.7,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  title,
                  style: profile.typography.section.copyWith(
                    color: Colors.white,
                    fontSize: 22,
                    height: 1.1,
                  ),
                ),
                if (body.trim().isNotEmpty) ...[
                  const SizedBox(height: 10),
                  Text(
                    body,
                    style: profile.typography.bodyReading.copyWith(
                      color: const Color(0xFFD1C8D9),
                      fontSize: 14.4,
                      height: 1.58,
                    ),
                  ),
                ],
              ],
            ),
          ),
          const SizedBox(width: 18),
          Column(
            children: [
              Container(
                width: 62,
                height: 62,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: accent,
                ),
                child: Center(
                  child: JoviaIllustrationAccent(
                    asset: illustrationAsset,
                    width: 34,
                    height: 34,
                    opacity: 1,
                  ),
                ),
              ),
              const SizedBox(height: 10),
              _ScoreBadge(value: score),
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
                        const Color(0x26FF8A4C),
                        const Color(0x1417D4FF),
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
                    border: Border.all(
                      color: Colors.white.withValues(alpha: 0.08),
                    ),
                  ),
                  child: Align(
                    alignment: Alignment.topCenter,
                    child: Container(
                      width: 18,
                      height: 18,
                      decoration: const BoxDecoration(
                        shape: BoxShape.circle,
                        color: Color(0xFFFF8A4C),
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
                    border: Border.all(color: const Color(0x668FD4FF)),
                  ),
                  child: Align(
                    alignment: Alignment.bottomCenter,
                    child: Container(
                      width: 14,
                      height: 14,
                      decoration: const BoxDecoration(
                        shape: BoxShape.circle,
                        color: Color(0xFF8FD4FF),
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
                  color: const Color(0xFF120F19),
                  border: Border.all(
                    color: Colors.white.withValues(alpha: 0.08),
                  ),
                ),
                child: const Center(
                  child: Icon(
                    Icons.auto_awesome_rounded,
                    size: 40,
                    color: Color(0xFFFFE3A8),
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
        ? const Color(0xFF88E8B0)
        : isActive
        ? const Color(0xFFFFC165)
        : Colors.white.withValues(alpha: 0.18);
    return AnimatedContainer(
      duration: const Duration(milliseconds: 280),
      padding: const EdgeInsets.fromLTRB(14, 12, 14, 12),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(18),
        color: isActive
            ? Colors.white.withValues(alpha: 0.06)
            : Colors.white.withValues(alpha: 0.03),
        border: Border.all(color: accent),
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
              style: profile.typography.metaSoft.copyWith(
                color: Colors.white,
                fontSize: 13.6,
                fontWeight: isActive ? FontWeight.w700 : FontWeight.w500,
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
    return Center(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 22),
        child: Container(
          padding: const EdgeInsets.fromLTRB(22, 22, 22, 22),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(28),
            color: Colors.white.withValues(alpha: 0.06),
            border: Border.all(color: Colors.white.withValues(alpha: 0.08)),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                'Arketip akisi acilamadi',
                style: profile.typography.section.copyWith(
                  color: Colors.white,
                  fontSize: 24,
                ),
              ),
              const SizedBox(height: 12),
              Text(
                error,
                textAlign: TextAlign.center,
                style: profile.typography.bodyReading.copyWith(
                  color: const Color(0xFFD7CEDF),
                  height: 1.58,
                ),
              ),
              const SizedBox(height: 18),
              MinimalCTAButton(
                label: 'Tekrar dene',
                onTap: onRetry,
                emphasized: true,
              ),
            ],
          ),
        ),
      ),
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
                color: Colors.white,
                fontWeight: FontWeight.w700,
              ),
            ),
            const Spacer(),
            Text(
              _scoreText(value),
              style: profile.typography.metaSoft.copyWith(
                color: const Color(0xFFD4CADC),
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        ClipRRect(
          borderRadius: BorderRadius.circular(999),
          child: LinearProgressIndicator(
            value: value.clamp(0.0, 1.0),
            minHeight: 10,
            backgroundColor: Colors.white.withValues(alpha: 0.08),
            valueColor: AlwaysStoppedAnimation<Color>(color),
          ),
        ),
      ],
    );
  }
}

class _MiniMetric extends StatelessWidget {
  const _MiniMetric({required this.label, required this.value});

  final String label;
  final double value;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Container(
      padding: const EdgeInsets.fromLTRB(10, 8, 10, 8),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(14),
        color: Colors.white.withValues(alpha: 0.05),
      ),
      child: Text(
        '$label ${_scoreText(value)}',
        style: profile.typography.metaSoft.copyWith(
          color: const Color(0xFFD3CBDC),
          fontSize: 12.4,
        ),
      ),
    );
  }
}

class _ScoreBadge extends StatelessWidget {
  const _ScoreBadge({required this.value});

  final double value;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Container(
      padding: const EdgeInsets.fromLTRB(12, 8, 12, 8),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(999),
        color: Colors.white.withValues(alpha: 0.08),
        border: Border.all(color: Colors.white.withValues(alpha: 0.09)),
      ),
      child: Text(
        _scoreText(value),
        style: profile.typography.buttonLabel.copyWith(
          color: Colors.white,
          fontWeight: FontWeight.w700,
        ),
      ),
    );
  }
}

class _HeroChip extends StatelessWidget {
  const _HeroChip({required this.label});

  final String label;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Container(
      padding: const EdgeInsets.fromLTRB(10, 8, 10, 8),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(999),
        color: Colors.white.withValues(alpha: 0.08),
        border: Border.all(color: Colors.white.withValues(alpha: 0.08)),
      ),
      child: Text(
        label,
        style: profile.typography.metaSoft.copyWith(
          color: const Color(0xFFEEE7F6),
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
    return Container(
      width: 160,
      padding: const EdgeInsets.fromLTRB(14, 12, 14, 12),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(18),
        color: Colors.white.withValues(alpha: 0.05),
        border: Border.all(color: Colors.white.withValues(alpha: 0.08)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: profile.typography.monoEyebrow.copyWith(
              color: const Color(0xFFFFC165),
              fontSize: 10.6,
              letterSpacing: 1.5,
            ),
          ),
          const SizedBox(height: 6),
          Text(
            value,
            style: profile.typography.buttonLabel.copyWith(
              color: Colors.white,
              fontSize: 14,
              height: 1.25,
            ),
          ),
        ],
      ),
    );
  }
}

class _GlowBlob extends StatelessWidget {
  const _GlowBlob({required this.color, required this.size});

  final Color color;
  final double size;

  @override
  Widget build(BuildContext context) {
    return IgnorePointer(
      child: Container(
        width: size,
        height: size,
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          gradient: RadialGradient(colors: <Color>[color, Colors.transparent]),
        ),
      ),
    );
  }
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
  for (final key in const <String>[
    'motto_tr',
    'portrait_tr',
    'gift_tr',
    'fear_tr',
    'shadow_tr',
    'relationship_tr',
    'work_style_tr',
    'growth_tr',
  ]) {
    if (_readString(item[key]).isNotEmpty) {
      return true;
    }
  }
  return false;
}

String _readString(dynamic value) => (value ?? '').toString().trim();

double _readDouble(dynamic value) {
  if (value is num) {
    return value.toDouble().clamp(0.0, 1.0);
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
