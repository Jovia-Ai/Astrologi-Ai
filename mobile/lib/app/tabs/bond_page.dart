import 'dart:ui';

import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:mobile/app/api/api_client.dart';
import 'package:mobile/app/people/add_person_page.dart';
import 'package:mobile/app/people/people_providers.dart';
import 'package:mobile/app/people/people_repository.dart';
import 'package:mobile/app/people/person_profile.dart';
import 'package:mobile/app/profile/profile_providers.dart';
import 'package:mobile/app/tabs/bond_models.dart';
import 'package:mobile/app/tabs/bond_result_page.dart';

class BondPage extends ConsumerStatefulWidget {
  const BondPage({super.key});

  @override
  ConsumerState<BondPage> createState() => _BondPageState();
}

class _BondPageState extends ConsumerState<BondPage> {
  static const String _baseUrl = 'http://127.0.0.1:5000';

  PersonProfile? _selectedPerson;
  BondType _bondType = BondType.romantic;
  bool _loading = false;

  @override
  Widget build(BuildContext context) {
    final profileAsync = ref.watch(userProfileProvider);
    final profile = profileAsync.valueOrNull;

    final canViewBond =
        !_loading && _selectedPerson != null && _hasBirthData(profile);

    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 28),
      children: [
        const Text(
          'Bond',
          style: TextStyle(fontSize: 22, fontWeight: FontWeight.w700),
        ),
        const SizedBox(height: 6),
        Text(
          'İki kişi arasındaki sinastri dinamiğini görüntüle.',
          style: Theme.of(
            context,
          ).textTheme.bodyMedium?.copyWith(color: Colors.black54),
        ),
        const SizedBox(height: 14),
        _GlassCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Kişiler',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700),
              ),
              const SizedBox(height: 10),
              Row(
                children: [
                  Expanded(
                    child: _SelectorCard(
                      title: 'Sen',
                      subtitle: _userSummary(profile),
                      icon: Icons.person,
                      onTap: null,
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: _SelectorCard(
                      title: _selectedPerson?.name ?? 'Kişi seç',
                      subtitle: _selectedPerson == null
                          ? 'Arkadaş seç'
                          : _personSummary(_selectedPerson!),
                      icon: Icons.groups_2_outlined,
                      onTap: _openPersonPicker,
                    ),
                  ),
                ],
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
                'Bond Türü',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700),
              ),
              const SizedBox(height: 10),
              DropdownButtonFormField<BondType>(
                initialValue: _bondType,
                decoration: const InputDecoration(
                  border: OutlineInputBorder(),
                  isDense: true,
                ),
                items: BondType.values
                    .map(
                      (type) => DropdownMenuItem<BondType>(
                        value: type,
                        child: Text(type.label),
                      ),
                    )
                    .toList(),
                onChanged: (value) {
                  if (value == null) {
                    return;
                  }
                  setState(() => _bondType = value);
                },
              ),
            ],
          ),
        ),
        const SizedBox(height: 18),
        FilledButton(
          onPressed: canViewBond ? () => _viewBond(profile!) : null,
          child: _loading
              ? const SizedBox(
                  width: 18,
                  height: 18,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : const Text('View Bond'),
        ),
      ],
    );
  }

  Future<void> _openPersonPicker() async {
    final selected = await showModalBottomSheet<PersonProfile>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (sheetContext) {
        return _PeoplePickerSheet(
          onPersonSelected: (person) => Navigator.of(sheetContext).pop(person),
        );
      },
    );

    if (selected == null) {
      return;
    }

    setState(() => _selectedPerson = selected);
  }

  Future<void> _viewBond(Map<String, dynamic> myProfile) async {
    final person = _selectedPerson;
    if (person == null) {
      return;
    }

    setState(() => _loading = true);

    final payload = <String, dynamic>{
      'partner_a': {
        'name': _userName(myProfile),
        'birthDate': (myProfile['birth_date'] ?? '').toString().trim(),
        'birthTime': _normalizeBirthTime(
          (myProfile['birth_time'] ?? '').toString(),
        ),
        'birthPlace': _resolvePlace(myProfile),
      },
      'partner_b': {
        'name': person.name,
        'birthDate': person.birthDate,
        'birthTime': person.normalizedBirthTime,
        'birthPlace': person.place,
      },
      'options': {
        'include_debug': false,
        'bond_type': _bondType.backendValue,
        'relationship_type': _bondType.backendValue,
      },
    };

    try {
      final client = ApiClient(baseUrl: _baseUrl);
      Response<dynamic> response;

      try {
        response = await client.post(
          '/api/v1/relationship/synastry/analyze',
          data: payload,
        );
      } on DioException catch (error) {
        final code = error.response?.statusCode;
        if (code == 404 || code == 405) {
          response = await client.post('/api/synastry/analyze', data: payload);
        } else {
          rethrow;
        }
      }

      if (!mounted) {
        return;
      }

      final data = _asMap(response.data);
      await Navigator.of(context).push(
        MaterialPageRoute<void>(
          builder: (_) => BondResultPage(
            response: data,
            youName: _userName(myProfile),
            partnerName: person.name,
            bondType: _bondType,
          ),
        ),
      );
    } catch (error) {
      if (!mounted) {
        return;
      }
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Bond analizi alınamadı: $error')));
    } finally {
      if (mounted) {
        setState(() => _loading = false);
      }
    }
  }

  bool _hasBirthData(Map<String, dynamic>? profile) {
    if (profile == null) {
      return false;
    }
    final birthDate = (profile['birth_date'] ?? '').toString().trim();
    final place = _resolvePlace(profile);
    return birthDate.isNotEmpty && place.isNotEmpty;
  }

  String _userName(Map<String, dynamic>? profile) {
    final fromProfile = (profile?['full_name'] ?? profile?['name'] ?? '')
        .toString()
        .trim();
    if (fromProfile.isNotEmpty) {
      return fromProfile;
    }
    return 'Sen';
  }

  String _userSummary(Map<String, dynamic>? profile) {
    if (profile == null) {
      return 'Profil yükleniyor';
    }
    final birthDate = (profile['birth_date'] ?? '').toString().trim();
    final birthTime = _normalizeBirthTime(
      (profile['birth_time'] ?? '').toString(),
    );
    final place = _resolvePlace(profile);
    if (birthDate.isEmpty || place.isEmpty) {
      return 'Doğum verisi eksik';
    }
    return '$birthDate • $birthTime • $place';
  }

  String _personSummary(PersonProfile person) {
    return '${person.birthDate} • ${person.normalizedBirthTime} • ${person.place}';
  }

  String _resolvePlace(Map<String, dynamic> profile) {
    final placeRaw = (profile['place'] ?? '').toString().trim();
    if (placeRaw.isNotEmpty) {
      return placeRaw;
    }
    final city = (profile['city'] ?? '').toString().trim();
    final country = (profile['country'] ?? '').toString().trim();
    if (city.isEmpty) {
      return country;
    }
    if (country.isEmpty) {
      return city;
    }
    return '$city, $country';
  }

  String _normalizeBirthTime(String raw) {
    final value = raw.trim();
    if (value.isEmpty) {
      return '12:00';
    }
    if (value.length >= 5) {
      return value.substring(0, 5);
    }
    return value;
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
}

