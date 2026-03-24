class UserProfile {
  final String userId; // uuid string
  final String name;
  final String birthDate; // YYYY-MM-DD
  final String birthTime; // HH:mm
  final String city;
  final String country;

  const UserProfile({
    required this.userId,
    required this.name,
    required this.birthDate,
    required this.birthTime,
    required this.city,
    required this.country,
  });

  Map<String, dynamic> toMap() => {
    'user_id': userId,
    'name': name,
    'birth_date': birthDate,
    'birth_time': birthTime,
    'city': city,
    'country': country,
  };

  static UserProfile fromMap(Map<String, dynamic> map) => UserProfile(
    userId: (map['user_id'] ?? '').toString(),
    name: (map['name'] ?? '').toString(),
    birthDate: (map['birth_date'] ?? '').toString(),
    birthTime: (map['birth_time'] ?? '').toString(),
    city: (map['city'] ?? '').toString(),
    country: (map['country'] ?? '').toString(),
  );
}

class NarrativeV2AspectBundle {
  const NarrativeV2AspectBundle({
    required this.bundleId,
    required this.bundleType,
    required this.score,
    required this.domains,
    required this.recognitionTags,
    required this.giftTags,
    required this.reflexTags,
  });

  final String bundleId;
  final String bundleType;
  final double score;
  final List<String> domains;
  final List<String> recognitionTags;
  final List<String> giftTags;
  final List<String> reflexTags;

  bool get hasContent =>
      recognitionTags.isNotEmpty ||
      giftTags.isNotEmpty ||
      reflexTags.isNotEmpty;

  factory NarrativeV2AspectBundle.fromMap(Map<String, dynamic> map) {
    List<String> readList(String key) {
      final raw = map[key];
      if (raw is! List) {
        return const <String>[];
      }
      return raw
          .map((item) => item.toString().trim())
          .where((item) => item.isNotEmpty)
          .toList();
    }

    double readScore() {
      final raw = map['score'];
      if (raw is num) {
        return raw.toDouble();
      }
      return double.tryParse(raw?.toString() ?? '') ?? 0.0;
    }

    return NarrativeV2AspectBundle(
      bundleId: (map['bundle_id'] ?? '').toString().trim(),
      bundleType: (map['bundle_type'] ?? '').toString().trim(),
      score: readScore(),
      domains: readList('domains'),
      recognitionTags: readList('recognition_tags'),
      giftTags: readList('gift_tags'),
      reflexTags: readList('reflex_tags'),
    );
  }
}

class NarrativeV2Profile {
  const NarrativeV2Profile({
    required this.contractVersion,
    required this.bundles,
  });

  final String contractVersion;
  final List<NarrativeV2AspectBundle> bundles;

  bool get hasContent => bundles.any((item) => item.hasContent);

  factory NarrativeV2Profile.fromMap(Map<String, dynamic> map) {
    final selector = map['aspect_bundle_selector'];
    final selectorMap = selector is Map<String, dynamic>
        ? selector
        : selector is Map
        ? Map<String, dynamic>.from(selector)
        : const <String, dynamic>{};
    final selectedRaw = selectorMap['selected_bundles'];
    final bundles = selectedRaw is List
        ? selectedRaw
              .whereType<Map>()
              .map(
                (item) => NarrativeV2AspectBundle.fromMap(
                  Map<String, dynamic>.from(item),
                ),
              )
              .where((item) => item.hasContent)
              .toList()
        : const <NarrativeV2AspectBundle>[];
    return NarrativeV2Profile(
      contractVersion: (map['contract_version'] ?? '').toString().trim(),
      bundles: bundles,
    );
  }
}

class ProfileNarrativeBlock {
  const ProfileNarrativeBlock({
    required this.id,
    required this.headline,
    required this.teaser,
    required this.subtitle,
    required this.body,
    required this.micro,
    required this.astroHint,
    required this.astroSources,
    required this.chips,
  });

  final String id;
  final String headline;
  final String teaser;
  final String subtitle;
  final String body;
  final String micro;
  final String astroHint;
  final List<String> astroSources;
  final List<String> chips;

  String get previewText {
    final candidate = subtitle.trim().isNotEmpty
        ? subtitle.trim()
        : teaser.trim();
    return candidate;
  }

