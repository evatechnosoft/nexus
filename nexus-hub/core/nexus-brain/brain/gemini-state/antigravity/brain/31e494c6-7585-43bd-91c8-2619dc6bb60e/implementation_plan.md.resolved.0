# Replace Deprecated `withOpacity`

`withOpacity` is deprecated in recent Flutter versions because it can lead to precision loss during color calculations. The replacement, `.withValues(alpha: ...)`, provides a more robust way to modify the alpha channel of a color.

## Proposed Changes

### Core UI
#### [MODIFY] [main.dart](file:///c:/projects/claude+antigravity/projects/car_dash/lib/main.dart)
Replace all instances of `withOpacity(x)` with `withValues(alpha: x)`.

### Presentation Widgets
#### [MODIFY] [vertical_info_bar.dart](file:///c:/projects/claude+antigravity/projects/car_dash/lib/presentation/widgets/vertical_info_bar.dart)
#### [MODIFY] [gauge_mini_settings.dart](file:///c:/projects/claude+antigravity/projects/car_dash/lib/presentation/widgets/gauge_mini_settings.dart)
#### [MODIFY] [gauge_layout_wrapper.dart](file:///c:/projects/claude+antigravity/projects/car_dash/lib/presentation/widgets/gauge_layout_wrapper.dart)
#### [MODIFY] [futuristic_gauge.dart](file:///c:/projects/claude+antigravity/projects/car_dash/lib/presentation/widgets/futuristic_gauge.dart)
#### [MODIFY] [digital_gauge.dart](file:///c:/projects/claude+antigravity/projects/car_dash/lib/presentation/widgets/digital_gauge.dart)

### Screens
#### [MODIFY] [settings_screen.dart](file:///c:/projects/claude+antigravity/projects/car_dash/lib/presentation/screens/settings_screen.dart)

### Painters
#### [MODIFY] [vertical_bar_gauge_painter.dart](file:///c:/projects/claude+antigravity/projects/car_dash/lib/presentation/painters/vertical_bar_gauge_painter.dart)
#### [MODIFY] [speed_particles_painter.dart](file:///c:/projects/claude+antigravity/projects/car_dash/lib/presentation/painters/speed_particles_painter.dart)
#### [MODIFY] [speedometer_painter.dart](file:///c:/projects/claude+antigravity/projects/car_dash/lib/presentation/painters/speedometer_painter.dart)

## Verification Plan

### Automated Tests
- Run `flutter analyze` to ensure no new warnings or errors are introduced.
- Run existing tests to ensure no regressions in UI rendering.

### Manual Verification
- Launch the application and verify that the dashboard UI, gauges, and settings screen still render with the correct transparency levels.
- Check the status bar lock toggle to see if the background color transitions correctly.
