// ignore_for_file: unused_element

import 'dart:ui' as ui;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import 'package:mobile/app/api/api_client.dart';
import 'package:mobile/app/people/friend_profile_page.dart';
import 'package:mobile/app/people/person_profile.dart';
import 'package:mobile/app/people/people_providers.dart';
import 'package:mobile/app/profile/profile_providers.dart';
import 'package:mobile/app/profile/profile_repository.dart';
import 'package:mobile/app/tabs/calendar_hub_page.dart';
import 'package:mobile/app/tabs/profile_detail_flow_page.dart';
import 'package:mobile/app/timing/narrative_dtos.dart';
import 'package:mobile/app/theme/app_theme_mode_provider.dart';
import 'package:mobile/design/astro/astro_theme_extension.dart';
import 'package:mobile/design/astro/astro_theme_generator.dart';
import 'package:mobile/design/astro/element_scores.dart';
import 'package:mobile/design/theme/profile_theme_extension.dart';
import 'package:mobile/design/widgets/jovia_editorial.dart';

const Color _kProfilePosterBg = Color(0xFF050505);
const Color _kProfilePosterSurface = Color(0xFF050505);
const Color _kProfilePosterSurfaceSoft = Color(0xFF090807);
const Color _kProfilePosterStroke = Color(0x285B4736);
const Color _kProfilePosterMuted = Color(0xFFC5BCD0);
const Color _kProfilePosterAccent = Color(0xFFFF8A1C);
const Color _kProfilePosterLilac = Color(0xFFB58DFF);
const Color _kProfilePosterBlush = Color(0xFFFFC5E7);
const Color _kProfilePosterMint = Color(0xFF9EF0E7);
const Color _kProfilePosterButter = Color(0xFFFFE5A4);

class ProfilePage extends StatefulWidget {
  const ProfilePage({
    super.key,
    this.viewedUserId,
    this.profileOverride,
    this.readOnly = false,
  });

  final String? viewedUserId;
  final Map<String, dynamic>? profileOverride;
  final bool readOnly;

  @override
  State<ProfilePage> createState() => _ProfilePageState();
}

class _ProfilePageState extends State<ProfilePage> {
  static const String _baseUrl = 'http://127.0.0.1:5000';
  static const Duration _natalCacheTtl = Duration(minutes: 5);
  static const Duration _fastProfileCacheTtl = Duration(minutes: 5);

  final _nameController = TextEditingController();
  final _birthDateController = TextEditingController();
  final _birthTimeController = TextEditingController();
  final _cityController = TextEditingController();
  final _countryController = TextEditingController();

  bool _didSeed = false;
  bool _isSaving = false;
  String? _saveMessage;
  bool _isAvatarUploading = false;
  String? _avatarUrl;

  bool _isNatalLoading = false;
  String? _natalHeadline;
  String? _natalSummary;
  String? _natalError;
  List<_SupportingThreadItem> _supportingThreads = const [];
  List<_ProfileNarrativeCard> _profilePrimaryCards = const [];
  List<_ProfileNarrativeCard> _profileExtraCards = const [];
  List<_ProfileNarrativeCard> _profilePlacementCards = const [];
  List<_ProfileInsightModule> _profileInsightModules = const [];
  List<_ProfileBundleTeaser> _profileBundleTeasers = const [];
  String _sunSign = '—';
  String _moonSign = '—';
  String _risingSign = '—';
  _ProfileIdentityContext? _identityContext;
  String? _lastNatalKey;
  int _segmentIndex = 0;

