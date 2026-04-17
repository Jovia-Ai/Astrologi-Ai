import 'package:flutter/material.dart';

import 'package:mobile/app/profile/profile_v8_adapter.dart';
import 'package:mobile/app/timing/turkish_text.dart';
import 'package:mobile/design/theme/profile_theme_extension.dart';
import 'package:mobile/design/widgets/jovia_editorial.dart';

class ProfileV8SectionsView extends StatelessWidget {
  const ProfileV8SectionsView({
    super.key,
    required this.data,
    this.isLoading = false,
    this.error,
    this.onOpenIdentity,
    this.onOpenCta,
  });

  final ProfileV8Data data;
  final bool isLoading;
  final String? error;
  final VoidCallback? onOpenIdentity;
  final VoidCallback? onOpenCta;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final children = <Widget>[];

    if ((error ?? '').trim().isNotEmpty && !data.hasRenderableContent) {
      final message = (error ?? '').trim();
      children.add(
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: JoviaReadingPanel(
            label: 'UYARI',
            title: 'Profil yorumu alınamadı',
            body: message,
          ),
        ),
      );
      children.add(const SizedBox(height: 18));
    }

    if (isLoading && !data.hasRenderableContent) {
      children.add(
        const Padding(
          padding: EdgeInsets.symmetric(horizontal: 16),
          child: Center(child: CircularProgressIndicator()),
        ),
      );
      children.add(const SizedBox(height: 18));
    }

    children.add(
      _V8CenterQuote(
        label: 'Kimlik ekseni',
        text: data.identityQuote,
        onTap: onOpenIdentity,
      ),
    );

    children.add(_V8InsightStrip(items: data.topInsights));

    final uniqueSection = data.uniqueBlock;
    final hasUniqueContent =
        (uniqueSection?.hasContent == true) || data.differentiators.isNotEmpty;
    if (hasUniqueContent) {
      final section =
          uniqueSection ??
          const ProfileV8TextSection(
            eyebrow: 'SENİ FARKLI KILAN',
            headline: '',
            body: '',
          );
      children.add(const SizedBox(height: 14));
      children.add(
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: _V8UniqueMetricSlab(
            section: section,
            differentiators: data.differentiators,
          ),
        ),
      );
    }

    if (_hasEditorialContent(data.originSection)) {
      final section = data.originSection;
      if (section != null) {
        children.add(const SizedBox(height: 14));
        children.add(
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: _V8PastTeaserCard(section: section),
          ),
        );
      }
    }

    if (_hasEditorialContent(data.firstImpressionSection)) {
      final section = data.firstImpressionSection;
      if (section != null) {
        children.add(const SizedBox(height: 12));
        children.add(
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: _V8FirstImpressionCard(section: section),
          ),
        );
      }
    }

    final hasTalents =
        data.talentItems.any((item) => item.hasContent) ||
        data.talents.any((item) => item.trim().isNotEmpty);
    if (hasTalents) {
      children.add(const SizedBox(height: 14));
      children.add(
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: _V8TalentsStrip(
            talents: data.talents,
            talentItems: data.talentItems,
          ),
        ),
      );
    }

    void addWhiteSection(
      ProfileV8TextSection? section, {
      Color accent = const Color(0xFF7F77DD),
      Color accentTextColor = const Color(0xFF26215C),
    }) {
      if (section == null || !section.hasContent) {
        return;
      }
      children.add(const SizedBox(height: 14));
      children.add(
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: _V8SectionCard(
            section: section,
            dark: false,
            subtle: false,
            leftAccent: false,
            accent: accent,
            accentTextColor: accentTextColor,
          ),
        ),
      );
    }

    if (_hasEditorialContent(data.conversationSection)) {
      children.add(const SizedBox(height: 14));
      children.add(
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: _V8ConversationCard(section: data.conversationSection!),
        ),
      );
    }

    if (_hasEditorialContent(data.effectSection)) {
      children.add(const SizedBox(height: 14));
      children.add(
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: _V8AffectsCard(section: data.effectSection!),
        ),
      );
    }

    if (_hasEditorialContent(data.defenseSection)) {
      children.add(const SizedBox(height: 14));
      children.add(
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: _V8DefenseCard(section: data.defenseSection!),
        ),
      );
    }

    if (_hasEditorialContent(data.firstFeltSection)) {
      children.add(const SizedBox(height: 14));
      children.add(
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: _V8FirstFeltCard(section: data.firstFeltSection!),
        ),
      );
    }

    if (data.collectiveSection?.hasContent == true) {
      final section = data.collectiveSection;
      if (section != null) {
        children.add(const SizedBox(height: 14));
        children.add(
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: _V8SectionCard(
              section: section,
              dark: false,
              subtle: false,
              leftAccent: false,
              accent: const Color(0xFFCAFF4D),
            ),
          ),
        );
      }
    }

    addWhiteSection(
      data.intimacySection,
      accent: const Color(0xFFE8A020),
      accentTextColor: const Color(0xFF8A5600),
    );
    addWhiteSection(data.mindSection);

    if (_hasEditorialContent(data.ctaSection)) {
      final section = data.ctaSection;
      if (section != null) {
        children.add(const SizedBox(height: 16));
        children.add(
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: _V8LimeCta(section: section, onTap: onOpenCta),
          ),
        );
      }
    }

    children.add(SizedBox(height: profile.spacing.s12));

    return ExcludeSemantics(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: children,
      ),
    );
  }
}

class _V8CenterQuote extends StatelessWidget {
  const _V8CenterQuote({required this.label, required this.text, this.onTap});

  final String label;
  final String text;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final resolved = _resolveIdentityQuote(text);
    final headline = _editorialBreak(resolved);

    final content = Container(
      color: Colors.white,
      padding: const EdgeInsets.fromLTRB(20, 28, 20, 22),
      child: Column(
        children: [
          Text(
            turkishToUpper(label),
            textAlign: TextAlign.center,
            style: profile.typography.micro.copyWith(
              color: const Color(0xFFBBBBBB),
              fontSize: 8,
              letterSpacing: 1.08,
              fontWeight: FontWeight.w400,
            ),
          ),
          const SizedBox(height: 12),
          Text(
            headline,
            textAlign: TextAlign.center,
            style: profile.typography.section.copyWith(
              color: const Color(0xFF111111),
              fontSize: 22.7,
              height: 28.83 / 22.7,
              fontWeight: FontWeight.w400,
              letterSpacing: -0.5,
            ),
          ),
          const SizedBox(height: 12),
          Container(
            width: 28,
            height: 2,
            decoration: BoxDecoration(
              color: const Color(0xFFCAFF4D),
              borderRadius: BorderRadius.circular(1),
            ),
          ),
        ],
      ),
    );

    if (onTap == null) {
      return content;
    }
    return Material(
      color: Colors.transparent,
      child: InkWell(onTap: onTap, child: content),
    );
  }

  static String _resolveIdentityQuote(String raw) {
    final compact = raw.replaceAll(RegExp(r'\s+'), ' ').trim();
    if (compact.isEmpty) {
      return 'Gücün sende zaten var.';
    }
    return compact;
  }

  static String _editorialBreak(String value) {
    if (value.contains('\n')) {
      return value;
    }
    if (value.length < 26) {
      return value;
    }
    final words = value.split(' ');
    if (words.length < 4) {
      return value;
    }
    final half = (words.length / 2).ceil();
    return '${words.take(half).join(' ')}\n${words.skip(half).join(' ')}';
  }
}

