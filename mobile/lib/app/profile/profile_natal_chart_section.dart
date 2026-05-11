import 'package:flutter/material.dart';

import 'package:mobile/app/chart/chart_wheel_data.dart';
import 'package:mobile/app/chart/chart_wheel_repository.dart';
import 'package:mobile/design/theme/profile_theme_extension.dart';
import 'package:mobile/design/widgets/jovia_editorial.dart';
import 'package:mobile/design/widgets/shou_chart_wheel.dart';

class ProfileNatalChartSection extends StatefulWidget {
  const ProfileNatalChartSection({
    super.key,
    required this.profile,
    required this.subtitle,
    this.payload,
  });

  final Map<String, dynamic>? profile;
  final Map<String, dynamic>? payload;
  final String subtitle;

  @override
  State<ProfileNatalChartSection> createState() =>
      _ProfileNatalChartSectionState();
}

class _ProfileNatalChartSectionState extends State<ProfileNatalChartSection> {
  final ChartWheelRepository _repository = ChartWheelRepository();

  Future<ChartWheelData?>? _future;
  String? _requestKey;

  @override
  void initState() {
    super.initState();
    _refreshFuture(allowSetState: false);
  }

  @override
  void didUpdateWidget(covariant ProfileNatalChartSection oldWidget) {
    super.didUpdateWidget(oldWidget);
    _refreshFuture();
  }

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Haritalarım',
            style: profile.typography.section.copyWith(
              color: profile.colors.text,
              fontSize: 26,
              height: 1.12,
            ),
          ),
          const SizedBox(height: 12),
          FutureBuilder<ChartWheelData?>(
            future: _future,
            builder: (context, snapshot) {
              final data = snapshot.data;
              final isLoading =
                  snapshot.connectionState == ConnectionState.waiting;
              final canOpen = data != null;
              final subtitle = widget.subtitle.trim().isNotEmpty
                  ? widget.subtitle.trim()
                  : 'Güneş, Ay ve yükselen bilgileri burada görünecek.';

              return GestureDetector(
                onTap: canOpen ? () => _openDetailSheet(context, data) : null,
                child: JoviaSurfaceCard(
                  radius: 30,
                  backgroundColor: profile.colors.surface,
                  borderColor: profile.colors.strokeSoft,
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 10,
                              vertical: 6,
                            ),
                            decoration: BoxDecoration(
                              color: Color.alphaBlend(
                                profile.colors.brandLime.withValues(
                                  alpha: 0.16,
                                ),
                                profile.colors.surface,
                              ),
                              borderRadius: BorderRadius.circular(999),
                              border: Border.all(
                                color: profile.colors.strokeSoft,
                              ),
                            ),
                            child: Text(
                              'NATAL HARITAN',
                              style: profile.typography.eyebrow.copyWith(
                                color: profile.colors.text,
                                fontSize: 10,
                                letterSpacing: 1.4,
                              ),
                            ),
                          ),
                          const Spacer(),
                          _ChartStatusPill(
                            label: isLoading
                                ? 'Hazırlanıyor'
                                : canOpen
                                ? 'Hazır'
                                : 'Bekleniyor',
                            accent: isLoading || canOpen
                                ? profile.colors.brandLime
                                : profile.colors.lavender,
                          ),
                        ],
                      ),
                      const SizedBox(height: 18),
                      Center(
                        child: SizedBox.square(
                          dimension: 220,
                          child: switch ((isLoading, data != null)) {
                            (true, _) => _ChartWheelLoadingState(
                              accent: profile.colors.brandLime,
                              stroke: profile.colors.strokeSoft,
                              textColor: profile.colors.muted,
                            ),
                            (_, true) => ShouChartWheel(
                              data: data!,
                              mode: ChartWheelMode.profilePreview,
                            ),
                            _ => _ChartWheelFallbackState(
                              stroke: profile.colors.strokeSoft,
                              textColor: profile.colors.muted,
                            ),
                          },
                        ),
                      ),
                      const SizedBox(height: 20),
                      Text(
                        'Natal Haritan',
                        style: profile.typography.card.copyWith(
                          color: profile.colors.text,
                          fontSize: 22,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        canOpen
                            ? subtitle
                            : _fallbackCopy(
                                hasBirthData: _hasBirthData(widget.profile),
                              ),
                        style: profile.typography.body.copyWith(
                          color: profile.colors.muted,
                          height: 1.55,
                        ),
                      ),
                      const SizedBox(height: 16),
                      Align(
                        alignment: Alignment.centerRight,
                        child: _ChartActionButton(
                          label: canOpen
                              ? 'Haritayı aç'
                              : isLoading
                              ? 'Harita hazırlanıyor'
                              : 'Veri bekleniyor',
                          enabled: canOpen,
                        ),
                      ),
                    ],
                  ),
                ),
              );
            },
          ),
        ],
      ),
    );
  }

  void _refreshFuture({bool allowSetState = true}) {
    final direct = ChartWheelData.tryFromInterpretPayload(widget.payload);
    final nextKey =
        '${_birthKey(widget.profile)}|direct:${direct != null ? 1 : 0}';
    if (nextKey == _requestKey) {
      return;
    }
    _requestKey = nextKey;
    _future = direct != null
        ? Future<ChartWheelData?>.value(direct)
        : _hasBirthData(widget.profile)
        ? _repository.fetch(profile: widget.profile!)
        : Future<ChartWheelData?>.value(null);
    if (allowSetState && mounted) {
      setState(() {});
    }
  }

  Future<void> _openDetailSheet(
    BuildContext context,
    ChartWheelData? data,
  ) async {
    if (data == null) {
      return;
    }
    final profile = context.profileTheme;
    final subtitle = widget.subtitle.trim();
    await showModalBottomSheet<void>(
      context: context,
      backgroundColor: Colors.transparent,
      isScrollControlled: true,
      builder: (sheetContext) {
        final sheetProfile = sheetContext.profileTheme;
        final height = MediaQuery.of(sheetContext).size.height * 0.9;
        return Padding(
          padding: EdgeInsets.fromLTRB(
            profile.spacing.lg,
            profile.spacing.lg,
            profile.spacing.lg,
            MediaQuery.of(sheetContext).viewInsets.bottom + profile.spacing.lg,
          ),
          child: ConstrainedBox(
            constraints: BoxConstraints(maxHeight: height),
            child: JoviaSurfaceCard(
              radius: 32,
              backgroundColor: sheetProfile.colors.surface,
              borderColor: sheetProfile.colors.strokeSoft,
              child: SingleChildScrollView(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Haritalarım',
                                style: sheetProfile.typography.eyebrow.copyWith(
                                  color: sheetProfile.colors.brandLime,
                                  letterSpacing: 1.4,
                                ),
                              ),
                              const SizedBox(height: 8),
                              Text(
                                'Natal Haritan',
                                style: sheetProfile.typography.section.copyWith(
                                  color: sheetProfile.colors.text,
                                  fontSize: 30,
                                  height: 1.08,
                                ),
                              ),
                              if (subtitle.isNotEmpty) ...[
                                const SizedBox(height: 8),
                                Text(
                                  subtitle,
                                  style: sheetProfile.typography.meta.copyWith(
                                    color: sheetProfile.colors.muted,
                                    height: 1.45,
                                  ),
                                ),
                              ],
                            ],
                          ),
                        ),
                        IconButton(
                          onPressed: () =>
                              Navigator.of(sheetContext).maybePop(),
                          icon: const Icon(Icons.close_rounded),
                        ),
                      ],
                    ),
                    const SizedBox(height: 20),
                    Center(
                      child: SizedBox.square(
                        dimension: 340,
                        child: ShouChartWheel(
                          data: data,
                          mode: ChartWheelMode.fullDetail,
                        ),
                      ),
                    ),
                    const SizedBox(height: 20),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: [
                        _DetailChip(
                          label:
                              'ASC · ${_signLabelForLongitude(data.ascDegree)}',
                        ),
                        _DetailChip(
                          label:
                              'MC · ${_signLabelForLongitude(data.mcDegree)}',
                        ),
                        for (final planet in _sortedPlanets(data.planets))
                          _DetailChip(label: _planetDetailLabel(planet)),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ),
        );
      },
    );
  }
}

