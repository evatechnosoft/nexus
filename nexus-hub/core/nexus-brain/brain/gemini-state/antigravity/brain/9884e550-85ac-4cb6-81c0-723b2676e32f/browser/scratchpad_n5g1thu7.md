# Task Checklist

- [x] Open http://localhost:5000
- [x] Login as 'student' with password '123'
- [x] Navigate to http://localhost:5000/week/1
- [ ] Verify "hello" card has "merhaba" -> **FAILED: "merhaba" not found.**
- [ ] Click "hello" and verify details (phonetic and syllables: [he-low]) -> **FAILED: Shows placeholders "[...]" and "...".**
- [x] Take screenshot of expanded card
- [x] Navigate to http://localhost:5000/week/2
- [ ] Verify "red" card has "kırmızı" -> **FAILED: "kırmızı" not found.**
- [ ] Long-press "red" and verify 'speaking' CSS class -> **FAILED: JS could not find the card with 'speaking' class.**
- [x] Check console for errors

## Findings
- Week 1: Card "hello" does not show "merhaba". Details are placeholders.
- Week 2: Card "red" does not show "kırmızı".
- Long-press on "red" did not trigger 'speaking' class (or card not found in JS).
- Console shows 401 for `/api/me` and 404 for `/login`.
- API `/api/week/1` and `/api/week/2` only return raw word strings, no metadata.
