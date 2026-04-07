# Fix Syntax Errors in providers_test.dart

The file `providers_test.dart` incorrectly uses arrow functions `() => { ... }` for `group` bodies. In Dart, `() => { ... }` is interpreted as returning a Set or Map literal. Since the bodies contain statement declarations (like `late ProviderContainer container;`), this causes a syntax error because these are not valid elements of a collection literal.

## Proposed Changes

### mobile/test/unit/

#### [MODIFY] [providers_test.dart](file:///c:/projects/EvAnotes/mobile/test/unit/providers_test.dart)

- Convert all `group('...', () => {` occurrences to `group('...', () {`.
- Ensure the corresponding `});` is kept (it will now close the function block and the `group` call).

## Verification Plan

### Automated Tests
- Run `flutter analyze mobile/test/unit/providers_test.dart` to ensure no syntax errors remain.
- Run `flutter test mobile/test/unit/providers_test.dart` (though currently most tests are marked as TODO, it should at least compile and run).

### Manual Verification
- None required as this is a syntax fix.
