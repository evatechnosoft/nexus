# End-to-End 2FA Flow Implementation

Implement a secure and seamless two-factor authentication flow starting from login through OTP verification.

## Proposed Changes

### [Backend] Authentication & 2FA Components
Modify the backend to support a multi-step login process when 2FA is enabled.

#### [MODIFY] [auth.js](file:///c:/projects/github/EvATasks/backend/src/routes/auth.js)
- Update `/login` route to check if `user.two_fa_enabled` is true.
- If true, issue a "pre-auth" token and return `two_fa_required: true`.
- Ensure standard routes only accept "full" tokens.

#### [MODIFY] [2fa.js](file:///c:/projects/github/EvATasks/backend/src/routes/2fa.js)
- Update `/verify` route to return a full JWT token upon successful OTP verification.
- Ensure the route works for both first-time setup and login verification.

#### [MODIFY] [auth.js (middleware)](file:///c:/projects/github/EvATasks/backend/src/middleware/auth.js)
- Update `authMiddleware` to differentiate between `pre-auth` and `full` tokens where necessary.

---

### [Frontend] Flutter Mobile App
Update the Flutter app to handle the new 2FA-inclusive login flow and use consistent API configurations.

#### [MODIFY] [api_client.dart](file:///c:/projects/github/EvATasks/mobile/lib/config/api_client.dart)
- Ensure consistently used `apiBaseUrl` and `dioProvider`.

#### [MODIFY] [login_screen.dart](file:///c:/projects/github/EvATasks/mobile/lib/features/auth/login_screen.dart)
- Replace local `Dio` with `dioProvider`.
- Add logic to handle `two_fa_required` response and navigate to `TwoFaScreen`.

#### [MODIFY] [two_fa_screen.dart](file:///c:/projects/github/EvATasks/mobile/lib/features/auth/two_fa_screen.dart)
- Use `dioProvider` for all requests.
- Update `authTokenProvider` with the full token upon successful verification.
- Improve error handling and loading feedback.

## Verification Plan

### Automated Tests
- Run existing tests: `npm test` in `backend/`
- Add new integration tests for the 2FA login flow in `backend/tests/auth_2fa.test.js`.
    - `POST /auth/login` returns `two_fa_required: true` for 2FA-enabled users.
    - `POST /2fa/verify` with valid OTP returns a full token.

### Manual Verification
1. **Direct Login**: Login with a user having 2FA disabled -> Verify immediate redirect to `/todos`.
2. **2FA Flow**: Login with a user having 2FA enabled -> Verify navigation to `TwoFaScreen`.
3. **Verification**: Enter 6-digit OTP -> Verify successful redirect to `/todos`.
4. **Resend**: Tap "Resend" -> Verify success snackbar.
