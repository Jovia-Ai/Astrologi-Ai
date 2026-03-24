import {
  DOMAIN_KEYS,
  NARRATIVE_V2_BUNDLE_TYPES,
  TIMING_PHASES,
  type Archetype,
  type BehavioralPattern,
  type ClarityLevel,
  type ContrastLevel,
  type CohesionLevel,
  type DensityLevel,
  type Directionality,
  type DomainKey,
  type EnergyType,
  type EmotionalPattern,
  type ExpressionPattern,
  type IllustrationSectionSlot,
  type IllustrationSlotInput,
  type IntensityBand,
  type LayoutHints,
  type LayoutEmphasis,
  type MentalPattern,
  type MoodType,
  type MotionFamily,
  type NarrativeV2BundleType,
  type NormalizedSemanticTags,
  type RawBackendVisiblePayloads,
  type RawEventCard,
  type RawInterpretResponse,
  type RawSkyFeedItem,
  type RawTransitNarrativeResponse,
  type RelationalPattern,
  type ShapeFamily,
  type SocialDensity,
  type StructureLevel,
  type SurfaceFamily,
  type TensionPattern,
  type TimingPhase,
  type TypographyMode,
  type VisualAdapterResult,
  type VisualSpeed,
  type VisualTokens,
  type WeightLevel,
  type WhitespaceMode,
} from './normalized_interpretation_schema';

type ElementCountMap = Record<'earth' | 'fire' | 'air' | 'water', number>;

interface AdapterFacts {
  elementCounts: ElementCountMap;
  dominantDomains: DomainKey[];
  activeDomains: DomainKey[];
  bundleTypes: Set<string>;
  contradictionCount: number;
  pressureCount: number;
  emotionalBundleCount: number;
  mentalBundleCount: number;
  relationalBundleCount: number;
  identityBundleCount: number;
  primaryEventIntensity: number;
  highestEventIntensity: number;
  timingPhase: TimingPhase;
  risingCollectiveTopics: number;
  activeCollectiveTopics: number;
  collectiveItemsCount: number;
  bondAsymmetryCount: number;
  triggerLoad: number;
  sustainableBond: number;
  magneticIntensity: number;
  saturnWeight: number;
  neptuneWeight: number;
  outwardDomainWeight: number;
  inwardDomainWeight: number;
}

const SIGN_TO_ELEMENT: Record<string, 'earth' | 'fire' | 'air' | 'water'> = {
  aries: 'fire',
  taurus: 'earth',
  gemini: 'air',
  cancer: 'water',
  leo: 'fire',
  virgo: 'earth',
  libra: 'air',
  scorpio: 'water',
  sagittarius: 'fire',
  capricorn: 'earth',
  aquarius: 'air',
  pisces: 'water',
};

const RISING_SIGN_TO_RULER: Record<string, string> = {
  aries: 'Mars',
  taurus: 'Venus',
  gemini: 'Mercury',
  cancer: 'Moon',
  leo: 'Sun',
  virgo: 'Mercury',
  libra: 'Venus',
  scorpio: 'Pluto',
  sagittarius: 'Jupiter',
  capricorn: 'Saturn',
  aquarius: 'Uranus',
  pisces: 'Neptune',
};

const INWARD_DOMAINS: DomainKey[] = [
  'identity',
  'intimacy_depth',
  'home_roots',
  'private_inner_world',
];

const OUTWARD_DOMAINS: DomainKey[] = [
  'career_visibility',
  'creativity_talent',
  'social_future',
  'mind_communication',
];

export function adaptBackendPayloadsToVisualSystem(
  payloads: RawBackendVisiblePayloads,
): VisualAdapterResult {
  const facts = deriveFacts(payloads);
  const normalizedTags = deriveNormalizedTags(facts);
  const visualTokens = deriveVisualTokens(facts, normalizedTags);
  const layoutHints = deriveLayoutHints(normalizedTags, visualTokens);
  const illustrationSlots = buildIllustrationSlots(
    normalizedTags,
    visualTokens,
  );

  return {
    normalizedTags,
    visualTokens,
    layoutHints,
    illustrationSlots,
  };
}

