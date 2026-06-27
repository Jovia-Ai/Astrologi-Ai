// FREE-PROFILE-R4B — internal narrow Free editorial Profile surface.
//
// Renders the five fixed domains in order; per domain at most two cards (sign
// first, house second). It does NOT
// route through the legacy poster selection system, shows no origin/defense/
// proof/aura badge ("Koruyucu dalga")/aspect labels/dominant chips, and the
// detail view renders structured role blocks in order (no _splitBodyIntoSlides,
// no carousel/page counters, role names hidden from the user).

import 'package:flutter/material.dart';

import 'free_editorial_profile_adapter.dart';

// Pre-uppercased Turkish eyebrows (Dart's locale-independent toUpperCase would
// turn "Kimlik" into "KIMLIK" with a dotless I, so use correct constants).
const Map<String, String> _kDomainEyebrowTr = <String, String>{
  'identity': 'KİMLİK',
  'emotion': 'DUYGU',
  'mind': 'ZİHİN',
  'relationship': 'İLİŞKİ',
  'action': 'HAREKET',
};

class FreeEditorialProfileView extends StatelessWidget {
  const FreeEditorialProfileView({super.key, required this.profile});

  final FreeEditorialProfileModel profile;

  @override
  Widget build(BuildContext context) {
    if (!profile.isValid) {
      assert(() {
        debugPrint(
          'FREE_EDITORIAL_VIEW parsed_card_count=0 identity_count=0 '
          'emotion_count=0 mind_count=0 relationship_count=0 action_count=0 '
          'rendered_section_count=0',
        );
        return true;
      }());
      return const _FreeEditorialEmptyState();
    }
    final domains = <Widget>[];
    final domainCounts = <String, int>{};
    for (final domain in kFreeEditorialDomainOrder) {
      final cards = profile.cardsForDomain(domain);
      domainCounts[domain] = cards.length;
      if (cards.isEmpty) continue;
      domains.add(
        _DomainSection(
          key: Key('free_editorial_domain_$domain'),
          domainTitle: _kDomainEyebrowTr[domain] ?? domain,
          cards: cards,
        ),
      );
    }
    assert(() {
      debugPrint(
        'FREE_EDITORIAL_VIEW parsed_card_count=${profile.cards.length} '
        'identity_count=${domainCounts['identity'] ?? 0} '
        'emotion_count=${domainCounts['emotion'] ?? 0} '
        'mind_count=${domainCounts['mind'] ?? 0} '
        'relationship_count=${domainCounts['relationship'] ?? 0} '
        'action_count=${domainCounts['action'] ?? 0} '
        'rendered_section_count=${domains.length}',
      );
      return true;
    }());
    return ListView(
      key: const Key('free_editorial_profile_root'),
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 32),
      primary: false,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      children: domains,
    );
  }
}

class _FreeEditorialEmptyState extends StatelessWidget {
  const _FreeEditorialEmptyState();

  @override
  Widget build(BuildContext context) {
    return const Center(
      key: Key('free_editorial_empty_state'),
      child: Padding(
        padding: EdgeInsets.all(24),
        child: Text('Profil hazırlanıyor.'),
      ),
    );
  }
}

class _DomainSection extends StatelessWidget {
  const _DomainSection({
    super.key,
    required this.domainTitle,
    required this.cards,
  });

  final String domainTitle;
  final List<FreeEditorialCardModel> cards;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: <Widget>[
        Padding(
          padding: const EdgeInsets.only(top: 8, bottom: 8),
          child: Text(
            domainTitle,
            style: const TextStyle(
              fontSize: 12,
              letterSpacing: 1.4,
              fontWeight: FontWeight.w700,
              color: Color(0xFF888888),
            ),
          ),
        ),
        for (final card in cards)
          Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: FreeEditorialCardTile(
              key: Key('free_editorial_card_${card.primaryKey}'),
              card: card,
            ),
          ),
        const SizedBox(height: 8),
      ],
    );
  }
}

class FreeEditorialCardTile extends StatelessWidget {
  const FreeEditorialCardTile({super.key, required this.card});

  final FreeEditorialCardModel card;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFFFFFFFF),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0x14000000)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Text(
            card.title,
            style: const TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.w600,
              height: 1.15,
              color: Color(0xFF0E0E10),
            ),
          ),
          if (card.summary.trim().isNotEmpty) ...<Widget>[
            const SizedBox(height: 8),
            Text(
              card.summary,
              style: const TextStyle(
                fontSize: 14,
                height: 1.5,
                color: Color(0xFF333333),
              ),
            ),
          ],
          if (card.chips.isNotEmpty) ...<Widget>[
            const SizedBox(height: 12),
            Wrap(
              spacing: 6,
              runSpacing: 6,
              children: <Widget>[
                for (final chip in card.chips)
                  _PlacementChip(label: chip.label),
              ],
            ),
          ],
          const SizedBox(height: 12),
          Align(
            alignment: Alignment.centerLeft,
            child: TextButton(
              key: Key('free-editorial-cta-${card.primaryKey}'),
              onPressed: () => Navigator.of(context).push(
                MaterialPageRoute<void>(
                  builder: (_) => FreeEditorialDetailPage(card: card),
                ),
              ),
              child: const Text('Detayı aç'),
            ),
          ),
        ],
      ),
    );
  }
}

class _PlacementChip extends StatelessWidget {
  const _PlacementChip({required this.label});
  final String label;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 4),
      decoration: BoxDecoration(
        border: Border.all(color: const Color(0x14000000)),
        borderRadius: BorderRadius.circular(999),
      ),
      child: Text(
        label,
        style: const TextStyle(fontSize: 12, color: Color(0xFF534AB7)),
      ),
    );
  }
}

/// Structured non-paged detail. Renders role blocks in fixed order, non-empty
/// only, without exposing role names. No slide splitting, no page counters.
class FreeEditorialDetailPage extends StatelessWidget {
  const FreeEditorialDetailPage({super.key, required this.card});

  final FreeEditorialCardModel card;

  @override
  Widget build(BuildContext context) {
    final blocks = card.orderedBlocks();
    return Scaffold(
      backgroundColor: const Color(0xFFFFFFFF),
      appBar: AppBar(
        backgroundColor: const Color(0xFFFFFFFF),
        elevation: 0,
        foregroundColor: const Color(0xFF0E0E10),
      ),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.fromLTRB(20, 8, 20, 40),
          children: <Widget>[
            Text(
              card.title,
              style: const TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.w600,
                height: 1.15,
                color: Color(0xFF0E0E10),
              ),
            ),
            if (card.summary.trim().isNotEmpty) ...<Widget>[
              const SizedBox(height: 12),
              Text(
                card.summary,
                style: const TextStyle(
                  fontSize: 15,
                  height: 1.55,
                  color: Color(0xFF333333),
                ),
              ),
            ],
            const SizedBox(height: 8),
            for (final block in blocks)
              Padding(
                key: Key('free-editorial-block-${block.role}'),
                padding: const EdgeInsets.only(top: 16),
                child: Text(
                  block.text,
                  style: const TextStyle(
                    fontSize: 15,
                    height: 1.6,
                    color: Color(0xFF222222),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
