import 'package:flutter/material.dart';

import 'package:mobile/app/tabs/tabs_shell.dart';
import 'package:mobile/app/timing/narrative_dtos.dart';

class TransitDetailPage extends StatelessWidget {
  const TransitDetailPage({super.key, required this.card});

  static const Color _bgWarm = Color(0xFFFAF9F6);
  static const Color _surfaceWarm = Color(0xFFFFFDF9);
  static const Color _textPrimary = Color(0xFF1F2328);
  static const Color _textSecondary = Color(0xFF505761);
  static const Color _stroke = Color(0xFFE7E3DB);
  static const Color _mint = Color(0xFFB8DCC8);
  static const Color _lavender = Color(0xFFD9D1F2);
  final EventCardDto card;

  @override
  Widget build(BuildContext context) {
    final periodStory = card.periodStory;
    final hasPeriodStory =
        card.horizon.trim().toLowerCase() == 'period' &&
        periodStory != null &&
        periodStory.hasContent;
    final headline = _cleanUiLine(card.title).isNotEmpty
        ? _cleanUiLine(card.title)
        : 'Transit Etkisi';

    final periodLead = _cleanUiLine(periodStory?.lead ?? '').trim();
    final periodBigPicture = _cleanUiLine(periodStory?.bigPicture ?? '').trim();
    final rawEssenceSource = periodLead.isNotEmpty
        ? periodLead
        : periodBigPicture.isNotEmpty
        ? periodBigPicture
        : card.teaser.trim().isNotEmpty
        ? card.teaser.trim()
        : card.whyNow.trim().isNotEmpty
        ? card.whyNow.trim()
        : card.upper.trim().isNotEmpty
        ? card.upper.trim()
        : card.conflict.trim();
    final essence = _cleanUiLine(rawEssenceSource);

    final mainBody = card.upper.trim().isNotEmpty
        ? card.upper.trim()
        : card.conflict.trim().isNotEmpty
        ? card.conflict.trim()
        : card.shadow.trim();
    final mainBodyClean = _cleanUiLine(mainBody);
    final conflictBody = _cleanUiLine(card.conflict);
    final shadowBody = _cleanUiLine(card.shadow);
    final upperBody = _cleanUiLine(card.upper);

    final displaySignature = card.signatureTr.trim().isNotEmpty
        ? card.signatureTr
        : _localizeSignature(card.signature);
    final capsuleMeta = _buildCapsuleMeta(card);
    final technicalRows = _buildTechnicalRows(card, displaySignature);

    final kept = <String>[];
    final showMain =
        !hasPeriodStory &&
        mainBodyClean.isNotEmpty &&
        !_isNearDuplicate(mainBodyClean, kept);
    if (showMain) {
      kept.add(mainBodyClean);
    }
    final showConflict =
        conflictBody.isNotEmpty && !_isNearDuplicate(conflictBody, kept);
    if (showConflict) {
      kept.add(conflictBody);
    }
    final showShadow =
        shadowBody.isNotEmpty && !_isNearDuplicate(shadowBody, kept);
    if (showShadow) {
      kept.add(shadowBody);
    }
    final showUpper =
        upperBody.isNotEmpty && !_isNearDuplicate(upperBody, kept);
    if (showUpper) {
      kept.add(upperBody);
    }

    return Scaffold(
      backgroundColor: _bgWarm,
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(20, 12, 20, 28),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  IconButton(
                    icon: const Icon(Icons.arrow_back_rounded),
                    onPressed: () async => _handleBack(context),
                  ),
                  const Expanded(
                    child: Text(
                      'Transit Detayi',
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        fontSize: 13,
                        letterSpacing: 0.4,
                        fontWeight: FontWeight.w600,
                        color: _textSecondary,
                      ),
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.info_outline_rounded),
                    onPressed: () =>
                        _showTechnicalSheet(context, technicalRows),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              _DetailHero(
                headline: headline,
                essence: essence,
                signature: displaySignature,
                capsuleMeta: capsuleMeta,
              ),
              const SizedBox(height: 22),
              if (hasPeriodStory) ...[
                _SectionBlock(
                  icon: Icons.explore_outlined,
                  title: 'Büyük Resim',
                  body: _cleanUiLine(periodStory.bigPicture),
                ),
                const Padding(
                  padding: EdgeInsets.symmetric(vertical: 12),
                  child: _WaveDivider(),
                ),
                _SectionBlock(
                  icon: Icons.settings_suggest_outlined,
                  title: 'Nasil Calisiyor',
                  body: _cleanUiLine(periodStory.mechanism),
                ),
                const Padding(
                  padding: EdgeInsets.symmetric(vertical: 12),
                  child: _WaveDivider(),
                ),
                _SectionBlock(
                  icon: Icons.workspace_premium_outlined,
                  title: 'Bu Donemin Sana Katkisi',
                  body: _cleanUiLine(
                    periodStory.contribution.trim().isNotEmpty
                        ? periodStory.contribution
                        : periodStory.upperMeaning,
                  ),
                ),
                const SizedBox(height: 14),
              ],
              if (showMain)
                Text(
                  mainBodyClean,
                  style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                    fontSize: 15.8,
                    height: 1.55,
                    color: _textPrimary,
                  ),
                ),
              if (showConflict) ...[
                const SizedBox(height: 20),
                _SectionBlock(
                  icon: Icons.change_history_rounded,
                  title: card.sectionLabels['conflict'] ?? 'Sürtünme',
                  body: conflictBody,
                ),
              ],
              if (showConflict && (showShadow || showUpper))
                const Padding(
                  padding: EdgeInsets.symmetric(vertical: 12),
                  child: _WaveDivider(),
                ),
              if (showShadow) ...[
                _SectionBlock(
                  icon: Icons.psychology_alt_outlined,
                  title: card.sectionLabels['shadow'] ?? 'Refleks',
                  body: shadowBody,
                ),
              ],
              if (showShadow && showUpper)
                const Padding(
                  padding: EdgeInsets.symmetric(vertical: 12),
                  child: _WaveDivider(),
                ),
              if (showUpper) ...[
                _SectionBlock(
                  icon: Icons.auto_awesome_outlined,
                  title: card.sectionLabels['upper'] ?? 'Ustalık / Potansiyel',
                  body: upperBody,
                ),
              ],
              if (card.guidance.isNotEmpty || card.watchOut.isNotEmpty) ...[
                const SizedBox(height: 14),
                _GuidanceCard(guidance: card.guidance, watchOut: card.watchOut),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _handleBack(BuildContext context) async {
    final popped = await Navigator.of(context).maybePop();
    if (popped) {
      return;
    }
    if (!context.mounted) {
      return;
    }
    final root = Navigator.of(context, rootNavigator: true);
    if (root.canPop()) {
      root.pop();
      return;
    }
    root.pushAndRemoveUntil(
      MaterialPageRoute<void>(builder: (_) => const TabsShell()),
      (_) => false,
    );
  }

  String _buildCapsuleMeta(EventCardDto card) {
    final house = _readHouse(
      card.scene['start_house'] ??
          (card.derivedContext['natal_target'] is Map
              ? (card.derivedContext['natal_target'] as Map)['house']
              : null),
    );
    final phase = _cleanUiLine(card.tags.phase);
    final houseText = house != null ? '$house.ev' : '';
    if (houseText.isEmpty && phase.isEmpty) {
      return '';
    }
    if (houseText.isEmpty) {
      return phase;
    }
    if (phase.isEmpty) {
      return houseText;
    }
    return '$houseText • $phase';
  }

  List<_TechRow> _buildTechnicalRows(EventCardDto card, String signature) {
    final rows = <_TechRow>[];

    void add(String label, String value) {
      final clean = value.trim();
      if (clean.isEmpty) {
        return;
      }
      rows.add(_TechRow(label: label, value: clean));
    }

    final parsed = _parseSignatureParts(
      signature.isNotEmpty ? signature : card.signature,
    );
    add('Transit body', parsed.body);
    add('Aspect', parsed.aspect);
    add('Natal point', parsed.point);

    add('Orb', _readMapValue(card, const ['orb_deg', 'orb']));
    add('Phase', card.tags.phase);
    add('Duration/Bucket', card.tags.duration);

    final startHouse = _readHouse(
      card.scene['start_house'] ?? _readMapObject(card, const ['start_house']),
    );
    final outcomeHouse = _readHouse(
      card.scene['outcome_house'] ??
          card.scene['end_house'] ??
          _readMapObject(card, const ['outcome_house', 'end_house']),
    );
    if (startHouse != null || outcomeHouse != null) {
      final houseText = [
        if (startHouse != null) 'baslangic $startHouse.ev',
        if (outcomeHouse != null) 'sonuc $outcomeHouse.ev',
      ].join(' • ');
      add('Houses', houseText);
    }

    return rows;
  }

  String _readMapValue(EventCardDto card, List<String> keys) {
    final value = _readMapObject(card, keys);
    if (value == null) {
      return '';
    }
    return value.toString();
  }

  Object? _readMapObject(EventCardDto card, List<String> keys) {
    for (final key in keys) {
      if (card.derivedContext.containsKey(key) &&
          card.derivedContext[key] != null) {
        return card.derivedContext[key];
      }
      if (card.scene.containsKey(key) && card.scene[key] != null) {
        return card.scene[key];
      }
    }
    return null;
  }

  void _showTechnicalSheet(BuildContext context, List<_TechRow> rows) {
    showModalBottomSheet<void>(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (_) {
        return SafeArea(
          child: Container(
            margin: const EdgeInsets.fromLTRB(12, 0, 12, 12),
            padding: const EdgeInsets.fromLTRB(18, 16, 18, 18),
            decoration: BoxDecoration(
              color: _surfaceWarm,
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: _stroke),
            ),
            child: rows.isEmpty
                ? const Text(
                    'Teknik detay bulunamadi.',
                    style: TextStyle(color: _textSecondary),
                  )
                : Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Teknik Detaylar',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w700,
                          color: _textPrimary,
                        ),
                      ),
                      const SizedBox(height: 10),
                      for (final row in rows) ...[
                        Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            SizedBox(
                              width: 118,
                              child: Text(
                                row.label,
                                style: const TextStyle(
                                  fontSize: 13,
                                  fontWeight: FontWeight.w600,
                                  color: _textSecondary,
                                ),
                              ),
                            ),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                row.value,
                                style: const TextStyle(
                                  fontSize: 13.5,
                                  color: _textPrimary,
                                  height: 1.35,
                                ),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                      ],
                    ],
                  ),
          ),
        );
      },
    );
  }
}

