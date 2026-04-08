// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Turkish (`tr`).
class AppLocalizationsTr extends AppLocalizations {
  AppLocalizationsTr([String locale = 'tr']) : super(locale);

  @override
  String get appTitle => 'Astrologi AI';

  @override
  String get supabaseConfigErrorTitle => 'Supabase Konfigürasyon Hatası';

  @override
  String get supabaseConfigErrorBody => 'Supabase başlatılamadı. Lütfen SUPABASE_URL ve SUPABASE_ANON_KEY değerlerini ekleyin.';

  @override
  String get supabaseConfigErrorExample => 'Örnek:\nflutter run --dart-define=SUPABASE_URL=https://YOUR_PROJECT.supabase.co --dart-define=SUPABASE_ANON_KEY=YOUR_KEY';

  @override
  String get loginTitle => 'Tekrar hoş geldin';

  @override
  String get loginBody => 'Hesabına gir ve kaldığın yerden devam et.';

  @override
  String get emailLabel => 'Email';

  @override
  String get passwordLabel => 'Şifre';

  @override
  String get confirmPasswordLabel => 'Şifreyi doğrula';

  @override
  String get nameLabel => 'Ad';

  @override
  String get birthDateLabel => 'Doğum tarihi (YYYY-MM-DD)';

  @override
  String get birthTimeLabel => 'Doğum saati (HH:mm)';

  @override
  String get cityLabel => 'Şehir';

  @override
  String get countryLabel => 'Ülke';

  @override
  String get loginSignIn => 'Giriş yap';

  @override
  String get authOr => 'veya';

  @override
  String get loginContinueWithGoogle => 'Google ile devam et';

  @override
  String get loginCreateAccount => 'Hesap oluştur';

  @override
  String get loginForgotPassword => 'Şifremi unuttum';

  @override
  String get loginPasswordResetSent => 'Şifre sıfırlama maili gönderildi';

  @override
  String get loginGoogleStartFailed => 'Google giriş akışı başlatılamadı.';

  @override
  String get registerTopLabel => 'Kayıt';

  @override
  String get registerTopCenter => 'yeni hesap';

  @override
  String get registerSectionLabel => 'Başlangıç';

  @override
  String get registerTitle => 'Profil ritmine giriş yap';

  @override
  String get registerBody => 'Hesabını oluştur, sonra profil ve doğum katmanlarını aynı tipografik sistemde tamamla.';

  @override
  String get registerCreateAccount => 'Hesap oluştur';

  @override
  String get registerBackToLogin => 'Girişe dön';

  @override
  String get registerPasswordsDoNotMatch => 'Şifreler eşleşmiyor.';

  @override
  String get onboardingSectionLabel => 'Onboarding';

  @override
  String get onboardingBirthTopLabel => 'Doğum';

  @override
  String get onboardingBirthTopCenter => 'temel veriler';

  @override
  String get onboardingBirthTitle => 'Haritanın doğum eksenini tamamla';

  @override
  String get onboardingBirthBody => 'Bu bilgiler backend akışına aynen gider; bu ekran sadece yüzeyi profil diliyle hizalar.';

  @override
  String get onboardingProfileTopLabel => 'Profil';

  @override
  String get onboardingProfileTopCenter => 'kurulum';

  @override
  String get onboardingProfileTitle => 'Kimlik ve doğum alanını aynı yerde kur';

  @override
  String get onboardingProfileBody => 'Form mantığı aynı kalır; sadece tipografik omurga artık profil sayfasıyla hizalıdır.';

  @override
  String get commonContinue => 'Devam et';

  @override
  String get commonRetry => 'Tekrar dene';

  @override
  String get commonOpen => 'Aç';

  @override
  String get commonSave => 'Kaydet';

  @override
  String get tabsHome => 'Ana sayfa';

  @override
  String get tabsBond => 'Bond';

  @override
  String get tabsStoryStudio => 'Story Studio';

  @override
  String get tabsAiChat => 'AI Sohbet';

