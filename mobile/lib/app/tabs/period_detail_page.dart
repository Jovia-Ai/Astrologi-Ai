import 'package:flutter/material.dart';

import 'package:mobile/app/timing/narrative_dtos.dart';
import 'package:mobile/design/theme/profile_theme_extension.dart';
import 'package:mobile/design/widgets/jovia_editorial.dart';
import 'package:mobile/l10n/l10n.dart';

class PeriodDetailPage extends StatelessWidget {
  const PeriodDetailPage({
    super.key,
    required this.card,
    required this.periodCore,
    this.routeSource = 'unknown',
  });

  final PeriodCardDto card;
  final PeriodCoreDto? periodCore;
  final String routeSource;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final colors = profile.colors;
    final typo = profile.typography;
    final l10n = context.l10n;
    final detail = card.buildDetailNarrative(
      periodCore: periodCore,
      routeSource: routeSource,
    );
    final isDaily = card.eventCard?.horizon.trim().toLowerCase() == 'day';
    final heroWash = JoviaEditorialArtResolver.colorForSurface(
      JoviaEditorialSurfaceVariant.detailHero,
    );
    final readingWash = JoviaEditorialArtResolver.colorForSurface(
      JoviaEditorialSurfaceVariant.readingSurface,
    );
    final leadSection = detail.sections.isNotEmpty
        ? detail.sections.first
        : null;
    final supportingSections = detail.sections.length > 1
        ? detail.sections.skip(1).toList(growable: false)
        : const <PeriodDetailSectionDto>[];
    final spacing = profile.spacing;
    final sectionGap = 18.0;
    final usesEditorialSerif = typo.prefersEditorialSerif(detail.headline);
    final heroTitleStyle = detail.headline.trim().runes.length > 26
        ? typo
              .headlineFor(detail.headline, color: colors.text)
              .copyWith(
                fontSize: usesEditorialSerif ? 40 : 28,
                height: usesEditorialSerif ? 42 / 40 : 32 / 28,
                letterSpacing: usesEditorialSerif ? -0.7 : -0.36,
              )
        : null;
    final heroTitleMaxLines = detail.headline.trim().runes.length > 26 ? 4 : 3;