  @override
  void dispose() {
    _nameController.dispose();
    _birthDateController.dispose();
    _birthTimeController.dispose();
    _cityController.dispose();
    _countryController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Consumer(
      builder: (context, ref, _) {
        final profileAsync = widget.profileOverride == null
            ? ref.watch(userProfileProvider)
            : const AsyncValue<Map<String, dynamic>?>.data(null);
        final uid = ref.watch(currentUserIdProvider);
        final repo = ref.watch(profileRepositoryProvider);
        final currentUserEmail =
            Supabase.instance.client.auth.currentUser?.email;
        final peopleAsync = ref.watch(peopleListProvider);
        final authAvatarUrl = Supabase
            .instance
            .client
            .auth
            .currentUser
            ?.userMetadata?['avatar_url']
            ?.toString();
        final profile = widget.profileOverride ?? profileAsync.valueOrNull;
        final elementScores = _computeElementScores(
          profile: profile,
          userId: widget.viewedUserId ?? uid,
          email: currentUserEmail,
        );

        final themed = withAstroTheme(
          withProfileTheme(Theme.of(context)),
          astroTheme: astroThemeFromElementScores(elementScores),
        );

        return Theme(
          data: themed,
          child: Builder(
            builder: (context) {
              if (profile != null) {
                if (!_didSeed) {
                  _nameController.text = _nameController.text.isEmpty
                      ? (profile['full_name'] ?? profile['name'] ?? '')
                            .toString()
                      : _nameController.text;
                  _birthDateController.text = _birthDateController.text.isEmpty
                      ? (profile['birth_date'] ?? '').toString()
                      : _birthDateController.text;
                  _birthTimeController.text = _birthTimeController.text.isEmpty
                      ? (profile['birth_time'] ?? '').toString()
                      : _birthTimeController.text;
                  _cityController.text = _cityController.text.isEmpty
                      ? (profile['city'] ?? '').toString()
                      : _cityController.text;
                  _countryController.text = _countryController.text.isEmpty
                      ? (profile['country'] ?? '').toString()
                      : _countryController.text;
                  _avatarUrl = (profile['avatar_url'] ?? authAvatarUrl ?? '')
                      .toString();
                  _didSeed = true;
                }
                _maybeLoadNatalInterpretation(profile);
              }

              final displayName = _displayName(profile);
              final username = _displayUsername(
                profile: profile,
                email: currentUserEmail,
              );
              final avatarUrl = (_avatarUrl ?? authAvatarUrl ?? '').trim();
              final summaryText = (_natalSummary ?? '').trim();
              final dominantElementLabel = _dominantElementLabel(elementScores);
              final identityHeadline =
                  (_identityContext?.headline ?? _natalHeadline ?? '').trim();
              final identitySummary =
                  (_identityContext?.overview ?? summaryText).trim();
              final identityDrivers = _identityContext?.drivers ?? const [];
              final imprintHeadline = (_identityContext?.imprintHeadline ?? '')
                  .trim();
              final leadInsight = _pickLeadInsightModule();
              final curatedCards = _uniqueNarrativeCards([
                ..._profilePrimaryCards,
                ..._profileExtraCards,
              ]).where((item) => !item.isPlacementLike).toList();
              final headlineCard = _pickNarrativeCard(
                source: curatedCards,
                preferredFamilies: const {
                  'outer_inner_split',
                  'contradiction_core',
                  'self_definition',
                  'identity',
                },
                keywords: const [
                  'dışarıda',
                  'disarida',
                  'disaridan',
                  'içeride',
                  'iceride',
                  'farklı',
                  'farkli',
                  'ilk his',
                ],
              );
              final featuredCard = _pickNarrativeCard(
                source: curatedCards,
                preferredFamilies: const {
                  'self_definition',
                  'outer_inner_split',
                  'creative_channel',
                  'intimacy_guard',
                  'mind_mechanics',
                },
                keywords: const [
                  'ilk his',
                  'dışarıda',
                  'disarida',
                  'iceride',
                  'zihin',
                  'mind',
                  'yakınlık',
                  'yakinlik',
                  'ilişki',
                  'iliski',
                  'içeride',
                  'iceride',
                  'akış',
                  'akis',
                ],
                excludedKeys: headlineCard == null
                    ? const <String>{}
                    : <String>{_cardIdentity(headlineCard)},
              );
              final heroNarrativeCard = featuredCard ?? headlineCard;
              final teaserCards = curatedCards
                  .where(
                    (item) =>
                        (heroNarrativeCard == null ||
                            _cardIdentity(item) !=
                                _cardIdentity(heroNarrativeCard)) &&
                        (headlineCard == null ||
                            _cardIdentity(item) != _cardIdentity(headlineCard)),
                  )
                  .take(2)
                  .toList();
              final allSignatureCards = _profilePlacementCards.isNotEmpty
                  ? _profilePlacementCards
                  : _profileBundleTeasers
                        .map((item) => item.toNarrativeCard())
                        .take(12)
                        .toList();
              final signatureCards = allSignatureCards.take(3).toList();
              final sideThemes = _supportingThreads.take(3).toList();
              final mainHeadlineText = _profilePosterLeadText(
                headlineCard: headlineCard ?? heroNarrativeCard,
                identityHeadline: identityHeadline,
                identitySummary: identitySummary,
              );
              final locationLabel = _profileLocation(profile);
              final heroMetaLabel = [
                locationLabel,
                _profileAgeLabel(profile),
              ].where((item) => item.trim().isNotEmpty).join(' • ');
              final isDark = Theme.of(context).brightness == Brightness.dark;
              final isOwnProfile =
                  !widget.readOnly &&
                  (widget.viewedUserId == null || widget.viewedUserId == uid);
              int readProfileCount(List<String> keys) {
                for (final key in keys) {
                  final parsed = int.tryParse((profile?[key] ?? '').toString());
                  if (parsed != null) {
                    return parsed;
                  }
                }
                return 0;
              }

              final connectedPeople = isOwnProfile
                  ? (peopleAsync.valueOrNull ?? const <PersonProfile>[])
                  : const <PersonProfile>[];
              final followingCount = connectedPeople.isNotEmpty
                  ? connectedPeople.length
                  : readProfileCount(const [
                      'following_count',
                      'following',
                      'friends_count',
                    ]);
              final followerCount = readProfileCount(const [
                'followers_count',
                'followers',
                'follower_count',
              ]);
              final peoplePreview = connectedPeople.take(4).toList();
              final profileMenuTap = widget.readOnly || uid == null
                  ? null
                  : () => _showProfileMenu(
                      context: context,
                      ref: ref,
                      uid: uid,
                      repo: repo,
                      currentUserEmail: currentUserEmail,
                    );
              final profileStats = <_ProfileStatItem>[
                _ProfileStatItem(value: '$followingCount', label: 'Takip'),
                _ProfileStatItem(value: '$followerCount', label: 'Takipçi'),
              ];
              final editorialStatementTitle = _profilePosterEditorialTitle(
                identityHeadline: identityHeadline,
                heroNarrativeCard: heroNarrativeCard,
                mainHeadlineText: mainHeadlineText,
              );
              final editorialStatementBody = _profilePosterEditorialBody(
                identitySummary: identitySummary,
                headlineCard: headlineCard ?? heroNarrativeCard,
                mainHeadlineText: mainHeadlineText,
              );
              final leadSectionBody = _profilePosterLeadNarrative(
                displayName: displayName,
                mainHeadlineText: mainHeadlineText,
                editorialStatementBody: editorialStatementBody,
                headlineCard: headlineCard,
                heroNarrativeCard: heroNarrativeCard,
              );
              final leadSectionChips = _profilePosterLeadChips(
                headlineCard: headlineCard,
                heroNarrativeCard: heroNarrativeCard,
                drivers: identityDrivers,
              );
              final showLeadSection =
                  heroNarrativeCard != null &&
                  (leadSectionBody.trim().isNotEmpty ||
                      mainHeadlineText.trim().isNotEmpty);
              final featureTiles = <_ProfilePosterFeatureTileData>[
                for (final card in teaserCards.take(2))
                  _ProfilePosterFeatureTileData(
                    title: card.title,
                    subtitle: card.summary.isNotEmpty
                        ? card.summary
                        : card.previewBody,
                    asset: _illustrationForCard(card),
                    onTap: () => _openNarrativeFlow(selectedCard: card),
                  ),
                if (leadInsight != null)
                  _ProfilePosterFeatureTileData(
                    title: leadInsight.title,
                    subtitle: leadInsight.subheadline.isNotEmpty
                        ? leadInsight.subheadline
                        : leadInsight.headline,
                    asset: JoviaIllustrationAsset.blocks,
                    onTap: () => _openInsightFlow(module: leadInsight),
                  )
                else if (sideThemes.isNotEmpty)
                  _ProfilePosterFeatureTileData(
                    title: sideThemes.first.title,
                    subtitle: sideThemes.first.oneLiner,
                    asset:
                        _containsAny(
                          '${sideThemes.first.title} ${sideThemes.first.oneLiner}',
                          const ['sevgi', 'yakın', 'yakin', 'kalp', 'ilişki'],
                        )
                        ? JoviaIllustrationAsset.heart
                        : JoviaIllustrationAsset.layers,
                    onTap: () => _openSideThemesFlow(
                      items: sideThemes,
                      selected: sideThemes.first,
                    ),
                  ),
              ].take(3).toList();
              final darkContentView = Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (_natalError != null &&
                      _natalError!.trim().isNotEmpty &&
                      identityHeadline.isEmpty &&
                      curatedCards.isEmpty) ...[
                    _ProfilePosterMessageCard(
                      title: 'Yorum akışı alınamadı',
                      body: _natalError!,
                    ),
                    const SizedBox(height: 20),
                  ],
                  if (!_hasBirthData(profile)) ...[
                    _ProfilePosterMessageCard(
                      title: 'Doğum bilgisi bekleniyor',
                      body:
                          'Bu ekran `core_story_ui`, `profile_narrative`, `personality_imprint` ve `insight_modules` alanlarıyla doluyor. Profil ayarlarından doğum tarihini, saati ve yeri tamamladığında içerik otomatik açılır.',
                    ),
                  ] else ...[
                    if (_isNatalLoading &&
                        identitySummary.isEmpty &&
                        curatedCards.isEmpty)
                      const _ProfilePosterLoadingCard(),
                    const Center(
                      child: _ProfilePosterSectionTag(label: 'Kimlik ekseni'),
                    ),
                    const SizedBox(height: 16),
                    Center(
                      child: _ProfilePosterQuickInfoRow(
                        dominantElementLabel: dominantElementLabel,
                        auraSourceLabel:
                            _identityContext?.auraSourceLabel ?? '',
                        rulerName: _identityContext?.rulerName ?? '',
                        rulerHouse: _identityContext?.rulerHouse,
                        element: elementScores.dominant,
                        risingSign: _risingSign,
                      ),
                    ),
                    if (editorialStatementTitle.trim().isNotEmpty ||
                        editorialStatementBody.trim().isNotEmpty) ...[
                      const SizedBox(height: 30),
                      Center(
                        child: ConstrainedBox(
                          constraints: const BoxConstraints(maxWidth: 420),
                          child: _ProfilePosterEditorialStatement(
                            title: editorialStatementTitle,
                            body: editorialStatementBody,
                          ),
                        ),
                      ),
                    ],
                    const SizedBox(height: 24),
                    Center(
                      child: ConstrainedBox(
                        constraints: const BoxConstraints(maxWidth: 248),
                        child: _ProfilePosterModeSwitch(
                          currentIndex: _segmentIndex,
                          onChanged: (value) {
                            if (value == _segmentIndex) {
                              return;
                            }
                            setState(() => _segmentIndex = value);
                          },
                        ),
                      ),
                    ),
                    const SizedBox(height: 24),
                    if (_segmentIndex == 0) ...[
                      if (showLeadSection) ...[
                        _ProfilePosterLeadSection(
                          title: 'Ana Hikayen',
                          subtitle: '',
                          intro: mainHeadlineText,
                          body: leadSectionBody,
                          chips: leadSectionChips,
                          illustrationAsset: _profilePosterIllustrationForCard(
                            heroNarrativeCard,
                          ),
                          onTap: () => _openNarrativeFlow(
                            selectedCard: heroNarrativeCard,
                          ),
                        ),
                      ] else if (heroNarrativeCard != null) ...[
                        _NarrativeCardLarge(
                          eyebrow: heroNarrativeCard.eyebrow,
                          title: heroNarrativeCard.title,
                          intro: heroNarrativeCard.summary,
                          body: heroNarrativeCard.previewBody,
                          chips: heroNarrativeCard.chips,
                          illustrationAsset: JoviaIllustrationAsset.rocks,
                          actionLabel: 'Tam okumayı aç',
                          nextLabel: teaserCards.isNotEmpty
                              ? teaserCards.first.title
                              : (signatureCards.isNotEmpty
                                    ? 'İmza Katmanları'
                                    : 'Yan Temalar'),
                          onTap: () => _openNarrativeFlow(
                            selectedCard: heroNarrativeCard,
                          ),
                        ),
                      ],
                      if (featureTiles.isNotEmpty) ...[
                        const SizedBox(height: 24),
                        _ProfilePosterFeatureRail(items: featureTiles),
                      ],
                      if (leadInsight != null) ...[
                        const SizedBox(height: 30),
                        _ProfilePosterInsightEntryCard(
                          title: leadInsight.title,
                          body: leadInsight.subheadline.isNotEmpty
                              ? leadInsight.subheadline
                              : leadInsight.headline,
                          ctaLabel: 'Savunma mekanizmanı aç',
                          onTap: () => _openInsightFlow(module: leadInsight),
                        ),
                      ],
                      if (signatureCards.isNotEmpty) ...[
                        const SizedBox(height: 30),
                        _ProfilePosterPlacementsStrip(
                          sectionTitle: imprintHeadline.isNotEmpty
                              ? imprintHeadline
                              : 'İmza Katmanları',
                          cards: signatureCards,
                          onOpenAll: () => _openSignatureFlow(
                            title: imprintHeadline.isNotEmpty
                                ? imprintHeadline
                                : 'İmza Katmanları',
                            cards: allSignatureCards,
                          ),
                          onOpenCard: (card) => _openSignatureFlow(
                            title: imprintHeadline.isNotEmpty
                                ? imprintHeadline
                                : 'İmza Katmanları',
                            cards: allSignatureCards,
                            selected: card,
                          ),
                        ),
                      ],
                      if (sideThemes.isNotEmpty) ...[
                        const SizedBox(height: 28),
                        _ProfilePosterThreadSection(
                          items: sideThemes,
                          onOpenAll: () =>
                              _openSideThemesFlow(items: sideThemes),
                          onOpenThread: (thread) => _openSideThemesFlow(
                            items: sideThemes,
                            selected: thread,
                          ),
                        ),
                      ],
                    ] else ...[
                      PeriodCalendarTab(
                        profileOverride: widget.profileOverride,
                        embedded: true,
                      ),
                    ],
                  ],
                ],
              );

              final lightContentView = Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (_natalError != null &&
                      _natalError!.trim().isNotEmpty &&
                      identityHeadline.isEmpty &&
                      curatedCards.isEmpty) ...[
                    JoviaReadingPanel(
                      label: 'Uyarı',
                      title: 'Yorum akışı alınamadı',
                      body: _natalError!,
                    ),
                    const SizedBox(height: 20),
                  ],
                  if (!_hasBirthData(profile)) ...[
                    const JoviaReadingPanel(
                      label: 'Profil',
                      title: 'Doğum bilgisi bekleniyor',
                      body:
                          'Bu ekran core story, profile narrative ve insight alanlarıyla doluyor. Doğum tarihini, saati ve yeri tamamladığında içerik otomatik açılır.',
                    ),
                  ] else ...[
                    _ProfileIdentityHeaderCard(
                      displayName: displayName,
                      username: username,
                      avatarUrl: avatarUrl.isEmpty ? null : avatarUrl,
                      isAvatarUploading: _isAvatarUploading,
                      onAvatarEdit: widget.readOnly
                          ? null
                          : _pickAndUploadAvatar,
                      dominantElementLabel: dominantElementLabel,
                      sunSign: _sunSign,
                      moonSign: _moonSign,
                      risingSign: _risingSign,
                      stats: profileStats,
                    ),
                    if (_identityContext != null) ...[
                      const SizedBox(height: 20),
                      _ProfileIdentityQuickSection(
                        contextData: _identityContext!,
                        dominantElementLabel: dominantElementLabel,
                      ),
                    ],
                    if (editorialStatementTitle.trim().isNotEmpty ||
                        editorialStatementBody.trim().isNotEmpty) ...[
                      const SizedBox(height: 24),
                      JoviaReadingPanel(
                        label: 'Kimlik ekseni',
                        title: editorialStatementTitle.trim().isNotEmpty
                            ? editorialStatementTitle
                            : 'Kimlik ekseni',
                        body: editorialStatementBody,
                      ),
                    ],
                    const SizedBox(height: 24),
                    Center(
                      child: ConstrainedBox(
                        constraints: const BoxConstraints(maxWidth: 248),
                        child: _ProfilePosterModeSwitch(
                          currentIndex: _segmentIndex,
                          onChanged: (value) {
                            if (value == _segmentIndex) {
                              return;
                            }
                            setState(() => _segmentIndex = value);
                          },
                        ),
                      ),
                    ),
                    const SizedBox(height: 24),
                    if (_segmentIndex == 0)
                      _ProfileRecoveryReadingBody(
                        isLoading: _isNatalLoading,
                        error: _natalError,
                        summary: identitySummary,
                        supportingThreads: sideThemes,
                        primaryCards: curatedCards,
                        placementCards: allSignatureCards,
                        insightModules: _profileInsightModules,
                        onOpenPlacementFlow: allSignatureCards.isEmpty
                            ? null
                            : () => _openSignatureFlow(
                                title: imprintHeadline.isNotEmpty
                                    ? imprintHeadline
                                    : 'İmza Katmanları',
                                cards: allSignatureCards,
                              ),
                        readOnly: widget.readOnly,
                      )
                    else
                      PeriodCalendarTab(
                        profileOverride: widget.profileOverride,
                        embedded: true,
                      ),
                  ],
                ],
              );

              final footer = widget.readOnly
                  ? _ProfilePosterFooterButton(
                      label: 'Geri dön',
                      onTap: () =>
                          Navigator.of(context, rootNavigator: true).maybePop(),
                    )
                  : Row(
                      children: [
                        Expanded(
                          child: _ProfilePosterFooterButton(
                            label: _segmentIndex == 0
                                ? 'Timing akışını aç'
                                : 'Harita akışına dön',
                            emphasized: true,
                            onTap: () {
                              setState(
                                () =>
                                    _segmentIndex = _segmentIndex == 0 ? 1 : 0,
                              );
                            },
                          ),
                        ),
                      ],
                    );

              if (!isDark) {
                final profileTheme = context.profileTheme;
                return Scaffold(
                  backgroundColor: profileTheme.colors.bg,
                  body: DecoratedBox(
                    decoration: BoxDecoration(color: profileTheme.colors.bg),
                    child: JoviaPageScaffold(
                      padding: const EdgeInsets.fromLTRB(20, 14, 20, 28),
                      child: ListView(
                        padding: EdgeInsets.zero,
                        children: [
                          Row(
                            children: [
                              SizedBox(
                                width: 72,
                                child: widget.readOnly
                                    ? Align(
                                        alignment: Alignment.centerLeft,
                                        child: JoviaGlassIconButton(
                                          onTap: () => Navigator.of(
                                            context,
                                            rootNavigator: true,
                                          ).maybePop(),
                                          child: const JoviaUiIcon(
                                            asset: JoviaUiAsset.back,
                                            size: 18,
                                          ),
                                        ),
                                      )
                                    : Text(
                                        'PROFIL',
                                        style: profileTheme.typography.eyebrow
                                            .copyWith(
                                              color: profileTheme.colors.text,
                                              fontSize: 13,
                                              fontWeight: FontWeight.w700,
                                              letterSpacing: 2.4,
                                            ),
                                      ),
                              ),
                              Expanded(
                                child: Text(
                                  username,
                                  textAlign: TextAlign.center,
                                  maxLines: 1,
                                  overflow: TextOverflow.ellipsis,
                                  style: profileTheme.typography.micro.copyWith(
                                    color: profileTheme.colors.text,
                                    fontSize: 13.5,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                              ),
                              SizedBox(
                                width: 72,
                                child: Align(
                                  alignment: Alignment.centerRight,
                                  child: profileMenuTap == null
                                      ? const SizedBox(width: 40, height: 40)
                                      : JoviaGlassIconButton(
                                          onTap: profileMenuTap,
                                          child: const JoviaUiIcon(
                                            asset: JoviaUiAsset.menuStack,
                                            size: 18,
                                          ),
                                        ),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 20),
                          lightContentView,
                          const SizedBox(height: 20),
                          footer,
                        ],
                      ),
                    ),
                  ),
                );
              }

              return Scaffold(
                backgroundColor: _kProfilePosterBg,
                body: ColoredBox(
                  color: _kProfilePosterBg,
                  child: Stack(
                    children: [
                      JoviaPageScaffold(
                        padding: const EdgeInsets.fromLTRB(0, 14, 0, 28),
                        child: ListView(
                          padding: EdgeInsets.zero,
                          children: [
                            Padding(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 16,
                              ),
                              child: _ProfilePosterTopBar(
                                username: username,
                                readOnly: widget.readOnly,
                                onLeadingTap: widget.readOnly
                                    ? () => Navigator.of(
                                        context,
                                        rootNavigator: true,
                                      ).maybePop()
                                    : null,
                                onActionTap: profileMenuTap,
                              ),
                            ),
                            const SizedBox(height: 20),
                            _ProfilePosterHeader(
                              displayName: displayName,
                              avatarUrl: avatarUrl.isEmpty ? null : avatarUrl,
                              isAvatarUploading: _isAvatarUploading,
                              onAvatarEdit: widget.readOnly
                                  ? null
                                  : _pickAndUploadAvatar,
                              metaLabel: heroMetaLabel,
                              followingCount: followingCount,
                              followerCount: followerCount,
                              peoplePreview: peoplePreview,
                              sunSign: _sunSign,
                              moonSign: _moonSign,
                              risingSign: _risingSign,
                              onConnectionsTap: connectedPeople.isEmpty
                                  ? null
                                  : () =>
                                        _showConnectionsSheet(connectedPeople),
                              onPrimaryTap: () => _openIdentityFlow(
                                displayName: displayName,
                                headline: identityHeadline,
                                summary: identitySummary,
                                drivers: identityDrivers,
                              ),
                            ),
                            const SizedBox(height: 24),
                            Padding(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 16,
                              ),
                              child: darkContentView,
                            ),
                            const SizedBox(height: 20),
                            Padding(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 16,
                              ),
                              child: footer,
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              );
            },
          ),
        );
      },
    );
  }

  Future<void> _pickAndUploadAvatar() async {
    final uid = Supabase.instance.client.auth.currentUser?.id;
    if (uid == null || _isAvatarUploading) {
      return;
    }

    try {
      final picker = ImagePicker();
      final picked = await picker.pickImage(
        source: ImageSource.gallery,
        maxWidth: 1400,
        imageQuality: 88,
      );
      if (picked == null) {
        return;
      }

      setState(() => _isAvatarUploading = true);
      final bytes = await picked.readAsBytes();
      final ext = picked.name.toLowerCase().endsWith('.png') ? 'png' : 'jpg';
      final path = '$uid/avatar.$ext';
      final contentType = ext == 'png' ? 'image/png' : 'image/jpeg';

      await Supabase.instance.client.storage
          .from('avatars')
          .uploadBinary(
            path,
            bytes,
            fileOptions: FileOptions(
              upsert: true,
              cacheControl: '3600',
              contentType: contentType,
            ),
          );
      final publicUrl = Supabase.instance.client.storage
          .from('avatars')
          .getPublicUrl(path);

      await Supabase.instance.client.auth.updateUser(
        UserAttributes(data: <String, dynamic>{'avatar_url': publicUrl}),
      );

      if (!mounted) {
        return;
      }
      setState(() => _avatarUrl = publicUrl);
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('Profil resmi güncellendi')));
    } catch (error) {
      if (!mounted) {
        return;
      }
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Profil resmi yüklenemedi: $error')),
      );
    } finally {
      if (mounted) {
        setState(() => _isAvatarUploading = false);
      }
    }
  }

  ElementScores _computeElementScores({
    required Map<String, dynamic>? profile,
    required String? userId,
    required String? email,
  }) {
    final fromProfile = _extractElementScoresFromProfile(profile);
    if (fromProfile != null) {
      return fromProfile;
    }

    final fromSigns = _extractElementScoresFromKnownSigns();
    if (fromSigns != null) {
      return fromSigns;
    }

    return _deterministicElementScores(seed: userId ?? email ?? 'anon');
  }

  ElementScores? _extractElementScoresFromProfile(
    Map<String, dynamic>? profile,
  ) {
    if (profile == null) {
      return null;
    }

    final direct = _extractElementScoresFromAny(profile);
    if (direct != null) {
      return direct;
    }

    for (final key in const <String>[
      'element_scores',
      'elements',
      'natal_element_scores',
      'astro_element_scores',
    ]) {
      final nested = _extractElementScoresFromAny(profile[key]);
      if (nested != null) {
        return nested;
      }
    }
    return null;
  }

  ElementScores? _extractElementScoresFromAny(dynamic source) {
    if (source is! Map) {
      return null;
    }
    final map = Map<String, dynamic>.from(source);
    final keys = map.keys.map((k) => k.toLowerCase()).toSet();
    if (!keys.contains('fire') ||
        !keys.contains('water') ||
        !keys.contains('air') ||
        !keys.contains('earth')) {
      return null;
    }
    return ElementScores.fromMap(map);
  }

  ElementScores? _extractElementScoresFromKnownSigns() {
    final weights = <AstroElement, double>{
      AstroElement.fire: 0,
      AstroElement.water: 0,
      AstroElement.air: 0,
      AstroElement.earth: 0,
    };

    void addSign(String sign, double weight) {
      final element = _elementFromSign(sign);
      if (element == null) {
        return;
      }
      weights[element] = (weights[element] ?? 0) + weight;
    }

    addSign(_sunSign, 0.4);
    addSign(_moonSign, 0.35);
    addSign(_risingSign, 0.25);

    if (weights.values.every((v) => v == 0)) {
      return null;
    }
    return ElementScores(
      fire: weights[AstroElement.fire] ?? 0,
      water: weights[AstroElement.water] ?? 0,
      air: weights[AstroElement.air] ?? 0,
      earth: weights[AstroElement.earth] ?? 0,
    ).normalize();
  }

  AstroElement? _elementFromSign(String rawSign) {
    final sign = rawSign.trim().toLowerCase();
    if (sign.isEmpty || sign == '—') {
      return null;
    }
    const fire = <String>{
      'aries',
      'leo',
      'sagittarius',
      'koc',
      'koç',
      'aslan',
      'yay',
    };
    const earth = <String>{
      'taurus',
      'virgo',
      'capricorn',
      'boga',
      'boğa',
      'basak',
      'başak',
      'oglak',
      'oğlak',
    };
    const air = <String>{
      'gemini',
      'libra',
      'aquarius',
      'ikizler',
      'terazi',
      'kova',
    };
    const water = <String>{
      'cancer',
      'scorpio',
      'pisces',
      'yengec',
      'yengeç',
      'akrep',
      'balik',
      'balık',
    };
    if (fire.contains(sign)) {
      return AstroElement.fire;
    }
    if (water.contains(sign)) {
      return AstroElement.water;
    }
    if (air.contains(sign)) {
      return AstroElement.air;
    }
    if (earth.contains(sign)) {
      return AstroElement.earth;
    }
    return null;
  }

  ElementScores _deterministicElementScores({required String seed}) {
    // Replace this with backend-provided element scores when API adds it.
    final hash = seed.codeUnits.fold<int>(
      17,
      (acc, c) => (acc * 31 + c) & 0x7fffffff,
    );
    final dominant = hash % 4;
    final values = <double>[0.22, 0.22, 0.22, 0.22];
    values[dominant] += 0.34;
    return ElementScores(
      fire: values[0],
      water: values[1],
      air: values[2],
      earth: values[3],
    ).normalize();
  }

  String _dominantElementLabel(ElementScores scores) {
    return switch (scores.dominant) {
      AstroElement.fire => 'Ateş baskın',
      AstroElement.water => 'Su baskın',
      AstroElement.air => 'Hava baskın',
      AstroElement.earth => 'Toprak baskın',
    };
  }

  String _displayName(Map<String, dynamic>? profile) {
    final fromProfile = (profile?['full_name'] ?? profile?['name'] ?? '')
        .toString()
        .trim();
    if (fromProfile.isNotEmpty) {
      return fromProfile;
    }
    final fromInput = _nameController.text.trim();
    if (fromInput.isNotEmpty) {
      return fromInput;
    }
    return 'Isimsiz Profil';
  }

  String _displayUsername({
    required Map<String, dynamic>? profile,
    required String? email,
  }) {
    final raw = (profile?['username'] ?? profile?['handle'] ?? '')
        .toString()
        .trim();
    if (raw.isNotEmpty) {
      return raw.startsWith('@') ? raw : '@$raw';
    }
    final mailPart = (email ?? '').split('@').first.trim();
    if (mailPart.isNotEmpty) {
      return '@${mailPart.toLowerCase()}';
    }
    final fallback = _displayName(
      profile,
    ).toLowerCase().replaceAll(RegExp(r'[^a-z0-9]+'), '');
    return fallback.isEmpty ? '@profile' : '@$fallback';
  }

  bool _hasBirthData(Map<String, dynamic>? profile) {
    if (profile == null) {
      return false;
    }
    final birthDate = (profile['birth_date'] ?? '').toString().trim();
    final birthTime = (profile['birth_time'] ?? '').toString().trim();
    final city = (profile['city'] ?? '').toString().trim();
    final country = (profile['country'] ?? '').toString().trim();
    final placeRaw = (profile['place'] ?? '').toString().trim();
    final place = placeRaw.isNotEmpty
        ? placeRaw
        : (city.isEmpty
              ? country
              : (country.isEmpty ? city : '$city, $country'));
    return birthDate.isNotEmpty && birthTime.isNotEmpty && place.isNotEmpty;
  }

  void _maybeLoadNatalInterpretation(Map<String, dynamic> profile) {
    if (!_hasBirthData(profile)) {
      return;
    }
    final city = (profile['city'] ?? '').toString().trim();
    final country = (profile['country'] ?? '').toString().trim();
    final placeRaw = (profile['place'] ?? '').toString().trim();
    final place = placeRaw.isNotEmpty
        ? placeRaw
        : (city.isEmpty
              ? country
              : (country.isEmpty ? city : '$city, $country'));
    final key =
        '${profile['birth_date']}|${profile['birth_time']}|$place|${profile['timezone'] ?? ''}';
    if (_lastNatalKey == key) {
      return;
    }
    _lastNatalKey = key;
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) {
        return;
      }
      _loadNatalInterpretation(profile);
    });
  }

  Future<void> _loadNatalInterpretation(Map<String, dynamic> profile) async {
    final city = (profile['city'] ?? '').toString().trim();
    final country = (profile['country'] ?? '').toString().trim();
    final placeRaw = (profile['place'] ?? '').toString().trim();
    final place = placeRaw.isNotEmpty
        ? placeRaw
        : (city.isEmpty
              ? country
              : (country.isEmpty ? city : '$city, $country'));
    final payload = <String, dynamic>{
      'birth_date': (profile['birth_date'] ?? '').toString().trim(),
      'birth_time': _normalizeBirthTime(
        (profile['birth_time'] ?? '').toString(),
      ),
      'birth_place': place,
      'locale': 'tr',
    };

    setState(() {
      _isNatalLoading = true;
      _natalError = null;
    });

    try {
      final client = ApiClient(baseUrl: _baseUrl);
      final responses = await Future.wait<Map<String, dynamic>>([
        _safePostMap(
          client,
          '/interpret/ui',
          data: payload,
          cacheTtl: _natalCacheTtl,
        ),
        _safePostMap(
          client,
          '/profile/fast',
          data: payload,
          cacheTtl: _fastProfileCacheTtl,
        ),
      ]);
      final publicMap = responses[0];
      final fastMap = responses[1];
      final shouldLoadLegacyFallback =
          publicMap.isEmpty ||
          (_extractNatalSummary(publicMap).trim().isEmpty &&
              _extractProfileNarrativeCards(
                publicMap,
                field: 'core_blocks',
              ).isEmpty &&
              _extractSupportingThreads(publicMap).isEmpty);
      final legacyMap = shouldLoadLegacyFallback
          ? await _safePostMap(
              client,
              '/interpret',
              data: payload,
              cacheTtl: _natalCacheTtl,
            )
          : <String, dynamic>{};
      final activeMap = publicMap.isNotEmpty
          ? _mergeMaps(publicMap, legacyMap)
          : legacyMap;

      if (activeMap.isEmpty) {
        throw Exception('Profile public payload is empty.');
      }

      final summary = _extractNatalSummary(activeMap);
      final headline = _extractNatalHeadline(activeMap);
      final supportingThreads = _extractSupportingThreads(activeMap);
      final profileBlocks = _extractProfileNarrativeCards(
        activeMap,
        field: 'blocks',
      );
      final coreBlocks = _extractProfileNarrativeCards(
        activeMap,
        field: 'core_blocks',
      );
      final extraBlocks = _extractProfileNarrativeCards(
        activeMap,
        field: 'extra_blocks',
      );
      final detailCards = _extractProfileNarrativeCards(
        activeMap,
        field: 'detail_cards',
      );
      final personalityCards = _extractPersonalityImprintCards(activeMap);
      final bundleTeasers = _extractBundleTeasers(activeMap);
      final identityContext = _buildIdentityContext(
        map: activeMap,
        fastMap: fastMap,
        profileBlocks: profileBlocks,
        coreBlocks: coreBlocks,
        extraBlocks: extraBlocks,
      );
      final primaryCards = _mergeNarrativeCards(
        coreBlocks.isNotEmpty ? coreBlocks : profileBlocks,
      );
      final extraNarrativeCards = _mergeNarrativeCards(extraBlocks);
      final placementCards = _selectSignatureCards([
        ...detailCards,
        ...personalityCards,
        if (detailCards.isEmpty && personalityCards.isEmpty)
          ...bundleTeasers
              .map((item) => item.toNarrativeCard())
              .where((item) => item.title.isNotEmpty),
      ]);
      final insightModules = _extractProfileInsightModules(activeMap);
      final fastSnapshot = _extractProfileFastSnapshot(fastMap);
      final signSource = legacyMap.isNotEmpty ? legacyMap : activeMap;
      final sun =
          fastSnapshot?.sunSign ?? _extractPlanetSign(signSource, 'Sun');
      final moon =
          fastSnapshot?.moonSign ?? _extractPlanetSign(signSource, 'Moon');
      final rising = fastSnapshot?.risingSign ?? _extractRisingSign(signSource);
      if (!mounted) {
        return;
      }

      setState(() {
        _natalHeadline = headline;
        _natalSummary = summary;
        _supportingThreads = supportingThreads;
        _profilePrimaryCards = primaryCards;
        _profileExtraCards = extraNarrativeCards;
        _profilePlacementCards = placementCards;
        _profileInsightModules = insightModules;
        _profileBundleTeasers = bundleTeasers;
        _identityContext = identityContext;
        _sunSign = _toTrSign(sun);
        _moonSign = _toTrSign(moon);
        _risingSign = _toTrSign(rising);
        _isNatalLoading = false;
      });
    } catch (e) {
      if (!mounted) {
        return;
      }
      setState(() {
        _isNatalLoading = false;
        _natalHeadline = null;
        _supportingThreads = const [];
        _profileExtraCards = const [];
        _profileBundleTeasers = const [];
        _natalError = 'Natal yorum alinamadi: $e';
      });
    }
  }

  Future<Map<String, dynamic>> _safePostMap(
    ApiClient client,
    String path, {
    required Map<String, dynamic> data,
    Duration? cacheTtl,
  }) async {
    try {
      final response = await client.post(path, data: data, cacheTtl: cacheTtl);
      return _asMap(response.data);
    } catch (_) {
      return <String, dynamic>{};
    }
  }

  Future<void> _showSettingsSheet({
    required BuildContext context,
    required WidgetRef ref,
    required String uid,
    required ProfileRepository repo,
    required String? currentUserEmail,
  }) async {
    final profile = context.profileTheme;
    final astro = context.astroTheme;
    final spacing = profile.spacing;
    final typo = profile.typography;
    final inputDecoration = _profileInputDecoration(context);

    await showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (sheetContext) {
        return Padding(
          padding: EdgeInsets.only(
            left: spacing.lg,
            right: spacing.lg,
            top: spacing.lg,
            bottom: MediaQuery.of(sheetContext).viewInsets.bottom + spacing.lg,
          ),
          child: _GlassCard(
            child: SingleChildScrollView(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Text('Profil Ayarlari', style: typo.h2),
                  SizedBox(height: spacing.md),
                  TextField(
                    controller: _nameController,
                    style: typo.body,
                    decoration: inputDecoration.copyWith(labelText: 'Name'),
                  ),
                  SizedBox(height: spacing.sm),
                  TextField(
                    controller: _birthDateController,
                    style: typo.body,
                    decoration: inputDecoration.copyWith(
                      labelText: 'Birth date (YYYY-MM-DD)',
                    ),
                  ),
                  SizedBox(height: spacing.sm),
                  TextField(
                    controller: _birthTimeController,
                    style: typo.body,
                    decoration: inputDecoration.copyWith(
                      labelText: 'Birth time (HH:mm)',
                    ),
                  ),
                  SizedBox(height: spacing.sm),
                  TextField(
                    controller: _cityController,
                    style: typo.body,
                    decoration: inputDecoration.copyWith(labelText: 'City'),
                  ),
                  SizedBox(height: spacing.sm),
                  TextField(
                    controller: _countryController,
                    style: typo.body,
                    decoration: inputDecoration.copyWith(labelText: 'Country'),
                  ),
                  SizedBox(height: spacing.sm),
                  if (_saveMessage != null)
                    Text(
                      _saveMessage ?? '',
                      style: typo.micro.copyWith(
                        color:
                            (_saveMessage ?? '').toLowerCase().startsWith(
                              'error',
                            )
                            ? Theme.of(context).colorScheme.error
                            : Theme.of(context).colorScheme.primary,
                      ),
                    ),
                  SizedBox(height: spacing.md),
                  ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: astro.accent,
                      foregroundColor: astro.text,
                      disabledBackgroundColor: astro.accent.withValues(
                        alpha: 0.45,
                      ),
                      disabledForegroundColor: astro.text.withValues(
                        alpha: 0.75,
                      ),
                    ),
                    onPressed: _isSaving
                        ? null
                        : () async {
                            await _saveProfile(
                              ref: ref,
                              uid: uid,
                              repo: repo,
                              currentUserEmail: currentUserEmail,
                            );
                            if (!sheetContext.mounted) {
                              return;
                            }
                            if ((_saveMessage ?? '').startsWith('Saved')) {
                              Navigator.of(sheetContext).pop();
                            }
                          },
                    child: _isSaving
                        ? const SizedBox(
                            height: 18,
                            width: 18,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Text('Save'),
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  Future<void> _showProfileMenu({
    required BuildContext context,
    required WidgetRef ref,
    required String uid,
    required ProfileRepository repo,
    required String? currentUserEmail,
  }) async {
    final profile = context.profileTheme;
    await showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (sheetContext) {
        return Consumer(
          builder: (context, ref, _) {
            final currentMode = ref.watch(joviaThemeModeProvider);
            final maxHeight = MediaQuery.of(sheetContext).size.height * 0.82;
            return SafeArea(
              child: Padding(
                padding: EdgeInsets.all(profile.spacing.lg),
                child: ConstrainedBox(
                  constraints: BoxConstraints(maxHeight: maxHeight),
                  child: JoviaSurfaceCard(
                    padding: const EdgeInsets.fromLTRB(18, 18, 18, 18),
                    radius: 30,
                    child: SingleChildScrollView(
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          JoviaEditorialHeroBlock(
                            label: 'Control center',
                            title: 'Profil menüsü',
                            body:
                                'Ayarlar, görünüm modu ve profil düzeni için daha rafine bir panel.',
                            surface: false,
                            accent: const JoviaIllustrationAccent(
                              asset: JoviaIllustrationAsset.planet,
                              width: 70,
                              height: 70,
                              opacity: 0.76,
                            ),
                          ),
                          const SizedBox(height: 16),
                          JoviaSurfaceCard(
                            radius: 24,
                            padding: const EdgeInsets.all(14),
                            child: JoviaUtilityRow(
                              label: 'Settings',
                              title: 'Profili düzenle',
                              body:
                                  'İsim, doğum bilgileri ve diğer ayarları aç.',
                              leading: const JoviaUiIcon(
                                asset: JoviaUiAsset.settingsRings,
                                size: 18,
                              ),
                              onTap: () {
                                Navigator.of(sheetContext).pop();
                                _showSettingsSheet(
                                  context: context,
                                  ref: ref,
                                  uid: uid,
                                  repo: repo,
                                  currentUserEmail: currentUserEmail,
                                );
                              },
                            ),
                          ),
                          const SizedBox(height: 16),
                          Text(
                            'Tema modu',
                            style: profile.typography.eyebrow.copyWith(
                              color: profile.colors.textLight,
                              letterSpacing: 1.45,
                            ),
                          ),
                          const SizedBox(height: 10),
                          JoviaModeSwitch<JoviaThemeMode>(
                            value: currentMode,
                            leadingValue: JoviaThemeMode.dark,
                            leadingLabel: 'Dark',
                            trailingValue: JoviaThemeMode.light,
                            trailingLabel: 'Light',
                            onChanged: (mode) {
                              ref
                                  .read(joviaThemeModeProvider.notifier)
                                  .setMode(mode);
                            },
                          ),
                          const SizedBox(height: 16),
                          JoviaSurfaceCard(
                            radius: 24,
                            padding: const EdgeInsets.all(14),
                            child: JoviaUtilityRow(
                              label: 'Session',
                              title: 'Çıkış yap',
                              body:
                                  'Mevcut oturumu kapat ve giriş ekranına dön.',
                              leading: const JoviaUiIcon(
                                asset: JoviaUiAsset.profileComet,
                                size: 18,
                              ),
                              onTap: () async {
                                Navigator.of(sheetContext).pop();
                                await Supabase.instance.client.auth.signOut();
                              },
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
            );
          },
        );
      },
    );
  }

  Future<void> _showConnectionsSheet(List<PersonProfile> people) async {
    if (people.isEmpty) {
      return;
    }
    final profile = context.profileTheme;
    await showModalBottomSheet<void>(
      context: context,
      backgroundColor: Colors.transparent,
      isScrollControlled: true,
      builder: (sheetContext) {
        return Padding(
          padding: EdgeInsets.fromLTRB(
            profile.spacing.lg,
            profile.spacing.lg,
            profile.spacing.lg,
            profile.spacing.lg,
          ),
          child: JoviaSurfaceCard(
            radius: 30,
            padding: const EdgeInsets.fromLTRB(18, 18, 18, 18),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                JoviaEditorialHeroBlock(
                  label: 'Connections',
                  title: 'Eklediğin kişiler',
                  body:
                      'Takip ve takipçi alanından açılan gerçek arkadaş listen burada görünüyor.',
                  surface: false,
                  accent: const JoviaIllustrationAccent(
                    asset: JoviaIllustrationAsset.flower,
                    width: 68,
                    height: 68,
                    opacity: 0.8,
                  ),
                ),
                const SizedBox(height: 16),
                ConstrainedBox(
                  constraints: BoxConstraints(
                    maxHeight: MediaQuery.of(sheetContext).size.height * 0.58,
                  ),
                  child: ListView.separated(
                    shrinkWrap: true,
                    itemCount: people.length,
                    separatorBuilder: (_, _) => const SizedBox(height: 10),
                    itemBuilder: (context, index) {
                      final person = people[index];
                      return JoviaSurfaceCard(
                        radius: 24,
                        padding: const EdgeInsets.all(12),
                        child: JoviaUtilityRow(
                          label: 'Friend',
                          title: person.name,
                          body:
                              '${person.birthDate} • ${person.place.isEmpty ? 'konum eksik' : person.place}',
                          leading: _ProfilePosterMiniAvatar(
                            name: person.name,
                            tint: _profilePosterFeatureColor(index + 1),
                            size: 42,
                            showIndicator: false,
                          ),
                          trailing: const JoviaUiIcon(
                            asset: JoviaUiAsset.chevronRight,
                            size: 16,
                          ),
                          onTap: () {
                            Navigator.of(sheetContext).pop();
                            Navigator.of(context).push(
                              MaterialPageRoute<void>(
                                builder: (_) =>
                                    FriendProfilePage(personId: person.id),
                              ),
                            );
                          },
                        ),
                      );
                    },
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Future<void> _saveProfile({
    required WidgetRef ref,
    required String uid,
    required ProfileRepository repo,
    required String? currentUserEmail,
  }) async {
    setState(() {
      _isSaving = true;
      _saveMessage = null;
    });
    try {
      if (_readName().isEmpty ||
          _readBirthDate().isEmpty ||
          _readBirthTime().isEmpty ||
          _readCity().isEmpty ||
          _readCountry().isEmpty) {
        throw Exception('Please fill all fields.');
      }

      final place = _readCountry().isEmpty
          ? _readCity()
          : '${_readCity()}, ${_readCountry()}';
      final timezone = DateTime.now().timeZoneName;

      await repo.upsertProfileBasics(
        userId: uid,
        fullName: _readName(),
        email: currentUserEmail,
      );

      await repo.upsertBirthData(
        userId: uid,
        birthDate: _readBirthDate(),
        birthTime: _readBirthTime(),
        place: place,
        city: _readCity(),
        country: _readCountry(),
        timezone: timezone,
        latitude: null,
        longitude: null,
      );

      ref.invalidate(userProfileProvider);
      _lastNatalKey = null;
      _saveMessage = 'Saved successfully.';
    } catch (e) {
      _saveMessage = 'Error: $e';
    } finally {
      if (mounted) {
        setState(() {
          _isSaving = false;
        });
      }
    }
  }

  Map<String, dynamic> _asMap(dynamic data) {
    if (data == null) {
      return <String, dynamic>{};
    }
    if (data is Map<String, dynamic>) {
      return data;
    }
    if (data is Map) {
      return Map<String, dynamic>.from(data);
    }
    return <String, dynamic>{};
  }

  Map<String, dynamic> _mergeMaps(
    Map<String, dynamic> primary,
    Map<String, dynamic> fallback,
  ) {
    final result = Map<String, dynamic>.from(fallback);
    for (final entry in primary.entries) {
      final key = entry.key;
      final primaryValue = entry.value;
      final fallbackValue = result[key];
      if (primaryValue is Map && fallbackValue is Map) {
        result[key] = _mergeMaps(
          Map<String, dynamic>.from(primaryValue),
          Map<String, dynamic>.from(fallbackValue),
        );
        continue;
      }
      if (primaryValue is List &&
          primaryValue.isEmpty &&
          fallbackValue is List &&
          fallbackValue.isNotEmpty) {
        continue;
      }
      if (primaryValue is String &&
          primaryValue.trim().isEmpty &&
          fallbackValue is String &&
          fallbackValue.trim().isNotEmpty) {
        continue;
      }
      if (primaryValue == null && fallbackValue != null) {
        continue;
      }
      result[key] = primaryValue;
    }
    return result;
  }

  String _extractNatalSummary(Map<String, dynamic> map) {
    final public = map['public'];
    if (public is Map) {
      final ui = public['core_story_ui'];
      if (ui is Map && (ui['text'] ?? '').toString().trim().isNotEmpty) {
        return (ui['text'] ?? '').toString().trim();
      }
      if ((public['core_story'] ?? '').toString().trim().isNotEmpty) {
        return (public['core_story'] ?? '').toString();
      }
    }
    final directUi = map['core_story_ui'];
    if (directUi is Map &&
        (directUi['text'] ?? '').toString().trim().isNotEmpty) {
      return (directUi['text'] ?? '').toString().trim();
    }
    final direct = (map['core_story'] ?? '').toString().trim();
    if (direct.isNotEmpty) {
      return direct;
    }
    final fallback = (map['narrative_text'] ?? map['summary'] ?? '')
        .toString()
        .trim();
    return fallback;
  }

  String _extractNatalHeadline(Map<String, dynamic> map) {
    final public = map['public'];
    if (public is Map) {
      final ui = public['core_story_ui'];
      if (ui is Map && (ui['headline'] ?? '').toString().trim().isNotEmpty) {
        return (ui['headline'] ?? '').toString().trim();
      }
    }
    final directUi = map['core_story_ui'];
    if (directUi is Map &&
        (directUi['headline'] ?? '').toString().trim().isNotEmpty) {
      return (directUi['headline'] ?? '').toString().trim();
    }
    final blocks = _extractProfileNarrativeCards(map, field: 'core_blocks');
    if (blocks.isNotEmpty) {
      return blocks.first.title;
    }
    return '';
  }

  List<String> _extractCoreStoryDrivers(Map<String, dynamic> map) {
    List<String> read(dynamic raw) {
      if (raw is! List) {
        return const <String>[];
      }
      return raw
          .map((item) => item.toString().trim())
          .where((item) => item.isNotEmpty)
          .take(3)
          .toList();
    }

    final public = map['public'];
    if (public is Map) {
      final ui = public['core_story_ui'];
      if (ui is Map) {
        final drivers = read(ui['drivers']);
        if (drivers.isNotEmpty) {
          return drivers;
        }
      }
    }
    final directUi = map['core_story_ui'];
    if (directUi is Map) {
      final drivers = read(directUi['drivers']);
      if (drivers.isNotEmpty) {
        return drivers;
      }
    }
    return const <String>[];
  }

  String _extractPersonalityImprintHeadline(Map<String, dynamic> map) {
    final personalityImprint = _extractPublicField(map, 'personality_imprint');
    return (personalityImprint['headline'] ?? '').toString().trim();
  }

  Map<String, dynamic> _extractProfilePublicPayload(Map<String, dynamic> map) {
    for (final scope in _natalScopes(map)) {
      final narrative = _asMap(scope['profile_narrative']);
      final profilePublic = _asMap(narrative['profile_public']);
      if (profilePublic.isNotEmpty) {
        return profilePublic;
      }
    }
    return <String, dynamic>{};
  }

  List<_ProfileNarrativeCard> _extractProfileNarrativeCards(
    Map<String, dynamic> map, {
    required String field,
  }) {
    final profilePublic = _extractProfilePublicPayload(map);
    final raw = profilePublic[field];
    if (raw is! List) {
      return const [];
    }
    return raw
        .whereType<Map>()
        .map(
          (item) =>
              _ProfileNarrativeCard.fromMap(Map<String, dynamic>.from(item)),
        )
        .where((item) => item.title.isNotEmpty && item.previewBody.isNotEmpty)
        .toList();
  }

  List<_ProfileInsightModule> _extractProfileInsightModules(
    Map<String, dynamic> map,
  ) {
    final profilePublic = _extractProfilePublicPayload(map);
    final raw = profilePublic['insight_modules'];
    if (raw is! List) {
      return const [];
    }
    return raw
        .whereType<Map>()
        .map(
          (item) =>
              _ProfileInsightModule.fromMap(Map<String, dynamic>.from(item)),
        )
        .where((item) => item.headline.isNotEmpty && item.title.isNotEmpty)
        .toList();
  }

  List<_ProfileNarrativeCard> _extractPersonalityImprintCards(
    Map<String, dynamic> map,
  ) {
    final personalityImprint = _extractPublicField(map, 'personality_imprint');
    final cards = <_ProfileNarrativeCard>[];
    for (final field in const <String>[
      'entries',
      'extra_entries',
      'support_entries',
    ]) {
      final raw = personalityImprint[field];
      if (raw is! List) {
        continue;
      }
      for (final item in raw.whereType<Map>()) {
        final normalized = _personalityImprintCardMap(
          Map<String, dynamic>.from(item),
        );
        if (normalized.isEmpty) {
          continue;
        }
        final card = _ProfileNarrativeCard.fromMap(normalized);
        if (card.title.isEmpty || card.previewBody.isEmpty) {
          continue;
        }
        cards.add(card);
      }
    }
    return cards;
  }

  Map<String, dynamic> _personalityImprintCardMap(Map<String, dynamic> item) {
    final kind = (item['kind'] ?? '').toString().trim();
    final title = (item['label_tr'] ?? '').toString().trim();
    if (title.isEmpty) {
      return const <String, dynamic>{};
    }
    final family = switch (kind) {
      'aspect' => 'contradiction_core',
      'sign_placement' => 'tone_signature',
      _ => 'placement_signature',
    };
    final aura = (item['aura'] ?? '').toString().trim();
    final trait = (item['trait'] ?? '').toString().trim();
    final drive = (item['drive'] ?? '').toString().trim();
    final gift = (item['gift'] ?? '').toString().trim();
    final shadow = (item['shadow'] ?? '').toString().trim();
    final backgroundHint = (item['background_hint'] ?? '').toString().trim();
    final bodyParts = <String>[
      aura,
      trait,
      drive,
      gift,
      shadow,
      backgroundHint,
    ].where((item) => item.isNotEmpty);
    return <String, dynamic>{
      'card_key': '${(item['key'] ?? title).toString().trim()}_library_detail',
      'id': (item['key'] ?? '').toString().trim(),
      'family': family,
      'origin': 'personality_imprint',
      'eyebrow': switch (kind) {
        'aspect' => 'Aci izi',
        'sign_placement' => 'Ton izi',
        _ => 'Kisilik izi',
      },
      'title': title,
      'summary': aura.isNotEmpty ? aura : (trait.isNotEmpty ? trait : drive),
      'body': bodyParts.join('\n\n'),
      'micro': gift,
      'chips': item['tags'],
    };
  }

  List<_ProfileNarrativeCard> _mergeNarrativeCards(
    List<_ProfileNarrativeCard> items,
  ) {
    final seen = <String>{};
    final out = <_ProfileNarrativeCard>[];
    for (final item in items) {
      if (item.isPlacementLike) {
        continue;
      }
      final key = item.cardKey.isNotEmpty ? item.cardKey : item.title;
      if (key.isEmpty || !seen.add(key)) {
        continue;
      }
      out.add(item);
    }
    return out;
  }

  List<_ProfileNarrativeCard> _selectSignatureCards(
    List<_ProfileNarrativeCard> items,
  ) {
    final preferred = <_ProfileNarrativeCard>[];
    final secondary = <_ProfileNarrativeCard>[];
    final seen = <String>{};
    for (final item in items) {
      final key = _signatureCardIdentity(item);
      if (key.isEmpty || !seen.add(key)) {
        continue;
      }
      final isSignatureLike =
          item.origin == 'personality_imprint' ||
          item.family == 'placement_signature' ||
          item.family == 'tone_signature' ||
          item.family == 'contradiction_core';
      if (isSignatureLike) {
        preferred.add(item);
      } else {
        secondary.add(item);
      }
    }
    if (preferred.isNotEmpty) {
      return [...preferred, ...secondary].take(12).toList();
    }
    return _uniqueSignatureCards(items).take(12).toList();
  }

  String _extractPlanetSign(Map<String, dynamic> map, String planetName) {
    final targets = <String>{
      planetName.toLowerCase(),
      if (planetName.toLowerCase() == 'ascendant') ...{'ascendant', 'asc'},
    };

    for (final scope in _natalScopes(map)) {
      final planets = scope['planets'];
      if (planets is List) {
        for (final raw in planets) {
          if (raw is! Map) {
            continue;
          }
          final name = (raw['planet'] ?? raw['name'] ?? raw['body'] ?? '')
              .toString()
              .toLowerCase();
          if (targets.contains(name)) {
            final sign = (raw['sign'] ?? raw['zodiac_sign'] ?? '')
                .toString()
                .trim();
            if (sign.isNotEmpty) {
              return sign;
            }
          }
        }
      }

      final signMap = scope['planet_signs'] ?? scope['signs'];
      if (signMap is Map) {
        for (final entry in signMap.entries) {
          final key = entry.key.toString().toLowerCase();
          if (targets.contains(key)) {
            final sign = entry.value.toString().trim();
            if (sign.isNotEmpty) {
              return sign;
            }
          }
        }
      }

      final formatted = scope['formatted_positions'];
      if (formatted is List) {
        final pattern = RegExp(
          '^$planetName\\s+in\\s+([A-Za-z]+)',
          caseSensitive: false,
        );
        for (final line in formatted) {
          final text = line.toString().trim();
          final match = pattern.firstMatch(text);
          if (match != null) {
            return match.group(1) ?? '—';
          }
        }
      }
    }
    return '—';
  }

  String _extractRisingSign(Map<String, dynamic> map) {
    final fromPlanet = _extractPlanetSign(map, 'Ascendant');
    if (fromPlanet != '—') {
      return fromPlanet;
    }

    for (final scope in _natalScopes(map)) {
      final angles = scope['angles'];
      if (angles is Map) {
        final sign = (angles['ascendant_sign'] ?? angles['asc_sign'] ?? '')
            .toString()
            .trim();
        if (sign.isNotEmpty) {
          return sign;
        }
      }

      final metaInfo = scope['meta_info'];
      if (metaInfo is Map) {
        final sign = (metaInfo['ascendant_sign'] ?? metaInfo['asc_sign'] ?? '')
            .toString()
            .trim();
        if (sign.isNotEmpty) {
          return sign;
        }
      }

      final houses = scope['formatted_houses'];
      if (houses is List) {
        final pattern = RegExp(
          r'^1st House in ([A-Za-z]+)',
          caseSensitive: false,
        );
        for (final line in houses) {
          final text = line.toString().trim();
          final match = pattern.firstMatch(text);
          if (match != null) {
            return match.group(1) ?? '—';
          }
        }
      }
    }
    return '—';
  }

  List<Map<String, dynamic>> _natalScopes(Map<String, dynamic> map) {
    final scopes = <Map<String, dynamic>>[map];
    final public = _asMap(map['public']);
    if (public.isNotEmpty) {
      scopes.add(public);
    }
    final metaInfo = _asMap(map['meta_info']);
    if (metaInfo.isNotEmpty) {
      scopes.add(metaInfo);
    }
    return scopes;
  }

  List<_SupportingThreadItem> _extractSupportingThreads(
    Map<String, dynamic> map,
  ) {
    for (final scope in _natalScopes(map)) {
      final raw = scope['sections_v2'];
      if (raw is! List) {
        continue;
      }
      final parsed = raw
          .whereType<Map>()
          .map(
            (item) => _SupportingThreadItem.fromMap(<String, dynamic>{
              'id': item['id'] ?? item['legacy_id'],
              'title': item['title'],
              'one_liner': item['subtitle'],
              'paragraph': item['body'],
              'chips': item['chips'],
            }),
          )
          .where((item) => item.title.isNotEmpty && item.oneLiner.isNotEmpty)
          .toList();
      if (parsed.isNotEmpty) {
        return parsed;
      }
    }
    for (final scope in _natalScopes(map)) {
      final raw = scope['supporting_threads'];
      if (raw is! List) {
        continue;
      }
      final parsed = raw
          .whereType<Map>()
          .map(
            (item) =>
                _SupportingThreadItem.fromMap(Map<String, dynamic>.from(item)),
          )
          .where((item) => item.title.isNotEmpty && item.oneLiner.isNotEmpty)
          .toList();
      if (parsed.isNotEmpty) {
        return parsed;
      }
    }
    return const [];
  }

  Map<String, dynamic> _extractPublicField(
    Map<String, dynamic> map,
    String field,
  ) {
    for (final scope in _natalScopes(map)) {
      final raw = _asMap(scope[field]);
      if (raw.isNotEmpty) {
        return raw;
      }
    }
    return <String, dynamic>{};
  }

  _ProfileIdentityContext _buildIdentityContext({
    required Map<String, dynamic> map,
    required Map<String, dynamic> fastMap,
    required List<_ProfileNarrativeCard> profileBlocks,
    required List<_ProfileNarrativeCard> coreBlocks,
    required List<_ProfileNarrativeCard> extraBlocks,
  }) {
    final leadIdentityCard = _pickLeadIdentityCard([
      ...coreBlocks,
      ...extraBlocks,
      if (coreBlocks.isEmpty && extraBlocks.isEmpty) ...profileBlocks,
    ]);
    final personalityImprint = _extractPublicField(map, 'personality_imprint');
    final auraLead = _extractAuraLead(personalityImprint);
    final natalGraphCompact = _extractPublicField(map, 'natal_graph_compact');
    final fastSnapshot = _extractProfileFastSnapshot(fastMap);
    final rulerInfo = fastSnapshot == null
        ? _extractAscRulerInfo(natalGraphCompact)
        : _ProfileAscRulerInfo(
            planet: fastSnapshot.chartRuler,
            house: fastSnapshot.chartRulerHouse,
          );
    final headline = _extractNatalHeadline(map);
    final drivers = _extractCoreStoryDrivers(map);
    final overview = _extractNatalSummary(map);
    final detailBody = leadIdentityCard?.body.isNotEmpty == true
        ? leadIdentityCard!.body
        : overview;
    final imprintHeadline = _extractPersonalityImprintHeadline(map);
    return _ProfileIdentityContext(
      headline: headline,
      overview: overview,
      detailBody: detailBody,
      drivers: drivers,
      imprintHeadline: imprintHeadline,
      auraLine: auraLead?.aura ?? '',
      auraSourceLabel: auraLead?.label ?? '',
      rulerName: rulerInfo == null ? '' : _planetLabelTr(rulerInfo.planet),
      rulerHouse: rulerInfo?.house,
    );
  }

  List<_ProfileBundleTeaser> _extractBundleTeasers(Map<String, dynamic> map) {
    final public = _extractPublicField(map, 'narrative_v2');
    final selector = _asMap(public['aspect_bundle_selector']);
    final selected = selector['selected_bundles'];
    if (selected is! List) {
      return const <_ProfileBundleTeaser>[];
    }
    return selected
        .whereType<Map>()
        .map(
          (item) => _ProfileBundleTeaser.fromBundleMap(
            Map<String, dynamic>.from(item),
          ),
        )
        .where((item) => item.title.isNotEmpty && item.summary.isNotEmpty)
        .take(6)
        .toList();
  }

  _ProfileFastSnapshot? _extractProfileFastSnapshot(Map<String, dynamic> map) {
    final raw = _asMap(map['profile_fast']);
    if (raw.isEmpty) {
      return null;
    }
    return _ProfileFastSnapshot(
      sunSign: (raw['sun_sign'] ?? '').toString().trim(),
      moonSign: (raw['moon_sign'] ?? '').toString().trim(),
      risingSign: (raw['rising_sign'] ?? '').toString().trim(),
      chartRuler: (raw['chart_ruler'] ?? '').toString().trim(),
      chartRulerHouse: _asInt(raw['chart_ruler_house']),
    );
  }

  _ProfileNarrativeCard? _pickLeadIdentityCard(
    List<_ProfileNarrativeCard> cards,
  ) {
    const preferredFamilies = <String>{
      'self_definition',
      'outer_inner_split',
      'identity',
    };
    for (final card in cards) {
      if (card.id == 'identity_aura') {
        return card;
      }
    }
    for (final card in cards) {
      if (preferredFamilies.contains(card.family)) {
        return card;
      }
    }
    for (final card in cards) {
      final lowerTitle = card.title.toLowerCase();
      if (lowerTitle.contains('disaridan') || lowerTitle.contains('icerden')) {
        return card;
      }
    }
    return cards.isEmpty ? null : cards.first;
  }

  _ProfileAuraLead? _extractAuraLead(Map<String, dynamic> personalityImprint) {
    for (final field in const <String>[
      'entries',
      'support_entries',
      'extra_entries',
    ]) {
      final raw = personalityImprint[field];
      if (raw is! List) {
        continue;
      }
      for (final item in raw.whereType<Map>()) {
        final mapItem = Map<String, dynamic>.from(item);
        final aura = (mapItem['aura'] ?? '').toString().trim();
        final label = (mapItem['label_tr'] ?? '').toString().trim();
        if (aura.isNotEmpty || label.isNotEmpty) {
          return _ProfileAuraLead(label: label, aura: aura);
        }
      }
    }
    return null;
  }

  _ProfileAscRulerInfo? _extractAscRulerInfo(Map<String, dynamic> graph) {
    final houseRulers = _asMap(graph['house_rulers']);
    final houseOne = _asMap(houseRulers['1']);
    final ruler = (houseOne['primary_ruler'] ?? '').toString().trim();
    if (ruler.isEmpty) {
      return null;
    }
    final house = _asInt(houseOne['primary_house']);
    return _ProfileAscRulerInfo(planet: ruler, house: house);
  }

  int? _asInt(dynamic value) {
    if (value == null) {
      return null;
    }
    if (value is int) {
      return value;
    }
    return int.tryParse(value.toString());
  }

  String _planetLabelTr(String raw) {
    const labels = <String, String>{
      'sun': 'Gunes',
      'moon': 'Ay',
      'mercury': 'Merkur',
      'venus': 'Venus',
      'mars': 'Mars',
      'jupiter': 'Jupiter',
      'saturn': 'Saturn',
      'uranus': 'Uranus',
      'neptune': 'Neptun',
      'pluto': 'Pluton',
    };
    final key = raw.trim().toLowerCase();
    return labels[key] ?? (raw.trim().isEmpty ? '—' : raw.trim());
  }

  String _toTrSign(String raw) {
    const signs = <String, String>{
      'aries': 'Koc',
      'taurus': 'Boga',
      'gemini': 'Ikizler',
      'cancer': 'Yengec',
      'leo': 'Aslan',
      'virgo': 'Basak',
      'libra': 'Terazi',
      'scorpio': 'Akrep',
      'sagittarius': 'Yay',
      'capricorn': 'Oglak',
      'aquarius': 'Kova',
      'pisces': 'Balik',
      'koç': 'Koc',
      'koc': 'Koc',
      'boğa': 'Boga',
      'boga': 'Boga',
      'yengeç': 'Yengec',
      'yengec': 'Yengec',
      'başak': 'Basak',
      'basak': 'Basak',
      'ikizler': 'Ikizler',
      'terazi': 'Terazi',
      'akrep': 'Akrep',
      'yay': 'Yay',
      'oğlak': 'Oglak',
      'oglak': 'Oglak',
      'kova': 'Kova',
      'balık': 'Balik',
      'balik': 'Balik',
    };
    final key = raw.trim().toLowerCase();
    return signs[key] ?? (raw.trim().isEmpty ? '—' : raw.trim());
  }

  String _normalizeBirthTime(String value) {
    final raw = value.trim();
    if (raw.isEmpty) {
      return '12:00';
    }
    final parts = raw.split(':');
    if (parts.length >= 2) {
      final hour = int.tryParse(parts[0]) ?? 12;
      final minute = int.tryParse(parts[1]) ?? 0;
      final hh = hour.clamp(0, 23).toString().padLeft(2, '0');
      final mm = minute.clamp(0, 59).toString().padLeft(2, '0');
      return '$hh:$mm';
    }
    return raw;
  }

  String _cardIdentity(_ProfileNarrativeCard card) {
    final cardKey = card.cardKey.trim();
    if (cardKey.isNotEmpty) {
      return cardKey;
    }
    final id = card.id.trim();
    if (id.isNotEmpty) {
      return id;
    }
    return card.title.trim();
  }

  String _normalizeSignatureDisplayTitle(String title) {
    return title
        .trim()
        .toLowerCase()
        .replaceAll('i̇', 'i')
        .replaceAll('ı', 'i')
        .replaceAll('ş', 's')
        .replaceAll('ğ', 'g')
        .replaceAll('ü', 'u')
        .replaceAll('ö', 'o')
        .replaceAll('ç', 'c')
        .replaceAll(RegExp(r'\s+'), ' ');
  }

  String _signatureCardIdentity(_ProfileNarrativeCard card) {
    final semanticTitle = _normalizeSignatureDisplayTitle(
      _displayTitleForCard(card),
    );
    if (semanticTitle.isNotEmpty) {
      return semanticTitle;
    }
    return _cardIdentity(card);
  }

  List<_ProfileNarrativeCard> _uniqueSignatureCards(
    Iterable<_ProfileNarrativeCard> items,
  ) {
    final seen = <String>{};
    final result = <_ProfileNarrativeCard>[];
    for (final item in items) {
      final key = _signatureCardIdentity(item);
      if (key.isEmpty || !seen.add(key)) {
        continue;
      }
      result.add(item);
    }
    return result;
  }

  List<_ProfileNarrativeCard> _uniqueNarrativeCards(
    Iterable<_ProfileNarrativeCard> items,
  ) {
    final seen = <String>{};
    final result = <_ProfileNarrativeCard>[];
    for (final item in items) {
      final key = _cardIdentity(item);
      if (key.isEmpty || !seen.add(key)) {
        continue;
      }
      result.add(item);
    }
    return result;
  }

  _ProfileNarrativeCard? _pickNarrativeCard({
    required Iterable<_ProfileNarrativeCard> source,
    Set<String> preferredFamilies = const <String>{},
    List<String> keywords = const <String>[],
    Set<String> excludedKeys = const <String>{},
  }) {
    final cards = _uniqueNarrativeCards(
      source,
    ).where((item) => !excludedKeys.contains(_cardIdentity(item))).toList();
    if (cards.isEmpty) {
      return null;
    }
    for (final item in cards) {
      if (preferredFamilies.contains(item.family)) {
        return item;
      }
    }
    if (keywords.isNotEmpty) {
      for (final item in cards) {
        final haystack = [
          item.title,
          item.summary,
          item.body,
          item.family,
          item.eyebrow,
        ].join(' ').toLowerCase();
        if (_containsAny(haystack, keywords)) {
          return item;
        }
      }
    }
    return cards.first;
  }

  bool _containsAny(String text, List<String> keywords) {
    final normalized = text.toLowerCase();
    for (final keyword in keywords) {
      if (normalized.contains(keyword.toLowerCase())) {
        return true;
      }
    }
    return false;
  }

  String _normalizePosterCopy(String value) {
    return value.replaceAll('\n', ' ').replaceAll(RegExp(r'\s+'), ' ').trim();
  }

  String _profilePosterLeadText({
    required _ProfileNarrativeCard? headlineCard,
    required String identityHeadline,
    required String identitySummary,
  }) {
    final options = <String>[
      if (headlineCard != null) headlineCard.summary,
      if (headlineCard != null) headlineCard.micro,
      identityHeadline,
      identitySummary,
      if (headlineCard != null) headlineCard.title,
      if (headlineCard != null) headlineCard.body,
    ];
    for (final option in options) {
      final normalized = _normalizePosterCopy(option);
      if (normalized.isNotEmpty) {
        return normalized;
      }
    }
    return '';
  }

  String _profilePosterEditorialTitle({
    required String identityHeadline,
    required _ProfileNarrativeCard? heroNarrativeCard,
    required String mainHeadlineText,
  }) {
    final normalizedHeadline = _normalizePosterCopy(mainHeadlineText);
    final options = <String>[
      identityHeadline,
      heroNarrativeCard?.title ?? '',
      heroNarrativeCard?.eyebrow ?? '',
    ];
    for (final option in options) {
      final normalized = _normalizePosterCopy(option);
      if (normalized.isEmpty) {
        continue;
      }
      if (normalized.toLowerCase() == normalizedHeadline.toLowerCase()) {
        continue;
      }
      return normalized;
    }
    return '';
  }

  String _profilePosterEditorialBody({
    required String identitySummary,
    required _ProfileNarrativeCard? headlineCard,
    required String mainHeadlineText,
  }) {
    final normalizedHeadline = _normalizePosterCopy(mainHeadlineText);
    final options = <String>[
      identitySummary,
      headlineCard?.summary ?? '',
      headlineCard?.previewBody ?? '',
      headlineCard?.body ?? '',
    ];
    for (final option in options) {
      final normalized = _normalizePosterCopy(option);
      if (normalized.isEmpty) {
        continue;
      }
      if (normalized.toLowerCase() == normalizedHeadline.toLowerCase()) {
        continue;
      }
      return normalized;
    }
    return '';
  }

  String _profilePosterLeadNarrative({
    required String displayName,
    required String mainHeadlineText,
    required String editorialStatementBody,
    required _ProfileNarrativeCard? headlineCard,
    required _ProfileNarrativeCard? heroNarrativeCard,
  }) {
    final leadCardIsDistinct =
        heroNarrativeCard != null &&
        (headlineCard == null ||
            _cardIdentity(heroNarrativeCard) != _cardIdentity(headlineCard));
    final segments = <String>[
      if (displayName.trim().isNotEmpty) '${displayName.trim()} sen..',
      mainHeadlineText,
      if (leadCardIsDistinct) heroNarrativeCard.previewBody,
      editorialStatementBody,
      if (headlineCard != null) headlineCard.previewBody,
      if (heroNarrativeCard != null) heroNarrativeCard.body,
    ];
    final unique = <String>[];
    for (final segment in segments) {
      final normalized = _normalizePosterCopy(segment);
      if (normalized.isEmpty) {
        continue;
      }
      final lower = normalized.toLowerCase();
      final duplicate = unique.any((existing) {
        final existingLower = existing.toLowerCase();
        return existingLower == lower ||
            existingLower.contains(lower) ||
            lower.contains(existingLower);
      });
      if (duplicate) {
        continue;
      }
      unique.add(normalized);
    }
    return unique.join(' ');
  }

  List<String> _profilePosterLeadChips({
    required _ProfileNarrativeCard? headlineCard,
    required _ProfileNarrativeCard? heroNarrativeCard,
    required List<String> drivers,
  }) {
    final chips = <String>[];

    void addAll(Iterable<String> values) {
      for (final value in values) {
        final clean = _sanitizeUserFacingChip(value);
        if (clean.isEmpty) {
          continue;
        }
        final duplicate = chips.any(
          (existing) => existing.toLowerCase() == clean.toLowerCase(),
        );
        if (duplicate) {
          continue;
        }
        chips.add(clean);
        if (chips.length >= 4) {
          return;
        }
      }
    }

    if (headlineCard != null) {
      addAll(headlineCard.chips);
    }
    if (heroNarrativeCard != null) {
      addAll(heroNarrativeCard.chips);
    }
    addAll(drivers);
    return chips;
  }

  _ProfileInsightModule? _pickLeadInsightModule() {
    for (final item in _profileInsightModules) {
      if (item.headline.isNotEmpty &&
          item.title.isNotEmpty &&
          item.body.isNotEmpty) {
        return item;
      }
    }
    return null;
  }

  String _profileLocation(Map<String, dynamic>? profile) {
    final city = (profile?['city'] ?? '').toString().trim();
    final country = (profile?['country'] ?? '').toString().trim();
    final parts = <String>[
      if (city.isNotEmpty) city,
      if (country.isNotEmpty && country != city) country,
    ];
    return parts.isEmpty ? 'Doğum yeri bekleniyor' : parts.join(', ');
  }

  String _profileAgeLabel(Map<String, dynamic>? profile) {
    final raw = (profile?['birth_date'] ?? '').toString().trim();
    if (raw.isEmpty) {
      return '';
    }
    final birthDate = DateTime.tryParse(raw);
    if (birthDate == null) {
      return '';
    }
    final now = DateTime.now();
    var age = now.year - birthDate.year;
    final hadBirthday =
        now.month > birthDate.month ||
        (now.month == birthDate.month && now.day >= birthDate.day);
    if (!hadBirthday) {
      age -= 1;
    }
    if (age < 0 || age > 120) {
      return '';
    }
    return '$age yaş';
  }

  JoviaIllustrationAsset _illustrationForElement(AstroElement element) {
    return switch (element) {
      AstroElement.fire => JoviaIllustrationAsset.sunGrowth,
      AstroElement.water => JoviaIllustrationAsset.layers,
      AstroElement.air => JoviaIllustrationAsset.bird,
      AstroElement.earth => JoviaIllustrationAsset.flower,
    };
  }

  JoviaIllustrationAsset _illustrationForCard(_ProfileNarrativeCard? card) {
    if (card == null) {
      return JoviaIllustrationAsset.planet;
    }
    final haystack = [
      card.family,
      card.title,
      card.summary,
      card.body,
      card.eyebrow,
    ].join(' ').toLowerCase();
    if (_containsAny(haystack, const ['zihin', 'mind', 'cümle', 'cumle'])) {
      return JoviaIllustrationAsset.dots;
    }
    if (_containsAny(haystack, const [
      'yakınlık',
      'yakinlik',
      'ilişki',
      'iliski',
      'kalp',
      'sevgi',
    ])) {
      return JoviaIllustrationAsset.heart;
    }
    if (_containsAny(haystack, const [
      'görün',
      'gorun',
      'kariyer',
      'sahne',
      'başarı',
      'basari',
    ])) {
      return JoviaIllustrationAsset.sunGrowth;
    }
    if (_containsAny(haystack, const [
      'koru',
      'savun',
      'tetik',
      'gölge',
      'golge',
    ])) {
      return JoviaIllustrationAsset.blocks;
    }
    if (_containsAny(haystack, const [
      'akış',
      'akis',
      'şans',
      'sans',
      'yarat',
    ])) {
      return JoviaIllustrationAsset.bird;
    }
    return switch (card.family) {
      'mind_mechanics' => JoviaIllustrationAsset.dots,
      'intimacy_guard' => JoviaIllustrationAsset.heart,
      'creative_channel' => JoviaIllustrationAsset.bird,
      'outer_inner_split' => JoviaIllustrationAsset.layers,
      _ => JoviaIllustrationAsset.planet,
    };
  }

  List<String> _detailBlocksFromText(String text, {int maxBlocks = 4}) {
    final raw = text.trim();
    if (raw.isEmpty) {
      return const <String>[];
    }
    final paragraphBlocks = raw
        .split(RegExp(r'\n\s*\n'))
        .map((item) => item.replaceAll(RegExp(r'\s+'), ' ').trim())
        .where((item) => item.isNotEmpty)
        .toList();
    if (paragraphBlocks.length >= 2) {
      return paragraphBlocks.take(maxBlocks).toList();
    }
    final sentenceBlocks = raw
        .replaceAll('\n', ' ')
        .split(RegExp(r'(?<=[.!?])\s+'))
        .map((item) => item.trim())
        .where((item) => item.isNotEmpty)
        .take(maxBlocks)
        .toList();
    if (sentenceBlocks.isNotEmpty) {
      return sentenceBlocks;
    }
    return <String>[raw];
  }

  String _whyTextForNarrativeCard(_ProfileNarrativeCard card) {
    if (card.astroSources.isNotEmpty) {
      return [
        'Bu yorum en çok şu astrolojik göstergelere dayanıyor:',
        ...card.astroSources.take(3).map((item) => '• $item'),
      ].join('\n');
    }
    if (card.chips.isNotEmpty) {
      return 'Bu yorum en çok ${card.chips.take(3).join(', ')} temalarına dayanıyor.';
    }
    return switch (card.family) {
      'mind_mechanics' =>
        'Bu bölüm, düşünme biçiminin kararlarını nasıl etkilediğini anlatıyor.',
      'intimacy_guard' =>
        'Bu bölüm, yakınlıkta ne zaman açıldığını ve neye ihtiyaç duyduğunu anlatıyor.',
      'outer_inner_split' =>
        'Bu bölüm, dışarıdan görünen tarafınla iç dünyandaki hassas tarafı birlikte anlatıyor.',
      'creative_channel' =>
        'Bu bölüm, hayatın hangi alanlarında daha kolay akmaya başladığını anlatıyor.',
      'contradiction_core' =>
        'Bu bölüm, içinde aynı anda çalışan iki farklı eğilimi gösteriyor.',
      _ => 'Bu bölüm, sende sık tekrar eden bir temayı anlatıyor.',
    };
  }

  String _whyTextForThread(_SupportingThreadItem item) {
    if (item.chips.isNotEmpty) {
      return 'Bu yan tema ${item.chips.take(3).join(' • ')} eksenlerinden besleniyor.';
    }
    return 'Bu bölüm ana kimlik akışının yanında çalışan ikinci bir tema olarak öne çıkıyor.';
  }

  String _whyTextForInsight(_ProfileInsightModule module) {
    return 'Bu modül savunma refleksi, duygusal gerilim ve büyüme hattını daha açık okumak için ayrılıyor.';
  }

  String _whyTextForIdentity({
    required String displayName,
    required List<String> drivers,
    required _ProfileIdentityContext? identityContext,
  }) {
    final parts = <String>[
      if (drivers.isNotEmpty) drivers.take(3).join(' • '),
      if ((identityContext?.rulerName ?? '').trim().isNotEmpty)
        '${identityContext!.rulerName}${identityContext.rulerHouse == null ? '' : ' • ${identityContext.rulerHouse}. ev'}',
    ];
    if (parts.isNotEmpty) {
      return '$displayName için bu okuma ${parts.join(' / ')} izleri üzerinden kuruluyor.';
    }
    return '$displayName için bu bölüm kamusal ton ile iç motivasyonun birleştiği kimlik katmanı.';
  }

  ProfileDetailTone _detailToneForNarrativeCard(_ProfileNarrativeCard card) {
    return profileDetailToneForSignature(
      title: _displayTitleForCard(card),
      summary: card.summary,
      family: card.family,
      eyebrow: card.eyebrow,
    );
  }

  ProfileDetailTone _detailToneForThread(_SupportingThreadItem item) {
    return profileDetailToneForSignature(
      title: item.title,
      summary: item.oneLiner,
      family: 'supporting_thread',
    );
  }

  ProfileDetailTone _detailToneForInsight(_ProfileInsightModule module) {
    return profileDetailToneForSignature(
      title: module.title,
      summary: module.subheadline,
      family: 'insight_module',
      eyebrow: module.headline,
    );
  }

  ProfileDetailTone _detailToneForIdentity({
    required String headline,
    required String summary,
    required List<String> drivers,
  }) {
    return profileDetailToneForSignature(
      title: headline,
      summary: [summary, ...drivers].join(' '),
      family: 'identity_flow',
    );
  }

  ProfileDetailSceneVariant _detailVariantForCard(
    _ProfileNarrativeCard card, {
    bool isPrimary = false,
    bool isSignature = false,
    int index = 0,
  }) {
    final detailText = card.body.trim().isNotEmpty
        ? card.body
        : card.previewBody;
    final blocks = _detailBlocksFromText(detailText);
    final totalLength = [
      card.title,
      card.summary,
      detailText,
      card.micro,
      ...card.chips,
    ].join(' ').trim().length;
    final splitFamily = <String>{
      'outer_inner_split',
      'contradiction_core',
      'control_vs_flow',
      'protection_pattern',
    }.contains(card.family);
    final structuredFamily = <String>{
      'mind_mechanics',
      'placement_signature',
      'tone_signature',
      'desire_style',
    }.contains(card.family);
    final shortScene = totalLength <= 160 && blocks.length <= 1;

    if (isPrimary) {
      return splitFamily
          ? ProfileDetailSceneVariant.split
          : ProfileDetailSceneVariant.posterScene;
    }
    if (isSignature && shortScene) {
      return ProfileDetailSceneVariant.symbol;
    }
    if (splitFamily ||
        _containsAny(
          [card.family, card.title, card.summary, detailText].join(' '),
          const [
            'dışarı',
            'disari',
            'içeri',
            'iceri',
            'gölge',
            'golge',
            'yakın',
            'yakin',
          ],
        )) {
      return ProfileDetailSceneVariant.split;
    }
    if (card.origin == 'personality_imprint' ||
        card.origin == 'narrative_v2_bundle' ||
        structuredFamily ||
        blocks.length >= 3) {
      return ProfileDetailSceneVariant.structuredInsight;
    }
    if (shortScene) {
      return index.isEven
          ? ProfileDetailSceneVariant.glance
          : ProfileDetailSceneVariant.symbol;
    }
    return ProfileDetailSceneVariant.posterScene;
  }

  ProfileDetailSceneVariant _detailVariantForThread(
    _SupportingThreadItem item, {
    int index = 0,
  }) {
    final bodyText = item.paragraph.isNotEmpty ? item.paragraph : item.oneLiner;
    final blocks = _detailBlocksFromText(bodyText);
    final totalLength = [
      item.title,
      item.oneLiner,
      bodyText,
      ...item.chips,
    ].join(' ').trim().length;
    if (_containsAny([item.title, item.oneLiner].join(' '), const [
          'zihin',
          'iliş',
          'ilis',
          'yakın',
          'yakin',
        ]) &&
        blocks.length >= 2) {
      return ProfileDetailSceneVariant.structuredInsight;
    }
    if (totalLength <= 150 && blocks.length <= 1) {
      return index.isEven
          ? ProfileDetailSceneVariant.glance
          : ProfileDetailSceneVariant.symbol;
    }
    return ProfileDetailSceneVariant.posterScene;
  }

  ProfileDetailSceneVariant _detailVariantForInsight(
    _ProfileInsightModule module, {
    bool portalStyle = false,
  }) {
    final blocks = _detailBlocksFromText(module.body);
    final totalLength = [
      module.title,
      module.subheadline,
      module.body,
    ].join(' ').trim().length;
    if (portalStyle && totalLength <= 260) {
      return ProfileDetailSceneVariant.portal;
    }
    if (blocks.length >= 3 || totalLength > 320) {
      return ProfileDetailSceneVariant.structuredInsight;
    }
    return ProfileDetailSceneVariant.posterScene;
  }

  ProfileDetailSceneData _sceneFromNarrativeCard(
    _ProfileNarrativeCard card, {
    required ProfileDetailSceneVariant variant,
    String? eyebrowOverride,
    String? titleOverride,
  }) {
    final intro = card.summary.trim().isNotEmpty
        ? card.summary.trim()
        : card.previewBody;
    final detailText = card.body.trim().isNotEmpty
        ? card.body
        : card.previewBody;
    return ProfileDetailSceneData(
      id: _cardIdentity(card),
      eyebrow: (eyebrowOverride ?? card.eyebrow).trim().isNotEmpty
          ? (eyebrowOverride ?? card.eyebrow).trim()
          : 'Detay',
      title: (titleOverride ?? card.title).trim(),
      intro: intro,
      bodyBlocks: _detailBlocksFromText(detailText),
      chips: card.chips,
      whyText: _whyTextForNarrativeCard(card),
      illustrationAsset: _illustrationForCard(card),
      variant: variant,
    );
  }

  ProfileDetailSceneData _sceneFromThread(
    _SupportingThreadItem item, {
    required ProfileDetailSceneVariant variant,
  }) {
    return ProfileDetailSceneData(
      id: item.id.isNotEmpty ? item.id : item.title,
      eyebrow: 'Yan tema',
      title: item.title,
      intro: item.oneLiner,
      bodyBlocks: _detailBlocksFromText(
        item.paragraph.isNotEmpty ? item.paragraph : item.oneLiner,
      ),
      chips: item.chips,
      whyText: _whyTextForThread(item),
      illustrationAsset: JoviaIllustrationAsset.layers,
      variant: variant,
    );
  }

  ProfileDetailSceneData _sceneFromInsight(
    _ProfileInsightModule module, {
    required ProfileDetailSceneVariant variant,
  }) {
    return ProfileDetailSceneData(
      id: module.moduleId.isNotEmpty ? module.moduleId : module.title,
      eyebrow: module.headline.isNotEmpty ? module.headline : 'Gölge & büyüme',
      title: module.title,
      intro: module.subheadline,
      bodyBlocks: _detailBlocksFromText(module.body),
      chips: const <String>['savunma', 'büyüme'],
      whyText: _whyTextForInsight(module),
      illustrationAsset: JoviaIllustrationAsset.blocks,
      variant: variant,
    );
  }

  ProfileDetailSceneData _sceneFromIdentity({
    required String displayName,
    required String headline,
    required String summary,
    required List<String> drivers,
  }) {
    final bodyText = (_identityContext?.detailBody ?? '').trim().isNotEmpty
        ? _identityContext!.detailBody
        : summary;
    return ProfileDetailSceneData(
      id: 'identity_flow',
      eyebrow: 'Kimlik',
      title: headline.trim().isNotEmpty ? headline.trim() : displayName,
      intro: summary,
      bodyBlocks: _detailBlocksFromText(bodyText),
      chips: drivers.take(3).toList(),
      whyText: _whyTextForIdentity(
        displayName: displayName,
        drivers: drivers,
        identityContext: _identityContext,
      ),
      illustrationAsset: JoviaIllustrationAsset.layers,
      variant: ProfileDetailSceneVariant.posterScene,
    );
  }

  List<ProfileDetailSceneData> _withNextLabels(
    List<ProfileDetailSceneData> scenes,
  ) {
    return [
      for (var index = 0; index < scenes.length; index++)
        scenes[index].copyWith(
          nextTitle: index + 1 < scenes.length ? scenes[index + 1].title : '',
        ),
    ];
  }

  List<ProfileDetailSceneData> _dedupeScenes(
    List<ProfileDetailSceneData> scenes,
  ) {
    final seen = <String>{};
    final out = <ProfileDetailSceneData>[];
    for (final scene in scenes) {
      if (scene.title.trim().isEmpty) {
        continue;
      }
      final key = scene.id.trim().isNotEmpty ? scene.id.trim() : scene.title;
      if (!seen.add(key)) {
        continue;
      }
      out.add(scene);
    }
    return out;
  }

  void _pushDetailFlow({
    required String title,
    required String subtitle,
    required List<ProfileDetailSceneData> scenes,
    ProfileDetailTone tone = const ProfileDetailTone(
      background: Color(0xFF08070B),
      surface: Color(0xFF12101A),
      surfaceStrong: Color(0xFF1A1524),
      accent: Color(0xFFB58DFF),
      accentSoft: Color(0xFF9EF0E7),
      stroke: Color(0x3DB58DFF),
      glow: Color(0x33B58DFF),
      mutedText: Color(0xFFD3CBDD),
    ),
  }) {
    final curatedScenes = _withNextLabels(_dedupeScenes(scenes));
    if (curatedScenes.isEmpty) {
      return;
    }
    Navigator.of(context).push(
      MaterialPageRoute<void>(
        builder: (context) => ProfileDetailPage(
          flowTitle: title,
          flowSubtitle: subtitle,
          scenes: curatedScenes,
          tone: tone,
        ),
      ),
    );
  }

  void _openIdentityFlow({
    required String displayName,
    required String headline,
    required String summary,
    required List<String> drivers,
  }) {
    final scenes = <ProfileDetailSceneData>[
      _sceneFromIdentity(
        displayName: displayName,
        headline: headline,
        summary: summary,
        drivers: drivers,
      ),
    ];
    _pushDetailFlow(
      title: 'Kimlik okuması',
      subtitle: headline.trim().isNotEmpty
          ? headline.trim()
          : 'Kimliğinin dışarıdan ve içeriden nasıl okunduğunu burada daha uzun gör.',
      scenes: scenes,
      tone: _detailToneForIdentity(
        headline: headline.trim().isNotEmpty ? headline : displayName,
        summary: summary,
        drivers: drivers,
      ),
    );
  }

  void _openNarrativeFlow({required _ProfileNarrativeCard selectedCard}) {
    final scenes = <ProfileDetailSceneData>[
      _sceneFromNarrativeCard(
        selectedCard,
        variant: _detailVariantForCard(selectedCard, isPrimary: true),
      ),
    ];
    _pushDetailFlow(
      title: selectedCard.title,
      subtitle: selectedCard.summary.isNotEmpty
          ? selectedCard.summary
          : 'Bu bölümün sende nasıl çalıştığını burada daha açık okuyorsun.',
      scenes: scenes,
      tone: _detailToneForNarrativeCard(selectedCard),
    );
  }

  void _openSignatureFlow({
    required String title,
    required List<_ProfileNarrativeCard> cards,
    _ProfileNarrativeCard? selected,
  }) {
    final uniqueCards = _uniqueSignatureCards(cards);
    if (selected == null && uniqueCards.isEmpty) {
      return;
    }
    if (selected != null) {
      _openSignatureCardDetail(title: title, card: selected);
      return;
    }
    if (uniqueCards.length == 1) {
      _openSignatureCardDetail(title: title, card: uniqueCards.first);
      return;
    }
    final items = [
      for (final card in uniqueCards)
        ProfileDetailCatalogItem(
          id: _cardIdentity(card),
          eyebrow: _signatureEyebrowForCard(card),
          title: _legacySignalLineForCard(card),
          subtitle: card.summary.isNotEmpty ? card.summary : card.previewBody,
          illustrationAsset: _profilePosterIllustrationForCard(card),
          tone: _detailToneForNarrativeCard(card),
        ),
    ];
    Navigator.of(context).push(
      MaterialPageRoute<void>(
        builder: (context) => ProfileDetailCatalogPage(
          title: title,
          subtitle:
              'Kart listesinde yalnızca başlıkları görürsün; bir karta basınca sadece onun detayı açılır.',
          items: items,
          onOpenItem: (item) {
            final card = uniqueCards.firstWhere(
              (candidate) => _cardIdentity(candidate) == item.id,
            );
            _openSignatureCardDetail(title: title, card: card);
          },
        ),
      ),
    );
  }

  void _openSignatureCardDetail({
    required String title,
    required _ProfileNarrativeCard card,
  }) {
    final scenes = <ProfileDetailSceneData>[
      _sceneFromNarrativeCard(
        card,
        variant: _detailVariantForCard(card, isSignature: true),
        eyebrowOverride: _signatureEyebrowForCard(card),
        titleOverride: _legacySignalLineForCard(card),
      ),
    ];
    _pushDetailFlow(
      title: title,
      subtitle: card.summary.isNotEmpty
          ? card.summary
          : 'Bu kişilik imzası kartının tam açıklaması burada açılıyor.',
      scenes: scenes,
      tone: _detailToneForNarrativeCard(card),
    );
  }

  void _openSideThemesFlow({
    required List<_SupportingThreadItem> items,
    _SupportingThreadItem? selected,
  }) {
    if (selected == null && items.isEmpty) {
      return;
    }
    final activeItem = selected ?? items.first;
    final scenes = <ProfileDetailSceneData>[
      _sceneFromThread(
        activeItem,
        variant: _detailVariantForThread(activeItem, index: 0),
      ),
    ];
    _pushDetailFlow(
      title: activeItem.title,
      subtitle: 'Burada ana portreni tamamlayan diğer taraflar öne çıkıyor.',
      scenes: scenes,
      tone: _detailToneForThread(activeItem),
    );
  }

  void _openInsightFlow({required _ProfileInsightModule module}) {
    final scenes = <ProfileDetailSceneData>[
      _sceneFromInsight(module, variant: _detailVariantForInsight(module)),
    ];
    _pushDetailFlow(
      title: module.title,
      subtitle: module.subheadline.isNotEmpty
          ? module.subheadline
          : 'Bu bölüm savunma ve büyüme eksenindeki tam akışı açıyor.',
      scenes: scenes,
      tone: _detailToneForInsight(module),
    );
  }

  Future<void> _showEditorialSheet({
    required String label,
    required String title,
    required String body,
    String? micro,
    List<String> chips = const <String>[],
  }) async {
    final resolvedBody = body.trim().isNotEmpty
        ? body.trim()
        : (micro ?? '').trim();
    if (resolvedBody.isEmpty) {
      return;
    }
    final profile = context.profileTheme;
    await showModalBottomSheet<void>(
      context: context,
      backgroundColor: Colors.transparent,
      isScrollControlled: true,
      builder: (sheetContext) {
        return Padding(
          padding: EdgeInsets.fromLTRB(
            profile.spacing.lg,
            profile.spacing.lg,
            profile.spacing.lg,
            MediaQuery.of(sheetContext).viewInsets.bottom + profile.spacing.lg,
          ),
          child: JoviaSurfaceCard(
            backgroundColor: _kProfilePosterSurface,
            borderColor: _kProfilePosterStroke,
            radius: 28,
            child: SingleChildScrollView(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    label.toUpperCase(),
                    style: profile.typography.eyebrow.copyWith(
                      color: _kProfilePosterAccent,
                      letterSpacing: 1.5,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    title,
                    style: profile.typography.card.copyWith(
                      color: Colors.white,
                      fontSize: 26,
                      height: 1.1,
                    ),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    resolvedBody,
                    style: profile.typography.body.copyWith(
                      color: Colors.white.withValues(alpha: 0.86),
                      height: 1.65,
                    ),
                  ),
                  if ((micro ?? '').trim().isNotEmpty) ...[
                    const SizedBox(height: 16),
                    Text(
                      micro!,
                      style: profile.typography.micro.copyWith(
                        color: _kProfilePosterMuted,
                      ),
                    ),
                  ],
                  if (chips.isNotEmpty) ...[
                    const SizedBox(height: 18),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: chips
                          .map((chip) => _ProfilePosterChip(label: chip))
                          .toList(),
                    ),
                  ],
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  String _readName() => _nameController.text.trim();
  String _readBirthDate() => _birthDateController.text.trim();
  String _readBirthTime() => _birthTimeController.text.trim();
  String _readCity() => _cityController.text.trim();
  String _readCountry() => _countryController.text.trim();
}

class _SupportingThreadItem {
  final String id;
  final String title;
  final String oneLiner;
  final String paragraph;
  final List<String> chips;

  const _SupportingThreadItem({
    required this.id,
    required this.title,
    required this.oneLiner,
    required this.paragraph,
    required this.chips,
  });

  factory _SupportingThreadItem.fromMap(Map<String, dynamic> map) {
    String s(String key) => (map[key] ?? '').toString().trim();
    List<String> readList(String key) {
      return _sanitizeUserFacingChips(map[key], max: 3);
    }

    return _SupportingThreadItem(
      id: s('id'),
      title: s('title'),
      oneLiner: s('one_liner'),
      paragraph: s('paragraph'),
      chips: readList('chips'),
    );
  }
}

class _ProfileIdentityContext {
  const _ProfileIdentityContext({
    required this.headline,
    required this.overview,
    required this.detailBody,
    required this.drivers,
    required this.imprintHeadline,
    required this.auraLine,
    required this.auraSourceLabel,
    required this.rulerName,
    required this.rulerHouse,
  });

  final String headline;
  final String overview;
  final String detailBody;
  final List<String> drivers;
  final String imprintHeadline;
  final String auraLine;
  final String auraSourceLabel;
  final String rulerName;
  final int? rulerHouse;

  bool get hasContent =>
      headline.isNotEmpty ||
      overview.isNotEmpty ||
      auraLine.isNotEmpty ||
      rulerName.isNotEmpty;
}

class _ProfileAuraLead {
  const _ProfileAuraLead({required this.label, required this.aura});

  final String label;
  final String aura;
}

class _ProfileAscRulerInfo {
  const _ProfileAscRulerInfo({required this.planet, required this.house});

  final String planet;
  final int? house;
}

class _ProfileFastSnapshot {
  const _ProfileFastSnapshot({
    required this.sunSign,
    required this.moonSign,
    required this.risingSign,
    required this.chartRuler,
    required this.chartRulerHouse,
  });

  final String sunSign;
  final String moonSign;
  final String risingSign;
  final String chartRuler;
  final int? chartRulerHouse;
}

class _ProfileBundleTeaser {
  const _ProfileBundleTeaser({
    required this.id,
    required this.family,
    required this.title,
    required this.summary,
    required this.body,
    required this.chips,
    required this.astroSources,
  });

  final String id;
  final String family;
  final String title;
  final String summary;
  final String body;
  final List<String> chips;
  final List<String> astroSources;

  factory _ProfileBundleTeaser.fromBundleMap(Map<String, dynamic> map) {
    List<String> readList(String key) {
      return _sanitizeUserFacingChips(map[key], max: 12);
    }

    List<String> readAstroSources(String key) {
      final raw = map[key];
      if (raw is! List) {
        return const <String>[];
      }
      return raw
          .map((item) => item.toString().trim())
          .where((item) => item.isNotEmpty)
          .take(3)
          .toList();
    }

    String editorialTitleForFamily(String family) {
      return switch (family) {
        'outer_inner_split' => 'Dışarıdan ve içeriden',
        'mind_mechanics' => 'Zihnin nasıl çalışıyor',
        'protection_pattern' => 'Kendini nasıl koruyorsun',
        'intimacy_guard' => 'Yakınlık sende nasıl açılıyor',
        'control_vs_flow' => 'Tutma ve bırakma dengesi',
        'creative_channel' => 'Fırsatın aktığı yer',
        'self_definition' => 'Sende kolay tanınan çizgi',
        'contradiction_core' => 'İçeride iki yönün nasıl çalışıyor',
        _ => 'Sende öne çıkan taraf',
      };
    }

    String joinEditorial(List<String> values, {int limit = 3}) {
      final cleaned = values
          .map((item) => item.trim())
          .where((item) => item.isNotEmpty)
          .take(limit)
          .toList();
      if (cleaned.isEmpty) {
        return '';
      }
      if (cleaned.length == 1) {
        return cleaned.first;
      }
      if (cleaned.length == 2) {
        return '${cleaned[0]} ve ${cleaned[1]}';
      }
      return '${cleaned.sublist(0, cleaned.length - 1).join(', ')} ve ${cleaned.last}';
    }

    String buildTeaser({
      required String family,
      required List<String> recognitionTags,
      required List<String> giftTags,
      required List<String> reflexTags,
    }) {
      final lead = joinEditorial(
        recognitionTags.isNotEmpty
            ? recognitionTags
            : (giftTags.isNotEmpty ? giftTags : reflexTags),
        limit: 2,
      );
      if (lead.isEmpty) {
        return editorialTitleForFamily(family);
      }
      return switch (family) {
        'mind_mechanics' =>
          'Zihninde ilk öne çıkan şey çoğu zaman $lead oluyor.',
        'intimacy_guard' => 'Yakınlıkta önce $lead tarafın devreye giriyor.',
        'creative_channel' => 'Akışın en çok $lead olduğunda güçleniyor.',
        'outer_inner_split' => 'İnsanlar sende önce $lead tarafını hissediyor.',
        'control_vs_flow' => 'İçinde aynı anda $lead çalışan bir denge var.',
        'protection_pattern' =>
          'Zorlandığında ilk devreye $lead tarafın giriyor.',
        'contradiction_core' => 'İçinde aynı anda $lead isteyen iki yön var.',
        'self_definition' =>
          'İnsanların sende ilk fark ettiği şey çoğu zaman $lead oluyor.',
        _ => 'Sende en çok $lead tarafı öne çıkıyor.',
      };
    }

    String buildBody({
      required String family,
      required List<String> recognitionTags,
      required List<String> giftTags,
      required List<String> reflexTags,
      required List<String> domains,
    }) {
      final domainText = joinEditorial(domains, limit: 2);
      final recognitionText = joinEditorial(recognitionTags);
      final giftText = joinEditorial(giftTags, limit: 2);
      final reflexText = joinEditorial(reflexTags, limit: 2);
      final sentences = <String>[
        if (domainText.isNotEmpty)
          switch (family) {
            'mind_mechanics' =>
              'Bu tema en çok $domainText alanında kendini gösteriyor.',
            'intimacy_guard' =>
              'Bu tema en çok $domainText alanında hissediliyor.',
            'creative_channel' =>
              'Bu akış en çok $domainText alanında açılıyor.',
            _ => 'Bu tema en çok $domainText alanında kendini gösteriyor.',
          },
        if (recognitionText.isNotEmpty)
          'İnsanların sende ilk fark ettiği şey çoğu zaman $recognitionText oluyor.',
        if (giftText.isNotEmpty)
          'Dengede olduğunda sende en çok $giftText öne çıkıyor.',
        if (reflexText.isNotEmpty)
          'Zorlandığında ise $reflexText tarafın öne çıkabiliyor.',
      ];
      return sentences.join(' ').trim();
    }

    final bundleType = (map['bundle_type'] ?? '').toString().trim();
    final recognitionTags = readList('recognition_tags');
    final giftTags = readList('gift_tags');
    final reflexTags = readList('reflex_tags');
    final domains = readList('domains');
    final family = switch (bundleType) {
      'contradiction_bundle' => 'contradiction_core',
      'emotional_regulation_bundle' => 'protection_pattern',
      'mental_style_bundle' => 'mind_mechanics',
      'relational_pattern_bundle' => 'intimacy_guard',
      'angle_identity_bundle' => 'outer_inner_split',
      'pressure_growth_bundle' => 'control_vs_flow',
      'soft_capacity_bundle' => 'creative_channel',
      'personal_core_bundle' => 'self_definition',
      _ => 'inner_layer',
    };
    final title = editorialTitleForFamily(family);
    final summary = buildTeaser(
      family: family,
      recognitionTags: recognitionTags,
      giftTags: giftTags,
      reflexTags: reflexTags,
    );
    final body = buildBody(
      family: family,
      recognitionTags: recognitionTags,
      giftTags: giftTags,
      reflexTags: reflexTags,
      domains: domains,
    );
    return _ProfileBundleTeaser(
      id: (map['bundle_id'] ?? bundleType).toString().trim(),
      family: family,
      title: title,
      summary: summary.trim().isEmpty ? title : summary.trim(),
      body: body,
      chips: (domains.isNotEmpty ? domains : giftTags).take(3).toList(),
      astroSources: readAstroSources('astro_sources'),
    );
  }

  _ProfileNarrativeCard toNarrativeCard() {
    return _ProfileNarrativeCard(
      cardKey: '${id}_detail',
      id: id,
      family: family,
      origin: 'narrative_v2_bundle',
      eyebrow: 'Öne çıkan tema',
      title: title,
      summary: summary,
      body: body,
      micro: '',
      chips: chips,
      astroSources: astroSources,
    );
  }
}

class _ProfileNarrativeCard {
  const _ProfileNarrativeCard({
    required this.cardKey,
    required this.id,
    required this.family,
    required this.origin,
    required this.eyebrow,
    required this.title,
    required this.summary,
    required this.body,
    required this.micro,
    required this.chips,
    required this.astroSources,
  });

  final String cardKey;
  final String id;
  final String family;
  final String origin;
  final String eyebrow;
  final String title;
  final String summary;
  final String body;
  final String micro;
  final List<String> chips;
  final List<String> astroSources;

  String get previewBody {
    final summaryText = summary.trim();
    if (summaryText.isNotEmpty) {
      return summaryText;
    }
    final microText = micro.trim();
    if (microText.isNotEmpty) {
      return microText;
    }
    return body.trim();
  }

  bool get isPlacementLike =>
      origin == 'personality_imprint' ||
      family == 'placement_signature' ||
      family == 'tone_signature';

  factory _ProfileNarrativeCard.fromMap(Map<String, dynamic> map) {
    List<String> normalizeChips(dynamic raw) {
      return _sanitizeUserFacingChips(raw, max: 4);
    }

    List<String> normalizeAstroSources(dynamic raw) {
      if (raw is! List) {
        return const <String>[];
      }
      final sources = <String>[];
      for (final item in raw) {
        final value = item.toString().trim();
        if (value.isEmpty) {
          continue;
        }
        final duplicate = sources.any(
          (existing) => existing.toLowerCase() == value.toLowerCase(),
        );
        if (duplicate) {
          continue;
        }
        sources.add(value);
        if (sources.length >= 3) {
          break;
        }
      }
      return sources;
    }

    String pickTitle() {
      final title = (map['title'] ?? '').toString().trim();
      if (title.isNotEmpty) {
        return title;
      }
      return (map['headline'] ?? '').toString().trim();
    }

    String pickSummary() {
      final teaser = (map['teaser'] ?? '').toString().trim();
      if (teaser.isNotEmpty) {
        return teaser;
      }
      return (map['summary'] ?? '').toString().trim();
    }

    String pickEyebrow() {
      final eyebrow = (map['eyebrow'] ?? '').toString().trim();
      final lowerEyebrow = eyebrow.toLowerCase();
      if (lowerEyebrow == 'kişilik izi' ||
          lowerEyebrow == 'kisilik izi' ||
          lowerEyebrow == 'ton izi' ||
          lowerEyebrow == 'aci izi') {
        return 'Öne çıkan tema';
      }
      if (eyebrow.isNotEmpty) {
        return eyebrow;
      }
      final family = (map['family'] ?? '').toString().trim();
      return switch (family) {
        'placement_signature' => 'Öne çıkan tema',
        'tone_signature' => 'Öne çıkan tema',
        'self_definition' => 'Sende kolay tanınan çizgi',
        'outer_inner_split' => 'Dışarıdan ve içeriden',
        'mind_mechanics' => 'Zihnin nasıl çalışıyor',
        'intimacy_guard' => 'Yakınlık sende nasıl açılıyor',
        'creative_channel' => 'Fırsatın aktığı yer',
        'contradiction_core' => 'İçeride iki yön',
        'control_vs_flow' => 'Tutma ve bırakma dengesi',
        _ => '',
      };
    }

    return _ProfileNarrativeCard(
      cardKey: (map['card_key'] ?? '').toString().trim(),
      id: (map['id'] ?? '').toString().trim(),
      family: (map['family'] ?? '').toString().trim(),
      origin: (map['origin'] ?? '').toString().trim(),
      eyebrow: pickEyebrow(),
      title: pickTitle(),
      summary: pickSummary(),
      body: (map['body'] ?? '').toString().trim(),
      micro: (map['micro'] ?? '').toString().trim(),
      chips: normalizeChips(map['chips']),
      astroSources: normalizeAstroSources(map['astro_sources']),
    );
  }
}

class _ProfileInsightModule {
  const _ProfileInsightModule({
    required this.moduleId,
    required this.headline,
    required this.subheadline,
    required this.title,
    required this.body,
  });

  final String moduleId;
  final String headline;
  final String subheadline;
  final String title;
  final String body;

  factory _ProfileInsightModule.fromMap(Map<String, dynamic> map) {
    final content = map['content'] is Map<String, dynamic>
        ? map['content'] as Map<String, dynamic>
        : (map['content'] is Map
              ? Map<String, dynamic>.from(map['content'] as Map)
              : <String, dynamic>{});
    return _ProfileInsightModule(
      moduleId: (map['module_id'] ?? '').toString().trim(),
      headline: (map['headline'] ?? '').toString().trim(),
      subheadline: (map['subheadline'] ?? '').toString().trim(),
      title: (content['title'] ?? map['title'] ?? '').toString().trim(),
      body: (content['body'] ?? map['body'] ?? '').toString().trim(),
    );
  }
}

class _ProfilePosterTopBar extends StatelessWidget {
  const _ProfilePosterTopBar({
    required this.username,
    required this.readOnly,
    this.onLeadingTap,
    this.onActionTap,
  });

  final String username;
  final bool readOnly;
  final VoidCallback? onLeadingTap;
  final VoidCallback? onActionTap;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Row(
      children: [
        SizedBox(
          width: 72,
          child: readOnly
              ? Align(
                  alignment: Alignment.centerLeft,
                  child: _ProfilePosterIconButton(
                    onTap: onLeadingTap,
                    child: const JoviaUiIcon(
                      asset: JoviaUiAsset.back,
                      size: 18,
                      color: Colors.white,
                    ),
                  ),
                )
              : Text(
                  'PROFIL',
                  style: profile.typography.eyebrow.copyWith(
                    color: Colors.white,
                    fontSize: 13,
                    fontWeight: FontWeight.w700,
                    letterSpacing: 2.4,
                  ),
                ),
        ),
        Expanded(
          child: Text(
            username,
            textAlign: TextAlign.center,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: profile.typography.micro.copyWith(
              color: Colors.white.withValues(alpha: 0.92),
              fontSize: 13.5,
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
        SizedBox(
          width: 72,
          child: Align(
            alignment: Alignment.centerRight,
            child: onActionTap == null
                ? const SizedBox(width: 40, height: 40)
                : _ProfilePosterIconButton(
                    onTap: onActionTap,
                    child: const JoviaUiIcon(
                      asset: JoviaUiAsset.menuStack,
                      size: 18,
                      color: Colors.white,
                    ),
                  ),
          ),
        ),
      ],
    );
  }
}

class _ProfilePosterHeader extends StatelessWidget {
  const _ProfilePosterHeader({
    required this.displayName,
    required this.avatarUrl,
    required this.isAvatarUploading,
    required this.onAvatarEdit,
    required this.metaLabel,
    required this.followingCount,
    required this.followerCount,
    required this.peoplePreview,
    required this.sunSign,
    required this.moonSign,
    required this.risingSign,
    this.onConnectionsTap,
    this.onPrimaryTap,
  });

  final String displayName;
  final String? avatarUrl;
  final bool isAvatarUploading;
  final VoidCallback? onAvatarEdit;
  final String metaLabel;
  final int followingCount;
  final int followerCount;
  final List<PersonProfile> peoplePreview;
  final String sunSign;
  final String moonSign;
  final String risingSign;
  final VoidCallback? onConnectionsTap;
  final VoidCallback? onPrimaryTap;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final content = Container(
      constraints: const BoxConstraints(minHeight: 180),
      padding: const EdgeInsets.fromLTRB(20, 26, 20, 26),
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.centerLeft,
          end: Alignment.centerRight,
          colors: <Color>[
            Color(0xFF090807),
            Color(0xFF12100F),
            Color(0xFF161312),
          ],
        ),
      ),
      child: Stack(
        children: [
          Positioned(
            right: -34,
            top: -18,
            child: Container(
              width: 170,
              height: 170,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: RadialGradient(
                  colors: [
                    Colors.white.withValues(alpha: 0.08),
                    Colors.transparent,
                  ],
                ),
              ),
            ),
          ),
          const Positioned(
            right: 14,
            top: 14,
            child: JoviaIllustrationAccent(
              asset: JoviaIllustrationAsset.sunGrowth,
              width: 84,
              height: 84,
              opacity: 0.82,
            ),
          ),
          Row(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              _AvatarHalo(
                size: 74,
                imageUrl: avatarUrl,
                onEdit: onAvatarEdit,
                isUploading: isAvatarUploading,
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      displayName,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: profile.typography.heroName.copyWith(
                        color: const Color(0xFFF5F2EE),
                        fontWeight: FontWeight.w600,
                        height: 0.94,
                      ),
                    ),
                    const SizedBox(height: 7),
                    _ProfilePosterFollowStatsRow(
                      followingCount: followingCount,
                      followerCount: followerCount,
                      people: peoplePreview,
                      onOpenConnections: onConnectionsTap,
                    ),
                    const SizedBox(height: 11),
                    Wrap(
                      spacing: 12,
                      runSpacing: 8,
                      children: [
                        _ProfilePosterAstroItem(label: 'Güneş', value: sunSign),
                        _ProfilePosterAstroItem(
                          label: 'Yükselen',
                          value: risingSign,
                        ),
                        _ProfilePosterAstroItem(label: 'Ay', value: moonSign),
                      ],
                    ),
                    if (metaLabel.trim().isNotEmpty) ...[
                      const SizedBox(height: 10),
                      Text(
                        metaLabel,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: profile.typography.micro.copyWith(
                          color: Colors.white.withValues(alpha: 0.48),
                          fontSize: 12.8,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
    if (onPrimaryTap == null) {
      return content;
    }
    return Material(
      color: Colors.transparent,
      child: InkWell(onTap: onPrimaryTap, child: content),
    );
  }
}

class _ProfilePosterFollowStatsRow extends StatelessWidget {
  const _ProfilePosterFollowStatsRow({
    required this.followingCount,
    required this.followerCount,
    required this.people,
    this.onOpenConnections,
  });

  final int followingCount;
  final int followerCount;
  final List<PersonProfile> people;
  final VoidCallback? onOpenConnections;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;

    Widget stat(int count, String label) {
      final child = Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
        decoration: BoxDecoration(
          color: Colors.white.withValues(alpha: 0.05),
          borderRadius: BorderRadius.circular(999),
          border: Border.all(color: Colors.white.withValues(alpha: 0.08)),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              '$count',
              style: profile.typography.micro.copyWith(
                color: Colors.white,
                fontSize: 13.3,
                fontWeight: FontWeight.w800,
              ),
            ),
            const SizedBox(width: 5),
            Text(
              label,
              style: profile.typography.micro.copyWith(
                color: Colors.white.withValues(alpha: 0.82),
                fontSize: 12.2,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
      );
      if (onOpenConnections == null || people.isEmpty) {
        return child;
      }
      return Material(
        color: Colors.transparent,
        child: InkWell(
          borderRadius: BorderRadius.circular(999),
          onTap: onOpenConnections,
          child: child,
        ),
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Wrap(
          spacing: 10,
          runSpacing: 8,
          children: [
            stat(followingCount, 'Takip'),
            stat(followerCount, 'Takipçi'),
          ],
        ),
        if (people.isNotEmpty) ...[
          const SizedBox(height: 10),
          Material(
            color: Colors.transparent,
            child: InkWell(
              borderRadius: BorderRadius.circular(999),
              onTap: onOpenConnections,
              child: Padding(
                padding: const EdgeInsets.symmetric(vertical: 2),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    SizedBox(
                      width: 72,
                      height: 28,
                      child: Stack(
                        clipBehavior: Clip.none,
                        children: [
                          for (
                            var index = 0;
                            index < people.take(3).length;
                            index++
                          )
                            Positioned(
                              left: index * 20,
                              child: _ProfilePosterMiniAvatar(
                                name: people[index].name,
                                tint: _profilePosterFeatureColor(index + 1),
                                size: 28,
                                showIndicator: false,
                              ),
                            ),
                        ],
                      ),
                    ),
                    const SizedBox(width: 8),
                    Text(
                      people.length == 1
                          ? '${people.first.name} profiline git'
                          : '${people.length} arkadaş profiline bak',
                      style: profile.typography.micro.copyWith(
                        color: Colors.white.withValues(alpha: 0.72),
                        fontSize: 12.4,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ],
    );
  }
}

class _ProfilePosterMainHeadline extends StatelessWidget {
  const _ProfilePosterMainHeadline({required this.label, required this.title});

  final String label;
  final String title;

  String _multilineTitle() {
    final words = title
        .replaceAll('\n', ' ')
        .trim()
        .split(RegExp(r'\s+'))
        .where((item) => item.isNotEmpty)
        .toList();
    if (words.length <= 3) {
      return words.join(' ');
    }
    if (words.length <= 6) {
      final split = (words.length / 2).ceil();
      return '${words.take(split).join(' ')}\n${words.skip(split).join(' ')}';
    }
    return '${words.take(3).join(' ')}\n${words.skip(3).take(3).join(' ')}';
  }

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label.toUpperCase(),
            textAlign: TextAlign.left,
            style: profile.typography.monoEyebrow.copyWith(
              color: const Color(0xFFF5F2EE),
              fontSize: 21,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            _multilineTitle(),
            textAlign: TextAlign.left,
            style: profile.typography.bodyReading.copyWith(
              color: const Color(0xFFF5F2EE),
              fontSize: 17.2,
              fontWeight: FontWeight.w500,
              height: 1.5,
              letterSpacing: -0.02,
              wordSpacing: 0.8,
            ),
          ),
        ],
      ),
    );
  }
}

class _ProfilePosterSectionTag extends StatelessWidget {
  const _ProfilePosterSectionTag({required this.label});

  final String label;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      decoration: BoxDecoration(
        color: context.profileTheme.colors.buttonSecondary,
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: context.profileTheme.colors.hairline),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.18),
            blurRadius: 18,
            offset: const Offset(0, 10),
            spreadRadius: -14,
          ),
        ],
      ),
      child: Text(
        label,
        style: context.profileTheme.typography.buttonLabel.copyWith(
          color: Colors.white,
          fontWeight: FontWeight.w700,
          fontSize: 12.8,
          letterSpacing: 0.08,
        ),
      ),
    );
  }
}

class _ProfilePosterEditorialStatement extends StatelessWidget {
  const _ProfilePosterEditorialStatement({
    required this.title,
    required this.body,
  });

  final String title;
  final String body;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        if (title.trim().isNotEmpty)
          Text(
            title.toUpperCase(),
            textAlign: TextAlign.center,
            style: profile.typography.monoEyebrow.copyWith(
              color: const Color(0xFFF5F2EE),
              fontWeight: FontWeight.w700,
              fontSize: 15.6,
              letterSpacing: 0.9,
              height: 1.3,
            ),
          ),
        if (body.trim().isNotEmpty) ...[
          const SizedBox(height: 14),
          Text(
            body,
            maxLines: 4,
            textAlign: TextAlign.center,
            overflow: TextOverflow.ellipsis,
            style: profile.typography.bodyReading.copyWith(
              color: Colors.white.withValues(alpha: 0.88),
              fontSize: 15,
              height: 1.58,
            ),
          ),
        ],
      ],
    );
  }
}

class _ProfilePosterIdentitySummaryCard extends StatelessWidget {
  const _ProfilePosterIdentitySummaryCard({
    required this.headline,
    required this.summary,
    required this.drivers,
    required this.onTap,
  });

  final String headline;
  final String summary;
  final List<String> drivers;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Container(
      padding: const EdgeInsets.fromLTRB(18, 18, 18, 18),
      decoration: BoxDecoration(
        color: _kProfilePosterSurface,
        borderRadius: BorderRadius.circular(28),
        border: Border.all(color: _kProfilePosterStroke),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'KİMLİK',
            style: profile.typography.monoEyebrow.copyWith(
              color: profile.colors.warmAccent,
              fontSize: 11.5,
              letterSpacing: 1.8,
            ),
          ),
          const SizedBox(height: 10),
          Text(
            headline.trim().isNotEmpty ? headline.trim() : 'Kimlik okuması',
            style: profile.typography.section.copyWith(
              color: Colors.white,
              fontSize: 24,
              height: 1.12,
            ),
          ),
          if (summary.trim().isNotEmpty) ...[
            const SizedBox(height: 10),
            Text(
              summary.trim(),
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
              style: profile.typography.bodyReading.copyWith(
                color: Colors.white.withValues(alpha: 0.84),
                fontSize: 15.2,
                height: 1.55,
              ),
            ),
          ],
          if (drivers.isNotEmpty) ...[
            const SizedBox(height: 14),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: drivers
                  .take(3)
                  .map((driver) => _ProfilePosterChip(label: driver))
                  .toList(),
            ),
          ],
          const SizedBox(height: 16),
          _ProfilePosterFooterButton(
            label: 'Kimlik okumasını aç',
            onTap: onTap,
          ),
        ],
      ),
    );
  }
}

class _ProfilePosterQuickInfoRow extends StatelessWidget {
  const _ProfilePosterQuickInfoRow({
    required this.dominantElementLabel,
    required this.auraSourceLabel,
    required this.rulerName,
    required this.rulerHouse,
    required this.element,
    required this.risingSign,
  });

  final String dominantElementLabel;
  final String auraSourceLabel;
  final String rulerName;
  final int? rulerHouse;
  final AstroElement element;
  final String risingSign;

  @override
  Widget build(BuildContext context) {
    final fallbackElementTitle = dominantElementLabel
        .replaceAll('baskın', 'etkili')
        .replaceAll('Baskın', 'Etkili')
        .trim();
    final elementTitle = fallbackElementTitle.isNotEmpty
        ? fallbackElementTitle
        : 'Toprak etkili';
    final elementBody = '';
    final rulerTitle = rulerName.trim().isNotEmpty
        ? 'En güçlü yönetici $rulerName'
        : (auraSourceLabel.trim().isNotEmpty
              ? auraSourceLabel.trim()
              : (risingSign.trim().isNotEmpty && risingSign.trim() != '—'
                    ? '$risingSign yöneticisi'
                    : 'Harita omurgası'));
    final rulerBody = rulerHouse == null ? '' : '$rulerHouse. ev vurgusu';
    return ConstrainedBox(
      constraints: const BoxConstraints(maxWidth: 300),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Expanded(
            child: _MiniSignatureCard(
              title: elementTitle,
              body: elementBody,
              art: JoviaElementArt(
                asset: JoviaElementAssetResolver.fromElement(element),
                width: 84,
                height: 84,
              ),
            ),
          ),
          const SizedBox(width: 30),
          Expanded(
            child: _ProfilePosterStructuredSnapshotCard(
              title: rulerTitle,
              body: rulerBody,
              overline: 'Yönetici',
              art: const _ProfilePosterSaturnSeal(),
            ),
          ),
        ],
      ),
    );
  }
}

class _ProfilePosterSaturnSeal extends StatelessWidget {
  const _ProfilePosterSaturnSeal();

  @override
  Widget build(BuildContext context) {
    const base = Color(0xFFF5F2EE);
    Widget dot(double size) => Container(
      width: size,
      height: size,
      decoration: const BoxDecoration(color: base, shape: BoxShape.circle),
    );

    return SizedBox(
      width: 96,
      height: 96,
      child: Stack(
        clipBehavior: Clip.none,
        alignment: Alignment.center,
        children: [
          Container(
            width: 78,
            height: 78,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              border: Border.all(color: base, width: 2.2),
            ),
          ),
          Text(
            '♄',
            style: Theme.of(context).textTheme.headlineMedium?.copyWith(
              color: base,
              fontSize: 60,
              fontWeight: FontWeight.w400,
              height: 1,
            ),
          ),
          Positioned(top: 10, right: 16, child: dot(6)),
          Positioned(top: 20, right: 6, child: dot(4)),
          Positioned(bottom: 18, right: 10, child: dot(5)),
          Positioned(bottom: 9, right: 20, child: dot(4)),
        ],
      ),
    );
  }
}

class _MiniSignatureCard extends StatelessWidget {
  const _MiniSignatureCard({
    required this.title,
    required this.body,
    required this.art,
  });

  final String title;
  final String body;
  final Widget art;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 2, vertical: 2),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          SizedBox(width: 92, height: 92, child: Center(child: art)),
          const SizedBox(height: 8),
          Text(
            'AURA',
            style: profile.typography.monoEyebrow.copyWith(
              color: _kProfilePosterMuted,
              fontSize: 11.5,
              letterSpacing: 1.95,
            ),
          ),
          const SizedBox(height: 7),
          Text(
            title,
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
            textAlign: TextAlign.center,
            style: profile.typography.card.copyWith(
              color: Colors.white,
              fontSize: 15.6,
              fontWeight: FontWeight.w700,
              height: 1.25,
            ),
          ),
          if (body.trim().isNotEmpty) ...[
            const SizedBox(height: 8),
            Text(
              body,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
              textAlign: TextAlign.center,
              style: profile.typography.micro.copyWith(
                color: _kProfilePosterMuted,
                fontSize: 12.5,
                height: 1.45,
              ),
            ),
          ],
        ],
      ),
    );
  }
}

class _ProfilePosterStructuredSnapshotCard extends StatelessWidget {
  const _ProfilePosterStructuredSnapshotCard({
    required this.title,
    required this.body,
    required this.overline,
    required this.art,
  });

  final String title;
  final String body;
  final String overline;
  final Widget art;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 2, vertical: 2),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          art,
          const SizedBox(height: 8),
          Text(
            overline.toUpperCase(),
            style: profile.typography.monoEyebrow.copyWith(
              color: _kProfilePosterMuted,
              fontSize: 11.5,
              letterSpacing: 1.95,
            ),
          ),
          const SizedBox(height: 7),
          Text(
            title,
            maxLines: 3,
            overflow: TextOverflow.ellipsis,
            textAlign: TextAlign.center,
            style: profile.typography.body.copyWith(
              color: Colors.white,
              fontSize: 14.9,
              fontWeight: FontWeight.w700,
              height: 1.42,
            ),
          ),
          if (body.trim().isNotEmpty) ...[
            const SizedBox(height: 8),
            Text(
              body,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
              textAlign: TextAlign.center,
              style: profile.typography.micro.copyWith(
                color: _kProfilePosterMuted,
                fontSize: 12.5,
                height: 1.45,
              ),
            ),
          ],
        ],
      ),
    );
  }
}

class _ProfilePosterModeSwitch extends StatelessWidget {
  const _ProfilePosterModeSwitch({
    required this.currentIndex,
    required this.onChanged,
  });

  final int currentIndex;
  final ValueChanged<int> onChanged;

  @override
  Widget build(BuildContext context) {
    return JoviaSegmentedControl<int>(
      value: currentIndex,
      options: const <int>[0, 1],
      labelBuilder: (value) => value == 0 ? 'Natal' : 'Timing',
      onChanged: onChanged,
    );
  }
}

class _ProfilePosterFeatureTileData {
  const _ProfilePosterFeatureTileData({
    required this.title,
    required this.subtitle,
    required this.asset,
    required this.onTap,
  });

  final String title;
  final String subtitle;
  final JoviaIllustrationAsset asset;
  final VoidCallback onTap;
}

class _ProfilePosterPortraitToken extends StatelessWidget {
  const _ProfilePosterPortraitToken({
    required this.label,
    required this.illustrationAsset,
    required this.element,
  });

  final String label;
  final JoviaIllustrationAsset illustrationAsset;
  final AstroElement element;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 118,
      height: 138,
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(28),
          color: _kProfilePosterSurfaceSoft,
          border: Border.all(color: _kProfilePosterStroke),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.2),
              blurRadius: 18,
              offset: const Offset(0, 12),
              spreadRadius: -18,
            ),
          ],
        ),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(27),
          child: Stack(
            children: [
              const Positioned.fill(
                child: JoviaColorWash(
                  asset: JoviaColorAsset.wash14,
                  opacity: 0.08,
                ),
              ),
              Center(
                child: JoviaIllustrationAccent(
                  asset: illustrationAsset,
                  width: 106,
                  height: 106,
                  opacity: 0.98,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _ProfilePosterLeadSection extends StatelessWidget {
  const _ProfilePosterLeadSection({
    required this.title,
    required this.subtitle,
    required this.intro,
    required this.body,
    required this.chips,
    required this.illustrationAsset,
    required this.onTap,
  });

  final String title;
  final String subtitle;
  final String intro;
  final String body;
  final List<String> chips;
  final JoviaIllustrationAsset illustrationAsset;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final bullets = _profilePosterBullets(
      body.trim().isNotEmpty ? body : intro,
    );
    final subtitleText = subtitle.trim();
    final leadLine = intro.trim().isNotEmpty
        ? intro.trim()
        : (bullets.isNotEmpty ? bullets.first : 'Senin ana hikâyen');
    final normalizedBody = <String>[];
    for (final bullet in bullets) {
      final text = bullet.replaceAll(RegExp(r'\s+'), ' ').trim();
      if (text.isEmpty) {
        continue;
      }
      if (text.toLowerCase() == leadLine.toLowerCase()) {
        continue;
      }
      if (normalizedBody.any(
        (item) => item.toLowerCase() == text.toLowerCase(),
      )) {
        continue;
      }
      normalizedBody.add(text);
      if (normalizedBody.length == 2) {
        break;
      }
    }
    return LayoutBuilder(
      builder: (context, constraints) {
        final compact = constraints.maxWidth < 390;
        final portraitWidth = compact ? 118.0 : 134.0;
        final portraitHeight = compact ? 156.0 : 182.0;
        final portraitRadius = compact ? 30.0 : 34.0;
        final crystalInset = compact ? 92.0 : 134.0;
        final ctaTop = portraitHeight + (compact ? 66.0 : 78.0);

        TextStyle monoStyle({
          required Color color,
          required double fontSize,
          required double height,
          double letterSpacing = 0.02,
          FontWeight fontWeight = FontWeight.w500,
        }) {
          return profile.typography.bodyReading.copyWith(
            color: color,
            fontSize: fontSize,
            height: height,
            fontWeight: fontWeight,
            letterSpacing: letterSpacing,
          );
        }

        return _ProfileLilacGlassCard(
          radius: 36,
          sequence: 0,
          strongerGlow: true,
          padding: EdgeInsets.fromLTRB(
            compact ? 18 : 22,
            22,
            compact ? 18 : 22,
            18,
          ),
          child: Stack(
            clipBehavior: Clip.none,
            children: [
              Positioned(
                top: -6,
                left: 0,
                right: 0,
                child: Center(
                  child: Container(
                    width: portraitWidth,
                    height: portraitHeight,
                    decoration: BoxDecoration(
                      color: const Color(0xFF181513),
                      borderRadius: BorderRadius.circular(portraitRadius),
                      border: Border.all(
                        color: Colors.white.withValues(alpha: 0.08),
                      ),
                    ),
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(portraitRadius - 1),
                      child: Stack(
                        children: [
                          const Positioned.fill(
                            child: JoviaColorWash(
                              asset: JoviaColorAsset.wash14,
                              opacity: 0.12,
                            ),
                          ),
                          Center(
                            child: JoviaIllustrationAccent(
                              asset: illustrationAsset,
                              width: compact ? 108 : 122,
                              height: compact ? 108 : 122,
                              opacity: 0.98,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
              Positioned(
                right: compact ? -10 : 2,
                bottom: 18,
                child: JoviaIllustrationAccent(
                  asset: JoviaIllustrationAsset.rocks,
                  width: compact ? 104 : 124,
                  height: compact ? 78 : 94,
                  opacity: 0.9,
                ),
              ),
              Positioned(
                right: compact ? 4 : 10,
                top: ctaTop,
                child: InkWell(
                  onTap: onTap,
                  borderRadius: BorderRadius.circular(999),
                  child: Padding(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 4,
                      vertical: 2,
                    ),
                    child: Text(
                      'TAM OKUMAYI AÇ',
                      style: profile.typography.monoEyebrow.copyWith(
                        color: Colors.white,
                        fontSize: compact ? 10.8 : 11.8,
                        fontWeight: FontWeight.w700,
                        letterSpacing: compact ? 1.24 : 1.48,
                      ),
                    ),
                  ),
                ),
              ),
              Padding(
                padding: EdgeInsets.only(
                  top: portraitHeight + (compact ? 24 : 28),
                  right: compact ? 0 : 4,
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title.toUpperCase(),
                      style: profile.typography.monoEyebrow.copyWith(
                        color: _kProfilePosterMuted.withValues(alpha: 0.7),
                        fontSize: 11.4,
                        letterSpacing: 1.8,
                      ),
                    ),
                    const SizedBox(height: 20),
                    Padding(
                      padding: EdgeInsets.only(right: crystalInset),
                      child: Text(
                        leadLine,
                        style: monoStyle(
                          color: const Color(0xFFF5F2EE),
                          fontSize: compact ? 16.6 : 18.0,
                          height: 1.42,
                          letterSpacing: 0.04,
                        ),
                      ),
                    ),
                    if (subtitleText.isNotEmpty) ...[
                      const SizedBox(height: 16),
                      Padding(
                        padding: EdgeInsets.only(right: crystalInset),
                        child: Text(
                          subtitleText,
                          style: monoStyle(
                            color: const Color(0xFFF2ECE4),
                            fontSize: compact ? 14.4 : 15.2,
                            height: 1.62,
                          ),
                        ),
                      ),
                    ],
                    if (normalizedBody.isNotEmpty) ...[
                      const SizedBox(height: 20),
                      for (
                        var index = 0;
                        index < normalizedBody.length;
                        index++
                      ) ...[
                        Padding(
                          padding: EdgeInsets.only(
                            right: index == normalizedBody.length - 1
                                ? crystalInset
                                : 0,
                          ),
                          child: Text(
                            normalizedBody[index],
                            style: monoStyle(
                              color: const Color(0xFFF2ECE4),
                              fontSize: compact ? 14.7 : 15.4,
                              height: 1.66,
                            ),
                          ),
                        ),
                        if (index != normalizedBody.length - 1)
                          const SizedBox(height: 20),
                      ],
                    ],
                    if (chips.isNotEmpty) ...[
                      const SizedBox(height: 24),
                      Padding(
                        padding: EdgeInsets.only(right: crystalInset),
                        child: Wrap(
                          spacing: 8,
                          runSpacing: 8,
                          children: chips
                              .take(4)
                              .map((chip) => _ProfilePosterChip(label: chip))
                              .toList(),
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}

class _ProfilePosterFeatureRail extends StatelessWidget {
  const _ProfilePosterFeatureRail({required this.items});

  final List<_ProfilePosterFeatureTileData> items;

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: [
          for (var index = 0; index < items.length; index++) ...[
            _ProfilePosterFeatureCard(
              title: items[index].title,
              subtitle: items[index].subtitle,
              asset: items[index].asset,
              color: _profilePosterFeatureColor(index),
              onTap: items[index].onTap,
            ),
            if (index != items.length - 1) const SizedBox(width: 12),
          ],
        ],
      ),
    );
  }
}

class _ProfilePosterFeatureCard extends StatelessWidget {
  const _ProfilePosterFeatureCard({
    required this.title,
    required this.subtitle,
    required this.asset,
    required this.color,
    required this.onTap,
  });

  final String title;
  final String subtitle;
  final JoviaIllustrationAsset asset;
  final Color color;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return JoviaPressable(
      onTap: onTap,
      borderRadius: BorderRadius.circular(22),
      child: Container(
        width: 118,
        height: 164,
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(22),
          color: const Color(0xFF050505),
          border: Border.all(color: _kProfilePosterStroke, width: 1.1),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.2),
              blurRadius: 18,
              offset: const Offset(0, 12),
              spreadRadius: -18,
            ),
          ],
        ),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(20),
          child: Stack(
            children: [
              const Positioned.fill(
                child: JoviaColorWash(
                  asset: JoviaColorAsset.wash05,
                  opacity: 0.1,
                ),
              ),
              Positioned(
                right: -6,
                top: 2,
                child: JoviaIllustrationAccent(
                  asset: asset,
                  width: 92,
                  height: 92,
                  opacity: 0.94,
                ),
              ),
              Positioned(
                left: 10,
                right: 10,
                bottom: 10,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title.toUpperCase(),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: profile.typography.card.copyWith(
                        color: Colors.white,
                        fontWeight: FontWeight.w700,
                        fontSize: 16.2,
                        height: 1.14,
                      ),
                    ),
                    if (subtitle.trim().isNotEmpty) ...[
                      const SizedBox(height: 6),
                      Text(
                        subtitle,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: profile.typography.metaSoft.copyWith(
                          color: Colors.white.withValues(alpha: 0.72),
                          fontSize: 12.2,
                          height: 1.42,
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _ProfilePosterPeopleStrip extends StatelessWidget {
  const _ProfilePosterPeopleStrip({required this.people});

  final List<PersonProfile> people;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return JoviaSurfaceCard(
      padding: const EdgeInsets.fromLTRB(18, 18, 18, 18),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'ONLINE ARKADAŞLARIN',
            style: profile.typography.eyebrow.copyWith(
              color: _kProfilePosterMuted,
              letterSpacing: 1.3,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Daha sakin bir sosyal halka',
            style: profile.typography.cardTitle.copyWith(
              color: const Color(0xFFF5F2EE),
            ),
          ),
          const SizedBox(height: 14),
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: [
                for (var index = 0; index < people.length; index++) ...[
                  _ProfilePosterMiniAvatar(
                    name: people[index].name,
                    tint: _profilePosterFeatureColor(index + 1),
                  ),
                  if (index != people.length - 1) const SizedBox(width: 12),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _ProfilePosterMiniAvatar extends StatelessWidget {
  const _ProfilePosterMiniAvatar({
    required this.name,
    required this.tint,
    this.size = 54,
    this.showIndicator = true,
  });

  final String name;
  final Color tint;
  final double size;
  final bool showIndicator;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final parts = name.trim().split(RegExp(r'\s+'));
    final initials = parts
        .where((item) => item.isNotEmpty)
        .take(2)
        .map((item) => item.characters.first.toUpperCase())
        .join();
    return SizedBox(
      width: size,
      height: size,
      child: Stack(
        clipBehavior: Clip.none,
        children: [
          Positioned.fill(
            child: Container(
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [
                    tint.withValues(alpha: 0.34),
                    const Color(0xFF121111),
                  ],
                ),
                border: Border.all(color: Colors.white.withValues(alpha: 0.1)),
              ),
              alignment: Alignment.center,
              child: Text(
                initials.isEmpty ? '•' : initials,
                style: profile.typography.micro.copyWith(
                  color: const Color(0xFFF5F2EE),
                  fontWeight: FontWeight.w800,
                ),
              ),
            ),
          ),
          if (showIndicator)
            Positioned(
              right: 1,
              bottom: 1,
              child: Container(
                width: size <= 32 ? 8 : 10,
                height: size <= 32 ? 8 : 10,
                decoration: BoxDecoration(
                  color: tint.withValues(alpha: 0.9),
                  shape: BoxShape.circle,
                  border: Border.all(color: _kProfilePosterBg, width: 2),
                ),
              ),
            ),
        ],
      ),
    );
  }
}

class _ProfilePosterVisualHero extends StatelessWidget {
  const _ProfilePosterVisualHero({
    required this.title,
    required this.summary,
    required this.dominantElementLabel,
    required this.illustrationAsset,
    required this.element,
  });

  final String title;
  final String summary;
  final String dominantElementLabel;
  final JoviaIllustrationAsset illustrationAsset;
  final AstroElement element;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final resolvedSummary = summary.trim().isNotEmpty
        ? summary.trim()
        : 'Kimlik aksın profil anlatısından açılıyor.';
    return Container(
      height: 220,
      padding: const EdgeInsets.fromLTRB(18, 18, 18, 18),
      decoration: BoxDecoration(
        color: _kProfilePosterSurface,
        borderRadius: BorderRadius.circular(28),
        border: Border.all(color: _kProfilePosterStroke),
      ),
      child: Stack(
        children: [
          Positioned(
            right: -8,
            bottom: -2,
            child: JoviaIllustrationAccent(
              asset: illustrationAsset,
              width: 154,
              height: 154,
              opacity: 0.94,
            ),
          ),
          Positioned(
            right: 90,
            top: 12,
            child: JoviaElementArt(
              asset: JoviaElementAssetResolver.fromElement(element),
              width: 36,
              height: 36,
              opacity: 0.78,
            ),
          ),
          SizedBox(
            width: 190,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  dominantElementLabel.toUpperCase(),
                  style: profile.typography.eyebrow.copyWith(
                    color: _kProfilePosterAccent,
                    letterSpacing: 1.5,
                  ),
                ),
                const SizedBox(height: 14),
                Text(
                  title.toUpperCase(),
                  maxLines: 3,
                  overflow: TextOverflow.ellipsis,
                  style: profile.typography.card.copyWith(
                    color: Colors.white,
                    fontSize: 28,
                    height: 1.04,
                  ),
                ),
                const SizedBox(height: 14),
                Text(
                  resolvedSummary,
                  maxLines: 4,
                  overflow: TextOverflow.ellipsis,
                  style: profile.typography.bodyCompact.copyWith(
                    color: Colors.white.withValues(alpha: 0.82),
                    height: 1.45,
                  ),
                ),
              ],
            ),
          ),
          Positioned(
            right: 12,
            bottom: 14,
            child: JoviaDividerAsset(
              kind: JoviaDividerVariant.profileReadingBreak.kind,
              width: 74,
              opacity: 0.22,
              color: Colors.white.withValues(alpha: 0.5),
            ),
          ),
        ],
      ),
    );
  }
}

class _ProfilePosterIconButton extends StatelessWidget {
  const _ProfilePosterIconButton({required this.onTap, required this.child});

  final VoidCallback? onTap;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(18),
        child: Container(
          width: 38,
          height: 38,
          decoration: BoxDecoration(
            color: const Color(0xFF111315),
            borderRadius: BorderRadius.circular(18),
            border: Border.all(color: Colors.white.withValues(alpha: 0.08)),
          ),
          child: Center(child: child),
        ),
      ),
    );
  }
}

class _ProfilePosterMessageCard extends StatelessWidget {
  const _ProfilePosterMessageCard({required this.title, required this.body});

  final String title;
  final String body;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Container(
      padding: const EdgeInsets.fromLTRB(18, 18, 18, 18),
      decoration: BoxDecoration(
        color: _kProfilePosterSurface,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: _kProfilePosterStroke),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: profile.typography.card.copyWith(color: Colors.white),
          ),
          const SizedBox(height: 8),
          Text(
            body,
            style: profile.typography.bodyCompact.copyWith(
              color: _kProfilePosterMuted,
              height: 1.5,
            ),
          ),
        ],
      ),
    );
  }
}

class _ProfilePosterLoadingCard extends StatelessWidget {
  const _ProfilePosterLoadingCard();

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Container(
      padding: const EdgeInsets.fromLTRB(18, 18, 18, 18),
      decoration: BoxDecoration(
        color: _kProfilePosterSurface,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: _kProfilePosterStroke),
      ),
      child: Row(
        children: [
          const SizedBox(
            width: 20,
            height: 20,
            child: CircularProgressIndicator(
              strokeWidth: 2,
              valueColor: AlwaysStoppedAnimation<Color>(_kProfilePosterAccent),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              'Profil anlatısı backend yorumundan çekiliyor...',
              style: profile.typography.bodyCompact.copyWith(
                color: Colors.white.withValues(alpha: 0.84),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _NarrativeCardLarge extends StatelessWidget {
  const _NarrativeCardLarge({
    required this.eyebrow,
    required this.title,
    required this.intro,
    required this.body,
    required this.chips,
    required this.illustrationAsset,
    required this.actionLabel,
    required this.nextLabel,
    required this.onTap,
  });

  final String eyebrow;
  final String title;
  final String intro;
  final String body;
  final List<String> chips;
  final JoviaIllustrationAsset illustrationAsset;
  final String actionLabel;
  final String nextLabel;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final textBlocks = <String>[
      if (intro.trim().isNotEmpty) intro.trim(),
      ..._profilePosterBullets(body.trim().isNotEmpty ? body : intro).take(2),
    ];
    final visibleBlocks = <String>[];
    for (final block in textBlocks) {
      final normalized = block.replaceAll(RegExp(r'\s+'), ' ').trim();
      if (normalized.isEmpty) {
        continue;
      }
      if (visibleBlocks.any(
        (existing) => existing.toLowerCase() == normalized.toLowerCase(),
      )) {
        continue;
      }
      visibleBlocks.add(normalized);
      if (visibleBlocks.length == 2) {
        break;
      }
    }
    return _ProfileLilacGlassCard(
      onTap: onTap,
      radius: 32,
      sequence: 1 + _profileAnimationSeed(title),
      strongerGlow: true,
      padding: const EdgeInsets.fromLTRB(20, 18, 18, 18),
      child: Stack(
        children: [
          Positioned.fill(
            child: ClipRRect(
              borderRadius: BorderRadius.circular(32),
              child: const JoviaColorWash(
                asset: JoviaColorAsset.wash09,
                opacity: 0.12,
              ),
            ),
          ),
          Positioned(
            right: -18,
            bottom: -6,
            child: JoviaIllustrationAccent(
              asset: illustrationAsset,
              width: 132,
              height: 132,
              opacity: 0.96,
            ),
          ),
          const Positioned(
            left: -30,
            top: 58,
            child: JoviaIllustrationAccent(
              asset: JoviaIllustrationAsset.shape,
              width: 74,
              height: 74,
              opacity: 0.08,
            ),
          ),
          Padding(
            padding: const EdgeInsets.only(right: 72),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Align(
                  alignment: Alignment.centerRight,
                  child: MinimalCTAButton(
                    label: actionLabel,
                    onTap: onTap,
                    glassy: true,
                  ),
                ),
                const SizedBox(height: 14),
                Text(
                  eyebrow.toUpperCase(),
                  style: profile.typography.monoEyebrow.copyWith(
                    color: profile.colors.textLight,
                    fontSize: 11.5,
                    letterSpacing: 1.7,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  title,
                  style: profile.typography.section.copyWith(
                    color: const Color(0xFFF5F2EE),
                    fontSize: 24,
                    height: 1.1,
                  ),
                ),
                const SizedBox(height: 12),
                if (visibleBlocks.isNotEmpty) ...[
                  for (
                    var index = 0;
                    index < visibleBlocks.length;
                    index++
                  ) ...[
                    Text(
                      visibleBlocks[index],
                      style: profile.typography.bodyReading.copyWith(
                        color: const Color(0xFFF0EAE2),
                        fontSize: 15.2,
                        height: 1.58,
                      ),
                    ),
                    if (index != visibleBlocks.length - 1)
                      const SizedBox(height: 18),
                  ],
                ],
                if (chips.isNotEmpty) ...[
                  const SizedBox(height: 18),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: chips
                        .take(4)
                        .map((chip) => _ProfilePosterChip(label: chip))
                        .toList(),
                  ),
                ],
                const SizedBox(height: 6),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _NarrativeCardStructured extends StatelessWidget {
  const _NarrativeCardStructured({
    required this.eyebrow,
    required this.title,
    required this.intro,
    required this.body,
    required this.chips,
    required this.actionLabel,
    required this.nextLabel,
    required this.onTap,
  });

  final String eyebrow;
  final String title;
  final String intro;
  final String body;
  final List<String> chips;
  final String actionLabel;
  final String nextLabel;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final bullets = _profilePosterBullets(
      body.trim().isNotEmpty ? body : intro,
    ).take(3).toList();
    return JoviaSurfaceCard(
      padding: const EdgeInsets.fromLTRB(18, 18, 18, 18),
      backgroundColor: _kProfilePosterSurface,
      borderColor: _kProfilePosterStroke,
      radius: 24,
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 3,
            height: 160,
            decoration: BoxDecoration(
              color: _kProfilePosterAccent,
              borderRadius: BorderRadius.circular(999),
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Stack(
              children: [
                Positioned(
                  right: -6,
                  top: -4,
                  child: JoviaIllustrationAccent(
                    asset: JoviaIllustrationAsset.layers,
                    width: 72,
                    height: 72,
                    opacity: 0.24,
                  ),
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      eyebrow.toUpperCase(),
                      style: profile.typography.monoEyebrow.copyWith(
                        color: profile.colors.warmAccent,
                        fontSize: 11.5,
                        letterSpacing: 1.7,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      title,
                      style: profile.typography.section.copyWith(
                        color: Colors.white,
                        fontSize: 22,
                        height: 1.12,
                      ),
                    ),
                    if (intro.trim().isNotEmpty) ...[
                      const SizedBox(height: 8),
                      Text(
                        intro,
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                        style: profile.typography.bodyReading.copyWith(
                          color: Colors.white.withValues(alpha: 0.86),
                          fontSize: 14.8,
                          height: 1.52,
                        ),
                      ),
                    ],
                    if (bullets.isNotEmpty) ...[
                      const SizedBox(height: 14),
                      for (var index = 0; index < bullets.length; index++) ...[
                        _ProfilePosterBullet(text: bullets[index]),
                        if (index != bullets.length - 1)
                          const SizedBox(height: 8),
                      ],
                    ],
                    if (chips.isNotEmpty) ...[
                      const SizedBox(height: 12),
                      Wrap(
                        spacing: 8,
                        runSpacing: 8,
                        children: chips
                            .take(3)
                            .map((chip) => _ProfilePosterChip(label: chip))
                            .toList(),
                      ),
                    ],
                    const SizedBox(height: 16),
                    _ProfilePosterFooterButton(
                      label: actionLabel,
                      onTap: onTap,
                    ),
                    const SizedBox(height: 12),
                    _ProfilePosterNextCardPreview(nextLabel: nextLabel),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _NarrativeCardImageLed extends StatelessWidget {
  const _NarrativeCardImageLed({
    required this.eyebrow,
    required this.title,
    required this.intro,
    required this.body,
    required this.chips,
    required this.illustrationAsset,
    required this.actionLabel,
    required this.nextLabel,
    required this.onTap,
  });

  final String eyebrow;
  final String title;
  final String intro;
  final String body;
  final List<String> chips;
  final JoviaIllustrationAsset illustrationAsset;
  final String actionLabel;
  final String nextLabel;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final bullets = _profilePosterBullets(
      body.trim().isNotEmpty ? body : intro,
    ).take(2).toList();
    return JoviaSurfaceCard(
      backgroundColor: _kProfilePosterSurface,
      borderColor: _kProfilePosterStroke,
      radius: 28,
      padding: EdgeInsets.zero,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            height: 188,
            decoration: BoxDecoration(
              borderRadius: const BorderRadius.vertical(
                top: Radius.circular(28),
              ),
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  const Color(0xFF050505),
                  Color.alphaBlend(
                    _kProfilePosterAccent.withValues(alpha: 0.08),
                    const Color(0xFF070605),
                  ),
                  const Color(0xFF050505),
                ],
              ),
            ),
            child: Stack(
              children: [
                Positioned(
                  right: -10,
                  bottom: -4,
                  child: JoviaIllustrationAccent(
                    asset: illustrationAsset,
                    width: 164,
                    height: 164,
                    opacity: 0.98,
                  ),
                ),
                const Positioned(
                  left: -26,
                  top: 66,
                  child: JoviaIllustrationAccent(
                    asset: JoviaIllustrationAsset.shape,
                    width: 84,
                    height: 84,
                    opacity: 0.18,
                  ),
                ),
                Positioned(
                  left: 18,
                  top: 18,
                  child: Text(
                    eyebrow.toUpperCase(),
                    style: profile.typography.monoEyebrow.copyWith(
                      color: _kProfilePosterMuted,
                      fontSize: 11.5,
                      letterSpacing: 1.75,
                    ),
                  ),
                ),
                Positioned(
                  left: 18,
                  right: 126,
                  bottom: 18,
                  child: Text(
                    title,
                    style: profile.typography.editorialHeadline.copyWith(
                      color: Colors.white,
                      fontSize: 28,
                      height: 1.02,
                    ),
                  ),
                ),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.fromLTRB(18, 18, 18, 18),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (intro.trim().isNotEmpty)
                  Text(
                    intro,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: profile.typography.bodyReading.copyWith(
                      color: Colors.white.withValues(alpha: 0.88),
                      fontSize: 15.2,
                      height: 1.52,
                    ),
                  ),
                if (bullets.isNotEmpty) ...[
                  const SizedBox(height: 14),
                  for (var index = 0; index < bullets.length; index++) ...[
                    Text(
                      bullets[index],
                      style: profile.typography.bodyCompact.copyWith(
                        color: _kProfilePosterMuted,
                        height: 1.5,
                      ),
                    ),
                    if (index != bullets.length - 1) const SizedBox(height: 10),
                  ],
                ],
                if (chips.isNotEmpty) ...[
                  const SizedBox(height: 12),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: chips
                        .take(3)
                        .map(
                          (chip) => _ProfilePosterChip(
                            label: chip,
                            tone: _ProfilePosterChipTone.accent,
                          ),
                        )
                        .toList(),
                  ),
                ],
                const SizedBox(height: 16),
                _ProfilePosterFooterButton(label: actionLabel, onTap: onTap),
                const SizedBox(height: 12),
                _ProfilePosterNextCardPreview(nextLabel: nextLabel),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _ProfilePosterNextCardPreview extends StatelessWidget {
  const _ProfilePosterNextCardPreview({required this.nextLabel});

  final String nextLabel;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    if (nextLabel.trim().isEmpty) {
      return const SizedBox.shrink();
    }
    return Text(
      'Sıradaki: $nextLabel',
      style: profile.typography.metaSoft.copyWith(
        color: Colors.white.withValues(alpha: 0.58),
        fontWeight: FontWeight.w600,
      ),
    );
  }
}

class _ProfilePosterNarrativeSection extends StatelessWidget {
  const _ProfilePosterNarrativeSection({
    required this.eyebrow,
    required this.title,
    required this.intro,
    required this.body,
    required this.chips,
    required this.illustrationAsset,
    required this.actionLabel,
    required this.onTap,
  });

  final String eyebrow;
  final String title;
  final String intro;
  final String body;
  final List<String> chips;
  final JoviaIllustrationAsset illustrationAsset;
  final String actionLabel;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final bullets = _profilePosterBullets(
      body.trim().isNotEmpty ? body : intro,
    );
    return JoviaSurfaceCard(
      padding: const EdgeInsets.fromLTRB(24, 22, 24, 22),
      backgroundColor: profile.colors.panelSoft,
      borderColor: profile.colors.hairline,
      radius: 28,
      child: Stack(
        children: [
          Positioned(
            left: 0,
            top: 2,
            bottom: 2,
            child: const _ProfilePosterDashedRail(),
          ),
          Positioned(
            right: 0,
            top: 2,
            bottom: 2,
            child: const _ProfilePosterDashedRail(),
          ),
          Positioned(
            right: -8,
            bottom: 0,
            child: JoviaIllustrationAccent(
              asset: illustrationAsset,
              width: 112,
              height: 112,
              opacity: 0.94,
            ),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  eyebrow.toUpperCase(),
                  style: profile.typography.monoEyebrow.copyWith(
                    color: profile.colors.warmAccent,
                    fontSize: 11.5,
                    letterSpacing: 1.75,
                  ),
                ),
                const SizedBox(height: 10),
                Text(
                  title.toUpperCase(),
                  style: profile.typography.section.copyWith(
                    color: Colors.white,
                    fontSize: 24,
                    height: 1.12,
                  ),
                ),
                if (intro.trim().isNotEmpty) ...[
                  const SizedBox(height: 10),
                  Text(
                    intro.trim(),
                    style: profile.typography.bodyReading.copyWith(
                      color: Colors.white.withValues(alpha: 0.82),
                      fontSize: 15.2,
                      height: 1.58,
                    ),
                  ),
                ],
                if (bullets.isNotEmpty) ...[
                  const SizedBox(height: 16),
                  for (final bullet in bullets) ...[
                    _ProfilePosterBullet(text: bullet),
                    const SizedBox(height: 10),
                  ],
                ],
                if (chips.isNotEmpty) ...[
                  const SizedBox(height: 6),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: chips
                        .map((chip) => _ProfilePosterChip(label: chip))
                        .toList(),
                  ),
                ],
                const SizedBox(height: 18),
                _ProfilePosterFooterButton(label: actionLabel, onTap: onTap),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _ProfilePosterPlacementsStrip extends StatelessWidget {
  const _ProfilePosterPlacementsStrip({
    required this.sectionTitle,
    required this.cards,
    required this.onOpenAll,
    required this.onOpenCard,
  });

  final String sectionTitle;
  final List<_ProfileNarrativeCard> cards;
  final VoidCallback onOpenAll;
  final ValueChanged<_ProfileNarrativeCard> onOpenCard;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'YERLEŞİM VE AÇILAR',
          style: profile.typography.monoEyebrow.copyWith(
            color: _kProfilePosterMuted,
            fontSize: 11.0,
            letterSpacing: 1.7,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          sectionTitle,
          style: profile.typography.section.copyWith(
            color: Colors.white,
            fontWeight: FontWeight.w700,
            fontSize: 19,
            height: 1.16,
          ),
        ),
        const SizedBox(height: 18),
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: Row(
            children: [
              for (var index = 0; index < cards.length; index++) ...[
                _ProfilePosterMiniCard(
                  title: _displayTitleForCard(cards[index]),
                  body: cards[index].summary.isNotEmpty
                      ? cards[index].summary
                      : cards[index].previewBody,
                  asset: _profilePosterIllustrationForCard(cards[index]),
                  tone: profileDetailToneForSignature(
                    title: _displayTitleForCard(cards[index]),
                    summary: cards[index].summary,
                    family: cards[index].family,
                    eyebrow: cards[index].eyebrow,
                  ),
                  onTap: () => onOpenCard(cards[index]),
                ),
                if (index != cards.length - 1) const SizedBox(width: 14),
              ],
            ],
          ),
        ),
        const SizedBox(height: 18),
        _ProfilePosterFooterButton(label: 'Daha fazla aç', onTap: onOpenAll),
      ],
    );
  }
}

class _ProfilePosterThreadSection extends StatelessWidget {
  const _ProfilePosterThreadSection({
    required this.items,
    required this.onOpenAll,
    required this.onOpenThread,
  });

  final List<_SupportingThreadItem> items;
  final VoidCallback onOpenAll;
  final ValueChanged<_SupportingThreadItem> onOpenThread;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'YAN TEMALAR',
          style: profile.typography.monoEyebrow.copyWith(
            color: _kProfilePosterMuted,
            fontSize: 11.0,
            letterSpacing: 1.7,
          ),
        ),
        const SizedBox(height: 14),
        for (var index = 0; index < items.length; index++) ...[
          JoviaPressable(
            onTap: () => onOpenThread(items[index]),
            borderRadius: BorderRadius.circular(18),
            child: Padding(
              padding: const EdgeInsets.symmetric(vertical: 9),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          items[index].title,
                          style: profile.typography.card.copyWith(
                            color: Colors.white,
                            fontWeight: FontWeight.w700,
                            fontSize: 17,
                            height: 1.24,
                          ),
                        ),
                        const SizedBox(height: 6),
                        Text(
                          items[index].oneLiner,
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                          style: profile.typography.metaSoft.copyWith(
                            color: _kProfilePosterMuted,
                            fontSize: 13.2,
                            height: 1.55,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 10),
                  const JoviaUiIcon(
                    asset: JoviaUiAsset.chevronRight,
                    size: 16,
                    color: _kProfilePosterAccent,
                  ),
                ],
              ),
            ),
          ),
          if (index != items.length - 1)
            Divider(color: Colors.white.withValues(alpha: 0.08), height: 18),
        ],
        const SizedBox(height: 14),
        Align(
          alignment: Alignment.centerLeft,
          child: _ProfilePosterFooterButton(
            label: 'Yan temaları aç',
            onTap: onOpenAll,
          ),
        ),
      ],
    );
  }
}

class _ProfilePosterInsightEntryCard extends StatelessWidget {
  const _ProfilePosterInsightEntryCard({
    required this.title,
    required this.body,
    required this.ctaLabel,
    required this.onTap,
  });

  final String title;
  final String body;
  final String ctaLabel;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return JoviaPressable(
      onTap: onTap,
      borderRadius: BorderRadius.circular(28),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 14),
        child: Column(
          children: [
            Text(
              'GÖLGE & BÜYÜME',
              style: profile.typography.monoEyebrow.copyWith(
                color: _kProfilePosterMuted,
                fontSize: 11.0,
                letterSpacing: 1.7,
              ),
            ),
            const SizedBox(height: 12),
            Text(
              title.toUpperCase(),
              textAlign: TextAlign.center,
              style: profile.typography.section.copyWith(
                color: Colors.white,
                fontSize: 19,
                height: 1.18,
              ),
            ),
            if (body.trim().isNotEmpty) ...[
              const SizedBox(height: 12),
              Text(
                body,
                maxLines: 4,
                overflow: TextOverflow.ellipsis,
                textAlign: TextAlign.center,
                style: profile.typography.bodyReading.copyWith(
                  color: _kProfilePosterMuted,
                  fontSize: 13.8,
                  height: 1.66,
                ),
              ),
            ],
            const SizedBox(height: 12),
            JoviaDividerAsset(
              kind: JoviaDividerVariant.detailBreak.kind,
              width: 88,
              opacity: 0.24,
              color: _kProfilePosterAccent,
            ),
            const SizedBox(height: 16),
            Container(
              width: 62,
              height: 62,
              decoration: const BoxDecoration(
                color: _kProfilePosterAccent,
                shape: BoxShape.circle,
              ),
              child: Center(
                child: JoviaIllustrationAccent(
                  asset: JoviaIllustrationAsset.planet,
                  width: 34,
                  height: 34,
                  opacity: 1,
                ),
              ),
            ),
            const SizedBox(height: 12),
            Text(
              ctaLabel.toUpperCase(),
              style: profile.typography.monoEyebrow.copyWith(
                color: Colors.white,
                fontSize: 11.5,
                letterSpacing: 1.7,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ProfilePosterTimingPreviewSection extends StatelessWidget {
  const _ProfilePosterTimingPreviewSection({
    required this.isLoading,
    required this.error,
    required this.periodCore,
    required this.peaks,
    required this.onOpenTiming,
  });

  final bool isLoading;
  final String? error;
  final PeriodCoreDto? periodCore;
  final List<PeriodPeakTimelineItemDto> peaks;
  final VoidCallback onOpenTiming;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final core = periodCore;
    final previewPeaks = peaks.take(2).toList();
    final summary = core == null
        ? ''
        : (core.coreStory.trim().isNotEmpty
              ? core.coreStory.trim()
              : (core.bigPicture.trim().isNotEmpty
                    ? core.bigPicture.trim()
                    : core.upperMeaning.trim()));
    return Container(
      padding: const EdgeInsets.fromLTRB(18, 18, 18, 18),
      decoration: BoxDecoration(
        color: _kProfilePosterSurface,
        borderRadius: BorderRadius.circular(28),
        border: Border.all(color: _kProfilePosterStroke),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'TIMING AKIŞI',
            style: profile.typography.monoEyebrow.copyWith(
              color: profile.colors.warmAccent,
              fontSize: 11.5,
              letterSpacing: 1.8,
            ),
          ),
          const SizedBox(height: 10),
          if (isLoading && core == null)
            const _ProfilePosterLoadingCard()
          else if ((error ?? '').trim().isNotEmpty && core == null)
            _ProfilePosterMessageCard(
              title: 'Timing akışı alınamadı',
              body: error!,
            )
          else if (core == null)
            const _ProfilePosterMessageCard(
              title: 'Timing akışı hazır değil',
              body:
                  'Dönem özeti geldiğinde burada sadece kısa bir teaser ve yaklaşan pikler görünecek.',
            )
          else ...[
            Text(
              core.title.trim().isNotEmpty
                  ? core.title.trim()
                  : 'Şu anki dönem',
              style: profile.typography.section.copyWith(
                color: Colors.white,
                fontSize: 24,
                height: 1.12,
              ),
            ),
            if (summary.isNotEmpty) ...[
              const SizedBox(height: 10),
              Text(
                summary,
                maxLines: 3,
                overflow: TextOverflow.ellipsis,
                style: profile.typography.bodyReading.copyWith(
                  color: Colors.white.withValues(alpha: 0.84),
                  fontSize: 15.2,
                  height: 1.54,
                ),
              ),
            ],
            if (previewPeaks.isNotEmpty) ...[
              const SizedBox(height: 16),
              Text(
                'Yaklaşan pikler',
                style: profile.typography.monoEyebrow.copyWith(
                  color: _kProfilePosterMuted,
                  fontSize: 11.5,
                  letterSpacing: 1.7,
                ),
              ),
              const SizedBox(height: 10),
              for (var index = 0; index < previewPeaks.length; index++) ...[
                _ProfilePosterPeakRow(item: previewPeaks[index]),
                if (index != previewPeaks.length - 1)
                  Divider(
                    color: Colors.white.withValues(alpha: 0.08),
                    height: 18,
                  ),
              ],
            ],
          ],
          const SizedBox(height: 18),
          SizedBox(
            width: double.infinity,
            child: _ProfilePosterFooterButton(
              label: 'Timing akışını aç',
              emphasized: true,
              onTap: onOpenTiming,
            ),
          ),
        ],
      ),
    );
  }
}

class _ProfilePosterPeakRow extends StatelessWidget {
  const _ProfilePosterPeakRow({required this.item});

  final PeriodPeakTimelineItemDto item;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final hint = item.timeHintTr.trim();
    final subtitle = item.signatureTr.trim().isNotEmpty
        ? item.signatureTr.trim()
        : hint;
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          width: 8,
          height: 8,
          margin: const EdgeInsets.only(top: 6),
          decoration: const BoxDecoration(
            color: _kProfilePosterAccent,
            shape: BoxShape.circle,
          ),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                item.displayTitle,
                style: profile.typography.body.copyWith(
                  color: Colors.white,
                  fontWeight: FontWeight.w700,
                ),
              ),
              if (subtitle.isNotEmpty) ...[
                const SizedBox(height: 3),
                Text(
                  subtitle,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: profile.typography.micro.copyWith(
                    color: _kProfilePosterMuted,
                    height: 1.4,
                  ),
                ),
              ],
            ],
          ),
        ),
      ],
    );
  }
}

class _ProfilePosterAstroItem extends StatelessWidget {
  const _ProfilePosterAstroItem({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final resolved = value.trim().isEmpty ? '—' : value.trim();
    final icon = switch (label.toLowerCase()) {
      'güneş' || 'gunes' => Icons.wb_sunny_outlined,
      'yükselen' || 'yukselen' => Icons.north_east_rounded,
      'ay' => Icons.brightness_2_outlined,
      _ => Icons.circle_outlined,
    };
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 16, color: const Color(0xFFF5F2EE)),
        const SizedBox(width: 6),
        Text(
          resolved,
          style: profile.typography.micro.copyWith(
            color: Colors.white.withValues(alpha: 0.9),
            fontSize: 13.5,
            fontWeight: FontWeight.w600,
          ),
        ),
      ],
    );
  }
}

class _ProfilePosterBullet extends StatelessWidget {
  const _ProfilePosterBullet({required this.text});

  final String text;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.only(top: 8),
          child: Container(
            width: 5,
            height: 5,
            decoration: const BoxDecoration(
              color: _kProfilePosterAccent,
              shape: BoxShape.circle,
            ),
          ),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: Text(
            text,
            style: profile.typography.bodyCompact.copyWith(
              color: Colors.white.withValues(alpha: 0.82),
              height: 1.55,
            ),
          ),
        ),
      ],
    );
  }
}

enum _ProfilePosterChipTone { neutral, accent }

class _ProfilePosterChip extends StatelessWidget {
  const _ProfilePosterChip({
    required this.label,
    this.tone = _ProfilePosterChipTone.neutral,
  });

  final String label;
  final _ProfilePosterChipTone tone;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final isAccent = tone == _ProfilePosterChipTone.accent;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 7),
      decoration: BoxDecoration(
        color: isAccent
            ? _kProfilePosterLilac.withValues(alpha: 0.18)
            : Colors.white.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(999),
        border: Border.all(
          color: isAccent
              ? _kProfilePosterLilac.withValues(alpha: 0.42)
              : Colors.white.withValues(alpha: 0.24),
          width: 1,
        ),
        boxShadow: [
          if (isAccent)
            BoxShadow(
              color: _kProfilePosterLilac.withValues(alpha: 0.18),
              blurRadius: 18,
              offset: const Offset(0, 8),
              spreadRadius: -10,
            ),
        ],
      ),
      child: Text(
        label,
        style: profile.typography.buttonLabel.copyWith(
          color: isAccent ? Colors.white : Colors.white.withValues(alpha: 0.90),
          fontSize: 12.0,
          fontWeight: FontWeight.w500,
          letterSpacing: 0.02,
        ),
      ),
    );
  }
}

int _profileAnimationSeed(String value) {
  final trimmed = value.trim();
  if (trimmed.isEmpty) {
    return 0;
  }
  return trimmed.runes.fold<int>(0, (sum, rune) => sum + rune) % 7;
}

class _ProfileCardEntrance extends StatelessWidget {
  const _ProfileCardEntrance({required this.sequence, required this.child});

  final int sequence;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return TweenAnimationBuilder<double>(
      tween: Tween<double>(begin: 0, end: 1),
      duration: Duration(milliseconds: 560 + (sequence * 80)),
      curve: Curves.easeOutCubic,
      builder: (context, value, child) {
        final eased = Curves.easeOutCubic.transform(value);
        return Opacity(
          opacity: eased,
          child: Transform.translate(
            offset: Offset(0, (1 - eased) * 20),
            child: Transform.scale(
              scale: 0.965 + (eased * 0.035),
              child: child,
            ),
          ),
        );
      },
      child: child,
    );
  }
}

class _ProfileAnimatedOrb extends StatelessWidget {
  const _ProfileAnimatedOrb({
    required this.sequence,
    required this.from,
    required this.to,
    required this.size,
    required this.colors,
    this.opacity = 0.22,
  });

  final int sequence;
  final Alignment from;
  final Alignment to;
  final double size;
  final List<Color> colors;
  final double opacity;

  @override
  Widget build(BuildContext context) {
    return TweenAnimationBuilder<double>(
      tween: Tween<double>(begin: 0, end: 1),
      duration: Duration(milliseconds: 900 + (sequence * 110)),
      curve: Curves.easeOutCubic,
      builder: (context, value, _) {
        final alignment = Alignment.lerp(from, to, value) ?? to;
        return Align(
          alignment: alignment,
          child: Opacity(
            opacity: opacity * (0.72 + (0.28 * value)),
            child: Transform.scale(
              scale: 0.84 + (0.16 * value),
              child: Container(
                width: size,
                height: size,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  gradient: RadialGradient(
                    colors: [
                      colors.first.withValues(alpha: 0.95),
                      colors.last.withValues(alpha: 0.0),
                    ],
                  ),
                ),
              ),
            ),
          ),
        );
      },
    );
  }
}

class _ProfileLilacGlassCard extends StatelessWidget {
  const _ProfileLilacGlassCard({
    required this.child,
    required this.radius,
    required this.sequence,
    this.padding = EdgeInsets.zero,
    this.onTap,
    this.strongerGlow = false,
    this.tone,
  });

  final Widget child;
  final double radius;
  final int sequence;
  final EdgeInsetsGeometry padding;
  final VoidCallback? onTap;
  final bool strongerGlow;
  final ProfileDetailTone? tone;

  @override
  Widget build(BuildContext context) {
    final resolvedTone = tone;
    final accent = resolvedTone?.accent ?? _kProfilePosterLilac;
    final accentSoft = resolvedTone?.accentSoft ?? _kProfilePosterMint;
    final accentWarm = resolvedTone?.mutedText ?? _kProfilePosterBlush;
    final surface = resolvedTone?.surface ?? const Color(0xFF151218);
    final surfaceDeep = resolvedTone?.background ?? const Color(0xFF09080B);
    final glow =
        resolvedTone?.glow ?? _kProfilePosterLilac.withValues(alpha: 0.12);
    final stroke = resolvedTone?.stroke ?? Colors.white.withValues(alpha: 0.16);
    final card = _ProfileCardEntrance(
      sequence: sequence,
      child: ClipRRect(
        borderRadius: BorderRadius.circular(radius),
        child: BackdropFilter(
          filter: ui.ImageFilter.blur(sigmaX: 18, sigmaY: 18),
          child: Container(
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(radius),
              border: Border.all(color: stroke, width: 1.1),
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  Color.alphaBlend(
                    accent.withValues(alpha: strongerGlow ? 0.22 : 0.14),
                    surface,
                  ),
                  Color.alphaBlend(
                    accentSoft.withValues(alpha: strongerGlow ? 0.12 : 0.08),
                    surfaceDeep,
                  ),
                  Color.alphaBlend(
                    accentWarm.withValues(alpha: strongerGlow ? 0.14 : 0.08),
                    surface,
                  ),
                ],
              ),
              boxShadow: [
                BoxShadow(
                  color: glow.withValues(alpha: strongerGlow ? 0.44 : 0.84),
                  blurRadius: strongerGlow ? 32 : 24,
                  offset: const Offset(0, 18),
                  spreadRadius: -22,
                ),
                BoxShadow(
                  color: Colors.black.withValues(alpha: 0.24),
                  blurRadius: 24,
                  offset: const Offset(0, 16),
                  spreadRadius: -18,
                ),
              ],
            ),
            child: Stack(
              children: [
                Positioned.fill(
                  child: DecoratedBox(
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                        colors: [
                          Colors.white.withValues(alpha: 0.08),
                          Colors.transparent,
                          Colors.white.withValues(alpha: 0.02),
                        ],
                      ),
                    ),
                  ),
                ),
                _ProfileAnimatedOrb(
                  sequence: sequence,
                  from: const Alignment(-1.05, -0.95),
                  to: const Alignment(-0.72, -0.58),
                  size: strongerGlow ? 210 : 156,
                  colors: [accentSoft, accent],
                  opacity: strongerGlow ? 0.20 : 0.14,
                ),
                _ProfileAnimatedOrb(
                  sequence: sequence + 1,
                  from: const Alignment(1.1, 1.05),
                  to: const Alignment(0.78, 0.88),
                  size: strongerGlow ? 240 : 170,
                  colors: [accentWarm, accent],
                  opacity: strongerGlow ? 0.24 : 0.16,
                ),
                _ProfileAnimatedOrb(
                  sequence: sequence + 2,
                  from: const Alignment(1.06, -1.08),
                  to: const Alignment(0.92, -0.92),
                  size: strongerGlow ? 156 : 110,
                  colors: [_kProfilePosterButter, accentSoft],
                  opacity: strongerGlow ? 0.12 : 0.08,
                ),
                Positioned(
                  left: 16,
                  right: 16,
                  top: 0,
                  child: TweenAnimationBuilder<double>(
                    tween: Tween<double>(begin: 0, end: 1),
                    duration: Duration(milliseconds: 760 + (sequence * 70)),
                    curve: Curves.easeOutCubic,
                    builder: (context, value, child) {
                      return Opacity(
                        opacity: 0.22 * value,
                        child: Transform.translate(
                          offset: Offset(0, -16 + (16 * value)),
                          child: child,
                        ),
                      );
                    },
                    child: Container(
                      height: 54,
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(radius),
                        gradient: LinearGradient(
                          begin: Alignment.topCenter,
                          end: Alignment.bottomCenter,
                          colors: [
                            Colors.white.withValues(alpha: 0.24),
                            Colors.transparent,
                          ],
                        ),
                      ),
                    ),
                  ),
                ),
                Padding(padding: padding, child: child),
              ],
            ),
          ),
        ),
      ),
    );
    if (onTap == null) {
      return card;
    }
    return JoviaPressable(
      onTap: onTap,
      borderRadius: BorderRadius.circular(radius),
      child: card,
    );
  }
}

