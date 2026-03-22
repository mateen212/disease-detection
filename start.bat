@echo off
REM AI Disease Diagnosis System Startup Script for Windows
REM This script sets up and runs the disease diagnosis system

echo 🏥 AI Disease Diagnosis System Startup
echo ======================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo [INFO] Python found: 
python --version

REM Check if virtual environment exists
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    echo [SUCCESS] Virtual environment created
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat
echo [SUCCESS] Virtual environment activated

REM Install dependencies if needed
if not exist "venv\installed_packages.txt" (
    echo [INFO] Installing Python dependencies...
    pip install -r requirements.txt
    pip freeze > venv\installed_packages.txt
    echo [SUCCESS] Dependencies installed
) else (
    echo [INFO] Dependencies already installed
)

REM Check if .env file exists
if not exist ".env" (
    echo [WARNING] .env file not found
    if exist ".env.example" (
        echo [INFO] Copying .env.example to .env...
        copy .env.example .env
        echo [WARNING] Please edit .env file with your database credentials
        echo [WARNING] Then run this script again
        pause
        exit /b 1
    ) else (
        echo [ERROR] .env.example not found. Please create .env file manually
        pause
        exit /b 1
    )
)

REM Initialize database if --init-db argument is provided
if "%1"=="--init-db" (
    echo [INFO] Initializing database...
    python init_db.py
    if %errorlevel% neq 0 (
        echo [ERROR] Database initialization failed
        pause
        exit /b 1
    )
    echo [SUCCESS] Database initialized successfully
)

REM Start the application
echo [INFO] Starting AI Disease Diagnosis System...
echo.
echo 🌐 Server will be available at:
echo    Main Page:      http://localhost:8000
echo    User Dashboard: http://localhost:8000/static/user/index.html
echo    Admin Panel:    http://localhost:8000/static/admin/index.html
echo    API Docs:       http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

cd backend && python main.py

pause