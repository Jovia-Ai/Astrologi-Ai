import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

enum JoviaThemeMode { dark, light }

final joviaThemeModeProvider =
    NotifierProvider<JoviaThemeModeController, JoviaThemeMode>(
      JoviaThemeModeController.new,
    );

class JoviaThemeModeController extends Notifier<JoviaThemeMode> {
  @override
  JoviaThemeMode build() {
    final raw = Supabase
        .instance
        .client
        .auth
        .currentUser
        ?.userMetadata?['theme_mode']
        ?.toString()
        .trim()
        .toLowerCase();
    return raw == 'dark' ? JoviaThemeMode.dark : JoviaThemeMode.light;
  }

  Future<void> setMode(JoviaThemeMode mode) async {
    state = mode;
    final user = Supabase.instance.client.auth.currentUser;
    if (user == null) {
      return;
    }
    final metadata = Map<String, dynamic>.from(
      user.userMetadata ?? const <String, dynamic>{},
    );
    metadata['theme_mode'] = mode.name;
    try {
      await Supabase.instance.client.auth.updateUser(
        UserAttributes(data: metadata),
      );
    } catch (error, stackTrace) {
      debugPrint('[ThemeMode] persist failed: $error');
      FlutterError.reportError(
        FlutterErrorDetails(
          exception: error,
          stack: stackTrace,
          library: 'app_theme_mode_provider',
          context: ErrorDescription('persisting theme mode'),
        ),
      );
    }
  }
}

extension JoviaThemeModeX on JoviaThemeMode {
  bool get isDark => this == JoviaThemeMode.dark;

  ThemeMode get materialMode => isDark ? ThemeMode.dark : ThemeMode.light;

  String get label => isDark ? 'Koyu mod' : 'Acik mod';
}
