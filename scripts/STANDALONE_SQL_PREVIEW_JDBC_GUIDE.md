# 🚀 Standalone SQL Preview Script with JDBC

## 📋 **Overview**

This is the **JDBC version** of the standalone SQL preview script that uses the same database connection approach as your main project. It uses **JayDeBeApi** for JDBC connectivity, supporting multiple database types.

## 🎯 **Key Features**

- ✅ **JDBC Connectivity**: Uses JayDeBeApi (same as your project)
- ✅ **Multi-Database Support**: SQL Server, MySQL, PostgreSQL, Oracle
- ✅ **Complete API Mimicry**: Same functionality as the original API endpoint
- ✅ **LLM Integration**: OpenAI for natural language parsing and SQL generation
- ✅ **Database-Specific SQL**: Generates appropriate syntax for each database type
- ✅ **Comprehensive Logging**: Detailed step-by-step execution logging
- ✅ **Multiple Output Formats**: JSON, pretty-printed, or SQL-only output

## 🛠️ **Installation**

### **Step 1: Install Python Dependencies**
```bash
# Install required packages
pip install -r standalone_requirements_jdbc.txt

# Or install manually
pip install jaydebeapi openai
```

### **Step 2: Install Java**
```bash
# JDBC requires Java to be installed
# Ubuntu/Debian
sudo apt-get install default-jdk

# CentOS/RHEL
sudo yum install java-11-openjdk-devel

# macOS
brew install openjdk@11

# Windows
# Download and install Java from Oracle or OpenJDK
```

### **Step 3: Download JDBC Drivers**

Create a directory for JDBC drivers and download the appropriate drivers:

```bash
# Create JDBC drivers directory
mkdir -p /opt/jdbc_drivers
cd /opt/jdbc_drivers

# SQL Server
wget https://download.microsoft.com/download/.../mssql-jdbc-12.4.2.jre11.jar

# MySQL
wget https://dev.mysql.com/get/Downloads/Connector-J/mysql-connector-j-8.2.0.jar

# PostgreSQL
wget https://jdbc.postgresql.org/download/postgresql-42.7.0.jar

# Oracle (requires Oracle account)
# Download ojdbc11.jar from Oracle website
```

### **Step 4: Set Environment Variables (Optional)**
```bash
# Set OpenAI API key (optional - can be passed as argument)
export OPENAI_API_KEY="your-openai-api-key-here"

# Set Java home if needed
export JAVA_HOME="/usr/lib/jvm/java-11-openjdk"
```

## 🚀 **Usage Examples**

### **Example 1: SQL Server with LLM**
```bash
python standalone_sql_preview_jdbc.py \
  --nl-definition "get products from hana_material_master where OPS_PLANNER is missing" \
  --kg-name "New_KG_101" \
  --select-schema "newdqnov7" \
  --openai-key "sk-your-openai-key" \
  --temperature 0.7 \
  --db-type "sqlserver" \
  --db-host "your-sql-server" \
  --db-port 1433 \
  --db-name "your-database" \
  --db-user "your-username" \
  --db-password "your-password" \
  --jdbc-drivers-path "/opt/jdbc_drivers" \
  --use-llm \
  --verbose
```

### **Example 2: MySQL with Rule-based Parsing**
```bash
python standalone_sql_preview_jdbc.py \
  --nl-definition "find missing planners in product_master" \
  --select-schema "production" \
  --db-type "mysql" \
  --db-host "mysql-server" \
  --db-port 3306 \
  --db-name "inventory" \
  --db-user "mysql_user" \
  --db-password "mysql_password" \
  --jdbc-drivers-path "/opt/jdbc_drivers" \
  --output-format pretty
```

### **Example 3: PostgreSQL with JSON Output**
```bash
python standalone_sql_preview_jdbc.py \
  --nl-definition "show products with missing codes" \
  --select-schema "public" \
  --db-type "postgresql" \
  --db-host "pg-server" \
  --db-port 5432 \
  --db-name "warehouse" \
  --db-user "postgres" \
  --db-password "pg_password" \
  --jdbc-drivers-path "/usr/local/jdbc" \
  --output-format json
```

### **Example 4: Oracle with Verbose Logging**
```bash
python standalone_sql_preview_jdbc.py \
  --nl-definition "get missing inventory items" \
  --select-schema "INVENTORY" \
  --db-type "oracle" \
  --db-host "oracle-server" \
  --db-port 1521 \
  --db-name "ORCL" \
  --db-user "inventory_user" \
  --db-password "oracle_password" \
  --jdbc-drivers-path "/opt/oracle/jdbc" \
  --verbose
```

## 📋 **Command Line Arguments**

### **Required Arguments:**
- `--nl-definition`: Natural language query definition
- `--select-schema`: Database schema name
- `--db-type`: Database type (sqlserver, mysql, postgresql, oracle)
- `--db-host`: Database server host
- `--db-name`: Database name
- `--db-user`: Database username
- `--db-password`: Database password
- `--jdbc-drivers-path`: Path to JDBC drivers directory

