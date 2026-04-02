import 'dart:async';
import 'dart:ui';

import 'package:flutter/material.dart';

import 'package:mobile/app/timing/turkish_text.dart';
import 'package:mobile/design/theme/profile_theme_extension.dart';
import 'package:mobile/design/widgets/jovia_assets.dart';

export 'package:mobile/design/widgets/jovia_assets.dart';
export 'package:mobile/ui/components/editorial_divider.dart';

enum JoviaSectionHeaderVariant { standard, editorial }

class JoviaReveal extends StatefulWidget {
  const JoviaReveal({
    super.key,
    required this.child,
    this.delay = Duration.zero,
  });

  final Widget child;
  final Duration delay;

  @override
  State<JoviaReveal> createState() => _JoviaRevealState();
}

class _JoviaRevealState extends State<JoviaReveal> {
  Timer? _timer;
  bool _visible = false;

  @override
  void initState() {
    super.initState();
    _timer = Timer(widget.delay, () {
      if (!mounted) {
        return;
      }
      setState(() => _visible = true);
    });
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedOpacity(
      opacity: _visible ? 1 : 0,
      duration: const Duration(milliseconds: 460),
      curve: Curves.easeOutCubic,
      child: AnimatedSlide(
        offset: _visible ? Offset.zero : const Offset(0, 0.02),
        duration: const Duration(milliseconds: 520),
        curve: Curves.easeOutCubic,
        child: widget.child,
      ),
    );
  }
}

class JoviaPageScaffold extends StatelessWidget {
  const JoviaPageScaffold({
    super.key,
    required this.child,
    this.padding = const EdgeInsets.fromLTRB(24, 20, 24, 32),
  });

  final Widget child;
  final EdgeInsetsGeometry padding;

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      top: false,
      child: Padding(padding: padding, child: child),
    );
  }
}

class JoviaPressable extends StatefulWidget {
  const JoviaPressable({
    super.key,
    required this.child,
    this.onTap,
    this.onLongPress,
    this.borderRadius,
    this.pressedScale = 0.985,
  });

  final Widget child;
  final VoidCallback? onTap;
  final VoidCallback? onLongPress;
  final BorderRadius? borderRadius;
  final double pressedScale;

  @override
  State<JoviaPressable> createState() => _JoviaPressableState();
}

class _JoviaPressableState extends State<JoviaPressable> {
  bool _pressed = false;

  @override
  Widget build(BuildContext context) {
    final radius = widget.borderRadius ?? BorderRadius.circular(24);
    return AnimatedScale(
      scale: _pressed ? widget.pressedScale : 1,
      duration: const Duration(milliseconds: 120),
      curve: Curves.easeOutCubic,
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: widget.onTap,
          onLongPress: widget.onLongPress,
          onHighlightChanged: (value) {
            if (_pressed == value) {
              return;
            }
            setState(() => _pressed = value);
          },
          borderRadius: radius,
          splashColor: context.profileTheme.colors.warmAccent.withValues(
            alpha: 0.08,
          ),
          highlightColor: Colors.transparent,
          child: widget.child,
        ),
      ),
    );
  }
}

class JoviaSurfaceCard extends StatelessWidget {
  const JoviaSurfaceCard({
    super.key,
    required this.child,
    this.padding = const EdgeInsets.all(20),
    this.color,
    this.backgroundColor,
    this.borderColor,
    this.radius = 28,
    this.shadow = true,
  });

