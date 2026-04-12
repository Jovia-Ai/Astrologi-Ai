import 'package:mobile/app/timing/narrative_dtos.dart';

class DailyTransitCardSelection {
  const DailyTransitCardSelection({
    required this.dailyCards,
    required this.periodCards,
    required this.usedPeriodFallback,
    required this.periodOnlyNote,
  });

  final List<EventCardDto> dailyCards;
  final List<EventCardDto> periodCards;
  final bool usedPeriodFallback;
  final String periodOnlyNote;
}

bool isDailyTransitCardBackedByPeriod(EventCardDto card) {
  final sourceHorizon = card.sourceHorizon.trim().toLowerCase();
  return card.isPeriodDerived ||
      card.todayFacingFallback ||
      sourceHorizon == 'period';
}

DailyTransitCardSelection selectDailyTransitCardsForDate({
  required NarrativeResponse narrative,
  required DateTime selectedDate,
}) {
  if (narrative.dailyEventCards.isNotEmpty ||
      narrative.periodEventCards.isNotEmpty) {
    final dailyCards = _dedupeEventCardSelection(narrative.dailyEventCards);
    final periodCards = _dedupeEventCardSelection(
      narrative.periodEventCards,
      avoid: dailyCards,
    );
    return DailyTransitCardSelection(
      dailyCards: dailyCards,
      periodCards: periodCards,
      usedPeriodFallback:
          narrative.dailySelection?.usedPeriodFallback == true &&
          dailyCards.isEmpty &&
          periodCards.isNotEmpty,
      periodOnlyNote: narrative.dailySelection?.periodOnlyNote.trim() ?? '',
    );
  }

  final scored = [
    for (final card in narrative.eventCards)
      (card: card, score: _scoreEventCardForToday(card, selectedDate)),
  ]..sort((a, b) => b.score.compareTo(a.score));

  final dailyCards = _dedupeEventCardSelection(
    <EventCardDto>[
      for (final entry in scored)
        if (entry.card.horizon.trim().toLowerCase() != 'period') entry.card,
    ].take(2).toList(growable: false),
  );
  final periodCards = _dedupeEventCardSelection(
    <EventCardDto>[
      for (final entry in scored)
        if (entry.card.horizon.trim().toLowerCase() == 'period') entry.card,
    ].take(3).toList(growable: false),
    avoid: dailyCards,
  );

  return DailyTransitCardSelection(
    dailyCards: dailyCards,
    periodCards: periodCards,
    usedPeriodFallback: dailyCards.isEmpty && periodCards.isNotEmpty,
    periodOnlyNote: '',
  );
}

String _normalizeTransitPageText(String value) {
  return value
      .toLowerCase()
      .replaceAll(RegExp(r'[^\w\s]', unicode: true), ' ')
      .replaceAll(RegExp(r'\s+'), ' ')
      .trim();
}

String _firstTransitPageText(Iterable<String> values) {
  for (final value in values) {
    final cleaned = value.trim();
    if (cleaned.isNotEmpty) {
      return cleaned;
    }
  }
  return '';
}

bool _isTransitPageDuplicateText(String left, String right) {
  final normalizedLeft = _normalizeTransitPageText(left);
  final normalizedRight = _normalizeTransitPageText(right);
  if (normalizedLeft.isEmpty || normalizedRight.isEmpty) {
    return false;
  }
  if (normalizedLeft == normalizedRight) {
    return true;
  }
  final shorter = normalizedLeft.length <= normalizedRight.length
      ? normalizedLeft
      : normalizedRight;
  final longer = shorter == normalizedLeft ? normalizedRight : normalizedLeft;
  return shorter.length >= 18 && longer.contains(shorter);
}

List<String> _dedupeTransitPageTexts(Iterable<String> values, {int limit = 3}) {
  final out = <String>[];
  for (final value in values) {
    final cleaned = value.trim();
    if (cleaned.isEmpty) {
      continue;
    }
    final duplicate = out.any(
      (existing) => _isTransitPageDuplicateText(existing, cleaned),
    );
    if (duplicate) {
      continue;
    }
    out.add(cleaned);
    if (out.length >= limit) {
      break;
    }
  }
  return out;
}

bool _transitPageTextListsOverlap(List<String> left, List<String> right) {
  if (left.isEmpty || right.isEmpty) {
    return false;
  }
  var matchCount = 0;
  var leadMatch = false;
  for (var leftIndex = 0; leftIndex < left.length; leftIndex++) {
    for (var rightIndex = 0; rightIndex < right.length; rightIndex++) {
      if (!_isTransitPageDuplicateText(left[leftIndex], right[rightIndex])) {
        continue;
      }
      matchCount += 1;
      if (leftIndex == 0 && rightIndex == 0) {
        leadMatch = true;
      }
      break;
    }
  }
  return matchCount >= 2 || (leadMatch && matchCount >= 1);
}

