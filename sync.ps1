# OVPFH Sync Wrapper
# This script activates the virtual environment and runs the FotMob sync service

Write-Host "🏟️ Starting OVPFH Data Sync..." -ForegroundColor Cyan

# 1. Activate Virtual Environment
if (Test-Path ".venv\Scripts\Activate.ps1" ) {
    & .venv\Scripts\Activate.ps1
} else {
    Write-Host "⚠️ Virtual environment not found. Ensure .venv exists." -ForegroundColor Yellow
}

# 2. Check Service Account Key
if (!(Test-Path "firebase-service-account.json")) {
    Write-Host "❌ Error: firebase-service-account.json not found in root directory!" -ForegroundColor Red
    Write-Host "Check instructions in md/FIREBASE_AUTH.md" -ForegroundColor Gray
    exit
}

# 3. Run Sync Script
python spiders/fotmob_sync.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Sync completed successfully!" -ForegroundColor Green
} else {
    Write-Host "❌ Sync failed with exit code $LASTEXITCODE" -ForegroundColor Red
}
