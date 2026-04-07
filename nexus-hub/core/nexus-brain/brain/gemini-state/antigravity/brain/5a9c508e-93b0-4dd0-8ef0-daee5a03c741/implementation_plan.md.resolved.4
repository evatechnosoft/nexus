# DeanOS Deployment & Exchange Email Fix Plan

The user reports that port 8001 is the intended production port, the Exchange email parsing may be broken, and the SSH deployment failed because the target folder is not a Git repository.

## Actions Required

### 1. Port Migration (9292 -> 8001)
- **[MODIFY] [docker-compose.yml](file:///c:/projects/it-inventory/it-inventory/docker-compose.yml)**: Change host port mapping to `8001:8000`.
- **[MODIFY] [.env](file:///c:/projects/it-inventory/it-inventory/.env)**: Update `APP_BASE_URL` to `http://192.168.1.186:8001`.
- **[MODIFY] [deploy.ps1](file:///c:/projects/it-inventory/it-inventory/deploy.ps1)**: Update local success message URLs to 8001.

### 2. Remote Git Initialization (DeanOS)
- **Fix**: The `~/projects/it-inventory` folder on DeanOS exists but lacks a `.git` metadata.
- **Solution**: Provide a one-liner to initialize and fetch from origin safely without deleting local data (especially the `data/` folder).

### 3. Exchange Email Verification
- **Audit**: Check `email_watcher.py` for any hardcoded values or logic that might fail under the new port or production environment.
- **Resilience**: Ensure the "Soft Match" logic is correctly propagated to the server.

## Verification Plan

### Automated
- **Simulation**: Run `simulate_test.py` locally on 8001.
- **Git**: Push everything to `main`.

### Manual
- **DeanOS Run**: User executes the provided SSH command.
- **UI Check**: Verify 192.168.1.186:8001 is reachable.
