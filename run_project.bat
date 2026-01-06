@echo off
TITLE Railway Inspection System Launcher

echo ====================================================
echo   RAILWAY WAGON INSPECTION SYSTEM - LAUNCHER
echo ====================================================

:: Set Python Path directly since we know where it is
set PY_CMD="C:\Users\kunjc\AppData\Local\Programs\Python\Python311\python.exe"

echo [INFO] Using Python: %PY_CMD%

:: 1. Check Node.js
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is NOT installed or not in PATH.
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b
)

:: 2. Install Backend Deps
echo.
echo [INFO] Installing Backend Dependencies...
%PY_CMD% -m pip install -r backend/requirements.txt

:: 3. Generate Data (if missing)
if not exist "data\sample_video.mp4" (
    echo.
    echo [INFO] Generating Synthetic Data...
    %PY_CMD% data/sample_generator.py
)

:: 4. Start Servers
echo.
echo [INFO] Starting Backend Server...
start "Backend API" cmd /k "%PY_CMD% -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000"

echo [INFO] Starting Frontend Server...
cd frontend
start "Frontend Dashboard" cmd /k "npm run dev"

echo.
echo ====================================================
echo   SYSTEM RUNNING
echo ====================================================
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Opening Browser in 5 seconds...
timeout /t 5 >nul
start http://localhost:5173