class _ChartActionButton extends StatelessWidget {
  const _ChartActionButton({required this.label, required this.enabled});

  final String label;
  final bool enabled;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return DecoratedBox(
      decoration: BoxDecoration(
        color: enabled
            ? profile.colors.brandLime
            : profile.colors.lavender.withValues(alpha: 0.7),
        borderRadius: BorderRadius.circular(999),
      ),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        child: Text(
          label,
          style: profile.typography.buttonLabel.copyWith(
            color: enabled ? const Color(0xFF1A3300) : profile.colors.muted,
          ),
        ),
      ),
    );
  }
}

class _ChartStatusPill extends StatelessWidget {
  const _ChartStatusPill({required this.label, required this.accent});

  final String label;
  final Color accent;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return DecoratedBox(
      decoration: BoxDecoration(
        color: accent.withValues(alpha: 0.16),
        borderRadius: BorderRadius.circular(999),
      ),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
        child: Text(
          label,
          style: profile.typography.meta.copyWith(
            color: profile.colors.text,
            fontSize: 12,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
    );
  }
}

class _ChartWheelLoadingState extends StatelessWidget {
  const _ChartWheelLoadingState({
    required this.accent,
    required this.stroke,
    required this.textColor,
  });

  final Color accent;
  final Color stroke;
  final Color textColor;

