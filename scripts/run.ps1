# ContactHub Windows Run Script
# Run from PowerShell: .\scripts\run.ps1

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Starting ContactHub Web Application..." -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# Check for virtual environment python
$venvPython = ".\venv\Scripts\python.exe"
if (Test-Path $venvPython) {
    $runner = $venvPython
} else {
    $runner = "python"
}

# Ensure database exists
if (-not (Test-Path "database\contacthub.db")) {
    Write-Host "[*] Database not detected. Initializing with sample demo data..." -ForegroundColor Yellow
    & $runner database/seed_data.py
}

Write-Host "`n[+] Application URL:    http://127.0.0.1:5000" -ForegroundColor Green
Write-Host "[+] Health Endpoint:    http://127.0.0.1:5000/health" -ForegroundColor Green
Write-Host "[+] Demo User Account:  demo@contacthub.local / Demo@12345" -ForegroundColor Yellow
Write-Host "`nPress Ctrl+C to stop the development server.`n" -ForegroundColor DarkGray

# Start server
& $runner app.py
