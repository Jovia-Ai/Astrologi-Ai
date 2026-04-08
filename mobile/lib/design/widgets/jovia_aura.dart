import 'dart:ui';

import 'package:flutter/material.dart';

import 'package:mobile/design/tokens/profile_tokens.dart';

enum JoviaAuraElement { fire, earth, air, water }

enum JoviaAuraSemanticFamily {
  ember,
  grounded,
  lucid,
  protective,
  tender,
  magnetic,
  expansive,
  electric,
  mist,
}

@immutable
class JoviaAuraSemantic {
  const JoviaAuraSemantic({
    required this.family,
    required this.displayLabel,
    required this.sourceLabel,
    required this.auraText,
  });

  final JoviaAuraSemanticFamily family;
  final String displayLabel;
  final String sourceLabel;
  final String auraText;
}

@immutable
class JoviaAuraPalette {
  const JoviaAuraPalette({
    required this.element,
    required this.label,
    required this.core,
    required this.mid,
    required this.outer,
    required this.glow,
    required this.ring,
    required this.spark,
  });

  final JoviaAuraElement element;
  final String label;
  final Color core;
  final Color mid;
  final Color outer;
  final Color glow;
  final Color ring;
  final Color spark;
}

JoviaAuraElement joviaAuraElementForBirthDate(
  String birthDate, {
  String? seedText,
}) {
  final sign = _zodiacSignForBirthDate(birthDate);
  if (sign != null) {
    switch (sign) {
      case _ZodiacSign.aries:
      case _ZodiacSign.leo:
      case _ZodiacSign.sagittarius:
        return JoviaAuraElement.fire;
      case _ZodiacSign.taurus:
      case _ZodiacSign.virgo:
      case _ZodiacSign.capricorn:
        return JoviaAuraElement.earth;
      case _ZodiacSign.gemini:
      case _ZodiacSign.libra:
      case _ZodiacSign.aquarius:
        return JoviaAuraElement.air;
      case _ZodiacSign.cancer:
      case _ZodiacSign.scorpio:
      case _ZodiacSign.pisces:
        return JoviaAuraElement.water;
    }
  }

  switch (_stableSeed(seedText ?? birthDate) % 4) {
    case 0:
      return JoviaAuraElement.fire;
    case 1:
      return JoviaAuraElement.earth;
    case 2:
      return JoviaAuraElement.air;
    default:
      return JoviaAuraElement.water;
  }
}