class _ProfilePosterMiniCard extends StatelessWidget {
  const _ProfilePosterMiniCard({
    required this.title,
    required this.body,
    required this.asset,
    required this.onTap,
    this.tone,
  });

  final String title;
  final String body;
  final JoviaIllustrationAsset asset;
  final VoidCallback onTap;
  final ProfileDetailTone? tone;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final resolvedTone = tone;
    return _ProfileLilacGlassCard(
      onTap: onTap,
      radius: 22,
      sequence: 3 + _profileAnimationSeed(title),
      padding: EdgeInsets.zero,
      tone: resolvedTone,
      child: SizedBox(
        width: 152,
        child: ClipRRect(
          borderRadius: BorderRadius.circular(22),
          child: Stack(
            children: [
              const Positioned.fill(
                child: JoviaColorWash(
                  asset: JoviaColorAsset.wash14,
                  opacity: 0.16,
                ),
              ),
              Positioned(
                right: -28,
                top: -20,
                child: Container(
                  width: 84,
                  height: 84,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    gradient: RadialGradient(
                      colors: [
                        (resolvedTone?.accent ?? _kProfilePosterLilac)
                            .withValues(alpha: 0.34),
                        (resolvedTone?.accentSoft ?? _kProfilePosterBlush)
                            .withValues(alpha: 0.0),
                      ],
                    ),
                  ),
                ),
              ),
              Padding(
                padding: const EdgeInsets.fromLTRB(14, 14, 14, 16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Container(
                      height: 108,
                      width: double.infinity,
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(18),
                        gradient: LinearGradient(
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                          colors: [
                            Color.alphaBlend(
                              (resolvedTone?.accent ?? _kProfilePosterLilac)
                                  .withValues(alpha: 0.32),
                              resolvedTone?.surfaceStrong ??
                                  const Color(0xFF262031),
                            ),
                            Color.alphaBlend(
                              (resolvedTone?.accentSoft ?? _kProfilePosterMint)
                                  .withValues(alpha: 0.16),
                              resolvedTone?.surface ?? const Color(0xFF15121D),
                            ),
                            Color.alphaBlend(
                              _kProfilePosterButter.withValues(alpha: 0.22),
                              resolvedTone?.background ??
                                  const Color(0xFF241F20),
                            ),
                          ],
                        ),
                      ),
                      child: Center(
                        child: JoviaIllustrationAccent(
                          asset: asset,
                          width: 74,
                          height: 74,
                          opacity: 0.9,
                        ),
                      ),
                    ),
                    const SizedBox(height: 14),
                    Text(
                      title,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: profile.typography.card.copyWith(
                        color: Colors.white,
                        fontWeight: FontWeight.w700,
                        fontSize: 16.5,
                        height: 1.28,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      body,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: profile.typography.metaSoft.copyWith(
                        color: resolvedTone?.mutedText ?? _kProfilePosterMuted,
                        fontSize: 12.6,
                        height: 1.58,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _ProfilePosterFooterButton extends StatelessWidget {
  const _ProfilePosterFooterButton({
    required this.label,
    this.onTap,
    this.emphasized = false,
  });

  final String label;
  final VoidCallback? onTap;
  final bool emphasized;

  @override
  Widget build(BuildContext context) {
    return emphasized
        ? JoviaPrimaryButton(label: label, onTap: onTap)
        : MinimalCTAButton(label: label, onTap: onTap, glassy: true);
  }
}

class _ProfilePosterDashedRail extends StatelessWidget {
  const _ProfilePosterDashedRail();

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final dashCount = (constraints.maxHeight / 14).floor().clamp(4, 18);
        return Column(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: List.generate(
            dashCount,
            (_) => Container(
              width: 2,
              height: 8,
              decoration: BoxDecoration(
                color: _kProfilePosterAccent.withValues(alpha: 0.9),
                borderRadius: BorderRadius.circular(999),
              ),
            ),
          ),
        );
      },
    );
  }
}

String _sanitizeUserFacingChip(String raw) {
  final normalized = raw.replaceAll(RegExp(r'\s+'), ' ').trim();
  if (normalized.isEmpty) {
    return '';
  }
  const chipReplacements = <String, String>{
    'upgrade': 'Yenilik',
    'kalibrasyon': 'İç Denge',
    'iç ayar': 'İç Denge',
    'sistem + yenilik': 'Yapı ve Yenilik',
    'network': 'Bağlantı',
    'inkübasyon': 'İçte Olgunlaşma',
    'pişirip çık': 'İçte Olgunlaşma',
    'identity': 'Kimlik',
    'relationships': 'İlişkiler',
    'relationship': 'İlişki',
    'mind': 'Zihin',
    'career': 'Kariyer',
    'home': 'Ev',
    'inner': 'İç Dünya',
  };
  final lower = normalized.toLowerCase();
  final replaced = chipReplacements[lower];
  final value = replaced ?? normalized;
  const hiddenPrefixes = <String>[
    'type:',
    'key:',
    'origin:',
    'family:',
    'bundle_type:',
    'card_key:',
  ];
  if (hiddenPrefixes.any(lower.startsWith)) {
    return '';
  }
  const hiddenWhole = <String>{
    'angle',
    'asc',
    'mc',
    'ic',
    'desc',
    'ascendant',
    'moon_sign',
    'sun_sign',
    'rising_sign',
  };
  if (hiddenWhole.contains(lower)) {
    return '';
  }
  if (lower.contains('angle_identity_bundle') ||
      lower.contains('type: angle') ||
      lower.contains('key: asc')) {
    return '';
  }
  if (lower.contains('_') && !lower.contains(' ')) {
    return '';
  }
  return value;
}

List<String> _sanitizeUserFacingChips(dynamic raw, {int max = 4}) {
  if (raw is! List) {
    return const <String>[];
  }
  final sanitized = <String>[];
  for (final item in raw) {
    final clean = _sanitizeUserFacingChip(item.toString());
    if (clean.isEmpty) {
      continue;
    }
    final duplicate = sanitized.any(
      (existing) => existing.toLowerCase() == clean.toLowerCase(),
    );
    if (duplicate) {
      continue;
    }
    sanitized.add(clean);
    if (sanitized.length >= max) {
      break;
    }
  }
  return sanitized;
}

List<String> _profilePosterBullets(String text) {
  final normalized = text
      .replaceAll('\n', ' ')
      .replaceAll(RegExp(r'\s+'), ' ')
      .trim();
  if (normalized.isEmpty) {
    return const <String>[];
  }
  final parts = normalized
      .split(RegExp(r'(?<=[.!?])\s+'))
      .map((item) => item.trim())
      .where((item) => item.isNotEmpty)
      .toList();
  if (parts.length >= 2) {
    return parts.take(4).toList();
  }
  return normalized
      .split(',')
      .map((item) => item.trim())
      .where((item) => item.length > 8)
      .take(4)
      .toList();
}

Color _profilePosterFeatureColor(int index) {
  const palette = <Color>[
    Color(0xFFD58A3D),
    Color(0xFF8A7F73),
    Color(0xFFB2A6C9),
    Color(0xFF5C5A56),
    Color(0xFF7A6553),
  ];
  return palette[index % palette.length];
}

JoviaIllustrationAsset _profilePosterIllustrationForCard(
  _ProfileNarrativeCard card,
) {
  final haystack = [
    card.family,
    card.title,
    card.summary,
    card.body,
    card.eyebrow,
  ].join(' ').toLowerCase();
  if (haystack.contains('zihin') || haystack.contains('mind')) {
    return JoviaIllustrationAsset.dots;
  }
  if (haystack.contains('yakın') ||
      haystack.contains('yakin') ||
      haystack.contains('kalp') ||
      haystack.contains('ilişki') ||
      haystack.contains('iliski')) {
    return JoviaIllustrationAsset.heart;
  }
  if (haystack.contains('görün') ||
      haystack.contains('gorun') ||
      haystack.contains('kariyer')) {
    return JoviaIllustrationAsset.sunGrowth;
  }
  if (haystack.contains('savun') || haystack.contains('tetik')) {
    return JoviaIllustrationAsset.blocks;
  }
  if (haystack.contains('akış') ||
      haystack.contains('akis') ||
      haystack.contains('şans') ||
      haystack.contains('sans')) {
    return JoviaIllustrationAsset.bird;
  }
  return switch (card.family) {
    'mind_mechanics' => JoviaIllustrationAsset.dots,
    'intimacy_guard' => JoviaIllustrationAsset.heart,
    'creative_channel' => JoviaIllustrationAsset.bird,
    'outer_inner_split' => JoviaIllustrationAsset.layers,
    _ => JoviaIllustrationAsset.planet,
  };
}

class _SupportingThreadsSection extends StatelessWidget {
  const _SupportingThreadsSection({required this.items});

  final List<_SupportingThreadItem> items;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final typo = profile.typography;

    return Container(
      decoration: BoxDecoration(
        color: profile.colors.surface,
        borderRadius: BorderRadius.circular(profile.radii.cardRadius * 0.65),
        border: Border.all(color: profile.colors.strokeSoft, width: 1.5),
      ),
      child: Padding(
        padding: EdgeInsets.symmetric(
          horizontal: profile.spacing.md,
          vertical: profile.spacing.sm,
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Yan Temalar',
              style: typo.body.copyWith(fontWeight: FontWeight.w700),
            ),
            SizedBox(height: profile.spacing.xs),
            for (final item in items)
              ExpansionTile(
                dense: true,
                tilePadding: EdgeInsets.zero,
                collapsedShape: const Border(),
                shape: const Border(),
                iconColor: profile.colors.primary,
                collapsedIconColor: profile.colors.textLight,
                childrenPadding: EdgeInsets.only(
                  left: profile.spacing.xs,
                  right: profile.spacing.xs,
                  bottom: profile.spacing.xs,
                ),
                title: Text(
                  item.title,
                  style: typo.body.copyWith(fontWeight: FontWeight.w600),
                ),
                subtitle: Text(item.oneLiner, style: typo.micro),
                children: [
                  Align(
                    alignment: Alignment.centerLeft,
                    child: Text(item.paragraph, style: typo.body),
                  ),
                ],
              ),
          ],
        ),
      ),
    );
  }
}

class _ElementDebugChip extends StatelessWidget {
  const _ElementDebugChip({required this.scores});

  final ElementScores scores;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final astro = context.astroTheme;
    final label = switch (scores.dominant) {
      AstroElement.fire => '🔥 Fire',
      AstroElement.water => '🌊 Water',
      AstroElement.air => '🌬 Air',
      AstroElement.earth => '🌱 Earth',
    };
    return Container(
      padding: EdgeInsets.symmetric(
        horizontal: profile.spacing.sm,
        vertical: profile.spacing.xs,
      ),
      decoration: BoxDecoration(
        color: astro.highlight.withValues(alpha: 0.18),
        border: Border.all(color: astro.accent.withValues(alpha: 0.35)),
        borderRadius: BorderRadius.circular(profile.radii.pillRadius),
      ),
      child: Text(
        label,
        style: profile.typography.micro.copyWith(color: astro.text),
      ),
    );
  }
}

InputDecoration _profileInputDecoration(BuildContext context) {
  final profile = context.profileTheme;
  return InputDecoration(
    labelStyle: profile.typography.micro.copyWith(
      color: profile.colors.textLight,
    ),
    floatingLabelStyle: profile.typography.micro.copyWith(
      color: profile.colors.primary,
    ),
    filled: true,
    fillColor: profile.colors.surface,
    contentPadding: EdgeInsets.symmetric(
      horizontal: profile.spacing.md,
      vertical: profile.spacing.sm,
    ),
    border: OutlineInputBorder(
      borderRadius: BorderRadius.circular(profile.radii.cardRadius * 0.55),
      borderSide: BorderSide(color: profile.colors.separator, width: 1),
    ),
    enabledBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(profile.radii.cardRadius * 0.55),
      borderSide: BorderSide(color: profile.colors.separator, width: 1),
    ),
    focusedBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(profile.radii.cardRadius * 0.55),
      borderSide: BorderSide(color: profile.colors.primary, width: 1.5),
    ),
  );
}

