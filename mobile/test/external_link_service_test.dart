import 'package:flutter_test/flutter_test.dart';
import 'package:url_launcher/url_launcher.dart';

import 'package:mobile/app/legal/external_link_service.dart';

void main() {
  test('opens privacy policy and terms in an external app', () async {
    final launched = <(Uri, LaunchMode)>[];
    final service = ExternalLinkService(
      launcher: (uri, mode) async {
        launched.add((uri, mode));
        return true;
      },
    );

    await service.openPrivacyPolicy();
    await service.openTermsOfUse();

    expect(launched, [
      (ShouExternalLinks.privacyPolicy, LaunchMode.externalApplication),
      (ShouExternalLinks.termsOfUse, LaunchMode.externalApplication),
    ]);
  });

  test('opens support email with the platform default mode', () async {
    (Uri, LaunchMode)? launch;
    final service = ExternalLinkService(
      launcher: (uri, mode) async {
        launch = (uri, mode);
        return true;
      },
    );

    await service.openSupport();

    expect(launch, (
      ShouExternalLinks.supportEmail,
      LaunchMode.platformDefault,
    ));
  });

  test('throws when the launcher reports failure', () async {
    final service = ExternalLinkService(launcher: (_, _) async => false);

    expect(service.openPrivacyPolicy(), throwsA(isA<ExternalLinkException>()));
  });
}
