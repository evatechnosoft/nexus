# Backend Problems Fix Implementation Plan

- [x] Find backend problems in the `@problems` tab
    - [x] Check `src` directory for obvious errors
    - [x] Examine models and controllers
    - [x] Look for syntax errors or missing imports
- [x] Fix identified issues
    - [x] Correct database type in `AdminLog.js` (JSONB -> JSON)
    - [x] Fix model imports in `migrate.js`
    - [x] Remove restrictive email validator in `User.js`
    - [x] Map `user_id` to `userId` etc. in mobile (if needed) or keep snake_case consistent.
- [x] Verify fix by running `npm run migrate` or `npm test`

- [x] Fix Android Gradle Issues
    - [x] Add Google Services plugin to `settings.gradle.kts`
    - [x] Add Google Services plugin to `app/build.gradle.kts`
    - [x] Set `minSdkVersion` to 21 for Firebase compatibility
    - [x] Verify Gradle configuration by running `gradlew tasks`

- [x] Fix Gradle Locking Issue
    - [x] Stop all Gradle daemons
    - [x] Clean Gradle cache if necessary
    - [x] Verify build works without locking errors
