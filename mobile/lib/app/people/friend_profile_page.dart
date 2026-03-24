import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile/design/theme/profile_theme_extension.dart';

import 'add_person_page.dart';
import '../tabs/profile_page.dart';
import 'people_providers.dart';
import 'people_repository.dart';

class FriendProfilePage extends ConsumerWidget {
  const FriendProfilePage({super.key, required this.personId});

  final String personId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final personAsync = ref.watch(personByIdProvider(personId));

    return personAsync.when(
      data: (person) {
        if (person == null) {
          return Scaffold(
            appBar: AppBar(
              title: Text(
                'KISI PROFILI',
                style: context.profileTheme.typography.navigationLabel(
                  color: context.profileTheme.colors.text,
                ),
              ),
            ),
            body: Center(
              child: Text(
                'Kişi bulunamadı.',
                style: context.profileTheme.typography.bodyCompact.copyWith(
                  color: context.profileTheme.colors.text,
                ),
              ),
            ),
          );
        }

        return Stack(
          children: [
            ProfilePage(
              viewedUserId: person.id,
              profileOverride: person.toProfileMap(),
              readOnly: true,
            ),
            Positioned(
              right: 16,
              bottom: 24,
              child: FloatingActionButton.small(
                tooltip: 'Kişiyi düzenle',
                onPressed: () async {
                  final updated = await Navigator.of(context).push<bool>(
                    MaterialPageRoute<bool>(
                      builder: (_) => AddPersonPage(initialPerson: person),
                    ),
                  );
                  if (updated == true) {
                    ref.invalidate(personByIdProvider(personId));
                    ref.invalidate(peopleListProvider);
                  }
                },
                child: const Icon(Icons.edit_outlined),
              ),
            ),
          ],
        );
      },
      loading: () =>
          const Scaffold(body: Center(child: CircularProgressIndicator())),
      error: (error, _) => Scaffold(
        appBar: AppBar(
          title: Text(
            'KISI PROFILI',
            style: context.profileTheme.typography.navigationLabel(
              color: context.profileTheme.colors.text,
            ),
          ),
        ),
        body: Center(
          child: Text(
            error is PeopleQueryException
                ? error.userMessage
                : 'Kişi yüklenemedi: $error',
            style: context.profileTheme.typography.bodyCompact.copyWith(
              color: context.profileTheme.colors.text,
            ),
          ),
        ),
      ),
    );
  }
}
