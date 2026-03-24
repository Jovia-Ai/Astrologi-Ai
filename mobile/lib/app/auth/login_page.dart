import 'dart:math' as math;

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:mobile/app/onboarding/onboarding_birth_page.dart';
import 'package:mobile/design/theme/profile_theme_extension.dart';
import 'package:mobile/design/widgets/jovia_editorial.dart';

import 'user_bootstrap.dart';

const String _kLoginTitle = 'Tekrar hos geldin';
const String _kLoginBody = 'Hesabina gir ve kaldigin yerden devam et.';
const String _kDarkLogoAsset = 'ios/Flutter/assets/logo/shou_logo.svg';
const String _kLightLogoAsset = 'ios/Flutter/assets/logo/shou_logo_light.svg';
const double _kLoginMaxContentWidth = 460;
const double _kLogoWidthFactor = 0.25;
const double _kLogoMinWidth = 92;
const double _kLogoMaxWidth = 132;
const String _kGoogleRedirectTo = 'com.sahra.jovia://login-callback/';

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final _email = TextEditingController();
  final _password = TextEditingController();
  bool _loading = false;
  String? _error;

  @override
  void dispose() {
    _email.dispose();
    _password.dispose();
    super.dispose();
  }

  Future<void> _signIn() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final authResponse = await Supabase.instance.client.auth
          .signInWithPassword(
            email: _email.text.trim(),
            password: _password.text,
          );
      await ensureUserRows(user: authResponse.user);
    } on AuthException catch (e) {
      setState(() => _error = e.message);
    } catch (e) {
      setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _signUp() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final authResponse = await Supabase.instance.client.auth.signUp(
        email: _email.text.trim(),
        password: _password.text,
      );
      await ensureUserRows(user: authResponse.user);
      if (mounted) {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (_) => const OnboardingBirthPage()),
        );
      }
    } on AuthException catch (e) {
      setState(() => _error = e.message);
    } catch (e) {
      setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _resetPassword() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      await Supabase.instance.client.auth.resetPasswordForEmail(
        _email.text.trim(),
      );
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Password reset email sent')),
        );
      }
    } on AuthException catch (e) {
      setState(() => _error = e.message);
    } catch (e) {
      setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _signInWithGoogle() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final launched = await Supabase.instance.client.auth.signInWithOAuth(
        OAuthProvider.google,
        redirectTo: kIsWeb ? null : _kGoogleRedirectTo,
      );
      if (!launched && mounted) {
        setState(() => _error = 'Google giris akisi baslatilamadi.');
      }
    } on AuthException catch (e) {
      setState(() => _error = e.message);
    } catch (e) {
      setState(() => _error = e.toString());
    } finally {
      if (mounted) {
        setState(() => _loading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final bottomInset = MediaQuery.of(context).viewInsets.bottom;
    final profile = context.profileTheme;
    final spacing = profile.spacing;
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;
    final backgroundTop = Color.alphaBlend(
      profile.colors.primary.withValues(alpha: isDark ? 0.12 : 0.08),
      profile.colors.heroBase,
    );
    final inputFill = isDark
        ? Colors.white.withValues(alpha: 0.06)
        : Colors.white.withValues(alpha: 0.78);
    final inputBorder = profile.colors.strokeSoft.withValues(
      alpha: isDark ? 0.84 : 1,
    );
    final primaryForeground = isDark ? const Color(0xFF17151F) : Colors.white;

    return Scaffold(
      body: DecoratedBox(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [backgroundTop, profile.colors.bg, profile.colors.bg],
            stops: const [0, 0.34, 1],
          ),
        ),
        child: Stack(
          fit: StackFit.expand,
          children: [
            IgnorePointer(
              child: Stack(
                children: [
                  Positioned(
                    top: -72,
                    right: -28,
                    child: _AmbientGlow(
                      size: 220,
                      color: profile.colors.primary.withValues(
                        alpha: isDark ? 0.16 : 0.1,
                      ),
                    ),
                  ),
                  Positioned(
                    left: -84,
                    bottom: 112,
                    child: _AmbientGlow(
                      size: 180,
                      color: profile.colors.warmAccent.withValues(
                        alpha: isDark ? 0.1 : 0.07,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            SafeArea(
              child: LayoutBuilder(
                builder: (context, constraints) {
                  final contentWidth = math.min(
                    constraints.maxWidth,
                    _kLoginMaxContentWidth,
                  );
                  final logoWidth = (constraints.maxWidth * _kLogoWidthFactor)
                      .clamp(_kLogoMinWidth, _kLogoMaxWidth)
                      .toDouble();

                  return SingleChildScrollView(
                    keyboardDismissBehavior:
                        ScrollViewKeyboardDismissBehavior.onDrag,
                    padding: EdgeInsets.fromLTRB(
                      spacing.s24,
                      spacing.s24 + spacing.s8,
                      spacing.s24,
                      spacing.s24 + bottomInset,
                    ),
                    child: ConstrainedBox(
                      constraints: BoxConstraints(
                        minHeight: constraints.maxHeight - spacing.s32,
                      ),
                      child: Align(
                        alignment: Alignment.topCenter,
                        child: SizedBox(
                          width: contentWidth,
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.stretch,
                            children: [
                              SizedBox(height: spacing.s20),
                              JoviaReveal(
                                child: _LoginBrandHeader(
                                  logoWidth: logoWidth,
                                  isDark: isDark,
                                ),
                              ),
                              SizedBox(height: spacing.s32 + spacing.s8),
                              JoviaReveal(
                                delay: const Duration(milliseconds: 90),
                                child: JoviaSurfaceCard(
                                  backgroundColor: profile.colors.surface
                                      .withValues(alpha: isDark ? 0.72 : 0.84),
                                  borderColor: inputBorder.withValues(
                                    alpha: isDark ? 0.78 : 0.92,
                                  ),
                                  padding: EdgeInsets.fromLTRB(
                                    spacing.s20,
                                    spacing.s20,
                                    spacing.s20,
                                    spacing.s16,
                                  ),
                                  child: AutofillGroup(
                                    child: Column(
                                      crossAxisAlignment:
                                          CrossAxisAlignment.stretch,
                                      children: [
                                        TextField(
                                          controller: _email,
                                          keyboardType:
                                              TextInputType.emailAddress,
                                          textInputAction: TextInputAction.next,
                                          autofillHints: const [
                                            AutofillHints.username,
                                            AutofillHints.email,
                                          ],
                                          decoration: _inputDecoration(
                                            context,
                                            hintText: 'Email',
                                            fillColor: inputFill,
                                            borderColor: inputBorder,
                                          ),
                                        ),
                                        SizedBox(height: spacing.s12),
                                        TextField(
                                          controller: _password,
                                          obscureText: true,
                                          textInputAction: TextInputAction.done,
                                          autofillHints: const [
                                            AutofillHints.password,
                                          ],
                                          onSubmitted: (_) {
                                            if (!_loading) {
                                              _signIn();
                                            }
                                          },
                                          decoration: _inputDecoration(
                                            context,
                                            hintText: 'Password',
                                            fillColor: inputFill,
                                            borderColor: inputBorder,
                                          ),
                                        ),
                                        if (_error != null) ...[
                                          SizedBox(height: spacing.s12),
                                          Text(
                                            _error!,
                                            style: profile.typography.meta
                                                .copyWith(
                                                  color:
                                                      theme.colorScheme.error,
                                                ),
                                          ),
                                        ],
                                        SizedBox(height: spacing.s24),
                                        SizedBox(
                                          height: 56,
                                          child: ElevatedButton(
                                            onPressed: _loading
                                                ? null
                                                : _signIn,
                                            style: ElevatedButton.styleFrom(
                                              backgroundColor:
                                                  profile.colors.primary,
                                              foregroundColor:
                                                  primaryForeground,
                                              disabledBackgroundColor: profile
                                                  .colors
                                                  .primary
                                                  .withValues(alpha: 0.5),
                                              disabledForegroundColor:
                                                  primaryForeground.withValues(
                                                    alpha: 0.7,
                                                  ),
                                              elevation: 0,
                                              shape: RoundedRectangleBorder(
                                                borderRadius:
                                                    BorderRadius.circular(
                                                      profile.radii.cardRadius *
                                                          0.9,
                                                    ),
                                              ),
                                              textStyle: profile
                                                  .typography
                                                  .cardTitle
                                                  .copyWith(
                                                    color: primaryForeground,
                                                    fontSize: 16,
                                                  ),
                                            ),
                                            child: _loading
                                                ? SizedBox(
                                                    height: 18,
                                                    width: 18,
                                                    child:
                                                        CircularProgressIndicator(
                                                          strokeWidth: 2,
                                                          color:
                                                              primaryForeground,
                                                        ),
                                                  )
                                                : const Text('Giris yap'),
                                          ),
                                        ),
                                        SizedBox(height: spacing.s16),
                                        _AuthDivider(
                                          label: 'veya',
                                          color: profile.colors.separator,
                                          textColor: profile.colors.textLight,
                                        ),
                                        SizedBox(height: spacing.s16),
                                        SizedBox(
                                          height: 54,
                                          child: OutlinedButton(
                                            onPressed: _loading
                                                ? null
                                                : _signInWithGoogle,
                                            style: OutlinedButton.styleFrom(
                                              side: BorderSide(
                                                color: inputBorder.withValues(
                                                  alpha: isDark ? 0.9 : 1,
                                                ),
                                              ),
                                              backgroundColor: inputFill,
                                              foregroundColor:
                                                  profile.colors.text,
                                              shape: RoundedRectangleBorder(
                                                borderRadius:
                                                    BorderRadius.circular(
                                                      profile.radii.cardRadius *
                                                          0.8,
                                                    ),
                                              ),
                                              textStyle: profile
                                                  .typography
                                                  .chipLabel
                                                  .copyWith(fontSize: 14),
                                            ),
                                            child: Row(
                                              mainAxisAlignment:
                                                  MainAxisAlignment.center,
                                              mainAxisSize: MainAxisSize.min,
                                              children: [
                                                const _GoogleBadge(),
                                                SizedBox(width: spacing.s12),
                                                const Text(
                                                  'Google ile devam et',
                                                ),
                                              ],
                                            ),
                                          ),
                                        ),
                                        SizedBox(height: spacing.s12),
                                        Align(
                                          alignment: Alignment.center,
                                          child: TextButton(
                                            onPressed: _loading
                                                ? null
                                                : _signUp,
                                            style: TextButton.styleFrom(
                                              foregroundColor:
                                                  profile.colors.muted,
                                              textStyle: profile
                                                  .typography
                                                  .chipLabel
                                                  .copyWith(
                                                    color: profile.colors.muted,
                                                  ),
                                            ),
                                            child: const Text('Hesap olustur'),
                                          ),
                                        ),
                                        SizedBox(height: spacing.s4),
                                        Align(
                                          alignment: Alignment.centerLeft,
                                          child: TextButton(
                                            onPressed: _loading
                                                ? null
                                                : _resetPassword,
                                            style: TextButton.styleFrom(
                                              padding:
                                                  const EdgeInsets.symmetric(
                                                    horizontal: 0,
                                                    vertical: 4,
                                                  ),
                                              minimumSize: Size.zero,
                                              tapTargetSize:
                                                  MaterialTapTargetSize
                                                      .shrinkWrap,
                                              foregroundColor:
                                                  profile.colors.textLight,
                                              textStyle: profile.typography.meta
                                                  .copyWith(
                                                    color: profile
                                                        .colors
                                                        .textLight,
                                                  ),
                                            ),
                                            child: const Text(
                                              'Sifremi unuttum',
                                            ),
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }

  InputDecoration _inputDecoration(
    BuildContext context, {
    required String hintText,
    required Color fillColor,
    required Color borderColor,
  }) {
    final profile = context.profileTheme;
    final radius = BorderRadius.circular(profile.radii.cardRadius * 0.8);
    return InputDecoration(
      hintText: hintText,
      fillColor: fillColor,
      contentPadding: EdgeInsets.symmetric(
        horizontal: profile.spacing.s20,
        vertical: profile.spacing.s16,
      ),
      border: OutlineInputBorder(
        borderRadius: radius,
        borderSide: BorderSide(color: borderColor),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: radius,
        borderSide: BorderSide(color: borderColor),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: radius,
        borderSide: BorderSide(color: profile.colors.primary, width: 1.2),
      ),
    );
  }
}

class _LoginBrandHeader extends StatelessWidget {
  const _LoginBrandHeader({required this.logoWidth, required this.isDark});

  final double logoWidth;
  final bool isDark;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final logoAsset = isDark ? _kDarkLogoAsset : _kLightLogoAsset;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        SvgPicture.asset(logoAsset, width: logoWidth, fit: BoxFit.contain),
        SizedBox(height: profile.spacing.s24),
        Text(
          _kLoginTitle,
          textAlign: TextAlign.center,
          style: profile.typography.heroEditorial.copyWith(
            color: profile.colors.heroText,
            fontSize: 42,
            height: 46 / 42,
          ),
        ),
        SizedBox(height: profile.spacing.s8),
        Text(
          _kLoginBody,
          textAlign: TextAlign.center,
          style: profile.typography.bodyCompact.copyWith(
            color: profile.colors.textLight,
            height: 1.45,
          ),
        ),
      ],
    );
  }
}

class _AmbientGlow extends StatelessWidget {
  const _AmbientGlow({required this.size, required this.color});

  final double size;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        boxShadow: [BoxShadow(color: color, blurRadius: 96, spreadRadius: 16)],
      ),
    );
  }
}

class _AuthDivider extends StatelessWidget {
  const _AuthDivider({
    required this.label,
    required this.color,
    required this.textColor,
  });

  final String label;
  final Color color;
  final Color textColor;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Row(
      children: [
        Expanded(child: Divider(color: color)),
        Padding(
          padding: EdgeInsets.symmetric(horizontal: profile.spacing.s12),
          child: Text(
            label,
            style: profile.typography.meta.copyWith(color: textColor),
          ),
        ),
        Expanded(child: Divider(color: color)),
      ],
    );
  }
}

class _GoogleBadge extends StatelessWidget {
  const _GoogleBadge();

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 24,
      height: 24,
      alignment: Alignment.center,
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(999),
      ),
      child: const Text(
        'G',
        style: TextStyle(
          color: Color(0xFF4285F4),
          fontSize: 14,
          fontWeight: FontWeight.w700,
        ),
      ),
    );
  }
}