class _V8InsightStrip extends StatelessWidget {
  const _V8InsightStrip({required this.items});

  final List<ProfileV8InsightCell> items;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final border = const Color.fromRGBO(0, 0, 0, 0.07);
    final labelColor = const Color(0xFFBBBBBB);
    final titleColor = const Color(0xFF111111);
    final subtitleColor = const Color(0xFF777777);
    final displayItems = _normalizedItems(items);

    return Container(
      decoration: const BoxDecoration(
        border: Border(
          top: BorderSide(color: Color.fromRGBO(0, 0, 0, 0.07)),
          bottom: BorderSide(color: Color.fromRGBO(0, 0, 0, 0.07)),
        ),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          for (var index = 0; index < displayItems.length; index++) ...[
            Expanded(
              child: Container(
                color: Colors.white,
                padding: const EdgeInsets.fromLTRB(12, 13, 12, 13),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      turkishToUpper(displayItems[index].label),
                      style: profile.typography.micro.copyWith(
                        color: labelColor,
                        fontSize: 8,
                        fontWeight: FontWeight.w400,
                        letterSpacing: 0.72,
                      ),
                    ),
                    const SizedBox(height: 7),
                    Container(
                      width: 26,
                      height: 26,
                      decoration: BoxDecoration(
                        color: displayItems[index].tint,
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Icon(
                        displayItems[index].icon,
                        size: 14,
                        color: const Color(0xFF111111),
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      displayItems[index].title,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: profile.typography.card.copyWith(
                        color: titleColor,
                        fontWeight: FontWeight.w400,
                        fontSize: 12,
                        height: 1.25,
                      ),
                    ),
                    const SizedBox(height: 3),
                    Text(
                      displayItems[index].subtitle,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: profile.typography.micro.copyWith(
                        color: subtitleColor,
                        fontSize: 9,
                        height: 13 / 9,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            if (index != displayItems.length - 1)
              Container(width: 1, color: border),
          ],
        ],
      ),
    );
  }

  static List<ProfileV8InsightCell> _normalizedItems(
    List<ProfileV8InsightCell> source,
  ) {
    const defaults = <ProfileV8InsightCell>[
      ProfileV8InsightCell(
        label: 'Aura',
        title: 'Auran net',
        subtitle: 'Dışarıdan güven veren bir ton.',
        icon: Icons.blur_on_rounded,
        tint: Color(0xFFD2F2A0),
      ),
      ProfileV8InsightCell(
        label: 'Yönetici',
        title: 'Yönetici etki',
        subtitle: 'Kimlik çizgini tutarlı kılıyor.',
        icon: Icons.public_rounded,
        tint: Color(0xFFF0F0F3),
      ),
      ProfileV8InsightCell(
        label: 'İç ritim',
        title: 'Ritmin dengeli',
        subtitle: 'Kararlarını iç dengeyle alırsın.',
        icon: Icons.graphic_eq_rounded,
        tint: Color(0xFFDDD8FC),
      ),
    ];
    final out = <ProfileV8InsightCell>[];
    for (var index = 0; index < 3; index++) {
      final item = index < source.length ? source[index] : defaults[index];
      var title = _cleanInsightText(item.title);
      var subtitle = _cleanInsightText(item.subtitle);
      if (_looksLikeAstroPlacement(title)) {
        final placement = _extractHousePlacement(title);
        if (placement != null) {
          title = placement.$1;
          if (subtitle.trim().isEmpty || subtitle.trim() == '—') {
            subtitle = '${placement.$2}. ev etkisi';
          }
        }
      }
      if (title.trim() == '—') {
        title = '';
      }
      if (subtitle.trim() == '—') {
        subtitle = '';
      }
      out.add(
        ProfileV8InsightCell(
          label: item.label.trim().isEmpty ? defaults[index].label : item.label,
          title: title.trim().isEmpty ? defaults[index].title : title,
          subtitle: subtitle.trim().isEmpty
              ? defaults[index].subtitle
              : subtitle,
          icon: item.icon,
          tint: item.tint,
        ),
      );
    }
    return out;
  }

  static String _cleanInsightText(String raw) {
    final compact = raw.replaceAll(RegExp(r'\s+'), ' ').trim();
    if (compact.isEmpty) {
      return '';
    }
    final replaced = compact
        .replaceAll('_', ' ')
        .replaceAll('-', ' ')
        .replaceAllMapped(
          RegExp(r'\bhouse\s+(\d+)\b', caseSensitive: false),
          (match) => '${match.group(1)}. ev',
        )
        .replaceAllMapped(
          RegExp(r'\bsun\b', caseSensitive: false),
          (_) => 'Güneş',
        )
        .replaceAllMapped(
          RegExp(r'\bmoon\b', caseSensitive: false),
          (_) => 'Ay',
        )
        .replaceAllMapped(
          RegExp(r'\bmercury\b', caseSensitive: false),
          (_) => 'Merkür',
        )
        .replaceAllMapped(
          RegExp(r'\bvenus\b', caseSensitive: false),
          (_) => 'Venüs',
        )
        .replaceAllMapped(
          RegExp(r'\bmars\b', caseSensitive: false),
          (_) => 'Mars',
        )
        .replaceAllMapped(
          RegExp(r'\bjupiter\b', caseSensitive: false),
          (_) => 'Jüpiter',
        )
        .replaceAllMapped(
          RegExp(r'\bsaturn\b', caseSensitive: false),
          (_) => 'Satürn',
        )
        .replaceAllMapped(
          RegExp(r'\buranus\b', caseSensitive: false),
          (_) => 'Uranüs',
        )
        .replaceAllMapped(
          RegExp(r'\bneptune\b', caseSensitive: false),
          (_) => 'Neptün',
        )
        .replaceAllMapped(
          RegExp(r'\bpluto\b', caseSensitive: false),
          (_) => 'Plüton',
        )
        .replaceAll(RegExp(r'\s+'), ' ')
        .trim();
    return replaced;
  }

  static bool _looksLikeAstroPlacement(String value) {
    final lower = value.toLowerCase();
    return RegExp(
          r'\b(güneş|ay|merkür|venüs|mars|jüpiter|satürn|uranüs|neptün|plüton|sun|moon|mercury|venus|mars|jupiter|saturn|uranus|neptune|pluto)\b',
        ).hasMatch(lower) &&
        RegExp(r'\b\d{1,2}\.?\s*ev\b').hasMatch(lower);
  }

  static (String, String)? _extractHousePlacement(String value) {
    final match = RegExp(
      r'^\s*([A-Za-zÇĞİÖŞÜçğıöşü]+)\s+(\d{1,2})\.?\s*ev\s*$',
      caseSensitive: false,
    ).firstMatch(value);
    if (match == null) {
      return null;
    }
    return ((match.group(1) ?? '').trim(), (match.group(2) ?? '').trim());
  }
}

class _V8UniqueMetricSlab extends StatelessWidget {
  const _V8UniqueMetricSlab({
    required this.section,
    this.differentiators = const <ProfileV8Differentiator>[],
  });

  final ProfileV8TextSection section;
  final List<ProfileV8Differentiator> differentiators;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final rows = differentiators.isNotEmpty
        ? _rowsFromDifferentiators(differentiators)
        : _rowsFromSection(section);
    final headline = section.headline.trim().isEmpty
        ? 'Sende çalışan çizgi belirgin.'
        : section.headline.trim();
    final subtitle = section.body.trim().isEmpty
        ? 'Haritadaki sayısal imzalar bunu destekliyor.'
        : section.body.trim();
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF111111),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFF1B1B1B)),
      ),
      padding: const EdgeInsets.fromLTRB(14, 14, 14, 14),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            turkishToUpper(
              section.eyebrow.trim().isEmpty
                  ? 'SENİ FARKLI KILAN'
                  : section.eyebrow,
            ),
            style: profile.typography.micro.copyWith(
              color: const Color(0xFF8D8D8D),
              fontSize: 8,
              letterSpacing: 0.78,
              fontWeight: FontWeight.w400,
            ),
          ),
          const SizedBox(height: 7),
          Text(
            headline,
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
            style: profile.typography.card.copyWith(
              color: Colors.white,
              fontSize: 15.2,
              height: 1.3,
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: 5),
          Text(
            subtitle,
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
            style: profile.typography.micro.copyWith(
              color: const Color(0xFF8A8A8A),
              fontSize: 10.2,
              height: 1.34,
            ),
          ),
          if (rows.isNotEmpty) ...[
            const SizedBox(height: 11),
            for (var i = 0; i < rows.length; i++) ...[
              _V8MetricRow(row: rows[i]),
              if (i != rows.length - 1) const SizedBox(height: 7),
            ],
          ],
        ],
      ),
    );
  }

  static List<_V8MetricRowData> _rowsFromDifferentiators(
    List<ProfileV8Differentiator> items,
  ) {
    final rows = <_V8MetricRowData>[];
    for (final item in items.take(3)) {
      final stat = item.stat.trim();
      rows.add(
        _V8MetricRowData(
          eyebrow: item.eyebrow.trim().isEmpty ? 'İMZA' : item.eyebrow,
          title: item.headline.trim().isEmpty
              ? 'Belirgin bir imza taşıyorsun.'
              : item.headline.trim(),
          subtitle: item.body.trim(),
          statValue: stat.isEmpty ? '•' : stat,
          statLabel: item.statLabel.trim(),
          accent: item.accent,
        ),
      );
    }
    return rows;
  }

  static List<_V8MetricRowData> _rowsFromSection(ProfileV8TextSection section) {
    final rows = <_V8MetricRowData>[];
    for (final bullet in section.bullets.take(3)) {
      final parsed = _parseMetricRow(bullet);
      if (parsed != null) {
        rows.add(parsed);
      }
    }
    if (rows.isNotEmpty) {
      return rows;
    }
    final fallbackStat = _extractTrailingStat(section.body);
    if (section.headline.trim().isNotEmpty || fallbackStat.$1.isNotEmpty) {
      rows.add(
        _V8MetricRowData(
          eyebrow: section.eyebrow.trim().isEmpty ? 'İMZA' : section.eyebrow,
          title: section.headline.trim().isEmpty
              ? 'Belirgin bir imza taşıyorsun.'
              : section.headline.trim(),
          subtitle: section.body.trim(),
          statValue: fallbackStat.$1.isEmpty ? '•' : fallbackStat.$1,
          statLabel: fallbackStat.$2,
        ),
      );
    }
    return rows;
  }

  static _V8MetricRowData? _parseMetricRow(String raw) {
    final parts = raw
        .split('·')
        .map((item) => item.replaceAll(RegExp(r'\s+'), ' ').trim())
        .where((item) => item.isNotEmpty)
        .toList();
    if (parts.isEmpty) {
      return null;
    }
    final eyebrow = parts.first;
    final title = parts.length >= 2 ? parts[1] : parts.first;
    final statRaw = parts.length >= 3 ? parts.sublist(2).join(' · ') : '';
    final stat = _extractTrailingStat(statRaw);
    return _V8MetricRowData(
      eyebrow: eyebrow,
      title: title,
      subtitle: statRaw,
      statValue: stat.$1.isEmpty ? '•' : stat.$1,
      statLabel: stat.$2,
    );
  }

  static (String, String) _extractTrailingStat(String text) {
    final clean = text.trim();
    if (clean.isEmpty) {
      return ('', '');
    }
    final match = RegExp(
      r'([0-9]+(?:[.,][0-9]+)?(?:°|×|x)?)\s*([a-zA-ZğüşöçıİĞÜŞÖÇ. ]*)$',
      caseSensitive: false,
    ).firstMatch(clean);
    if (match == null) {
      return ('', '');
    }
    return (
      (match.group(1) ?? '').trim(),
      (match.group(2) ?? '').replaceAll(RegExp(r'\s+'), ' ').trim(),
    );
  }
}

