# Task: Implement/Fix End-to-End 2FA Flow

- [ ] Backend: Update Login logic to support 2FA [/]
    - [ ] Update `auth.js` login route to check `two_fa_enabled`
    - [ ] Create a "pre-auth" token system for 2FA verification
    - [ ] Update `2fa.js` to return a full JWT upon successful OTP verification
- [ ] Frontend: Update Login and 2FA UI [/]
    - [ ] Fix `LoginScreen` to handle 2FA required status and navigate to `TwoFaScreen`
    - [ ] Fix `TwoFaScreen` to use the `apiClientProvider` and store the authenticated token
    - [ ] Improve UI/UX of the 2FA screen (loading states, error messages)
- [ ] Verification [/]
    - [ ] Verify login flow with 2FA disabled
    - [ ] Verify login flow with 2FA enabled
    - [ ] Verify resend functionality
