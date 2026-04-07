# Fix GoogleSignIn and Riverpod 3.x Compatibility

The project is using `google_sign_in: ^7.2.0` and `riverpod: ^3.2.1`, which introduced breaking changes in their respective APIs.

## Proposed Changes

### Configuration

#### [MODIFY] [google_auth.dart](file:///c:/projects/EvAnotes/mobile/lib/config/google_auth.dart)
- Update `googleSignInProvider` to use `GoogleSignIn.standard()` constructor.
- Migrate `GoogleAuthNotifier` from `StateNotifier` to `AsyncNotifier`.
- Update `googleAuthNotifierProvider` to use `AsyncNotifierProvider`.

## Verification Plan

### Automated Tests
- Run `flutter analyze mobile/lib/config/google_auth.dart` to ensure all compilation errors are resolved.

### Manual Verification
- If possible, verify the Google Sign-In flow in the app.
