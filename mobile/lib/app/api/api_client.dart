import 'dart:async';
import 'dart:convert';

import 'package:dio/dio.dart';
import 'package:mobile/app/telemetry/perf_telemetry.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import 'api_environment.dart';

enum ApiRequestSla { fast, interactive, background }

class ApiClient {
  ApiClient({String? baseUrl})
    : _baseUrl = ApiEnvironment.resolveBaseUrl(baseUrl),
      _dio = _dioPool.putIfAbsent(
        ApiEnvironment.resolveBaseUrl(baseUrl),
        () => _buildDio(ApiEnvironment.resolveBaseUrl(baseUrl)),
      );

  final String _baseUrl;
  final Dio _dio;
  static final Map<String, Dio> _dioPool = <String, Dio>{};
  static final Map<String, _CachedResponse> _responseCache =
      <String, _CachedResponse>{};
  static final Map<String, Future<Response<dynamic>>> _inflightRequests =
      <String, Future<Response<dynamic>>>{};

  static Duration timeoutFor(ApiRequestSla sla) {
    return switch (sla) {
      ApiRequestSla.fast => const Duration(seconds: 3),
      ApiRequestSla.interactive => const Duration(seconds: 8),
      ApiRequestSla.background => const Duration(seconds: 18),
    };
  }

