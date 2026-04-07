# Fix StateProvider Undefined Error

The "StateProvider isn't defined" error was caused by missing or desynchronized dependencies in the local environment. Running `flutter pub get` has resolved the issue where the Dart analyzer could not find Riverpod types.

## Proposed Changes

### mobile

#### [MODIFY] [api_client.dart](file:///c:/projects/EvAnotes/mobile/lib/config/api_client.dart)
- Revert experimental `StateNotifierProvider`, `NotifierProvider`, and aliased imports.
- Restore the original `StateProvider` for `authTokenProvider`.
- Clean up redundant imports.

## Verification Plan

### Automated Tests
- Run `dart analyze lib/config/api_client.dart` to ensure no errors remain.
- Run `dart analyze lib/config/google_auth.dart` to ensure no regression in other related files.
