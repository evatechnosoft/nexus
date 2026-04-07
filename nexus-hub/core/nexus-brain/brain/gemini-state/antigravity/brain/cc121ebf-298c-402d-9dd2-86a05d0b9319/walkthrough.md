# Walkthrough: ZimaOS Infrastructure and Database Setup

We have successfully stabilized the ZimaOS environment, resolved network routing issues, and deployed the PostgreSQL database stack.

## Changes Made

### 1. Network & Connectivity Fixes
- **Routing Correction:** Removed problematic default route via `169.254.0.1` and prioritized `wlan0`.
- **DNS Persistence:** Forced `1.1.1.1` and `8.8.8.8` in `/etc/resolv.conf` and Docker configuration.
- **Time Sync:** Enabled NTP synchronization to prevent certificate and Docker Hub handshake errors.

### 2. PostgreSQL Database Deployment
- **Location:** All files are stored in a persistent directory: `/DATA/AppData/postgres`.
- **Initialization:** Created `init-db.sql` to automatically provision the following databases:
    - `nextcloud`
    - `inventory`
    - `db-dev`
    - `db-test`
- **Containerization:** Deployed using `docker run` (fallback mode) with the following credentials:
    - **User:** `dean`
    - **Password:** `Eralp123!`
    - **Port:** `5432`

### 3. MySQL Database Configuration
- **Status:** Initialized for external extension connections.
- **User:** `dean`
- **Password:** `Eralp123!`
- **Port:** `3306`

### 4. Database Verification
- [x] PostgreSQL on port 5432 (nextcloud, inventory, db-dev, db-test)
- [x] PostgreSQL on port 5433 (dev-evaitec)
- [x] MySQL on port 3306 (dean user configured)

### Connectivity
- [x] `ping google.com` successful.
- [x] Docker Hub image pulling active.

### Databases
- [x] PostgreSQL container started.
- [x] Databases initialized via entrypoint script.

## Next Steps
- **Application Deployment:** You can now proceed with installing Nextcloud and IT Inventory, pointing them to the PostgreSQL instance at `192.168.1.186:5432`.
