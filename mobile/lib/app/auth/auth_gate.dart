import 'package:flutter/material.dart';
import 'package:mobile/app/telemetry/perf_telemetry.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:mobile/app/onboarding/onboarding_birth_page.dart';
import 'package:mobile/app/profile/profile_repository.dart';
import 'package:mobile/app/tabs/tabs_shell.dart';
import 'package:mobile/app/auth/login_page.dart';
import 'package:mobile/design/theme/profile_theme_extension.dart';
import 'package:mobile/design/widgets/jovia_editorial.dart';
import 'package:mobile/l10n/l10n.dart';

enum BirthDataGateTarget { tabs, onboarding, retry }

class BirthDataGateDecision {
  const BirthDataGateDecision._({required this.target, this.error});

  const BirthDataGateDecision.tabs() : this._(target: BirthDataGateTarget.tabs);

  const BirthDataGateDecision.onboarding()
    : this._(target: BirthDataGateTarget.onboarding);

  const BirthDataGateDecision.retry({Object? error})
    : this._(target: BirthDataGateTarget.retry, error: error);

  final BirthDataGateTarget target;
  final Object? error;
}

bool profileHasBirthData(Map<String, dynamic>? row) {
  return row != null &&
      row['birth_date'] != null &&
      (row['place'] ?? '').toString().trim().isNotEmpty;
}

Future<BirthDataGateDecision> loadBirthDataGateDecision({
  required String userId,
  required Future<Map<String, dynamic>?> Function(String userId) profileLoader,
}) async {
  final span = PerfTelemetry.startSpan(
    'auth_gate',
    finishEvent: 'auth_gate_resolved',
    data: <String, Object?>{
      'has_session': true,
      'user_id_present': userId.trim().isNotEmpty,
    },
  );
  try {
    final row = await profileLoader(userId);
    final hasBirth = profileHasBirthData(row);
    debugPrint(
      'AUTH_GATE_BIRTH_CHECK user=$userId hasBirth=$hasBirth row=$row',
    );
    span.finish(
      data: <String, Object?>{
        'target': hasBirth ? 'tabs' : 'onboarding',
        'has_birth_data': hasBirth,
      },
    );
    return hasBirth
        ? const BirthDataGateDecision.tabs()
        : const BirthDataGateDecision.onboarding();
  } catch (error) {
    debugPrint('AUTH_GATE_BIRTH_CHECK_ERROR user=$userId error=$error');
    span.finish(
      status: 'error',
      data: <String, Object?>{
        'target': 'retry',
        'error_type': error.runtimeType.toString(),
      },
    );
    return BirthDataGateDecision.retry(error: error);
  }
}

class AuthGate extends StatelessWidget {
  const AuthGate({super.key, this.profileLoader});

  final Future<Map<String, dynamic>?> Function(String userId)? profileLoader;

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
          PerfTelemetry.logPointOnce(
            'startup.auth_gate_no_session_start',
            'auth_gate_start',
            data: const <String, Object?>{'has_session': false},
          );
          PerfTelemetry.logPointOnce(
            'startup.auth_gate_login_resolved',
            'auth_gate_resolved',
            data: const <String, Object?>{
              'has_session': false,
              'target': 'login',
            },
          );
          return const LoginPage();
        }
        return _BirthDataGate(
          userId: session.user.id,
          profileLoader:
              profileLoader ?? ProfileRepository().getBirthGateProfile,
        );
      },
    );
  }
}

class _BirthDataGate extends StatefulWidget {
  const _BirthDataGate({required this.userId, required this.profileLoader});

  final String userId;
  final Future<Map<String, dynamic>?> Function(String userId) profileLoader;

  @override
  State<_BirthDataGate> createState() => _BirthDataGateState();
}

class _BirthDataGateState extends State<_BirthDataGate> {
  late Future<BirthDataGateDecision> _future;

  @override
  void initState() {
    super.initState();
    _future = _loadDecision();
  }

  Future<BirthDataGateDecision> _loadDecision() {
    return loadBirthDataGateDecision(
      userId: widget.userId,
      profileLoader: widget.profileLoader,
    );
  }

  void _retry() {
    setState(() {
      _future = _loadDecision();
    });
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<BirthDataGateDecision>(
      future: _future,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Scaffold(
            body: Center(child: CircularProgressIndicator()),
          );
        }
        final decision = snapshot.data ?? const BirthDataGateDecision.retry();
        switch (decision.target) {
          case BirthDataGateTarget.tabs:
            return const TabsShell();
          case BirthDataGateTarget.onboarding:
            return const OnboardingBirthPage();
          case BirthDataGateTarget.retry:
            return _BirthDataRetryPage(error: decision.error, onRetry: _retry);
        }
      },
    );
  }
}

class _BirthDataRetryPage extends StatelessWidget {
  const _BirthDataRetryPage({required this.error, required this.onRetry});

  final Object? error;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final spacing = profile.spacing;
    final l10n = context.l10n;

    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: EdgeInsets.all(spacing.s24),
          child: Center(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 460),
              child: JoviaSurfaceCard(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Text(
                      l10n.authGateBirthDataErrorTitle,
                      style: profile.typography.sectionTitle.copyWith(
                        fontSize: 28,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    SizedBox(height: spacing.s12),
                    Text(
                      l10n.authGateBirthDataErrorBody,
                      style: profile.typography.bodyCompact.copyWith(
                        color: profile.colors.textLight,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    if (error != null) ...[
                      SizedBox(height: spacing.s16),
                      Text(
                        error.toString(),
                        style: profile.typography.meta.copyWith(
                          color: Theme.of(context).colorScheme.error,
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ],
                    SizedBox(height: spacing.s20),
                    JoviaPrimaryButton(label: l10n.commonRetry, onTap: onRetry),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
