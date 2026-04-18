// Explainability panel — Faz 2 PR 8b.
//
// Her arketip kartının altında, tap ile açılan inline panel. Kullanıcıya
// "neden bu öne çıktı?" sorusuna astrolojik derinlikte ama editorial tonla
// yanıt verir.
//
// Role: narrative-only surface — scoring'e dokunmaz. PR 3 (why_this_not_that),
// PR 4a (primary_threshold_flags), PR 6 (dignity_bonus), PR 7 (lunar_phase),
// PR 8a (aspect_direction_breakdown) field'larını tek yüzeyde toplar.
//
// Tone: sade, açıklayıcı, mekanik değil. Teknik field adları gösterilmez;
// sayılar nitel ifadelere dönüştürülür. Hedef his: "beni anlıyor", değil
// "algoritma böyle hesapladı".

import 'package:flutter/material.dart';
import 'package:mobile/design/theme/profile_theme_extension.dart';

/// Signature planet mapping — backend/app/astro/dignity.py'deki
/// ARCHETYPE_SIGNATURE_PLANETS ile sync. Ton notu uyarınca planet adları
/// TR karşılıklarıyla görünür.
const Map<String, List<String>> _archetypeSignaturePlanetsTr = {
  'builder': ['Satürn'],
  'visionary': ['Jüpiter'],
  'analyst': ['Merkür'],
  'connector': ['Venüs'],
  'guardian': ['Satürn', 'Ay'],
  'depthkeeper': ['Plüton', 'Mars'],
  'catalyst': ['Uranüs', 'Mars'],
};

/// Lunar phase → TR bağlam chip'i (PR 7 surface).
const Map<String, String> _lunarPhaseLabelTr = {
  'new': 'Yeni ay gecesi',
  'waxing_crescent': 'Hilâl büyürken',
  'first_quarter': 'İlk çeyrek arifesi',
  'waxing_gibbous': 'Dolunaya yaklaşırken',
  'full': 'Dolunay altında',
  'waning_gibbous': 'Dolunaydan sonra',
  'last_quarter': 'Son çeyrek döneminde',
  'balsamic': 'Balsamic an',
};

/// Kamuya açık phrase helper'ları — widget test'lerden doğrulanır.

/// score_meets_primary_threshold × dignity_bonus → güç nitelemesi.
/// Dignity nötr bölgesinde (|bonus|<0.05) sadece threshold bilgisi kullanılır.
String strengthLabel({
  required bool meetsThreshold,
  required double dignityBonus,
}) {
  final positiveDignity = dignityBonus >= 0.05;
  final negativeDignity = dignityBonus <= -0.05;
  if (meetsThreshold && positiveDignity) return 'güçlü oturmuş';
  if (meetsThreshold && negativeDignity) return 'net ama gerilimde';
  if (meetsThreshold) return 'net ayrışıyor';
  if (negativeDignity) return 'arka planda';
  return 'hafif';
}

/// Signature planetlerin dignity bonus değerine göre nitel chip.
/// null döndüğü durumda chip gösterilmez (peregrine zone).
String? dignityChip({
  required String archetypeId,
  required double dignityBonus,
}) {
  final planets = _archetypeSignaturePlanetsTr[archetypeId.trim().toLowerCase()];
  if (planets == null || planets.isEmpty) return null;
  final joined = planets.join(', ');
  if (dignityBonus >= 0.12) return '$joined güçlü destekli';
  if (dignityBonus >= 0.05) return '$joined destekli';
  if (dignityBonus <= -0.12) return '$joined yabancı alanda';
  if (dignityBonus <= -0.05) return '$joined hafif gerilimde';
  return null;
}

/// aspect_direction_breakdown → chip listesi. Count>0 olan bucket'lar için
/// tek chip, `unknown` bucket'ı kullanıcıya gösterilmez (internal).
List<String> tensionChips(Map<String, dynamic>? breakdown) {
  if (breakdown == null) return const [];
  final applying = (breakdown['applying'] as num?)?.toInt() ?? 0;
  final separating = (breakdown['separating'] as num?)?.toInt() ?? 0;
  final exact = (breakdown['exact'] as num?)?.toInt() ?? 0;
  final chips = <String>[];
  if (exact > 0) chips.add('$exact tam aspect');
  if (applying > 0) chips.add('$applying yaklaşan gerilim');
  if (separating > 0) chips.add('$separating işlenmiş hareket');
  return chips;
}

