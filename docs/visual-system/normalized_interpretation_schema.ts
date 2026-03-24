export const DOMAIN_KEYS = [
  'identity',
  'relationships',
  'intimacy_depth',
  'mind_communication',
  'meaning_learning',
  'career_visibility',
  'creativity_talent',
  'home_roots',
  'private_inner_world',
  'social_future',
] as const;

export type DomainKey = (typeof DOMAIN_KEYS)[number];

export const NARRATIVE_V2_BUNDLE_TYPES = [
  'emotional_regulation_bundle',
  'mental_style_bundle',
  'relational_pattern_bundle',
  'angle_identity_bundle',
  'pressure_growth_bundle',
  'soft_capacity_bundle',
  'contradiction_bundle',
  'personal_core_bundle',
] as const;

export type NarrativeV2BundleType =
  (typeof NARRATIVE_V2_BUNDLE_TYPES)[number];

export const IMPRINT_KINDS = [
  'aspect',
  'house_placement',
  'sign_placement',
] as const;

export type ImprintKind = (typeof IMPRINT_KINDS)[number];

export const TIMING_HORIZONS = ['day', 'period'] as const;
export type TimingHorizon = (typeof TIMING_HORIZONS)[number];

export const TIMING_PHASES = [
  'applying',
  'peak',
  'exact',
  'exit',
  'waning',
  'receding',
  'unknown',
] as const;

export type TimingPhase = (typeof TIMING_PHASES)[number];

export const INTENT_TYPES = [
  'general',
  'beauty_care',
  'business',
  'money',
  'relationship',
] as const;

export type IntentType = (typeof INTENT_TYPES)[number];

export const BOND_LENSES = ['romantic', 'friendship', 'work'] as const;
export type BondLens = (typeof BOND_LENSES)[number];

export const ENERGY_TYPES = ['earth', 'fire', 'air', 'water', 'mixed'] as const;
export type EnergyType = (typeof ENERGY_TYPES)[number];

export const MOOD_TYPES = [
  'calm',
  'focused',
  'contained',
  'intense',
  'diffuse',
  'volatile',
  'structured',
  'ambiguous',
] as const;

export type MoodType = (typeof MOOD_TYPES)[number];

export const BEHAVIORAL_PATTERNS = [
  'observer',
  'initiator',
  'stabilizer',
  'adapter',
  'container',
  'amplifier',
  'integrator',
  'distiller',
] as const;

export type BehavioralPattern = (typeof BEHAVIORAL_PATTERNS)[number];

export const MENTAL_PATTERNS = [
  'analytical',
  'reflective',
  'looping',
  'anticipatory',
  'narrative',
  'comparative',
  'concrete',
  'synthetic',
] as const;

export type MentalPattern = (typeof MENTAL_PATTERNS)[number];

export const EMOTIONAL_PATTERNS = [
  'steady',
  'guarded',
  'permeable',
  'expressive',
  'oscillating',
  'deepening',
  'contained',
  'detached',
] as const;

export type EmotionalPattern = (typeof EMOTIONAL_PATTERNS)[number];

export const EXPRESSION_PATTERNS = [
  'direct',
  'measured',
  'symbolic',
  'quiet',
  'curated',
  'persuasive',
  'performative',
  'exploratory',
] as const;

export type ExpressionPattern = (typeof EXPRESSION_PATTERNS)[number];

export const RELATIONAL_PATTERNS = [
  'bonding',
  'testing',
  'mirroring',
  'caretaking',
  'autonomy_seeking',
  'merging',
  'negotiating',
  'instructive',
] as const;

export type RelationalPattern = (typeof RELATIONAL_PATTERNS)[number];

export const TENSION_PATTERNS = [
  'none',
  'inner_split',
  'overcontrol',
  'diffusion',
  'friction',
  'asymmetry',
  'delayed_release',
  'intensity_spike',
] as const;

export type TensionPattern = (typeof TENSION_PATTERNS)[number];

export const ARCHETYPES = [
  'builder',
  'observer',
  'distiller',
  'integrator',
  'amplifier',
  'container',
  'disruptor',
  'mirror',
] as const;

export type Archetype = (typeof ARCHETYPES)[number];

