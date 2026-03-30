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
    required this.motion,
    required this.typography,
  });

  final ProfileColors colors;
  final ProfileRadii radii;
  final ProfileSpacing spacing;
  final ProfileShadows shadows;
  final ProfileMotion motion;
  final ProfileTypography typography;

  factory ProfileTheme.light() {
    const colors = ProfileColors.light;
    return ProfileTheme(
      colors: colors,
      radii: ProfileRadii.standard,
      spacing: ProfileSpacing.standard,
      shadows: ProfileShadows.soft,
      motion: ProfileMotion.soft,
      typography: ProfileTypography.fromColors(
        textColor: colors.text,
        secondaryColor: colors.muted,
        mutedLabelColor: colors.textLight,
      ),
    );
  }

  factory ProfileTheme.dark() {
    const colors = ProfileColors.dark;
    return ProfileTheme(
      colors: colors,
      radii: ProfileRadii.standard,
      spacing: ProfileSpacing.standard,
      shadows: ProfileShadows.soft,
      motion: ProfileMotion.soft,
      typography: ProfileTypography.fromColors(
        textColor: colors.text,
        secondaryColor: colors.muted,
        mutedLabelColor: colors.textLight,
      ),
    );
  }

  static final _fallback = ProfileTheme.dark();

  static ProfileTheme fallback() => _fallback;

  @override
  ProfileTheme copyWith({
    ProfileColors? colors,
    ProfileRadii? radii,
    ProfileSpacing? spacing,
    ProfileShadows? shadows,
    ProfileMotion? motion,
    ProfileTypography? typography,
  }) {
    return ProfileTheme(
      colors: colors ?? this.colors,
      radii: radii ?? this.radii,
      spacing: spacing ?? this.spacing,
      shadows: shadows ?? this.shadows,
      motion: motion ?? this.motion,
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
        small: lerpDouble(radii.small, other.radii.small, t) ?? radii.small,
        medium: lerpDouble(radii.medium, other.radii.medium, t) ?? radii.medium,
        large: lerpDouble(radii.large, other.radii.large, t) ?? radii.large,
        pillRadius:
            lerpDouble(radii.pillRadius, other.radii.pillRadius, t) ??
            radii.pillRadius,
      ),
      spacing: ProfileSpacing(
        xxs: lerpDouble(spacing.xxs, other.spacing.xxs, t) ?? spacing.xxs,
        xs: lerpDouble(spacing.xs, other.spacing.xs, t) ?? spacing.xs,
        sm: lerpDouble(spacing.sm, other.spacing.sm, t) ?? spacing.sm,
        md: lerpDouble(spacing.md, other.spacing.md, t) ?? spacing.md,
        step20:
            lerpDouble(spacing.step20, other.spacing.step20, t) ??
            spacing.step20,
        lg: lerpDouble(spacing.lg, other.spacing.lg, t) ?? spacing.lg,
        xl: lerpDouble(spacing.xl, other.spacing.xl, t) ?? spacing.xl,
        xxl: lerpDouble(spacing.xxl, other.spacing.xxl, t) ?? spacing.xxl,
        xxxl: lerpDouble(spacing.xxxl, other.spacing.xxxl, t) ?? spacing.xxxl,
        heroGap:
            lerpDouble(spacing.heroGap, other.spacing.heroGap, t) ??
            spacing.heroGap,
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
      motion: t < 0.5 ? motion : other.motion,
      typography: ProfileTypography(
        sectionLabel:
            TextStyle.lerp(
              typography.sectionLabel,
              other.typography.sectionLabel,
              t,
            ) ??
            typography.sectionLabel,
        pageTitle:
            TextStyle.lerp(
              typography.pageTitle,
              other.typography.pageTitle,
              t,
            ) ??
            typography.pageTitle,
        sectionTitle:
            TextStyle.lerp(
              typography.sectionTitle,
              other.typography.sectionTitle,
              t,
            ) ??
            typography.sectionTitle,
        cardTitle:
            TextStyle.lerp(
              typography.cardTitle,
              other.typography.cardTitle,
              t,
            ) ??
            typography.cardTitle,
        bodyLarge:
            TextStyle.lerp(
              typography.bodyLarge,
              other.typography.bodyLarge,
              t,
            ) ??
            typography.bodyLarge,
        bodyCompact:
            TextStyle.lerp(
              typography.bodyCompact,
              other.typography.bodyCompact,
              t,
            ) ??
            typography.bodyCompact,
        meta:
            TextStyle.lerp(typography.meta, other.typography.meta, t) ??
            typography.meta,
        chipLabel:
            TextStyle.lerp(
              typography.chipLabel,
              other.typography.chipLabel,
              t,
            ) ??
            typography.chipLabel,
        heroEditorial:
            TextStyle.lerp(
              typography.heroEditorial,
              other.typography.heroEditorial,
              t,
            ) ??
            typography.heroEditorial,
      ),
    );
  }
}