  final Widget child;
  final EdgeInsetsGeometry padding;
  final Color? color;
  final Color? backgroundColor;
  final Color? borderColor;
  final double radius;
  final bool shadow;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final base = backgroundColor ?? color ?? profile.colors.surface;
    final stroke = borderColor ?? profile.colors.strokeSoft;
    final topBlend = Color.alphaBlend(
      Colors.white.withValues(alpha: isDark ? 0.14 : 0.72),
      base,
    );
    final bottomBlend = Color.alphaBlend(
      Colors.black.withValues(alpha: isDark ? 0.14 : 0.04),
      base,
    );
    return ClipRRect(
      borderRadius: BorderRadius.circular(radius),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 20, sigmaY: 20),
        child: Container(
          padding: padding,
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                topBlend.withValues(alpha: isDark ? 0.88 : 0.94),
                base.withValues(alpha: isDark ? 0.86 : 0.9),
                bottomBlend.withValues(alpha: isDark ? 0.92 : 0.96),
              ],
            ),
            borderRadius: BorderRadius.circular(radius),
            border: Border.all(color: stroke, width: 1.1),
            boxShadow: shadow
                ? [
                    profile.shadows.cardShadow,
                    BoxShadow(
                      color: Colors.white.withValues(
                        alpha: isDark ? 0.04 : 0.7,
                      ),
                      blurRadius: 24,
                      offset: const Offset(-10, -10),
                      spreadRadius: -24,
                    ),
                  ]
                : const [],
          ),
          child: Stack(
            children: [
              Positioned(
                left: 0,
                right: 0,
                top: 0,
                child: IgnorePointer(
                  child: Container(
                    height: 1,
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: [
                          Colors.transparent,
                          Colors.white.withValues(alpha: isDark ? 0.18 : 0.9),
                          Colors.transparent,
                        ],
                      ),
                    ),
                  ),
                ),
              ),
              child,
            ],
          ),
        ),
      ),
    );
  }
}

class JoviaProfileTopBar extends StatelessWidget {
  const JoviaProfileTopBar({
    super.key,
    required this.label,
    this.centerText,
    this.onBackTap,
    this.onActionTap,
    this.actionAsset,
    this.actionTooltip,
    this.reserveTrailingSpace = false,
  });

  final String label;
  final String? centerText;
  final VoidCallback? onBackTap;
  final VoidCallback? onActionTap;
  final JoviaUiAsset? actionAsset;
  final String? actionTooltip;
  final bool reserveTrailingSpace;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final center = (centerText ?? '').trim();
    final trailingAsset = actionAsset;
    return Row(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        JoviaGlassIconButton(
          onTap: onBackTap ?? () => Navigator.of(context).maybePop(),
          size: 46,
          child: const JoviaUiIcon(asset: JoviaUiAsset.back, size: 17),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              Text(
                turkishToUpper(label),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: profile.typography.monoEyebrow.copyWith(
                  color: profile.colors.textLight,
                  fontSize: 11.5,
                  letterSpacing: 2.1,
                ),
              ),
              if (center.isNotEmpty) ...[
                const SizedBox(height: 5),
                Text(
                  center,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  textAlign: TextAlign.center,
                  style: profile.typography.metaSoft.copyWith(
                    color: profile.colors.text.withValues(alpha: 0.94),
                    fontSize: 12.5,
                    letterSpacing: 0.18,
                  ),
                ),
              ],
            ],
          ),
        ),
        const SizedBox(width: 12),
        if (onActionTap != null && trailingAsset != null)
          Tooltip(
            message: actionTooltip ?? '',
            child: JoviaGlassIconButton(
              onTap: onActionTap,
              size: 50,
              child: JoviaUiIcon(asset: trailingAsset, size: 18),
            ),
          )
        else if (reserveTrailingSpace)
          const SizedBox(width: 50, height: 50)
        else
          const SizedBox.shrink(),
      ],
    );
  }
}

class JoviaSectionHeader extends StatelessWidget {
  const JoviaSectionHeader({
    super.key,
    required this.title,
    this.label,
    this.body,
    this.variant = JoviaSectionHeaderVariant.standard,
  });

  final String title;
  final String? label;
  final String? body;
  final JoviaSectionHeaderVariant variant;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final resolvedLabel = (label ?? '').trim();
    final resolvedBody = (body ?? '').trim();
    final hasBody = resolvedBody.isNotEmpty;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (resolvedLabel.isNotEmpty) ...[
          Text(
            turkishToUpper(resolvedLabel),
            style: profile.typography.monoEyebrow.copyWith(
              color: profile.colors.textLight,
              letterSpacing: variant == JoviaSectionHeaderVariant.editorial
                  ? 1.95
                  : 1.55,
            ),
          ),
          const SizedBox(height: 8),
        ],
        Text(
          title,
          style:
              (variant == JoviaSectionHeaderVariant.editorial
                      ? profile.typography.section.copyWith(
                          fontSize: 26,
                          height: 1.08,
                          fontWeight: FontWeight.w600,
                        )
                      : profile.typography.card)
                  .copyWith(
                    color: profile.colors.text,
                    letterSpacing:
                        variant == JoviaSectionHeaderVariant.editorial
                        ? -0.42
                        : -0.22,
                  ),
        ),
        if (hasBody) ...[
          const SizedBox(height: 10),
          Text(
            resolvedBody,
            style: profile.typography.bodyCompact.copyWith(
              color: profile.colors.textLight,
              height: 1.48,
            ),
          ),
        ],
      ],
    );
  }
}

