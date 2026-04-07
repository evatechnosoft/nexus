# IT Inventory V2 Fresh Deployment to DeanOS

The objective is to perform a fresh, stable deployment of the IT Inventory V2 application onto the DeanOS server using the correct repository and production configuration.

## Proposed Changes

### DeanOS Server (SSH Deployment)

1.  **Clone Repository:**
    - Source: `https://github.com/evatechnosoft/it-inventory.git`
    - Destination: `~/it-inventory_production`
2.  **Configuration:**
    - Update `APP_BASE_URL` in `.env` to `https://it.evaitec.com`.
3.  **Deployment:**
    - Run `sudo docker compose up -d --build` in the project directory.
    - Host Port: `8001` (Container Port: `8000`).

## Verification Plan

### Automated Tests
1.  **Container Status:**
    - Run `sudo docker ps --filter "name=it-inventory"` on the server.
2.  **Server Health:**
    - Run `curl -I http://localhost:8001` on the server to check for a 200 OK response.

### Manual Verification (User)
1.  **Cloudflare Tunnel:**
    - Update the tunnel for `it.evaitec.com` to point to `http://localhost:8001`.
2.  **Final Check:**
    - Verify the application is live and functional at `https://it.evaitec.com`.