class _V8MetricRow extends StatelessWidget {
  const _V8MetricRow({required this.row});

  final _V8MetricRowData row;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF151515),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: const Color(0xFF202020)),
      ),
      padding: const EdgeInsets.fromLTRB(11, 9, 11, 9),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  turkishToUpper(row.eyebrow),
                  style: profile.typography.micro.copyWith(
                    color: const Color(0xFF8A8A8A),
                    fontSize: 7.7,
                    letterSpacing: 0.7,
                    fontWeight: FontWeight.w400,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  row.title,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: profile.typography.bodyCompact.copyWith(
                    color: Colors.white,
                    fontSize: 11.2,
                    height: 1.32,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                if (row.subtitle.trim().isNotEmpty) ...[
                  const SizedBox(height: 3),
                  Text(
                    row.subtitle,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: profile.typography.micro.copyWith(
                      color: const Color(0xFF7A7A7A),
                      fontSize: 9,
                    ),
                  ),
                ],
              ],
            ),
          ),
          const SizedBox(width: 10),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                row.statValue,
                style: profile.typography.section.copyWith(
                  color: _v8StatColor(row.accent),
                  fontSize: 18,
                  height: 1.08,
                  fontWeight: FontWeight.w500,
                ),
              ),
              if (row.statLabel.trim().isNotEmpty)
                Text(
                  row.statLabel,
                  style: profile.typography.micro.copyWith(
                    color: const Color(0xFF8A8A8A),
                    fontSize: 8,
                  ),
                ),
            ],
          ),
        ],
      ),
    );
  }
}

class _V8PastTeaserCard extends StatelessWidget {
  const _V8PastTeaserCard({required this.section});