class JoviaReadingPanel extends StatelessWidget {
  const JoviaReadingPanel({
    super.key,
    this.label,
    this.title,
    this.body,
    this.child,
    this.leading,
    this.background,
    this.padding = const EdgeInsets.all(18),
    this.large = false,
  });

  final String? label;
  final String? title;
  final String? body;
  final Widget? child;
  final Widget? leading;
  final Widget? background;
  final EdgeInsetsGeometry padding;
  final bool large;

  @override
  Widget build(BuildContext context) {
    final resolvedLabel = (label ?? '').trim();
    final resolvedTitle = (title ?? '').trim();
    final resolvedBody = (body ?? '').trim();
    final backgroundLayer = background;
    final leadingWidget = leading;
    final hasHeader =
        resolvedLabel.isNotEmpty ||
        resolvedTitle.isNotEmpty ||
        resolvedBody.isNotEmpty;
    final content =
        child ??
        (resolvedBody.isEmpty
            ? const SizedBox.shrink()
            : Text(
                resolvedBody,
                style: context.profileTheme.typography.bodyCompact.copyWith(
                  color: context.profileTheme.colors.text,
                ),
              ));

    return JoviaSurfaceCard(
      padding: large ? const EdgeInsets.fromLTRB(20, 20, 20, 18) : padding,
      child: Stack(
        children: [
          if (backgroundLayer != null) Positioned.fill(child: backgroundLayer),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              if (leadingWidget != null || hasHeader)
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    if (leadingWidget != null) ...[
                      leadingWidget,
                      const SizedBox(width: 10),
                    ],
                    Expanded(
                      child: JoviaSectionHeader(
                        label: resolvedLabel.isEmpty ? null : resolvedLabel,
                        title: resolvedTitle.isEmpty
                            ? resolvedLabel
                            : resolvedTitle,
                        body:
                            hasHeader &&
                                child != null &&
                                resolvedBody.isNotEmpty
                            ? resolvedBody
                            : null,
                      ),
                    ),
                  ],
                ),
              if (hasHeader && child != null) const SizedBox(height: 14),
              content,
            ],
          ),
        ],
      ),
    );
  }
}

class JoviaTopicSurface extends StatelessWidget {
  const JoviaTopicSurface({
    super.key,
    required this.title,
    required this.body,
    this.eyebrow,
    this.meta = const <String>[],
    this.secondaryAction,
    this.onTap,
  });

  final String title;
  final String body;
  final String? eyebrow;
  final List<String> meta;
  final Widget? secondaryAction;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final resolvedEyebrow = (eyebrow ?? '').trim();
    final action = secondaryAction;
    return JoviaPressable(
      onTap: onTap,
      borderRadius: BorderRadius.circular(22),
      child: JoviaSurfaceCard(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (resolvedEyebrow.isNotEmpty) ...[
              Text(
                turkishToUpper(resolvedEyebrow),
                style: profile.typography.eyebrow.copyWith(
                  color: profile.colors.textLight,
                  letterSpacing: 1.4,
                ),
              ),
              const SizedBox(height: 6),
            ],
            Text(title, style: profile.typography.cardTitle),
            const SizedBox(height: 8),
            Text(
              body,
              style: profile.typography.bodyCompact.copyWith(
                color: profile.colors.textLight,
              ),
            ),
            if (meta.isNotEmpty) ...[
              const SizedBox(height: 12),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  for (final item in meta.take(3)) JoviaMetaPill(label: item),
                ],
              ),
            ],
            if (action != null) ...[const SizedBox(height: 14), action],
          ],
        ),
      ),
    );
  }
}

class JoviaPrimaryButton extends StatelessWidget {
  const JoviaPrimaryButton({
    super.key,
    required this.label,
    required this.onTap,
    this.leading,
  });

