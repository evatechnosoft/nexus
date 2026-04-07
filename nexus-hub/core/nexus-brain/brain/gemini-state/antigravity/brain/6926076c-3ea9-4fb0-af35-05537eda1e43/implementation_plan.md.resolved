# Fix Docker Connection and Deploy IT Inventory

The user is experiencing a connection error with Docker in the terminal. The Docker service is currently stopped.

## Proposed Changes

### [System]
- Start the Docker service (`com.docker.service`).
- Switch Docker context to `default` (already done).

### [Deployment]
- Run `docker compose up -d` in the `it-inventory/it-inventory` directory.

## Verification Plan

### Automated Tests
- Run `docker info` to verify the daemon is reachable.
- Run `docker ps` to verify the container is running.

### Manual Verification
- Access `http://localhost:8000` in the browser to confirm the IT inventory app is accessible.
