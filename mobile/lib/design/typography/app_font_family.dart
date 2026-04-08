import 'package:flutter/foundation.dart';

const String _appleDisplayFontFamily = '.SF Pro Display';

String? platformDisplayFontFamily() {
  switch (defaultTargetPlatform) {
    case TargetPlatform.iOS:
    case TargetPlatform.macOS:
      return _appleDisplayFontFamily;
    default:
      return null;
  }
}