  static Dio _buildDio(String baseUrl) {
    final dio = Dio(
      BaseOptions(
        baseUrl: baseUrl,
        connectTimeout: const Duration(seconds: 10),
        receiveTimeout: const Duration(seconds: 20),
      ),
    );
    dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          final token =
              Supabase.instance.client.auth.currentSession?.accessToken;
          if (token != null && token.isNotEmpty) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          handler.next(options);
        },
      ),
    );
    return dio;
  }

  Future<Response<dynamic>> post(
    String path, {
    Object? data,
    Duration? receiveTimeout,
    ApiRequestSla? requestSla,
    Duration? cacheTtl,
  }) {
    return _request(
      method: 'POST',
      path: path,
      data: data,
      receiveTimeout: receiveTimeout,
      requestSla: requestSla,
      cacheTtl: cacheTtl,
    );
  }

  Future<Response<dynamic>> get(
    String path, {
    Map<String, dynamic>? queryParameters,
    Duration? receiveTimeout,
    ApiRequestSla? requestSla,
    Duration? cacheTtl,
  }) {
    return _request(
      method: 'GET',
      path: path,
      queryParameters: queryParameters,
      receiveTimeout: receiveTimeout,
      requestSla: requestSla,
      cacheTtl: cacheTtl,
    );
  }

  Future<Response<dynamic>> delete(
    String path, {
    Object? data,
    Map<String, dynamic>? queryParameters,
    Duration? receiveTimeout,
    ApiRequestSla? requestSla,
  }) {
    return _request(
      method: 'DELETE',
      path: path,
      data: data,
      queryParameters: queryParameters,
      receiveTimeout: receiveTimeout,
      requestSla: requestSla,
    );
  }

  Future<Response<dynamic>> _request({
    required String method,
    required String path,
    Object? data,
    Map<String, dynamic>? queryParameters,
    Duration? receiveTimeout,
    ApiRequestSla? requestSla,
    Duration? cacheTtl,
  }) {
    final requestKey = _buildRequestKey(
      method: method,
      path: path,
      data: data,
      queryParameters: queryParameters,
    );
    final now = DateTime.now();
    final baseTelemetry = <String, Object?>{
      'endpoint': path,
      'method': method,
      'request_sla': requestSla?.name ?? '',
      'client_cache_enabled': cacheTtl != null,
    };

    if (cacheTtl != null) {
      final cached = _responseCache[requestKey];
      if (cached != null && cached.expiresAt.isAfter(now)) {
        final span = PerfTelemetry.startSpan(
          'api_request',
          data: baseTelemetry,
        );
        final response = cached.toResponse(
          path: path,
          baseUrl: _baseUrl,
          telemetry: <String, Object?>{
            ...baseTelemetry,
            'cache_status': 'hit',
            'inflight_dedupe': false,
            'status_code': cached.statusCode ?? 200,
            'payload_bytes': _payloadSizeBytes(cached.data),
            'payload_kb': _payloadSizeKb(cached.data),
          },
        );
        span.finish(
          data: Map<String, Object?>.from(
            response.requestOptions.extra['api_telemetry'] as Map,
          ),
        );
        return Future<Response<dynamic>>.value(response);
      }
      if (cached != null && !cached.expiresAt.isAfter(now)) {
        _responseCache.remove(requestKey);
      }
    }

    final inflight = _inflightRequests[requestKey];
    if (inflight != null) {
      PerfTelemetry.logPoint(
        'api_request_deduped',
        data: <String, Object?>{...baseTelemetry, 'inflight_dedupe': true},
      );
      return inflight;
    }

    final span = PerfTelemetry.startSpan('api_request', data: baseTelemetry);
    final future =
        _send(
              method: method,
              path: path,
              data: data,
              queryParameters: queryParameters,
              receiveTimeout: receiveTimeout,
              requestSla: requestSla,
            )
            .then((response) {
              final telemetry = <String, Object?>{
                ...baseTelemetry,
                'cache_status': cacheTtl != null ? 'miss' : 'disabled',
                'cache_store':
                    cacheTtl != null && (response.statusCode ?? 200) < 400,
                'inflight_dedupe': false,
                'status_code': response.statusCode ?? 0,
                'payload_bytes': _payloadSizeBytes(response.data),
                'payload_kb': _payloadSizeKb(response.data),
              };
              _attachTelemetry(response, telemetry);
              if (cacheTtl != null && (response.statusCode ?? 200) < 400) {
                _responseCache[requestKey] = _CachedResponse.fromResponse(
                  response,
                  expiresAt: now.add(cacheTtl),
                );
              }
              span.finish(data: telemetry);
              return response;
            })
            .catchError((error) {
              final statusCode = error is DioException
                  ? error.response?.statusCode
                  : null;
              span.finish(
                status: 'error',
                data: <String, Object?>{
                  ...baseTelemetry,
                  'cache_status': cacheTtl != null ? 'miss' : 'disabled',
                  'inflight_dedupe': false,
                  'status_code': statusCode ?? 0,
                  'error_type': error.runtimeType.toString(),
                },
              );
              throw error;
            })
            .whenComplete(() {
              _inflightRequests.remove(requestKey);
            });

    _inflightRequests[requestKey] = future;
    return future;
  }

  Future<Response<dynamic>> _send({
    required String method,
    required String path,
    Object? data,
    Map<String, dynamic>? queryParameters,
    Duration? receiveTimeout,
    ApiRequestSla? requestSla,
  }) {
    final effectiveTimeout =
        receiveTimeout ?? (requestSla == null ? null : timeoutFor(requestSla));
    final options = Options(
      method: method,
      responseType: ResponseType.json,
      receiveTimeout: effectiveTimeout,
      sendTimeout: effectiveTimeout,
    );
    return _dio.request<dynamic>(
      path,
      data: data,
      queryParameters: queryParameters,
      options: options,
    );
  }

  String _buildRequestKey({
    required String method,
    required String path,
    Object? data,
    Map<String, dynamic>? queryParameters,
  }) {
    final authUserId = Supabase.instance.client.auth.currentUser?.id ?? 'anon';
    return jsonEncode(<String, dynamic>{
      'baseUrl': _baseUrl,
      'method': method,
      'path': path,
      'user': authUserId,
      'data': _normalize(data),
      'query': _normalize(queryParameters),
    });
  }

  dynamic _normalize(Object? value) {
    if (value == null) {
      return null;
    }
    if (value is Map) {
      final entries = value.entries.toList()
        ..sort((a, b) => a.key.toString().compareTo(b.key.toString()));
      return <String, dynamic>{
        for (final entry in entries)
          entry.key.toString(): _normalize(entry.value),
      };
    }
    if (value is List) {
      return value.map(_normalize).toList(growable: false);
    }
    if (value is DateTime) {
      return value.toIso8601String();
    }
    return value;
  }

  static void _attachTelemetry(
    Response<dynamic> response,
    Map<String, Object?> telemetry,
  ) {
    response.requestOptions.extra['api_telemetry'] = telemetry;
  }

  static int _payloadSizeBytes(Object? value) {
    try {
      return utf8.encode(jsonEncode(value)).length;
    } catch (_) {
      return utf8.encode(value?.toString() ?? '').length;
    }
  }

  static double _payloadSizeKb(Object? value) {
    return double.parse((_payloadSizeBytes(value) / 1024).toStringAsFixed(3));
  }
}

class _CachedResponse {
  const _CachedResponse({
    required this.data,
    required this.statusCode,
    required this.expiresAt,
  });

  final dynamic data;
  final int? statusCode;
  final DateTime expiresAt;

  factory _CachedResponse.fromResponse(
    Response<dynamic> response, {
    required DateTime expiresAt,
  }) {
    return _CachedResponse(
      data: _deepCopy(response.data),
      statusCode: response.statusCode,
      expiresAt: expiresAt,
    );
  }

  Response<dynamic> toResponse({
    required String path,
    required String baseUrl,
    Map<String, Object?> telemetry = const <String, Object?>{},
  }) {
    return Response<dynamic>(
      requestOptions: RequestOptions(
        path: path,
        baseUrl: baseUrl,
        extra: <String, dynamic>{'api_telemetry': telemetry},
      ),
      data: _deepCopy(data),
      statusCode: statusCode,
    );
  }

  static dynamic _deepCopy(dynamic value) {
    try {
      return jsonDecode(jsonEncode(value));
    } catch (_) {
      return value;
    }
  }
}
