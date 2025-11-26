@echo off
REM Quick launcher for Voice-to-Sign-Language Demo
echo ============================================================
echo Voice to Sign Language Converter - Demo Launcher
echo ============================================================
echo.
echo Choose which script to run:
echo.
echo 1. vosk_demo.py      - Record with auto-stop (Recommended)
echo 2. vosk_pipeline.py  - Continuous mode (Ctrl+C to stop)
echo 3. start.py          - Whisper live captions
echo 4. verify_setup.py   - Test installation
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto option1
if "%choice%"=="2" goto option2
if "%choice%"=="3" goto option3
if "%choice%"=="4" goto option4
echo Invalid choice!
goto end

:option1
echo.
echo Starting vosk_demo.py...
echo.
.venv\Scripts\python.exe vosk_demo.py
goto end

:option2
echo.
echo Starting vosk_pipeline.py...
echo.
.venv\Scripts\python.exe vosk_pipeline.py
goto end

:option3
echo.
echo Starting start.py (Whisper)...
echo This will download ~240MB on first run
echo.
.venv\Scripts\python.exe start.py
goto end

:option4
echo.
.venv\Scripts\python.exe verify_setup.py
goto end

:end
echo.
echo.
pause
