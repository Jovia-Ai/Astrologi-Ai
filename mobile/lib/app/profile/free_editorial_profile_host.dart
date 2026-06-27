// FREE-PROFILE-R4C — pure host decision for the narrow Free editorial surface.
//
// Decides whether the narrow surface should replace the legacy Profile content,
// based ONLY on a valid editorial_profile payload. Records a typed reason for
// diagnostics. No legacy fallback consulted, no mutation, no mock content.

import 'free_editorial_profile_adapter.dart';

enum FreeEditorialHostReason {
  show,
  payloadAbsent, // EDITORIAL_PAYLOAD_ABSENT
  payloadInvalid, // EDITORIAL_PAYLOAD_INVALID
  cardsEmpty, // EDITORIAL_CARDS_EMPTY
}

extension FreeEditorialHostReasonCode on FreeEditorialHostReason {
  String get code {
    switch (this) {
      case FreeEditorialHostReason.show:
        return 'EDITORIAL_SHOW';
      case FreeEditorialHostReason.payloadAbsent:
        return 'EDITORIAL_PAYLOAD_ABSENT';
      case FreeEditorialHostReason.payloadInvalid:
        return 'EDITORIAL_PAYLOAD_INVALID';
      case FreeEditorialHostReason.cardsEmpty:
        return 'EDITORIAL_CARDS_EMPTY';
    }
  }
}

class FreeEditorialHostDecision {
  const FreeEditorialHostDecision({
    required this.showNarrow,
    required this.reason,
    required this.model,
    required this.payloadPresent,
    required this.editorialFieldPresent,
    required this.cardCount,
  });

  final bool showNarrow;
  final FreeEditorialHostReason reason;
  final FreeEditorialProfileModel model;
  final bool payloadPresent;
  final bool editorialFieldPresent;
  final int cardCount;

  String get decisionLabel => showNarrow ? 'narrow' : 'legacy';
  String? get diagnosticReason => showNarrow ? null : reason.code;

  String get diagnosticLine =>
      'FREE_EDITORIAL_HOST decision=$decisionLabel '
      'raw_payload_present=$payloadPresent '
      'editorial_field_present=$editorialFieldPresent raw_card_count=$cardCount '
      'reason=${diagnosticReason ?? 'null'}';
}

/// Decide host behavior. Production-safe: when the narrow surface is not shown,
/// the caller keeps the existing legacy Profile path. The reason is internal
/// diagnostics only and never masquerades as user content.
FreeEditorialHostDecision decideFreeEditorialHost({
  required Map<String, dynamic>? payload,
  FreeEditorialProfileAdapter adapter = const FreeEditorialProfileAdapter(),
}) {
  final payloadPresent = payload != null;
  final directFieldPresent = payload?.containsKey('editorial_profile') ?? false;
  final public = payload == null ? null : payload['public'];
  final nestedFieldPresent =
      public is Map && public.containsKey('editorial_profile');
  final editorialFieldPresent = directFieldPresent || nestedFieldPresent;
  final raw = adapter.editorialProfileRaw(payload);
  final cardsRaw = raw == null ? null : raw['cards'];
  final cardCount = cardsRaw is List ? cardsRaw.length : 0;
  final parseResult = adapter.parseDetailed(payload);
  if (!payloadPresent || !editorialFieldPresent) {
    return FreeEditorialHostDecision(
      showNarrow: false,
      reason: FreeEditorialHostReason.payloadAbsent,
      model: FreeEditorialProfileModel.empty,
      payloadPresent: payloadPresent,
      editorialFieldPresent: editorialFieldPresent,
      cardCount: cardCount,
    );
  }
  if (raw == null || cardsRaw is! List) {
    return FreeEditorialHostDecision(
      showNarrow: false,
      reason: FreeEditorialHostReason.payloadInvalid,
      model: FreeEditorialProfileModel.empty,
      payloadPresent: payloadPresent,
      editorialFieldPresent: editorialFieldPresent,
      cardCount: cardCount,
    );
  }
  final model = parseResult.model;
  if (!model.isValid || model.cards.isEmpty) {
    return FreeEditorialHostDecision(
      showNarrow: false,
      reason: FreeEditorialHostReason.cardsEmpty,
      model: model,
      payloadPresent: payloadPresent,
      editorialFieldPresent: editorialFieldPresent,
      cardCount: cardCount,
    );
  }
  return FreeEditorialHostDecision(
    showNarrow: true,
    reason: FreeEditorialHostReason.show,
    model: model,
    payloadPresent: payloadPresent,
    editorialFieldPresent: editorialFieldPresent,
    cardCount: cardCount,
  );
}
