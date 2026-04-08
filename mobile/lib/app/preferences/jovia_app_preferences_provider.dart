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
  });

  final JoviaAppLocale locale;
  final bool dailyBriefEnabled;
  final bool skyAlertsEnabled;
  final bool socialAlertsEnabled;
  final bool premiumInterest;

  JoviaAppPreferences copyWith({
    JoviaAppLocale? locale,
    bool? dailyBriefEnabled,
    bool? skyAlertsEnabled,
    bool? socialAlertsEnabled,
    bool? premiumInterest,
  }) {
    return JoviaAppPreferences(
      locale: locale ?? this.locale,
      dailyBriefEnabled: dailyBriefEnabled ?? this.dailyBriefEnabled,
      skyAlertsEnabled: skyAlertsEnabled ?? this.skyAlertsEnabled,
      socialAlertsEnabled: socialAlertsEnabled ?? this.socialAlertsEnabled,
      premiumInterest: premiumInterest ?? this.premiumInterest,
    );
  }

  Map<String, dynamic> toMetadataPatch() {
    return <String, dynamic>{
      'app_locale': locale.code,
      'notifications_daily_brief': dailyBriefEnabled,
      'notifications_sky_alerts': skyAlertsEnabled,
      'notifications_social_alerts': socialAlertsEnabled,
      'premium_interest': premiumInterest,
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
