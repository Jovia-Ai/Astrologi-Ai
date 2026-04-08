import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import 'package:mobile/app/api/api_client.dart';
import 'package:mobile/app/people/add_person_page.dart';
import 'package:mobile/app/people/people_providers.dart';
import 'package:mobile/app/people/people_repository.dart';
import 'package:mobile/app/people/person_profile.dart';
import 'package:mobile/app/profile/profile_providers.dart';
import 'package:mobile/app/tabs/bond_models.dart';
import 'package:mobile/app/tabs/bond_result_page.dart';
import 'package:mobile/app/timing/turkish_text.dart';
import 'package:mobile/design/theme/profile_theme_extension.dart';
import 'package:mobile/design/widgets/jovia_editorial.dart';

class BondPage extends ConsumerStatefulWidget {
  const BondPage({super.key});

  @override
  ConsumerState<BondPage> createState() => _BondPageState();
}

class _BondPageState extends ConsumerState<BondPage> {
  _BondSelection _primarySelection = const _BondSelection.self();
  _BondSelection? _secondarySelection;
  BondType _bondType = BondType.romantic;
  bool _loading = false;

  @override
  Widget build(BuildContext context) {
    final profileAsync = ref.watch(userProfileProvider);
    final profile = profileAsync.valueOrNull;
    final profileLoaded = profileAsync.hasValue;
    final displayProfile = _displayProfile(profile);
    final selfBirthDataMissing =
        profileLoaded && _primarySelection.isSelf && !_hasBirthData(profile);

    final canViewBond =
        !_loading &&
        _hasSelectionBirthData(_primarySelection, profile) &&
        _hasSelectionBirthData(_secondarySelection, profile);
    final themed = withProfileTheme(Theme.of(context));

    return Theme(
      data: themed,
      child: Builder(
        builder: (context) {
          final spacing = context.profileTheme.spacing;
          final palette = _BondReferencePalette.of(context);
          final authAvatarUrl = _authAvatarUrl();
          return Scaffold(
            backgroundColor: palette.canvas,
            body: DecoratedBox(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [palette.canvas, palette.canvas, palette.lowerGlow],
                  stops: const [0, 0.64, 1],
                ),
              ),
              child: JoviaPageScaffold(
                child: ListView(
                  padding: EdgeInsets.zero,
                  children: [
                    JoviaReveal(
                      child: JoviaProfileTopBar(
                        label: 'Bond',
                        centerText: _selectionDisplayName(
                          _secondarySelection,
                          displayProfile,
                          fallback: 'iliski lensi',
                        ),
                        onActionTap: () => _openPersonPicker(
                          _BondSlot.secondary,
                          displayProfile,
                        ),
                        actionAsset: JoviaUiAsset.plusCrosshair,
                        actionTooltip: 'Kisi sec',
                      ),
                    ),
                    SizedBox(height: spacing.s24),
                    JoviaReveal(
                      delay: const Duration(milliseconds: 20),
                      child: const _BondReferenceHero(
                        title: 'Aranızdaki uyumu gör',
                        body:
                            'İki kişiyi seç, uyumu tek bir ilişki lensiyle daha net ve daha sakin bir yüzeyden oku.',
                      ),
                    ),
                    SizedBox(height: spacing.s20),
                    JoviaReveal(
                      delay: const Duration(milliseconds: 100),
                      child: _BondPairSelectorCard(
                        primaryName: _selectionDisplayName(
                          _primarySelection,
                          displayProfile,
                        ),
                        primaryLabel: _selectionDisplayName(
                          _primarySelection,
                          displayProfile,
                        ),
                        secondaryName: _selectionDisplayName(
                          _secondarySelection,
                          displayProfile,
                        ),
                        secondaryLabel: _selectionDisplayName(
                          _secondarySelection,
                          displayProfile,
                        ),
                        selfAvatarUrl:
                            !_primarySelection.isSelf || authAvatarUrl.isEmpty
                            ? null
                            : authAvatarUrl,
                        onPrimaryTap: () => _openPersonPicker(
                          _BondSlot.primary,
                          displayProfile,
                        ),
                        onSecondaryTap: () => _openPersonPicker(
                          _BondSlot.secondary,
                          displayProfile,
                        ),
                        footer: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'LENS',
                              style: context.profileTheme.typography.eyebrow
                                  .copyWith(color: palette.softText),
                            ),
                            const SizedBox(height: 8),
                            _BondLensSelector(
                              value: _bondType,
                              options: BondType.values,
                              labelBuilder: (value) => value.label,
                              onChanged: (value) =>
                                  setState(() => _bondType = value),
                            ),
                          ],
                        ),
                      ),
                    ),
                    if (selfBirthDataMissing) ...[
                      SizedBox(height: spacing.s24),
                      JoviaReveal(
                        delay: const Duration(milliseconds: 120),
                        child: const _BondReferenceDashedPanel(
                          child: EmptyStateBlock(
                            title: 'Dogum verisi eksik',
                            body:
                                'Bond analizi icin once kendi dogum tarihi, saati ve yer bilginin dolu olmasi gerekiyor.',
                            framed: false,
                          ),
                        ),
                      ),
                    ],
                    SizedBox(height: spacing.s40),
                    JoviaReveal(
                      delay: const Duration(milliseconds: 150),
                      child: Column(
                        children: [
                          JoviaDividerAsset(
                            kind: JoviaDividerVariant.bondSectionBreak.kind,
                            width: JoviaDividerVariant
                                .bondSectionBreak
                                .defaultWidth,
                            color: palette.rule,
                            opacity: 0.58,
                          ),
                          SizedBox(height: spacing.s24),
                          _BondCtaDoorway(
                            label: _loading
                                ? 'Hazirlaniyor...'
                                : 'Bond sonucunu ac',
                            enabled: canViewBond,
                            isBusy: _loading,
                            onTap: canViewBond
                                ? () => _viewBond(profile!)
                                : null,
                          ),
                        ],
                      ),
                    ),
                    SizedBox(height: spacing.s32),
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  Future<void> _openPersonPicker(
    _BondSlot slot,
    Map<String, dynamic>? profile,
  ) async {
    final selected = await showModalBottomSheet<_BondSelection>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (sheetContext) {
        return _PeoplePickerSheet(
          selfName: _userName(profile),
          onSelection: (selection) => Navigator.of(sheetContext).pop(selection),
        );
      },
    );

    if (selected == null) {
      return;
    }

    setState(() {
      if (slot == _BondSlot.primary) {
        _primarySelection = selected;
      } else {
        _secondarySelection = selected;
      }
    });
  }

  Future<void> _viewBond(Map<String, dynamic> myProfile) async {
    final secondary = _secondarySelection;
    if (secondary == null) {
      return;
    }

    setState(() => _loading = true);

    final payload = <String, dynamic>{
      'partner_a': _selectionPayload(_primarySelection, myProfile),
      'partner_b': _selectionPayload(secondary, myProfile),
      'options': {
        'include_debug': false,
        'bond_type': _bondType.backendValue,
        'relationship_type': _bondType.backendValue,
      },
    };

    try {
      final client = ApiClient();
      Response<dynamic> response;

      try {
        response = await client.post(
          '/api/v1/relationship/synastry/analyze',
          data: payload,
        );
      } on DioException catch (error) {
        final code = error.response?.statusCode;
        if (code == 404 || code == 405) {
          response = await client.post('/api/synastry/analyze', data: payload);
        } else {
          rethrow;
        }
      }

      if (!mounted) {
        return;
      }

      final data = _asMap(response.data);
      await Navigator.of(context).push(
        MaterialPageRoute<void>(
          builder: (_) => BondResultPage(
            response: data,
            youName: _selectionDisplayName(_primarySelection, myProfile),
            partnerName: _selectionDisplayName(secondary, myProfile),
            bondType: _bondType,
            partnerPersonId: secondary.person?.id,
          ),
        ),
      );
    } catch (error) {
      if (!mounted) {
        return;
      }
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Bond analizi alınamadı: $error')));
    } finally {
      if (mounted) {
        setState(() => _loading = false);
      }
    }
  }

  bool _hasBirthData(Map<String, dynamic>? profile) {
    if (profile == null) {
      return false;
    }
    final birthDate = (profile['birth_date'] ?? '').toString().trim();
    final place = _resolvePlace(profile);
    return birthDate.isNotEmpty && place.isNotEmpty;
  }

  bool _hasSelectionBirthData(
    _BondSelection? selection,
    Map<String, dynamic>? profile,
  ) {
    if (selection == null) {
      return false;
    }
    if (selection.isSelf) {
      return _hasBirthData(profile);
    }
    final person = selection.person;
    if (person == null) {
      return false;
    }
    return person.birthDate.trim().isNotEmpty && person.place.trim().isNotEmpty;
  }

  Map<String, dynamic>? _displayProfile(Map<String, dynamic>? profile) {
    final authName = _authDisplayName();
    final authAvatarUrl = _authAvatarUrl();
    if (profile == null) {
      if (authName.isEmpty && authAvatarUrl.isEmpty) {
        return null;
      }
      return <String, dynamic>{
        if (authName.isNotEmpty) 'full_name': authName,
        if (authAvatarUrl.isNotEmpty) 'avatar_url': authAvatarUrl,
      };
    }

    return <String, dynamic>{
      ...profile,
      if (((profile['full_name'] ?? profile['name'] ?? '').toString().trim())
              .isEmpty &&
          authName.isNotEmpty)
        'full_name': authName,
      if ((profile['avatar_url'] ?? '').toString().trim().isEmpty &&
          authAvatarUrl.isNotEmpty)
        'avatar_url': authAvatarUrl,
    };
  }

  String _authDisplayName() {
    final metadata = Supabase.instance.client.auth.currentUser?.userMetadata;
    final fullName = (metadata?['full_name'] ?? metadata?['name'] ?? '')
        .toString()
        .trim();
    if (fullName.isNotEmpty) {
      return fullName;
    }
    return '';
  }

  String _authAvatarUrl() {
    return Supabase
            .instance
            .client
            .auth
            .currentUser
            ?.userMetadata?['avatar_url']
            ?.toString()
            .trim() ??
        '';
  }

  String _userName(Map<String, dynamic>? profile) {
    final user = Supabase.instance.client.auth.currentUser;
    final metadata = user?.userMetadata ?? const <String, dynamic>{};
    final first = _cleanHumanName(
      (metadata['first_name'] ?? metadata['firstName'] ?? '').toString(),
    );
    final last = _cleanHumanName(
      (metadata['last_name'] ?? metadata['lastName'] ?? '').toString(),
    );
    final candidates = <String>[
      (profile?['full_name'] ?? '').toString(),
      (profile?['display_name'] ?? profile?['displayName'] ?? '').toString(),
      (profile?['name'] ?? '').toString(),
      (metadata['full_name'] ?? metadata['fullName'] ?? '').toString(),
      (metadata['display_name'] ?? metadata['displayName'] ?? '').toString(),
      (metadata['name'] ?? '').toString(),
      if (first.isNotEmpty || last.isNotEmpty) '$first $last'.trim(),
    ];
    for (final candidate in candidates) {
      final cleaned = _cleanHumanName(candidate);
      if (cleaned.isNotEmpty) {
        return cleaned;
      }
    }
    return 'Sen';
  }

  bool _looksLikeSystemHandle(String value) {
    final trimmed = value.trim();
    if (trimmed.isEmpty) {
      return false;
    }
    if (trimmed.contains('@')) {
      return true;
    }
    return !trimmed.contains(' ') &&
        (RegExp(r'[0-9]').hasMatch(trimmed) ||
            trimmed.contains('_') ||
            trimmed.contains('.'));
  }

  String _cleanHumanName(String raw) {
    final trimmed = raw.trim();
    if (trimmed.isEmpty || _looksLikeSystemHandle(trimmed)) {
      return '';
    }
    return trimmed;
  }

  String _selectionDisplayName(
    _BondSelection? selection,
    Map<String, dynamic>? profile, {
    String fallback = 'Kisi sec',
  }) {
    if (selection == null) {
      return fallback;
    }
    if (selection.isSelf) {
      final name = _userName(profile).trim();
      return name.isEmpty ? fallback : name;
    }
    final name = selection.person?.name.trim() ?? '';
    return name.isEmpty ? fallback : name;
  }

  Map<String, dynamic> _selectionPayload(
    _BondSelection selection,
    Map<String, dynamic> myProfile,
  ) {
    if (selection.isSelf) {
      return <String, dynamic>{
        'name': _userName(myProfile),
        'birthDate': (myProfile['birth_date'] ?? '').toString().trim(),
        'birthTime': _normalizeBirthTime(
          (myProfile['birth_time'] ?? '').toString(),
        ),
        'birthPlace': _resolvePlace(myProfile),
      };
    }
    final person = selection.person!;
    return <String, dynamic>{
      'name': person.name,
      'birthDate': person.birthDate,
      'birthTime': person.normalizedBirthTime,
      'birthPlace': person.place,
    };
  }

  String _resolvePlace(Map<String, dynamic> profile) {
    final placeRaw = (profile['place'] ?? '').toString().trim();
    if (placeRaw.isNotEmpty) {
      return placeRaw;
    }
    final city = (profile['city'] ?? '').toString().trim();
    final country = (profile['country'] ?? '').toString().trim();
    if (city.isEmpty) {
      return country;
    }
    if (country.isEmpty) {
      return city;
    }
    return '$city, $country';
  }

  String _normalizeBirthTime(String raw) {
    final value = raw.trim();
    if (value.isEmpty) {
      return '12:00';
    }
    if (value.length >= 5) {
      return value.substring(0, 5);
    }
    return value;
  }

  Map<String, dynamic> _asMap(dynamic raw) {
    if (raw is Map<String, dynamic>) {
      return raw;
    }
    if (raw is Map) {
      return Map<String, dynamic>.from(raw);
    }
    return <String, dynamic>{};
  }
}

class _PeoplePickerSheet extends ConsumerWidget {
  const _PeoplePickerSheet({required this.selfName, required this.onSelection});

  final String selfName;
  final ValueChanged<_BondSelection> onSelection;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final peopleAsync = ref.watch(peopleListProvider);
    final profile = context.profileTheme;
    final palette = _BondReferencePalette.of(context);

    return Padding(
      padding: EdgeInsets.fromLTRB(
        profile.spacing.lg,
        profile.spacing.lg,
        profile.spacing.lg,
        profile.spacing.lg,
      ),
      child: _BondReferenceDashedPanel(
        fillColor: palette.sheetFill,
        borderColor: palette.edge,
        child: SafeArea(
          top: false,
          child: SizedBox(
            height: MediaQuery.of(context).size.height * 0.65,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SectionLabel(
                  label: 'Arkadaslarim',
                  title: 'Bond icin bir kisi sec',
                ),
                SizedBox(height: profile.spacing.sm),
                Align(
                  alignment: Alignment.centerLeft,
                  child: MinimalCTAButton(
                    label: '+ Kisi ekle',
                    glassy: true,
                    onTap: () async {
                      final created = await Navigator.of(context).push<bool>(
                        MaterialPageRoute<bool>(
                          builder: (_) => const AddPersonPage(),
                        ),
                      );
                      if (created == true) {
                        ref.invalidate(peopleListProvider);
                      }
                    },
                  ),
                ),
                SizedBox(height: profile.spacing.sm),
                Expanded(
                  child: peopleAsync.when(
                    data: (items) {
                      return ListView.separated(
                        itemCount: items.length + 1,
                        separatorBuilder: (_, _) => const ThinDivider(),
                        itemBuilder: (_, index) {
                          if (index == 0) {
                            return EditorialListItem(
                              title: selfName,
                              body: 'Kendi profilin',
                              meta: const <String>['Ben'],
                              onTap: () =>
                                  onSelection(const _BondSelection.self()),
                              trailing: JoviaUiIcon(
                                asset: JoviaUiAsset.chevronRight,
                                color: profile.colors.primary,
                                size: 16,
                              ),
                            );
                          }
                          final person = items[index - 1];
                          return EditorialListItem(
                            title: person.name,
                            body:
                                '${person.birthDate} • ${person.normalizedBirthTime}',
                            meta: <String>[person.place],
                            onTap: () =>
                                onSelection(_BondSelection.person(person)),
                            trailing: JoviaUiIcon(
                              asset: JoviaUiAsset.chevronRight,
                              color: profile.colors.primary,
                              size: 16,
                            ),
                          );
                        },
                      );
                    },
                    loading: () =>
                        const Center(child: CircularProgressIndicator()),
                    error: (error, _) {
                      WidgetsBinding.instance.addPostFrameCallback((_) {
                        if (!context.mounted) {
                          return;
                        }
                        final msg = error is PeopleQueryException
                            ? error.userMessage
                            : 'Arkadaslar yuklenemedi: $error';
                        ScaffoldMessenger.of(
                          context,
                        ).showSnackBar(SnackBar(content: Text(msg)));
                      });
                      return Center(
                        child: Text(
                          error is PeopleQueryException
                              ? error.userMessage
                              : 'Arkadaslar yuklenemedi: $error',
                          textAlign: TextAlign.center,
                        ),
                      );
                    },
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

enum _BondSlot { primary, secondary }

class _BondSelection {
  const _BondSelection.self() : isSelf = true, person = null;

  const _BondSelection.person(this.person) : isSelf = false;

  final bool isSelf;
  final PersonProfile? person;
}

class _BondPairSelectorCard extends StatelessWidget {
  const _BondPairSelectorCard({
    required this.primaryName,
    required this.primaryLabel,
    required this.secondaryName,
    required this.secondaryLabel,
    required this.onPrimaryTap,
    required this.onSecondaryTap,
    this.selfAvatarUrl,
    this.footer,
  });

  final String primaryName;
  final String primaryLabel;
  final String secondaryName;
  final String secondaryLabel;
  final VoidCallback onPrimaryTap;
  final VoidCallback onSecondaryTap;
  final String? selfAvatarUrl;
  final Widget? footer;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final spacing = profile.spacing;
    final palette = _BondReferencePalette.of(context);
    return _BondReferenceDashedPanel(
      fillColor: palette.sheetFill,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(
            'KARŞILAŞTIRMA',
            style: profile.typography.eyebrow.copyWith(color: palette.softText),
          ),
          const SizedBox(height: 10),
          Text(
            'İki kişi',
            style: profile.typography.sectionTitle.copyWith(
              color: palette.text,
              fontSize: 22,
              height: 1.08,
            ),
          ),
          const SizedBox(height: 10),
          Text(
            'Karşılaştırmayı tek bir ilişki lensiyle aç.',
            style: profile.typography.bodyCompact.copyWith(
              color: palette.mutedText,
              fontSize: 15,
              height: 1.48,
            ),
          ),
          SizedBox(height: spacing.s20),
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: _BondProfileChooser(
                  name: primaryName,
                  label: primaryLabel,
                  imageUrl: selfAvatarUrl,
                  icon: JoviaUiAsset.profileComet,
                  onTap: onPrimaryTap,
                ),
              ),
              Padding(
                padding: EdgeInsets.only(top: spacing.s32 + 2),
                child: Text(
                  '&',
                  style: profile.typography.pageTitle.copyWith(
                    color: palette.text,
                    fontSize: 32,
                    height: 36 / 32,
                    fontWeight: FontWeight.w500,
                    letterSpacing: -0.6,
                  ),
                ),
              ),
              Expanded(
                child: _BondProfileChooser(
                  name: secondaryName,
                  label: secondaryLabel,
                  icon: JoviaUiAsset.heartOrbit,
                  onTap: onSecondaryTap,
                ),
              ),
            ],
          ),
          if (footer != null) ...[
            SizedBox(height: spacing.sectionToContent),
            Divider(color: palette.rule.withValues(alpha: 0.62), height: 1),
            SizedBox(height: spacing.sectionToContent),
            footer!,
          ],
        ],
      ),
    );
  }
}

class _BondProfileChooser extends StatelessWidget {
  const _BondProfileChooser({
    required this.name,
    required this.label,
    required this.icon,
    required this.onTap,
    this.imageUrl,
  });

  final String name;
  final String label;
  final JoviaUiAsset icon;
  final VoidCallback onTap;
  final String? imageUrl;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        _BondAvatarCircle(
          imageUrl: imageUrl,
          icon: icon,
          name: name,
          onTap: onTap,
        ),
        SizedBox(height: profile.spacing.s12),
        _BondSelectPill(label: label, onTap: onTap, showChevron: true),
      ],
    );
  }
}

class _BondLensSelector extends StatelessWidget {
  const _BondLensSelector({
    required this.value,
    required this.options,
    required this.labelBuilder,
    required this.onChanged,
  });

