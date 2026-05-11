import 'dart:collection';

import 'package:flutter/foundation.dart';

@immutable
class ChartWheelData {
  ChartWheelData({
    required double ascDegree,
    required double mcDegree,
    required List<double> houseCusps,
    required List<ChartPlanetPoint> planets,
    List<ChartAspectLine> aspects = const <ChartAspectLine>[],
  }) : ascDegree = _normalizeLongitude(ascDegree),
       mcDegree = _normalizeLongitude(mcDegree),
       houseCusps = List<double>.unmodifiable(
         houseCusps.take(12).map(_normalizeLongitude),
       ),
       planets = List<ChartPlanetPoint>.unmodifiable(planets),
       aspects = List<ChartAspectLine>.unmodifiable(aspects);

  final double ascDegree;
  final double mcDegree;
  final List<double> houseCusps;
  final List<ChartPlanetPoint> planets;
  final List<ChartAspectLine> aspects;

  bool get hasMinimumGeometry => houseCusps.length == 12 && planets.isNotEmpty;

  ChartPlanetPoint? findPlanet(String id) {
    final normalized = _normalizePlanetId(id);
    for (final planet in planets) {
      if (planet.id == normalized) {
        return planet;
      }
    }
    return null;
  }

  static ChartWheelData? tryFromInterpretPayload(
    Map<String, dynamic>? payload,
  ) {
    if (payload == null || payload.isEmpty) {
      return null;
    }

    final scopes = <Map<String, dynamic>>[
      payload,
      _asMap(payload['chart_data']),
      _asMap(payload['public']),
      _asMap(_asMap(payload['public'])['chart_data']),
      _asMap(payload['data']),
    ].where((scope) => scope.isNotEmpty);

    for (final scope in scopes) {
      final direct = tryFromChartResponse(scope);
      if (direct != null) {
        return direct;
      }
    }
    return null;
  }

  static ChartWheelData? tryFromChartResponse(Map<String, dynamic>? payload) {
    if (payload == null || payload.isEmpty) {
      return null;
    }

    final angles = _asMap(payload['angles']);
    final houses = _asMap(payload['house_positions']);
    final planets = _parsePlanets(payload['planets']);

    final ascDegree = _readDouble(angles['ascendant']);
    final mcDegree = _readDouble(angles['midheaven']);
    if (ascDegree == null ||
        mcDegree == null ||
        houses.isEmpty ||
        planets.isEmpty) {
      return null;
    }

    final houseCusps = <double>[];
    for (var index = 1; index <= 12; index++) {
      final house = _asMap(houses['$index']);
      final cusp =
          _readDouble(house['longitude']) ??
          _readDouble(house['degree']) ??
          _readDouble(house['position']);
      if (cusp == null) {
        return null;
      }
      houseCusps.add(cusp);
    }

    final aspects = _parseAspects(payload['aspects']);
    final data = ChartWheelData(
      ascDegree: ascDegree,
      mcDegree: mcDegree,
      houseCusps: houseCusps,
      planets: planets,
      aspects: aspects,
    );
    return data.hasMinimumGeometry ? data : null;
  }

  static List<ChartPlanetPoint> _parsePlanets(dynamic raw) {
    final planets = <ChartPlanetPoint>[];
    final dedupe = HashSet<String>();

    void addPlanet({
      required String id,
      required Map<String, dynamic> payload,
    }) {
      final normalizedId = _normalizePlanetId(id);
      if (normalizedId.isEmpty || !dedupe.add(normalizedId)) {
        return;
      }
      final longitude =
          _readDouble(payload['longitude']) ??
          _readDouble(payload['degree']) ??
          _readDouble(payload['position']);
      if (longitude == null) {
        return;
      }
      final house = _readInt(payload['house']);
      final sign = (payload['sign'] ?? payload['zodiac_sign'] ?? '')
          .toString()
          .trim();
      planets.add(
        ChartPlanetPoint(
          id: normalizedId,
          longitude: longitude,
          sign: sign.isEmpty ? _signFromLongitude(longitude) : sign,
          house: house,
          retrograde: payload['retrograde'] == true,
        ),
      );
    }

    if (raw is Map) {
      for (final entry in raw.entries) {
        final value = _asMap(entry.value);
        if (value.isEmpty) {
          continue;
        }
        addPlanet(id: entry.key.toString(), payload: value);
      }
    } else if (raw is List) {
      for (final item in raw) {
        final value = _asMap(item);
        if (value.isEmpty) {
          continue;
        }
        addPlanet(
          id: (value['planet'] ?? value['name'] ?? value['body'] ?? '')
              .toString(),
          payload: value,
        );
      }
    }

    return planets;
  }

