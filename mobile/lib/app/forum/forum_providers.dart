import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile/app/forum/forum_models.dart';
import 'package:mobile/app/forum/forum_service.dart';

final forumServiceProvider = Provider<ForumService>((_) => ForumService());

final forumNotifierProvider = StateNotifierProvider<ForumNotifier, ForumState>((
  ref,
) {
  return ForumNotifier(ref.read(forumServiceProvider));
});

class ForumNotifier extends StateNotifier<ForumState> {
  ForumNotifier(this._service) : super(const ForumState()) {
    _init();
  }

  final ForumService _service;

  Future<void> _init() async {
    await Future.wait([loadPosts(), _loadTransit()]);
  }

  Future<void> _loadTransit() async {
    final label = await _service.fetchActiveTransit();
    if (mounted) state = state.copyWith(activeTransit: label);
  }

  Future<void> loadPosts({bool refresh = false}) async {
    if (state.isLoading) return;
    state = state.copyWith(isLoading: true, error: null);
    try {
      final posts = await _service.fetchPosts(
        category: state.selectedCategory,
        offset: 0,
      );
      state = state.copyWith(
        posts: posts,
        isLoading: false,
        hasMore: posts.length == 20,
      );
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<void> selectCategory(String category) async {
    if (state.selectedCategory == category) return;
    state = state.copyWith(selectedCategory: category, posts: [], error: null);
    await loadPosts();
  }

  Future<ForumPost?> submitPost({
    required String title,
    required String body,
    required String category,
    String? activeTransit,
  }) async {
    try {
      final post = await _service.createPost(
        title: title,
        body: body,
        category: category,
        activeTransit: activeTransit ?? state.activeTransit,
      );
      state = state.copyWith(posts: [post, ...state.posts], error: null);
      return post;
    } catch (_) {
      return null;
    }
  }

  void syncPost(ForumPost post) {
    final index = state.posts.indexWhere((item) => item.id == post.id);
    if (index == -1) {
      return;
    }
    final updated = [...state.posts];
    updated[index] = post;
    state = state.copyWith(posts: updated);
  }

  Future<void> toggleLike(String postId) async {
    final idx = state.posts.indexWhere((p) => p.id == postId);
    if (idx == -1) return;
    final post = state.posts[idx];
    // Optimistic update
    final optimistic = post.copyWith(
      isLikedByMe: !post.isLikedByMe,
      likeCount: post.isLikedByMe ? post.likeCount - 1 : post.likeCount + 1,
    );
    final updated = [...state.posts];
    updated[idx] = optimistic;
    state = state.copyWith(posts: updated);

    try {
      final result = await _service.toggleLike(postId);
      final settled = optimistic.copyWith(
        isLikedByMe: result.liked,
        likeCount: result.likeCount,
      );
      final finalList = [...state.posts];
      final newIdx = finalList.indexWhere((p) => p.id == postId);
      if (newIdx != -1) finalList[newIdx] = settled;
      state = state.copyWith(posts: finalList);
    } catch (_) {
      // Revert on error
      final reverted = [...state.posts];
      final revertIdx = reverted.indexWhere((p) => p.id == postId);
      if (revertIdx != -1) reverted[revertIdx] = post;
      state = state.copyWith(posts: reverted);
    }
  }
}
