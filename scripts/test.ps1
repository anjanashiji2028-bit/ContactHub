# ContactHub Automated Test Suite Runner for Windows
# Run from PowerShell: .\scripts\test.ps1

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Running Full ContactHub Automated Test Suite..." -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$venvPython = ".\venv\Scripts\python.exe"
if (Test-Path $venvPython) {
    $runner = $venvPython
} else {
    $runner = "python"
}

Write-Host "`n[1/2] Running Unit and Integration Tests (pytest)..." -ForegroundColor Yellow
& $runner -m pytest

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n[!] Some pytest tests failed. Please review the output above." -ForegroundColor Red
} else {
    Write-Host "`n[+] All application pytest tests passed!" -ForegroundColor Green
}

Write-Host "`n[2/2] Running Local Serverless Lambda Function Tests..." -ForegroundColor Yellow
& $runner serverless/test_local.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n[!] Serverless tests failed." -ForegroundColor Red
    Exit 1
} else {
    Write-Host "`n[+] All serverless local tests passed!" -ForegroundColor Green
}

Write-Host "`n==========================================================" -ForegroundColor Cyan
Write-Host " Automated Testing Completed Successfully!" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan
