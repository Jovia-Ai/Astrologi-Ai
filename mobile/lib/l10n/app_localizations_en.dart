// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for English (`en`).
class AppLocalizationsEn extends AppLocalizations {
  AppLocalizationsEn([String locale = 'en']) : super(locale);

  @override
  String get appTitle => 'SHOU';

  @override
  String get appStoreSubtitle => 'Your personal astrology space';

  @override
  String get appStoreShortDescription => 'SHOU offers a deeper, more personal astrology experience across your natal chart, transits, and personal insight spaces.';

  @override
  String get supabaseConfigErrorTitle => 'Supabase Configuration Error';

  @override
  String get supabaseConfigErrorBody => 'Supabase could not start. Please provide SUPABASE_URL and SUPABASE_ANON_KEY.';

  @override
  String get supabaseConfigErrorExample => 'Example:\nflutter run --dart-define=SUPABASE_URL=https://YOUR_PROJECT.supabase.co --dart-define=SUPABASE_ANON_KEY=YOUR_KEY';

  @override
  String get loginTitle => 'Welcome back';

  @override
  String get loginBody => 'Sign in and continue where you left off.';

  @override
  String get emailLabel => 'Email';

  @override
  String get passwordLabel => 'Password';

  @override
  String get confirmPasswordLabel => 'Confirm password';

  @override
  String get nameLabel => 'Name';

  @override
  String get birthDateLabel => 'Birth date (YYYY-MM-DD)';

  @override
  String get birthTimeLabel => 'Birth time (HH:mm)';

  @override
  String get cityLabel => 'City';

  @override
  String get countryLabel => 'Country';

  @override
  String get loginSignIn => 'Sign in';

  @override
  String get authOr => 'or';

  @override
  String get loginContinueWithGoogle => 'Continue with Google';

  @override
  String get loginCreateAccount => 'Create account';

  @override
  String get loginForgotPassword => 'Forgot password';

  @override
  String get loginPasswordResetSent => 'Password reset email sent';

  @override
  String get loginGoogleStartFailed => 'Google sign-in flow could not be started.';

  @override
  String get registerTopLabel => 'Sign up';

  @override
  String get registerTopCenter => 'new account';

  @override
  String get registerSectionLabel => 'Start';

  @override
  String get registerTitle => 'Create your profile rhythm';

  @override
  String get registerBody => 'Create your account, then complete your profile and birth layers inside the same typographic system.';

  @override
  String get registerCreateAccount => 'Create account';

  @override
  String get registerBackToLogin => 'Back to login';

  @override
  String get registerPasswordsDoNotMatch => 'Passwords do not match.';

  @override
  String get onboardingSectionLabel => 'Onboarding';

  @override
  String get onboardingBirthTopLabel => 'Birth';

  @override
  String get onboardingBirthTopCenter => 'core data';

  @override
  String get onboardingBirthTitle => 'Complete your birth axis';

  @override
  String get onboardingBirthBody => 'This data goes to the backend as-is; this screen only aligns the surface with the profile language.';

  @override
  String get onboardingProfileTopLabel => 'Profile';

  @override
  String get onboardingProfileTopCenter => 'setup';

  @override
  String get onboardingProfileTitle => 'Set up identity and birth in one place';

  @override
  String get onboardingProfileBody => 'The form logic stays the same; only the typographic spine is now aligned with the profile page.';

  @override
  String get commonContinue => 'Continue';

  @override
  String get commonRetry => 'Retry';

  @override
  String get commonOpen => 'Open';

  @override
  String get commonSave => 'Save';

  @override
  String get externalLinkOpenFailed => 'Could not open link.';

  @override
  String get tabsHome => 'Home';

  @override
  String get tabsBond => 'Bond';

  @override
  String get tabsStoryStudio => 'Story Studio';

  @override
  String get tabsAiChat => 'AI Chat';

  @override
  String get tabsProfile => 'Profile';

  @override
  String get homePlansTitle => 'Your plans';

  @override
  String get homePlansSubtitle => 'Your weekly flow and the collective pulse side by side.';

  @override
  String get homeSignalFallback => 'Today\'s highlighted theme.';

  @override
  String get homeActivePeriodTitle => 'Active period';

  @override
  String get homeActivePeriodBody => 'The transit theme working in the background of this period opens here.';

  @override
  String get homeStoryLoading => 'Today\'s story is loading...';

  @override
  String get homeStoryUnavailable => 'A short reading for today isn\'t ready yet.';

  @override
  String get homeDailyTransitLabel => 'Daily transit';

  @override
  String get homeHeroOpening => 'Today\'s opening';

  @override
  String get homeHeroPrompt => 'What is opening in me today?';

  @override
  String get homeHeroQuestionTitle => 'Today\'s opening question';

  @override
  String get homeGoToCalendar => 'Go to calendar';

  @override
  String get homeCollectivePulse => 'Collective pulse';

  @override
  String get homeDayPlan => 'Today\'s plan';

  @override
  String get homeCalendarTitle => 'Calendar';

  @override
  String get homeWeekFlowOpen => 'Open the flow ahead for the next week.';

  @override
  String get homeWeekView => '1-week view';

  @override
  String get homeWeeklyCalendar => 'Weekly calendar';

  @override
  String get homeWeeklyCalendarBody => 'Open the current calendar flow from the compact view and see the full week.';

  @override
  String get homePeriodCardsPending => 'Period cards will appear here when ready.';

  @override
  String get homeActiveThemePending => 'Waiting for active theme';

  @override
  String get homeActiveThemeBody => 'The active theme from the period flow will appear here as a compact card.';

  @override
  String get homeOpenTheme => 'Open theme';

  @override
  String get homeNowActive => 'Active now';

  @override
  String get homeOpenTopicsTitle => 'Open themes';

  @override
  String get homeOpenTopicsBody => 'Enter all themes currently active in the collective from here.';

  @override
  String get homeAllTopics => 'All themes';

  @override
  String get homePrimaryMeta => 'Primary';

  @override
  String get homeCollectiveMeta => 'Collective';

  @override
  String get homeWeekMeta => 'Week';

