class ApiEnvironment {
  ApiEnvironment._();

  static const String _fallbackBaseUrl = 'http://127.0.0.1:5000';
  static const String _rawBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: _fallbackBaseUrl,
  );

  static String get apiBaseUrl => _normalizeBaseUrl(_rawBaseUrl);

  static bool get usesDefaultBaseUrl => _rawBaseUrl.trim().isEmpty;

  static Uri get apiBaseUri => Uri.parse(apiBaseUrl);

  static bool get usesLoopbackHost => _isLoopbackHost(apiBaseUri.host);

  static bool get usesInsecureHttp => apiBaseUri.scheme == 'http';

  static String resolveBaseUrl(String? override) {
    final candidate = override?.trim();
    if (candidate == null || candidate.isEmpty) {
      return apiBaseUrl;
    }
    return _normalizeBaseUrl(candidate);
  }

  static String _normalizeBaseUrl(String value) {
    final trimmed = value.trim();
    final normalized = trimmed.isEmpty ? _fallbackBaseUrl : trimmed;
    if (normalized.endsWith('/')) {
      return normalized.substring(0, normalized.length - 1);
    }
    return normalized;
  }

  static bool _isLoopbackHost(String host) {
    final normalized = host.trim().toLowerCase();
    return normalized == 'localhost' ||
        normalized == '127.0.0.1' ||
        normalized == '::1';
  }
}