  final BondType value;
  final List<BondType> options;
  final String Function(BondType value) labelBuilder;
  final ValueChanged<BondType> onChanged;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final palette = _BondReferencePalette.of(context);
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final trackColor = isDark
        ? const Color(0xFF120E0D)
        : Color.alphaBlend(
            profile.colors.primary.withValues(alpha: 0.06),
            palette.softFill,
          );

    return Container(
      padding: const EdgeInsets.all(4),
      decoration: BoxDecoration(
        color: trackColor,
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: palette.edge.withValues(alpha: 0.86)),
        boxShadow: [
          BoxShadow(
            color: palette.shadow.withValues(alpha: isDark ? 0.12 : 0.08),
            blurRadius: 16,
            offset: const Offset(0, 8),
            spreadRadius: -14,
          ),
        ],
      ),
      child: Row(
        children: [
          for (final option in options)
            Expanded(
              child: _BondLensSelectorOption(
                label: labelBuilder(option),
                selected: option == value,
                onTap: () => onChanged(option),
              ),
            ),
        ],
      ),
    );
  }
}

class _BondLensSelectorOption extends StatelessWidget {
  const _BondLensSelectorOption({
    required this.label,
    required this.selected,
    required this.onTap,
  });

  final String label;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final palette = _BondReferencePalette.of(context);
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final activeFill = isDark
        ? Color.alphaBlend(
            palette.edge.withValues(alpha: 0.18),
            const Color(0xFF261B17),
          )
        : Color.alphaBlend(
            Colors.white.withValues(alpha: 0.82),
            profile.colors.primary.withValues(alpha: 0.18),
          );
    final activeBorder = isDark
        ? palette.edge.withValues(alpha: 0.92)
        : profile.colors.primary.withValues(alpha: 0.4);

