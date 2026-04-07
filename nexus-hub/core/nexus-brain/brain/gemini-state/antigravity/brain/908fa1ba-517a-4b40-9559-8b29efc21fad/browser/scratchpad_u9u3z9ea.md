# Local App Testing Plan

## Current Tasks
- [x] Open `http://localhost:5007` and verify login/register section.
- [ ] Register a new user:
    - [x] Click 'Kayıt Ol' tab.
    - [x] Fill: `testuser`, `test@test.com`, `password123`.
    - [x] Submit and verify success.
- [x] Login with the registered user:
    - [x] Click 'Giriş Yap' tab.
    - [x] Login: `testuser`, `password123`.
    - [x] Verify success (Status Cards, User List visible).
- [x] Verify `currentUserName` in header shows `testuser`.
- [x] Add a new user via dashboard:
    - [x] Fill: `newbuddy`, `buddy@test.com`, `buddy123`.
    - [x] Verify `newbuddy` in user table.
- [x] Click 'Çıkış Yap' and verify logout.

## Notes
- URL: http://localhost:5007
