import 'package:flutter/foundation.dart';

import 'package:mobile/app/api/api_client.dart';

import 'chart_wheel_data.dart';

class ChartWheelRepository {
  ChartWheelRepository({ApiClient? client}) : _client = client ?? ApiClient();

  final ApiClient _client;
  static const Duration _cacheTtl = Duration(minutes: 30);

  Future<ChartWheelData?> fetch({required Map<String, dynamic> profile}) async {
    final payload = buildChartWheelPayload(profile);
    if (payload.isEmpty) {
      return null;
    }

    final response = await _client.post(
      '/api/calculate-natal-chart',
      data: payload,
      cacheTtl: _cacheTtl,
      receiveTimeout: const Duration(seconds: 40),
      requestSla: ApiRequestSla.background,
    );
    final data = response.data;
    if (data is! Map) {
      return null;
    }
    return ChartWheelData.tryFromChartResponse(Map<String, dynamic>.from(data));
  }
}

@visibleForTesting
Map<String, dynamic> buildChartWheelPayload(Map<String, dynamic> profile) {
  final birthDate = (profile['birth_date'] ?? '').toString().trim();
  final birthTime = _normalizeChartWheelBirthTime(
    (profile['birth_time'] ?? '').toString(),
  );
  final place = _chartWheelPlaceLabel(profile);
  if (birthDate.isEmpty || birthTime.isEmpty || place.isEmpty) {
    return const <String, dynamic>{};
  }

  return <String, dynamic>{
    'birth_date': birthDate,
    'birth_time': birthTime,
    'birth_place': place,
    if (profile['country'] != null) 'country': profile['country'],
    if (profile['timezone'] != null) 'timezone': profile['timezone'],
    if (profile['latitude'] != null) 'latitude': profile['latitude'],
    if (profile['longitude'] != null) 'longitude': profile['longitude'],
  };
}

String _normalizeChartWheelBirthTime(String raw) {
  final text = raw.trim();
  if (text.isEmpty) {
    return '';
  }
  final parts = text.split(':');
  if (parts.length < 2) {
    return text;
  }
  final hour = parts[0].padLeft(2, '0');
  final minute = parts[1].padLeft(2, '0');
  return '$hour:$minute';
}

String _chartWheelPlaceLabel(Map<String, dynamic> profile) {
  final place = (profile['place'] ?? '').toString().trim();
  if (place.isNotEmpty) {
    return place;
  }
  final city = (profile['city'] ?? '').toString().trim();
  final country = (profile['country'] ?? '').toString().trim();
  if (city.isEmpty) {
    return country;
  }
  if (country.isEmpty) {
    return city;
  }
  return '$city, $country';
}
