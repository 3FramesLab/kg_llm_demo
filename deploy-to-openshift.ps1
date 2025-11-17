# Deploy Knowledge Graph Builder to OpenShift with Enhanced Logging
# PowerShell version for Windows

param(
    [string]$Namespace = "cognito-ai-dq-dev",
    [string]$AppName = "kg-builder-backend",
    [string]$ImageName = "kg-builder-backend"
)

# Colors
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Header {
    param([string]$Text)
    Write-ColorOutput "========================================" "Blue"
    Write-ColorOutput "  $Text" "Blue"
    Write-ColorOutput "========================================" "Blue"
    Write-Host ""
}

function Write-Step {
    param([string]$Text)
    Write-ColorOutput $Text "Yellow"
}

function Write-Success {
    param([string]$Text)
    Write-ColorOutput "✓ $Text" "Green"
}

function Write-Error-Message {
    param([string]$Text)
    Write-ColorOutput "✗ $Text" "Red"
}

function Write-Info {
    param([string]$Text)
    Write-ColorOutput $Text "Cyan"
}

# Start deployment
Write-Header "KG Builder OpenShift Deployment`nWith Enhanced Logging"

# Check if logged into OpenShift
Write-Step "1. Checking OpenShift login..."
try {
    $user = oc whoami 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Message "Not logged into OpenShift"
        Write-Host "Please run: oc login <your-cluster-url>"
        exit 1
    }
    Write-Success "Logged in as: $user"
    Write-Host ""
} catch {
    Write-Error-Message "Error checking OpenShift login"
    exit 1
}

# Switch to project
Write-Step "2. Switching to project: $Namespace"
oc project $Namespace 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Error-Message "Could not switch to project $Namespace"
    exit 1
}
Write-Success "Using project: $Namespace"
Write-Host ""

# Apply ConfigMaps
Write-Step "3. Applying ConfigMaps..."
oc apply -f openshift/00-complete-configmap.yaml
if ($LASTEXITCODE -eq 0) {
    Write-Success "ConfigMaps applied successfully"
} else {
    Write-Error-Message "Failed to apply ConfigMaps"
    exit 1
}
Write-Host ""

# Check secrets
Write-Step "4. Checking secrets..."
oc get secret openai-secret 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Success "Secret 'openai-secret' already exists"
} else {
    Write-Info "  Creating secret 'openai-secret'..."
    oc apply -f openshift/05-secrets.yaml
}

oc get secret mssql-secret 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Success "Secret 'mssql-secret' already exists"
} else {
    Write-Info "  Creating secret 'mssql-secret'..."
    oc apply -f openshift/05-secrets.yaml
}
Write-Host ""

# Start build
Write-Step "5. Starting image build..."
Write-Info "   This will build the Docker image with enhanced logging middleware"

# Check if BuildConfig exists
oc get bc $ImageName 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Info "   BuildConfig doesn't exist, creating it..."
    oc apply -f openshift/04-buildconfigs.yaml
}

# Start the build
Write-Info "   Starting build from current directory..."
oc start-build $ImageName --from-dir=. --follow --wait

if ($LASTEXITCODE -eq 0) {
    Write-Success "Build completed successfully"
} else {
    Write-Error-Message "Build failed"
    exit 1
}
Write-Host ""

# Deploy application
Write-Step "6. Deploying application with enhanced logging..."

# Check which deployment file to use
$deploymentFile = "openshift/01-backend-deployment.yaml"
if (Test-Path "openshift/01-backend-deployment-enhanced.yaml") {
    $deploymentFile = "openshift/01-backend-deployment-enhanced.yaml"
    Write-Info "   Using enhanced deployment configuration"
} else {
    Write-Info "   Using standard deployment configuration"
}

oc apply -f $deploymentFile

if ($LASTEXITCODE -eq 0) {
    Write-Success "Deployment configuration applied"
} else {
    Write-Error-Message "Failed to apply deployment"
    exit 1
}
Write-Host ""

# Wait for rollout
Write-Step "7. Waiting for rollout to complete..."
oc rollout status deployment/$AppName --timeout=5m

if ($LASTEXITCODE -eq 0) {
    Write-Success "Rollout completed successfully"
} else {
    Write-Error-Message "Rollout failed or timed out"
    Write-Info "   Check pod status with: oc get pods"
    Write-Info "   View logs with: oc logs -f deployment/$AppName"
    exit 1
}
Write-Host ""

# Get pod status
Write-Step "8. Checking pod status..."
oc get pods -l app=$AppName
Write-Host ""

# Get service and route information
Write-Step "9. Service and Route Information:"
Write-Info "   Service:"
oc get svc "$AppName-service"

oc get route $AppName 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Info "   Route:"
    $routeUrl = oc get route $AppName -o jsonpath='{.spec.host}'
    Write-Host "   URL: https://$routeUrl"
} else {
    Write-Info "   No route found. Create one if needed."
}
Write-Host ""

# Display logs command
Write-Header "Deployment Complete!"
Write-Host ""
Write-Info "To view real-time logs with detailed request/response information:"
Write-ColorOutput "   oc logs -f deployment/$AppName" "Yellow"
Write-Host ""
Write-Info "To view logs from a specific pod:"
$podName = oc get pods -l app=$AppName -o jsonpath='{.items[0].metadata.name}' 2>&1
if ($podName) {
    Write-ColorOutput "   oc logs -f $podName" "Yellow"
}
Write-Host ""
Write-Info "To check ConfigMap:"
Write-ColorOutput "   oc get configmap kg-builder-app-config -o yaml" "Yellow"
Write-Host ""
Write-Info "To restart deployment (if needed):"
Write-ColorOutput "   oc rollout restart deployment/$AppName" "Yellow"
Write-Host ""
Write-Info "Enhanced Logging Features Enabled:"
Write-Host "  ✓ Request/Response body logging"
Write-Host "  ✓ Request timing and duration"
Write-Host "  ✓ Client IP and headers"
Write-Host "  ✓ SQL query logging"
Write-Host "  ✓ Function-level tracing"
Write-Host "  ✓ DEBUG level logging"
Write-Host ""
