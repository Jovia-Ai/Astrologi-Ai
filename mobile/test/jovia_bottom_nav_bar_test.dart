import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/design/theme/profile_theme_extension.dart';
import 'package:mobile/design/widgets/jovia_editorial.dart';

void main() {
  testWidgets('nav icons stay aligned without showing labels', (
    WidgetTester tester,
  ) async {
    const homeKey = Key('home-icon');
    const bondKey = Key('bond-icon');
    const addKey = Key('add-icon');

    await tester.pumpWidget(
      MaterialApp(
        theme: withProfileTheme(ThemeData.light()),
        home: Scaffold(
          bottomNavigationBar: JoviaBottomNavBar(
            currentIndex: 0,
            onTap: (_) {},
            items: const [
              JoviaBottomNavItem(
                icon: Icon(Icons.home_rounded, key: homeKey),
                label: 'Home',
              ),
              JoviaBottomNavItem(
                icon: Icon(Icons.favorite_border_rounded, key: bondKey),
                label: 'Bond',
              ),
              JoviaBottomNavItem(
                icon: Icon(Icons.add_rounded, key: addKey),
                label: 'Add',
                prominent: true,
              ),
            ],
          ),
        ),
      ),
    );

    await tester.pumpAndSettle();

    final homeCenter = tester.getCenter(find.byKey(homeKey));
    final bondCenter = tester.getCenter(find.byKey(bondKey));
    final addCenter = tester.getCenter(find.byKey(addKey));
    final navRect = tester.getRect(find.byType(JoviaBottomNavBar));

    expect(find.text('Home'), findsNothing);
    expect(find.text('Bond'), findsNothing);
    expect((homeCenter.dy - bondCenter.dy).abs(), lessThan(1.0));
    expect((homeCenter.dy - addCenter.dy).abs(), lessThan(1.0));
    expect(navRect.height, lessThan(96));
  });
}
