# AgentOps-Nexus Production Deployment Plan

## Objective
Deploy the `AgentOps-Nexus` application to the remote production server using SSH (user: `dean`), Docker v2, and PostgreSQL.

## Architecture
- **Web App**: FastAPI (Uvicorn) running in a Python 3.11-slim Docker container on port `4550`.
- **Database**: PostgreSQL 15 running in a separate container, mapped to the internal Docker network.
- **Reverse Proxy / SSL**: (Optional) Can be handled by Caddy/Nginx on the host server if required, pointing to `4550`.

## Implementation Steps

### 1. Local Preparation (Dev Branch)
- Update `database.py` to seamlessly switch between local SQLite and Production PostgreSQL based on the `DATABASE_URL` environment variable.
- Create a `Dockerfile` optimized for production (no debug dependencies).
- Create a `docker-compose.prod.yml` defining the `web` and `db` (PostgreSQL) services.
- Merge the feature to `main` (prod) and push to the new GitHub repository (`evatechnosoft/agentops-nexus`).

### 2. Server Deployment (via SSH)
1. SSH into the server as `dean`: `ssh dean@<server-ip>`
2. Clone/Pull the repository to the production directory (e.g., `/opt/agentops-nexus`).
3. Create a `.env.prod` file containing the real PostgreSQL credentials and `APP_PORT=4550`.
4. Execute Docker v2 command: `docker compose -f docker-compose.prod.yml up -d --build`.

### 3. Verification
- Verify the PostgreSQL container is healthy and the database is created.
- Verify the FastAPI container connects successfully and runs migrations (`metadata.create_all`).
- Access the dashboard at `http://<server-ip>:4550` (or via the configured reverse proxy).

## Rollback Strategy
If the deployment fails, use `docker compose down` and revert the Git commit, then rebuild. Data persistence is ensured via Docker volumes (`postgres_data`).
