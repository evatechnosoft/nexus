# Implementation Plan - Resolving Model Constructor Conflict

The `Note` and `Task` models are currently failing to compile because they contain manual getter and `toJson` overrides that conflict with the `freezed` generated code. Specifically, there is a mismatch between the nullable fields in the constructor and the non-nullable manual overrides.

## Proposed Changes

### [Mobile Models]

#### [MODIFY] [note.dart](file:///c:/projects/github/EvAnotes/mobile/lib/models/note.dart)
- Remove all manual `@override` getters for `id`, `title`, `content`, `category`, `userId`, `createdAt`, and `updatedAt`.
- Remove manual `toJson()` implementation.
- Keep `const Note._();` if needed for future custom methods (currently empty but good practice for `freezed`).

#### [MODIFY] [task.dart](file:///c:/projects/github/EvAnotes/mobile/lib/models/task.dart)
- Remove all manual `@override` getters for `id`, `title`, `description`, `category`, `status`, `deadline`, `userId`, `createdAt`, and `updatedAt`.
- Remove manual `toJson()` implementation.
- Keep `isCompleted` getter as it is a legitimate custom extension.

## Verification Plan

### Automated Tests
- Run `flutter pub run build_runner build --delete-conflicting-outputs` to ensure code generation succeeds.
- Run existing unit tests:
  ```bash
  flutter test test/unit/models_test.dart
  ```

### Manual Verification
- Verify that the IDE no longer reports constructor incompatibility errors in `note.dart` and `task.dart`.
