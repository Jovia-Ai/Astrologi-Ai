// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Turkish (`tr`).
class AppLocalizationsTr extends AppLocalizations {
  AppLocalizationsTr([String locale = 'tr']) : super(locale);

  @override
  String get appTitle => 'SHOU';

  @override
  String get appStoreSubtitle => 'Sana özel astroloji deneyimi';

  @override
  String get appStoreShortDescription => 'SHOU, doğum haritan, transitlerin ve kişisel içgörü alanların arasında daha derin ve kişisel bir astroloji deneyimi sunar.';

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
  String get externalLinkOpenFailed => 'Bağlantı açılamadı.';

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
  String get menuInfoAndSupport => 'Bilgi ve destek';

  @override
  String get menuAccount => 'Hesap';

  @override
  String get menuInList => 'Listede';

  @override
  String get menuSoon => 'Yakında';

  @override
  String get menuSignOut => 'Çıkış yap';

  @override
  String get menuSignOutSubtitle => 'Mevcut oturumu kapat ve giriş ekranına dön.';

  @override
  String get restorePurchasesTitle => 'Satın Alımları Geri Yükle';

  @override
  String get restorePurchasesDescription => 'Daha önce yaptığın satın alımları veya abonelik erişimini bu cihazda yeniden eşitle.';

  @override
  String get restorePurchasesSuccess => 'Satın alımların geri yüklendi.';

  @override
  String get restorePurchasesNoActive => 'Geri yüklenecek aktif bir satın alım bulunamadı.';

  @override
  String get restorePurchasesError => 'Satın alımlar geri yüklenemedi. Lütfen tekrar dene.';

  @override
  String get privacyPolicyTitle => 'Gizlilik Politikası';

  @override
  String get privacyPolicyDescription => 'SHOU, hesabını oluşturmak, deneyimini kişiselleştirmek ve uygulama özelliklerini sunmak için gerekli verileri işler.';

  @override
  String get termsOfUseTitle => 'Kullanım Koşulları';

  @override
  String get termsOfUseDescription => 'SHOU\'yu kullanarak uygulamanın kullanım koşullarını ve sunulan dijital hizmetlere ilişkin kuralları kabul etmiş olursun.';

  @override
  String get supportTitle => 'Destek';

  @override
  String get supportDescription => 'Soruların, teknik bir problemin veya hesabınla ilgili bir desteğe ihtiyacın varsa bizimle iletişime geçebilirsin.';

  @override
  String get deleteAccountTitle => 'Hesabı Sil';

  @override
  String get deleteAccountDescription => 'Hesabını sildiğinde profilin, kişisel hesap verilerin ve uygulama içi erişimin kalıcı olarak kaldırılır. Bu işlem geri alınamaz.';

  @override
  String get deleteAccountDialogTitle => 'Hesabını silmek istediğine emin misin?';

  @override
  String get deleteAccountDialogBody => 'Bu işlem geri alınamaz. Hesabın ve ilişkili kişisel verilerin silinir. Aktif aboneliğin varsa App Store abonelik yönetimi ayrıca kontrol edilmelidir.';

  @override
  String get deleteAccountSubscriptionNote => 'Hesabını silmek, App Store üzerinden yönetilen aboneliğini otomatik olarak iptal etmez.';

  @override
  String get deleteAccountCancel => 'Vazgeç';

  @override
  String get deleteAccountConfirm => 'Hesabı Sil';

  @override
  String get deleteAccountSuccess => 'Hesabın silindi.';

  @override
  String get deleteAccountError => 'Hesabın silinemedi. Lütfen tekrar dene.';

  @override
  String get deleteAccountProgress => 'Hesap siliniyor...';

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
  String get profileAvatarHelperText => 'Profilini sana daha ait hissettirmek için bir fotoğraf ekleyebilirsin.';

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

  @override
  String aiFreeRemaining(int count) {
    return '$count ücretsiz kaldı';
  }

  @override
  String aiCreditsRemaining(int count) {
    return '$count kredi';
  }

  @override
  String get aiProActive => 'Pro aktif';

  @override
  String get aiSending => 'Aila düşünüyor...';

  @override
  String get aiPaywallTitle => 'Kredi veya Pro ile devam et';

