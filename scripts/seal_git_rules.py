import paramiko

hostname = "192.168.1.186"
username = "dean"
password = "Eralp123!"

git_rules_content = """# Nexus Git Standard Rules (Mühürlü)

## 1. Branch Strategy (Dal Stratejisi)
- **feature/**: Yeni özellikler için.
- **bug/**: Hata düzeltmeleri için.
- **fix/**: Acil yamalar için.
- **dev**: Tüm geliştirmelerin toplandığı ana geliştirme dalı.
- **test**: Kullanıcı onayı öncesi QA/Test dalı.
- **main / prod**: Canlı üretim ortamı. Kullanıcı 'tamam' demeden buraya geçiş yapılmaz.

## 2. Commit Discipline (Commit Disiplini)
- **Incremental Commits**: Her alt görev (task) bittiğinde commit atılır, biriktirilmez.
- **Clear Messages**: Commit mesajları kısa, öz ve 'neden' yapıldığını açıklamalıdır.
- **Junk-Free Policy**: `.venv`, `.zip`, `.log`, `.bak` gibi geçici dosyalar asla stage edilmez/commitlenmez.

## 3. Preservation (Koruma)
- **Data Files**: `.json` uzantılı veri dosyaları projenin hafızasıdır, silinmez ve korunur.
- **Dotfiles**: `.gemini/`, `.claude/`, `.handoff.md` gibi gizli dosyalar oturum sürekliliği için hayati önem taşır, asla silinmez.

## 4. Workflow (İş Akışı)
- Geliştirme `feature/` branch'inde başlar.
- Önce `dev` branch'ine merge edilir.
- Kullanıcı onayıyla `test` branch'ine aktarılır.
- Son doğrulamadan sonra `main` branch'ine 'mühürlenir'.
"""

def seal_git_rules():
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=username, password=password)
        
        # Git kurallarını hafızaya mühürle
        cmd = f"cat << 'EOF' > /DATA/AppData/nexus-brain/data/memory/git_standard_rules.md\n{git_rules_content}\nEOF"
        ssh.exec_command(cmd)
        
        # Index tazeleme (Surgical restart)
        ssh.exec_command("export DOCKER_CONFIG=/DATA/AppData/docker-config; cd /DATA/AppData/nexus-brain/; docker compose restart nexus-brain")
        
        print("Nexus Universal Intelligence: Git Standard Rules successfully sealed on DeanOS.")
        ssh.close()
    except Exception as e:
        print(f"Sealing Error: {e}")

if __name__ == "__main__":
    seal_git_rules()
