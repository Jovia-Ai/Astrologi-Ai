import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

enum JoviaAppLocale { tr, en }

extension JoviaAppLocaleX on JoviaAppLocale {
  String get code => name;

  String get label => this == JoviaAppLocale.tr ? 'TR' : 'EN';

  Locale get materialLocale => Locale(code);
}

@immutable
class JoviaAppPreferences {
  const JoviaAppPreferences({
    required this.locale,
    required this.dailyBriefEnabled,
    required this.skyAlertsEnabled,
    required this.socialAlertsEnabled,
    required this.premiumInterest,
    this.stackClauseLastShownAtMs,
  });

  final JoviaAppLocale locale;
  final bool dailyBriefEnabled;
  final bool skyAlertsEnabled;
  final bool socialAlertsEnabled;
  final bool premiumInterest;
  // PR7b hand-off: epoch milliseconds of the last time the stack synergy
  // clause was actually rendered on this device. null = never shown. Read
  // by StackClauseGate to enforce a rolling 7-day cooldown. Written by
  // JoviaAppPreferencesController.markClauseShown.
  final int? stackClauseLastShownAtMs;

  JoviaAppPreferences copyWith({
    JoviaAppLocale? locale,
    bool? dailyBriefEnabled,
    bool? skyAlertsEnabled,
    bool? socialAlertsEnabled,
    bool? premiumInterest,
    int? stackClauseLastShownAtMs,
  }) {
    return JoviaAppPreferences(
      locale: locale ?? this.locale,
      dailyBriefEnabled: dailyBriefEnabled ?? this.dailyBriefEnabled,
      skyAlertsEnabled: skyAlertsEnabled ?? this.skyAlertsEnabled,
      socialAlertsEnabled: socialAlertsEnabled ?? this.socialAlertsEnabled,
      premiumInterest: premiumInterest ?? this.premiumInterest,
      stackClauseLastShownAtMs:
          stackClauseLastShownAtMs ?? this.stackClauseLastShownAtMs,
    );
  }

  Map<String, dynamic> toMetadataPatch() {
    return <String, dynamic>{
      'app_locale': locale.code,
      'notifications_daily_brief': dailyBriefEnabled,
      'notifications_sky_alerts': skyAlertsEnabled,
      'notifications_social_alerts': socialAlertsEnabled,
      'premium_interest': premiumInterest,
      // Only include the timestamp if it's been set, so we don't overwrite
      // server-side state with null for users who've never seen the clause.
      if (stackClauseLastShownAtMs != null)
        'stack_clause_last_shown_at_ms': stackClauseLastShownAtMs,
    };
  }

  static JoviaAppPreferences fromMetadata(Map<String, dynamic>? metadata) {
    final raw = metadata ?? const <String, dynamic>{};
    final localeRaw = (raw['app_locale'] ?? raw['locale'] ?? 'tr')
        .toString()
        .trim()
        .toLowerCase();
    return JoviaAppPreferences(
      locale: localeRaw == 'en' ? JoviaAppLocale.en : JoviaAppLocale.tr,
      dailyBriefEnabled: _readBool(raw['notifications_daily_brief'], true),
      skyAlertsEnabled: _readBool(raw['notifications_sky_alerts'], true),
      socialAlertsEnabled: _readBool(raw['notifications_social_alerts'], false),
      premiumInterest: _readBool(raw['premium_interest'], false),
      stackClauseLastShownAtMs: _readInt(raw['stack_clause_last_shown_at_ms']),
    );
  }

  static bool _readBool(dynamic value, bool fallback) {
    if (value is bool) {
      return value;
    }
    final raw = value?.toString().trim().toLowerCase();
    if (raw == 'true') {
      return true;
    }
    if (raw == 'false') {
      return false;
    }
    return fallback;
  }

  static int? _readInt(dynamic value) {
    if (value is int) {
      return value;
    }
    if (value is num) {
      return value.toInt();
    }
    final raw = value?.toString().trim();
    if (raw == null || raw.isEmpty) {
      return null;
    }
    return int.tryParse(raw);
  }
}

final joviaAppPreferencesProvider =
    NotifierProvider<JoviaAppPreferencesController, JoviaAppPreferences>(
      JoviaAppPreferencesController.new,
    );

class JoviaAppPreferencesController extends Notifier<JoviaAppPreferences> {
  @override
  JoviaAppPreferences build() {
    final metadata = Supabase.instance.client.auth.currentUser?.userMetadata;
    return JoviaAppPreferences.fromMetadata(metadata);
  }

  Future<void> setLocale(JoviaAppLocale locale) async {
    await _persist(state.copyWith(locale: locale));
  }

  Future<void> setDailyBriefEnabled(bool value) async {
    await _persist(state.copyWith(dailyBriefEnabled: value));
  }

  Future<void> setSkyAlertsEnabled(bool value) async {
    await _persist(state.copyWith(skyAlertsEnabled: value));
  }

  Future<void> setSocialAlertsEnabled(bool value) async {
    await _persist(state.copyWith(socialAlertsEnabled: value));
  }

  Future<void> setPremiumInterest(bool value) async {
    await _persist(state.copyWith(premiumInterest: value));
  }

  /// Record that the stack synergy clause was just rendered to the user.
  ///
  /// Idempotency guard: if the existing timestamp is within
  /// [dedupeWindowMs] (default 1 second) of [nowMs], the call is skipped.
  /// This prevents duplicate Supabase writes when two widgets in the same
  /// frame both observe the clause becoming visible (e.g. home_page and
  /// calendar_hub_page both rendering the top-sig event of the day). The
  /// state update itself is synchronous via _persist, so subsequent reads
  /// in the same frame see the fresh lastShownAt and skip re-marking via
  /// the cooldown check in StackClauseGate.
  Future<void> markClauseShown(
    int nowMs, {
    int dedupeWindowMs = 1000,
  }) async {
    final last = state.stackClauseLastShownAtMs;
    if (last != null && (nowMs - last).abs() < dedupeWindowMs) {
      return;
    }
    await _persist(state.copyWith(stackClauseLastShownAtMs: nowMs));
  }

  Future<void> _persist(JoviaAppPreferences next) async {
    state = next;
    final user = Supabase.instance.client.auth.currentUser;
    if (user == null) {
      return;
    }
    final metadata = Map<String, dynamic>.from(
      user.userMetadata ?? const <String, dynamic>{},
    )..addAll(next.toMetadataPatch());
    try {
      await Supabase.instance.client.auth.updateUser(
        UserAttributes(data: metadata),
      );
    } catch (error, stackTrace) {
      debugPrint('[JoviaAppPreferences] persist failed: $error');
      FlutterError.reportError(
        FlutterErrorDetails(
          exception: error,
          stack: stackTrace,
          library: 'jovia_app_preferences_provider',
          context: ErrorDescription('persisting app preferences'),
        ),
      );
    }
  }
}