  final ProfileV8TextSection section;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final title = section.headline.trim().isEmpty
        ? 'Geçmişten gelen bir iz var.'
        : section.headline.trim();
    final body = section.body.trim().isEmpty
        ? 'Zamanında öğrendiğin bir savunma bugün hâlâ görünür olabilir.'
        : section.body.trim();
    return Container(
      clipBehavior: Clip.antiAlias,
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color.fromRGBO(0, 0, 0, 0.07)),
      ),
      child: Stack(
        children: [
          Padding(
            padding: const EdgeInsets.only(left: 3),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
          Expanded(
            child: Padding(
              padding: const EdgeInsets.fromLTRB(13, 12, 13, 12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        width: 5,
                        height: 5,
                        decoration: BoxDecoration(
                          color: const Color(0xFF7F77DD),
                          borderRadius: BorderRadius.circular(2.5),
                        ),
                      ),
                      const SizedBox(width: 7),
                      Expanded(
                        child: Text(
                          turkishToUpper(
                            section.eyebrow.trim().isEmpty
                                ? 'BU NEREDEN GELİYOR OLABİLİR'
                                : section.eyebrow,
                          ),
                          style: profile.typography.micro.copyWith(
                            color: const Color(0xFFB1ABD9),
                            fontSize: 8,
                            letterSpacing: 0.8,
                            fontWeight: FontWeight.w400,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text(
                    title,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: profile.typography.section.copyWith(
                      color: const Color(0xFF111111),
                      fontSize: 16,
                      height: 1.36,
                      letterSpacing: -0.3,
                      fontWeight: FontWeight.w400,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    body,
                    maxLines: 3,
                    overflow: TextOverflow.ellipsis,
                    style: profile.typography.bodyCompact.copyWith(
                      color: const Color(0xFF8A8A8A),
                      fontSize: 10.8,
                      height: 1.56,
                    ),
                  ),
                  if ((section.callout ?? '').trim().isNotEmpty) ...[
                    const SizedBox(height: 8),
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 8,
                        vertical: 4,
                      ),
                      decoration: BoxDecoration(
                        color: const Color(0xFFF0EEFF),
                        borderRadius: BorderRadius.circular(4),
                        border: Border.all(
                          color: const Color.fromRGBO(83, 74, 183, 0.15),
                        ),
                      ),
                      child: Text(
                        (section.callout ?? '').trim(),
                        style: profile.typography.micro.copyWith(
                          color: const Color(0xFF534AB7),
                          fontSize: 8.8,
                        ),
                      ),
                    ),
                  ],
                  if ((section.footer ?? '').trim().isNotEmpty ||
                      (section.cta ?? '').trim().isNotEmpty) ...[
                    const SizedBox(height: 10),
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            (section.footer ?? '').trim().isEmpty
                                ? 'Daha fazla geçmiş katmanı var'
                                : (section.footer ?? '').trim(),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: profile.typography.micro.copyWith(
                              color: const Color(0xFFAAAAAA),
                              fontSize: 8.9,
                            ),
                          ),
                        ),
                        if ((section.cta ?? '').trim().isNotEmpty)
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 10,
                              vertical: 5,
                            ),
                            decoration: BoxDecoration(
                              color: Colors.white,
                              borderRadius: BorderRadius.circular(20),
                              border: Border.all(
                                color: const Color(0xFFDDD8FC),
                              ),
                            ),
                            child: Text(
                              (section.cta ?? '').trim(),
                              style: profile.typography.micro.copyWith(
                                color: const Color(0xFF534AB7),
                                fontSize: 8.9,
                              ),
                            ),
                          ),
                      ],
                    ),
                  ],
                ],
              ),
            ),
          ),
              ],
            ),
          ),
          Positioned(
            left: 0,
            top: 0,
            bottom: 0,
            width: 3,
            child: Container(color: const Color(0xFF7F77DD)),
          ),
        ],
      ),
    );
  }
}

class _V8FirstImpressionCard extends StatelessWidget {
  const _V8FirstImpressionCard({required this.section});

  final ProfileV8TextSection section;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final title = section.headline.trim().isEmpty
        ? 'İlk anda sakin, yakında derin hissedilirsin.'
        : section.headline.trim();
    final body = section.body.trim().isEmpty
        ? 'İnsanlar sende önce duruşu, sonra gerçek derinliği fark eder.'
        : section.body.trim();
    final split = _splitLead(title);
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color.fromRGBO(0, 0, 0, 0.07)),
      ),
      padding: const EdgeInsets.fromLTRB(14, 13, 14, 13),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Container(
                  height: 1,
                  color: const Color.fromRGBO(0, 0, 0, 0.07),
                ),
              ),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 8),
                child: Text(
                  turkishToUpper(
                    section.eyebrow.trim().isEmpty
                        ? 'İLK İZLENİM'
                        : section.eyebrow,
                  ),
                  style: profile.typography.micro.copyWith(
                    color: const Color(0xFFBBBBBB),
                    fontSize: 8,
                    letterSpacing: 0.8,
                    fontWeight: FontWeight.w400,
                  ),
                ),
              ),
              Expanded(
                child: Container(
                  height: 1,
                  color: const Color.fromRGBO(0, 0, 0, 0.07),
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          if (split.$1.trim().isNotEmpty)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 3),
              decoration: BoxDecoration(
                color: const Color(0xFFDDD8FC),
                borderRadius: BorderRadius.circular(3),
              ),
              child: Text(
                split.$1,
                style: profile.typography.bodyCompact.copyWith(
                  color: const Color(0xFF26215C),
                  fontSize: 15,
                  height: 1.35,
                ),
              ),
            ),
          if (split.$2.trim().isNotEmpty) ...[
            const SizedBox(height: 4),
            Text(
              split.$2,
              style: profile.typography.bodyCompact.copyWith(
                color: const Color(0xFF111111),
                fontSize: 16,
                height: 1.38,
                letterSpacing: -0.2,
              ),
            ),
          ],
          const SizedBox(height: 9),
          Text(
            body,
            maxLines: 3,
            overflow: TextOverflow.ellipsis,
            style: profile.typography.micro.copyWith(
              color: const Color(0xFF9A9A9A),
              fontSize: 10.6,
              height: 1.52,
            ),
          ),
          if (section.chips.isNotEmpty) ...[
            const SizedBox(height: 8),
            Wrap(
              spacing: 5,
              runSpacing: 5,
              children: [
                for (final chip in section.chips.take(4))
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 5,
                    ),
                    decoration: BoxDecoration(
                      color: const Color(0xFFF5F5F8),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(
                        color: const Color.fromRGBO(0, 0, 0, 0.1),
                      ),
                    ),
                    child: Text(
                      chip,
                      style: profile.typography.micro.copyWith(
                        color: const Color(0xFF666666),
                        fontSize: 9.2,
                      ),
                    ),
                  ),
              ],
            ),
          ],
        ],
      ),
    );
  }

  static (String, String) _splitLead(String text) {
    final compact = text.replaceAll(RegExp(r'\s+'), ' ').trim();
    if (compact.isEmpty) {
      return ('', '');
    }
    final punctuation = RegExp(r'[,:;.!?]');
    final punctMatch = punctuation.firstMatch(compact);
    if (punctMatch != null && punctMatch.start > 4) {
      final left = compact.substring(0, punctMatch.start).trim();
      final right = compact.substring(punctMatch.start + 1).trim();
      return (left, right);
    }
    final words = compact.split(' ');
    if (words.length < 4) {
      return (compact, '');
    }
    final take = words.length > 7 ? 4 : 3;
    return (words.take(take).join(' '), words.skip(take).join(' '));
  }
}

class _V8MetricRowData {
  const _V8MetricRowData({
    required this.eyebrow,
    required this.title,
    required this.subtitle,
    required this.statValue,
    required this.statLabel,
    this.accent = 'lime',
  });

  final String eyebrow;
  final String title;
  final String subtitle;
  final String statValue;
  final String statLabel;
  final String accent;
}

Color _v8StatColor(String accent) {
  switch (accent.trim().toLowerCase()) {
    case 'lavender':
      return const Color(0xFF9B8FFF);
    case 'stone':
    case 'neutral':
      return const Color(0xFFE0DED4);
    case 'lime':
    default:
      return const Color(0xFFCAFF4D);
  }
}

