import 'package:url_launcher/url_launcher.dart';

typedef ExternalLinkLauncher = Future<bool> Function(Uri uri, LaunchMode mode);

class ExternalLinkException implements Exception {
  const ExternalLinkException(this.message);

  final String message;

  @override
  String toString() => message;
}

class ShouExternalLinks {
  const ShouExternalLinks._();

  static final Uri privacyPolicy = Uri.parse(
    'https://shouastrology.com/privacy',
  );
  static final Uri termsOfUse = Uri.parse('https://shouastrology.com/terms');
  static final Uri supportEmail = Uri(
    scheme: 'mailto',
    path: 'info@shouastrology.com',
  );
}

class ExternalLinkService {
  const ExternalLinkService({ExternalLinkLauncher? launcher})
    : _launcher = launcher ?? _defaultLauncher;

  final ExternalLinkLauncher _launcher;

  Future<void> openPrivacyPolicy() => open(ShouExternalLinks.privacyPolicy);

  Future<void> openTermsOfUse() => open(ShouExternalLinks.termsOfUse);

  Future<void> openSupport() => open(ShouExternalLinks.supportEmail);

  Future<void> open(Uri uri) async {
    final launched = await _launcher(uri, _launchModeFor(uri));
    if (!launched) {
      throw const ExternalLinkException('Could not open link.');
    }
  }

  static Future<bool> _defaultLauncher(Uri uri, LaunchMode mode) {
    return launchUrl(uri, mode: mode);
  }

  LaunchMode _launchModeFor(Uri uri) {
    if (uri.scheme == 'http' || uri.scheme == 'https') {
      return LaunchMode.externalApplication;
    }
    return LaunchMode.platformDefault;
  }
}
