# Infrastructure Strategy: Local Docker-Compose Deployment on Coolify V4

This plan bypasses the SSH/Git 'Read-only' errors by using local project files and a direct Docker-Compose configuration within the Coolify V4 management panel.

## User Review Required

> [!IMPORTANT]
> - We will use the **'Docker Compose'** resource type in Coolify instead of 'Public/Private Repository'.
> - We will manually sync the project files from your local machine to the DeanOS server.

## Proposed Changes

### [Component] IT-Inventory Source Files

#### [EXECUTE] [Local Sync]
1. **Sync Files:** Use `scp` or `rsync` to move the current `it-inventory` files from `c:\projects\it-inventory` to `dean@192.168.1.186:/DATA/AppData/it-inventory`.
2. **Permissions:** Ensure the sync folder is writable by the Docker process.

### [Component] Coolify V4 Configuration

#### [MODIFY] [Coolify UI Application]
- **Resource Type:** Docker Compose.
- **Compose Content:** I will provide a refined `docker-compose.yml` that points to the local volume for the database and uses the correct build context.
- **Port Mapping:** Host 9700 -> Container 8000.

## Open Questions

> [!NOTE]
> - Hocam, dosyaları sunucuya (DeanOS) benim şu anki `ssh dean` bağlantım üzerinden mi gönderelim yoksa sen terminalden bir `scp` mi tercih edersin? (Benim yapmam daha hızlı olur). 🚀🦾🦾
