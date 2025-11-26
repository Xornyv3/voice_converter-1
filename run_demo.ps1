# Voice to Sign Language Converter - Faster-Whisper Edition
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Voice to Sign Language Converter (Faster-Whisper)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Choose your option:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Start Voice to ASL Converter (RECOMMENDED) ⭐" -ForegroundColor Green
Write-Host "2. Test WLASL Video Generator" -ForegroundColor Green
Write-Host "3. Verify Installation" -ForegroundColor Green
Write-Host "4. Exit" -ForegroundColor Green
Write-Host ""

$choice = Read-Host "Enter your choice (1-4)"

$python = ".venv\Scripts\python.exe"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Starting Voice to Sign Language Converter..." -ForegroundColor Cyan
        Write-Host "First run will auto-download ~150MB model (one-time only)" -ForegroundColor Yellow
        Write-Host ""
        & $python faster_whisper_demo.py
    }
    "2" {
        Write-Host ""
        $text = Read-Host "Enter text to convert to ASL"
        & $python wlasl_generator.py $text
    }
    "3" {
        Write-Host ""
        Write-Host "Running installation check..." -ForegroundColor Cyan
        & $python verify_setup.py
    }
    "4" {
        Write-Host ""
        Write-Host "Goodbye!" -ForegroundColor Cyan
        exit
    }
    default {
        Write-Host "Invalid choice!" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host ""
Read-Host "Press Enter to exit"
