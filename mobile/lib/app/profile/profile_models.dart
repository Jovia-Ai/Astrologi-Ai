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
