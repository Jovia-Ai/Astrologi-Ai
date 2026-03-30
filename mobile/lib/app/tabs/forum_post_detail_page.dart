import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:mobile/app/forum/forum_models.dart';
import 'package:mobile/app/forum/forum_providers.dart';
import 'package:mobile/app/widgets/forum_compose_bar.dart';
import 'package:mobile/app/widgets/forum_post_card.dart';

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
    return Scaffold(
      backgroundColor: const Color(0xFF050505),
      appBar: AppBar(
        backgroundColor: const Color(0xFF050505),
        foregroundColor: Colors.white,
        elevation: 0,
        title: const Text('Konu'),
      ),
      body: RefreshIndicator(
        onRefresh: _load,
        child: ListView(
          padding: const EdgeInsets.only(bottom: 96),
          children: [
            ForumPostCard(post: post, onTap: () {}, onLike: _toggleLike),
            const Padding(
              padding: EdgeInsets.fromLTRB(16, 12, 16, 8),
              child: Text(
                'Yanitlar',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 16,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ),
            if (_loading)
              const Padding(
                padding: EdgeInsets.all(24),
                child: Center(child: CircularProgressIndicator()),
              )
            else if (_error != null)
              Padding(
                padding: const EdgeInsets.all(16),
                child: Text(
                  _error!,
                  style: const TextStyle(color: Color(0xFFBDB6C9)),
                ),
              )
            else if (_replies.isEmpty)
              const Padding(
                padding: EdgeInsets.fromLTRB(16, 8, 16, 8),
                child: Text(
                  'Henuz yanit yok. Ilk sesi sen birak.',
                  style: TextStyle(color: Color(0xFF8C8795)),
                ),
              )
            else
              for (final reply in _replies) _ReplyTile(reply: reply),
          ],
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
    return Container(
      margin: const EdgeInsets.fromLTRB(16, 8, 16, 0),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFF101012),
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: const Color(0xFF1D1D21)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              CircleAvatar(
                radius: 15,
                backgroundColor: const Color(0xFF2A2437),
                child: Text(
                  reply.initials,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 10,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  reply.userDisplayName,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
              Text(
                _timeAgo(reply.createdAt),
                style: const TextStyle(color: Color(0xFF706A7D), fontSize: 11),
              ),
            ],
          ),
          const SizedBox(height: 10),
          Text(
            reply.body,
            style: const TextStyle(
              color: Color(0xFFD2CDD9),
              fontSize: 13,
              height: 1.45,
            ),
          ),
        ],
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
    return Padding(
      padding: EdgeInsets.fromLTRB(
        16,
        24,
        16,
        MediaQuery.of(context).viewInsets.bottom + 16,
      ),
      child: Material(
        color: const Color(0xFF0F0F11),
        borderRadius: BorderRadius.circular(24),
        child: Padding(
          padding: const EdgeInsets.all(18),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Yanit birak',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 18,
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: _controller,
                maxLength: 300,
                minLines: 4,
                maxLines: 6,
                style: const TextStyle(color: Colors.white),
                decoration: const InputDecoration(
                  hintText: 'Ne dusunuyorsun?',
                  hintStyle: TextStyle(color: Color(0xFF6F6A7A)),
                  filled: true,
                  fillColor: Color(0xFF151519),
                  border: OutlineInputBorder(),
                ),
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
      ),
    );
  }
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
