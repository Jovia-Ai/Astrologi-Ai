// Stack-clause cooldown + composition helpers.
//
// The backend emits the stack synergy clause as a sibling field on
// qualifying event cards (see `docs/flutter_stack_clause_integration.md`).
// This module encapsulates two pure decisions the UI layer needs:
//
//   * Should we show the clause right now? (rolling 7-day cooldown +
//     feature flag + presence check)
//   * How do we compose the final displayed line from whatever base
//     narrative the widget already selected?
//
// Everything here is a pure function. State (last-shown timestamp,
// feature flag, idempotency guard) lives in the Riverpod providers
// that wrap these helpers — `joviaAppPreferencesProvider` and
// `stackClauseFeatureEnabledProvider`.

import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Rolling cooldown window: one clause appearance per 7 days per device.
/// Constant is exposed so tests can reference it directly.
const int kStackClauseCooldownMs = 7 * 24 * 60 * 60 * 1000;

/// Feature flag / kill switch. Defaults to on. Flip to `false` here to
/// disable the clause entirely across every render site without touching
/// engine state. See `docs/engine_toggles.md` for the server-side
/// counterpart (`apply_stack_boost`) that also silences the clause.
final stackClauseFeatureEnabledProvider = Provider<bool>((ref) => true);

/// Returns true iff the stack synergy clause should be concatenated onto
/// the displayed line for this event at this moment.
///
/// Evaluation order matches the contract in
/// `docs/flutter_stack_clause_integration.md`:
///
///   1. Feature flag must be on
///   2. The event must actually carry a clause (engine gate already
///      decided the "top-sig member per day" selection)
///   3. The 7-day rolling cooldown must be satisfied (or never started)
///
/// Pure function — no side effects, no clock access. The caller passes in
/// [nowMs] explicitly so tests can pin time and so a single frame's
/// decisions stay consistent.
bool stackClauseShouldShow({
  required String stackClauseTr,
  required int? lastShownMs,
  required int nowMs,
  required bool featureEnabled,
  int cooldownMs = kStackClauseCooldownMs,
}) {
  if (!featureEnabled) {
    return false;
  }
  if (stackClauseTr.isEmpty) {
    return false;
  }
  if (lastShownMs == null) {
    return true;
  }
  return (nowMs - lastShownMs) >= cooldownMs;
}

/// Concatenates [stackClauseTr] onto [baseText] when [showStackClause] is
/// true. Otherwise returns [baseText] unchanged.
///
/// The separator is a single space. If [baseText] is empty we return just
/// the clause (a card with no base narrative should still surface the
/// synergy cue rather than becoming blank text).
///
/// Does NOT check cooldown or feature flag — that's `stackClauseShouldShow`'s
/// job. Composition here is deliberately trivial so any render site can
/// call it with whichever narrative field (whyItFeelsThisWayTr, whyNow,
/// opening, essence, ...) it picked from its own fallback chain.
String stackClauseComposeLine({
  required String baseText,
  required String stackClauseTr,
  required bool showStackClause,
}) {
  if (!showStackClause || stackClauseTr.isEmpty) {
    return baseText;
  }
  if (baseText.isEmpty) {
    return stackClauseTr;
  }
  return '$baseText $stackClauseTr';
}
