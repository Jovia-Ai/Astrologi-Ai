class SupabaseTables {
  const SupabaseTables._();

  static const String profiles = 'profiles';
  static const String birthData = 'birth_data';

  static const String peopleProfiles = 'people_profiles';
  static const String people = 'people';
  static const String savedPeople = 'saved_people';

  static const List<String> peopleCandidates = <String>[
    peopleProfiles,
    people,
    savedPeople,
    profiles,
  ];
}
