const String joviaPlanetAssetRoot = 'ios/Flutter/assets/planets';
const String joviaPlanetFallbackIllustrationRoot =
    'ios/Flutter/assets/illustrations';

enum JoviaPlanetAsset {
  sun('$joviaPlanetFallbackIllustrationRoot/sun growth.svg', tintable: false),
  moon('$joviaPlanetAssetRoot/moon _ venus.svg'),
  mercury('$joviaPlanetAssetRoot/mercury.svg'),
  venus('$joviaPlanetAssetRoot/venus.svg'),
  mars('$joviaPlanetAssetRoot/mars.svg'),
  jupiter('$joviaPlanetAssetRoot/jupiter.svg'),
  saturn('$joviaPlanetAssetRoot/saturn.svg'),
  uranus('$joviaPlanetAssetRoot/uranus.svg'),
  neptune('$joviaPlanetAssetRoot/neptune.svg'),
  pluto('$joviaPlanetAssetRoot/pluton.svg'),
  rising('$joviaPlanetFallbackIllustrationRoot/planet.svg', tintable: false);

  const JoviaPlanetAsset(this.path, {this.tintable = true});

  final String path;
  final bool tintable;
}

class JoviaPlanetAssetResolver {
  const JoviaPlanetAssetResolver._();

  static JoviaPlanetAsset fromPlacementLabel(String label) {
    switch (label.trim().toLowerCase()) {
      case 'gunes':
        return JoviaPlanetAsset.sun;
      case 'ay':
        return JoviaPlanetAsset.moon;
      case 'yukselen':
      default:
        return JoviaPlanetAsset.rising;
    }
  }

  static JoviaPlanetAsset? fromNarrativeText(String text) {
    final normalized = text.toLowerCase();
    if (normalized.contains('sun') || normalized.contains('gunes')) {
      return JoviaPlanetAsset.sun;
    }
    if (normalized.contains('moon') || normalized.contains('ay')) {
      return JoviaPlanetAsset.moon;
    }
    if (normalized.contains('mercury') || normalized.contains('merkur')) {
      return JoviaPlanetAsset.mercury;
    }
    if (normalized.contains('venus')) {
      return JoviaPlanetAsset.venus;
    }
    if (normalized.contains('mars')) {
      return JoviaPlanetAsset.mars;
    }
    if (normalized.contains('jupiter') || normalized.contains('jup')) {
      return JoviaPlanetAsset.jupiter;
    }
    if (normalized.contains('saturn') || normalized.contains('saturn')) {
      return JoviaPlanetAsset.saturn;
    }
    if (normalized.contains('uranus')) {
      return JoviaPlanetAsset.uranus;
    }
    if (normalized.contains('neptune') || normalized.contains('neptun')) {
      return JoviaPlanetAsset.neptune;
    }
    if (normalized.contains('pluto') || normalized.contains('pluton')) {
      return JoviaPlanetAsset.pluto;
    }
    return null;
  }
}
