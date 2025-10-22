@echo off
echo ================================================
echo   DQ-POC Web App Starter
echo ================================================
echo.

REM Check if node_modules exists
if not exist node_modules (
    echo Installing dependencies...
    call npm install
    echo.
)

echo ================================================
echo   Starting Frontend Development Server...
echo ================================================
echo.
echo Web App will run on: http://localhost:3000
echo.
echo Browser will open automatically
echo Press Ctrl+C to stop the server
echo.
echo ================================================
echo.

call npm start

pause
