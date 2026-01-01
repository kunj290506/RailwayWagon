@echo off
echo Starting AI Railway Inspection System (GPU Powered)...

start "Backend Server" cmd /k "cd backend && (if exist ..\.venv\Scripts\activate.bat (call ..\.venv\Scripts\activate.bat) else (call venv\Scripts\activate.bat)) && uvicorn main:app --reload"
timeout /t 5 >nul
start "Frontend Dashboard" cmd /k "cd frontend && npm run dev"

echo System started!
echo Frontend: http://localhost:5174
pause
