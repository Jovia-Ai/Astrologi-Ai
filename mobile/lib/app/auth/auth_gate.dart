import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:mobile/app/data/supabase_tables.dart';
import 'package:mobile/app/onboarding/onboarding_birth_page.dart';
import 'package:mobile/app/tabs/tabs_shell.dart';
import 'package:mobile/app/auth/login_page.dart';

class AuthGate extends StatelessWidget {
  const AuthGate({super.key});

  @override
  Widget build(BuildContext context) {
    debugPrint(
      'AUTH_GATE_BUILD session=${Supabase.instance.client.auth.currentSession != null}',
    );
    return StreamBuilder<AuthState>(
      stream: Supabase.instance.client.auth.onAuthStateChange,
      builder: (context, snapshot) {
        final session = Supabase.instance.client.auth.currentSession;
        if (session == null) {
          return const LoginPage();
        }
        return _BirthDataGate(userId: session.user.id);
      },
    );
  }
}

class _BirthDataGate extends StatelessWidget {
  const _BirthDataGate({required this.userId});

  final String userId;

  Future<bool> _hasBirthData() async {
    try {
      final row = await Supabase.instance.client
          .from(SupabaseTables.birthData)
          .select('birth_date, place')
          .eq('user_id', userId)
          .limit(1)
          .maybeSingle();

      final hasBirth =
          row != null &&
          row['birth_date'] != null &&
          (row['place'] ?? '').toString().trim().isNotEmpty;
      debugPrint(
        'AUTH_GATE_BIRTH_CHECK user=$userId hasBirth=$hasBirth row=$row',
      );
      return hasBirth;
    } catch (e) {
      debugPrint('AUTH_GATE_BIRTH_CHECK_ERROR user=$userId error=$e');
      return false;
    }
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<bool>(
      future: _hasBirthData(),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Scaffold(
            body: Center(child: CircularProgressIndicator()),
          );
        }
        if (snapshot.data == true) {
          return const TabsShell();
        }
        return const OnboardingBirthPage();
      },
    );
  }
}
