import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:mobile/app/profile/profile_providers.dart';
import 'package:mobile/app/tabs/sky_event_detail_page.dart';
import 'package:mobile/app/timing/transit_repositories.dart';
import 'package:mobile/design/theme/profile_theme_extension.dart';
import 'package:mobile/design/widgets/jovia_editorial.dart';

class SkyEventFeedPage extends ConsumerStatefulWidget {
  const SkyEventFeedPage({super.key});

  @override
  ConsumerState<SkyEventFeedPage> createState() => _SkyEventFeedPageState();
}

class _SkyEventFeedPageState extends ConsumerState<SkyEventFeedPage> {
  final SkyRepository _repository = SkyRepository();

  bool _loading = true;
  String? _error;
  SkyNowDto? _feed;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final profile = ref.read(userProfileProvider).asData?.value;
      final feed = await _repository.fetchFeed(
        tz: (profile?['timezone'] ?? 'Europe/Istanbul').toString().trim(),
        limit: 12,
        window: 'week',
      );
      if (!mounted) {
        return;
      }
      setState(() {
        _feed = feed;
        _loading = false;
      });
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

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Scaffold(
      backgroundColor: profile.colors.bg,
      appBar: AppBar(
        leadingWidth: 52,
        leading: Padding(
          padding: const EdgeInsets.only(left: 12),
          child: JoviaGlassIconButton(
            onTap: () => Navigator.of(context).maybePop(),
            child: const Icon(Icons.arrow_back_rounded, size: 18),
          ),
        ),
        title: Text(
          'TUM KONULAR',
          style: profile.typography.navigationLabel(color: profile.colors.text),
        ),
      ),
      body: SafeArea(
        top: false,
        child: JoviaPageScaffold(
          padding: EdgeInsets.fromLTRB(
            profile.spacing.pageHorizontal,
            profile.spacing.xs,
            profile.spacing.pageHorizontal,
            profile.spacing.pageBottom,
          ),
          child: _loading
              ? const Center(child: CircularProgressIndicator())
              : _error != null
              ? _SkyFeedErrorState(message: _error!, onRetry: _load)
              : _SkyFeedList(feed: _feed, onRetry: _load),
        ),
      ),
    );
  }
}

class _SkyFeedList extends StatelessWidget {
  const _SkyFeedList({required this.feed, required this.onRetry});

  final SkyNowDto? feed;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    final items = feed?.items ?? const <SkyFeedItemDto>[];
    return ListView(
      padding: EdgeInsets.zero,
      children: [
        JoviaEditorialHeroBlock(
          label: 'Kolektif akim',
          title: 'Ayni gokyuzu dalgasinin diger parcalari',
          body: (feed?.summary ?? '').trim().isNotEmpty
              ? feed!.summary.trim()
              : 'Bu hafta kolektifte ust uste calisan basliklar burada.',
          large: true,
        ),
        const SizedBox(height: 22),
        if (items.isEmpty)
          JoviaSurfaceCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const JoviaSectionHeader(
                  label: 'Bosluk',
                  title: 'Burada gosterilecek baslik yok',
                ),
                const SizedBox(height: 12),
                MinimalCTAButton(
                  label: 'Yeniden yukle',
                  emphasized: true,
                  onTap: onRetry,
                ),
              ],
            ),
          ),
        for (final item in items) ...[
          _SkyFeedCard(item: item),
          if (item != items.last) const SizedBox(height: 12),
        ],
      ],
    );
  }
}

class _SkyFeedCard extends StatelessWidget {
  const _SkyFeedCard({required this.item});

  final SkyFeedItemDto item;

  @override
  Widget build(BuildContext context) {
    return JoviaTopicSurface(
      eyebrow: item.previewChips.isNotEmpty ? item.previewChips.first : null,
      title: item.title,
      body: item.hookTr,
      meta: item.previewChips.skip(1).take(2).toList(growable: false),
      secondaryAction: const Icon(Icons.arrow_outward_rounded, size: 18),
      onTap: () {
        Navigator.of(context).push(
          _adaptiveFeedRoute<void>(
            context,
            (_) => SkyEventDetailPage(item: item),
          ),
        );
      },
    );
  }
}

class _SkyFeedErrorState extends StatelessWidget {
  const _SkyFeedErrorState({required this.message, required this.onRetry});

  final String message;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: EdgeInsets.zero,
      children: [
        JoviaSurfaceCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const JoviaSectionHeader(
                label: 'Baglanti',
                title: 'Sky feed simdi acilamadi',
              ),
              const SizedBox(height: 12),
              Text(
                message,
                style: context.profileTheme.typography.bodyCompact.copyWith(
                  color: context.profileTheme.colors.textLight,
                ),
              ),
              const SizedBox(height: 16),
              MinimalCTAButton(
                label: 'Tekrar dene',
                emphasized: true,
                onTap: onRetry,
              ),
            ],
          ),
        ),
      ],
    );
  }
}

Route<T> _adaptiveFeedRoute<T>(BuildContext context, WidgetBuilder builder) {
  final platform = Theme.of(context).platform;
  if (platform == TargetPlatform.iOS || platform == TargetPlatform.macOS) {
    return CupertinoPageRoute<T>(builder: builder);
  }
  return MaterialPageRoute<T>(builder: builder);
}
