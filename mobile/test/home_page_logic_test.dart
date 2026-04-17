import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/app/tabs/home_page.dart';
import 'package:mobile/app/timing/narrative_dtos.dart';
import 'package:mobile/app/timing/turkish_text.dart';
import 'package:mobile/l10n/app_localizations.dart';

String tr(String value) => normalizeTurkishText(value);

void main() {
  group('Home transit logic', () {
    final l10n = lookupAppLocalizations(const Locale('tr'));

    test(
      'buildHomeTransitSnapshot keeps period cards but does not promote them into daily slot',
      () {
        final narrative = NarrativeResponse.fromMap({
          'calendar': {
            'days': [
              {
                'date': '2026-04-02',
                'rating': 2,
                'heat': 2,
                'event_count': 0,
                'signals_count': 1,
                'has_signals': true,
                'is_critical': false,
                'labels': const <String>[],
                'critical_reasons': const <String>[],
                'signal_label_tr': 'Bugün öne çıkan tema bu.',
                'tone_label_tr': 'akiskan',
                'micro_summary_tr': 'Bugün transit teması belirgin.',
              },
            ],
          },
          'public': {
            'period_core': {
              'title': 'Transit Donemi',
              'core_story': 'Transit ana hikayesi',
              'upper_meaning': 'Buyuk akis',
              'big_picture': 'Transit buyuk resmi',
              'mechanism': 'Transit mekanizmasi',
              'tags': [],
            },
            'event_cards': [],
            'daily_event_cards': [],
            'period_event_cards': [
              {
                'event_id': 'evt_period',
                'headline': 'Transit Baslik',
                'opening': 'Transit acilisi',
                'essence': 'Transit ozeti',
                'what_it_builds': 'Transit yonu',
                'signature_tr': 'Transit imza',
                'time_hint_tr': 'Bu hafta',
                'horizon': 'period',
                'tags': {
                  'phase': 'peak',
                  'duration': 'weeks',
                  'domain': 'general',
                },
              },
            ],
          },
        });

        final snapshot = buildHomeTransitSnapshot(
          narrative: narrative,
          today: DateTime(2026, 4, 2),
          l10n: l10n,
        );

        expect(snapshot.periodCore?.title, tr('Transit Donemi'));
        expect(snapshot.periodCards, hasLength(1));
        expect(snapshot.periodCards.first.title, tr('Transit Baslik'));
        expect(snapshot.dailyCards, isEmpty);
      },
    );

    test(
      'buildHomeDefaultHeroBody prefers transit copy over natal summary',
      () {
        final dailyCard = EventCardDto.fromMap({
          'event_id': 'evt_daily',
          'headline': 'Gunluk Baslik',
          'opening': 'Transit acilisi',
          'essence': 'Transit ozeti',
          'horizon': 'day',
          'tags': {'phase': 'peak'},
        });

        final bodyFromDaily = buildHomeDefaultHeroBody(
          todayDailyCard: dailyCard,
          activeCard: null,
          periodCore: null,
          natalSummary: 'Natal yorum',
          loading: false,
          l10n: l10n,
        );

        final bodyFromPeriodCore = buildHomeDefaultHeroBody(
          todayDailyCard: null,
          activeCard: null,
          periodCore: PeriodCoreDto.fromMap({
            'title': 'Donem',
            'core_story': 'Transit donem hikayesi',
            'upper_meaning': 'Yukari',
            'big_picture': 'Buyuk resim',
            'mechanism': 'Mekanizma',
            'tags': [],
          }),
          natalSummary: 'Natal yorum',
          loading: false,
          l10n: l10n,
        );

        expect(bodyFromDaily, tr('Transit acilisi'));
        expect(bodyFromPeriodCore, tr('Transit donem hikayesi'));
      },
    );

    test(
      'buildHomeFastFallbackDailyCardFromPayloadMap promotes fast transit copy',
      () {
        final card = buildHomeFastFallbackDailyCardFromPayloadMap({
          'headline': 'Bugun akista bir vurgu var',
          'summary': 'Mesajlar ve temaslar daha belirgin calisiyor.',
          'energy': {
            'badge': 'Bugun bende ne aciliyor?',
            'focus': 'Iletisim',
            'summary': 'Kisa bir toplama',
          },
          'highlights': [
            {
              'id': 'fast-transit-1',
              'kind': 'transit',
              'title': 'Konusurken tek bir sey fazla one cikabilir',
              'summary': 'Iletisim alaninda bugun bir vurgu var.',
            },
          ],
        }, l10n: l10n);

        expect(card, isNotNull);
        expect(
          card!.headline,
          tr('Konusurken tek bir sey fazla one cikabilir'),
        );
        expect(card.opening, tr('Iletisim alaninda bugun bir vurgu var.'));
        expect(
          card.feltLineTr,
          tr('Konusurken tek bir sey fazla one cikabilir'),
        );
        expect(card.signalLabelTr, tr('Bugun bende ne aciliyor?'));
        expect(card.horizon, 'daily');
        expect(card.todayFacingFallback, isFalse);
      },
    );

    test(
      'buildHomeFastFallbackDailyCardFromPayloadMap skips natal or sky fallback copy without a transit highlight',
      () {
        final card = buildHomeFastFallbackDailyCardFromPayloadMap({
          'headline': 'Capricorn yukselenle acilan cizgi',
          'summary':
              'Capricorn yukselen ve Capricorn Gunes birlesimi disari verdigin tonu daha belirgin kuruyor.',
          'energy': {
            'badge': 'Exact aci',
            'focus': 'Capricorn yukselenle acilan cizgi',
            'summary': 'Profil ozeti',
          },
          'highlights': [
            {
              'id': 'sky-1',
              'kind': 'sky',
              'title': 'Merkur geriliyor',
              'summary': 'Kolektif nabizda yavaslama var.',
            },
          ],
          'section_states': {
            'transit_summary': 'deferred',
            'natal_summary': 'ready',
          },
        }, l10n: l10n);

        expect(card, isNull);
      },
    );

    test(
      'deferred home fast payload does not promote sky copy into transit period preview',
      () {
        final payload = {
          'headline': 'Mars-Uranus sekstili',
          'summary':
              'Mars-Uranus sekstili su siralar kolektif ritimde daha gorunur calisiyor.',
          'energy': {
            'badge': 'Exact aci',
            'focus': 'Mars-Uranus sekstili',
            'summary': 'Kolektif ritimde hizli bir acilim var.',
          },
          'highlights': [
            {
              'id': 'sky-1',
              'kind': 'sky',
              'title': 'Mars-Uranus sekstili',
              'summary':
                  'Mars-Uranus sekstili su siralar kolektif ritimde daha gorunur calisiyor.',
            },
          ],
          'section_states': {
            'transit_summary': 'deferred',
            'natal_summary': 'ready',
          },
        };

        expect(
          buildHomeFastFallbackDailyCardFromPayloadMap(payload, l10n: l10n),
          isNull,
        );
        expect(
          buildHomeFastPeriodCoreFromPayloadMap(payload, l10n: l10n),
          isNull,
        );
        expect(
          buildHomeFastPeriodCardsFromPayloadMap(payload, l10n: l10n),
          isEmpty,
        );
      },
    );

    test(
      'mergeHomeTransitSnapshot preserves existing home transit when incoming snapshot is empty',
      () {
        final existingDailyCard = EventCardDto.fromMap({
          'event_id': 'fast-fallback',
          'headline': 'Mevcut transit basligi',
          'opening': 'Mevcut transit acilisi',
          'essence': 'Mevcut transit ozeti',
          'horizon': 'daily',
          'tags': {'phase': 'preview'},
        });
        final existingDayMeta = NarrativeCalendarDay.fromMap({
          'date': '2026-04-06',
          'rating': 2,
          'heat': 2,
          'event_count': 1,
          'signals_count': 1,
          'has_signals': true,
          'is_critical': false,
          'labels': const <String>[],
          'critical_reasons': const <String>[],
          'signal_label_tr': 'Bugun tek tema var.',
          'tone_label_tr': 'hareketli',
          'micro_summary_tr': 'Bugun bir sey belirgin.',
        });

        final merged = mergeHomeTransitSnapshot(
          incoming: const HomeTransitSnapshot(
            periodCore: null,
            periodCards: <PeriodCardDto>[],
            dailyCards: <EventCardDto>[],
            calendarDays: <String, NarrativeCalendarDay>{},
            todayDayMeta: null,
          ),
          currentPeriodCards: const <PeriodCardDto>[
            PeriodCardDto(
              id: 'existing-period',
              title: 'Mevcut donem',
              subtitle: 'Mevcut donem aciklamasi',
              timeHint: 'Bu hafta',
            ),
          ],
          currentDailyCards: <EventCardDto>[existingDailyCard],
          currentCalendarDays: <String, NarrativeCalendarDay>{
            '2026-04-06': existingDayMeta,
          },
          currentTodayDayMeta: existingDayMeta,
        );

        expect(merged.periodCards, hasLength(1));
        expect(merged.dailyCards, hasLength(1));
        expect(merged.dailyCards.first.headline, tr('Mevcut transit basligi'));
        expect(
          merged.calendarDays['2026-04-06']?.microSummaryTr,
          tr('Bugun bir sey belirgin.'),
        );
        expect(merged.todayDayMeta?.toneLabelTr, tr('hareketli'));
      },
    );

    test(
      'mergeHomeTransitSnapshot keeps stronger existing daily card over period-derived fallback',
      () {
        final existingDailyCard = EventCardDto.fromMap({
          'event_id': 'evt_daily_strong',
          'headline': 'Bugun bir konu daha net aciliyor',
          'opening': 'Gunun odagi daha belirgin ilerliyor.',
          'why_it_feels_this_way_tr':
              'Cunku bu aci dogrudan kisa vadeli ritmini uyandiriyor.',
          'guidance_micro_tr': 'Tek bir seye odaklanman daha iyi calisir.',
          'house_touchpoint_hint_tr': '3. ev temasi',
          'essence': 'Net bir gunluk vurgu var.',
          'horizon': 'daily',
          'source_horizon': 'daily',
          'tags': {'phase': 'exact', 'duration': 'day', 'domain': 'general'},
        });
        final incomingFallback = EventCardDto.fromMap({
          'event_id': 'evt_period_fallback',
          'headline': 'Arkada calisan tema bugune dusuyor',
          'opening': 'Daha uzun bir tema bugun daha gorunur.',
          'why_it_feels_this_way_tr':
              'Bu vurgu kisa tetikten cok uzun bir akis tasiyor.',
          'essence': 'Donem etkisi bugune dusuyor.',
          'horizon': 'daily',
          'source_horizon': 'period',
          'is_period_derived': true,
          'tags': {'phase': 'peak', 'duration': 'weeks', 'domain': 'general'},
        });

        final merged = mergeHomeTransitSnapshot(
          incoming: HomeTransitSnapshot(
            periodCore: null,
            periodCards: const <PeriodCardDto>[],
            dailyCards: <EventCardDto>[incomingFallback],
            calendarDays: const <String, NarrativeCalendarDay>{},
            todayDayMeta: null,
          ),
          currentDailyCards: <EventCardDto>[existingDailyCard],
        );

        expect(merged.dailyCards, hasLength(1));
        expect(merged.dailyCards.first.eventId, 'evt_daily_strong');
      },
    );

    test(
      'mergeHomeTransitSnapshot upgrades fast preview when richer true daily card arrives',
      () {
        final existingFastPreview = EventCardDto.fromMap({
          'event_id': 'home-fast-daily-fallback',
          'headline': 'Bugun bir vurgu var',
          'opening': 'Iletisim alaninda bir hareket var.',
          'why_it_feels_this_way_tr': 'Kisa bir on izleme.',
          'essence': 'On izleme ozeti.',
          'horizon': 'daily',
          'source_horizon': 'daily',
          'tags': {'phase': 'preview', 'duration': 'day', 'domain': 'general'},
        });
        final incomingDailyCard = EventCardDto.fromMap({
          'event_id': 'evt_daily_rich',
          'headline': 'Konusmalar bugun daha hizli aciliyor',
          'opening': 'Merkuryen trafik daha canli ve yonlu akiyor.',
          'why_it_feels_this_way_tr':
              'Bu aci 3. ev alanini tetikledigi icin mesaj, akis ve yakin cevre vurgusu buyuyor.',
          'guidance_micro_tr':
              'Tek bir mesaji netlestirip sonra dagilmak daha iyi calisir.',
          'house_touchpoint_hint_tr': '3. ev ve Merkur temasi',
          'essence': 'Gercek gunluk yorum.',
          'horizon': 'daily',
          'source_horizon': 'daily',
          'tags': {'phase': 'exact', 'duration': 'day', 'domain': 'general'},
        });

        final merged = mergeHomeTransitSnapshot(
          incoming: HomeTransitSnapshot(
            periodCore: null,
            periodCards: const <PeriodCardDto>[],
            dailyCards: <EventCardDto>[incomingDailyCard],
            calendarDays: const <String, NarrativeCalendarDay>{},
            todayDayMeta: null,
          ),
          currentDailyCards: <EventCardDto>[existingFastPreview],
        );

        expect(merged.dailyCards, hasLength(1));
        expect(merged.dailyCards.first.eventId, 'evt_daily_rich');
      },
    );

    test(
      'buildHomeTransitSnapshot scores legacy event cards so stronger daily stays on home',
      () {
        final narrative = NarrativeResponse.fromMap({
          'calendar': {
            'days': [
              {
                'date': '2026-04-08',
                'rating': 2,
                'heat': 2,
                'event_count': 2,
                'signals_count': 2,
                'has_signals': true,
                'is_critical': false,
                'labels': const <String>[],
                'critical_reasons': const <String>[],
                'signal_label_tr': 'Bugun iki sey belirgin.',
                'tone_label_tr': 'yogun',
                'micro_summary_tr': 'Bugunun asil karti daha net.',
              },
            ],
          },
          'public': {
            'period_core': {},
            'daily_event_cards': [],
            'period_event_cards': [],
            'event_cards': [
              {
                'event_id': 'evt_weaker',
                'transit_body': 'venus',
                'aspect': 'trine',
                'phase': 'separating',
                'bucket': 'short',
                'orb_deg': 4.6,
                'headline': 'Daha yumusak bir akis',
                'opening': 'Bu kart bugun icin ikincil kaliyor.',
                'essence': 'Ikincil gunluk vurgu.',
                'horizon': 'daily',
                'timing': {
                  'peak_date_utc': '2026-04-11T12:00:00Z',
                  'entry_date_utc': '2026-04-09T12:00:00Z',
                },
                'tags': {
                  'phase': 'separating',
                  'duration': 'day',
                  'domain': 'general',
                  'exact_in_days': 3,
                  'intensity': 0.2,
                },
              },
              {
                'event_id': 'evt_stronger',
                'transit_body': 'moon',
                'aspect': 'square',
                'phase': 'exact',
                'bucket': 'short',
                'orb_deg': 0.1,
                'headline': 'Asil gunluk kart',
                'opening': 'Bugunun ana vurgu karti bu olmali.',
                'essence': 'Guclu gunluk vurgu.',
                'horizon': 'daily',
                'timing': {
                  'peak_date_utc': '2026-04-08T12:00:00Z',
                  'entry_date_utc': '2026-04-08T00:00:00Z',
                },
                'tags': {
                  'phase': 'exact',
                  'duration': 'day',
                  'domain': 'general',
                  'exact_in_days': 0,
                  'intensity': 0.9,
                },
              },
            ],
          },
        });

        final snapshot = buildHomeTransitSnapshot(
          narrative: narrative,
          today: DateTime(2026, 4, 8),
          l10n: l10n,
        );

        expect(snapshot.dailyCards, isNotEmpty);
        expect(snapshot.dailyCards.first.eventId, 'evt_stronger');
      },
    );

    test(
      'hasUsableHomeDailyContent is false when home has no card copy or day meta',
      () {
        expect(
          hasUsableHomeDailyContent(
            dailyCards: const <EventCardDto>[],
            dayMeta: null,
          ),
          isFalse,
        );
      },
    );

    test(
      'hasUsableHomeDailyContent is true when today micro summary exists',
      () {
        final dayMeta = NarrativeCalendarDay.fromMap({
          'date': '2026-04-08',
          'rating': 2,
          'heat': 2,
          'event_count': 1,
          'signals_count': 1,
          'has_signals': true,
          'is_critical': false,
          'labels': const <String>[],
          'critical_reasons': const <String>[],
          'signal_label_tr': 'Bugun tek tema var.',
          'tone_label_tr': 'yogun',
          'micro_summary_tr': 'Bugun bir sey aciliyor.',
        });

        expect(
          hasUsableHomeDailyContent(
            dailyCards: const <EventCardDto>[],
            dayMeta: dayMeta,
          ),
          isTrue,
        );
        expect(
          hasStrongHomeDailyContent(dailyCards: const <EventCardDto>[]),
          isFalse,
        );
        expect(
          hasHomeMetaOnlyContent(
            dailyCards: const <EventCardDto>[],
            dayMeta: dayMeta,
          ),
          isTrue,
        );
      },
    );

    test('fast preview fallback never counts as ready daily', () {
      final fastFallback = EventCardDto.fromMap({
        'event_id': 'home-fast-daily-fallback',
        'headline': 'Bugun bir vurgu var',
        'opening': 'On izleme metni',
        'horizon': 'daily',
        'source_horizon': 'daily',
        'tags': {'phase': 'preview', 'duration': 'day', 'domain': 'general'},
      });

      expect(
        hasStrongHomeDailyContent(dailyCards: <EventCardDto>[fastFallback]),
        isFalse,
      );
      expect(
        resolveHomeDailyRenderState(
          loading: false,
          dailyCards: <EventCardDto>[fastFallback],
          dayMeta: null,
          errorMessage: null,
        ),
        HomeDailyRenderState.degraded,
      );
      expect(
        homeDailyDegradedReason(
          loading: false,
          dailyCards: <EventCardDto>[fastFallback],
          dayMeta: null,
          errorMessage: null,
        ),
        'fast_preview_only',
      );
    });

    test('period-derived daily card never counts as ready daily', () {
      final periodDerived = EventCardDto.fromMap({
        'event_id': 'evt_period_fallback',
        'headline': 'Donem etkisi bugune tasiyor',
        'opening': 'Bu kart period kaynakli.',
        'horizon': 'daily',
        'source_horizon': 'period',
        'is_period_derived': true,
        'today_facing_fallback': true,
        'tags': {'phase': 'peak', 'duration': 'weeks', 'domain': 'general'},
      });

      expect(
        hasStrongHomeDailyContent(dailyCards: <EventCardDto>[periodDerived]),
        isFalse,
      );
      expect(
        resolveHomeDailyRenderState(
          loading: false,
          dailyCards: <EventCardDto>[periodDerived],
          dayMeta: null,
          errorMessage: null,
        ),
        HomeDailyRenderState.degraded,
      );
      expect(
        homeDailyDegradedReason(
          loading: false,
          dailyCards: <EventCardDto>[periodDerived],
          dayMeta: null,
          errorMessage: null,
        ),
        'period_derived_only',
      );
    });

    test(
      'hasUsableHomeDailyContent is true when a daily card carries copy',
      () {
        final dailyCard = EventCardDto.fromMap({
          'event_id': 'evt_daily_copy',
          'headline': 'Bugunun karti',
          'opening': 'Bugun sende bir vurgu var.',
          'horizon': 'daily',
          'tags': {'phase': 'exact', 'duration': 'day', 'domain': 'general'},
        });

        expect(
          hasUsableHomeDailyContent(
            dailyCards: <EventCardDto>[dailyCard],
            dayMeta: null,
          ),
          isTrue,
        );
        expect(
          hasStrongHomeDailyContent(dailyCards: <EventCardDto>[dailyCard]),
          isTrue,
        );
      },
    );

    test('meta-only content is degraded and never ready', () {
      final dayMeta = NarrativeCalendarDay.fromMap({
        'date': '2026-04-08',
        'rating': 2,
        'heat': 2,
        'event_count': 1,
        'signals_count': 1,
        'has_signals': true,
        'is_critical': false,
        'labels': const <String>[],
        'critical_reasons': const <String>[],
        'signal_label_tr': 'Bugun tek tema var.',
        'tone_label_tr': 'yogun',
        'micro_summary_tr': 'Bugun bir sey aciliyor.',
      });

      expect(
        resolveHomeDailyRenderState(
          loading: false,
          dailyCards: const <EventCardDto>[],
          dayMeta: dayMeta,
          errorMessage: null,
        ),
        HomeDailyRenderState.degraded,
      );
      expect(
        homeDailyDegradedReason(
          loading: false,
          dailyCards: const <EventCardDto>[],
          dayMeta: dayMeta,
          errorMessage: null,
        ),
        'meta_only',
      );
    });

    test(
      'hasUsableHomeDailyContent is false when daily card only carries a title',
      () {
        final dailyCard = EventCardDto.fromMap({
          'event_id': 'evt_daily_title_only',
          'headline': 'Bugunun karti',
          'felt_line_tr': 'Bugunun karti',
          'horizon': 'daily',
          'tags': {'phase': 'exact', 'duration': 'day', 'domain': 'general'},
        });

        expect(hasUsableHomeDailyCardCopy(dailyCard), isFalse);
        expect(
          hasUsableHomeDailyContent(
            dailyCards: <EventCardDto>[dailyCard],
            dayMeta: null,
          ),
          isFalse,
        );
        expect(
          hasHomeMetaOnlyContent(
            dailyCards: <EventCardDto>[dailyCard],
            dayMeta: null,
          ),
          isFalse,
        );
      },
    );

    test('hasHomeMetaOnlyContent is false when strong daily card exists', () {
      final dayMeta = NarrativeCalendarDay.fromMap({
        'date': '2026-04-08',
        'rating': 2,
        'heat': 2,
        'event_count': 1,
        'signals_count': 1,
        'has_signals': true,
        'is_critical': false,
        'labels': const <String>[],
        'critical_reasons': const <String>[],
        'signal_label_tr': 'Bugun tek tema var.',
        'tone_label_tr': 'yogun',
        'micro_summary_tr': 'Bugun bir sey aciliyor.',
      });
      final dailyCard = EventCardDto.fromMap({
        'event_id': 'evt_daily_copy',
        'headline': 'Bugunun karti',
        'opening': 'Bugun sende bir vurgu var.',
        'horizon': 'daily',
        'tags': {'phase': 'exact', 'duration': 'day', 'domain': 'general'},
      });

      expect(
        hasHomeMetaOnlyContent(
          dailyCards: <EventCardDto>[dailyCard],
          dayMeta: dayMeta,
        ),
        isFalse,
      );
    });

    test('buildHomeDayContext normalizes day key using profile timezone', () {
      final context = buildHomeDayContext(
        <String, dynamic>{'timezone': 'Europe/Istanbul'},
        utcNow: DateTime.utc(2026, 4, 14, 22, 30),
        localNow: DateTime.utc(2026, 4, 14, 22, 30),
      );

      expect(context.dayKey, '2026-04-15');
      expect(context.timezone, 'Europe/Istanbul');
      expect(context.source, 'profile_timezone');
    });

    test(
      'resolveHomeDailyResponseAnchorDay uses payload date when present',
      () {
        expect(
          resolveHomeDailyResponseAnchorDay({
            'selected_date': '2026-04-10',
            'public': {'anchor_date': '2026-04-09'},
          }, fallbackDayKey: '2026-04-08'),
          '2026-04-10',
        );
        expect(
          resolveHomeDailyResponseAnchorDay({
            'public': {'selected_date': '2026-04-11'},
          }, fallbackDayKey: '2026-04-08'),
          '2026-04-11',
        );
        expect(
          resolveHomeDailyResponseAnchorDay(
            const {},
            fallbackDayKey: '2026-04-08',
          ),
          '2026-04-08',
        );
      },
    );

    test(
      'shouldRunHomeCalendarDayFallback is true when raw daily cards are empty even with micro summary',
      () {
        final dayMeta = NarrativeCalendarDay.fromMap({
          'date': '2026-04-08',
          'rating': 2,
          'heat': 2,
          'event_count': 1,
          'signals_count': 1,
          'has_signals': true,
          'is_critical': false,
          'labels': const <String>[],
          'critical_reasons': const <String>[],
          'signal_label_tr': 'Bugun tek tema var.',
          'tone_label_tr': 'yogun',
          'micro_summary_tr': 'Bugun bir sey aciliyor.',
        });

        expect(
          shouldRunHomeCalendarDayFallback(
            rawDailyEventCardsCount: 0,
            dailyCards: const <EventCardDto>[],
            dayMeta: dayMeta,
          ),
          isTrue,
        );
        expect(
          homeCalendarDayFallbackReasonCode(
            rawDailyEventCardsCount: 0,
            dailyCards: const <EventCardDto>[],
            dayMeta: dayMeta,
          ),
          'daily_event_cards_empty',
        );
      },
    );
  });
}
