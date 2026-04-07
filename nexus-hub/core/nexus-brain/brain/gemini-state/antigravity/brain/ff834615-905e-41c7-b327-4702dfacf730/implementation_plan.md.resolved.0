# Fix file_picker Implementation Error

The `file_picker` package version `6.2.1` currently resolved in the project is causing "missing inline implementation" errors for Linux, macOS, and Windows. This is a known configuration issue in older versions of the package when used with newer Flutter SDKs. Upgrading to the latest major version (`^10.0.0`) should resolve this.

## User Review Required

> [!IMPORTANT]
> This change upgrades `file_picker` from version `6.x` to `10.x`. This is a significant jump and may include breaking changes in the API. While I will check the code for basic compatibility, you should verify any custom file picking logic after the upgrade.

## Proposed Changes

### mobile

#### [MODIFY] [pubspec.yaml](file:///c:/projects/EvAnotes/mobile/pubspec.yaml)
- Update `file_picker` to `^10.3.10`.
- Update `connectivity_plus` to `^7.0.0`.
- Update `device_info_plus` to `^12.3.0`.
- Update `google_sign_in` to `^7.2.0`.

## Verification Plan

### Automated Tests
- Run `flutter pub get` in the `mobile` directory to ensure all dependencies resolve without the "missing inline implementation" error.
- Run existing tests to ensure no regressions:
  ```powershell
  cd mobile
  flutter test
  ```

### Manual Verification
- Launch the app on a target platform and verify that file picking functionality still works.
