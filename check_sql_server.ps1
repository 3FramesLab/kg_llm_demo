# SQL Server Diagnostic Script
Write-Host "=== SQL Server Diagnostic Check ===" -ForegroundColor Cyan
Write-Host ""

# Check if SQL Server services are running
Write-Host "1. Checking SQL Server Services..." -ForegroundColor Yellow
$sqlServices = Get-Service | Where-Object { $_.DisplayName -like "*SQL Server*" }

if ($sqlServices) {
    foreach ($service in $sqlServices) {
        $status = if ($service.Status -eq "Running") { "[OK]" } else { "[X]" }
        $color = if ($service.Status -eq "Running") { "Green" } else { "Red" }
        Write-Host "   $status $($service.DisplayName): $($service.Status)" -ForegroundColor $color
    }
} else {
    Write-Host "   [X] No SQL Server services found!" -ForegroundColor Red
    Write-Host "   SQL Server may not be installed on this machine." -ForegroundColor Yellow
}

Write-Host ""

# Check if port 1433 is listening
Write-Host "2. Checking if port 1433 is listening..." -ForegroundColor Yellow
$port1433 = Get-NetTCPConnection -LocalPort 1433 -ErrorAction SilentlyContinue

if ($port1433) {
    Write-Host "   [OK] Port 1433 is LISTENING" -ForegroundColor Green
    Write-Host "   Process: $($port1433.OwningProcess)" -ForegroundColor Gray
} else {
    Write-Host "   [X] Port 1433 is NOT listening" -ForegroundColor Red
    Write-Host "   SQL Server may not be configured for TCP/IP connections." -ForegroundColor Yellow
}

Write-Host ""

# Check all SQL Server listening ports
Write-Host "3. Finding all SQL Server listening ports..." -ForegroundColor Yellow
$allSqlPorts = Get-NetTCPConnection | Where-Object { 
    $_.State -eq "Listen" -and $_.LocalPort -gt 1024 
} | ForEach-Object {
    $processId = $_.OwningProcess
    $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
    if ($process -and $process.ProcessName -like "*sql*") {
        [PSCustomObject]@{
            Port = $_.LocalPort
            Process = $process.ProcessName
            ProcessId = $processId
        }
    }
} | Sort-Object Port -Unique

if ($allSqlPorts) {
    Write-Host "   Found SQL Server listening on these ports:" -ForegroundColor Green
    foreach ($portInfo in $allSqlPorts) {
        Write-Host "   [OK] Port $($portInfo.Port) - $($portInfo.Process) (PID: $($portInfo.ProcessId))" -ForegroundColor Green
    }
} else {
    Write-Host "   [X] No SQL Server processes found listening on any port" -ForegroundColor Red
}

Write-Host ""

# Test connection to localhost:1433
Write-Host "4. Testing TCP connection to localhost:1433..." -ForegroundColor Yellow
try {
    $tcpClient = New-Object System.Net.Sockets.TcpClient
    $tcpClient.Connect("localhost", 1433)
    $tcpClient.Close()
    Write-Host "   [OK] Successfully connected to localhost:1433" -ForegroundColor Green
} catch {
    Write-Host "   [X] Cannot connect to localhost:1433" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "=== Recommendations ===" -ForegroundColor Cyan

if (-not $sqlServices -or ($sqlServices | Where-Object { $_.Status -ne "Running" })) {
    Write-Host "• Start SQL Server service using SQL Server Configuration Manager" -ForegroundColor Yellow
}

if (-not $port1433) {
    Write-Host "• Enable TCP/IP protocol in SQL Server Configuration Manager" -ForegroundColor Yellow
    Write-Host "• Set TCP/IP port to 1433 in SQL Server Configuration Manager" -ForegroundColor Yellow
    Write-Host "• Restart SQL Server service after making changes" -ForegroundColor Yellow
}

if ($allSqlPorts -and -not $port1433) {
    Write-Host "• SQL Server is running on a different port. Update your connection to use:" -ForegroundColor Yellow
    foreach ($portInfo in $allSqlPorts | Select-Object -First 1) {
        Write-Host "  Port: $($portInfo.Port)" -ForegroundColor Cyan
    }
}

Write-Host ""

