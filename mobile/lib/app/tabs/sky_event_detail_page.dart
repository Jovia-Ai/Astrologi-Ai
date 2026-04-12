import 'package:dio/dio.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:mobile/app/profile/profile_providers.dart';
import 'package:mobile/app/timing/transit_repositories.dart';
import 'package:mobile/design/theme/profile_theme_extension.dart';
import 'package:mobile/design/widgets/jovia_editorial.dart';

class SkyEventDetailPage extends ConsumerStatefulWidget {
  const SkyEventDetailPage({super.key, required this.item});

  final SkyFeedItemDto item;

  @override
  ConsumerState<SkyEventDetailPage> createState() => _SkyEventDetailPageState();
}

class _SkyEventDetailPageState extends ConsumerState<SkyEventDetailPage> {
  final SkyRepository _skyRepository = SkyRepository();

  bool _loading = true;
  String? _error;
  SkyEventDetailDto? _detail;

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
      final profile = ref.read(userProfileProvider).valueOrNull;
      final detail = await _skyRepository.fetchEventDetail(
        idOrSlug: widget.item.eventKey,
        tz: _resolveTimezone(profile),
      );
      if (!mounted) {
        return;
      }
      setState(() {
        _detail = detail;
        _loading = false;
      });
    } catch (e) {
      if (!mounted) {
        return;
      }
      if (!mounted) return;
      setState(() {
        _loading = false;
        if (e is DioException) {
          if (e.type == DioExceptionType.receiveTimeout ||
              e.type == DioExceptionType.sendTimeout ||
              e.type == DioExceptionType.connectionTimeout) {
            _error = 'Sunucu şu an yavaş, birazdan tekrar dene.';
          } else if (e.type == DioExceptionType.connectionError) {
            _error = 'Bağlantı kurulamadı.';
          } else {
            _error = 'Bir sorun oluştu, tekrar dene.';
          }
        } else {
          _error = 'Bir sorun oluştu, tekrar dene.';
        }
      });
    }
  }

  String _resolveTimezone(Map<String, dynamic>? profile) {
    return (profile?['timezone'] ?? 'Europe/Istanbul').toString().trim();
  }

  Future<void> _openPersonalLayer(
    BuildContext context,
    SkyEventDetailDto detail,
  ) async {
    final profile = ref.read(userProfileProvider).valueOrNull;
    if (!TransitRequestBuilder.hasProfile(profile)) {
      await showModalBottomSheet<void>(
        context: context,
        backgroundColor: Colors.transparent,
        builder: (_) => _SkyInfoSheet(
          title: 'Daha net gostereyim',
          body:
              'Bu olayin seni nasil etkiledigini gosterebilmem icin dogum tarihi, saat ve yer bilgisinin tamamlanmasi gerekiyor.',
        ),
      );
      return;
    }

    if (!mounted || profile == null) {
      return;
    }

    await showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => _SkyPersonalizationSheet(
        repository: _skyRepository,
        profile: profile,
        tz: _resolveTimezone(profile),
        detail: detail,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final profile = ref.watch(userProfileProvider).valueOrNull;
    final profileTheme = context.profileTheme;
    final colors = profileTheme.colors;
    final previewTitle = widget.item.title.trim().isNotEmpty
        ? widget.item.title.trim()
        : 'Kolektif konu';
    final previewBody = widget.item.hookTr;

    return Scaffold(
      backgroundColor: colors.bg,
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
          'GOKYUZUNDE NE VAR',
          style: profileTheme.typography.navigationLabel(color: colors.text),
        ),
      ),
      body: SafeArea(
        top: false,
        child: JoviaPageScaffold(
          padding: EdgeInsets.fromLTRB(
            profileTheme.spacing.pageHorizontal,
            profileTheme.spacing.xs,
            profileTheme.spacing.pageHorizontal,
            profileTheme.spacing.pageBottom,
          ),
          child: _loading
              ? _SkyLoadingState(title: previewTitle, body: previewBody)
              : _error != null
              ? _SkyErrorState(
                  message: _error!,
                  onRetry: _load,
                  fallbackTitle: previewTitle,
                  fallbackBody: previewBody,
                )
              : _detail == null
              ? _SkyEmptyState(onRetry: _load)
              : _SkyDetailBody(
                  previewItem: widget.item,
                  detail: _detail!,
                  hasCompleteProfile: TransitRequestBuilder.hasProfile(profile),
                  onOpenPersonalLayer: () =>
                      _openPersonalLayer(context, _detail!),
                ),
        ),
      ),
    );
  }
}