class _DetailHero extends StatelessWidget {
  const _DetailHero({
    required this.headline,
    required this.essence,
    required this.signature,
    required this.capsuleMeta,
  });

  final String headline;
  final String essence;
  final String signature;
  final String capsuleMeta;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final placeBadgeBelow =
            constraints.maxWidth < 365 || headline.characters.length > 30;
        return Padding(
          padding: const EdgeInsets.symmetric(vertical: 4),
          child: Stack(
            children: [
              Positioned(
                right: 2,
                top: 2,
                child: Container(
                  width: 66,
                  height: 66,
                  decoration: BoxDecoration(
                    color: TransitDetailPage._lavender.withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(33),
                  ),
                ),
              ),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (!placeBadgeBelow)
                    Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Expanded(
                          child: Text(
                            headline,
                            style: Theme.of(context).textTheme.headlineMedium
                                ?.copyWith(
                                  fontSize: 28,
                                  fontWeight: FontWeight.w700,
                                  color: TransitDetailPage._textPrimary,
                                  height: 1.18,
                                ),
                          ),
                        ),
                        const SizedBox(width: 12),
                        _CapsuleBadge(signature: signature, meta: capsuleMeta),
                      ],
                    )
                  else ...[
                    Text(
                      headline,
                      style: Theme.of(context).textTheme.headlineMedium
                          ?.copyWith(
                            fontSize: 28,
                            fontWeight: FontWeight.w700,
                            color: TransitDetailPage._textPrimary,
                            height: 1.18,
                          ),
                    ),
                    const SizedBox(height: 8),
                    Align(
                      alignment: Alignment.centerRight,
                      child: _CapsuleBadge(
                        signature: signature,
                        meta: capsuleMeta,
                      ),
                    ),
                  ],
                  if (essence.trim().isNotEmpty) ...[
                    const SizedBox(height: 10),
                    _EssenceText(text: essence),
                  ],
                ],
              ),
            ],
          ),
        );
      },
    );
  }
}