    return JoviaPressable(
      onTap: onTap,
      borderRadius: BorderRadius.circular(999),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 180),
        curve: Curves.easeOutCubic,
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
        decoration: BoxDecoration(
          color: selected ? activeFill : Colors.transparent,
          borderRadius: BorderRadius.circular(999),
          border: Border.all(
            color: selected ? activeBorder : Colors.transparent,
          ),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              label,
              textAlign: TextAlign.center,
              style: profile.typography.buttonLabel.copyWith(
                color: selected ? palette.text : palette.softText,
                fontWeight: selected ? FontWeight.w800 : FontWeight.w600,
                letterSpacing: selected ? -0.18 : -0.08,
              ),
            ),
            const SizedBox(height: 5),
            AnimatedContainer(
              duration: const Duration(milliseconds: 180),
              curve: Curves.easeOutCubic,
              width: selected ? 18 : 0,
              height: 2,
              decoration: BoxDecoration(
                color: selected
                    ? (isDark
                          ? const Color(0xFFF3D4B6)
                          : profile.colors.primary)
                    : Colors.transparent,
                borderRadius: BorderRadius.circular(999),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _BondAvatarCircle extends StatelessWidget {
  const _BondAvatarCircle({
    required this.icon,
    required this.name,
    required this.onTap,
    this.imageUrl,
  });

  final JoviaUiAsset icon;
  final String name;
  final VoidCallback onTap;
  final String? imageUrl;

  @override
  Widget build(BuildContext context) {
    final palette = _BondReferencePalette.of(context);
    final content = Container(
      width: 92,
      height: 92,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: palette.avatarFill,
        border: Border.all(
          color: palette.edge.withValues(alpha: 0.92),
          width: 1.5,
        ),
        boxShadow: [
          BoxShadow(
            color: palette.shadow.withValues(alpha: 0.1),
            blurRadius: 26,
            offset: const Offset(0, 14),
          ),
        ],
      ),
      child: ClipOval(
        child: ColoredBox(
          color: palette.avatarInset,
          child: (imageUrl ?? '').trim().isEmpty
              ? Center(
                  child: _BondAvatarFallback(name: name, icon: icon),
                )
              : Image.network(
                  imageUrl!,
                  fit: BoxFit.cover,
                  errorBuilder: (_, _, _) => Center(
                    child: _BondAvatarFallback(name: name, icon: icon),
                  ),
                ),
        ),
      ),
    );

    return JoviaPressable(
      onTap: onTap,
      borderRadius: BorderRadius.circular(46),
      child: content,
    );
  }
}

class _BondSelectPill extends StatelessWidget {
  const _BondSelectPill({
    required this.label,
    required this.showChevron,
    this.onTap,
  });

  final String label;
  final bool showChevron;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final palette = _BondReferencePalette.of(context);
    final child = Container(
      constraints: const BoxConstraints(minHeight: 48),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: palette.softFill,
        borderRadius: BorderRadius.circular(profile.radii.cardRadius),
        border: Border.all(color: palette.edge.withValues(alpha: 0.88)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Flexible(
            child: Text(
              label,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: profile.typography.bodyCompact.copyWith(
                color: palette.text,
                fontSize: 15,
                height: 20 / 15,
                fontWeight: FontWeight.w500,
                letterSpacing: -0.14,
              ),
            ),
          ),
          if (showChevron) ...[
            const SizedBox(width: 8),
            JoviaUiIcon(
              asset: JoviaUiAsset.chevronRight,
              color: palette.softText,
              size: 14,
            ),
          ],
        ],
      ),
    );

    if (onTap == null) {
      return child;
    }

    return JoviaPressable(
      onTap: onTap,
      borderRadius: BorderRadius.circular(profile.radii.cardRadius),
      child: child,
    );
  }
}