  @override
  String get aiPaywallBody => '3 ücretsiz sorunu kullandın. Sohbete devam etmek için kredi paketi al veya Pro\'yu aç.';

  @override
  String get aiPaywallMembershipNote => 'SHOU\'nun daha derin yorumlarına ve premium deneyimine erişmek için üyeliğini başlatabilirsin. Mevcut satın alımın varsa aşağıdan geri yükleyebilirsin.';

  @override
  String get aiPaywallLoading => 'Ürünler yükleniyor...';

  @override
  String get aiPaywallUnavailable => 'Satın alma şu anda kullanılamıyor.';

  @override
  String get aiPaywallRestoreHint => 'Satın alma sonrası webhook bakiyeni güncellerken birkaç saniye bekleyip mesajını tekrar dene.';

  @override
  String get aiProductQ1Title => '1 soru';

  @override
  String get aiProductQ1Subtitle => 'Tek cevap kredisi';

  @override
  String get aiProductQ5Title => '5 soru';

  @override
  String get aiProductQ5Subtitle => 'Kısa kullanım için kredi paketi';

  @override
  String get aiProductQ15Title => '15 soru';

  @override
  String get aiProductQ15Subtitle => 'Yoğun kullanım için kredi paketi';

  @override
  String get aiProductProTitle => 'Aylık Pro';

  @override
  String get aiProductProSubtitle => 'Pro aktifken sınırsız sohbet';

  @override
  String get aiStorePriceUnavailable => 'Hazır değil';

  @override
  String get aiPurchasePending => 'Satın alma alındı. Birkaç saniye içinde mesajını tekrar dene.';

  @override
  String get aiPurchaseNotSupported => 'Satın alma yalnızca iOS ve Android\'de kullanılabilir.';

  @override
  String aiChatUnavailable(Object error) {
    return 'AI sohbet şu anda kullanılamıyor: $error';
  }

  @override
  String get peopleFormAddTitle => 'Kişi ekle';

  @override
  String get peopleFormEditTitle => 'Kişiyi düzenle';

  @override
  String get peopleFormNameRequired => 'Ad zorunlu.';

  @override
  String get peopleFormBirthDateRequired => 'Doğum tarihi zorunlu.';

  @override
  String get peopleFormBirthTimeOptional => 'Doğum saati (isteğe bağlı)';

  @override
  String get peopleFormBirthTimeHint => 'Doğum saatini bilmiyorsan boş bırakabilirsin.';

  @override
  String get peopleFormCityRequired => 'Şehir zorunlu.';

  @override
  String get peopleFormCountryRequired => 'Ülke zorunlu.';

  @override
  String get peopleFormSaving => 'Kaydediliyor...';

  @override
  String get peopleFormLoginRequired => 'Kişi eklemek için önce giriş yap.';

  @override
  String peopleFormSaveFailed(Object error) {
    return 'Kişi kaydedilemedi: $error';
  }

  @override
  String get peoplePageLabel => 'Kişiler';

  @override
  String get peoplePageCenterText => 'çevren';

  @override
  String get peoplePageAddTooltip => 'Kişi ekle';

  @override
  String get peoplePageEmptyTitle => 'Henüz kayıtlı kişi yok';

  @override
  String get peoplePageEmptyBody => 'Bond ve sosyal akışlarda kullanmak için çevrenden kişileri burada kaydedebilirsin.';

  @override
  String get peoplePageCircleLabel => 'Çevren';

  @override
  String get peoplePageCircleTitle => 'Kayıtlı kişiler';

  @override
  String get peoplePageCircleBody => 'Bond, arkadaş profilleri ve sosyal akışlar için kullandığın kişi listesi burada görünür.';

  @override
  String get peoplePageHeroLabel => 'Kişiler';

  @override
  String get peoplePageHeroTitle => 'Bond ve sosyal akışların için çevreni burada tut';

  @override
  String get peoplePageHeroBody => 'Eklediğin kişiler bond eşleşmeleri, arkadaş profilleri ve daha sonra açılacak sosyal okumalar için aynı yerden kullanılır.';

  @override
  String get peoplePagePillAura => 'Aura';

  @override
  String get peoplePagePillBirthAxis => 'Doğum ekseni';

  @override
  String get peoplePagePillSocialTone => 'Sosyal ton';