  final String label;
  final VoidCallback? onTap;
  final Widget? leading;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final leadingWidget = leading;
    final background = Color.alphaBlend(
      profile.colors.warmAccent.withValues(alpha: 0.2),
      profile.colors.panelSoft,
    );
    final foreground = profile.colors.text;
    return JoviaPressable(
      onTap: onTap,
      borderRadius: BorderRadius.circular(999),
      child: Container(
        constraints: BoxConstraints(minHeight: profile.spacing.buttonHeight),
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 13),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Colors.white.withValues(
                alpha: Theme.of(context).brightness == Brightness.dark
                    ? 0.14
                    : 0.92,
              ),
              background,
            ],
          ),
          borderRadius: BorderRadius.circular(999),
          border: Border.all(color: profile.colors.strokeSoft, width: 1),
          boxShadow: [
            BoxShadow(
              color: profile.colors.shadowLift.withValues(alpha: 0.16),
              blurRadius: 22,
              offset: const Offset(0, 14),
              spreadRadius: -18,
            ),
          ],
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          mainAxisSize: MainAxisSize.min,
          children: [
            if (leadingWidget != null) ...[
              leadingWidget,
              const SizedBox(width: 8),
            ],
            Text(
              label,
              style: profile.typography.buttonLabel.copyWith(
                color: foreground,
                fontWeight: FontWeight.w700,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class MinimalCTAButton extends StatelessWidget {
  const MinimalCTAButton({
    super.key,
    required this.label,
    this.onTap,
    this.emphasized = false,
    this.glassy = false,
  });

  final String label;
  final VoidCallback? onTap;
  final bool emphasized;
  final bool glassy;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final background = emphasized
        ? Color.alphaBlend(
            profile.colors.warmAccent.withValues(alpha: 0.22),
            profile.colors.panelSoft,
          )
        : glassy
        ? Color.alphaBlend(
            Colors.white.withValues(alpha: 0.08),
            profile.colors.buttonSecondary,
          )
        : profile.colors.panelStrong;
    final foreground = profile.colors.text;

    return JoviaPressable(
      onTap: onTap,
      borderRadius: BorderRadius.circular(999),
      child: Container(
        constraints: BoxConstraints(minHeight: profile.spacing.pillHeight),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Colors.white.withValues(
                alpha: Theme.of(context).brightness == Brightness.dark
                    ? 0.12
                    : 0.86,
              ),
              background,
            ],
          ),
          borderRadius: BorderRadius.circular(999),
          border: Border.all(
            color: emphasized
                ? profile.colors.chipBorder
                : profile.colors.hairline,
            width: 1.05,
          ),
          boxShadow: [
            BoxShadow(
              color: profile.colors.shadowLift.withValues(
                alpha: emphasized ? 0.14 : 0.08,
              ),
              blurRadius: emphasized ? 20 : 14,
              offset: const Offset(0, 10),
              spreadRadius: -14,
            ),
          ],
        ),
        child: Text(
          label,
          style: profile.typography.buttonLabel.copyWith(
            color: foreground,
            fontWeight: FontWeight.w700,
          ),
        ),
      ),
    );
  }
}

class JoviaUtilityRow extends StatelessWidget {
  const JoviaUtilityRow({
    super.key,
    this.label,
    required this.title,
    this.body,
    this.meta = const <String>[],
    this.leading,
    this.trailing,
    this.onTap,
  });

  final String? label;
  final String title;
  final String? body;
  final List<String> meta;
  final Widget? leading;
  final Widget? trailing;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final resolvedLabel = (label ?? '').trim();
    final resolvedBody = (body ?? '').trim();
    final leadingWidget = leading;
    final trailingWidget = trailing;
    return JoviaPressable(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 8),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (leadingWidget != null) ...[
              leadingWidget,
              const SizedBox(width: 12),
            ],
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (resolvedLabel.isNotEmpty) ...[
                    Text(
                      turkishToUpper(resolvedLabel),
                      style: profile.typography.eyebrow.copyWith(
                        color: profile.colors.textLight,
                        letterSpacing: 1.3,
                      ),
                    ),
                    const SizedBox(height: 4),
                  ],
                  Text(title, style: profile.typography.cardTitle),
                  if (resolvedBody.isNotEmpty) ...[
                    const SizedBox(height: 4),
                    Text(
                      resolvedBody,
                      style: profile.typography.bodyCompact.copyWith(
                        color: profile.colors.textLight,
                      ),
                    ),
                  ],
                  if (meta.isNotEmpty) ...[
                    const SizedBox(height: 8),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: [
                        for (final item in meta.take(2))
                          JoviaMetaPill(label: item),
                      ],
                    ),
                  ],
                ],
              ),
            ),
            if (trailingWidget != null) ...[
              const SizedBox(width: 12),
              trailingWidget,
            ],
          ],
        ),
      ),
    );
  }
}