JoviaAuraPalette joviaAuraPaletteForBirthData({
  required ProfileColors colors,
  required String birthDate,
  String? birthTime,
  String? seedText,
}) {
  final sign = _zodiacSignForBirthDate(birthDate);
  final seed = _stableSeed('$birthDate|${birthTime ?? ''}|${seedText ?? ''}');
  final element = joviaAuraElementForBirthDate(birthDate, seedText: seedText);

  switch (sign) {
    case _ZodiacSign.aries:
      return _palette(
        element: element,
        label: 'Ates tonu',
        core: const Color(0xFFFF8C71),
        mid: colors.warmAccent,
        outer: const Color(0xFFFFC0A8),
        glow: const Color(0xFFFF7E88),
        ring: const Color(0xFFFFF4D6),
      );
    case _ZodiacSign.taurus:
      return _palette(
        element: element,
        label: 'Toprak tonu',
        core: const Color(0xFF9ED39E),
        mid: colors.lime,
        outer: const Color(0xFFE8F3BA),
        glow: const Color(0xFFC5E2B7),
        ring: const Color(0xFFFFF8D8),
      );
    case _ZodiacSign.gemini:
      return _palette(
        element: element,
        label: 'Hava tonu',
        core: const Color(0xFF9FCBFF),
        mid: const Color(0xFFB8F5FF),
        outer: colors.primary,
        glow: const Color(0xFF8EDBFF),
        ring: const Color(0xFFF6F6FF),
      );
    case _ZodiacSign.cancer:
      return _palette(
        element: element,
        label: 'Su tonu',
        core: const Color(0xFFFFA6C8),
        mid: const Color(0xFF9DD8FF),
        outer: colors.lavender,
        glow: const Color(0xFFC4CAFF),
        ring: const Color(0xFFFFF8FF),
      );
    case _ZodiacSign.leo:
      return _palette(
        element: element,
        label: 'Ates tonu',
        core: const Color(0xFFFFD86B),
        mid: colors.warmAccent,
        outer: const Color(0xFFFFB37E),
        glow: const Color(0xFFFFAE66),
        ring: const Color(0xFFFFF8DA),
      );
    case _ZodiacSign.virgo:
      return _palette(
        element: element,
        label: 'Toprak tonu',
        core: const Color(0xFFB5D99D),
        mid: const Color(0xFFE7F6C4),
        outer: const Color(0xFFF5F3D7),
        glow: const Color(0xFFDCECBF),
        ring: const Color(0xFFFFFFFF),
      );
    case _ZodiacSign.libra:
      return _palette(
        element: element,
        label: 'Hava tonu',
        core: const Color(0xFFFFA0C7),
        mid: colors.lavender,
        outer: const Color(0xFFFFD8E7),
        glow: const Color(0xFFD6C3FF),
        ring: const Color(0xFFFFF8FF),
      );
    case _ZodiacSign.scorpio:
      return _palette(
        element: element,
        label: 'Su tonu',
        core: const Color(0xFFF45CA4),
        mid: const Color(0xFF7E7BD7),
        outer: const Color(0xFFFFBDD7),
        glow: const Color(0xFF9F7BFF),
        ring: const Color(0xFFFFE8F3),
      );
    case _ZodiacSign.sagittarius:
      return _palette(
        element: element,
        label: 'Ates tonu',
        core: const Color(0xFFFFA56B),
        mid: const Color(0xFF8EE6FF),
        outer: const Color(0xFFFFE2AE),
        glow: const Color(0xFFFF8E86),
        ring: const Color(0xFFFFF7DC),
      );
    case _ZodiacSign.capricorn:
      return _palette(
        element: element,
        label: 'Toprak tonu',
        core: const Color(0xFF93A0B4),
        mid: const Color(0xFFD3D9C7),
        outer: const Color(0xFFF2EDDA),
        glow: const Color(0xFFBFC8BB),
        ring: const Color(0xFFFFFFFF),
      );
    case _ZodiacSign.aquarius:
      return _palette(
        element: element,
        label: 'Hava tonu',
        core: const Color(0xFF7FDBFF),
        mid: colors.neonCyan,
        outer: const Color(0xFFB9E9FF),
        glow: const Color(0xFF8DE0FF),
        ring: const Color(0xFFF3FBFF),
      );
    case _ZodiacSign.pisces:
      return _palette(
        element: element,
        label: 'Su tonu',
        core: const Color(0xFFA7D9FF),
        mid: const Color(0xFFFFBCE8),
        outer: const Color(0xFFD7CCFF),
        glow: const Color(0xFF8FD9F5),
        ring: const Color(0xFFFFF5FF),
      );
    case null:
      switch (seed % 4) {
        case 0:
          return _palette(
            element: JoviaAuraElement.fire,
            label: 'Ates tonu',
            core: const Color(0xFFFFA17D),
            mid: colors.warmAccent,
            outer: const Color(0xFFFFD0B5),
            glow: const Color(0xFFFF8F99),
            ring: const Color(0xFFFFF6DE),
          );
        case 1:
          return _palette(
            element: JoviaAuraElement.earth,
            label: 'Toprak tonu',
            core: const Color(0xFFB4D199),
            mid: colors.lime,
            outer: const Color(0xFFEAF0C2),
            glow: const Color(0xFFD2E5B6),
            ring: const Color(0xFFFFFFFF),
          );
        case 2:
          return _palette(
            element: JoviaAuraElement.air,
            label: 'Hava tonu',
            core: const Color(0xFFA8CBFF),
            mid: const Color(0xFFBEF4FF),
            outer: colors.primary,
            glow: const Color(0xFFA6D3FF),
            ring: const Color(0xFFF8FAFF),
          );
        default:
          return _palette(
            element: JoviaAuraElement.water,
            label: 'Su tonu',
            core: const Color(0xFFFFAED4),
            mid: const Color(0xFFA6D8FF),
            outer: colors.lavender,
            glow: const Color(0xFFBBC4FF),
            ring: const Color(0xFFFFF7FF),
          );
      }
  }
}

