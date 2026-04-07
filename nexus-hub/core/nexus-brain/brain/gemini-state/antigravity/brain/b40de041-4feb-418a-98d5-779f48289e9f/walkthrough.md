# Backend Problems Fixed

I have addressed several backend issues that were likely causing errors in your "@problems" tab and preventing the system from working correctly.

## Summary of Changes

### 🔧 Database & Models
- **[AdminLog.js](file:///c:/projects/github/EvATasks/backend/src/models/AdminLog.js)**: Changed `JSONB` to `JSON`. SQLite (used in development) does not support `JSONB`, which was causing potential schema synchronization issues.
- **[User.js](file:///c:/projects/github/EvATasks/backend/src/models/User.js)**: Removed the restrictive `isEmail` validator from the `phone_email` field. This allows users to use phone numbers as identifiers, matching the field's intended purpose.

### 🚀 Migration Script
- **[migrate.js](file:///c:/projects/github/EvATasks/backend/scripts/migrate.js)**: Fixed the model imports. Previously, it was importing model factory functions instead of the initialized models from `src/models/index.js`, which prevented `sequelize.sync()` from recognizing the tables.

### 🔐 Authentication & Logic
- **[auth.js](file:///c:/projects/github/EvATasks/backend/src/routes/auth.js)**: Added `family_id` to the JWT token payload. This ensures that the frontend can access the user's family association directly from the token.
- **[tasks.js](file:///c:/projects/github/EvATasks/backend/src/routes/tasks.js)** & **[notes.js](file:///c:/projects/github/EvATasks/backend/src/routes/notes.js)**: Updated creation logic to automatically associate new tasks and notes with the user's `family_id` if they are part of a family.

## Note on Database Connection
The migration script is currently failing with a `getaddrinfo ENOTFOUND` error for the Supabase host. 
> [!IMPORTANT]
> To run the backend locally using SQLite, please comment out the `DATABASE_URL` line in your `backend/.env` file. The server is configured to fall back to SQLite automatically when no Postgres URL is provided.

## Verification Results
- **Syntax Check**: All modified files pass Node.js syntax checks.
- **Model Consistency**: Mobile app is confirmed to be using `field_rename: snake` in `build.yaml`, which is compatible with these backend changes.

---

### 📱 Android Gradle Fixed
- **[settings.gradle.kts](file:///c:/projects/github/EvATasks/mobile/android/settings.gradle.kts)**: Added the `com.google.gms.google-services` plugin definition.
- **[app/build.gradle.kts](file:///c:/projects/github/EvATasks/mobile/android/app/build.gradle.kts)**: 
    - Applied the Google Services plugin to enable Firebase features.
    - Updated `minSdk` to 21 to ensure compatibility with modern Firebase and Google Sign-In plugins.
- **Build Verification**: Successfully ran `./gradlew tasks` to confirm the configuration is valid.

---

### 🔒 Gradle Locking Issue Resolved
- **Diagnostic**: The error "The requested operation cannot be performed on a file with a user-mapped section open" was caused by background Gradle processes or IDE instances locking build files.
- **Fix**: 
    - Stopped all active Gradle daemons using `.\gradlew --stop`.
    - Performed a clean build state with `.\gradlew clean`.
- **Status**: The build system is now fully unlocked and configuration check passes without errors.
