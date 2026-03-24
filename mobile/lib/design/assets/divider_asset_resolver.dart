const String joviaDividerAssetRoot = 'ios/Flutter/assets/dividers';

enum JoviaDividerKind {
  cutLine('$joviaDividerAssetRoot/cut line divider.svg'),
  divider1('$joviaDividerAssetRoot/divider1.svg'),
  divider2('$joviaDividerAssetRoot/divider2.svg'),
  divider3('$joviaDividerAssetRoot/divider3.svg'),
  divider4('$joviaDividerAssetRoot/divider4.svg'),
  divider5('$joviaDividerAssetRoot/divider5.svg'),
  divider6('$joviaDividerAssetRoot/divider6.svg');

  const JoviaDividerKind(this.path);

  final String path;
}

enum JoviaDividerVariant {
  homeHeroBreak(JoviaDividerKind.divider1, 148),
  homeTimingBreak(JoviaDividerKind.divider2, 124),
  profileHeroBreak(JoviaDividerKind.divider3, 132),
  profileReadingBreak(JoviaDividerKind.divider5, 128),
  bondSectionBreak(JoviaDividerKind.divider6, 128),
  detailBreak(JoviaDividerKind.divider2, 132);

  const JoviaDividerVariant(this.kind, this.defaultWidth);

  final JoviaDividerKind kind;
  final double defaultWidth;
}
