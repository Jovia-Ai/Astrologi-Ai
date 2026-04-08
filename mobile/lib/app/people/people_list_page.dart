import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile/design/theme/profile_theme_extension.dart';
import 'package:mobile/design/widgets/jovia_editorial.dart';

import 'add_person_page.dart';
import 'people_aura_repository.dart';
import 'friend_profile_page.dart';
import 'people_providers.dart';
import 'people_repository.dart';
import 'person_profile.dart';

class PeopleListPage extends ConsumerWidget {
  const PeopleListPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final peopleAsync = ref.watch(peopleListProvider);
    final profile = context.profileTheme;
    final spacing = profile.spacing;
    final colors = profile.colors;

    Future<void> openCreatePerson([PersonProfile? initial]) async {
      final created = await Navigator.of(context).push<bool>(
        MaterialPageRoute<bool>(
          builder: (_) => AddPersonPage(initialPerson: initial),
        ),
      );
      if (created == true) {
        ref.invalidate(peopleListProvider);
      }
    }

    return Scaffold(
      backgroundColor: colors.bg,
      body: DecoratedBox(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              colors.bg,
              colors.bg,
              Color.alphaBlend(
                colors.neonPink.withValues(alpha: 0.1),
                colors.bg,
              ),
            ],
            stops: const [0, 0.7, 1],
          ),
        ),
        child: JoviaPageScaffold(
          child: RefreshIndicator(
            onRefresh: () async {
              ref.invalidate(peopleListProvider);
              await ref.read(peopleListProvider.future);
            },
            child: ListView(
              padding: EdgeInsets.zero,
              children: [
                JoviaProfileTopBar(
                  label: 'People',
                  centerText: 'Sosyal çevren',
                  onActionTap: () => openCreatePerson(),
                  actionAsset: JoviaUiAsset.plusCrosshair,
                  actionTooltip: 'Kişi ekle',
                ),
                SizedBox(height: spacing.s24),
                const _PeopleHeroCard(),
                SizedBox(height: spacing.s24),
                peopleAsync.when(
                  data: (items) {
                    if (items.isEmpty) {
                      return Column(
                        children: [
                          JoviaReadingPanel(
                            label: 'People',
                            title: 'Henüz kayıtlı kişi yok',
                            body:
                                'Bond ve diğer ilişki akışları için çevreni burada kuracaksın. Aynı spacing ve aynı sosyal yüzey diliyle ilerliyor.',
                          ),
                          SizedBox(height: spacing.s12),
                          SizedBox(
                            width: double.infinity,
                            child: JoviaPrimaryButton(
                              label: 'Kişi ekle',
                              onTap: () => openCreatePerson(),
                            ),
                          ),
                        ],
                      );
                    }

                    return JoviaReadingPanel(
                      label: 'Circle',
                      title: 'Yakın çevren',
                      body:
                          'Kayıtlı kişiler utility listede değil, daha sakin ve tutarlı bir sosyal yüzeyde tutuluyor.',
                      background: const Align(
                        alignment: Alignment.topRight,
                        child: Padding(
                          padding: EdgeInsets.only(right: 10, top: 8),
                          child: JoviaIllustrationAccent(
                            asset: JoviaIllustrationAsset.flower,
                            width: 82,
                            height: 82,
                            opacity: 0.78,
                          ),
                        ),
                      ),
                      child: Column(
                        children: [
                          for (
                            var index = 0;
                            index < items.length;
                            index++
                          ) ...[
                            _PeopleListItem(
                              person: items[index],
                              onTap: () {
                                Navigator.of(context).push(
                                  MaterialPageRoute<void>(
                                    builder: (_) => FriendProfilePage(
                                      personId: items[index].id,
                                    ),
                                  ),
                                );
                              },
                              onEdit: () => openCreatePerson(items[index]),
                            ),
                            if (index != items.length - 1) ...[
                              SizedBox(height: spacing.s8),
                              const ThinDivider(),
                              SizedBox(height: spacing.s8),
                            ],
                          ],
                        ],
                      ),
                    );
                  },
                  loading: () => const Padding(
                    padding: EdgeInsets.symmetric(vertical: 48),
                    child: Center(child: CircularProgressIndicator()),
                  ),
                  error: (error, _) {
                    WidgetsBinding.instance.addPostFrameCallback((_) {
                      final msg = error is PeopleQueryException
                          ? error.userMessage
                          : 'Arkadaş listesi yüklenemedi: $error';
                      ScaffoldMessenger.of(
                        context,
                      ).showSnackBar(SnackBar(content: Text(msg)));
                    });
                    return JoviaReadingPanel(
                      label: 'People',
                      title: 'Kişi listesi yüklenemedi',
                      body: error is PeopleQueryException
                          ? error.userMessage
                          : 'Arkadaş listesi yüklenemedi: $error',
                    );
                  },
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _PeopleHeroCard extends StatelessWidget {
  const _PeopleHeroCard();

  @override
  Widget build(BuildContext context) {
    return JoviaEditorialHeroBlock(
      label: 'Social',
      title: 'Çevrenin aura tonlarını aynı akışta gör.',
      body:
          'Kişiler artık yalnızca isim olarak değil, yumuşak orb diliyle de okunuyor. Aura rengi doğum ekseninden geliyor ve people listesini daha canlı bir sosyal yüzeye çeviriyor.',
      large: true,
      background: Stack(
        children: [
          const Positioned.fill(
            child: JoviaColorWash(
              asset: JoviaColorAsset.wash05,
              fit: BoxFit.cover,
              opacity: 0.1,
            ),
          ),
          const _PeopleAuraCluster(),
        ],
      ),
      footer: const Wrap(
        spacing: 8,
        runSpacing: 8,
        children: [
          JoviaMetaPill(label: 'Aura görünümü'),
          JoviaMetaPill(label: 'Doğum ekseni'),
          JoviaMetaPill(label: 'Sosyal ton'),
        ],
      ),
    );
  }
}

class _PeopleAuraCluster extends StatelessWidget {
  const _PeopleAuraCluster();

  @override
  Widget build(BuildContext context) {
    final colors = context.profileTheme.colors;
    return Stack(
      children: [
        Positioned(
          right: 14,
          top: 18,
          child: JoviaAuraOrb(
            palette: joviaAuraPaletteForBirthData(
              colors: colors,
              birthDate: '1996-07-27',
              seedText: 'hero-fire',
            ),
            size: 82,
          ),
        ),
        Positioned(
          right: 76,
          top: 76,
          child: JoviaAuraOrb(
            palette: joviaAuraPaletteForBirthData(
              colors: colors,
              birthDate: '1996-10-31',
              seedText: 'hero-water',
            ),
            size: 58,
          ),
        ),
        Positioned(
          right: 34,
          top: 102,
          child: JoviaAuraOrb(
            palette: joviaAuraPaletteForBirthData(
              colors: colors,
              birthDate: '1996-02-12',
              seedText: 'hero-air',
            ),
            size: 42,
          ),
        ),
      ],
    );
  }
}

class _PeopleListItem extends ConsumerWidget {
  const _PeopleListItem({
    required this.person,
    required this.onTap,
    required this.onEdit,
  });

  final PersonProfile person;
  final VoidCallback onTap;
  final VoidCallback onEdit;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final colors = context.profileTheme.colors;
    final fallbackAura = joviaAuraPaletteForBirthData(
      colors: colors,
      birthDate: person.birthDate,
      birthTime: person.birthTime,
      seedText: person.auraSeedKey,
    );
    final semanticAsync = ref.watch(
      personAuraSemanticProvider(PersonAuraRequest.fromPerson(person)),
    );
    final semantic = semanticAsync.valueOrNull;
    final aura = semantic == null
        ? fallbackAura
        : joviaAuraPaletteForSemantic(colors: colors, semantic: semantic);
    final auraLabel = semantic?.displayLabel ?? fallbackAura.label;

    return JoviaUtilityRow(
      label: 'Friend',
      title: person.name,
      body:
          '${person.birthDate} • ${((person.birthTime ?? '').trim().isEmpty ? 'saat yok' : person.birthTime!.trim())} • ${person.city}, ${person.country}',
      meta: [auraLabel],
      leading: JoviaAuraOrb(palette: aura, size: 44, monogram: person.monogram),
      trailing: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          IconButton(
            tooltip: 'Düzenle',
            icon: const Icon(Icons.edit_outlined, size: 18),
            onPressed: onEdit,
          ),
          const SizedBox(width: 2),
          const JoviaUiIcon(asset: JoviaUiAsset.chevronRight, size: 16),
        ],
      ),
      onTap: onTap,
    );
  }
}
