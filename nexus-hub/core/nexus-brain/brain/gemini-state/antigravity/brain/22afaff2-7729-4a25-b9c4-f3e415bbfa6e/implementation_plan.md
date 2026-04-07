# Add Simple Variable Test

## Goal Description
Create a basic test in the `mobile` Flutter project that verifies a Dart variable's value, ensuring the test infrastructure works.

## Proposed Changes
---
### Mobile Project
#### [MODIFY] main.dart (no changes needed)

#### [NEW] test/variable_test.dart
```dart
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('variable holds expected value', () {
    const int testValue = 42;
    expect(testValue, equals(42));
  });
}
```

---
## Verification Plan
### Automated Tests
- Run `flutter test` in `c:\projects\EvAnotes\mobile`.
- Expect the command to exit with code 0 and show the test passing.

### Manual Verification (optional)
- Open the project in an IDE and ensure the `test/` folder appears.
- Run the test via IDE test runner and confirm success.
