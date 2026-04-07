# Tasks

- [ ] Diagnose and fix `google_auth.dart` <!-- id: 0 -->
    - [x] Research `google_sign_in` 7.x API changes <!-- id: 1 -->
    - [x] Research Riverpod 3.x migration (`StateNotifier` to `Notifier`) <!-- id: 2 -->
    - [x] Update `googleSignInProvider` to use `GoogleSignIn.standard` <!-- id: 3 -->
    - [x] Migrate `GoogleAuthNotifier` to `AsyncNotifier` <!-- id: 4 -->
- [ ] Verify fix <!-- id: 5 -->
    - [ ] Run `flutter analyze` to confirm no errors in `google_auth.dart` <!-- id: 6 -->
- [ ] Clean up <!-- id: 7 -->
    - [ ] Remove `mobile/tmp_check.dart` <!-- id: 8 -->
