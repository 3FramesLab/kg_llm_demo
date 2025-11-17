#!/bin/bash

# Unix Shell Script for Running KPI Executor
# Usage: ./run_kpi_executor.sh

echo "================================================================================"
echo "                          STANDALONE KPI EXECUTOR"
echo "================================================================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "ERROR: Python is not installed or not in PATH"
        echo "Please install Python 3.7+ and try again"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

echo "Using Python: $PYTHON_CMD"

# Check if required files exist
if [ ! -f "kpi_executor_standalone.py" ]; then
    echo "ERROR: kpi_executor_standalone.py not found"
    echo "Please ensure the script file is in the current directory"
    exit 1
fi

if [ ! -f "requirements_standalone.txt" ]; then
    echo "ERROR: requirements_standalone.txt not found"
    echo "Please ensure the requirements file is in the current directory"
    exit 1
fi

# Install dependencies if needed
echo "Checking Python dependencies..."
if ! $PYTHON_CMD -c "import pyodbc" &> /dev/null; then
    echo "Installing Python dependencies..."
    pip install -r requirements_standalone.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install dependencies"
        exit 1
    fi
fi

echo "Dependencies OK"
echo

# Set default values (modify these as needed)
DEFAULT_KG_NAME="default"
DEFAULT_DB_HOST="localhost"
DEFAULT_DB_PORT="1433"
DEFAULT_DB_NAME="KPI_Analytics"
DEFAULT_SCHEMA="newdqschemanov"
DEFAULT_LIMIT="1000"
DEFAULT_TEMPERATURE="0.0"
DEFAULT_KPI_ID="19"

# Function to read input with default value
read_with_default() {
    local prompt="$1"
    local default="$2"
    local var_name="$3"
    
    if [ -n "$default" ]; then
        read -p "$prompt [$default]: " input
        if [ -z "$input" ]; then
            input="$default"
        fi
    else
        read -p "$prompt: " input
    fi
    
    eval "$var_name='$input'"
}

# Prompt for required parameters
echo "Please provide the following required parameters:"
echo

read -p "OpenAI API Key: " OPENAI_KEY
if [ -z "$OPENAI_KEY" ]; then
    echo "ERROR: OpenAI API Key is required"
    exit 1
fi

read -p "Database Username: " DB_USER
if [ -z "$DB_USER" ]; then
    echo "ERROR: Database Username is required"
    exit 1
fi

read -s -p "Database Password: " DB_PASSWORD
echo
if [ -z "$DB_PASSWORD" ]; then
    echo "ERROR: Database Password is required"
    exit 1
fi

echo
echo "Optional parameters (press Enter for defaults):"
echo

read_with_default "KG Name" "$DEFAULT_KG_NAME" "KG_NAME"
read_with_default "Database Host" "$DEFAULT_DB_HOST" "DB_HOST"
read_with_default "Database Port" "$DEFAULT_DB_PORT" "DB_PORT"
read_with_default "Database Name" "$DEFAULT_DB_NAME" "DB_NAME"
read_with_default "KPI ID" "$DEFAULT_KPI_ID" "KPI_ID"
read_with_default "Select Schema" "$DEFAULT_SCHEMA" "SCHEMA"
read_with_default "Limit Records" "$DEFAULT_LIMIT" "LIMIT"
read_with_default "Temperature" "$DEFAULT_TEMPERATURE" "TEMPERATURE"
read_with_default "Output File (optional)" "" "OUTPUT_FILE"
read_with_default "Verbose logging? (y/N)" "N" "VERBOSE"

echo
echo "================================================================================"
echo "                              EXECUTION SUMMARY"
echo "================================================================================"
echo "KPI ID: $KPI_ID"
echo "KG Name: $KG_NAME"
echo "Database: $DB_HOST:$DB_PORT/$DB_NAME"
echo "Schema: $SCHEMA"
echo "Limit: $LIMIT"
echo "Temperature: $TEMPERATURE"
if [ -n "$OUTPUT_FILE" ]; then
    echo "Output File: $OUTPUT_FILE"
fi
echo "================================================================================"
echo

read -p "Proceed with execution? (Y/n): " CONFIRM
if [[ "$CONFIRM" =~ ^[Nn]$ ]]; then
    echo "Execution cancelled"
    exit 0
fi

# Build command
CMD="$PYTHON_CMD kpi_executor_standalone.py --openai-key \"$OPENAI_KEY\" --kg-name \"$KG_NAME\" --db-host \"$DB_HOST\" --db-port $DB_PORT --db-name \"$DB_NAME\" --db-user \"$DB_USER\" --db-password \"$DB_PASSWORD\" --kpi-id $KPI_ID --select-schema \"$SCHEMA\" --limit-records $LIMIT --temperature $TEMPERATURE"

if [ -n "$OUTPUT_FILE" ]; then
    CMD="$CMD --output-file \"$OUTPUT_FILE\""
fi

if [[ "$VERBOSE" =~ ^[Yy]$ ]]; then
    CMD="$CMD --verbose"
fi

echo
echo "Executing KPI..."
echo

# Execute the command
eval $CMD

echo
echo "================================================================================"
echo "Execution completed. Check the output above for results."
echo "================================================================================"