class _ProfileHeroScene extends StatelessWidget {
  const _ProfileHeroScene({
    required this.displayName,
    required this.username,
    required this.avatarUrl,
    required this.isAvatarUploading,
    required this.onAvatarEdit,
    required this.readOnly,
    required this.onSettingsTap,
  });

  final String displayName;
  final String username;
  final String? avatarUrl;
  final bool isAvatarUploading;
  final VoidCallback? onAvatarEdit;
  final bool readOnly;
  final VoidCallback? onSettingsTap;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final astro = context.astroTheme;
    final colors = profile.colors;
    final settingsTap = onSettingsTap;
    final bottomInset = MediaQuery.paddingOf(context).top;

    double clamp(double value, double min, double max) {
      if (value < min) return min;
      if (value > max) return max;
      return value;
    }

    return LayoutBuilder(
      builder: (context, constraints) {
        final width = constraints.maxWidth;
        final largeTileW = clamp(width * 0.58, 240, 260);
        const largeTileH = 280.0;
        final leftTileW = clamp(width * 0.42, 170, 190);
        const leftTileH = 210.0;

        return Stack(
          fit: StackFit.expand,
          children: <Widget>[
            DecoratedBox(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: <Color>[
                    astro.auraStops.first,
                    colors.brandPurple,
                    colors.brandLavender,
                  ],
                ),
              ),
            ),
            Align(
              alignment: Alignment.bottomLeft,
              child: IgnorePointer(
                child: Container(
                  height: 144,
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      begin: Alignment.bottomLeft,
                      end: Alignment.topLeft,
                      colors: <Color>[
                        Colors.black.withValues(alpha: 0.18),
                        Colors.transparent,
                      ],
                    ),
                  ),
                ),
              ),
            ),
            Positioned(
              top: bottomInset + 56,
              left: width - largeTileW + 20,
              child: _FloatingTile(
                width: largeTileW,
                height: largeTileH,
                radius: 28,
                rotationDeg: -10,
                fill: colors.brandLavender.withValues(alpha: 0.94),
                stroke: Colors.white.withValues(alpha: 0.18),
              ),
            ),
            Positioned(
              top: bottomInset + 48,
              left: 20,
              child: _FloatingTile(
                width: leftTileW,
                height: leftTileH,
                radius: 24,
                rotationDeg: 10,
                fill: colors.brandPurple.withValues(alpha: 0.92),
                stroke: Colors.white.withValues(alpha: 0.16),
              ),
            ),
            Positioned(
              top: bottomInset + 122,
              left: clamp(width * 0.44, 140, 184),
              child: _FloatingTile(
                width: 140,
                height: 160,
                radius: 22,
                rotationDeg: -6,
                fill: colors.brandLime.withValues(alpha: 0.9),
                stroke: Colors.white.withValues(alpha: 0.14),
              ),
            ),
            Positioned(
              top: bottomInset + 220,
              left: 24,
              child: Transform.rotate(
                angle: -0.16,
                child: Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 8,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.82),
                    borderRadius: BorderRadius.circular(999),
                    border: Border.all(
                      color: colors.brandPurple.withValues(alpha: 0.12),
                    ),
                  ),
                  child: Text(
                    'NEON WAVES',
                    style: profile.typography.meta.copyWith(
                      color: colors.brandPurple.withValues(alpha: 0.82),
                      letterSpacing: 0.5,
                    ),
                  ),
                ),
              ),
            ),
            SafeArea(
              bottom: false,
              child: Padding(
                padding: EdgeInsets.fromLTRB(
                  profile.spacing.s20,
                  profile.spacing.s12,
                  profile.spacing.s20,
                  profile.spacing.s24,
                ),
                child: Column(
                  children: <Widget>[
                    Row(
                      mainAxisAlignment: MainAxisAlignment.end,
                      children: <Widget>[
                        if (settingsTap != null)
                          _HeaderActionButton(
                            icon: Icons.settings_outlined,
                            onTap: settingsTap,
                            sceneStyle: true,
                          ),
                        if (readOnly)
                          _HeaderActionButton(
                            icon: Icons.arrow_back_rounded,
                            onTap: () => Navigator.of(
                              context,
                              rootNavigator: true,
                            ).maybePop(),
                            sceneStyle: true,
                          ),
                      ],
                    ),
                    const Spacer(),
                    Row(
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: <Widget>[
                        _AvatarHalo(
                          size: 82,
                          imageUrl: avatarUrl,
                          isUploading: isAvatarUploading,
                          onEdit: onAvatarEdit,
                          heroStyle: true,
                        ),
                        SizedBox(width: profile.spacing.s12),
                        Expanded(
                          child: Padding(
                            padding: EdgeInsets.only(
                              bottom: profile.spacing.s8,
                            ),
                            child: Column(
                              mainAxisSize: MainAxisSize.min,
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: <Widget>[
                                Text(
                                  displayName,
                                  maxLines: 2,
                                  overflow: TextOverflow.ellipsis,
                                  style: profile.typography.heroTitle.copyWith(
                                    color: Colors.white.withValues(alpha: 0.95),
                                    height: 1.06,
                                  ),
                                ),
                                SizedBox(height: profile.spacing.s4),
                                Text(
                                  username,
                                  maxLines: 1,
                                  overflow: TextOverflow.ellipsis,
                                  style: profile.typography.meta.copyWith(
                                    color: Colors.white.withValues(alpha: 0.85),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ],
        );
      },
    );
  }
}

class _ProfileRecoveryHeroFooter extends StatelessWidget {
  const _ProfileRecoveryHeroFooter({
    required this.username,
    required this.sunSign,
    required this.moonSign,
    required this.risingSign,
  });

  final String username;
  final String sunSign;
  final String moonSign;
  final String risingSign;

  @override
  Widget build(BuildContext context) {
    final chips = <String>[
      if (username.trim().isNotEmpty) username.trim(),
      if (sunSign.trim().isNotEmpty && sunSign.trim() != '—') 'Gunes $sunSign',
      if (moonSign.trim().isNotEmpty && moonSign.trim() != '—') 'Ay $moonSign',
      if (risingSign.trim().isNotEmpty && risingSign.trim() != '—')
        'Yukselen $risingSign',
    ];
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: [
          for (var index = 0; index < chips.length; index++) ...[
            JoviaMetaPill(label: chips[index]),
            if (index != chips.length - 1) const SizedBox(width: 8),
          ],
        ],
      ),
    );
  }
}

class _ProfileIdentityHeaderCard extends StatelessWidget {
  const _ProfileIdentityHeaderCard({
    required this.displayName,
    required this.username,
    required this.avatarUrl,
    required this.isAvatarUploading,
    required this.onAvatarEdit,
    required this.dominantElementLabel,
    required this.sunSign,
    required this.moonSign,
    required this.risingSign,
    required this.stats,
  });

  final String displayName;
  final String username;
  final String? avatarUrl;
  final bool isAvatarUploading;
  final VoidCallback? onAvatarEdit;
  final String dominantElementLabel;
  final String sunSign;
  final String moonSign;
  final String risingSign;
  final List<_ProfileStatItem> stats;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return JoviaSurfaceCard(
      padding: const EdgeInsets.fromLTRB(18, 18, 18, 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'WHO AM I?',
            style: profile.typography.eyebrow.copyWith(
              color: profile.colors.textLight,
              letterSpacing: 1.6,
            ),
          ),
          const SizedBox(height: 16),
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _AvatarHalo(
                size: 82,
                imageUrl: avatarUrl,
                onEdit: onAvatarEdit,
                isUploading: isAvatarUploading,
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      displayName,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: profile.typography.heroTitle.copyWith(
                        color: profile.colors.text,
                        fontSize: 28,
                        height: 1.02,
                      ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      username,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: profile.typography.bodyCompact.copyWith(
                        color: profile.colors.textLight,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),
          _ProfileRecoveryHeroFooter(
            username: '',
            sunSign: sunSign,
            moonSign: moonSign,
            risingSign: risingSign,
          ),
          const SizedBox(height: 14),
          _ProfileStatsRow(items: stats),
          const SizedBox(height: 16),
          Text(
            dominantElementLabel,
            style: profile.typography.body.copyWith(
              color: profile.colors.text,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 16),
          const ThinDivider(),
        ],
      ),
    );
  }
}

class _ProfileIdentityQuickSection extends StatelessWidget {
  const _ProfileIdentityQuickSection({
    required this.contextData,
    required this.dominantElementLabel,
  });

  final _ProfileIdentityContext contextData;
  final String dominantElementLabel;

  String _auraTitle() {
    final normalized = dominantElementLabel.trim();
    if (normalized.isEmpty || normalized == '—') {
      return 'Kimlik tonu';
    }
    return normalized.replaceAll(
      RegExp('baskin', caseSensitive: false),
      'etkili',
    );
  }

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final cards = <Widget>[
      Expanded(
        child: _ProfileIdentityMiniCard(
          label: 'Aura',
          title: _auraTitle(),
          subtitle: contextData.auraSourceLabel,
          kind: _ProfileIdentityMiniCardKind.aura,
        ),
      ),
    ];
    if (contextData.rulerName.trim().isNotEmpty) {
      final houseLabel = contextData.rulerHouse == null
          ? ''
          : '${contextData.rulerHouse}. ev vurgusu';
      cards.add(const SizedBox(width: 12));
      cards.add(
        Expanded(
          child: _ProfileIdentityMiniCard(
            label: 'Yonetici',
            title: contextData.rulerName,
            subtitle: houseLabel,
            kind: _ProfileIdentityMiniCardKind.ruler,
          ),
        ),
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Align(
          alignment: Alignment.centerLeft,
          child: JoviaMetaPill(label: 'Kimlik ozeti'),
        ),
        if (contextData.overview.trim().isNotEmpty) ...[
          const SizedBox(height: 12),
          Padding(
            padding: const EdgeInsets.only(left: 2, right: 6),
            child: Text(
              contextData.overview,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
              style: profile.typography.bodyCompact.copyWith(
                color: profile.colors.textLight,
                height: 1.45,
              ),
            ),
          ),
        ],
        const SizedBox(height: 16),
        Row(children: cards),
      ],
    );
  }
}

enum _ProfileIdentityMiniCardKind { aura, ruler }

class _ProfileIdentityMiniCard extends StatelessWidget {
  const _ProfileIdentityMiniCard({
    required this.label,
    required this.title,
    required this.subtitle,
    required this.kind,
  });

  final String label;
  final String title;
  final String subtitle;
  final _ProfileIdentityMiniCardKind kind;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return JoviaSurfaceCard(
      radius: 24,
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 18),
      child: ConstrainedBox(
        constraints: const BoxConstraints(minHeight: 164),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _ProfileIdentityMiniArt(kind: kind),
            const SizedBox(height: 18),
            Text(
              label.toUpperCase(),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: profile.typography.eyebrow.copyWith(
                color: profile.colors.textLight,
                letterSpacing: 1.5,
              ),
            ),
            const SizedBox(height: 10),
            Text(
              title,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
              style: profile.typography.card.copyWith(
                color: profile.colors.text,
                fontWeight: FontWeight.w600,
                height: 1.06,
              ),
            ),
            if (subtitle.trim().isNotEmpty) ...[
              const SizedBox(height: 8),
              Text(
                subtitle,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: profile.typography.bodyCompact.copyWith(
                  color: profile.colors.textLight,
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _ProfileIdentityMiniArt extends StatelessWidget {
  const _ProfileIdentityMiniArt({required this.kind});

  final _ProfileIdentityMiniCardKind kind;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final astro = context.astroTheme;
    final isAura = kind == _ProfileIdentityMiniCardKind.aura;

    return Container(
      width: 58,
      height: 58,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(18),
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: isAura
              ? [
                  astro.highlight.withValues(alpha: 0.9),
                  astro.accent.withValues(alpha: 0.62),
                  Colors.white.withValues(alpha: 0.72),
                ]
              : [
                  profile.colors.surfaceCard.withValues(alpha: 0.96),
                  astro.highlight.withValues(alpha: 0.45),
                  astro.accent.withValues(alpha: 0.22),
                ],
        ),
        border: Border.all(
          color: profile.colors.strokeSoft.withValues(alpha: 0.84),
        ),
      ),
      child: Center(
        child: isAura
            ? Container(
                width: 18,
                height: 18,
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.78),
                  borderRadius: BorderRadius.circular(999),
                  boxShadow: [
                    BoxShadow(
                      blurRadius: 18,
                      color: astro.accent.withValues(alpha: 0.24),
                    ),
                  ],
                ),
              )
            : Stack(
                alignment: Alignment.center,
                children: [
                  Container(
                    width: 24,
                    height: 24,
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(8),
                      color: profile.colors.surfaceCard.withValues(alpha: 0.86),
                    ),
                  ),
                  Container(
                    width: 10,
                    height: 10,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: astro.accent.withValues(alpha: 0.92),
                    ),
                  ),
                ],
              ),
      ),
    );
  }
}

class _ProfileRecoveryReadingBody extends StatelessWidget {
  const _ProfileRecoveryReadingBody({
    required this.isLoading,
    required this.error,
    required this.summary,
    required this.supportingThreads,
    required this.primaryCards,
    required this.placementCards,
    required this.insightModules,
    required this.onOpenPlacementFlow,
    required this.readOnly,
  });

  final bool isLoading;
  final String? error;
  final String summary;
  final List<_SupportingThreadItem> supportingThreads;
  final List<_ProfileNarrativeCard> primaryCards;
  final List<_ProfileNarrativeCard> placementCards;
  final List<_ProfileInsightModule> insightModules;
  final VoidCallback? onOpenPlacementFlow;
  final bool readOnly;

  @override
  Widget build(BuildContext context) {
    final placementPreviewCards = placementCards.take(3).toList();
    final showSummaryPanel =
        isLoading ||
        (error ?? '').trim().isNotEmpty ||
        summary.trim().isNotEmpty;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        if (placementPreviewCards.isNotEmpty) ...[
          _ProfileEditorialFlow(cards: placementPreviewCards),
          if (onOpenPlacementFlow != null) ...[
            const SizedBox(height: 10),
            Align(
              alignment: Alignment.centerLeft,
              child: TextButton(
                onPressed: onOpenPlacementFlow,
                child: const Text('Daha fazla aç'),
              ),
            ),
          ],
        ],
        if (insightModules.isNotEmpty) ...[
          const SizedBox(height: 24),
          for (final module in insightModules) ...[
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 10),
              child: _ProfileInsightModuleCard(module: module),
            ),
            if (module != insightModules.last) const SizedBox(height: 18),
          ],
        ],
        if (primaryCards.isNotEmpty) ...[
          const SizedBox(height: 24),
          _ProfileEditorialFlow(cards: primaryCards),
        ],
        if (showSummaryPanel) ...[
          if (placementCards.isNotEmpty ||
              insightModules.isNotEmpty ||
              primaryCards.isNotEmpty)
            const SizedBox(height: 24),
          JoviaReadingPanel(
            label: 'Natal',
            title: 'Ana okuma',
            large: true,
            child: _ProfileRecoverySummaryBlock(
              isLoading: isLoading,
              error: error,
              summary: summary,
            ),
          ),
        ],
        if (supportingThreads.isNotEmpty) ...[
          const SizedBox(height: 24),
          JoviaReadingPanel(
            label: 'Katmanlar',
            title: 'Destekleyen izler',
            child: Column(
              children: [
                for (
                  var index = 0;
                  index < supportingThreads.length;
                  index++
                ) ...[
                  JoviaUtilityRow(
                    title: supportingThreads[index].title,
                    body: supportingThreads[index].oneLiner,
                  ),
                  if (index != supportingThreads.length - 1) ...[
                    const SizedBox(height: 10),
                    const ThinDivider(),
                    const SizedBox(height: 10),
                  ],
                ],
              ],
            ),
          ),
        ],
      ],
    );
  }
}

