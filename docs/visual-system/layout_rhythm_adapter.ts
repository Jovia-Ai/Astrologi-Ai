import {
  type LayoutRhythmInput,
  type LayoutSectionKind,
} from './normalized_interpretation_schema';

export function selectLayoutRhythm(input: LayoutRhythmInput): LayoutSectionKind {
  if (input.layer === 'utility_item') {
    return 'utility_card';
  }

  if (input.layer === 'transition_bridge') {
    return input.hasIllustrationOpportunity &&
        (input.tokens.ornamentLevel === 'medium' ||
          input.tokens.whitespaceMode === 'breathing')
      ? 'illustration_break'
      : 'centered_break';
  }

  if (
    input.layer === 'identity_core' ||
    input.layer === 'timing_feature' ||
    input.layer === 'bond_summary'
  ) {
    return input.prominence === 'primary' ? 'hero_statement' : 'soft_card';
  }

  if (
    input.layer === 'collective_topic' ||
    input.layer === 'share_object'
  ) {
    return input.hasSocialActions || input.hasMeta ? 'dense_card' : 'soft_card';
  }

  if (input.layer === 'thread_body') {
    return input.contentLength === 'long' ? 'open_text' : 'dense_card';
  }

  if (
    input.layer === 'profile_narrative' ||
    input.layer === 'haritam_section' ||
    input.layer === 'bond_detail'
  ) {
    if (input.contentLength === 'long' && input.tokens.clarity === 'clear') {
      return 'open_text';
    }
    if (input.tokens.densityLevel === 'high') {
      return 'soft_card';
    }
    return 'open_text';
  }

  if (
    input.layer === 'identity_summary' ||
    input.layer === 'personality_imprint' ||
    input.layer === 'timing_support'
  ) {
    return input.tokens.whitespaceMode === 'compressed'
      ? 'dense_card'
      : 'soft_card';
  }

  return 'soft_card';
}