  @override
  String get peoplePageListLoadFailedTitle => 'Kişi listesi alınamadı';

  @override
  String peoplePageListLoadFailed(Object error) {
    return 'Kişi listesi yüklenemedi: $error';
  }

  @override
  String get peoplePageFriendLabel => 'Kişi';

  @override
  String get peoplePageNoBirthTime => 'Doğum saati yok';

  @override
  String get peoplePageEditTooltip => 'Düzenle';

  @override
  String get peopleRepoListFailed => 'Kişi listesi alınamadı.';

  @override
  String get peopleRepoDetailFailed => 'Kişi detayı alınamadı.';

  @override
  String get peopleRepoCreateFailed => 'Kişi oluşturulamadı.';

  @override
  String get peopleRepoUpdateFailed => 'Kişi güncellenemedi.';

  @override
  String get peopleRepoProfilesListUnsupported => 'Profiles tablosu kayıtlı kişileri listelemeyi desteklemiyor.';

  @override
  String get peopleRepoProfilesDetailUnsupported => 'Profiles tablosu bu kayıtlı kişiyi okumayı desteklemiyor.';

  @override
  String get peopleRepoProfilesCreateUnsupported => 'Profiles tablosu ayrı kayıtlı kişi oluşturmayı desteklemiyor.';

  @override
  String peopleRepoTableNotFound(Object candidates) {
    return 'Kişi kayıtları için uygun tablo bulunamadı. Denenenler: $candidates';
  }

  @override
  String get peopleRepoTableValidationFailed => 'Kişi tablosu doğrulanamadı.';

  @override
  String get forumActiveTransitFallback => 'Gökyüzü hareketli';

  @override
  String get transitSkyCollectiveFallback => 'Kolektifte hareket var.';

  @override
  String get transitSkyTypeIngress => 'Yeni alan';

  @override
  String get transitSkyTypeFullMoon => 'Dolunay';

  @override
  String get transitSkyTypeNewMoon => 'Yeniay';

  @override
  String get transitSkyTypeExactAspect => 'Keskin açı';

  @override
  String get transitSkyTypeEclipse => 'Tutulma';

  @override
  String get transitSkyTypeRetroStart => 'Retro başlıyor';

  @override
  String get transitSkyTypeRetroEnd => 'Retro bitiyor';

  @override
  String get transitSkyTimingNow => 'Şimdi';

  @override
  String get transitSkyTimingThisWeek => 'Bu hafta';

  @override
  String get transitMeaningRelationships => 'İlişkiler';

  @override
  String get transitMeaningMoney => 'Para';

  @override
  String get transitMeaningVisibility => 'Görünürlük';

  @override
  String get transitMeaningDecision => 'Karar';

  @override
  String get transitMeaningCloseness => 'Yakınlık';

  @override
  String get transitMeaningBuilding => 'İnşa';

  @override
  String get transitMeaningRelease => 'Bırakma';

  @override
  String get transitMeaningTension => 'Gerilim';

  @override
  String get transitMeaningClarifying => 'Netleşme';

  @override
  String get transitMeaningTransformation => 'Dönüşüm';

  @override
  String get profileDetailFallbackEyebrow => 'Derin okuma';

  @override
  String get profileDetailFallbackTitle => 'Bu kart için detay hazırlanıyor';

  @override
  String get profileDetailFallbackIntro => 'Ana anlatı akışı şu an boş döndü.';

  @override
  String get profileDetailFallbackBody => 'Kartın anlamı yine burada açılacak; şu an içerik akışının gelmesini bekliyoruz.';

  @override
  String get bondSelfName => 'Ben';

  @override
  String get bondPageSelectPerson => 'Kişi seç';

  @override
  String get bondPageLensFallback => 'bağ lensi';

  @override
  String get bondPageHeroTitle => 'İki kişi arasındaki dinamiği buradan aç';

  @override
  String get bondPageHeroBody => 'Kendi profilinle kayıtlı bir kişiyi seç, sonra aranızdaki ana ritmi ve gerilim hattını aynı akışta oku.';

  @override
  String get bondPageLensLabel => 'Lens';

  @override
  String get bondPageBirthDataMissingTitle => 'Bond için doğum verisi gerekli';

  @override
  String get bondPageBirthDataMissingBody => 'Kendi doğum tarihi ve konum bilgini tamamladığında bu eşleşme daha doğru açılır.';

