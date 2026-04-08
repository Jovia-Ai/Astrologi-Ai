class PersonProfile {
  const PersonProfile({
    required this.id,
    required this.ownerUserId,
    required this.name,
    required this.birthDate,
    this.birthTime,
    required this.city,
    required this.country,
    required this.timezone,
    required this.createdAt,
  });

  final String id;
  final String ownerUserId;
  final String name;
  final String birthDate;
  final String? birthTime;
  final String city;
  final String country;
  final String timezone;
  final DateTime createdAt;

  String get place {
    if (city.isEmpty) {
      return country;
    }
    if (country.isEmpty) {
      return city;
    }
    return '$city, $country';
  }

  String get normalizedBirthTime {
    final raw = (birthTime ?? '').trim();
    if (raw.isEmpty) {
      return '12:00';
    }
    if (raw.length >= 5) {
      return raw.substring(0, 5);
    }
    return raw;
  }

  String get auraSeedKey {
    return '$id|$name|$birthDate|${birthTime ?? ''}|$city|$country|$timezone';
  }

  String get monogram {
    final parts = name
        .trim()
        .split(RegExp(r'\s+'))
        .where((part) => part.isNotEmpty)
        .toList();
    if (parts.isEmpty) {
      return '?';
    }
    if (parts.length == 1) {
      return String.fromCharCode(parts.first.runes.first).toUpperCase();
    }
    final first = String.fromCharCode(parts.first.runes.first).toUpperCase();
    final last = String.fromCharCode(parts.last.runes.first).toUpperCase();
    return '$first$last';
  }

  Map<String, dynamic> toProfileMap() {
    return {
      'person_id': id,
      'full_name': name,
      'name': name,
      'birth_date': birthDate,
      'birth_time': normalizedBirthTime,
      'place': place,
      'city': city,
      'country': country,
      'timezone': timezone,
    };
  }

  static PersonProfile fromMap(Map<String, dynamic> map) {
    final created = DateTime.tryParse((map['created_at'] ?? '').toString());

    final resolvedName = (map['name'] ?? map['full_name'] ?? '').toString();
    final resolvedOwner =
        (map['owner_user_id'] ?? map['owner_id'] ?? map['user_id'] ?? '')
            .toString();

    return PersonProfile(
      id: (map['id'] ?? '').toString(),
      ownerUserId: resolvedOwner,
      name: resolvedName,
      birthDate: (map['birth_date'] ?? '').toString(),
      birthTime: _normalizeDbTime((map['birth_time'] ?? '').toString()),
      city: (map['city'] ?? '').toString(),
      country: (map['country'] ?? '').toString(),
      timezone: (map['timezone'] ?? 'Europe/Istanbul').toString(),
      createdAt: created ?? DateTime.fromMillisecondsSinceEpoch(0),
    );
  }

  static String? _normalizeDbTime(String raw) {
    final value = raw.trim();
    if (value.isEmpty) {
      return null;
    }
    if (value.length >= 5) {
      return value.substring(0, 5);
    }
    return value;
  }
}
