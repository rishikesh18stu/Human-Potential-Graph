@echo off
REM HUMAN-POTENTIAL-GRAPH Quick Start for Windows

echo.
echo ============================================================
echo   HUMAN-POTENTIAL-GRAPH - Quick Start
echo   Redrob Intelligent Candidate Discovery ^& Ranking
echo ============================================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python not found. Please install Python 3.9 or later.
    exit /b 1
)

echo Checking Python...
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Found Python %PYTHON_VERSION%
echo.

REM Check Flask
echo Checking dependencies...
python -c "import flask" >nul 2>&1
if %errorlevel% equ 0 (
    echo Flask already installed
) else (
    echo Installing Flask...
    pip install -q flask
    echo Flask installed
)
echo.

REM Menu
echo Choose an option:
echo.
echo   1) Web App (recommended)
echo   2) CLI (headless ranking)
echo   3) Try Demo (sample data)
echo   4) Docker (container)
echo.

set /p CHOICE="Enter choice (1-4, default 1): "
if "%CHOICE%"=="" set CHOICE=1

if "%CHOICE%"=="1" (
    echo.
    echo Starting web app...
    echo.
    echo Open your browser to: http://localhost:5000
    echo.
    echo Tip: Click 'Try Sample (50 candidates)' for quick demo
    echo.
    python app.py
) else if "%CHOICE%"=="2" (
    echo.
    set /p INPUT_FILE="Enter path to candidates.jsonl: "
    set /p OUTPUT_FILE="Enter output filename (default: submission.csv): "
    if "%OUTPUT_FILE%"=="" set OUTPUT_FILE=submission.csv
    echo.
    echo Ranking %INPUT_FILE% to %OUTPUT_FILE%...
    python app.py rank "%INPUT_FILE%" "%OUTPUT_FILE%"
    echo.
    echo Done! Output: %OUTPUT_FILE%
) else if "%CHOICE%"=="3" (
    echo.
    echo Starting web app...
    echo Open your browser to: http://localhost:5000
    echo Click: 'Try Sample (50 candidates)'
    echo.
    python app.py
) else if "%CHOICE%"=="4" (
    echo.
    docker --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo Error: Docker not found. Please install Docker Desktop.
        exit /b 1
    )
    echo Building Docker image...
    docker build -t hpg-ranker .
    echo.
    echo Starting container...
    echo Open your browser to: http://localhost:7860
    docker run -p 7860:7860 hpg-ranker
) else (
    echo Invalid choice
    exit /b 1
)
