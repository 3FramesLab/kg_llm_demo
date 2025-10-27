# JDBC Driver Pattern Fix ✅

## Problem

When executing a KPI with `db_type: "sqlserver"`, the following error occurred:

```
No JDBC driver found for sqlserver at D:\learning\dq-poc\jdbc_drivers/*sqlserver*.jar
```

The issue was that the code was looking for a JAR file matching `*sqlserver*.jar`, but the actual SQL Server JDBC driver is named `mssql-jdbc-*.jar`.

## Root Cause

In `landing_kpi_executor.py` at line 246, the code was using a generic pattern:

```python
# ❌ WRONG - Generic pattern doesn't match actual JAR names
driver_pattern = f"{JDBC_DRIVERS_PATH}/*{db_type_lower}*.jar"
# For sqlserver: "*sqlserver*.jar" (doesn't match "mssql-jdbc-9.4.0.jre11.jar")
```

This generic approach worked for some databases by coincidence but failed for SQL Server because:
- Database type: `sqlserver`
- Generic pattern: `*sqlserver*.jar`
- Actual JAR name: `mssql-jdbc-9.4.0.jre11.jar` ❌ No match!

## Solution

Updated the code to use proper JAR patterns for each database type, matching patterns used in other parts of the codebase:

```python
if db_type_lower == "sqlserver":
    jar_pattern = "mssql-jdbc*.jar"  # ✅ Matches mssql-jdbc-9.4.0.jre11.jar
elif db_type_lower == "mysql":
    jar_pattern = "mysql-connector-j*.jar"  # ✅ Matches mysql-connector-j-8.0.33.jar
elif db_type_lower == "postgresql":
    jar_pattern = "postgresql-*.jar"  # ✅ Matches postgresql-42.3.1.jar
elif db_type_lower == "oracle":
    jar_pattern = "ojdbc*.jar"  # ✅ Matches ojdbc8.jar or ojdbc11.jar
```

### Updated Code

```python
# Build JDBC URL based on database type
db_type_lower = db_type.lower()

if db_type_lower == "sqlserver":
    jdbc_url = f"jdbc:sqlserver://{db_config.host}:{db_config.port};databaseName={db_config.database}"
    driver_class = "com.microsoft.sqlserver.jdbc.SQLServerDriver"
    jar_pattern = "mssql-jdbc*.jar"
elif db_type_lower == "mysql":
    jdbc_url = f"jdbc:mysql://{db_config.host}:{db_config.port}/{db_config.database}?..."
    driver_class = "com.mysql.cj.jdbc.Driver"
    jar_pattern = "mysql-connector-j*.jar"
elif db_type_lower == "postgresql":
    jdbc_url = f"jdbc:postgresql://{db_config.host}:{db_config.port}/{db_config.database}"
    driver_class = "org.postgresql.Driver"
    jar_pattern = "postgresql-*.jar"
elif db_type_lower == "oracle":
    jdbc_url = f"jdbc:oracle:thin:@{db_config.host}:{db_config.port}:{service_name}"
    driver_class = "oracle.jdbc.driver.OracleDriver"
    jar_pattern = "ojdbc*.jar"

# Find JDBC driver JAR using proper pattern
driver_pattern = os.path.join(JDBC_DRIVERS_PATH, jar_pattern)
jars = glob.glob(driver_pattern)

if not jars:
    logger.error(f"No JDBC driver found for {db_type} at {driver_pattern}")
    logger.error(f"Available files: {os.listdir(JDBC_DRIVERS_PATH)}")
    return None

driver_jar = jars[0]
logger.info(f"Using JDBC driver: {driver_jar}")
```

## JDBC Driver Mapping

| Database | DB Type | JAR Pattern | Example JAR Name |
|----------|---------|-------------|------------------|
| SQL Server | `sqlserver` | `mssql-jdbc*.jar` | `mssql-jdbc-9.4.0.jre11.jar` |
| MySQL | `mysql` | `mysql-connector-j*.jar` | `mysql-connector-j-8.0.33.jar` |
| PostgreSQL | `postgresql` | `postgresql-*.jar` | `postgresql-42.3.1.jar` |
| Oracle | `oracle` | `ojdbc*.jar` | `ojdbc8.jar` or `ojdbc11.jar` |

## Files Modified

- **kg_builder/services/landing_kpi_executor.py** (lines 226-259)
  - Added proper JAR patterns for each database type
  - Updated driver class for MySQL (com.mysql.cj.jdbc.Driver)
  - Added better error logging showing available files

## Additional Improvements

1. **Better Error Messages**: Now shows available files in jdbc_drivers directory when driver not found
2. **Consistent Patterns**: Uses same patterns as other services (data_extractor.py, rule_validator.py, reconciliation_executor.py)
3. **Driver Class Updates**: Updated MySQL driver class to use newer `com.mysql.cj.jdbc.Driver`

## Status

✅ **COMPLETE** - JDBC driver patterns now correctly match actual JAR file names!

## Testing

To verify the fix works:

1. Ensure JDBC drivers are in `jdbc_drivers/` directory:
   ```
   jdbc_drivers/
   ├── mssql-jdbc-9.4.0.jre11.jar
   ├── mysql-connector-j-8.0.33.jar
   ├── postgresql-42.3.1.jar
   └── ojdbc8.jar
   ```

2. Execute KPI with `db_type: "sqlserver"`
3. Should now find and use the correct JDBC driver ✅