export const INTENSITY_BANDS = ['low', 'medium', 'high'] as const;
export type IntensityBand = (typeof INTENSITY_BANDS)[number];

export const DENSITY_LEVELS = ['low', 'medium', 'high'] as const;
export type DensityLevel = (typeof DENSITY_LEVELS)[number];

export const CONTRAST_LEVELS = ['soft', 'medium', 'high'] as const;
export type ContrastLevel = (typeof CONTRAST_LEVELS)[number];

export const STRUCTURE_LEVELS = ['fluid', 'balanced', 'structured'] as const;
export type StructureLevel = (typeof STRUCTURE_LEVELS)[number];

export const DIRECTIONALITY = ['inward', 'balanced', 'outward'] as const;
export type Directionality = (typeof DIRECTIONALITY)[number];

export const VISUAL_SPEEDS = ['slow', 'steady', 'fast', 'oscillating'] as const;
export type VisualSpeed = (typeof VISUAL_SPEEDS)[number];

export const COHESION_LEVELS = ['cohesive', 'tensioned', 'fragmented'] as const;
export type CohesionLevel = (typeof COHESION_LEVELS)[number];

export const CLARITY_LEVELS = ['clear', 'mixed', 'ambiguous'] as const;
export type ClarityLevel = (typeof CLARITY_LEVELS)[number];

export const WEIGHT_LEVELS = ['light', 'grounded', 'heavy'] as const;
export type WeightLevel = (typeof WEIGHT_LEVELS)[number];

export const WHITESPACE_MODES = ['compressed', 'balanced', 'breathing'] as const;
export type WhitespaceMode = (typeof WHITESPACE_MODES)[number];

export const TYPOGRAPHY_MODES = ['editorial', 'balanced', 'technical'] as const;
export type TypographyMode = (typeof TYPOGRAPHY_MODES)[number];

export const ORNAMENT_LEVELS = ['low', 'medium', 'high'] as const;
export type OrnamentLevel = (typeof ORNAMENT_LEVELS)[number];

export const SOCIAL_DENSITIES = ['quiet', 'active', 'busy'] as const;
export type SocialDensity = (typeof SOCIAL_DENSITIES)[number];

export const SURFACE_FAMILIES = ['hero', 'reading', 'social', 'utility'] as const;
export type SurfaceFamily = (typeof SURFACE_FAMILIES)[number];

export const LAYOUT_SECTION_KINDS = [
  'hero_statement',
  'soft_card',
  'dense_card',
  'open_text',
  'centered_break',
  'illustration_break',
  'utility_card',
] as const;

export type LayoutSectionKind = (typeof LAYOUT_SECTION_KINDS)[number];

export const LAYOUT_EMPHASIS = [
  'identity',
  'timing',
  'collective',
  'bond',
  'share',
] as const;

export type LayoutEmphasis = (typeof LAYOUT_EMPHASIS)[number];

export const SHAPE_FAMILIES = [
  'orbit',
  'spiral',
  'grid',
  'wave',
  'fracture',
  'paired_axis',
  'stack',
  'burst',
] as const;

export type ShapeFamily = (typeof SHAPE_FAMILIES)[number];

export const MOTION_FAMILIES = [
  'still',
  'pulse',
  'drift',
  'rise',
  'oscillate',
  'split',
  'merge',
] as const;

export type MotionFamily = (typeof MOTION_FAMILIES)[number];

export const ILLUSTRATION_SECTION_SLOTS = [
  'home_hero',
  'profile_hero',
  'haritam_identity_overview',
  'haritam_signature',
  'timing_feature',
  'collective_topic_card',
  'thread_detail_header',
  'bond_summary',
  'studio_share_card',
] as const;

export type IllustrationSectionSlot =
  (typeof ILLUSTRATION_SECTION_SLOTS)[number];

export interface RawPlanetPlacement {
  planet?: string;
  name?: string;
  body?: string;
  sign?: string;
  zodiac_sign?: string;
  house?: number | string;
}

export interface RawProfileNarrativeBlock {
  id?: string;
  headline?: string;
  teaser?: string;
  subtitle?: string;
  body?: string;
  micro?: string;
  astro_hint?: string;
  astro_sources?: string[];
  chips?: string[];
}