  @override
  String get homeTimingMeta => 'Timing';

  @override
  String get homeOpenDetail => 'Open detail';

  @override
  String homeDataLoadFailed(Object error) {
    return 'Home data could not be loaded: $error';
  }

  @override
  String get homeRequestTimedOut => 'Today\'s home reading took too long to load. The screen was opened with lighter data; try again in a moment.';

  @override
  String get authGateBirthDataErrorTitle => 'Your session is still active';

  @override
  String get authGateBirthDataErrorBody => 'Supabase is unreachable right now, so we cannot verify your birth data. We keep you on this retry screen instead of redirecting you to onboarding.';

  @override
  String get sessionExpiredLoginAgain => 'Session expired. Please log in again.';

  @override
  String errorFailedToLoadBirthData(Object error) {
    return 'Failed to load birth data: $error';
  }

  @override
  String errorFailedToSaveBirthData(Object error) {
    return 'Failed to save birth data: $error';
  }

  @override
  String get errorPleaseFillBirthFields => 'Please fill birth date, time, city and country.';

  @override
  String errorFailedToLoadProfile(Object error) {
    return 'Failed to load profile: $error';
  }

  @override
  String errorFailedToSaveProfile(Object error) {
    return 'Failed to save profile: $error';
  }

  @override
  String get errorPleaseFillAllFields => 'Please fill all fields.';

  @override
  String get menuQuickAccess => 'Quick access';

  @override
  String get menuEditProfile => 'Edit profile';

  @override
  String get menuEditProfileSubtitle => 'Open your details and profile settings.';

  @override
  String get menuManagePeople => 'Manage people';

  @override
  String get menuAddPerson => 'Add person';

  @override
  String get menuPeopleSubtitle => 'Open your saved people list for bond and social flows.';

  @override
  String get menuCalendar => 'Calendar and timing';

  @override
  String get menuCalendarSubtitle => 'Daily rhythm, periods and best times.';

  @override
  String get menuArchetypeExperience => 'Archetype experience';

  @override
  String get menuCompleteBirthData => 'Complete birth data';

  @override
  String get menuArchetypeSubtitle => 'Open your identity axis in the deeper experience.';

  @override
  String get menuCompleteBirthDataSubtitle => 'Complete missing data to unlock archetype screens.';

  @override
  String get menuPreferences => 'Preferences';

  @override
  String get menuThemeMode => 'Theme mode';

  @override
  String get themeModeDark => 'Dark';

  @override
  String get themeModeLight => 'Light';

  @override
  String get menuLanguage => 'Language';

  @override
  String get menuNotificationPreferences => 'Notification preferences';

  @override
  String get menuDailySummary => 'Daily summary';

  @override
  String get menuDailySummarySubtitle => 'A short rhythm briefing in the morning';

  @override
  String get menuSkyEvents => 'Sky events';

  @override
  String get menuSkyEventsSubtitle => 'Highlighted transit and event alerts';

  @override
  String get menuSocialActivity => 'Social activity';

  @override
  String get menuSocialActivitySubtitle => 'Forum and relationship-side updates';

  @override
  String get menuMembership => 'Membership';

  @override
  String get menuPremiumSubscription => 'Premium subscription';

  @override
  String get menuPremiumInterestSubtitle => 'You\'re on the list. We\'ll let you know when Premium opens.';

  @override
  String get menuPremiumDefaultSubtitle => 'A deeper layer for longer readings and extended flows.';

  @override
  String get menuInfoAndSupport => 'Info and support';

  @override
  String get menuAccount => 'Account';

  @override
  String get menuInList => 'On list';

  @override
  String get menuSoon => 'Soon';

  @override
  String get menuSignOut => 'Sign out';

  @override
  String get menuSignOutSubtitle => 'Close the current session and return to login.';

  @override
  String get restorePurchasesTitle => 'Restore Purchases';

  @override
  String get restorePurchasesDescription => 'Restore your previous purchases or subscription access on this device.';

  @override
  String get restorePurchasesSuccess => 'Your purchases have been restored.';

  @override
  String get restorePurchasesNoActive => 'No active purchases were found to restore.';

  @override
  String get restorePurchasesError => 'Could not restore purchases. Please try again.';

  @override
  String get privacyPolicyTitle => 'Privacy Policy';

  @override
  String get privacyPolicyDescription => 'SHOU processes the data needed to create your account, personalize your experience, and provide app features.';

  @override
  String get termsOfUseTitle => 'Terms of Use';

  @override
  String get termsOfUseDescription => 'By using SHOU, you agree to the app\'s terms of use and the rules governing the digital services provided.';

  @override
  String get supportTitle => 'Support';

  @override
  String get supportDescription => 'If you have questions, technical issues, or need help with your account, you can contact us here.';

  @override
  String get deleteAccountTitle => 'Delete Account';

  @override
  String get deleteAccountDescription => 'Deleting your account permanently removes your profile, personal account data, and access within the app. This action cannot be undone.';

  @override
  String get deleteAccountDialogTitle => 'Are you sure you want to delete your account?';

  @override
  String get deleteAccountDialogBody => 'This action cannot be undone. Your account and associated personal data will be deleted. If you have an active subscription, you may also need to manage it through App Store subscriptions.';

  @override
  String get deleteAccountSubscriptionNote => 'Deleting your account does not automatically cancel subscriptions managed through the App Store.';

  @override
  String get deleteAccountCancel => 'Cancel';

  @override
  String get deleteAccountConfirm => 'Delete Account';

  @override
  String get deleteAccountSuccess => 'Your account has been deleted.';

  @override
  String get deleteAccountError => 'Your account could not be deleted. Please try again.';

  @override
  String get deleteAccountProgress => 'Deleting your account...';

  @override
  String menuPeopleCount(int count) {
    return '$count people';
  }

  @override
  String get menuArchetypeReady => 'Archetype ready';

  @override
  String get menuBirthDataMissing => 'Birth data missing';

  @override
  String get premiumSheetTitle => 'Premium subscription';

  @override
  String get premiumSheetBody => 'A premium layer is being prepared for longer readings, more depth and early access.';