function deriveFacts(payloads: RawBackendVisiblePayloads): AdapterFacts {
  const placements = collectPlacements(payloads.profile);
  const elementCounts = countElements(placements);
  const domains = collectDomains(payloads);
  const bundleTypes = collectBundleTypes(payloads.profile);
  const timingCards = collectEventCards(payloads.timing);
  const collectiveItems = payloads.collective?.items ?? [];
  const risingSign = extractRisingSign(payloads.profile);
  const chartRuler = RISING_SIGN_TO_RULER[normalizeKey(risingSign)] ?? '';
  const scoreMap = payloads.bond?.public?.scores ?? {};

  return {
    elementCounts,
    dominantDomains: domains.slice(0, 3),
    activeDomains: domains,
    bundleTypes,
    contradictionCount: bundleTypes.has('contradiction_bundle') ? 1 : 0,
    pressureCount: bundleTypes.has('pressure_growth_bundle') ? 1 : 0,
    emotionalBundleCount: bundleTypes.has('emotional_regulation_bundle') ? 1 : 0,
    mentalBundleCount: bundleTypes.has('mental_style_bundle') ? 1 : 0,
    relationalBundleCount: bundleTypes.has('relational_pattern_bundle') ? 1 : 0,
    identityBundleCount: bundleTypes.has('angle_identity_bundle') ? 1 : 0,
    primaryEventIntensity: timingCards[0]?.tags?.intensity ?? 0,
    highestEventIntensity: timingCards.reduce<number>(
      (max, card) => Math.max(max, card.tags?.intensity ?? 0),
      0,
    ),
    timingPhase: normalizeTimingPhase(timingCards[0]?.tags?.phase),
    risingCollectiveTopics: collectiveItems.filter(isRisingCollectiveItem).length,
    activeCollectiveTopics: collectiveItems.filter(isChartActiveCollectiveItem).length,
    collectiveItemsCount: collectiveItems.length,
    bondAsymmetryCount:
      payloads.bond?.public?.derived_context?.asymmetry_notes?.length ?? 0,
    triggerLoad: readNumber(scoreMap.trigger_load),
    sustainableBond: readNumber(scoreMap.sustainable_bond),
    magneticIntensity: readNumber(scoreMap.magnetic_intensity),
    saturnWeight: computePlanetWeight(placements, 'saturn', chartRuler),
    neptuneWeight: computePlanetWeight(placements, 'neptune', chartRuler),
    outwardDomainWeight: domains.filter((domain) =>
      OUTWARD_DOMAINS.includes(domain),
    ).length,
    inwardDomainWeight: domains.filter((domain) =>
      INWARD_DOMAINS.includes(domain),
    ).length,
  };
}

function deriveNormalizedTags(facts: AdapterFacts): NormalizedSemanticTags {
  const energyType = deriveEnergyType(facts);
  const moodType = deriveMoodType(facts, energyType);
  const behavioralPattern = deriveBehavioralPattern(facts, energyType);
  const mentalPattern = deriveMentalPattern(facts, energyType);
  const emotionalPattern = deriveEmotionalPattern(facts, energyType);
  const expressionPattern = deriveExpressionPattern(facts, energyType);
  const relationalPattern = deriveRelationalPattern(facts);
  const tensionPattern = deriveTensionPattern(facts);
  const archetype = deriveArchetype({
    energyType,
    moodType,
    behavioralPattern,
    tensionPattern,
  });

  return {
    energyType,
    moodType,
    behavioralPattern,
    mentalPattern,
    emotionalPattern,
    expressionPattern,
    relationalPattern,
    tensionPattern,
    archetype,
    dominantDomains: facts.dominantDomains,
    activeDomains: facts.activeDomains,
    bundleTypes: [...facts.bundleTypes].filter(isNarrativeV2BundleType),
    intensityBand: bandFromNumber(facts.highestEventIntensity, [0.34, 0.67]),
    timingPhase: facts.timingPhase,
    collectiveActivation:
      facts.activeCollectiveTopics > 0
        ? 'active'
        : facts.collectiveItemsCount > 0
        ? 'possible'
        : 'none',
  };
}

