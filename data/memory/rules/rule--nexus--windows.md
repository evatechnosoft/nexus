---
id: rule--nexus--windows
type: infrastructure
context: global
extends: rule--nexus--master
description: Windows ortamÄ± (win32) iÃ§in kabuk, yol ve SSH standartlarÄ±.
---
# NEXUS WINDOWS PROTOCOL (LOCAL & REMOTE)

## 💻 KABUK (SHELL) STANDARTLARI
Windows ortamÄ±nda her zaman **PowerShell** kullanÄ±lÄ±r.

1. **Operatörler:**
   - `&&` veya `||` ASLA KULLANILMAZ.
   - ArdÄ±ÅŸÄ±k komutlar iÃ§in her zaman `;` (noktalÄ± virgÃ¼l) kullanÄ±lÄ±r.
2. **Yollar (Paths):**
   - Windows yerel yollarÄ± iÃ§in her zaman `\` (ters slash) kullanÄ±lÄ±r.
   - Git/Docker komutlarÄ± iÃ§in Linux formatÄ±na (`/`) dikkat edilir.
3. **Heredoc:**
   - `cat <<EOF` (Linux) yerine her zaman `@"..."@` (PowerShell Heredoc) kullanÄ±lÄ±r.

## 🔐 SSH STANDARTLARI (REMOTE ACCESS)
ZimaOS (192.168.1.186) Ã¼zerindeki iÅŸlemler iÃ§in her zaman SSH kullanÄ±lÄ±r.

1. **Sabit SSH Komutu:**
   - `ssh -i ~/.ssh/zimaos_key dean@192.168.1.186 "<komut>"`
2. **Remote Operatörler:**
   - SSH tÄ±rnak iÃ§indeki komutlarda Linux standartlarÄ± (`&&`, `||`, `|`) geÃ§erlidir.
3. **Dosya Transferi:**
   - `scp -i ~/.ssh/zimaos_key <kaynak> dean@192.168.1.186:<hedef>`

## 📊 KONTROL LÄ°STESÄ° (WINDOWS)
- [ ] Komutlar `;` ile ayrÄ±ldÄ± mÄ±?
- [ ] Path `D:\MainProjects\...` formatÄ±nda mÄ±?
- [ ] `&&` yerine `;` kullanÄ±ldÄ± mÄ±?
- [ ] SSH iÃ§in `dean` kullanÄ±ldÄ± mÄ±?
