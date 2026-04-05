import paramiko

hostname = "192.168.1.186"
username = "dean"
password = "Eralp123!"

memory_content = """# ZimaOS Survival Lessons

- **Rule 1:** ZimaOS (Buildroot) does NOT have `xargs`. Avoid using it in scripts.
- **Rule 2:** Always use Dockerized CLI (node:20-slim) for NPM, NPX, and Claude Code to bypass Read-only errors.
- **Rule 3:** Persistent data must stay in `/DATA/AppData/`.
- **Rule 4:** Dynamic IP can be found with `ip route get 1`.
- **Rule 5:** SSH password for dean is `Eralp123!`.
"""

def seal_memory():
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=username, password=password)
        
        # Hafıza dizinine dosyayı mühürle
        cmd = f"cat << 'EOF' > /DATA/AppData/nexus-brain/data/memory/zimaos_survival_lessons.md\n{memory_content}\nEOF"
        ssh.exec_command(cmd)
        
        # Index'in yenilenmesi için nexus-brain'i tetikle
        ssh.exec_command("export DOCKER_CONFIG=/DATA/AppData/docker-config; cd /DATA/AppData/nexus-brain/; docker compose restart nexus-brain")
        
        print("Nexus Live Memory: 'zimaos_survival_lessons.md' successfully sealed on DeanOS.")
        ssh.close()
    except Exception as e:
        print(f"Sealing Error: {e}")

if __name__ == "__main__":
    seal_memory()