  bool get hasContent =>
      headline.trim().isNotEmpty ||
      teaser.trim().isNotEmpty ||
      subtitle.trim().isNotEmpty ||
      body.trim().isNotEmpty ||
      micro.trim().isNotEmpty;

  factory ProfileNarrativeBlock.fromMap(Map<String, dynamic> map) {
    final chipsRaw = map['chips'];
    return ProfileNarrativeBlock(
      id: (map['id'] ?? '').toString().trim(),
      headline: (map['headline'] ?? '').toString().trim(),
      teaser: (map['teaser'] ?? '').toString().trim(),
      subtitle: (map['subtitle'] ?? '').toString().trim(),
      body: (map['body'] ?? '').toString().trim(),
      micro: (map['micro'] ?? '').toString().trim(),
      astroHint: (map['astro_hint'] ?? '').toString().trim(),
      astroSources: map['astro_sources'] is List
          ? (map['astro_sources'] as List)
                .map((item) => item.toString().trim())
                .where((item) => item.isNotEmpty)
                .toList()
          : const <String>[],
      chips: chipsRaw is List
          ? chipsRaw
                .map((item) => item.toString().trim())
                .where((item) => item.isNotEmpty)
                .toList()
          : const <String>[],
    );
  }
}

class PersonalityImprintEntry {
  const PersonalityImprintEntry({
    required this.key,
    required this.kind,
    required this.labelTr,
    required this.tags,
    required this.aura,
    required this.trait,
    required this.drive,
    required this.shadow,
    required this.backgroundHint,
    required this.gift,
    required this.supportKeys,
  });

  final String key;
  final String kind;
  final String labelTr;
  final List<String> tags;
  final String aura;
  final String trait;
  final String drive;
  final String shadow;
  final String backgroundHint;
  final String gift;
  final List<String> supportKeys;

  bool get hasContent =>
      labelTr.trim().isNotEmpty ||
      aura.trim().isNotEmpty ||
      trait.trim().isNotEmpty ||
      drive.trim().isNotEmpty ||
      shadow.trim().isNotEmpty ||
      backgroundHint.trim().isNotEmpty ||
      gift.trim().isNotEmpty;

  factory PersonalityImprintEntry.fromMap(Map<String, dynamic> map) {
    List<String> readList(String key) {
      final raw = map[key];
      if (raw is! List) {
        return const <String>[];
      }
      return raw
          .map((item) => item.toString().trim())
          .where((item) => item.isNotEmpty)
          .toList();
    }

    return PersonalityImprintEntry(
      key: (map['key'] ?? '').toString().trim(),
      kind: (map['kind'] ?? '').toString().trim(),
      labelTr: (map['label_tr'] ?? '').toString().trim(),
      tags: readList('tags'),
      aura: (map['aura'] ?? '').toString().trim(),
      trait: (map['trait'] ?? '').toString().trim(),
      drive: (map['drive'] ?? '').toString().trim(),
      shadow: (map['shadow'] ?? '').toString().trim(),
      backgroundHint: (map['background_hint'] ?? '').toString().trim(),
      gift: (map['gift'] ?? '').toString().trim(),
      supportKeys: readList('support_keys'),
    );
  }
}

class PersonalityImprintBundle {
  const PersonalityImprintBundle({
    required this.id,
    required this.dominantKey,
    required this.dominantKind,
    required this.relatedPlanets,
    required this.supportKeys,
  });

  final String id;
  final String dominantKey;
  final String dominantKind;
  final List<String> relatedPlanets;
  final List<String> supportKeys;

  bool get hasContent => dominantKey.trim().isNotEmpty;

  factory PersonalityImprintBundle.fromMap(Map<String, dynamic> map) {
    List<String> readList(String key) {
      final raw = map[key];
      if (raw is! List) {
        return const <String>[];
      }
      return raw
          .map((item) => item.toString().trim())
          .where((item) => item.isNotEmpty)
          .toList();
    }

    return PersonalityImprintBundle(
      id: (map['id'] ?? '').toString().trim(),
      dominantKey: (map['dominant_key'] ?? '').toString().trim(),
      dominantKind: (map['dominant_kind'] ?? '').toString().trim(),
      relatedPlanets: readList('related_planets'),
      supportKeys: readList('support_keys'),
    );
  }
}