  @override
  String get tabsProfile => 'Profil';

  @override
  String get homePlansTitle => 'Senin planların';

  @override
  String get homePlansSubtitle => 'Bu hafta akışın ve kolektif nabız yan yana.';

  @override
  String get homeSignalFallback => 'Bugün öne çıkan tema bu.';

  @override
  String get homeActivePeriodTitle => 'Aktif dönem';

  @override
  String get homeActivePeriodBody => 'Bu dönemde arkada çalışan transit teması burada açılıyor.';

  @override
  String get homeStoryLoading => 'Bugünün hikayesi yükleniyor...';

  @override
  String get homeStoryUnavailable => 'Bugün için kısa yorum henüz hazır değil.';

  @override
  String get homeDailyTransitLabel => 'Günlük transit';

  @override
  String get homeHeroOpening => 'Bugünün açılışı';

  @override
  String get homeHeroPrompt => 'Bugün bende ne açılıyor?';

  @override
  String get homeHeroQuestionTitle => 'Bugünün açılış sorusu';

  @override
  String get homeGoToCalendar => 'Takvime geç';

  @override
  String get homeCollectivePulse => 'Kolektif nabız';

  @override
  String get homeDayPlan => 'Günün planı';

  @override
  String get homeCalendarTitle => 'Takvim';

  @override
  String get homeWeekFlowOpen => 'Önündeki 1 haftalık akışı aç.';

  @override
  String get homeWeekView => '1 haftalık görünüm';

  @override
  String get homeWeeklyCalendar => 'Haftalık takvim';

  @override
  String get homeWeeklyCalendarBody => 'Mevcut takvim akışını küçük görünümden aç ve tüm haftayı gör.';

  @override
  String get homePeriodCardsPending => 'Period kartları hazır olduğunda burada görünecek.';

  @override
  String get homeActiveThemePending => 'Aktif tema bekleniyor';

  @override
  String get homeActiveThemeBody => 'Period akışından gelen aktif tema burada kompakt kart olarak görünecek.';

  @override
  String get homeOpenTheme => 'Temayı aç';

  @override
  String get homeNowActive => 'Şimdi aktif';

  @override
  String get homeOpenTopicsTitle => 'Açık konular';

  @override
  String get homeOpenTopicsBody => 'Kolektifte şu an çalışan tüm başlıklara buradan gir.';

  @override
  String get homeAllTopics => 'Tüm konular';

  @override
  String get homePrimaryMeta => 'Ana';

  @override
  String get homeCollectiveMeta => 'Kolektif';

  @override
  String get homeWeekMeta => 'Hafta';

  @override
  String get homeTimingMeta => 'Timing';

  @override
  String get homeOpenDetail => 'Detayı aç';

  @override
  String homeDataLoadFailed(Object error) {
    return 'Home verisi alınamadı: $error';
  }

  @override
  String get homeRequestTimedOut => 'Bugünkü home okuması uzun sürdü. Ekran daha hafif veriyle açıldı; biraz sonra tekrar deneyebilirsin.';

  @override
  String get authGateBirthDataErrorTitle => 'Hesabın açık, veri kontrolü başarısız';

  @override
  String get authGateBirthDataErrorBody => 'Supabase bağlantısına şu an ulaşılamıyor. Bu yüzden seni eksik doğum verisi ekranına atmak yerine burada bekletiyoruz. Bağlantı gelince tekrar dene.';

  @override
  String get sessionExpiredLoginAgain => 'Oturum süresi doldu. Lütfen tekrar giriş yap.';

  @override
  String errorFailedToLoadBirthData(Object error) {
    return 'Doğum verileri yüklenemedi: $error';
  }

  @override
  String errorFailedToSaveBirthData(Object error) {
    return 'Doğum verileri kaydedilemedi: $error';
  }

  @override
  String get errorPleaseFillBirthFields => 'Lütfen doğum tarihi, saat, şehir ve ülke alanlarını doldur.';