class _BondAvatarFallback extends StatelessWidget {
  const _BondAvatarFallback({required this.name, required this.icon});

  final String name;
  final JoviaUiAsset icon;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final palette = _BondReferencePalette.of(context);
    final initials = _initials(name);
    if (initials.isEmpty || _isPlaceholder(name)) {
      return JoviaUiIcon(asset: icon, size: 34, color: palette.softText);
    }
    return Text(
      initials,
      style: profile.typography.pageTitle.copyWith(
        color: palette.text,
        fontSize: 28,
        height: 30 / 28,
        fontWeight: FontWeight.w600,
        letterSpacing: -0.4,
      ),
    );
  }

  static String _initials(String value) {
    final parts = value
        .trim()
        .split(RegExp(r'\s+'))
        .where((part) => part.isNotEmpty)
        .toList();
    if (parts.isEmpty) {
      return '';
    }
    final first = parts.first.substring(0, 1);
    final second = parts.length > 1 ? parts.last.substring(0, 1) : '';
    return turkishToUpper(first + second);
  }

  static bool _isPlaceholder(String value) {
    final normalized = value.trim().toLowerCase();
    return normalized.isEmpty || normalized == 'kisi sec';
  }
}

class _BondReferencePalette {
  const _BondReferencePalette({
    required this.canvas,
    required this.lowerGlow,
    required this.panelFill,
    required this.sheetFill,
    required this.softFill,
    required this.avatarFill,
    required this.avatarInset,
    required this.edge,
    required this.rule,
    required this.text,
    required this.mutedText,
    required this.softText,
    required this.shadow,
  });

  final Color canvas;
  final Color lowerGlow;
  final Color panelFill;
  final Color sheetFill;
  final Color softFill;
  final Color avatarFill;
  final Color avatarInset;
  final Color edge;
  final Color rule;
  final Color text;
  final Color mutedText;
  final Color softText;
  final Color shadow;

  static _BondReferencePalette of(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final profile = context.profileTheme;
    return isDark
        ? const _BondReferencePalette(
            canvas: Color(0xFF080606),
            lowerGlow: Color(0xFF16100D),
            panelFill: Color(0xFF0F0A09),
            sheetFill: Color(0xFF16100F),
            softFill: Color(0xFF1C1512),
            avatarFill: Color(0xFF181110),
            avatarInset: Color(0xFF221917),
            edge: Color(0xFFB97B46),
            rule: Color(0xFF4B3A30),
            text: Color(0xFFF6F1EA),
            mutedText: Color(0xFFC8BCB0),
            softText: Color(0xFFB9A99A),
            shadow: Color(0xFF000000),
          )
        : _BondReferencePalette(
            canvas: profile.colors.bg,
            lowerGlow: Color.alphaBlend(
              profile.colors.primary.withValues(alpha: 0.08),
              profile.colors.heroBase,
            ),
            panelFill: Color.alphaBlend(
              Colors.white.withValues(alpha: 0.56),
              profile.colors.heroBase,
            ),
            sheetFill: Color.alphaBlend(
              Colors.white.withValues(alpha: 0.68),
              profile.colors.surface,
            ),
            softFill: Color.alphaBlend(
              profile.colors.warmAccent.withValues(alpha: 0.08),
              profile.colors.panelSoft,
            ),
            avatarFill: Color.alphaBlend(
              profile.colors.primary.withValues(alpha: 0.06),
              profile.colors.panelSoft,
            ),
            avatarInset: profile.colors.surface,
            edge: Color.alphaBlend(
              profile.colors.primary.withValues(alpha: 0.34),
              profile.colors.strokeSoft,
            ),
            rule: profile.colors.separator,
            text: profile.colors.text,
            mutedText: profile.colors.muted,
            softText: profile.colors.textLight,
            shadow: profile.colors.shadowLift,
          );
  }
}

