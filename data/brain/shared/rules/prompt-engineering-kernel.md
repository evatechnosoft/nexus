# Nexus Prompt Engineering: KERNEL Framework

## Mandatory 6 Patterns (Reddit r/PromptEngineering Anchor)
- **K - Knowledge Context:** Define exactly what the AI needs to know (Single goal focus).
- **E - Easy to Verify:** Include measurable success criteria (e.g., "3 code examples").
- **R - Reproducible Results:** Use specific versions and avoid temporal references ("current trends").
- **N - Narrow Scope:** One prompt = One goal. Separate code, docs, and tests.
- **E - Explicit Constraints:** Tell AI what NOT to do (Negative constraints).
- **L - Logical Structure:** Format as: [Context] -> [Task] -> [Constraints] -> [Output Format].

## Operational Protocols
- **Prompt Chaining:** Prefer simple KERNEL prompts chained together over one complex "mega-prompt".
- **Token Optimization:** KERNEL compliance targets -50% token usage and +300% accuracy.
- **Revision Reduction:** Goal is first-try success (72% -> 94% improvement target).

## Example: Before KERNEL vs After KERNEL
- **Bad:** "Help me write a script to process data files."
- **Good:**
    - Task: Python script to merge CSVs.
    - Input: Multiple CSVs with same headers.
    - Constraints: Pandas only, <50 lines, no external libs.
    - Output: single merged.csv.
    - Verify: Test on `data/test_csv/`.
