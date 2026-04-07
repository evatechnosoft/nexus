# Goal Description

The user wants to improve the customization options of the E-Car Dashboard by adding:
1. An **Edit Mode on the Dashboard** where they can visually adjust the vertical text/gauge alignments and sizes using sliders directly on the main screen, rather than adjusting them blindly from the settings screen.
2. **Digital Font Options** using `google_fonts` to give the dashboard a more tech/digital feel.
3. **More Accent Color Choices** beyond the existing neon, cyan, and orange.

## Proposed Changes

### Dependencies
#### [MODIFY] pubspec.yaml
- Add `google_fonts` package to provide digital font families like Orbitron, Rajdhani, or Share Tech Mono.

---
### Settings Provider
#### [MODIFY] lib/providers/settings_provider.dart
- Add `enum AppFont { system, orbitron, rajdhani, shareTechMono }`.
- Expand `enum AccentColor { neon, cyan, orange, red, green, purple, pink, blue }`.
- Add `fontFamily` to the `AppSettings` model with state management and persistence using SharedPreferences.

---
### Theme Configuration
#### [MODIFY] lib/theme/app_theme.dart
- Update the `accentOf(AccentColor a)` method to return Flutter `Color` objects for the new accent colors.
- Update `dark()` and `light()` methods to accept an `AppFont` and apply it to the `textTheme` using `GoogleFonts.getFont()` (falling back to default if `system`).

---
### Dashboard Screen (Edit Mode Overlay)
#### [MODIFY] lib/screens/dashboard_screen.dart
- Introduce a global or local state `isEditingLayoutProvider = StateProvider<bool>((ref) => false);`.
- In the `build` method, check if `isEditingLayout` is true. If true:
  - Hide the normal app bar icons (Settings, Mock, BLE).
  - Overlay a **Bottom Control Panel** with sliders for the vertical alignments (`speedVerticalAlign`, `rpmVerticalAlign`, `battVerticalAlign`) and scales so the user gets instant visual feedback on the main gauges.
  - Add a **"Bitti (Kaydet)"** button at the top to exit edit mode and lock changes.

---
### Settings Screen
#### [MODIFY] lib/screens/settings_screen.dart
- **Font Selection**: Add a new "YAZI TİPİ" (Font) section to let the user pick their preferred digital font.
- **Colors**: Update the "VURGU RENGİ" (Accent Color) picker to display the newly added colors as visual color chips or circles.
- **Layout Edit Button**: In the "GÖSTERGE STİLİ + BOYUT" section, add a prominent "Ana Ekranda Düzenle" (Edit on Main Screen) button. When tapped, it will set `isEditingLayoutProvider` to true and pop the Navigation stack back to the Dashboard.

## Verification Plan

### Automated Tests
- Run `flutter analyze` to ensure no syntax or typing errors were introduced.
- Run `flutter run -d chrome --web-port=8080` to interact with the updated app in the browser subagent.

### Manual Verification
1. I will use the browser subagent to click the "Ayarlar" (Settings) icon.
2. Verify that the new Font and Color options are present and selectable.
3. Click the new "Ana Ekranda Düzenle" button in settings.
4. Verify that the app returns to the Dashboard and the new "Edit Mode" bottom panel with layout sliders is visible.
5. Capture a screenshot of the Edit Mode on the dashboard to prove it works dynamically.
