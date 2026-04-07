# Adjust Dashboard Layout

The goal is to refine the bottom indicators' layout to be edge-aligned and properly sized without requiring scrolling.

## Proposed Changes

### Dashboard Layout

#### [MODIFY] [dashboard_screen.dart](file:///c:/projects/claude/e-car-dashboard/flutter_app/lib/screens/dashboard_screen.dart)

- Modify `_ZoneBar` to use a `Row` instead of `ListView` for better alignment control.
- Implement zone-based alignment:
    - `MetricZone.left`: `MainAxisAlignment.start`
    - `MetricZone.right`: `MainAxisAlignment.end`
    - `MetricZone.center`: `MainAxisAlignment.center`
- Update `_MetricChip` to allow for flexible sizing and prevent overflow.
- Ensure padding and spacing are optimized for "edge-aligned" appearance.

## Verification Plan

### Automated Tests
- None.

### Manual Verification
- Use `browser_subagent` to verify the new layout on the dashboard.
- Check different screen widths if possible (via browser resizing or URL parameters if supported).
