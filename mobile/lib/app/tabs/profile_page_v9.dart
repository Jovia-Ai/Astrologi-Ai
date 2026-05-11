// Profile v9 — paralel tek-katmanlı tasarım.
//
// Önceki "iceberg" yaklaşımı (yüzey 5 bölüm + derinlik kart galerisi)
// over-engineered'dı; ikisi de aynı görsel dile düştü. Kullanıcı kararı:
// **Profil = direkt kart galerisi** (Tam Okuma tasarımı), kartlar
// tıklanabilir → editöryal detay sayfası açar.
//
// Yapı:
//   ├─ BioCard (her zaman üstte)
//   ├─ Outer tabs: Profil | Haritam (2 tab)
//   ├─ Profil → embedded TamOkumaView (4 eksen tab + kart grid)
//   └─ Haritam → mevcut chart wheel
//
// Eski [profile_page.dart] paralel duruyor — drawer'daki "Profil v9"
// linkinden açılır, prod cutover'da silinir.

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import 'package:mobile/app/profile/haritam_view.dart';
import 'package:mobile/app/profile/layered_kart_detail_page.dart';
import 'package:mobile/app/profile/profile_providers.dart';
import 'package:mobile/app/profile/profile_v9_provider.dart';
import 'package:mobile/app/profile/tam_okuma_view.dart';
import 'package:mobile/design/widgets/shou_topbar.dart';

class ProfilePageV9 extends ConsumerStatefulWidget {
  const ProfilePageV9({super.key});

  @override
  ConsumerState<ProfilePageV9> createState() => _ProfilePageV9State();
}

class _ProfilePageV9State extends ConsumerState<ProfilePageV9> {
  int _outerTab = 0; // 0 Profil (kart galerisi), 1 Haritam