class _ProfileEditorialFlow extends StatelessWidget {
  const _ProfileEditorialFlow({required this.cards});

  final List<_ProfileNarrativeCard> cards;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final compact = constraints.maxWidth < 390;
        return Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            for (var index = 0; index < cards.length; index++) ...[
              Padding(
                padding: compact || index == 0
                    ? EdgeInsets.zero
                    : EdgeInsets.only(
                        left: index.isOdd ? 18 : 0,
                        right: index.isOdd ? 0 : 18,
                      ),
                child: _ProfileEditorialCard(
                  card: cards[index],
                  featured: index == 0,
                ),
              ),
              if (index != cards.length - 1)
                SizedBox(height: index == 0 ? 20 : 16),
            ],
          ],
        );
      },
    );
  }
}

class _ProfileRecoverySummaryBlock extends StatelessWidget {
  const _ProfileRecoverySummaryBlock({
    required this.isLoading,
    required this.error,
    required this.summary,
  });

  final bool isLoading;
  final String? error;
  final String summary;

  @override
  Widget build(BuildContext context) {
    if (isLoading) {
      return const Padding(
        padding: EdgeInsets.symmetric(vertical: 8),
        child: Center(child: CircularProgressIndicator()),
      );
    }
    if ((error ?? '').trim().isNotEmpty) {
      return Text(
        error!,
        style: context.profileTheme.typography.bodyCompact.copyWith(
          color: Theme.of(context).colorScheme.error,
        ),
      );
    }
    if (summary.trim().isEmpty) {
      return Text(
        'Natal okuma henuz hazir degil.',
        style: context.profileTheme.typography.bodyCompact.copyWith(
          color: context.profileTheme.colors.textLight,
        ),
      );
    }
    return Text(
      summary,
      style: context.profileTheme.typography.bodyCompact.copyWith(
        color: context.profileTheme.colors.text,
      ),
    );
  }
}

