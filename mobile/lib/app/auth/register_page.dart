import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:mobile/app/onboarding/onboarding_birth_page.dart';
import 'package:mobile/design/theme/profile_theme_extension.dart';
import 'package:mobile/design/widgets/jovia_editorial.dart';
import 'package:mobile/l10n/l10n.dart';

import 'auth_debug_state.dart';
import 'user_bootstrap.dart';

class RegisterPage extends StatefulWidget {
  const RegisterPage({super.key});

  @override
  State<RegisterPage> createState() => _RegisterPageState();
}

class _RegisterPageState extends State<RegisterPage> {
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmController = TextEditingController();
  bool _isLoading = false;
  String? _error;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    _confirmController.dispose();
    super.dispose();
  }

  Future<void> _register() async {
    if (_passwordController.text != _confirmController.text) {
      setState(() {
        _error = context.l10n.registerPasswordsDoNotMatch;
      });
      return;
    }

    setState(() {
      _isLoading = true;
      _error = null;
    });
    try {
      final authResponse = await Supabase.instance.client.auth.signUp(
        email: _emailController.text.trim(),
        password: _passwordController.text,
      );
      await ensureUserRows(user: authResponse.user);
      AuthDebugState.instance.clearAuthError();
      if (mounted) {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (_) => const OnboardingBirthPage()),
        );
      }
    } on AuthException catch (exc) {
      AuthDebugState.instance.setAuthError(
        code: 'auth_exception',
        message: exc.message,
      );
      setState(() {
        _error = _friendlyAuthError(exc);
      });
    } catch (e) {
      final message = e.toString();
      AuthDebugState.instance.setAuthError(code: 'unknown', message: message);
      setState(() {
        _error = message;
      });
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  String _friendlyAuthError(AuthException e) {
    return _withDebugCode('auth_exception', e.message);
  }

  String _withDebugCode(String code, String message) {
    if (kDebugMode) {
      return '$code: $message';
    }
    return message;
  }

  @override
  Widget build(BuildContext context) {
    final bottomInset = MediaQuery.of(context).viewInsets.bottom;
    final profile = context.profileTheme;
    final spacing = profile.spacing;
    final l10n = context.l10n;

    return Scaffold(
      body: SafeArea(
        child: LayoutBuilder(
          builder: (context, constraints) => SingleChildScrollView(
            keyboardDismissBehavior: ScrollViewKeyboardDismissBehavior.onDrag,
            padding: EdgeInsets.fromLTRB(
              spacing.s24,
              spacing.s20,
              spacing.s24,
              spacing.s20 + bottomInset,
            ),
            child: ConstrainedBox(
              constraints: BoxConstraints(
                minHeight: constraints.maxHeight - spacing.s40,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  JoviaProfileTopBar(
                    label: l10n.registerTopLabel,
                    centerText: l10n.registerTopCenter,
                    reserveTrailingSpace: true,
                  ),
                  SizedBox(height: spacing.s16),
                  const Align(
                    alignment: Alignment.centerLeft,
                    child: JoviaBrandMark(width: 62, opacity: 0.84),
                  ),
                  SizedBox(height: spacing.s24),
                  JoviaSectionHeader(
                    label: l10n.registerSectionLabel,
                    title: l10n.registerTitle,
                    body: l10n.registerBody,
                    variant: JoviaSectionHeaderVariant.editorial,
                  ),
                  SizedBox(height: spacing.s24),
                  JoviaSurfaceCard(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        TextField(
                          controller: _emailController,
                          keyboardType: TextInputType.emailAddress,
                          decoration: InputDecoration(
                            labelText: l10n.emailLabel,
                          ),
                        ),
                        SizedBox(height: spacing.s12),
                        TextField(
                          controller: _passwordController,
                          obscureText: true,
                          decoration: InputDecoration(
                            labelText: l10n.passwordLabel,
                          ),
                        ),
                        SizedBox(height: spacing.s12),
                        TextField(
                          controller: _confirmController,
                          obscureText: true,
                          decoration: InputDecoration(
                            labelText: l10n.confirmPasswordLabel,
                          ),
                        ),
                        if (_error != null) ...[
                          SizedBox(height: spacing.s16),
                          Text(
                            _error!,
                            style: profile.typography.meta.copyWith(
                              color: Theme.of(context).colorScheme.error,
                            ),
                          ),
                        ],
                        SizedBox(height: spacing.s16),
                        SizedBox(
                          width: double.infinity,
                          child: ElevatedButton(
                            onPressed: _isLoading ? null : _register,
                            child: _isLoading
                                ? const SizedBox(
                                    height: 18,
                                    width: 18,
                                    child: CircularProgressIndicator(
                                      strokeWidth: 2,
                                    ),
                                  )
                                : Text(l10n.registerCreateAccount),
                          ),
                        ),
                        SizedBox(height: spacing.s8),
                        Align(
                          alignment: Alignment.centerLeft,
                          child: TextButton(
                            onPressed: () => Navigator.of(context).pop(),
                            child: Text(l10n.registerBackToLogin),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