  @override
  Widget build(BuildContext context) {
    final profileAsync = ref.watch(userProfileProvider);
    final profile = profileAsync.asData?.value;
    final authUser = Supabase.instance.client.auth.currentUser;
    final v9Async = ref.watch(profileV9DataProvider);
    final v9Data = v9Async.asData?.value;

    // Hero alanları: önce adapter çıktısı, yoksa Supabase + auth fallback.
    final hero = v9Data?.surface.hero;
    final displayName =
        hero?.displayName ?? _displayName(profile, authUser);
    final username = _displayUsername(profile, authUser);
    final locationAge =
        hero?.locationAge ?? _composeLocationAge(profile);
    final risingSign = hero?.risingSign ?? '—';

    return Scaffold(
      backgroundColor: _V9.bg,
      body: SafeArea(
        bottom: false,
        child: Column(
          children: [
            ShouTopBar(
              label: username,
              variant: ShouTopBarVariant.light,
              onBack: () => Navigator.of(context).maybePop(),
              onMenu: () {},
            ),
            Expanded(
              child: SingleChildScrollView(
                physics: const BouncingScrollPhysics(),
                padding: const EdgeInsets.only(bottom: 80),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    _BioCard(
                      displayName: displayName,
                      avatarUrl: _avatarUrl(profile, authUser),
                      locationAge: locationAge,
                      risingSign: risingSign,
                    ),
                    const SizedBox(height: 12),
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      child: _OuterTabStrip(
                        currentIndex: _outerTab,
                        onChanged: (i) {
                          if (i == _outerTab) return;
                          setState(() => _outerTab = i);
                        },
                      ),
                    ),
                    const SizedBox(height: 18),
                    if (_outerTab == 0)
                      TamOkumaView(
                        profile: profile,
                        displayName: displayName,
                        data: v9Data?.tamOkuma,
                        embedded: true,
                        onCardTap: (card) {
                          Navigator.of(context).push(
                            MaterialPageRoute<void>(
                              builder: (_) => LayeredKartDetailPage(
                                card: card,
                                username: username,
                              ),
                            ),
                          );
                        },
                      )
                    else
                      HaritamView(profile: profile),
                    const SizedBox(height: 20),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // ── helpers ────────────────────────────────────────────────────────
  String _displayName(Map<String, dynamic>? profile, User? user) {
    final fromProfile = (profile?['full_name'] ?? profile?['name'] ?? '')
        .toString()
        .trim();
    if (fromProfile.isNotEmpty) return fromProfile;
    final fromMail = (user?.email ?? '').split('@').first.trim();
    if (fromMail.isNotEmpty) return fromMail;
    return 'Profil';
  }

  String _displayUsername(Map<String, dynamic>? profile, User? user) {
    final candidate = [
          profile?['username'],
          profile?['handle'],
          user?.email?.split('@').first,
        ]
        .map((e) => (e ?? '').toString().trim())
        .firstWhere((e) => e.isNotEmpty, orElse: () => 'profil');
    return candidate.startsWith('@') ? candidate : '@$candidate';
  }

  String? _avatarUrl(Map<String, dynamic>? profile, User? user) {
    final pUrl = (profile?['avatar_url'] ?? '').toString().trim();
    if (pUrl.isNotEmpty) return pUrl;
    final mUrl = (user?.userMetadata?['avatar_url'] ?? '').toString().trim();
    return mUrl.isEmpty ? null : mUrl;
  }

  String _composeLocationAge(Map<String, dynamic>? profile) {
    if (profile == null) return '';
    final city = (profile['city'] ?? '').toString().trim();
    final country = (profile['country'] ?? '').toString().trim();
    final birthDate = (profile['birth_date'] ?? '').toString().trim();
    final parts = <String>[];
    if (city.isNotEmpty) {
      parts.add(country.isNotEmpty ? '$city, $country' : city);
    } else if (country.isNotEmpty) {
      parts.add(country);
    }
    if (birthDate.isNotEmpty) {
      final segs = birthDate.split('-');
      if (segs.length == 3) {
        final year = int.tryParse(segs[0]);
        if (year != null) {
          parts.add('${DateTime.now().year - year} yaş');
        }
      }
    }
    return parts.join(' · ');
  }
}

// ═══════════════════════════════════════════════════════════════════
// Palette (matches haritam/tamokuma ink-on-paper, lime micro-accent only)
// ═══════════════════════════════════════════════════════════════════

class _V9 {
  static const bg = Color(0xFFE2E2E8);
  static const ink = Color(0xFF0E0E10);
  static const mist = Color(0xFF888888);
  static const silver = Color(0xFFB0B0B0);
  static const hairline = Color(0x1A000000);
  static const paper = Color(0xFFFFFFFF);
  static const cream = Color(0xFFFAFAF7);
  static const lavCard = Color(0xFFF4F2FA);
  static const lavDeep = Color(0xFF534AB7);
}

class _Fonts {
  static const body = 'Inter';
}

// ═══════════════════════════════════════════════════════════════════
// Bio card — avatar + ad + meta + "Tam Okumayı aç" mikro CTA
// ═══════════════════════════════════════════════════════════════════

class _BioCard extends StatelessWidget {
  const _BioCard({
    required this.displayName,
    required this.avatarUrl,
    required this.locationAge,
    required this.risingSign,
  });

  final String displayName;
  final String? avatarUrl;
  final String locationAge;
  final String risingSign;

  @override
  Widget build(BuildContext context) {
    final meta = locationAge;
    final risingDisplay = (risingSign.trim().isEmpty || risingSign == '—')
        ? '—'
        : risingSign;

    return Padding(
      padding: const EdgeInsets.fromLTRB(10, 4, 10, 0),
      child: Container(
        clipBehavior: Clip.antiAlias,
        decoration: BoxDecoration(
          color: _V9.paper,
          borderRadius: BorderRadius.circular(28),
        ),
        padding: const EdgeInsets.fromLTRB(20, 22, 20, 22),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _Avatar(url: avatarUrl),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const SizedBox(height: 4),
                  Text(
                    displayName,
                    style: const TextStyle(
                      fontFamily: _Fonts.body,
                      fontSize: 22,
                      fontWeight: FontWeight.w500,
                      color: _V9.ink,
                      letterSpacing: -0.4,
                      height: 1.2,
                    ),
                  ),
                  if (meta.isNotEmpty) ...[
                    const SizedBox(height: 6),
                    Text(
                      meta,
                      style: const TextStyle(
                        fontFamily: _Fonts.body,
                        fontSize: 12,
                        color: _V9.mist,
                        letterSpacing: 0.1,
                        height: 1.2,
                      ),
                    ),
                  ],
                  const SizedBox(height: 14),
                  // "Yükselen" tek vurgu — kritiğe göre üç pill yerine bir
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 10,
                      vertical: 5,
                    ),
                    decoration: BoxDecoration(
                      color: _V9.lavCard,
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Text(
                          '↗',
                          style: TextStyle(
                            fontSize: 11,
                            color: _V9.lavDeep,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        const SizedBox(width: 5),
                        const Text(
                          'Yükselen',
                          style: TextStyle(
                            fontFamily: _Fonts.body,
                            fontSize: 11,
                            color: _V9.mist,
                            letterSpacing: 0.2,
                          ),
                        ),
                        const SizedBox(width: 5),
                        Text(
                          risingDisplay,
                          style: const TextStyle(
                            fontFamily: _Fonts.body,
                            fontSize: 11.5,
                            color: _V9.ink,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _Avatar extends StatelessWidget {
  const _Avatar({required this.url});
  final String? url;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 84,
      height: 84,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        border: Border.all(color: _V9.hairline, width: 0.6),
      ),
      child: ClipOval(
        child: url != null
            ? Image.network(
                url!,
                fit: BoxFit.cover,
                errorBuilder: (_, _, _) => _avatarFallback(),
                loadingBuilder: (context, child, loading) {
                  if (loading == null) return child;
                  return _avatarFallback();
                },
              )
            : _avatarFallback(),
      ),
    );
  }

  Widget _avatarFallback() {
    return Container(
      color: _V9.cream,
      alignment: Alignment.center,
      child: const Icon(Icons.person, size: 36, color: _V9.silver),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════
// Outer 3-tab strip (Profil / Haritam / Tam Okuma)
// ═══════════════════════════════════════════════════════════════════

class _OuterTabStrip extends StatelessWidget {
  const _OuterTabStrip({required this.currentIndex, required this.onChanged});

  final int currentIndex;
  final ValueChanged<int> onChanged;

  static const _labels = ['Profil', 'Haritam'];

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: _V9.paper,
        border: Border.all(color: _V9.hairline, width: 1),
        borderRadius: BorderRadius.circular(8),
      ),
      clipBehavior: Clip.antiAlias,
      child: Row(
        children: [
          for (var i = 0; i < _labels.length; i++) ...[
            Expanded(
              child: GestureDetector(
                behavior: HitTestBehavior.opaque,
                onTap: () => onChanged(i),
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 180),
                  curve: Curves.easeOutCubic,
                  padding: const EdgeInsets.symmetric(vertical: 11),
                  color: currentIndex == i ? _V9.ink : _V9.paper,
                  alignment: Alignment.center,
                  child: Text(
                    _labels[i],
                    style: TextStyle(
                      fontFamily: _Fonts.body,
                      fontSize: 11.5,
                      fontWeight: FontWeight.w400,
                      letterSpacing: 0.2,
                      color: currentIndex == i ? Colors.white : _V9.mist,
                    ),
                  ),
                ),
              ),
            ),
            if (i != _labels.length - 1)
              Container(width: 1, height: 38, color: _V9.hairline),
          ],
        ],
      ),
    );
  }
}
