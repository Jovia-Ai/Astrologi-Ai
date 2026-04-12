import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import '../telemetry/perf_telemetry.dart';
import 'profile_repository.dart';

final profileRepositoryProvider = Provider<ProfileRepository>(
  (ref) => ProfileRepository(),
);

final currentUserIdProvider = Provider<String?>((ref) {
  return Supabase.instance.client.auth.currentUser?.id;
});

final userProfileProvider = FutureProvider<Map<String, dynamic>?>((ref) async {
  final uid = ref.watch(currentUserIdProvider);
  if (uid == null) return null;
  final span = PerfTelemetry.startSpan(
    'userProfileProvider_resolve',
    data: const <String, Object?>{'provider': 'userProfileProvider'},
  );
  final repo = ref.watch(profileRepositoryProvider);
  try {
    final profile = await repo.getProfile(uid);
    span.finish(
      data: <String, Object?>{
        'provider': 'userProfileProvider',
        'has_profile': profile != null,
      },
    );
    return profile;
  } catch (error) {
    span.finish(
      status: 'error',
      data: <String, Object?>{
        'provider': 'userProfileProvider',
        'error_type': error.runtimeType.toString(),
      },
    );
    rethrow;
  }
});