class JoviaInsightListItem extends StatelessWidget {
  const JoviaInsightListItem({
    super.key,
    required this.title,
    required this.body,
    this.meta = const <String>[],
    this.trailing,
    this.onTap,
  });

  final String title;
  final String body;
  final List<String> meta;
  final Widget? trailing;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return JoviaUtilityRow(
      title: title,
      body: body,
      meta: meta,
      trailing: trailing,
      onTap: onTap,
    );
  }
}

class EditorialListItem extends StatelessWidget {
  const EditorialListItem({
    super.key,
    required this.title,
    required this.body,
    this.meta = const <String>[],
    this.leading,
    this.trailing,
    this.onTap,
  });

  final String title;
  final String body;
  final List<String> meta;
  final Widget? leading;
  final Widget? trailing;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return JoviaUtilityRow(
      title: title,
      body: body,
      meta: meta,
      leading: leading,
      trailing: trailing,
      onTap: onTap,
    );
  }
}

class JoviaGlassIconButton extends StatelessWidget {
  const JoviaGlassIconButton({
    super.key,
    required this.child,
    this.onTap,
    this.size = 42,
  });

  final Widget child;
  final VoidCallback? onTap;
  final double size;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return JoviaPressable(
      onTap: onTap,
      borderRadius: BorderRadius.circular(size / 2),
      child: Container(
        width: size,
        height: size,
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Colors.white.withValues(alpha: isDark ? 0.14 : 0.9),
              profile.colors.buttonSecondary.withValues(alpha: 0.94),
            ],
          ),
          borderRadius: BorderRadius.circular(size / 2),
          border: Border.all(color: profile.colors.strokeSoft, width: 1.05),
          boxShadow: [
            BoxShadow(
              color: profile.colors.shadowLift.withValues(alpha: 0.12),
              blurRadius: 18,
              offset: const Offset(0, 10),
              spreadRadius: -16,
            ),
          ],
        ),
        child: Center(child: child),
      ),
    );
  }
}

class JoviaMetaPill extends StatelessWidget {
  const JoviaMetaPill({super.key, required this.label});

  final String label;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            Colors.white.withValues(
              alpha: Theme.of(context).brightness == Brightness.dark
                  ? 0.08
                  : 0.84,
            ),
            profile.colors.chipBg,
          ],
        ),
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: profile.colors.strokeSoft, width: 1),
      ),
      child: Text(
        label,
        style: profile.typography.micro.copyWith(
          color: profile.colors.textLight,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }
}

class JoviaSegmentedControl<T> extends StatelessWidget {
  const JoviaSegmentedControl({
    super.key,
    required this.value,
    required this.options,
    required this.labelBuilder,
    required this.onChanged,
  });