  @override
  String get premiumBulletIdentity => 'Long-form identity and relationship readings';

  @override
  String get premiumBulletTiming => 'Extra timing and period depth';

  @override
  String get premiumBulletEarlyAccess => 'Early access to new features';

  @override
  String get premiumNotifyMe => 'Notify me';

  @override
  String get premiumAlreadyInList => 'You\'re on the list';

  @override
  String get premiumNotifySnackbar => 'We\'ll notify you when Premium opens.';

  @override
  String homeGreeting(Object name) {
    return 'Hello $name';
  }

  @override
  String homeTodayLabel(Object date) {
    return 'Today $date';
  }

  @override
  String get homeGreetingFallbackName => 'you';

  @override
  String get periodDetailTransitTitle => 'Transit Detail';

  @override
  String get periodDetailPeriodTitle => 'Period Detail';

  @override
  String get periodDetailTodayEyebrow => 'Today';

  @override
  String get periodDetailPeriodEyebrow => 'Period';

  @override
  String get periodDetailContextLabel => 'Context';

  @override
  String get periodDetailContextTitle => 'Part of a larger period';

  @override
  String get periodDetailCoreLabel => 'Core';

  @override
  String get periodDetailCoreTitle => 'The central line of this effect';

  @override
  String get periodDetailSupportingLabel => 'Supporting';

  @override
  String get periodDetailSupportingTitle => 'Other layers opening up';

  @override
  String get periodDetailTechnicalLabel => 'Technical';

  @override
  String get periodDetailTechnicalTitle => 'Background notes';

  @override
  String get calendarPanelLabel => 'Calendar';

  @override
  String get calendarMonthMode => 'Month';

  @override
  String get calendarWeekMode => 'Week';

  @override
  String get calendarMonthIntro => 'Tap a day from the month view to open that day\'s page.';

  @override
  String get calendarWeekIntro => 'Focus on the selected week, open a day, and move left-right through detail.';

  @override
  String get calendarPickDate => 'Pick date';

  @override
  String get calendarDayThemeLabel => 'Day theme';

  @override
  String get calendarOpenDay => 'Open day';

  @override
  String get calendarSelectedDayFallback => 'When you tap a day, its cards, markers, and longer-period context open in detail.';

  @override
  String get calendarContextLabel => 'Context';

  @override
  String get calendarLongTermEffectTitle => 'Long-term effect';

  @override
  String get calendarLongTermEffectFallback => 'There is a longer-running period working behind this day.';

  @override
  String get calendarLongTermEffectReadMore => 'You can read the period story running in the background of the day more fully on the day page.';

  @override
  String get calendarPreviewFallback => 'Quickly scan nearby days, tap one, and move into that day\'s page.';

  @override
  String get profileAvatarUpdated => 'Profile photo updated';

  @override
  String profileAvatarUploadFailed(Object error) {
    return 'Profile photo could not be uploaded: $error';
  }

  @override
  String get profileAvatarHelperText => 'You can add a photo to make your profile feel more like yours.';

  @override
  String get profileInterpretationUnavailableTitle => 'Reading stream unavailable';

  @override
  String get profileBirthDataPendingTitle => 'Birth data pending';

  @override
  String get profileBirthDataPendingBodyDark => 'This screen is filled by `core_story_ui`, `profile_narrative`, `personality_imprint`, and `insight_modules`. When you complete your birth date, time, and place from profile settings, the content opens automatically.';

  @override
  String get profileBirthDataPendingBodyLight => 'This screen fills with core story, profile narrative, and insight content. When you complete your birth date, time, and place, the content opens automatically.';

  @override
  String get profileIdentityAxis => 'Identity axis';

  @override
  String get profileMainStory => 'Your main story';

  @override
  String get profileOpenFullReading => 'Open full reading';

  @override
  String get profileSignatureLayers => 'Signature layers';

  @override
  String get profileSideThemes => 'Side themes';

  @override
  String get profileWarning => 'Warning';

  @override
  String get profileBack => 'Go back';

  @override
  String get profileOpenRelationshipFlow => 'Open relationship flow';

  @override
  String get profileOpenTimingFlow => 'Open timing flow';

  @override
  String get profileReturnToChartFlow => 'Return to chart flow';

  @override
  String get profileConnectionsLabel => 'Connections';

  @override
  String get profileConnectionsTitle => 'People you added';

  @override
  String get profileConnectionsBody => 'Your real friend list opened from following and followers appears here.';

  @override
  String get profileFriendLabel => 'Friend';

  @override
  String get profileLocationMissing => 'location missing';

  @override
  String get profileFollowing => 'Following';

  @override
  String get profileFollowers => 'Followers';

  @override
  String profileOpenSinglePersonProfile(Object name) {
    return '$name\'s profile';
  }

  @override
  String profileOpenManyPersonProfiles(int count) {
    return 'View $count friend profiles';
  }

  @override
  String get profileSunLabel => 'Sun';

  @override
  String get profileRisingLabel => 'Rising';

  @override
  String get profileMoonLabel => 'Moon';

  @override
  String get profileIdentityLabel => 'IDENTITY';

  @override
  String get profileIdentityReading => 'Identity reading';

  @override
  String get profileOpenIdentityReading => 'Open identity reading';

  @override
  String get profileGenerateResult => 'Generate result';

  @override
  String profileConfidenceScore(Object score) {
    return 'Confidence score $score';
  }

  @override
  String profileNatalLoadFailed(Object error) {
    return 'Natal reading could not be loaded: $error';
  }

  @override
  String get profileTimingFlowLabel => 'TIMING FLOW';

  @override
  String get profileTimingFlowUnavailable => 'Timing flow unavailable';

  @override
  String get profileTimingFlowNotReady => 'Timing flow not ready';

  @override
  String get profileTimingFlowNotReadyBody => 'When the period summary arrives, only a short teaser and upcoming peaks will appear here.';

  @override
  String get profileCurrentPeriod => 'Current period';

  @override
  String get profileUpcomingPeaks => 'Upcoming peaks';