List<String> _eventCardSelectionTexts(EventCardDto card) {
  return _dedupeTransitPageTexts([
    _firstTransitPageText([
      card.feltLineTr,
      card.headline,
      card.title,
      card.signatureTr,
    ]),
    _firstTransitPageText([
      card.opening,
      card.essence,
      card.whyNow,
      card.bigPicture,
    ]),
    _firstTransitPageText([
      card.timeHintTr,
      card.signatureTr,
      card.houseTouchpointHintTr,
      card.eventFamily,
    ]),
  ]);
}

bool _eventCardsSharePageMeaning(EventCardDto left, EventCardDto right) {
  final leftEventId = left.eventId.trim();
  final rightEventId = right.eventId.trim();
  if (leftEventId.isNotEmpty && leftEventId == rightEventId) {
    return true;
  }
  return _transitPageTextListsOverlap(
    _eventCardSelectionTexts(left),
    _eventCardSelectionTexts(right),
  );
}

bool _eventAndPeriodSharePageMeaning(EventCardDto event, EventCardDto period) {
  return _transitPageTextListsOverlap(
    _eventCardSelectionTexts(event),
    _eventCardSelectionTexts(period),
  );
}

List<EventCardDto> _dedupeEventCardSelection(
  Iterable<EventCardDto> cards, {
  Iterable<EventCardDto> avoid = const <EventCardDto>[],
}) {
  final out = <EventCardDto>[];
  for (final card in cards) {
    if (_eventCardSelectionTexts(card).isEmpty) {
      continue;
    }
    final duplicateInAvoid = avoid.any(
      (existing) => _eventAndPeriodSharePageMeaning(existing, card),
    );
    if (duplicateInAvoid) {
      continue;
    }
    final duplicate = out.any(
      (existing) => _eventCardsSharePageMeaning(existing, card),
    );
    if (duplicate) {
      continue;
    }
    out.add(card);
  }
  return out;
}

double _scoreEventCardForToday(EventCardDto card, DateTime selectedDate) {
  var score = 0.0;

  if (card.eventFamily == 'lunation_trigger' ||
      card.eventFamily == 'eclipse_trigger') {
    score += 38;
  }

  score += switch (card.transitBody.trim().toLowerCase()) {
    'moon' => 24,
    'sun' => 18,
    'mercury' => 16,
    'mars' => 16,
    'venus' => 10,
    _ => 0,
  };

  score += switch (card.aspect.trim().toLowerCase()) {
    'opposition' => 18,
    'square' => 18,
    'conjunction' => 15,
    'quincunx' => 13,
    'trine' => 10,
    'sextile' => 8,
    _ => 6,
  };

  final orb = card.orbDeg;
  if (orb != null) {
    score += (20 - (orb * 5)).clamp(0, 20).toDouble();
  }

  final exactInDays = card.tags.exactInDays;
  if (exactInDays != null) {
    score += switch (exactInDays) {
      0 => 18,
      1 => 12,
      2 => 6,
      _ => exactInDays >= 5 ? 0 : 4,
    };
  }

  final phase = card.phase.trim().toLowerCase();
  if (phase == 'exact' || phase == 'exactish') {
    score += 16;
  } else if (phase == 'applying') {
    score += 8;
  }

  if (const {
    'asc',
    'dsc',
    'mc',
    'ic',
  }.contains(card.natalPoint.trim().toLowerCase())) {
    score += 14;
  }

  if (card.natalPromiseScore != null) {
    score += card.natalPromiseScore!.clamp(0, 1) * 14;
  }
  score += card.tags.intensity.clamp(0, 1) * 8;

  int? dayDelta(String raw) {
    final value = raw.trim();
    if (value.length < 10) {
      return null;
    }
    final parsed = DateTime.tryParse(value.substring(0, 10));
    if (parsed == null) {
      return null;
    }
    final normalizedSelected = DateTime(
      selectedDate.year,
      selectedDate.month,
      selectedDate.day,
    );
    return parsed.difference(normalizedSelected).inDays.abs();
  }

  for (final entry in <({String raw, double exact, double near})>[
    (raw: card.timing.peakDateUtc, exact: 16, near: 8),
    (raw: card.timing.entryDateUtc, exact: 10, near: 4),
  ]) {
    final delta = dayDelta(entry.raw);
    if (delta == null) {
      continue;
    }
    if (delta == 0) {
      score += entry.exact;
    } else if (delta == 1) {
      score += entry.near;
    }
  }

  if (card.horizon.trim().toLowerCase() == 'daily') {
    score += 18;
  }
  if (card.bucket.trim().toLowerCase() == 'short') {
    score += 12;
  }

  score += switch (card.importanceTier.trim().toLowerCase()) {
    'critical' => 10,
    'high' => 6,
    _ => 0,
  };

  return score;
}
