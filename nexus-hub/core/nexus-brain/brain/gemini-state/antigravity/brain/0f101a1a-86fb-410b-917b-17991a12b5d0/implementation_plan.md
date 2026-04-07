# Fix Pubspec Asset Paths

The current asset paths in `mobile/pubspec.yaml` incorrectly include the `mobile/` prefix, which is redundant since the `pubspec.yaml` file is already within the `mobile` directory. This causes Flutter to look for assets in `mobile/mobile/assets/...`, which does not exist.

## Proposed Changes

### Mobile App

#### [MODIFY] [pubspec.yaml](file:///c:/projects/evapps/EvA-NoTeS/EvAnotes/mobile/pubspec.yaml)
- Remove `mobile/` prefix from lines 73-74:
  - `- mobile/assets/images/` -> `- assets/images/`
  - `- mobile/assets/icons/` -> `- assets/icons/`

#### [NEW] [images directory](file:///c:/projects/evapps/EvA-NoTeS/EvAnotes/mobile/assets/images)
- Create the `assets/images` directory if it doesn't exist to ensure the defined asset path is valid.

## Verification Plan

### Automated Tests
- Run `flutter pub get` in the `mobile` directory to ensure the configuration is valid and all assets are found.
  ```powershell
  cd mobile
  flutter pub get
  ```

### Manual Verification
- Check if the terminal reports any errors regarding missing asset directories.
