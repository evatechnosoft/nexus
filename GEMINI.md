# Nexus State Anchor (2026-04-04)

## Current State (Vaziyet: Universal Nexus Brain)
- **Hub:** 192.168.1.186 (DeanOS).
- **Intelligence (8900/4601/4602):** Successfully centralized. Port 8900 is the gateway for ALL external tools.
- **Universal Memory:** ChromaDB is persistent on DeanOS and synced across all interfaces (Open WebUI, VS Code, Claude Code).
- **Dockerized CLI:** `npm`, `npx` and `claude` are now server-side services accessible via MCP.

## Hard-Learned Lessons (Mühürlü Tecrübeler)
- **Server-First:** Never rely on local paths; always use /DATA/AppData/ nexus-brain/ structure.
- **Surgical SSH:** Use 'paramiko' or direct SSH for autonomous server management.
- **ZimaOS Survival:** Use 'node:20-slim' containers for all Node-based CLI operations.

## Next Steps (Sıradaki Adımlar)
- [ ] **Universal Integration:** Add Claude and Gemini API keys to the server-side `claude.sh` wrapper.
- [ ] **Global Dashboard:** Launch the "Beyin Bedava" Grafana (3100) counter.
- [ ] **MCP Expansion:** Expose server-side 'npm' and 'npx' commands as MCP tools on Port 8900.

## Critical Constraints
- **Dual Environment Protocol:** Commands for ZimaOS (Server, Linux/Bash) must use Linux paths (/DATA/AppData/...) and Bash syntax (cat << 'EOF'). Commands for Windows (Desktop, PowerShell) must use PowerShell syntax (Out-File, $env:). Never mix them. If the target environment is ambiguous, I MUST ask for clarification.
- **Universal Access:** All memory and tool access MUST be via Port 8900 (MCP).
- **Zero Localism:** Treat local 'C:\projects\skills' only as a git mirror.
