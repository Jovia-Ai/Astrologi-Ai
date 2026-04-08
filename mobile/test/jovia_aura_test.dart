import 'package:flutter_test/flutter_test.dart';

import 'package:mobile/design/tokens/profile_tokens.dart';
import 'package:mobile/design/widgets/jovia_aura.dart';

void main() {
  test('maps zodiac dates to stable aura elements', () {
    expect(joviaAuraElementForBirthDate('1996-07-27'), JoviaAuraElement.fire);
    expect(joviaAuraElementForBirthDate('1996-09-04'), JoviaAuraElement.earth);
    expect(joviaAuraElementForBirthDate('1996-02-12'), JoviaAuraElement.air);
    expect(joviaAuraElementForBirthDate('1996-11-02'), JoviaAuraElement.water);
  });

  test('returns deterministic palette for same person seed', () {
    final first = joviaAuraPaletteForBirthData(
      colors: ProfileColors.light,
      birthDate: 'not-a-date',
      birthTime: '09:15',
      seedText: 'person-1',
    );
    final second = joviaAuraPaletteForBirthData(
      colors: ProfileColors.light,
      birthDate: 'not-a-date',
      birthTime: '09:15',
      seedText: 'person-1',
    );

    expect(first.label, second.label);
    expect(first.core, second.core);
    expect(first.mid, second.mid);
    expect(first.glow, second.glow);
  });

  test('classifies backend aura text into richer semantic families', () {
    final mist = joviaAuraSemanticFromText(
      auraText:
          'Sende tam çözülemeyen, sezgisel ve biraz buğulu bir enerji var.',
      sourceLabel: 'Yukselen Balik',
    );
    final magnetic = joviaAuraSemanticFromText(
      auraText: 'Sende güçlü, yoğun ve kolay unutulmayan bir etki var.',
      sourceLabel: 'Mars Akrep',
    );
    final grounded = joviaAuraSemanticFromText(
      auraText:
          'Sende ağırbaşlı, kontrollü ve güven veren bir giriş tonu olabilir.',
      sourceLabel: 'Saturn Oglak',
    );

    expect(mist?.displayLabel, 'Sisli sezgi');
    expect(magnetic?.displayLabel, 'Manyetik alan');
    expect(grounded?.displayLabel, 'Koklu denge');
  });
}