class _V8TalentsStrip extends StatelessWidget {
  const _V8TalentsStrip({
    required this.talents,
    this.talentItems = const <ProfileV8Talent>[],
  });

  final List<String> talents;
  final List<ProfileV8Talent> talentItems;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final items = talentItems.isNotEmpty
        ? _fromStructured(talentItems)
        : _buildTalentItems(talents);
    if (items.isEmpty) {
      return const SizedBox.shrink();
    }

    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color.fromRGBO(0, 0, 0, 0.07)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          for (var index = 0; index < items.length; index++) ...[
            Expanded(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(10, 11, 10, 11),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      turkishToUpper(items[index].eyebrow),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: profile.typography.micro.copyWith(
                        color: const Color(0xFFAAAAAA),
                        fontSize: 7.8,
                        height: 1.2,
                        letterSpacing: 0.74,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    const SizedBox(height: 7),
                    Container(
                      width: 24,
                      height: 24,
                      decoration: BoxDecoration(
                        color: _talentTintFor(items[index].accent, index),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Icon(
                        _talentIconFor(items[index].accent, index),
                        size: 13,
                        color: const Color(0xFF111111),
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      items[index].headline,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: profile.typography.bodyCompact.copyWith(
                        color: const Color(0xFF171717),
                        fontSize: 11.2,
                        height: 1.34,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            if (index != items.length - 1)
              Container(
                width: 1,
                margin: const EdgeInsets.symmetric(vertical: 10),
                color: const Color.fromRGBO(0, 0, 0, 0.06),
              ),
          ],
        ],
      ),
    );
  }

  static List<_V8TalentItem> _buildTalentItems(List<String> source) {
    final out = <_V8TalentItem>[];
    for (final raw in source.take(3)) {
      final compact = raw.replaceAll(RegExp(r'\s+'), ' ').trim();
      if (compact.isEmpty) {
        continue;
      }
      if (_looksLikeAstroPlacement(compact)) {
        continue;
      }
      final parts = compact.split(':');
      final eyebrow = parts.length > 1 ? parts.first.trim() : 'YETENEK';
      final headline = parts.length > 1
          ? parts.sublist(1).join(':').trim()
          : compact;
      out.add(
        _V8TalentItem(
          eyebrow: eyebrow.isEmpty ? 'YETENEK' : eyebrow,
          headline: headline.isEmpty ? compact : headline,
        ),
      );
    }
    return out.take(3).toList(growable: false);
  }

  static List<_V8TalentItem> _fromStructured(List<ProfileV8Talent> source) {
    final out = <_V8TalentItem>[];
    for (final item in source.take(3)) {
      if (!item.hasContent) {
        continue;
      }
      out.add(
        _V8TalentItem(
          eyebrow: item.eyebrow.trim().isEmpty ? 'YETENEK' : item.eyebrow,
          headline: item.headline,
          accent: item.accent,
        ),
      );
    }
    return List<_V8TalentItem>.unmodifiable(out);
  }

  static IconData _talentIconFor(String? accent, int index) {
    switch ((accent ?? '').trim().toLowerCase()) {
      case 'lime':
        return Icons.auto_awesome_rounded;
      case 'lavender':
        return Icons.graphic_eq_rounded;
      case 'stone':
      case 'neutral':
        return Icons.adjust_rounded;
      default:
        return _talentIcon(index);
    }
  }

  static Color _talentTintFor(String? accent, int index) {
    switch ((accent ?? '').trim().toLowerCase()) {
      case 'lime':
        return const Color(0xFFD2F2A0);
      case 'lavender':
        return const Color(0xFFDDD8FC);
      case 'stone':
      case 'neutral':
        return const Color(0xFFF0F0F3);
      default:
        return _talentTint(index);
    }
  }

  static IconData _talentIcon(int index) {
    switch (index) {
      case 0:
        return Icons.auto_awesome_rounded;
      case 1:
        return Icons.graphic_eq_rounded;
      default:
        return Icons.adjust_rounded;
    }
  }

  static Color _talentTint(int index) {
    switch (index) {
      case 0:
        return const Color(0xFFD2F2A0);
      case 1:
        return const Color(0xFFDDD8FC);
      default:
        return const Color(0xFFF0F0F3);
    }
  }

  static bool _looksLikeAstroPlacement(String value) {
    final lower = value.toLowerCase();
    return RegExp(
          r'\b(güneş|ay|merkür|venüs|mars|jüpiter|satürn|uranüs|neptün|plüton|sun|moon|mercury|venus|mars|jupiter|saturn|uranus|neptune|pluto)\b',
        ).hasMatch(lower) &&
        RegExp(r'\b\d{1,2}\.?\s*ev\b').hasMatch(lower);
  }
}

class _V8TalentItem {
  const _V8TalentItem({
    required this.eyebrow,
    required this.headline,
    this.accent,
  });

  final String eyebrow;
  final String headline;
  final String? accent;
}

class _V8ConversationCard extends StatelessWidget {
  const _V8ConversationCard({required this.section});

  final ProfileV8TextSection section;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final headline = section.headline.trim().isEmpty
        ? 'Fikir alışverişi, derin konular, uzun vadeli planlar.'
        : section.headline.trim();
    final body = section.body.trim().isEmpty
        ? 'Yüzeysel sohbet kısa sürer; birlikte düşünmek bağı açar.'
        : section.body.trim();
    final callout = (section.callout ?? '').trim().isEmpty
        ? '“Projeler, fikirler, ne inşa ediyorsun?”'
        : (section.callout ?? '').trim();
    final split = _splitForHighlight(headline);

    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color.fromRGBO(0, 0, 0, 0.07)),
      ),
      padding: const EdgeInsets.fromLTRB(14, 13, 14, 13),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Container(
                  height: 1,
                  color: const Color.fromRGBO(0, 0, 0, 0.07),
                ),
              ),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 8),
                child: Text(
                  turkishToUpper(
                    section.eyebrow.trim().isEmpty
                        ? 'BU KİŞİYLE NE KONUŞULUR'
                        : section.eyebrow,
                  ),
                  style: profile.typography.micro.copyWith(
                    color: const Color(0xFFBBBBBB),
                    fontSize: 8,
                    letterSpacing: 0.8,
                    fontWeight: FontWeight.w400,
                  ),
                ),
              ),
              Expanded(
                child: Container(
                  height: 1,
                  color: const Color.fromRGBO(0, 0, 0, 0.07),
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          if (split.$1.trim().isNotEmpty)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 3),
              decoration: BoxDecoration(
                color: const Color(0xFFCAFF4D),
                borderRadius: BorderRadius.circular(3),
              ),
              child: Text(
                split.$1.trim(),
                style: profile.typography.bodyCompact.copyWith(
                  color: const Color(0xFF1A3300),
                  fontSize: 15.2,
                  height: 1.33,
                  letterSpacing: -0.28,
                  fontWeight: FontWeight.w400,
                ),
              ),
            ),
          if (split.$2.trim().isNotEmpty) ...[
            const SizedBox(height: 4),
            Text(
              split.$2.trim(),
              style: profile.typography.section.copyWith(
                color: const Color(0xFF111111),
                fontSize: 16.2,
                height: 1.33,
                letterSpacing: -0.28,
                fontWeight: FontWeight.w400,
              ),
            ),
          ],
          const SizedBox(height: 8),
          Text(
            body,
            maxLines: 3,
            overflow: TextOverflow.ellipsis,
            style: profile.typography.micro.copyWith(
              color: const Color(0xFF8F8F8F),
              fontSize: 10.5,
              height: 1.5,
            ),
          ),
          const SizedBox(height: 10),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.fromLTRB(13, 10, 13, 10),
            decoration: BoxDecoration(
              color: const Color(0xFFFAFAFA),
              borderRadius: BorderRadius.circular(11),
              border: Border.all(color: const Color.fromRGBO(0, 0, 0, 0.06)),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                Expanded(
                  child: Text(
                    callout,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: profile.typography.micro.copyWith(
                      color: const Color(0xFF888888),
                      fontSize: 10.5,
                      height: 1.4,
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                Text(
                  '↗',
                  style: profile.typography.micro.copyWith(
                    color: const Color(0xFFCCCCCC),
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _V8AffectsCard extends StatelessWidget {
  const _V8AffectsCard({required this.section});

  final ProfileV8TextSection section;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final rows = section.bullets
        .where((item) => item.trim().isNotEmpty)
        .take(3)
        .toList(growable: false);
    final headline = section.headline.trim().isEmpty
        ? 'Başta mesafeli, yakında çok daha derin.'
        : section.headline.trim();
    final body = section.body.trim().isEmpty
        ? 'Güven kurulduğunda etki hızla yoğunlaşır.'
        : section.body.trim();

    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color.fromRGBO(0, 0, 0, 0.07)),
      ),
      padding: const EdgeInsets.fromLTRB(14, 12, 14, 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 5,
                height: 5,
                decoration: BoxDecoration(
                  color: const Color(0xFFCAFF4D),
                  borderRadius: BorderRadius.circular(2.5),
                ),
              ),
              const SizedBox(width: 7),
              Text(
                turkishToUpper(
                  section.eyebrow.trim().isEmpty
                      ? 'SENİ NASIL ETKİLER'
                      : section.eyebrow,
                ),
                style: profile.typography.micro.copyWith(
                  color: const Color(0xFFA9A9A9),
                  fontSize: 8,
                  letterSpacing: 0.8,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            headline,
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
            style: profile.typography.section.copyWith(
              color: const Color(0xFF111111),
              fontSize: 17,
              height: 1.33,
              letterSpacing: -0.3,
              fontWeight: FontWeight.w400,
            ),
          ),
          const SizedBox(height: 6),
          Text(
            body,
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
            style: profile.typography.micro.copyWith(
              color: const Color(0xFF898989),
              fontSize: 10.5,
              height: 1.48,
            ),
          ),
          if (rows.isNotEmpty) ...[
            const SizedBox(height: 10),
            Container(
              decoration: BoxDecoration(
                color: const Color(0xFFFAFAFC),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(
                  color: const Color.fromRGBO(0, 0, 0, 0.055),
                ),
              ),
              child: Column(
                children: [
                  for (var i = 0; i < rows.length; i++) ...[
                    Padding(
                      padding: const EdgeInsets.fromLTRB(10, 9, 10, 9),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Container(
                            width: 7,
                            height: 7,
                            margin: const EdgeInsets.only(top: 4),
                            decoration: BoxDecoration(
                              color: _v8AffectsDotColor(i),
                              borderRadius: BorderRadius.circular(3.5),
                            ),
                          ),
                          const SizedBox(width: 9),
                          Expanded(
                            child: Text(
                              rows[i],
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                              style: profile.typography.bodyCompact.copyWith(
                                color: _v8AffectsTextColor(i),
                                fontSize: 10.3,
                                height: 1.4,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                    if (i != rows.length - 1)
                      Container(
                        height: 1,
                        color: const Color.fromRGBO(0, 0, 0, 0.05),
                      ),
                  ],
                ],
              ),
            ),
          ],
          if ((section.footer ?? '').trim().isNotEmpty) ...[
            const SizedBox(height: 8),
            Text(
              (section.footer ?? '').trim(),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: profile.typography.micro.copyWith(
                color: const Color(0xFFB2B2B2),
                fontSize: 8.9,
              ),
            ),
          ],
        ],
      ),
    );
  }
}

Color _v8AffectsDotColor(int index) {
  switch (index) {
    case 0:
      return const Color(0xFF7F77DD);
    case 1:
      return const Color(0xFFCAFF4D);
    default:
      return const Color(0xFFDDDDDD);
  }
}

Color _v8AffectsTextColor(int index) {
  if (index >= 2) {
    return const Color(0xFFAAAAAA);
  }
  return const Color(0xFF444444);
}

class _V8DefenseCard extends StatelessWidget {
  const _V8DefenseCard({required this.section});

  final ProfileV8TextSection section;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final split = _splitForHighlight(section.headline);
    final showHighlight =
        split.$1.trim().isNotEmpty && split.$2.trim().isNotEmpty;
    final headlineMain = split.$2.trim().isEmpty
        ? (section.headline.trim().isEmpty
              ? 'Sevilmek için önce güçlü tarafını gösterirsin.'
              : section.headline.trim())
        : split.$2.trim();
    final normalizedBody = section.body.trim();
    final body = normalizedBody.isEmpty
        ? 'Bu bir zırh değil, temkinli bir ritim. Güvenle birlikte yumuşar.'
        : _dedupeBody(normalizedBody, headlineMain);

    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color.fromRGBO(0, 0, 0, 0.07)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 2.5,
            margin: const EdgeInsets.symmetric(vertical: 12),
            decoration: const BoxDecoration(color: Color(0xFF7F77DD)),
          ),
          Expanded(
            child: Padding(
              padding: const EdgeInsets.fromLTRB(12, 14, 14, 14),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        width: 5,
                        height: 5,
                        decoration: const BoxDecoration(
                          color: Color(0xFF7F77DD),
                          shape: BoxShape.circle,
                        ),
                      ),
                      const SizedBox(width: 8),
                      Text(
                        turkishToUpper(
                          section.eyebrow.trim().isEmpty
                              ? 'SAVUNMA MEKANİZMAN'
                              : section.eyebrow,
                        ),
                        style: profile.typography.micro.copyWith(
                          color: const Color(0xFFBBBBBB),
                          fontSize: 8,
                          letterSpacing: 0.8,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 10),
                  if (showHighlight)
                    Container(
                      margin: const EdgeInsets.only(bottom: 4),
                      padding: const EdgeInsets.symmetric(
                        horizontal: 6,
                        vertical: 2,
                      ),
                      decoration: BoxDecoration(
                        color: const Color(0xFFDDD8FC),
                        borderRadius: BorderRadius.circular(3),
                      ),
                      child: Text(
                        split.$1.trim(),
                        style: profile.typography.bodyCompact.copyWith(
                          color: const Color(0xFF26215C),
                          fontSize: 15.2,
                          height: 1.33,
                          letterSpacing: -0.28,
                          fontWeight: FontWeight.w400,
                        ),
                      ),
                    ),
                  Text(
                    headlineMain,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: profile.typography.section.copyWith(
                      color: const Color(0xFF111111),
                      fontSize: 16,
                      height: 1.375,
                      letterSpacing: -0.3,
                      fontWeight: FontWeight.w400,
                    ),
                  ),
                  if (body.trim().isNotEmpty) ...[
                    const SizedBox(height: 8),
                    Text(
                      body,
                      maxLines: 3,
                      overflow: TextOverflow.ellipsis,
                      style: profile.typography.micro.copyWith(
                        color: const Color(0xFF888888),
                        fontSize: 10.8,
                        height: 1.66,
                      ),
                    ),
                  ],
                  if (section.chips.isNotEmpty) ...[
                    const SizedBox(height: 10),
                    Wrap(
                      spacing: 5,
                      runSpacing: 5,
                      children: [
                        for (final chip in section.chips.take(4))
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 9,
                              vertical: 4,
                            ),
                            decoration: BoxDecoration(
                              color: Colors.transparent,
                              borderRadius: BorderRadius.circular(20),
                              border: Border.all(
                                color: const Color.fromRGBO(127, 119, 221, 0.2),
                              ),
                            ),
                            child: Text(
                              chip,
                              style: profile.typography.micro.copyWith(
                                color: const Color(0xFF7F77DD),
                                fontSize: 9.5,
                              ),
                            ),
                          ),
                      ],
                    ),
                  ],
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _V8FirstFeltCard extends StatelessWidget {
  const _V8FirstFeltCard({required this.section});

  final ProfileV8TextSection section;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final rawHeadline = _looksLikeAstroPlacement(section.headline)
        ? ''
        : section.headline.trim();
    final split = _splitForHighlight(rawHeadline);
    final title = rawHeadline.isEmpty
        ? 'İlk anda sakin, kısa sürede güçlü bir iz bırakırsın.'
        : rawHeadline;
    final body = section.body.trim().isEmpty
        ? 'İnsanlar sende önce duruşu, sonra ritmi ve derinliği algılar.'
        : section.body.trim();

    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color.fromRGBO(0, 0, 0, 0.07)),
      ),
      padding: const EdgeInsets.fromLTRB(14, 13, 14, 13),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Container(
                  height: 1,
                  color: const Color.fromRGBO(0, 0, 0, 0.07),
                ),
              ),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 8),
                child: Text(
                  turkishToUpper(
                    section.eyebrow.trim().isEmpty
                        ? 'İLK HİSSEDİLEN ŞEY'
                        : section.eyebrow,
                  ),
                  style: profile.typography.micro.copyWith(
                    color: const Color(0xFFB6B6B6),
                    fontSize: 8,
                    letterSpacing: 0.8,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
              Expanded(
                child: Container(
                  height: 1,
                  color: const Color.fromRGBO(0, 0, 0, 0.07),
                ),
              ),
            ],
          ),
          const SizedBox(height: 9),
          if (split.$1.trim().isNotEmpty)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 3),
              decoration: BoxDecoration(
                color: const Color(0xFFEFF8D7),
                borderRadius: BorderRadius.circular(4),
              ),
              child: Text(
                split.$1.trim(),
                style: profile.typography.bodyCompact.copyWith(
                  color: const Color(0xFF30430A),
                  fontSize: 13.6,
                  height: 1.33,
                ),
              ),
            ),
          const SizedBox(height: 4),
          Text(
            split.$2.trim().isEmpty ? title : split.$2.trim(),
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
            style: profile.typography.section.copyWith(
              color: const Color(0xFF111111),
              fontSize: 17,
              height: 1.33,
              letterSpacing: -0.28,
              fontWeight: FontWeight.w400,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            body,
            maxLines: 3,
            overflow: TextOverflow.ellipsis,
            style: profile.typography.micro.copyWith(
              color: const Color(0xFF8D8D8D),
              fontSize: 10.4,
              height: 1.5,
            ),
          ),
          if (section.chips.isNotEmpty) ...[
            const SizedBox(height: 8),
            Wrap(
              spacing: 5,
              runSpacing: 5,
              children: [
                for (final chip in section.chips.take(4))
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: const Color(0xFFF5F5F8),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(
                        color: const Color.fromRGBO(0, 0, 0, 0.08),
                      ),
                    ),
                    child: Text(
                      chip,
                      style: profile.typography.micro.copyWith(
                        color: const Color(0xFF616161),
                        fontSize: 8.8,
                      ),
                    ),
                  ),
              ],
            ),
          ],
        ],
      ),
    );
  }
}