  @override
  String errorFailedToLoadProfile(Object error) {
    return 'Profil yüklenemedi: $error';
  }

  @override
  String errorFailedToSaveProfile(Object error) {
    return 'Profil kaydedilemedi: $error';
  }

  @override
  String get errorPleaseFillAllFields => 'Lütfen tüm alanları doldur.';

  @override
  String get menuQuickAccess => 'Hızlı geçiş';

  @override
  String get menuEditProfile => 'Profili düzenle';

  @override
  String get menuEditProfileSubtitle => 'Bilgilerini ve profil ayarlarını aç.';

  @override
  String get menuManagePeople => 'Kişileri yönet';

  @override
  String get menuAddPerson => 'Kişi ekle';

  @override
  String get menuPeopleSubtitle => 'Bond ve sosyal akışlar için kayıtlı kişi listesini aç.';

  @override
  String get menuCalendar => 'Takvim ve timing';

  @override
  String get menuCalendarSubtitle => 'Gün ritmi, dönemler ve best times.';

  @override
  String get menuArchetypeExperience => 'Arketip deneyimi';

  @override
  String get menuCompleteBirthData => 'Doğum verini tamamla';

  @override
  String get menuArchetypeSubtitle => 'Kimlik eksenini derin deneyimde aç.';

  @override
  String get menuCompleteBirthDataSubtitle => 'Arketip ekranlarını açmak için eksik veriyi tamamla.';

  @override
  String get menuPreferences => 'Tercihler';

  @override
  String get menuThemeMode => 'Tema modu';

  @override
  String get themeModeDark => 'Koyu';

  @override
  String get themeModeLight => 'Açık';

  @override
  String get menuLanguage => 'Dil';

  @override
  String get menuNotificationPreferences => 'Bildirim tercihleri';

  @override
  String get menuDailySummary => 'Günlük özet';

  @override
  String get menuDailySummarySubtitle => 'Sabah kısa ritim özeti';

  @override
  String get menuSkyEvents => 'Gök olayları';

  @override
  String get menuSkyEventsSubtitle => 'Öne çıkan transit ve event uyarıları';

  @override
  String get menuSocialActivity => 'Sosyal hareket';

  @override
  String get menuSocialActivitySubtitle => 'Forum ve ilişki tarafındaki gelişmeler';

  @override
  String get menuMembership => 'Üyelik';

  @override
  String get menuPremiumSubscription => 'Premium abonelik';

  @override
  String get menuPremiumInterestSubtitle => 'Listedesin. Premium açıldığında haber vereceğiz.';

  @override
  String get menuPremiumDefaultSubtitle => 'Daha uzun yorumlar ve geniş akışlar için derin katman.';

  @override
  String get menuInList => 'Listede';

  @override
  String get menuSoon => 'Yakında';

  @override
  String get menuSignOut => 'Çıkış yap';

  @override
  String get menuSignOutSubtitle => 'Mevcut oturumu kapat ve giriş ekranına dön.';

  @override
  String menuPeopleCount(int count) {
    return '$count kişi';
  }

  @override
  String get menuArchetypeReady => 'Arketip hazır';

  @override
  String get menuBirthDataMissing => 'Doğum verisi eksik';

  @override
  String get premiumSheetTitle => 'Premium abonelik';

  @override
  String get premiumSheetBody => 'Daha uzun yorumlar, daha fazla derinlik ve erken erişim için premium katman hazırlanıyor.';

  @override
  String get premiumBulletIdentity => 'Uzun kimlik ve ilişki okumaları';

  @override
  String get premiumBulletTiming => 'Ekstra timing ve dönem derinliği';

  @override
  String get premiumBulletEarlyAccess => 'Yeni özelliklere erken erişim';

  @override
  String get premiumNotifyMe => 'Beni haberdar et';

  @override
  String get premiumAlreadyInList => 'Listedesin';

  @override
  String get premiumNotifySnackbar => 'Premium açıldığında sana haber vereceğiz.';

