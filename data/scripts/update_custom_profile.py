import paramiko

hostname = "192.168.1.186"
username = "dean"
password = "Eralp123!"

# Sizin istediğiniz o akıllı dinamik IP tespiti
content = """# Nexus Brain - Custom Profile Standard (Dinamik IP)
alias npm='docker run -it --rm -v /DATA/AppData/npm-global:/root -v $(pwd):/app -w /app node:20-slim npm'
alias npx='docker run -it --rm -v /DATA/AppData/npm-global:/root -v $(pwd):/app -w /app node:20-slim npx'
alias claude='/DATA/AppData/nexus-brain/ops/claude.sh'

# Dinamik Ollama Host Tespiti (ZimaOS Standard)
export OLLAMA_HOST="http://$(ip route get 1 | awk '{print $7}'):11434"
export DOCKER_CONFIG="/DATA/AppData/claude-config/.docker"
"""

def update_profile():
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=username, password=password)
        
        # Literal Cat (No escaping mess)
        cmd = f"cat << 'EOF' > /DATA/AppData/nexus-brain/ops/custom_profile.sh\n{content}\nEOF"
        ssh.exec_command(cmd)
        print("Universal Intelligence: custom_profile.sh updated with Dynamic IP on DeanOS.")
        ssh.close()
    except Exception as e:
        print(f"Update Error: {e}")

if __name__ == "__main__":
    update_profile()