JoviaAuraSemantic? joviaAuraSemanticFromText({
  required String auraText,
  String sourceLabel = '',
}) {
  final normalizedAura = auraText.trim();
  if (normalizedAura.isEmpty) {
    return null;
  }
  final family = _classifySemanticFamily(
    text: normalizedAura,
    sourceLabel: sourceLabel,
  );
  return JoviaAuraSemantic(
    family: family,
    displayLabel: _semanticDisplayLabel(family),
    sourceLabel: sourceLabel.trim(),
    auraText: normalizedAura,
  );
}

JoviaAuraPalette joviaAuraPaletteForSemantic({
  required ProfileColors colors,
  required JoviaAuraSemantic semantic,
}) {
  switch (semantic.family) {
    case JoviaAuraSemanticFamily.ember:
      return _palette(
        element: JoviaAuraElement.fire,
        label: semantic.displayLabel,
        core: const Color(0xFFFF9B6B),
        mid: colors.warmAccent,
        outer: const Color(0xFFFFD3A9),
        glow: const Color(0xFFFF8A8A),
        ring: const Color(0xFFFFF4D8),
      );
    case JoviaAuraSemanticFamily.grounded:
      return _palette(
        element: JoviaAuraElement.earth,
        label: semantic.displayLabel,
        core: const Color(0xFFA3C08F),
        mid: const Color(0xFFD5E2B7),
        outer: const Color(0xFFF2ECD8),
        glow: const Color(0xFFC6D6AD),
        ring: const Color(0xFFFFFFFF),
      );
    case JoviaAuraSemanticFamily.lucid:
      return _palette(
        element: JoviaAuraElement.air,
        label: semantic.displayLabel,
        core: const Color(0xFFA8CCFF),
        mid: const Color(0xFFB8F4FF),
        outer: colors.primary,
        glow: const Color(0xFF97D6FF),
        ring: const Color(0xFFF7FAFF),
      );
    case JoviaAuraSemanticFamily.protective:
      return _palette(
        element: JoviaAuraElement.water,
        label: semantic.displayLabel,
        core: const Color(0xFFFFB4C5),
        mid: const Color(0xFFA9DFFF),
        outer: const Color(0xFFE8DFFF),
        glow: const Color(0xFFBDD3FF),
        ring: const Color(0xFFFFF8FF),
      );
    case JoviaAuraSemanticFamily.tender:
      return _palette(
        element: JoviaAuraElement.air,
        label: semantic.displayLabel,
        core: const Color(0xFFFFA9CF),
        mid: const Color(0xFFFFD7E8),
        outer: colors.lavender,
        glow: const Color(0xFFFFC6DA),
        ring: const Color(0xFFFFFAFF),
      );
    case JoviaAuraSemanticFamily.magnetic:
      return _palette(
        element: JoviaAuraElement.water,
        label: semantic.displayLabel,
        core: const Color(0xFFF25FA6),
        mid: const Color(0xFF8D7BE8),
        outer: const Color(0xFFFFC1DD),
        glow: const Color(0xFF9B74FF),
        ring: const Color(0xFFFFEBF6),
      );
    case JoviaAuraSemanticFamily.expansive:
      return _palette(
        element: JoviaAuraElement.fire,
        label: semantic.displayLabel,
        core: const Color(0xFF7FE0FF),
        mid: const Color(0xFFFFE28C),
        outer: const Color(0xFFC7F2FF),
        glow: const Color(0xFFFFC46D),
        ring: const Color(0xFFFFF7E0),
      );
    case JoviaAuraSemanticFamily.electric:
      return _palette(
        element: JoviaAuraElement.air,
        label: semantic.displayLabel,
        core: const Color(0xFF7FE5FF),
        mid: const Color(0xFFB29DFF),
        outer: const Color(0xFFC9EEFF),
        glow: const Color(0xFF8BE3FF),
        ring: const Color(0xFFF3FBFF),
      );
    case JoviaAuraSemanticFamily.mist:
      return _palette(
        element: JoviaAuraElement.water,
        label: semantic.displayLabel,
        core: const Color(0xFFC6C8FF),
        mid: const Color(0xFFFFCBEA),
        outer: const Color(0xFFE9E7FF),
        glow: const Color(0xFFB9D5FF),
        ring: const Color(0xFFFFF8FF),
      );
  }
}