export interface RawNarrativeV2Bundle {
  bundle_id?: string;
  bundle_type?: NarrativeV2BundleType | string;
  score?: number;
  domains?: string[];
  recognition_tags?: string[];
  gift_tags?: string[];
  reflex_tags?: string[];
}

export interface RawNarrativeV2Payload {
  contract_version?: string;
  aspect_bundle_selector?: {
    selected_bundles?: RawNarrativeV2Bundle[];
  };
}

export interface RawPersonalityImprintEntry {
  key?: string;
  kind?: ImprintKind | string;
  label_tr?: string;
  tags?: string[];
  aura?: string;
  trait?: string;
  drive?: string;
  shadow?: string;
  background_hint?: string;
  gift?: string;
  support_keys?: string[];
}

export interface RawPersonalityImprintBundle {
  id?: string;
  dominant_key?: string;
  dominant_kind?: string;
  related_planets?: string[];
  support_keys?: string[];
}

export interface RawPersonalityImprintPayload {
  engine_version?: string;
  library_version?: string;
  locale?: string;
  headline?: string;
  render_shape?: Record<string, unknown>;
  entries?: RawPersonalityImprintEntry[];
  extra_entries?: RawPersonalityImprintEntry[];
  support_entries?: RawPersonalityImprintEntry[];
  bundles?: RawPersonalityImprintBundle[];
  extra_bundles?: RawPersonalityImprintBundle[];
}

export interface RawSupportingThread {
  id?: string;
  title?: string;
  one_liner?: string;
  paragraph?: string;
}

export interface RawInterpretScope {
  core_story?: string;
  core_story_ui?: { text?: string };
  narrative_text?: string;
  summary?: string;
  planets?: RawPlanetPlacement[];
  planet_signs?: Record<string, string>;
  signs?: Record<string, string>;
  angles?: {
    ascendant_sign?: string;
    asc_sign?: string;
  };
  formatted_positions?: string[];
  formatted_houses?: string[];
  profile_narrative?: {
    profile_public?: {
      engine_version?: string;
      blocks?: RawProfileNarrativeBlock[];
    };
  };
  narrative_v2?: RawNarrativeV2Payload;
  personality_imprint?: RawPersonalityImprintPayload;
  supporting_threads?: RawSupportingThread[];
}

export interface RawInterpretResponse extends RawInterpretScope {
  public?: RawInterpretScope;
  meta_info?: RawInterpretScope;
}

export interface RawNarrativeCopy {
  title?: string;
  short?: string;
  medium?: string;
  long?: string;
}

export interface RawNarrativeBlock {
  id?: string;
  type?: string;
  horizon?: string;
  intensity?: number;
  domains?: string[];
  copy?: RawNarrativeCopy;
  why?: string[];
  meta?: Record<string, unknown>;
  cta?: Record<string, unknown>;
}

export interface RawNarrativeScreen {
  title?: string;
  blocks?: RawNarrativeBlock[];
  events_count?: number;
  signals_count?: number;
  has_signals?: boolean;
  date?: string;
}

export interface RawNarrativeCalendarDay {
  date?: string;
  rating?: number;
  heat?: number;
  event_count?: number;
  signals_count?: number;
  has_signals?: boolean;
  is_critical?: boolean;
  labels?: string[];
  critical_reasons?: string[];
}

export interface RawPeriodCoreTag {
  type?: string;
  value?: string;
}

export interface RawPeriodCore {
  title?: string;
  core_story?: string;
  upper_meaning?: string;
  big_picture?: string;
  mechanism?: string;
  tags?: RawPeriodCoreTag[];
}

export interface RawPeriodStory {
  title?: string;
  lead?: string;
  big_picture?: string;
  mechanism?: string;
  contribution?: string;
  upper_meaning?: string;
}

export interface RawEventCardTags {
  duration?: string;
  phase?: string;
  domain?: string;
  intensity?: number;
  exact_in_days?: number;
}

export interface RawEventCardTiming {
  entry_date_utc?: string;
  peak_date_utc?: string;
  exit_date_utc?: string;
  timing_note?: string;
}

