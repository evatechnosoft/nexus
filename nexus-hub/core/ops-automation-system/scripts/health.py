import os
import json
import time
import requests
import subprocess
from datetime import datetime, timedelta
import argparse

def get_git_info():
    try:
        branch = subprocess.check_output(['git', 'branch', '--show-current'], stderr=subprocess.DEVNULL).decode().strip()
        status = subprocess.check_output(['git', 'status', '--porcelain'], stderr=subprocess.DEVNULL).decode().strip()
        dirty_count = len(status.splitlines()) if status else 0
        return {"branch": branch, "dirtyCount": dirty_count}
    except:
        return {"branch": "unknown", "dirtyCount": 0}

def test_endpoint(url, timeout=8):
    result = {"url": url, "ok": False, "status": None, "latencyMs": None, "error": None}
    try:
        start_time = time.time()
        resp = requests.get(url, timeout=timeout)
        latency = int((time.time() - start_time) * 1000)
        result["ok"] = 200 <= resp.status_code < 400
        result["status"] = resp.status_code
        result["latencyMs"] = latency
    except Exception as e:
        result["error"] = str(e)
    return result

def check_npm_integrity(repo_root):
    # Nginx Proxy Manager specific checks
    data_path = os.path.join(repo_root, 'data')
    db_path = os.path.join(data_path, 'database.sqlite')
    proxy_config_path = os.path.join(data_path, 'nginx', 'proxy_host')
    
    integrity = {
        "data_dir": os.path.exists(data_path),
        "database_exists": os.path.exists(db_path),
        "proxy_configs_count": 0
    }
    
    if os.path.exists(proxy_config_path):
        integrity["proxy_configs_count"] = len([f for f in os.listdir(proxy_config_path) if f.endswith('.conf')])
        
    return integrity

def run_health_report(endpoints_urls=None, backup_root=None, out_file=None):
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    if not backup_root:
        backup_root = os.path.join(repo_root, 'output', 'shared', 'checkpoints')
    
    if not out_file:
        out_file = os.path.join(repo_root, 'output', 'results', 'ops-health-latest.json')
        
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    
    # Default NPM endpoints if none provided
    if not endpoints_urls:
        endpoints_urls = [
            "http://127.0.0.1:81", # NPM Admin UI
            "http://127.0.0.1:9201/healthz",
            "http://192.168.1.186:8900" # Nexus Hub
        ]

    # Backup Freshness
    latest_backup = None
    age_hours = None
    if os.path.exists(backup_root):
        backups = [f for f in os.listdir(backup_root) if f.startswith('checkpoint-') and f.endswith('.zip')]
        if backups:
            backups.sort(key=lambda x: os.path.getmtime(os.path.join(backup_root, x)), reverse=True)
            latest_file = os.path.join(backup_root, backups[0])
            mtime = os.path.getmtime(latest_file)
            age_hours = round((time.time() - mtime) / 3600, 2)
            latest_backup = latest_file

    # Tests
    endpoints_results = [test_endpoint(url) for url in endpoints_urls]
    npm_integrity = check_npm_integrity(repo_root)
    git_info = get_git_info()
    
    # Overall Status
    local_ok = endpoints_results[0]["ok"]
    backup_fresh = age_hours is not None and age_hours <= 24
    
    overall = "ok" if local_ok and backup_fresh and npm_integrity["database_exists"] else "warn"
    
    report = {
        "generatedAt": datetime.now().isoformat(),
        "overall": overall,
        "git": git_info,
        "npm_integrity": npm_integrity,
        "backup": {
            "root": backup_root,
            "latestFile": latest_backup,
            "ageHours": age_hours,
            "fresh24h": backup_fresh
        },
        "endpoints": endpoints_results
    }
    
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
        
    print(f"\033[92m[ops:health-report]\033[0m completed")
    print(f"overall={overall}")
    print(f"report={out_file}")
    
    return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NPM-aligned Health Monitoring")
    parser.add_argument("--endpoints", nargs="+", help="Endpoints to probe")
    parser.add_argument("--output", help="Output report file path")
    args = parser.parse_args()
    
    run_health_report(args.endpoints, out_file=args.output)
