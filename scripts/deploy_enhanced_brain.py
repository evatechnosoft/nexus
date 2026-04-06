import paramiko

hostname = "192.168.1.186"
username = "dean"
password = "Eralp123!"

def deploy_enhanced_brain():
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=username, password=password)
        print("Connected to DeanOS.")

        # Gelişmiş sunucu kodunu yerelden oku
        with open("mcp_server_enhanced.py", "r", encoding="utf-8") as f:
            content = f.read()
            # Cat ile yaz (Literal String)
            cmd = f"cat << 'EOF' > /DATA/AppData/nexus-brain/src/mcp_server.py\n{content}\nEOF"
            ssh.exec_command(cmd)
            print("Enhanced mcp_server.py written to server.")

        # Docker Restart
        ssh.exec_command("export DOCKER_CONFIG=/DATA/AppData/docker-config; cd /DATA/AppData/nexus-brain/; docker compose restart nexus-brain")
        print("Nexus Brain restarted with Live Memory support.")
        
        ssh.close()
    except Exception as e:
        print(f"Brain Deployment Error: {e}")

if __name__ == "__main__":
    deploy_enhanced_brain()
