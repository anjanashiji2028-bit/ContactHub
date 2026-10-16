# ContactHub Automated Windows Setup Script
# Run from PowerShell: .\scripts\setup.ps1

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " ContactHub - Windows Environment Automated Setup" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Check Python installation
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "[ERROR] Python 3 was not found on your system PATH." -ForegroundColor Red
    Write-Host "Please install Python 3.10+ from python.org and check 'Add Python to PATH'." -ForegroundColor Yellow
    Exit 1
}

$pyVersion = python --version
Write-Host "[+] Detected $pyVersion" -ForegroundColor Green

# 2. Virtual Environment Setup (optional but recommended)
$venvDir = "venv"
if (-not (Test-Path $venvDir)) {
    Write-Host "[*] Creating Python virtual environment in '$venvDir'..." -ForegroundColor Yellow
    python -m venv $venvDir
} else {
    Write-Host "[+] Virtual environment '$venvDir' already exists." -ForegroundColor Green
}

# Identify python and pip paths
$venvPython = ".\$venvDir\Scripts\python.exe"
if (Test-Path $venvPython) {
    $runner = $venvPython
} else {
    $runner = "python"
}

# 3. Upgrade pip and install required packages
Write-Host "[*] Installing dependencies from requirements.txt..." -ForegroundColor Yellow
& $runner -m pip install --upgrade pip
& $runner -m pip install -r requirements.txt

# 4. Copy .env template if not present
if (-not (Test-Path ".env")) {
    Write-Host "[*] Creating default .env configuration file from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
}

# 5. Initialize and seed SQLite database
Write-Host "[*] Initializing and seeding the SQLite development database..." -ForegroundColor Yellow
& $runner database/seed_data.py

Write-Host "`n==========================================================" -ForegroundColor Green
Write-Host " ContactHub Setup Completed Successfully!" -ForegroundColor Green
Write-Host " Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Start the application:   .\scripts\run.ps1" -ForegroundColor White
Write-Host "   2. Run automated tests:     .\scripts\test.ps1" -ForegroundColor White
Write-Host "   3. Demo Login:              demo@contacthub.local / Demo@12345" -ForegroundColor White
Write-Host "==========================================================" -ForegroundColor Green
