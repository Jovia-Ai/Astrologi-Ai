import 'dart:async';
import 'dart:convert';

import 'package:dio/dio.dart';
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

    if (cacheTtl != null) {
      final cached = _responseCache[requestKey];
      if (cached != null && cached.expiresAt.isAfter(now)) {
        return Future<Response<dynamic>>.value(
          cached.toResponse(path: path, baseUrl: _baseUrl),
        );
      }
      if (cached != null && !cached.expiresAt.isAfter(now)) {
        _responseCache.remove(requestKey);
      }
    }

    final inflight = _inflightRequests[requestKey];
    if (inflight != null) {
      return inflight;
    }

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
              if (cacheTtl != null && (response.statusCode ?? 200) < 400) {
                _responseCache[requestKey] = _CachedResponse.fromResponse(
                  response,
                  expiresAt: now.add(cacheTtl),
                );
              }
              return response;
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
  }) {
    return Response<dynamic>(
      requestOptions: RequestOptions(path: path, baseUrl: baseUrl),
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