class _ProfileEditorialCard extends StatelessWidget {
  const _ProfileEditorialCard({required this.card, this.featured = false});

  final _ProfileNarrativeCard card;
  final bool featured;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return _ProfileLilacGlassCard(
      radius: featured ? 30 : 26,
      sequence: 2 + _profileAnimationSeed(card.title),
      strongerGlow: featured,
      padding: EdgeInsets.fromLTRB(
        featured ? 22 : 18,
        featured ? 22 : 18,
        featured ? 22 : 18,
        featured ? 20 : 18,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (card.eyebrow.trim().isNotEmpty) ...[
            Text(
              card.eyebrow.toUpperCase(),
              style: profile.typography.eyebrow.copyWith(
                color: Colors.white.withValues(alpha: 0.74),
                letterSpacing: 1.45,
              ),
            ),
            const SizedBox(height: 10),
          ],
          Text(
            _displayTitleForCard(card),
            style: profile.typography.card.copyWith(
              color: Colors.white,
              fontSize: featured ? 30 : 22,
              height: 1.08,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 10),
          Text(
            card.previewBody,
            maxLines: featured ? 8 : 5,
            overflow: TextOverflow.ellipsis,
            style: profile.typography.bodyCompact.copyWith(
              color: Colors.white.withValues(alpha: 0.86),
              height: 1.45,
            ),
          ),
          if (card.chips.isNotEmpty) ...[
            const SizedBox(height: 14),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                for (final chip in card.chips) JoviaMetaPill(label: chip),
              ],
            ),
          ],
        ],
      ),
    );
  }
}

