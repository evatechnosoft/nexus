# Fix Freezed Model Generation Issue

The user is experiencing "Missing concrete implementations" errors in `Note` and `Task` models. This is caused by `freezed` and `json_serializable` generated files being out of sync with the source code, likely due to multiple conflicting `build_runner` processes running in the background.

## User Review Required

> [!IMPORTANT]
> I will need to terminate existing `dart` and `flutter` processes that are running `build_runner` to release file locks and ensure a clean build. This may interrupt any other active Flutter/Dart tasks you have running.

## Proposed Changes

### Build Environment Cleanup

1.  **Terminate Stale Processes**: Kill all background `dart.exe` and `flutter.exe` processes related to `build_runner`.
2.  **Clean Build Cache**: Run `flutter pub run build_runner clean` in the `mobile` directory.

### Code Regeneration

1.  **Run Build Runner**: Execute `flutter pub run build_runner build --delete-conflicting-outputs` to regenerate `note.freezed.dart`, `note.g.dart`, `task.freezed.dart`, and `task.g.dart`.

## Verification Plan

### Automated Tests
- Run existing model tests:
  ```powershell
  cd mobile
  flutter test test/unit/models_test.dart
  flutter test test/unit/task_model_test.dart
  ```

### Manual Verification
- Verify that the analyzer errors in `lib/models/note.dart` and `lib/models/task.dart` have disappeared.
- Inspect `lib/models/note.freezed.dart` to ensure `userId`, `createdAt`, and `updatedAt` are correctly marked as nullable/optional as defined in the source.
