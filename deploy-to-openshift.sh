#!/bin/bash

# Deploy Knowledge Graph Builder to OpenShift with Enhanced Logging
# This script builds, pushes, and deploys the application with detailed logging enabled

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="cognito-ai-dq-dev"
APP_NAME="kg-builder-backend"
IMAGE_NAME="kg-builder-backend"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  KG Builder OpenShift Deployment${NC}"
echo -e "${BLUE}  With Enhanced Logging${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if logged into OpenShift
echo -e "${YELLOW}1. Checking OpenShift login...${NC}"
if ! oc whoami &> /dev/null; then
    echo -e "${RED}Error: Not logged into OpenShift${NC}"
    echo "Please run: oc login <your-cluster-url>"
    exit 1
fi
echo -e "${GREEN}✓ Logged in as: $(oc whoami)${NC}"
echo ""

# Check if in correct project
echo -e "${YELLOW}2. Switching to project: ${NAMESPACE}${NC}"
oc project ${NAMESPACE} || {
    echo -e "${RED}Error: Could not switch to project ${NAMESPACE}${NC}"
    exit 1
}
echo -e "${GREEN}✓ Using project: ${NAMESPACE}${NC}"
echo ""

# Apply ConfigMaps
echo -e "${YELLOW}3. Applying ConfigMaps...${NC}"
oc apply -f openshift/00-complete-configmap.yaml
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ ConfigMaps applied successfully${NC}"
else
    echo -e "${RED}✗ Failed to apply ConfigMaps${NC}"
    exit 1
fi
echo ""

# Apply Secrets (if they don't exist)
echo -e "${YELLOW}4. Checking secrets...${NC}"
if oc get secret openai-secret &> /dev/null; then
    echo -e "${GREEN}✓ Secret 'openai-secret' already exists${NC}"
else
    echo -e "${YELLOW}  Creating secret 'openai-secret'...${NC}"
    oc apply -f openshift/05-secrets.yaml
fi

if oc get secret mssql-secret &> /dev/null; then
    echo -e "${GREEN}✓ Secret 'mssql-secret' already exists${NC}"
else
    echo -e "${YELLOW}  Creating secret 'mssql-secret'...${NC}"
    oc apply -f openshift/05-secrets.yaml
fi
echo ""

# Start build
echo -e "${YELLOW}5. Starting image build...${NC}"
echo -e "${BLUE}   This will build the Docker image with enhanced logging middleware${NC}"

# Check if BuildConfig exists
if ! oc get bc ${IMAGE_NAME} &> /dev/null; then
    echo -e "${YELLOW}   BuildConfig doesn't exist, creating it...${NC}"
    oc apply -f openshift/04-buildconfigs.yaml
fi

# Start the build
echo -e "${YELLOW}   Starting build from current directory...${NC}"
oc start-build ${IMAGE_NAME} --from-dir=. --follow --wait

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Build completed successfully${NC}"
else
    echo -e "${RED}✗ Build failed${NC}"
    exit 1
fi
echo ""

# Deploy application using enhanced deployment config
echo -e "${YELLOW}6. Deploying application with enhanced logging...${NC}"

# Check which deployment file to use
if [ -f "openshift/01-backend-deployment-enhanced.yaml" ]; then
    DEPLOYMENT_FILE="openshift/01-backend-deployment-enhanced.yaml"
    echo -e "${BLUE}   Using enhanced deployment configuration${NC}"
else
    DEPLOYMENT_FILE="openshift/01-backend-deployment.yaml"
    echo -e "${BLUE}   Using standard deployment configuration${NC}"
fi

oc apply -f ${DEPLOYMENT_FILE}

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Deployment configuration applied${NC}"
else
    echo -e "${RED}✗ Failed to apply deployment${NC}"
    exit 1
fi
echo ""

# Wait for rollout
echo -e "${YELLOW}7. Waiting for rollout to complete...${NC}"
oc rollout status deployment/${APP_NAME} --timeout=5m

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Rollout completed successfully${NC}"
else
    echo -e "${RED}✗ Rollout failed or timed out${NC}"
    echo -e "${YELLOW}   Check pod status with: oc get pods${NC}"
    echo -e "${YELLOW}   View logs with: oc logs -f deployment/${APP_NAME}${NC}"
    exit 1
fi
echo ""

# Get pod status
echo -e "${YELLOW}8. Checking pod status...${NC}"
oc get pods -l app=${APP_NAME}
echo ""

# Get service and route information
echo -e "${YELLOW}9. Service and Route Information:${NC}"
echo -e "${BLUE}   Service:${NC}"
oc get svc ${APP_NAME}-service

if oc get route ${APP_NAME} &> /dev/null; then
    echo -e "${BLUE}   Route:${NC}"
    ROUTE_URL=$(oc get route ${APP_NAME} -o jsonpath='{.spec.host}')
    echo -e "   URL: https://${ROUTE_URL}"
else
    echo -e "${YELLOW}   No route found. Create one if needed.${NC}"
fi
echo ""

# Display logs command
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}To view real-time logs with detailed request/response information:${NC}"
echo -e "${YELLOW}   oc logs -f deployment/${APP_NAME}${NC}"
echo ""
echo -e "${BLUE}To view logs from a specific pod:${NC}"
POD_NAME=$(oc get pods -l app=${APP_NAME} -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
if [ -n "$POD_NAME" ]; then
    echo -e "${YELLOW}   oc logs -f ${POD_NAME}${NC}"
fi
echo ""
echo -e "${BLUE}To check ConfigMap:${NC}"
echo -e "${YELLOW}   oc get configmap kg-builder-app-config -o yaml${NC}"
echo ""
echo -e "${BLUE}To restart deployment (if needed):${NC}"
echo -e "${YELLOW}   oc rollout restart deployment/${APP_NAME}${NC}"
echo ""
echo -e "${BLUE}Enhanced Logging Features Enabled:${NC}"
echo -e "  ✓ Request/Response body logging"
echo -e "  ✓ Request timing and duration"
echo -e "  ✓ Client IP and headers"
echo -e "  ✓ SQL query logging"
echo -e "  ✓ Function-level tracing"
echo -e "  ✓ DEBUG level logging"
echo ""
