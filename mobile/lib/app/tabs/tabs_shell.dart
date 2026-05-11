import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

import 'package:mobile/app/people/people_list_page.dart';
import 'package:mobile/app/telemetry/perf_telemetry.dart';
import 'package:mobile/app/tabs/calendar_hub_page.dart';
import 'ai_page.dart';
import 'bond_page.dart';
import 'chart_lab_page.dart';
import 'home_page.dart';
import 'home_page_v2.dart';
import 'profile_page.dart';
import 'profile_archetype_page.dart';
import 'story_studio_page.dart';
import 'package:mobile/design/theme/profile_theme_extension.dart';
import 'package:mobile/design/widgets/jovia_app_menu_scope.dart';
import 'package:mobile/design/widgets/jovia_editorial.dart';
import 'package:mobile/app/widgets/jovia_app_menu_drawer.dart';
import 'package:mobile/l10n/l10n.dart';

/// Bugün tab'ı SHOU v2 Figma tasarımı ile render ediliyor. Legacy
/// [HomePage] hâlâ dosyada — geri dönüş gerekirse flag `false` yapıp
/// sonra silinir.
const bool kUseHomeV2 = true;

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

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) {
        return;
      }
      PerfTelemetry.logPointOnce(
        'startup.tabs_shell_visible',
        'tabs_shell_visible',
        data: <String, Object?>{'initial_index': _index},
      );
    });
  }

  List<_TabItem> _buildTabs(BuildContext context) {
    final l10n = context.l10n;
    return <_TabItem>[
      _TabItem(
        page: kUseHomeV2 ? const HomePageV2() : const HomePage(),
        item: JoviaBottomNavItem(
          icon: const Icon(Icons.home_outlined, size: 24),
          label: l10n.tabsHome,
          showLabel: false,
        ),
      ),
      _TabItem(
        page: const BondPage(),
        item: JoviaBottomNavItem(
          icon: const Icon(Icons.favorite_border_rounded, size: 23),
          label: l10n.tabsBond,
          showLabel: false,
        ),
      ),
      _TabItem(
        page: const StoryStudioPage(),
        item: JoviaBottomNavItem(
          icon: const Icon(Icons.add_rounded, size: 28),
          label: l10n.tabsStoryStudio,
          prominent: true,
          showLabel: false,
        ),
      ),
      _TabItem(
        page: const AiPage(),
        item: JoviaBottomNavItem(
          icon: const _AiTabIcon(),
          label: l10n.tabsAiChat,
          showLabel: false,
        ),
      ),
      _TabItem(
        page: const ProfilePage(),
        item: JoviaBottomNavItem(
          icon: const Icon(Icons.person_outline_rounded, size: 24),
          label: l10n.tabsProfile,
          showLabel: false,
        ),
      ),
    ];
  }

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
    final resolvedProfile = profile;
    if (resolvedProfile == null) {
      await _openProfile(context, profile);
      return;
    }
    await Navigator.of(context).push(
      MaterialPageRoute<void>(
        builder: (_) => ProfileArchetypeExperiencePage(
          displayName: _displayName(profile, context.l10n.tabsProfile),
          requestPayload: _buildArchetypePayload(resolvedProfile),
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

  String _displayName(Map<String, dynamic>? profile, String fallback) {
    final fromProfile = (profile?['full_name'] ?? profile?['name'] ?? '')
        .toString()
        .trim();
    if (fromProfile.isNotEmpty) {
      return fromProfile;
    }
    return fallback;
  }

  Map<String, dynamic> _buildArchetypePayload(Map<String, dynamic> profile) {
    return <String, dynamic>{
      'birth_date': (profile['birth_date'] ?? '').toString().trim(),
      'birth_time': _normalizeBirthTime(
        (profile['birth_time'] ?? '').toString(),
      ),
      'birth_place': _resolveBirthPlace(profile),
      'locale': Localizations.localeOf(context).languageCode,
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
    final tabs = _buildTabs(context);
    final activeIndex = _index.clamp(0, tabs.length - 1);

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
              for (var index = 0; index < tabs.length; index++)
                _builtIndexes.contains(index)
                    ? tabs[index].page
                    : const SizedBox.shrink(),
            ],
          ),
        ),
      ),
      bottomNavigationBar: JoviaBottomNavBar(
        currentIndex: activeIndex,
        onTap: (value) => setState(() {
          if (value == 4 && _index != value && _builtIndexes.contains(value)) {
            PerfTelemetry.logPoint(
              'profile_reopen_same_session',
              data: const <String, Object?>{'source': 'tabs_shell'},
            );
          }
          _index = value;
          _builtIndexes.add(value);
        }),
        items: tabs.map((entry) => entry.item).toList(),
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
      child: const Icon(Icons.chat_bubble_outline_rounded, size: 22),
    );
  }
}