class _CapsuleBadge extends StatelessWidget {
  const _CapsuleBadge({required this.signature, required this.meta});

  final String signature;
  final String meta;

  @override
  Widget build(BuildContext context) {
    final display = signature.trim().isEmpty ? 'Transit' : signature.trim();
    final compactDisplay = _compactSignature(display);
    return Container(
      constraints: const BoxConstraints(maxWidth: 156),
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 7),
      decoration: BoxDecoration(
        color: TransitDetailPage._mint.withValues(alpha: 0.28),
        borderRadius: BorderRadius.circular(14),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          Text(
            compactDisplay,
            maxLines: 2,
            textAlign: TextAlign.right,
            style: const TextStyle(
              fontSize: 12.5,
              fontWeight: FontWeight.w600,
              color: TransitDetailPage._textPrimary,
              height: 1.2,
            ),
          ),
          if (meta.trim().isNotEmpty)
            Text(
              meta,
              maxLines: 2,
              textAlign: TextAlign.right,
              style: const TextStyle(
                fontSize: 11.5,
                color: TransitDetailPage._textSecondary,
                height: 1.2,
              ),
            ),
        ],
      ),
    );
  }
}

class _SectionBlock extends StatelessWidget {
  const _SectionBlock({
    required this.icon,
    required this.title,
    required this.body,
  });

