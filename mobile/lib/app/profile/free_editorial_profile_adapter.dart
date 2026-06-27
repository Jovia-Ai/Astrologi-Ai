// FREE-PROFILE-R4B — dedicated narrow Free editorial profile adapter.
//
// Parses ONLY the additive `editorial_profile` payload field. It never searches
// profile_v8, sections_v2, supporting threads or mock cards for missing data,
// never merges chips across cards, and never synthesizes a title. Host selection
// is driven only by whether this payload contains valid cards.

import 'package:flutter/foundation.dart';

/// Fixed Free V1 domain order.
const List<String> kFreeEditorialDomainOrder = <String>[
  'identity',
  'emotion',
  'mind',
  'relationship',
  'action',
];

/// Public block roles, in display order. Role names are NOT shown to the user.
const List<String> kFreeEditorialBlockOrder = <String>[
  'recognition',
  'mechanism',
  'tension',
  'capacity',
];

class FreeEditorialChip {
  const FreeEditorialChip({required this.label, required this.source});
  final String label;
  final String source;
}

class FreeEditorialBlock {
  const FreeEditorialBlock({
    required this.role,
    required this.text,
    required this.sourceField,
  });
  final String role;
  final String text;
  final String sourceField;
}

class FreeEditorialCardModel {
  const FreeEditorialCardModel({
    required this.cardId,
    required this.ordinal,
    required this.domain,
    required this.planet,
    required this.placementType,
    required this.primaryKey,
    required this.assetId,
    required this.title,
    required this.summary,
    required this.blocks,
    required this.chips,
    required this.meaningOwner,
    required this.expressionOwner,
    required this.ownershipStatus,
  });

  final String cardId;
  final int ordinal;
  final String domain;
  final String planet;
  final String placementType; // planet_sign | planet_house
  final String primaryKey;
  final String assetId;
  final String title;
  final String summary;
  final List<FreeEditorialBlock> blocks;
  final List<FreeEditorialChip> chips;
  final String meaningOwner;
  final String expressionOwner;
  final String ownershipStatus;

  bool get isSign => placementType == 'planet_sign';

  /// Blocks in fixed role order, non-empty only. No role label is exposed.
  List<FreeEditorialBlock> orderedBlocks() {
    final byRole = <String, FreeEditorialBlock>{
      for (final b in blocks)
        if (b.text.trim().isNotEmpty) b.role: b,
    };
    return <FreeEditorialBlock>[
      for (final role in kFreeEditorialBlockOrder)
        if (byRole.containsKey(role)) byRole[role]!,
    ];
  }
}

class FreeEditorialOmission {
  const FreeEditorialOmission({required this.primaryKey, required this.reason});
  final String primaryKey;
  final String reason;
}

class FreeEditorialProfileModel {
  const FreeEditorialProfileModel({
    required this.version,
    required this.locale,
    required this.cards,
    required this.missingKeys,
    required this.isValid,
  });

  final String version;
  final String locale;
  final List<FreeEditorialCardModel> cards;
  final List<FreeEditorialOmission> missingKeys;
  final bool isValid;

  static const FreeEditorialProfileModel empty = FreeEditorialProfileModel(
    version: '',
    locale: '',
    cards: <FreeEditorialCardModel>[],
    missingKeys: <FreeEditorialOmission>[],
    isValid: false,
  );

  /// Cards for a domain, backend order preserved, maximum two (sign then house).
  /// No cross-domain reuse, no fallback card.
  List<FreeEditorialCardModel> cardsForDomain(String domain) {
    final list = cards.where((c) => c.domain == domain).toList()
      ..sort((a, b) => a.ordinal.compareTo(b.ordinal));
    return list.length > 2 ? list.sublist(0, 2) : list;
  }
}

class FreeEditorialParseResult {
  const FreeEditorialParseResult({
    required this.model,
    required this.rawCardCount,
    required this.parsedCardCount,
    required this.invalidCardCount,
    required this.invalidReasons,
  });

  final FreeEditorialProfileModel model;
  final int rawCardCount;
  final int parsedCardCount;
  final int invalidCardCount;
  final List<String> invalidReasons;

  String get diagnosticLine =>
      'FREE_EDITORIAL_ADAPTER raw_card_count=$rawCardCount '
      'parsed_card_count=$parsedCardCount invalid_card_count=$invalidCardCount '
      'invalid_reasons=$invalidReasons';
}

class FreeEditorialProfileAdapter {
  const FreeEditorialProfileAdapter();

  /// Return the additive `editorial_profile` field from either the direct public
  /// payload map or the `/interpret/ui` response envelope (`{"public": ...}`).
  Map<dynamic, dynamic>? editorialProfileRaw(Map<String, dynamic>? payload) {
    if (payload == null) return null;
    final direct = payload['editorial_profile'];
    if (direct is Map) return direct;
    final public = payload['public'];
    if (public is Map) {
      final nested = public['editorial_profile'];
      if (nested is Map) return nested;
    }
    return null;
  }

  /// Parse the additive `editorial_profile` field from a public payload map.
  /// Returns a typed invalid/empty model when the field is absent or malformed.
  FreeEditorialProfileModel parse(Map<String, dynamic>? payload) {
    return parseDetailed(payload).model;
  }