export interface RawEventCard {
  event_id?: string;
  headline?: string;
  opening?: string;
  essence?: string;
  asks?: string;
  watchout?: string;
  what_it_builds?: string;
  technical_note?: string;
  title?: string;
  signature?: string;
  signature_tr?: string;
  teaser?: string;
  big_picture?: string;
  mechanism?: string;
  horizon?: TimingHorizon | string;
  tone?: string;
  section_labels?: Record<string, string>;
  why_now?: string;
  conflict?: string;
  shadow?: string;
  upper?: string;
  extra_line?: string;
  time_hint?: string;
  time_hint_tr?: string;
  guidance?: string[];
  watch_out?: string[];
  hook_tags?: string[];
  tags?: RawEventCardTags;
  timing?: RawEventCardTiming;
  derived_context?: Record<string, unknown>;
  scene?: Record<string, unknown>;
  narrative_provenance?: Record<string, unknown>;
  period_story?: RawPeriodStory;
  story_track_id?: string;
}

export interface RawPeriodPeakTimelineItem {
  event_id?: string;
  title?: string;
  signature_tr?: string;
  peak_date_utc?: string;
  entry_date_utc?: string;
  exit_date_utc?: string;
  bucket?: string;
  phase?: string;
  time_hint_tr?: string;
  event_card?: RawEventCard;
}

export interface RawTimelinePayload {
  date?: string;
  summary?: string;
  lines?: string[];
  dot_intensity?: number;
}

export interface RawPeriodMarker {
  id?: string;
  marker_id?: string;
  event_id?: string;
  slug?: string;
  key?: string;
  title?: string;
  label?: string;
  headline?: string;
  name?: string;
  summary?: string;
  subtitle?: string;
  description?: string;
  core_story?: string;
  range?: string;
  time_hint?: string;
  time_hint_tr?: string;
  timing?: RawEventCardTiming;
}

export interface RawPeriodTheme {
  id?: string;
  theme_id?: string;
  event_id?: string;
  label?: string;
  title?: string;
  summary?: string;
  description?: string;
  why?: string;
  note?: string;
  theme?: string;
  time_hint?: string;
  range?: string;
  phase_kind?: string;
  label_pack?: {
    short?: string;
    full?: string;
    where?: string;
  };
}

export interface RawIntentSummaryByDateRow {
  score?: number;
  rating?: number;
}

export interface RawIntentSummary {
  by_date?: Record<string, RawIntentSummaryByDateRow>;
}

export interface RawTransitNarrativePublic {
  period_core?: RawPeriodCore;
  event_cards?: RawEventCard[] | { items?: RawEventCard[]; cards?: RawEventCard[] };
  period_peak_timeline?: RawPeriodPeakTimelineItem[];
  timeline?: RawTimelinePayload;
  markers?: RawPeriodMarker[];
  period_markers?: RawPeriodMarker[];
  themes?: RawPeriodTheme[];
  intent_summary?: Record<string, RawIntentSummary>;
}

export interface RawTransitNarrativeResponse {
  blocks?: RawNarrativeBlock[];
  screens?: {
    space_hub?: RawNarrativeScreen;
    personal_transit?: RawNarrativeScreen;
    calendar_day?: RawNarrativeScreen;
    feed_snippet?: RawNarrativeScreen;
  };
  calendar?: {
    days?: RawNarrativeCalendarDay[];
  };
  public?: RawTransitNarrativePublic;
}

export interface RawSkyFeedItem {
  id?: string;
  short_title_tr?: string;
  title_tr?: string;
  summary_tr?: string;
  badge_tr?: string;
  relative_timing_tr?: string;
  tags?: string[];
}

export interface RawSkyNowResponse {
  summary_tr?: string;
  items?: RawSkyFeedItem[];
}

export interface RawBondNarrativeReadyStory {
  lived_as?: string;
  primary_domain?: string;
  secondary_domain?: string;
  surface_domain?: string;
  background_domain?: string;
}

export interface RawBondNarrative {
  blocks?: RawProfileNarrativeBlock[];
}

