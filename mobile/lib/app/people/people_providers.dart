import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile/design/widgets/jovia_aura.dart';

import '../preferences/jovia_app_preferences_provider.dart';
import '../profile/profile_providers.dart';
import '../telemetry/perf_telemetry.dart';
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
  final span = PerfTelemetry.startSpan(
    'peopleListProvider_resolve',
    data: const <String, Object?>{'provider': 'peopleListProvider'},
  );
  final repository = ref.watch(peopleRepositoryProvider);
  try {
    final people = await repository.listPeople(ownerUserId);
    span.finish(
      data: <String, Object?>{
        'provider': 'peopleListProvider',
        'count': people.length,
      },
    );
    return people;
  } catch (error) {
    span.finish(
      status: 'error',
      data: <String, Object?>{
        'provider': 'peopleListProvider',
        'error_type': error.runtimeType.toString(),
      },
    );
    rethrow;
  }
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
