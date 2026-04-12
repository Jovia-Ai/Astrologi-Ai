import 'dart:convert';
import 'dart:developer' as developer;

class PerfTelemetry {
  PerfTelemetry._();

  static final Stopwatch _appClock = Stopwatch()..start();
  static final DateTime _appLaunchAt = DateTime.now().toUtc();
  static final Set<String> _onceKeys = <String>{};
  static final Set<String> _sessionFlags = <String>{};

  static int get uptimeMs => _appClock.elapsedMilliseconds;

  static DateTime get appLaunchAt => _appLaunchAt;

  static PerfSpan startSpan(
    String name, {
    String? startEvent,
    String? finishEvent,
    Map<String, Object?>? data,
  }) {
    final span = PerfSpan._(
      name: name,
      startEvent: startEvent ?? '${name}_start',
      finishEvent: finishEvent ?? '${name}_end',
      startedAt: DateTime.now().toUtc(),
      startMs: uptimeMs,
      baseData: data ?? const <String, Object?>{},
    );
    _emit(span.startEvent, <String, Object?>{
      ...span.baseData,
      'start_ms': span.startMs,
      'end_ms': span.startMs,
      'duration_ms': 0,
      'started_at': span.startedAt.toIso8601String(),
      'ended_at': span.startedAt.toIso8601String(),
    });
    return span;
  }

  static void logPoint(String event, {Map<String, Object?>? data}) {
    final now = DateTime.now().toUtc();
    final nowMs = uptimeMs;
    _emit(event, <String, Object?>{
      ...?data,
      'start_ms': nowMs,
      'end_ms': nowMs,
      'duration_ms': 0,
      'started_at': now.toIso8601String(),
      'ended_at': now.toIso8601String(),
    });
  }

  static bool logPointOnce(
    String onceKey,
    String event, {
    Map<String, Object?>? data,
  }) {
    if (!_onceKeys.add(onceKey)) {
      return false;
    }
    logPoint(event, data: data);
    return true;
  }

  static bool markSessionFlag(String flag) => _sessionFlags.add(flag);

  static void logEvent(String event, {Map<String, Object?>? data}) {
    _emit(event, data ?? const <String, Object?>{});
  }

  static void _emit(String event, Map<String, Object?> data) {
    final payload = <String, Object?>{
      'event': event,
      'app_launch_at': _appLaunchAt.toIso8601String(),
      'uptime_ms': uptimeMs,
      ...data,
    };
    developer.log(jsonEncode(_normalize(payload)), name: 'mobile.perf');
  }

  static Object? _normalize(Object? value) {
    if (value == null || value is num || value is bool || value is String) {
      return value;
    }
    if (value is DateTime) {
      return value.toIso8601String();
    }
    if (value is Duration) {
      return value.inMilliseconds;
    }
    if (value is Enum) {
      return value.name;
    }
    if (value is Map) {
      final entries = value.entries.toList()
        ..sort((a, b) => a.key.toString().compareTo(b.key.toString()));
      return <String, Object?>{
        for (final entry in entries)
          entry.key.toString(): _normalize(entry.value),
      };
    }
    if (value is Iterable) {
      return value.map(_normalize).toList(growable: false);
    }
    return value.toString();
  }
}

class PerfSpan {
  PerfSpan._({
    required this.name,
    required this.startEvent,
    required this.finishEvent,
    required this.startedAt,
    required this.startMs,
    required this.baseData,
  });

  final String name;
  final String startEvent;
  final String finishEvent;
  final DateTime startedAt;
  final int startMs;
  final Map<String, Object?> baseData;

  bool _finished = false;

  int elapsedMs() => PerfTelemetry.uptimeMs - startMs;

  void finish({String status = 'ok', Map<String, Object?>? data}) {
    if (_finished) {
      return;
    }
    _finished = true;
    final endedAt = DateTime.now().toUtc();
    final endMs = PerfTelemetry.uptimeMs;
    PerfTelemetry.logEvent(
      finishEvent,
      data: <String, Object?>{
        ...baseData,
        ...?data,
        'status': status,
        'span_name': name,
        'start_ms': startMs,
        'end_ms': endMs,
        'duration_ms': endMs - startMs,
        'started_at': startedAt.toIso8601String(),
        'ended_at': endedAt.toIso8601String(),
      },
    );
  }
}
