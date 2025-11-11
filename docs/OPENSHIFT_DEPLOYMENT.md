# OpenShift Deployment Guide for Knowledge Graph Builder

This guide explains how to deploy the Knowledge Graph Builder application on OpenShift.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Deployment Methods](#deployment-methods)
- [Configuration](#configuration)
- [Accessing the Application](#accessing-the-application)
- [Troubleshooting](#troubleshooting)
- [Advanced Configuration](#advanced-configuration)

## Prerequisites

1. **OpenShift CLI (oc)**: Install from [OpenShift CLI Downloads](https://docs.openshift.com/container-platform/latest/cli_reference/openshift_cli/getting-started-cli.html)
2. **Access to OpenShift cluster**: Login credentials
3. **OpenAI API Key**: Required for LLM features

## Quick Start

### 1. Login to OpenShift

```bash
oc login https://your-openshift-cluster:6443 --token=your-token
```

### 2. Create a New Project

```bash
oc new-project kg-builder
```

### 3. Deploy Using Template

```bash
# Process and apply the template with your OpenAI API key
oc process -f openshift-template.yaml \
  -p OPENAI_API_KEY=sk-your-key-here \
  -p NAMESPACE=kg-builder \
  | oc apply -f -
```

### 4. Start Build (if using BuildConfig)

```bash
# Trigger a build from your Git repository
oc start-build kg-builder

# Or build from local directory
oc start-build kg-builder --from-dir=.
```

### 5. Check Deployment Status

```bash
# Watch the build progress
oc logs -f bc/kg-builder

# Check pod status
oc get pods

# Check deployment
oc get dc
```

### 6. Get Application URL

```bash
oc get route kg-builder
```

## Deployment Methods

### Method 1: Using OpenShift Template (Recommended)

The template includes all necessary resources (BuildConfig, DeploymentConfig, Services, Routes, etc.)

```bash
# With custom parameters
oc process -f openshift-template.yaml \
  -p APPLICATION_NAME=kg-builder \
  -p NAMESPACE=kg-builder \
  -p OPENAI_API_KEY=sk-your-key \
  -p SOURCE_REPOSITORY_URL=https://github.com/your-org/dq-poc.git \
  -p SOURCE_REPOSITORY_REF=master \
  -p REPLICAS=2 \
  -p MEMORY_LIMIT=1Gi \
  -p CPU_LIMIT=1000m \
  | oc apply -f -
```

### Method 2: Using Pre-built Docker Image

If you've already built the image:

```bash
# Tag and push to OpenShift internal registry
docker tag kg-builder:latest default-route-openshift-image-registry/kg-builder/kg-builder:latest
docker push default-route-openshift-image-registry/kg-builder/kg-builder:latest

# Deploy using the image
oc new-app kg-builder:latest
oc expose svc/kg-builder
```

### Method 3: Direct Build from Dockerfile

```bash
# Create app from current directory
oc new-app . --name=kg-builder

# Or from Git repository
oc new-app https://github.com/your-org/dq-poc.git --name=kg-builder

# Expose the service
oc expose svc/kg-builder
```

## Configuration

### Environment Variables

The application uses ConfigMap and Secrets for configuration:

#### ConfigMap (kg-builder-config)
- `LOG_LEVEL`: Logging level (default: INFO)
- `FALKORDB_HOST`: FalkorDB host (default: falkordb-service)
- `FALKORDB_PORT`: FalkorDB port (default: 6379)
- `OPENAI_MODEL`: OpenAI model to use (default: gpt-3.5-turbo)
- `OPENAI_TEMPERATURE`: Temperature for LLM (default: 0.7)
- `OPENAI_MAX_TOKENS`: Max tokens for LLM responses (default: 2000)
- `ENABLE_LLM_EXTRACTION`: Enable LLM extraction (default: true)
- `ENABLE_LLM_ANALYSIS`: Enable LLM analysis (default: true)

#### Secret (kg-builder-secrets)
- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `FALKORDB_PASSWORD`: FalkorDB password (optional)

### Updating Configuration

```bash
# Edit ConfigMap
oc edit configmap kg-builder-config

# Edit Secret
oc edit secret kg-builder-secrets

# Trigger redeployment after changes
oc rollout latest dc/kg-builder-app
```

## Accessing the Application

### Get the Route URL

```bash
# Get route information
oc get route kg-builder -o jsonpath='{.spec.host}'

# Full route details
oc describe route kg-builder
```

### Test the Application

```bash
# Health check
curl https://$(oc get route kg-builder -o jsonpath='{.spec.host}')/health

# API docs
curl https://$(oc get route kg-builder -o jsonpath='{.spec.host}')/docs
```

## Troubleshooting

### Check Pod Logs

```bash
# Get pod name
oc get pods -l app=kg-builder

# View logs
oc logs -f <pod-name>

# View previous logs if pod crashed
oc logs --previous <pod-name>
```

### Check Pod Status

```bash
# Detailed pod information
oc describe pod <pod-name>

# Get events
oc get events --sort-by='.lastTimestamp'
```

### Debug Pod Issues

```bash
# Open shell in running pod
oc rsh <pod-name>

# Check file permissions
oc rsh <pod-name> ls -la /app

# Check running user
oc rsh <pod-name> id
```

### Common Issues

#### 1. Permission Denied Errors

The Dockerfile is configured for OpenShift's security model:
- Runs as arbitrary UID with root group (GID 0)
- Directories are group-writable
- Uses `chmod g=u` for proper permissions

If you still see permission errors:
```bash
# Check security context
oc get pod <pod-name> -o yaml | grep -A 10 securityContext

# Verify directory permissions in container
oc rsh <pod-name> ls -la /app/data /app/logs
```

#### 2. Build Failures

```bash
# View build logs
oc logs -f bc/kg-builder

# Check build status
oc get builds

# Retry failed build
oc start-build kg-builder --follow
```

#### 3. ImagePullBackOff

```bash
# Check image stream
oc get imagestream kg-builder

# Describe image stream for details
oc describe imagestream kg-builder
```

#### 4. CrashLoopBackOff

Usually indicates application errors:
```bash
# Check logs
oc logs <pod-name>

# Check environment variables
oc set env dc/kg-builder-app --list

# Verify ConfigMap and Secrets
oc get configmap kg-builder-config -o yaml
oc get secret kg-builder-secrets -o yaml
```

## Advanced Configuration

### Scaling

```bash
# Manual scaling
oc scale dc/kg-builder-app --replicas=3

# Auto-scaling (HPA is already configured in template)
oc get hpa kg-builder-hpa

# Edit HPA settings
oc edit hpa kg-builder-hpa
```

### Resource Limits

```bash
# View current resource limits
oc get dc/kg-builder-app -o yaml | grep -A 10 resources

# Update resource limits
oc set resources dc/kg-builder-app \
  --limits=cpu=2,memory=2Gi \
  --requests=cpu=500m,memory=512Mi
```

### Persistent Storage

To add persistent storage for data:

```bash
# Create PVC
oc create -f - <<EOF
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: kg-builder-data
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
EOF

# Add volume to deployment
oc set volume dc/kg-builder-app \
  --add --name=data-volume \
  --type=persistentVolumeClaim \
  --claim-name=kg-builder-data \
  --mount-path=/app/data
```

### Custom Domain

```bash
# Update route with custom domain
oc patch route kg-builder -p \
  '{"spec":{"host":"kg-builder.yourdomain.com"}}'
```

### HTTPS/TLS

The Route is configured with edge TLS termination by default. To use custom certificates:

```bash
# Create TLS secret
oc create secret tls kg-builder-tls \
  --cert=path/to/cert.crt \
  --key=path/to/key.key

# Update route to use the secret
oc patch route kg-builder -p \
  '{"spec":{"tls":{"certificate":"$(cat cert.crt)","key":"$(cat key.key)"}}}'
```

## Monitoring and Health Checks

### Health Endpoints

- **Liveness**: `GET /health` - Returns 200 if application is running
- **Readiness**: `GET /health` - Returns 200 if application is ready to serve traffic

### View Metrics

```bash
# CPU and memory usage
oc adm top pods -l app=kg-builder

# Node usage
oc adm top nodes
```

## Cleanup

To remove all resources:

```bash
# Delete all resources in the project
oc delete all -l app=kg-builder

# Or delete the entire project
oc delete project kg-builder
```

## Security Considerations

1. **Non-root User**: Application runs as UID 1001 (or arbitrary UID assigned by OpenShift)
2. **Security Context**: Configured with `allowPrivilegeEscalation: false` and drops all capabilities
3. **Network Policies**: Consider adding NetworkPolicy for production environments
4. **Secrets Management**: Store sensitive data in Secrets, not ConfigMaps
5. **TLS**: Route uses edge TLS termination by default

## Additional Resources

- [OpenShift Documentation](https://docs.openshift.com/)
- [OpenShift Container Platform](https://docs.openshift.com/container-platform/latest/welcome/index.html)
- [Building Images](https://docs.openshift.com/container-platform/latest/cicd/builds/understanding-image-builds.html)
- [Security Context Constraints](https://docs.openshift.com/container-platform/latest/authentication/managing-security-context-constraints.html)