  @override
  String profileNextLabel(Object label) {
    return 'Next: $label';
  }

  @override
  String get profileMoreOpen => 'Open more';

  @override
  String get profileNatal => 'Natal';

  @override
  String get profileRelationship => 'Relationship';

  @override
  String get profileTiming => 'Timing';

  @override
  String get profileMainReading => 'Main reading';

  @override
  String get profileShadowGrowth => 'Shadow & growth';

  @override
  String get profileIdentityEyebrow => 'Identity';

  @override
  String get profileIdentityFlow => 'Identity flow';

  @override
  String get profileIdentityTone => 'Identity tone';

  @override
  String get profileIdentitySummary => 'Identity summary';

  @override
  String get profileArchetypeBirthDataRequired => 'Birth date, time, and place are required before opening the archetype experience.';

  @override
  String get profileIdentityFlowSubtitleFallback => 'See a longer read of how your identity is perceived from the outside and inside here.';

  @override
  String get profileNarrativeFlowSubtitleFallback => 'Read more clearly how this section works in you here.';

  @override
  String get profileSignatureCatalogSubtitle => 'In the card list you only see the titles; tap one card to open only its detail.';

  @override
  String get profileSignatureCardSubtitleFallback => 'The full explanation of this personality signature card opens here.';

  @override
  String get profileSideThemesFlowSubtitle => 'Other sides that complete your main portrait stand out here.';

  @override
  String get profileInsightFlowSubtitleFallback => 'This section opens the full flow on the axis of defense and growth.';

  @override
  String get profileOpenDefensePattern => 'Open your defense pattern';

  @override
  String get profileSeeArchetype => 'See your archetype';

  @override
  String get profileArchetypeBodyReady => 'Open the active identity, protection, and tension lines in your chart in a single experience.';

  @override
  String get profileArchetypeBodyPending => 'When you complete your birth date, time, and place, the archetype experience will open here.';

  @override
  String get profileCompleteBirthData => 'Complete your birth data';

  @override
  String get profileOnlineFriends => 'ONLINE FRIENDS';

  @override
  String get profileQuietSocialCircle => 'A calmer social circle';

  @override
  String get profileIdentitySummaryFallback => 'Your identity axis opens from the profile narrative.';

  @override
  String get profileNarrativeLoading => 'Profile narrative is being pulled from the backend reading...';

  @override
  String get profilePlacementsAndAspects => 'PLACEMENTS & ASPECTS';

  @override
  String get profileOpenSideThemes => 'Open side themes';

  @override
  String get profilePlacement => 'Placement';

  @override
  String get profileAspect => 'Aspect';

  @override
  String get profileSignTone => 'Sign tone';

  @override
  String get profileFeaturedTheme => 'Featured theme';

  @override
  String get profileRuler => 'Ruler';

  @override
  String profileStrongestRuler(Object name) {
    return 'Strongest ruler: $name';
  }

  @override
  String profileSignRuler(Object sign) {
    return '$sign ruler';
  }

  @override
  String get profileChartBackbone => 'Chart backbone';

  @override
  String profileHouseEmphasis(int house) {
    return '$house. house emphasis';
  }

  @override
  String get profileEarthInfluential => 'Earth influential';

  @override
  String get profileOutsideInside => 'Outside and inside';

  @override
  String get profileMindWorks => 'How your mind works';

  @override
  String get profileSelfProtection => 'How you protect yourself';

  @override
  String get profileIntimacyOpens => 'How intimacy opens in you';

  @override
  String get profileHoldReleaseBalance => 'Balance between holding and releasing';

  @override
  String get profileWhereOpportunityFlows => 'Where opportunity flows';

  @override
  String get profileRecognizableLine => 'The line that is easily recognized in you';

  @override
  String get profileTwoInnerDirections => 'How your two inner directions work';

  @override
  String get profileStandoutSide => 'The side that stands out in you';

  @override
  String get profileElementFireDominant => 'Fire dominant';

  @override
  String get profileElementWaterDominant => 'Water dominant';

  @override
  String get profileElementAirDominant => 'Air dominant';

  @override
  String get profileElementEarthDominant => 'Earth dominant';

  @override
  String get profileBirthPlacePending => 'Birth place pending';

  @override
  String profileAgeLabel(int age) {
    return '$age years old';
  }

  @override
  String get calendarSelectedDaySummaryPrompt => 'Tap the selected day to open its rhythm, cards, and long-term effect.';

  @override
  String get calendarMarkerDirectionChange => 'Direction change';

  @override
  String get calendarMarkerNewArea => 'New area';

  @override
  String get calendarMarkerRetrograde => 'Retrograde';

  @override
  String get calendarMarkerPeak => 'Peak';

  @override
  String get calendarMarkerBeginning => 'Beginning';

  @override
  String get calendarMarkerThreshold => 'Threshold';

  @override
  String get calendarMarkerMultipleThresholds => 'multiple thresholds';

  @override
  String get calendarFallbackSensitiveDay => 'Sensitive day.';

  @override
  String get calendarFallbackHighTempo => 'High tempo.';

  @override
  String get calendarFallbackBusyDay => 'Busy day.';

  @override
  String get calendarFallbackTwoSignals => 'Two things stand out today.';

  @override
  String get calendarFallbackOneSignal => 'One thing stands out.';

  @override
  String get calendarFallbackMixedDay => 'Today feels a bit mixed.';

  @override
  String get calendarFallbackCalmDay => 'Today is calm.';

  @override
  String get calendarFallbackHooked => 'You may get snagged on things quickly today.';

  @override
  String get calendarFallbackSeveralThings => 'Several things may draw your attention at once.';

  @override
  String get calendarFallbackOneThingPushes => 'One thing is pushing the day\'s rhythm forward a bit.';

  @override
  String get calendarFallbackSimpleRhythm => 'Today\'s rhythm is flowing a bit more simply.';

  @override
  String get calendarFallbackBreath => 'A breath will help.';

  @override
  String get calendarFallbackDoNotPileOn => 'Don\'t load everything on at once.';

  @override
  String get calendarFallbackDoNotRush => 'Don\'t rush.';

