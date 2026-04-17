import 'package:flutter/material.dart';

import 'package:mobile/design/assets/shou_brand_assets.dart';

enum ShouWordmarkTone { auto, light, dark }

enum ShouSymbolTone { lime, dark }

class ShouWordmark extends StatelessWidget {
  const ShouWordmark({
    super.key,
    this.width,
    this.height,
    this.fit = BoxFit.contain,
    this.alignment = Alignment.centerLeft,
    this.tone = ShouWordmarkTone.auto,
    this.color,
  });

  final double? width;
  final double? height;
  final BoxFit fit;
  final Alignment alignment;
  final ShouWordmarkTone tone;
  final Color? color;

  @override
  Widget build(BuildContext context) {
    final brightness = Theme.of(context).brightness;
    final path = switch (tone) {
      ShouWordmarkTone.auto => ShouBrandAssets.wordmarkForSurfaceBrightness(
        brightness,
      ),
      ShouWordmarkTone.light => ShouBrandAssets.wordmarkLight,
      ShouWordmarkTone.dark => ShouBrandAssets.wordmarkDark,
    };
    return Image.asset(
      path,
      width: width,
      height: height,
      fit: fit,
      alignment: alignment,
      color: color,
      colorBlendMode: color == null ? null : BlendMode.srcIn,
    );
  }
}

class ShouSymbol extends StatelessWidget {
  const ShouSymbol({
    super.key,
    this.size = 96,
    this.fit = BoxFit.contain,
    this.alignment = Alignment.center,
    this.tone = ShouSymbolTone.lime,
    this.color,
  });

  final double size;
  final BoxFit fit;
  final Alignment alignment;
  final ShouSymbolTone tone;
  final Color? color;

  @override
  Widget build(BuildContext context) {
    final path = tone == ShouSymbolTone.lime
        ? ShouBrandAssets.symbolLime
        : ShouBrandAssets.symbolDark;
    return Image.asset(
      path,
      width: size,
      height: size,
      fit: fit,
      alignment: alignment,
      color: color,
      colorBlendMode: color == null ? null : BlendMode.srcIn,
    );
  }
}