class _BondReferenceDashedPanel extends StatelessWidget {
  const _BondReferenceDashedPanel({
    required this.child,
    this.fillColor,
    this.borderColor,
  });

  final Widget child;
  final Color? fillColor;
  final Color? borderColor;

  @override
  Widget build(BuildContext context) {
    final palette = _BondReferencePalette.of(context);
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.fromLTRB(20, 20, 20, 20),
      decoration: BoxDecoration(
        color: fillColor ?? palette.panelFill,
        borderRadius: BorderRadius.circular(28),
        border: Border.all(
          color: (borderColor ?? palette.edge).withValues(alpha: 0.86),
          width: 1.4,
        ),
      ),
      child: child,
    );
  }
}

class _BondReferenceHero extends StatelessWidget {
  const _BondReferenceHero({required this.title, required this.body});

  final String title;
  final String body;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final palette = _BondReferencePalette.of(context);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'BOND',
          style: profile.typography.eyebrow.copyWith(color: palette.softText),
        ),
        const SizedBox(height: 10),
        ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 300),
          child: Text(
            title,
            style: profile.typography.pageTitle.copyWith(
              color: palette.text,
              fontSize: 24,
              height: 1.06,
            ),
          ),
        ),
        const SizedBox(height: 10),
        ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 352),
          child: Text(
            body,
            style: profile.typography.bodyCompact.copyWith(
              color: palette.mutedText,
              fontSize: 15,
              height: 1.52,
            ),
          ),
        ),
      ],
    );
  }
}

