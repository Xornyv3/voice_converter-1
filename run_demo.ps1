# Voice to Sign Language Converter - Demo Launcher
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Voice to Sign Language Converter - Demo Launcher" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Choose which script to run:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. vosk_demo.py      - Record with auto-stop (Recommended)" -ForegroundColor Green
Write-Host "2. vosk_pipeline.py  - Continuous mode (Ctrl+C to stop)" -ForegroundColor Green
Write-Host "3. start.py          - Whisper live captions" -ForegroundColor Green
Write-Host "4. verify_setup.py   - Test installation" -ForegroundColor Green
Write-Host ""

$choice = Read-Host "Enter your choice (1-4)"

$python = ".venv\Scripts\python.exe"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Starting vosk_demo.py..." -ForegroundColor Cyan
        Write-Host ""
        & $python vosk_demo.py
    }
    "2" {
        Write-Host ""
        Write-Host "Starting vosk_pipeline.py..." -ForegroundColor Cyan
        Write-Host ""
        & $python vosk_pipeline.py
    }
    "3" {
        Write-Host ""
        Write-Host "Starting start.py (Whisper)..." -ForegroundColor Cyan
        Write-Host "This will download ~240MB on first run" -ForegroundColor Yellow
        Write-Host ""
        & $python start.py
    }
    "4" {
        Write-Host ""
        & $python verify_setup.py
    }
    default {
        Write-Host "Invalid choice!" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host ""
Read-Host "Press Enter to exit"