### **Optional Arguments:**
- `--kg-name`: Knowledge Graph name (default: "default")
- `--openai-key`: OpenAI API key (or use OPENAI_API_KEY env var)
- `--temperature`: OpenAI temperature 0.0-1.0 (default: 0.7)
- `--db-port`: Database port (auto-detected based on db-type)
- `--use-llm`: Enable LLM-based processing
- `--verbose`: Enable detailed logging
- `--output-format`: Output format (json|pretty|sql-only, default: pretty)

## 📊 **Database-Specific Features**

### **SQL Server / MSSQL**
- **Schema Qualification**: `[schema].[table]`
- **LIMIT Syntax**: `SELECT TOP 1000`
- **JDBC URL**: `jdbc:sqlserver://host:port;databaseName=db`
- **Driver**: `com.microsoft.sqlserver.jdbc.SQLServerDriver`

### **MySQL**
- **Schema Qualification**: `` `schema`.`table` ``
- **LIMIT Syntax**: `SELECT ... LIMIT 1000`
- **JDBC URL**: `jdbc:mysql://host:port/database`
- **Driver**: `com.mysql.cj.jdbc.Driver`

### **PostgreSQL**
- **Schema Qualification**: `"schema"."table"`
- **LIMIT Syntax**: `SELECT ... LIMIT 1000`
- **JDBC URL**: `jdbc:postgresql://host:port/database`
- **Driver**: `org.postgresql.Driver`

### **Oracle**
- **Schema Qualification**: `schema.table`
- **LIMIT Syntax**: `SELECT ... WHERE ROWNUM <= 1000`
- **JDBC URL**: `jdbc:oracle:thin:@host:port:sid`
- **Driver**: `oracle.jdbc.driver.OracleDriver`

## 📝 **Sample Output**

### **Pretty Format:**
```
================================================================================
🎉 SQL PREVIEW RESULT (JDBC)
================================================================================
✅ Success: True
📊 Storage Type: sqlserver_jdbc
🔧 Enhancement Applied: True
📋 Material Master Added: True
⚙️ OPS Planner Added: True
💾 Database Type: sqlserver (JDBC)
📊 Schema: newdqnov7
📋 Tables Discovered: 10
⏱️ Total Time: 2456.78ms
🚀 Process Time: 1234.56ms
🎯 Intent Confidence: 0.85
📝 Query Type: comparison_query
⚙️ Operation: NOT_IN
📊 Source Table: hana_material_master
📊 Target Table: none

🔧 GENERATED SQL:
--------------------------------------------------------------------------------
SELECT *
FROM [newdqnov7].[hana_material_master]
WHERE OPS_PLANNER IS NULL
   OR OPS_PLANNER = ''

✨ ENHANCED SQL:
--------------------------------------------------------------------------------
SELECT *
FROM [newdqnov7].[hana_material_master]
LEFT JOIN [newdqnov7].[hana_material_master] mm ON mm.MATERIAL = s.MATERIAL
WHERE OPS_PLANNER IS NULL
   OR OPS_PLANNER = ''
================================================================================
```

## 🔧 **Troubleshooting**

### **Common Issues:**

1. **Java Not Found**
   ```
   ❌ Error: Java not found
   ```
   **Solution**: Install Java and ensure it's in your PATH

2. **JDBC Driver Not Found**
   ```
   ❌ No JDBC driver found for sqlserver at /path/to/drivers/mssql-jdbc*.jar
   ```
   **Solution**: Download the correct JDBC driver and place it in the specified directory

3. **Database Connection Failed**
   ```
   ❌ Failed to connect to database via JDBC
   ```
   **Solution**: Check database host, credentials, and network connectivity

4. **Schema Not Found**
   ```
   ⚠️ No source table found, generating basic SELECT
   ```
   **Solution**: Verify schema name and ensure tables exist

## 🎯 **Advantages of JDBC Version**

| Feature | JDBC Version | pyodbc Version |
|---------|-------------|----------------|
| Database Support | ✅ Multi-database | ❌ SQL Server only |
| Connection Method | ✅ JDBC (same as project) | ❌ ODBC |
| Driver Management | ✅ JAR files | ❌ System drivers |
| Cross-platform | ✅ Java-based | ❌ Platform-specific |
| SQL Syntax | ✅ Database-specific | ❌ SQL Server only |
| Schema Qualification | ✅ Database-appropriate | ❌ SQL Server brackets |

## 🎉 **Success!**

You now have a complete JDBC-based standalone script that:
- ✅ Uses the same JDBC approach as your main project
- ✅ Supports multiple database types
- ✅ Provides complete API functionality
- ✅ Includes comprehensive logging
- ✅ Works independently outside your project

**Run the script with your database parameters and get the same results as your API!** 🚀