  final IconData icon;
  final String title;
  final String body;

  @override
  Widget build(BuildContext context) {
    if (body.trim().isEmpty) {
      return const SizedBox.shrink();
    }
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(icon, size: 16, color: TransitDetailPage._textSecondary),
            const SizedBox(width: 8),
            Expanded(
              child: Text(
                title,
                style: const TextStyle(
                  fontSize: 17,
                  fontWeight: FontWeight.w700,
                  color: TransitDetailPage._textPrimary,
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Text(
          body.trim(),
          style: const TextStyle(
            fontSize: 15.5,
            height: 1.55,
            color: TransitDetailPage._textPrimary,
          ),
        ),
      ],
    );
  }
}

class _GuidanceCard extends StatelessWidget {
  const _GuidanceCard({required this.guidance, required this.watchOut});

  final List<String> guidance;
  final List<String> watchOut;

  @override
  Widget build(BuildContext context) {
    final doItems = _normalizeLines(guidance).take(3).toList(growable: false);
    final avoidItems = _normalizeLines(
      watchOut,
    ).take(3).toList(growable: false);
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: TransitDetailPage._mint.withValues(alpha: 0.22),
        borderRadius: BorderRadius.circular(18),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(
                Icons.track_changes_rounded,
                size: 16,
                color: TransitDetailPage._textSecondary,
              ),
              SizedBox(width: 6),
              Text(
                'Net Adım',
                style: TextStyle(
                  fontSize: 17,
                  fontWeight: FontWeight.w600,
                  color: TransitDetailPage._textPrimary,
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          _ListBlock(title: 'Yap', icon: Icons.check_circle, items: doItems),
          const SizedBox(height: 10),
          _ListBlock(
            title: 'Kaçın',
            icon: Icons.remove_circle_outline,
            items: avoidItems,
          ),
        ],
      ),
    );
  }
}

