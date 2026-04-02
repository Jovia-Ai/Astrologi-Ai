import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:mobile/app/auth/auth_gate.dart';
import 'package:mobile/app/splash/splash_screen.dart';
import 'package:mobile/app/theme/app_theme_mode_provider.dart';
import 'package:mobile/design/theme/profile_theme_extension.dart';

import 'app/supabase/supabase_bootstrap.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  debugPrint('SUPABASE INIT START');
  final supabaseReady = await SupabaseBootstrap.init();
  if (supabaseReady) {
    debugPrint('SUPABASE INIT OK');
  } else {
    debugPrint('SUPABASE INIT FAILED: ${SupabaseBootstrap.lastError}');
  }
  runApp(ProviderScope(child: MyApp(supabaseReady: supabaseReady)));
}

class MyApp extends ConsumerWidget {
  const MyApp({super.key, required this.supabaseReady});
  final bool supabaseReady;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final themeMode = supabaseReady
        ? ref.watch(joviaThemeModeProvider)
        : JoviaThemeMode.light;
    final lightTheme = withProfileTheme(
      ThemeData(brightness: Brightness.light, useMaterial3: true),
      profileTheme: ProfileTheme.light(),
    );
    final darkTheme = withProfileTheme(
      ThemeData(brightness: Brightness.dark, useMaterial3: true),
      profileTheme: ProfileTheme.dark(),
    );
    return MaterialApp(
      title: 'Astrologi AI',
      theme: lightTheme,
      darkTheme: darkTheme,
      themeMode: themeMode.materialMode,
      themeAnimationDuration: const Duration(milliseconds: 520),
      themeAnimationCurve: Curves.easeInOutCubic,
      home: SplashScreen(
        child: supabaseReady
            ? const AuthGate()
            : _SupabaseConfigErrorScreen(message: SupabaseBootstrap.lastError),
      ),
    );
  }
}

class _SupabaseConfigErrorScreen extends StatelessWidget {
  const _SupabaseConfigErrorScreen({this.message});

  final String? message;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Center(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Supabase Konfigurasyon Hatasi',
                  style: TextStyle(fontSize: 20, fontWeight: FontWeight.w700),
                ),
                const SizedBox(height: 12),
                Text(
                  message ??
                      'Supabase baslatilamadi. Lutfen SUPABASE_URL ve SUPABASE_ANON_KEY degerlerini ekleyin.',
                ),
                const SizedBox(height: 16),
                const Text(
                  'Ornek:\nflutter run --dart-define=SUPABASE_URL=https://YOUR_PROJECT.supabase.co --dart-define=SUPABASE_ANON_KEY=YOUR_KEY',
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
