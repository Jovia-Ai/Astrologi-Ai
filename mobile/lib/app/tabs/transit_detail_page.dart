import 'package:flutter/material.dart';

import 'package:mobile/app/tabs/period_detail_navigation.dart';
import 'package:mobile/app/timing/narrative_dtos.dart';

/// Legacy bridge from event detail entry to period detail surface.
/// Kept temporarily while transit detail routing is being cleaned up.
@Deprecated(
  'Legacy event-to-period bridge. Use period detail navigation helpers for new routes.',
)
class TransitDetailPage extends StatelessWidget {
  const TransitDetailPage({super.key, required this.card});

  final EventCardDto card;

  @override
  Widget build(BuildContext context) {
    return buildPeriodDetailPageFromEventCard(
      eventCard: card,
      periodCore: null,
      routeSource: PeriodDetailRouteSource.transitDetailLegacy,
    );
  }
}
