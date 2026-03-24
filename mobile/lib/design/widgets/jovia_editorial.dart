import 'package:flutter/material.dart';

import 'package:mobile/design/theme/profile_theme_extension.dart';
import 'package:mobile/design/widgets/jovia_assets.dart';

export 'package:mobile/design/widgets/jovia_assets.dart';
export 'package:mobile/ui/components/editorial_divider.dart';

enum JoviaSectionHeaderVariant { standard, editorial }

class JoviaReveal extends StatelessWidget {
  const JoviaReveal({
    super.key,
    required this.child,
    this.delay = Duration.zero,
  });

  final Widget child;
  final Duration delay;

  @override
  Widget build(BuildContext context) {
    return child;
  }
}

class JoviaPageScaffold extends StatelessWidget {
  const JoviaPageScaffold({
    super.key,
    required this.child,
    this.padding = const EdgeInsets.fromLTRB(20, 16, 20, 28),
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

class JoviaPressable extends StatelessWidget {
  const JoviaPressable({
    super.key,
    required this.child,
    this.onTap,
    this.onLongPress,
    this.borderRadius,
  });

  final Widget child;
  final VoidCallback? onTap;
  final VoidCallback? onLongPress;
  final BorderRadius? borderRadius;

  @override
  Widget build(BuildContext context) {
    final radius = borderRadius ?? BorderRadius.circular(18);
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        onLongPress: onLongPress,
        borderRadius: radius,
        child: child,
      ),
    );
  }
}

class JoviaSurfaceCard extends StatelessWidget {
  const JoviaSurfaceCard({
    super.key,
    required this.child,
    this.padding = const EdgeInsets.all(18),
    this.color,
    this.backgroundColor,
    this.borderColor,
    this.radius = 22,
  });

