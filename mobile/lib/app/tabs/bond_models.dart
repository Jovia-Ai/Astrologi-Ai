enum BondType {
  romantic('Romantic Connection', 'romantic'),
  friendship('Friendship', 'friendship'),
  work('Work / Collaboration', 'work');

  const BondType(this.label, this.backendValue);

  final String label;
  final String backendValue;
}