function deriveVisualTokens(
  facts: AdapterFacts,
  tags: NormalizedSemanticTags,
): VisualTokens {
  const densityScore =
    facts.activeDomains.length +
    facts.contradictionCount +
    facts.pressureCount +
    (facts.highestEventIntensity >= 0.67 ? 1 : 0);
  const contrastScore =
    facts.contradictionCount +
    (facts.bondAsymmetryCount > 0 ? 1 : 0) +
    (facts.triggerLoad >= 0.67 ? 1 : 0) +
    (facts.magneticIntensity >= 0.67 ? 1 : 0);

  const densityLevel = densityScore >= 5 ? 'high' : densityScore >= 3 ? 'medium' : 'low';
  const contrastLevel =
    contrastScore >= 3 ? 'high' : contrastScore >= 1 ? 'medium' : 'soft';

  const structureLevel: StructureLevel =
    facts.saturnWeight >= 2 || tags.energyType === 'earth'
      ? 'structured'
      : facts.neptuneWeight >= 2 || tags.energyType === 'water'
      ? 'fluid'
      : 'balanced';

  const directionality: Directionality =
    facts.outwardDomainWeight > facts.inwardDomainWeight
      ? 'outward'
      : facts.outwardDomainWeight < facts.inwardDomainWeight
      ? 'inward'
      : 'balanced';

  const speed: VisualSpeed =
    tags.timingPhase === 'peak' || tags.timingPhase === 'exact'
      ? 'fast'
      : tags.timingPhase === 'applying'
      ? 'steady'
      : tags.timingPhase === 'waning' || tags.timingPhase === 'receding'
      ? 'slow'
      : tags.tensionPattern === 'inner_split'
      ? 'oscillating'
      : 'steady';

  const cohesion: CohesionLevel =
    facts.contradictionCount > 0 || facts.bondAsymmetryCount > 1
      ? facts.activeDomains.length >= 4
        ? 'fragmented'
        : 'tensioned'
      : 'cohesive';

  const clarity: ClarityLevel =
    structureLevel === 'structured' && contrastLevel !== 'high'
      ? 'clear'
      : facts.neptuneWeight >= 2 || tags.moodType === 'ambiguous'
      ? 'ambiguous'
      : 'mixed';

  const weight: WeightLevel =
    tags.energyType === 'earth' || facts.saturnWeight >= 2
      ? 'grounded'
      : tags.energyType === 'fire' && contrastLevel === 'high'
      ? 'heavy'
      : 'light';

  const whitespaceMode: WhitespaceMode =
    densityLevel === 'high'
      ? 'compressed'
      : tags.archetype === 'observer' || tags.archetype === 'container'
      ? 'breathing'
      : 'balanced';

  const typographyMode: TypographyMode =
    structureLevel === 'structured'
      ? 'technical'
      : tags.archetype === 'amplifier' || tags.archetype === 'mirror'
      ? 'editorial'
      : 'balanced';

  const ornamentLevel =
    contrastLevel === 'high'
      ? 'medium'
      : tags.archetype === 'observer' || tags.archetype === 'distiller'
      ? 'low'
      : 'medium';

  const socialDensity: SocialDensity =
    facts.collectiveItemsCount >= 4 || facts.risingCollectiveTopics >= 2
      ? 'busy'
      : facts.collectiveItemsCount > 0
      ? 'active'
      : 'quiet';

  return {
    densityLevel,
    contrastLevel,
    structureLevel,
    directionality,
    speed,
    cohesion,
    clarity,
    weight,
    whitespaceMode,
    typographyMode,
    ornamentLevel,
    socialDensity,
  };
}

