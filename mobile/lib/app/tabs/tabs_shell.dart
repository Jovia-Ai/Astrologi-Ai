import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

import 'package:mobile/app/people/people_list_page.dart';
import 'package:mobile/app/tabs/calendar_hub_page.dart';
import 'ai_page.dart';
import 'bond_page.dart';
import 'chart_lab_page.dart';
import 'home_page.dart';
import 'profile_page.dart';
import 'profile_archetype_page.dart';
import 'story_studio_page.dart';
import 'package:mobile/design/theme/profile_theme_extension.dart';
import 'package:mobile/design/widgets/jovia_app_menu_scope.dart';
import 'package:mobile/design/widgets/jovia_editorial.dart';
import 'package:mobile/app/widgets/jovia_app_menu_drawer.dart';

class TabsShell extends StatefulWidget {
  const TabsShell({super.key});

  @override
  State<TabsShell> createState() => _TabsShellState();
}

class _TabsShellState extends State<TabsShell> {
  static const String _baseUrl = 'http://127.0.0.1:5000';

  final _scaffoldKey = GlobalKey<ScaffoldState>();
  int _index = 0;
  final Set<int> _builtIndexes = <int>{0};

  late final List<_TabItem> _tabs = <_TabItem>[
    const _TabItem(
      page: HomePage(),
      item: JoviaBottomNavItem(
        icon: JoviaUiIcon(asset: JoviaUiAsset.homePortal, size: 23),
        label: 'Home',
        showLabel: false,
      ),
    ),
    const _TabItem(
      page: BondPage(),
      item: JoviaBottomNavItem(
        icon: JoviaUiIcon(asset: JoviaUiAsset.heartOrbit, size: 23),
        label: 'Bond',
        showLabel: false,
      ),
    ),
    const _TabItem(
      page: StoryStudioPage(),
      item: JoviaBottomNavItem(
        icon: Icon(Icons.add_rounded, size: 30),
        label: 'Story Studio',
        prominent: true,
        showLabel: false,
      ),
    ),
    const _TabItem(
      page: AiPage(),
      item: JoviaBottomNavItem(
        icon: _AiTabIcon(),
        label: 'AI Chat',
        showLabel: false,
      ),
    ),
    const _TabItem(
      page: ProfilePage(),
      item: JoviaBottomNavItem(
        icon: JoviaUiIcon(asset: JoviaUiAsset.profileComet, size: 23),
        label: 'Profile',
        showLabel: false,
      ),
    ),
  ];

  Future<void> _openProfile(
    BuildContext context,
    Map<String, dynamic>? profile,
  ) async {
    await Navigator.of(
      context,
    ).push(MaterialPageRoute<void>(builder: (_) => const ProfilePage()));
  }

  Future<void> _openPeople(
    BuildContext context,
    Map<String, dynamic>? profile,
  ) async {
    await Navigator.of(
      context,
    ).push(MaterialPageRoute<void>(builder: (_) => const PeopleListPage()));
  }

  Future<void> _openCalendar(
    BuildContext context,
    Map<String, dynamic>? profile,
  ) async {
    await Navigator.of(context).push(
      MaterialPageRoute<void>(
        builder: (_) => CalendarHubPage(profileOverride: profile),
      ),
    );
  }

  Future<void> _openArchetype(
    BuildContext context,
    Map<String, dynamic>? profile,
  ) async {
    if (!_hasBirthData(profile)) {
      await _openProfile(context, profile);
      return;
    }
    await Navigator.of(context).push(
      MaterialPageRoute<void>(
        builder: (_) => ProfileArchetypeExperiencePage(
          displayName: _displayName(profile),
          requestPayload: _buildArchetypePayload(profile!),
          baseUrl: _baseUrl,
        ),
      ),
    );
  }

  bool _hasBirthData(Map<String, dynamic>? profile) {
    if (profile == null) {
      return false;
    }
    final birthDate = (profile['birth_date'] ?? '').toString().trim();
    final birthTime = (profile['birth_time'] ?? '').toString().trim();
    final place = _resolveBirthPlace(profile);
    return birthDate.isNotEmpty && birthTime.isNotEmpty && place.isNotEmpty;
  }

  String _displayName(Map<String, dynamic>? profile) {
    final fromProfile = (profile?['full_name'] ?? profile?['name'] ?? '')
        .toString()
        .trim();
    if (fromProfile.isNotEmpty) {
      return fromProfile;
    }
    return 'Profil';
  }

  Map<String, dynamic> _buildArchetypePayload(Map<String, dynamic> profile) {
    return <String, dynamic>{
      'birth_date': (profile['birth_date'] ?? '').toString().trim(),
      'birth_time': _normalizeBirthTime(
        (profile['birth_time'] ?? '').toString(),
      ),
      'birth_place': _resolveBirthPlace(profile),
      'locale': 'tr',
      'birth_time_confidence': 'exact',
    };
  }

  String _resolveBirthPlace(Map<String, dynamic>? profile) {
    final city = (profile?['city'] ?? '').toString().trim();
    final country = (profile?['country'] ?? '').toString().trim();
    final place = (profile?['place'] ?? '').toString().trim();
    if (place.isNotEmpty) {
      return place;
    }
    if (city.isEmpty) {
      return country;
    }
    if (country.isEmpty) {
      return city;
    }
    return '$city, $country';
  }

  String _normalizeBirthTime(String raw) {
    final cleaned = raw.trim();
    if (cleaned.isEmpty) {
      return cleaned;
    }
    final segments = cleaned.split(':');
    if (segments.length != 2) {
      return cleaned;
    }
    final hour = segments.first.padLeft(2, '0');
    final minute = segments.last.padLeft(2, '0');
    return '$hour:$minute';
  }

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final activeIndex = _index.clamp(0, _tabs.length - 1);

    return Scaffold(
      key: _scaffoldKey,
      extendBody: true,
      backgroundColor: profile.colors.bg,
      endDrawerEnableOpenDragGesture: false,
      endDrawer: JoviaAppMenuDrawer(
        onEditProfile: _openProfile,
        onOpenPeople: _openPeople,
        onOpenCalendar: _openCalendar,
        onOpenArchetype: _openArchetype,
      ),
      body: JoviaAppMenuScope(
        openMenu: () => _scaffoldKey.currentState?.openEndDrawer(),
        child: SafeArea(
          child: IndexedStack(
            index: activeIndex,
            children: [
              for (var index = 0; index < _tabs.length; index++)
                _builtIndexes.contains(index)
                    ? _tabs[index].page
                    : const SizedBox.shrink(),
            ],
          ),
        ),
      ),
      bottomNavigationBar: JoviaBottomNavBar(
        currentIndex: activeIndex,
        onTap: (value) => setState(() {
          _index = value;
          _builtIndexes.add(value);
        }),
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
      child: const JoviaUiIcon(asset: JoviaUiAsset.chatOrbit, size: 23),
    );
  }
}
