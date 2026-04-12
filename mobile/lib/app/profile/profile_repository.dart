import 'package:supabase_flutter/supabase_flutter.dart';

import '../data/supabase_tables.dart';
import '../telemetry/perf_telemetry.dart';

class ProfileRepository {
  static const String _avatarBucket = 'avatars';
  static const Duration _profileCacheTtl = Duration(minutes: 3);
  static const Duration _birthGateCacheTtl = Duration(minutes: 3);
  static final Map<String, _ProfileCacheEntry> _profileCache =
      <String, _ProfileCacheEntry>{};
  static final Map<String, _ProfileCacheEntry> _birthGateCache =
      <String, _ProfileCacheEntry>{};
  static final Map<String, Future<Map<String, dynamic>?>> _inflight =
      <String, Future<Map<String, dynamic>?>>{};
  static final Map<String, Future<Map<String, dynamic>?>> _birthGateInflight =
      <String, Future<Map<String, dynamic>?>>{};

  final SupabaseClient _client;
  ProfileRepository({SupabaseClient? client})
    : _client = client ?? Supabase.instance.client;

  Future<Map<String, dynamic>?> getProfile(String userId) async {
    final now = DateTime.now();
    final cached = _profileCache[userId];
    if (cached != null && cached.expiresAt.isAfter(now)) {
      PerfTelemetry.logPoint(
        'profile_loaded_from_cache',
        data: const <String, Object?>{'source': 'ProfileRepository.getProfile'},
      );
      return cached.data == null
          ? null
          : Map<String, dynamic>.from(cached.data!);
    }

    final inflight = _inflight[userId];
    if (inflight != null) {
      PerfTelemetry.logPoint(
        'profile_repository_inflight_dedupe',
        data: const <String, Object?>{'source': 'ProfileRepository.getProfile'},
      );
      return inflight;
    }

    final future = _fetchProfile(userId).whenComplete(() {
      _inflight.remove(userId);
    });
    _inflight[userId] = future;
    return future;
  }

  Future<Map<String, dynamic>?> getBirthGateProfile(String userId) async {
    final now = DateTime.now();
    final cached = _birthGateCache[userId];
    if (cached != null && cached.expiresAt.isAfter(now)) {
      PerfTelemetry.logPoint(
        'birth_gate_profile_loaded_from_cache',
        data: const <String, Object?>{
          'source': 'ProfileRepository.getBirthGateProfile',
        },
      );
      return cached.data == null
          ? null
          : Map<String, dynamic>.from(cached.data!);
    }

    final inflight = _birthGateInflight[userId];
    if (inflight != null) {
      PerfTelemetry.logPoint(
        'birth_gate_profile_inflight_dedupe',
        data: const <String, Object?>{
          'source': 'ProfileRepository.getBirthGateProfile',
        },
      );
      return inflight;
    }

    final future = _fetchBirthGateProfile(userId).whenComplete(() {
      _birthGateInflight.remove(userId);
    });
    _birthGateInflight[userId] = future;
    return future;
  }

  Future<Map<String, dynamic>?> _fetchProfile(String userId) async {
    final span = PerfTelemetry.startSpan(
      'profile_repository_fetch',
      data: const <String, Object?>{
        'source': 'ProfileRepository._fetchProfile',
      },
    );
    try {
      final responses = await Future.wait<dynamic>([
        _client
            .from(SupabaseTables.profiles)
            .select('id,email,full_name,avatar_path')
            .eq('id', userId)
            .limit(1)
            .maybeSingle(),
        _client
            .from(SupabaseTables.birthData)
            .select(
              'user_id,birth_date,birth_time,place,city,country,timezone,latitude,longitude',
            )
            .eq('user_id', userId)
            .limit(1)
            .maybeSingle(),
      ]);

      final profile = responses[0] as Map<String, dynamic>?;
      final birthData = responses[1] as Map<String, dynamic>?;

      Map<String, dynamic>? result;
      if (profile != null || birthData != null) {
        result = <String, dynamic>{
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
      }

      _profileCache[userId] = _ProfileCacheEntry(
        data: result == null ? null : Map<String, dynamic>.from(result),
        expiresAt: DateTime.now().add(_profileCacheTtl),
      );
      span.finish(
        data: <String, Object?>{
          'source': 'ProfileRepository._fetchProfile',
          'has_profile': result != null,
        },
      );
      PerfTelemetry.logPoint(
        'profile_loaded_from_network',
        data: const <String, Object?>{'source': 'ProfileRepository.getProfile'},
      );
      return result;
    } catch (error) {
      span.finish(
        status: 'error',
        data: <String, Object?>{
          'source': 'ProfileRepository._fetchProfile',
          'error_type': error.runtimeType.toString(),
        },
      );
      rethrow;
    }
  }

  Future<Map<String, dynamic>?> _fetchBirthGateProfile(String userId) async {
    final span = PerfTelemetry.startSpan(
      'birth_gate_profile_fetch',
      data: const <String, Object?>{
        'source': 'ProfileRepository._fetchBirthGateProfile',
      },
    );
    try {
      final birthData = await _client
          .from(SupabaseTables.birthData)
          .select('user_id,birth_date,place')
          .eq('user_id', userId)
          .limit(1)
          .maybeSingle();
      final result = birthData == null
          ? null
          : Map<String, dynamic>.from(birthData);
      _birthGateCache[userId] = _ProfileCacheEntry(
        data: result == null ? null : Map<String, dynamic>.from(result),
        expiresAt: DateTime.now().add(_birthGateCacheTtl),
      );
      span.finish(
        data: <String, Object?>{
          'source': 'ProfileRepository._fetchBirthGateProfile',
          'has_birth_gate_profile': result != null,
        },
      );
      return result;
    } catch (error) {
      span.finish(
        status: 'error',
        data: <String, Object?>{
          'source': 'ProfileRepository._fetchBirthGateProfile',
          'error_type': error.runtimeType.toString(),
        },
      );
      rethrow;
    }
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
    _invalidateProfile(userId);
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
      _invalidateProfile(userId);
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
    _invalidateProfile(userId);
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
      _invalidateProfile(userId);
      return;
    }

    await _client
        .from(SupabaseTables.birthData)
        .update(payload)
        .eq('user_id', userId);
    _invalidateProfile(userId);
  }

  Future<Map<String, dynamic>?> getArchetypeProfile(String userId) async {
    try {
      final row = await _client
          .from(SupabaseTables.archetypeProfiles)
          .select('user_id,computed_at,input_mode,final_profile')
          .eq('user_id', userId)
          .limit(1)
          .maybeSingle();
      if (row == null) {
        return null;
      }
      final finalProfile = row['final_profile'];
      if (finalProfile is! Map) {
        return null;
      }
      final payload = Map<String, dynamic>.from(finalProfile);
      final snapshot = payload['snapshot'];
      payload['snapshot'] = <String, dynamic>{
        if (snapshot is Map) ...Map<String, dynamic>.from(snapshot),
        'persisted': true,
        'computed_at': row['computed_at'],
        'input_mode': row['input_mode'] ?? payload['input_mode'],
      };
      return payload;
    } catch (_) {
      return null;
    }
  }

  void _invalidateProfile(String userId) {
    _profileCache.remove(userId);
    _birthGateCache.remove(userId);
    _inflight.remove(userId);
    _birthGateInflight.remove(userId);
  }
}

class _ProfileCacheEntry {
  const _ProfileCacheEntry({required this.data, required this.expiresAt});

  final Map<String, dynamic>? data;
  final DateTime expiresAt;
}
