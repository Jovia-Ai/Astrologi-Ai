// Buzdağının "altı" — bir kartın editöryal açılma sayfası.
//
// Tasarım kuralları (kullanıcı geri bildirimine göre):
//   • Üstte pastel hero bandı + büyük el-çizimi illüstrasyon (cute,
//     prominent — kart ile sürekliliği koruyor).
//   • Başlık Inter 24px medium — italic dominansı yok; Fraunces italic
//     sadece küçük dekoratif elementlerde sınırlı.
//   • Renkler minimal: zemin beyaz, sadece hero bandı pastel tone'da.
//   • Layer 1 etiket küçük mono caps.
//   • Layer 3 yorum: Inter body + detail_blocks paragrafları + KAYNAK chip'leri.

import 'package:flutter/material.dart';

import 'package:mobile/app/profile/layered_kart.dart';
import 'package:mobile/design/widgets/shou_topbar.dart';

class LayeredKartDetailPage extends StatelessWidget {
  const LayeredKartDetailPage({super.key, required this.card, this.username});

  final LayeredKartData card;
  final String? username;

  @override
  Widget build(BuildContext context) {
    final palette = layeredKartPalette(card.tone);
    final hasBody = (card.body ?? '').trim().isNotEmpty;
    final hasBlocks = card.detailBlocks.any((b) => b.trim().isNotEmpty);
    final hasChips = card.chips.any((c) => c.trim().isNotEmpty);
    final hasSources = card.astroSources.any((s) => s.trim().isNotEmpty);

    return Scaffold(
      backgroundColor: _D.bg,
      body: SafeArea(
        bottom: false,
        child: Column(
          children: [
            ShouTopBar(
              label: username ?? '',
              variant: ShouTopBarVariant.light,
              onBack: () => Navigator.of(context).maybePop(),
            ),
            Expanded(
              child: SingleChildScrollView(
                physics: const BouncingScrollPhysics(),
                padding: EdgeInsets.zero,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // ─── Hero band: pastel tone + illüstrasyon ──────────
                    _IllustrationHero(
                      tone: card.tone,
                      illust: card.illust,
                      bg: palette.bg,
                      illustColor: palette.illust,
                    ),
                    // ─── Content body ────────────────────────────────
                    Padding(
                      padding: const EdgeInsets.fromLTRB(24, 26, 24, 60),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          // Layer 1 — etiket / orb / kaynak
                          if (card.label.trim().isNotEmpty) ...[
                            _Eyebrow(text: card.label, accent: palette.strong),
                            const SizedBox(height: 14),
                          ],
                          // Layer 2 — çekirdek başlık (Inter, italic değil)
                          Text(
                            card.core,
                            style: const TextStyle(
                              fontFamily: 'Inter',
                              fontSize: 24,
                              fontWeight: FontWeight.w500,
                              letterSpacing: -0.5,
                              height: 1.22,
                              color: _D.ink,
                            ),
                          ),
                          const SizedBox(height: 16),
                          Container(
                            width: 28,
                            height: 1.5,
                            color: _D.ink,
                          ),
                          const SizedBox(height: 24),
                          // Layer 3 — yorum lead
                          if (hasBody) ...[
                            Text(
                              card.body!.trim(),
                              style: const TextStyle(
                                fontFamily: 'Inter',
                                fontSize: 14,
                                height: 1.62,
                                letterSpacing: -0.05,
                                color: _D.fog,
                              ),
                            ),
                            const SizedBox(height: 18),
                          ],
                          // Detail blocks
                          if (hasBlocks)
                            ...card.detailBlocks
                                .where((b) => b.trim().isNotEmpty)
                                .map(
                                  (block) => Padding(
                                    padding: const EdgeInsets.only(bottom: 16),
                                    child: Text(
                                      block.trim(),
                                      style: const TextStyle(
                                        fontFamily: 'Inter',
                                        fontSize: 13.5,
                                        height: 1.62,
                                        letterSpacing: -0.05,
                                        color: _D.fog,
                                      ),
                                    ),
                                  ),
                                ),
                          // Sources & chips
                          if (hasChips || hasSources) ...[
                            const SizedBox(height: 6),
                            Container(height: 1, color: _D.hairline),
                            const SizedBox(height: 18),
                          ],
                          if (hasSources)
                            _SourceRow(
                              label: 'KAYNAK',
                              items: card.astroSources,
                              accent: palette.strong,
                            ),
                          if (hasSources && hasChips)
                            const SizedBox(height: 14),
                          if (hasChips)
                            _SourceRow(
                              label: 'NOT',
                              items: card.chips,
                              accent: _D.mist,
                            ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Pastel zeminli hero bandı + ortalanmış illüstrasyon.
class _IllustrationHero extends StatelessWidget {
  const _IllustrationHero({
    required this.tone,
    required this.illust,
    required this.bg,
    required this.illustColor,
  });

  final LayeredKartTone tone;
  final LayeredKartIllust illust;
  final Color bg;
  final Color illustColor;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      color: bg,
      padding: const EdgeInsets.symmetric(vertical: 38),
      child: Center(
        child: LayeredKartIllustration(
          kind: illust,
          color: illustColor,
          width: 132,
          height: 98,
        ),
      ),
    );
  }
}

class _Eyebrow extends StatelessWidget {
  const _Eyebrow({required this.text, required this.accent});
  final String text;
  final Color accent;

  @override
  Widget build(BuildContext context) {
    return Text(
      text.toUpperCase(),
      style: TextStyle(
        fontFamily: 'Space Mono',
        fontSize: 9,
        letterSpacing: 1.4,
        color: accent,
        fontWeight: FontWeight.w700,
      ),
    );
  }
}

class _SourceRow extends StatelessWidget {
  const _SourceRow({
    required this.label,
    required this.items,
    required this.accent,
  });

  final String label;
  final List<String> items;
  final Color accent;

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(
          width: 56,
          child: Text(
            label,
            style: const TextStyle(
              fontFamily: 'Space Mono',
              fontSize: 8.5,
              letterSpacing: 1.2,
              color: _D.silver,
              fontWeight: FontWeight.w500,
            ),
          ),
        ),
        Expanded(
          child: Wrap(
            spacing: 6,
            runSpacing: 6,
            children: [
              for (final item in items.where((s) => s.trim().isNotEmpty))
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 9,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    border: Border.all(color: _D.hairline),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    item,
                    style: TextStyle(
                      fontFamily: 'Space Mono',
                      fontSize: 9.5,
                      letterSpacing: 0.2,
                      color: accent,
                    ),
                  ),
                ),
            ],
          ),
        ),
      ],
    );
  }
}

class _D {
  static const bg = Color(0xFFFFFFFF);
  static const ink = Color(0xFF0E0E10);
  static const fog = Color(0xFF333333);
  static const mist = Color(0xFF888888);
  static const silver = Color(0xFFB0B0B0);
  static const hairline = Color(0x14000000);
}