class PersonalityImprintProfile {
  const PersonalityImprintProfile({
    required this.engineVersion,
    required this.libraryVersion,
    required this.locale,
    required this.headline,
    required this.renderShape,
    required this.entries,
    required this.extraEntries,
    required this.supportEntries,
    required this.bundles,
    required this.extraBundles,
  });

  final String engineVersion;
  final String libraryVersion;
  final String locale;
  final String headline;
  final Map<String, dynamic> renderShape;
  final List<PersonalityImprintEntry> entries;
  final List<PersonalityImprintEntry> extraEntries;
  final List<PersonalityImprintEntry> supportEntries;
  final List<PersonalityImprintBundle> bundles;
  final List<PersonalityImprintBundle> extraBundles;

  bool get hasContent => entries.any((item) => item.hasContent);
  bool get hasExtraContent => extraEntries.any((item) => item.hasContent);

  factory PersonalityImprintProfile.fromMap(Map<String, dynamic> map) {
    List<PersonalityImprintEntry> readEntries(String key) {
      final raw = map[key];
      if (raw is! List) {
        return const <PersonalityImprintEntry>[];
      }
      return raw
          .whereType<Map>()
          .map(
            (item) => PersonalityImprintEntry.fromMap(
              Map<String, dynamic>.from(item),
            ),
          )
          .where((item) => item.hasContent)
          .toList();
    }

    final bundlesRaw = map['bundles'];
    final bundles = bundlesRaw is List
        ? bundlesRaw
              .whereType<Map>()
              .map(
                (item) => PersonalityImprintBundle.fromMap(
                  Map<String, dynamic>.from(item),
                ),
              )
              .where((item) => item.hasContent)
              .toList()
        : const <PersonalityImprintBundle>[];

    return PersonalityImprintProfile(
      engineVersion: (map['engine_version'] ?? '').toString().trim(),
      libraryVersion: (map['library_version'] ?? '').toString().trim(),
      locale: (map['locale'] ?? 'tr').toString().trim(),
      headline: (map['headline'] ?? '').toString().trim(),
      renderShape: map['render_shape'] is Map<String, dynamic>
          ? Map<String, dynamic>.from(
              map['render_shape'] as Map<String, dynamic>,
            )
          : map['render_shape'] is Map
          ? Map<String, dynamic>.from(map['render_shape'] as Map)
          : const <String, dynamic>{},
      entries: readEntries('entries'),
      extraEntries: readEntries('extra_entries'),
      supportEntries: readEntries('support_entries'),
      bundles: bundles,
      extraBundles: map['extra_bundles'] is List
          ? (map['extra_bundles'] as List)
                .whereType<Map>()
                .map(
                  (item) => PersonalityImprintBundle.fromMap(
                    Map<String, dynamic>.from(item),
                  ),
                )
                .where((item) => item.hasContent)
                .toList()
          : const <PersonalityImprintBundle>[],
    );
  }
}

class ProfileInsightAstroSource {
  const ProfileInsightAstroSource({required this.primary, required this.value});

  final String primary;
  final String value;

  bool get hasContent => primary.trim().isNotEmpty || value.trim().isNotEmpty;

  factory ProfileInsightAstroSource.fromMap(Map<String, dynamic> map) {
    return ProfileInsightAstroSource(
      primary: (map['primary'] ?? '').toString().trim(),
      value: (map['value'] ?? '').toString().trim(),
    );
  }
}

class ProfileInsightContent {
  const ProfileInsightContent({
    required this.title,
    required this.body,
    required this.shareText,
    required this.tone,
  });

  final String title;
  final String body;
  final String shareText;
  final String tone;

  bool get hasContent =>
      title.trim().isNotEmpty ||
      body.trim().isNotEmpty ||
      shareText.trim().isNotEmpty;

  factory ProfileInsightContent.fromMap(Map<String, dynamic> map) {
    return ProfileInsightContent(
      title: (map['title'] ?? '').toString().trim(),
      body: (map['body'] ?? '').toString().trim(),
      shareText: (map['share_text'] ?? '').toString().trim(),
      tone: (map['tone'] ?? '').toString().trim(),
    );
  }
}

