import 'package:flutter/foundation.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

class SupabaseBootstrap {
  static const String _fallbackProjectRef = 'uolpnoncfpptukxbmzal';
  static const String _fallbackUrl = 'https://$_fallbackProjectRef.supabase.co';
  static const String _fallbackAnonKey =
      'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVvbHBub25jZnBwdHVreGJtemFsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ0MjkxNTIsImV4cCI6MjA4MDAwNTE1Mn0.70QsATWnfW0klqFdU0atiTlRxxMHTGFUi80uFbAZYxo';
  static const String _rawUrl = String.fromEnvironment(
    'SUPABASE_URL',
    defaultValue: _fallbackUrl,
  );
  static const String _rawAnonKey = String.fromEnvironment(
    'SUPABASE_ANON_KEY',
    defaultValue: _fallbackAnonKey,
  );
  static bool _initialized = false;
  static String? _lastError;

  static String get url => _normalizeUrl(_rawUrl);
  static String get anonKey => _rawAnonKey;

  static bool get isConfigured =>
      url.trim().isNotEmpty && anonKey.trim().isNotEmpty;
  static bool get isInitialized => _initialized;
  static String? get lastError => _lastError;

  static Future<bool> init() async {
    if (_initialized) {
      debugPrint('SUPABASE INIT SKIP: already initialized');
      return true;
    }
    final resolvedUrl = url;
    final hasAnonKey = anonKey.trim().isNotEmpty;
    debugPrint(
      'SUPABASE CONFIG url=$resolvedUrl host=${Uri.tryParse(resolvedUrl)?.host ?? ''} anonKeyPresent=$hasAnonKey',
    );
    if (resolvedUrl.isEmpty) {
      _lastError =
          'SUPABASE_URL tanimli degil. Uygulamayi --dart-define=SUPABASE_URL=https://YOUR_PROJECT.supabase.co ile baslatin.';
      debugPrint('SUPABASE INIT ERROR: $_lastError');
      return false;
    }
    if (!hasAnonKey) {
      _lastError =
          'SUPABASE_ANON_KEY tanimli degil. Uygulamayi --dart-define=SUPABASE_ANON_KEY=... ile baslatin.';
      debugPrint('SUPABASE INIT ERROR: $_lastError');
      return false;
    }
    final parsedUrl = Uri.tryParse(resolvedUrl);
    if (parsedUrl == null ||
        !parsedUrl.hasScheme ||
        parsedUrl.host.trim().isEmpty) {
      _lastError = 'SUPABASE_URL gecersiz: $resolvedUrl';
      debugPrint('SUPABASE INIT ERROR: $_lastError');
      return false;
    }
    try {
      await Supabase.initialize(url: resolvedUrl, anonKey: anonKey);
      _initialized = true;
      _lastError = null;
      debugPrint('SUPABASE INIT CLIENT READY host=${parsedUrl.host}');
      return true;
    } catch (e, st) {
      _lastError = 'Supabase initialize basarisiz (url=$resolvedUrl): $e';
      debugPrint('SUPABASE INIT ERROR: $_lastError');
      debugPrintStack(stackTrace: st);
      return false;
    }
  }

  static SupabaseClient get client => Supabase.instance.client;

  static String _normalizeUrl(String value) {
    final trimmed = value.trim();
    if (trimmed.isEmpty) {
      return '';
    }
    return trimmed.endsWith('/')
        ? trimmed.substring(0, trimmed.length - 1)
        : trimmed;
  }
}
