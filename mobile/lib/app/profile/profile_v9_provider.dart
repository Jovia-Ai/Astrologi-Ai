// Profile v9 natal provider — `/interpret/ui` payload'ını çağırır,
// `ProfileV9Adapter` ile domain data'sına dönüştürür.
//
// Legacy `_loadNatalInterpretation` (profile_page.dart:1961+) ağır
// telemetry + fallback chain içeriyor. v9'da sade bir Riverpod
// FutureProvider yeterli — cache TTL'i ApiClient katmanında zaten var.

import 'package:dio/dio.dart' show DioException;
import 'package:flutter/foundation.dart' show debugPrint, kDebugMode;
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:mobile/app/api/api_client.dart';
import 'package:mobile/app/performance/load_tuning.dart';
import 'package:mobile/app/profile/profile_providers.dart';
import 'package:mobile/app/profile/profile_v9_adapter.dart';
import 'package:mobile/app/timing/transit_repositories.dart';

/// `ProfileV9Data` — natal yorumu yüklendikten sonra adapter çıktısı.
/// `null` döner: doğum bilgisi eksik VEYA payload boş geldiğinde.
final profileV9DataProvider = FutureProvider<ProfileV9Data?>((ref) async {
  final profileAsync = ref.watch(userProfileProvider);
  final supabaseProfile = profileAsync.asData?.value;
  if (supabaseProfile == null) return null;
  if (!_hasBirthData(supabaseProfile)) {
    // Doğum bilgisi yoksa hero'yu yine de adapter ile üretelim;
    // narrative bölümler boş olur ama UI hero'yu render eder.
    return ProfileV9Adapter.fromInputs(
      natalPayload: null,
      supabaseProfile: supabaseProfile,
    );
  }

  final natalPayload = await _fetchInterpretUi(supabaseProfile);
  return ProfileV9Adapter.fromInputs(
    natalPayload: natalPayload,
    supabaseProfile: supabaseProfile,
  );
});

bool _hasBirthData(Map<String, dynamic> profile) {
  final birthDate = (profile['birth_date'] ?? '').toString().trim();
  final birthTime = (profile['birth_time'] ?? '').toString().trim();
  final city = (profile['city'] ?? '').toString().trim();
  final country = (profile['country'] ?? '').toString().trim();
  final place = (profile['place'] ?? '').toString().trim();
  return birthDate.isNotEmpty &&
      birthTime.isNotEmpty &&
      (city.isNotEmpty || country.isNotEmpty || place.isNotEmpty);
}

Future<Map<String, dynamic>?> _fetchInterpretUi(
  Map<String, dynamic> profile,
) async {
  final city = (profile['city'] ?? '').toString().trim();
  final country = (profile['country'] ?? '').toString().trim();
  final placeRaw = (profile['place'] ?? '').toString().trim();
  final place = placeRaw.isNotEmpty
      ? placeRaw
      : (city.isEmpty
            ? country
            : (country.isEmpty ? city : '$city, $country'));

  final body = <String, dynamic>{
    'birth_date': (profile['birth_date'] ?? '').toString().trim(),
    'birth_time': TransitRequestBuilder.normalizeBirthTime(
      (profile['birth_time'] ?? '').toString(),
    ),
    'birth_place': place,
    'locale': 'tr',
    'include_full_profile': true,
  };
  TransitRequestBuilder.appendKnownLocationFields(body, profile: profile);

  try {
    final client = ApiClient();
    // include_full_profile hem query string hem body'de — backend'in
    // her iki kanaldan da okuduğunu varsayıyoruz, query ile garanti.
    final response = await client.post(
      '/interpret/ui?include_full_profile=true',
      data: body,
      cacheTtl: LoadTuning.profileNatalCacheTtl,
      receiveTimeout: LoadTuning.profileInterpretUiTimeout,
      requestSla: LoadTuning.profileInterpretUiRequestSla,
    );
    final data = response.data;
    if (data is Map<String, dynamic>) return data;
    if (data is Map) {
      return data.map((k, v) => MapEntry(k.toString(), v));
    }
    return null;
  } on DioException catch (e) {
    if (kDebugMode) {
      debugPrint(
        '[profile_v9] /interpret/ui DioException '
        'status=${e.response?.statusCode} type=${e.type.name}',
      );
    }
    return null;
  } catch (e) {
    if (kDebugMode) {
      debugPrint('[profile_v9] /interpret/ui error: $e');
    }
    return null;
  }
}
