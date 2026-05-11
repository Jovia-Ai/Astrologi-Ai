// Home v12 — natal chart DTOs + repository + provider.
//
// `/calculate-natal-chart` endpoint'inden dönen büyük natal payload'unu,
// chart wheel + manifesto yükselen burcu için yeterli kompakt bir
// [HomeV2NatalSnapshot]'a sarar. 30 dk local cache (ApiClient seviyesinde).

import 'dart:async' show TimeoutException;

import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:mobile/app/api/api_client.dart';
import 'package:mobile/app/profile/profile_providers.dart';

// ─── DTO ──────────────────────────────────────────────────────

class NatalPlanetDto {
  const NatalPlanetDto({
    required this.name,
    required this.sign,
    required this.house,
    required this.longitude,
    required this.degree,
    required this.minute,
    required this.retrograde,
  });

  final String name; // "Sun", "Moon", …
  final String sign; // "Capricorn"
  final int house; // 1..12
  final double longitude; // 0..360
  final int degree; // 0..29
  final int minute; // 0..59
  final bool retrograde;

  factory NatalPlanetDto.fromMap(String name, Map<String, dynamic> map) {
    return NatalPlanetDto(
      name: name,
      sign: (map['sign'] ?? '').toString(),
      house: _asInt(map['house']),
      longitude: _asDouble(map['longitude']),
      degree: _asInt(map['degree']),
      minute: _asInt(map['minute']),
      retrograde: map['retrograde'] == true,
    );
  }
}

class HouseCuspDto {
  const HouseCuspDto({
    required this.number,
    required this.sign,
    required this.longitude,
    required this.degree,
    required this.minute,
  });

  final int number;
  final String sign;
  final double longitude;
  final int degree;
  final int minute;

  factory HouseCuspDto.fromMap(int number, Map<String, dynamic> map) {
    return HouseCuspDto(
      number: number,
      sign: (map['sign'] ?? '').toString(),
      longitude: _asDouble(map['longitude']),
      degree: _asInt(map['degree']),
      minute: _asInt(map['minute']),
    );
  }
}

class AnglesDto {
  const AnglesDto({
    required this.ascendantLon,
    required this.ascendantSign,
    required this.midheavenLon,
    required this.midheavenSign,
    required this.descendantLon,
    required this.descendantSign,
    required this.imumCoeliLon,
    required this.imumCoeliSign,
  });

  final double ascendantLon;
  final String ascendantSign;
  final double midheavenLon;
  final String midheavenSign;
  final double descendantLon;
  final String descendantSign;
  final double imumCoeliLon;
  final String imumCoeliSign;

  factory AnglesDto.fromMap(Map<String, dynamic> map) {
    return AnglesDto(
      ascendantLon: _asDouble(map['ascendant']),
      ascendantSign: (map['ascendant_sign'] ?? '').toString(),
      midheavenLon: _asDouble(map['midheaven']),
      midheavenSign: (map['midheaven_sign'] ?? '').toString(),
      descendantLon: _asDouble(map['descendant']),
      descendantSign: (map['descendant_sign'] ?? '').toString(),
      imumCoeliLon: _asDouble(map['imum_coeli']),
      imumCoeliSign: (map['imum_coeli_sign'] ?? '').toString(),
    );
  }
}

class NatalAspectDto {
  const NatalAspectDto({
    required this.planet1,
    required this.planet2,
    required this.aspect,
    required this.orb,
  });

  final String planet1;
  final String planet2;
  final String aspect; // "Square", "Trine", "Conjunction"…
  final double orb;

  factory NatalAspectDto.fromMap(Map<String, dynamic> map) {
    return NatalAspectDto(
      planet1: (map['planet1'] ?? '').toString(),
      planet2: (map['planet2'] ?? '').toString(),
      aspect: (map['aspect'] ?? '').toString(),
      orb: _asDouble(map['orb']),
    );
  }
}

class HomeV2NatalSnapshot {
  const HomeV2NatalSnapshot({
    required this.planets,
    required this.houses,
    required this.angles,
    required this.aspects,
  });

  final List<NatalPlanetDto> planets;
  final Map<int, HouseCuspDto> houses;
  final AnglesDto angles;
  final List<NatalAspectDto> aspects;

  /// İsimle gezegen arar — `null` dönerse ekranda sabit/mock kullanılır.
  NatalPlanetDto? findPlanet(String name) {
    final target = name.toLowerCase();
    for (final p in planets) {
      if (p.name.toLowerCase() == target) return p;
    }
    return null;
  }

