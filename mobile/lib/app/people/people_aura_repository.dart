import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';

import 'package:mobile/app/api/api_client.dart';
import 'package:mobile/app/profile/profile_models.dart';
import 'package:mobile/design/widgets/jovia_aura.dart';

import 'person_profile.dart';

@immutable
class PersonAuraRequest {
  const PersonAuraRequest({
    required this.personId,
    required this.birthDate,
    required this.birthTime,
    required this.place,
    required this.seedKey,
  });

  factory PersonAuraRequest.fromPerson(PersonProfile person) {
    return PersonAuraRequest(
      personId: person.id,
      birthDate: person.birthDate,
      birthTime: person.normalizedBirthTime,
      place: person.place,
      seedKey: person.auraSeedKey,
    );
  }

  final String personId;
  final String birthDate;
  final String birthTime;
  final String place;
  final String seedKey;

  bool get hasEnoughData =>
      birthDate.trim().isNotEmpty &&
      birthTime.trim().isNotEmpty &&
      place.trim().isNotEmpty;

  @override
  bool operator ==(Object other) {
    return other is PersonAuraRequest &&
        other.personId == personId &&
        other.birthDate == birthDate &&
        other.birthTime == birthTime &&
        other.place == place &&
        other.seedKey == seedKey;
  }

  @override
  int get hashCode =>
      Object.hash(personId, birthDate, birthTime, place, seedKey);
}

class PeopleAuraRepository {
  PeopleAuraRepository({ApiClient? client}) : _client = client ?? ApiClient();

  static const Duration _cacheTtl = Duration(hours: 6);
  static const String _payloadVersion = 'natal_profile_v3_2026_04_02';

  final ApiClient _client;

  Future<JoviaAuraSemantic?> getAuraSemantic({
    required PersonAuraRequest request,
    String locale = 'tr',
  }) async {
    if (!request.hasEnoughData) {
      return null;
    }

    final payload = <String, dynamic>{
      'birth_date': request.birthDate.trim(),
      'birth_time': request.birthTime.trim(),
      'birth_place': request.place.trim(),
      'locale': locale.trim().isEmpty ? 'tr' : locale.trim(),
      'client_surface_version': _payloadVersion,
    };

    try {
      final response = await _client.post(
        '/interpret/ui',
        data: payload,
        requestSla: ApiRequestSla.interactive,
        cacheTtl: _cacheTtl,
      );
      final map = _asMap(response.data);
      if (map.isEmpty) {
        return null;
      }
      final parsed = _extractPersonalityImprint(map);
      if (parsed == null) {
        return null;
      }
      return _extractAuraSemantic(parsed);
    } on DioException catch (_) {
      return null;
    } catch (_) {
      return null;
    }
  }
}

Map<String, dynamic> _asMap(dynamic data) {
  if (data is Map<String, dynamic>) {
    return data;
  }
  if (data is Map) {
    return Map<String, dynamic>.from(data);
  }
  return <String, dynamic>{};
}

List<Map<String, dynamic>> _natalScopes(Map<String, dynamic> map) {
  final scopes = <Map<String, dynamic>>[map];
  final public = _asMap(map['public']);
  if (public.isNotEmpty) {
    scopes.add(public);
  }
  final metaInfo = _asMap(map['meta_info']);
  if (metaInfo.isNotEmpty) {
    scopes.add(metaInfo);
  }
  return scopes;
}

PersonalityImprintProfile? _extractPersonalityImprint(
  Map<String, dynamic> map,
) {
  for (final scope in _natalScopes(map)) {
    final raw = scope['personality_imprint'];
    if (raw is! Map) {
      continue;
    }
    final parsed = PersonalityImprintProfile.fromMap(
      Map<String, dynamic>.from(raw),
    );
    if (parsed.hasContent || parsed.hasExtraContent) {
      return parsed;
    }
  }
  return null;
}

JoviaAuraSemantic? _extractAuraSemantic(PersonalityImprintProfile profile) {
  for (final entries in <List<PersonalityImprintEntry>>[
    profile.entries,
    profile.supportEntries,
    profile.extraEntries,
  ]) {
    for (final entry in entries) {
      final semantic = joviaAuraSemanticFromText(
        auraText: entry.aura,
        sourceLabel: entry.labelTr,
      );
      if (semantic != null) {
        return semantic;
      }
    }
  }
  return null;
}
