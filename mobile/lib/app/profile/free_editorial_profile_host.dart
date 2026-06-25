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
  });

  final bool showNarrow;
  final FreeEditorialHostReason reason;
  final FreeEditorialProfileModel model;
}

/// Decide host behavior. Production-safe: when the narrow surface is not shown,
/// the caller keeps the existing legacy Profile path. The reason is internal
/// diagnostics only and never masquerades as user content.
FreeEditorialHostDecision decideFreeEditorialHost({
  required Map<String, dynamic>? payload,
  FreeEditorialProfileAdapter adapter = const FreeEditorialProfileAdapter(),
}) {
  if (payload == null || !payload.containsKey('editorial_profile')) {
    return const FreeEditorialHostDecision(
      showNarrow: false,
      reason: FreeEditorialHostReason.payloadAbsent,
      model: FreeEditorialProfileModel.empty,
    );
  }
  final raw = payload['editorial_profile'];
  if (raw is! Map || raw['cards'] is! List) {
    return const FreeEditorialHostDecision(
      showNarrow: false,
      reason: FreeEditorialHostReason.payloadInvalid,
      model: FreeEditorialProfileModel.empty,
    );
  }
  final model = adapter.parse(payload);
  if (!model.isValid || model.cards.isEmpty) {
    return FreeEditorialHostDecision(
      showNarrow: false,
      reason: FreeEditorialHostReason.cardsEmpty,
      model: model,
    );
  }
  return FreeEditorialHostDecision(
    showNarrow: true,
    reason: FreeEditorialHostReason.show,
    model: model,
  );
}
