import 'package:flutter/material.dart';

import 'package:mobile/app/tabs/period_detail_page.dart';
import 'package:mobile/app/timing/narrative_dtos.dart';

class TransitDetailPage extends StatelessWidget {
  const TransitDetailPage({super.key, required this.card});

  final EventCardDto card;

  @override
  Widget build(BuildContext context) {
    return PeriodDetailPage(
      card: PeriodCardDto.fromEventCard(eventCard: card, index: 0),
      periodCore: null,
      routeSource: 'transit_detail_legacy',
    );
  }
}
