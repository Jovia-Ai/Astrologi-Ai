import 'package:flutter/material.dart';

import 'package:mobile/app/timing/narrative_dtos.dart';
import 'package:mobile/design/theme/profile_theme_extension.dart';
import 'package:mobile/design/widgets/jovia_assets.dart';
import 'package:mobile/design/widgets/jovia_editorial.dart';

class PeriodMarkerDetailPage extends StatelessWidget {
  const PeriodMarkerDetailPage({super.key, required this.marker});

  final PeriodMarkerDto marker;

  @override
  Widget build(BuildContext context) {
    final colors = context.profileTheme.colors;
    final typo = context.profileTheme.typography;
    final heroWash = JoviaEditorialArtResolver.colorForSurface(
      JoviaEditorialSurfaceVariant.detailHero,
    );

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
          'DONEM ISARETI',
          style: typo.navigationLabel(color: colors.text),
        ),
      ),
      body: SafeArea(
        top: false,
        child: JoviaPageScaffold(
          padding: const EdgeInsets.fromLTRB(24, 8, 24, 32),
          child: ListView(
            padding: EdgeInsets.zero,
            children: [
              JoviaReveal(
                child: JoviaEditorialHeroBlock(
                  label: 'Marker',
                  title: marker.title.isNotEmpty
                      ? marker.title
                      : 'Donem Isareti',
                  body: marker.summary.isNotEmpty
                      ? marker.summary
                      : 'Bu marker icin ek ozet bulunamadi.',
                  bodyMaxLines: 4,
                  surface: true,
                  large: true,
                  glyph: const JoviaPlanetGlyph(
                    asset: JoviaPlanetAsset.moon,
                    size: 16,
                  ),
                  background: JoviaColorWash(asset: heroWash, opacity: 0.14),
                  accent: const Padding(
                    padding: EdgeInsets.only(top: 8, right: 4),
                    child: JoviaIllustrationAccent(
                      asset: JoviaIllustrationAsset.planet,
                      width: 60,
                      height: 60,
                      opacity: 0.24,
                    ),
                  ),
                  footer: marker.timeHint.trim().isEmpty
                      ? null
                      : Text(
                          marker.timeHint.trim(),
                          style: typo.meta.copyWith(color: colors.textLight),
                        ),
                ),
              ),
              if (marker.summary.isNotEmpty &&
                  marker.timeHint.trim().isNotEmpty) ...[
                const SizedBox(height: 40),
                JoviaReveal(
                  delay: const Duration(milliseconds: 40),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      JoviaDividerAsset(
                        kind: JoviaDividerVariant.detailBreak.kind,
                        width: JoviaDividerVariant.detailBreak.defaultWidth,
                      ),
                      const SizedBox(height: 24),
                      const JoviaSectionHeader(
                        label: 'Not',
                        title: 'Bu isaret neyi aciyor',
                      ),
                      const SizedBox(height: 20),
                      Text(
                        marker.summary,
                        style: typo.bodyLarge.copyWith(color: colors.text),
                      ),
                    ],
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
