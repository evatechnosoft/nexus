# Bug Fix Plan: Graph API Email Table Parsing

## Objective
Fix the HTML stripping logic in `email_watcher.py` to correctly parse HTML tables coming from Microsoft Graph API (e.g., `support@findtalent.net`).

## Background & Motivation
The current `_strip_html` function blindly removes HTML tags, which causes table cells (`<td>`) from Outlook emails to mash together (e.g., "NameEmail" instead of "Name | Email"). This breaks the regex parser in `email_parser.py` that expects spaces or pipes (`|`) between columns.

## Implementation Steps
- [ ] Modify `_strip_html` in `email_watcher.py`:
  - Convert `</td`> and `</th>` closing tags to pipes (` | `) before removing tags.
  - Convert block elements (`</tr>`, `</p>`, `<br>`) to newlines (`\n`).
  - Unescape HTML entities (e.g., `&nbsp;`).
  - Safely strip the remaining tags.
  - Normalize spacing and trailing pipes.

## Verification
- Receive an HTML table email from Graph API.
- Verify `email_parser.py` correctly identifies the columns (Name, Email, Phone, Department) and creates the Request object without error.
