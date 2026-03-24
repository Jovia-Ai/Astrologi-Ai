import {
  type IllustrationSectionSlot,
  type IllustrationSelection,
  type IllustrationSlotInput,
  type LayoutEmphasis,
  type ShapeFamily,
  type SurfaceFamily,
  type VisualTokens,
} from './normalized_interpretation_schema';

const SLOT_OVERRIDES: Partial<Record<IllustrationSectionSlot, string>> = {
  home_hero: 'orbit_signal_01',
  profile_hero: 'container_orbit_01',
  haritam_identity_overview: 'grid_field_01',
  haritam_signature: 'spiral_signature_01',
  timing_feature: 'timeline_pulse_01',
  collective_topic_card: 'paired_topic_01',
  thread_detail_header: 'paired_topic_01',
  bond_summary: 'paired_bond_01',
  studio_share_card: 'share_frame_01',
};

const SHAPE_TO_ASSET: Record<ShapeFamily, string> = {
  orbit: 'orbit_signal_01',
  spiral: 'spiral_container_01',
  grid: 'grid_builder_01',
  wave: 'wave_reflective_01',
  fracture: 'fracture_disruptor_01',
  paired_axis: 'paired_mirror_01',
  stack: 'stack_identity_01',
  burst: 'burst_amplifier_01',
};

const EMPHASIS_TO_FALLBACK: Record<LayoutEmphasis, string> = {
  identity: 'stack_identity_01',
  timing: 'orbit_signal_01',
  collective: 'paired_topic_01',
  bond: 'paired_bond_01',
  share: 'share_frame_01',
};

export function selectIllustration(
  slotInput: IllustrationSlotInput,
  visualTokens: VisualTokens,
  emphasisOverride?: LayoutEmphasis,
): IllustrationSelection {
  const assetId = resolveAssetId(slotInput, emphasisOverride);

  return {
    assetId,
    opacity: resolveOpacity(slotInput.sectionType, visualTokens),
    scale: resolveScale(slotInput.sectionType, visualTokens),
    alignX: resolveAlignX(slotInput.sectionType, slotInput.slot),
    alignY: resolveAlignY(slotInput.sectionType, slotInput.slot),
  };
}

function resolveAssetId(
  input: IllustrationSlotInput,
  emphasisOverride?: LayoutEmphasis,
): string {
  const slotOverride = SLOT_OVERRIDES[input.slot];
  if (slotOverride) {
    return slotOverride;
  }

  const shapeAsset = SHAPE_TO_ASSET[input.shapeFamily];
  if (shapeAsset) {
    return shapeAsset;
  }

  const emphasisAsset = EMPHASIS_TO_FALLBACK[emphasisOverride ?? input.emphasis];
  if (emphasisAsset) {
    return emphasisAsset;
  }

  return fallbackBySectionType(input.sectionType);
}

function fallbackBySectionType(sectionType: SurfaceFamily): string {
  switch (sectionType) {
    case 'hero':
      return 'orbit_signal_01';
    case 'reading':
      return 'grid_builder_01';
    case 'social':
      return 'paired_topic_01';
    case 'utility':
    default:
      return 'stack_identity_01';
  }
}

function resolveOpacity(
  sectionType: SurfaceFamily,
  visualTokens: VisualTokens,
): number {
  if (sectionType === 'hero') {
    return visualTokens.contrastLevel === 'high' ? 0.22 : 0.16;
  }
  if (sectionType === 'social') {
    return 0.12;
  }
  if (sectionType === 'reading') {
    return visualTokens.whitespaceMode === 'breathing' ? 0.1 : 0.08;
  }
  return 0.06;
}

function resolveScale(
  sectionType: SurfaceFamily,
  visualTokens: VisualTokens,
): number {
  if (sectionType === 'hero') {
    return visualTokens.densityLevel === 'high' ? 1.1 : 1.22;
  }
  if (sectionType === 'social') {
    return 0.92;
  }
  if (sectionType === 'reading') {
    return 1;
  }
  return 0.84;
}

function resolveAlignX(
  sectionType: SurfaceFamily,
  slot: IllustrationSectionSlot,
): number {
  if (slot === 'profile_hero' || slot === 'home_hero') {
    return 0.82;
  }
  if (slot === 'thread_detail_header' || sectionType === 'social') {
    return 0.86;
  }
  return 0.78;
}

function resolveAlignY(
  sectionType: SurfaceFamily,
  slot: IllustrationSectionSlot,
): number {
  if (slot === 'studio_share_card') {
    return 0.16;
  }
  if (sectionType === 'hero') {
    return 0.12;
  }
  if (sectionType === 'reading') {
    return 0.18;
  }
  return 0.14;
}
