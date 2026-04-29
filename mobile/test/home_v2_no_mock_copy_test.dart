// Lint guard for P0-A Home V2 cleanup.
//
// Asserts that hardcoded mock copy and mock partner names that the
// cleanup removed cannot silently re-enter `home_page_v2.dart`. If a
// test below fails, someone re-introduced a hardcoded editorial line or
// a fictional friend identity — replace it with a backend-driven hook
// or gate behind `kHomeBondFeatureEnabled`.
//
// Source: docs/system/home_profile_surface_cleanup_plan.md (P0-A).

import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

const _homePageV2Path = 'lib/app/tabs/home_page_v2.dart';

String _readSource() {
  // Tests run from the `mobile/` directory; resolve relative to CWD.
  final file = File(_homePageV2Path);
  if (!file.existsSync()) {
    fail('expected to find $_homePageV2Path relative to test cwd ${Directory.current.path}');
  }
  return file.readAsStringSync();
}

void _expectAbsent(String source, String forbidden, {required String reason}) {
  // String.allMatches is inherited from Pattern; counts non-overlapping
  // occurrences of `forbidden` in `source`.
  final hits = forbidden.allMatches(source).length;
  expect(
    hits,
    0,
    reason:
        'P0-A drift: forbidden mock copy "$forbidden" reappeared in '
        '$_homePageV2Path. $reason',
  );
}

void main() {
  group('Home V2 mock-copy lint (P0-A)', () {
    late final String source;
    setUpAll(() {
      source = _readSource();
    });

    test('Manifesto title hardcoded copy removed', () {
      _expectAbsent(
        source,
        'Sahnede olmak istemediğin anlar',
        reason:
            'Manifesto title must come from HomeV2Snapshot.coreStoryHeadline. '
            'If this string returns, the hardcoded fallback was re-added.',
      );
      _expectAbsent(
        source,
        'en çok bakıldığın anlar olabilir',
        reason: 'Trailing half of the same hardcoded manifesto title.',
      );
    });

    test('Sky central quote hardcoded copy removed', () {
      _expectAbsent(
        source,
        'Ay Aslan\'da — görünmek değil',
        reason:
            'Central sky-quote was hardcoded. Until a backend sky-now '
            'hook ships, the section keeps eyebrow + horizontal rail only.',
      );
      _expectAbsent(
        source,
        'görünmek değil, görülmek istiyor',
        reason: 'Trailing half of the same hardcoded sky-quote.',
      );
    });

    test('Mock friend names removed from Near rail', () {
      // Each name is checked as a quoted Dart string literal so we don't
      // false-positive on substrings inside genuine code (e.g. a comment).
      const mockNames = <String>[
        "name: 'Mira'",
        "name: 'Ela'",
        "name: 'Burak'",
        "name: 'Deniz'",
        "name: 'Kayra'",
      ];
      for (final pattern in mockNames) {
        _expectAbsent(
          source,
          pattern,
          reason:
              'Mock _FriendAviData entries with this name were removed. '
              'Once the Bond feature ships, populate _NearRail from '
              'bondPartnersProvider, not a hardcoded list.',
        );
      }
    });

    test('Mock friend chip labels removed from feed posts', () {
      // _FeedPost* widgets previously rendered _FeedMetaChip(label:'Mira'…)
      // etc. Their bodies are now SizedBox.shrink — these chip labels
      // must not reappear unless the section is rewritten with live data.
      const chipPatterns = <String>[
        "label: 'Mira'",
        "label: 'Ela'",
        "label: 'Burak'",
        "label: 'Deniz'",
      ];
      for (final pattern in chipPatterns) {
        _expectAbsent(
          source,
          pattern,
          reason:
              '_FeedMetaChip with a hardcoded mock author name was removed.',
        );
      }
    });

    test('Mock friend transit body copy removed', () {
      // Sentinel snippets from the four _FeedPost* widget bodies.
      const bodySnippets = <String>[
        'Mira da bugün Ay Aslan',
        'Ela\'nın Venüs\'ü senin',
        'Burak için bugün',
        'Deniz\'in ',
      ];
      for (final snippet in bodySnippets) {
        _expectAbsent(
          source,
          snippet,
          reason:
              'Hardcoded "friend transit" editorial copy removed; live '
              'feed data must come from a future bondFeedProvider.',
        );
      }
    });

    test('Bond feature flag is wired and default-off', () {
      expect(
        source.contains('const bool kHomeBondFeatureEnabled = false'),
        isTrue,
        reason:
            'kHomeBondFeatureEnabled flag must exist and default to false '
            'so _NearSection / _FeedSection do not render before live data.',
      );
    });
  });
}
