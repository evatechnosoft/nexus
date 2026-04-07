# Implementation Plan: Dark Mode & English Language

Enhance the food delivery platform with a premium Dark Mode and multi-language (Turkish/English) support.

## User Review Required

> [!NOTE]
> Translations will be handled via a simple JavaScript object map. Dark mode will be toggled by adding a `dark` class to the `document.documentElement`.

## Proposed Changes

### Frontend

#### [MODIFY] [index.html](file:///c:/projects/food-delivery-mock/index.html)
- **Dark Mode**:
  - Add CSS variables for colors (backgrounds, texts) that swap in `.dark` mode.
  - Add a "Moon/Sun" toggle button in the navbar.
  - Update components (glass, cards, hero) to look stunning in dark mode (deep blues/blacks with vibrant orange accents).
- **Language Support**:
  - Add a language dropdown/toggle (TR/EN) in the navbar.
  - Implement a `translations` object in JS.
  - Add `data-i18n` attributes to relevant HTML elements for automatic translation.
  - Ensure the "Keşfet" (Discover) and other UI elements refresh content on language change.

## Verification Plan

### Automated Tests
- N/A.

### Manual Verification
- Toggle Dark Mode and check all sections for readability and aesthetic consistency.
- Toggle EN/TR and verify all strings are translated correctly.
- Ensure the 3D animations and "glass" effects remain high-quality in both modes.
