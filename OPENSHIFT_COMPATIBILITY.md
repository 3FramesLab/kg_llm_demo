# OpenShift Compatibility Summary

This document explains the changes made to ensure the Docker container works seamlessly with OpenShift.

## Key OpenShift Requirements

OpenShift has stricter security requirements compared to standard Kubernetes:

1. **Arbitrary User IDs**: Containers run with random UIDs assigned by OpenShift
2. **Root Group (GID 0)**: All containers run with the root group (GID 0)
3. **Non-root Users**: Containers must not run as root
4. **Security Context Constraints (SCCs)**: Enforce security policies

## Dockerfile Changes

### Before (Standard Docker)
```dockerfile
# Create user with specific UID
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Copy with user ownership
COPY --chown=appuser:appuser . .

# Simple permissions
RUN chown -R appuser:appuser /app

USER appuser
```

### After (OpenShift-Compatible)
```dockerfile
# Create user with root group (GID 0)
RUN useradd -m -u 1001 -g 0 appuser && \
    chown -R appuser:0 /app

# Copy with group ownership set to root group
COPY --chown=appuser:0 . .

# Set group permissions to match user permissions
RUN mkdir -p \
    /app/data/reconciliation_rules \
    /app/data/graphiti_storage \
    /app/logs \
    && chown -R appuser:0 /app \
    && chmod -R g=u /app \
    && chmod -R g+w /app/data /app/logs

# Use numeric UID instead of username
USER 1001
```

## Key Changes Explained

### 1. Group Ownership (GID 0)
```dockerfile
# Old: -u 1000
# New: -u 1001 -g 0
RUN useradd -m -u 1001 -g 0 appuser
```
**Why**: OpenShift assigns random UIDs but always uses root group (GID 0). Setting `-g 0` ensures files are accessible.

### 2. Group Permissions (`chmod g=u`)
```dockerfile
chmod -R g=u /app
```
**Why**: This gives the root group (GID 0) the same permissions as the user, allowing OpenShift's random UID to access files.

### 3. Group-Writable Directories
```dockerfile
chmod -R g+w /app/data /app/logs
```
**Why**: Runtime directories need write access for the root group, regardless of the assigned UID.

### 4. Numeric User ID
```dockerfile
# Old: USER appuser
# New: USER 1001
USER 1001
```
**Why**: Using numeric UIDs is more explicit and works better with OpenShift's UID assignment.

### 5. Ownership with Root Group
```dockerfile
# Old: --chown=appuser:appuser
# New: --chown=appuser:0
COPY --chown=appuser:0 . .
```
**Why**: Files must be owned by root group (0) to be accessible by OpenShift's assigned UID.

## OpenShift Template vs Kubernetes Deployment

| Aspect | Kubernetes (k8s-deployment.yaml) | OpenShift (openshift-template.yaml) |
|--------|----------------------------------|-------------------------------------|
| **Deployment Resource** | `Deployment` | `DeploymentConfig` |
| **Routing** | `Ingress` | `Route` |
| **Image Building** | External (CI/CD) | `BuildConfig` (built-in) |
| **Image Storage** | External registry | `ImageStream` |
| **Security Context** | Optional | Required with SCCs |
| **User/Group** | Specified in Pod | Assigned by OpenShift |
| **TLS** | Ingress Controller | Route with edge termination |

## Security Context Configuration

### Standard Kubernetes
```yaml
securityContext:
  runAsUser: 1000
  runAsGroup: 1000
  fsGroup: 1000
```

### OpenShift
```yaml
securityContext:
  # OpenShift assigns UID automatically
  fsGroup: 0  # Root group
  allowPrivilegeEscalation: false
  runAsNonRoot: true
  capabilities:
    drop:
      - ALL
```

## Testing OpenShift Compatibility

### 1. Verify User and Group
```bash
# Shell into running container
oc rsh <pod-name>

# Check current user
id
# Expected output: uid=1000630000(random) gid=0(root) groups=0(root)
```

### 2. Verify Permissions
```bash
# Check directory permissions
ls -la /app
# Should show: drwxrwxr-x ... user root

ls -la /app/data
# Should show: drwxrwxrwx ... user root

# Test write access
touch /app/data/test.txt
echo "test" > /app/logs/test.log
```

### 3. Verify No Root Process
```bash
# Check processes
ps aux | grep -v grep
# Should not show any process running as root (UID 0)
```

## Common OpenShift Errors and Solutions

### Error: "Permission Denied" on /app/data
**Cause**: Directory not group-writable

**Solution**: Add to Dockerfile:
```dockerfile
RUN chmod -R g+w /app/data /app/logs
```

### Error: "container has runAsNonRoot and image will run as root"
**Cause**: USER directive not set or set to 0

**Solution**: Ensure Dockerfile has:
```dockerfile
USER 1001
```

### Error: Files not accessible by container user
**Cause**: Files owned by specific UID/GID, not root group

**Solution**: Change ownership:
```dockerfile
RUN chown -R appuser:0 /app && chmod -R g=u /app
```

### Error: "Unable to write to directory"
**Cause**: Missing group write permissions

**Solution**: Set proper permissions:
```dockerfile
RUN chmod -R g=u /app && chmod -R g+w /app/data
```

## Verification Checklist

- [x] Dockerfile uses root group (GID 0) for all files
- [x] Directories use `chmod g=u` or `chmod g+w`
- [x] USER directive uses numeric UID (1001)
- [x] No hardcoded UIDs in application code
- [x] All runtime directories are group-writable
- [x] Security context drops all capabilities
- [x] Application runs as non-root
- [x] Health checks use HTTP (not requiring special permissions)
- [x] Port is > 1024 (8000)

## Best Practices

1. **Always use root group (0)** for file ownership
2. **Make runtime directories group-writable** (`chmod g+w`)
3. **Use `chmod g=u`** to sync group and user permissions
4. **Use numeric UIDs** in USER directive
5. **Test with random UID** before deploying:
   ```bash
   docker run --user 1000630000:0 your-image
   ```
6. **Avoid hardcoded UIDs** in application code
7. **Use SecurityContext** appropriately in OpenShift templates
8. **Prefer emptyDir** for temporary storage
9. **Use PVC** for persistent data
10. **Document all assumptions** about file permissions

## Additional Resources

- [OpenShift Container Platform - Creating Images](https://docs.openshift.com/container-platform/latest/openshift_images/create-images.html)
- [OpenShift - Guidelines for Creating Images](https://docs.openshift.com/container-platform/latest/openshift_images/create-images.html#images-create-guide-openshift_create-images)
- [Security Context Constraints (SCCs)](https://docs.openshift.com/container-platform/latest/authentication/managing-security-context-constraints.html)
- [OpenShift Support for Docker](https://docs.openshift.com/container-platform/latest/openshift_images/create-images.html#images-create-guide-general_create-images)

## Summary

The main principle for OpenShift compatibility is:

> **All files must be accessible by the root group (GID 0) with appropriate permissions, as OpenShift will assign an arbitrary UID from its range, but always with root group membership.**

This is achieved through:
1. Setting group ownership to 0 (root group)
2. Ensuring group permissions match or exceed user permissions
3. Making writable directories group-writable
4. Using numeric UIDs
5. Never assuming a specific UID will be assigned