/// Lunar phase → bağlam chip'i.
String? lunarPhaseChip(String? lunarPhase) {
  if (lunarPhase == null) return null;
  return _lunarPhaseLabelTr[lunarPhase];
}

/// Panel'in dört block'undan herhangi birinde gösterilecek içerik var mı?
/// Tek bir kez kontrol etmek için top-level helper.
bool hasExplainableContent({
  required Map<String, dynamic> item,
  String? lunarPhase,
}) {
  final why = (item['why_this_not_that'] as String?)?.trim() ?? '';
  if (why.isNotEmpty) return true;
  if (lunarPhaseChip(lunarPhase) != null) return true;
  final breakdown = item['aspect_direction_breakdown'] as Map<String, dynamic>?;
  if (tensionChips(breakdown).isNotEmpty) return true;
  final dignity = _readDignityBonus(item);
  final dignityLabel = dignityChip(
    archetypeId: (item['id'] as String?) ?? '',
    dignityBonus: dignity,
  );
  if (dignityLabel != null) return true;
  if (item['score_meets_primary_threshold'] == true) return true;
  return false;
}

double _readDignityBonus(Map<String, dynamic> item) {
  final components = item['components'];
  if (components is Map) {
    final raw = components['dignity_bonus'];
    if (raw is num) return raw.toDouble();
  }
  // `components` sometimes not threaded up to top_archetypes — check
  // chart_prior by_id fallback if passed directly.
  return 0.0;
}

/// Inline expand/collapse panel — arketip kartının altında yer alır.
class ExplainabilityPanel extends StatefulWidget {
  const ExplainabilityPanel({
    required this.item,
    required this.accent,
    this.lunarPhase,
    this.dignityBonus = 0.0,
    super.key,
  });

  /// Arketip item dict'i — backend top_archetypes'dan bir eleman.
  final Map<String, dynamic> item;

  /// Block 4 için top-level `lunar_phase` değeri.
  final String? lunarPhase;

  /// Block 2 dignity chip'i için `components.dignity_bonus` değeri.
  /// Backend item'da components bazı path'lerde flatten edilmediği için
  /// çağıran widget explicit geçirir (test'te de override edilebilir).
  final double dignityBonus;

  /// Panel accent rengi — arketip kartıyla eşleşir.
  final Color accent;

  @override
  State<ExplainabilityPanel> createState() => _ExplainabilityPanelState();
}

class _ExplainabilityPanelState extends State<ExplainabilityPanel> {
  bool _expanded = false;

  bool get _hasContent => hasExplainableContent(
    item: widget.item,
    lunarPhase: widget.lunarPhase,
  );

  @override
  Widget build(BuildContext context) {
    if (!_hasContent) return const SizedBox.shrink();
    final profile = context.profileTheme;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const SizedBox(height: 14),
        _ToggleRow(
          expanded: _expanded,
          accent: widget.accent,
          onTap: () => setState(() => _expanded = !_expanded),
        ),
        AnimatedSize(
          duration: const Duration(milliseconds: 240),
          curve: Curves.easeInOutCubic,
          alignment: Alignment.topCenter,
          child: _expanded
              ? Padding(
                  padding: const EdgeInsets.only(top: 14),
                  child: _ExpandedContent(
                    item: widget.item,
                    lunarPhase: widget.lunarPhase,
                    dignityBonus: widget.dignityBonus,
                    accent: widget.accent,
                    profile: profile,
                  ),
                )
              : const SizedBox.shrink(),
        ),
      ],
    );
  }
}

class _ToggleRow extends StatelessWidget {
  const _ToggleRow({
    required this.expanded,
    required this.accent,
    required this.onTap,
  });

