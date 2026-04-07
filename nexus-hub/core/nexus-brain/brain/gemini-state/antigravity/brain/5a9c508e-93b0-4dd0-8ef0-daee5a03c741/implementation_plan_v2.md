# Enhanced Email Notification & Automated Selection Plan

The user wants to receive a detailed list of ranked devices in the notification email, including features (specs) and serial numbers, and be able to choose which one to assign.

## Proposed Changes

### 1. Token Creation [email_watcher.py]
- Modify `_process_email_item`:
  - Instead of creating a single "approve" token for the top device, create an `ApprovalToken` for **each** of the top 5 (or all) ranked devices.
  - Keep one "reject" token.
  - Pass the list of `(device, score, token)` tuples to the notifier.

### 2. Notification Templates [notifier.py]
- **`send_email_notification`**:
  - Update HTML table to include **Serial Number**, **Features (Notes)**, and an **"Onayla ve Ata" (Approve & Assign)** button for *each* row.
  - Increase the limit of displayed devices from 3 to 10 (or all suitable ones).
- **`send_teams_notification`**:
  - Update the "Facts" or "Sections" to show more devices. (Teams handles multiple buttons in `potentialAction`, but we'll focus on the email as requested).

### 3. Approval Logic [routers/approval.py]
- Modify `approve_request`:
  - When an approval token is used, find all other `ApprovalToken` records linked to the same `request_id` and mark them as `used=1`. This prevents multiple assignments if a user clicks different links in the same email.

### 4. Database [models.py]
- No schema changes required. Existing `ApprovalToken.suggested_device_id` supports this.

## User Review Required
> [!NOTE]
> - Do you want a limit on how many devices are listed in the email? (e.g., "Top 5 most suitable" or "List all available")
> - If no perfect match is found, should the system still send the email with "best effort" matches?

## Verification Plan
### Automated Tests
- Script to trigger `process_queue` on a mock `EmailQueue` item and verify multiple tokens are created.
- Verify that clicking the 2nd device's link in the email correctly assigns that 2nd device.

### Manual Verification
- Send a test email, check the layout of the ranked list.
- Click a specific device's approval button and verify the correct assignment in the IT Inventory dashboard.
