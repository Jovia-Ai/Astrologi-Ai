// End-to-end integration test — Voice spec v2.1 §11.4 + §13.4 (S2 Commit 2c).
//
// Coverage: SceneData.proofRaw → playback pages → widget render site.
// Unit tests (Commit 2a/2b) cover adapter and widget in isolation; this
// file locks the chain between them.
//
// Scope doc: docs/voice/s2_mobile_plan.md §7 doğrulama check-list:
//   - SceneData.proofRaw → primary page.proofRaw (non-empty flows)
//   - continuation pages proof_raw = '' (sessiz imza scene başında bir kere)
//   - empty proof_raw scene → pages all ''
//   - card/insight/identity scenes (no proofRaw arg) → default ''

import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/app/tabs/profile_detail_flow_page.dart';
import 'package:mobile/design/widgets/jovia_editorial.dart';

ProfileDetailSceneData _sceneWithProof(String proofRaw) {
  return ProfileDetailSceneData(
    id: 'mind_system',
    eyebrow: 'ZIHINSEL ISLEYIS',
    title: 'Zihinsel işleyiş',
    intro: 'Kendini tartıyorsun.',
    bodyBlocks: const <String>[
      'İlk blok paragraf.',
      'İkinci blok paragraf.',
    ],
    chips: const <String>['Satürn', '3. evde', 'Oğlak'],
    astroSources: const <String>[],
    whyText: '',
    illustrationAsset: JoviaIllustrationAsset.planet,
    variant: ProfileDetailSceneVariant.glance,
    proofRaw: proofRaw,
  );
}

void main() {
  group('SceneData.proofRaw → PlaybackPageData.proofRaw passthrough', () {
    test('primary page carries scene.proofRaw', () {
      final pages = debugBuildProfileDetailPlaybackPages(<ProfileDetailSceneData>[
        _sceneWithProof('Satürn · 3. ev · Oğlak'),
      ]);
      expect(pages, isNotEmpty);
      expect(pages.first.proofRaw, 'Satürn · 3. ev · Oğlak');
    });

    test('empty scene.proofRaw → primary page.proofRaw empty', () {
      final pages = debugBuildProfileDetailPlaybackPages(<ProfileDetailSceneData>[
        _sceneWithProof(''),
      ]);
      expect(pages, isNotEmpty);
      expect(pages.first.proofRaw, '');
    });

    test('continuation pages proofRaw always empty — editorial invariant', () {
      // Scene with enough bodyBlocks to force continuation split.
      final scene = ProfileDetailSceneData(
        id: 'mind_system',
        eyebrow: 'Kimlik',
        title: 'Çok uzun sahne',
        intro: 'Kısa giriş.',
        bodyBlocks: const <String>[
          'Birinci blok.',
          'İkinci blok.',
          'Üçüncü blok.',
          'Dördüncü blok.',
          'Beşinci blok.',
          'Altıncı blok.',
        ],
        chips: const <String>['net duruş', 'yapı kurucu', 'odak'],
        astroSources: const <String>[],
        whyText: 'Açıklama.',
        illustrationAsset: JoviaIllustrationAsset.planet,
        variant: ProfileDetailSceneVariant.structuredInsight,
        proofRaw: 'Satürn · 3. ev · Oğlak',
      );
      final pages = debugBuildProfileDetailPlaybackPages(<ProfileDetailSceneData>[scene]);

      // Voice spec v2.1 §11.4 editorial: sessiz imza sadece primary page'de.
      expect(pages.length, greaterThan(1), reason: 'Scene should split into continuation pages');
      expect(pages.first.isContinuation, isFalse);
      expect(pages.first.proofRaw, 'Satürn · 3. ev · Oğlak');

      for (var i = 1; i < pages.length; i++) {
        expect(
          pages[i].isContinuation,
          isTrue,
          reason: 'page $i should be continuation',
        );
        expect(
          pages[i].proofRaw,
          '',
          reason: 'continuation page $i must have empty proofRaw',
        );
      }
    });

    test('multiple scenes — each primary keeps its own proofRaw', () {
      final pages = debugBuildProfileDetailPlaybackPages(<ProfileDetailSceneData>[
        _sceneWithProof('Satürn · 3. ev · Oğlak'),
        _sceneWithProof('Venüs · 11. ev · Balık'),
      ]);
      // Each scene produces at least a primary page.
      final primaryPages = pages.where((page) => !page.isContinuation).toList();
      expect(primaryPages.length, 2);
      expect(primaryPages[0].proofRaw, 'Satürn · 3. ev · Oğlak');
      expect(primaryPages[1].proofRaw, 'Venüs · 11. ev · Balık');
    });

    test('scene without proofRaw argument uses default empty', () {
      const scene = ProfileDetailSceneData(
        id: 'card_scene',
        eyebrow: 'Kart',
        title: 'Kart bazlı sahne',
        intro: 'Giriş.',
        bodyBlocks: <String>['Blok.'],
        chips: <String>[],
        astroSources: <String>[],
        whyText: '',
        illustrationAsset: JoviaIllustrationAsset.planet,
        variant: ProfileDetailSceneVariant.glance,
        // no proofRaw → default ''
      );
      final pages = debugBuildProfileDetailPlaybackPages(<ProfileDetailSceneData>[scene]);
      expect(pages.first.proofRaw, '');
    });

    test('copyWith preserves proofRaw', () {
      final scene = _sceneWithProof('Merkür · 6. ev · Başak');
      final variantChanged = scene.copyWith(
        variant: ProfileDetailSceneVariant.structuredInsight,
      );
      expect(variantChanged.proofRaw, 'Merkür · 6. ev · Başak');
    });
  });

}