  final bool expanded;
  final Color accent;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Semantics(
      button: true,
      toggled: expanded,
      label: expanded
          ? 'Açıklamayı kapat'
          : 'Neden bu öne çıktı, aç',
      child: InkWell(
        borderRadius: BorderRadius.circular(8),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 6),
          child: Row(
            children: [
              Text(
                'Neden bu öne çıktı?',
                style: profile.typography.metaSoft.copyWith(
                  color: accent,
                  fontSize: 12.4,
                  fontWeight: FontWeight.w700,
                  letterSpacing: 0.2,
                ),
              ),
              const SizedBox(width: 6),
              AnimatedRotation(
                duration: const Duration(milliseconds: 200),
                curve: Curves.easeOutCubic,
                turns: expanded ? 0.5 : 0.0,
                child: Icon(
                  Icons.keyboard_arrow_down_rounded,
                  size: 18,
                  color: accent,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _ExpandedContent extends StatelessWidget {
  const _ExpandedContent({
    required this.item,
    required this.lunarPhase,
    required this.dignityBonus,
    required this.accent,
    required this.profile,
  });

  final Map<String, dynamic> item;
  final String? lunarPhase;
  final double dignityBonus;
  final Color accent;
  final ProfileTheme profile;

  @override
  Widget build(BuildContext context) {
    final why = (item['why_this_not_that'] as String?)?.trim() ?? '';
    final meetsThreshold = item['score_meets_primary_threshold'] == true;
    final strength = strengthLabel(
      meetsThreshold: meetsThreshold,
      dignityBonus: dignityBonus,
    );
    final dignityLabel = dignityChip(
      archetypeId: (item['id'] as String?) ?? '',
      dignityBonus: dignityBonus,
    );
    final breakdown = item['aspect_direction_breakdown'] as Map<String, dynamic>?;
    final tensions = tensionChips(breakdown);
    final contextChip = lunarPhaseChip(lunarPhase);

    final blocks = <Widget>[];

    // Block 1 — Neden bu, başka değil
    if (why.isNotEmpty) {
      blocks.add(_NarrativeBlock(text: why, profile: profile));
    } else {
      blocks.add(
        _NarrativeBlock(text: 'Bu profil sende ayrışıyor.', profile: profile),
      );
    }

    // Block 2 — Güç derecesi
    final strengthChips = <String>[strength];
    if (dignityLabel != null) strengthChips.add(dignityLabel);
    blocks.add(_ChipBlock(chips: strengthChips, accent: accent, profile: profile));

    // Block 3 — Gerilim ritmi
    if (tensions.isNotEmpty) {
      blocks.add(
        _ChipBlock(
          chips: tensions,
          accent: profile.colors.warmAccent,
          profile: profile,
        ),
      );
    }

    // Block 4 — Bağlam
    if (contextChip != null) {
      blocks.add(
        _ChipBlock(
          chips: [contextChip],
          accent: profile.colors.lime,
          profile: profile,
        ),
      );
    }

    return Container(
      padding: const EdgeInsets.fromLTRB(14, 14, 14, 16),
      decoration: BoxDecoration(
        color: profile.colors.bg.withValues(alpha: 0.55),
        borderRadius: BorderRadius.circular(18),
        border: Border.all(
          color: accent.withValues(alpha: 0.18),
          width: 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          for (var i = 0; i < blocks.length; i++) ...[
            if (i != 0) const SizedBox(height: 10),
            blocks[i],
          ],
        ],
      ),
    );
  }
}

class _NarrativeBlock extends StatelessWidget {
  const _NarrativeBlock({required this.text, required this.profile});

  final String text;
  final ProfileTheme profile;

  @override
  Widget build(BuildContext context) {
    return Text(
      text,
      style: profile.typography.bodyCompact.copyWith(
        color: profile.colors.text,
        height: 1.45,
        fontSize: 13.4,
      ),
    );
  }
}

class _ChipBlock extends StatelessWidget {
  const _ChipBlock({
    required this.chips,
    required this.accent,
    required this.profile,
  });

  final List<String> chips;
  final Color accent;
  final ProfileTheme profile;

  @override
  Widget build(BuildContext context) {
    return Wrap(
      spacing: 6,
      runSpacing: 6,
      children: [
        for (final label in chips) _Chip(label: label, accent: accent, profile: profile),
      ],
    );
  }
}

class _Chip extends StatelessWidget {
  const _Chip({
    required this.label,
    required this.accent,
    required this.profile,
  });

  final String label;
  final Color accent;
  final ProfileTheme profile;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(
        color: accent.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: accent.withValues(alpha: 0.28), width: 1),
      ),
      child: Text(
        label,
        style: profile.typography.metaSoft.copyWith(
          color: profile.colors.text,
          fontSize: 11.8,
          fontWeight: FontWeight.w600,
          letterSpacing: 0.1,
        ),
      ),
    );
  }
}