class _SkyDetailBody extends StatelessWidget {
  const _SkyDetailBody({
    required this.previewItem,
    required this.detail,
    required this.hasCompleteProfile,
    required this.onOpenPersonalLayer,
  });

  final SkyFeedItemDto previewItem;
  final SkyEventDetailDto detail;
  final bool hasCompleteProfile;
  final VoidCallback onOpenPersonalLayer;

  @override
  Widget build(BuildContext context) {
    final sections = _buildCollectiveSections(detail);
    final chips = _detailHeroChips(detail, previewItem);
    final ctaLabel =
        (detail.personalizationCta['label_tr'] ?? '').toString().trim().isEmpty
        ? 'Sende nasil calisiyor?'
        : (detail.personalizationCta['label_tr'] ?? '').toString().trim();

    return ListView(
      padding: EdgeInsets.zero,
      children: [
        JoviaEditorialHeroBlock(
          label: _detailHeroLabel(detail),
          title: detail.displayTitle.isNotEmpty
              ? detail.displayTitle
              : previewItem.title,
          body: _firstNonEmpty([
            detail.summaryTr,
            previewItem.hookTr,
            detail.generalMeaningTr,
          ]),
          large: true,
          accent: const Padding(
            padding: EdgeInsets.only(top: 8),
            child: Icon(Icons.auto_awesome_rounded, size: 36),
          ),
          footer: Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [for (final chip in chips) JoviaMetaPill(label: chip)],
          ),
        ),
        const SizedBox(height: 22),
        for (final section in sections) ...[
          JoviaReadingPanel(
            label: section.eyebrow,
            title: section.title,
            child: Text(
              section.body,
              style: context.profileTheme.typography.bodyCompact.copyWith(
                color: context.profileTheme.colors.text,
                height: 1.55,
              ),
            ),
          ),
          const SizedBox(height: 18),
        ],
        JoviaSurfaceCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const JoviaSectionHeader(
                label: 'Kisisel katman',
                title: 'Sende nasil calisiyor?',
              ),
              const SizedBox(height: 12),
              Text(
                'Kolektifte bu tema calisiyor. Sende bunun en cok nereye dustugunu gormek icin haritana bagla.',
                style: context.profileTheme.typography.bodyCompact.copyWith(
                  color: context.profileTheme.colors.textLight,
                  height: 1.5,
                ),
              ),
              const SizedBox(height: 16),
              MinimalCTAButton(
                label: ctaLabel,
                emphasized: hasCompleteProfile,
                glassy: !hasCompleteProfile,
                onTap: onOpenPersonalLayer,
              ),
            ],
          ),
        ),
        if (detail.relatedEvents.isNotEmpty) ...[
          const SizedBox(height: 22),
          const JoviaSectionHeader(
            label: 'Devam eden dalga',
            title: 'Bununla birlikte calisan basliklar',
          ),
          const SizedBox(height: 12),
          for (final item in detail.relatedEvents) ...[
            _SkyEventLinkCard(item: item),
            if (item != detail.relatedEvents.last) const SizedBox(height: 12),
          ],
        ],
      ],
    );
  }
}

class _SkyEventLinkCard extends StatelessWidget {
  const _SkyEventLinkCard({required this.item});

  final SkyFeedItemDto item;

  @override
  Widget build(BuildContext context) {
    return EditorialListItem(
      title: item.title,
      body: item.hookTr,
      meta: item.previewChips,
      trailing: const Icon(Icons.arrow_outward_rounded, size: 18),
      onTap: () {
        Navigator.of(context).push(
          _adaptiveSkyRoute<void>(
            context,
            (_) => SkyEventDetailPage(item: item),
          ),
        );
      },
    );
  }
}

class _SkyPersonalizationSheet extends StatefulWidget {
  const _SkyPersonalizationSheet({
    required this.repository,
    required this.profile,
    required this.tz,
    required this.detail,
  });

  final SkyRepository repository;
  final Map<String, dynamic> profile;
  final String tz;
  final SkyEventDetailDto detail;

  @override
  State<_SkyPersonalizationSheet> createState() =>
      _SkyPersonalizationSheetState();
}

class _SkyPersonalizationSheetState extends State<_SkyPersonalizationSheet> {
  late Future<SkyEventPersonalizationDto> _future;

  @override
  void initState() {
    super.initState();
    _future = _load();
  }