(String, String) _splitForHighlight(String raw) {
  final compact = raw.replaceAll(RegExp(r'\s+'), ' ').trim();
  if (compact.isEmpty) {
    return ('', '');
  }
  final punctuation = RegExp(r'[,:;!?]');
  final punctMatch = punctuation.firstMatch(compact);
  if (punctMatch != null && punctMatch.start > 3) {
    final left = compact.substring(0, punctMatch.start).trim();
    final right = compact.substring(punctMatch.start + 1).trim();
    return (left, right);
  }
  final words = compact.split(' ');
  if (words.length < 4) {
    return (compact, '');
  }
  final take = words.length > 7 ? 4 : 3;
  return (words.take(take).join(' '), words.skip(take).join(' '));
}

class _V8SectionCard extends StatelessWidget {
  const _V8SectionCard({
    required this.section,
    required this.dark,
    required this.subtle,
    required this.leftAccent,
    this.accent,
    this.accentTextColor,
  });

  final ProfileV8TextSection section;
  final bool dark;
  final bool subtle;
  final bool leftAccent;
  final Color? accent;
  final Color? accentTextColor;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final isDarkTheme = Theme.of(context).brightness == Brightness.dark;

    final background = dark
        ? const Color(0xFF121212)
        : subtle
        ? (isDarkTheme ? const Color(0xFF1A1A1A) : const Color(0xFFF5F8F2))
        : (isDarkTheme ? const Color(0xFF191919) : Colors.white);

