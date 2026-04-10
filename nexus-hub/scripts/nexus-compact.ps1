<#
.SYNOPSIS
Nexus Compact - Hafıza Sıkıştırma ve Temizlik Görevi (Windows)

.DESCRIPTION
Bu betik, Nexus Hub'ın hafıza dosyalarını analiz eder ve eski/tekrar eden kayıtları temizler.
Windows Görev Zamanlayıcısı (Task Scheduler) ile her gece çalıştırılması önerilir.

KULLANIM:
powershell.exe -ExecutionPolicy Bypass -File .\nexus-compact.ps1
#>

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonPath = "python" # Eğer venv kullanıyorsanız tam yolu buraya yazın (Ör: C:\projects\skills\.venv\Scripts\python.exe)
$CompactScript = Join-Path $ScriptDir "nexus-compact.py"

Write-Host "--- Nexus Compact Başlatılıyor ---" -ForegroundColor Cyan
& $PythonPath $CompactScript

if ($LASTEXITCODE -eq 0) {
    Write-Host "Nexus Compact başarıyla tamamlandı." -ForegroundColor Green
} else {
    Write-Host "Nexus Compact sırasında bir hata oluştu!" -ForegroundColor Red
}
