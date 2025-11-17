# SQL Preview Script - Troubleshooting Guide

This guide helps you resolve common issues when running the SQL preview scripts.

## 🚨 Common Errors and Solutions

### 1. **ModuleNotFoundError: No module named 'pyodbc'**

**Error:**
```
ModuleNotFoundError: No module named 'pyodbc'
```

**Solution:**
```bash
# Install pyodbc
pip install pyodbc

# Or if using Python 3 specifically
pip3 install pyodbc

# On some systems
python -m pip install pyodbc
python3 -m pip install pyodbc
```

**Additional Requirements:**
- **ODBC Driver 17 for SQL Server** must be installed
- **Windows:** Download from [Microsoft's official page](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)
- **Linux (Ubuntu/Debian):**
  ```bash
  curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
  curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list
  apt-get update
  ACCEPT_EULA=Y apt-get install -y msodbcsql17
  ```
- **macOS:**
  ```bash
  brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
  brew update
  HOMEBREW_NO_ENV_FILTERING=1 ACCEPT_EULA=Y brew install msodbcsql17
  ```

### 2. **ModuleNotFoundError: No module named 'openai'**

**Error:**
```
ModuleNotFoundError: No module named 'openai'
```

**Solution:**
```bash
# Install openai
pip install openai

# Or if using Python 3 specifically
pip3 install openai

# On some systems
python -m pip install openai
python3 -m pip install openai
```

### 3. **Database Connection Errors**

**Error:**
```
Error retrieving database schema: ('08001', '[08001] [Microsoft][ODBC Driver 17 for SQL Server]...')
```

**Possible Causes & Solutions:**

#### A. **Server Not Running or Not Accessible**
- Ensure SQL Server is running
- Check if the server name is correct: `DESKTOP-41O1AL9\LOCALHOST`
- Try using just `DESKTOP-41O1AL9` or `localhost` or `127.0.0.1`

#### B. **Incorrect Connection Details**
- Verify database name: `NewDQ`
- Verify username: `mithun`
- Verify password: `mithun123`
- Check if the database exists and user has access

#### C. **Firewall Issues**
- Ensure SQL Server port (1433) is open
- Check Windows Firewall settings
- Verify SQL Server is configured to accept remote connections

#### D. **Authentication Issues**
- Ensure SQL Server Authentication is enabled (not just Windows Authentication)
- Verify the user account exists and has proper permissions
- Try connecting with SQL Server Management Studio first

### 4. **OpenAI API Errors**

**Error:**
```
Error parsing with LLM: Invalid API key provided
```

**Solutions:**
- Verify your OpenAI API key is correct
- Check if you have sufficient credits in your OpenAI account
- Ensure the API key has access to GPT-4 models
- Try a different API key if available

**Error:**
```
Error generating SQL with LLM: The model 'gpt-4o' does not exist
```

**Solution:**
- The model name might have changed
- Try changing `gpt-4o` to `gpt-4` or `gpt-3.5-turbo` in the script
- Check OpenAI's documentation for current model names

### 5. **Configuration Errors**

**Error:**
```
CONFIGURATION ERRORS:
   - OPENAI_KEY must be set to a valid OpenAI API key
```

**Solution:**
- Update the configuration section at the top of the script
- Replace placeholder values with your actual values
- Ensure no fields are empty or contain placeholder text

## 🔧 Step-by-Step Installation

### Step 1: Install Python Dependencies
```bash
# Create a virtual environment (recommended)
python3 -m venv sql_preview_env
source sql_preview_env/bin/activate  # On Windows: sql_preview_env\Scripts\activate

# Install dependencies
pip install pyodbc openai

# Or install from requirements file
pip install -r requirements_sql_preview.txt
```

### Step 2: Install ODBC Driver
Follow the platform-specific instructions above for installing ODBC Driver 17 for SQL Server.

### Step 3: Configure the Script
Edit `sql_preview_simple.py` and update these values:
```python
NL_DEFINITION = "your natural language query"
KG_NAME = "your_kg_name"
SELECT_SCHEMA = "your_schema"
OPENAI_KEY = "your_actual_openai_key"
DB_HOST = "your_database_host"
DB_USER = "your_database_user"
DB_PASSWORD = "your_database_password"
```

### Step 4: Test the Installation
```bash
python3 test_installation.py
```

### Step 5: Run the Script
```bash
python3 sql_preview_simple.py
```

## 🧪 Testing Database Connection

Create a simple test script to verify database connectivity:

```python
import pyodbc

# Test connection
try:
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=DESKTOP-41O1AL9\\LOCALHOST;"
        "DATABASE=NewDQ;"
        "UID=mithun;"
        "PWD=mithun123;"
        "TrustServerCertificate=yes;"
    )
    
    conn = pyodbc.connect(conn_str)
    print("✅ Database connection successful!")
    
    cursor = conn.cursor()
    cursor.execute("SELECT @@VERSION")
    version = cursor.fetchone()[0]
    print(f"SQL Server Version: {version}")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Database connection failed: {e}")
```

## 🧪 Testing OpenAI Connection

Create a simple test script to verify OpenAI connectivity:

```python
from openai import OpenAI

try:
    client = OpenAI(api_key="your_openai_key_here")
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello, world!"}],
        max_tokens=10
    )
    
    print("✅ OpenAI connection successful!")
    print(f"Response: {response.choices[0].message.content}")
    
except Exception as e:
    print(f"❌ OpenAI connection failed: {e}")
```

## 📞 Getting Help

If you're still having issues:

1. **Check the log file:** `sql_preview.log` contains detailed error information
2. **Run with verbose mode:** Set `VERBOSE = True` in the configuration
3. **Test components individually:** Use the test scripts above
4. **Check system requirements:**
   - Python 3.7+
   - ODBC Driver 17 for SQL Server
   - Network access to database and OpenAI API
   - Valid credentials for both services

## 🎯 Quick Fixes

### If pip is not available:
```bash
# Install pip
python3 -m ensurepip --upgrade

# Or download get-pip.py and run
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py
```

### If you get permission errors:
```bash
# Install with user flag
pip install --user pyodbc openai

# Or use sudo (Linux/macOS)
sudo pip install pyodbc openai
```

### If you're behind a corporate firewall:
```bash
# Use proxy
pip install --proxy http://proxy.company.com:8080 pyodbc openai

# Or configure pip
pip config set global.proxy http://proxy.company.com:8080
```
