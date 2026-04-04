import paramiko

hostname = "192.168.1.186"
username = "dean"
password = "Eralp123!"

def rescue_brain():
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=username, password=password, timeout=60)
        print("Connected to DeanOS.")

        # 1. Dockerfile Düzelt (Surgical Fix)
        with open("ops/Dockerfile.fix", "r", encoding="utf-8") as f:
            content = f.read()
            cmd = f"cat << 'EOF' > /DATA/AppData/nexus-brain/Dockerfile\n{content}\nEOF"
            ssh.exec_command(cmd)
            print("Dockerfile repaired (CMD quotes fixed).")

        # 2. Restart Loop Durdur & Temizle
        print("Stopping and cleaning up broken nexus-brain container...")
        ssh.exec_command("export DOCKER_CONFIG=/DATA/AppData/docker-config; cd /DATA/AppData/nexus-brain/; docker compose down nexus-brain")
        
        # 3. Yeniden Build Et ve Başlat
        print("Rebuilding and starting nexus-brain (Port 8900)...")
        ssh.exec_command("export DOCKER_CONFIG=/DATA/AppData/docker-config; cd /DATA/AppData/nexus-brain/; docker compose up -d --build nexus-brain")
        
        print("Nexus Brain successfully rescued and restarted on Port 8900!")
        ssh.close()
    except Exception as e:
        print(f"Rescue Error: {e}")

if __name__ == "__main__":
    rescue_brain()