  @override
  String get calendarFallbackLeaveSimple => 'Keep today a little simpler.';

  @override
  String calendarHouseTouchpointHint(Object area) {
    return 'It may show up most around $area.';
  }

  @override
  String get calendarEditorialCurrentFallback => 'The rhythm of the day becomes a bit more readable here.';

  @override
  String get calendarEditorialChangeFallback => 'Notice which area of your life this shows up in most.';

  @override
  String get calendarEditorialDirectionFallback => 'The theme does not end here; it will take more shape over the coming days.';

  @override
  String get calendarEditorialSecondaryFallback => 'This is a second layer working alongside it in the background.';

  @override
  String get calendarPhaseIntensifying => 'Intensifying';

  @override
  String get calendarPhasePeakToday => 'Peaking today';

  @override
  String get calendarPhaseReleasing => 'Starting to release';

  @override
  String calendarTimingPeak(Object date) {
    return 'Peak $date';
  }

  @override
  String calendarTimingStart(Object date) {
    return 'Start $date';
  }

  @override
  String calendarTimingPrefix(Object timing) {
    return 'Timing: $timing';
  }

  @override
  String calendarBestWindow(Object labels) {
    return 'Best window this week: $labels';
  }

  @override
  String get calendarCombinedTitle => 'Unified calendar';

  @override
  String get calendarCombinedBody => 'Follow the month and week flow on the same surface. When you tap a day, that day\'s page opens and the long-term context stays intact.';

  @override
  String get calendarProfileLoadFailed => 'Profile data could not be loaded.';

  @override
  String get calendarBirthDataRequiredTitle => 'Birth data required for calendar';

  @override
  String get calendarBirthDataRequiredBody => 'When birth date, time, and place are completed, the calendar opens.';

  @override
  String get calendarSectionNow => 'What\'s happening now';

  @override
  String get calendarSelectedDayWindows => 'Selected day windows';

  @override
  String get calendarSectionChange => 'What this changes in you';

  @override
  String get calendarSectionDirection => 'Where it\'s going';

  @override
  String get calendarSectionBackground => 'What is working underneath';

  @override
  String get calendarSectionSecondaryTheme => 'Additional theme in play';

  @override
  String get calendarOpenMainTheme => 'Open main theme';

  @override
  String get calendarOpenPeriod => 'Open period';

  @override
  String get calendarWhyItMatters => 'Why does this matter?';

  @override
  String get calendarLongTermLabel => 'Long term';

  @override
  String get calendarLongTermActiveTodayTitle => 'The long-term story is still active today';

  @override
  String get calendarLongTermActiveTodayBody => 'This is not today itself; it is the longer story carrying today from the background.';

  @override
  String get calendarOpenCalendar => 'Open calendar';

  @override
  String calendarLongTermEffectPrefix(Object title) {
    return 'Long-term effect: $title';
  }

  @override
  String get calendarBackgroundActive => 'active in the background';

  @override
  String get calendarDailyReadingPreparing => 'The main reading for this day is being prepared.';

  @override
  String get calendarSelectedDayCalm => 'Selected day is calm';

  @override
  String get calendarNoDistinctEventCard => 'There is no standout event card for this day. You can choose another day from the calendar and check the flow.';

  @override
  String get calendarMonthPanelBody => 'The month view that behaves like a calendar lives here. Tap a day and open daily data in the same flow.';

  @override
  String get calendarTimingPersonalized => 'Your personal timing';

  @override
  String get calendarTimingPersonalizedBody => 'You can read the periods opening ahead of you here in a calmer order.';

  @override
  String get calendarPeriodLabel => 'Period';

  @override
  String get calendarCurrentPeriodTheme => 'The main theme of this period';

  @override
  String get calendarTimingPreparing => 'Timing is being prepared';

  @override
  String get calendarTimingPreparingBody => 'The editorial list of your personal periods is loading.';

  @override
  String get calendarNoSelectedPeriod => 'No selected period';

  @override
  String get calendarNoSelectedPeriodBody => 'You\'ll see it here when active period cards are ready.';

  @override
  String get calendarPeakListShort => 'Short peak list';

  @override
  String get calendarPeakListBody => 'Follow the dates when the effects ahead of you get stronger, in order.';

  @override
  String get calendarPeriodCardNotFound => 'No period card found';

  @override
  String get calendarPeriodCardNotFoundBody => 'No period marker/card was found.';

  @override
  String get calendarPeriodCardsTitle => 'Period cards';

  @override
  String get calendarTransitTimeout => 'The transit summary did not return in time. I lightened the period screen; can you try again?';

  @override
  String get calendarInvalidDateOrProfile => 'The submitted date or profile fields are invalid (422).';

  @override
  String get calendarPeriodDataUnavailable => 'Period data could not be loaded.';

  @override
  String get calendarPeriodCoreFallbackTitle => 'The main theme of this period';

  @override
  String get calendarPeriodCoreFallbackBody => 'The period summary is not ready yet.';

  @override
  String get calendarTodayForeground => 'This stands out most today.';

  @override
  String get calendarPeriodFromBackgroundToday => 'Today, rather than a short trigger, the theme working in the background stands out.';

  @override
  String get aiOnline => 'Online';

  @override
  String get aiIntroMessage => 'Hello, I\'m Aila. If you want, write what you\'re feeling today, something on your mind, or a chart detail you\'re curious about.';

  @override
  String get aiUserLabel => 'You';

  @override
  String get aiNow => 'Now';

  @override
  String get aiComposerHint => 'Write to Aila...';

  @override
  String aiFreeRemaining(int count) {
    return '$count free left';
  }

  @override
  String aiCreditsRemaining(int count) {
    return '$count credits';
  }

  @override
  String get aiProActive => 'Pro active';

  @override
  String get aiSending => 'Aila is thinking...';

  @override
  String get aiPaywallTitle => 'Continue with credits or Pro';

  @override
  String get aiPaywallBody => 'You used all 3 free questions. Buy a credit pack or unlock Pro to keep chatting.';

