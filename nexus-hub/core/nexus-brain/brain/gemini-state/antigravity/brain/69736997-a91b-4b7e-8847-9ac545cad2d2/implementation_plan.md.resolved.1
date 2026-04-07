# Server Connectivity, Subdomain Restoration & Status Dashboard Plan

The goal is to restore access to all services via their subdomains (specifically fixing the IT Inventory link), provide a comprehensive access list, and create a premium live status dashboard for all containers.

## User Review Required

> [!IMPORTANT]
> The `cloudflared` tunnel ingress configuration is currently incomplete. It only routes `api.evaitec.com`. I need to re-add the missing subdomains (`it`, `next`, `evaitec`, `ha`) to the tunnel to make them accessible again.

> [!TIP]
> I will also implement a **Premium Status Dashboard** (Glassmorphism design) that will show the live health of all services in one place, fulfilling the "Follow-up monitoring" request.

## Proposed Changes

### Documentation

#### [NEW] [access_list.md](file:///d:/OS/Zimaos/access_list.md)
Create a master list of all services, their internal ports, and their corresponding subdomains for easy reference.

### Infrastructure & Monitoring (DeanOS)

#### [MODIFY] cloudflared configuration
Identify and update the `ingress` rules for the Cloudflare tunnel to include:
- `it.evaitec.com` -> `http://localhost:8001`
- `evaitec.com` -> `http://localhost:3001`
- `next.evaitec.com` -> `http://localhost:80`
- `ha.evaitec.com` -> `http://localhost:8123`
- `status.evaitec.com` -> `http://localhost:8088` (New Dashboard)

#### [NEW] [Status Dashboard](file:///DATA/dean/projects/status_dashboard)
Create a premium, glassmorphism-themed status page using HTML/CSS/JS. It will:
- Display the status (UP/DOWN) of all containers.
- Provide direct links to each service.
- Show system resource usage (RAM/CPU/Disk).
- Auto-refresh every 60 seconds.

#### [NEW] [Status Check Script](file:///DATA/dean/projects/status_dashboard/monitor.sh)
A lightweight bash/python script that runs via Cron to update a `status.json` file used by the dashboard.

#### [MODIFY] [handoff_memory.md](file:///d:/OS/Zimaos/handoff_memory.md)
Add a "Recovery & Troubleshooting" section that specifically details how to fix the Cloudflare Tunnel if it loses its ingress configuration again, and how the status dashboard works.

## Open Questions

1. Are there any other subdomains that should be active?
2. Does the user have access to the Cloudflare Dashboard to verify the tunnel status if my remote fix doesn't persist?

## Verification Plan

### Automated Tests
- `ping` each subdomain from the system.
- Check `Test-NetConnection` for each public port.
- Use the `browser_subagent` to verify `http://it.evaitec.com/` loads correctly.

### Manual Verification
- Ask the user to click the links in the newly created `access_list.md`.