class _PeoplePickerSheet extends ConsumerWidget {
  const _PeoplePickerSheet({required this.onPersonSelected});

  final ValueChanged<PersonProfile> onPersonSelected;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final peopleAsync = ref.watch(peopleListProvider);

    return Padding(
      padding: const EdgeInsets.fromLTRB(12, 12, 12, 12),
      child: _GlassCard(
        child: SafeArea(
          top: false,
          child: SizedBox(
            height: MediaQuery.of(context).size.height * 0.65,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Arkadaşlarım',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700),
                ),
                const SizedBox(height: 10),
                Align(
                  alignment: Alignment.centerLeft,
                  child: OutlinedButton.icon(
                    onPressed: () async {
                      final created = await Navigator.of(context).push<bool>(
                        MaterialPageRoute<bool>(
                          builder: (_) => const AddPersonPage(),
                        ),
                      );
                      if (created == true) {
                        ref.invalidate(peopleListProvider);
                      }
                    },
                    icon: const Icon(Icons.add),
                    label: const Text('+ Kişi Ekle'),
                  ),
                ),
                const SizedBox(height: 10),
                Expanded(
                  child: peopleAsync.when(
                    data: (items) {
                      if (items.isEmpty) {
                        return const Center(child: Text('Kayıtlı kişi yok.'));
                      }
                      return ListView.separated(
                        itemCount: items.length,
                        separatorBuilder: (_, _) => const SizedBox(height: 8),
                        itemBuilder: (_, index) {
                          final person = items[index];
                          return Card(
                            child: ListTile(
                              leading: const CircleAvatar(
                                child: Icon(Icons.person_outline),
                              ),
                              title: Text(person.name),
                              subtitle: Text(
                                '${person.birthDate} • ${person.normalizedBirthTime} • ${person.place}',
                              ),
                              onTap: () => onPersonSelected(person),
                            ),
                          );
                        },
                      );
                    },
                    loading: () =>
                        const Center(child: CircularProgressIndicator()),
                    error: (error, _) {
                      WidgetsBinding.instance.addPostFrameCallback((_) {
                        if (!context.mounted) {
                          return;
                        }
                        final msg = error is PeopleQueryException
                            ? error.userMessage
                            : 'Arkadaşlar yüklenemedi: $error';
                        ScaffoldMessenger.of(
                          context,
                        ).showSnackBar(SnackBar(content: Text(msg)));
                      });
                      return Center(
                        child: Text(
                          error is PeopleQueryException
                              ? error.userMessage
                              : 'Arkadaşlar yüklenemedi: $error',
                          textAlign: TextAlign.center,
                        ),
                      );
                    },
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _SelectorCard extends StatelessWidget {
  const _SelectorCard({
    required this.title,
    required this.subtitle,
    required this.icon,
    required this.onTap,
  });

  final String title;
  final String subtitle;
  final IconData icon;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: Ink(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: Colors.black12),
          color: Colors.white.withValues(alpha: 0.65),
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            CircleAvatar(
              radius: 18,
              backgroundColor: Colors.black12,
              child: Icon(icon, color: Colors.black87),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(fontWeight: FontWeight.w700),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    subtitle,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(fontSize: 12, color: Colors.black54),
                  ),
                ],
              ),
            ),
            Icon(
              Icons.expand_more,
              color: onTap == null ? Colors.transparent : Colors.black45,
            ),
          ],
        ),
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