  @override
  String get aiPaywallMembershipNote => 'Start your membership to unlock SHOU\'s deeper readings and premium experience. If you already have a purchase, you can restore it below.';

  @override
  String get aiPaywallLoading => 'Loading products...';

  @override
  String get aiPaywallUnavailable => 'Purchases are not available right now.';

  @override
  String get aiPaywallRestoreHint => 'After purchase, retry your message in a few seconds while the webhook updates your balance.';

  @override
  String get aiProductQ1Title => '1 question';

  @override
  String get aiProductQ1Subtitle => 'Single reply credit';

  @override
  String get aiProductQ5Title => '5 questions';

  @override
  String get aiProductQ5Subtitle => 'Credit pack for a short streak';

  @override
  String get aiProductQ15Title => '15 questions';

  @override
  String get aiProductQ15Subtitle => 'Credit pack for heavier use';

  @override
  String get aiProductProTitle => 'Pro monthly';

  @override
  String get aiProductProSubtitle => 'Unlimited chat while Pro is active';

  @override
  String get aiStorePriceUnavailable => 'Unavailable';

  @override
  String get aiPurchasePending => 'Purchase received. Retry your message in a few seconds.';

  @override
  String get aiPurchaseNotSupported => 'Purchases are only available on iOS and Android.';

  @override
  String aiChatUnavailable(Object error) {
    return 'AI chat is unavailable right now: $error';
  }

  @override
  String get peopleFormAddTitle => 'Add person';

  @override
  String get peopleFormEditTitle => 'Edit person';

  @override
  String get peopleFormNameRequired => 'Name is required.';

  @override
  String get peopleFormBirthDateRequired => 'Birth date is required.';

  @override
  String get peopleFormBirthTimeOptional => 'Birth time (optional)';

  @override
  String get peopleFormBirthTimeHint => 'If you do not know the birth time, you can leave it empty.';

  @override
  String get peopleFormCityRequired => 'City is required.';

  @override
  String get peopleFormCountryRequired => 'Country is required.';

  @override
  String get peopleFormSaving => 'Saving...';

  @override
  String get peopleFormLoginRequired => 'Sign in before adding a person.';

  @override
  String peopleFormSaveFailed(Object error) {
    return 'Person could not be saved: $error';
  }

  @override
  String get peoplePageLabel => 'People';

  @override
  String get peoplePageCenterText => 'your circle';

  @override
  String get peoplePageAddTooltip => 'Add person';

  @override
  String get peoplePageEmptyTitle => 'No saved people yet';

  @override
  String get peoplePageEmptyBody => 'Save people from your circle here to use them in Bond and social flows.';

  @override
  String get peoplePageCircleLabel => 'Circle';

  @override
  String get peoplePageCircleTitle => 'Saved people';

  @override
  String get peoplePageCircleBody => 'The people you use for Bond, friend profiles, and social flows appear here.';

  @override
  String get peoplePageHeroLabel => 'People';

  @override
  String get peoplePageHeroTitle => 'Keep your circle here for Bond and social flows';

  @override
  String get peoplePageHeroBody => 'The people you add are reused from the same place for Bond matches, friend profiles, and future social readings.';

  @override
  String get peoplePagePillAura => 'Aura';

  @override
  String get peoplePagePillBirthAxis => 'Birth axis';

  @override
  String get peoplePagePillSocialTone => 'Social tone';

  @override
  String get peoplePageListLoadFailedTitle => 'People list unavailable';

  @override
  String peoplePageListLoadFailed(Object error) {
    return 'People list could not be loaded: $error';
  }

  @override
  String get peoplePageFriendLabel => 'Person';

  @override
  String get peoplePageNoBirthTime => 'No birth time';

  @override
  String get peoplePageEditTooltip => 'Edit';

  @override
  String get peopleRepoListFailed => 'People list could not be fetched.';

  @override
  String get peopleRepoDetailFailed => 'Person details could not be fetched.';

  @override
  String get peopleRepoCreateFailed => 'Person could not be created.';

  @override
  String get peopleRepoUpdateFailed => 'Person could not be updated.';

  @override
  String get peopleRepoProfilesListUnsupported => 'The profiles table does not support listing saved people.';

  @override
  String get peopleRepoProfilesDetailUnsupported => 'The profiles table does not support loading this saved person.';

  @override
  String get peopleRepoProfilesCreateUnsupported => 'The profiles table does not support creating separate saved people.';

  @override
  String peopleRepoTableNotFound(Object candidates) {
    return 'No valid table for people records was found. Tried: $candidates';
  }

  @override
  String get peopleRepoTableValidationFailed => 'The people table could not be validated.';

  @override
  String get forumActiveTransitFallback => 'The sky is active';

  @override
  String get transitSkyCollectiveFallback => 'Something is moving in the collective.';

  @override
  String get transitSkyTypeIngress => 'Ingress';

  @override
  String get transitSkyTypeFullMoon => 'Full moon';

  @override
  String get transitSkyTypeNewMoon => 'New moon';

  @override
  String get transitSkyTypeExactAspect => 'Exact aspect';

  @override
  String get transitSkyTypeEclipse => 'Eclipse';

  @override
  String get transitSkyTypeRetroStart => 'Retrograde starts';

  @override
  String get transitSkyTypeRetroEnd => 'Retrograde ends';

  @override
  String get transitSkyTimingNow => 'Now';

  @override
  String get transitSkyTimingThisWeek => 'This week';

  @override
  String get transitMeaningRelationships => 'Relationships';

  @override
  String get transitMeaningMoney => 'Money';

  @override
  String get transitMeaningVisibility => 'Visibility';

  @override
  String get transitMeaningDecision => 'Decision';

  @override
  String get transitMeaningCloseness => 'Closeness';

  @override
  String get transitMeaningBuilding => 'Building';

  @override
  String get transitMeaningRelease => 'Release';

  @override
  String get transitMeaningTension => 'Tension';

  @override
  String get transitMeaningClarifying => 'Clarifying';

  @override
  String get transitMeaningTransformation => 'Transformation';

  @override
  String get profileDetailFallbackEyebrow => 'Deep reading';

