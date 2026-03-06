import 'dart:ui';

import 'package:flutter/material.dart';

import 'bond_models.dart';

class BondResultPage extends StatelessWidget {
  const BondResultPage({
    super.key,
    required this.response,
    required this.youName,
    required this.partnerName,
    required this.bondType,
  });

  final Map<String, dynamic> response;
  final String youName;
  final String partnerName;
  final BondType bondType;

  @override
  Widget build(BuildContext context) {
    final public = _asMap(response['public']);
    final scores = _asMap(public['scores']);
    final drivers = _asMap(public['drivers']);
    final display = _asMap(public['display']);
    final aspectsLines = _toStringList(_asMap(display['aspects_lines'])['top']);
    final touchLines = _toStringList(display['touchpoints_lines']);

    return Scaffold(
      appBar: AppBar(title: const Text('Bond Sonucu')),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(16, 16, 16, 28),
        children: [
          _GlassCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '$youName + $partnerName',
                  style: const TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  'Tür: ${bondType.label}',
                  style: const TextStyle(color: Colors.black54),
                ),
              ],
            ),
          ),
          const SizedBox(height: 12),
          _GlassCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Skorlar',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700),
                ),
                const SizedBox(height: 10),
                if (scores.isEmpty)
                  const Text('Skor alanı bulunamadı.')
                else
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: scores.entries.map((entry) {
                      final label = _scoreLabel(entry.key);
                      return _ScoreChip(label: '$label: ${entry.value}');
                    }).toList(),
                  ),
              ],
            ),
          ),
          const SizedBox(height: 12),
          _GlassCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Öne Çıkan Dinamikler',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700),
                ),
                const SizedBox(height: 10),
                if (drivers.isEmpty)
                  const Text('Driver verisi bulunamadı.')
                else
                  for (final entry in drivers.entries) ...[
                    Text(
                      _scoreLabel(entry.key),
                      style: const TextStyle(fontWeight: FontWeight.w700),
                    ),
                    const SizedBox(height: 4),
                    Text(_driverText(entry.value)),
                    const SizedBox(height: 8),
                  ],
              ],
            ),
          ),
          const SizedBox(height: 12),
          if (aspectsLines.isNotEmpty)
            _GlassCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Başlıca Açılar',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700),
                  ),
                  const SizedBox(height: 10),
                  for (final line in aspectsLines.take(10)) ...[
                    Text('• $line'),
                    const SizedBox(height: 6),
                  ],
                ],
              ),
            ),
          if (touchLines.isNotEmpty) ...[
            const SizedBox(height: 12),
            _GlassCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Touchpoints',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700),
                  ),
                  const SizedBox(height: 10),
                  for (final line in touchLines.take(10)) ...[
                    Text('• $line'),
                    const SizedBox(height: 6),
                  ],
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }

  Map<String, dynamic> _asMap(dynamic raw) {
    if (raw is Map<String, dynamic>) {
      return raw;
    }
    if (raw is Map) {
      return Map<String, dynamic>.from(raw);
    }
    return <String, dynamic>{};
  }

  List<String> _toStringList(dynamic raw) {
    if (raw is! List) {
      return const <String>[];
    }
    return raw.map((item) => item.toString()).toList();
  }

  String _scoreLabel(String key) {
    switch (key) {
      case 'bond':
        return 'Bağ';
      case 'depth':
        return 'Derinlik';
      case 'spark':
        return 'Kıvılcım';
      case 'freedom':
        return 'Özgürlük';
      case 'risk_index':
        return 'Risk';
      case 'confidence':
        return 'Güven';
      default:
        return key;
    }
  }

  String _driverText(dynamic value) {
    if (value is List && value.isNotEmpty) {
      return value.map((item) => item.toString()).join(', ');
    }
    return '—';
  }
}

class _ScoreChip extends StatelessWidget {
  const _ScoreChip({required this.label});

  final String label;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 7),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(999),
        color: const Color(0x14000000),
      ),
      child: Text(
        label,
        style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
      ),
    );
  }
}

class _GlassCard extends StatelessWidget {
  const _GlassCard({required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(22),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 18, sigmaY: 18),
        child: DecoratedBox(
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(22),
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                Colors.white.withValues(alpha: 0.9),
                Colors.white.withValues(alpha: 0.74),
              ],
            ),
            border: Border.all(color: Colors.white.withValues(alpha: 0.7)),
            boxShadow: const [
              BoxShadow(
                color: Color(0x14000000),
                blurRadius: 16,
                offset: Offset(0, 8),
              ),
            ],
          ),
          child: Padding(padding: const EdgeInsets.all(14), child: child),
        ),
      ),
    );
  }
}
