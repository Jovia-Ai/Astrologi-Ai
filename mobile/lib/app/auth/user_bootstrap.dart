import 'package:supabase_flutter/supabase_flutter.dart';

import '../data/supabase_tables.dart';

Future<void> ensureUserRows({User? user}) async {
  final client = Supabase.instance.client;
  final current = user ?? client.auth.currentUser;
  if (current == null) {
    return;
  }

  final fallbackName = (current.email ?? '').split('@').first;
  final fullName =
      (current.userMetadata?['full_name'] as String?)?.trim().isNotEmpty == true
      ? (current.userMetadata?['full_name'] as String).trim()
      : fallbackName;

  await client.from(SupabaseTables.profiles).upsert({
    'id': current.id,
    'email': current.email,
    'full_name': fullName,
  });

  await client.from('astro_settings').upsert({
    'user_id': current.id,
    'house_system': 'placidus',
    'zodiac_type': 'tropical',
  });
}
