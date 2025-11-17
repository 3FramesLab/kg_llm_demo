# Updated SQL Preview Scripts - Configuration-Based

I've updated the SQL preview scripts to make them much easier to use. Now you can simply update the configuration values at the top of the files and run them without any command line arguments!

## 📁 Available Scripts

### 1. **`standalone_sql_preview.py`** - Full-Featured Version
- **Configuration + Command Line**: Update defaults in the script, optionally override with command line args
- **All Features**: Complete functionality with argument parsing
- **Flexibility**: Can still use command line arguments to override defaults

### 2. **`sql_preview_simple.py`** - Simple Configuration-Only Version  
- **Configuration Only**: Just update the config and run - no command line arguments needed
- **Streamlined**: Cleaner, simpler code focused on ease of use
- **Perfect for**: Quick testing and repeated runs with same parameters

## 🚀 Quick Start - Simple Version

### Step 1: Update Configuration
Edit `sql_preview_simple.py` and update these values at the top:

```python
# Natural Language Definition
NL_DEFINITION = "get products from hana_material_master where OPS_PLANNER is missing"

# Knowledge Graph Settings
KG_NAME = "KG_Test_001"
SELECT_SCHEMA = "newdqnov7"

# OpenAI Settings
OPENAI_KEY = "your-openai-key-here"
TEMPERATURE = 0.0

# Database Settings
DB_HOST = "DESKTOP-41O1AL9\\LOCALHOST"
DB_PORT = 1433
DB_NAME = "NewDQ"
DB_USER = "mithun"
DB_PASSWORD = "mithun123"

# Script Settings
USE_LLM = True
VERBOSE = True
OUTPUT_FILE = None  # Set to filename to save results
```

### Step 2: Run the Script
```bash
python sql_preview_simple.py
```

That's it! No command line arguments needed.

## 🔧 Advanced Usage - Full Version

### Option 1: Configuration Only
1. Update the `DEFAULT_CONFIG` section in `standalone_sql_preview.py`
2. Run: `python standalone_sql_preview.py`

### Option 2: Configuration + Command Line Override
1. Update defaults in the script
2. Override specific values: `python standalone_sql_preview.py --nl-definition "new query" --temperature 0.1`

## 📊 Example Configuration

Here's your exact configuration ready to use:

```python
# =============================================================================
# CONFIGURATION - UPDATE THESE VALUES AND RUN THE SCRIPT
# =============================================================================

# Natural Language Definition
NL_DEFINITION = "get products from hana_material_master where OPS_PLANNER is missing"

# Knowledge Graph Settings
KG_NAME = "KG_Test_001"
SELECT_SCHEMA = "newdqnov7"

# OpenAI Settings
OPENAI_KEY = "Test"
TEMPERATURE = 0

# Database Settings
DB_HOST = "DESKTOP-41O1AL9\\LOCALHOST"
DB_PORT = 1433
DB_NAME = "NewDQ"
DB_USER = "mithun"
DB_PASSWORD = "mithun123"

# Script Settings
USE_LLM = True
VERBOSE = True
OUTPUT_FILE = None
```

## 🎯 Benefits of Configuration-Based Approach

### ✅ **Easier to Use**
- No need to remember long command line arguments
- Just edit the file once and run multiple times
- Perfect for development and testing

### ✅ **Version Control Friendly**
- Create different configuration files for different environments
- Easy to share configurations with team members
- Track configuration changes in git

### ✅ **Less Error-Prone**
- No typos in command line arguments
- Configuration is validated when the script loads
- Clear separation of config and logic

### ✅ **Still Flexible**
- Full version still supports command line overrides
- Easy to switch between different configurations
- Can create multiple copies with different settings

## 🔄 Migration from Command Line

### Before (Command Line):
```bash
python standalone_sql_preview.py \
     --nl-definition "get products from hana_material_master where OPS_PLANNER is missing" \
     --kg-name "KG_Test_001" \
     --select-schema "newdqnov7" \
     --openai-key "sk-proj-..." \
     --temperature 0 \
     --db-host "DESKTOP-41O1AL9\LOCALHOST" \
     --db-name "NewDQ" \
     --db-user "mithun" \
     --db-password "mithun123" \
     --use-llm \
     --verbose
```

### After (Configuration):
1. Update the config in the script file
2. Run: `python sql_preview_simple.py`

## 📝 Multiple Configurations

You can create multiple configuration files for different scenarios:

```bash
# Copy the simple script for different use cases
cp sql_preview_simple.py sql_preview_production.py
cp sql_preview_simple.py sql_preview_testing.py
cp sql_preview_simple.py sql_preview_development.py

# Edit each file with different configurations
# Then run the appropriate one:
python sql_preview_production.py
python sql_preview_testing.py
```

## 🛠️ Installation

Same as before:
```bash
pip install -r requirements_sql_preview.txt
```

## 🎉 Ready to Use!

Both scripts are ready to use with your exact configuration. The simple version (`sql_preview_simple.py`) is perfect for your use case - just update the config at the top and run it!