ThemeData withProfileTheme(ThemeData base, {ProfileTheme? profileTheme}) {
  final resolved =
      profileTheme ?? base.extension<ProfileTheme>() ?? ProfileTheme.fallback();
  final extensions = List<ThemeExtension<dynamic>>.from(base.extensions.values);
  extensions.removeWhere((ext) => ext is ProfileTheme);
  extensions.add(resolved);
  final textTheme = base.textTheme.copyWith(
    titleLarge: resolved.typography.pageTitle.copyWith(
      color: resolved.colors.text,
    ),
    titleMedium: resolved.typography.sectionTitle.copyWith(
      color: resolved.colors.text,
    ),
    titleSmall: resolved.typography.cardTitle.copyWith(
      color: resolved.colors.text,
    ),
    bodyLarge: resolved.typography.bodyLarge.copyWith(
      color: resolved.colors.text,
    ),
    bodyMedium: resolved.typography.bodyCompact.copyWith(
      color: resolved.colors.text,
    ),
    bodySmall: resolved.typography.meta.copyWith(color: resolved.colors.muted),
    labelLarge: resolved.typography.chipLabel.copyWith(
      color: resolved.colors.text,
    ),
    labelMedium: resolved.typography.meta.copyWith(
      color: resolved.colors.muted,
    ),
    labelSmall: resolved.typography.sectionLabel.copyWith(
      color: resolved.colors.textLight,
    ),
    headlineSmall: resolved.typography.pageTitle.copyWith(
      color: resolved.colors.text,
    ),
  );
  return base.copyWith(
    scaffoldBackgroundColor: resolved.colors.bg,
    dividerColor: resolved.colors.separator,
    cardColor: resolved.colors.surface,
    textTheme: textTheme,
    primaryTextTheme: textTheme,
    iconTheme: IconThemeData(color: resolved.colors.text, size: 20),
    splashColor: resolved.colors.primary.withValues(alpha: 0.05),
    highlightColor: Colors.transparent,
    dividerTheme: DividerThemeData(
      color: resolved.colors.separator,
      thickness: 1,
      space: 1,
    ),
    colorScheme: base.colorScheme.copyWith(
      surface: resolved.colors.surface,
      primary: resolved.colors.primary,
      onSurface: resolved.colors.text,
      onPrimary: Colors.white,
      secondary: resolved.colors.primary,
      outline: resolved.colors.strokeSoft,
      outlineVariant: resolved.colors.separator,
    ),
    cardTheme: CardThemeData(
      color: resolved.colors.panelSoft,
      elevation: 0,
      margin: EdgeInsets.zero,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(resolved.radii.cardRadius),
        side: BorderSide(color: resolved.colors.hairline),
      ),
    ),
    appBarTheme: AppBarTheme(
      backgroundColor: resolved.colors.bg,
      foregroundColor: resolved.colors.text,
      elevation: 0,
      scrolledUnderElevation: 0,
      surfaceTintColor: Colors.transparent,
      centerTitle: false,
      titleTextStyle: resolved.typography.pageTitle.copyWith(
        color: resolved.colors.text,
      ),
    ),
    tabBarTheme: TabBarThemeData(
      labelColor: resolved.colors.primary,
      unselectedLabelColor: resolved.colors.textLight,
      indicatorColor: resolved.colors.primary,
      dividerColor: resolved.colors.separator,
      labelStyle: resolved.typography.chipLabel.copyWith(
        color: resolved.colors.primary,
      ),
      unselectedLabelStyle: resolved.typography.chipLabel.copyWith(
        color: resolved.colors.textLight,
      ),
    ),
    chipTheme: base.chipTheme.copyWith(
      backgroundColor: resolved.colors.chipBg,
      disabledColor: resolved.colors.chipBg,
      selectedColor: resolved.colors.lavender,
      side: BorderSide(color: resolved.colors.chipBorder),
      labelStyle: resolved.typography.chipLabel.copyWith(
        color: resolved.colors.text,
      ),
      secondaryLabelStyle: resolved.typography.chipLabel.copyWith(
        color: resolved.colors.text,
      ),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(resolved.radii.pillRadius),
      ),
    ),
    filledButtonTheme: FilledButtonThemeData(
      style: FilledButton.styleFrom(
        backgroundColor: resolved.colors.buttonPrimary,
        foregroundColor: resolved.colors.heroText,
        elevation: 0,
        padding: EdgeInsets.symmetric(
          horizontal: resolved.spacing.s20,
          vertical: resolved.spacing.sm,
        ),
        textStyle: resolved.typography.buttonLabel.copyWith(
          color: resolved.colors.heroText,
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(resolved.radii.pillRadius),
        ),
      ),
    ),
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: resolved.colors.buttonPrimary,
        foregroundColor: resolved.colors.heroText,
        elevation: 0,
        padding: EdgeInsets.symmetric(
          horizontal: resolved.spacing.s20,
          vertical: resolved.spacing.sm,
        ),
        textStyle: resolved.typography.buttonLabel.copyWith(
          color: resolved.colors.heroText,
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(resolved.radii.pillRadius),
        ),
      ),
    ),
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        foregroundColor: resolved.colors.text,
        side: BorderSide(color: resolved.colors.strokeSoft),
        padding: EdgeInsets.symmetric(
          horizontal: resolved.spacing.s20,
          vertical: resolved.spacing.sm,
        ),
        textStyle: resolved.typography.chipLabel.copyWith(
          color: resolved.colors.text,
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(resolved.radii.pillRadius),
        ),
      ),
    ),
    textButtonTheme: TextButtonThemeData(
      style: TextButton.styleFrom(
        foregroundColor: resolved.colors.text,
        textStyle: resolved.typography.chipLabel.copyWith(
          color: resolved.colors.text,
        ),
      ),
    ),
    iconButtonTheme: IconButtonThemeData(
      style: IconButton.styleFrom(
        foregroundColor: resolved.colors.text,
        iconSize: 20,
      ),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: resolved.colors.surface,
      hintStyle: resolved.typography.bodyCompact.copyWith(
        color: resolved.colors.textLight,
      ),
      labelStyle: resolved.typography.meta.copyWith(
        color: resolved.colors.muted,
      ),
      helperStyle: resolved.typography.meta.copyWith(
        color: resolved.colors.textLight,
      ),
      errorStyle: resolved.typography.meta.copyWith(
        color: base.colorScheme.error,
      ),
      floatingLabelStyle: resolved.typography.meta.copyWith(
        color: resolved.colors.primary,
      ),
      contentPadding: EdgeInsets.symmetric(
        horizontal: resolved.spacing.s20,
        vertical: resolved.spacing.sm,
      ),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(resolved.radii.cardRadius * 0.55),
        borderSide: BorderSide(color: resolved.colors.separator),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(resolved.radii.cardRadius * 0.55),
        borderSide: BorderSide(color: resolved.colors.separator),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(resolved.radii.cardRadius * 0.55),
        borderSide: BorderSide(color: resolved.colors.primary, width: 1.4),
      ),
    ),
    expansionTileTheme: ExpansionTileThemeData(
      iconColor: resolved.colors.primary,
      collapsedIconColor: resolved.colors.textLight,
      textColor: resolved.colors.text,
      collapsedTextColor: resolved.colors.text,
    ),
    extensions: extensions,
  );
}

extension ProfileThemeBuildContextX on BuildContext {
  ProfileTheme get profileTheme =>
      Theme.of(this).extension<ProfileTheme>() ?? ProfileTheme.fallback();
}
