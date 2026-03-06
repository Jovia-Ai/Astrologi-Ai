import 'dart:ui';

import 'package:flutter/material.dart';
import 'package:mobile/design/theme/profile_theme_extension.dart';

class ProfileStylePreviewScreen extends StatelessWidget {
  const ProfileStylePreviewScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final themed = withProfileTheme(Theme.of(context));
    return Theme(data: themed, child: const _ProfileStylePreviewBody());
  }
}

class _ProfileStylePreviewBody extends StatelessWidget {
  const _ProfileStylePreviewBody();

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final c = profile.colors;
    final s = profile.spacing;
    final t = profile.typography;

    return Scaffold(
      backgroundColor: c.bg,
      body: SafeArea(
        child: ListView(
          padding: EdgeInsets.fromLTRB(s.lg, s.lg, s.lg, s.xxl),
          children: [
            _AnimatedAuraHeader(
              height: 280,
              child: Padding(
                padding: EdgeInsets.all(s.xl),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _AvatarHalo(size: 86),
                    SizedBox(height: s.lg),
                    Text('Sahra Deniz', style: t.h1),
                    SizedBox(height: s.sm),
                    Wrap(
                      spacing: s.xs,
                      runSpacing: s.xs,
                      children: const [
                        _MetaPill(text: 'Güneş: Oğlak'),
                        _MetaPill(text: 'Ay: Aslan'),
                        _MetaPill(text: 'Yükselen: Oğlak'),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            SizedBox(height: s.xl),
            _GlassCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Core Story', style: t.h2),
                  SizedBox(height: s.sm),
                  Text(
                    'Bu dönem profil hattında kimlik ve ifade dili birlikte parlıyor. Dış görünürlük artarken iç ritim sadeleşiyor.',
                    style: t.body,
                  ),
                ],
              ),
            ),
            SizedBox(height: s.lg),
            Text('Domain Chips', style: t.micro),
            SizedBox(height: s.sm),
            Wrap(
              spacing: s.sm,
              runSpacing: s.sm,
              children: const [
                _DomainChip(label: 'Kimlik'),
                _DomainChip(label: 'İlişki'),
                _DomainChip(label: 'Kariyer'),
              ],
            ),
            SizedBox(height: s.xl),
            _UpperMeaningPanel(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Upper Meaning', style: t.h2),
                  SizedBox(height: s.sm),
                  Text(
                    'Yumuşak ama net bir sınır çizgisi, bu dönemin kazanç kapısını açar. Tek bir hedefe odaklandığında ivme kalıcı olur.',
                    style: t.body,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _AnimatedAuraHeader extends StatefulWidget {
  const _AnimatedAuraHeader({required this.height, required this.child});

  final double height;
  final Widget child;

  @override
  State<_AnimatedAuraHeader> createState() => _AnimatedAuraHeaderState();
}

class _AnimatedAuraHeaderState extends State<_AnimatedAuraHeader>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller = AnimationController(
    vsync: this,
    duration: const Duration(seconds: 14),
  )..repeat(reverse: true);

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final c = profile.colors;
    final r = profile.radii;

    return ClipRRect(
      borderRadius: BorderRadius.circular(r.cardRadius + 4),
      child: SizedBox(
        height: widget.height,
        child: Stack(
          fit: StackFit.expand,
          children: [
            AnimatedBuilder(
              animation: _controller,
              builder: (context, _) {
                final scale = 1 + (_controller.value * 0.08);
                final alignX = -0.12 + (_controller.value * 0.24);
                return Transform.scale(
                  scale: scale,
                  child: DecoratedBox(
                    decoration: BoxDecoration(
                      gradient: RadialGradient(
                        center: Alignment(alignX, -0.1),
                        radius: 1.05,
                        colors: [
                          c.auraStops[0].withValues(alpha: 0.82),
                          c.auraStops[1].withValues(alpha: 0.65),
                          c.auraStops[2].withValues(alpha: 0.52),
                          c.warmAccent.withValues(alpha: 0.22),
                        ],
                        stops: const [0.0, 0.42, 0.78, 1.0],
                      ),
                    ),
                  ),
                );
              },
            ),
            DecoratedBox(
              decoration: BoxDecoration(
                color: c.surface.withValues(alpha: 0.18),
                border: Border.all(color: c.border),
                borderRadius: BorderRadius.circular(r.cardRadius + 4),
              ),
            ),
            widget.child,
          ],
        ),
      ),
    );
  }
}

class _AvatarHalo extends StatelessWidget {
  const _AvatarHalo({required this.size});

  final double size;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final c = profile.colors;
    return SizedBox(
      width: size,
      height: size,
      child: Stack(
        alignment: Alignment.center,
        children: [
          Container(
            width: size,
            height: size,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: c.auraStops[1].withValues(alpha: 0.28),
              boxShadow: [profile.shadows.floatingShadow],
            ),
          ),
          Container(
            width: size * 0.76,
            height: size * 0.76,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: c.surface.withValues(alpha: 0.92),
              border: Border.all(color: c.border),
            ),
            alignment: Alignment.center,
            child: Icon(
              Icons.person_rounded,
              size: size * 0.36,
              color: c.text.withValues(alpha: 0.78),
            ),
          ),
        ],
      ),
    );
  }
}

class _MetaPill extends StatelessWidget {
  const _MetaPill({required this.text});

  final String text;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Container(
      padding: EdgeInsets.symmetric(
        horizontal: profile.spacing.sm,
        vertical: profile.spacing.xs,
      ),
      decoration: BoxDecoration(
        color: profile.colors.chipBg,
        border: Border.all(color: profile.colors.chipBorder),
        borderRadius: BorderRadius.circular(profile.radii.pillRadius),
      ),
      child: Text(
        text,
        style: profile.typography.micro.copyWith(
          color: profile.colors.text.withValues(alpha: 0.9),
        ),
      ),
    );
  }
}

class _DomainChip extends StatelessWidget {
  const _DomainChip({required this.label});

  final String label;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Container(
      padding: EdgeInsets.symmetric(
        horizontal: profile.spacing.md,
        vertical: profile.spacing.xs,
      ),
      decoration: BoxDecoration(
        color: profile.colors.chipBg,
        border: Border.all(color: profile.colors.chipBorder),
        borderRadius: BorderRadius.circular(profile.radii.pillRadius),
      ),
      child: Text(
        label,
        style: profile.typography.micro.copyWith(color: profile.colors.text),
      ),
    );
  }
}

class _GlassCard extends StatelessWidget {
  const _GlassCard({required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return ClipRRect(
      borderRadius: BorderRadius.circular(profile.radii.cardRadius),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 12, sigmaY: 12),
        child: Container(
          padding: EdgeInsets.all(profile.spacing.lg),
          decoration: BoxDecoration(
            color: profile.colors.surface,
            border: Border.all(color: profile.colors.border),
            borderRadius: BorderRadius.circular(profile.radii.cardRadius),
            boxShadow: [profile.shadows.cardShadow],
          ),
          child: child,
        ),
      ),
    );
  }
}

class _UpperMeaningPanel extends StatelessWidget {
  const _UpperMeaningPanel({required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final c = profile.colors;
    return Container(
      padding: EdgeInsets.all(profile.spacing.lg),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(profile.radii.cardRadius),
        border: Border.all(color: c.border),
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            c.auraStops[2].withValues(alpha: 0.20),
            c.auraStops[1].withValues(alpha: 0.12),
            c.surface.withValues(alpha: 0.94),
          ],
        ),
        boxShadow: [profile.shadows.cardShadow],
      ),
      child: child,
    );
  }
}
