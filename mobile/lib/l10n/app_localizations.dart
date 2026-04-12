import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:intl/intl.dart' as intl;

import 'app_localizations_en.dart';
import 'app_localizations_tr.dart';

// ignore_for_file: type=lint

/// Callers can lookup localized strings with an instance of AppLocalizations
/// returned by `AppLocalizations.of(context)`.
///
/// Applications need to include `AppLocalizations.delegate()` in their app's
/// `localizationDelegates` list, and the locales they support in the app's
/// `supportedLocales` list. For example:
///
/// ```dart
/// import 'l10n/app_localizations.dart';
///
/// return MaterialApp(
///   localizationsDelegates: AppLocalizations.localizationsDelegates,
///   supportedLocales: AppLocalizations.supportedLocales,
///   home: MyApplicationHome(),
/// );
/// ```
///
/// ## Update pubspec.yaml
///
/// Please make sure to update your pubspec.yaml to include the following
/// packages:
///
/// ```yaml
/// dependencies:
///   # Internationalization support.
///   flutter_localizations:
///     sdk: flutter
///   intl: any # Use the pinned version from flutter_localizations
///
///   # Rest of dependencies
/// ```
///
/// ## iOS Applications
///
/// iOS applications define key application metadata, including supported
/// locales, in an Info.plist file that is built into the application bundle.
/// To configure the locales supported by your app, you’ll need to edit this
/// file.
///
/// First, open your project’s ios/Runner.xcworkspace Xcode workspace file.
/// Then, in the Project Navigator, open the Info.plist file under the Runner
/// project’s Runner folder.
///
/// Next, select the Information Property List item, select Add Item from the
/// Editor menu, then select Localizations from the pop-up menu.
///
/// Select and expand the newly-created Localizations item then, for each
/// locale your application supports, add a new item and select the locale
/// you wish to add from the pop-up menu in the Value field. This list should
/// be consistent with the languages listed in the AppLocalizations.supportedLocales
/// property.
abstract class AppLocalizations {
  AppLocalizations(String locale) : localeName = intl.Intl.canonicalizedLocale(locale.toString());

  final String localeName;

