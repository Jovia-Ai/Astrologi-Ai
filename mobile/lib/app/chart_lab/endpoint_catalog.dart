class EndpointAction {
  const EndpointAction({
    required this.id,
    required this.label,
    required this.method,
    required this.path,
    this.templateKey,
    this.notes,
  });

  final String id;
  final String label;
  final String method;
  final String path;
  final String? templateKey;
  final String? notes;
}

const List<EndpointAction> endpointCatalog = [
  EndpointAction(
    id: 'charts.build',
    label: 'Charts: Build (Unified)',
    method: 'POST',
    path: '/api/v1/charts/build',
    templateKey: '/api/v1/charts/build',
  ),
  EndpointAction(
    id: 'natal.interpret',
    label: 'Natal: Interpret',
    method: 'POST',
    path: '/interpret',
    templateKey: '/interpret',
  ),
  EndpointAction(
    id: 'natal.interpret.ui',
    label: 'Natal: Interpret (UI)',
    method: 'POST',
    path: '/interpret/ui',
    templateKey: '/interpret/ui',
  ),
  EndpointAction(
    id: 'natal.interpret.debug',
    label: 'Natal: Interpret (Debug)',
    method: 'POST',
    path: '/interpret/debug',
    templateKey: '/interpret/debug',
  ),
  EndpointAction(
    id: 'natal.interpret.premium',
    label: 'Natal: Interpret (Premium)',
    method: 'POST',
    path: '/interpret/premium',
    templateKey: '/interpret/premium',
  ),
  EndpointAction(
    id: 'natal.interpret.premium.ui',
    label: 'Natal: Interpret (Premium UI)',
    method: 'POST',
    path: '/interpret/premium/ui',
    templateKey: '/interpret/premium/ui',
  ),
  EndpointAction(
    id: 'natal.interpret.premium.debug',
    label: 'Natal: Interpret (Premium Debug)',
    method: 'POST',
    path: '/interpret/premium/debug',
    templateKey: '/interpret/premium/debug',
  ),
  EndpointAction(
    id: 'transits.core',
    label: 'Transits: Core',
    method: 'POST',
    path: '/transits',
    templateKey: '/transits',
  ),
  EndpointAction(
    id: 'transits.debug',
    label: 'Transits: Debug',
    method: 'POST',
    path: '/transits/debug',
    templateKey: '/transits/debug',
  ),
  EndpointAction(
    id: 'transit.calendar',
    label: 'Transit: Calendar (Debug)',
    method: 'GET',
    path: '/transit/calendar/day',
    templateKey: '/transit/calendar',
  ),
  EndpointAction(
    id: 'transit.calendar.best',
    label: 'Transit: Calendar Best Times (Debug)',
    method: 'GET',
    path: '/transit/calendar/best-times',
    templateKey: '/transit/calendar/best-times',
  ),
  EndpointAction(
    id: 'transit.calendar.day',
    label: 'Transit: Calendar Day (Debug)',
    method: 'GET',
    path: '/transit/calendar/day',
    templateKey: '/transit/calendar/day',
  ),
  EndpointAction(
    id: 'transits.window',
    label: 'Transits: Window',
    method: 'POST',
    path: '/transits/window',
    templateKey: '/transits/window',
  ),
  EndpointAction(
    id: 'transits.event_timing',
    label: 'Transits: Event Timing',
    method: 'POST',
    path: '/transits/event_timing',
    templateKey: '/transits/event_timing',
  ),
  EndpointAction(
    id: 'synastry.analyze.v1',
    label: 'Synastry: Analyze (v1)',
    method: 'POST',
    path: '/api/v1/relationship/synastry/analyze',
    templateKey: '/api/v1/relationship/synastry/analyze',
  ),
  EndpointAction(
    id: 'synastry.analyze',
    label: 'Synastry: Analyze',
    method: 'POST',
    path: '/api/synastry/analyze',
    templateKey: '/api/synastry/analyze',
  ),
];
