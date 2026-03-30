import 'package:flutter/material.dart';

import 'package:mobile/app/tabs/forum_page.dart';
import 'package:mobile/design/theme/profile_theme_extension.dart';
import 'package:mobile/design/widgets/jovia_editorial.dart';

class ForumCTA extends StatelessWidget {
  const ForumCTA({super.key});

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 14),
      child: DecoratedBox(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(28),
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Color.alphaBlend(
                profile.colors.lavender.withValues(alpha: 0.12),
                profile.colors.panelStrong,
              ),
              profile.colors.panelSoft,
            ],
          ),
          border: Border.all(color: profile.colors.strokeSoft, width: 1.05),
        ),
        child: JoviaPressable(
          borderRadius: BorderRadius.circular(28),
          onTap: () {
            Navigator.of(
              context,
            ).push(MaterialPageRoute<void>(builder: (_) => const ForumPage()));
          },
          child: JoviaSurfaceCard(
            radius: 28,
            color: Colors.transparent,
            padding: const EdgeInsets.fromLTRB(18, 18, 18, 16),
            child: Stack(
              children: [
                Positioned(
                  right: -16,
                  top: -18,
                  child: IgnorePointer(
                    child: Container(
                      width: 112,
                      height: 112,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: profile.colors.lavender.withValues(alpha: 0.08),
                      ),
                    ),
                  ),
                ),
                Positioned(
                  right: 30,
                  bottom: 10,
                  child: IgnorePointer(
                    child: Container(
                      width: 70,
                      height: 70,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: profile.colors.warmAccent.withValues(
                          alpha: 0.05,
                        ),
                      ),
                    ),
                  ),
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'FORUM',
                      style: profile.typography.monoEyebrow.copyWith(
                        color: profile.colors.textLight,
                        fontSize: 11,
                        letterSpacing: 1.7,
                      ),
                    ),
                    const SizedBox(height: 10),
                    ConstrainedBox(
                      constraints: const BoxConstraints(maxWidth: 280),
                      child: Text(
                        'Toplulugun nabzina gir',
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                        style: profile.typography.section.copyWith(
                          color: profile.colors.text,
                          fontSize: 23,
                          height: 1.1,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                    const SizedBox(height: 8),
                    ConstrainedBox(
                      constraints: const BoxConstraints(maxWidth: 310),
                      child: Text(
                        'Transit, iliski ve gundem yorumlarini daha temiz ve toplu bir akista gor.',
                        maxLines: 3,
                        overflow: TextOverflow.ellipsis,
                        style: profile.typography.bodyCompact.copyWith(
                          color: profile.colors.textLight,
                          fontSize: 13.8,
                          height: 1.46,
                        ),
                      ),
                    ),
                    const SizedBox(height: 18),
                    Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 10,
                            vertical: 6,
                          ),
                          decoration: BoxDecoration(
                            borderRadius: BorderRadius.circular(999),
                            color: profile.colors.buttonSecondary.withValues(
                              alpha: 0.84,
                            ),
                            border: Border.all(
                              color: profile.colors.strokeSoft,
                              width: 1,
                            ),
                          ),
                          child: Text(
                            'Yeni basliklar',
                            style: profile.typography.metaSoft.copyWith(
                              color: profile.colors.textLight,
                            ),
                          ),
                        ),
                        const Spacer(),
                        _ForumCardAction(label: 'Foruma gir'),
                      ],
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _ForumCardAction extends StatelessWidget {
  const _ForumCardAction({required this.label});

  final String label;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(999),
        color: profile.colors.buttonSecondary.withValues(alpha: 0.92),
        border: Border.all(color: profile.colors.strokeSoft, width: 1),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            label,
            style: profile.typography.buttonLabel.copyWith(
              color: profile.colors.text,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(width: 8),
          Icon(
            Icons.arrow_outward_rounded,
            size: 15,
            color: profile.colors.text,
          ),
        ],
      ),
    );
  }
}