function deriveLayoutHints(
  tags: NormalizedSemanticTags,
  tokens: VisualTokens,
): LayoutHints {
  return {
    heroMode:
      tags.archetype === 'amplifier'
        ? 'staged'
        : tokens.clarity === 'clear'
        ? 'statement'
        : 'signal_led',
    narrativeMode:
      tokens.densityLevel === 'high'
        ? 'panel_led'
        : tags.archetype === 'observer' || tags.archetype === 'container'
        ? 'chaptered'
        : 'modular',
    sectionSpacing:
      tokens.whitespaceMode === 'compressed'
        ? 'tight'
        : tokens.whitespaceMode === 'breathing'
        ? 'airy'
        : 'balanced',
    ctaMode:
      tokens.socialDensity === 'busy'
        ? 'primary_inline_mix'
        : tags.archetype === 'distiller'
        ? 'secondary_led'
        : 'single_primary',
    socialMode:
      tokens.socialDensity === 'busy'
        ? 'dense_topic'
        : tokens.socialDensity === 'active'
        ? 'balanced_topic'
        : 'compact_topic',
    utilityMode:
      tags.timingPhase === 'peak' || tags.timingPhase === 'exact'
        ? 'timeline_rows'
        : tokens.structureLevel === 'structured'
        ? 'divider_rows'
        : 'tight_rows',
    emphasisOrder: buildEmphasisOrder(tags),
    allowIllustrationBreak:
      tokens.ornamentLevel !== 'low' &&
      (tags.archetype === 'amplifier' ||
        tags.archetype === 'integrator' ||
        tokens.whitespaceMode === 'breathing'),
  };
}

function buildIllustrationSlots(
  tags: NormalizedSemanticTags,
  tokens: VisualTokens,
): Record<IllustrationSectionSlot, IllustrationSlotInput> {
  return {
    home_hero: createIllustrationSlot('home_hero', 'hero', 'timing', tags, tokens),
    profile_hero: createIllustrationSlot('profile_hero', 'hero', 'identity', tags, tokens),
    haritam_identity_overview: createIllustrationSlot(
      'haritam_identity_overview',
      'reading',
      'identity',
      tags,
      tokens,
    ),
    haritam_signature: createIllustrationSlot(
      'haritam_signature',
      'reading',
      'identity',
      tags,
      tokens,
    ),
    timing_feature: createIllustrationSlot(
      'timing_feature',
      'hero',
      'timing',
      tags,
      tokens,
    ),
    collective_topic_card: createIllustrationSlot(
      'collective_topic_card',
      'social',
      'collective',
      tags,
      tokens,
    ),
    thread_detail_header: createIllustrationSlot(
      'thread_detail_header',
      'social',
      'collective',
      tags,
      tokens,
    ),
    bond_summary: createIllustrationSlot(
      'bond_summary',
      'reading',
      'bond',
      tags,
      tokens,
    ),
    studio_share_card: createIllustrationSlot(
      'studio_share_card',
      'social',
      'share',
      tags,
      tokens,
    ),
  };
}

function createIllustrationSlot(
  slot: IllustrationSectionSlot,
  sectionType: SurfaceFamily,
  emphasis: LayoutEmphasis,
  tags: NormalizedSemanticTags,
  tokens: VisualTokens,
): IllustrationSlotInput {
  return {
    slot,
    sectionType,
    emphasis,
    energyFamily: tags.energyType,
    moodFamily: tags.moodType,
    shapeFamily: deriveShapeFamily(tags, tokens),
    motionFamily: deriveMotionFamily(tags, tokens),
    density: tokens.densityLevel,
    contrast: tokens.contrastLevel,
    archetype: tags.archetype,
  };
}

function deriveEnergyType(facts: AdapterFacts): EnergyType {
  const ordered = Object.entries(facts.elementCounts).sort((a, b) => b[1] - a[1]);
  const [topKey, topValue] = ordered[0];
  const secondValue = ordered[1]?.[1] ?? 0;
  if (topValue === 0) {
    return 'mixed';
  }
  if (topValue - secondValue <= 1) {
    return 'mixed';
  }
  return topKey as EnergyType;
}