  @override
  String get profileDetailFallbackTitle => 'Detail is being prepared for this card';

  @override
  String get profileDetailFallbackIntro => 'The main narrative flow came back empty for now.';

  @override
  String get profileDetailFallbackBody => 'The meaning of this card will still open here; right now the content stream is still on the way.';

  @override
  String get bondSelfName => 'Me';

  @override
  String get bondPageSelectPerson => 'Select person';

  @override
  String get bondPageLensFallback => 'bond lens';

  @override
  String get bondPageHeroTitle => 'Open the dynamic between two people here';

  @override
  String get bondPageHeroBody => 'Pick your own profile and one saved person, then read the main rhythm and tension line between you in the same flow.';

  @override
  String get bondPageLensLabel => 'Lens';

  @override
  String get bondPageBirthDataMissingTitle => 'Birth data is required for Bond';

  @override
  String get bondPageBirthDataMissingBody => 'When you complete your own birth date and location, this match opens more accurately.';

  @override
  String get bondPagePreparing => 'Preparing...';

  @override
  String get bondPageOpenResult => 'Open Bond result';

  @override
  String bondPageAnalyzeFailed(Object error) {
    return 'Bond analysis could not be loaded: $error';
  }

  @override
  String get bondPickerLabel => 'People selection';

  @override
  String get bondPickerTitle => 'Choose the second person for Bond';

  @override
  String get bondPickerAddPerson => 'Add new person';

  @override
  String get bondPickerOwnProfile => 'Your own profile';

  @override
  String get bondPickerMe => 'You';

  @override
  String bondPickerLoadFailed(Object error) {
    return 'People could not be loaded: $error';
  }

  @override
  String get bondPairEyebrow => 'Selection';

  @override
  String get bondPairTitle => 'Compare two people';

  @override
  String get bondPairBody => 'Pick two profiles, then see the main rhythm of their bond in the same flow.';

  @override
  String get storyStudioTopLabel => 'Story Studio';

  @override
  String get storyStudioTopCenter => 'imprint deck';

  @override
  String get storyStudioLoadingProfile => 'Profile is loading...';

  @override
  String get storyStudioBirthDataRequired => 'Story Studio needs birth date, time, and location before it can open.';

  @override
  String get storyStudioIdentityTitle => 'Identity cards';

  @override
  String get storyStudioIdentityBody => 'Open the dominant placements, inner drive, and shadow line in your chart one card at a time.';

  @override
  String get storyStudioIdentityTab => 'Identity';

  @override
  String get storyStudioMomentTitle => 'Live sources';

  @override
  String get storyStudioMomentBody => 'Return to the surfaces working right now and open the active flows from there.';

  @override
  String get storyStudioMomentTab => 'Moment';

  @override
  String get storyStudioCardsLoadFailed => 'Cards could not be loaded';

  @override
  String get storyStudioCardsPreparing => 'Cards are being prepared';

  @override
  String get storyStudioCardsPreparingBody => 'The personality imprint layer is coming in from the backend.';

  @override
  String get storyStudioCardsNotFound => 'No cards found';

  @override
  String get storyStudioCardsNotFoundBody => 'No Story Studio cards could be produced from this profile yet.';

  @override
  String get storyStudioMomentPanelTitle => 'Live studio sources';

  @override
  String get storyStudioMomentPanelBody => 'This section does not create a new card; it sends you back to the active Home and Bond surfaces.';

  @override
  String get storyStudioReturnToSources => 'Return to sources';

  @override
  String get storyStudioTraitLabel => 'Standout line';

  @override
  String get storyStudioInnerDriveLabel => 'Inner drive';

  @override
  String get storyStudioWhenTooMuchLabel => 'When overloaded';

  @override
  String get storyStudioRefreshing => 'Refreshing...';

  @override
  String get storyStudioKindAspect => 'Aspect';

  @override
  String get storyStudioKindHousePlacement => 'House placement';

  @override
  String get storyStudioKindSignPlacement => 'Sign placement';

  @override
  String get storyStudioKindLayer => 'Layer';

  @override
  String storyStudioLoadFailed(Object error) {
    return 'Story Studio could not be loaded: $error';
  }

  @override
  String get relationshipPreviewLabel => 'Relationship preview';

  @override
  String get relationshipPreviewBirthDataRequiredTitle => 'Birth data is required for relationship preview';

  @override
  String get relationshipPreviewBirthDataRequiredBody => 'When birth date, time, and location are complete, the relationship line opens here.';

  @override
  String get relationshipPreviewLoadFailedTitle => 'Relationship flow unavailable';

  @override
  String get relationshipPreviewMainThemeLabel => 'Main theme';

  @override
  String get relationshipPreviewDriversLabel => 'What is shaping today';

  @override
  String get relationshipPreviewBackdropLabel => 'Backdrop';

  @override
  String get relationshipPreviewUpperMeaningLabel => 'Deeper meaning';

  @override
  String get relationshipPreviewSupportingThemeLabel => 'Supporting theme';

  @override
  String get relationshipPreviewWhyImportant => 'Why this matters';

  @override
  String get relationshipPreviewFallbackNotice => 'The relationship lens was slow, so this opened with the general reading instead.';

  @override
  String get relationshipPreviewTimeout => 'The relationship reading took too long to return. Try again in a moment.';

  @override
  String get relationshipPreviewInvalidProfile => 'The submitted profile data is not enough for the relationship flow.';

  @override
  String get relationshipPreviewServerError => 'The relationship flow could not be loaded from the server right now.';

  @override
  String get relationshipPreviewFetchFailed => 'The relationship flow could not be loaded.';

  @override
  String get relationshipPreviewStageStarted => 'Started';

  @override
  String get relationshipPreviewStageIntensifying => 'Intensifying';

  @override
  String get relationshipPreviewStagePeak => 'Peak';

  @override
  String get relationshipPreviewStageResolving => 'Resolving';

  @override
  String get relationshipPreviewPeriodToToday => 'From the period into today';

  @override
  String get relationshipPreviewDefaultDriversFallback => 'There is movement on the relationship side today, but a single theme has not fully separated yet.';

