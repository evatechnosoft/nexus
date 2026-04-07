# Fix Library Errors (Mobile)

The project currently has a mix of `StateNotifier` and `Notifier` patterns, missing providers, and incorrect imports. This plan will unify the architecture and fix all compilation errors.

## Proposed Changes

### Configuration & State
#### [MODIFY] [api_client.dart](file:///c:/projects/github/EvAnotes/mobile/lib/config/api_client.dart)
- Ensure `authTokenProvider` is correctly defined as a `NotifierProvider`.
- Ensure `apiClientProvider` is correctly defined.

#### [MODIFY] [providers.dart](file:///c:/projects/github/EvAnotes/mobile/lib/config/providers.dart)
- Convert `AuthStateNotifier` to `Notifier` (Riverpod 3.0+ path).
- Correct `tasksNotifierProvider` and `notesNotifierProvider` to use `NotifierProvider` to match the `TasksNotifier` and `NotesNotifier` classes.
- Standardize on `apiClientProvider` instead of `dioProvider`.
- Remove redundant/incorrect definitions of `localDatabaseProvider` and `syncServiceProvider` (they are in `sync_service.dart`).
- Define `taskRepositoryProvider` and `noteRepositoryProvider`.

#### [MODIFY] [tasks_notifier.dart](file:///c:/projects/github/EvAnotes/mobile/lib/state/tasks_notifier.dart)
- Watch `taskRepositoryProvider` correctly within the `build()` method.

#### [MODIFY] [notes_notifier.dart](file:///c:/projects/github/EvAnotes/mobile/lib/state/notes_notifier.dart)
- Watch `noteRepositoryProvider` correctly within the `build()` method.

### Models
- Verify `Task` and `Note` models are correctly imported.

## Verification Plan

### Automated Tests
- Run `flutter analyze` to ensure zero errors.
- Run `flutter test` (if applicable).