function deriveMoodType(facts: AdapterFacts, energyType: EnergyType): MoodType {
  if (facts.neptuneWeight >= 2) {
    return 'diffuse';
  }
  if (facts.contradictionCount > 0 && energyType === 'water') {
    return 'ambiguous';
  }
  if (facts.saturnWeight >= 2 || energyType === 'earth') {
    return 'structured';
  }
  if (energyType === 'fire' && facts.highestEventIntensity >= 0.67) {
    return 'intense';
  }
  if (energyType === 'water') {
    return 'contained';
  }
  if (energyType === 'air') {
    return 'focused';
  }
  return 'calm';
}

function deriveBehavioralPattern(
  facts: AdapterFacts,
  energyType: EnergyType,
): BehavioralPattern {
  if (facts.pressureCount > 0 && energyType === 'earth') {
    return 'distiller';
  }
  if (facts.relationalBundleCount > 0) {
    return 'integrator';
  }
  if (energyType === 'fire') {
    return 'initiator';
  }
  if (energyType === 'earth') {
    return 'stabilizer';
  }
  if (energyType === 'water') {
    return 'container';
  }
  return 'observer';
}

function deriveMentalPattern(
  facts: AdapterFacts,
  energyType: EnergyType,
): MentalPattern {
  if (facts.mentalBundleCount > 0 && facts.saturnWeight >= 2) {
    return 'analytical';
  }
  if (facts.mentalBundleCount > 0 && energyType === 'air') {
    return 'synthetic';
  }
  if (facts.neptuneWeight >= 2) {
    return 'reflective';
  }
  if (energyType === 'fire') {
    return 'anticipatory';
  }
  return 'concrete';
}

function deriveEmotionalPattern(
  facts: AdapterFacts,
  energyType: EnergyType,
): EmotionalPattern {
  if (facts.emotionalBundleCount > 0 && facts.saturnWeight >= 2) {
    return 'guarded';
  }
  if (facts.emotionalBundleCount > 0 && energyType === 'water') {
    return 'deepening';
  }
  if (energyType === 'earth') {
    return 'steady';
  }
  if (energyType === 'water') {
    return 'permeable';
  }
  if (energyType === 'fire') {
    return 'expressive';
  }
  return 'contained';
}

function deriveExpressionPattern(
  facts: AdapterFacts,
  energyType: EnergyType,
): ExpressionPattern {
  if (facts.identityBundleCount > 0 && facts.saturnWeight >= 2) {
    return 'measured';
  }
  if (facts.identityBundleCount > 0 && energyType === 'fire') {
    return 'performative';
  }
  if (energyType === 'earth') {
    return 'curated';
  }
  if (energyType === 'water') {
    return 'quiet';
  }
  if (energyType === 'air') {
    return 'symbolic';
  }
  return 'direct';
}

function deriveRelationalPattern(facts: AdapterFacts): RelationalPattern {
  if (facts.bondAsymmetryCount > 0) {
    return 'negotiating';
  }
  if (facts.relationalBundleCount > 0 && facts.sustainableBond >= 0.67) {
    return 'bonding';
  }
  if (facts.relationalBundleCount > 0 && facts.triggerLoad >= 0.67) {
    return 'testing';
  }
  return facts.activeDomains.includes('relationships') ? 'mirroring' : 'autonomy_seeking';
}

function deriveTensionPattern(facts: AdapterFacts): TensionPattern {
  if (facts.bondAsymmetryCount > 0) {
    return 'asymmetry';
  }
  if (facts.contradictionCount > 0) {
    return 'inner_split';
  }
  if (facts.saturnWeight >= 2 && facts.pressureCount > 0) {
    return 'overcontrol';
  }
  if (facts.neptuneWeight >= 2) {
    return 'diffusion';
  }
  if (facts.triggerLoad >= 0.67 || facts.highestEventIntensity >= 0.8) {
    return 'intensity_spike';
  }
  return 'none';
}

function deriveArchetype(input: {
  energyType: EnergyType;
  moodType: MoodType;
  behavioralPattern: BehavioralPattern;
  tensionPattern: TensionPattern;
}): Archetype {
  if (input.tensionPattern === 'asymmetry' || input.energyType === 'fire') {
    return input.moodType === 'intense' ? 'amplifier' : 'disruptor';
  }
  if (input.behavioralPattern === 'stabilizer') {
    return 'builder';
  }
  if (input.behavioralPattern === 'distiller') {
    return 'distiller';
  }
  if (input.behavioralPattern === 'container') {
    return 'container';
  }
  if (input.behavioralPattern === 'integrator') {
    return 'integrator';
  }
  if (input.energyType === 'water') {
    return 'mirror';
  }
  return 'observer';
}

