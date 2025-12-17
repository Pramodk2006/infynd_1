@echo off
echo ============================================================
echo B2B Data Fusion Engine - Startup Script
echo ============================================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo Please run: python -m venv venv
    echo Then: venv\Scripts\activate
    echo Then: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Check if node_modules exists
if not exist "frontend\node_modules" (
    echo [ERROR] Frontend dependencies not installed!
    echo Please run: cd frontend
    echo Then: npm install
    pause
    exit /b 1
)

echo [1/2] Starting Flask API Server...
echo.
start "Backend API" cmd /k "venv\Scripts\activate && python api_server.py"

timeout /t 3 /nobreak > nul

echo [2/2] Starting React Frontend...
echo.
start "Frontend Dev Server" cmd /k "cd frontend && npm start"

echo.
echo ============================================================
echo ✅ Both servers are starting!
echo ============================================================
echo.
echo Backend API:  http://localhost:5000
echo Frontend App: http://localhost:3000 (opens automatically)
echo.
echo Two new command windows have opened.
echo Close those windows to stop the servers.
echo.
echo ============================================================
pause
