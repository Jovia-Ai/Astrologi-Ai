import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:mobile/app/forum/forum_models.dart';
import 'package:mobile/app/forum/forum_providers.dart';
import 'package:mobile/app/tabs/forum_post_detail_page.dart';
import 'package:mobile/app/widgets/forum_compose_bar.dart';
import 'package:mobile/app/widgets/forum_post_card.dart';
import 'package:mobile/design/theme/profile_theme_extension.dart';
import 'package:mobile/design/widgets/jovia_editorial.dart';

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
          color: profile.colors.primary,
          backgroundColor: profile.colors.surface,
          onRefresh: () => notifier.loadPosts(refresh: true),
          child: CustomScrollView(
            physics: const AlwaysScrollableScrollPhysics(),
            slivers: [
              SliverToBoxAdapter(
                child: Column(
                  children: [
                    JoviaReveal(
                      child: JoviaProfileTopBar(
                        label: 'Forum',
                        centerText: 'Toplulugun akisi',
                        onActionTap: () => _openComposeSheet(context, state),
                        actionAsset: JoviaUiAsset.plusCrosshair,
                        actionTooltip: 'Yeni konu',
                      ),
                    ),
                    SizedBox(height: spacing.s24),
                    JoviaReveal(
                      delay: const Duration(milliseconds: 20),
                      child: _ForumHero(
                        activeTransit: state.activeTransit,
                        selectedCategory: state.selectedCategory,
                        postCount: state.posts.length,
                      ),
                    ),
                    SizedBox(height: spacing.s20),
                    JoviaReveal(
                      delay: const Duration(milliseconds: 60),
                      child: _ForumCategoryStrip(
                        categories: _forumCategories,
                        selectedCategory: state.selectedCategory,
                        onSelect: notifier.selectCategory,
                      ),
                    ),
                    SizedBox(height: spacing.s20),
                  ],
                ),
              ),
              if (state.isLoading && state.posts.isEmpty)
                const SliverFillRemaining(
                  hasScrollBody: false,
                  child: _ForumLoadingState(),
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
                SliverList.builder(
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
              const SliverToBoxAdapter(child: SizedBox(height: 104)),
            ],
          ),
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
  const _ForumHero({
    required this.activeTransit,
    required this.selectedCategory,
    required this.postCount,
  });

  final String activeTransit;
  final String selectedCategory;
  final int postCount;

  @override
  Widget build(BuildContext context) {
    final cleanedTransit = activeTransit.trim();
    final statusLabel = postCount == 0
        ? 'Akis hazirlaniyor'
        : '$postCount baslik';
    return JoviaEditorialHeroBlock(
      label: 'Toplulugun nabzi',
      title: 'Haritani forumun diliyle konustur',
      body: cleanedTransit.isEmpty
          ? 'Transit, iliski ve golge basliklarini daha yumusak, editoryal bir akista takip et.'
          : cleanedTransit,
      large: true,
      glyph: const JoviaUiIcon(asset: JoviaUiAsset.chatOrbit, size: 18),
      accent: const JoviaIllustrationAccent(
        asset: JoviaIllustrationAsset.layers,
        width: 96,
        height: 96,
        opacity: 0.22,
      ),
      footer: Wrap(
        spacing: 8,
        runSpacing: 8,
        children: [
          JoviaMetaPill(label: statusLabel),
          JoviaMetaPill(label: _forumHeroCategoryLabel(selectedCategory)),
          if (cleanedTransit.isNotEmpty)
            JoviaMetaPill(
              label: cleanedTransit.length > 38
                  ? '${cleanedTransit.substring(0, 38).trim()}...'
                  : cleanedTransit,
            ),
        ],
      ),
    );
  }
}

class _ForumCategoryStrip extends StatelessWidget {
  const _ForumCategoryStrip({
    required this.categories,
    required this.selectedCategory,
    required this.onSelect,
  });

  final List<String> categories;
  final String selectedCategory;
  final ValueChanged<String> onSelect;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 46,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        itemCount: categories.length,
        separatorBuilder: (_, _) => const SizedBox(width: 8),
        itemBuilder: (context, index) {
          final category = categories[index];
          return _ForumCategoryPill(
            category: category,
            selected: selectedCategory == category,
            onTap: () => onSelect(category),
          );
        },
      ),
    );
  }
}

class _ForumCategoryPill extends StatelessWidget {
  const _ForumCategoryPill({
    required this.category,
    required this.selected,
    this.onTap,
  });

