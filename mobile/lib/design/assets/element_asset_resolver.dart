import 'package:mobile/design/astro/element_scores.dart';

const String joviaElementAssetRoot = 'ios/Flutter/assets/elements';

enum JoviaElementAsset {
  fire('$joviaElementAssetRoot/fire.svg'),
  water('$joviaElementAssetRoot/water.svg'),
  air('$joviaElementAssetRoot/air.svg'),
  earth('$joviaElementAssetRoot/earth.svg');

  const JoviaElementAsset(this.path);

  final String path;
}

class JoviaElementAssetResolver {
  const JoviaElementAssetResolver._();

  static JoviaElementAsset fromElement(AstroElement element) {
    return switch (element) {
      AstroElement.fire => JoviaElementAsset.fire,
      AstroElement.water => JoviaElementAsset.water,
      AstroElement.air => JoviaElementAsset.air,
      AstroElement.earth => JoviaElementAsset.earth,
    };
  }
}
