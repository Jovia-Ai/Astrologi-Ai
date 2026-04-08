import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:mobile/app/preferences/jovia_app_preferences_provider.dart';
import 'package:mobile/app/auth/auth_gate.dart';
import 'package:mobile/app/splash/splash_screen.dart';
import 'package:mobile/app/theme/app_theme_mode_provider.dart';
import 'package:mobile/design/theme/profile_theme_extension.dart';
import 'package:mobile/design/typography/app_font_family.dart';
import 'package:mobile/l10n/app_localizations.dart';
import 'package:mobile/l10n/l10n.dart';

import 'app/supabase/supabase_bootstrap.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const ProviderScope(child: MyApp()));
}

class MyApp extends ConsumerStatefulWidget {
  const MyApp({super.key});

  @override
  ConsumerState<MyApp> createState() => _MyAppState();
}

class _MyAppState extends ConsumerState<MyApp> {
  late final Future<bool> _bootstrapFuture;
  bool _bootstrapResolved = SupabaseBootstrap.isInitialized;
  bool _supabaseReady = SupabaseBootstrap.isInitialized;

  @override
  void initState() {
    super.initState();
    _bootstrapFuture = SupabaseBootstrap.init().then((ready) {
      if (mounted) {
        setState(() {
          _bootstrapResolved = true;
          _supabaseReady = ready;
        });
      } else {
        _bootstrapResolved = true;
        _supabaseReady = ready;
      }
      return ready;
    });
  }

  @override
  Widget build(BuildContext context) {
    final themeMode = _supabaseReady
        ? ref.watch(joviaThemeModeProvider)
        : JoviaThemeMode.light;
    final locale = _supabaseReady
        ? ref.watch(joviaAppPreferencesProvider).locale
        : JoviaAppLocale.tr;
    final lightTheme = withProfileTheme(
      ThemeData(
        brightness: Brightness.light,
        useMaterial3: true,
        fontFamily: platformDisplayFontFamily(),
      ),
      profileTheme: ProfileTheme.light(),
    );
    final darkTheme = withProfileTheme(
      ThemeData(
        brightness: Brightness.dark,
        useMaterial3: true,
        fontFamily: platformDisplayFontFamily(),
      ),
      profileTheme: ProfileTheme.dark(),
    );
    return MaterialApp(
      onGenerateTitle: (context) => context.l10n.appTitle,
      theme: lightTheme,
      darkTheme: darkTheme,
      themeMode: themeMode.materialMode,
      locale: locale.materialLocale,
      supportedLocales: AppLocalizations.supportedLocales,
      localizationsDelegates: const [
        AppLocalizations.delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      themeAnimationDuration: const Duration(milliseconds: 520),
      themeAnimationCurve: Curves.easeInOutCubic,
      home: SplashScreen(
        readyToReveal: _bootstrapResolved,
        child: _SupabaseBootstrapGate(bootstrapFuture: _bootstrapFuture),
      ),
    );
  }
}

class _SupabaseBootstrapGate extends StatelessWidget {
  const _SupabaseBootstrapGate({required this.bootstrapFuture});

  final Future<bool> bootstrapFuture;

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<bool>(
      future: bootstrapFuture,
      builder: (context, snapshot) {
        if (snapshot.connectionState != ConnectionState.done) {
          return const SizedBox.expand();
        }
        final ready = snapshot.data == true && SupabaseBootstrap.isInitialized;
        if (ready) {
          return const AuthGate();
        }
        return _SupabaseConfigErrorScreen(message: SupabaseBootstrap.lastError);
      },
    );
  }
}

class _SupabaseConfigErrorScreen extends StatelessWidget {
  const _SupabaseConfigErrorScreen({this.message});

  final String? message;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    return Scaffold(
      body: SafeArea(
        child: Center(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  l10n.supabaseConfigErrorTitle,
                  style: TextStyle(fontSize: 20, fontWeight: FontWeight.w700),
                ),
                const SizedBox(height: 12),
                Text(message ?? l10n.supabaseConfigErrorBody),
                const SizedBox(height: 16),
                Text(l10n.supabaseConfigErrorExample),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