  @override
  String get bondPagePreparing => 'Hazırlanıyor...';

  @override
  String get bondPageOpenResult => 'Bond sonucunu aç';

  @override
  String bondPageAnalyzeFailed(Object error) {
    return 'Bond analizi alınamadı: $error';
  }

  @override
  String get bondPickerLabel => 'Kişi seçimi';

  @override
  String get bondPickerTitle => 'Bond için ikinci kişiyi seç';

  @override
  String get bondPickerAddPerson => 'Yeni kişi ekle';

  @override
  String get bondPickerOwnProfile => 'Kendi profilin';

  @override
  String get bondPickerMe => 'Sen';

  @override
  String bondPickerLoadFailed(Object error) {
    return 'Kişiler yüklenemedi: $error';
  }

  @override
  String get bondPairEyebrow => 'Seçim';

  @override
  String get bondPairTitle => 'İki kişiyi karşılaştır';

  @override
  String get bondPairBody => 'İki profili seç, sonra aralarındaki bağın ana ritmini aynı akışta gör.';

  @override
  String get storyStudioTopLabel => 'Story Studio';

  @override
  String get storyStudioTopCenter => 'iz kartları';

  @override
  String get storyStudioLoadingProfile => 'Profil yükleniyor...';

  @override
  String get storyStudioBirthDataRequired => 'Story Studio açılmadan önce doğum tarihi, saati ve konumu gerekli.';

  @override
  String get storyStudioIdentityTitle => 'Kimlik kartları';

  @override
  String get storyStudioIdentityBody => 'Haritandaki baskın yerleşimleri, iç itkiyi ve gölge hattını kart kart aç.';

  @override
  String get storyStudioIdentityTab => 'Kimlik';

  @override
  String get storyStudioMomentTitle => 'Canlı kaynaklar';

  @override
  String get storyStudioMomentBody => 'Şu an çalışan yüzeylere dön ve aktif akışları oradan aç.';

  @override
  String get storyStudioMomentTab => 'An';

  @override
  String get storyStudioCardsLoadFailed => 'Kartlar yüklenemedi';

  @override
  String get storyStudioCardsPreparing => 'Kartlar hazırlanıyor';

  @override
  String get storyStudioCardsPreparingBody => 'Kişilik imprint katmanı backend\'den çekiliyor.';

  @override
  String get storyStudioCardsNotFound => 'Kart bulunamadı';

  @override
  String get storyStudioCardsNotFoundBody => 'Bu profilden henüz Story Studio kartı üretilemedi.';

  @override
  String get storyStudioMomentPanelTitle => 'Canlı stüdyo kaynakları';

  @override
  String get storyStudioMomentPanelBody => 'Bu bölüm yeni kart üretmez; seni aktif Home ve Bond yüzeylerine geri gönderir.';

  @override
  String get storyStudioReturnToSources => 'Kaynaklara dön';

  @override
  String get storyStudioTraitLabel => 'Öne çıkan çizgi';

  @override
  String get storyStudioInnerDriveLabel => 'İç itki';

  @override
  String get storyStudioWhenTooMuchLabel => 'Zorlandığında';

  @override
  String get storyStudioRefreshing => 'Yenileniyor...';

  @override
  String get storyStudioKindAspect => 'Açı';

  @override
  String get storyStudioKindHousePlacement => 'Ev yerleşimi';

  @override
  String get storyStudioKindSignPlacement => 'Burç yerleşimi';

  @override
  String get storyStudioKindLayer => 'Katman';

  @override
  String storyStudioLoadFailed(Object error) {
    return 'Story Studio yüklenemedi: $error';
  }

  @override
  String get relationshipPreviewLabel => 'İlişki görünümü';

  @override
  String get relationshipPreviewBirthDataRequiredTitle => 'İlişki görünümü için doğum verisi gerekli';

  @override
  String get relationshipPreviewBirthDataRequiredBody => 'Doğum tarihi, saati ve konum bilgisi tamamlandığında ilişki hattı burada açılır.';

  @override
  String get relationshipPreviewLoadFailedTitle => 'İlişki akışı alınamadı';

  @override
  String get relationshipPreviewMainThemeLabel => 'Ana tema';

