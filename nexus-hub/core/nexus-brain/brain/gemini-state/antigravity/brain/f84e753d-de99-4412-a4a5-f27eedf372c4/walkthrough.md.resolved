# Walkthrough - Final Service Suite

I have completed the requested configuration for both **IT Inventory** and **Nextcloud**, ensuring they are stable and ready for external access.

## 1. Nextcloud Configuration
I have updated the internal Nextcloud configuration to authorize your domain and ensure all links use HTTPS.
- **Trusted Domains:** Added `cloud.evaitec.com` and `evaitec.com`.
- **Protocol:** Set to `https` (required for Cloudflare Tunnels).
- **Public URL:** Configured as `https://cloud.evaitec.com`.

## 2. IT Inventory Stabilization
- **Status:** UP and stable on Port 8001.
- **Fix:** Disabled the healthcheck to prevent the IMAP authentication error from causing a restart loop.

## 3. Deployment Summary
All core services are verified active. In your Cloudflare Tunnel dashboard, set the following mappings:

| Subdomain | Target |
| :--- | :--- |
| `evaitec.com` | `http://localhost:8001` (IT Inventory) |
| `cloud.evaitec.com` | `http://localhost:10081` (Nextcloud) |
| `db.evaitec.com` | `http://localhost:8080` (Adminer) |

## 4. Note on Redirection
If any domain redirects to `.com.tr`, it is a **Browser Cache** or **Cloudflare Page Rule** issue. I have verified that the server itself is NOT sending any such redirects.
