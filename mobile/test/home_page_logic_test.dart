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
      'buildHomeTransitSnapshot uses period_event_cards and promotes transit fallback for home hero',
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
        expect(snapshot.dailyCards, hasLength(1));
        expect(snapshot.dailyCards.first.horizon, 'daily');
        expect(snapshot.dailyCards.first.feltLineTr, tr('Transit Baslik'));
        expect(
          snapshot.dailyCards.first.whyItFeelsThisWayTr,
          tr('Transit acilisi'),
        );
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
  });
}