  static List<ChartAspectLine> _parseAspects(dynamic raw) {
    if (raw is! List) {
      return const <ChartAspectLine>[];
    }
    final out = <ChartAspectLine>[];
    for (final item in raw) {
      final value = _asMap(item);
      if (value.isEmpty) {
        continue;
      }
      final from = _normalizePlanetId(
        (value['planet1'] ?? value['from'] ?? '').toString(),
      );
      final to = _normalizePlanetId(
        (value['planet2'] ?? value['to'] ?? '').toString(),
      );
      final type = (value['type'] ?? value['aspect'] ?? '').toString().trim();
      if (from.isEmpty || to.isEmpty || type.isEmpty) {
        continue;
      }
      out.add(
        ChartAspectLine(
          from: from,
          to: to,
          type: type,
          orb: _readDouble(value['orb']) ?? 0,
        ),
      );
    }
    return out;
  }
}

@immutable
class ChartPlanetPoint {
  ChartPlanetPoint({
    required this.id,
    required double longitude,
    required this.sign,
    required this.house,
    required this.retrograde,
  }) : longitude = _normalizeLongitude(longitude);

  final String id;
  final double longitude;
  final String sign;
  final int? house;
  final bool retrograde;
}

@immutable
class ChartAspectLine {
  const ChartAspectLine({
    required this.from,
    required this.to,
    required this.type,
    required this.orb,
  });

  final String from;
  final String to;
  final String type;
  final double orb;
}

Map<String, dynamic> _asMap(dynamic value) {
  if (value is Map<String, dynamic>) {
    return value;
  }
  if (value is Map) {
    return Map<String, dynamic>.from(value);
  }
  return const <String, dynamic>{};
}

double? _readDouble(dynamic value) {
  if (value is num) {
    return value.toDouble();
  }
  return double.tryParse(value?.toString() ?? '');
}

int? _readInt(dynamic value) {
  if (value is int) {
    return value;
  }
  if (value is num) {
    return value.toInt();
  }
  return int.tryParse(value?.toString() ?? '');
}

double _normalizeLongitude(double value) {
  final normalized = value % 360;
  return normalized < 0 ? normalized + 360 : normalized;
}

String _normalizePlanetId(String raw) {
  final normalized = raw.trim().toLowerCase().replaceAll(
    RegExp(r'[^a-z0-9]+'),
    '_',
  );
  return switch (normalized) {
    'sun' => 'sun',
    'moon' => 'moon',
    'mercury' => 'mercury',
    'venus' => 'venus',
    'mars' => 'mars',
    'jupiter' => 'jupiter',
    'saturn' => 'saturn',
    'uranus' => 'uranus',
    'neptune' => 'neptune',
    'pluto' => 'pluto',
    'north_node' || 'true_node' || 'mean_node' || 'node' => 'north_node',
    'south_node' => 'south_node',
    'chiron' => 'chiron',
    'lilith' || 'black_moon_lilith' => 'lilith',
    'fortune' || 'part_of_fortune' => 'fortune',
    'vertex' => 'vertex',
    'asc' || 'ascendant' => 'ascendant',
    'mc' || 'midheaven' => 'midheaven',
    'dsc' || 'descendant' => 'descendant',
    'ic' || 'imum_coeli' => 'imum_coeli',
    _ => normalized,
  };
}

String _signFromLongitude(double longitude) {
  const signs = <String>[
    'Aries',
    'Taurus',
    'Gemini',
    'Cancer',
    'Leo',
    'Virgo',
    'Libra',
    'Scorpio',
    'Sagittarius',
    'Capricorn',
    'Aquarius',
    'Pisces',
  ];
  final index = (_normalizeLongitude(longitude) ~/ 30) % 12;
  return signs[index];
}