class JoviaAuraOrb extends StatelessWidget {
  const JoviaAuraOrb({
    super.key,
    required this.palette,
    this.size = 48,
    this.monogram,
    this.showSparkles = true,
  });

  final JoviaAuraPalette palette;
  final double size;
  final String? monogram;
  final bool showSparkles;

  @override
  Widget build(BuildContext context) {
    final label = (monogram ?? '').trim();
    final ringWidth = (size * 0.04).clamp(1.1, 2.4);
    final textSize = size * 0.24;

    return SizedBox(
      width: size,
      height: size,
      child: Stack(
        clipBehavior: Clip.none,
        alignment: Alignment.center,
        children: [
          Positioned.fill(
            child: ImageFiltered(
              imageFilter: ImageFilter.blur(
                sigmaX: size * 0.18,
                sigmaY: size * 0.18,
              ),
              child: DecoratedBox(
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  gradient: RadialGradient(
                    colors: [
                      palette.glow.withValues(alpha: 0.5),
                      palette.glow.withValues(alpha: 0),
                    ],
                    stops: const [0, 1],
                  ),
                ),
              ),
            ),
          ),
          DecoratedBox(
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              border: Border.all(
                color: palette.ring.withValues(alpha: 0.78),
                width: ringWidth,
              ),
              gradient: RadialGradient(
                center: const Alignment(-0.18, -0.22),
                colors: [
                  palette.ring.withValues(alpha: 0.92),
                  palette.mid.withValues(alpha: 0.94),
                  palette.outer.withValues(alpha: 0.78),
                  palette.glow.withValues(alpha: 0.1),
                ],
                stops: const [0, 0.42, 0.78, 1],
              ),
              boxShadow: [
                BoxShadow(
                  color: palette.glow.withValues(alpha: 0.28),
                  blurRadius: size * 0.36,
                  spreadRadius: size * 0.04,
                ),
              ],
            ),
            child: SizedBox(width: size, height: size),
          ),
          Container(
            width: size * 0.62,
            height: size * 0.62,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: RadialGradient(
                colors: [
                  Colors.white.withValues(alpha: 0.92),
                  palette.core.withValues(alpha: 0.96),
                  palette.core.withValues(alpha: 0.1),
                ],
                stops: const [0, 0.44, 1],
              ),
            ),
          ),
          Container(
            width: size * 0.28,
            height: size * 0.28,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: RadialGradient(
                colors: [
                  Colors.white.withValues(alpha: 0.98),
                  palette.spark.withValues(alpha: 0.76),
                  palette.spark.withValues(alpha: 0),
                ],
                stops: const [0, 0.42, 1],
              ),
            ),
          ),
          if (showSparkles) ...[
            Positioned(
              top: size * 0.16,
              right: size * 0.18,
              child: _AuraSpark(color: palette.ring, size: size * 0.08),
            ),
            Positioned(
              left: size * 0.16,
              bottom: size * 0.22,
              child: _AuraSpark(
                color: palette.spark.withValues(alpha: 0.86),
                size: size * 0.06,
              ),
            ),
          ],
          if (label.isNotEmpty)
            Text(
              _firstSymbol(label),
              style: TextStyle(
                color: Colors.white.withValues(alpha: 0.92),
                fontWeight: FontWeight.w700,
                fontSize: textSize,
                letterSpacing: 0.2,
              ),
            ),
        ],
      ),
    );
  }
}

