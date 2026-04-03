import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:mobile/app/forum/forum_models.dart';
import 'package:mobile/app/forum/forum_providers.dart';
import 'package:mobile/app/widgets/forum_compose_bar.dart';
import 'package:mobile/app/widgets/forum_post_card.dart';
import 'package:mobile/design/theme/profile_theme_extension.dart';
import 'package:mobile/design/widgets/jovia_editorial.dart';

class ForumPostDetailPage extends ConsumerStatefulWidget {
  const ForumPostDetailPage({super.key, required this.post});

  final ForumPost post;

  @override
  ConsumerState<ForumPostDetailPage> createState() =>
      _ForumPostDetailPageState();
}

class _ForumPostDetailPageState extends ConsumerState<ForumPostDetailPage> {
  ForumPost? _post;
  List<ForumReply> _replies = const <ForumReply>[];
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _post = widget.post;
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final service = ref.read(forumServiceProvider);
      final detail = await service.fetchPostDetail(widget.post.id);
      if (!mounted) {
        return;
      }
      setState(() {
        _post = detail.post;
        _replies = detail.replies;
        _loading = false;
      });
      ref.read(forumNotifierProvider.notifier).syncPost(detail.post);
    } catch (e) {
      if (!mounted) {
        return;
      }
      setState(() {
        _loading = false;
        _error = e.toString();
      });
    }
  }

  Future<void> _toggleLike() async {
    final current = _post;
    if (current == null) {
      return;
    }
    final optimistic = current.copyWith(
      isLikedByMe: !current.isLikedByMe,
      likeCount: current.isLikedByMe
          ? current.likeCount - 1
          : current.likeCount + 1,
    );
    setState(() {
      _post = optimistic;
    });
    ref.read(forumNotifierProvider.notifier).syncPost(optimistic);

    try {
      final result = await ref
          .read(forumServiceProvider)
          .toggleLike(current.id);
      final settled = optimistic.copyWith(
        isLikedByMe: result.liked,
        likeCount: result.likeCount,
      );
      if (!mounted) {
        return;
      }
      setState(() {
        _post = settled;
      });
      ref.read(forumNotifierProvider.notifier).syncPost(settled);
    } catch (_) {
      if (!mounted) {
        return;
      }
      setState(() {
        _post = current;
      });
      ref.read(forumNotifierProvider.notifier).syncPost(current);
    }
  }

  Future<void> _openReplySheet() async {
    final reply = await showModalBottomSheet<ForumReply>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => _ReplyComposeSheet(
        onSubmit: (body) async {
          return ref
              .read(forumServiceProvider)
              .addReply(postId: widget.post.id, body: body);
        },
      ),
    );
    if (!mounted || reply == null) {
      return;
    }
    final current = _post;
    setState(() {
      _replies = [..._replies, reply];
      if (current != null) {
        _post = current.copyWith(replyCount: current.replyCount + 1);
      }
    });
    if (_post != null) {
      ref.read(forumNotifierProvider.notifier).syncPost(_post!);
    }
  }

  @override
  Widget build(BuildContext context) {
    final post = _post ?? widget.post;
    final profile = context.profileTheme;
    final spacing = profile.spacing;
    return Scaffold(
      backgroundColor: profile.colors.bg,
      body: JoviaPageScaffold(
        padding: EdgeInsets.fromLTRB(
          spacing.pageHorizontal,
          spacing.xs,
          spacing.pageHorizontal,
          0,
        ),
        child: RefreshIndicator(
          onRefresh: _load,
          color: profile.colors.primary,
          backgroundColor: profile.colors.surface,
          child: ListView(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: const EdgeInsets.only(bottom: 104),
            children: [
              JoviaReveal(
                child: const JoviaProfileTopBar(
                  label: 'Forum',
                  centerText: 'Konu',
                  reserveTrailingSpace: true,
                ),
              ),
              SizedBox(height: spacing.s24),
              ForumPostCard(
                post: post,
                onTap: () {},
                onLike: _toggleLike,
                showFullBody: true,
              ),
              SizedBox(height: spacing.s8),
              const JoviaSectionHeader(
                label: 'Yanitlar',
                title: 'Akisa eklenen sesler',
              ),
              SizedBox(height: spacing.s12),
              if (_loading)
                const Padding(
                  padding: EdgeInsets.all(24),
                  child: Center(child: CircularProgressIndicator()),
                )
              else if (_error != null)
                JoviaSurfaceCard(
                  child: Text(
                    _error!,
                    style: profile.typography.bodyCompact.copyWith(
                      color: profile.colors.textLight,
                    ),
                  ),
                )
              else if (_replies.isEmpty)
                JoviaSurfaceCard(
                  child: Text(
                    'Henuz yanit yok. Ilk sesi sen birak.',
                    style: profile.typography.bodyCompact.copyWith(
                      color: profile.colors.textLight,
                    ),
                  ),
                )
              else
                for (final reply in _replies) _ReplyTile(reply: reply),
            ],
          ),
        ),
      ),
      bottomNavigationBar: ForumComposeBar(
        label: 'Yanit yaz...',
        onTap: _openReplySheet,
      ),
    );
  }
}