    final borderColor = dark
        ? Colors.white.withValues(alpha: 0.08)
        : isDarkTheme
        ? Colors.white.withValues(alpha: 0.12)
        : Colors.black.withValues(alpha: 0.06);

    final textColor = dark || isDarkTheme
        ? Colors.white
        : const Color(0xFF111111);
    final softText = dark || isDarkTheme
        ? Colors.white.withValues(alpha: 0.74)
        : const Color(0xFF5C5C5C);

    final eyebrowColor = accent != null && !dark && !isDarkTheme
        ? (accentTextColor ?? accent!)
        : (dark
              ? const Color(0xFFCAFF4D)
              : (isDarkTheme
                    ? Colors.white.withValues(alpha: 0.66)
                    : const Color(0xFF8A8A8A)));

    final card = Container(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 16),
      decoration: BoxDecoration(
        color: background,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: borderColor),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            turkishToUpper(section.eyebrow),
            style: profile.typography.micro.copyWith(
              color: eyebrowColor,
              fontWeight: FontWeight.w500,
              letterSpacing: 0.8,
            ),
          ),
          if (section.headline.trim().isNotEmpty) ...[
            const SizedBox(height: 8),
            Text(
              section.headline.trim(),
              style: profile.typography.section.copyWith(
                color: textColor,
                fontSize: 16.5,
                height: 1.35,
                letterSpacing: -0.2,
              ),
            ),
          ],
          if (section.body.trim().isNotEmpty) ...[
            const SizedBox(height: 10),
            Text(
              section.body.trim(),
              style: profile.typography.bodyReading.copyWith(
                color: softText,
                height: 1.55,
              ),
            ),
          ],
          if (section.bullets.isNotEmpty) ...[
            const SizedBox(height: 12),
            for (final bullet in section.bullets.take(5)) ...[
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    width: 5,
                    height: 5,
                    margin: const EdgeInsets.only(top: 8),
                    decoration: BoxDecoration(
                      color: dark
                          ? const Color(0xFFCAFF4D)
                          : (isDarkTheme
                                ? Colors.white.withValues(alpha: 0.64)
                                : const Color(0xFF111111)),
                      shape: BoxShape.circle,
                    ),
                  ),
                  const SizedBox(width: 9),
                  Expanded(
                    child: Text(
                      bullet,
                      style: profile.typography.bodyCompact.copyWith(
                        color: softText,
                        height: 1.5,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
            ],
          ],
          if (section.chips.isNotEmpty) ...[
            const SizedBox(height: 6),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                for (final chip in section.chips.take(4))
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 10,
                      vertical: 6,
                    ),
                    decoration: BoxDecoration(
                      color: dark
                          ? Colors.white.withValues(alpha: 0.08)
                          : (isDarkTheme
                                ? Colors.white.withValues(alpha: 0.1)
                                : const Color(0xFFF6F6F6)),
                      borderRadius: BorderRadius.circular(999),
                      border: Border.all(color: borderColor),
                    ),
                    child: Text(
                      chip,
                      style: profile.typography.micro.copyWith(
                        color: textColor,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
              ],
            ),
          ],
          if ((section.callout ?? '').trim().isNotEmpty) ...[
            const SizedBox(height: 12),
            Text(
              (section.callout ?? '').trim(),
              style: profile.typography.bodyCompact.copyWith(
                color: softText,
                fontStyle: FontStyle.italic,
              ),
            ),
          ],
          if ((section.footer ?? '').trim().isNotEmpty) ...[
            const SizedBox(height: 12),
            Text(
              (section.footer ?? '').trim(),
              style: profile.typography.meta.copyWith(color: softText),
            ),
          ],
          if ((section.cta ?? '').trim().isNotEmpty) ...[
            const SizedBox(height: 12),
            Text(
              (section.cta ?? '').trim(),
              style: profile.typography.buttonLabel.copyWith(
                color: dark
                    ? const Color(0xFFCAFF4D)
                    : (isDarkTheme ? Colors.white : const Color(0xFF111111)),
              ),
            ),
          ],
        ],
      ),
    );

    if (accent != null && !dark && !isDarkTheme) {
      return Container(
        clipBehavior: Clip.antiAlias,
        decoration: BoxDecoration(
          color: background,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: borderColor),
        ),
        child: Stack(
          children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(18.5, 16, 16, 16),
              child: card.child!,
            ),
            Positioned(
              left: 0,
              top: 0,
              bottom: 0,
              width: 2.5,
              child: Container(color: accent),
            ),
          ],
        ),
      );
    }

    if (!leftAccent) {
      return card;
    }

    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          width: 4,
          decoration: BoxDecoration(
            color: const Color(0xFFCAFF4D),
            borderRadius: BorderRadius.circular(999),
          ),
        ),
        const SizedBox(width: 10),
        Expanded(child: card),
      ],
    );
  }
}

