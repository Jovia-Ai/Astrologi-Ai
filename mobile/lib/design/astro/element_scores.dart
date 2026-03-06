enum AstroElement { fire, water, air, earth }

class ElementScores {
  const ElementScores({
    required this.fire,
    required this.water,
    required this.air,
    required this.earth,
  });

  final double fire;
  final double water;
  final double air;
  final double earth;

  AstroElement get dominant {
    final values = <AstroElement, double>{
      AstroElement.fire: fire,
      AstroElement.water: water,
      AstroElement.air: air,
      AstroElement.earth: earth,
    };
    var winner = AstroElement.fire;
    var max = -1.0;
    for (final entry in values.entries) {
      if (entry.value > max) {
        max = entry.value;
        winner = entry.key;
      }
    }
    return winner;
  }

  ElementScores normalize() {
    final total = fire + water + air + earth;
    if (total <= 0) {
      return const ElementScores(
        fire: 0.25,
        water: 0.25,
        air: 0.25,
        earth: 0.25,
      );
    }
    return ElementScores(
      fire: fire / total,
      water: water / total,
      air: air / total,
      earth: earth / total,
    );
  }

  static ElementScores fromMap(Map<String, dynamic> map) {
    final f = _asDouble(map['fire']);
    final w = _asDouble(map['water']);
    final a = _asDouble(map['air']);
    final e = _asDouble(map['earth']);
    return ElementScores(fire: f, water: w, air: a, earth: e).normalize();
  }
}

double _asDouble(dynamic value) {
  if (value is num) {
    return value.toDouble();
  }
  if (value is String) {
    return double.tryParse(value) ?? 0;
  }
  return 0;
}