  @override
  String get relationshipPreviewDriversLabel => 'Bugünü kuran etkiler';

  @override
  String get relationshipPreviewBackdropLabel => 'Arka plan';

  @override
  String get relationshipPreviewUpperMeaningLabel => 'Üst anlam';

  @override
  String get relationshipPreviewSupportingThemeLabel => 'Yan tema';

  @override
  String get relationshipPreviewWhyImportant => 'Neden burada';

  @override
  String get relationshipPreviewFallbackNotice => 'İlişki lensi yavaş döndüğü için ekran daha genel yorumla açıldı.';

  @override
  String get relationshipPreviewTimeout => 'İlişki yorumu zamanında dönmedi. Biraz sonra tekrar deneyebilirsin.';

  @override
  String get relationshipPreviewInvalidProfile => 'Gönderilen profil verisi ilişki akışı için yeterli değil.';

  @override
  String get relationshipPreviewServerError => 'İlişki akışı şu an sunucudan alınamıyor.';

  @override
  String get relationshipPreviewFetchFailed => 'İlişki akışı alınamadı.';

  @override
  String get relationshipPreviewStageStarted => 'Başladı';

  @override
  String get relationshipPreviewStageIntensifying => 'Yoğunlaşıyor';

  @override
  String get relationshipPreviewStagePeak => 'Zirve';

  @override
  String get relationshipPreviewStageResolving => 'Çözülüyor';

  @override
  String get relationshipPreviewPeriodToToday => 'Dönemden bugüne';

  @override
  String get relationshipPreviewDefaultDriversFallback => 'Bugün ilişki tarafında hareket var, ama tek bir tema henüz tam olarak ayrışmıyor.';

  @override
  String get relationshipPreviewDefaultBackdropFallback => 'Altta çalışan dönem hattı var, ama bunun ilişki tarafındaki asıl sonucu biraz daha zamanla netleşecek.';

  @override
  String get friendProfileTitle => 'Kişi profili';

  @override
  String get friendProfileNotFound => 'Kişi bulunamadı.';

  @override
  String get friendProfileEditTooltip => 'Kişiyi düzenle';

  @override
  String friendProfileLoadFailed(Object error) {
    return 'Kişi yüklenemedi: $error';
  }

  @override
  String get profileDetailInfluences => 'Etkileyenler';

  @override
  String get profileDetailAllCards => 'Tüm kartlar';

  @override
  String get profileDetailSignatureCardsTitle => 'Kişilik imzası kartları';

  @override
  String get profileDetailDefaultEyebrow => 'Detay';

  @override
  String get profileDetailDefaultTitle => 'Detay akışı';

  @override
  String get profileDetailWhyHere => 'Neden burada';

  @override
  String profileDetailNextLabel(Object title) {
    return 'Sıradaki: $title';
  }

  @override
  String profileDetailContinuationTitle(Object title) {
    return '$title · Devam';
  }

  @override
  String get profileDetailSideA => 'Bir tarafı';

  @override
  String get profileDetailSideB => 'Diğer tarafı';

  @override
  String get profileDetailContinueFlow => 'Akışı sürdür';

  @override
  String get profileDetailContinueFromHere => 'Buradan devam et';

  @override
  String profileDetailContinuationFooter(int page, int total) {
    return 'Devam $page/$total';
  }

  @override
  String get profileDetailFlowEnds => 'Akış burada bitiyor';

  @override
  String get periodFallbackEffectTitle => 'Dönem etkisi';

  @override
  String periodIntentSummaryGeneric(Object title) {
    return '$title için bu dönemde takip edilecek pencereler var.';
  }

  @override
  String periodIntentTopDays(Object title, Object dates) {
    return '$title odağı için öne çıkan günler: $dates.';
  }

  @override
  String periodIntentScores(Object ratings) {
    return 'Puanlar: $ratings';
  }

  @override
  String get periodIntentBeautyCare => 'Bakım ve Beden';

  @override
  String get periodIntentBusiness => 'İş ve Üretim';

  @override
  String get periodIntentMoney => 'Para ve Kaynak';

  @override
  String get periodIntentRelationship => 'İlişki ve Uyum';

  @override
  String periodIntentLabel(int index) {
    return 'Niyet $index';
  }

  @override
  String get periodDefaultTitle => 'Dönem';

