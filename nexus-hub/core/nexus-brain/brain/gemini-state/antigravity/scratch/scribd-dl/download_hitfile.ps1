param (
    [string]$Url
)

# Set environment variables for Puppeteer
$env:PUPPETEER_EXECUTABLE_PATH = "C:\Program Files\Google\Chrome\Application\chrome.exe"
$env:PUPPETEER_SKIP_CHROMIUM_DOWNLOAD = "true"

# Interactive prompt if no URL is provided
if (-not $Url) {
    $Url = Read-Host -Prompt "Please enter the Hitfile URL to download"
}

if ($Url) {
    Write-Host "`nGenerating Direct Link via OkDebrid for: $Url" -ForegroundColor Cyan
    node okdebrid_downloader.js $Url
} else {
    Write-Host "`nNo URL provided. Exiting..." -ForegroundColor Yellow
}
