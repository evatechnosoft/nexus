# Task: Test SpeechSynthesis for Child and Adult tones

## Checklist
- [x] Open http://localhost:5000/week/1
- [x] Test Child simulation (Pitch 1.6, Rate 1.1)
- [x] Test Child simulation (Pitch 1.8, Rate 1.1)
- [x] Compare Child simulations
- [x] Test Adult simulation (Pitch 1.0, Rate 1.0)
- [x] Test Adult simulation (Pitch 0.9, Rate 1.0)
- [x] Compare Adult simulations
- [x] Identify the most distinct pair
- [x] Return the recommended Pitch/Rate values

## Findings
- Child Simulation (1.6, 1.1): Sounds like a clear, young voice (~10-12 years).
- Child Simulation (1.8, 1.1): Sounds very high-pitched, potentially a younger child (~5-7 years).
- Adult Simulation (1.0, 1.0): Standard natural voice.
- Adult Simulation (0.9, 1.0): Slightly deeper, more mature sounding voice.

**Recommendation:**
The most distinct and natural-sounding pair for a 10-year-old vs an adult is:
- **Child:** Pitch **1.6**, Rate **1.1**
- **Adult:** Pitch **0.9**, Rate **1.0**
