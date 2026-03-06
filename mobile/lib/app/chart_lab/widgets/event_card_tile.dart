import 'package:flutter/material.dart';

import '../models/event_card_dto.dart';

class EventCardTile extends StatelessWidget {
  const EventCardTile({super.key, required this.card, required this.onTap});

  final EventCardDto card;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final signature = [
      if (card.transitBody.isNotEmpty) card.transitBody,
      if (card.aspect.isNotEmpty) _aspectSymbol(card.aspect),
      if (card.natalPoint.isNotEmpty) card.natalPoint,
    ].join(' ');
    final subtitle = [
      if (signature.trim().isNotEmpty) signature.trim(),
      if (card.timeHint.isNotEmpty) card.timeHint,
    ].join(' • ');

    return InkWell(
      borderRadius: BorderRadius.circular(12),
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          border: Border.all(color: Colors.black12),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              card.title.isNotEmpty ? card.title : 'Aktif Etki',
              style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w700),
            ),
            if (subtitle.isNotEmpty) ...[
              const SizedBox(height: 6),
              Text(
                subtitle,
                style: Theme.of(
                  context,
                ).textTheme.bodySmall?.copyWith(color: Colors.black54),
              ),
            ],
            if (card.timeHint.isNotEmpty) ...[
              const SizedBox(height: 8),
              Chip(
                visualDensity: VisualDensity.compact,
                label: Text(card.timeHint),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

String _aspectSymbol(String aspectRaw) {
  switch (aspectRaw.toLowerCase().trim()) {
    case 'conjunction':
      return '☌';
    case 'opposition':
      return '☍';
    case 'trine':
      return '△';
    case 'square':
      return '□';
    case 'sextile':
      return '✶';
    default:
      return aspectRaw;
  }
}