  Future<SkyEventPersonalizationDto> _load() {
    return widget.repository.personalizeEvent(
      idOrSlug: widget.detail.slug.trim().isNotEmpty
          ? widget.detail.slug.trim()
          : widget.detail.id.trim(),
      profile: widget.profile,
      tz: widget.tz,
    );
  }

  @override
  Widget build(BuildContext context) {
    final profileTheme = context.profileTheme;
    return Padding(
      padding: EdgeInsets.fromLTRB(
        14,
        24,
        14,
        MediaQuery.of(context).viewInsets.bottom + 14,
      ),
      child: JoviaSurfaceCard(
        radius: 28,
        child: FutureBuilder<SkyEventPersonalizationDto>(
          future: _future,
          builder: (context, snapshot) {
            if (snapshot.connectionState != ConnectionState.done) {
              return const SizedBox(
                height: 220,
                child: Center(child: CircularProgressIndicator()),
              );
            }
            if (snapshot.hasError) {
              return Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  const JoviaSectionHeader(
                    label: 'Kisisel etki',
                    title: 'Burada bir kopma oldu',
                  ),
                  const SizedBox(height: 12),
                  Text(
                    snapshot.error.toString(),
                    style: profileTheme.typography.bodyCompact.copyWith(
                      color: profileTheme.colors.textLight,
                    ),
                  ),
                  const SizedBox(height: 16),
                  MinimalCTAButton(
                    label: 'Tekrar dene',
                    emphasized: true,
                    onTap: () {
                      setState(() {
                        _future = _load();
                      });
                    },
                  ),
                ],
              );
            }
            final data = snapshot.data;
            if (data == null) {
              return const SizedBox.shrink();
            }
            final sections = _buildPersonalSections(data, widget.detail);
            final meta = <String>[
              _relevanceLabel(data.relevanceLevel),
              '${data.impactScore.round()} etki puani',
            ];
            return SingleChildScrollView(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  const JoviaSectionHeader(
                    label: 'Kisisel etki',
                    title: 'Sende nasil calisiyor?',
                  ),
                  const SizedBox(height: 10),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: [
                      for (final item in meta) JoviaMetaPill(label: item),
                    ],
                  ),
                  const SizedBox(height: 16),
                  for (final section in sections) ...[
                    _SkySheetSectionCard(section: section),
                    const SizedBox(height: 12),
                  ],
                  if (data.matchedNatalPoints.isNotEmpty) ...[
                    const SizedBox(height: 4),
                    const JoviaSectionHeader(
                      label: 'Teknik kanit',
                      title: 'Neden sende bu kadar calisiyor?',
                    ),
                    const SizedBox(height: 10),
                    for (final point in data.matchedNatalPoints.take(4)) ...[
                      _SkyTouchpointEvidenceCard(point: point),
                      const SizedBox(height: 10),
                    ],
                  ],
                ],
              ),
            );
          },
        ),
      ),
    );
  }
}

class _SkyTouchpointEvidenceCard extends StatelessWidget {
  const _SkyTouchpointEvidenceCard({required this.point});

  final SkyPersonalTouchpointDto point;

  @override
  Widget build(BuildContext context) {
    final body = point.house == null
        ? 'En yakin teknik temas ${_normalizeSentence(point.noteTr).toLowerCase()} hattinda gorunuyor.'
        : 'Bu olay sende ${point.house}. ev hattini uyandiriyor; ${_normalizeSentence(point.noteTr).toLowerCase()} cizgisi burada daha hizli cevap veriyor.';
    final chips = <String>[
      if (point.aspect.trim().isNotEmpty) _aspectLabel(point.aspect),
      if (point.point.trim().isNotEmpty) point.point,
      if (point.house != null) '${point.house}. ev',
    ];
    return JoviaSurfaceCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            body,
            style: context.profileTheme.typography.bodyCompact.copyWith(
              color: context.profileTheme.colors.text,
              height: 1.45,
            ),
          ),
          if (chips.isNotEmpty) ...[
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [for (final chip in chips) JoviaMetaPill(label: chip)],
            ),
          ],
        ],
      ),
    );
  }
}

class _SkySheetSectionCard extends StatelessWidget {
  const _SkySheetSectionCard({required this.section});

  final _SkySectionData section;

  @override
  Widget build(BuildContext context) {
    return JoviaSurfaceCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(section.title, style: context.profileTheme.typography.cardTitle),
          const SizedBox(height: 8),
          Text(
            section.body,
            style: context.profileTheme.typography.bodyCompact.copyWith(
              color: context.profileTheme.colors.textLight,
              height: 1.5,
            ),
          ),
        ],
      ),
    );
  }
}

