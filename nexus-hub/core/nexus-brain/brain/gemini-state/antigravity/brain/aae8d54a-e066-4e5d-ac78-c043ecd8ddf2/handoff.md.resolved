# Session Handoff: it-inventory Deployment (DeanOS)

## Current Status
- **Goal:** Successful it-inventory deployment on Coolify V4 on ZimaOS.
- **Problem Solved:** Bypassed the 'Read-only file system' error caused by ZimaOS kernel restrictions on `/root/.ssh`.
- **Infrastructure:** Coolify V4 instance is stable on port 9800.
- **Source Files:** Synced directly to `/DATA/AppData/it-inventory` on the DeanOS server.

## Next Steps for Tomorrow
1. **Coolify UI Access:** Navigate to `http://192.168.1.186:9800`.
2. **New Application:** Create a new resource -> 'Docker Compose'.
3. **Paste Config:** Use the finalized compose snippet below:

```yaml
version: '3.8'
services:
  it-inventory:
    build:
      context: /DATA/AppData/it-inventory
      dockerfile: Dockerfile
    container_name: it-inventory-coolify
    ports:
      - "9700:8000"
    volumes:
      - /DATA/AppData/it-inventory/data:/app/data
    environment:
      - DATABASE_URL=sqlite:///app/data/inventory.db
    restart: always
```

4. **Deploy:** Hit 'Save' and 'Deploy'.
5. **Verify:** Check Port 9700.

## Knowledge Updates
- [zimaos_deployment.md](file:///c:/projects/it-inventory/.gemini/knowledge/zimaos_deployment.md) has been updated with the 'Local Sync Bypass' strategy for future reference.

> [!TIP]
> All files on the server at `/DATA/AppData/it-inventory` are currently set to `777` permissions to avoid any ZimaOS UID mismatch during the build phase.
