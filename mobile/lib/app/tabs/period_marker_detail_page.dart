import 'package:flutter/material.dart';

import 'package:mobile/app/timing/narrative_dtos.dart';

class PeriodMarkerDetailPage extends StatelessWidget {
  const PeriodMarkerDetailPage({super.key, required this.marker});

  final PeriodMarkerDto marker;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Dönem İşareti')),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            Text(
              marker.title.isNotEmpty ? marker.title : 'Dönem İşareti',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 10),
            Text(
              marker.summary.isNotEmpty
                  ? marker.summary
                  : 'Bu marker için ek özet bulunamadı.',
            ),
            if (marker.timeHint.trim().isNotEmpty) ...[
              const SizedBox(height: 12),
              Text(
                marker.timeHint.trim(),
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ],
          ],
        ),
      ),
    );
  }
}
