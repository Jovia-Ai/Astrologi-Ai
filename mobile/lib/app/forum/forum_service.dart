import 'package:mobile/app/api/api_client.dart';
import 'package:mobile/app/forum/forum_models.dart';
import 'package:mobile/l10n/current_localizations.dart';

class ForumService {
  ForumService({ApiClient? client}) : _client = client ?? ApiClient();

  final ApiClient _client;

  static const _base = '/api/forum';

  Future<List<ForumPost>> fetchPosts({
    String category = 'all',
    int limit = 20,
    int offset = 0,
  }) async {
    final res = await _client.get(
      '$_base/posts',
      queryParameters: {'category': category, 'limit': limit, 'offset': offset},
      cacheTtl: const Duration(seconds: 30),
    );
    final data = res.data as Map<String, dynamic>?;
    final list = data?['posts'] as List<dynamic>? ?? [];
    return list
        .cast<Map<String, dynamic>>()
        .map(ForumPost.fromJson)
        .toList(growable: false);
  }

  Future<({ForumPost post, List<ForumReply> replies})> fetchPostDetail(
    String postId,
  ) async {
    final res = await _client.get('$_base/posts/$postId');
    final data = res.data as Map<String, dynamic>;
    final post = ForumPost.fromJson(data['post'] as Map<String, dynamic>);
    final replies = (data['replies'] as List<dynamic>? ?? [])
        .cast<Map<String, dynamic>>()
        .map(ForumReply.fromJson)
        .toList(growable: false);
    return (post: post, replies: replies);
  }

  Future<ForumPost> createPost({
    required String title,
    required String body,
    required String category,
    String? activeTransit,
  }) async {
    final res = await _client.post(
      '$_base/posts',
      data: {
        'title': title,
        'body': body,
        'category': category,
        ...?activeTransit == null
            ? null
            : <String, dynamic>{'active_transit': activeTransit},
      },
    );
    return ForumPost.fromJson(res.data as Map<String, dynamic>);
  }

  Future<({bool liked, int likeCount})> toggleLike(String postId) async {
    final res = await _client.post('$_base/posts/$postId/like');
    final data = res.data as Map<String, dynamic>;
    return (
      liked: data['liked'] as bool? ?? false,
      likeCount: (data['like_count'] as num?)?.toInt() ?? 0,
    );
  }

  Future<ForumReply> addReply({
    required String postId,
    required String body,
  }) async {
    final res = await _client.post(
      '$_base/posts/$postId/replies',
      data: {'body': body},
    );
    return ForumReply.fromJson(res.data as Map<String, dynamic>);
  }

  Future<String> fetchActiveTransit() async {
    final l10n = currentL10n();
    try {
      final res = await _client.get(
        '$_base/active-transit',
        cacheTtl: const Duration(minutes: 30),
      );
      final data = res.data as Map<String, dynamic>?;
      return data?['label'] as String? ?? l10n.forumActiveTransitFallback;
    } catch (_) {
      return l10n.forumActiveTransitFallback;
    }
  }
}
