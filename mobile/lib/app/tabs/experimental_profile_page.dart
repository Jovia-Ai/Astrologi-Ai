import 'package:flutter/material.dart';

import 'package:mobile/app/tabs/profile_page_v2_experiment.dart';

class ExperimentalProfilePage extends StatelessWidget {
  const ExperimentalProfilePage({
    super.key,
    this.viewedUserId,
    this.profileOverride,
    this.readOnly = false,
  });

  final String? viewedUserId;
  final Map<String, dynamic>? profileOverride;
  final bool readOnly;

  @override
  Widget build(BuildContext context) {
    return ProfilePageV2Experiment(
      viewedUserId: viewedUserId,
      profileOverride: profileOverride,
      readOnly: readOnly,
    );
  }
}
