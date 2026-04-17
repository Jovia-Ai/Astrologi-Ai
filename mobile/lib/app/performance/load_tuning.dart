import 'package:mobile/app/api/api_client.dart';

class LoadTuning {
  const LoadTuning._();

  static const Duration homeFastTimeout = Duration(seconds: 6);
  static const Duration homeSkyTimeout = Duration(seconds: 30);
  static const Duration homeNarrativeTimeout = Duration(seconds: 18);
  static const Duration homeWeekNarrativeTimeout = Duration(seconds: 18);
  static const Duration homeFastDeferredRetryDelay = Duration(
    milliseconds: 1400,
  );
  static const int maxHomeFastDeferredRetries = 2;
  static const Duration homeNatalCacheTtl = Duration(minutes: 5);
  static const Duration homeSkyCacheTtl = Duration(seconds: 60);

  static const Duration profileNatalCacheTtl = Duration(minutes: 5);
  static const Duration profileFastCacheTtl = Duration(minutes: 5);
  static const Duration profileFastTimeout = Duration(seconds: 4);
  static const Duration profileInterpretUiTimeout = Duration(seconds: 18);
  static const Duration profileLegacyInterpretTimeout = Duration(seconds: 18);
  static const ApiRequestSla profileFastRequestSla = ApiRequestSla.fast;
  static const ApiRequestSla profileInterpretUiRequestSla =
      ApiRequestSla.background;
  static const ApiRequestSla profileLegacyInterpretRequestSla =
      ApiRequestSla.background;
}
