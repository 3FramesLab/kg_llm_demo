@echo off
echo ================================================
echo   DQ-POC Local Development Starter
echo ================================================
echo.

REM Check if virtual environment exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

echo Installing/Updating dependencies...
pip install -r requirements.txt --quiet
echo.

echo ================================================
echo   Starting Backend Server...
echo ================================================
echo.
echo Backend will run on: http://localhost:8000
echo API Docs available at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.
echo ================================================
echo.

python -m kg_builder.main

pause
