import 'package:flutter/material.dart';

import 'package:mobile/design/theme/profile_theme_extension.dart';
import 'package:mobile/l10n/app_localizations.dart';

Widget buildTestApp({
  required Widget child,
  Locale? locale,
  ThemeData? theme,
}) {
  return MaterialApp(
    locale: locale,
    theme: withProfileTheme(theme ?? ThemeData.light()),
    localizationsDelegates: AppLocalizations.localizationsDelegates,
    supportedLocales: AppLocalizations.supportedLocales,
    home: child,
  );
}
