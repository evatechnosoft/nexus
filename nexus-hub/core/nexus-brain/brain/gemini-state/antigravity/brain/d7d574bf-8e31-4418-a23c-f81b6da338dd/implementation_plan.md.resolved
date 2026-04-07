# Implementation Plan - Migration to casatozima

The goal is to migrate the latest changes and infrastructure improvements from `casaos-home-server` to the `casatozima` project, document the work done, and transition to `casatozima` as the primary development repository.

## Proposed Changes

### casatozima

#### [MODIFY] [docker-compose.yml](file:///c:/projects/github/casatozima/docker-compose.yml)
- Update port mappings to match the latest configuration (API: 5010, Prod: 5005).
- Add the `db` (PostgreSQL 16.2) service to ensure a self-contained stack, or maintain the host-gateway setup if specifically required for ZimaOS (I will assume the user wants the full stack including DB as per the last working version in `casaos-home-server`).
- Update `DATABASE_URL` to point to the containerized DB.

#### [NEW] [README.md](file:///c:/projects/github/casatozima/README.md)
- Document the recent work:
    - Implementation of 4 environments (Dev, Test, API, Prod).
    - Premium UI/UX design for the Dashboard.
    - PostgreSQL integration with SQLAlchemy.
    - Port standardizations.

#### [MODIFY] [setup.sh](file:///c:/projects/github/casatozima/setup.sh)
- Copy and adapt the latest `setup.sh` from `casaos-home-server` if it contains useful automation.

## Verification Plan

### Automated Tests
- Run `docker-compose config` in `casatozima` to verify the syntax.
- Check file integrity between the two projects.

### Manual Verification
- Verify that `casatozima` contains all files from `casaos-home-server/flask-app`.
- User can test the deployment on ZimaOS.
