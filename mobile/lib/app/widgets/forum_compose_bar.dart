import 'package:flutter/material.dart';

import 'package:mobile/design/theme/profile_theme_extension.dart';
import 'package:mobile/design/widgets/jovia_editorial.dart';

class ForumComposeBar extends StatelessWidget {
  const ForumComposeBar({super.key, required this.label, required this.onTap});

  final String label;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return SafeArea(
      top: false,
      child: Padding(
        padding: const EdgeInsets.fromLTRB(16, 8, 16, 14),
        child: JoviaPressable(
          onTap: onTap,
          borderRadius: BorderRadius.circular(28),
          child: JoviaSurfaceCard(
            radius: 28,
            padding: const EdgeInsets.fromLTRB(16, 14, 16, 14),
            child: Row(
              children: [
                Container(
                  width: 42,
                  height: 42,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    gradient: LinearGradient(
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                      colors: [
                        Color.alphaBlend(
                          Colors.white.withValues(
                            alpha:
                                Theme.of(context).brightness == Brightness.dark
                                ? 0.12
                                : 0.6,
                          ),
                          profile.colors.warmAccent.withValues(alpha: 0.26),
                        ),
                        Color.alphaBlend(
                          profile.colors.primary.withValues(alpha: 0.2),
                          profile.colors.heroBase,
                        ),
                      ],
                    ),
                    border: Border.all(color: profile.colors.strokeSoft),
                  ),
                  child: const Center(
                    child: JoviaUiIcon(asset: JoviaUiAsset.chatOrbit, size: 19),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'FORUM',
                        style: profile.typography.monoEyebrow.copyWith(
                          color: profile.colors.textLight,
                          fontSize: 10.8,
                          letterSpacing: 1.6,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        label,
                        style: profile.typography.bodyCompact.copyWith(
                          color: profile.colors.textLight,
                          fontSize: 13.3,
                        ),
                      ),
                    ],
                  ),
                ),
                Container(
                  width: 38,
                  height: 38,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: profile.colors.buttonSecondary.withValues(
                      alpha: 0.88,
                    ),
                    border: Border.all(color: profile.colors.strokeSoft),
                  ),
                  child: Icon(
                    Icons.arrow_upward_rounded,
                    size: 18,
                    color: profile.colors.text,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
