# Fix Docker Hub Connectivity for ZimaOS

The user is experiencing frequent failures when pulling Docker images ("Docker Hub patlıyor"). This is common in certain regions (like Turkey) due to DNS poisoning, ISP throttling, or MTU mismatches. This plan implements a multi-layered fix.

## Proposed Changes

### Configuration Files

#### [MODIFY] [daemon.json](file:///d:/OS/Zimaos/daemon.json)
- Add `registry-mirrors` to use reliable mirrors (Google, ArvanCloud, etc.).
- Keep verified DNS settings.

#### [MODIFY] [config.php](file:///DATA/AppData/nextcloud/var/www/html/config/config.php)
- Add `192.168.1.186` and `it.evatechnosoft.com` to `trusted_domains`.

### Manual Verification
- Access Nextcloud via `http://192.168.1.186` and verify the "untrusted domain" error is gone.
- Ensure all other services remain accessible.

## Proposed Command for USer
```bash
# One-liner to apply the fix remotely (once files are updated locally)
scp -i ~/.ssh/zimaos_key d:/OS/Zimaos/fix_all.sh dean@192.168.1.186:/home/dean/fix_all.sh
ssh -i ~/.ssh/zimaos_key dean@192.168.1.186 "chmod +x /home/dean/fix_all.sh && sudo ./home/dean/fix_all.sh"
```
> [!NOTE]
> Since direct SSH currently requires a password or a specific key setup, I will provide the script content for the user to copy-paste if automated deployment fails.