export interface RawBondPublic {
  scores?: Record<string, number>;
  raw_scores?: Record<string, number>;
  contextual_scores?: Record<string, number>;
  resonance_scores?: {
    partner_a?: Record<string, number>;
    partner_b?: Record<string, number>;
    relationship?: Record<string, number>;
  };
  drivers?: Record<string, string[]>;
  derived_context?: {
    partner_a_activated?: Array<{
      domain?: string;
      score?: number;
      because?: string[];
    }>;
    partner_b_activated?: Array<{
      domain?: string;
      score?: number;
      because?: string[];
    }>;
    asymmetry_notes?: string[];
  };
  synastry_imprint?: {
    headline?: string;
    summary?: string;
    theme?: string;
    lesson?: string;
    emotional_dynamic?: string;
  };
  narrative_ready?: {
    partner_a_story?: RawBondNarrativeReadyStory;
    partner_b_story?: RawBondNarrativeReadyStory;
  };
  narrative?: RawBondNarrative;
  display?: {
    aspects_lines?: { top?: string[] };
    touchpoints_lines?: string[];
  };
}

export interface RawBondResponse {
  public?: RawBondPublic;
}

export interface RawBackendVisiblePayloads {
  profile?: RawInterpretResponse;
  timing?: RawTransitNarrativeResponse;
  collective?: RawSkyNowResponse;
  bond?: RawBondResponse;
}

export interface NormalizedSemanticTags {
  energyType: EnergyType;
  moodType: MoodType;
  behavioralPattern: BehavioralPattern;
  mentalPattern: MentalPattern;
  emotionalPattern: EmotionalPattern;
  expressionPattern: ExpressionPattern;
  relationalPattern: RelationalPattern;
  tensionPattern: TensionPattern;
  archetype: Archetype;
  dominantDomains: DomainKey[];
  activeDomains: DomainKey[];
  bundleTypes: NarrativeV2BundleType[];
  intensityBand: IntensityBand;
  timingPhase: TimingPhase;
  collectiveActivation: 'none' | 'possible' | 'active';
}

export interface VisualTokens {
  densityLevel: DensityLevel;
  contrastLevel: ContrastLevel;
  structureLevel: StructureLevel;
  directionality: Directionality;
  speed: VisualSpeed;
  cohesion: CohesionLevel;
  clarity: ClarityLevel;
  weight: WeightLevel;
  whitespaceMode: WhitespaceMode;
  typographyMode: TypographyMode;
  ornamentLevel: OrnamentLevel;
  socialDensity: SocialDensity;
}

export interface LayoutHints {
  heroMode: 'statement' | 'staged' | 'signal_led';
  narrativeMode: 'chaptered' | 'panel_led' | 'modular';
  sectionSpacing: 'tight' | 'balanced' | 'airy';
  ctaMode: 'single_primary' | 'primary_inline_mix' | 'secondary_led';
  socialMode: 'compact_topic' | 'balanced_topic' | 'dense_topic';
  utilityMode: 'divider_rows' | 'tight_rows' | 'timeline_rows';
  emphasisOrder: LayoutEmphasis[];
  allowIllustrationBreak: boolean;
}

export interface IllustrationSlotInput {
  slot: IllustrationSectionSlot;
  sectionType: SurfaceFamily;
  emphasis: LayoutEmphasis;
  energyFamily: EnergyType;
  moodFamily: MoodType;
  shapeFamily: ShapeFamily;
  motionFamily: MotionFamily;
  density: DensityLevel;
  contrast: ContrastLevel;
  archetype: Archetype;
}

export interface VisualAdapterResult {
  normalizedTags: NormalizedSemanticTags;
  visualTokens: VisualTokens;
  layoutHints: LayoutHints;
  illustrationSlots: Record<IllustrationSectionSlot, IllustrationSlotInput>;
}

export interface LayoutRhythmInput {
  layer:
    | 'identity_core'
    | 'identity_summary'
    | 'personality_imprint'
    | 'profile_narrative'
    | 'haritam_section'
    | 'timing_feature'
    | 'timing_support'
    | 'collective_topic'
    | 'thread_body'
    | 'bond_summary'
    | 'bond_detail'
    | 'share_object'
    | 'utility_item'
    | 'transition_bridge';
  prominence: 'primary' | 'secondary' | 'supporting';
  contentLength: 'short' | 'medium' | 'long';
  hasSocialActions: boolean;
  hasMeta: boolean;
  hasIllustrationOpportunity: boolean;
  tags: NormalizedSemanticTags;
  tokens: VisualTokens;
}

export interface IllustrationSelection {
  assetId: string;
  opacity: number;
  scale: number;
  alignX: number;
  alignY: number;
}