  final String category;
  final bool selected;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final accent = _forumCategoryAccent(context, category);
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final fill = selected
        ? Color.alphaBlend(
            accent.withValues(alpha: isDark ? 0.18 : 0.14),
            profile.colors.surface,
          )
        : Color.alphaBlend(
            Colors.white.withValues(alpha: isDark ? 0.04 : 0.54),
            profile.colors.heroBase,
          );
    return JoviaPressable(
      onTap: onTap,
      borderRadius: BorderRadius.circular(999),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 180),
        curve: Curves.easeOutCubic,
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 11),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(999),
          gradient: selected
              ? LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [
                    Color.alphaBlend(
                      Colors.white.withValues(alpha: isDark ? 0.08 : 0.72),
                      fill,
                    ),
                    fill,
                  ],
                )
              : null,
          color: selected ? null : fill,
          border: Border.all(
            color: selected
                ? accent.withValues(alpha: 0.24)
                : profile.colors.strokeSoft,
          ),
          boxShadow: selected
              ? [
                  BoxShadow(
                    color: accent.withValues(alpha: 0.12),
                    blurRadius: 18,
                    offset: const Offset(0, 10),
                    spreadRadius: -14,
                  ),
                ]
              : const [],
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 8,
              height: 8,
              decoration: BoxDecoration(shape: BoxShape.circle, color: accent),
            ),
            const SizedBox(width: 8),
            Text(
              _forumCategoryLabel(category),
              style: profile.typography.buttonLabel.copyWith(
                color: selected
                    ? profile.colors.text
                    : profile.colors.textLight,
                fontWeight: FontWeight.w700,
              ),
            ),
          ],
        ),
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
    final profile = context.profileTheme;
    final activeTransit = widget.activeTransit.trim();
    return Padding(
      padding: EdgeInsets.fromLTRB(
        16,
        24,
        16,
        MediaQuery.of(context).viewInsets.bottom + 16,
      ),
      child: JoviaSurfaceCard(
        radius: 30,
        padding: const EdgeInsets.fromLTRB(18, 18, 18, 18),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            JoviaEditorialHeroBlock(
              label: 'Yeni konu',
              title: 'Foruma bir sey birak',
              body: activeTransit.isEmpty
                  ? 'Toplulugun tonunu acacak bir baslik ve kisa bir metin yaz.'
                  : 'Aktif tema: $activeTransit',
              glyph: const JoviaUiIcon(asset: JoviaUiAsset.editPen, size: 18),
              accent: const JoviaIllustrationAccent(
                asset: JoviaIllustrationAsset.layers,
                width: 74,
                height: 74,
                opacity: 0.22,
              ),
              surface: false,
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _titleController,
              maxLength: 120,
              style: profile.typography.bodyCompact.copyWith(
                color: profile.colors.text,
              ),
              decoration: _forumInputDecoration(context, 'Baslik'),
            ),
            const SizedBox(height: 10),
            TextField(
              controller: _bodyController,
              maxLength: 600,
              minLines: 4,
              maxLines: 6,
              style: profile.typography.bodyCompact.copyWith(
                color: profile.colors.text,
              ),
              decoration: _forumInputDecoration(
                context,
                'Ne paylasmak istiyorsun?',
              ),
            ),
            const SizedBox(height: 10),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                for (final category in _forumCategories.skip(1))
                  _ForumCategoryPill(
                    category: category,
                    selected: _category == category,
                    onTap: () => setState(() {
                      _category = category;
                    }),
                  ),
              ],
            ),
            const SizedBox(height: 18),
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
    );
  }
}

class _ForumLoadingState extends StatelessWidget {
  const _ForumLoadingState();

  @override
  Widget build(BuildContext context) {
    return Center(
      child: JoviaSurfaceCard(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const CircularProgressIndicator(),
            const SizedBox(height: 16),
            Text(
              'Forum akisi yukleniyor.',
              style: context.profileTheme.typography.cardTitle,
            ),
          ],
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
    final profile = context.profileTheme;
    return Center(
      child: JoviaSurfaceCard(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 52,
              height: 52,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: profile.colors.buttonSecondary.withValues(alpha: 0.82),
                border: Border.all(color: profile.colors.strokeSoft),
              ),
              child: const Center(
                child: JoviaUiIcon(asset: JoviaUiAsset.chatOrbit, size: 20),
              ),
            ),
            const SizedBox(height: 16),
            Text(
              'Forum daha yeni aciliyor.',
              style: profile.typography.sectionTitle.copyWith(fontSize: 24),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 10),
            Text(
              'Ilk paylasimi birak ve toplulugun tonunu sen baslat.',
              textAlign: TextAlign.center,
              style: profile.typography.bodyCompact.copyWith(
                color: profile.colors.textLight,
              ),
            ),
            const SizedBox(height: 18),
            JoviaPrimaryButton(label: 'Ilk paylasimi yap', onTap: onCompose),
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
    final profile = context.profileTheme;
    return Center(
      child: JoviaSurfaceCard(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              'Forum su an acilamiyor.',
              style: profile.typography.sectionTitle.copyWith(fontSize: 24),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 10),
            Text(
              message,
              textAlign: TextAlign.center,
              style: profile.typography.bodyCompact.copyWith(
                color: profile.colors.textLight,
              ),
            ),
            const SizedBox(height: 18),
            JoviaPrimaryButton(label: 'Tekrar dene', onTap: onRetry),
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

String _forumHeroCategoryLabel(String raw) {
  if (raw == 'all') {
    return 'Tum basliklar';
  }
  return '${_forumCategoryLabel(raw)} odagi';
}

Color _forumCategoryAccent(BuildContext context, String category) {
  final profile = context.profileTheme;
  switch (category) {
    case 'transit':
      return profile.colors.primary;
    case 'iliski':
      return const Color(0xFF4EA86C);
    case 'kariyer':
      return const Color(0xFF4E83C8);
    case 'golge':
      return const Color(0xFFC26B63);
    case 'genel':
      return profile.colors.warmAccent;
    case 'all':
    default:
      return profile.colors.textLight;
  }
}

InputDecoration _forumInputDecoration(BuildContext context, String hint) {
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
    hintText: hint,
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
