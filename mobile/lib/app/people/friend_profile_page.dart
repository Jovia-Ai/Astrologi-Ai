import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile/design/theme/profile_theme_extension.dart';
import 'package:mobile/design/widgets/jovia_editorial.dart';
import 'package:mobile/l10n/l10n.dart';

import 'add_person_page.dart';
import 'people_aura_repository.dart';
import 'person_profile.dart';
import '../tabs/profile_page.dart';
import 'people_providers.dart';
import 'people_repository.dart';

class FriendProfilePage extends ConsumerWidget {
  const FriendProfilePage({super.key, required this.personId});

  final String personId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    final personAsync = ref.watch(personByIdProvider(personId));

    return personAsync.when(
      data: (person) {
        if (person == null) {
          return Scaffold(
            appBar: AppBar(
              title: Text(
                l10n.friendProfileTitle,
                style: context.profileTheme.typography.navigationLabel(
                  color: context.profileTheme.colors.text,
                ),
              ),
            ),
            body: Center(
              child: Text(
                l10n.friendProfileNotFound,
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
              left: 16,
              bottom: 24,
              child: SafeArea(
                top: false,
                child: IgnorePointer(child: _FriendAuraBadge(person: person)),
              ),
            ),
            Positioned(
              right: 16,
              bottom: 24,
              child: FloatingActionButton.small(
                tooltip: l10n.friendProfileEditTooltip,
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
            l10n.friendProfileTitle,
            style: context.profileTheme.typography.navigationLabel(
              color: context.profileTheme.colors.text,
            ),
          ),
        ),
        body: Center(
          child: Text(
            error is PeopleQueryException
                ? error.userMessage
                : l10n.friendProfileLoadFailed('$error'),
            style: context.profileTheme.typography.bodyCompact.copyWith(
              color: context.profileTheme.colors.text,
            ),
          ),
        ),
      ),
    );
  }
}

class _FriendAuraBadge extends ConsumerWidget {
  const _FriendAuraBadge({required this.person});

  final PersonProfile person;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final profile = context.profileTheme;
    final fallbackAura = joviaAuraPaletteForBirthData(
      colors: profile.colors,
      birthDate: person.birthDate,
      birthTime: person.birthTime,
      seedText: person.auraSeedKey,
    );
    final semanticAsync = ref.watch(
      personAuraSemanticProvider(PersonAuraRequest.fromPerson(person)),
    );
    final semantic = semanticAsync.asData?.value;
    final aura = semantic == null
        ? fallbackAura
        : joviaAuraPaletteForSemantic(
            colors: profile.colors,
            semantic: semantic,
          );
    final eyebrow = semantic?.sourceLabel.trim().isNotEmpty == true
        ? (semantic?.sourceLabel ?? '')
        : 'Aura';
    final title = semantic?.displayLabel ?? fallbackAura.label;

    return JoviaSurfaceCard(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          JoviaAuraOrb(
            palette: aura,
            size: 42,
            monogram: person.monogram,
            showSparkles: false,
          ),
          const SizedBox(width: 12),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                eyebrow,
                style: profile.typography.eyebrow.copyWith(
                  color: profile.colors.textLight,
                ),
              ),
              const SizedBox(height: 3),
              Text(
                title,
                style: profile.typography.cardTitle.copyWith(fontSize: 15),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
