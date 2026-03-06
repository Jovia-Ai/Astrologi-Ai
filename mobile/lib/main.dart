import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'app/supabase/supabase_bootstrap.dart';
import 'package:mobile/app/auth/auth_gate.dart';
import 'package:mobile/design/theme/profile_theme_extension.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final supabaseReady = await SupabaseBootstrap.init();
  runApp(ProviderScope(child: MyApp(supabaseReady: supabaseReady)));
}

class MyApp extends StatelessWidget {
  const MyApp({super.key, required this.supabaseReady});
  final bool supabaseReady;

  @override
  Widget build(BuildContext context) {
    final baseTheme = ThemeData();
    return MaterialApp(
      title: 'Astrologi AI',
      theme: withProfileTheme(baseTheme),
      home: supabaseReady
          ? const AuthGate()
          : _SupabaseConfigErrorScreen(message: SupabaseBootstrap.lastError),
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
                      'Supabase baslatilamadi. Lutfen SUPABASE_ANON_KEY degerini ekleyin.',
                ),
                const SizedBox(height: 16),
                const Text(
                  'Ornek:\nflutter run --dart-define=SUPABASE_ANON_KEY=YOUR_KEY',
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