function deriveShapeFamily(
  tags: NormalizedSemanticTags,
  tokens: VisualTokens,
): ShapeFamily {
  if (tags.archetype === 'builder' || tokens.structureLevel === 'structured') {
    return 'grid';
  }
  if (tags.archetype === 'container') {
    return 'spiral';
  }
  if (tags.archetype === 'mirror') {
    return 'paired_axis';
  }
  if (tags.archetype === 'amplifier' || tokens.contrastLevel === 'high') {
    return 'burst';
  }
  if (tokens.structureLevel === 'fluid') {
    return 'wave';
  }
  if (tokens.cohesion === 'fragmented') {
    return 'fracture';
  }
  return 'orbit';
}

function deriveMotionFamily(
  tags: NormalizedSemanticTags,
  tokens: VisualTokens,
): MotionFamily {
  if (tokens.speed === 'fast') {
    return 'rise';
  }
  if (tokens.speed === 'oscillating') {
    return 'oscillate';
  }
  if (tokens.structureLevel === 'fluid') {
    return 'drift';
  }
  if (tags.archetype === 'integrator' || tags.archetype === 'mirror') {
    return 'merge';
  }
  if (tokens.cohesion === 'fragmented') {
    return 'split';
  }
  return 'still';
}

function buildEmphasisOrder(tags: NormalizedSemanticTags): LayoutEmphasis[] {
  const ordered: LayoutEmphasis[] = ['identity'];
  if (tags.collectiveActivation !== 'none') {
    ordered.push('collective');
  }
  if (tags.intensityBand !== 'low') {
    ordered.push('timing');
  }
  if (tags.relationalPattern !== 'autonomy_seeking') {
    ordered.push('bond');
  }
  ordered.push('share');
  return dedupe(ordered);
}

function collectPlacements(profile?: RawInterpretResponse) {
  if (!profile) {
    return [] as NonNullable<RawInterpretResponse['planets']>;
  }
  const scopes = [profile, profile.public, profile.meta_info].filter(Boolean);
  return scopes.flatMap((scope) => scope?.planets ?? []);
}

function collectDomains(payloads: RawBackendVisiblePayloads): DomainKey[] {
  const counts = new Map<DomainKey, number>();
  const push = (raw: string | undefined) => {
    const key = normalizeDomain(raw);
    if (!key) {
      return;
    }
    counts.set(key, (counts.get(key) ?? 0) + 1);
  };

  const scopes = [
    payloads.profile,
    payloads.profile?.public,
    payloads.profile?.meta_info,
  ].filter(Boolean);

  scopes.forEach((scope) => {
    const bundles =
      scope?.narrative_v2?.aspect_bundle_selector?.selected_bundles ?? [];
    bundles.forEach((bundle) => (bundle.domains ?? []).forEach(push));
  });

  collectEventCards(payloads.timing).forEach((card) => push(card.tags?.domain));

  const bondStories = payloads.bond?.public?.narrative_ready;
  [bondStories?.partner_a_story, bondStories?.partner_b_story].forEach((story) => {
    push(story?.primary_domain);
    push(story?.secondary_domain);
    push(story?.surface_domain);
    push(story?.background_domain);
  });

  return [...counts.entries()]
    .sort((a, b) => b[1] - a[1])
    .map(([domain]) => domain);
}

function collectBundleTypes(profile?: RawInterpretResponse): Set<string> {
  const scopes = [profile, profile?.public, profile?.meta_info].filter(Boolean);
  const bundleTypes = new Set<string>();
  scopes.forEach((scope) => {
    const bundles =
      scope?.narrative_v2?.aspect_bundle_selector?.selected_bundles ?? [];
    bundles.forEach((bundle) => {
      if (bundle.bundle_type) {
        bundleTypes.add(bundle.bundle_type);
      }
    });
  });
  return bundleTypes;
}