class _AuraSpark extends StatelessWidget {
  const _AuraSpark({required this.color, required this.size});

  final Color color;
  final double size;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: color,
        boxShadow: [
          BoxShadow(
            color: color.withValues(alpha: 0.4),
            blurRadius: size * 1.8,
            spreadRadius: size * 0.12,
          ),
        ],
      ),
    );
  }
}

JoviaAuraPalette _palette({
  required JoviaAuraElement element,
  required String label,
  required Color core,
  required Color mid,
  required Color outer,
  required Color glow,
  required Color ring,
}) {
  return JoviaAuraPalette(
    element: element,
    label: label,
    core: core,
    mid: mid,
    outer: outer,
    glow: glow,
    ring: ring,
    spark: Color.alphaBlend(
      Colors.white.withValues(alpha: 0.38),
      core.withValues(alpha: 0.9),
    ),
  );
}

int _stableSeed(String value) {
  var hash = 23;
  for (final unit in value.codeUnits) {
    hash = (hash * 37 + unit) & 0x7fffffff;
  }
  return hash;
}

JoviaAuraSemanticFamily _classifySemanticFamily({
  required String text,
  required String sourceLabel,
}) {
  final normalized = _normalizeSemanticText('$sourceLabel $text');

  if (_containsAny(normalized, const <String>[
    'elektrik',
    'ozgun',
    'siradisi',
    'ongorulemez',
    'farkli',
    'ozgurluk',
    'kaliba girmeyen',
  ])) {
    return JoviaAuraSemanticFamily.electric;
  }

  if (_containsAny(normalized, const <String>[
    'bugulu',
    'sezgisel',
    'zor tarif',
    'ince',
    'siirsel',
    'buyulu',
    'ruhsal',
    'gizemli',
  ])) {
    return JoviaAuraSemanticFamily.mist;
  }

  if (_containsAny(normalized, const <String>[
    'koruyucu',
    'besleyen',
    'duygusal',
    'sefkat',
    'hisseden',
    'icten',
    'buyur eden',
  ])) {
    return JoviaAuraSemanticFamily.protective;
  }

  if (_containsAny(normalized, const <String>[
    'zarif',
    'hos',
    'yumusak',
    'cekicilik',
    'romantik',
    'tatli',
    'hosluk',
  ])) {
    return JoviaAuraSemanticFamily.tender;
  }

  if (_containsAny(normalized, const <String>[
    'guven veren',
    'saglam',
    'kontrollu',
    'dayanikli',
    'agirbasli',
    'koklu',
    'omurga',
    'sakin',
  ])) {
    return JoviaAuraSemanticFamily.grounded;
  }

  if (_containsAny(normalized, const <String>[
    'merakli',
    'zihinsel',
    'zihnin',
    'dusuncen',
    'kelimelerini',
    'iletisim',
    'baglanti',
    'kivrak',
  ])) {
    return JoviaAuraSemanticFamily.lucid;
  }

  if (_containsAny(normalized, const <String>[
    'alan acan',
    'buyuten',
    'ufuk',
    'genis',
    'acilan',
    'gelecege',
    'umut',
    'buyume',
  ])) {
    return JoviaAuraSemanticFamily.expansive;
  }

  if (_containsAny(normalized, const <String>[
    'yogun',
    'derin',
    'manyetik',
    'unutulmayan',
    'etkisi altina',
    'mahrem',
    'kolay kayitsiz',
  ])) {
    return JoviaAuraSemanticFamily.magnetic;
  }

  return JoviaAuraSemanticFamily.ember;
}