  @override
  String get periodMainFlowFallback => 'Bu dönemin ana akışı.';

  @override
  String get periodMainThemeFallback => 'Bu dönemin ana teması.';

  @override
  String get periodHighlightedThemeFallback => 'Bu dönemde öne çıkan tema.';

  @override
  String get periodThemeCollectFallback => 'Bu dönemde öne çıkan tema burada toplanır.';

  @override
  String get periodEssenceTitle => 'Bu dönemin özü';

  @override
  String get periodSummaryUnavailable => 'Bu döneme ait özet anlatım bulunamadı.';

  @override
  String get periodTimeLabel => 'Zaman';

  @override
  String get periodGuidancePrefix => 'Küçük pratik:';

  @override
  String get periodDifficultyPrefix => 'Bunu zorlaştıran şey genelde şu olur:';

  @override
  String get periodHowItWorksTitle => 'Nasıl çalışıyor';

  @override
  String get periodAsksTitle => 'Senden ne istiyor';

  @override
  String get periodWatchTitle => 'Dikkat edilmesi gereken';

  @override
  String get periodBuildsTitle => 'Sende neyi geliştiriyor';

  @override
  String get periodEffectLabel => 'Etki';

  @override
  String get periodTechnicalNoteLabel => 'Teknik not';

  @override
  String get periodCoreMainThemeTitle => 'Bu Dönemin Ana Teması';

  @override
  String get periodCoreSummaryUnavailable => 'Bu dönem için period özeti bulunamadı.';

  @override
  String get profileExperimentPreviewLabel => 'Preview';

  @override
  String get profileExperimentCenterText => 'Nocturne Identity';

  @override
  String get profileExperimentMenuTooltip => 'Tema ve deney ayarları';

  @override
  String get profileExperimentHeroFallback => 'Haritanın ilk izi burada toplanır.';

  @override
  String get profileExperimentSignatureFallback => 'Kimlik izi';

  @override
  String get profileExperimentNatalPanelBody => 'Bu preview, kimliği tam portre hissiyle açan spotlight hero üzerinde çalışıyor. Alt chapter katmanları sonraki patchte eklenecek.';

  @override
  String get profileExperimentTimingPanelBody => 'Timing modu burada sadece odak değişimi gibi davranır. Alt dönem kompozisyonu sonraki patchte gelecek.';

  @override
  String get profileExperimentMenuTitle => 'Nocturne experiment';

  @override
  String get profileExperimentMenuBody => 'Patch 1 sadece üst kimlik kompozisyonunu dener.';

  @override
  String get profileExperimentSeeProfile => 'Profili gör';

  @override
  String get profileExperimentHeroLineFallback => 'Kimliğin bu ekranda yeni bir odak yüzeyine toplanır.';

  @override
  String get profileExperimentAuraLabel => 'Aura';

  @override
  String get profileExperimentRulerLabel => 'Yönetici';

  @override
  String get profileExperimentWaiting => 'Bekliyor';

  @override
  String get profileExperimentRulerBodyFallback => '1. ev yöneticisi okunuyor';

  @override
  String get profileExperimentRisingTrace => 'Yükselen izi';

  @override
  String get profileExperimentSignatureLabel => 'İmza';

  @override
  String get profileExperimentSpotlightCards => 'Spotlight Cards';

  @override
  String get profileExperimentSwipe => 'Kaydır';

  @override
  String get profileExperimentFocusTitle => 'Okuma odağı';

  @override
  String get profileExperimentNatalFocus => 'Senin Yapın';

  @override
  String get profileExperimentTimingFocus => 'Şu Anki Dönemin';

  @override
  String get profileExperimentUnnamedProfile => 'İsimsiz Profil';

  @override
  String get profileExperimentFireDominant => 'Ateş baskın';

  @override
  String get profileExperimentWaterDominant => 'Su baskın';

  @override
  String get profileExperimentAirDominant => 'Hava baskın';

  @override
  String get profileExperimentEarthDominant => 'Toprak baskın';

  @override
  String get errorTimeout => 'Sunucu şu an yavaş, birazdan tekrar dene.';

  @override
  String get errorNoConnection => 'Bağlantı kurulamadı.';

  @override
  String get errorGeneric => 'Bir sorun oluştu, tekrar dene.';
}
