import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/app/tabs/profile_page.dart';

void main() {
  test('narrative cards prefer explicit detail blocks over body splitting', () {
    final blocks = debugProfileNarrativeDetailBlocksFromMap({
      'id': 'career_visibility',
      'family': 'visible_power',
      'title': 'Dışarıya verdiğin iz',
      'summary': 'Kısa teaser.',
      'body': 'Bu body fallback olarak bölünmemeli. İkinci cümle.',
      'detail_blocks': [
        'İlk blok.',
        'İkinci blok.',
        'Üçüncü blok.',
        'Dördüncü blok.',
        'Beşinci blok.',
        'Altıncı blok.',
        'Yedinci blok.',
        'Sekizinci blok görünmemeli.',
      ],
    });

    expect(blocks, hasLength(7));
    expect(blocks.first, 'İlk blok.');
    expect(blocks.last, 'Yedinci blok.');
    expect(blocks, isNot(contains('Bu body fallback olarak bölünmemeli.')));
  });

  test('narrative cards still split body text when detail blocks are absent', () {
    final blocks = debugProfileNarrativeDetailBlocksFromMap({
      'id': 'mind_voice',
      'family': 'mind_mechanics',
      'title': 'Zihin tonu',
      'body':
          'İlk cümle burada. İkinci cümle burada. Üçüncü cümle burada. Dördüncü cümle burada. Beşinci cümle görünmemeli.',
    });

    expect(blocks, hasLength(4));
    expect(blocks.first, 'İlk cümle burada.');
    expect(blocks.last, 'Dördüncü cümle burada.');
  });
}
