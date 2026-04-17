import 'package:flutter/material.dart';

/// SHOU logo usage contract.
///
/// Keep all brand asset paths in this file so runtime UI, native icon tooling,
/// and splash tooling stay aligned.
final class ShouBrandAssets {
  const ShouBrandAssets._();

  /// Primary app icon consumed by flutter_launcher_icons.
  static const String primaryAppIconPng = 'assets/logos/circle_dark_mode.png';

  /// Optional small circular mark for compact contexts.
  static const String circleIconDark = 'assets/logos/circle_dark_mode.png';

  /// Launch/splash symbol consumed by flutter_native_splash.
  static const String splashSymbolPng =
      'assets/logos/splash_shou_symbol_dark_2048.png';

  static const String symbolDark = 'assets/logos/shou_symbol_dark.png';
  static const String symbolLight = 'assets/logos/shou_symbol_light.png';
  static const String symbolLime = 'assets/logos/shou_symbol_lime.png';

  /// Use on light backgrounds.
  static const String wordmarkDark = 'assets/logos/shou_wordmark_dark_mode.png';

  /// Use on dark backgrounds.
  static const String wordmarkLight =
      'assets/logos/shou_wordmark_light_mode.png';

  /// In-app small branding contract:
  /// - dark surfaces -> light wordmark
  /// - light surfaces -> dark wordmark
  static String wordmarkForSurfaceBrightness(Brightness brightness) {
    return brightness == Brightness.dark ? wordmarkLight : wordmarkDark;
  }
}
