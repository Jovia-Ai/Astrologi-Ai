import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

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
  final repo = ref.watch(profileRepositoryProvider);
  return repo.getProfile(uid);
});
