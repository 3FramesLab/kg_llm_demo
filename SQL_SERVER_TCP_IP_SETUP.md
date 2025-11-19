# SQL Server TCP/IP Connection Setup Guide

## Problem
SQL Server is running but not accepting TCP/IP connections on port 1433.

**Error Message:**
```
The TCP/IP connection to the host localhost, port 1433 has failed. 
Error: "Connection refused: getsockopt"
```

## Diagnostic Results
- ✅ SQL Server (MSSQLSERVER) service is **RUNNING**
- ❌ Port 1433 is **NOT listening**
- ✅ SQL Server is listening on port **1434** (unusual)
- ✅ MySQL is running on port **3306**

---

## Solution 1: Enable TCP/IP on Port 1433 (Recommended)

### Step 1: Open SQL Server Configuration Manager
1. Press `Win + R`
2. Type: `SQLServerManager16.msc` (or `SQLServerManager15.msc` for SQL Server 2019)
3. Press Enter

### Step 2: Enable TCP/IP Protocol
1. Expand **SQL Server Network Configuration**
2. Click **Protocols for MSSQLSERVER**
3. Right-click **TCP/IP** → Select **Enable**

### Step 3: Configure TCP/IP Port
1. Right-click **TCP/IP** → Select **Properties**
2. Go to **IP Addresses** tab
3. Scroll down to **IPAll** section (at the bottom)
4. Configure:
   - **TCP Dynamic Ports:** (leave blank or remove any value)
   - **TCP Port:** `1433`
5. Click **OK**

### Step 4: Restart SQL Server
1. In SQL Server Configuration Manager, click **SQL Server Services**
2. Right-click **SQL Server (MSSQLSERVER)**
3. Select **Restart**

### Step 5: Test Connection
Use this payload:
```json
{
    "name": "Test_SQL Server",
    "type": "sqlserver",
    "host": "localhost",
    "port": "1433",
    "database": "NewDQ",
    "username": "sa",
    "password": "your_password",
    "service_name": ""
}
```

**Note:** Replace `username` and `password` with your actual SQL Server credentials.
- SQL Server typically uses `sa` (system administrator) account, not `root`
- If using Windows Authentication, you'll need to configure that separately

---

## Solution 2: Use Port 1434 (Quick Test)

Since SQL Server is already listening on port 1434, you can test immediately:

```json
{
    "name": "Test_SQL Server",
    "type": "sqlserver",
    "host": "localhost",
    "port": "1434",
    "database": "NewDQ",
    "username": "sa",
    "password": "your_password",
    "service_name": ""
}
```

---

## Solution 3: Use MySQL (Alternative)

If your NewDQ database is in MySQL (which is running on port 3306):

```json
{
    "name": "Test_MySQL",
    "type": "mysql",
    "host": "localhost",
    "port": "3306",
    "database": "NewDQ",
    "username": "root",
    "password": "3frames",
    "service_name": ""
}
```

---

## Common Issues

### Issue 1: SQL Server Authentication
**Problem:** SQL Server may be configured for Windows Authentication only.

**Solution:**
1. Open SQL Server Management Studio (SSMS)
2. Connect to your server
3. Right-click server → **Properties**
4. Go to **Security** page
5. Select **SQL Server and Windows Authentication mode**
6. Restart SQL Server service

### Issue 2: Firewall Blocking Port 1433
**Problem:** Windows Firewall may be blocking port 1433.

**Solution:**
```powershell
# Run PowerShell as Administrator
New-NetFirewallRule -DisplayName "SQL Server" -Direction Inbound -Protocol TCP -LocalPort 1433 -Action Allow
```

### Issue 3: SQL Server Browser Not Running
**Problem:** SQL Server Browser service is stopped (detected in diagnostic).

**Solution:**
1. Open SQL Server Configuration Manager
2. Click **SQL Server Services**
3. Right-click **SQL Server Browser**
4. Select **Start**
5. Right-click again → **Properties** → Set **Start Mode** to **Automatic**

---

## Verification

After making changes, run the diagnostic script again:
```powershell
powershell -ExecutionPolicy Bypass -File check_sql_server.ps1
```

You should see:
- ✅ Port 1433 is LISTENING
- ✅ Successfully connected to localhost:1433

---

## Additional Resources

- [Configure SQL Server to Listen on TCP/IP](https://learn.microsoft.com/en-us/sql/database-engine/configure-windows/configure-a-server-to-listen-on-a-specific-tcp-port)
- [Enable SQL Server Authentication](https://learn.microsoft.com/en-us/sql/database-engine/configure-windows/change-server-authentication-mode)
- [SQL Server Network Configuration](https://learn.microsoft.com/en-us/sql/tools/configuration-manager/sql-server-network-configuration)

