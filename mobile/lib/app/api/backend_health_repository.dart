import 'package:dio/dio.dart';

import 'api_client.dart';
import 'api_environment.dart';

class BackendHealthSnapshot {
  const BackendHealthSnapshot({
    required this.baseUrl,
    required this.statusCode,
    required this.reachable,
    required this.backendStatus,
    required this.supabaseOk,
    required this.supabaseMessage,
    required this.responseTime,
  });

  final String baseUrl;
  final int? statusCode;
  final bool reachable;
  final String backendStatus;
  final bool? supabaseOk;
  final String supabaseMessage;
  final Duration responseTime;

  factory BackendHealthSnapshot.fromResponse(
    Response<dynamic> response,
    Duration responseTime,
  ) {
    final data = _asMap(response.data);
    final status = (data['status'] ?? '').toString().trim();
    return BackendHealthSnapshot(
      baseUrl: ApiEnvironment.apiBaseUrl,
      statusCode: response.statusCode,
      reachable: true,
      backendStatus: status.isEmpty ? 'unknown' : status,
      supabaseOk: data['supabase'] is bool ? data['supabase'] as bool : null,
      supabaseMessage: (data['supabase_message'] ?? '').toString().trim(),
      responseTime: responseTime,
    );
  }

  static Map<String, dynamic> _asMap(dynamic data) {
    if (data is Map<String, dynamic>) {
      return data;
    }
    if (data is Map) {
      return Map<String, dynamic>.from(data);
    }
    return const <String, dynamic>{};
  }
}

class BackendHealthRepository {
  BackendHealthRepository({ApiClient? client})
    : _client = client ?? ApiClient();

  final ApiClient _client;

  Future<BackendHealthSnapshot> fetchHealth() async {
    final stopwatch = Stopwatch()..start();
    final response = await _client.get('/api/health');
    stopwatch.stop();
    return BackendHealthSnapshot.fromResponse(response, stopwatch.elapsed);
  }
}
