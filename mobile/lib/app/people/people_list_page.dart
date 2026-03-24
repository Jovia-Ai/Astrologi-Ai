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

    return Scaffold(
      appBar: AppBar(
        title: Text(
          'KISILER',
          style: profile.typography.navigationLabel(color: profile.colors.text),
        ),
        actions: [
          IconButton(
            tooltip: 'Kişi ekle',
            icon: const Icon(Icons.person_add_alt_1_outlined),
            onPressed: () async {
              final created = await Navigator.of(context).push<bool>(
                MaterialPageRoute<bool>(builder: (_) => const AddPersonPage()),
              );
              if (created == true) {
                ref.invalidate(peopleListProvider);
              }
            },
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          ref.invalidate(peopleListProvider);
          await ref.read(peopleListProvider.future);
        },
        child: peopleAsync.when(
          data: (items) {
            if (items.isEmpty) {
              return ListView(
                padding: EdgeInsets.all(spacing.s24),
                children: [
                  JoviaReadingPanel(
                    label: 'People',
                    title: 'Henuz kayitli kisi yok',
                    body:
                        'Bond ve diger iliski akislari icin kisi alanini buradan kuracaksin.',
                  ),
                  SizedBox(height: spacing.s12),
                  JoviaPrimaryButton(
                    label: 'Kisi ekle',
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
                ],
              );
            }

            return ListView(
              padding: EdgeInsets.all(spacing.s16),
              children: [
                JoviaReadingPanel(
                  label: 'People',
                  title: 'Kisi alanin',
                  body:
                      'Kaydettigin insanlar burada tek bir utility listede durur.',
                  child: Column(
                    children: [
                      for (var index = 0; index < items.length; index++) ...[
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
                          onEdit: () async {
                            final updated = await Navigator.of(context)
                                .push<bool>(
                                  MaterialPageRoute<bool>(
                                    builder: (_) => AddPersonPage(
                                      initialPerson: items[index],
                                    ),
                                  ),
                                );
                            if (updated == true) {
                              ref.invalidate(peopleListProvider);
                            }
                          },
                        ),
                        if (index != items.length - 1) const ThinDivider(),
                      ],
                    ],
                  ),
                ),
              ],
            );
          },
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (error, _) => ListView(
            padding: EdgeInsets.all(spacing.s24),
            children: [
              Builder(
                builder: (context) {
                  WidgetsBinding.instance.addPostFrameCallback((_) {
                    final msg = error is PeopleQueryException
                        ? error.userMessage
                        : 'Arkadaş listesi yüklenemedi: $error';
                    ScaffoldMessenger.of(
                      context,
                    ).showSnackBar(SnackBar(content: Text(msg)));
                  });
                  return const SizedBox.shrink();
                },
              ),
              JoviaReadingPanel(
                label: 'People',
                title: 'Kisi listesi yuklenemedi',
                body: error is PeopleQueryException
                    ? error.userMessage
                    : 'Arkadaş listesi yüklenemedi: $error',
              ),
            ],
          ),
        ),
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
    return JoviaUtilityRow(
      label: 'Kisi',
      title: person.name,
      body:
          '${person.birthDate} • ${((person.birthTime ?? '').trim().isEmpty ? 'saat yok' : person.birthTime!.trim())} • ${person.city}, ${person.country}',
      leading: CircleAvatar(
        radius: 18,
        backgroundColor: context.profileTheme.colors.lavender,
        child: const JoviaUiIcon(asset: JoviaUiAsset.profileComet, size: 16),
      ),
      trailing: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          IconButton(
            tooltip: 'Duzenle',
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
