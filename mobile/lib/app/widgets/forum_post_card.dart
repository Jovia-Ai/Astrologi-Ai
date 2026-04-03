import 'package:flutter/material.dart';
import 'package:mobile/app/forum/forum_models.dart';
import 'package:mobile/app/timing/turkish_text.dart';
import 'package:mobile/design/theme/profile_theme_extension.dart';
import 'package:mobile/design/widgets/jovia_editorial.dart';

/// Reusable forum post card.
/// Displays post header, title, body preview, and footer actions.
class ForumPostCard extends StatefulWidget {
  const ForumPostCard({
    super.key,
    required this.post,
    required this.onTap,
    required this.onLike,
    this.animationIndex = 0,
    this.showFullBody = false,
  });

  final ForumPost post;
  final VoidCallback onTap;
  final VoidCallback onLike;
  final int animationIndex;
  final bool showFullBody;

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
    final activeTransit = (post.activeTransit ?? '').trim();
    final profile = context.profileTheme;
    return Padding(
      padding: const EdgeInsets.only(bottom: 14),
      child: JoviaPressable(
        onTap: widget.onTap,
        borderRadius: BorderRadius.circular(30),
        child: JoviaSurfaceCard(
          radius: 30,
          padding: const EdgeInsets.fromLTRB(18, 18, 18, 16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _PostHeader(post: post),
              if (activeTransit.isNotEmpty) ...[
                const SizedBox(height: 12),
                _TransitRibbon(text: activeTransit),
              ],
              const SizedBox(height: 14),
              Text(
                post.title,
                style: profile.typography.card.copyWith(
                  color: profile.colors.text,
                  fontSize: 17.4,
                  height: 1.24,
                  fontWeight: FontWeight.w600,
                  letterSpacing: -0.18,
                ),
              ),
              const SizedBox(height: 9),
              Text(
                post.body,
                maxLines: widget.showFullBody ? null : 4,
                overflow: widget.showFullBody
                    ? TextOverflow.visible
                    : TextOverflow.ellipsis,
                style: profile.typography.bodyCompact.copyWith(
                  color: profile.colors.textLight,
                  fontSize: 13.8,
                  height: 1.55,
                ),
              ),
              const SizedBox(height: 14),
              const ThinDivider(),
              const SizedBox(height: 12),
              _PostFooter(
                post: post,
                likeScale: _likeScale,
                onLike: _handleLike,
              ),
            ],
          ),
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
    final profile = context.profileTheme;
    final secondaryLine = [
      if (post.userSunSign.trim().isNotEmpty) post.userSunSign.trim(),
      if (post.userRisingSign.trim().isNotEmpty)
        'Yukselen ${post.userRisingSign.trim()}',
    ].join(' • ');
    final base = post.avatarColor;
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          width: 38,
          height: 38,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                Color.alphaBlend(
                  Colors.white.withValues(alpha: 0.22),
                  base.withValues(alpha: 0.92),
                ),
                Color.alphaBlend(
                  profile.colors.lavender.withValues(alpha: 0.24),
                  base,
                ),
              ],
            ),
            border: Border.all(color: profile.colors.strokeSoft),
          ),
          child: Center(
            child: Text(
              post.initials,
              style: profile.typography.buttonLabel.copyWith(
                fontSize: 11.2,
                color: Colors.white,
                fontWeight: FontWeight.w700,
              ),
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
                style: profile.typography.metaSoft.copyWith(
                  color: profile.colors.text,
                  fontSize: 12.4,
                  fontWeight: FontWeight.w700,
                ),
              ),
              if (secondaryLine.isNotEmpty)
                Text(
                  secondaryLine,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: profile.typography.meta.copyWith(
                    fontSize: 11,
                    color: profile.colors.textLight,
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
    final profile = context.profileTheme;
    final bg = _bgColors[category] ?? const Color(0x19888888);
    final fg = _textColors[category] ?? profile.colors.text;
    final label = _labels[category] ?? category;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 6),
      decoration: BoxDecoration(
        color: Color.alphaBlend(
          fg.withValues(alpha: 0.08),
          profile.colors.surface,
        ),
        borderRadius: BorderRadius.circular(999),
        border: Border.all(
          color: Color.alphaBlend(
            fg.withValues(alpha: 0.22),
            profile.colors.strokeSoft,
          ),
        ),
        boxShadow: [
          BoxShadow(
            color: bg.withValues(alpha: 0.16),
            blurRadius: 14,
            offset: const Offset(0, 8),
            spreadRadius: -10,
          ),
        ],
      ),
      child: Text(
        turkishToUpper(label),
        style: TextStyle(
          fontSize: 9.6,
          color: fg,
          fontWeight: FontWeight.w700,
          letterSpacing: 0.92,
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
    final profile = context.profileTheme;
    return Row(
      children: [
        JoviaPressable(
          onTap: onLike,
          borderRadius: BorderRadius.circular(999),
          child: ScaleTransition(
            scale: likeScale,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 7),
              decoration: BoxDecoration(
                color: post.isLikedByMe
                    ? Color.alphaBlend(
                        profile.colors.neonPink.withValues(alpha: 0.3),
                        profile.colors.surface,
                      )
                    : profile.colors.buttonSecondary.withValues(alpha: 0.82),
                borderRadius: BorderRadius.circular(999),
                border: Border.all(
                  color: post.isLikedByMe
                      ? profile.colors.primary.withValues(alpha: 0.2)
                      : profile.colors.strokeSoft,
                ),
              ),
              child: Row(
                children: [
                  Icon(
                    post.isLikedByMe ? Icons.favorite : Icons.favorite_border,
                    size: 14,
                    color: post.isLikedByMe
                        ? const Color(0xFFB45F87)
                        : profile.colors.textLight,
                  ),
                  const SizedBox(width: 5),
                  Text(
                    '${post.likeCount}',
                    style: profile.typography.metaSoft.copyWith(
                      fontSize: 11.5,
                      color: post.isLikedByMe
                          ? profile.colors.text
                          : profile.colors.textLight,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
        const SizedBox(width: 8),
        _FooterPill(
          icon: Icons.chat_bubble_outline_rounded,
          label: '${post.replyCount}',
        ),
        const Spacer(),
        Text(
          _timeAgo(post.createdAt),
          style: profile.typography.meta.copyWith(
            fontSize: 11.2,
            color: profile.colors.textLight,
          ),
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

class _TransitRibbon extends StatelessWidget {
  const _TransitRibbon({required this.text});

  final String text;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 9),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(18),
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            Color.alphaBlend(
              profile.colors.warmAccent.withValues(alpha: 0.14),
              profile.colors.surface,
            ),
            Color.alphaBlend(
              profile.colors.primary.withValues(alpha: 0.08),
              profile.colors.heroBase,
            ),
          ],
        ),
        border: Border.all(color: profile.colors.strokeSoft),
      ),
      child: Row(
        children: [
          const JoviaUiIcon(asset: JoviaUiAsset.orbitPlanet, size: 15),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              text,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: profile.typography.metaSoft.copyWith(
                color: profile.colors.textLight,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _FooterPill extends StatelessWidget {
  const _FooterPill({required this.icon, required this.label});

  final IconData icon;
  final String label;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 7),
      decoration: BoxDecoration(
        color: profile.colors.buttonSecondary.withValues(alpha: 0.82),
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: profile.colors.strokeSoft),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 13.5, color: profile.colors.textLight),
          const SizedBox(width: 5),
          Text(
            label,
            style: profile.typography.metaSoft.copyWith(
              fontSize: 11.5,
              color: profile.colors.textLight,
              fontWeight: FontWeight.w700,
            ),
          ),
        ],
      ),
    );
  }
}
