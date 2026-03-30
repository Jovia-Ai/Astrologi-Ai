import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:mobile/app/forum/forum_models.dart';
import 'package:mobile/app/forum/forum_providers.dart';
import 'package:mobile/app/tabs/forum_post_detail_page.dart';
import 'package:mobile/app/widgets/forum_compose_bar.dart';
import 'package:mobile/app/widgets/forum_post_card.dart';

const List<String> _forumCategories = <String>[
  'all',
  'transit',
  'iliski',
  'kariyer',
  'golge',
  'genel',
];

class ForumPage extends ConsumerStatefulWidget {
  const ForumPage({super.key});

  @override
  ConsumerState<ForumPage> createState() => _ForumPageState();
}

class _ForumPageState extends ConsumerState<ForumPage> {
  Future<void> _openComposeSheet(BuildContext context, ForumState state) async {
    final notifier = ref.read(forumNotifierProvider.notifier);
    final created = await showModalBottomSheet<ForumPost>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => _ForumComposeSheet(
        activeTransit: state.activeTransit,
        onSubmit: (title, body, category) async {
          return notifier.submitPost(
            title: title,
            body: body,
            category: category,
            activeTransit: state.activeTransit,
          );
        },
      ),
    );
    if (!mounted || created == null) {
      return;
    }
    ScaffoldMessenger.of(this.context).showSnackBar(
      const SnackBar(content: Text('Paylasimin forumda yerini aldi.')),
    );
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(forumNotifierProvider);
    final notifier = ref.read(forumNotifierProvider.notifier);

    return Scaffold(
      backgroundColor: const Color(0xFF050505),
      appBar: AppBar(
        backgroundColor: const Color(0xFF050505),
        foregroundColor: Colors.white,
        elevation: 0,
        title: const Text('Forum'),
      ),
      body: RefreshIndicator(
        onRefresh: () => notifier.loadPosts(refresh: true),
        child: CustomScrollView(
          slivers: [
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(16, 10, 16, 8),
                child: _ForumHero(activeTransit: state.activeTransit),
              ),
            ),
            SliverToBoxAdapter(
              child: SizedBox(
                height: 44,
                child: ListView.separated(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  scrollDirection: Axis.horizontal,
                  itemCount: _forumCategories.length,
                  separatorBuilder: (_, _) => const SizedBox(width: 8),
                  itemBuilder: (context, index) {
                    final category = _forumCategories[index];
                    final selected = state.selectedCategory == category;
                    return FilterChip(
                      selected: selected,
                      onSelected: (_) => notifier.selectCategory(category),
                      label: Text(_forumCategoryLabel(category)),
                      selectedColor: const Color(0xFF1F1A2E),
                      backgroundColor: const Color(0xFF111111),
                      checkmarkColor: const Color(0xFFC3A7FF),
                      labelStyle: TextStyle(
                        color: selected
                            ? const Color(0xFFE7DAFF)
                            : const Color(0xFFB8B8B8),
                      ),
                      side: BorderSide(
                        color: selected
                            ? const Color(0xFF3E335B)
                            : const Color(0xFF242424),
                      ),
                    );
                  },
                ),
              ),
            ),
            if (state.isLoading && state.posts.isEmpty)
              const SliverFillRemaining(
                hasScrollBody: false,
                child: Center(child: CircularProgressIndicator()),
              )
            else if (state.error != null && state.posts.isEmpty)
              SliverFillRemaining(
                hasScrollBody: false,
                child: _ForumErrorState(
                  message: state.error!,
                  onRetry: () => notifier.loadPosts(refresh: true),
                ),
              )
            else if (state.posts.isEmpty)
              SliverFillRemaining(
                hasScrollBody: false,
                child: _ForumEmptyState(
                  onCompose: () => _openComposeSheet(context, state),
                ),
              )
            else
              SliverPadding(
                padding: const EdgeInsets.fromLTRB(0, 12, 0, 96),
                sliver: SliverList.builder(
                  itemCount: state.posts.length,
                  itemBuilder: (context, index) {
                    final post = state.posts[index];
                    return ForumPostCard(
                      post: post,
                      animationIndex: index,
                      onTap: () {
                        Navigator.of(context).push(
                          MaterialPageRoute<void>(
                            builder: (_) => ForumPostDetailPage(post: post),
                          ),
                        );
                      },
                      onLike: () => notifier.toggleLike(post.id),
                    );
                  },
                ),
              ),
          ],
        ),
      ),
      bottomNavigationBar: ForumComposeBar(
        label: 'Bir sey paylas...',
        onTap: () => _openComposeSheet(context, state),
      ),
    );
  }
}

class _ForumHero extends StatelessWidget {
  const _ForumHero({required this.activeTransit});

