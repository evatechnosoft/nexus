# Walkthrough - Fixing Model Serialization

I have fixed the issue where the `Note` and `Task` models were failing to serialize/deserialize correctly with the local database due to naming mismatches (camelCase vs snake_case).

## Changes Made

### Configuration
Created [build.yaml](file:///c:/projects/github/EvAnotes/mobile/build.yaml) to globally configure `json_serializable` to use `snake_case` for field renaming. This ensures all models align with the database schema without needing individual annotations on every class.

### Models
Restored and cleaned up [note.dart](file:///c:/projects/github/EvAnotes/mobile/lib/models/note.dart) and [task.dart](file:///c:/projects/github/EvAnotes/mobile/lib/models/task.dart). I ensured the `freezed_annotation` imports and `part` statements are correct.

## Verification Results

### Code Generation
Ran `flutter pub run build_runner build --delete-conflicting-outputs` successfully.

### Generated JSON Keys
Verified that `note.g.dart` and `task.g.dart` now use the correct keys:
- `user_id`
- `created_at`
- `updated_at`

Example from `note.g.dart`:
```dart
_Note _$NoteFromJson(Map<String, dynamic> json) => _Note(
      id: json['id'] as String,
      title: json['title'] as String,
      content: json['content'] as String?,
      category: json['category'] as String?,
      userId: json['user_id'] as String,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );
```
