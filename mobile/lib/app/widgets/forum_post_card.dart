import 'package:flutter/material.dart';
import 'package:mobile/app/forum/forum_models.dart';

/// Reusable forum post card.
/// Displays post header, title, body preview, and footer actions.
class ForumPostCard extends StatefulWidget {
  const ForumPostCard({
    super.key,
    required this.post,
    required this.onTap,
    required this.onLike,
    this.animationIndex = 0,
  });

  final ForumPost post;
  final VoidCallback onTap;
  final VoidCallback onLike;
  final int animationIndex;

  @override
  State<ForumPostCard> createState() => _ForumPostCardState();
}

class _ForumPostCardState extends State<ForumPostCard>
    with SingleTickerProviderStateMixin {
  late AnimationController _likeController;
  late Animation<double> _likeScale;

  @override
  void initState() {
    super.initState();
    _likeController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 200),
    );
    _likeScale = TweenSequence<double>([
      TweenSequenceItem(tween: Tween(begin: 1.0, end: 1.4), weight: 50),
      TweenSequenceItem(tween: Tween(begin: 1.4, end: 1.0), weight: 50),
    ]).animate(CurvedAnimation(parent: _likeController, curve: Curves.easeOut));
  }

  @override
  void dispose() {
    _likeController.dispose();
    super.dispose();
  }

  void _handleLike() {
    _likeController.forward(from: 0);
    widget.onLike();
  }

  @override
  Widget build(BuildContext context) {
    final post = widget.post;
    return GestureDetector(
      onTap: widget.onTap,
      behavior: HitTestBehavior.opaque,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: const BoxDecoration(
          border: Border(
            bottom: BorderSide(color: Color(0xFF0E0E0E), width: 0.5),
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _PostHeader(post: post),
            const SizedBox(height: 10),
            Text(
              post.title,
              style: const TextStyle(
                fontFamily: 'Georgia',
                fontSize: 15,
                fontWeight: FontWeight.w600,
                color: Color(0xFFE0E0E0),
                height: 1.4,
              ),
            ),
            const SizedBox(height: 6),
            Text(
              post.body,
              maxLines: 3,
              overflow: TextOverflow.ellipsis,
              style: const TextStyle(
                fontSize: 12,
                color: Color(0xFF606060),
                height: 1.5,
              ),
            ),
            const SizedBox(height: 10),
            _PostFooter(
              post: post,
              likeScale: _likeScale,
              onLike: _handleLike,
            ),
          ],
        ),
      ),
    );
  }
}

class _PostHeader extends StatelessWidget {
  const _PostHeader({required this.post});
  final ForumPost post;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        CircleAvatar(
          radius: 16,
          backgroundColor: post.avatarColor,
          child: Text(
            post.initials,
            style: const TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.w600,
              color: Color(0xFFE0E0E0),
            ),
          ),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                post.userDisplayName,
                style: const TextStyle(
                  fontSize: 12,
                  color: Color(0xFF888888),
                  fontWeight: FontWeight.w500,
                ),
              ),
              if (post.userSunSign.isNotEmpty)
                Text(
                  post.userSunSign,
                  style: const TextStyle(
                    fontSize: 10,
                    color: Color(0xFF444444),
                    letterSpacing: 0.5,
                  ),
                ),
            ],
          ),
        ),
        _CategoryBadge(category: post.category),
      ],
    );
  }
}

class _CategoryBadge extends StatelessWidget {
  const _CategoryBadge({required this.category});
  final String category;

  static const _labels = <String, String>{
    'transit': 'Transit',
    'iliski': 'İlişki',
    'kariyer': 'Kariyer',
    'golge': 'Gölge',
    'genel': 'Genel',
  };

  static const _bgColors = <String, Color>{
    'transit': Color(0x1E7864C8),
    'iliski': Color(0x193CB474),
    'kariyer': Color(0x193C64C8),
    'golge': Color(0x19C85050),
    'genel': Color(0x19888888),
  };

  static const _textColors = <String, Color>{
    'transit': Color(0xFF7060C0),
    'iliski': Color(0xFF3A9060),
    'kariyer': Color(0xFF4060C0),
    'golge': Color(0xFFC06060),
    'genel': Color(0xFF666666),
  };

  @override
  Widget build(BuildContext context) {
    final bg = _bgColors[category] ?? const Color(0x19888888);
    final fg = _textColors[category] ?? const Color(0xFF666666);
    final label = _labels[category] ?? category;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 3),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(
        label.toUpperCase(),
        style: TextStyle(
          fontSize: 9,
          color: fg,
          fontWeight: FontWeight.w600,
          letterSpacing: 0.8,
        ),
      ),
    );
  }
}

class _PostFooter extends StatelessWidget {
  const _PostFooter({
    required this.post,
    required this.likeScale,
    required this.onLike,
  });

  final ForumPost post;
  final Animation<double> likeScale;
  final VoidCallback onLike;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        GestureDetector(
          onTap: onLike,
          child: ScaleTransition(
            scale: likeScale,
            child: Row(
              children: [
                Icon(
                  post.isLikedByMe ? Icons.favorite : Icons.favorite_border,
                  size: 14,
                  color: post.isLikedByMe
                      ? const Color(0xFFC060C0)
                      : const Color(0xFF444444),
                ),
                const SizedBox(width: 4),
                Text(
                  '${post.likeCount}',
                  style: const TextStyle(
                    fontSize: 11,
                    color: Color(0xFF444444),
                  ),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(width: 16),
        const Icon(Icons.chat_bubble_outline, size: 13, color: Color(0xFF383838)),
        const SizedBox(width: 4),
        Text(
          '${post.replyCount}',
          style: const TextStyle(fontSize: 11, color: Color(0xFF444444)),
        ),
        const Spacer(),
        Text(
          _timeAgo(post.createdAt),
          style: const TextStyle(fontSize: 10, color: Color(0xFF333333)),
        ),
      ],
    );
  }

  String _timeAgo(DateTime dt) {
    final diff = DateTime.now().difference(dt);
    if (diff.inMinutes < 1) return 'şimdi';
    if (diff.inMinutes < 60) return '${diff.inMinutes}d';
    if (diff.inHours < 24) return '${diff.inHours}s';
    if (diff.inDays < 7) return '${diff.inDays}g';
    return '${(diff.inDays / 7).floor()}h';
  }
}
