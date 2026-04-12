import 'package:flutter/widgets.dart';
import 'package:intl/intl.dart';

import 'package:mobile/l10n/app_localizations.dart';

AppLocalizations currentL10n() {
  final localeName = Intl.getCurrentLocale();
  final languageCode = localeName.split(RegExp('[-_]')).first.trim();
  return lookupAppLocalizations(
    Locale(languageCode.isEmpty ? 'tr' : languageCode),
  );
}

bool isCurrentLocaleTurkish() => currentL10n().localeName.startsWith('tr');
