# Voice to Sign Language with 3D Avatar - PowerShell Launcher
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Voice to Sign Language - 3D Avatar Edition" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting GUI application..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Features:" -ForegroundColor Green
Write-Host " - Visual interface (no terminal needed)" -ForegroundColor White
Write-Host " - Record voice with one click" -ForegroundColor White
Write-Host " - Real-time progress display" -ForegroundColor White
Write-Host " - Blue futuristic 3D avatar" -ForegroundColor White
Write-Host " - Export avatar videos" -ForegroundColor White
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

& ".venv\Scripts\python.exe" gui_app.py

Write-Host ""
Write-Host ""
Read-Host "Press Enter to exit"
