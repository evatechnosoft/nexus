# AgentOps-Nexus Implementation Plan

## Objective
Refactor the existing `it-inventory` project into a clean, dual-dashboard system named `agentops-nexus`. 
This system will manage both physical hardware (IT Inventory) and digital assets (Project Health, Agent Skills, Ops Reports).

## Implementation Steps

### Phase 1: Environment & Cleanup (Completed)
- [x] Create `C:\projects\agentops-nexus`.
- [x] Initialize fresh Git repository.
- [x] Create a strict `.gitignore` (ignoring .env, __pycache__, logs, zips).
- [x] Copy only essential source files (`main.py`, `models.py`, `routers/`, `templates/`, `static/`, etc.).

### Phase 2: Architecture Refactoring (Completed)
- [x] **Model Splitting**: Added DigitalModels (Project, ProjectHealth, GlobalSkill).
- [x] **Router Organization**: Created `/api/v1/ops/` router.
- [x] **Frontend Separation**: Created `dashboard_ops.html` for AgentOps and retained `dashboard.html` for Inventory.

### Phase 3: Global Integration (Completed)
- [x] Link `agentops-nexus` to `C:\projects\global-shared`.
- [x] Implement `scripts/discovery.py` to auto-discover projects and global skills and populate the database.

### Phase 4: Local Test & Port Setup (Completed)
- [x] Set `APP_PORT=4550` for dev/test environments.
- [x] Test local functionality with `uvicorn` on port 4550.

### Phase 5: GitHub & CI/CD (Completed)
- [x] Merge `dev` to `test` branch.
- [x] Create new remote repository (`evatechnosoft/agentops-nexus`).
- [x] Push clean code (`main`, `dev`, `test` branches).

### Phase 6: Prod Server Deployment (PostgreSQL & Docker v2) (Completed)
- [x] **Local Preparation:**
  - [x] Ensure `database.py` dynamically handles PostgreSQL vs SQLite using SOLID/DI principles.
  - [x] Create `prod.Dockerfile` optimized for production.
  - [x] Create `prod-docker-compose.yml` configured with a `postgres:15` container.
- [x] **Server Setup & Execution (via SSH 'dean@192.168.1.186'):**
  - [x] Clone/Pull the repository to the designated server directory.
  - [x] Configure `prod.env` with real PostgreSQL credentials and `APP_PORT=4500`.
  - [x] Deploy using Docker Compose v2: `docker compose -f prod-docker-compose.yml --env-file prod.env up -d --build`.

### Phase 7: Bug Fix - Graph API Email Parsing (Completed)
- [x] Modify `_strip_html` in `email_watcher.py` to correctly extract HTML tables coming from `support@findtalent.net`.
  - [x] Convert `</td>` and `</th>` to pipes (` | `).
  - [x] Convert `</tr>` and other block elements to newlines.
  - [x] Unescape HTML entities (e.g., `&nbsp;`).
  - [x] Clean up redundant spaces and trailing pipes.

## Verification & Testing
- [x] Verify local discovery script populates the database correctly.
- [ ] Verify PostgreSQL connection and data persistence on the prod server.
- [ ] Test Microsoft Graph API connectivity for email-to-request flow.