  @override
  String homeGreeting(Object name) {
    return 'Merhaba $name';
  }

  @override
  String homeTodayLabel(Object date) {
    return 'Bugün $date';
  }

  @override
  String get homeGreetingFallbackName => 'sen';

  @override
  String get periodDetailTransitTitle => 'Transit Detayı';

  @override
  String get periodDetailPeriodTitle => 'Dönem Detayı';

  @override
  String get periodDetailTodayEyebrow => 'Bugün';

  @override
  String get periodDetailPeriodEyebrow => 'Süreç';

  @override
  String get periodDetailContextLabel => 'Bağlam';

  @override
  String get periodDetailContextTitle => 'Bu büyük dönemin parçası';

  @override
  String get periodDetailCoreLabel => 'Çekirdek';

  @override
  String get periodDetailCoreTitle => 'Bu etkinin merkez çizgisi';

  @override
  String get periodDetailSupportingLabel => 'Destekleyen';

  @override
  String get periodDetailSupportingTitle => 'Açılan diğer katmanlar';

  @override
  String get periodDetailTechnicalLabel => 'Teknik';

  @override
  String get periodDetailTechnicalTitle => 'Arka plan notları';

  @override
  String get calendarPanelLabel => 'Takvim';

  @override
  String get calendarMonthMode => 'Ay';

  @override
  String get calendarWeekMode => 'Hafta';

  @override
  String get calendarMonthIntro => 'Ay görünümünden bir güne dokunup o günün sayfasına geç.';

  @override
  String get calendarWeekIntro => 'Hafta görünümünde seçili haftaya odaklan, günü açıp detayda sağ-sol ilerle.';

  @override
  String get calendarPickDate => 'Tarih seç';

  @override
  String get calendarDayThemeLabel => 'Günün teması';

  @override
  String get calendarOpenDay => 'Günü aç';

  @override
  String get calendarSelectedDayFallback => 'Bir güne dokunduğunda o günün kartları, markerları ve uzun dönem bağlamı ayrıntılı açılır.';

  @override
  String get calendarContextLabel => 'Bağlam';

  @override
  String get calendarLongTermEffectTitle => 'Uzun dönem etkisi';

  @override
  String get calendarLongTermEffectFallback => 'Bu günün arkasında çalışan daha uzun bir dönem etkisi var.';

  @override
  String get calendarLongTermEffectReadMore => 'Günün arka planında çalışan dönem hikayesini gün sayfasında daha uzun okuyabilirsin.';

  @override
  String get calendarPreviewFallback => 'Yakın günleri hızlıca tara, bir güne dokunup gün sayfasına geç.';

  @override
  String get profileAvatarUpdated => 'Profil resmi güncellendi';

  @override
  String profileAvatarUploadFailed(Object error) {
    return 'Profil resmi yüklenemedi: $error';
  }

  @override
  String get profileInterpretationUnavailableTitle => 'Yorum akışı alınamadı';

  @override
  String get profileBirthDataPendingTitle => 'Doğum bilgisi bekleniyor';

  @override
  String get profileBirthDataPendingBodyDark => 'Bu ekran `core_story_ui`, `profile_narrative`, `personality_imprint` ve `insight_modules` alanlarıyla doluyor. Profil ayarlarından doğum tarihini, saati ve yeri tamamladığında içerik otomatik açılır.';

  @override
  String get profileBirthDataPendingBodyLight => 'Bu ekran core story, profile narrative ve insight alanlarıyla doluyor. Doğum tarihini, saati ve yeri tamamladığında içerik otomatik açılır.';

  @override
  String get profileIdentityAxis => 'Kimlik ekseni';

  @override
  String get profileMainStory => 'Ana Hikayen';

  @override
  String get profileOpenFullReading => 'Tam okumayı aç';

  @override
  String get profileSignatureLayers => 'İmza Katmanları';

  @override
  String get profileSideThemes => 'Yan Temalar';

  @override
  String get profileWarning => 'Uyarı';

  @override
  String get profileBack => 'Geri dön';

