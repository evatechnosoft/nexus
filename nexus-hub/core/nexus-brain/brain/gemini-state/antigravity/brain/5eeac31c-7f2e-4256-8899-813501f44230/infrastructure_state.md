# DeanOS Infrastructure State (Persistence & Memory)

This document summarizes the final stable state of the DeanOS (ZimaOS) server as of March 27, 2026.

## 🖥️ Server Details
- **Hostname:** `DeanOS`
- **Static IP:** `192.168.1.186`
- **SSH Access:** Passwordless (`ssh deanos`) using `~/.ssh/deanos` key.
- **Root FS:** Writable via squashfs overlay (though core is read-only).

## 🚀 Active Services
| Service | Internal Port | URL (if applicable) | Path |
| :--- | :--- | :--- | :--- |
| **Nextcloud** | 80 | `next.evaitec.com` | `/DATA/AppData/nextcloud` |
| **IT Inventory** | 8001 | - | `/DATA/dean/projects/inventory_app` |
| **Evaiteclabs** | 3001 | `evaitec.com` | `/DATA/dean/projects/evaiteclabs` |
| **Home Assistant** | 8123 | `ha.evaitec.com` | `/DATA/AppData/homeassistant` |
| **Adminer** | 8080 | - | - |
| **PostgreSQL** | 5432 | - | `/DATA/AppData/postgresql` |
| **Dozzle (Logs)** | 8888 | `192.168.1.186:8888` | Real-time Docker logs |
| **Uptime Kuma** | 3002 | `192.168.1.186:3002` | Status monitoring |

## 🛠️ Automation & Maintenance
- **Master Fix Script:** `/DATA/fix_deanos.sh`
  - Re-applies Network, DNS, Docker Mirrors, SSH, and Sudo fixes.
- **Self-Healing:** `/DATA/monitor_deanos.sh`
  - Runs every 5 mins via **Cron**.
  - Pings `8.8.8.8`; if unreachable, it triggers `fix_deanos.sh`.
- **Daily Backups:** `/DATA/daily_backup.sh`
  - Runs daily at **17:30** via **Cron**.
  - Archives system state + AppData (excludes large AI data).
  - Syncs to **Nextcloud** user `dean` (Backups folder).

## 🐱‍💻 Version Control
- **Setup Repo:** `evatechnosoft/zimaSetup` (local: `d:\OS\Zimaos`).
- **Scripts:** All `.sh` scripts are pushed to this repo.

## 💡 Future Development Notes
- The system is designed to be **immutable-friendly**: All persistent data and scripts live on `/DATA`.
- **Resource Warning:** Stable Diffusion models (4.6GB+) were removed to prevent OOM. Re-enable only with dedicated VRAM management.

---
*Status: 100% Operational & Automated.* 🚀