String _semanticDisplayLabel(JoviaAuraSemanticFamily family) {
  return switch (family) {
    JoviaAuraSemanticFamily.ember => 'Kivilcim aura',
    JoviaAuraSemanticFamily.grounded => 'Koklu denge',
    JoviaAuraSemanticFamily.lucid => 'Berrak zihin',
    JoviaAuraSemanticFamily.protective => 'Koruyucu dalga',
    JoviaAuraSemanticFamily.tender => 'Yumusak cekim',
    JoviaAuraSemanticFamily.magnetic => 'Manyetik alan',
    JoviaAuraSemanticFamily.expansive => 'Acilan ufuk',
    JoviaAuraSemanticFamily.electric => 'Elektrik cizgi',
    JoviaAuraSemanticFamily.mist => 'Sisli sezgi',
  };
}

String _normalizeSemanticText(String value) {
  return value
      .toLowerCase()
      .replaceAll('ı', 'i')
      .replaceAll('ğ', 'g')
      .replaceAll('ş', 's')
      .replaceAll('ö', 'o')
      .replaceAll('ü', 'u')
      .replaceAll('ç', 'c')
      .replaceAll('â', 'a')
      .replaceAll('î', 'i')
      .replaceAll('û', 'u')
      .replaceAll(RegExp(r'\s+'), ' ')
      .trim();
}

bool _containsAny(String text, List<String> needles) {
  for (final needle in needles) {
    if (text.contains(needle)) {
      return true;
    }
  }
  return false;
}

String _firstSymbol(String text) {
  return text.runes.isEmpty ? '' : String.fromCharCode(text.runes.first);
}

_ZodiacSign? _zodiacSignForBirthDate(String birthDate) {
  final parts = birthDate.trim().split('-');
  if (parts.length != 3) {
    return null;
  }

  final month = int.tryParse(parts[1]);
  final day = int.tryParse(parts[2]);
  if (month == null || day == null) {
    return null;
  }

  switch (month) {
    case 1:
      return day >= 20 ? _ZodiacSign.aquarius : _ZodiacSign.capricorn;
    case 2:
      return day >= 19 ? _ZodiacSign.pisces : _ZodiacSign.aquarius;
    case 3:
      return day >= 21 ? _ZodiacSign.aries : _ZodiacSign.pisces;
    case 4:
      return day >= 20 ? _ZodiacSign.taurus : _ZodiacSign.aries;
    case 5:
      return day >= 21 ? _ZodiacSign.gemini : _ZodiacSign.taurus;
    case 6:
      return day >= 21 ? _ZodiacSign.cancer : _ZodiacSign.gemini;
    case 7:
      return day >= 23 ? _ZodiacSign.leo : _ZodiacSign.cancer;
    case 8:
      return day >= 23 ? _ZodiacSign.virgo : _ZodiacSign.leo;
    case 9:
      return day >= 23 ? _ZodiacSign.libra : _ZodiacSign.virgo;
    case 10:
      return day >= 23 ? _ZodiacSign.scorpio : _ZodiacSign.libra;
    case 11:
      return day >= 22 ? _ZodiacSign.sagittarius : _ZodiacSign.scorpio;
    case 12:
      return day >= 22 ? _ZodiacSign.capricorn : _ZodiacSign.sagittarius;
    default:
      return null;
  }
}

enum _ZodiacSign {
  aries,
  taurus,
  gemini,
  cancer,
  leo,
  virgo,
  libra,
  scorpio,
  sagittarius,
  capricorn,
  aquarius,
  pisces,
}
