import 'package:flutter/material.dart';

import 'package:mobile/app/timing/narrative_dtos.dart';
import 'package:mobile/design/theme/profile_theme_extension.dart';
import 'package:mobile/design/widgets/jovia_editorial.dart';

class PeriodPeakTimelineWidget extends StatelessWidget {
  const PeriodPeakTimelineWidget({
    super.key,
    required this.items,
    this.compact = false,
    this.framed = true,
    this.title,
    this.subtitle,
    this.onTapItem,
  });

  final List<PeriodPeakTimelineItemDto> items;
  final bool compact;
  final bool framed;
  final String? title;
  final String? subtitle;
  final ValueChanged<PeriodPeakTimelineItemDto>? onTapItem;

  @override
  Widget build(BuildContext context) {
    if (items.isEmpty) {
      return const SizedBox.shrink();
    }

    final body = Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        for (var index = 0; index < items.length; index++) ...[
          _PeriodPeakTimelineTile(
            item: items[index],
            compact: compact,
            onTap: onTapItem == null ? null : () => onTapItem!(items[index]),
          ),
          if (index != items.length - 1) ...[
            SizedBox(height: compact ? 10 : 12),
            const ThinDivider(),
            SizedBox(height: compact ? 10 : 12),
          ],
        ],
      ],
    );

    if (!framed) {
      return body;
    }

    return JoviaReadingPanel(
      label: 'Timeline',
      title: title ?? 'Peak listesi',
      body: subtitle,
      child: body,
    );
  }
}

class _PeriodPeakTimelineTile extends StatelessWidget {
  const _PeriodPeakTimelineTile({
    required this.item,
    required this.compact,
    this.onTap,
  });

  final PeriodPeakTimelineItemDto item;
  final bool compact;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final chips = <String>[
      if (item.bucket.trim().isNotEmpty) item.bucket.trim(),
      if (item.phase.trim().isNotEmpty) item.phase.trim(),
      if (item.timeHintTr.trim().isNotEmpty) item.timeHintTr.trim(),
    ];
    final dateLabel = _formatDateLabel(item.peakDateUtc);

    return JoviaPressable(
      onTap: onTap,
      borderRadius: BorderRadius.circular(18),
      child: Padding(
        padding: EdgeInsets.symmetric(vertical: compact ? 2 : 4),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  width: compact ? 10 : 12,
                  height: compact ? 10 : 12,
                  margin: EdgeInsets.only(top: compact ? 6 : 5),
                  decoration: BoxDecoration(
                    color: profile.colors.primary,
                    shape: BoxShape.circle,
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        item.displayTitle,
                        maxLines: compact ? 2 : 3,
                        overflow: TextOverflow.ellipsis,
                        style: profile.typography.cardTitle,
                      ),
                      if (dateLabel.isNotEmpty) ...[
                        const SizedBox(height: 4),
                        Text(
                          dateLabel,
                          style: profile.typography.micro.copyWith(
                            color: profile.colors.textLight,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
                if (item.canOpenDetail)
                  Padding(
                    padding: const EdgeInsets.only(left: 12),
                    child: JoviaUiIcon(
                      asset: JoviaUiAsset.chevronRight,
                      size: 16,
                      color: profile.colors.primary,
                    ),
                  ),
              ],
            ),
            if (chips.isNotEmpty) ...[
              SizedBox(height: compact ? 8 : 10),
              SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: Row(
                  children: [
                    for (var index = 0; index < chips.length; index++) ...[
                      JoviaMetaPill(label: chips[index]),
                      if (index != chips.length - 1) const SizedBox(width: 8),
                    ],
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  String _formatDateLabel(String raw) {
    final value = raw.trim();
    if (value.isEmpty) {
      return '';
    }
    final parsed = DateTime.tryParse(value);
    if (parsed == null) {
      return value;
    }
    final local = parsed.toLocal();
    final day = local.day.toString().padLeft(2, '0');
    final month = local.month.toString().padLeft(2, '0');
    return '$day.$month.${local.year}';
  }
}
