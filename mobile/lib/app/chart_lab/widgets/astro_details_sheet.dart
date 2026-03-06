import 'package:flutter/material.dart';

import '../models/event_card_dto.dart';

class AstroDetailsSheet extends StatelessWidget {
  const AstroDetailsSheet({super.key, required this.card});

  final EventCardDto card;

  @override
  Widget build(BuildContext context) {
    final hasTiming = card.timing.hasAny;
    final hasHouses = card.houses.hasAny;

    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Astro Detaylar',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700),
            ),
            const SizedBox(height: 12),
            _kv('Transit', card.transitBody),
            _kv('Aci', card.aspect),
            _kv('Natal Nokta', card.natalPoint),
            if (card.orbDeg != null)
              _kv('Orb', '${card.orbDeg!.toStringAsFixed(2)}°'),
            if (card.phase.isNotEmpty) _kv('Faz', card.phase),
            if (hasTiming) ...[
              const SizedBox(height: 10),
              const Text(
                'Zamanlama',
                style: TextStyle(fontWeight: FontWeight.w600),
              ),
              _kv('Giris', card.timing.entryDateUtc ?? ''),
              _kv('Tepe', card.timing.peakDateUtc ?? ''),
              _kv('Cikis', card.timing.exitDateUtc ?? ''),
            ],
            if (hasHouses) ...[
              const SizedBox(height: 10),
              const Text(
                'Evler',
                style: TextStyle(fontWeight: FontWeight.w600),
              ),
              if (card.houses.transitInNatalHouse != null)
                _kv('Transit ev', '${card.houses.transitInNatalHouse}'),
              if (card.houses.natalPointHouse != null)
                _kv('Natal nokta ev', '${card.houses.natalPointHouse}'),
            ],
          ],
        ),
      ),
    );
  }

  Widget _kv(String label, String value) {
    if (value.trim().isEmpty) {
      return const SizedBox.shrink();
    }
    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: Text('$label: $value'),
    );
  }
}
