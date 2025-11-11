@echo off
REM DQ-POC Environment Setup Script for Windows
REM Quick setup for different environments

echo.
echo ========================================
echo   DQ-POC Environment Setup
echo ========================================
echo.

if "%1"=="" (
    echo Usage: setup-env.bat [development^|docker^|production]
    echo.
    echo Examples:
    echo   setup-env.bat development    - Setup for local development
    echo   setup-env.bat docker         - Setup for Docker deployment
    echo   setup-env.bat production     - Setup for production deployment
    echo.
    goto :end
)

echo Setting up %1 environment...
echo.

REM Run the Python setup script
python scripts\setup-environment.py %1

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   Environment Setup Complete!
    echo ========================================
    echo.
    echo Next steps:
    echo 1. Review and customize .env file
    echo 2. Update database credentials
    echo 3. Set OpenAI API key if needed
    echo 4. Run: setup-env.bat validate
    echo.
) else (
    echo.
    echo ========================================
    echo   Environment Setup Failed!
    echo ========================================
    echo.
    echo Please check the error messages above.
    echo.
)

:end
pause