class _ProfileInsightModuleCard extends StatelessWidget {
  const _ProfileInsightModuleCard({required this.module});

  final _ProfileInsightModule module;

  @override
  Widget build(BuildContext context) {
    final card = _ProfileNarrativeCard(
      cardKey: module.moduleId,
      id: module.moduleId,
      family: 'protection_pattern',
      origin: 'insight_module',
      eyebrow: module.headline,
      title: module.title,
      summary: module.subheadline,
      body: module.body,
      micro: '',
      chips: const [],
      astroSources: const [],
    );
    return _ProfileEditorialCard(card: card);
  }
}

String _displayTitleForCard(_ProfileNarrativeCard card) {
  if (card.origin == 'personality_imprint') {
    return _legacySignalLineForCard(card);
  }
  return card.title;
}

String _signatureEyebrowForCard(_ProfileNarrativeCard card) {
  final title = card.title.trim();
  if (RegExp(r'^.+?\s+\d+\.\s*Ev$', caseSensitive: false).hasMatch(title)) {
    return 'Yerleşim';
  }
  if (card.family == 'contradiction_core') {
    return 'Açı';
  }
  if (card.family == 'tone_signature') {
    return 'Burç tonu';
  }
  return 'Öne çıkan tema';
}

String _legacySignalLineForCard(_ProfileNarrativeCard card) {
  final title = card.title.trim();
  if (title.isEmpty) {
    return title;
  }
  final houseMatch = RegExp(
    r'^(.+?)\s+(\d+)\.\s*Ev$',
    caseSensitive: false,
  ).firstMatch(title);
  if (houseMatch != null) {
    return '${houseMatch.group(1)} ${houseMatch.group(2)}. evde';
  }
  final signMatch = RegExp(
    r'^(.+?)\s+(Koç|Boğa|İkizler|Yengeç|Aslan|Başak|Terazi|Akrep|Yay|Oğlak|Kova|Balık)$',
    caseSensitive: false,
  ).firstMatch(title);
  if (signMatch != null) {
    return '${signMatch.group(1)} ${signMatch.group(2)} burcunda';
  }
  return title;
}