class ProfileInsightMeta {
  const ProfileInsightMeta({
    required this.visibility,
    required this.priority,
    required this.expandable,
    required this.version,
  });

  final String visibility;
  final int priority;
  final bool expandable;
  final String version;

  factory ProfileInsightMeta.fromMap(Map<String, dynamic> map) {
    final rawPriority = map['priority'];
    return ProfileInsightMeta(
      visibility: (map['visibility'] ?? '').toString().trim(),
      priority: rawPriority is num
          ? rawPriority.toInt()
          : int.tryParse(rawPriority?.toString() ?? '') ?? 999,
      expandable: map['expandable'] == true,
      version: (map['version'] ?? '').toString().trim(),
    );
  }
}

class ProfileInsightModule {
  const ProfileInsightModule({
    required this.moduleId,
    required this.type,
    required this.headline,
    required this.subheadline,
    required this.moonSign,
    required this.title,
    required this.body,
    required this.tone,
    required this.shareText,
    required this.priority,
    required this.astroSource,
    required this.content,
    required this.meta,
  });

  final String moduleId;
  final String type;
  final String headline;
  final String subheadline;
  final String moonSign;
  final String title;
  final String body;
  final String tone;
  final String shareText;
  final int priority;
  final ProfileInsightAstroSource astroSource;
  final ProfileInsightContent content;
  final ProfileInsightMeta meta;

  bool get hasContent =>
      headline.trim().isNotEmpty &&
      resolvedTitle.isNotEmpty &&
      resolvedBody.isNotEmpty;

  String get resolvedTitle =>
      title.trim().isNotEmpty ? title.trim() : content.title.trim();

  String get resolvedBody =>
      body.trim().isNotEmpty ? body.trim() : content.body.trim();

  String get resolvedShareText =>
      shareText.trim().isNotEmpty ? shareText.trim() : content.shareText.trim();

  int get resolvedPriority => priority >= 0 ? priority : meta.priority;

  factory ProfileInsightModule.fromMap(Map<String, dynamic> map) {
    final astroSourceRaw = map['astro_source'];
    final contentRaw = map['content'];
    final metaRaw = map['meta'];
    final content = contentRaw is Map<String, dynamic>
        ? ProfileInsightContent.fromMap(contentRaw)
        : contentRaw is Map
        ? ProfileInsightContent.fromMap(Map<String, dynamic>.from(contentRaw))
        : const ProfileInsightContent(
            title: '',
            body: '',
            shareText: '',
            tone: '',
          );
    final meta = metaRaw is Map<String, dynamic>
        ? ProfileInsightMeta.fromMap(metaRaw)
        : metaRaw is Map
        ? ProfileInsightMeta.fromMap(Map<String, dynamic>.from(metaRaw))
        : const ProfileInsightMeta(
            visibility: '',
            priority: 999,
            expandable: false,
            version: '',
          );
    final rawPriority = map['priority'];

    return ProfileInsightModule(
      moduleId: (map['module_id'] ?? '').toString().trim(),
      type: (map['type'] ?? '').toString().trim(),
      headline: (map['headline'] ?? '').toString().trim(),
      subheadline: (map['subheadline'] ?? '').toString().trim(),
      moonSign: (map['moon_sign'] ?? '').toString().trim(),
      title: (map['title'] ?? content.title).toString().trim(),
      body: (map['body'] ?? content.body).toString().trim(),
      tone: (map['tone'] ?? content.tone).toString().trim(),
      shareText: (map['share_text'] ?? content.shareText).toString().trim(),
      priority: rawPriority is num
          ? rawPriority.toInt()
          : int.tryParse(rawPriority?.toString() ?? '') ?? meta.priority,
      astroSource: astroSourceRaw is Map<String, dynamic>
          ? ProfileInsightAstroSource.fromMap(astroSourceRaw)
          : astroSourceRaw is Map
          ? ProfileInsightAstroSource.fromMap(
              Map<String, dynamic>.from(astroSourceRaw),
            )
          : const ProfileInsightAstroSource(primary: '', value: ''),
      content: content,
      meta: meta,
    );
  }
}
