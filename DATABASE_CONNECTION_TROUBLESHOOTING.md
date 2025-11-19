# Database Connection Troubleshooting Guide

## Your System Analysis

Based on the diagnostic scan of your system, here's what was found:

### ✅ Running Databases

1. **MySQL** - Port 3306 (LISTENING)
2. **PostgreSQL** - Port 5432 (LISTENING)
3. **SQL Server** - Running but NOT listening on standard port 1433

### ❌ Your Connection Error

You tried to connect with:
```json
{
    "name": "DQ",
    "type": "mysql",        ← MySQL type
    "host": "localhost",
    "port": "1433",         ← SQL Server port!
    "database": "newDQ",
    "username": "root",
    "password": "root"
}
```

**Problem**: You're using MySQL type with SQL Server port (1433). MySQL uses port 3306.

## Solutions

### Option 1: Connect to MySQL (Recommended)

Since you have MySQL running on port 3306, use this configuration:

```json
{
    "name": "DQ MySQL",
    "type": "mysql",
    "host": "localhost",
    "port": 3306,
    "database": "NewDQ",
    "username": "root",
    "password": "root",
    "service_name": ""
}
```

**Steps to verify MySQL database exists:**
```bash
# Open MySQL command line
mysql -u root -p

# List databases
SHOW DATABASES;

# Check if NewDQ exists
USE NewDQ;
```

### Option 2: Connect to PostgreSQL

If you want to use PostgreSQL instead:

```json
{
    "name": "DQ PostgreSQL",
    "type": "postgresql",
    "host": "localhost",
    "port": 5432,
    "database": "NewDQ",
    "username": "postgres",
    "password": "your_password",
    "service_name": ""
}
```

### Option 3: Connect to SQL Server (Requires Configuration)

SQL Server is running but not listening on port 1433. This usually means:
1. TCP/IP is disabled in SQL Server Configuration Manager
2. SQL Server is using dynamic ports
3. SQL Server is using a named instance

**To enable SQL Server on port 1433:**

1. Open **SQL Server Configuration Manager**
2. Navigate to: SQL Server Network Configuration → Protocols for MSSQLSERVER
3. Enable **TCP/IP**
4. Right-click TCP/IP → Properties → IP Addresses tab
5. Scroll to **IPAll** section
6. Set **TCP Port** to `1433`
7. Clear **TCP Dynamic Ports**
8. Restart SQL Server service

**Then use this configuration:**
```json
{
    "name": "DQ SQL Server",
    "type": "sqlserver",
    "host": "localhost",
    "port": 1433,
    "database": "NewDQ",
    "username": "sa",
    "password": "your_password",
    "service_name": ""
}
```

**For SQL Server Named Instance:**
If you're using a named instance like `LOCALHOST\SQLEXPRESS`, you need to:
1. Find the dynamic port it's using
2. Use that port in the connection

```json
{
    "name": "DQ SQL Server Express",
    "type": "sqlserver",
    "host": "localhost",
    "port": 49152,  // Replace with actual dynamic port
    "database": "NewDQ",
    "username": "sa",
    "password": "your_password"
}
```

## Quick Diagnostic Commands

### Check MySQL
```bash
# Test MySQL connection
mysql -u root -p -h localhost -P 3306

# List databases
mysql -u root -p -e "SHOW DATABASES;"
```

### Check PostgreSQL
```bash
# Test PostgreSQL connection
psql -U postgres -h localhost -p 5432

# List databases
psql -U postgres -l
```

### Check SQL Server
```bash
# Using sqlcmd
sqlcmd -S localhost -U sa -P your_password

# List databases
sqlcmd -S localhost -U sa -P your_password -Q "SELECT name FROM sys.databases"
```

## Common Port Numbers

| Database | Default Port |
|----------|-------------|
| MySQL | 3306 |
| PostgreSQL | 5432 |
| SQL Server | 1433 |
| Oracle | 1521 |
| MongoDB | 27017 |

## Testing Your Connection

After updating your configuration, test it using the diagnostic script:

```bash
python diagnose_database.py localhost 3306
```

Or test directly in the web interface:
1. Open the Schema Wizard
2. Click "New Connection"
3. Fill in the corrected details
4. Click "Test Connection" before adding

## Error Messages Explained

### "Failed to establish connection"
- Database server is not running
- Wrong host or port
- Firewall blocking connection

### "Access denied" / "Authentication failed"
- Wrong username or password
- User doesn't have permission to connect

### "Unknown database"
- Database name doesn't exist
- Check spelling and case sensitivity

### "Communications link failure"
- Network issue
- Database not listening on specified port
- Firewall blocking connection

## Recommended Next Steps

1. **Try MySQL first** (since it's confirmed running on port 3306)
2. Verify the database "NewDQ" exists in MySQL
3. Test the connection using the corrected configuration above
4. If you need SQL Server, configure it to listen on port 1433 first

## Need More Help?

Run the diagnostic tool to check any port:
```bash
python diagnose_database.py localhost 3306   # Check MySQL
python diagnose_database.py localhost 5432   # Check PostgreSQL
python diagnose_database.py localhost 1433   # Check SQL Server
```

The tool will tell you:
- If the port is open
- What database type typically uses that port
- Recommended connection settings