class _V8LimeCta extends StatelessWidget {
  const _V8LimeCta({required this.section, this.onTap});

  final ProfileV8TextSection section;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final eyebrow = section.eyebrow.trim().isEmpty
        ? 'ARKETİP PORTALI'
        : section.eyebrow;
    final headline = section.headline.trim().isEmpty
        ? 'Seni yöneten eksenleri birlikte gör.'
        : section.headline.trim();
    final body = section.body.trim().isEmpty
        ? 'Aktif kimlik, koruma ve gerilim çizgilerini tek akışta aç.'
        : section.body.trim();
    final cta = (section.cta ?? '').trim().isEmpty
        ? 'Akışı aç'
        : (section.cta ?? '').trim();

    final chipLine = section.chips
        .where((item) => item.trim().isNotEmpty)
        .take(4)
        .map((item) => item.trim())
        .join(' · ');

    final content = Container(
      padding: const EdgeInsets.fromLTRB(20, 18, 14, 18),
      decoration: const BoxDecoration(color: Color(0xFFCAFF4D)),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  turkishToUpper(eyebrow),
                  style: profile.typography.micro.copyWith(
                    color: const Color(0xFF3B6D11),
                    fontSize: 8,
                    letterSpacing: 0.8,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  headline,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: profile.typography.section.copyWith(
                    color: const Color(0xFF1A3300),
                    fontSize: 15.9,
                    height: 1.34,
                    letterSpacing: -0.25,
                    fontWeight: FontWeight.w400,
                  ),
                ),
                if (chipLine.isNotEmpty) ...[
                  const SizedBox(height: 4),
                  Text(
                    chipLine,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: profile.typography.micro.copyWith(
                      color: const Color(0xFF3B6D11),
                      fontSize: 10,
                      height: 1.4,
                    ),
                  ),
                ] else if (body.isNotEmpty) ...[
                  const SizedBox(height: 4),
                  Text(
                    body,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: profile.typography.micro.copyWith(
                      color: const Color(0xFF3B6D11),
                      fontSize: 10,
                      height: 1.42,
                    ),
                  ),
                ],
              ],
            ),
          ),
          const SizedBox(width: 10),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 15, vertical: 10),
            decoration: BoxDecoration(
              color: const Color(0xFF111111),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Text(
              cta,
              style: profile.typography.micro.copyWith(
                color: const Color(0xFFCAFF4D),
                fontSize: 11.8,
                letterSpacing: 0.2,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
        ],
      ),
    );

    if (onTap == null) {
      return content;
    }

    return Material(
      color: Colors.transparent,
      child: InkWell(onTap: onTap, child: content),
    );
  }
}

bool _hasEditorialContent(ProfileV8TextSection? section) {
  if (section == null || !section.hasContent) {
    return false;
  }
  final headline = section.headline.trim();
  final body = section.body.trim();
  final hasRows = section.bullets.any((item) => item.trim().isNotEmpty);
  final hasChips = section.chips.any((item) => item.trim().isNotEmpty);
  final hasCallout = (section.callout ?? '').trim().isNotEmpty;
  return headline.isNotEmpty ||
      body.isNotEmpty ||
      hasRows ||
      hasChips ||
      hasCallout;
}

String _dedupeBody(String body, String headline) {
  final normalizedBody = body.replaceAll(RegExp(r'\s+'), ' ').trim();
  final normalizedHeadline = headline.replaceAll(RegExp(r'\s+'), ' ').trim();
  if (normalizedBody.toLowerCase() == normalizedHeadline.toLowerCase()) {
    return '';
  }
  return normalizedBody;
}

bool _looksLikeAstroPlacement(String text) {
  final lower = text.toLowerCase().replaceAll(RegExp(r'\s+'), ' ').trim();
  if (lower.isEmpty) {
    return false;
  }
  final hasHouse = RegExp(r'\b\d{1,2}\.?\s*ev\b').hasMatch(lower);
  final hasPlanet = RegExp(
    r'\b(güneş|ay|merkür|venüs|mars|jüpiter|satürn|uranüs|neptün|plüton|sun|moon|mercury|venus|mars|jupiter|saturn|uranus|neptune|pluto)\b',
  ).hasMatch(lower);
  return hasHouse && hasPlanet;
}