  @override
  String get profileOpenRelationshipFlow => 'İlişki akışını aç';

  @override
  String get profileOpenTimingFlow => 'Timing akışını aç';

  @override
  String get profileReturnToChartFlow => 'Harita akışına dön';

  @override
  String get profileConnectionsLabel => 'Connections';

  @override
  String get profileConnectionsTitle => 'Eklediğin kişiler';

  @override
  String get profileConnectionsBody => 'Takip ve takipçi alanından açılan gerçek arkadaş listen burada görünüyor.';

  @override
  String get profileFriendLabel => 'Friend';

  @override
  String get profileLocationMissing => 'konum eksik';

  @override
  String get profileFollowing => 'Takip';

  @override
  String get profileFollowers => 'Takipçi';

  @override
  String profileOpenSinglePersonProfile(Object name) {
    return '$name profiline git';
  }

  @override
  String profileOpenManyPersonProfiles(int count) {
    return '$count arkadaş profiline bak';
  }

  @override
  String get profileSunLabel => 'Güneş';

  @override
  String get profileRisingLabel => 'Yükselen';

  @override
  String get profileMoonLabel => 'Ay';

  @override
  String get profileIdentityLabel => 'KİMLİK';

  @override
  String get profileIdentityReading => 'Kimlik okuması';

  @override
  String get profileOpenIdentityReading => 'Kimlik okumasını aç';

  @override
  String get profileGenerateResult => 'Sonucu oluştur';

  @override
  String profileConfidenceScore(Object score) {
    return 'Güven skoru $score';
  }

  @override
  String profileNatalLoadFailed(Object error) {
    return 'Natal yorum alınamadı: $error';
  }

  @override
  String get profileTimingFlowLabel => 'TIMING AKIŞI';

  @override
  String get profileTimingFlowUnavailable => 'Timing akışı alınamadı';

  @override
  String get profileTimingFlowNotReady => 'Timing akışı hazır değil';

  @override
  String get profileTimingFlowNotReadyBody => 'Dönem özeti geldiğinde burada sadece kısa bir teaser ve yaklaşan pikler görünecek.';

  @override
  String get profileCurrentPeriod => 'Şu anki dönem';

  @override
  String get profileUpcomingPeaks => 'Yaklaşan pikler';

  @override
  String profileNextLabel(Object label) {
    return 'Sıradaki: $label';
  }

  @override
  String get profileMoreOpen => 'Daha fazla aç';

  @override
  String get profileNatal => 'Natal';

  @override
  String get profileRelationship => 'İlişki';

  @override
  String get profileTiming => 'Timing';

  @override
  String get profileMainReading => 'Ana okuma';

  @override
  String get profileShadowGrowth => 'Gölge & büyüme';

  @override
  String get profileIdentityEyebrow => 'Kimlik';

  @override
  String get profileIdentityFlow => 'Kimlik akışı';

  @override
  String get profileIdentityTone => 'Kimlik tonu';

  @override
  String get profileIdentitySummary => 'Kimlik özeti';

  @override
  String get profileArchetypeBirthDataRequired => 'Arketip deneyimini açmadan önce doğum tarihi, saati ve yeri gerekli.';

  @override
  String get profileIdentityFlowSubtitleFallback => 'Kimliğinin dışarıdan ve içeriden nasıl okunduğunu burada daha uzun gör.';

  @override
  String get profileNarrativeFlowSubtitleFallback => 'Bu bölümün sende nasıl çalıştığını burada daha açık okuyorsun.';

  @override
  String get profileSignatureCatalogSubtitle => 'Kart listesinde yalnızca başlıkları görürsün; bir karta basınca sadece onun detayı açılır.';

  @override
  String get profileSignatureCardSubtitleFallback => 'Bu kişilik imzası kartının tam açıklaması burada açılıyor.';

  @override
  String get profileSideThemesFlowSubtitle => 'Burada ana portreni tamamlayan diğer taraflar öne çıkıyor.';

