import paramiko

hostname = "192.168.1.186"
username = "dean"
password = "Eralp123!"

handoff_content = """# Nexus Handoff (2026-04-04) - Mühürlü

## Context (Vaziyet)
- **Universal Nexus Brain:** 192.168.1.186 (DeanOS). Zekâ (Ollama:4602), Hafıza (MCP:8900) ve Dashboard (Grafana:3100) başarıyla merkezileştirildi.
- **Dockerized CLI:** ZimaOS'taki kısıtlamalar `node:20-slim` konteynerleri (alias npm/npx/claude) ile aşıldı. `ops/` dizinindeki scriptler sunucuya mühürlendi.
- **Dual Environment Protocol:** ZimaOS (Linux/Bash) ve Masaüstü (Windows/PowerShell) ayrımı %100 asistan hafızasında mühürlü.
- **Live Memory:** `mcp_server.py` artık `save_memory` yeteneğine sahip. Git kuralları ve ZimaOS dersleri sunucu hafızasına (.md) yazıldı.

## Artifacts (Mühürlü Dosyalar)
- `ops/claude.sh` & `ops/custom_profile.sh`: Sunucu operasyon araçları.
- `mcp_server.py`: Gelişmiş Live Memory destekli MCP sunucusu.

## Current State
- **Git Branch:** `feature/nexus-universal-intelligence` (GitHub güncel).
- **Nexus Hub Status:** ALL SYSTEMS NOMINAL (8900, 4601, 4602, 3100).
"""

def seal_server_handoff():
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=username, password=password)
        
        # Sunucu hafızasına (data/memory) mühürle
        cmd = f"cat << 'EOF' > /DATA/AppData/nexus-brain/data/memory/handoff_2026_04_04.md\n{handoff_content}\nEOF"
        ssh.exec_command(cmd)
        
        # Index tazele (Restart)
        ssh.exec_command("export DOCKER_CONFIG=/DATA/AppData/docker-config; cd /DATA/AppData/nexus-brain/; docker compose restart nexus-brain")
        
        print("Nexus Server Intelligence: Handoff successfully sealed on DeanOS.")
        ssh.close()
    except Exception as e:
        print(f"Sealing Error: {e}")

if __name__ == "__main__":
    seal_server_handoff()