  final String activeTransit;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(24),
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFF18131F), Color(0xFF0F0E12)],
        ),
        border: Border.all(color: const Color(0xFF24212A)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Toplulugun nabzi',
            style: TextStyle(
              color: Color(0xFF8F889E),
              fontSize: 11,
              letterSpacing: 1.2,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 10),
          const Text(
            'Haritani ve anlik gundemi forumun diliyle konustur.',
            style: TextStyle(
              color: Colors.white,
              fontSize: 22,
              fontWeight: FontWeight.w700,
              height: 1.2,
            ),
          ),
          const SizedBox(height: 10),
          Text(
            activeTransit.trim().isEmpty ? 'Gokyuzu hareketli' : activeTransit,
            style: const TextStyle(
              color: Color(0xFFC8C1D6),
              fontSize: 13,
              height: 1.45,
            ),
          ),
        ],
      ),
    );
  }
}

class _ForumComposeSheet extends StatefulWidget {
  const _ForumComposeSheet({
    required this.activeTransit,
    required this.onSubmit,
  });

  final String activeTransit;
  final Future<ForumPost?> Function(String title, String body, String category)
  onSubmit;

  @override
  State<_ForumComposeSheet> createState() => _ForumComposeSheetState();
}

class _ForumComposeSheetState extends State<_ForumComposeSheet> {
  final TextEditingController _titleController = TextEditingController();
  final TextEditingController _bodyController = TextEditingController();
  String _category = 'genel';
  bool _submitting = false;

  @override
  void dispose() {
    _titleController.dispose();
    _bodyController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    final title = _titleController.text.trim();
    final body = _bodyController.text.trim();
    if (title.isEmpty || body.isEmpty) {
      return;
    }
    setState(() {
      _submitting = true;
    });
    final post = await widget.onSubmit(title, body, _category);
    if (!mounted) {
      return;
    }
    setState(() {
      _submitting = false;
    });
    if (post == null) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('Paylasim gonderilemedi.')));
      return;
    }
    Navigator.of(context).pop(post);
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
                'Foruma bir sey birak',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 18,
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'Aktif tema: ${widget.activeTransit}',
                style: const TextStyle(color: Color(0xFF9791A5), fontSize: 12),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: _titleController,
                maxLength: 120,
                style: const TextStyle(color: Colors.white),
                decoration: _forumInputDecoration('Baslik'),
              ),
              const SizedBox(height: 10),
              TextField(
                controller: _bodyController,
                maxLength: 600,
                minLines: 4,
                maxLines: 6,
                style: const TextStyle(color: Colors.white),
                decoration: _forumInputDecoration('Ne paylasmak istiyorsun?'),
              ),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  for (final category in _forumCategories.skip(1))
                    ChoiceChip(
                      selected: _category == category,
                      label: Text(_forumCategoryLabel(category)),
                      onSelected: (_) => setState(() {
                        _category = category;
                      }),
                    ),
                ],
              ),
              const SizedBox(height: 16),
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
                      : const Text('Paylas'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _ForumEmptyState extends StatelessWidget {
  const _ForumEmptyState({required this.onCompose});

  final VoidCallback onCompose;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(
              Icons.forum_outlined,
              color: Color(0xFF7A7488),
              size: 36,
            ),
            const SizedBox(height: 12),
            const Text(
              'Forum daha yeni aciliyor.',
              style: TextStyle(
                color: Colors.white,
                fontSize: 17,
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              'Ilk paylasimi birak ve toplulugun tonunu sen baslat.',
              textAlign: TextAlign.center,
              style: TextStyle(color: Color(0xFF9591A0), height: 1.45),
            ),
            const SizedBox(height: 14),
            OutlinedButton(
              onPressed: onCompose,
              child: const Text('Ilk paylasimi yap'),
            ),
          ],
        ),
      ),
    );
  }
}

class _ForumErrorState extends StatelessWidget {
  const _ForumErrorState({required this.message, required this.onRetry});

  final String message;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              'Forum su an acilamiyor.',
              style: TextStyle(
                color: Colors.white,
                fontSize: 17,
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              message,
              textAlign: TextAlign.center,
              style: const TextStyle(color: Color(0xFF9591A0), height: 1.4),
            ),
            const SizedBox(height: 14),
            OutlinedButton(
              onPressed: onRetry,
              child: const Text('Tekrar dene'),
            ),
          ],
        ),
      ),
    );
  }
}

String _forumCategoryLabel(String raw) {
  switch (raw) {
    case 'all':
      return 'Tum';
    case 'transit':
      return 'Transit';
    case 'iliski':
      return 'Iliski';
    case 'kariyer':
      return 'Kariyer';
    case 'golge':
      return 'Golge';
    case 'genel':
      return 'Genel';
    default:
      return raw;
  }
}

InputDecoration _forumInputDecoration(String hint) {
  return InputDecoration(
    hintText: hint,
    hintStyle: const TextStyle(color: Color(0xFF6F6A7A)),
    filled: true,
    fillColor: const Color(0xFF151519),
    border: OutlineInputBorder(
      borderRadius: BorderRadius.circular(16),
      borderSide: const BorderSide(color: Color(0xFF24242A)),
    ),
    enabledBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(16),
      borderSide: const BorderSide(color: Color(0xFF24242A)),
    ),
    focusedBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(16),
      borderSide: const BorderSide(color: Color(0xFF4F4380)),
    ),
  );
}
