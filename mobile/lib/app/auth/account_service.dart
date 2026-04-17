import 'package:dio/dio.dart';

import 'package:mobile/app/api/api_client.dart';

class AccountDeletionException implements Exception {
  const AccountDeletionException(this.message);

  final String message;

  @override
  String toString() => message;
}

class AccountService {
  AccountService({ApiClient? client}) : _client = client ?? ApiClient();

  final ApiClient _client;

  Future<void> deleteCurrentAccount() async {
    try {
      await _client.delete(
        '/api/users/me',
        requestSla: ApiRequestSla.background,
      );
    } on DioException catch (error) {
      throw AccountDeletionException(_dioMessage(error));
    }
  }

  static String _dioMessage(DioException error) {
    final data = error.response?.data;
    if (data is Map) {
      final detail = (data['detail'] ?? data['message'] ?? '').toString().trim();
      if (detail.isNotEmpty) {
        return detail;
      }
    }
    return 'Account deletion failed.';
  }
}