  @override
  String get profileInsightFlowSubtitleFallback => 'Bu bölüm savunma ve büyüme eksenindeki tam akışı açıyor.';

  @override
  String get profileOpenDefensePattern => 'Savunma mekanizmanı aç';

  @override
  String get profileSeeArchetype => 'Arketipini gör';

  @override
  String get profileArchetypeBodyReady => 'Haritandaki aktif kimlik, koruma ve gerilim çizgilerini tek bir deneyimde aç.';

  @override
  String get profileArchetypeBodyPending => 'Doğum tarihi, saati ve yerini tamamladığında arketip deneyimi buradan açılacak.';

  @override
  String get profileCompleteBirthData => 'Doğum verini tamamla';

  @override
  String get profileOnlineFriends => 'ONLINE ARKADAŞLARIN';

  @override
  String get profileQuietSocialCircle => 'Daha sakin bir sosyal halka';

  @override
  String get profileIdentitySummaryFallback => 'Kimlik aksın profil anlatısından açılıyor.';

  @override
  String get profileNarrativeLoading => 'Profil anlatısı backend yorumundan çekiliyor...';

  @override
  String get profilePlacementsAndAspects => 'YERLEŞİM VE AÇILAR';

  @override
  String get profileOpenSideThemes => 'Yan temaları aç';

  @override
  String get profilePlacement => 'Yerleşim';

  @override
  String get profileAspect => 'Açı';

  @override
  String get profileSignTone => 'Burç tonu';

  @override
  String get profileFeaturedTheme => 'Öne çıkan tema';

  @override
  String get profileRuler => 'Yönetici';

  @override
  String profileStrongestRuler(Object name) {
    return 'En güçlü yönetici $name';
  }

  @override
  String profileSignRuler(Object sign) {
    return '$sign yöneticisi';
  }

  @override
  String get profileChartBackbone => 'Harita omurgası';

  @override
  String profileHouseEmphasis(int house) {
    return '$house. ev vurgusu';
  }

  @override
  String get profileEarthInfluential => 'Toprak etkili';

  @override
  String get profileOutsideInside => 'Dışarıdan ve içeriden';

  @override
  String get profileMindWorks => 'Zihnin nasıl çalışıyor';

  @override
  String get profileSelfProtection => 'Kendini nasıl koruyorsun';

  @override
  String get profileIntimacyOpens => 'Yakınlık sende nasıl açılıyor';

  @override
  String get profileHoldReleaseBalance => 'Tutma ve bırakma dengesi';

  @override
  String get profileWhereOpportunityFlows => 'Fırsatın aktığı yer';

  @override
  String get profileRecognizableLine => 'Sende kolay tanınan çizgi';

  @override
  String get profileTwoInnerDirections => 'İçeride iki yönün nasıl çalışıyor';

  @override
  String get profileStandoutSide => 'Sende öne çıkan taraf';

  @override
  String get profileElementFireDominant => 'Ateş baskın';

  @override
  String get profileElementWaterDominant => 'Su baskın';

  @override
  String get profileElementAirDominant => 'Hava baskın';

  @override
  String get profileElementEarthDominant => 'Toprak baskın';

  @override
  String get profileBirthPlacePending => 'Doğum yeri bekleniyor';

  @override
  String profileAgeLabel(int age) {
    return '$age yaş';
  }

  @override
  String get calendarSelectedDaySummaryPrompt => 'Seçili güne dokunup günün ritmini, kartlarını ve uzun dönem etkisini aç.';

  @override
  String get calendarMarkerDirectionChange => 'Yön değişimi';

  @override
  String get calendarMarkerNewArea => 'Yeni alan';

  @override
  String get calendarMarkerRetrograde => 'Geri akış';

  @override
  String get calendarMarkerPeak => 'Zirve';

  @override
  String get calendarMarkerBeginning => 'Başlangıç';

  @override
  String get calendarMarkerThreshold => 'Eşik';

  @override
  String get calendarMarkerMultipleThresholds => 'birden fazla eşik';

