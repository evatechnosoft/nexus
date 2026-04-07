import argparse
import sys
import os

# Add scripts directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

import backup
import health
import restore_checkpoint_test

def main():
    parser = argparse.ArgumentParser(description="Nexus Ops Automation CLI (NPM-Aligned)")
    subparsers = parser.add_subparsers(dest="command", help="Operational commands")

    # Backup Command
    backup_parser = subparsers.add_parser("backup", help="Create a ZIP checkpoint")
    backup_parser.add_argument("--root", help="Custom backup root directory")

    # Health Command
    health_parser = subparsers.add_parser("health", help="Run health probes and monitoring")
    health_parser.add_argument("--endpoints", nargs="+", help="Endpoints to probe")

    # Restore Test Command
    restore_parser = subparsers.add_parser("restore-test", help="Dry-run validation of latest backup")

    args = parser.parse_args()

    if args.command == "backup":
        backup.create_backup(backup_root=args.root)
    elif args.command == "health":
        health.run_health_report(endpoints_urls=args.endpoints)
    elif args.command == "restore-test":
        restore_checkpoint_test.run_restore_test()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
