import 'package:flutter/material.dart';
import 'package:mobile/app/timing/turkish_text.dart';

class ForumPost {
  const ForumPost({
    required this.id,
    required this.userId,
    required this.userDisplayName,
    required this.userSunSign,
    required this.userRisingSign,
    required this.category,
    required this.title,
    required this.body,
    this.activeTransit,
    required this.likeCount,
    required this.replyCount,
    required this.createdAt,
    required this.isLikedByMe,
  });

  final String id;
  final String userId;
  final String userDisplayName;
  final String userSunSign;
  final String userRisingSign;
  final String category;
  final String title;
  final String body;
  final String? activeTransit;
  final int likeCount;
  final int replyCount;
  final DateTime createdAt;
  final bool isLikedByMe;

  factory ForumPost.fromJson(Map<String, dynamic> json) {
    return ForumPost(
      id: json['id'] as String? ?? '',
      userId: json['user_id'] as String? ?? '',
      userDisplayName: json['user_display_name'] as String? ?? 'Anonim',
      userSunSign: json['user_sun_sign'] as String? ?? '',
      userRisingSign: json['user_rising_sign'] as String? ?? '',
      category: json['category'] as String? ?? 'genel',
      title: json['title'] as String? ?? '',
      body: json['body'] as String? ?? '',
      activeTransit: json['active_transit'] as String?,
      likeCount: (json['like_count'] as num?)?.toInt() ?? 0,
      replyCount: (json['reply_count'] as num?)?.toInt() ?? 0,
      createdAt: json['created_at'] != null
          ? DateTime.tryParse(json['created_at'] as String) ?? DateTime.now()
          : DateTime.now(),
      isLikedByMe: json['is_liked_by_me'] as bool? ?? false,
    );
  }

  ForumPost copyWith({int? likeCount, bool? isLikedByMe, int? replyCount}) {
    return ForumPost(
      id: id,
      userId: userId,
      userDisplayName: userDisplayName,
      userSunSign: userSunSign,
      userRisingSign: userRisingSign,
      category: category,
      title: title,
      body: body,
      activeTransit: activeTransit,
      likeCount: likeCount ?? this.likeCount,
      replyCount: replyCount ?? this.replyCount,
      createdAt: createdAt,
      isLikedByMe: isLikedByMe ?? this.isLikedByMe,
    );
  }

  Color get avatarColor {
    final hash = userSunSign.isEmpty ? userId.hashCode : userSunSign.hashCode;
    final hue = (hash.abs() % 360).toDouble();
    return HSLColor.fromAHSL(1.0, hue, 0.35, 0.28).toColor();
  }

  String get initials {
    final parts = userDisplayName.trim().split(' ');
    if (parts.isEmpty) return '?';
    if (parts.length == 1) return turkishToUpper(parts.first.substring(0, 1));
    return turkishToUpper(
      parts.first.substring(0, 1) + parts.last.substring(0, 1),
    );
  }
}

class ForumReply {
  const ForumReply({
    required this.id,
    required this.postId,
    required this.userId,
    required this.userDisplayName,
    required this.userSunSign,
    required this.body,
    required this.likeCount,
    required this.createdAt,
  });

  final String id;
  final String postId;
  final String userId;
  final String userDisplayName;
  final String userSunSign;
  final String body;
  final int likeCount;
  final DateTime createdAt;

  factory ForumReply.fromJson(Map<String, dynamic> json) {
    return ForumReply(
      id: json['id'] as String? ?? '',
      postId: json['post_id'] as String? ?? '',
      userId: json['user_id'] as String? ?? '',
      userDisplayName: json['user_display_name'] as String? ?? 'Anonim',
      userSunSign: json['user_sun_sign'] as String? ?? '',
      body: json['body'] as String? ?? '',
      likeCount: (json['like_count'] as num?)?.toInt() ?? 0,
      createdAt: json['created_at'] != null
          ? DateTime.tryParse(json['created_at'] as String) ?? DateTime.now()
          : DateTime.now(),
    );
  }

  String get initials {
    final parts = userDisplayName.trim().split(' ');
    if (parts.isEmpty) return '?';
    if (parts.length == 1) return turkishToUpper(parts.first.substring(0, 1));
    return turkishToUpper(
      parts.first.substring(0, 1) + parts.last.substring(0, 1),
    );
  }
}

class ForumState {
  const ForumState({
    this.posts = const [],
    this.isLoading = false,
    this.selectedCategory = 'all',
    this.hasMore = false,
    this.error,
    this.activeTransit = 'Gökyüzü hareketli',
  });

  final List<ForumPost> posts;
  final bool isLoading;
  final String selectedCategory;
  final bool hasMore;
  final String? error;
  final String activeTransit;

  ForumState copyWith({
    List<ForumPost>? posts,
    bool? isLoading,
    String? selectedCategory,
    bool? hasMore,
    String? error,
    String? activeTransit,
  }) {
    return ForumState(
      posts: posts ?? this.posts,
      isLoading: isLoading ?? this.isLoading,
      selectedCategory: selectedCategory ?? this.selectedCategory,
      hasMore: hasMore ?? this.hasMore,
      error: error,
      activeTransit: activeTransit ?? this.activeTransit,
    );
  }
}