  @override
  String get relationshipPreviewDefaultBackdropFallback => 'A longer period is still working underneath, and its relationship-side result will become clearer with a bit more time.';

  @override
  String get friendProfileTitle => 'Person profile';

  @override
  String get friendProfileNotFound => 'Person not found.';

  @override
  String get friendProfileEditTooltip => 'Edit person';

  @override
  String friendProfileLoadFailed(Object error) {
    return 'Person could not be loaded: $error';
  }

  @override
  String get profileDetailInfluences => 'Influences';

  @override
  String get profileDetailAllCards => 'All cards';

  @override
  String get profileDetailSignatureCardsTitle => 'Signature cards';

  @override
  String get profileDetailDefaultEyebrow => 'Detail';

  @override
  String get profileDetailDefaultTitle => 'Detail flow';

  @override
  String get profileDetailWhyHere => 'Why here';

  @override
  String profileDetailNextLabel(Object title) {
    return 'Next: $title';
  }

  @override
  String profileDetailContinuationTitle(Object title) {
    return '$title · Continue';
  }

  @override
  String get profileDetailSideA => 'One side';

  @override
  String get profileDetailSideB => 'The other side';

  @override
  String get profileDetailContinueFlow => 'Continue the flow';

  @override
  String get profileDetailContinueFromHere => 'Continue from here';

  @override
  String profileDetailContinuationFooter(int page, int total) {
    return 'Continues $page/$total';
  }

  @override
  String get profileDetailFlowEnds => 'The flow ends here';

  @override
  String get periodFallbackEffectTitle => 'Period effect';

  @override
  String periodIntentSummaryGeneric(Object title) {
    return 'There are windows to track for $title in this period.';
  }

  @override
  String periodIntentTopDays(Object title, Object dates) {
    return 'Standout days for $title: $dates.';
  }

  @override
  String periodIntentScores(Object ratings) {
    return 'Scores: $ratings';
  }

  @override
  String get periodIntentBeautyCare => 'Care and body';

  @override
  String get periodIntentBusiness => 'Work and output';

  @override
  String get periodIntentMoney => 'Money and resources';

  @override
  String get periodIntentRelationship => 'Relationship and harmony';

  @override
  String periodIntentLabel(int index) {
    return 'Intent $index';
  }

  @override
  String get periodDefaultTitle => 'Period';

  @override
  String get periodMainFlowFallback => 'The main flow of this period.';

  @override
  String get periodMainThemeFallback => 'The main theme of this period.';

  @override
  String get periodHighlightedThemeFallback => 'The standout theme in this period.';

  @override
  String get periodThemeCollectFallback => 'The standout theme of this period gathers here.';

  @override
  String get periodEssenceTitle => 'Essence of this period';

  @override
  String get periodSummaryUnavailable => 'No summary for this period is available.';

  @override
  String get periodTimeLabel => 'Timing';

  @override
  String get periodGuidancePrefix => 'Small practice:';

  @override
  String get periodDifficultyPrefix => 'What tends to make this harder is:';

  @override
  String get periodHowItWorksTitle => 'How it works';

  @override
  String get periodAsksTitle => 'What it asks of you';

  @override
  String get periodWatchTitle => 'What to watch';

  @override
  String get periodBuildsTitle => 'What it develops in you';

  @override
  String get periodEffectLabel => 'Effect';

  @override
  String get periodTechnicalNoteLabel => 'Technical note';

  @override
  String get periodCoreMainThemeTitle => 'The main theme of this period';

  @override
  String get periodCoreSummaryUnavailable => 'No period summary was available for this period.';

  @override
  String get profileExperimentPreviewLabel => 'Preview';

  @override
  String get profileExperimentCenterText => 'Nocturne Identity';

  @override
  String get profileExperimentMenuTooltip => 'Theme and experiment settings';

  @override
  String get profileExperimentHeroFallback => 'The first trace of the chart gathers here.';

  @override
  String get profileExperimentSignatureFallback => 'Identity trace';

  @override
  String get profileExperimentNatalPanelBody => 'This preview currently focuses on a spotlight hero that opens identity as a full portrait surface. Lower chapter layers will follow in a later patch.';

  @override
  String get profileExperimentTimingPanelBody => 'Timing mode behaves like a focus switch here for now. The lower period composition will arrive in a later patch.';

  @override
  String get profileExperimentMenuTitle => 'Nocturne experiment';

  @override
  String get profileExperimentMenuBody => 'Patch 1 only tests the upper identity composition.';

  @override
  String get profileExperimentSeeProfile => 'See profile';

  @override
  String get profileExperimentHeroLineFallback => 'Your identity is gathered into a new focal surface on this screen.';

  @override
  String get profileExperimentAuraLabel => 'Aura';

  @override
  String get profileExperimentRulerLabel => 'Ruler';

  @override
  String get profileExperimentWaiting => 'Waiting';

  @override
  String get profileExperimentRulerBodyFallback => 'The ruler of the 1st house is being read.';

  @override
  String get profileExperimentRisingTrace => 'Rising trace';

  @override
  String get profileExperimentSignatureLabel => 'Signature';

  @override
  String get profileExperimentSpotlightCards => 'Spotlight cards';

  @override
  String get profileExperimentSwipe => 'Swipe';

  @override
  String get profileExperimentFocusTitle => 'Reading focus';

  @override
  String get profileExperimentNatalFocus => 'Your structure';

  @override
  String get profileExperimentTimingFocus => 'Your current period';

  @override
  String get profileExperimentUnnamedProfile => 'Unnamed profile';

  @override
  String get profileExperimentFireDominant => 'Fire dominant';

  @override
  String get profileExperimentWaterDominant => 'Water dominant';

  @override
  String get profileExperimentAirDominant => 'Air dominant';

  @override
  String get profileExperimentEarthDominant => 'Earth dominant';

  @override
  String get errorTimeout => 'The server is a bit slow right now, try again in a moment.';

  @override
  String get errorNoConnection => 'Could not connect. Check your internet connection.';

  @override
  String get errorGeneric => 'Something went wrong. Please try again.';
}