  final T value;
  final List<T> options;
  final String Function(T value) labelBuilder;
  final ValueChanged<T> onChanged;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final trackColor = isDark
        ? const Color(0xFF090807)
        : Color.alphaBlend(
            profile.colors.primary.withValues(alpha: 0.08),
            profile.colors.panelStrong,
          );
    final selectedColor = isDark
        ? const Color(0xFF15110F)
        : Color.alphaBlend(
            Colors.white.withValues(alpha: 0.76),
            profile.colors.panelSoft,
          );
    return Container(
      padding: const EdgeInsets.all(4),
      decoration: BoxDecoration(
        color: trackColor,
        borderRadius: BorderRadius.circular(999),
        border: Border.all(
          color: isDark ? profile.colors.strokeSoft : profile.colors.chipBorder,
          width: 1.05,
        ),
        boxShadow: [
          BoxShadow(
            color: (isDark ? Colors.black : profile.colors.shadowLift)
                .withValues(alpha: isDark ? 0.12 : 0.08),
            blurRadius: isDark ? 10 : 14,
            offset: const Offset(0, 6),
            spreadRadius: -14,
          ),
        ],
      ),
      child: Row(
        children: [
          for (final option in options)
            Expanded(
              child: JoviaPressable(
                onTap: () => onChanged(option),
                borderRadius: BorderRadius.circular(999),
                child: Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 11,
                  ),
                  decoration: BoxDecoration(
                    color: option == value ? selectedColor : Colors.transparent,
                    borderRadius: BorderRadius.circular(999),
                    border: option == value
                        ? Border.all(
                            color: isDark
                                ? profile.colors.strokeSoft
                                : profile.colors.chipBorder,
                            width: 1,
                          )
                        : null,
                    boxShadow: option == value
                        ? [
                            BoxShadow(
                              color:
                                  (isDark
                                          ? Colors.black
                                          : profile.colors.shadowLift)
                                      .withValues(alpha: isDark ? 0.14 : 0.08),
                              blurRadius: isDark ? 8 : 12,
                              offset: const Offset(0, 4),
                              spreadRadius: -10,
                            ),
                          ]
                        : const [],
                  ),
                  child: Text(
                    labelBuilder(option),
                    textAlign: TextAlign.center,
                    style: profile.typography.buttonLabel.copyWith(
                      color: option == value
                          ? profile.colors.text
                          : profile.colors.textLight,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }
}

class JoviaModeSwitch<T> extends StatelessWidget {
  const JoviaModeSwitch({
    super.key,
    required this.value,
    required this.leadingValue,
    required this.leadingLabel,
    required this.trailingValue,
    required this.trailingLabel,
    required this.onChanged,
  });

  final T value;
  final T leadingValue;
  final String leadingLabel;
  final T trailingValue;
  final String trailingLabel;
  final ValueChanged<T> onChanged;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final leadingSelected = value == leadingValue;
    return JoviaSurfaceCard(
      radius: 999,
      padding: const EdgeInsets.all(4),
      child: SizedBox(
        height: 52,
        child: Stack(
          children: [
            AnimatedAlign(
              duration: const Duration(milliseconds: 280),
              curve: Curves.easeOutCubic,
              alignment: leadingSelected
                  ? Alignment.centerLeft
                  : Alignment.centerRight,
              child: FractionallySizedBox(
                widthFactor: 0.5,
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 2),
                  child: JoviaSurfaceCard(
                    radius: 999,
                    padding: const EdgeInsets.symmetric(vertical: 11),
                    backgroundColor: Color.alphaBlend(
                      profile.colors.warmAccent.withValues(alpha: 0.16),
                      profile.colors.panelSoft,
                    ),
                    borderColor: profile.colors.chipBorder,
                    child: const SizedBox.expand(),
                  ),
                ),
              ),
            ),
            Row(
              children: [
                Expanded(
                  child: JoviaPressable(
                    onTap: () => onChanged(leadingValue),
                    borderRadius: BorderRadius.circular(999),
                    child: Center(
                      child: Text(
                        leadingLabel,
                        style: profile.typography.buttonLabel.copyWith(
                          color: profile.colors.text,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ),
                  ),
                ),
                Expanded(
                  child: JoviaPressable(
                    onTap: () => onChanged(trailingValue),
                    borderRadius: BorderRadius.circular(999),
                    child: Center(
                      child: Text(
                        trailingLabel,
                        style: profile.typography.buttonLabel.copyWith(
                          color: profile.colors.text,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class JoviaEditorialHeroBlock extends StatelessWidget {
  const JoviaEditorialHeroBlock({
    super.key,
    required this.title,
    this.label,
    this.body,
    this.titleStyle,
    this.titleMaxLines = 3,
    this.bodyMaxLines = 5,
    this.glyph,
    this.background,
    this.accent,
    this.footer,
    this.surface = true,
    this.large = false,
  });

  final String title;
  final String? label;
  final String? body;
  final TextStyle? titleStyle;
  final int titleMaxLines;
  final int bodyMaxLines;
  final Widget? glyph;
  final Widget? background;
  final Widget? accent;
  final Widget? footer;
  final bool surface;
  final bool large;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final resolvedLabel = (label ?? '').trim();
    final resolvedBody = (body ?? '').trim();
    final backgroundLayer = background;
    final accentWidget = accent;
    final glyphWidget = glyph;
    final footerWidget = footer;
    final content = Stack(
      children: [
        if (backgroundLayer != null) Positioned.fill(child: backgroundLayer),
        if (accentWidget != null)
          Positioned(
            right: 0,
            top: 0,
            child: IgnorePointer(child: accentWidget),
          ),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (glyphWidget != null || resolvedLabel.isNotEmpty)
              Row(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  if (glyphWidget != null) ...[
                    glyphWidget,
                    const SizedBox(width: 8),
                  ],
                  if (resolvedLabel.isNotEmpty)
                    Expanded(
                      child: Text(
                        turkishToUpper(resolvedLabel),
                        style: profile.typography.eyebrow.copyWith(
                          color: profile.colors.textLight,
                          letterSpacing: 1.5,
                        ),
                      ),
                    ),
                ],
              ),
            if (glyphWidget != null || resolvedLabel.isNotEmpty)
              const SizedBox(height: 12),
            Text(
              title,
              maxLines: titleMaxLines,
              overflow: TextOverflow.ellipsis,
              style:
                  titleStyle ??
                  profile.typography.pageTitle.copyWith(
                    color: profile.colors.text,
                    fontSize: large ? 32 : 26,
                    height: 1.05,
                  ),
            ),
            if (resolvedBody.isNotEmpty) ...[
              const SizedBox(height: 12),
              Text(
                resolvedBody,
                maxLines: bodyMaxLines,
                overflow: TextOverflow.ellipsis,
                style: profile.typography.bodyCompact.copyWith(
                  color: profile.colors.textLight,
                ),
              ),
            ],
            if (footerWidget != null) ...[
              const SizedBox(height: 16),
              footerWidget,
            ],
          ],
        ),
      ],
    );

    if (!surface) {
      return content;
    }
    return JoviaSurfaceCard(
      padding: EdgeInsets.all(large ? 24 : 20),
      child: content,
    );
  }
}

class JoviaActionRail extends StatelessWidget {
  const JoviaActionRail({
    super.key,
    required this.title,
    this.body,
    this.leading,
    this.primaryAction,
    this.secondaryActions = const <Widget>[],
    this.showTopDivider = true,
  });

  final String title;
  final String? body;
  final Widget? leading;
  final Widget? primaryAction;
  final List<Widget> secondaryActions;
  final bool showTopDivider;

  @override
  Widget build(BuildContext context) {
    final leadingWidget = leading;
    final primary = primaryAction;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (showTopDivider) const ThinDivider(),
        if (showTopDivider) const SizedBox(height: 14),
        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (leadingWidget != null) ...[
              leadingWidget,
              const SizedBox(width: 10),
            ],
            Expanded(
              child: JoviaSectionHeader(title: title, body: body),
            ),
          ],
        ),
        const SizedBox(height: 14),
        if (primary != null) ...[primary],
        if (secondaryActions.isNotEmpty) ...[
          const SizedBox(height: 12),
          Wrap(spacing: 10, runSpacing: 10, children: secondaryActions),
        ],
      ],
    );
  }
}

class JoviaInteractiveSocialBar extends StatelessWidget {
  const JoviaInteractiveSocialBar({
    super.key,
    required this.seedKey,
    required this.title,
    required this.initialLikeCount,
    required this.initialCommentCount,
    this.color,
  });

  final String seedKey;
  final String title;
  final int initialLikeCount;
  final int initialCommentCount;
  final Color? color;

  @override
  Widget build(BuildContext context) {
    final tint = color ?? context.profileTheme.colors.text;
    return Row(
      children: [
        _SocialPill(
          icon: Icons.favorite_border_rounded,
          label: initialLikeCount.toString(),
          color: tint,
        ),
        const SizedBox(width: 8),
        _SocialPill(
          icon: Icons.mode_comment_outlined,
          label: initialCommentCount.toString(),
          color: tint,
        ),
      ],
    );
  }
}

class _SocialPill extends StatelessWidget {
  const _SocialPill({
    required this.icon,
    required this.label,
    required this.color,
  });

  final IconData icon;
  final String label;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: color.withValues(alpha: 0.2)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 14, color: color),
          const SizedBox(width: 6),
          Text(
            label,
            style: TextStyle(color: color, fontWeight: FontWeight.w700),
          ),
        ],
      ),
    );
  }
}

class JoviaBottomNavItem {
  const JoviaBottomNavItem({
    required this.icon,
    required this.label,
    this.prominent = false,
    this.showLabel = false,
  });

  final Widget icon;
  final String label;
  final bool prominent;
  final bool showLabel;
}

class JoviaBottomNavBar extends StatelessWidget {
  const JoviaBottomNavBar({
    super.key,
    required this.currentIndex,
    required this.onTap,
    required this.items,
  });

  final int currentIndex;
  final ValueChanged<int> onTap;
  final List<JoviaBottomNavItem> items;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final shellColor = Theme.of(context).brightness == Brightness.dark
        ? const Color(0xFFF3EEE8)
        : profile.colors.surface;
    final shellBorder = Theme.of(context).brightness == Brightness.dark
        ? const Color(0x26FFFFFF)
        : profile.colors.border.withValues(alpha: 0.74);
    return SafeArea(
      top: false,
      child: Container(
        margin: const EdgeInsets.fromLTRB(16, 0, 16, 14),
        constraints: const BoxConstraints(minHeight: 78),
        padding: const EdgeInsets.fromLTRB(12, 8, 12, 8),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              shellColor,
              Color.alphaBlend(const Color(0x0D000000), shellColor),
            ],
          ),
          borderRadius: BorderRadius.circular(36),
          border: Border.all(color: shellBorder, width: 1),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.2),
              blurRadius: 30,
              offset: const Offset(0, 18),
              spreadRadius: -22,
            ),
          ],
        ),
        child: Row(
          children: [
            for (var index = 0; index < items.length; index++)
              Expanded(
                child: JoviaPressable(
                  onTap: () => onTap(index),
                  borderRadius: BorderRadius.circular(22),
                  child: _BottomNavCell(
                    item: items[index],
                    selected: index == currentIndex,
                    profile: profile,
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}

class _BottomNavCell extends StatelessWidget {
  const _BottomNavCell({
    required this.item,
    required this.selected,
    required this.profile,
  });

  final JoviaBottomNavItem item;
  final bool selected;
  final ProfileTheme profile;

  @override
  Widget build(BuildContext context) {
    final iconColor = item.prominent
        ? Colors.white
        : selected
        ? const Color(0xFF171311)
        : const Color(0xFF91877D);

    return SizedBox(
      height: item.prominent ? 70 : (item.showLabel ? 60 : 48),
      child: Align(
        alignment: Alignment.bottomCenter,
        child: Transform.translate(
          offset: Offset(0, item.prominent ? -18 : 0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              AnimatedContainer(
                duration: const Duration(milliseconds: 220),
                curve: Curves.easeOutCubic,
                width: item.prominent ? 64 : 36,
                height: item.prominent ? 64 : 36,
                decoration: BoxDecoration(
                  color: item.prominent
                      ? const Color(0xFF111111)
                      : selected
                      ? const Color(0x14171311)
                      : Colors.transparent,
                  shape: BoxShape.circle,
                  border: !item.prominent && selected
                      ? Border.all(color: const Color(0x1A171311), width: 1)
                      : null,
                  boxShadow: item.prominent
                      ? [
                          BoxShadow(
                            color: Colors.black.withValues(alpha: 0.3),
                            blurRadius: 26,
                            offset: const Offset(0, 12),
                            spreadRadius: -14,
                          ),
                        ]
                      : const [],
                ),
                child: Center(
                  child: IconTheme(
                    data: IconThemeData(
                      color: iconColor,
                      size: item.prominent ? 30 : 22,
                    ),
                    child: item.icon,
                  ),
                ),
              ),
              if (item.showLabel) ...[
                const SizedBox(height: 6),
                Text(
                  item.label,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: profile.typography.micro.copyWith(
                    color: selected
                        ? const Color(0xFF171311)
                        : const Color(0xFF8F867D),
                    fontWeight: selected ? FontWeight.w700 : FontWeight.w500,
                    fontSize: 10,
                    letterSpacing: 0.02,
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

class ThinDivider extends StatelessWidget {
  const ThinDivider({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 1,
      color: context.profileTheme.colors.strokeSoft.withValues(alpha: 0.62),
    );
  }
}

class EmptyStateBlock extends StatelessWidget {
  const EmptyStateBlock({
    super.key,
    required this.title,
    required this.body,
    this.framed = true,
  });

  final String title;
  final String body;
  final bool framed;

  @override
  Widget build(BuildContext context) {
    final content = Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(title, style: context.profileTheme.typography.cardTitle),
        const SizedBox(height: 8),
        Text(
          body,
          style: context.profileTheme.typography.bodyCompact.copyWith(
            color: context.profileTheme.colors.textLight,
          ),
        ),
      ],
    );
    if (!framed) {
      return content;
    }
    return JoviaSurfaceCard(child: content);
  }
}

class SectionLabel extends StatelessWidget {
  const SectionLabel({super.key, required this.label, required this.title});

  final String label;
  final String title;

  @override
  Widget build(BuildContext context) {
    return JoviaSectionHeader(label: label, title: title);
  }
}
