import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

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

    return Scaffold(
      appBar: AppBar(
        title: const Text('Arkadaşlar'),
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
                padding: const EdgeInsets.all(24),
                children: [
                  const Card(
                    child: Padding(
                      padding: EdgeInsets.all(16),
                      child: Text('Henüz kayıtlı kişi yok.'),
                    ),
                  ),
                  const SizedBox(height: 12),
                  OutlinedButton.icon(
                    onPressed: () async {
                      final created = await Navigator.of(context).push<bool>(
                        MaterialPageRoute<bool>(
                          builder: (_) => const AddPersonPage(),
                        ),
                      );
                      if (created == true) {
                        ref.invalidate(peopleListProvider);
                      }
                    },
                    icon: const Icon(Icons.add),
                    label: const Text('Kişi Ekle'),
                  ),
                ],
              );
            }

            return ListView.separated(
              padding: const EdgeInsets.all(16),
              itemCount: items.length,
              separatorBuilder: (_, _) => const SizedBox(height: 10),
              itemBuilder: (context, index) {
                final person = items[index];
                return Card(
                  child: ListTile(
                    contentPadding: const EdgeInsets.symmetric(
                      horizontal: 14,
                      vertical: 8,
                    ),
                    leading: const CircleAvatar(
                      child: Icon(Icons.person_outline),
                    ),
                    title: Text(person.name),
                    subtitle: Text(_subtitle(person)),
                    trailing: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        IconButton(
                          tooltip: 'Düzenle',
                          icon: const Icon(Icons.edit_outlined),
                          onPressed: () async {
                            final updated = await Navigator.of(context)
                                .push<bool>(
                                  MaterialPageRoute<bool>(
                                    builder: (_) =>
                                        AddPersonPage(initialPerson: person),
                                  ),
                                );
                            if (updated == true) {
                              ref.invalidate(peopleListProvider);
                            }
                          },
                        ),
                        const Icon(Icons.chevron_right),
                      ],
                    ),
                    onTap: () {
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
            );
          },
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (error, _) => ListView(
            padding: const EdgeInsets.all(24),
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
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Text(
                    error is PeopleQueryException
                        ? error.userMessage
                        : 'Arkadaş listesi yüklenemedi: $error',
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  String _subtitle(PersonProfile person) {
    final birthTime = (person.birthTime ?? '').trim();
    final timePart = birthTime.isEmpty ? 'saat yok' : birthTime;
    return '${person.birthDate} • $timePart • ${person.city}, ${person.country}';
  }
}
