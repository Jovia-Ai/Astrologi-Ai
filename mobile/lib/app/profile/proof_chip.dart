// Proof chip — voice spec v2.1 §11.4–11.9.
//
// Thread-level raw proof satırı: "Satürn · 3. ev · Oğlak" formatında
// astrolojik künye. Profile detail flow'da paragraph'ın altında, sessiz bir
// "imza" olarak görünür.
//
// Tone (v2.1 §11.5–11.6):
//   - Title Case korunur — metin backend'den geldiği gibi render edilir.
//   - Alpha ≥ 0.60, font ≥ 11px (WCAG AA minimum, voice spec §11.6).
//   - Sol border lime accent — marka teması, bastırılmış sinyal.
//
// Render koşulları (v2.1 §11.8, §11.9):
//   - Sadece TR locale'de görünür — EN havuzu hazır değil.
//   - proof_raw.isEmpty → SizedBox.shrink.
//   - Widget kendisi fallback-safe; parent null/empty geçirse de çökmez.

import 'package:flutter/material.dart';
import 'package:mobile/design/theme/profile_theme_extension.dart';

/// Thread-level raw proof chip — astrological credit line.
///
/// Paragraph'ın altına yerleşir; sessiz, ikincil bir kanıt satırıdır.
/// Kullanıcı okumak zorunda değil — görmek yeterli.
class ProfileProofChip extends StatelessWidget {
  const ProfileProofChip({
    required this.proofRaw,
    this.topSpacing = 14,
    super.key,
  });

  /// Rendered raw proof string from backend.
  /// Title Case, middle-dot ayraç: "Satürn · 3. ev · Oğlak".
  final String proofRaw;

  /// Paragraph ile chip arasındaki dikey boşluk (default 14).
  final double topSpacing;

  @override
  Widget build(BuildContext context) {
    // Voice spec §11.9 — empty string → render yok (invariant).
    if (proofRaw.isEmpty) return const SizedBox.shrink();

    // Voice spec §11.8 — locale-gated render. İlk sürüm TR-only.
    final locale = Localizations.localeOf(context);
    if (locale.languageCode != 'tr') return const SizedBox.shrink();

    final profile = context.profileTheme;
    return Padding(
      padding: EdgeInsets.only(top: topSpacing),
      child: Container(
        padding: const EdgeInsets.fromLTRB(10, 4, 10, 4),
        decoration: BoxDecoration(
          border: Border(
            left: BorderSide(
              color: profile.colors.lime.withValues(alpha: 0.55),
              width: 2,
            ),
          ),
        ),
        child: Text(
          proofRaw,
          style: profile.typography.metaSoft.copyWith(
            // Voice spec §11.6 — alpha ≥ 0.60 invariant (WCAG AA).
            color: profile.colors.text.withValues(alpha: 0.60),
            fontSize: 11,
            fontWeight: FontWeight.w500,
            letterSpacing: 0.3,
            height: 1.35,
          ),
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
      ),
    );
  }
}
