import 'package:flutter/material.dart';

import 'package:mobile/app/timing/narrative_dtos.dart';

class PeriodDetailPage extends StatelessWidget {
  const PeriodDetailPage({
    super.key,
    required this.card,
    required this.periodCore,
  });

  final PeriodCardDto card;
  final PeriodCoreDto? periodCore;

  @override
  Widget build(BuildContext context) {
    final core = periodCore;
    final eventCard = card.eventCard;
    return Scaffold(
      appBar: AppBar(title: const Text('Period Detail')),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            Text(
              card.title,
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 10),
            Text(card.subtitle.isNotEmpty ? card.subtitle : 'Detay bulunamadi.'),
            if (card.timeHint.trim().isNotEmpty) ...[
              const SizedBox(height: 8),
              Text(
                card.timeHint.trim(),
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ],
            if (eventCard != null) ...[
              const SizedBox(height: 20),
              if (eventCard.whyNow.trim().isNotEmpty)
                _Section(title: 'Why Now', body: eventCard.whyNow.trim()),
              if (eventCard.conflict.trim().isNotEmpty)
                _Section(title: 'Conflict', body: eventCard.conflict.trim()),
              if (eventCard.shadow.trim().isNotEmpty)
                _Section(title: 'Shadow', body: eventCard.shadow.trim()),
              if (eventCard.upper.trim().isNotEmpty)
                _Section(title: 'Upper Meaning', body: eventCard.upper.trim()),
            ],
            if (core != null) ...[
              const SizedBox(height: 20),
              if (core.bigPicture.trim().isNotEmpty)
                _Section(title: 'Big Picture', body: core.bigPicture.trim()),
              if (core.mechanism.trim().isNotEmpty)
                _Section(title: 'Mechanism', body: core.mechanism.trim()),
              if (core.upperMeaning.trim().isNotEmpty)
                _Section(title: 'Upper Meaning', body: core.upperMeaning.trim()),
            ],
          ],
        ),
      ),
    );
  }
}

class _Section extends StatelessWidget {
  const _Section({required this.title, required this.body});

  final String title;
  final String body;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 6),
          Text(body),
        ],
      ),
    );
  }
}
