import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/app/tabs/profile_archetype_page.dart';
import 'package:mobile/design/theme/profile_theme_extension.dart';

void main() {
  testWidgets('renders subprofile, summary, and assembled copy blocks', (
    tester,
  ) async {
    await _pumpPage(
      tester,
      payload: {
        'top_archetypes': [
          {
            'id': 'builder',
            'label': 'Kurucu',
            'score': 0.91,
            'subprofile_id': 'systems_architect',
            'subprofile_label_tr': 'Sistem Mimari',
            'copy_blocks': {
              'plain_summary_tr':
                  'Bu sonuc en cok sistem kurma sinyalinden geliyor.',
              'portrait_tr': 'Dinamik portre.',
              'gift_tr': 'Dinamik hediye.',
              'fear_tr': 'Dinamik korku.',
              'shadow_tr': 'Dinamik golge.',
              'relationship_tr': 'Dinamik iliski.',
              'work_style_tr': 'Dinamik is.',
              'growth_tr': 'Dinamik buyume.',
              'flavor_tr': 'Bu ton model kurar.',
            },
            'differentiators': ['Kurarken yalnizca tasimaz; modeli de kurar.'],
            'mixins': [
              {'id': 'visibility_mode', 'value_label_tr': 'Secici vitrin'},
            ],
            'copy_variant':
                'builder:systems_architect:curated:deliberate:observing',
            'why_this_not_that': 'Bu profil onde.',
            'source_split': {
              'chart_prior': 0.72,
              'test_score': 0.82,
              'context_score': 0.0,
            },
          },
        ],
        'test_scores': [
          {'id': 'builder', 'label': 'Kurucu', 'score': 0.82},
        ],
        'chart_prior': {'items': []},
        'shadow_archetype': {},
        'primary_contradiction': {},
        'confidence': {'global': 0.88, 'chart': 0.79, 'test': 0.91},
        'slots': {'primary_identity_spine': 'builder'},
        'question_summary': {'has_test_result': true},
      },
    );

    expect(find.text('Kurucu / Sistem Mimari'), findsOneWidget);
    expect(find.text('Secici vitrin'), findsOneWidget);
    expect(
      find.text('Bu sonuc en cok sistem kurma sinyalinden geliyor.'),
      findsWidgets,
    );
    expect(find.text('Dinamik is.'), findsOneWidget);
    expect(find.text('Bu ton model kurar.'), findsOneWidget);
  });

  testWidgets(
    'falls back to legacy archetype copy when new fields are absent',
    (tester) async {
      await _pumpPage(
        tester,
        payload: {
          'top_archetypes': [
            {
              'id': 'builder',
              'label': 'Kurucu',
              'score': 0.89,
              'motto_tr': 'Bir seyin omurgasi yoksa, onu kur.',
              'portrait_tr': 'Eski portre metni.',
              'gift_tr': 'Eski hediye metni.',
              'fear_tr': 'Eski korku metni.',
              'shadow_tr': 'Eski golge metni.',
              'relationship_tr': 'Eski iliski metni.',
              'work_style_tr': 'Eski is metni.',
              'growth_tr': 'Eski buyume metni.',
              'source_split': {
                'chart_prior': 0.7,
                'test_score': 0.0,
                'context_score': 0.0,
              },
            },
          ],
          'test_scores': [],
          'chart_prior': {'items': []},
          'shadow_archetype': {},
          'primary_contradiction': {},
          'confidence': {'global': 0.74, 'chart': 0.74, 'test': 0.0},
          'slots': {'primary_identity_spine': 'builder'},
          'question_summary': {'has_test_result': false},
        },
      );

      expect(find.text('Kurucu sende one cikiyor'), findsOneWidget);
      expect(find.text('Eski hediye metni.'), findsOneWidget);
      expect(find.text('Eski buyume metni.'), findsOneWidget);
      expect(find.text('Sistem Mimari'), findsNothing);
    },
  );
}

Future<void> _pumpPage(
  WidgetTester tester, {
  required Map<String, dynamic> payload,
}) async {
  await tester.pumpWidget(
    DefaultAssetBundle(
      bundle: _FakeSvgAssetBundle(),
      child: MaterialApp(
        theme: withProfileTheme(ThemeData.light()),
        home: ProfileArchetypeExperiencePage(
          displayName: 'Sahra',
          requestPayload: const {},
          initialPayload: payload,
        ),
      ),
    ),
  );
  await tester.pump();
}

class _FakeSvgAssetBundle extends CachingAssetBundle {
  static const _svg = '''
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">
  <rect width="10" height="10" fill="white"/>
</svg>
''';

  @override
  Future<ByteData> load(String key) async {
    final bytes = Uint8List.fromList(utf8.encode(_svg));
    return ByteData.view(bytes.buffer);
  }
}
