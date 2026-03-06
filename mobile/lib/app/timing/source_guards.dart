import 'package:flutter/foundation.dart';

import 'package:mobile/app/timing/narrative_dtos.dart';

bool assertDailySource(
  Object? candidate, {
  String context = 'daily',
}) {
  if (candidate is EventCardDto) {
    return true;
  }
  debugPrint(
    'Daily source mismatch in $context: expected EventCardDto, got ${candidate.runtimeType}.',
  );
  return false;
}

bool assertPeriodSource(
  Object? candidate, {
  String context = 'period',
}) {
  if (candidate is PeriodCardDto || candidate is PeriodMarkerDto) {
    return true;
  }
  debugPrint(
    'Period source mismatch in $context: expected PeriodCardDto/PeriodMarkerDto, got ${candidate.runtimeType}.',
  );
  return false;
}

List<EventCardDto> pickDailyEventCards(
  Iterable<EventCardDto> cards, {
  String context = 'daily',
}) {
  final out = <EventCardDto>[];
  for (final card in cards) {
    if (!assertDailySource(card, context: context)) {
      continue;
    }
    if (card.horizon.trim().toLowerCase() == 'period') {
      debugPrint(
        'Daily source mismatch in $context: ignored period-horizon card ${card.eventId}.',
      );
      continue;
    }
    out.add(card);
  }
  return out;
}

List<EventCardDto> pickPeriodEventCards(
  Iterable<EventCardDto> cards, {
  String context = 'period',
}) {
  final out = <EventCardDto>[];
  for (final card in cards) {
    if (!assertDailySource(card, context: context)) {
      continue;
    }
    if (card.horizon.trim().toLowerCase() != 'period') {
      continue;
    }
    out.add(card);
  }
  return out;
}
