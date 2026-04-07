# Project Handoff: casatozima

This document provides a technical summary and transition guide for the `casatozima` project, which was migrated from `casaos-home-server`.

## 🏗️ Technical Architecture

- **Framework:** Flask (Python 3.9)
- **Database:** PostgreSQL 16.2 (Containerized)
- **ORM:** SQLAlchemy
- **Frontend:** Vanilla HTML/CSS/JS with a premium "Evaitec" design system (Glassmorphism, Inter font).
- **Orchestration:** Docker Compose (Multiple environments).

## 🌐 Environment Details

The project is structured into 4 distinct Dockerized environments:

| Service | Port | Purpose | DB |
| :--- | :--- | :--- | :--- |
| `flask-dev` | 5007 | Active development with hot-reload (`./src` volume mount). | `casaos` |
| `flask-test` | 5006 | Staging/QA testing environment. | `casaos` |
| `flask-api` | 5010 | Dedicated backend API layer. | `evanotes` |
| `flask-prod` | 5005 | Production-ready live environment. | `evanotes` |

## 📁 Key Files & Directories

- `docker-compose.yml`: Main orchestration file for all 4 environments + DB.
- `setup.sh`: Automated server setup script for ZimaOS/CasaOS.
- `src/app.py`: Core Flask application logic.
- `src/static/style.css`: Evaitec Design System.
- `src/templates/index.html`: Dashboard UI.

## 🚀 Recent Accomplishments
- **UI/UX Overhaul:** Implemented a modern dashboard with real-time status tracking.
- **Infrastructure:** Moved from a host-gateway DB setup to a fully containerized PostgreSQL stack for portability.
- **Port Standardization:** Resolved port conflicts for ZimaOS deployment.

## 📝 Next Steps
- [ ] Implement user authentication (OAuth or JWT).
- [ ] Add real-time log monitoring to the dashboard.
- [ ] Configure Cloudflare Tunnel (cloudflared) inside the Docker network.
- [ ] Extend the API to support more complex data models beyond `User`.

---
*Generated on 2026-03-24*
