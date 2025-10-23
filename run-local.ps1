# PowerShell script to run application locally (without Docker)
# This is a fallback if Docker networking issues persist

Write-Host "=== Running Application Locally ===" -ForegroundColor Green

# Check Python
Write-Host "`nChecking Python..." -ForegroundColor Yellow
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python not found. Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

# Check Node.js
Write-Host "`nChecking Node.js..." -ForegroundColor Yellow
node --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Node.js not found. Please install Node.js 18+" -ForegroundColor Red
    exit 1
}

# Update .env for local mode
Write-Host "`nConfiguring .env for local mode..." -ForegroundColor Yellow
$envContent = Get-Content .env -Raw
$envContent = $envContent -replace 'FALKORDB_HOST=falkordb', 'FALKORDB_HOST=localhost'
$envContent = $envContent -replace 'SOURCE_DB_HOST=host.docker.internal', 'SOURCE_DB_HOST=localhost'
$envContent = $envContent -replace 'TARGET_DB_HOST=host.docker.internal', 'TARGET_DB_HOST=localhost'
$envContent = $envContent -replace 'JDBC_DRIVERS_PATH=/app/jdbc_drivers', 'JDBC_DRIVERS_PATH=D:\\learning\\dq-poc\\jdbc_drivers'
Set-Content .env $envContent

Write-Host "`n=== Starting Services ===" -ForegroundColor Green

# Start backend
Write-Host "`nStarting Backend API on http://localhost:8000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; python -m uvicorn kg_builder.main:app --host 0.0.0.0 --port 8000 --reload"

Start-Sleep -Seconds 3

# Start frontend
Write-Host "Starting Frontend on http://localhost:3000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\web-app'; npm start"

Write-Host "`n=== Services Started ===" -ForegroundColor Green
Write-Host "Backend: http://localhost:8000/docs"
Write-Host "Frontend: http://localhost:3000"
Write-Host "`nNote: You need FalkorDB and MongoDB running separately"
Write-Host "Press Ctrl+C in each PowerShell window to stop services"
