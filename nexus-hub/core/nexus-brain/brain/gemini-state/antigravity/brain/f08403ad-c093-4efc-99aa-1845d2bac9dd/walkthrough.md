# Walkthrough - BuildContext async gaps fix

I fixed the "Don't use 'BuildContext's across async gaps" lint warning in `SplashScreen`.

## Changes Made

### Component: Splash Screen

#### [MODIFY] [splash_screen.dart](file:///c:/projects/github/EvATasks/mobile/lib/features/splash/splash_screen.dart)

Added a `mounted` check immediately after `await SharedPreferences.getInstance()` to ensure the `context` is still valid before being used for navigation.

render_diffs(file:///c:/projects/github/EvATasks/mobile/lib/features/splash/splash_screen.dart)

### Component: Two Factor Authentication Screen

#### [MODIFY] [two_fa_screen.dart](file:///c:/projects/github/EvATasks/mobile/lib/features/auth/two_fa_screen.dart)

Added a `mounted` check in the `catch` block of `_handleVerify` to ensure `setState` is only called if the widget is still in the tree.

render_diffs(file:///c:/projects/github/EvATasks/mobile/lib/features/auth/two_fa_screen.dart)

## Verification Results

### Automated Tests
- The lint warning is resolved.

### Manual Verification
- Navigating from the splash screen should work correctly as long as the widget is still mounted after the asynchronous initialization of `SharedPreferences`.
