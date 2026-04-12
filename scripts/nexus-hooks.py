#!/usr/bin/env python3
import sys
import os
import subprocess
import json

def check_branch():
    """Branch kontrolü yapar. 'dev' veya 'prod' ise Exit 2 ile engeller."""
    try:
        branch = subprocess.check_output(["git", "branch", "--show-current"]).decode().strip()
        if branch in ["dev", "prod"]:
            print(f"❌ [NEXUS HOOK BLOCK] Doğrudan '{branch}' branch'inde kod değiştiremezsin!")
            print("👉 Lütfen önce yeni bir dal aç: git checkout -b feature/veya-fix/...")
            sys.exit(2) # 2 = Claude Code / LLM Tool Block Error
    except Exception as e:
        pass

def handle_pre_use():
    """Tool çalışmadan önce tetiklenir."""
    # Sadece dosya değiştiren komutlarda veya Bash'te çalışsın (örnek olarak tümünde branch kontrolü)
    check_branch()
    print("✅ [NEXUS HOOK] Pre-Use Validation Passed.")
    sys.exit(0)

def handle_post_use():
    """Tool çalıştıktan sonra (Post-Use) tetiklenir."""
    # Sadece yeni bir skill veya hafıza (memory) eklendiğinde (veya değiştiğinde) senkronizasyon yap.
    try:
        status = subprocess.check_output(["git", "status", "--porcelain"]).decode().strip()
        if "data/memory/" in status or ".ai/" in status:
            print("🧠 [NEXUS HOOK] Yeni Hafıza/Skill kazanımı tespit edildi!")
            print("🚀 Otomatik Distribute ve Push tetikleniyor...")
            
            # 1. Distribute (Skill ve Kural tasnifi)
            subprocess.run([sys.executable, "scripts/nexus-sync.py", "distribute"], capture_output=True)
            
            # 2. Push (ZimaOS Hub'a mühürleme)
            push_res = subprocess.run([sys.executable, "scripts/nexus-sync.py", "push"], capture_output=True, text=True)
            
            if "Başarılı" in push_res.stdout or "işlendi" in push_res.stdout:
                print("✨ Kazanım merkezi hafızaya (Hub) mühürlendi.")
            else:
                print("⚠️ Hub'a push edilirken bir sorun oluştu.")
    except Exception as e:
        pass
    sys.exit(0)

def handle_stop():
    """Claude/LLM işlemi bitirmeden önce (StopHook) tetiklenir."""
    print("⚠️ [NEXUS HOOK] Stop Hook Tetiklendi. Hafıza ve limit kontrolü yapılıyor...")
    
    state_file = ".nexus-session-state"
    if os.path.exists(state_file):
        try:
            with open(state_file, "r") as f:
                state = json.load(f)
                turns = state.get("turns", 0)
                if turns >= 5:
                    print("❌ [NEXUS HOOK BLOCK] Turn limiti aşıldı! (5+)")
                    print("👉 Hafıza şişmek üzere. Kullanıcıya 'gc' veya 'n-compress' çalıştırmasını söyle ve oturumu sonlandır!")
                    sys.exit(2) # LLM'in durmasını engeller ve ona bu hatayı çözmesini emreder
        except Exception:
            pass
    sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(0)
    
    hook_type = sys.argv[1]
    
    if hook_type == "pre-use":
        handle_pre_use()
    elif hook_type == "post-use":
        handle_post_use()
    elif hook_type == "stop":
        handle_stop()
    else:
        sys.exit(0)
