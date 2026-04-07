# EV Dashboard Architecture Spec

## Core Principles
- **SOLID Compliance**:
  - **S**: Each Gauge is a separate widget/painter.
  - **O**: New Gauge types can be added by implementing a base `GaugeProvider`.
  - **L**: All gauges adhere to a uniform lifecycle.
  - **I**: Smaller interfaces for Gauge settings vs Gauge rendering.
  - **D**: Depend on abstractions for data (EVDataRepository).

- **Clean Architecture**:
  - `domain`: Entities (VehicleState, GaugeConfig) and Use Cases.
  - `data`: Repositories and local storage (for persistence of layout).
  - `presentation`: BLoC/Riverpod for state, Flutter CustomPainters for high-perf gauges.

## Design System (Frontend Design Skill)
- **Aesthetic**: Cyber-Neon / Dark-Mode.
- **Micro-interactions**: Hover glows, elastic transitions for needles, and haptic-feedback ready.
- **Dynamic Background**: Particle system or gradient mesh reacting to speed (using CustomPainter).

## Key Features
- **Draggable Layout**: Gauges can be moved and their positions saved.
- **Customization**: Per-gauge settings for color, max value, and style.
