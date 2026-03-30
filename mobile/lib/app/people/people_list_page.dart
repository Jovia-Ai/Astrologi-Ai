import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile/design/theme/profile_theme_extension.dart';
import 'package:mobile/design/widgets/jovia_editorial.dart';

import 'add_person_page.dart';
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
      title: 'Çevreni aynı editorial ritimde tut.',
      body:
          'Illustration üstte, spacing daha geniş, kart yapısı daha sakin. Buradaki insanlar artık geri kalan tasarımla aynı premium akışın içinde.',
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
          Positioned(
            right: -8,
            top: -4,
            child: JoviaIllustrationAccent(
              asset: JoviaIllustrationAsset.heart,
              width: 88,
              height: 88,
              opacity: 0.84,
            ),
          ),
        ],
      ),
      footer: const Wrap(
        spacing: 8,
        runSpacing: 8,
        children: [
          JoviaMetaPill(label: 'Bond hazır'),
          JoviaMetaPill(label: 'Sessiz ton'),
          JoviaMetaPill(label: 'Premium social'),
        ],
      ),
    );
  }
}

class _PeopleListItem extends StatelessWidget {
  const _PeopleListItem({
    required this.person,
    required this.onTap,
    required this.onEdit,
  });

  final PersonProfile person;
  final VoidCallback onTap;
  final VoidCallback onEdit;

  @override
  Widget build(BuildContext context) {
    final colors = context.profileTheme.colors;
    return JoviaUtilityRow(
      label: 'Friend',
      title: person.name,
      body:
          '${person.birthDate} • ${((person.birthTime ?? '').trim().isEmpty ? 'saat yok' : person.birthTime!.trim())} • ${person.city}, ${person.country}',
      leading: Container(
        width: 40,
        height: 40,
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          color: colors.panelSoft,
          border: Border.all(color: colors.strokeSoft),
        ),
        child: const Center(
          child: JoviaUiIcon(asset: JoviaUiAsset.profileComet, size: 16),
        ),
      ),
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