  @override
  Widget build(BuildContext context) {
    return Stack(
      alignment: Alignment.center,
      children: [
        _ChartWheelFallbackState(stroke: stroke, textColor: textColor),
        SizedBox(
          width: 30,
          height: 30,
          child: CircularProgressIndicator(strokeWidth: 2.2, color: accent),
        ),
      ],
    );
  }
}

class _ChartWheelFallbackState extends StatelessWidget {
  const _ChartWheelFallbackState({
    required this.stroke,
    required this.textColor,
  });

  final Color stroke;
  final Color textColor;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return DecoratedBox(
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        border: Border.all(color: stroke),
      ),
      child: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.auto_awesome_rounded, color: textColor, size: 28),
            const SizedBox(height: 10),
            Text(
              'Harita bekleniyor',
              style: profile.typography.meta.copyWith(
                color: textColor,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _DetailChip extends StatelessWidget {
  const _DetailChip({required this.label});

  final String label;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return DecoratedBox(
      decoration: BoxDecoration(
        color: Color.alphaBlend(
          profile.colors.lavender.withValues(alpha: 0.32),
          profile.colors.surface,
        ),
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: profile.colors.strokeSoft),
      ),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 9),
        child: Text(
          label,
          style: profile.typography.chipLabel.copyWith(
            color: profile.colors.text,
          ),
        ),
      ),
    );
  }
}

bool _hasBirthData(Map<String, dynamic>? profile) {
  if (profile == null) {
    return false;
  }
  final birthDate = (profile['birth_date'] ?? '').toString().trim();
  final birthTime = (profile['birth_time'] ?? '').toString().trim();
  return birthDate.isNotEmpty &&
      birthTime.isNotEmpty &&
      _placeLabel(profile).isNotEmpty;
}

String _birthKey(Map<String, dynamic>? profile) {
  if (profile == null) {
    return 'empty';
  }
  return [
    (profile['birth_date'] ?? '').toString().trim(),
    (profile['birth_time'] ?? '').toString().trim(),
    _placeLabel(profile),
    (profile['timezone'] ?? '').toString().trim(),
  ].join('|');
}

