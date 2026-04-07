# Implementation Plan - Fixing Build and Model Errors

The codebase currently has multiple compilation and analysis errors primarily caused by out-of-sync generated files for `freezed` models and incorrect Riverpod `Notifier` overrides. This plan addresses these issues and ensures the project can be built and tested successfully.

## User Review Required
> [!IMPORTANT]
> I will be regenerating all `freezed` and `json_serializable` files. This may change the structure of the generated code if the models were recently modified.
> I will also update `SyncService` to handle the new `List<ConnectivityResult>` return type from `connectivity_plus` ^7.0.0.

## Proposed Changes

### [Models]
- Ensure nullability consistency in `Note` and `Task` factories.
- Regenerate `.freezed.dart` and `.g.dart` files.

#### [MODIFY] [note.dart](file:///c:/projects/github/EvAnotes/mobile/lib/models/note.dart)
- Ensure fields like `userId`, `createdAt`, and `updatedAt` are consistently nullable or required to match the intended usage and generator output.

#### [MODIFY] [task.dart](file:///c:/projects/github/EvAnotes/mobile/lib/models/task.dart)
- Similar consistency check for `Task` fields.

---

### [State Management]
- Fix `Notifier` build methods and syntax errors.

#### [MODIFY] [notes_notifier.dart](file:///c:/projects/github/EvAnotes/mobile/lib/state/notes_notifier.dart)
- Fix the `build` method if it's incorrectly overriding. (Current view looks okay, but I'll double check for hidden `async` or type mismatches).
- Fix `rethrow` visibility if needed (though current view looked okay, analyzer might see it differently if types are broken).

#### [MODIFY] [tasks_notifier.dart](file:///c:/projects/github/EvAnotes/mobile/lib/state/tasks_notifier.dart)
- Same fixes as `notes_notifier.dart`.

---

### [Services]
- Update connectivity logic.

#### [MODIFY] [sync_service.dart](file:///c:/projects/github/EvAnotes/mobile/lib/services/sync_service.dart)
- Update check to correctly handle `List<ConnectivityResult>` (already partially done, but ensuring it's robust).

---

## Verification Plan

### Automated Tests
- **Regenerate Files**: `flutter pub run build_runner build --delete-conflicting-outputs`
- **Static Analysis**: `flutter analyze`
- **Unit/Widget Tests**: `flutter test`

### Manual Verification
- N/A
