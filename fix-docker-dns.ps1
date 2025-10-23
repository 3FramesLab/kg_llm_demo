# PowerShell script to fix Docker DNS issues
# Run as Administrator

Write-Host "=== Docker DNS Fix Script ===" -ForegroundColor Green

# Step 1: Flush DNS Cache
Write-Host "`n1. Flushing DNS cache..." -ForegroundColor Yellow
ipconfig /flushdns

# Step 2: Reset network adapter
Write-Host "`n2. Resetting network adapter..." -ForegroundColor Yellow
ipconfig /release
ipconfig /renew

# Step 3: Test DNS resolution
Write-Host "`n3. Testing DNS resolution..." -ForegroundColor Yellow
Write-Host "Testing Google DNS..."
nslookup google.com 8.8.8.8

Write-Host "`nTesting Docker Hub..."
nslookup hub.docker.com

# Step 4: Check Docker status
Write-Host "`n4. Checking Docker status..." -ForegroundColor Yellow
docker version

Write-Host "`n=== Next Steps ===" -ForegroundColor Green
Write-Host "1. Restart Docker Desktop from system tray"
Write-Host "2. Go to Docker Desktop > Settings > Docker Engine"
Write-Host "3. Add this configuration:"
Write-Host @"
{
  "dns": ["8.8.8.8", "8.8.4.4", "1.1.1.1"],
  "registry-mirrors": ["https://mirror.gcr.io"]
}
"@ -ForegroundColor Cyan
Write-Host "`n4. Click 'Apply & Restart'"
Write-Host "`n5. Try: docker-compose build"

Write-Host "`nPress any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
