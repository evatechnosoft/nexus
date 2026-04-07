# Implementation Plan - Backend Problems Fix

Fix several backend issues identified in the models, migration scripts, and route logic to ensure compatibility and consistency.

## Proposed Changes

### Database Models

#### [MODIFY] [AdminLog.js](file:///c:/projects/github/EvATasks/backend/src/models/AdminLog.js)
- Change `DataTypes.JSONB` to `DataTypes.JSON` to ensure compatibility with SQLite (the current development database).

#### [MODIFY] [User.js](file:///c:/projects/github/EvATasks/backend/src/models/User.js)
- Remove `isEmail` validator from `phone_email` field to allow phone numbers as identifiers, as suggested by the field name.

---

### Migration & Setup

#### [MODIFY] [migrate.js](file:///c:/projects/github/EvATasks/backend/scripts/migrate.js)
- Replace direct imports of model files with the centralized `src/models/index.js` to ensure models are correctly initialized with `sequelize`.
- Improve error reporting during the migration process.

---

### API Routes

#### [MODIFY] [tasks.js](file:///c:/projects/github/EvATasks/backend/src/routes/tasks.js)
- Ensure `family_id` is assigned to new tasks if the user belongs to a family.

#### [MODIFY] [notes.js](file:///c:/projects/github/EvATasks/backend/src/routes/notes.js)
- Ensure `family_id` is assigned to new notes if the user belongs to a family.

---

### Android Gradle Configuration

#### [MODIFY] [settings.gradle.kts](file:///c:/projects/github/EvATasks/mobile/android/settings.gradle.kts)
- Add `com.google.gms.google-services` plugin definition to the `plugins` block.

#### [MODIFY] [build.gradle.kts](file:///c:/projects/github/EvATasks/mobile/android/app/build.gradle.kts)
- Apply `com.google.gms.google-services` plugin.
- Set `minSdk = 21` explicitly to ensure compatibility with Firebase and Google Sign-In plugins.

## Verification Plan

### Automated Tests
- Run `npm run migrate` inside the `backend` directory to verify the database syncing works correctly.
- Run `npm test` to ensure existing functionality remains intact.

### Manual Verification
- Verify the server starts successfully using `npm start` or `npm run dev`.
