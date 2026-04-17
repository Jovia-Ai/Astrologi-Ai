# SHOU App Store Release Checklist

## Store Metadata
- App name: `SHOU`
- Default subtitle: `Sana özel astroloji deneyimi`
- EN short description: `SHOU offers a deeper, more personal astrology experience across your natal chart, transits, and personal insight spaces.`
- TR short description: `SHOU, doğum haritan, transitlerin ve kişisel içgörü alanların arasında daha derin ve kişisel bir astroloji deneyimi sunar.`
- Support email: `info@shouastrology.com`
- Privacy Policy: [https://shouastrology.com/privacy](https://shouastrology.com/privacy)
- Terms of Use: [https://shouastrology.com/terms](https://shouastrology.com/terms)

## iOS Permissions
- `NSPhotoLibraryUsageDescription` is present for profile photo selection.
- `NSCameraUsageDescription` is intentionally omitted until camera capture exists.
- `NSPhotoLibraryAddUsageDescription` is intentionally omitted until the app saves images to the device.

## In-App Review Readiness
- `Restore Purchases` is visible from the app menu and paywall surface.
- `Delete Account` is visible from the app menu with an irreversible-action confirmation.
- Delete-account copy states that App Store subscriptions are not cancelled automatically.
- Privacy Policy, Terms of Use, and Support links open from inside the app.

## Release Checks
- Legal pages are live and reachable at the production URLs.
- Support email inbox is active and monitored.
- RevenueCat product IDs and public SDK keys are set for the release build.
- App Store subscription metadata and review notes are updated for the current build.
- iOS build shows `SHOU` as the visible app name.
