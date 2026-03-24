const String joviaColorAssetRoot = 'ios/Flutter/assets/colors';
const String joviaIllustrationAssetRoot = 'ios/Flutter/assets/illustrations';

enum JoviaColorAsset {
  wash01('$joviaColorAssetRoot/1.svg'),
  wash02('$joviaColorAssetRoot/2.svg'),
  wash03('$joviaColorAssetRoot/3.svg'),
  wash04('$joviaColorAssetRoot/4.svg'),
  wash05('$joviaColorAssetRoot/5.svg'),
  wash06('$joviaColorAssetRoot/6.svg'),
  wash07('$joviaColorAssetRoot/7.svg'),
  wash08('$joviaColorAssetRoot/8.svg'),
  wash09('$joviaColorAssetRoot/9.svg'),
  wash10('$joviaColorAssetRoot/10.svg'),
  wash11('$joviaColorAssetRoot/11.svg'),
  wash12('$joviaColorAssetRoot/12.svg'),
  wash13('$joviaColorAssetRoot/13.svg'),
  wash14('$joviaColorAssetRoot/14.svg'),
  wash15('$joviaColorAssetRoot/15.svg');

  const JoviaColorAsset(this.path);

  final String path;
}

enum JoviaIllustrationAsset {
  bird('$joviaIllustrationAssetRoot/bird.svg'),
  blocks('$joviaIllustrationAssetRoot/blocks.svg'),
  dots('$joviaIllustrationAssetRoot/dots.svg'),
  flower('$joviaIllustrationAssetRoot/flower.svg'),
  heart('$joviaIllustrationAssetRoot/heart.svg'),
  layers('$joviaIllustrationAssetRoot/layers.svg'),
  leo('$joviaIllustrationAssetRoot/leo.svg'),
  planet('$joviaIllustrationAssetRoot/planet.svg'),
  rocks('$joviaIllustrationAssetRoot/rocks.svg'),
  shape('$joviaIllustrationAssetRoot/shape.svg'),
  sunGrowth('$joviaIllustrationAssetRoot/sun growth.svg'),
  sunMountain('$joviaIllustrationAssetRoot/sun mountin.svg');

  const JoviaIllustrationAsset(this.path);

  final String path;
}

enum JoviaNarrativeAsset {
  reveal(JoviaIllustrationAsset.layers),
  signal(JoviaIllustrationAsset.dots),
  threshold(JoviaIllustrationAsset.blocks),
  echo(JoviaIllustrationAsset.bird),
  fateOrbit(JoviaIllustrationAsset.planet),
  integrationWave(JoviaIllustrationAsset.layers);

  const JoviaNarrativeAsset(this.illustration);

  final JoviaIllustrationAsset illustration;
}

enum JoviaEditorialSurfaceVariant {
  homeHero,
  profileHero,
  bondHero,
  detailHero,
  readingSurface,
}

class JoviaEditorialArtResolver {
  const JoviaEditorialArtResolver._();

  static JoviaColorAsset colorForSurface(JoviaEditorialSurfaceVariant variant) {
    return switch (variant) {
      JoviaEditorialSurfaceVariant.homeHero => JoviaColorAsset.wash03,
      JoviaEditorialSurfaceVariant.profileHero => JoviaColorAsset.wash11,
      JoviaEditorialSurfaceVariant.bondHero => JoviaColorAsset.wash05,
      JoviaEditorialSurfaceVariant.detailHero => JoviaColorAsset.wash13,
      JoviaEditorialSurfaceVariant.readingSurface => JoviaColorAsset.wash09,
    };
  }

  static JoviaIllustrationAsset? illustrationForSurface(
    JoviaEditorialSurfaceVariant variant,
  ) {
    return switch (variant) {
      JoviaEditorialSurfaceVariant.homeHero => JoviaIllustrationAsset.dots,
      JoviaEditorialSurfaceVariant.profileHero => null,
      JoviaEditorialSurfaceVariant.bondHero => JoviaIllustrationAsset.heart,
      JoviaEditorialSurfaceVariant.detailHero => JoviaIllustrationAsset.planet,
      JoviaEditorialSurfaceVariant.readingSurface =>
        JoviaIllustrationAsset.layers,
    };
  }
}
