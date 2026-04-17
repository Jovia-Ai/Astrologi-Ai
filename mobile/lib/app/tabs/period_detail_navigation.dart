import 'package:flutter/material.dart';

import 'package:mobile/app/telemetry/perf_telemetry.dart';
import 'package:mobile/app/tabs/period_detail_page.dart';
import 'package:mobile/app/timing/narrative_dtos.dart';

class PeriodDetailRouteSource {
  const PeriodDetailRouteSource._();

  static const String home = 'home';
  static const String calendarHubLongTerm = 'calendar_hub_long_term';
  static const String calendarHubDaily = 'calendar_hub_daily';
  static const String calendarHubPeriodSection = 'calendar_hub_period_section';
  static const String profileTiming = 'profile_timing';
  static const String calendarHubPeriod = 'calendar_hub_period';
  static const String calendarHubTimeline = 'calendar_hub_timeline';
  static const String transitDetailLegacy = 'transit_detail_legacy';

  static String calendarHubDayCard(String source) => '${source}_day_card';
  static String calendarHubDayPeriod(String source) => '${source}_day_period';
}

PeriodDetailPage buildPeriodDetailPageFromEventCard({
  required EventCardDto eventCard,
  required String routeSource,
  PeriodCoreDto? periodCore,
  int index = 0,
}) {
  return PeriodDetailPage(
    card: PeriodCardDto.fromEventCard(eventCard: eventCard, index: index),
    periodCore: periodCore,
    routeSource: routeSource,
  );
}

void openPeriodDetailFromEventCard({
  required BuildContext context,
  required EventCardDto eventCard,
  required String routeSource,
  required String surface,
  PeriodCoreDto? periodCore,
  int index = 0,
  bool rootNavigator = true,
}) {
  PerfTelemetry.logEvent(
    'period_detail_event_coercion',
    data: <String, Object?>{
      'surface': surface,
      'route_source': routeSource,
      'coercion_type': 'event_to_period',
      'has_period_core': periodCore != null,
      'event_id': eventCard.eventId.trim(),
    },
  );

  Navigator.of(context, rootNavigator: rootNavigator).push(
    MaterialPageRoute<void>(
      builder: (_) => buildPeriodDetailPageFromEventCard(
        eventCard: eventCard,
        routeSource: routeSource,
        periodCore: periodCore,
        index: index,
      ),
    ),
  );
}