    return Scaffold(
      backgroundColor: colors.bg,
      appBar: AppBar(
        leadingWidth: 52,
        leading: Padding(
          padding: const EdgeInsets.only(left: 12),
          child: JoviaGlassIconButton(
            onTap: () => Navigator.of(context).maybePop(),
            child: const JoviaUiIcon(asset: JoviaUiAsset.back, size: 18),
          ),
        ),
        title: Text(
          isDaily
              ? l10n.periodDetailTransitTitle
              : l10n.periodDetailPeriodTitle,
          style: typo.navigationLabel(color: colors.text),
        ),
      ),
      body: SafeArea(
        top: false,
        child: JoviaPageScaffold(
          padding: EdgeInsets.fromLTRB(
            spacing.pageHorizontal,
            spacing.xs,
            spacing.pageHorizontal,
            spacing.pageBottom,
          ),
          child: ListView(
            padding: EdgeInsets.zero,
            children: <Widget>[
              JoviaReveal(
                child: JoviaEditorialHeroBlock(
                  label: detail.eyebrow.trim().isNotEmpty
                      ? detail.eyebrow.trim()
                      : (isDaily
                            ? l10n.periodDetailTodayEyebrow
                            : l10n.periodDetailPeriodEyebrow),
                  title: detail.headline,
                  titleStyle: heroTitleStyle,
                  titleMaxLines: heroTitleMaxLines,
                  body: detail.summary,
                  bodyMaxLines: 4,
                  surface: true,
                  large: true,
                  glyph: JoviaUiIcon(
                    asset: JoviaUiAsset.orbitPlanet,
                    size: 16,
                    color: colors.primary,
                  ),
                  background: JoviaColorWash(asset: heroWash, opacity: 0.16),
                  accent: Padding(
                    padding: const EdgeInsets.only(top: 10, right: 2),
                    child: JoviaIllustrationAccent(
                      asset: isDaily
                          ? JoviaIllustrationAsset.planet
                          : JoviaIllustrationAsset.layers,
                      width: 68,
                      height: 68,
                      opacity: 0.28,
                    ),
                  ),
                  footer: _HeroMeta(detail: detail),
                ),
              ),
              if (detail.hasUmbrella) ...<Widget>[
                SizedBox(height: sectionGap),
                JoviaReveal(
                  delay: const Duration(milliseconds: 40),
                  child: JoviaReadingPanel(
                    label: l10n.periodDetailContextLabel,
                    title: detail.umbrellaTitle.trim().isNotEmpty
                        ? detail.umbrellaTitle
                        : l10n.periodDetailContextTitle,
                    padding: const EdgeInsets.fromLTRB(18, 18, 18, 14),
                    leading: const JoviaIllustrationAccent(
                      asset: JoviaIllustrationAsset.blocks,
                      width: 18,
                      height: 18,
                      opacity: 0.84,
                    ),
                    background: JoviaColorWash(
                      asset: readingWash,
                      opacity: 0.08,
                    ),
                    child: Text(
                      detail.umbrellaBody,
                      style: typo.bodyCompact.copyWith(color: colors.text),
                    ),
                  ),
                ),
              ],
              if (leadSection != null) ...<Widget>[
                SizedBox(height: sectionGap),
                JoviaReveal(
                  delay: const Duration(milliseconds: 80),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      JoviaSectionHeader(
                        label: l10n.periodDetailCoreLabel,
                        title: l10n.periodDetailCoreTitle,
                      ),
                      const SizedBox(height: 10),
                      JoviaReadingPanel(
                        background: JoviaColorWash(
                          asset: readingWash,
                          opacity: 0.08,
                        ),
                        child: _NarrativeSectionBlock(
                          section: leadSection,
                          index: 0,
                          featured: true,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
              if (supportingSections.isNotEmpty) ...<Widget>[
                SizedBox(height: sectionGap),
                JoviaReveal(
                  delay: const Duration(milliseconds: 120),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      JoviaSectionHeader(
                        label: l10n.periodDetailSupportingLabel,
                        title: l10n.periodDetailSupportingTitle,
                      ),
                      const SizedBox(height: 20),
                      const ThinDivider(),
                      for (var i = 0; i < supportingSections.length; i++) ...[
                        _NarrativeSectionBlock(
                          section: supportingSections[i],
                          index: i + 1,
                        ),
                        const ThinDivider(),
                      ],
                    ],
                  ),
                ),
              ],
              if (detail.hasMetaRows) ...<Widget>[
                SizedBox(height: sectionGap),
                JoviaReveal(
                  delay: const Duration(milliseconds: 160),
                  child: JoviaReadingPanel(
                    label: l10n.periodDetailTechnicalLabel,
                    title: l10n.periodDetailTechnicalTitle,
                    child: _TechnicalMetaBlock(rows: detail.metaRows),
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

class _HeroMeta extends StatelessWidget {
  const _HeroMeta({required this.detail});

  final PeriodDetailNarrativeDto detail;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final colors = profile.colors;
    final typo = profile.typography;

    if (detail.chips.isEmpty && detail.timingNote.trim().isEmpty) {
      return const SizedBox.shrink();
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: <Widget>[
        if (detail.chips.isNotEmpty)
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: <Widget>[
              for (final chip in detail.chips.take(3))
                JoviaMetaPill(label: chip),
            ],
          ),
        if (detail.chips.isNotEmpty && detail.timingNote.trim().isNotEmpty)
          const SizedBox(height: 16),
        if (detail.timingNote.trim().isNotEmpty)
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: <Widget>[
              const Padding(
                padding: EdgeInsets.only(top: 2),
                child: JoviaUiIcon(asset: JoviaUiAsset.calendarLunar, size: 15),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  detail.timingNote.trim(),
                  style: typo.meta.copyWith(color: colors.textLight),
                ),
              ),
            ],
          ),
      ],
    );
  }
}

class _NarrativeSectionBlock extends StatelessWidget {
  const _NarrativeSectionBlock({
    required this.section,
    required this.index,
    this.featured = false,
  });

  final PeriodDetailSectionDto section;
  final int index;
  final bool featured;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final colors = profile.colors;
    final typo = profile.typography;

    return Padding(
      padding: EdgeInsets.symmetric(vertical: featured ? 0 : 20),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Padding(
            padding: const EdgeInsets.only(top: 2),
            child: JoviaPlanetGlyph(
              asset: _planetForTitle(section.title, index),
              size: featured ? 18 : 16,
              color: colors.primary,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: <Widget>[
                Text(
                  section.title,
                  style: (featured ? typo.sectionTitle : typo.cardTitle)
                      .copyWith(color: colors.text),
                ),
                const SizedBox(height: 8),
                Text(
                  section.body,
                  style: (featured ? typo.bodyLarge : typo.bodyCompact)
                      .copyWith(color: colors.text),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  JoviaPlanetAsset _planetForTitle(String title, int index) {
    final normalized = title.toLowerCase();
    if (normalized.contains('oz')) {
      return JoviaPlanetAsset.sun;
    }
    if (normalized.contains('calis')) {
      return JoviaPlanetAsset.mars;
    }
    if (normalized.contains('ist')) {
      return JoviaPlanetAsset.jupiter;
    }
    const cycle = <JoviaPlanetAsset>[
      JoviaPlanetAsset.saturn,
      JoviaPlanetAsset.neptune,
      JoviaPlanetAsset.venus,
    ];
    return cycle[index % cycle.length];
  }
}

class _TechnicalMetaBlock extends StatelessWidget {
  const _TechnicalMetaBlock({required this.rows});

  final List<PeriodDetailMetaRowDto> rows;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final colors = profile.colors;
    final typo = profile.typography;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: <Widget>[
        if (rows.isNotEmpty) ...<Widget>[
          const ThinDivider(),
          for (var i = 0; i < rows.length; i++) ...<Widget>[
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 14),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: <Widget>[
                  SizedBox(
                    width: 112,
                    child: Text(
                      rows[i].label,
                      style: typo.meta.copyWith(color: colors.textLight),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      rows[i].value,
                      style: typo.bodyCompact.copyWith(color: colors.text),
                    ),
                  ),
                ],
              ),
            ),
            if (i != rows.length - 1) const ThinDivider(),
          ],
        ],
      ],
    );
  }
}
