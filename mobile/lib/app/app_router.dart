import 'package:go_router/go_router.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import 'auth/auth_gate.dart';
import 'auth/login_page.dart';
import 'auth/register_page.dart';
import 'onboarding/onboarding_profile_page.dart';
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
