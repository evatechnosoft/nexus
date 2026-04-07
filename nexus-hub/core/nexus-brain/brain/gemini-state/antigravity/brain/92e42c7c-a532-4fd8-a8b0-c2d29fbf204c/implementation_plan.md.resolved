# Implementation Plan: Fix ZimaOS Cloud Backup Error

The user is experiencing a `failed to create subtask 0` error on ZimaOS. Investigation reveals that the backup tasks (ID 1 and 50) are misconfigured: they attempts to backup *from* the Google Drive mount *to* a non-existent local path, whereas the user intended to backup *from* local storage *to* the cloud.

## Proposed Changes

### ZimaOS Backup Configuration
1. **Clear Stuck Tasks**: Manually remove the misconfigured tasks (ID 1 and 50) from the `/var/lib/icewhale/backup.db` database. This will stop the recurring "unknown error" and "failed to create subtask" messages that likely block the UI.
2. **Verify Environment**: Ensure the `/media/deancjxvr_google_drive_1774592568` mount is stable and has sufficient permissions.
3. **User Guidance**: Advise the user to recreate the backup task in the ZimaOS "Files" or "Backup" app, ensuring that:
    - **Source**: Is a local folder (e.g., `/DATA/it-inventory` or `/DATA/AppData`).
    - **Destination**: Is the Google Drive remote (`deancjxvr_google_drive_1774592568`).

## Verification Plan

### Automated Verification
- **Log Monitoring**: After clearing the tasks, I will monitor `/var/log/icewhale/files-backup.log` to confirm that the `Task error` messages have stopped.
- **Service Restart**: I will restart the `icewhale-files-backup.service` to ensure it reloads with a clean state.

### Manual Verification
- **Create Test Backup**: I will ask the user to attempt creating a small test backup from a local folder to the cloud via the UI and report if the "subtask 0" error persists.
