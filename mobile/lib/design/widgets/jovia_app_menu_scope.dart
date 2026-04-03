import 'package:flutter/widgets.dart';

class JoviaAppMenuScope extends InheritedWidget {
  const JoviaAppMenuScope({
    super.key,
    required this.openMenu,
    required super.child,
  });

  final VoidCallback openMenu;

  static JoviaAppMenuScope? maybeOf(BuildContext context) {
    return context.dependOnInheritedWidgetOfExactType<JoviaAppMenuScope>();
  }

  @override
  bool updateShouldNotify(JoviaAppMenuScope oldWidget) {
    return openMenu != oldWidget.openMenu;
  }
}
