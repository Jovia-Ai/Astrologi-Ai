import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:mobile/app/tabs/profile_detail_flow_page.dart';
import 'package:mobile/design/widgets/jovia_editorial.dart';

void main() {
  testWidgets('detail flow uses a vertical PageView player', (tester) async {
    await _pumpDetailFlow(
      tester,
      scenes: const [
        ProfileDetailSceneData(
          id: 'scene_a',
          eyebrow: 'Kimlik',
          title: 'Ilk Sahne',
          intro: 'Kisa giris',
          bodyBlocks: ['Birinci blok.'],
          chips: ['net durus'],
          whyText: '',
          illustrationAsset: JoviaIllustrationAsset.planet,
          variant: ProfileDetailSceneVariant.glance,
          nextTitle: 'Ikinci Sahne',
        ),
      ],
    );

    expect(find.byKey(const Key('profileDetailPageView')), findsOneWidget);
    expect(find.byType(PageView), findsOneWidget);
    expect(find.byType(ListView), findsNothing);
  });

  test('long scene is split into continuation playback pages', () {
    final pages = debugBuildProfileDetailPlaybackPages(const [
      ProfileDetailSceneData(
        id: 'scene_split',
        eyebrow: 'Kimlik',
        title: 'Parcalanan Sahne',
        intro: 'Bu sahne bolunmeli.',
        bodyBlocks: [
          'Birinci blok.',
          'Ikinci blok.',
          'Ucuncu blok.',
          'Dorduncu blok.',
          'Besinci blok.',
        ],
        chips: ['net durus', 'yapi kurucu', 'odak'],
        whyText: 'Bu neden burada aciklamasi.',
        illustrationAsset: JoviaIllustrationAsset.planet,
        variant: ProfileDetailSceneVariant.structuredInsight,
      ),
    ]);

    expect(pages, hasLength(3));
    expect(pages[0].bodyBlocks, [
      'Birinci blok.',
      'Ikinci blok.',
      'Ucuncu blok.',
    ]);
    expect(pages[1].bodyBlocks, ['Dorduncu blok.', 'Besinci blok.']);
    expect(pages[2].whyText, 'Bu neden burada aciklamasi.');
    expect(pages[2].allowAutoAdvance, isFalse);
  });

  testWidgets('multi-part scene uses a horizontal continuation pager', (
    tester,
  ) async {
    await _pumpDetailFlow(
      tester,
      scenes: const [
        ProfileDetailSceneData(
          id: 'scene_split',
          eyebrow: 'Kimlik',
          title: 'Parcalanan Sahne',
          intro: 'Bu sahne bolunmeli.',
          bodyBlocks: [
            'Birinci blok.',
            'Ikinci blok.',
            'Ucuncu blok.',
            'Dorduncu blok.',
            'Besinci blok.',
          ],
          chips: ['net durus', 'yapi kurucu', 'odak'],
          whyText: 'Bu neden burada aciklamasi.',
          illustrationAsset: JoviaIllustrationAsset.planet,
          variant: ProfileDetailSceneVariant.structuredInsight,
        ),
      ],
    );

    expect(
      find.byKey(const ValueKey('detailScenePager_scene_split')),
      findsOneWidget,
    );
    expect(find.byType(PageView), findsNWidgets(2));

    await tester.drag(
      find.byKey(const ValueKey('detailScenePager_scene_split')),
      const Offset(-320, 0),
    );
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 400));

    expect(
      find.byKey(const ValueKey('detailPlaybackPage_scene_split_1')),
      findsOneWidget,
    );
  });

  testWidgets('autoplay advances and stops on final page', (tester) async {
    await _pumpDetailFlow(
      tester,
      scenes: const [
        ProfileDetailSceneData(
          id: 'scene_auto_a',
          eyebrow: 'Kimlik',
          title: 'Birinci Sayfa',
          intro: 'Acilis',
          bodyBlocks: ['Ilk blok.'],
          chips: <String>[],
          whyText: '',
          illustrationAsset: JoviaIllustrationAsset.planet,
          variant: ProfileDetailSceneVariant.glance,
          nextTitle: 'Ikinci Sayfa',
        ),
        ProfileDetailSceneData(
          id: 'scene_auto_b',
          eyebrow: 'Zihin',
          title: 'Ikinci Sayfa',
          intro: 'Devam',
          bodyBlocks: ['Ikinci blok.'],
          chips: <String>[],
          whyText: '',
          illustrationAsset: JoviaIllustrationAsset.planet,
          variant: ProfileDetailSceneVariant.glance,
        ),
      ],
    );

    expect(find.text('Birinci Sayfa'), findsWidgets);

    await tester.pump(const Duration(seconds: 8));
    await tester.pump(const Duration(milliseconds: 200));

    expect(
      find.byKey(const ValueKey('detailPlaybackPage_scene_auto_b_0')),
      findsOneWidget,
    );

    await tester.pump(const Duration(seconds: 8));
    await tester.pumpAndSettle();

    expect(
      find.byKey(const ValueKey('detailPlaybackPage_scene_auto_b_0')),
      findsOneWidget,
    );
  });

  testWidgets('tap zones move between pages', (tester) async {
    await _pumpDetailFlow(
      tester,
      scenes: const [
        ProfileDetailSceneData(
          id: 'scene_tap_a',
          eyebrow: 'Kimlik',
          title: 'Tap Bir',
          intro: 'Acilis',
          bodyBlocks: ['Ilk blok.'],
          chips: <String>[],
          whyText: '',
          illustrationAsset: JoviaIllustrationAsset.planet,
          variant: ProfileDetailSceneVariant.glance,
          nextTitle: 'Tap Iki',
        ),
        ProfileDetailSceneData(
          id: 'scene_tap_b',
          eyebrow: 'Zihin',
          title: 'Tap Iki',
          intro: 'Devam',
          bodyBlocks: ['Ikinci blok.'],
          chips: <String>[],
          whyText: '',
          illustrationAsset: JoviaIllustrationAsset.planet,
          variant: ProfileDetailSceneVariant.glance,
        ),
      ],
    );

    await tester.tap(find.byKey(const Key('profileDetailTapNext')));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 400));

    expect(
      find.byKey(const ValueKey('detailPlaybackPage_scene_tap_b_0')),
      findsOneWidget,
    );

    await tester.tap(find.byKey(const Key('profileDetailTapPrev')));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 400));

    expect(
      find.byKey(const ValueKey('detailPlaybackPage_scene_tap_a_0')),
      findsOneWidget,
    );
  });
}

Future<void> _pumpDetailFlow(
  WidgetTester tester, {
  required List<ProfileDetailSceneData> scenes,
}) async {
  await tester.pumpWidget(
    DefaultAssetBundle(
      bundle: _FakeSvgAssetBundle(),
      child: MaterialApp(
        home: ProfileDetailFlowPage(
          flowTitle: 'Kimlik okuması',
          flowSubtitle: 'Detay flow test',
          scenes: scenes,
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
