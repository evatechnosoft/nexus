#!/usr/bin/env python3
import zipfile
import json
import os
import sys
import shutil
from datetime import datetime
from pathlib import Path
import tempfile

def run_restore_test():
    repo_root = Path(__file__).parent.parent
    backup_root = repo_root / 'output' / 'shared' / 'checkpoints'

    if not backup_root.exists():
        print(f'[restore-checkpoint-test] Backup folder not found: {backup_root}')
        return False

    # Find latest checkpoint
    checkpoints = sorted(backup_root.glob('checkpoint-*.zip'), key=lambda p: p.stat().st_mtime, reverse=True)
    if not checkpoints:
        print(f'[restore-checkpoint-test] No checkpoint zip found')
        return False

    checkpoint_file = checkpoints[0]
    print(f'[ops:restore-test] using {checkpoint_file}')

    # Extract to temp dir
    temp_dir = tempfile.mkdtemp(prefix=f"checkpoint-restore-test-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
    extract_dir = Path(temp_dir)
    print(f'[ops:restore-test] extracting to {extract_dir}')

    try:
        try:
            with zipfile.ZipFile(checkpoint_file, 'r') as z:
                z.extractall(extract_dir)
        except Exception as e:
            print(f'[restore-checkpoint-test] Extraction failed: {e}')
            return False

        # Validate manifest
        manifest_path = extract_dir / 'manifest.json'
        if not manifest_path.exists():
            print(f'[restore-checkpoint-test] manifest.json not found in checkpoint')
            return False

        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            entries = len(manifest.get('included', []))
            print(f'[ops:restore-test] manifest has {entries} entries')
        except Exception as e:
            print(f'[restore-checkpoint-test] Failed to read manifest: {e}')
            return False

        # Check NPM specific files in backup
        # NPM structure inside ZIP might be 'data/database.sqlite' or just 'database.sqlite'
        npm_files = ['database.sqlite', 'data/database.sqlite']
        npm_found = any((extract_dir / f).exists() for f in npm_files)
        if npm_found:
            print(f'[ops:restore-test] ✓ NPM Database found in backup')

        print(f'[ops:restore-test] ✓ PASS')
        return True

    finally:
        # Cleanup
        shutil.rmtree(extract_dir, ignore_errors=True)
        print(f'Temporary extraction cleaned up.')

if __name__ == "__main__":
    run_restore_test()
