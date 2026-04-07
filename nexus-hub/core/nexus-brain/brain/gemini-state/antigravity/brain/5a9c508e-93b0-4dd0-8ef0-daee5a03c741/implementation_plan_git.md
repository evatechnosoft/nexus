# Git & Local Deployment Automation Plan

The user wants a "single script" to handle committing, pushing to `dev`, merging to `test`, and bringing the system up locally. This will act like a "skill" that the AI can trigger or the user can run.

## Proposed Changes

### 1. Root Automation Script (`deploy.ps1`) [NEW]
Create a PowerShell script (`deploy.ps1`) for Windows that automates the entire lifecycle:
- **Phase 1: Git Sync**:
  - `git commit -a -m "..."`
  - Push to `origin/dev`.
  - Create/Update `test` branch from `dev`.
  - Push to `origin/test`.
- **Phase 2: Local Run**:
  - Stop existing containers (`docker-compose down`).
  - Build and start containers in background (`docker-compose up --build -d`).
  - Show status of services.

### 2. AI Workflow (`.agents/workflows/git.md`) [NEW]
Create a workflow file so that whenever the user says "git" or "/git", I can:
1.  Summarize pending changes.
2.  Run the `deploy.ps1` script with a proper commit message.
3.  Report the deployment status.

### 3. README Update (`README.md`) [MODIFY]
- Add a "Quick Deploy" section explaining how to use the new script.

## User Review Required
> [!IMPORTANT]
> - **Branching Strategy**: You are currently on `main`. My plan assumes you work on `main`, but you want the code to be synced to `dev` and `test` branches automatically. Is this correct?
> - **Local Run**: Do you prefer starting locally via **Docker** (port 8001) or via **Python/Uvicorn** (port 8000) directly? My script will default to Docker as it's more "CI/CD-like".

## Verification Plan
### Automated Tests
- Run `.\deploy.ps1` and verify that all three branches (`main`, `dev`, `test`) have the same latest commit.
- Verify `docker ps` shows the `it-inventory` container running.

### Manual Verification
- Access `http://localhost:8001` to ensure the app is live after deployment.