  static AppLocalizations? of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations);
  }

  static const LocalizationsDelegate<AppLocalizations> delegate = _AppLocalizationsDelegate();

  /// A list of this localizations delegate along with the default localizations
  /// delegates.
  ///
  /// Returns a list of localizations delegates containing this delegate along with
  /// GlobalMaterialLocalizations.delegate, GlobalCupertinoLocalizations.delegate,
  /// and GlobalWidgetsLocalizations.delegate.
  ///
  /// Additional delegates can be added by appending to this list in
  /// MaterialApp. This list does not have to be used at all if a custom list
  /// of delegates is preferred or required.
  static const List<LocalizationsDelegate<dynamic>> localizationsDelegates = <LocalizationsDelegate<dynamic>>[
    delegate,
    GlobalMaterialLocalizations.delegate,
    GlobalCupertinoLocalizations.delegate,
    GlobalWidgetsLocalizations.delegate,
  ];

  /// A list of this localizations delegate's supported locales.
  static const List<Locale> supportedLocales = <Locale>[
    Locale('en'),
    Locale('tr')
  ];

  /// No description provided for @appTitle.
  ///
  /// In en, this message translates to:
  /// **'Astrologi AI'**
  String get appTitle;

  /// No description provided for @supabaseConfigErrorTitle.
  ///
  /// In en, this message translates to:
  /// **'Supabase Configuration Error'**
  String get supabaseConfigErrorTitle;

  /// No description provided for @supabaseConfigErrorBody.
  ///
  /// In en, this message translates to:
  /// **'Supabase could not start. Please provide SUPABASE_URL and SUPABASE_ANON_KEY.'**
  String get supabaseConfigErrorBody;

  /// No description provided for @supabaseConfigErrorExample.
  ///
  /// In en, this message translates to:
  /// **'Example:\nflutter run --dart-define=SUPABASE_URL=https://YOUR_PROJECT.supabase.co --dart-define=SUPABASE_ANON_KEY=YOUR_KEY'**
  String get supabaseConfigErrorExample;

  /// No description provided for @loginTitle.
  ///
  /// In en, this message translates to:
  /// **'Welcome back'**
  String get loginTitle;

  /// No description provided for @loginBody.
  ///
  /// In en, this message translates to:
  /// **'Sign in and continue where you left off.'**
  String get loginBody;

  /// No description provided for @emailLabel.
  ///
  /// In en, this message translates to:
  /// **'Email'**
  String get emailLabel;

  /// No description provided for @passwordLabel.
  ///
  /// In en, this message translates to:
  /// **'Password'**
  String get passwordLabel;

  /// No description provided for @confirmPasswordLabel.
  ///
  /// In en, this message translates to:
  /// **'Confirm password'**
  String get confirmPasswordLabel;

  /// No description provided for @nameLabel.
  ///
  /// In en, this message translates to:
  /// **'Name'**
  String get nameLabel;

  /// No description provided for @birthDateLabel.
  ///
  /// In en, this message translates to:
  /// **'Birth date (YYYY-MM-DD)'**
  String get birthDateLabel;

  /// No description provided for @birthTimeLabel.
  ///
  /// In en, this message translates to:
  /// **'Birth time (HH:mm)'**
  String get birthTimeLabel;

  /// No description provided for @cityLabel.
  ///
  /// In en, this message translates to:
  /// **'City'**
  String get cityLabel;

  /// No description provided for @countryLabel.
  ///
  /// In en, this message translates to:
  /// **'Country'**
  String get countryLabel;

  /// No description provided for @loginSignIn.
  ///
  /// In en, this message translates to:
  /// **'Sign in'**
  String get loginSignIn;

  /// No description provided for @authOr.
  ///
  /// In en, this message translates to:
  /// **'or'**
  String get authOr;

  /// No description provided for @loginContinueWithGoogle.
  ///
  /// In en, this message translates to:
  /// **'Continue with Google'**
  String get loginContinueWithGoogle;

  /// No description provided for @loginCreateAccount.
  ///
  /// In en, this message translates to:
  /// **'Create account'**
  String get loginCreateAccount;

  /// No description provided for @loginForgotPassword.
  ///
  /// In en, this message translates to:
  /// **'Forgot password'**
  String get loginForgotPassword;

  /// No description provided for @loginPasswordResetSent.
  ///
  /// In en, this message translates to:
  /// **'Password reset email sent'**
  String get loginPasswordResetSent;

  /// No description provided for @loginGoogleStartFailed.
  ///
  /// In en, this message translates to:
  /// **'Google sign-in flow could not be started.'**
  String get loginGoogleStartFailed;

  /// No description provided for @registerTopLabel.
  ///
  /// In en, this message translates to:
  /// **'Sign up'**
  String get registerTopLabel;

  /// No description provided for @registerTopCenter.
  ///
  /// In en, this message translates to:
  /// **'new account'**
  String get registerTopCenter;

  /// No description provided for @registerSectionLabel.
  ///
  /// In en, this message translates to:
  /// **'Start'**
  String get registerSectionLabel;

  /// No description provided for @registerTitle.
  ///
  /// In en, this message translates to:
  /// **'Create your profile rhythm'**
  String get registerTitle;

  /// No description provided for @registerBody.
  ///
  /// In en, this message translates to:
  /// **'Create your account, then complete your profile and birth layers inside the same typographic system.'**
  String get registerBody;

  /// No description provided for @registerCreateAccount.
  ///
  /// In en, this message translates to:
  /// **'Create account'**
  String get registerCreateAccount;

  /// No description provided for @registerBackToLogin.
  ///
  /// In en, this message translates to:
  /// **'Back to login'**
  String get registerBackToLogin;

  /// No description provided for @registerPasswordsDoNotMatch.
  ///
  /// In en, this message translates to:
  /// **'Passwords do not match.'**
  String get registerPasswordsDoNotMatch;

  /// No description provided for @onboardingSectionLabel.
  ///
  /// In en, this message translates to:
  /// **'Onboarding'**
  String get onboardingSectionLabel;

  /// No description provided for @onboardingBirthTopLabel.
  ///
  /// In en, this message translates to:
  /// **'Birth'**
  String get onboardingBirthTopLabel;

  /// No description provided for @onboardingBirthTopCenter.
  ///
  /// In en, this message translates to:
  /// **'core data'**
  String get onboardingBirthTopCenter;

  /// No description provided for @onboardingBirthTitle.
  ///
  /// In en, this message translates to:
  /// **'Complete your birth axis'**
  String get onboardingBirthTitle;

  /// No description provided for @onboardingBirthBody.
  ///
  /// In en, this message translates to:
  /// **'This data goes to the backend as-is; this screen only aligns the surface with the profile language.'**
  String get onboardingBirthBody;

  /// No description provided for @onboardingProfileTopLabel.
  ///
  /// In en, this message translates to:
  /// **'Profile'**
  String get onboardingProfileTopLabel;

  /// No description provided for @onboardingProfileTopCenter.
  ///
  /// In en, this message translates to:
  /// **'setup'**
  String get onboardingProfileTopCenter;

  /// No description provided for @onboardingProfileTitle.
  ///
  /// In en, this message translates to:
  /// **'Set up identity and birth in one place'**
  String get onboardingProfileTitle;

  /// No description provided for @onboardingProfileBody.
  ///
  /// In en, this message translates to:
  /// **'The form logic stays the same; only the typographic spine is now aligned with the profile page.'**
  String get onboardingProfileBody;

  /// No description provided for @commonContinue.
  ///
  /// In en, this message translates to:
  /// **'Continue'**
  String get commonContinue;

  /// No description provided for @commonRetry.
  ///
  /// In en, this message translates to:
  /// **'Retry'**
  String get commonRetry;

  /// No description provided for @commonOpen.
  ///
  /// In en, this message translates to:
  /// **'Open'**
  String get commonOpen;

  /// No description provided for @commonSave.
  ///
  /// In en, this message translates to:
  /// **'Save'**
  String get commonSave;

  /// No description provided for @tabsHome.
  ///
  /// In en, this message translates to:
  /// **'Home'**
  String get tabsHome;

  /// No description provided for @tabsBond.
  ///
  /// In en, this message translates to:
  /// **'Bond'**
  String get tabsBond;

  /// No description provided for @tabsStoryStudio.
  ///
  /// In en, this message translates to:
  /// **'Story Studio'**
  String get tabsStoryStudio;

  /// No description provided for @tabsAiChat.
  ///
  /// In en, this message translates to:
  /// **'AI Chat'**
  String get tabsAiChat;

  /// No description provided for @tabsProfile.
  ///
  /// In en, this message translates to:
  /// **'Profile'**
  String get tabsProfile;

  /// No description provided for @homePlansTitle.
  ///
  /// In en, this message translates to:
  /// **'Your plans'**
  String get homePlansTitle;

  /// No description provided for @homePlansSubtitle.
  ///
  /// In en, this message translates to:
  /// **'Your weekly flow and the collective pulse side by side.'**
  String get homePlansSubtitle;

  /// No description provided for @homeSignalFallback.
  ///
  /// In en, this message translates to:
  /// **'Today\'s highlighted theme.'**
  String get homeSignalFallback;

  /// No description provided for @homeActivePeriodTitle.
  ///
  /// In en, this message translates to:
  /// **'Active period'**
  String get homeActivePeriodTitle;

  /// No description provided for @homeActivePeriodBody.
  ///
  /// In en, this message translates to:
  /// **'The transit theme working in the background of this period opens here.'**
  String get homeActivePeriodBody;

  /// No description provided for @homeStoryLoading.
  ///
  /// In en, this message translates to:
  /// **'Today\'s story is loading...'**
  String get homeStoryLoading;

  /// No description provided for @homeStoryUnavailable.
  ///
  /// In en, this message translates to:
  /// **'A short reading for today isn\'t ready yet.'**
  String get homeStoryUnavailable;

  /// No description provided for @homeDailyTransitLabel.
  ///
  /// In en, this message translates to:
  /// **'Daily transit'**
  String get homeDailyTransitLabel;

  /// No description provided for @homeHeroOpening.
  ///
  /// In en, this message translates to:
  /// **'Today\'s opening'**
  String get homeHeroOpening;

  /// No description provided for @homeHeroPrompt.
  ///
  /// In en, this message translates to:
  /// **'What is opening in me today?'**
  String get homeHeroPrompt;

  /// No description provided for @homeHeroQuestionTitle.
  ///
  /// In en, this message translates to:
  /// **'Today\'s opening question'**
  String get homeHeroQuestionTitle;

  /// No description provided for @homeGoToCalendar.
  ///
  /// In en, this message translates to:
  /// **'Go to calendar'**
  String get homeGoToCalendar;

  /// No description provided for @homeCollectivePulse.
  ///
  /// In en, this message translates to:
  /// **'Collective pulse'**
  String get homeCollectivePulse;

  /// No description provided for @homeDayPlan.
  ///
  /// In en, this message translates to:
  /// **'Today\'s plan'**
  String get homeDayPlan;

  /// No description provided for @homeCalendarTitle.
  ///
  /// In en, this message translates to:
  /// **'Calendar'**
  String get homeCalendarTitle;

  /// No description provided for @homeWeekFlowOpen.
  ///
  /// In en, this message translates to:
  /// **'Open the flow ahead for the next week.'**
  String get homeWeekFlowOpen;

  /// No description provided for @homeWeekView.
  ///
  /// In en, this message translates to:
  /// **'1-week view'**
  String get homeWeekView;

  /// No description provided for @homeWeeklyCalendar.
  ///
  /// In en, this message translates to:
  /// **'Weekly calendar'**
  String get homeWeeklyCalendar;

  /// No description provided for @homeWeeklyCalendarBody.
  ///
  /// In en, this message translates to:
  /// **'Open the current calendar flow from the compact view and see the full week.'**
  String get homeWeeklyCalendarBody;

  /// No description provided for @homePeriodCardsPending.
  ///
  /// In en, this message translates to:
  /// **'Period cards will appear here when ready.'**
  String get homePeriodCardsPending;

  /// No description provided for @homeActiveThemePending.
  ///
  /// In en, this message translates to:
  /// **'Waiting for active theme'**
  String get homeActiveThemePending;

  /// No description provided for @homeActiveThemeBody.
  ///
  /// In en, this message translates to:
  /// **'The active theme from the period flow will appear here as a compact card.'**
  String get homeActiveThemeBody;

  /// No description provided for @homeOpenTheme.
  ///
  /// In en, this message translates to:
  /// **'Open theme'**
  String get homeOpenTheme;

  /// No description provided for @homeNowActive.
  ///
  /// In en, this message translates to:
  /// **'Active now'**
  String get homeNowActive;

  /// No description provided for @homeOpenTopicsTitle.
  ///
  /// In en, this message translates to:
  /// **'Open themes'**
  String get homeOpenTopicsTitle;

  /// No description provided for @homeOpenTopicsBody.
  ///
  /// In en, this message translates to:
  /// **'Enter all themes currently active in the collective from here.'**
  String get homeOpenTopicsBody;

  /// No description provided for @homeAllTopics.
  ///
  /// In en, this message translates to:
  /// **'All themes'**
  String get homeAllTopics;

  /// No description provided for @homePrimaryMeta.
  ///
  /// In en, this message translates to:
  /// **'Primary'**
  String get homePrimaryMeta;

  /// No description provided for @homeCollectiveMeta.
  ///
  /// In en, this message translates to:
  /// **'Collective'**
  String get homeCollectiveMeta;

  /// No description provided for @homeWeekMeta.
  ///
  /// In en, this message translates to:
  /// **'Week'**
  String get homeWeekMeta;

  /// No description provided for @homeTimingMeta.
  ///
  /// In en, this message translates to:
  /// **'Timing'**
  String get homeTimingMeta;

  /// No description provided for @homeOpenDetail.
  ///
  /// In en, this message translates to:
  /// **'Open detail'**
  String get homeOpenDetail;

  /// No description provided for @homeDataLoadFailed.
  ///
  /// In en, this message translates to:
  /// **'Home data could not be loaded: {error}'**
  String homeDataLoadFailed(Object error);

  /// No description provided for @homeRequestTimedOut.
  ///
  /// In en, this message translates to:
  /// **'Today\'s home reading took too long to load. The screen was opened with lighter data; try again in a moment.'**
  String get homeRequestTimedOut;

  /// No description provided for @authGateBirthDataErrorTitle.
  ///
  /// In en, this message translates to:
  /// **'Your session is still active'**
  String get authGateBirthDataErrorTitle;

  /// No description provided for @authGateBirthDataErrorBody.
  ///
  /// In en, this message translates to:
  /// **'Supabase is unreachable right now, so we cannot verify your birth data. We keep you on this retry screen instead of redirecting you to onboarding.'**
  String get authGateBirthDataErrorBody;

  /// No description provided for @sessionExpiredLoginAgain.
  ///
  /// In en, this message translates to:
  /// **'Session expired. Please log in again.'**
  String get sessionExpiredLoginAgain;

  /// No description provided for @errorFailedToLoadBirthData.
  ///
  /// In en, this message translates to:
  /// **'Failed to load birth data: {error}'**
  String errorFailedToLoadBirthData(Object error);

  /// No description provided for @errorFailedToSaveBirthData.
  ///
  /// In en, this message translates to:
  /// **'Failed to save birth data: {error}'**
  String errorFailedToSaveBirthData(Object error);

  /// No description provided for @errorPleaseFillBirthFields.
  ///
  /// In en, this message translates to:
  /// **'Please fill birth date, time, city and country.'**
  String get errorPleaseFillBirthFields;

  /// No description provided for @errorFailedToLoadProfile.
  ///
  /// In en, this message translates to:
  /// **'Failed to load profile: {error}'**
  String errorFailedToLoadProfile(Object error);

  /// No description provided for @errorFailedToSaveProfile.
  ///
  /// In en, this message translates to:
  /// **'Failed to save profile: {error}'**
  String errorFailedToSaveProfile(Object error);

  /// No description provided for @errorPleaseFillAllFields.
  ///
  /// In en, this message translates to:
  /// **'Please fill all fields.'**
  String get errorPleaseFillAllFields;

  /// No description provided for @menuQuickAccess.
  ///
  /// In en, this message translates to:
  /// **'Quick access'**
  String get menuQuickAccess;

  /// No description provided for @menuEditProfile.
  ///
  /// In en, this message translates to:
  /// **'Edit profile'**
  String get menuEditProfile;

  /// No description provided for @menuEditProfileSubtitle.
  ///
  /// In en, this message translates to:
  /// **'Open your details and profile settings.'**
  String get menuEditProfileSubtitle;

  /// No description provided for @menuManagePeople.
  ///
  /// In en, this message translates to:
  /// **'Manage people'**
  String get menuManagePeople;

  /// No description provided for @menuAddPerson.
  ///
  /// In en, this message translates to:
  /// **'Add person'**
  String get menuAddPerson;

  /// No description provided for @menuPeopleSubtitle.
  ///
  /// In en, this message translates to:
  /// **'Open your saved people list for bond and social flows.'**
  String get menuPeopleSubtitle;

  /// No description provided for @menuCalendar.
  ///
  /// In en, this message translates to:
  /// **'Calendar and timing'**
  String get menuCalendar;

  /// No description provided for @menuCalendarSubtitle.
  ///
  /// In en, this message translates to:
  /// **'Daily rhythm, periods and best times.'**
  String get menuCalendarSubtitle;

  /// No description provided for @menuArchetypeExperience.
  ///
  /// In en, this message translates to:
  /// **'Archetype experience'**
  String get menuArchetypeExperience;

  /// No description provided for @menuCompleteBirthData.
  ///
  /// In en, this message translates to:
  /// **'Complete birth data'**
  String get menuCompleteBirthData;

  /// No description provided for @menuArchetypeSubtitle.
  ///
  /// In en, this message translates to:
  /// **'Open your identity axis in the deeper experience.'**
  String get menuArchetypeSubtitle;

  /// No description provided for @menuCompleteBirthDataSubtitle.
  ///
  /// In en, this message translates to:
  /// **'Complete missing data to unlock archetype screens.'**
  String get menuCompleteBirthDataSubtitle;

  /// No description provided for @menuPreferences.
  ///
  /// In en, this message translates to:
  /// **'Preferences'**
  String get menuPreferences;

  /// No description provided for @menuThemeMode.
  ///
  /// In en, this message translates to:
  /// **'Theme mode'**
  String get menuThemeMode;

  /// No description provided for @themeModeDark.
  ///
  /// In en, this message translates to:
  /// **'Dark'**
  String get themeModeDark;

  /// No description provided for @themeModeLight.
  ///
  /// In en, this message translates to:
  /// **'Light'**
  String get themeModeLight;

  /// No description provided for @menuLanguage.
  ///
  /// In en, this message translates to:
  /// **'Language'**
  String get menuLanguage;

  /// No description provided for @menuNotificationPreferences.
  ///
  /// In en, this message translates to:
  /// **'Notification preferences'**
  String get menuNotificationPreferences;

  /// No description provided for @menuDailySummary.
  ///
  /// In en, this message translates to:
  /// **'Daily summary'**
  String get menuDailySummary;

  /// No description provided for @menuDailySummarySubtitle.
  ///
  /// In en, this message translates to:
  /// **'A short rhythm briefing in the morning'**
  String get menuDailySummarySubtitle;

  /// No description provided for @menuSkyEvents.
  ///
  /// In en, this message translates to:
  /// **'Sky events'**
  String get menuSkyEvents;

  /// No description provided for @menuSkyEventsSubtitle.
  ///
  /// In en, this message translates to:
  /// **'Highlighted transit and event alerts'**
  String get menuSkyEventsSubtitle;

  /// No description provided for @menuSocialActivity.
  ///
  /// In en, this message translates to:
  /// **'Social activity'**
  String get menuSocialActivity;

  /// No description provided for @menuSocialActivitySubtitle.
  ///
  /// In en, this message translates to:
  /// **'Forum and relationship-side updates'**
  String get menuSocialActivitySubtitle;

  /// No description provided for @menuMembership.
  ///
  /// In en, this message translates to:
  /// **'Membership'**
  String get menuMembership;

  /// No description provided for @menuPremiumSubscription.
  ///
  /// In en, this message translates to:
  /// **'Premium subscription'**
  String get menuPremiumSubscription;

  /// No description provided for @menuPremiumInterestSubtitle.
  ///
  /// In en, this message translates to:
  /// **'You\'re on the list. We\'ll let you know when Premium opens.'**
  String get menuPremiumInterestSubtitle;

  /// No description provided for @menuPremiumDefaultSubtitle.
  ///
  /// In en, this message translates to:
  /// **'A deeper layer for longer readings and extended flows.'**
  String get menuPremiumDefaultSubtitle;

  /// No description provided for @menuInList.
  ///
  /// In en, this message translates to:
  /// **'On list'**
  String get menuInList;

  /// No description provided for @menuSoon.
  ///
  /// In en, this message translates to:
  /// **'Soon'**
  String get menuSoon;

  /// No description provided for @menuSignOut.
  ///
  /// In en, this message translates to:
  /// **'Sign out'**
  String get menuSignOut;

  /// No description provided for @menuSignOutSubtitle.
  ///
  /// In en, this message translates to:
  /// **'Close the current session and return to login.'**
  String get menuSignOutSubtitle;

  /// No description provided for @menuPeopleCount.
  ///
  /// In en, this message translates to:
  /// **'{count} people'**
  String menuPeopleCount(int count);

  /// No description provided for @menuArchetypeReady.
  ///
  /// In en, this message translates to:
  /// **'Archetype ready'**
  String get menuArchetypeReady;

  /// No description provided for @menuBirthDataMissing.
  ///
  /// In en, this message translates to:
  /// **'Birth data missing'**
  String get menuBirthDataMissing;

  /// No description provided for @premiumSheetTitle.
  ///
  /// In en, this message translates to:
  /// **'Premium subscription'**
  String get premiumSheetTitle;

  /// No description provided for @premiumSheetBody.
  ///
  /// In en, this message translates to:
  /// **'A premium layer is being prepared for longer readings, more depth and early access.'**
  String get premiumSheetBody;

  /// No description provided for @premiumBulletIdentity.
  ///
  /// In en, this message translates to:
  /// **'Long-form identity and relationship readings'**
  String get premiumBulletIdentity;

  /// No description provided for @premiumBulletTiming.
  ///
  /// In en, this message translates to:
  /// **'Extra timing and period depth'**
  String get premiumBulletTiming;

  /// No description provided for @premiumBulletEarlyAccess.
  ///
  /// In en, this message translates to:
  /// **'Early access to new features'**
  String get premiumBulletEarlyAccess;

  /// No description provided for @premiumNotifyMe.
  ///
  /// In en, this message translates to:
  /// **'Notify me'**
  String get premiumNotifyMe;

  /// No description provided for @premiumAlreadyInList.
  ///
  /// In en, this message translates to:
  /// **'You\'re on the list'**
  String get premiumAlreadyInList;

  /// No description provided for @premiumNotifySnackbar.
  ///
  /// In en, this message translates to:
  /// **'We\'ll notify you when Premium opens.'**
  String get premiumNotifySnackbar;

  /// No description provided for @homeGreeting.
  ///
  /// In en, this message translates to:
  /// **'Hello {name}'**
  String homeGreeting(Object name);

  /// No description provided for @homeTodayLabel.
  ///
  /// In en, this message translates to:
  /// **'Today {date}'**
  String homeTodayLabel(Object date);

  /// No description provided for @homeGreetingFallbackName.
  ///
  /// In en, this message translates to:
  /// **'you'**
  String get homeGreetingFallbackName;

  /// No description provided for @periodDetailTransitTitle.
  ///
  /// In en, this message translates to:
  /// **'Transit Detail'**
  String get periodDetailTransitTitle;

  /// No description provided for @periodDetailPeriodTitle.
  ///
  /// In en, this message translates to:
  /// **'Period Detail'**
  String get periodDetailPeriodTitle;

  /// No description provided for @periodDetailTodayEyebrow.
  ///
  /// In en, this message translates to:
  /// **'Today'**
  String get periodDetailTodayEyebrow;

  /// No description provided for @periodDetailPeriodEyebrow.
  ///
  /// In en, this message translates to:
  /// **'Period'**
  String get periodDetailPeriodEyebrow;

  /// No description provided for @periodDetailContextLabel.
  ///
  /// In en, this message translates to:
  /// **'Context'**
  String get periodDetailContextLabel;

  /// No description provided for @periodDetailContextTitle.
  ///
  /// In en, this message translates to:
  /// **'Part of a larger period'**
  String get periodDetailContextTitle;

  /// No description provided for @periodDetailCoreLabel.
  ///
  /// In en, this message translates to:
  /// **'Core'**
  String get periodDetailCoreLabel;

  /// No description provided for @periodDetailCoreTitle.
  ///
  /// In en, this message translates to:
  /// **'The central line of this effect'**
  String get periodDetailCoreTitle;

  /// No description provided for @periodDetailSupportingLabel.
  ///
  /// In en, this message translates to:
  /// **'Supporting'**
  String get periodDetailSupportingLabel;

  /// No description provided for @periodDetailSupportingTitle.
  ///
  /// In en, this message translates to:
  /// **'Other layers opening up'**
  String get periodDetailSupportingTitle;

  /// No description provided for @periodDetailTechnicalLabel.
  ///
  /// In en, this message translates to:
  /// **'Technical'**
  String get periodDetailTechnicalLabel;

  /// No description provided for @periodDetailTechnicalTitle.
  ///
  /// In en, this message translates to:
  /// **'Background notes'**
  String get periodDetailTechnicalTitle;

  /// No description provided for @calendarPanelLabel.
  ///
  /// In en, this message translates to:
  /// **'Calendar'**
  String get calendarPanelLabel;

  /// No description provided for @calendarMonthMode.
  ///
  /// In en, this message translates to:
  /// **'Month'**
  String get calendarMonthMode;

  /// No description provided for @calendarWeekMode.
  ///
  /// In en, this message translates to:
  /// **'Week'**
  String get calendarWeekMode;

  /// No description provided for @calendarMonthIntro.
  ///
  /// In en, this message translates to:
  /// **'Tap a day from the month view to open that day\'s page.'**
  String get calendarMonthIntro;

  /// No description provided for @calendarWeekIntro.
  ///
  /// In en, this message translates to:
  /// **'Focus on the selected week, open a day, and move left-right through detail.'**
  String get calendarWeekIntro;

  /// No description provided for @calendarPickDate.
  ///
  /// In en, this message translates to:
  /// **'Pick date'**
  String get calendarPickDate;

  /// No description provided for @calendarDayThemeLabel.
  ///
  /// In en, this message translates to:
  /// **'Day theme'**
  String get calendarDayThemeLabel;

  /// No description provided for @calendarOpenDay.
  ///
  /// In en, this message translates to:
  /// **'Open day'**
  String get calendarOpenDay;

  /// No description provided for @calendarSelectedDayFallback.
  ///
  /// In en, this message translates to:
  /// **'When you tap a day, its cards, markers, and longer-period context open in detail.'**
  String get calendarSelectedDayFallback;

  /// No description provided for @calendarContextLabel.
  ///
  /// In en, this message translates to:
  /// **'Context'**
  String get calendarContextLabel;

  /// No description provided for @calendarLongTermEffectTitle.
  ///
  /// In en, this message translates to:
  /// **'Long-term effect'**
  String get calendarLongTermEffectTitle;

  /// No description provided for @calendarLongTermEffectFallback.
  ///
  /// In en, this message translates to:
  /// **'There is a longer-running period working behind this day.'**
  String get calendarLongTermEffectFallback;

  /// No description provided for @calendarLongTermEffectReadMore.
  ///
  /// In en, this message translates to:
  /// **'You can read the period story running in the background of the day more fully on the day page.'**
  String get calendarLongTermEffectReadMore;

  /// No description provided for @calendarPreviewFallback.
  ///
  /// In en, this message translates to:
  /// **'Quickly scan nearby days, tap one, and move into that day\'s page.'**
  String get calendarPreviewFallback;

  /// No description provided for @profileAvatarUpdated.
  ///
  /// In en, this message translates to:
  /// **'Profile photo updated'**
  String get profileAvatarUpdated;

  /// No description provided for @profileAvatarUploadFailed.
  ///
  /// In en, this message translates to:
  /// **'Profile photo could not be uploaded: {error}'**
  String profileAvatarUploadFailed(Object error);

  /// No description provided for @profileInterpretationUnavailableTitle.
  ///
  /// In en, this message translates to:
  /// **'Reading stream unavailable'**
  String get profileInterpretationUnavailableTitle;

  /// No description provided for @profileBirthDataPendingTitle.
  ///
  /// In en, this message translates to:
  /// **'Birth data pending'**
  String get profileBirthDataPendingTitle;

  /// No description provided for @profileBirthDataPendingBodyDark.
  ///
  /// In en, this message translates to:
  /// **'This screen is filled by `core_story_ui`, `profile_narrative`, `personality_imprint`, and `insight_modules`. When you complete your birth date, time, and place from profile settings, the content opens automatically.'**
  String get profileBirthDataPendingBodyDark;

  /// No description provided for @profileBirthDataPendingBodyLight.
  ///
  /// In en, this message translates to:
  /// **'This screen fills with core story, profile narrative, and insight content. When you complete your birth date, time, and place, the content opens automatically.'**
  String get profileBirthDataPendingBodyLight;

  /// No description provided for @profileIdentityAxis.
  ///
  /// In en, this message translates to:
  /// **'Identity axis'**
  String get profileIdentityAxis;

  /// No description provided for @profileMainStory.
  ///
  /// In en, this message translates to:
  /// **'Your main story'**
  String get profileMainStory;

  /// No description provided for @profileOpenFullReading.
  ///
  /// In en, this message translates to:
  /// **'Open full reading'**
  String get profileOpenFullReading;

  /// No description provided for @profileSignatureLayers.
  ///
  /// In en, this message translates to:
  /// **'Signature layers'**
  String get profileSignatureLayers;

  /// No description provided for @profileSideThemes.
  ///
  /// In en, this message translates to:
  /// **'Side themes'**
  String get profileSideThemes;

  /// No description provided for @profileWarning.
  ///
  /// In en, this message translates to:
  /// **'Warning'**
  String get profileWarning;

  /// No description provided for @profileBack.
  ///
  /// In en, this message translates to:
  /// **'Go back'**
  String get profileBack;

  /// No description provided for @profileOpenRelationshipFlow.
  ///
  /// In en, this message translates to:
  /// **'Open relationship flow'**
  String get profileOpenRelationshipFlow;

  /// No description provided for @profileOpenTimingFlow.
  ///
  /// In en, this message translates to:
  /// **'Open timing flow'**
  String get profileOpenTimingFlow;

  /// No description provided for @profileReturnToChartFlow.
  ///
  /// In en, this message translates to:
  /// **'Return to chart flow'**
  String get profileReturnToChartFlow;

  /// No description provided for @profileConnectionsLabel.
  ///
  /// In en, this message translates to:
  /// **'Connections'**
  String get profileConnectionsLabel;

  /// No description provided for @profileConnectionsTitle.
  ///
  /// In en, this message translates to:
  /// **'People you added'**
  String get profileConnectionsTitle;

  /// No description provided for @profileConnectionsBody.
  ///
  /// In en, this message translates to:
  /// **'Your real friend list opened from following and followers appears here.'**
  String get profileConnectionsBody;

  /// No description provided for @profileFriendLabel.
  ///
  /// In en, this message translates to:
  /// **'Friend'**
  String get profileFriendLabel;

  /// No description provided for @profileLocationMissing.
  ///
  /// In en, this message translates to:
  /// **'location missing'**
  String get profileLocationMissing;

  /// No description provided for @profileFollowing.
  ///
  /// In en, this message translates to:
  /// **'Following'**
  String get profileFollowing;

  /// No description provided for @profileFollowers.
  ///
  /// In en, this message translates to:
  /// **'Followers'**
  String get profileFollowers;

  /// No description provided for @profileOpenSinglePersonProfile.
  ///
  /// In en, this message translates to:
  /// **'{name}\'s profile'**
  String profileOpenSinglePersonProfile(Object name);

  /// No description provided for @profileOpenManyPersonProfiles.
  ///
  /// In en, this message translates to:
  /// **'View {count} friend profiles'**
  String profileOpenManyPersonProfiles(int count);

  /// No description provided for @profileSunLabel.
  ///
  /// In en, this message translates to:
  /// **'Sun'**
  String get profileSunLabel;

  /// No description provided for @profileRisingLabel.
  ///
  /// In en, this message translates to:
  /// **'Rising'**
  String get profileRisingLabel;

  /// No description provided for @profileMoonLabel.
  ///
  /// In en, this message translates to:
  /// **'Moon'**
  String get profileMoonLabel;

  /// No description provided for @profileIdentityLabel.
  ///
  /// In en, this message translates to:
  /// **'IDENTITY'**
  String get profileIdentityLabel;

  /// No description provided for @profileIdentityReading.
  ///
  /// In en, this message translates to:
  /// **'Identity reading'**
  String get profileIdentityReading;

  /// No description provided for @profileOpenIdentityReading.
  ///
  /// In en, this message translates to:
  /// **'Open identity reading'**
  String get profileOpenIdentityReading;

  /// No description provided for @profileGenerateResult.
  ///
  /// In en, this message translates to:
  /// **'Generate result'**
  String get profileGenerateResult;

  /// No description provided for @profileConfidenceScore.
  ///
  /// In en, this message translates to:
  /// **'Confidence score {score}'**
  String profileConfidenceScore(Object score);

  /// No description provided for @profileNatalLoadFailed.
  ///
  /// In en, this message translates to:
  /// **'Natal reading could not be loaded: {error}'**
  String profileNatalLoadFailed(Object error);

  /// No description provided for @profileTimingFlowLabel.
  ///
  /// In en, this message translates to:
  /// **'TIMING FLOW'**
  String get profileTimingFlowLabel;

  /// No description provided for @profileTimingFlowUnavailable.
  ///
  /// In en, this message translates to:
  /// **'Timing flow unavailable'**
  String get profileTimingFlowUnavailable;

  /// No description provided for @profileTimingFlowNotReady.
  ///
  /// In en, this message translates to:
  /// **'Timing flow not ready'**
  String get profileTimingFlowNotReady;

  /// No description provided for @profileTimingFlowNotReadyBody.
  ///
  /// In en, this message translates to:
  /// **'When the period summary arrives, only a short teaser and upcoming peaks will appear here.'**
  String get profileTimingFlowNotReadyBody;

  /// No description provided for @profileCurrentPeriod.
  ///
  /// In en, this message translates to:
  /// **'Current period'**
  String get profileCurrentPeriod;

  /// No description provided for @profileUpcomingPeaks.
  ///
  /// In en, this message translates to:
  /// **'Upcoming peaks'**
  String get profileUpcomingPeaks;

  /// No description provided for @profileNextLabel.
  ///
  /// In en, this message translates to:
  /// **'Next: {label}'**
  String profileNextLabel(Object label);

  /// No description provided for @profileMoreOpen.
  ///
  /// In en, this message translates to:
  /// **'Open more'**
  String get profileMoreOpen;

  /// No description provided for @profileNatal.
  ///
  /// In en, this message translates to:
  /// **'Natal'**
  String get profileNatal;

  /// No description provided for @profileRelationship.
  ///
  /// In en, this message translates to:
  /// **'Relationship'**
  String get profileRelationship;

  /// No description provided for @profileTiming.
  ///
  /// In en, this message translates to:
  /// **'Timing'**
  String get profileTiming;

  /// No description provided for @profileMainReading.
  ///
  /// In en, this message translates to:
  /// **'Main reading'**
  String get profileMainReading;

  /// No description provided for @profileShadowGrowth.
  ///
  /// In en, this message translates to:
  /// **'Shadow & growth'**
  String get profileShadowGrowth;

  /// No description provided for @profileIdentityEyebrow.
  ///
  /// In en, this message translates to:
  /// **'Identity'**
  String get profileIdentityEyebrow;

  /// No description provided for @profileIdentityFlow.
  ///
  /// In en, this message translates to:
  /// **'Identity flow'**
  String get profileIdentityFlow;

  /// No description provided for @profileIdentityTone.
  ///
  /// In en, this message translates to:
  /// **'Identity tone'**
  String get profileIdentityTone;

  /// No description provided for @profileIdentitySummary.
  ///
  /// In en, this message translates to:
  /// **'Identity summary'**
  String get profileIdentitySummary;

  /// No description provided for @profileArchetypeBirthDataRequired.
  ///
  /// In en, this message translates to:
  /// **'Birth date, time, and place are required before opening the archetype experience.'**
  String get profileArchetypeBirthDataRequired;

  /// No description provided for @profileIdentityFlowSubtitleFallback.
  ///
  /// In en, this message translates to:
  /// **'See a longer read of how your identity is perceived from the outside and inside here.'**
  String get profileIdentityFlowSubtitleFallback;

  /// No description provided for @profileNarrativeFlowSubtitleFallback.
  ///
  /// In en, this message translates to:
  /// **'Read more clearly how this section works in you here.'**
  String get profileNarrativeFlowSubtitleFallback;

  /// No description provided for @profileSignatureCatalogSubtitle.
  ///
  /// In en, this message translates to:
  /// **'In the card list you only see the titles; tap one card to open only its detail.'**
  String get profileSignatureCatalogSubtitle;

  /// No description provided for @profileSignatureCardSubtitleFallback.
  ///
  /// In en, this message translates to:
  /// **'The full explanation of this personality signature card opens here.'**
  String get profileSignatureCardSubtitleFallback;

  /// No description provided for @profileSideThemesFlowSubtitle.
  ///
  /// In en, this message translates to:
  /// **'Other sides that complete your main portrait stand out here.'**
  String get profileSideThemesFlowSubtitle;

  /// No description provided for @profileInsightFlowSubtitleFallback.
  ///
  /// In en, this message translates to:
  /// **'This section opens the full flow on the axis of defense and growth.'**
  String get profileInsightFlowSubtitleFallback;

  /// No description provided for @profileOpenDefensePattern.
  ///
  /// In en, this message translates to:
  /// **'Open your defense pattern'**
  String get profileOpenDefensePattern;

  /// No description provided for @profileSeeArchetype.
  ///
  /// In en, this message translates to:
  /// **'See your archetype'**
  String get profileSeeArchetype;

  /// No description provided for @profileArchetypeBodyReady.
  ///
  /// In en, this message translates to:
  /// **'Open the active identity, protection, and tension lines in your chart in a single experience.'**
  String get profileArchetypeBodyReady;

  /// No description provided for @profileArchetypeBodyPending.
  ///
  /// In en, this message translates to:
  /// **'When you complete your birth date, time, and place, the archetype experience will open here.'**
  String get profileArchetypeBodyPending;

  /// No description provided for @profileCompleteBirthData.
  ///
  /// In en, this message translates to:
  /// **'Complete your birth data'**
  String get profileCompleteBirthData;

  /// No description provided for @profileOnlineFriends.
  ///
  /// In en, this message translates to:
  /// **'ONLINE FRIENDS'**
  String get profileOnlineFriends;

  /// No description provided for @profileQuietSocialCircle.
  ///
  /// In en, this message translates to:
  /// **'A calmer social circle'**
  String get profileQuietSocialCircle;

  /// No description provided for @profileIdentitySummaryFallback.
  ///
  /// In en, this message translates to:
  /// **'Your identity axis opens from the profile narrative.'**
  String get profileIdentitySummaryFallback;

  /// No description provided for @profileNarrativeLoading.
  ///
  /// In en, this message translates to:
  /// **'Profile narrative is being pulled from the backend reading...'**
  String get profileNarrativeLoading;

  /// No description provided for @profilePlacementsAndAspects.
  ///
  /// In en, this message translates to:
  /// **'PLACEMENTS & ASPECTS'**
  String get profilePlacementsAndAspects;

  /// No description provided for @profileOpenSideThemes.
  ///
  /// In en, this message translates to:
  /// **'Open side themes'**
  String get profileOpenSideThemes;

  /// No description provided for @profilePlacement.
  ///
  /// In en, this message translates to:
  /// **'Placement'**
  String get profilePlacement;

  /// No description provided for @profileAspect.
  ///
  /// In en, this message translates to:
  /// **'Aspect'**
  String get profileAspect;

  /// No description provided for @profileSignTone.
  ///
  /// In en, this message translates to:
  /// **'Sign tone'**
  String get profileSignTone;

  /// No description provided for @profileFeaturedTheme.
  ///
  /// In en, this message translates to:
  /// **'Featured theme'**
  String get profileFeaturedTheme;

  /// No description provided for @profileRuler.
  ///
  /// In en, this message translates to:
  /// **'Ruler'**
  String get profileRuler;

  /// No description provided for @profileStrongestRuler.
  ///
  /// In en, this message translates to:
  /// **'Strongest ruler: {name}'**
  String profileStrongestRuler(Object name);

  /// No description provided for @profileSignRuler.
  ///
  /// In en, this message translates to:
  /// **'{sign} ruler'**
  String profileSignRuler(Object sign);

  /// No description provided for @profileChartBackbone.
  ///
  /// In en, this message translates to:
  /// **'Chart backbone'**
  String get profileChartBackbone;

  /// No description provided for @profileHouseEmphasis.
  ///
  /// In en, this message translates to:
  /// **'{house}. house emphasis'**
  String profileHouseEmphasis(int house);

  /// No description provided for @profileEarthInfluential.
  ///
  /// In en, this message translates to:
  /// **'Earth influential'**
  String get profileEarthInfluential;

  /// No description provided for @profileOutsideInside.
  ///
  /// In en, this message translates to:
  /// **'Outside and inside'**
  String get profileOutsideInside;

  /// No description provided for @profileMindWorks.
  ///
  /// In en, this message translates to:
  /// **'How your mind works'**
  String get profileMindWorks;

  /// No description provided for @profileSelfProtection.
  ///
  /// In en, this message translates to:
  /// **'How you protect yourself'**
  String get profileSelfProtection;

  /// No description provided for @profileIntimacyOpens.
  ///
  /// In en, this message translates to:
  /// **'How intimacy opens in you'**
  String get profileIntimacyOpens;

  /// No description provided for @profileHoldReleaseBalance.
  ///
  /// In en, this message translates to:
  /// **'Balance between holding and releasing'**
  String get profileHoldReleaseBalance;

  /// No description provided for @profileWhereOpportunityFlows.
  ///
  /// In en, this message translates to:
  /// **'Where opportunity flows'**
  String get profileWhereOpportunityFlows;

  /// No description provided for @profileRecognizableLine.
  ///
  /// In en, this message translates to:
  /// **'The line that is easily recognized in you'**
  String get profileRecognizableLine;

  /// No description provided for @profileTwoInnerDirections.
  ///
  /// In en, this message translates to:
  /// **'How your two inner directions work'**
  String get profileTwoInnerDirections;

  /// No description provided for @profileStandoutSide.
  ///
  /// In en, this message translates to:
  /// **'The side that stands out in you'**
  String get profileStandoutSide;

  /// No description provided for @profileElementFireDominant.
  ///
  /// In en, this message translates to:
  /// **'Fire dominant'**
  String get profileElementFireDominant;

  /// No description provided for @profileElementWaterDominant.
  ///
  /// In en, this message translates to:
  /// **'Water dominant'**
  String get profileElementWaterDominant;

  /// No description provided for @profileElementAirDominant.
  ///
  /// In en, this message translates to:
  /// **'Air dominant'**
  String get profileElementAirDominant;

  /// No description provided for @profileElementEarthDominant.
  ///
  /// In en, this message translates to:
  /// **'Earth dominant'**
  String get profileElementEarthDominant;

  /// No description provided for @profileBirthPlacePending.
  ///
  /// In en, this message translates to:
  /// **'Birth place pending'**
  String get profileBirthPlacePending;

  /// No description provided for @profileAgeLabel.
  ///
  /// In en, this message translates to:
  /// **'{age} years old'**
  String profileAgeLabel(int age);

  /// No description provided for @calendarSelectedDaySummaryPrompt.
  ///
  /// In en, this message translates to:
  /// **'Tap the selected day to open its rhythm, cards, and long-term effect.'**
  String get calendarSelectedDaySummaryPrompt;

  /// No description provided for @calendarMarkerDirectionChange.
  ///
  /// In en, this message translates to:
  /// **'Direction change'**
  String get calendarMarkerDirectionChange;

  /// No description provided for @calendarMarkerNewArea.
  ///
  /// In en, this message translates to:
  /// **'New area'**
  String get calendarMarkerNewArea;

  /// No description provided for @calendarMarkerRetrograde.
  ///
  /// In en, this message translates to:
  /// **'Retrograde'**
  String get calendarMarkerRetrograde;

  /// No description provided for @calendarMarkerPeak.
  ///
  /// In en, this message translates to:
  /// **'Peak'**
  String get calendarMarkerPeak;

  /// No description provided for @calendarMarkerBeginning.
  ///
  /// In en, this message translates to:
  /// **'Beginning'**
  String get calendarMarkerBeginning;

  /// No description provided for @calendarMarkerThreshold.
  ///
  /// In en, this message translates to:
  /// **'Threshold'**
  String get calendarMarkerThreshold;

  /// No description provided for @calendarMarkerMultipleThresholds.
  ///
  /// In en, this message translates to:
  /// **'multiple thresholds'**
  String get calendarMarkerMultipleThresholds;

  /// No description provided for @calendarFallbackSensitiveDay.
  ///
  /// In en, this message translates to:
  /// **'Sensitive day.'**
  String get calendarFallbackSensitiveDay;

  /// No description provided for @calendarFallbackHighTempo.
  ///
  /// In en, this message translates to:
  /// **'High tempo.'**
  String get calendarFallbackHighTempo;

  /// No description provided for @calendarFallbackBusyDay.
  ///
  /// In en, this message translates to:
  /// **'Busy day.'**
  String get calendarFallbackBusyDay;

  /// No description provided for @calendarFallbackTwoSignals.
  ///
  /// In en, this message translates to:
  /// **'Two things stand out today.'**
  String get calendarFallbackTwoSignals;

  /// No description provided for @calendarFallbackOneSignal.
  ///
  /// In en, this message translates to:
  /// **'One thing stands out.'**
  String get calendarFallbackOneSignal;

  /// No description provided for @calendarFallbackMixedDay.
  ///
  /// In en, this message translates to:
  /// **'Today feels a bit mixed.'**
  String get calendarFallbackMixedDay;

  /// No description provided for @calendarFallbackCalmDay.
  ///
  /// In en, this message translates to:
  /// **'Today is calm.'**
  String get calendarFallbackCalmDay;

  /// No description provided for @calendarFallbackHooked.
  ///
  /// In en, this message translates to:
  /// **'You may get snagged on things quickly today.'**
  String get calendarFallbackHooked;

  /// No description provided for @calendarFallbackSeveralThings.
  ///
  /// In en, this message translates to:
  /// **'Several things may draw your attention at once.'**
  String get calendarFallbackSeveralThings;

  /// No description provided for @calendarFallbackOneThingPushes.
  ///
  /// In en, this message translates to:
  /// **'One thing is pushing the day\'s rhythm forward a bit.'**
  String get calendarFallbackOneThingPushes;

  /// No description provided for @calendarFallbackSimpleRhythm.
  ///
  /// In en, this message translates to:
  /// **'Today\'s rhythm is flowing a bit more simply.'**
  String get calendarFallbackSimpleRhythm;

  /// No description provided for @calendarFallbackBreath.
  ///
  /// In en, this message translates to:
  /// **'A breath will help.'**
  String get calendarFallbackBreath;

  /// No description provided for @calendarFallbackDoNotPileOn.
  ///
  /// In en, this message translates to:
  /// **'Don\'t load everything on at once.'**
  String get calendarFallbackDoNotPileOn;

  /// No description provided for @calendarFallbackDoNotRush.
  ///
  /// In en, this message translates to:
  /// **'Don\'t rush.'**
  String get calendarFallbackDoNotRush;

  /// No description provided for @calendarFallbackLeaveSimple.
  ///
  /// In en, this message translates to:
  /// **'Keep today a little simpler.'**
  String get calendarFallbackLeaveSimple;

  /// No description provided for @calendarHouseTouchpointHint.
  ///
  /// In en, this message translates to:
  /// **'It may show up most around {area}.'**
  String calendarHouseTouchpointHint(Object area);

  /// No description provided for @calendarEditorialCurrentFallback.
  ///
  /// In en, this message translates to:
  /// **'The rhythm of the day becomes a bit more readable here.'**
  String get calendarEditorialCurrentFallback;

  /// No description provided for @calendarEditorialChangeFallback.
  ///
  /// In en, this message translates to:
  /// **'Notice which area of your life this shows up in most.'**
  String get calendarEditorialChangeFallback;

  /// No description provided for @calendarEditorialDirectionFallback.
  ///
  /// In en, this message translates to:
  /// **'The theme does not end here; it will take more shape over the coming days.'**
  String get calendarEditorialDirectionFallback;

  /// No description provided for @calendarEditorialSecondaryFallback.
  ///
  /// In en, this message translates to:
  /// **'This is a second layer working alongside it in the background.'**
  String get calendarEditorialSecondaryFallback;

  /// No description provided for @calendarPhaseIntensifying.
  ///
  /// In en, this message translates to:
  /// **'Intensifying'**
  String get calendarPhaseIntensifying;

  /// No description provided for @calendarPhasePeakToday.
  ///
  /// In en, this message translates to:
  /// **'Peaking today'**
  String get calendarPhasePeakToday;

  /// No description provided for @calendarPhaseReleasing.
  ///
  /// In en, this message translates to:
  /// **'Starting to release'**
  String get calendarPhaseReleasing;

  /// No description provided for @calendarTimingPeak.
  ///
  /// In en, this message translates to:
  /// **'Peak {date}'**
  String calendarTimingPeak(Object date);

  /// No description provided for @calendarTimingStart.
  ///
  /// In en, this message translates to:
  /// **'Start {date}'**
  String calendarTimingStart(Object date);

  /// No description provided for @calendarTimingPrefix.
  ///
  /// In en, this message translates to:
  /// **'Timing: {timing}'**
  String calendarTimingPrefix(Object timing);

  /// No description provided for @calendarBestWindow.
  ///
  /// In en, this message translates to:
  /// **'Best window this week: {labels}'**
  String calendarBestWindow(Object labels);

  /// No description provided for @calendarCombinedTitle.
  ///
  /// In en, this message translates to:
  /// **'Unified calendar'**
  String get calendarCombinedTitle;

  /// No description provided for @calendarCombinedBody.
  ///
  /// In en, this message translates to:
  /// **'Follow the month and week flow on the same surface. When you tap a day, that day\'s page opens and the long-term context stays intact.'**
  String get calendarCombinedBody;

  /// No description provided for @calendarProfileLoadFailed.
  ///
  /// In en, this message translates to:
  /// **'Profile data could not be loaded.'**
  String get calendarProfileLoadFailed;

  /// No description provided for @calendarBirthDataRequiredTitle.
  ///
  /// In en, this message translates to:
  /// **'Birth data required for calendar'**
  String get calendarBirthDataRequiredTitle;

  /// No description provided for @calendarBirthDataRequiredBody.
  ///
  /// In en, this message translates to:
  /// **'When birth date, time, and place are completed, the calendar opens.'**
  String get calendarBirthDataRequiredBody;

  /// No description provided for @calendarSectionNow.
  ///
  /// In en, this message translates to:
  /// **'What\'s happening now'**
  String get calendarSectionNow;

  /// No description provided for @calendarSelectedDayWindows.
  ///
  /// In en, this message translates to:
  /// **'Selected day windows'**
  String get calendarSelectedDayWindows;

  /// No description provided for @calendarSectionChange.
  ///
  /// In en, this message translates to:
  /// **'What this changes in you'**
  String get calendarSectionChange;

  /// No description provided for @calendarSectionDirection.
  ///
  /// In en, this message translates to:
  /// **'Where it\'s going'**
  String get calendarSectionDirection;

  /// No description provided for @calendarSectionBackground.
  ///
  /// In en, this message translates to:
  /// **'What is working underneath'**
  String get calendarSectionBackground;

  /// No description provided for @calendarSectionSecondaryTheme.
  ///
  /// In en, this message translates to:
  /// **'Additional theme in play'**
  String get calendarSectionSecondaryTheme;

  /// No description provided for @calendarOpenMainTheme.
  ///
  /// In en, this message translates to:
  /// **'Open main theme'**
  String get calendarOpenMainTheme;

  /// No description provided for @calendarOpenPeriod.
  ///
  /// In en, this message translates to:
  /// **'Open period'**
  String get calendarOpenPeriod;

  /// No description provided for @calendarWhyItMatters.
  ///
  /// In en, this message translates to:
  /// **'Why does this matter?'**
  String get calendarWhyItMatters;

  /// No description provided for @calendarLongTermLabel.
  ///
  /// In en, this message translates to:
  /// **'Long term'**
  String get calendarLongTermLabel;

  /// No description provided for @calendarLongTermActiveTodayTitle.
  ///
  /// In en, this message translates to:
  /// **'The long-term story is still active today'**
  String get calendarLongTermActiveTodayTitle;

  /// No description provided for @calendarLongTermActiveTodayBody.
  ///
  /// In en, this message translates to:
  /// **'This is not today itself; it is the longer story carrying today from the background.'**
  String get calendarLongTermActiveTodayBody;

  /// No description provided for @calendarOpenCalendar.
  ///
  /// In en, this message translates to:
  /// **'Open calendar'**
  String get calendarOpenCalendar;

  /// No description provided for @calendarLongTermEffectPrefix.
  ///
  /// In en, this message translates to:
  /// **'Long-term effect: {title}'**
  String calendarLongTermEffectPrefix(Object title);

  /// No description provided for @calendarBackgroundActive.
  ///
  /// In en, this message translates to:
  /// **'active in the background'**
  String get calendarBackgroundActive;

  /// No description provided for @calendarDailyReadingPreparing.
  ///
  /// In en, this message translates to:
  /// **'The main reading for this day is being prepared.'**
  String get calendarDailyReadingPreparing;

  /// No description provided for @calendarSelectedDayCalm.
  ///
  /// In en, this message translates to:
  /// **'Selected day is calm'**
  String get calendarSelectedDayCalm;

  /// No description provided for @calendarNoDistinctEventCard.
  ///
  /// In en, this message translates to:
  /// **'There is no standout event card for this day. You can choose another day from the calendar and check the flow.'**
  String get calendarNoDistinctEventCard;

  /// No description provided for @calendarMonthPanelBody.
  ///
  /// In en, this message translates to:
  /// **'The month view that behaves like a calendar lives here. Tap a day and open daily data in the same flow.'**
  String get calendarMonthPanelBody;

  /// No description provided for @calendarTimingPersonalized.
  ///
  /// In en, this message translates to:
  /// **'Your personal timing'**
  String get calendarTimingPersonalized;

  /// No description provided for @calendarTimingPersonalizedBody.
  ///
  /// In en, this message translates to:
  /// **'You can read the periods opening ahead of you here in a calmer order.'**
  String get calendarTimingPersonalizedBody;

  /// No description provided for @calendarPeriodLabel.
  ///
  /// In en, this message translates to:
  /// **'Period'**
  String get calendarPeriodLabel;

  /// No description provided for @calendarCurrentPeriodTheme.
  ///
  /// In en, this message translates to:
  /// **'The main theme of this period'**
  String get calendarCurrentPeriodTheme;

  /// No description provided for @calendarTimingPreparing.
  ///
  /// In en, this message translates to:
  /// **'Timing is being prepared'**
  String get calendarTimingPreparing;

  /// No description provided for @calendarTimingPreparingBody.
  ///
  /// In en, this message translates to:
  /// **'The editorial list of your personal periods is loading.'**
  String get calendarTimingPreparingBody;

  /// No description provided for @calendarNoSelectedPeriod.
  ///
  /// In en, this message translates to:
  /// **'No selected period'**
  String get calendarNoSelectedPeriod;

  /// No description provided for @calendarNoSelectedPeriodBody.
  ///
  /// In en, this message translates to:
  /// **'You\'ll see it here when active period cards are ready.'**
  String get calendarNoSelectedPeriodBody;

  /// No description provided for @calendarPeakListShort.
  ///
  /// In en, this message translates to:
  /// **'Short peak list'**
  String get calendarPeakListShort;

  /// No description provided for @calendarPeakListBody.
  ///
  /// In en, this message translates to:
  /// **'Follow the dates when the effects ahead of you get stronger, in order.'**
  String get calendarPeakListBody;

  /// No description provided for @calendarPeriodCardNotFound.
  ///
  /// In en, this message translates to:
  /// **'No period card found'**
  String get calendarPeriodCardNotFound;

  /// No description provided for @calendarPeriodCardNotFoundBody.
  ///
  /// In en, this message translates to:
  /// **'No period marker/card was found.'**
  String get calendarPeriodCardNotFoundBody;

  /// No description provided for @calendarPeriodCardsTitle.
  ///
  /// In en, this message translates to:
  /// **'Period cards'**
  String get calendarPeriodCardsTitle;

  /// No description provided for @calendarTransitTimeout.
  ///
  /// In en, this message translates to:
  /// **'The transit summary did not return in time. I lightened the period screen; can you try again?'**
  String get calendarTransitTimeout;

  /// No description provided for @calendarInvalidDateOrProfile.
  ///
  /// In en, this message translates to:
  /// **'The submitted date or profile fields are invalid (422).'**
  String get calendarInvalidDateOrProfile;

  /// No description provided for @calendarPeriodDataUnavailable.
  ///
  /// In en, this message translates to:
  /// **'Period data could not be loaded.'**
  String get calendarPeriodDataUnavailable;

  /// No description provided for @calendarPeriodCoreFallbackTitle.
  ///
  /// In en, this message translates to:
  /// **'The main theme of this period'**
  String get calendarPeriodCoreFallbackTitle;

  /// No description provided for @calendarPeriodCoreFallbackBody.
  ///
  /// In en, this message translates to:
  /// **'The period summary is not ready yet.'**
  String get calendarPeriodCoreFallbackBody;

  /// No description provided for @calendarTodayForeground.
  ///
  /// In en, this message translates to:
  /// **'This stands out most today.'**
  String get calendarTodayForeground;

  /// No description provided for @calendarPeriodFromBackgroundToday.
  ///
  /// In en, this message translates to:
  /// **'Today, rather than a short trigger, the theme working in the background stands out.'**
  String get calendarPeriodFromBackgroundToday;

  /// No description provided for @aiOnline.
  ///
  /// In en, this message translates to:
  /// **'Online'**
  String get aiOnline;

  /// No description provided for @aiIntroMessage.
  ///
  /// In en, this message translates to:
  /// **'Hello, I\'m Aila. If you want, write what you\'re feeling today, something on your mind, or a chart detail you\'re curious about.'**
  String get aiIntroMessage;

  /// No description provided for @aiUserLabel.
  ///
  /// In en, this message translates to:
  /// **'You'**
  String get aiUserLabel;

  /// No description provided for @aiNow.
  ///
  /// In en, this message translates to:
  /// **'Now'**
  String get aiNow;

  /// No description provided for @aiComposerHint.
  ///
  /// In en, this message translates to:
  /// **'Write to Aila...'**
  String get aiComposerHint;

  /// No description provided for @aiFreeRemaining.
  ///
  /// In en, this message translates to:
  /// **'{count} free left'**
  String aiFreeRemaining(int count);

  /// No description provided for @aiCreditsRemaining.
  ///
  /// In en, this message translates to:
  /// **'{count} credits'**
  String aiCreditsRemaining(int count);

  /// No description provided for @aiProActive.
  ///
  /// In en, this message translates to:
  /// **'Pro active'**
  String get aiProActive;

  /// No description provided for @aiSending.
  ///
  /// In en, this message translates to:
  /// **'Aila is thinking...'**
  String get aiSending;

  /// No description provided for @aiPaywallTitle.
  ///
  /// In en, this message translates to:
  /// **'Continue with credits or Pro'**
  String get aiPaywallTitle;

  /// No description provided for @aiPaywallBody.
  ///
  /// In en, this message translates to:
  /// **'You used all 3 free questions. Buy a credit pack or unlock Pro to keep chatting.'**
  String get aiPaywallBody;

  /// No description provided for @aiPaywallLoading.
  ///
  /// In en, this message translates to:
  /// **'Loading products...'**
  String get aiPaywallLoading;

  /// No description provided for @aiPaywallUnavailable.
  ///
  /// In en, this message translates to:
  /// **'Purchases are not available right now.'**
  String get aiPaywallUnavailable;

  /// No description provided for @aiPaywallRestoreHint.
  ///
  /// In en, this message translates to:
  /// **'After purchase, retry your message in a few seconds while the webhook updates your balance.'**
  String get aiPaywallRestoreHint;

  /// No description provided for @aiProductQ1Title.
  ///
  /// In en, this message translates to:
  /// **'1 question'**
  String get aiProductQ1Title;

  /// No description provided for @aiProductQ1Subtitle.
  ///
  /// In en, this message translates to:
  /// **'Single reply credit'**
  String get aiProductQ1Subtitle;

  /// No description provided for @aiProductQ5Title.
  ///
  /// In en, this message translates to:
  /// **'5 questions'**
  String get aiProductQ5Title;

  /// No description provided for @aiProductQ5Subtitle.
  ///
  /// In en, this message translates to:
  /// **'Credit pack for a short streak'**
  String get aiProductQ5Subtitle;

  /// No description provided for @aiProductQ15Title.
  ///
  /// In en, this message translates to:
  /// **'15 questions'**
  String get aiProductQ15Title;

  /// No description provided for @aiProductQ15Subtitle.
  ///
  /// In en, this message translates to:
  /// **'Credit pack for heavier use'**
  String get aiProductQ15Subtitle;

  /// No description provided for @aiProductProTitle.
  ///
  /// In en, this message translates to:
  /// **'Pro monthly'**
  String get aiProductProTitle;

  /// No description provided for @aiProductProSubtitle.
  ///
  /// In en, this message translates to:
  /// **'Unlimited chat while Pro is active'**
  String get aiProductProSubtitle;

  /// No description provided for @aiStorePriceUnavailable.
  ///
  /// In en, this message translates to:
  /// **'Unavailable'**
  String get aiStorePriceUnavailable;

  /// No description provided for @aiPurchasePending.
  ///
  /// In en, this message translates to:
  /// **'Purchase received. Retry your message in a few seconds.'**
  String get aiPurchasePending;

  /// No description provided for @aiPurchaseNotSupported.
  ///
  /// In en, this message translates to:
  /// **'Purchases are only available on iOS and Android.'**
  String get aiPurchaseNotSupported;

  /// No description provided for @aiChatUnavailable.
  ///
  /// In en, this message translates to:
  /// **'AI chat is unavailable right now: {error}'**
  String aiChatUnavailable(Object error);

  /// No description provided for @peopleFormAddTitle.
  ///
  /// In en, this message translates to:
  /// **'Add person'**
  String get peopleFormAddTitle;

  /// No description provided for @peopleFormEditTitle.
  ///
  /// In en, this message translates to:
  /// **'Edit person'**
  String get peopleFormEditTitle;

  /// No description provided for @peopleFormNameRequired.
  ///
  /// In en, this message translates to:
  /// **'Name is required.'**
  String get peopleFormNameRequired;

  /// No description provided for @peopleFormBirthDateRequired.
  ///
  /// In en, this message translates to:
  /// **'Birth date is required.'**
  String get peopleFormBirthDateRequired;

  /// No description provided for @peopleFormBirthTimeOptional.
  ///
  /// In en, this message translates to:
  /// **'Birth time (optional)'**
  String get peopleFormBirthTimeOptional;

  /// No description provided for @peopleFormBirthTimeHint.
  ///
  /// In en, this message translates to:
  /// **'If you do not know the birth time, you can leave it empty.'**
  String get peopleFormBirthTimeHint;

  /// No description provided for @peopleFormCityRequired.
  ///
  /// In en, this message translates to:
  /// **'City is required.'**
  String get peopleFormCityRequired;

  /// No description provided for @peopleFormCountryRequired.
  ///
  /// In en, this message translates to:
  /// **'Country is required.'**
  String get peopleFormCountryRequired;

  /// No description provided for @peopleFormSaving.
  ///
  /// In en, this message translates to:
  /// **'Saving...'**
  String get peopleFormSaving;

  /// No description provided for @peopleFormLoginRequired.
  ///
  /// In en, this message translates to:
  /// **'Sign in before adding a person.'**
  String get peopleFormLoginRequired;

  /// No description provided for @peopleFormSaveFailed.
  ///
  /// In en, this message translates to:
  /// **'Person could not be saved: {error}'**
  String peopleFormSaveFailed(Object error);

  /// No description provided for @peoplePageLabel.
  ///
  /// In en, this message translates to:
  /// **'People'**
  String get peoplePageLabel;

  /// No description provided for @peoplePageCenterText.
  ///
  /// In en, this message translates to:
  /// **'your circle'**
  String get peoplePageCenterText;

  /// No description provided for @peoplePageAddTooltip.
  ///
  /// In en, this message translates to:
  /// **'Add person'**
  String get peoplePageAddTooltip;

  /// No description provided for @peoplePageEmptyTitle.
  ///
  /// In en, this message translates to:
  /// **'No saved people yet'**
  String get peoplePageEmptyTitle;

  /// No description provided for @peoplePageEmptyBody.
  ///
  /// In en, this message translates to:
  /// **'Save people from your circle here to use them in Bond and social flows.'**
  String get peoplePageEmptyBody;

  /// No description provided for @peoplePageCircleLabel.
  ///
  /// In en, this message translates to:
  /// **'Circle'**
  String get peoplePageCircleLabel;

  /// No description provided for @peoplePageCircleTitle.
  ///
  /// In en, this message translates to:
  /// **'Saved people'**
  String get peoplePageCircleTitle;

  /// No description provided for @peoplePageCircleBody.
  ///
  /// In en, this message translates to:
  /// **'The people you use for Bond, friend profiles, and social flows appear here.'**
  String get peoplePageCircleBody;

  /// No description provided for @peoplePageHeroLabel.
  ///
  /// In en, this message translates to:
  /// **'People'**
  String get peoplePageHeroLabel;

  /// No description provided for @peoplePageHeroTitle.
  ///
  /// In en, this message translates to:
  /// **'Keep your circle here for Bond and social flows'**
  String get peoplePageHeroTitle;

  /// No description provided for @peoplePageHeroBody.
  ///
  /// In en, this message translates to:
  /// **'The people you add are reused from the same place for Bond matches, friend profiles, and future social readings.'**
  String get peoplePageHeroBody;

  /// No description provided for @peoplePagePillAura.
  ///
  /// In en, this message translates to:
  /// **'Aura'**
  String get peoplePagePillAura;

  /// No description provided for @peoplePagePillBirthAxis.
  ///
  /// In en, this message translates to:
  /// **'Birth axis'**
  String get peoplePagePillBirthAxis;

  /// No description provided for @peoplePagePillSocialTone.
  ///
  /// In en, this message translates to:
  /// **'Social tone'**
  String get peoplePagePillSocialTone;

  /// No description provided for @peoplePageListLoadFailedTitle.
  ///
  /// In en, this message translates to:
  /// **'People list unavailable'**
  String get peoplePageListLoadFailedTitle;

  /// No description provided for @peoplePageListLoadFailed.
  ///
  /// In en, this message translates to:
  /// **'People list could not be loaded: {error}'**
  String peoplePageListLoadFailed(Object error);

  /// No description provided for @peoplePageFriendLabel.
  ///
  /// In en, this message translates to:
  /// **'Person'**
  String get peoplePageFriendLabel;

  /// No description provided for @peoplePageNoBirthTime.
  ///
  /// In en, this message translates to:
  /// **'No birth time'**
  String get peoplePageNoBirthTime;

  /// No description provided for @peoplePageEditTooltip.
  ///
  /// In en, this message translates to:
  /// **'Edit'**
  String get peoplePageEditTooltip;

  /// No description provided for @peopleRepoListFailed.
  ///
  /// In en, this message translates to:
  /// **'People list could not be fetched.'**
  String get peopleRepoListFailed;

  /// No description provided for @peopleRepoDetailFailed.
  ///
  /// In en, this message translates to:
  /// **'Person details could not be fetched.'**
  String get peopleRepoDetailFailed;

  /// No description provided for @peopleRepoCreateFailed.
  ///
  /// In en, this message translates to:
  /// **'Person could not be created.'**
  String get peopleRepoCreateFailed;

  /// No description provided for @peopleRepoUpdateFailed.
  ///
  /// In en, this message translates to:
  /// **'Person could not be updated.'**
  String get peopleRepoUpdateFailed;

  /// No description provided for @peopleRepoProfilesListUnsupported.
  ///
  /// In en, this message translates to:
  /// **'The profiles table does not support listing saved people.'**
  String get peopleRepoProfilesListUnsupported;

  /// No description provided for @peopleRepoProfilesDetailUnsupported.
  ///
  /// In en, this message translates to:
  /// **'The profiles table does not support loading this saved person.'**
  String get peopleRepoProfilesDetailUnsupported;

  /// No description provided for @peopleRepoProfilesCreateUnsupported.
  ///
  /// In en, this message translates to:
  /// **'The profiles table does not support creating separate saved people.'**
  String get peopleRepoProfilesCreateUnsupported;

  /// No description provided for @peopleRepoTableNotFound.
  ///
  /// In en, this message translates to:
  /// **'No valid table for people records was found. Tried: {candidates}'**
  String peopleRepoTableNotFound(Object candidates);

  /// No description provided for @peopleRepoTableValidationFailed.
  ///
  /// In en, this message translates to:
  /// **'The people table could not be validated.'**
  String get peopleRepoTableValidationFailed;

  /// No description provided for @forumActiveTransitFallback.
  ///
  /// In en, this message translates to:
  /// **'The sky is active'**
  String get forumActiveTransitFallback;

  /// No description provided for @transitSkyCollectiveFallback.
  ///
  /// In en, this message translates to:
  /// **'Something is moving in the collective.'**
  String get transitSkyCollectiveFallback;

  /// No description provided for @transitSkyTypeIngress.
  ///
  /// In en, this message translates to:
  /// **'Ingress'**
  String get transitSkyTypeIngress;

  /// No description provided for @transitSkyTypeFullMoon.
  ///
  /// In en, this message translates to:
  /// **'Full moon'**
  String get transitSkyTypeFullMoon;

  /// No description provided for @transitSkyTypeNewMoon.
  ///
  /// In en, this message translates to:
  /// **'New moon'**
  String get transitSkyTypeNewMoon;

  /// No description provided for @transitSkyTypeExactAspect.
  ///
  /// In en, this message translates to:
  /// **'Exact aspect'**
  String get transitSkyTypeExactAspect;

  /// No description provided for @transitSkyTypeEclipse.
  ///
  /// In en, this message translates to:
  /// **'Eclipse'**
  String get transitSkyTypeEclipse;

  /// No description provided for @transitSkyTypeRetroStart.
  ///
  /// In en, this message translates to:
  /// **'Retrograde starts'**
  String get transitSkyTypeRetroStart;

  /// No description provided for @transitSkyTypeRetroEnd.
  ///
  /// In en, this message translates to:
  /// **'Retrograde ends'**
  String get transitSkyTypeRetroEnd;

  /// No description provided for @transitSkyTimingNow.
  ///
  /// In en, this message translates to:
  /// **'Now'**
  String get transitSkyTimingNow;

  /// No description provided for @transitSkyTimingThisWeek.
  ///
  /// In en, this message translates to:
  /// **'This week'**
  String get transitSkyTimingThisWeek;

  /// No description provided for @transitMeaningRelationships.
  ///
  /// In en, this message translates to:
  /// **'Relationships'**
  String get transitMeaningRelationships;

  /// No description provided for @transitMeaningMoney.
  ///
  /// In en, this message translates to:
  /// **'Money'**
  String get transitMeaningMoney;

  /// No description provided for @transitMeaningVisibility.
  ///
  /// In en, this message translates to:
  /// **'Visibility'**
  String get transitMeaningVisibility;

  /// No description provided for @transitMeaningDecision.
  ///
  /// In en, this message translates to:
  /// **'Decision'**
  String get transitMeaningDecision;

  /// No description provided for @transitMeaningCloseness.
  ///
  /// In en, this message translates to:
  /// **'Closeness'**
  String get transitMeaningCloseness;

  /// No description provided for @transitMeaningBuilding.
  ///
  /// In en, this message translates to:
  /// **'Building'**
  String get transitMeaningBuilding;

  /// No description provided for @transitMeaningRelease.
  ///
  /// In en, this message translates to:
  /// **'Release'**
  String get transitMeaningRelease;

  /// No description provided for @transitMeaningTension.
  ///
  /// In en, this message translates to:
  /// **'Tension'**
  String get transitMeaningTension;

  /// No description provided for @transitMeaningClarifying.
  ///
  /// In en, this message translates to:
  /// **'Clarifying'**
  String get transitMeaningClarifying;

  /// No description provided for @transitMeaningTransformation.
  ///
  /// In en, this message translates to:
  /// **'Transformation'**
  String get transitMeaningTransformation;

  /// No description provided for @profileDetailFallbackEyebrow.
  ///
  /// In en, this message translates to:
  /// **'Deep reading'**
  String get profileDetailFallbackEyebrow;

  /// No description provided for @profileDetailFallbackTitle.
  ///
  /// In en, this message translates to:
  /// **'Detail is being prepared for this card'**
  String get profileDetailFallbackTitle;

  /// No description provided for @profileDetailFallbackIntro.
  ///
  /// In en, this message translates to:
  /// **'The main narrative flow came back empty for now.'**
  String get profileDetailFallbackIntro;

  /// No description provided for @profileDetailFallbackBody.
  ///
  /// In en, this message translates to:
  /// **'The meaning of this card will still open here; right now the content stream is still on the way.'**
  String get profileDetailFallbackBody;

  /// No description provided for @bondSelfName.
  ///
  /// In en, this message translates to:
  /// **'Me'**
  String get bondSelfName;

  /// No description provided for @bondPageSelectPerson.
  ///
  /// In en, this message translates to:
  /// **'Select person'**
  String get bondPageSelectPerson;

  /// No description provided for @bondPageLensFallback.
  ///
  /// In en, this message translates to:
  /// **'bond lens'**
  String get bondPageLensFallback;

  /// No description provided for @bondPageHeroTitle.
  ///
  /// In en, this message translates to:
  /// **'Open the dynamic between two people here'**
  String get bondPageHeroTitle;

  /// No description provided for @bondPageHeroBody.
  ///
  /// In en, this message translates to:
  /// **'Pick your own profile and one saved person, then read the main rhythm and tension line between you in the same flow.'**
  String get bondPageHeroBody;

  /// No description provided for @bondPageLensLabel.
  ///
  /// In en, this message translates to:
  /// **'Lens'**
  String get bondPageLensLabel;

  /// No description provided for @bondPageBirthDataMissingTitle.
  ///
  /// In en, this message translates to:
  /// **'Birth data is required for Bond'**
  String get bondPageBirthDataMissingTitle;

  /// No description provided for @bondPageBirthDataMissingBody.
  ///
  /// In en, this message translates to:
  /// **'When you complete your own birth date and location, this match opens more accurately.'**
  String get bondPageBirthDataMissingBody;

  /// No description provided for @bondPagePreparing.
  ///
  /// In en, this message translates to:
  /// **'Preparing...'**
  String get bondPagePreparing;

  /// No description provided for @bondPageOpenResult.
  ///
  /// In en, this message translates to:
  /// **'Open Bond result'**
  String get bondPageOpenResult;

  /// No description provided for @bondPageAnalyzeFailed.
  ///
  /// In en, this message translates to:
  /// **'Bond analysis could not be loaded: {error}'**
  String bondPageAnalyzeFailed(Object error);

  /// No description provided for @bondPickerLabel.
  ///
  /// In en, this message translates to:
  /// **'People selection'**
  String get bondPickerLabel;

  /// No description provided for @bondPickerTitle.
  ///
  /// In en, this message translates to:
  /// **'Choose the second person for Bond'**
  String get bondPickerTitle;

  /// No description provided for @bondPickerAddPerson.
  ///
  /// In en, this message translates to:
  /// **'Add new person'**
  String get bondPickerAddPerson;

  /// No description provided for @bondPickerOwnProfile.
  ///
  /// In en, this message translates to:
  /// **'Your own profile'**
  String get bondPickerOwnProfile;

  /// No description provided for @bondPickerMe.
  ///
  /// In en, this message translates to:
  /// **'You'**
  String get bondPickerMe;

  /// No description provided for @bondPickerLoadFailed.
  ///
  /// In en, this message translates to:
  /// **'People could not be loaded: {error}'**
  String bondPickerLoadFailed(Object error);

  /// No description provided for @bondPairEyebrow.
  ///
  /// In en, this message translates to:
  /// **'Selection'**
  String get bondPairEyebrow;

  /// No description provided for @bondPairTitle.
  ///
  /// In en, this message translates to:
  /// **'Compare two people'**
  String get bondPairTitle;

  /// No description provided for @bondPairBody.
  ///
  /// In en, this message translates to:
  /// **'Pick two profiles, then see the main rhythm of their bond in the same flow.'**
  String get bondPairBody;

  /// No description provided for @storyStudioTopLabel.
  ///
  /// In en, this message translates to:
  /// **'Story Studio'**
  String get storyStudioTopLabel;

  /// No description provided for @storyStudioTopCenter.
  ///
  /// In en, this message translates to:
  /// **'imprint deck'**
  String get storyStudioTopCenter;

  /// No description provided for @storyStudioLoadingProfile.
  ///
  /// In en, this message translates to:
  /// **'Profile is loading...'**
  String get storyStudioLoadingProfile;

  /// No description provided for @storyStudioBirthDataRequired.
  ///
  /// In en, this message translates to:
  /// **'Story Studio needs birth date, time, and location before it can open.'**
  String get storyStudioBirthDataRequired;

  /// No description provided for @storyStudioIdentityTitle.
  ///
  /// In en, this message translates to:
  /// **'Identity cards'**
  String get storyStudioIdentityTitle;

  /// No description provided for @storyStudioIdentityBody.
  ///
  /// In en, this message translates to:
  /// **'Open the dominant placements, inner drive, and shadow line in your chart one card at a time.'**
  String get storyStudioIdentityBody;

  /// No description provided for @storyStudioIdentityTab.
  ///
  /// In en, this message translates to:
  /// **'Identity'**
  String get storyStudioIdentityTab;

  /// No description provided for @storyStudioMomentTitle.
  ///
  /// In en, this message translates to:
  /// **'Live sources'**
  String get storyStudioMomentTitle;

  /// No description provided for @storyStudioMomentBody.
  ///
  /// In en, this message translates to:
  /// **'Return to the surfaces working right now and open the active flows from there.'**
  String get storyStudioMomentBody;

  /// No description provided for @storyStudioMomentTab.
  ///
  /// In en, this message translates to:
  /// **'Moment'**
  String get storyStudioMomentTab;

  /// No description provided for @storyStudioCardsLoadFailed.
  ///
  /// In en, this message translates to:
  /// **'Cards could not be loaded'**
  String get storyStudioCardsLoadFailed;

  /// No description provided for @storyStudioCardsPreparing.
  ///
  /// In en, this message translates to:
  /// **'Cards are being prepared'**
  String get storyStudioCardsPreparing;

  /// No description provided for @storyStudioCardsPreparingBody.
  ///
  /// In en, this message translates to:
  /// **'The personality imprint layer is coming in from the backend.'**
  String get storyStudioCardsPreparingBody;

  /// No description provided for @storyStudioCardsNotFound.
  ///
  /// In en, this message translates to:
  /// **'No cards found'**
  String get storyStudioCardsNotFound;

  /// No description provided for @storyStudioCardsNotFoundBody.
  ///
  /// In en, this message translates to:
  /// **'No Story Studio cards could be produced from this profile yet.'**
  String get storyStudioCardsNotFoundBody;

  /// No description provided for @storyStudioMomentPanelTitle.
  ///
  /// In en, this message translates to:
  /// **'Live studio sources'**
  String get storyStudioMomentPanelTitle;

  /// No description provided for @storyStudioMomentPanelBody.
  ///
  /// In en, this message translates to:
  /// **'This section does not create a new card; it sends you back to the active Home and Bond surfaces.'**
  String get storyStudioMomentPanelBody;

  /// No description provided for @storyStudioReturnToSources.
  ///
  /// In en, this message translates to:
  /// **'Return to sources'**
  String get storyStudioReturnToSources;

  /// No description provided for @storyStudioTraitLabel.
  ///
  /// In en, this message translates to:
  /// **'Standout line'**
  String get storyStudioTraitLabel;

  /// No description provided for @storyStudioInnerDriveLabel.
  ///
  /// In en, this message translates to:
  /// **'Inner drive'**
  String get storyStudioInnerDriveLabel;

  /// No description provided for @storyStudioWhenTooMuchLabel.
  ///
  /// In en, this message translates to:
  /// **'When overloaded'**
  String get storyStudioWhenTooMuchLabel;

  /// No description provided for @storyStudioRefreshing.
  ///
  /// In en, this message translates to:
  /// **'Refreshing...'**
  String get storyStudioRefreshing;

  /// No description provided for @storyStudioKindAspect.
  ///
  /// In en, this message translates to:
  /// **'Aspect'**
  String get storyStudioKindAspect;

  /// No description provided for @storyStudioKindHousePlacement.
  ///
  /// In en, this message translates to:
  /// **'House placement'**
  String get storyStudioKindHousePlacement;

  /// No description provided for @storyStudioKindSignPlacement.
  ///
  /// In en, this message translates to:
  /// **'Sign placement'**
  String get storyStudioKindSignPlacement;

  /// No description provided for @storyStudioKindLayer.
  ///
  /// In en, this message translates to:
  /// **'Layer'**
  String get storyStudioKindLayer;

  /// No description provided for @storyStudioLoadFailed.
  ///
  /// In en, this message translates to:
  /// **'Story Studio could not be loaded: {error}'**
  String storyStudioLoadFailed(Object error);

  /// No description provided for @relationshipPreviewLabel.
  ///
  /// In en, this message translates to:
  /// **'Relationship preview'**
  String get relationshipPreviewLabel;

  /// No description provided for @relationshipPreviewBirthDataRequiredTitle.
  ///
  /// In en, this message translates to:
  /// **'Birth data is required for relationship preview'**
  String get relationshipPreviewBirthDataRequiredTitle;

  /// No description provided for @relationshipPreviewBirthDataRequiredBody.
  ///
  /// In en, this message translates to:
  /// **'When birth date, time, and location are complete, the relationship line opens here.'**
  String get relationshipPreviewBirthDataRequiredBody;

  /// No description provided for @relationshipPreviewLoadFailedTitle.
  ///
  /// In en, this message translates to:
  /// **'Relationship flow unavailable'**
  String get relationshipPreviewLoadFailedTitle;

  /// No description provided for @relationshipPreviewMainThemeLabel.
  ///
  /// In en, this message translates to:
  /// **'Main theme'**
  String get relationshipPreviewMainThemeLabel;

  /// No description provided for @relationshipPreviewDriversLabel.
  ///
  /// In en, this message translates to:
  /// **'What is shaping today'**
  String get relationshipPreviewDriversLabel;

  /// No description provided for @relationshipPreviewBackdropLabel.
  ///
  /// In en, this message translates to:
  /// **'Backdrop'**
  String get relationshipPreviewBackdropLabel;

  /// No description provided for @relationshipPreviewUpperMeaningLabel.
  ///
  /// In en, this message translates to:
  /// **'Deeper meaning'**
  String get relationshipPreviewUpperMeaningLabel;

  /// No description provided for @relationshipPreviewSupportingThemeLabel.
  ///
  /// In en, this message translates to:
  /// **'Supporting theme'**
  String get relationshipPreviewSupportingThemeLabel;

  /// No description provided for @relationshipPreviewWhyImportant.
  ///
  /// In en, this message translates to:
  /// **'Why this matters'**
  String get relationshipPreviewWhyImportant;

  /// No description provided for @relationshipPreviewFallbackNotice.
  ///
  /// In en, this message translates to:
  /// **'The relationship lens was slow, so this opened with the general reading instead.'**
  String get relationshipPreviewFallbackNotice;

  /// No description provided for @relationshipPreviewTimeout.
  ///
  /// In en, this message translates to:
  /// **'The relationship reading took too long to return. Try again in a moment.'**
  String get relationshipPreviewTimeout;

  /// No description provided for @relationshipPreviewInvalidProfile.
  ///
  /// In en, this message translates to:
  /// **'The submitted profile data is not enough for the relationship flow.'**
  String get relationshipPreviewInvalidProfile;

  /// No description provided for @relationshipPreviewServerError.
  ///
  /// In en, this message translates to:
  /// **'The relationship flow could not be loaded from the server right now.'**
  String get relationshipPreviewServerError;

  /// No description provided for @relationshipPreviewFetchFailed.
  ///
  /// In en, this message translates to:
  /// **'The relationship flow could not be loaded.'**
  String get relationshipPreviewFetchFailed;

  /// No description provided for @relationshipPreviewStageStarted.
  ///
  /// In en, this message translates to:
  /// **'Started'**
  String get relationshipPreviewStageStarted;

  /// No description provided for @relationshipPreviewStageIntensifying.
  ///
  /// In en, this message translates to:
  /// **'Intensifying'**
  String get relationshipPreviewStageIntensifying;

  /// No description provided for @relationshipPreviewStagePeak.
  ///
  /// In en, this message translates to:
  /// **'Peak'**
  String get relationshipPreviewStagePeak;

  /// No description provided for @relationshipPreviewStageResolving.
  ///
  /// In en, this message translates to:
  /// **'Resolving'**
  String get relationshipPreviewStageResolving;

  /// No description provided for @relationshipPreviewPeriodToToday.
  ///
  /// In en, this message translates to:
  /// **'From the period into today'**
  String get relationshipPreviewPeriodToToday;

  /// No description provided for @relationshipPreviewDefaultDriversFallback.
  ///
  /// In en, this message translates to:
  /// **'There is movement on the relationship side today, but a single theme has not fully separated yet.'**
  String get relationshipPreviewDefaultDriversFallback;

  /// No description provided for @relationshipPreviewDefaultBackdropFallback.
  ///
  /// In en, this message translates to:
  /// **'A longer period is still working underneath, and its relationship-side result will become clearer with a bit more time.'**
  String get relationshipPreviewDefaultBackdropFallback;

  /// No description provided for @friendProfileTitle.
  ///
  /// In en, this message translates to:
  /// **'Person profile'**
  String get friendProfileTitle;

  /// No description provided for @friendProfileNotFound.
  ///
  /// In en, this message translates to:
  /// **'Person not found.'**
  String get friendProfileNotFound;

  /// No description provided for @friendProfileEditTooltip.
  ///
  /// In en, this message translates to:
  /// **'Edit person'**
  String get friendProfileEditTooltip;

  /// No description provided for @friendProfileLoadFailed.
  ///
  /// In en, this message translates to:
  /// **'Person could not be loaded: {error}'**
  String friendProfileLoadFailed(Object error);

  /// No description provided for @profileDetailInfluences.
  ///
  /// In en, this message translates to:
  /// **'Influences'**
  String get profileDetailInfluences;

  /// No description provided for @profileDetailAllCards.
  ///
  /// In en, this message translates to:
  /// **'All cards'**
  String get profileDetailAllCards;

  /// No description provided for @profileDetailSignatureCardsTitle.
  ///
  /// In en, this message translates to:
  /// **'Signature cards'**
  String get profileDetailSignatureCardsTitle;

  /// No description provided for @profileDetailDefaultEyebrow.
  ///
  /// In en, this message translates to:
  /// **'Detail'**
  String get profileDetailDefaultEyebrow;

  /// No description provided for @profileDetailDefaultTitle.
  ///
  /// In en, this message translates to:
  /// **'Detail flow'**
  String get profileDetailDefaultTitle;

  /// No description provided for @profileDetailWhyHere.
  ///
  /// In en, this message translates to:
  /// **'Why here'**
  String get profileDetailWhyHere;

  /// No description provided for @profileDetailNextLabel.
  ///
  /// In en, this message translates to:
  /// **'Next: {title}'**
  String profileDetailNextLabel(Object title);

  /// No description provided for @profileDetailContinuationTitle.
  ///
  /// In en, this message translates to:
  /// **'{title} · Continue'**
  String profileDetailContinuationTitle(Object title);

  /// No description provided for @profileDetailSideA.
  ///
  /// In en, this message translates to:
  /// **'One side'**
  String get profileDetailSideA;

  /// No description provided for @profileDetailSideB.
  ///
  /// In en, this message translates to:
  /// **'The other side'**
  String get profileDetailSideB;

  /// No description provided for @profileDetailContinueFlow.
  ///
  /// In en, this message translates to:
  /// **'Continue the flow'**
  String get profileDetailContinueFlow;

  /// No description provided for @profileDetailContinueFromHere.
  ///
  /// In en, this message translates to:
  /// **'Continue from here'**
  String get profileDetailContinueFromHere;

  /// No description provided for @profileDetailContinuationFooter.
  ///
  /// In en, this message translates to:
  /// **'Continues {page}/{total}'**
  String profileDetailContinuationFooter(int page, int total);

  /// No description provided for @profileDetailFlowEnds.
  ///
  /// In en, this message translates to:
  /// **'The flow ends here'**
  String get profileDetailFlowEnds;

  /// No description provided for @periodFallbackEffectTitle.
  ///
  /// In en, this message translates to:
  /// **'Period effect'**
  String get periodFallbackEffectTitle;

  /// No description provided for @periodIntentSummaryGeneric.
  ///
  /// In en, this message translates to:
  /// **'There are windows to track for {title} in this period.'**
  String periodIntentSummaryGeneric(Object title);

  /// No description provided for @periodIntentTopDays.
  ///
  /// In en, this message translates to:
  /// **'Standout days for {title}: {dates}.'**
  String periodIntentTopDays(Object title, Object dates);

  /// No description provided for @periodIntentScores.
  ///
  /// In en, this message translates to:
  /// **'Scores: {ratings}'**
  String periodIntentScores(Object ratings);

  /// No description provided for @periodIntentBeautyCare.
  ///
  /// In en, this message translates to:
  /// **'Care and body'**
  String get periodIntentBeautyCare;

  /// No description provided for @periodIntentBusiness.
  ///
  /// In en, this message translates to:
  /// **'Work and output'**
  String get periodIntentBusiness;

  /// No description provided for @periodIntentMoney.
  ///
  /// In en, this message translates to:
  /// **'Money and resources'**
  String get periodIntentMoney;

  /// No description provided for @periodIntentRelationship.
  ///
  /// In en, this message translates to:
  /// **'Relationship and harmony'**
  String get periodIntentRelationship;

  /// No description provided for @periodIntentLabel.
  ///
  /// In en, this message translates to:
  /// **'Intent {index}'**
  String periodIntentLabel(int index);

  /// No description provided for @periodDefaultTitle.
  ///
  /// In en, this message translates to:
  /// **'Period'**
  String get periodDefaultTitle;

  /// No description provided for @periodMainFlowFallback.
  ///
  /// In en, this message translates to:
  /// **'The main flow of this period.'**
  String get periodMainFlowFallback;

  /// No description provided for @periodMainThemeFallback.
  ///
  /// In en, this message translates to:
  /// **'The main theme of this period.'**
  String get periodMainThemeFallback;

  /// No description provided for @periodHighlightedThemeFallback.
  ///
  /// In en, this message translates to:
  /// **'The standout theme in this period.'**
  String get periodHighlightedThemeFallback;

  /// No description provided for @periodThemeCollectFallback.
  ///
  /// In en, this message translates to:
  /// **'The standout theme of this period gathers here.'**
  String get periodThemeCollectFallback;

  /// No description provided for @periodEssenceTitle.
  ///
  /// In en, this message translates to:
  /// **'Essence of this period'**
  String get periodEssenceTitle;

  /// No description provided for @periodSummaryUnavailable.
  ///
  /// In en, this message translates to:
  /// **'No summary for this period is available.'**
  String get periodSummaryUnavailable;

  /// No description provided for @periodTimeLabel.
  ///
  /// In en, this message translates to:
  /// **'Timing'**
  String get periodTimeLabel;

  /// No description provided for @periodGuidancePrefix.
  ///
  /// In en, this message translates to:
  /// **'Small practice:'**
  String get periodGuidancePrefix;

  /// No description provided for @periodDifficultyPrefix.
  ///
  /// In en, this message translates to:
  /// **'What tends to make this harder is:'**
  String get periodDifficultyPrefix;

  /// No description provided for @periodHowItWorksTitle.
  ///
  /// In en, this message translates to:
  /// **'How it works'**
  String get periodHowItWorksTitle;

  /// No description provided for @periodAsksTitle.
  ///
  /// In en, this message translates to:
  /// **'What it asks of you'**
  String get periodAsksTitle;

  /// No description provided for @periodWatchTitle.
  ///
  /// In en, this message translates to:
  /// **'What to watch'**
  String get periodWatchTitle;

  /// No description provided for @periodBuildsTitle.
  ///
  /// In en, this message translates to:
  /// **'What it develops in you'**
  String get periodBuildsTitle;

  /// No description provided for @periodEffectLabel.
  ///
  /// In en, this message translates to:
  /// **'Effect'**
  String get periodEffectLabel;

  /// No description provided for @periodTechnicalNoteLabel.
  ///
  /// In en, this message translates to:
  /// **'Technical note'**
  String get periodTechnicalNoteLabel;

  /// No description provided for @periodCoreMainThemeTitle.
  ///
  /// In en, this message translates to:
  /// **'The main theme of this period'**
  String get periodCoreMainThemeTitle;

  /// No description provided for @periodCoreSummaryUnavailable.
  ///
  /// In en, this message translates to:
  /// **'No period summary was available for this period.'**
  String get periodCoreSummaryUnavailable;

  /// No description provided for @profileExperimentPreviewLabel.
  ///
  /// In en, this message translates to:
  /// **'Preview'**
  String get profileExperimentPreviewLabel;

  /// No description provided for @profileExperimentCenterText.
  ///
  /// In en, this message translates to:
  /// **'Nocturne Identity'**
  String get profileExperimentCenterText;

  /// No description provided for @profileExperimentMenuTooltip.
  ///
  /// In en, this message translates to:
  /// **'Theme and experiment settings'**
  String get profileExperimentMenuTooltip;

  /// No description provided for @profileExperimentHeroFallback.
  ///
  /// In en, this message translates to:
  /// **'The first trace of the chart gathers here.'**
  String get profileExperimentHeroFallback;

  /// No description provided for @profileExperimentSignatureFallback.
  ///
  /// In en, this message translates to:
  /// **'Identity trace'**
  String get profileExperimentSignatureFallback;

  /// No description provided for @profileExperimentNatalPanelBody.
  ///
  /// In en, this message translates to:
  /// **'This preview currently focuses on a spotlight hero that opens identity as a full portrait surface. Lower chapter layers will follow in a later patch.'**
  String get profileExperimentNatalPanelBody;

  /// No description provided for @profileExperimentTimingPanelBody.
  ///
  /// In en, this message translates to:
  /// **'Timing mode behaves like a focus switch here for now. The lower period composition will arrive in a later patch.'**
  String get profileExperimentTimingPanelBody;

  /// No description provided for @profileExperimentMenuTitle.
  ///
  /// In en, this message translates to:
  /// **'Nocturne experiment'**
  String get profileExperimentMenuTitle;

  /// No description provided for @profileExperimentMenuBody.
  ///
  /// In en, this message translates to:
  /// **'Patch 1 only tests the upper identity composition.'**
  String get profileExperimentMenuBody;

  /// No description provided for @profileExperimentSeeProfile.
  ///
  /// In en, this message translates to:
  /// **'See profile'**
  String get profileExperimentSeeProfile;

  /// No description provided for @profileExperimentHeroLineFallback.
  ///
  /// In en, this message translates to:
  /// **'Your identity is gathered into a new focal surface on this screen.'**
  String get profileExperimentHeroLineFallback;

  /// No description provided for @profileExperimentAuraLabel.
  ///
  /// In en, this message translates to:
  /// **'Aura'**
  String get profileExperimentAuraLabel;

  /// No description provided for @profileExperimentRulerLabel.
  ///
  /// In en, this message translates to:
  /// **'Ruler'**
  String get profileExperimentRulerLabel;

  /// No description provided for @profileExperimentWaiting.
  ///
  /// In en, this message translates to:
  /// **'Waiting'**
  String get profileExperimentWaiting;

  /// No description provided for @profileExperimentRulerBodyFallback.
  ///
  /// In en, this message translates to:
  /// **'The ruler of the 1st house is being read.'**
  String get profileExperimentRulerBodyFallback;

  /// No description provided for @profileExperimentRisingTrace.
  ///
  /// In en, this message translates to:
  /// **'Rising trace'**
  String get profileExperimentRisingTrace;

  /// No description provided for @profileExperimentSignatureLabel.
  ///
  /// In en, this message translates to:
  /// **'Signature'**
  String get profileExperimentSignatureLabel;

  /// No description provided for @profileExperimentSpotlightCards.
  ///
  /// In en, this message translates to:
  /// **'Spotlight cards'**
  String get profileExperimentSpotlightCards;

  /// No description provided for @profileExperimentSwipe.
  ///
  /// In en, this message translates to:
  /// **'Swipe'**
  String get profileExperimentSwipe;

  /// No description provided for @profileExperimentFocusTitle.
  ///
  /// In en, this message translates to:
  /// **'Reading focus'**
  String get profileExperimentFocusTitle;

  /// No description provided for @profileExperimentNatalFocus.
  ///
  /// In en, this message translates to:
  /// **'Your structure'**
  String get profileExperimentNatalFocus;

  /// No description provided for @profileExperimentTimingFocus.
  ///
  /// In en, this message translates to:
  /// **'Your current period'**
  String get profileExperimentTimingFocus;

  /// No description provided for @profileExperimentUnnamedProfile.
  ///
  /// In en, this message translates to:
  /// **'Unnamed profile'**
  String get profileExperimentUnnamedProfile;

  /// No description provided for @profileExperimentFireDominant.
  ///
  /// In en, this message translates to:
  /// **'Fire dominant'**
  String get profileExperimentFireDominant;

  /// No description provided for @profileExperimentWaterDominant.
  ///
  /// In en, this message translates to:
  /// **'Water dominant'**
  String get profileExperimentWaterDominant;

  /// No description provided for @profileExperimentAirDominant.
  ///
  /// In en, this message translates to:
  /// **'Air dominant'**
  String get profileExperimentAirDominant;

  /// No description provided for @profileExperimentEarthDominant.
  ///
  /// In en, this message translates to:
  /// **'Earth dominant'**
  String get profileExperimentEarthDominant;

  /// No description provided for @errorTimeout.
  ///
  /// In en, this message translates to:
  /// **'The server is a bit slow right now, try again in a moment.'**
  String get errorTimeout;

  /// No description provided for @errorNoConnection.
  ///
  /// In en, this message translates to:
  /// **'Could not connect. Check your internet connection.'**
  String get errorNoConnection;

  /// No description provided for @errorGeneric.
  ///
  /// In en, this message translates to:
  /// **'Something went wrong. Please try again.'**
  String get errorGeneric;
}

class _AppLocalizationsDelegate extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  Future<AppLocalizations> load(Locale locale) {
    return SynchronousFuture<AppLocalizations>(lookupAppLocalizations(locale));
  }

  @override
  bool isSupported(Locale locale) => <String>['en', 'tr'].contains(locale.languageCode);

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}

AppLocalizations lookupAppLocalizations(Locale locale) {


  // Lookup logic when only language code is specified.
  switch (locale.languageCode) {
    case 'en': return AppLocalizationsEn();
    case 'tr': return AppLocalizationsTr();
  }

  throw FlutterError(
    'AppLocalizations.delegate failed to load unsupported locale "$locale". This is likely '
    'an issue with the localizations generation tool. Please file an issue '
    'on GitHub with a reproducible sample app and the gen-l10n configuration '
    'that was used.'
  );
}
