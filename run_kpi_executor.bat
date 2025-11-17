@echo off
REM Windows Batch Script for Running KPI Executor
REM Usage: run_kpi_executor.bat

echo ================================================================================
echo                          STANDALONE KPI EXECUTOR
echo ================================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

REM Check if required files exist
if not exist "kpi_executor_standalone.py" (
    echo ERROR: kpi_executor_standalone.py not found
    echo Please ensure the script file is in the current directory
    pause
    exit /b 1
)

if not exist "requirements_standalone.txt" (
    echo ERROR: requirements_standalone.txt not found
    echo Please ensure the requirements file is in the current directory
    pause
    exit /b 1
)

REM Install dependencies if needed
echo Checking Python dependencies...
pip show pyodbc >nul 2>&1
if errorlevel 1 (
    echo Installing Python dependencies...
    pip install -r requirements_standalone.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo Dependencies OK
echo.

REM Set default values (modify these as needed)
set DEFAULT_KG_NAME=default
set DEFAULT_DB_HOST=localhost
set DEFAULT_DB_PORT=1433
set DEFAULT_DB_NAME=KPI_Analytics
set DEFAULT_SCHEMA=newdqschemanov
set DEFAULT_LIMIT=1000
set DEFAULT_TEMPERATURE=0.0
set DEFAULT_KPI_ID=19

REM Prompt for required parameters
echo Please provide the following required parameters:
echo.

set /p OPENAI_KEY="OpenAI API Key: "
if "%OPENAI_KEY%"=="" (
    echo ERROR: OpenAI API Key is required
    pause
    exit /b 1
)

set /p DB_USER="Database Username: "
if "%DB_USER%"=="" (
    echo ERROR: Database Username is required
    pause
    exit /b 1
)

set /p DB_PASSWORD="Database Password: "
if "%DB_PASSWORD%"=="" (
    echo ERROR: Database Password is required
    pause
    exit /b 1
)

echo.
echo Optional parameters (press Enter for defaults):
echo.

set /p KG_NAME="KG Name [%DEFAULT_KG_NAME%]: "
if "%KG_NAME%"=="" set KG_NAME=%DEFAULT_KG_NAME%

set /p DB_HOST="Database Host [%DEFAULT_DB_HOST%]: "
if "%DB_HOST%"=="" set DB_HOST=%DEFAULT_DB_HOST%

set /p DB_PORT="Database Port [%DEFAULT_DB_PORT%]: "
if "%DB_PORT%"=="" set DB_PORT=%DEFAULT_DB_PORT%

set /p DB_NAME="Database Name [%DEFAULT_DB_NAME%]: "
if "%DB_NAME%"=="" set DB_NAME=%DEFAULT_DB_NAME%

set /p KPI_ID="KPI ID [%DEFAULT_KPI_ID%]: "
if "%KPI_ID%"=="" set KPI_ID=%DEFAULT_KPI_ID%

set /p SCHEMA="Select Schema [%DEFAULT_SCHEMA%]: "
if "%SCHEMA%"=="" set SCHEMA=%DEFAULT_SCHEMA%

set /p LIMIT="Limit Records [%DEFAULT_LIMIT%]: "
if "%LIMIT%"=="" set LIMIT=%DEFAULT_LIMIT%

set /p TEMPERATURE="Temperature [%DEFAULT_TEMPERATURE%]: "
if "%TEMPERATURE%"=="" set TEMPERATURE=%DEFAULT_TEMPERATURE%

set /p OUTPUT_FILE="Output File (optional): "

set /p VERBOSE="Verbose logging? (y/N): "

echo.
echo ================================================================================
echo                              EXECUTION SUMMARY
echo ================================================================================
echo KPI ID: %KPI_ID%
echo KG Name: %KG_NAME%
echo Database: %DB_HOST%:%DB_PORT%/%DB_NAME%
echo Schema: %SCHEMA%
echo Limit: %LIMIT%
echo Temperature: %TEMPERATURE%
if not "%OUTPUT_FILE%"=="" echo Output File: %OUTPUT_FILE%
echo ================================================================================
echo.

set /p CONFIRM="Proceed with execution? (Y/n): "
if /i "%CONFIRM%"=="n" (
    echo Execution cancelled
    pause
    exit /b 0
)

REM Build command
set CMD=python kpi_executor_standalone.py --openai-key "%OPENAI_KEY%" --kg-name "%KG_NAME%" --db-host "%DB_HOST%" --db-port %DB_PORT% --db-name "%DB_NAME%" --db-user "%DB_USER%" --db-password "%DB_PASSWORD%" --kpi-id %KPI_ID% --select-schema "%SCHEMA%" --limit-records %LIMIT% --temperature %TEMPERATURE%

if not "%OUTPUT_FILE%"=="" set CMD=%CMD% --output-file "%OUTPUT_FILE%"
if /i "%VERBOSE%"=="y" set CMD=%CMD% --verbose

echo.
echo Executing KPI...
echo.

REM Execute the command
%CMD%

echo.
echo ================================================================================
echo Execution completed. Check the output above for results.
echo ================================================================================
pause