  final Widget child;
  final EdgeInsetsGeometry padding;
  final Color? color;
  final Color? backgroundColor;
  final Color? borderColor;
  final double radius;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Container(
      padding: padding,
      decoration: BoxDecoration(
        color: backgroundColor ?? color ?? profile.colors.surface,
        borderRadius: BorderRadius.circular(radius),
        border: Border.all(
          color: borderColor ?? profile.colors.strokeSoft,
          width: 1.2,
        ),
        boxShadow: [profile.shadows.cardShadow],
      ),
      child: child,
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
    return Row(
      children: [
        JoviaGlassIconButton(
          onTap: onBackTap ?? () => Navigator.of(context).maybePop(),
          child: const JoviaUiIcon(asset: JoviaUiAsset.back, size: 18),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            children: [
              Text(
                label.toUpperCase(),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: profile.typography.eyebrow.copyWith(
                  color: profile.colors.textLight,
                  letterSpacing: 1.5,
                ),
              ),
              if (center.isNotEmpty) ...[
                const SizedBox(height: 4),
                Text(
                  center,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  textAlign: TextAlign.center,
                  style: profile.typography.navigationLabel(
                    color: profile.colors.text,
                  ),
                ),
              ],
            ],
          ),
        ),
        const SizedBox(width: 12),
        if (onActionTap != null && actionAsset != null)
          Tooltip(
            message: actionTooltip ?? '',
            child: JoviaGlassIconButton(
              onTap: onActionTap,
              child: JoviaUiIcon(asset: actionAsset!, size: 18),
            ),
          )
        else if (reserveTrailingSpace)
          const SizedBox(width: 42, height: 42)
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
    final hasBody = (body ?? '').trim().isNotEmpty;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if ((label ?? '').trim().isNotEmpty) ...[
          Text(
            label!.toUpperCase(),
            style: profile.typography.eyebrow.copyWith(
              color: profile.colors.textLight,
              letterSpacing: variant == JoviaSectionHeaderVariant.editorial
                  ? 1.6
                  : 1.3,
            ),
          ),
          const SizedBox(height: 6),
        ],
        Text(
          title,
          style: profile.typography.card.copyWith(
            color: profile.colors.text,
            fontSize: variant == JoviaSectionHeaderVariant.editorial ? 24 : 20,
            height: 1.12,
            fontWeight: FontWeight.w600,
          ),
        ),
        if (hasBody) ...[
          const SizedBox(height: 8),
          Text(
            body!,
            style: profile.typography.bodyCompact.copyWith(
              color: profile.colors.textLight,
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
    final hasHeader =
        (label ?? '').trim().isNotEmpty ||
        (title ?? '').trim().isNotEmpty ||
        (body ?? '').trim().isNotEmpty;
    final content =
        child ??
        ((body ?? '').trim().isEmpty
            ? const SizedBox.shrink()
            : Text(
                body!,
                style: context.profileTheme.typography.bodyCompact.copyWith(
                  color: context.profileTheme.colors.text,
                ),
              ));

    return JoviaSurfaceCard(
      padding: large ? const EdgeInsets.fromLTRB(20, 20, 20, 18) : padding,
      child: Stack(
        children: [
          if (background != null) Positioned.fill(child: background!),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              if (leading != null || hasHeader)
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    if (leading != null) ...[
                      leading!,
                      const SizedBox(width: 10),
                    ],
                    Expanded(
                      child: JoviaSectionHeader(
                        label: label,
                        title: (title ?? '').trim().isEmpty
                            ? (label ?? '')
                            : title!,
                        body: hasHeader && child != null ? body : null,
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
    return JoviaPressable(
      onTap: onTap,
      borderRadius: BorderRadius.circular(22),
      child: JoviaSurfaceCard(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if ((eyebrow ?? '').trim().isNotEmpty) ...[
              Text(
                eyebrow!.toUpperCase(),
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
            if (secondaryAction != null) ...[
              const SizedBox(height: 14),
              secondaryAction!,
            ],
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
    return JoviaPressable(
      onTap: onTap,
      borderRadius: BorderRadius.circular(999),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
        decoration: BoxDecoration(
          color: profile.colors.primary,
          borderRadius: BorderRadius.circular(999),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          mainAxisSize: MainAxisSize.min,
          children: [
            if (leading != null) ...[leading!, const SizedBox(width: 8)],
            Text(
              label,
              style: profile.typography.body.copyWith(
                color: profile.colors.heroText,
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
        ? profile.colors.primary
        : glassy
        ? profile.colors.surface.withValues(alpha: 0.8)
        : Colors.transparent;
    final foreground = emphasized
        ? profile.colors.heroText
        : profile.colors.text;

    return JoviaPressable(
      onTap: onTap,
      borderRadius: BorderRadius.circular(999),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        decoration: BoxDecoration(
          color: background,
          borderRadius: BorderRadius.circular(999),
          border: emphasized
              ? null
              : Border.all(color: profile.colors.strokeSoft, width: 1.1),
        ),
        child: Text(
          label,
          style: profile.typography.micro.copyWith(
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
    return JoviaPressable(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 8),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (leading != null) ...[leading!, const SizedBox(width: 12)],
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if ((label ?? '').trim().isNotEmpty) ...[
                    Text(
                      label!.toUpperCase(),
                      style: profile.typography.eyebrow.copyWith(
                        color: profile.colors.textLight,
                        letterSpacing: 1.3,
                      ),
                    ),
                    const SizedBox(height: 4),
                  ],
                  Text(title, style: profile.typography.cardTitle),
                  if ((body ?? '').trim().isNotEmpty) ...[
                    const SizedBox(height: 4),
                    Text(
                      body!,
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
            if (trailing != null) ...[const SizedBox(width: 12), trailing!],
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
    return JoviaPressable(
      onTap: onTap,
      borderRadius: BorderRadius.circular(14),
      child: Container(
        width: size,
        height: size,
        decoration: BoxDecoration(
          color: profile.colors.surface.withValues(alpha: 0.78),
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: profile.colors.strokeSoft, width: 1.1),
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
        color: profile.colors.chipBg,
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
    return Container(
      padding: const EdgeInsets.all(4),
      decoration: BoxDecoration(
        color: profile.colors.chipBg.withValues(alpha: 0.88),
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: profile.colors.strokeSoft, width: 1),
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
                    horizontal: 10,
                    vertical: 10,
                  ),
                  decoration: BoxDecoration(
                    color: option == value
                        ? profile.colors.primary
                        : Colors.transparent,
                    borderRadius: BorderRadius.circular(999),
                  ),
                  child: Text(
                    labelBuilder(option),
                    textAlign: TextAlign.center,
                    style: profile.typography.micro.copyWith(
                      color: option == value
                          ? profile.colors.heroText
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
    final content = Stack(
      children: [
        if (background != null) Positioned.fill(child: background!),
        if (accent != null)
          Positioned(right: 0, top: 0, child: IgnorePointer(child: accent!)),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (glyph != null || (label ?? '').trim().isNotEmpty)
              Row(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  if (glyph != null) ...[glyph!, const SizedBox(width: 8)],
                  if ((label ?? '').trim().isNotEmpty)
                    Expanded(
                      child: Text(
                        label!.toUpperCase(),
                        style: profile.typography.eyebrow.copyWith(
                          color: profile.colors.textLight,
                          letterSpacing: 1.5,
                        ),
                      ),
                    ),
                ],
              ),
            if (glyph != null || (label ?? '').trim().isNotEmpty)
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
            if ((body ?? '').trim().isNotEmpty) ...[
              const SizedBox(height: 12),
              Text(
                body!,
                maxLines: bodyMaxLines,
                overflow: TextOverflow.ellipsis,
                style: profile.typography.bodyCompact.copyWith(
                  color: profile.colors.textLight,
                ),
              ),
            ],
            if (footer != null) ...[const SizedBox(height: 16), footer!],
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
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (showTopDivider) const ThinDivider(),
        if (showTopDivider) const SizedBox(height: 14),
        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (leading != null) ...[leading!, const SizedBox(width: 10)],
            Expanded(
              child: JoviaSectionHeader(title: title, body: body),
            ),
          ],
        ),
        const SizedBox(height: 14),
        if (primaryAction != null) ...[primaryAction!],
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
  const JoviaBottomNavItem({required this.icon, required this.label});

  final Widget icon;
  final String label;
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
    return SafeArea(
      top: false,
      child: Container(
        margin: const EdgeInsets.fromLTRB(16, 0, 16, 14),
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
        decoration: BoxDecoration(
          color: profile.colors.surface.withValues(alpha: 0.94),
          borderRadius: BorderRadius.circular(24),
          border: Border.all(color: profile.colors.strokeSoft, width: 1.1),
          boxShadow: [profile.shadows.cardShadow],
        ),
        child: Row(
          children: [
            for (var index = 0; index < items.length; index++)
              Expanded(
                child: JoviaPressable(
                  onTap: () => onTap(index),
                  borderRadius: BorderRadius.circular(18),
                  child: Container(
                    padding: const EdgeInsets.symmetric(vertical: 10),
                    decoration: BoxDecoration(
                      color: index == currentIndex
                          ? profile.colors.primary.withValues(alpha: 0.12)
                          : Colors.transparent,
                      borderRadius: BorderRadius.circular(18),
                    ),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        IconTheme(
                          data: IconThemeData(
                            color: index == currentIndex
                                ? profile.colors.primary
                                : profile.colors.textLight,
                          ),
                          child: items[index].icon,
                        ),
                        const SizedBox(height: 6),
                        Text(
                          items[index].label,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: profile.typography.micro.copyWith(
                            color: index == currentIndex
                                ? profile.colors.primary
                                : profile.colors.textLight,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
          ],
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