class _SkyLoadingState extends StatelessWidget {
  const _SkyLoadingState({required this.title, required this.body});

  final String title;
  final String body;

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: EdgeInsets.zero,
      children: [
        JoviaEditorialHeroBlock(
          label: 'Kolektif konu',
          title: title,
          body: body,
          large: true,
        ),
        const SizedBox(height: 28),
        const Center(child: CircularProgressIndicator()),
      ],
    );
  }
}

class _SkyErrorState extends StatelessWidget {
  const _SkyErrorState({
    required this.message,
    required this.onRetry,
    required this.fallbackTitle,
    required this.fallbackBody,
  });

  final String message;
  final VoidCallback onRetry;
  final String fallbackTitle;
  final String fallbackBody;

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: EdgeInsets.zero,
      children: [
        JoviaEditorialHeroBlock(
          label: 'Kolektif konu',
          title: fallbackTitle,
          body: fallbackBody,
          large: true,
        ),
        const SizedBox(height: 20),
        JoviaSurfaceCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const JoviaSectionHeader(
                label: 'Baglanti',
                title: 'Detay simdi acilamadi',
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

class _SkyEmptyState extends StatelessWidget {
  const _SkyEmptyState({required this.onRetry});

  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: JoviaSurfaceCard(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const JoviaSectionHeader(
              label: 'Kolektif konu',
              title: 'Burada gosterecek veri yok',
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
    );
  }
}

class _SkyInfoSheet extends StatelessWidget {
  const _SkyInfoSheet({required this.title, required this.body});

  final String title;
  final String body;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(14, 24, 14, 14),
      child: JoviaSurfaceCard(
        radius: 28,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            JoviaSectionHeader(label: 'Bilgi', title: title),
            const SizedBox(height: 12),
            Text(
              body,
              style: context.profileTheme.typography.bodyCompact.copyWith(
                color: context.profileTheme.colors.textLight,
                height: 1.5,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _SkySectionData {
  const _SkySectionData({
    required this.eyebrow,
    required this.title,
    required this.body,
  });

  final String eyebrow;
  final String title;
  final String body;
}

List<_SkySectionData> _buildCollectiveSections(SkyEventDetailDto detail) {
  final primaryMeaning = _primaryMeaningLabel(
    detail.tags,
    detail.bodies,
    detail.aspect,
    detail.sign,
    detail.summaryTr,
  );
  return <_SkySectionData>[
    _SkySectionData(
      eyebrow: 'Acilis',
      title: 'Atmosferde ne degisiyor?',
      body: _firstNonEmpty([
        detail.summaryTr,
        detail.generalMeaningTr,
        'Su an kolektif ritmi yeni bir basliga kaydiran bir degisim var.',
      ]),
    ),
    _SkySectionData(
      eyebrow: 'Hayat sahnesi',
      title: 'Bu kolektifte nerede gorunur olur?',
      body: _firstNonEmpty([
        detail.lifeDomainsTr,
        _deriveLifeDomains(detail, primaryMeaning),
        detail.whatItCanFeelLikeTr,
      ]),
    ),
    _SkySectionData(
      eyebrow: 'Potansiyel',
      title: 'Hediyesi ne?',
      body: _firstNonEmpty([
        detail.giftTr,
        _deriveGift(detail, primaryMeaning),
      ]),
    ),
    _SkySectionData(
      eyebrow: 'Golge',
      title: 'Golgesi ne?',
      body: _firstNonEmpty([
        detail.shadowTr,
        detail.whatToWatchTr,
        _deriveShadow(primaryMeaning),
      ]),
    ),
    _SkySectionData(
      eyebrow: 'Yon',
      title: 'Bununla nasil calisilir?',
      body: _firstNonEmpty([
        detail.microActionTr,
        detail.howToWorkWithItTr,
        _deriveMicroAction(primaryMeaning),
      ]),
    ),
    _SkySectionData(
      eyebrow: 'Zaman',
      title: 'Bu neden simdi onemli?',
      body: _firstNonEmpty([detail.whyNowTr, _deriveWhyNow(detail)]),
    ),
  ];
}

List<_SkySectionData> _buildPersonalSections(
  SkyEventPersonalizationDto data,
  SkyEventDetailDto detail,
) {
  final leadArea = data.activatedAreasTr.isNotEmpty
      ? data.activatedAreasTr.first
      : 'yakindan tuttugun bir alan';
  final leadTouchpoint = data.matchedNatalPoints.isNotEmpty
      ? data.matchedNatalPoints.first
      : null;
  return <_SkySectionData>[
    _SkySectionData(
      eyebrow: 'Acilis',
      title: 'Sende en cok nereye dokunuyor?',
      body: data.activatedAreasTr.isEmpty
          ? data.summaryTr
          : '${data.summaryTr} En cok ${data.activatedAreasTr.join(', ')} hattinda belirginlesiyor.',
    ),
    _SkySectionData(
      eyebrow: 'Hissettigi yer',
      title: 'Nasil hissedilebilir?',
      body: _firstNonEmpty([
        data.howItMayShowUpTr,
        'Bu etki sende en cok $leadArea ekseninde kendini hatirlatir; gundelik ritim degisirken tepkin daha hizli ve daha kisisel hale gelebilir.',
      ]),
    ),
    _SkySectionData(
      eyebrow: 'Kullanim',
      title: 'En iyi kullanim',
      body: _firstNonEmpty([
        data.bestUseTr,
        'Bu dalgayi en iyi, $leadArea alaninda net bir secim yapip enerjiyi dagitmadan kullanirsin.',
      ]),
    ),
    _SkySectionData(
      eyebrow: 'Denge',
      title: 'Dikkat edilmesi gereken nokta',
      body: _firstNonEmpty([
        data.watchOutTr,
        _personalWatchOut(data.relevanceLevel, leadArea),
      ]),
    ),
    _SkySectionData(
      eyebrow: 'Zaman',
      title: 'En guclu zaman penceresi',
      body: _buildTimeWindow(data),
    ),
    _SkySectionData(
      eyebrow: 'Mikro adim',
      title: 'Kucuk adim',
      body: _firstNonEmpty([
        data.microActionTr,
        'Bugun sadece $leadArea alaninda tek bir adimi netlestir. Kucuk ama geri alinmayan bir secim bu etkiyi daha temiz calistirir.',
      ]),
    ),
    if (leadTouchpoint != null)
      _SkySectionData(
        eyebrow: 'Teknik iz',
        title: 'Neden sende bu kadar calisiyor?',
        body:
            'En yakin teknik temas ${_normalizeSentence(leadTouchpoint.noteTr).toLowerCase()} hattinda. Bu da kolektif basligin sende daha kisisel duyulmasina neden oluyor.',
      ),
  ];
}

List<String> _detailHeroChips(
  SkyEventDetailDto detail,
  SkyFeedItemDto previewItem,
) {
  final chips = <String>[
    if (_detailHeroLabel(detail).isNotEmpty) _detailHeroLabel(detail),
  ];
  final timing = previewItem.previewChips.firstWhere(
    (item) => item == previewItem.badge || item == previewItem.relativeTiming,
    orElse: () => previewItem.relativeTiming.trim(),
  );
  if (timing.trim().isNotEmpty && !chips.contains(timing.trim())) {
    chips.add(timing.trim());
  }
  final meaning = _primaryMeaningLabel(
    detail.tags,
    detail.bodies,
    detail.aspect,
    detail.sign,
    detail.summaryTr,
  );
  if (meaning.isNotEmpty && !chips.contains(meaning)) {
    chips.add(meaning);
  }
  return chips.take(3).toList(growable: false);
}

String _detailHeroLabel(SkyEventDetailDto detail) {
  switch (detail.eventType.trim()) {
    case 'ingress':
      return 'Burc gecisi';
    case 'lunation_full_moon':
      return 'Dolunay';
    case 'lunation_new_moon':
      return 'Yeniay';
    case 'exact_aspect_major':
      return 'Exact aci';
    case 'eclipse':
      return 'Tutulma';
    case 'retrograde_start':
      return 'Retro basliyor';
    case 'retrograde_end':
      return 'Retro bitiyor';
    default:
      return 'Kolektif konu';
  }
}

String _deriveLifeDomains(SkyEventDetailDto detail, String meaning) {
  switch (meaning) {
    case 'Iliskiler':
      return 'Bu tema kolektifte iliski kurma bicimi, yakinlik dengesi ve karsilikli beklentiler uzerinde daha gorunur olur.';
    case 'Para':
      return 'Bu dalga en cok para, kaynak kullanimi ve guvende kalma ihtiyacinin dili degisirken kendini belli eder.';
    case 'Gorunurluk':
      return 'Bu etki topluluk icindeki gorunurluk, sahneye cikma bicimi ve kimlerin one ciktiginda daha net hissedilir.';
    case 'Karar':
      return 'Bu baslik karar alma hizi, zihinsel yon ve hangi secenege odak verildigi alaninda calisir.';
    case 'Yakinlik':
      return 'Bu tema duygusal yakinlik, bedenin verdigi sinyal ve koruma ihtiyacinda daha kolay fark edilir.';
    case 'Yapi kurma':
      return 'Bu etki sorumluluk, sinir, uzun vadeli plan ve bir seyi ayakta tutma gucunde gorunur olur.';
    case 'Birakma':
      return 'Bu baslik bitmesi gereken seyler, kapanislar ve artik tasinmayan yukun gorunur hale gelmesinde calisir.';
    case 'Gerilim':
      return 'Bu dalga gerilim, tepki hizi ve biriken basincin nereye akacagi alaninda daha kolay okunur.';
    case 'Netlesme':
      return 'Bu tema daginik duran bir konunun daha net gorunmesi ve sonuca dogru itilmesinde belirginlesir.';
    case 'Donusum':
      return 'Bu etki guc, kriz, birakis ve koklu yon degisikligi isteyen sahnelerde gorunur olur.';
    default:
      return _firstNonEmpty([
        detail.whatItCanFeelLikeTr,
        detail.generalMeaningTr,
        'Bu baslik kolektif ritimde ton degisikligi yarattigi yerlerde fark edilir.',
      ]);
  }
}

String _deriveGift(SkyEventDetailDto detail, String meaning) {
  if (detail.howToWorkWithItTr.trim().isNotEmpty) {
    return detail.howToWorkWithItTr.trim();
  }
  switch (meaning) {
    case 'Iliskiler':
      return 'Dogru kullanildiginda iliskilerde daha sakin, daha net ve daha gercek bir ritim kurmana yardim eder.';
    case 'Para':
      return 'Kaynaklarini daha bilincli yonetmek ve neyin degerli oldugunu secmek icin alan acabilir.';
    case 'Gorunurluk':
      return 'Seni daha net gosteren bir ton kurmana ve hangi sahnede durdugunu fark etmene yardim edebilir.';
    case 'Karar':
      return 'Dagilan dikkati toparlayip neye evet neye hayir diyecegini netlestirebilir.';
    case 'Yakinlik':
      return 'Duygusal ihtiyaci dogru yerden adlandirip daha duru bir temas kurmani destekleyebilir.';
    case 'Yapi kurma':
      return 'Kalici duzen, sabir ve omurlu adimlar icin saglam bir omurga kurabilir.';
    case 'Birakma':
      return 'Biteni gormek, yuku azaltmak ve yeni bir alan acmak konusunda seni hafifletebilir.';
    case 'Gerilim':
      return 'Birikmis enerjiyi dogru yone cevirirsen net aksiyon ve cesaret uretebilir.';
    case 'Netlesme':
      return 'Kapali kalan bir konuyu gozle gorulur hale getirip sonraki adimi secmeni kolaylastirabilir.';
    case 'Donusum':
      return 'Eski kalibi birakip daha dogru bir eksene gecmek icin kuvvet toplayabilirsin.';
    default:
      return 'Dogru kullanildiginda bu tema daha temiz secimler ve daha net bir ritim kurmana yardim eder.';
  }
}

String _deriveShadow(String meaning) {
  switch (meaning) {
    case 'Iliskiler':
      return 'Beklentiyi buyutmek, sahiplenmek ya da duygusal agirligi fazla biriktirmek iliski tonunu yorabilir.';
    case 'Para':
      return 'Guvende kalma istegi inada donerse harcama, biriktirme ya da kontrol ihtiyaci sertlesebilir.';
    case 'Gorunurluk':
      return 'Fazla onay arayisi ya da kendini kanitlama baskisi gereksiz agirlik yaratabilir.';
    case 'Karar':
      return 'Acele karar ya da zihni fazla dolastirmak ayni anda iki yone cekilme hissi yaratabilir.';
    case 'Yakinlik':
      return 'Hassasiyet artarken alinma, geri cekilme ya da ihtiyaci dolayli anlatma riski buyuyebilir.';
    case 'Yapi kurma':
      return 'Asiri kontrol, katilik ve her seyi bir anda duzene sokma baskisi akisi hantallastirabilir.';
    case 'Birakma':
      return 'Bitmis olana tutunmak ya da kapanisi geciktirmek gereksiz yorgunluk yaratabilir.';
    case 'Gerilim':
      return 'Bastirilan tepki dogru yere akmazsa tansiyon gereksiz yerden yukselebilir.';
    case 'Netlesme':
      return 'Gorulen seyi hemen sonuca zorlama hali, sabirsizlik ve keskinlik yaratabilir.';
    case 'Donusum':
      return 'Guce tutunmak ya da eski yapidan kopmamak degisimi daha sancili hale getirebilir.';
    default:
      return 'Bu temanin golgesinde acele, katilik ve fazlalik birikmeye baslayabilir.';
  }
}

String _deriveMicroAction(String meaning) {
  switch (meaning) {
    case 'Iliskiler':
      return 'Bugun bir iliskide beklentiyi degil, ihtiyaci net bir cumleyle soyle.';
    case 'Para':
      return 'Gun icinde sadece bir finansal karari sadeleştir; dagilan enerjiyi tek yere topla.';
    case 'Gorunurluk':
      return 'Bugun kendini gosteren tek bir adimi erteleme; kisa ama net bir cikis yap.';
    case 'Karar':
      return 'Aklinda dolasan secenekleri ikiye indir ve bir tanesi icin somut tarih koy.';
    case 'Yakinlik':
      return 'Bedeninin neye evet neye hayir dedigini fark et ve bunu saklamadan adlandir.';
    case 'Yapi kurma':
      return 'Uzun vadede isine yarayacak tek bir duzeni bugun kur ve onu tekrar et.';
    case 'Birakma':
      return 'Tutundugun bir seyi fark et ve bugun sadece onunla arana kucuk bir mesafe koy.';
    case 'Gerilim':
      return 'Tepki vermeden once enerjiyi nereye akitmak istedigini sec; sonra hareket et.';
    case 'Netlesme':
      return 'Belirsiz duran tek bir konuyu yaz, adini koy ve sonraki adimi sabitle.';
    case 'Donusum':
      return 'Eski kalibin yeniden acildigi yerde bu kez farkli bir secim yapmayi dene.';
    default:
      return 'Bugun bu temayi daha temiz calistirmak icin tek bir net adim sec ve onu tamamla.';
  }
}

String _deriveWhyNow(SkyEventDetailDto detail) {
  final dateNote = _shortDate(detail.exactAt);
  switch (detail.eventType.trim()) {
    case 'ingress':
      return 'Bu bir burc gecisi. Ton degisimi soyut kalmaz; gunluk hayatin ritminde ve iliskilerin dilinde kendini gostermeye baslar${dateNote.isEmpty ? '' : ' $dateNote civarinda bunu daha net hissedersin'}';
    case 'lunation_full_moon':
      return 'Dolunaylar sakli olani gorunur eder. Bu tema simdi sonuc, farkindalik ve birikmis duygunun aciga cikmasi istiyor${dateNote.isEmpty ? '' : ' ve $dateNote bandi bunu keskinlestiriyor'}';
    case 'lunation_new_moon':
      return 'Yeniaylar niyeti tohumu gibi calisir. Burada yeni yon, yeni karar ve taze odak ihtiyaci daha belirgin hale gelir${dateNote.isEmpty ? '' : '; cikis noktasi $dateNote civarinda guclenir'}';
    case 'exact_aspect_major':
      return 'Aci simdi exact banda yaklasiyor. Bu nedenle tema arka planda kalmaz; daha hissedilir, daha somut ve daha hizli cevap veren bir ritme girer${dateNote.isEmpty ? '' : ' ve $dateNote bu sikismayi buyutur'}';
    case 'retrograde_start':
      return 'Bu retro baslangici, hiz yerine ayar istemesiyle onemli. Eski basliklar geri gelirken ritmi yeniden kurmak gerekir.';
    case 'retrograde_end':
      return 'Bu retro cikisi, takilan akisin yeniden ileri gitmeye baslamasi yuzunden onemli. Beklemede kalan konu hareket ister.';
    case 'eclipse':
      return 'Tutulmalar ritmi bir anda degistirir. Bu baslik o yuzden simdi daha sert bir esik gibi calisir ve yon degisikligini hizlandirir.';
    default:
      return 'Bu tema su anda kolektif ritimde ust siraya cikmis durumda; bu yuzden gundelik kararlarda ve sosyal tonda daha kolay hissediliyor.';
  }
}

String _buildTimeWindow(SkyEventPersonalizationDto data) {
  final start = _shortDate(data.strongestWindowStart);
  final end = _shortDate(data.strongestWindowEnd);
  if (start.isEmpty && end.isEmpty) {
    return 'Bu etkinin en guclu zamani detay verisi geldikce daha net gorunur.';
  }
  if (start.isNotEmpty && end.isNotEmpty) {
    return 'Bu etki sende en cok $start ile $end arasinda belirgin calisir.';
  }
  return 'Bu etki sende en cok ${start.isNotEmpty ? start : end} civarinda belirginlesir.';
}

String _personalWatchOut(String relevanceLevel, String leadArea) {
  switch (relevanceLevel.trim()) {
    case 'high':
      return '$leadArea hattinda tepkiyi fazla buyutmek yerine ritmi yavaslatman daha dogru olur; cunku etki sende daha hizli calisiyor.';
    case 'medium':
      return '$leadArea alaninda ayni anda fazla seye cevap vermek enerjiyi dagitabilir; tek cizgi secmek daha iyi calisir.';
    default:
      return '$leadArea tarafinda hafif bir hassasiyet artisi olabilir; bunu gereksiz buyutmadan izlemen yeterli.';
  }
}

String _relevanceLabel(String raw) {
  switch (raw.trim()) {
    case 'high':
      return 'Yuksek yanki';
    case 'medium':
      return 'Belirgin yanki';
    case 'light':
      return 'Hafif yanki';
    default:
      return 'Kisisel etki';
  }
}

String _primaryMeaningLabel(
  List<String> tags,
  List<String> bodies,
  String aspect,
  String sign,
  String summary,
) {
  final lower = '${tags.join(' ')} ${bodies.join(' ')} $aspect $sign $summary'
      .toLowerCase();
  if (lower.contains('venus') ||
      lower.contains('taurus') ||
      lower.contains('libra') ||
      lower.contains('iliski')) {
    return 'Iliskiler';
  }
  if (lower.contains('para') || lower.contains('kaynak')) {
    return 'Para';
  }
  if (lower.contains('sun') ||
      lower.contains('leo') ||
      lower.contains('gorun')) {
    return 'Gorunurluk';
  }
  if (lower.contains('mercury') ||
      lower.contains('gemini') ||
      lower.contains('virgo') ||
      lower.contains('karar')) {
    return 'Karar';
  }
  if (lower.contains('moon') ||
      lower.contains('cancer') ||
      lower.contains('yakin')) {
    return 'Yakinlik';
  }
  if (lower.contains('saturn') ||
      lower.contains('capricorn') ||
      lower.contains('yapi')) {
    return 'Yapi kurma';
  }
  if (lower.contains('dolunay') ||
      lower.contains('full moon') ||
      lower.contains('birak')) {
    return 'Birakma';
  }
  if (lower.contains('mars') ||
      lower.contains('aries') ||
      lower.contains('gerilim')) {
    return 'Gerilim';
  }
  if (lower.contains('exact') || lower.contains('net')) {
    return 'Netlesme';
  }
  if (lower.contains('pluto') ||
      lower.contains('scorpio') ||
      lower.contains('donus')) {
    return 'Donusum';
  }
  return '';
}

String _normalizeSentence(String raw) {
  final trimmed = raw.trim();
  if (trimmed.isEmpty) {
    return trimmed;
  }
  return trimmed.endsWith('.')
      ? trimmed.substring(0, trimmed.length - 1)
      : trimmed;
}

String _firstNonEmpty(List<String> values) {
  for (final value in values) {
    final trimmed = value.trim();
    if (trimmed.isNotEmpty) {
      return trimmed;
    }
  }
  return '';
}

String _aspectLabel(String raw) {
  switch (raw.trim().toLowerCase()) {
    case 'conjunction':
      return 'Kavusum';
    case 'square':
      return 'Kare';
    case 'trine':
      return 'Ucgen';
    case 'sextile':
      return 'Sekstil';
    case 'opposition':
      return 'Karsi';
    default:
      return raw.trim();
  }
}

String _shortDate(String raw) {
  final parsed = DateTime.tryParse(raw.trim());
  if (parsed == null) {
    return '';
  }
  const months = <String>[
    'Ocak',
    'Subat',
    'Mart',
    'Nisan',
    'Mayis',
    'Haziran',
    'Temmuz',
    'Agustos',
    'Eylul',
    'Ekim',
    'Kasim',
    'Aralik',
  ];
  return '${parsed.day} ${months[parsed.month - 1]}';
}

Route<T> _adaptiveSkyRoute<T>(BuildContext context, WidgetBuilder builder) {
  final platform = Theme.of(context).platform;
  if (platform == TargetPlatform.iOS || platform == TargetPlatform.macOS) {
    return CupertinoPageRoute<T>(builder: builder);
  }
  return MaterialPageRoute<T>(builder: builder);
}
