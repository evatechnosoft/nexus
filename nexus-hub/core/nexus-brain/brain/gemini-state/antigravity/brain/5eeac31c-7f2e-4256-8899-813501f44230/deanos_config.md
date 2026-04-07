# DeanOS Connection & Configuration

This document provides the necessary details for connecting to and maintaining the DeanOS server.

## Connection Details
- **Static IP:** `192.168.1.186`
- **User:** `dean`
- **SSH Private Key:** `C:\Users\Deacjx\.ssh\deanos` (Unencrypted)
- **SSH Public Key:** `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIKESujH8+5iJjeTxqKGiPpDehLbKyeGjTqIBk6vXXp/W dean`
- **Host Alias:** `deanos` (configured in `~/.ssh/config`)

## Maintenance & Restoration
A master fix script is located at `/usr/local/bin/fix_deanos.sh` on the server. This script reapplies:
1. Static IP & DNS settings.
2. Docker Hub mirrors and MTU optimization.
3. Passwordless sudo privileges.
4. Persistent SSH authorized keys (redirected to `/DATA`).
5. Nextcloud trusted domains.

### How to Run Fix
If the system is reset or connectivity issues recur, run:
```bash
sudo fix_deanos.sh
```

### Local Management
Use the `zima.ps1` script in the root directory for common management tasks.
