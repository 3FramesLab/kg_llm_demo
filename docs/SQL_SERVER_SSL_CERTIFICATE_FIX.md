# SQL Server SSL Certificate Fix ✅

## Problem

When executing a KPI with SQL Server database, the following error occurred:

```
com.microsoft.sqlserver.jdbc.SQLServerException: "encrypt" property is set to "true" 
and "trustServerCertificate" property is set to "false" but the driver could not 
establish a secure connection to SQL Server by using Secure Sockets Layer (SSL) encryption: 
Error: PKIX path building failed: sun.security.provider.certpath.SunCertPathBuilderException: 
unable to find valid certification path to requested target.
```

## Root Cause

The SQL Server JDBC URL in `landing_kpi_executor.py` was missing SSL/TLS certificate handling parameters:

```python
# ❌ WRONG - Missing SSL certificate parameters
jdbc_url = f"jdbc:sqlserver://{db_config.host}:{db_config.port};databaseName={db_config.database}"
```

This caused the driver to:
1. Default to `encrypt=true` (enable SSL)
2. Default to `trustServerCertificate=false` (verify certificate)
3. Fail when the server certificate couldn't be verified

## Solution

Added the SSL certificate parameters to the JDBC URL:

```python
# ✅ CORRECT - Includes SSL certificate handling
jdbc_url = f"jdbc:sqlserver://{db_config.host}:{db_config.port};databaseName={db_config.database};encrypt=true;trustServerCertificate=true"
```

### Parameters Explained

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `encrypt` | `true` | Enable SSL/TLS encryption for connection |
| `trustServerCertificate` | `true` | Trust server certificate without validation |

**Note**: `trustServerCertificate=true` is appropriate for:
- Development/testing environments
- Internal networks with self-signed certificates
- Environments where certificate validation is not required

For production with proper certificates, use `trustServerCertificate=false` and ensure proper certificate chain is available.

## Updated Code

```python
if db_type_lower == "sqlserver":
    # ✅ Now includes encrypt and trustServerCertificate parameters
    jdbc_url = f"jdbc:sqlserver://{db_config.host}:{db_config.port};databaseName={db_config.database};encrypt=true;trustServerCertificate=true"
    driver_class = "com.microsoft.sqlserver.jdbc.SQLServerDriver"
    jar_pattern = "mssql-jdbc*.jar"
```

## Consistency with Other Services

This fix aligns with how other services handle SQL Server connections:

- ✅ `kg_builder/services/reconciliation_executor.py` (line 1062)
- ✅ `kg_builder/services/rule_validator.py` (line 235)
- ✅ `kg_builder/services/data_extractor.py` (line 180)
- ✅ `kg_builder/routes.py` (line 67)

All now use the same SSL certificate parameters.

## Files Modified

- **kg_builder/services/landing_kpi_executor.py** (line 230)
  - Added `encrypt=true;trustServerCertificate=true` to SQL Server JDBC URL

## Testing

To verify the fix works:

1. Ensure SQL Server database is configured in `.env`
2. Execute KPI with `db_type: "sqlserver"`
3. Should now connect successfully without SSL certificate errors ✅

## Related Documentation

- [Microsoft SQL Server JDBC Connection Properties](https://docs.microsoft.com/en-us/sql/connect/jdbc/setting-the-connection-properties)
- [JDBC URL Format for SQL Server](https://docs.microsoft.com/en-us/sql/connect/jdbc/building-the-connection-url)

## Status

✅ **COMPLETE** - SQL Server SSL certificate handling now properly configured!

