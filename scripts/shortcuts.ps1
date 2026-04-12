# Nexus Hub Interactive G-System (Windows PowerShell) v3.4
# Kullanım: . .\scripts\shortcuts.ps1

function n-c { python scripts/nexus-compress.py }
function n-sync { python scripts/nexus-sync.py build }
function n-doctor { python scripts/nexus-doctor.py }
function n-index { python core/build_skill_index.py }
function n-dream { python scripts/nexus-dream.py --light }
function n-context { python scripts/nexus-stats.py }

# --- Git Helpers ---
function g-all { 
    param([string]$m) 
    if (!$m) { $m = "chore: nexus hub auto-sync " + (Get-Date -Format "yyyy-MM-dd HH:mm") }
    git add .
    git commit -m "$m"
    git push origin (git branch --show-current)
    Write-Host "🚀 G-ALL: Add, Commit ve Push tamamlandi!" -ForegroundColor Green
}

function g {
    param([string]$cmd, [string]$val)

    if ($cmd) {
        switch ($cmd) {
            "n" { n-context; return }
            "c" { n-compress; return }
            "a" { n-sync; return }
            "d" { n-doctor; return }
            "b" { n-dream; return }
            "i" { n-index; return }
            "s" { git status; return }
            "ga" { git add .; return }
            "m" { if(!$val){$val="chore: update"}; git commit -m "$val"; return }
            "p" { git push origin (git branch --show-current); return }
            "all" { g-all $val; return }
        }
    }

    Clear-Host
    Write-Host "--- NEXUS G-SYSTEM MENU (v3.4) ---" -ForegroundColor Cyan
    Write-Host "[n] Context Status      - Token ve Turn takibi"
    Write-Host "[c] Master Compress     - Oturumu muhurle ve sikistir"
    Write-Host "[a] Sync Rules          - Kurallari (rules) senkronize et"
    Write-Host "[d] System Doctor       - Sistem saglik kontrolu"
    Write-Host "[b] Light Dream         - Dream raporu olustur"
    Write-Host "--------------------------------------"
    Write-Host "[s] Git Status          - Degisiklikleri gor"
    Write-Host "[m] Git Commit          - Degisiklikleri kaydet"
    Write-Host "[p] Git Push            - Buluta gonder"
    Write-Host "[all] G-ALL             - Add + Commit + Push"
    Write-Host "[x] Exit                - Menuden cik"
    Write-Host "--------------------------------------"
    
    $choice = Read-Host "Seciminiz (Harf basin)"
    
    switch ($choice) {
        "n" { n-context }
        "c" { n-compress }
        "a" { n-sync }
        "d" { n-doctor }
        "b" { n-dream }
        "s" { git status }
        "m" { $msg = Read-Host "Commit mesaji"; git commit -m "$msg" }
        "p" { git push origin (git branch --show-current) }
        "all" { g-all }
        "x" { return }
        default { Write-Host "Gecersiz secim!" -ForegroundColor Red }
    }
}

function gn { g n }
function gc { g c }
function gd { g d }
function gs { g s }
function gp { g p }
function gm { g m }
function gall { g all }

Write-Host "🚀 Nexus 'G' System v3.4 Loaded!" -ForegroundColor Green
Write-Host "gall (add+commit+push) aktif."
