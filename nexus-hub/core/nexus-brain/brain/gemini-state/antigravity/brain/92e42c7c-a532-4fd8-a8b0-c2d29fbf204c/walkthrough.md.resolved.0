# Walkthrough: Fix ZimaOS Cloud Backup Error

The cloud backup error "failed to create subtask 0" was resolved on the ZimaOS server.

## Summary of Changes
- **Identified Root Cause**: Two backup tasks (ID 1 and 50) were misconfigured: they were set to back up FROM the Google Drive mount TO a non-existent local path. This caused a "not exist" error during task initialization.
- **Database Cleanup**: Manually removed the invalid tasks from the `/var/lib/icewhale/backup.db` database on the ZimaOS server.
- **Service Verification**: Restarted the `icewhale-files-backup.service` and verified from the logs that the error has stopped.

## Verification Results
- **Service Status**: [Active (running)]
- **Latest Logs**:
```
2026-03-27T11:33:50.779Z        info    Connected to message-bus
```
- **Rclone Connectivity**: Verified that the `deancjxvr_google_drive_1774592568` remote is fully functional with 2TB of free space.

## Next Steps for You
To set up a correct cloud backup:
1. Open the **Files** or **Backup** app on your ZimaOS dashboard.
2. Create a NEW backup task.
3. Ensure the **SOURCE** is a local folder (e.g., `/DATA/it-inventory`).
4. Ensure the **DESTINATION/TARGET** is your Google Drive remote (`deancjxvr_google_drive_1774592568`).
