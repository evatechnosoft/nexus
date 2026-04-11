---
id: rule--nexus--windows
type: infrastructure
context: global
extends: rule--nexus--master
description: Windows ortamı (win32) için kabuk, yol ve SSH standartları.
---
# NEXUS WINDOWS PROTOCOL (LOCAL & REMOTE)

## 💻 KABUK (SHELL) STANDARTLARI
Windows ortamında her zaman **PowerShell** kullanılır.

1. **Operatörler:**
   - `&&` veya `||` ASLA KULLANILMAZ.
   - Ardışık komutlar için her zaman `;` (noktalı virgül) kullanılır.
2. **Yollar (Paths):**
   - Windows yerel yolları için her zaman `\` (ters slash) kullanılır.
   - Git/Docker komutları için Linux formatına (`/`) dikkat edilir.
3. **Heredoc:**
   - `cat <<EOF` (Linux) yerine her zaman `@"..."@` (PowerShell Heredoc) kullanılır.

## 🔐 SSH STANDARTLARI (REMOTE ACCESS)
ZimaOS (192.168.1.186) üzerindeki işlemler için her zaman SSH kullanılır.

1. **Sabit SSH Komutu:**
   - `ssh -i ~/.ssh/zimaos_key dean@192.168.1.186 "<komut>"`
2. **Remote Operatörler:**
   - SSH tırnak içindeki komutlarda Linux standartları (`&&`, `||`, `|`) geçerlidir.
3. **Dosya Transferi:**
   - `scp -i ~/.ssh/zimaos_key <kaynak> dean@192.168.1.186:<hedef>`

## 📊 KONTROL LİSTESİ (WINDOWS)
- [ ] Komutlar `;` ile ayrıldı mı?
- [ ] Path `D:\MainProjects\...` formatında mı?
- [ ] `&&` yerine `;` kullanıldı mı?
- [ ] SSH için `dean` kullanıldı mı?
