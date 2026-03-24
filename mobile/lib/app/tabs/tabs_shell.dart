import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

import 'ai_page.dart';
import 'bond_page.dart';
import 'chart_lab_page.dart';
import 'home_page.dart';
import 'profile_page.dart';
import 'story_studio_page.dart';
import 'package:mobile/design/theme/profile_theme_extension.dart';
import 'package:mobile/design/widgets/jovia_assets.dart';
import 'package:mobile/design/widgets/jovia_editorial.dart';

class TabsShell extends StatefulWidget {
  const TabsShell({super.key});

  @override
  State<TabsShell> createState() => _TabsShellState();
}

class _TabsShellState extends State<TabsShell> {
  int _index = 0;

  late final List<_TabItem> _tabs = <_TabItem>[
    const _TabItem(
      page: HomePage(),
      item: JoviaBottomNavItem(
        icon: JoviaUiIcon(asset: JoviaUiAsset.homePortal),
        label: 'Home',
      ),
    ),
    const _TabItem(
      page: BondPage(),
      item: JoviaBottomNavItem(
        icon: JoviaUiIcon(asset: JoviaUiAsset.heartOrbit),
        label: 'Bond',
      ),
    ),
    const _TabItem(
      page: AiPage(),
      item: JoviaBottomNavItem(icon: _AiTabIcon(), label: 'AI'),
    ),
    const _TabItem(
      page: StoryStudioPage(),
      item: JoviaBottomNavItem(
        icon: JoviaUiIcon(asset: JoviaUiAsset.menuStack),
        label: 'Studio',
      ),
    ),
    const _TabItem(
      page: ProfilePage(),
      item: JoviaBottomNavItem(
        icon: JoviaUiIcon(asset: JoviaUiAsset.profileComet),
        label: 'Profile',
      ),
    ),
  ];

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final activeIndex = _index.clamp(0, _tabs.length - 1);

    return Scaffold(
      backgroundColor: profile.colors.bg,
      body: SafeArea(
        child: IndexedStack(
          index: activeIndex,
          children: _tabs.map((entry) => entry.page).toList(),
        ),
      ),
      bottomNavigationBar: JoviaBottomNavBar(
        currentIndex: activeIndex,
        onTap: (value) => setState(() => _index = value),
        items: _tabs.map((entry) => entry.item).toList(),
      ),
    );
  }
}

class _TabItem {
  const _TabItem({required this.page, required this.item});

  final Widget page;
  final JoviaBottomNavItem item;
}

class _AiTabIcon extends StatelessWidget {
  const _AiTabIcon();

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onLongPress: kDebugMode
          ? () {
              Navigator.of(context).push(
                MaterialPageRoute<void>(builder: (_) => const ChartLabPage()),
              );
            }
          : null,
      child: const JoviaUiIcon(asset: JoviaUiAsset.chatOrbit),
    );
  }
}
