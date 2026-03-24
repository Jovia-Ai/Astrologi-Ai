import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/app/profile/profile_models.dart';

void main() {
  test('NarrativeV2Profile parses selected aspect bundles', () {
    final profile = NarrativeV2Profile.fromMap({
      'contract_version': 'narrative_v2_draft_2026_03',
      'aspect_bundle_selector': {
        'selected_bundles': [
          {
            'bundle_id': 'moon_saturn_square',
            'bundle_type': 'emotional_regulation_bundle',
            'score': 0.87,
            'domains': ['relationships', 'intimacy_depth'],
            'recognition_tags': ['duyguyu filtreleme'],
            'gift_tags': ['duygusal dayaniklilik'],
            'reflex_tags': ['geri cekilme'],
          },
        ],
      },
    });

    expect(profile.contractVersion, 'narrative_v2_draft_2026_03');
    expect(profile.bundles, hasLength(1));
    expect(profile.bundles.first.bundleType, 'emotional_regulation_bundle');
    expect(
      profile.bundles.first.recognitionTags,
      contains('duyguyu filtreleme'),
    );
    expect(profile.hasContent, isTrue);
  });

  test('ProfileInsightModule parses nested content payload', () {
    final module = ProfileInsightModule.fromMap({
      'module_id': 'moon_defense_mechanism',
      'headline': 'Senin savunma mekanizman',
      'subheadline': 'Ay Akrep',
      'moon_sign': 'Scorpio',
      'content': {
        'title': 'Incinmemek icin hep tetikte kaliyorsun',
        'body':
            'Yakinlik arttiginda kontrolu kaybetmemek icin duygunu saklayabilirsin.',
        'share_text': 'Senin savunma mekanizman: tetikte kalmak.',
        'tone': 'reflective',
      },
      'meta': {'priority': 32, 'expandable': true},
    });

    expect(module.hasContent, isTrue);
    expect(module.resolvedTitle, 'Incinmemek icin hep tetikte kaliyorsun');
    expect(
      module.resolvedBody,
      'Yakinlik arttiginda kontrolu kaybetmemek icin duygunu saklayabilirsin.',
    );
    expect(
      module.resolvedShareText,
      'Senin savunma mekanizman: tetikte kalmak.',
    );
    expect(module.resolvedPriority, 32);
    expect(module.meta.expandable, isTrue);
  });
}