class _BondCtaDoorway extends StatelessWidget {
  const _BondCtaDoorway({
    required this.label,
    required this.enabled,
    required this.isBusy,
    this.onTap,
  });

  final String label;
  final bool enabled;
  final bool isBusy;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final palette = _BondReferencePalette.of(context);
    return JoviaPressable(
      onTap: enabled ? onTap : null,
      borderRadius: BorderRadius.circular(999),
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 18),
        decoration: BoxDecoration(
          color: enabled
              ? palette.softFill
              : palette.softFill.withValues(alpha: 0.56),
          borderRadius: BorderRadius.circular(999),
          border: Border.all(color: palette.edge.withValues(alpha: 0.86)),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            if (isBusy) ...[
              SizedBox(
                width: 16,
                height: 16,
                child: CircularProgressIndicator(
                  strokeWidth: 2.1,
                  valueColor: AlwaysStoppedAnimation<Color>(palette.text),
                ),
              ),
              const SizedBox(width: 10),
            ],
            Text(
              label,
              style: profile.typography.cardTitle.copyWith(
                color: palette.text,
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(width: 10),
            JoviaUiIcon(
              asset: JoviaUiAsset.chevronRight,
              size: 15,
              color: palette.text,
            ),
          ],
        ),
      ),
    );
  }
}