  @override
  String get calendarFallbackSensitiveDay => 'Hassas gün.';

  @override
  String get calendarFallbackHighTempo => 'Yüksek tempo.';

  @override
  String get calendarFallbackBusyDay => 'Bugün yoğun.';

  @override
  String get calendarFallbackTwoSignals => 'Bugün iki şey belirgin.';

  @override
  String get calendarFallbackOneSignal => 'Tek bir şey öne çıkıyor.';

  @override
  String get calendarFallbackMixedDay => 'Bugün biraz karışık.';

  @override
  String get calendarFallbackCalmDay => 'Bugün sakin.';

  @override
  String get calendarFallbackHooked => 'Bir şeylere bugün çabuk takılabilirsin.';

  @override
  String get calendarFallbackSeveralThings => 'Aynı anda birkaç şey dikkatini çekebilir.';

  @override
  String get calendarFallbackOneThingPushes => 'Tek bir şey günün ritmini biraz öne itiyor.';

  @override
  String get calendarFallbackSimpleRhythm => 'Bugün ritim biraz daha sade akıyor.';

  @override
  String get calendarFallbackBreath => 'Bir nefes daha iyi gelir.';

  @override
  String get calendarFallbackDoNotPileOn => 'Her şeye aynı anda yüklenme.';

  @override
  String get calendarFallbackDoNotRush => 'Acele etme.';

  @override
  String get calendarFallbackLeaveSimple => 'Bugünü biraz sade bırak.';

  @override
  String calendarHouseTouchpointHint(Object area) {
    return 'En çok $area tarafında belli olabilir.';
  }

  @override
  String get calendarEditorialCurrentFallback => 'Bugünün ritmi burada biraz daha okunur hale geliyor.';

  @override
  String get calendarEditorialChangeFallback => 'Bunun sende hangi tarafta daha çok belli olduğuna bak.';

  @override
  String get calendarEditorialDirectionFallback => 'Tema burada bitmiyor; önündeki günlerde biraz daha şekil kazanacak.';

  @override
  String get calendarEditorialSecondaryFallback => 'Bu da arka planda beraber çalışan ikinci bir katman.';

  @override
  String get calendarPhaseIntensifying => 'Yoğunlaşıyor';

  @override
  String get calendarPhasePeakToday => 'Bugün zirvede';

  @override
  String get calendarPhaseReleasing => 'Çözülmeye geçiyor';

  @override
  String calendarTimingPeak(Object date) {
    return 'Zirve $date';
  }

  @override
  String calendarTimingStart(Object date) {
    return 'Başlangıç $date';
  }

  @override
  String calendarTimingPrefix(Object timing) {
    return 'Zaman: $timing';
  }

  @override
  String calendarBestWindow(Object labels) {
    return 'Bu hafta iyi pencere: $labels';
  }

  @override
  String get calendarCombinedTitle => 'Birleşik takvim';

  @override
  String get calendarCombinedBody => 'Ay ve hafta akışını aynı yüzde takip et. Bir güne dokunduğunda o günün sayfası açılır ve uzun dönem bağlamı korunur.';

  @override
  String get calendarProfileLoadFailed => 'Profil verisi yüklenemedi.';

  @override
  String get calendarBirthDataRequiredTitle => 'Takvim için doğum verisi gerekiyor';

  @override
  String get calendarBirthDataRequiredBody => 'Doğum tarihi, saati ve yeri tamamlandığında takvim açılır.';

  @override
  String get calendarSectionNow => 'Şimdi ne oluyor';

  @override
  String get calendarSelectedDayWindows => 'Seçili gün pencereleri';

  @override
  String get calendarSectionChange => 'Bu sende neyi değiştiriyor';

  @override
  String get calendarSectionDirection => 'Nereye gidiyor';

  @override
  String get calendarSectionBackground => 'Derinde çalışan şey';

  @override
  String get calendarSectionSecondaryTheme => 'Ayrıca çalışan tema';

