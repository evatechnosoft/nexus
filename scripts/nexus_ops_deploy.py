import paramiko
import os

hostname = "192.168.1.186"
username = "dean"
password = "Eralp123!"

def deploy_ops():
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=username, password=password)
        print("Connected to DeanOS.")

        # Dizin oluştur
        ssh.exec_command("mkdir -p /DATA/AppData/nexus-brain/ops")

        # claude.sh dosyasını yerelden oku ve sunucuya yaz
        with open("ops/claude.sh", "r", encoding="utf-8") as f:
            content = f.read()
            # Cat ile yaz (Literal String)
            cmd = f"cat << 'EOF' > /DATA/AppData/nexus-brain/ops/claude.sh\n{content}\nEOF"
            ssh.exec_command(cmd)

        # custom_profile.sh dosyasını yerelden oku ve sunucuya yaz
        with open("ops/custom_profile.sh", "r", encoding="utf-8") as f:
            content = f.read()
            cmd = f"cat << 'EOF' > /DATA/AppData/nexus-brain/ops/custom_profile.sh\n{content}\nEOF"
            ssh.exec_command(cmd)

        # Yetkileri ayarla
        ssh.exec_command("chmod +x /DATA/AppData/nexus-brain/ops/claude.sh")
        print("Nexus Ops Tools (Claude/NPM/NPX) successfully deployed to DeanOS.")
        
        ssh.close()
    except Exception as e:
        print(f"Ops Deployment Error: {e}")

if __name__ == "__main__":
    deploy_ops()