function collectEventCards(timing?: RawTransitNarrativeResponse): RawEventCard[] {
  const raw = timing?.public?.event_cards;
  if (!raw) {
    return [];
  }
  if (Array.isArray(raw)) {
    return raw;
  }
  return raw.items ?? raw.cards ?? [];
}

function countElements(
  placements: Array<{ sign?: string; zodiac_sign?: string }>,
): ElementCountMap {
  const counts: ElementCountMap = { earth: 0, fire: 0, air: 0, water: 0 };
  placements.forEach((placement) => {
    const sign = normalizeKey(placement.sign ?? placement.zodiac_sign ?? '');
    const element = SIGN_TO_ELEMENT[sign];
    if (element) {
      counts[element] += 1;
    }
  });
  return counts;
}

function extractRisingSign(profile?: RawInterpretResponse): string {
  if (!profile) {
    return '';
  }
  const scopes = [profile, profile.public, profile.meta_info].filter(Boolean);
  for (const scope of scopes) {
    const angles = scope?.angles;
    const direct = angles?.ascendant_sign ?? angles?.asc_sign ?? '';
    if (direct) {
      return direct;
    }
  }
  return '';
}

function computePlanetWeight(
  placements: Array<{ planet?: string; name?: string; body?: string }>,
  targetPlanet: string,
  chartRuler: string,
): number {
  let total = 0;
  placements.forEach((placement) => {
    const label = normalizeKey(
      placement.planet ?? placement.name ?? placement.body ?? '',
    );
    if (label === targetPlanet) {
      total += 1;
    }
  });
  if (normalizeKey(chartRuler) === targetPlanet) {
    total += 1;
  }
  return total;
}

function isRisingCollectiveItem(item: RawSkyFeedItem): boolean {
  const value = `${item.badge_tr ?? ''} ${item.relative_timing_tr ?? ''}`.toLowerCase();
  return value.includes('yuksel') || value.includes('peak') || value.includes('simdi');
}

function isChartActiveCollectiveItem(item: RawSkyFeedItem): boolean {
  return (item.tags ?? []).some((tag) =>
    ['identity', 'relationships', 'mind_communication', 'intimacy_depth'].includes(
      normalizeKey(tag),
    ),
  );
}

function normalizeTimingPhase(raw?: string): TimingPhase {
  const value = normalizeKey(raw ?? '');
  if ((TIMING_PHASES as readonly string[]).includes(value)) {
    return value as TimingPhase;
  }
  if (value.includes('peak') || value.includes('exact')) {
    return value.includes('peak') ? 'peak' : 'exact';
  }
  if (value.includes('apply')) {
    return 'applying';
  }
  if (value.includes('exit')) {
    return 'exit';
  }
  if (value.includes('wan')) {
    return 'waning';
  }
  if (value.includes('reced')) {
    return 'receding';
  }
  return 'unknown';
}

function normalizeDomain(raw?: string): DomainKey | null {
  const value = normalizeKey(raw ?? '');
  return (DOMAIN_KEYS as readonly string[]).includes(value)
    ? (value as DomainKey)
    : null;
}

function normalizeKey(value: string): string {
  return value.trim().toLowerCase().replace(/\s+/g, '_');
}

function bandFromNumber(
  value: number,
  [mediumThreshold, highThreshold]: [number, number],
): IntensityBand {
  if (value >= highThreshold) {
    return 'high';
  }
  if (value >= mediumThreshold) {
    return 'medium';
  }
  return 'low';
}

function readNumber(value: unknown): number {
  if (typeof value === 'number') {
    return value;
  }
  if (typeof value === 'string') {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : 0;
  }
  return 0;
}

function dedupe<T>(items: T[]): T[] {
  return [...new Set(items)];
}

function isNarrativeV2BundleType(
  value: string,
): value is NarrativeV2BundleType {
  return (NARRATIVE_V2_BUNDLE_TYPES as readonly string[]).includes(value);
}