  @override
  String get calendarOpenMainTheme => 'Ana temayı aç';

  @override
  String get calendarOpenPeriod => 'Dönemi aç';

  @override
  String get calendarWhyItMatters => 'Neden bu önemli?';

  @override
  String get calendarLongTermLabel => 'Uzun dönem';

  @override
  String get calendarLongTermActiveTodayTitle => 'Uzun dönem bugün de etkili';

  @override
  String get calendarLongTermActiveTodayBody => 'Burası bugünün kendisi değil; bugünü arkadan taşıyan daha uzun hikaye.';

  @override
  String get calendarOpenCalendar => 'Takvimi aç';

  @override
  String calendarLongTermEffectPrefix(Object title) {
    return 'Uzun dönem etkisi: $title';
  }

  @override
  String get calendarBackgroundActive => 'arka planda aktif';

  @override
  String get calendarDailyReadingPreparing => 'Bu günün ana okuması hazırlanıyor.';

  @override
  String get calendarSelectedDayCalm => 'Seçili gün sakin';

  @override
  String get calendarNoDistinctEventCard => 'Bu gün için belirgin event kartı yok. Takvimden başka bir gün seçip akışı kontrol edebilirsin.';

  @override
  String get calendarMonthPanelBody => 'Takvim gibi görünen ay görünümü burada. Güne dokun, günlük datayı aynı akışta aç.';

  @override
  String get calendarTimingPersonalized => 'Sana özel zamanlama';

  @override
  String get calendarTimingPersonalizedBody => 'Önünde açılan dönemleri burada daha sakin bir sırayla okuyabilirsin.';

  @override
  String get calendarPeriodLabel => 'Period';

  @override
  String get calendarCurrentPeriodTheme => 'Bu dönemin ana teması';

  @override
  String get calendarTimingPreparing => 'Timing hazırlanıyor';

  @override
  String get calendarTimingPreparingBody => 'Kişisel dönemlerin editoryal listesi yükleniyor.';

  @override
  String get calendarNoSelectedPeriod => 'Seçili dönem yok';

  @override
  String get calendarNoSelectedPeriodBody => 'Aktif period kartları hazır olduğunda burada göreceksin.';

  @override
  String get calendarPeakListShort => 'Kısa peak listesi';

  @override
  String get calendarPeakListBody => 'Önündeki etkilerin güçlendiği tarihleri sırayla takip et.';

  @override
  String get calendarPeriodCardNotFound => 'Dönem kartı bulunamadı';

  @override
  String get calendarPeriodCardNotFoundBody => 'Period marker/kart bulunamadı.';

  @override
  String get calendarPeriodCardsTitle => 'Dönem kartları';

  @override
  String get calendarTransitTimeout => 'Transit özeti zamanında dönmedi. Dönem ekranını hafiflettim; tekrar dener misin?';

  @override
  String get calendarInvalidDateOrProfile => 'Gönderilen tarih veya profil alanları geçersiz (422).';

  @override
  String get calendarPeriodDataUnavailable => 'Period veri alınamadı.';

  @override
  String get calendarPeriodCoreFallbackTitle => 'Bu dönemin ana teması';

  @override
  String get calendarPeriodCoreFallbackBody => 'Period özeti henüz hazır değil.';

  @override
  String get calendarTodayForeground => 'Bugün en çok bu öne çıkıyor.';

  @override
  String get calendarPeriodFromBackgroundToday => 'Bugün kısa vadeli bir tetikten çok, arkada çalışan tema öne çıkıyor.';

  @override
  String get aiOnline => 'Çevrimiçi';

  @override
  String get aiIntroMessage => 'Merhaba, ben Aila. İstersen bugün hissettiğin şeyi, aklındaki bir konuyu ya da haritana dair merak ettiğin bir detayı yaz.';

  @override
  String get aiUserLabel => 'Sen';

  @override
  String get aiNow => 'Şimdi';

  @override
  String get aiComposerHint => 'Aila\'ya yaz...';
}
