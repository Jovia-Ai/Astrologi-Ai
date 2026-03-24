import 'package:supabase_flutter/supabase_flutter.dart';

import '../data/supabase_tables.dart';

class ProfileRepository {
  static const String _avatarBucket = 'avatars';

  final SupabaseClient _client;
  ProfileRepository({SupabaseClient? client})
    : _client = client ?? Supabase.instance.client;

  Future<Map<String, dynamic>?> getProfile(String userId) async {
    final profile = await _client
        .from(SupabaseTables.profiles)
        .select('id,email,full_name,avatar_path')
        .eq('id', userId)
        .limit(1)
        .maybeSingle();
    final birthData = await _client
        .from(SupabaseTables.birthData)
        .select(
          'user_id,birth_date,birth_time,place,city,country,timezone,latitude,longitude',
        )
        .eq('user_id', userId)
        .limit(1)
        .maybeSingle();

    if (profile == null && birthData == null) {
      return null;
    }

    final result = {
      if (profile != null) ...Map<String, dynamic>.from(profile),
      if (birthData != null) ...Map<String, dynamic>.from(birthData),
    };

    final fullName = (result['full_name'] ?? '').toString().trim();
    if (fullName.isNotEmpty &&
        (result['name'] == null ||
            (result['name'] as Object).toString().trim().isEmpty)) {
      result['name'] = fullName;
    }

    final avatarPath = (result['avatar_path'] ?? '').toString().trim();
    if (avatarPath.isNotEmpty) {
      result['avatar_url'] = avatarPublicUrl(avatarPath);
    }

    return result;
  }

  Future<void> upsertProfileBasics({
    required String userId,
    required String fullName,
    String? email,
  }) async {
    await _client.from(SupabaseTables.profiles).upsert({
      'id': userId,
      'email': email,
      'full_name': fullName,
    });
  }

  Future<void> saveAvatarPath({
    required String userId,
    required String avatarPath,
  }) async {
    final existing = await _client
        .from(SupabaseTables.profiles)
        .select('id')
        .eq('id', userId)
        .limit(1)
        .maybeSingle();

    if (existing != null) {
      await _client
          .from(SupabaseTables.profiles)
          .update({'avatar_path': avatarPath})
          .eq('id', userId);
      return;
    }

    final user = _client.auth.currentUser;
    final email = (user?.email ?? '').trim();
    if (email.isEmpty) {
      throw StateError(
        'Profil satiri olusturulamadi: kullanici email bilgisi eksik.',
      );
    }

    final fullName =
        (user?.userMetadata?['full_name'] ?? user?.userMetadata?['name'] ?? '')
            .toString()
            .trim();

    await _client.from(SupabaseTables.profiles).insert({
      'id': userId,
      'email': email,
      if (fullName.isNotEmpty) 'full_name': fullName,
      'avatar_path': avatarPath,
    });
  }

  String avatarPublicUrl(String path) {
    return _client.storage.from(_avatarBucket).getPublicUrl(path);
  }

  Future<void> upsertBirthData({
    required String userId,
    required String birthDate,
    required String birthTime,
    required String place,
    required String city,
    required String country,
    required String timezone,
    double? latitude,
    double? longitude,
  }) async {
    final payload = {
      'user_id': userId,
      'birth_date': birthDate,
      'birth_time': birthTime,
      'place': place,
      'city': city,
      'country': country,
      'timezone': timezone,
      'latitude': latitude,
      'longitude': longitude,
    };

    final existing = await _client
        .from(SupabaseTables.birthData)
        .select('user_id')
        .eq('user_id', userId)
        .limit(1)
        .maybeSingle();

    if (existing == null) {
      await _client.from(SupabaseTables.birthData).insert(payload);
      return;
    }

    await _client
        .from(SupabaseTables.birthData)
        .update(payload)
        .eq('user_id', userId);
  }
}
