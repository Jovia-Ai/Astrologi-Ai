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
