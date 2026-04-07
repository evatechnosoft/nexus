# IT Inventory Deployment & Port Standardization

We will standardize the IT Inventory deployment on ZimaOS by moving Production to Port **9700** and Staging/Test to Port **9600**. We will also fix the discrepancies in the deployment scripts and path mappings.

## User Review Required

> [!IMPORTANT]
> - **Production Port Change**: The application will move from `192.168.1.186:9600` to `192.168.1.186:9700`.
> - **Test Port Change**: The Test environment will move to port `9600`.
> - **Deployment Scripts**: We will synchronize the local and remote paths to ensure the `deploy.ps1` script works correctly.

## Proposed Changes

### Configuration Files

#### [MODIFY] [.env.prod](file:///c:/projects/it-inventory/.env.prod)
- Update `APP_PORT` and `HOST_PORT` to **9700**.
- Update `APP_BASE_URL` to `http://192.168.1.186:9700`.

#### [MODIFY] [.env.test](file:///c:/projects/it-inventory/.env.test)
- Update `APP_PORT` and `HOST_PORT` to **9600**.
- Update `APP_BASE_URL` to `http://192.168.1.186:9600`.

#### [MODIFY] [docker-compose.yml](file:///c:/projects/it-inventory/docker-compose.yml)
- Clean up redundant environment variables.
- Ensure `HOST_PORT` from `.env` is correctly mapped.

---

### Deployment Scripts

#### [MODIFY] [deploy.ps1](file:///c:/projects/it-inventory/deploy.ps1)
- Swap the port logic:
  - **Main Branch (Prod)**: Deploy to Port **9700**.
  - **Test Branch (Test)**: Deploy to Port **9600**.
- Fix the remote path to `/DATA/AppData/it-inventory`.

#### [MODIFY] [inv.ps1](file:///c:/projects/it-inventory/inv.ps1)
- Update the help text to match the new port mapping (Prod: 9700, Test: 9600).

#### [NEW] [deploy_deanos.sh](file:///c:/projects/it-inventory/deploy_deanos.sh)
- Create a robust shell script for the server to handle:
  - Docker Compose up/down.
  - Image rebuilding if needed.
  - Port assignment based on environment (`test` or `prod`).

---

### Documentation

#### [MODIFY] [zimaos_deployment.md](file:///c:/projects/it-inventory/.gemini/knowledge/zimaos_deployment.md)
- Reflect the final port standard (Prod: 9700, Test: 9600).

## Open Questions

- Should I also update the **Cloudflare Tunnel** (if configured via CLI) to point to the new port 9700 for the production domain?

## Verification Plan

### Automated Tests
- Run `.\inv.ps1 status` after deployment to verify container health.
- Use `curl` or `ssh` to test the internal ports on the server.

### Manual Verification
- Access the app via browser at `http://192.168.1.186:9700`.
- Verify the "Badge" color matches the environment (Green for Prod, Red for Test).
