import os
import shutil
import zipfile
import json
from datetime import datetime
import tempfile
import argparse

def create_backup(backup_root=None, include_paths=None):
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    if not backup_root:
        backup_root = os.path.join(repo_root, 'output', 'shared', 'checkpoints')
    
    os.makedirs(backup_root, exist_ok=True)
    
    # NPM (Nginx Proxy Manager) Standard Paths + User Defaults
    user_home = os.path.expanduser('~')
    if not include_paths:
        include_paths = [
            # Nginx Proxy Manager standard data folders
            os.path.join(repo_root, 'data'),
            os.path.join(repo_root, 'letsencrypt'),
            # AI/Dev environment configs
            os.path.join(user_home, '.claude'),
            os.path.join(user_home, '.copilot'),
            os.path.join(repo_root, '.env'),
            os.path.join(repo_root, '.gitignore')
        ]

    stamp = datetime.now().strftime('%Y%m%d-%HH%MM%SS')
    zip_filename = f"checkpoint-{stamp}.zip"
    zip_path = os.path.join(backup_root, zip_filename)
    
    temp_stage = tempfile.mkdtemp(prefix=f"checkpoint-stage-{stamp}")
    
    manifest = {
        "createdAt": datetime.now().isoformat(),
        "host": os.environ.get('COMPUTERNAME', os.environ.get('HOSTNAME', 'unknown')),
        "repoRoot": repo_root,
        "included": []
    }

    try:
        for path in include_paths:
            if not os.path.exists(path):
                continue
            
            name = os.path.basename(path)
            dest = os.path.join(temp_stage, name)
            
            if os.path.isdir(path):
                shutil.copytree(path, dest, dirs_exist_ok=True)
                manifest["included"].append({"path": path, "type": "directory"})
            else:
                shutil.copy2(path, dest)
                manifest["included"].append({"path": path, "type": "file"})
        
        # Save manifest
        with open(os.path.join(temp_stage, 'manifest.json'), 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
            
        # Create ZIP
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(temp_stage):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_stage)
                    zipf.write(file_path, arcname)
        
        print(f"\033[92m[ops:backup]\033[0m checkpoint created: {zip_path}")
        return zip_path

    finally:
        shutil.rmtree(temp_stage, ignore_errors=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NPM-aligned Python Backup Utility")
    parser.add_argument("--root", help="Custom backup root directory")
    parser.add_argument("--include", nargs="+", help="Additional paths to include")
    args = parser.parse_args()
    
    create_backup(args.root, args.include)
