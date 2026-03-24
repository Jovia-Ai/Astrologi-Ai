import 'package:dio/dio.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import 'api_environment.dart';

class ApiClient {
  ApiClient({String? baseUrl})
    : _dio = Dio(
        BaseOptions(
          baseUrl: ApiEnvironment.resolveBaseUrl(baseUrl),
          connectTimeout: const Duration(seconds: 10),
          receiveTimeout: const Duration(seconds: 20),
        ),
      ) {
    _dio.interceptors.add(
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
  }

  final Dio _dio;

  Future<Response<dynamic>> post(
    String path, {
    Object? data,
    Duration? receiveTimeout,
  }) {
    return _dio.post(
      path,
      data: data,
      options: Options(
        responseType: ResponseType.json,
        receiveTimeout: receiveTimeout,
        sendTimeout: receiveTimeout,
      ),
    );
  }

  Future<Response<dynamic>> get(
    String path, {
    Map<String, dynamic>? queryParameters,
    Duration? receiveTimeout,
  }) {
    return _dio.get(
      path,
      queryParameters: queryParameters,
      options: Options(
        responseType: ResponseType.json,
        receiveTimeout: receiveTimeout,
        sendTimeout: receiveTimeout,
      ),
    );
  }
}
