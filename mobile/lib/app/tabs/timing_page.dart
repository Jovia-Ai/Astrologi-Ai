import 'package:flutter/material.dart';

import 'package:mobile/app/tabs/calendar_hub_page.dart';

/// Deprecated shell kept for compatibility. Use [CalendarHubPage] directly.
class TimingPage extends StatelessWidget {
  const TimingPage({super.key, this.profileOverride});

  final Map<String, dynamic>? profileOverride;

  @override
  Widget build(BuildContext context) {
    return CalendarHubPage(profileOverride: profileOverride);
  }
}
