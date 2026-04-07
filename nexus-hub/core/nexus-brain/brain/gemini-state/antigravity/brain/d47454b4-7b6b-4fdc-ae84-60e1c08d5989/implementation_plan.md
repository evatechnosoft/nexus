# Packaging IT Inventory for Docker Deployment

The goal is to provide a single, portable solution to transfer the IT Inventory application to a remote server. This will involve building the Docker image locally and exporting it to a `.tar` file, along with the necessary configuration files.

## User Review Required

> [!IMPORTANT]
> This process requires Docker to be running on the local Windows machine. 

## Proposed Changes

### Docker Packaging Script

#### [NEW] [package_docker.ps1](file:///c:/projects/it-inventory/it-inventory/package_docker.ps1)
A PowerShell script to automate the build and export process.
- Builds the `it-inventory:latest` image.
- Exports the image to `it-inventory-image.tar`.
- Copies `docker-compose.yml` and `.env.example` to the output folder.

### Documentation Update

#### [MODIFY] [DOCKER.md](file:///c:/projects/it-inventory/it-inventory/DOCKER.md)
Update the documentation to include instructions for "Transferring via Image Tarball".

## Verification Plan

### Manual Verification
1. Run `package_docker.ps1` and verify the output files exist.
2. Instrucing the user to transfer the `dist/` folder to the server.
3. On the server: `docker load -i it-inventory-image.tar`.
4. Run `docker compose up -d`.
5. Check if the app is accessible at port 8000.
