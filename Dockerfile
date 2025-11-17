# =============================================================================
# Multi-stage Dockerfile for Knowledge Graph Builder
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Builder - Install dependencies
# -----------------------------------------------------------------------------
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    default-jdk \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# -----------------------------------------------------------------------------
# Stage 2: Runtime - Create lean production image
# -----------------------------------------------------------------------------
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

# Install runtime dependencies (JRE for JDBC, unixodbc for pyodbc)
RUN apt-get update && apt-get install -y \
    default-jre \
    wget \
    curl \
    unixodbc \
    unixodbc-dev \
    gnupg2 \
    apt-transport-https \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Microsoft ODBC Driver 17 for SQL Server
RUN wget -qO /usr/share/keyrings/microsoft-prod.asc https://packages.microsoft.com/keys/microsoft.asc \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft-prod.asc] https://packages.microsoft.com/debian/11/prod bullseye main" > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && rm -rf /var/lib/apt/lists/*

# Create app user (non-root for security)
# OpenShift runs containers with arbitrary UIDs that are part of the root group (GID 0)
RUN useradd -m -u 1001 -g 0 appuser && \
    mkdir -p /app /app/data /app/schemas /app/jdbc_drivers && \
    chown -R appuser:0 /app

# Download MSSQL JDBC driver
RUN wget -q https://repo1.maven.org/maven2/com/microsoft/sqlserver/mssql-jdbc/12.4.2.jre11/mssql-jdbc-12.4.2.jre11.jar \
    -O /app/jdbc_drivers/mssql-jdbc-12.4.2.jre11.jar && \
    chown appuser:0 /app/jdbc_drivers/mssql-jdbc-12.4.2.jre11.jar && \
    chmod 664 /app/jdbc_drivers/mssql-jdbc-12.4.2.jre11.jar

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=appuser:0 . .

# Create necessary directories with proper permissions
# Set group ownership to root (0) and make directories group-writable for OpenShift
RUN mkdir -p \
    /app/data/reconciliation_rules \
    /app/data/graphiti_storage \
    /app/logs \
    && chown -R appuser:0 /app \
    && chmod -R g=u /app \
    && chmod -R g+w /app/data /app/logs

# Switch to non-root user
# OpenShift will run as a random UID but will be part of root group (GID 0)
USER 1001

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["uvicorn", "kg_builder.main:app", "--host", "0.0.0.0", "--port", "8000"]
