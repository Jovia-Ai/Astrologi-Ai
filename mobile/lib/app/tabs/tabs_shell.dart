import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

import 'ai_page.dart';
import 'bond_page.dart';
import 'calendar_hub_page.dart';
import 'chart_lab_page.dart';
import 'home_page.dart';
import 'profile_page.dart';

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
      item: BottomNavigationBarItem(icon: Icon(Icons.home), label: 'Home'),
    ),
    const _TabItem(
      page: BondPage(),
      item: BottomNavigationBarItem(icon: Icon(Icons.favorite), label: 'Bond'),
    ),
    const _TabItem(
      page: AiPage(),
      item: BottomNavigationBarItem(icon: _AiTabIcon(), label: 'AI'),
    ),
    const _TabItem(
      page: ProfilePage(),
      item: BottomNavigationBarItem(icon: Icon(Icons.person), label: 'Profile'),
    ),
  ];

  @override
  Widget build(BuildContext context) {
    final activeIndex = _index.clamp(0, _tabs.length - 1);
    final activeTitle = _tabs[activeIndex].item.label ?? 'Tabs';
    final showCalendarAction = activeIndex == 0 || activeIndex == 3;

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        title: Text(activeTitle),
        backgroundColor: Colors.white,
        actions: showCalendarAction
            ? <Widget>[
                IconButton(
                  tooltip: 'Calendar',
                  onPressed: () => _openTiming(context),
                  icon: const Icon(Icons.calendar_month),
                ),
              ]
            : null,
      ),
      body: SafeArea(
        child: IndexedStack(
          index: activeIndex,
          children: _tabs.map((entry) => entry.page).toList(),
        ),
      ),
      bottomNavigationBar: BottomNavigationBar(
        type: BottomNavigationBarType.fixed,
        backgroundColor: Colors.white,
        currentIndex: activeIndex,
        onTap: (value) => setState(() => _index = value),
        items: _tabs.map((entry) => entry.item).toList(),
      ),
    );
  }

  void _openTiming(BuildContext context) {
    Navigator.of(context).push(
      MaterialPageRoute<void>(
        builder: (_) => const CalendarHubPage(),
      ),
    );
  }
}

class _TabItem {
  const _TabItem({required this.page, required this.item});

  final Widget page;
  final BottomNavigationBarItem item;
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
      child: const Icon(Icons.auto_awesome),
    );
  }
}
