@echo off
REM Voice to Sign Language Converter - Faster-Whisper Edition
echo ============================================================
echo Voice to Sign Language Converter (Faster-Whisper)
echo ============================================================
echo.
echo Choose your option:
echo.
echo 1. Start Voice to ASL Converter (RECOMMENDED) ⭐
echo 2. Test WLASL Video Generator
echo 3. Verify Installation
echo 4. Exit
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto option1
if "%choice%"=="2" goto option2
if "%choice%"=="3" goto option3
if "%choice%"=="4" goto exit
echo Invalid choice!
goto end

:option1
echo.
echo Starting Voice to Sign Language Converter...
echo First run will auto-download ~150MB model (one-time only)
echo.
.venv\Scripts\python.exe faster_whisper_demo.py
goto end

:option2
echo.
echo Testing WLASL video generator...
set /p "text=Enter text to convert to ASL: "
.venv\Scripts\python.exe wlasl_generator.py %text%
goto end

:option3
echo.
echo Running installation check...
.venv\Scripts\python.exe verify_setup.py
goto end

:exit
echo.
echo Goodbye!
exit /b

:end
echo.
echo.
pause