  FreeEditorialParseResult parseDetailed(Map<String, dynamic>? payload) {
    final raw = editorialProfileRaw(payload);
    if (raw == null) {
      return _diagnose(
        const FreeEditorialParseResult(
          model: FreeEditorialProfileModel.empty,
          rawCardCount: 0,
          parsedCardCount: 0,
          invalidCardCount: 0,
          invalidReasons: <String>['editorial_field_absent'],
        ),
      );
    }
    final cardsRaw = raw['cards'];
    if (cardsRaw is! List) {
      return _diagnose(
        const FreeEditorialParseResult(
          model: FreeEditorialProfileModel.empty,
          rawCardCount: 0,
          parsedCardCount: 0,
          invalidCardCount: 0,
          invalidReasons: <String>['cards_not_list'],
        ),
      );
    }

    final cards = <FreeEditorialCardModel>[];
    final invalidReasons = <String>[];
    for (final item in cardsRaw) {
      if (item is! Map) {
        invalidReasons.add('card_not_object');
        continue;
      }
      final invalidReason = _invalidCardReason(item);
      if (invalidReason != null) {
        invalidReasons.add(invalidReason);
        continue;
      }
      final card = _parseCard(item);
      if (card != null) cards.add(card);
    }
    cards.sort((a, b) => a.ordinal.compareTo(b.ordinal));

    final missing = <FreeEditorialOmission>[];
    final diag = raw['diagnostics'];
    if (diag is Map && diag['missing_keys'] is List) {
      for (final m in diag['missing_keys'] as List) {
        if (m is Map) {
          missing.add(
            FreeEditorialOmission(
              primaryKey: '${m['primary_key'] ?? ''}',
              reason: '${m['reason'] ?? ''}',
            ),
          );
        }
      }
    }

    return _diagnose(
      FreeEditorialParseResult(
        model: FreeEditorialProfileModel(
          version: '${raw['version'] ?? ''}',
          locale: '${raw['locale'] ?? ''}',
          cards: cards,
          missingKeys: missing,
          isValid: cards.isNotEmpty,
        ),
        rawCardCount: cardsRaw.length,
        parsedCardCount: cards.length,
        invalidCardCount: invalidReasons.length,
        invalidReasons: List<String>.unmodifiable(invalidReasons),
      ),
    );
  }

  FreeEditorialParseResult _diagnose(FreeEditorialParseResult result) {
    assert(() {
      debugPrint(result.diagnosticLine);
      return true;
    }());
    return result;
  }

  String? _invalidCardReason(Map<dynamic, dynamic> item) {
    if ('${item['title'] ?? ''}'.trim().isEmpty) {
      return 'missing_title';
    }
    if ('${item['primary_key'] ?? ''}'.trim().isEmpty) {
      return 'missing_primary_key';
    }
    return null;
  }

  FreeEditorialCardModel? _parseCard(Map<dynamic, dynamic> item) {
    final title = '${item['title'] ?? ''}'.trim();
    final primaryKey = '${item['primary_key'] ?? ''}'.trim();
    if (title.isEmpty || primaryKey.isEmpty) return null; // never synthesize

    final blocks = <FreeEditorialBlock>[];
    final blocksRaw = item['content_blocks'];
    if (blocksRaw is List) {
      for (final b in blocksRaw) {
        if (b is Map) {
          blocks.add(
            FreeEditorialBlock(
              role: '${b['role'] ?? ''}',
              text: '${b['text'] ?? ''}',
              sourceField: '${b['source_field'] ?? ''}',
            ),
          );
        }
      }
    }

    // Chips stay with their card; never merged across cards.
    final chips = <FreeEditorialChip>[];
    final chipsRaw = item['chips'];
    if (chipsRaw is List) {
      for (final c in chipsRaw) {
        if (c is Map) {
          chips.add(
            FreeEditorialChip(
              label: '${c['label'] ?? ''}',
              source: '${c['source'] ?? ''}',
            ),
          );
        }
      }
    }

    final ownership = item['ownership'];
    final meaningOwner = ownership is Map
        ? '${ownership['meaning_owner'] ?? ''}'
        : '';
    final expressionOwner = ownership is Map
        ? '${ownership['expression_owner'] ?? ''}'
        : '';
    final status = ownership is Map ? '${ownership['status'] ?? ''}' : '';

    return FreeEditorialCardModel(
      cardId: '${item['card_id'] ?? ''}',
      ordinal: item['ordinal'] is int
          ? item['ordinal'] as int
          : int.tryParse('${item['ordinal']}') ?? 0,
      domain: '${item['domain'] ?? ''}',
      planet: '${item['planet'] ?? ''}',
      placementType: '${item['placement_type'] ?? ''}',
      primaryKey: primaryKey,
      assetId: '${item['asset_id'] ?? ''}',
      title: title,
      summary: '${item['summary'] ?? ''}',
      blocks: blocks,
      chips: chips,
      meaningOwner: meaningOwner,
      expressionOwner: expressionOwner,
      ownershipStatus: status,
    );
  }
}
