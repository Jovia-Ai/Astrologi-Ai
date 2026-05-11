import 'package:go_router/go_router.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import 'auth/auth_gate.dart';
import 'auth/login_page.dart';
import 'auth/register_page.dart';
import 'onboarding/onboarding_profile_page.dart';
import 'tabs/home_page_v2.dart';
import 'tabs/profile_page_v9.dart';
import 'tabs/tabs_shell.dart';

GoRouter buildRouter() {
  return GoRouter(
    initialLocation: '/',
    routes: [
      GoRoute(path: '/', builder: (context, state) => const AuthGate()),
      GoRoute(path: '/login', builder: (context, state) => const LoginPage()),
      GoRoute(
        path: '/register',
        builder: (context, state) => const RegisterPage(),
      ),
      GoRoute(
        path: '/onboarding_profile',
        builder: (context, state) => const OnboardingProfilePage(),
      ),
      GoRoute(path: '/tabs', builder: (context, state) => const TabsShell()),
      // Dev-only: yeni Home v12 tasarımı. Prod Bugün tab'ı legacy'de kalır.
      GoRoute(
        path: '/dev/home-v2',
        builder: (context, state) => const HomePageV2(),
      ),
      // Dev-only: paralel "iceberg" Profile (v9). Prod Profile tab'ı legacy'de
      // kalır; v9 olgunlaştığında eski [profile_page.dart] silinir.
      GoRoute(
        path: '/dev/profile-v9',
        builder: (context, state) => const ProfilePageV9(),
      ),
    ],
    redirect: (context, state) {
      final session = Supabase.instance.client.auth.currentSession;
      final isLoggedIn = session != null;
      final location = state.uri.path;
      final isRoot = location == '/';
      final isAuthPage =
          location == '/login' || location == '/register' || isRoot;

      if (!isLoggedIn) {
        if (isAuthPage) {
          return null;
        }
        return '/';
      }

      if (location == '/login' || location == '/register') {
        return '/';
      }

      return null;
    },
  );
}