class _EssenceText extends StatefulWidget {
  const _EssenceText({required this.text});

  final String text;

  @override
  State<_EssenceText> createState() => _EssenceTextState();
}

class _EssenceTextState extends State<_EssenceText> {
  bool _expanded = false;

  @override
  Widget build(BuildContext context) {
    final text = widget.text.trim();
    if (text.isEmpty) {
      return const SizedBox.shrink();
    }

    final showToggle = text.length > 130;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          text,
          maxLines: showToggle && !_expanded ? 2 : null,
          overflow: showToggle && !_expanded
              ? TextOverflow.fade
              : TextOverflow.visible,
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
            fontSize: 16,
            fontWeight: FontWeight.w500,
            height: 1.45,
            color: TransitDetailPage._textSecondary,
          ),
        ),
        if (showToggle)
          Align(
            alignment: Alignment.centerLeft,
            child: TextButton(
              onPressed: () => setState(() => _expanded = !_expanded),
              style: TextButton.styleFrom(
                visualDensity: VisualDensity.compact,
                padding: const EdgeInsets.symmetric(horizontal: 0, vertical: 2),
                tapTargetSize: MaterialTapTargetSize.shrinkWrap,
              ),
              child: Text(
                _expanded ? 'Daha az' : 'Devamı',
                style: const TextStyle(
                  fontSize: 12.5,
                  fontWeight: FontWeight.w600,
                  color: TransitDetailPage._textSecondary,
                ),
              ),
            ),
          ),
      ],
    );
  }
}

class _WaveDivider extends StatelessWidget {
  const _WaveDivider();

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        return CustomPaint(
          painter: _WavePainter(),
          size: Size(constraints.maxWidth, 10),
        );
      },
    );
  }
}

class _WavePainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = TransitDetailPage._textSecondary.withValues(alpha: 0.14)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.2;
    final path = Path()
      ..moveTo(0, size.height / 2)
      ..quadraticBezierTo(
        size.width * 0.25,
        size.height * 0.1,
        size.width * 0.5,
        size.height / 2,
      )
      ..quadraticBezierTo(
        size.width * 0.75,
        size.height * 0.9,
        size.width,
        size.height / 2,
      );
    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

class _ListBlock extends StatelessWidget {
  const _ListBlock({
    required this.title,
    required this.icon,
    required this.items,
  });

  final String title;
  final IconData icon;
  final List<String> items;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(icon, size: 15, color: TransitDetailPage._textSecondary),
            const SizedBox(width: 6),
            Text(
              title,
              style: const TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w600,
                color: TransitDetailPage._textPrimary,
              ),
            ),
          ],
        ),
        const SizedBox(height: 6),
        if (items.isEmpty)
          const Text('-', style: TextStyle(fontSize: 14, color: Colors.black54))
        else
          for (final item in items) ...[
            Text(
              '• $item',
              style: const TextStyle(
                fontSize: 14.5,
                height: 1.45,
                color: TransitDetailPage._textPrimary,
              ),
            ),
            const SizedBox(height: 4),
          ],
      ],
    );
  }
}

class _TechRow {
  const _TechRow({required this.label, required this.value});

  final String label;
  final String value;
}

class _SignatureParts {
  const _SignatureParts({
    required this.body,
    required this.aspect,
    required this.point,
  });

  final String body;
  final String aspect;
  final String point;
}

_SignatureParts _parseSignatureParts(String signature) {
  final clean = signature.trim();
  if (clean.isEmpty) {
    return const _SignatureParts(body: '', aspect: '', point: '');
  }

  final tokens = clean
      .split(RegExp(r'\s+'))
      .where((e) => e.trim().isNotEmpty)
      .toList();
  if (tokens.length >= 3) {
    return _SignatureParts(
      body: tokens.first,
      aspect: tokens[1],
      point: tokens.sublist(2).join(' '),
    );
  }

  return _SignatureParts(body: clean, aspect: '', point: '');
}

