# Tasks

- [x] Clean up environment
    - [x] Terminate all background `build_runner` processes
    - [x] Clean `build_runner` cache
- [ ] Verify configuration
    - [x] Check `pubspec.yaml`
    - [x] Check `build.yaml` (if exists)
- [/] Regenerate code
    - [/] Run `flutter pub run build_runner build --delete-conflicting-outputs`
- [ ] Verify fix
    - [ ] Check if analyzer errors are gone
    - [ ] Verify `note.freezed.dart` matches `note.dart`
