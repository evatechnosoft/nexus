# Fix Critical Syntax Errors and Restore Application Functionality

The `public/index.html` file contains multiple critical syntax errors, likely due to previous truncated edits. These errors prevent the JavaScript from executing, which makes both the login and "Offline" modes appear broken.

## User Review Required

> [!IMPORTANT]
> The `index.html` file is a large single-file SPA (over 1000 lines). I will be making focused edits to repair corrupted sections. If there are specific features that were recently added and might be affected, please let me know.

## Proposed Changes

### Frontend Fixes

#### [MODIFY] [index.html](file:///c:/projects/SportApp/public/index.html)
- **Fix Measurement Button**: Repair the broken HTML tag at line 526-527.
- **Fix JavaScript Corruption**: 
    - Repair the `resetAll` function (around line 586).
    - Fix the `onLoginSuccess` function and `const await` error (line 772).
    - Fix the `renderLive` function (line 835).
    - Repair various other truncated lines (851, 869, 889, etc.).
- **Ensure Offline Mode**: Verify `skipLogin()` logic is intact.

### Backend Enhancements

- **Default User (Optional)**: Since the `users` table is empty, I can add a registration guide or a default "Dean" user for testing.

## Open Questions

- Did the `index.html` file recently get corrupted during an edit? 
- Would you like me to move the JavaScript to a separate `app.js` file for better maintainability?

## Verification Plan

### Automated Tests
- Use the browser tool to navigate to `http://localhost:3002/`.
- Verify the login overlay appears.
- Click "Offline Kullan" and verify the main dashboard loads without JS errors.

### Manual Verification
- Test the measurement saving and workout logging in "Offline" mode.
