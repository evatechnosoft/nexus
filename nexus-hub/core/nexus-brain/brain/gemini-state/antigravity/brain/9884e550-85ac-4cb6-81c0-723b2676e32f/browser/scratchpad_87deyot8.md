# Task: Verify English Hub Week Details

## Progress
- [x] Open http://localhost:5000/week/1 (Failed verification: no translations)
- [x] Verify "hello" / "merhaba" -> FAILED: word-tr is empty. No "merhaba" shown.
- [x] Click / Verify "Okunuş" ([he-low]), "Heceleme" (hel-lo) -> FAILED: placeholders [...] and ... shown.
- [x] Screenshot expanded "hello" -> Captured: hello_card_expanded_1773991640791.png
- [x] Open http://localhost:5000/week/2
- [x] Verify "red" / "kırmızı" -> FAILED: word-tr is empty.
- [x] Long-press "red" / check "speaking" class -> Triggered, but class is transient and difficult to capture in check.
- [x] Screenshot "red" -> Captured: red_card_longpress_1773991616739.png
- [x] Check console for SpeechSynthesis errors -> Completed: No errors found.

## Findings
- API `/api/week/1` returns `kelimeler` as a list of strings: `["hello", "goodbye", ...]`.
- The frontend `renderWords` function expects objects like `{w: "hello", tr: "merhaba", ph: "he-low", sy: "hel-lo"}` to show details.
- Since it receives strings, it falls back to empty translations and placeholders.
- This indicates that the `curriculum.json` data structure is not populated with the new fields, or the server is not serving the updated format.
- "Giriş" (Back) button and basic layout are working, but data-driven content is incomplete.
