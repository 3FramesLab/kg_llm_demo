# PowerShell script to run KPI cache fields migration
# Run this script to add the new cache fields to the database

param(
    [string]$Server = "localhost",
    [string]$Database = "newdqschemanov",
    [string]$SqlFile = "scripts/add_kpi_cache_fields.sql"
)

Write-Host "🔧 Running KPI Cache Fields Migration..." -ForegroundColor Cyan
Write-Host "   Server: $Server" -ForegroundColor Gray
Write-Host "   Database: $Database" -ForegroundColor Gray
Write-Host "   SQL File: $SqlFile" -ForegroundColor Gray
Write-Host ""

# Check if SQL file exists
if (-not (Test-Path $SqlFile)) {
    Write-Host "❌ SQL file not found: $SqlFile" -ForegroundColor Red
    exit 1
}

# Try different methods to run the SQL
$methods = @(
    @{Name="sqlcmd"; Command="sqlcmd -S $Server -d $Database -E -i `"$SqlFile`""},
    @{Name="Invoke-Sqlcmd"; Command="Invoke-Sqlcmd -ServerInstance $Server -Database $Database -InputFile `"$SqlFile`""}
)

$success = $false

foreach ($method in $methods) {
    Write-Host "🔍 Trying method: $($method.Name)..." -ForegroundColor Yellow
    
    try {
        if ($method.Name -eq "sqlcmd") {
            # Check if sqlcmd is available
            $null = Get-Command sqlcmd -ErrorAction Stop
            Invoke-Expression $method.Command
            $success = $true
            Write-Host "✅ Migration completed successfully using sqlcmd!" -ForegroundColor Green
            break
        }
        elseif ($method.Name -eq "Invoke-Sqlcmd") {
            # Check if SQL Server PowerShell module is available
            Import-Module SqlServer -ErrorAction Stop
            Invoke-Sqlcmd -ServerInstance $Server -Database $Database -InputFile $SqlFile
            $success = $true
            Write-Host "✅ Migration completed successfully using Invoke-Sqlcmd!" -ForegroundColor Green
            break
        }
    }
    catch {
        Write-Host "   ⚠️ $($method.Name) not available: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

if (-not $success) {
    Write-Host ""
    Write-Host "❌ Could not run migration automatically." -ForegroundColor Red
    Write-Host ""
    Write-Host "📋 Manual Steps:" -ForegroundColor Cyan
    Write-Host "1. Open SQL Server Management Studio (SSMS)" -ForegroundColor White
    Write-Host "2. Connect to server: $Server" -ForegroundColor White
    Write-Host "3. Select database: $Database" -ForegroundColor White
    Write-Host "4. Open and execute the file: $SqlFile" -ForegroundColor White
    Write-Host ""
    Write-Host "📄 Or copy and paste this SQL:" -ForegroundColor Cyan
    Write-Host ""
    Get-Content $SqlFile | Write-Host -ForegroundColor Gray
}
else {
    Write-Host ""
    Write-Host "🎉 Migration completed! The KPI cache features are now ready to use." -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Next Steps:" -ForegroundColor Cyan
    Write-Host "1. Restart your backend server if it's running" -ForegroundColor White
    Write-Host "2. Navigate to the KPI Management page" -ForegroundColor White
    Write-Host "3. Test the new cache toggle buttons (✓ and 🔄)" -ForegroundColor White
    Write-Host "4. Try the clear cache button (💫)" -ForegroundColor White
}

Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
