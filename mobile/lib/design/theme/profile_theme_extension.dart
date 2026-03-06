import 'dart:ui' show lerpDouble;

import 'package:flutter/material.dart';

import 'package:mobile/design/tokens/profile_tokens.dart';
import 'package:mobile/design/typography/profile_typography.dart';

@immutable
class ProfileTheme extends ThemeExtension<ProfileTheme> {
  const ProfileTheme({
    required this.colors,
    required this.radii,
    required this.spacing,
    required this.shadows,
    required this.typography,
  });

  final ProfileColors colors;
  final ProfileRadii radii;
  final ProfileSpacing spacing;
  final ProfileShadows shadows;
  final ProfileTypography typography;

  factory ProfileTheme.light() {
    const colors = ProfileColors.light;
    return ProfileTheme(
      colors: colors,
      radii: ProfileRadii.standard,
      spacing: ProfileSpacing.standard,
      shadows: ProfileShadows.soft,
      typography: ProfileTypography.fromColor(colors.text, colors.textLight),
    );
  }

  static final _fallback = ProfileTheme.light();

  static ProfileTheme fallback() => _fallback;

  @override
  ProfileTheme copyWith({
    ProfileColors? colors,
    ProfileRadii? radii,
    ProfileSpacing? spacing,
    ProfileShadows? shadows,
    ProfileTypography? typography,
  }) {
    return ProfileTheme(
      colors: colors ?? this.colors,
      radii: radii ?? this.radii,
      spacing: spacing ?? this.spacing,
      shadows: shadows ?? this.shadows,
      typography: typography ?? this.typography,
    );
  }

  @override
  ProfileTheme lerp(covariant ThemeExtension<ProfileTheme>? other, double t) {
    if (other is! ProfileTheme) {
      return this;
    }
    return ProfileTheme(
      colors: ProfileColors(
        bg: Color.lerp(colors.bg, other.colors.bg, t) ?? colors.bg,
        surface:
            Color.lerp(colors.surface, other.colors.surface, t) ??
            colors.surface,
        text: Color.lerp(colors.text, other.colors.text, t) ?? colors.text,
        muted: Color.lerp(colors.muted, other.colors.muted, t) ?? colors.muted,
        textLight:
            Color.lerp(colors.textLight, other.colors.textLight, t) ??
            colors.textLight,
        primary:
            Color.lerp(colors.primary, other.colors.primary, t) ??
            colors.primary,
        lime: Color.lerp(colors.lime, other.colors.lime, t) ?? colors.lime,
        lavender:
            Color.lerp(colors.lavender, other.colors.lavender, t) ??
            colors.lavender,
        border:
            Color.lerp(colors.border, other.colors.border, t) ?? colors.border,
        strokeSoft:
            Color.lerp(colors.strokeSoft, other.colors.strokeSoft, t) ??
            colors.strokeSoft,
        separator:
            Color.lerp(colors.separator, other.colors.separator, t) ??
            colors.separator,
        auraStops: List<Color>.generate(
          3,
          (index) =>
              Color.lerp(
                colors.auraStops[index],
                other.colors.auraStops[index],
                t,
              ) ??
              colors.auraStops[index],
        ),
        chipBg:
            Color.lerp(colors.chipBg, other.colors.chipBg, t) ?? colors.chipBg,
        chipBorder:
            Color.lerp(colors.chipBorder, other.colors.chipBorder, t) ??
            colors.chipBorder,
        warmAccent:
            Color.lerp(colors.warmAccent, other.colors.warmAccent, t) ??
            colors.warmAccent,
        heroText:
            Color.lerp(colors.heroText, other.colors.heroText, t) ??
            colors.heroText,
        heroBase:
            Color.lerp(colors.heroBase, other.colors.heroBase, t) ??
            colors.heroBase,
        neonPink:
            Color.lerp(colors.neonPink, other.colors.neonPink, t) ??
            colors.neonPink,
        neonCyan:
            Color.lerp(colors.neonCyan, other.colors.neonCyan, t) ??
            colors.neonCyan,
      ),
      radii: ProfileRadii(
        cardRadius:
            lerpDouble(radii.cardRadius, other.radii.cardRadius, t) ??
            radii.cardRadius,
        pillRadius:
            lerpDouble(radii.pillRadius, other.radii.pillRadius, t) ??
            radii.pillRadius,
      ),
      spacing: ProfileSpacing(
        xxs: lerpDouble(spacing.xxs, other.spacing.xxs, t) ?? spacing.xxs,
        xs: lerpDouble(spacing.xs, other.spacing.xs, t) ?? spacing.xs,
        sm: lerpDouble(spacing.sm, other.spacing.sm, t) ?? spacing.sm,
        md: lerpDouble(spacing.md, other.spacing.md, t) ?? spacing.md,
        lg: lerpDouble(spacing.lg, other.spacing.lg, t) ?? spacing.lg,
        xl: lerpDouble(spacing.xl, other.spacing.xl, t) ?? spacing.xl,
        xxl: lerpDouble(spacing.xxl, other.spacing.xxl, t) ?? spacing.xxl,
        xxxl: lerpDouble(spacing.xxxl, other.spacing.xxxl, t) ?? spacing.xxxl,
      ),
      shadows: ProfileShadows(
        cardShadow:
            BoxShadow.lerp(shadows.cardShadow, other.shadows.cardShadow, t) ??
            shadows.cardShadow,
        floatingShadow:
            BoxShadow.lerp(
              shadows.floatingShadow,
              other.shadows.floatingShadow,
              t,
            ) ??
            shadows.floatingShadow,
      ),
      typography: ProfileTypography(
        hero:
            TextStyle.lerp(typography.hero, other.typography.hero, t) ??
            typography.hero,
        section:
            TextStyle.lerp(typography.section, other.typography.section, t) ??
            typography.section,
        card:
            TextStyle.lerp(typography.card, other.typography.card, t) ??
            typography.card,
        body:
            TextStyle.lerp(typography.body, other.typography.body, t) ??
            typography.body,
        meta:
            TextStyle.lerp(typography.meta, other.typography.meta, t) ??
            typography.meta,
      ),
    );
  }
}

ThemeData withProfileTheme(ThemeData base, {ProfileTheme? profileTheme}) {
  final resolved = profileTheme ?? ProfileTheme.light();
  final extensions = List<ThemeExtension<dynamic>>.from(base.extensions.values);
  extensions.removeWhere((ext) => ext is ProfileTheme);
  extensions.add(resolved);
  return base.copyWith(extensions: extensions);
}

extension ProfileThemeBuildContextX on BuildContext {
  ProfileTheme get profileTheme =>
      Theme.of(this).extension<ProfileTheme>() ?? ProfileTheme.fallback();
}
