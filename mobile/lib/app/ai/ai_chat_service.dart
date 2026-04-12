import 'package:dio/dio.dart';
import 'package:mobile/app/api/api_client.dart';

class AiChatException implements Exception {
  const AiChatException(this.message);

  final String message;

  @override
  String toString() => message;
}

class AiChatQuotaState {
  const AiChatQuotaState({
    required this.remainingFree,
    required this.creditsRemaining,
    required this.isPro,
  });

  final int remainingFree;
  final int creditsRemaining;
  final bool isPro;

  factory AiChatQuotaState.fromJson(Map<String, dynamic> json) {
    return AiChatQuotaState(
      remainingFree: (json['remaining_free'] as num?)?.toInt() ?? 0,
      creditsRemaining: (json['credits_remaining'] as num?)?.toInt() ?? 0,
      isPro: json['is_pro'] as bool? ?? false,
    );
  }
}

sealed class AiChatResult {
  const AiChatResult();
}

class AiChatSuccess extends AiChatResult {
  const AiChatSuccess({
    required this.text,
    required this.quotaState,
    this.conversationId,
  });

  final String text;
  final AiChatQuotaState quotaState;
  final String? conversationId;
}

class AiChatPaywall extends AiChatResult {
  const AiChatPaywall({required this.code, required this.message});

  final String code;
  final String message;
}

class AiChatService {
  AiChatService({ApiClient? client}) : _client = client ?? ApiClient();

  final ApiClient _client;

  Future<AiChatResult> sendMessage({
    required String message,
    String? conversationId,
  }) async {
    try {
      final response = await _client.post(
        '/v1/ai/chat',
        requestSla: ApiRequestSla.interactive,
        data: <String, dynamic>{
          'message': message,
          'conversation_id': conversationId,
        },
      );
      final data = _asMap(response.data);
      if (data['ok'] == true) {
        return AiChatSuccess(
          text: (data['text'] ?? '').toString(),
          quotaState: AiChatQuotaState.fromJson(data),
          conversationId: _stringOrNull(data['conversation_id']),
        );
      }
      if (data['paywall'] == true) {
        return AiChatPaywall(
          code: (data['code'] ?? 'QUOTA_EXCEEDED').toString(),
          message: (data['message'] ?? 'Free quota is exhausted').toString(),
        );
      }
      throw const AiChatException('Unexpected AI chat response.');
    } on DioException catch (error) {
      throw AiChatException(_dioMessage(error));
    }
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

  static String? _stringOrNull(dynamic value) {
    final text = value?.toString().trim() ?? '';
    return text.isEmpty ? null : text;
  }

  static String _dioMessage(DioException error) {
    final data = _asMap(error.response?.data);
    final detail = (data['detail'] ?? data['message'] ?? '').toString().trim();
    if (detail.isNotEmpty) {
      return detail;
    }
    return 'AI chat request failed.';
  }
}
