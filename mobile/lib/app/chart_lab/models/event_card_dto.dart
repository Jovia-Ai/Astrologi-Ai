class EventCardTimingDto {
  const EventCardTimingDto({
    this.entryDateUtc,
    this.peakDateUtc,
    this.exitDateUtc,
  });

  final String? entryDateUtc;
  final String? peakDateUtc;
  final String? exitDateUtc;

  bool get hasAny =>
      (entryDateUtc?.isNotEmpty ?? false) ||
      (peakDateUtc?.isNotEmpty ?? false) ||
      (exitDateUtc?.isNotEmpty ?? false);

  factory EventCardTimingDto.fromMap(Map<String, dynamic> map) {
    return EventCardTimingDto(
      entryDateUtc: _s(map, 'entry_date_utc', 'entryDateUtc'),
      peakDateUtc: _s(map, 'peak_date_utc', 'peakDateUtc'),
      exitDateUtc: _s(map, 'exit_date_utc', 'exitDateUtc'),
    );
  }
}

class EventCardHousesDto {
  const EventCardHousesDto({this.transitInNatalHouse, this.natalPointHouse});

  final int? transitInNatalHouse;
  final int? natalPointHouse;

  bool get hasAny => transitInNatalHouse != null || natalPointHouse != null;

  factory EventCardHousesDto.fromMap(Map<String, dynamic> map) {
    return EventCardHousesDto(
      transitInNatalHouse: _i(
        map,
        'transit_in_natal_house',
        'transitInNatalHouse',
      ),
      natalPointHouse: _i(map, 'natal_point_house', 'natalPointHouse'),
    );
  }
}

class EventCardDto {
  const EventCardDto({
    required this.eventId,
    required this.title,
    required this.transitBody,
    required this.aspect,
    required this.natalPoint,
    required this.timeHint,
    required this.phase,
    required this.orbDeg,
    required this.houses,
    required this.conflict,
    required this.shadow,
    required this.upper,
    required this.guidance,
    required this.watchOut,
    required this.timing,
    required this.timelineSummary,
    required this.timelineLines,
  });

  final String eventId;
  final String title;
  final String transitBody;
  final String aspect;
  final String natalPoint;
  final String timeHint;
  final String phase;
  final double? orbDeg;
  final EventCardHousesDto houses;
  final String conflict;
  final String shadow;
  final String upper;
  final List<String> guidance;
  final List<String> watchOut;
  final EventCardTimingDto timing;
  final String timelineSummary;
  final List<String> timelineLines;

  String get subtitleSignature {
    final parts = <String>[];
    if (transitBody.isNotEmpty) {
      parts.add(transitBody);
    }
    if (aspect.isNotEmpty) {
      parts.add(aspect);
    }
    if (natalPoint.isNotEmpty) {
      parts.add(natalPoint);
    }
    return parts.join(' ');
  }

  factory EventCardDto.fromMap(Map<String, dynamic> map) {
    final timingMap = map['timing'] is Map
        ? Map<String, dynamic>.from(map['timing'] as Map)
        : const <String, dynamic>{};
    final housesMap = map['houses'] is Map
        ? Map<String, dynamic>.from(map['houses'] as Map)
        : const <String, dynamic>{};

    return EventCardDto(
      eventId: _s(map, 'event_id', 'eventId') ?? '',
      title: _s(map, 'title') ?? '',
      transitBody: _s(map, 'transit_body', 'transitBody') ?? '',
      aspect: _s(map, 'aspect') ?? '',
      natalPoint: _s(map, 'natal_point', 'natalPoint') ?? '',
      timeHint: _s(map, 'time_hint', 'timeHint') ?? '',
      phase: _s(map, 'phase') ?? '',
      orbDeg: _d(map, 'orb_deg', 'orbDeg'),
      houses: EventCardHousesDto.fromMap(housesMap),
      conflict: _s(map, 'conflict') ?? '',
      shadow: _s(map, 'shadow') ?? '',
      upper: _s(map, 'upper', 'upper_meaning') ?? '',
      guidance: _ls(map, 'guidance'),
      watchOut: _ls(map, 'watch_out', 'watchOut'),
      timing: EventCardTimingDto.fromMap(timingMap),
      timelineSummary: _s(map, 'timeline_summary', 'timelineSummary') ?? '',
      timelineLines: _ls(map, 'timeline_lines', 'timelineLines'),
    );
  }
}

String? _s(Map<String, dynamic> map, String a, [String? b]) {
  final value = map[a] ?? (b == null ? null : map[b]);
  if (value == null) {
    return null;
  }
  final out = value.toString().trim();
  return out.isEmpty ? null : out;
}

int? _i(Map<String, dynamic> map, String a, [String? b]) {
  final value = map[a] ?? (b == null ? null : map[b]);
  if (value is int) {
    return value;
  }
  if (value is num) {
    return value.toInt();
  }
  if (value is String && value.trim().isNotEmpty) {
    return int.tryParse(value.trim());
  }
  return null;
}

double? _d(Map<String, dynamic> map, String a, [String? b]) {
  final value = map[a] ?? (b == null ? null : map[b]);
  if (value is num) {
    return value.toDouble();
  }
  if (value is String && value.trim().isNotEmpty) {
    return double.tryParse(value.trim());
  }
  return null;
}

List<String> _ls(Map<String, dynamic> map, String a, [String? b]) {
  final value = map[a] ?? (b == null ? null : map[b]);
  if (value is! List) {
    return const <String>[];
  }
  return value
      .map((item) => item.toString().trim())
      .where((item) => item.isNotEmpty)
      .toList();
}