String _placeLabel(Map<String, dynamic>? profile) {
  final place = (profile?['place'] ?? '').toString().trim();
  if (place.isNotEmpty) {
    return place;
  }
  final city = (profile?['city'] ?? '').toString().trim();
  final country = (profile?['country'] ?? '').toString().trim();
  if (city.isEmpty) {
    return country;
  }
  if (country.isEmpty) {
    return city;
  }
  return '$city, $country';
}

String _fallbackCopy({required bool hasBirthData}) {
  if (!hasBirthData) {
    return 'Natal harita için doğum tarihi, saat ve yer bilgisi gerekiyor.';
  }
  return 'Harita verisi hazırlanırken profil akışı çalışmaya devam eder.';
}

List<ChartPlanetPoint> _sortedPlanets(List<ChartPlanetPoint> planets) {
  const order = <String, int>{
    'sun': 0,
    'moon': 1,
    'mercury': 2,
    'venus': 3,
    'mars': 4,
    'jupiter': 5,
    'saturn': 6,
    'uranus': 7,
    'neptune': 8,
    'pluto': 9,
    'north_node': 10,
    'south_node': 11,
    'chiron': 12,
    'lilith': 13,
    'fortune': 14,
    'vertex': 15,
  };
  final copy = [...planets];
  copy.sort((a, b) {
    final aOrder = order[a.id] ?? 99;
    final bOrder = order[b.id] ?? 99;
    if (aOrder != bOrder) {
      return aOrder.compareTo(bOrder);
    }
    return a.longitude.compareTo(b.longitude);
  });
  return copy;
}

String _planetDetailLabel(ChartPlanetPoint planet) {
  final house = planet.house == null ? '' : ' · ${planet.house}. ev';
  final retro = planet.retrograde ? ' · R' : '';
  return '${_planetTitle(planet.id)} · ${_trSign(planet.sign)}$house$retro';
}

String _planetTitle(String id) {
  return switch (id) {
    'sun' => 'Güneş',
    'moon' => 'Ay',
    'mercury' => 'Merkür',
    'venus' => 'Venüs',
    'mars' => 'Mars',
    'jupiter' => 'Jüpiter',
    'saturn' => 'Satürn',
    'uranus' => 'Uranüs',
    'neptune' => 'Neptün',
    'pluto' => 'Plüton',
    'north_node' => 'Kuzey Ay Düğümü',
    'south_node' => 'Güney Ay Düğümü',
    'chiron' => 'Kiron',
    'lilith' => 'Lilith',
    'fortune' => 'Fortuna',
    'vertex' => 'Vertex',
    _ => id,
  };
}

String _signLabelForLongitude(double longitude) {
  const signs = <String>[
    'Koç',
    'Boğa',
    'İkizler',
    'Yengeç',
    'Aslan',
    'Başak',
    'Terazi',
    'Akrep',
    'Yay',
    'Oğlak',
    'Kova',
    'Balık',
  ];
  final normalized = longitude % 360;
  final index = ((normalized < 0 ? normalized + 360 : normalized) ~/ 30) % 12;
  return signs[index];
}

String _trSign(String sign) {
  final normalized = sign.trim().toLowerCase();
  return switch (normalized) {
    'aries' || 'koç' || 'koc' => 'Koç',
    'taurus' || 'boğa' || 'boga' => 'Boğa',
    'gemini' || 'ikizler' => 'İkizler',
    'cancer' || 'yengeç' || 'yengec' => 'Yengeç',
    'leo' || 'aslan' => 'Aslan',
    'virgo' || 'başak' || 'basak' => 'Başak',
    'libra' || 'terazi' => 'Terazi',
    'scorpio' || 'akrep' => 'Akrep',
    'sagittarius' || 'yay' => 'Yay',
    'capricorn' || 'oğlak' || 'oglak' => 'Oğlak',
    'aquarius' || 'kova' => 'Kova',
    'pisces' || 'balık' || 'balik' => 'Balık',
    _ => sign.trim(),
  };
}