class _FloatingTile extends StatelessWidget {
  const _FloatingTile({
    required this.width,
    required this.height,
    required this.radius,
    required this.rotationDeg,
    required this.fill,
    required this.stroke,
  });

  final double width;
  final double height;
  final double radius;
  final double rotationDeg;
  final Color fill;
  final Color stroke;

  @override
  Widget build(BuildContext context) {
    return Transform.rotate(
      angle: rotationDeg * 3.1415926535 / 180.0,
      child: ClipRRect(
        borderRadius: BorderRadius.circular(radius),
        child: Container(
          width: width,
          height: height,
          decoration: BoxDecoration(
            color: fill,
            border: Border.all(color: stroke, width: 1),
            boxShadow: <BoxShadow>[
              BoxShadow(
                blurRadius: 18,
                offset: const Offset(0, 10),
                color: Colors.black.withValues(alpha: 0.12),
              ),
            ],
          ),
          child: Stack(
            fit: StackFit.expand,
            children: <Widget>[
              DecoratedBox(
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: <Color>[
                      Colors.white.withValues(alpha: 0.18),
                      Colors.transparent,
                      Colors.black.withValues(alpha: 0.06),
                    ],
                  ),
                ),
              ),
              Positioned(
                left: 16,
                right: 16,
                bottom: 16,
                child: Container(
                  height: 10,
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.18),
                    borderRadius: BorderRadius.circular(999),
                  ),
                ),
              ),
              Positioned(
                right: 14,
                top: 14,
                child: Container(
                  width: 18,
                  height: 18,
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.14),
                    shape: BoxShape.circle,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _EditorialDivider extends StatelessWidget {
  const _EditorialDivider();

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Padding(
      padding: EdgeInsets.symmetric(vertical: profile.spacing.s12),
      child: Row(
        children: <Widget>[
          Expanded(
            child: Container(height: 1, color: profile.colors.strokeDivider),
          ),
          SizedBox(width: profile.spacing.s12),
          Text(
            '✦',
            style: profile.typography.meta.copyWith(
              fontSize: 16,
              fontWeight: FontWeight.w700,
              color: profile.colors.brandPurple.withValues(alpha: 0.6),
            ),
          ),
          SizedBox(width: profile.spacing.s12),
          Expanded(
            child: Container(height: 1, color: profile.colors.strokeDivider),
          ),
        ],
      ),
    );
  }
}

class _CardShell extends StatelessWidget {
  const _CardShell({required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Container(
      padding: EdgeInsets.all(profile.spacing.s16),
      decoration: BoxDecoration(
        color: profile.colors.panelStrong,
        borderRadius: BorderRadius.circular(22),
        border: Border.all(color: profile.colors.strokeSoft, width: 1.15),
        boxShadow: <BoxShadow>[
          BoxShadow(
            blurRadius: 14,
            offset: const Offset(0, 8),
            color: Colors.black.withValues(alpha: 0.09),
            spreadRadius: -12,
          ),
        ],
      ),
      child: child,
    );
  }
}

class _HeaderActionButton extends StatelessWidget {
  const _HeaderActionButton({
    required this.icon,
    required this.onTap,
    this.sceneStyle = false,
  });

  final IconData icon;
  final VoidCallback onTap;
  final bool sceneStyle;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Padding(
      padding: EdgeInsets.only(left: profile.spacing.xs),
      child: Material(
        color: sceneStyle
            ? profile.colors.surface
            : profile.colors.buttonSecondary,
        borderRadius: BorderRadius.circular(14),
        child: InkWell(
          borderRadius: BorderRadius.circular(14),
          onTap: onTap,
          child: Container(
            width: 38,
            height: 38,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(14),
              border: Border.all(
                color: sceneStyle
                    ? profile.colors.primary.withValues(alpha: 0.18)
                    : profile.colors.strokeSoft,
                width: 1,
              ),
            ),
            child: Icon(
              icon,
              size: 18,
              color: sceneStyle ? profile.colors.primary : profile.colors.text,
            ),
          ),
        ),
      ),
    );
  }
}

class _AvatarHalo extends StatelessWidget {
  const _AvatarHalo({
    required this.size,
    this.imageUrl,
    this.onEdit,
    this.isUploading = false,
    this.heroStyle = false,
  });

  final double size;
  final String? imageUrl;
  final VoidCallback? onEdit;
  final bool isUploading;
  final bool heroStyle;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return SizedBox(
      width: size,
      height: size,
      child: Stack(
        alignment: Alignment.center,
        children: [
          Container(
            width: size,
            height: size,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: heroStyle
                  ? Colors.white.withValues(alpha: 0.18)
                  : profile.colors.lavender.withValues(alpha: 0.26),
              boxShadow: [profile.shadows.floatingShadow],
            ),
          ),
          Container(
            width: size * 0.76,
            height: size * 0.76,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: heroStyle
                  ? Colors.white.withValues(alpha: 0.96)
                  : profile.colors.surface,
              border: Border.all(
                color: heroStyle
                    ? Colors.white.withValues(alpha: 0.45)
                    : profile.colors.separator,
                width: heroStyle ? 1 : 1.5,
              ),
            ),
            alignment: Alignment.center,
            child: ClipOval(
              child: SizedBox.expand(
                child: (imageUrl ?? '').trim().isEmpty
                    ? Icon(
                        Icons.person_rounded,
                        size: size * 0.36,
                        color: heroStyle
                            ? profile.colors.primary
                            : profile.colors.primary.withValues(alpha: 0.78),
                      )
                    : Image.network(
                        imageUrl!,
                        fit: BoxFit.cover,
                        errorBuilder: (_, _, _) => Icon(
                          Icons.person_rounded,
                          size: size * 0.36,
                          color: heroStyle
                              ? profile.colors.primary
                              : profile.colors.primary.withValues(alpha: 0.78),
                        ),
                      ),
              ),
            ),
          ),
          if (isUploading)
            SizedBox(
              width: size * 0.28,
              height: size * 0.28,
              child: const CircularProgressIndicator(strokeWidth: 2),
            ),
          if (onEdit != null)
            Positioned(
              right: 0,
              bottom: 0,
              child: InkWell(
                onTap: onEdit,
                borderRadius: BorderRadius.circular(99),
                child: Container(
                  width: size * 0.28,
                  height: size * 0.28,
                  decoration: BoxDecoration(
                    color: profile.colors.primary,
                    shape: BoxShape.circle,
                    border: Border.all(
                      color: profile.colors.surface,
                      width: 1.5,
                    ),
                  ),
                  child: Icon(
                    Icons.edit_outlined,
                    size: size * 0.14,
                    color: Colors.white,
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }
}

class _ProfileTabBar extends StatelessWidget {
  const _ProfileTabBar({required this.currentIndex, required this.onChanged});

  final int currentIndex;
  final ValueChanged<int> onChanged;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final labels = const <String>['Natal', 'Timing'];
    return Row(
      children: [
        for (var index = 0; index < labels.length; index++)
          Expanded(
            child: InkWell(
              onTap: () => onChanged(index),
              borderRadius: BorderRadius.circular(14),
              child: Padding(
                padding: const EdgeInsets.symmetric(vertical: 12),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      labels[index],
                      style: profile.typography.body.copyWith(
                        fontWeight: FontWeight.w700,
                        color: currentIndex == index
                            ? profile.colors.primary
                            : profile.colors.textLight,
                      ),
                    ),
                    const SizedBox(height: 8),
                    AnimatedContainer(
                      duration: const Duration(milliseconds: 180),
                      height: 2,
                      width: 42,
                      decoration: BoxDecoration(
                        color: currentIndex == index
                            ? profile.colors.primary
                            : Colors.transparent,
                        borderRadius: BorderRadius.circular(999),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
      ],
    );
  }
}

class _ProfileStatItem {
  const _ProfileStatItem({required this.value, required this.label});

  final String value;
  final String label;
}

class _ProfileStatsRow extends StatelessWidget {
  const _ProfileStatsRow({required this.items});

  final List<_ProfileStatItem> items;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Row(
      children: [
        for (var index = 0; index < items.length; index++) ...[
          Expanded(child: _StatCell(item: items[index])),
          if (index != items.length - 1)
            Container(width: 1, height: 32, color: profile.colors.separator),
        ],
      ],
    );
  }
}

class _StatCell extends StatelessWidget {
  const _StatCell({required this.item});

  final _ProfileStatItem item;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(
          item.value,
          style: profile.typography.card.copyWith(
            fontWeight: FontWeight.w600,
            color: profile.colors.text,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          item.label,
          style: profile.typography.meta.copyWith(
            color: profile.colors.textLight,
          ),
        ),
      ],
    );
  }
}

class _GlassCard extends StatelessWidget {
  const _GlassCard({required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context) {
    return _CardShell(child: child);
  }
}