  factory HomeV2NatalSnapshot.fromMap(Map<String, dynamic> map) {
    final planets = <NatalPlanetDto>[];
    final rawPlanets = map['planets'];
    if (rawPlanets is Map) {
      rawPlanets.forEach((key, value) {
        if (value is Map) {
          planets.add(
            NatalPlanetDto.fromMap(
              key.toString(),
              Map<String, dynamic>.from(value),
            ),
          );
        }
      });
    }

    final houses = <int, HouseCuspDto>{};
    final rawHouses = map['house_positions'];
    if (rawHouses is Map) {
      rawHouses.forEach((key, value) {
        final n = int.tryParse(key.toString());
        if (n != null && value is Map) {
          houses[n] = HouseCuspDto.fromMap(
            n,
            Map<String, dynamic>.from(value),
          );
        }
      });
    }

    final angles = map['angles'] is Map
        ? AnglesDto.fromMap(Map<String, dynamic>.from(map['angles'] as Map))
        : const AnglesDto(
            ascendantLon: 0,
            ascendantSign: '',
            midheavenLon: 0,
            midheavenSign: '',
            descendantLon: 0,
            descendantSign: '',
            imumCoeliLon: 0,
            imumCoeliSign: '',
          );

    final aspects = <NatalAspectDto>[];
    final rawAspects = map['aspects'];
    if (rawAspects is List) {
      for (final a in rawAspects) {
        if (a is Map) {
          aspects.add(
            NatalAspectDto.fromMap(Map<String, dynamic>.from(a)),
          );
        }
      }
    }

    return HomeV2NatalSnapshot(
      planets: planets,
      houses: houses,
      angles: angles,
      aspects: aspects,
    );
  }
}

// ─── Repository ───────────────────────────────────────────────

class NatalRepository {
  NatalRepository({ApiClient? client}) : _client = client ?? ApiClient();

  final ApiClient _client;
  static const Duration _cacheTtl = Duration(minutes: 30);

  Future<HomeV2NatalSnapshot?> fetch({
    required Map<String, dynamic> profile,
  }) async {
    // Backend birth_date / birth_time / city alanlarını okuyor; ekstra
    // lat/lon/tz override'ı zararsız.
    final payload = <String, dynamic>{
      if (profile['birth_date'] != null) 'birth_date': profile['birth_date'],
      if (profile['birth_time'] != null) 'birth_time': profile['birth_time'],
      if (profile['place'] != null) 'birth_place': profile['place'],
      if (profile['city'] != null) 'city': profile['city'],
      if (profile['country'] != null) 'country': profile['country'],
      if (profile['timezone'] != null) 'timezone': profile['timezone'],
      if (profile['latitude'] != null) 'latitude': profile['latitude'],
      if (profile['longitude'] != null) 'longitude': profile['longitude'],
    };
    final response = await _client.post(
      '/api/calculate-natal-chart',
      data: payload,
      cacheTtl: _cacheTtl,
      receiveTimeout: const Duration(seconds: 40),
      requestSla: ApiRequestSla.background,
    );
    final data = response.data;
    if (data is! Map) return null;
    return HomeV2NatalSnapshot.fromMap(Map<String, dynamic>.from(data));
  }
}

// ─── Provider ─────────────────────────────────────────────────

final homeV2NatalProvider = FutureProvider<HomeV2NatalSnapshot?>((ref) async {
  final profile = await ref
      .watch(userProfileProvider.future)
      .timeout(
        const Duration(seconds: 6),
        onTimeout: () => throw TimeoutException(
          'Profil yüklenemedi (6sn timeout)',
          const Duration(seconds: 6),
        ),
      );
  if (profile == null) return null;

  final repo = NatalRepository();
  return repo
      .fetch(profile: profile)
      .timeout(
        const Duration(seconds: 25),
        onTimeout: () => throw TimeoutException(
          'calculate-natal-chart 25sn timeout',
          const Duration(seconds: 25),
        ),
      );
});

// ─── helpers ──────────────────────────────────────────────────

double _asDouble(Object? v) {
  if (v is num) return v.toDouble();
  if (v is String) return double.tryParse(v) ?? 0;
  return 0;
}

int _asInt(Object? v) {
  if (v is int) return v;
  if (v is num) return v.toInt();
  if (v is String) return int.tryParse(v) ?? 0;
  return 0;
}
