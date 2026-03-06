import 'package:supabase_flutter/supabase_flutter.dart';

class SupabaseBootstrap {
  static const String _projectRef = 'uolpnoncfpptukxbmzal';
  static const String url = 'https://$_projectRef.supabase.co';
  static bool _initialized = false;
  static String? _lastError;

  static String get anonKey =>
      const String.fromEnvironment('SUPABASE_ANON_KEY', defaultValue: '');

  static bool get isConfigured => anonKey.trim().isNotEmpty;
  static bool get isInitialized => _initialized;
  static String? get lastError => _lastError;

  static Future<bool> init() async {
    if (_initialized) {
      return true;
    }
    if (!isConfigured) {
      _lastError =
          'SUPABASE_ANON_KEY tanimli degil. Uygulamayi --dart-define=SUPABASE_ANON_KEY=... ile baslatin.';
      return false;
    }
    try {
      await Supabase.initialize(url: url, anonKey: anonKey);
      _initialized = true;
      _lastError = null;
      return true;
    } catch (e) {
      _lastError = 'Supabase initialize basarisiz: $e';
      return false;
    }
  }

  static SupabaseClient get client => Supabase.instance.client;
}
