enum BondType {
  romantic('Romantic', 'romantic'),
  friendship('Friendship', 'friendship'),
  work('Work', 'work');

  const BondType(this.label, this.backendValue);

  final String label;
  final String backendValue;
}