class _ReplyTile extends StatelessWidget {
  const _ReplyTile({required this.reply});

  final ForumReply reply;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: JoviaSurfaceCard(
        radius: 24,
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  width: 34,
                  height: 34,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    gradient: LinearGradient(
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                      colors: [
                        Color.alphaBlend(
                          Colors.white.withValues(alpha: 0.2),
                          profile.colors.primary.withValues(alpha: 0.82),
                        ),
                        Color.alphaBlend(
                          profile.colors.lavender.withValues(alpha: 0.22),
                          profile.colors.primary,
                        ),
                      ],
                    ),
                    border: Border.all(color: profile.colors.strokeSoft),
                  ),
                  child: Center(
                    child: Text(
                      reply.initials,
                      style: profile.typography.buttonLabel.copyWith(
                        color: Colors.white,
                        fontSize: 10.5,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    reply.userDisplayName,
                    style: profile.typography.metaSoft.copyWith(
                      color: profile.colors.text,
                      fontSize: 13,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
                Text(
                  _timeAgo(reply.createdAt),
                  style: profile.typography.meta.copyWith(
                    color: profile.colors.textLight,
                    fontSize: 11,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Text(
              reply.body,
              style: profile.typography.bodyCompact.copyWith(
                color: profile.colors.textLight,
                fontSize: 13.6,
                height: 1.5,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ReplyComposeSheet extends StatefulWidget {
  const _ReplyComposeSheet({required this.onSubmit});

  final Future<ForumReply> Function(String body) onSubmit;

  @override
  State<_ReplyComposeSheet> createState() => _ReplyComposeSheetState();
}

class _ReplyComposeSheetState extends State<_ReplyComposeSheet> {
  final TextEditingController _controller = TextEditingController();
  bool _submitting = false;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    final body = _controller.text.trim();
    if (body.isEmpty) {
      return;
    }
    setState(() {
      _submitting = true;
    });
    try {
      final reply = await widget.onSubmit(body);
      if (!mounted) {
        return;
      }
      Navigator.of(context).pop(reply);
    } catch (_) {
      if (!mounted) {
        return;
      }
      setState(() {
        _submitting = false;
      });
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('Yanit gonderilemedi.')));
    }
  }

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Padding(
      padding: EdgeInsets.fromLTRB(
        16,
        24,
        16,
        MediaQuery.of(context).viewInsets.bottom + 16,
      ),
      child: JoviaSurfaceCard(
        radius: 28,
        padding: const EdgeInsets.all(18),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const JoviaEditorialHeroBlock(
              label: 'Yanit',
              title: 'Yanit birak',
              body: 'Konuya kisa ama net bir yorum ekle.',
              glyph: JoviaUiIcon(asset: JoviaUiAsset.editPen, size: 18),
              surface: false,
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _controller,
              maxLength: 300,
              minLines: 4,
              maxLines: 6,
              style: profile.typography.bodyCompact.copyWith(
                color: profile.colors.text,
              ),
              decoration: _replyInputDecoration(context),
            ),
            const SizedBox(height: 14),
            SizedBox(
              width: double.infinity,
              child: FilledButton(
                onPressed: _submitting ? null : _submit,
                child: _submitting
                    ? const SizedBox(
                        height: 18,
                        width: 18,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Text('Yanitla'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

InputDecoration _replyInputDecoration(BuildContext context) {
  final profile = context.profileTheme;
  final isDark = Theme.of(context).brightness == Brightness.dark;
  final fillColor = Color.alphaBlend(
    profile.colors.heroBase.withValues(alpha: isDark ? 0.38 : 0.54),
    profile.colors.surface,
  );
  final borderColor = profile.colors.strokeSoft.withValues(
    alpha: isDark ? 0.94 : 0.86,
  );
  return InputDecoration(
    hintText: 'Ne dusunuyorsun?',
    hintStyle: profile.typography.bodyCompact.copyWith(
      color: profile.colors.textLight,
    ),
    filled: true,
    fillColor: fillColor,
    contentPadding: const EdgeInsets.symmetric(horizontal: 18, vertical: 16),
    border: OutlineInputBorder(
      borderRadius: BorderRadius.circular(18),
      borderSide: BorderSide(color: borderColor),
    ),
    enabledBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(18),
      borderSide: BorderSide(color: borderColor),
    ),
    focusedBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(18),
      borderSide: BorderSide(color: profile.colors.primary, width: 1.2),
    ),
  );
}

String _timeAgo(DateTime dt) {
  final diff = DateTime.now().difference(dt);
  if (diff.inMinutes < 1) {
    return 'simdi';
  }
  if (diff.inMinutes < 60) {
    return '${diff.inMinutes}d';
  }
  if (diff.inHours < 24) {
    return '${diff.inHours}s';
  }
  if (diff.inDays < 7) {
    return '${diff.inDays}g';
  }
  return '${(diff.inDays / 7).floor()}h';
}
