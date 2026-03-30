import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:mobile/app/forum/forum_models.dart';
import 'package:mobile/app/forum/forum_providers.dart';
import 'package:mobile/app/tabs/forum_page.dart';
import 'package:mobile/app/tabs/forum_post_detail_page.dart';
import 'package:mobile/design/theme/profile_theme_extension.dart';
import 'package:mobile/design/widgets/jovia_editorial.dart';

class SocialPreviewStrip extends ConsumerWidget {
  const SocialPreviewStrip({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(forumNotifierProvider);
    final posts = state.posts.take(3).toList(growable: false);

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 14),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const JoviaSectionHeader(label: 'Forum', title: 'Topluluktan sesler'),
          const SizedBox(height: 12),
          if (state.isLoading && posts.isEmpty)
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 12),
              child: Center(child: CircularProgressIndicator()),
            )
          else if (posts.isEmpty)
            JoviaSurfaceCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Forum daha yeni aciliyor.',
                    style: context.profileTheme.typography.cardTitle,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Ilk basliklari gormek icin foruma gec.',
                    style: context.profileTheme.typography.bodyCompact.copyWith(
                      color: context.profileTheme.colors.textLight,
                    ),
                  ),
                ],
              ),
            )
          else
            SizedBox(
              height: 238,
              child: ListView.separated(
                scrollDirection: Axis.horizontal,
                itemCount: posts.length + 1,
                separatorBuilder: (_, _) => const SizedBox(width: 12),
                itemBuilder: (context, index) {
                  if (index == posts.length) {
                    return _ForumMoreCard(
                      onTap: () => Navigator.of(context).push(
                        MaterialPageRoute<void>(
                          builder: (_) => const ForumPage(),
                        ),
                      ),
                    );
                  }
                  return _ForumPreviewCard(post: posts[index]);
                },
              ),
            ),
        ],
      ),
    );
  }
}

class _ForumPreviewCard extends StatelessWidget {
  const _ForumPreviewCard({required this.post});

  final ForumPost post;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return SizedBox(
      width: 206,
      child: JoviaPressable(
        borderRadius: BorderRadius.circular(26),
        onTap: () {
          Navigator.of(context).push(
            MaterialPageRoute<void>(
              builder: (_) => ForumPostDetailPage(post: post),
            ),
          );
        },
        child: JoviaSurfaceCard(
          radius: 26,
          padding: const EdgeInsets.fromLTRB(16, 16, 16, 14),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Text(
                      _categoryLabel(post.category).toUpperCase(),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: profile.typography.monoEyebrow.copyWith(
                        color: profile.colors.textLight,
                        fontSize: 10.6,
                        letterSpacing: 1.55,
                      ),
                    ),
                  ),
                  Container(
                    width: 8,
                    height: 8,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: _categoryTint(context, post.category),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Text(
                post.title,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: profile.typography.card.copyWith(
                  color: profile.colors.text,
                  fontSize: 16.8,
                  height: 1.18,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 9),
              Text(
                _previewExcerpt(post.body),
                maxLines: 3,
                overflow: TextOverflow.ellipsis,
                style: profile.typography.bodyCompact.copyWith(
                  color: profile.colors.textLight,
                  fontSize: 13.1,
                  height: 1.46,
                ),
              ),
              const Spacer(),
              Container(
                width: double.infinity,
                height: 1,
                color: profile.colors.separator.withValues(alpha: 0.72),
              ),
              const SizedBox(height: 10),
              Row(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  Expanded(
                    child: Text(
                      _footerLine(post),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: profile.typography.metaSoft.copyWith(
                        color: profile.colors.textLight,
                        fontWeight: FontWeight.w600,
                        fontSize: 12.2,
                      ),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Icon(
                    Icons.arrow_outward_rounded,
                    size: 16,
                    color: profile.colors.text,
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _ForumMoreCard extends StatelessWidget {
  const _ForumMoreCard({required this.onTap});

  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return SizedBox(
      width: 186,
      child: JoviaPressable(
        borderRadius: BorderRadius.circular(26),
        onTap: onTap,
        child: JoviaSurfaceCard(
          radius: 26,
          padding: const EdgeInsets.fromLTRB(16, 16, 16, 14),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'FORUM',
                style: profile.typography.monoEyebrow.copyWith(
                  color: profile.colors.textLight,
                  fontSize: 10.6,
                  letterSpacing: 1.55,
                ),
              ),
              const SizedBox(height: 12),
              Text(
                'Daha fazlasi',
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: profile.typography.card.copyWith(
                  color: profile.colors.text,
                  fontSize: 16.8,
                  height: 1.18,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 9),
              Text(
                'Forumdaki tum basliklari ac ve toplulugun nabzini izlemeye devam et.',
                maxLines: 3,
                overflow: TextOverflow.ellipsis,
                style: profile.typography.bodyCompact.copyWith(
                  color: profile.colors.textLight,
                  fontSize: 13.1,
                  height: 1.46,
                ),
              ),
              const Spacer(),
              Container(
                width: double.infinity,
                height: 1,
                color: profile.colors.separator.withValues(alpha: 0.72),
              ),
              const SizedBox(height: 10),
              Row(
                children: [
                  Text(
                    'Foruma gir',
                    style: profile.typography.buttonLabel.copyWith(
                      color: profile.colors.text,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  const Spacer(),
                  Icon(
                    Icons.arrow_outward_rounded,
                    size: 16,
                    color: profile.colors.text,
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

String _categoryLabel(String raw) {
  switch (raw) {
    case 'transit':
      return 'Transit';
    case 'iliski':
      return 'Iliski';
    case 'kariyer':
      return 'Kariyer';
    case 'golge':
      return 'Golge';
    default:
      return 'Genel';
  }
}

String _previewExcerpt(String raw) {
  final trimmed = raw.trim();
  if (trimmed.length <= 64) {
    return trimmed;
  }
  return '${trimmed.substring(0, 64).trim()}...';
}

String _footerLine(ForumPost post) {
  final transit = post.activeTransit?.trim();
  final reply = '${post.replyCount} yanit';
  if (transit == null || transit.isEmpty) {
    return reply;
  }
  final clipped = transit.length <= 22
      ? transit
      : '${transit.substring(0, 22).trim()}...';
  return '$clipped • $reply';
}

Color _categoryTint(BuildContext context, String raw) {
  final profile = context.profileTheme;
  switch (raw) {
    case 'transit':
      return profile.colors.lavender;
    case 'iliski':
      return profile.colors.neonPink;
    case 'kariyer':
      return profile.colors.warmAccent;
    case 'golge':
      return profile.colors.muted;
    default:
      return profile.colors.textLight;
  }
}