List<String> _normalizeLines(List<String> raw) {
  final out = <String>[];
  for (final item in raw) {
    final parts = item
        .split(RegExp(r'[\n•\-]+'))
        .map((e) => e.trim())
        .where((e) => e.isNotEmpty);
    for (final part in parts) {
      final clean = _cleanUiLine(part);
      if (clean.isNotEmpty) {
        out.add(clean);
      }
    }
  }
  final dedup = <String>{};
  return out.where((e) => dedup.add(e.toLowerCase())).toList();
}

int? _readHouse(Object? raw) {
  if (raw is int) {
    return raw;
  }
  return int.tryParse((raw ?? '').toString());
}

String _cleanUiLine(String text) {
  final value = text.trim();
  if (value.isEmpty) {
    return '';
  }
  if (_isUiMetaLine(value)) {
    return '';
  }
  return value;
}

String _localizeSignature(String text) {
  var out = text.trim();
  if (out.isEmpty) {
    return '';
  }
  const tokenMap = <String, String>{
    'NEPTUNE': 'Neptün',
    'URANUS': 'Uranüs',
    'PLUTO': 'Plüton',
    'JUPITER': 'Jüpiter',
    'SATURN': 'Satürn',
    'MERCURY': 'Merkür',
    'VENUS': 'Venüs',
    'MARS': 'Mars',
    'SUN': 'Güneş',
    'MOON': 'Ay',
    'ASC': 'Yükselen',
    'DSC': 'Alçalan',
    'MC': 'Tepe Noktası',
    'IC': 'Dip Noktası',
  };
  tokenMap.forEach((src, dst) {
    out = out.replaceAll(RegExp('\\b$src\\b'), dst);
  });
  return out;
}

String _compactSignature(String signature) {
  var out = signature.trim();
  if (out.isEmpty) {
    return out;
  }
  // Keep badge signature compact: drop trailing time-hint fragments.
  if (out.contains('•')) {
    out = out.split('•').first.trim();
  }
  const compactMap = <String, String>{
    'Yükselen': 'ASC',
    'Alçalan': 'DSC',
    'Tepe Noktası': 'MC',
    'Dip Noktası': 'IC',
  };
  compactMap.forEach((src, dst) {
    out = out.replaceAll(src, dst);
  });
  return out;
}

bool _isUiMetaLine(String text) {
  final v = text.trim();
  if (v.isEmpty) {
    return true;
  }
  final lower = v.toLowerCase();
  if (lower.startsWith('arka bağlantı:') ||
      lower.startsWith('arka baglanti:')) {
    return true;
  }
  if (lower.contains('period') ||
      lower.contains('exact') ||
      lower.contains('applying') ||
      lower.contains('separating')) {
    return true;
  }
  if (RegExp(r'^\d+([.,]\d+)?$').hasMatch(lower)) {
    return true;
  }
  if (RegExp(r'^bu dönem \d+\.$', caseSensitive: false).hasMatch(v)) {
    return true;
  }
  return false;
}

bool _isNearDuplicate(String text, List<String> existing) {
  final a = _tokenSet(text);
  if (a.isEmpty) {
    return false;
  }
  for (final other in existing) {
    final b = _tokenSet(other);
    if (b.isEmpty) {
      continue;
    }
    final sim = _jaccard(a, b);
    if (sim >= 0.8) {
      return true;
    }
  }
  return false;
}

Set<String> _tokenSet(String text) {
  return text
      .toLowerCase()
      .replaceAll(RegExp(r'[^a-z0-9çğıöşü\s]'), ' ')
      .split(RegExp(r'\s+'))
      .where((e) => e.isNotEmpty)
      .toSet();
}

double _jaccard(Set<String> a, Set<String> b) {
  final inter = a.intersection(b).length.toDouble();
  final union = a.union(b).length.toDouble();
  if (union == 0) {
    return 0;
  }
  return inter / union;
}
