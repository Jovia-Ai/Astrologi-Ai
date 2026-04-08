// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for English (`en`).
class AppLocalizationsEn extends AppLocalizations {
  AppLocalizationsEn([String locale = 'en']) : super(locale);

  @override
  String get appTitle => 'Astrologi AI';

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
  String get menuInList => 'On list';

  @override
  String get menuSoon => 'Soon';

  @override
  String get menuSignOut => 'Sign out';

  @override
  String get menuSignOutSubtitle => 'Close the current session and return to login.';

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
}
