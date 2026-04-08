import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile/design/widgets/jovia_aura.dart';

import '../preferences/jovia_app_preferences_provider.dart';
import '../profile/profile_providers.dart';
import 'people_aura_repository.dart';
import 'people_repository.dart';
import 'person_profile.dart';

final peopleRepositoryProvider = Provider<PeopleRepository>(
  (ref) => PeopleRepository(),
);

final peopleAuraRepositoryProvider = Provider<PeopleAuraRepository>(
  (ref) => PeopleAuraRepository(),
);

final peopleListProvider = FutureProvider<List<PersonProfile>>((ref) async {
  final ownerUserId = ref.watch(currentUserIdProvider);
  if (ownerUserId == null) {
    return const <PersonProfile>[];
  }
  final repository = ref.watch(peopleRepositoryProvider);
  return repository.listPeople(ownerUserId);
});

final personByIdProvider = FutureProvider.family<PersonProfile?, String>((
  ref,
  personId,
) async {
  final ownerUserId = ref.watch(currentUserIdProvider);
  if (ownerUserId == null) {
    return null;
  }
  final repository = ref.watch(peopleRepositoryProvider);
  return repository.getPerson(ownerUserId: ownerUserId, personId: personId);
});

final personAuraSemanticProvider =
    FutureProvider.family<JoviaAuraSemantic?, PersonAuraRequest>((
      ref,
      request,
    ) async {
      final locale = ref.watch(joviaAppPreferencesProvider).locale.code;
      final repository = ref.watch(peopleAuraRepositoryProvider);
      return repository.getAuraSemantic(request: request, locale: locale);
    });
