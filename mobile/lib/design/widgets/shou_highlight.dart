import 'package:flutter/material.dart';

import 'package:mobile/design/theme/profile_theme_extension.dart';

/// SHOU v2 text highlight system.
///
/// Brand guide reserves three inline highlight tones for "text highlight" —
/// short spans of text that sit on a pill-shaped coloured background inside
/// flowing copy. They are never used as full card backgrounds; each tone
/// carries semantic meaning:
///
/// - [ShouHighlightTone.lime]   — potential / opportunity / action
///   ("buradan açılıyor", "bir kez daha geçiyorsun").
/// - [ShouHighlightTone.lavender] — past / defense / bilinçdışı katmanlar
///   ("tam halini görmüyor").
/// - [ShouHighlightTone.stone]  — neutral emphasis / first impression
///   ("ciddi görünür", "ilk izlenim").
///
/// Prefer the [span] factory when inlining inside a [Text.rich] / RichText
/// so the highlight flows with the surrounding paragraph. Use the widget
/// form for standalone badge-style chips.
enum ShouHighlightTone { lime, lavender, stone }

class ShouHighlight extends StatelessWidget {
  const ShouHighlight({
    super.key,
    required this.text,
    this.tone = ShouHighlightTone.lime,
    this.baseStyle,
  });

  final String text;
  final ShouHighlightTone tone;

  /// Optional base style the highlight should inherit from. If null, the
  /// surrounding [DefaultTextStyle] is used.
  final TextStyle? baseStyle;

  /// Inline span form. Drop into a [Text.rich] / [TextSpan] tree to get
  /// a flowing, pill-backed highlight that wraps naturally with the line.
  ///
  /// ```dart
  /// Text.rich(TextSpan(children: [
  ///   const TextSpan(text: 'Söylemeden önce içinden '),
  ///   ShouHighlight.span(
  ///     context,
  ///     text: 'bir kez daha geçiyorsun.',
  ///     tone: ShouHighlightTone.lime,
  ///   ),
  /// ]));
  /// ```
  static InlineSpan span(
    BuildContext context, {
    required String text,
    ShouHighlightTone tone = ShouHighlightTone.lime,
    TextStyle? baseStyle,
  }) {
    return WidgetSpan(
      alignment: PlaceholderAlignment.baseline,
      baseline: TextBaseline.alphabetic,
      child: ShouHighlight(text: text, tone: tone, baseStyle: baseStyle),
    );
  }

  _ShouHighlightPalette _palette(BuildContext context) {
    final colors = context.profileTheme.colors;
    switch (tone) {
      case ShouHighlightTone.lime:
        return _ShouHighlightPalette(
          background: colors.brandLime,
          foreground: colors.limeText,
        );
      case ShouHighlightTone.lavender:
        return _ShouHighlightPalette(
          background: colors.lavBg,
          foreground: colors.lavText,
        );
      case ShouHighlightTone.stone:
        return _ShouHighlightPalette(
          background: colors.stone,
          foreground: colors.stoneText,
        );
    }
  }

  @override
  Widget build(BuildContext context) {
    final palette = _palette(context);
    final inherited =
        baseStyle ?? DefaultTextStyle.of(context).style;
    final style = inherited.copyWith(color: palette.foreground);

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 1),
      decoration: BoxDecoration(
        color: palette.background,
        borderRadius: BorderRadius.circular(3),
      ),
      child: Text(text, style: style),
    );
  }
}

class _ShouHighlightPalette {
  const _ShouHighlightPalette({
    required this.background,
    required this.foreground,
  });

  final Color background;
  final Color foreground;
}
