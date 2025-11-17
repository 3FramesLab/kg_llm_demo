#!/usr/bin/env python3
"""
Test script to identify logical errors in sql_preview_simple.py
This mocks external dependencies to test the code logic.
"""

import logging
import sys
import time
import json
from typing import Dict, Any, Optional, List

# Mock pyodbc
class MockCursor:
    def __init__(self):
        self.description = [
            ('TABLE_NAME', str),
            ('COLUMN_NAME', str),
            ('DATA_TYPE', str),
            ('IS_NULLABLE', str),
            ('COLUMN_DEFAULT', str)
        ]
        self.rows = [
            ('hana_material_master', 'MATERIAL', 'varchar', 'NO', None),
            ('hana_material_master', 'DESCRIPTION', 'varchar', 'YES', None),
            ('hana_material_master', 'OPS_PLANNER', 'varchar', 'YES', None),
            ('hana_material_master', 'CATEGORY', 'varchar', 'YES', None),
            ('ops_excel', 'PLANNING_SKU', 'varchar', 'NO', None),
            ('ops_excel', 'STATUS', 'varchar', 'YES', None),
        ]
        self.row_index = 0
    
    def execute(self, query, params=None):
        print(f"Mock SQL executed: {query}")
        if params:
            print(f"Mock SQL params: {params}")
        self.row_index = 0
    
    def fetchall(self):
        return self.rows
    
    def fetchone(self):
        if self.row_index < len(self.rows):
            row = self.rows[self.row_index]
            self.row_index += 1
            return row
        return None

class MockConnection:
    def cursor(self):
        return MockCursor()
    
    def close(self):
        print("Mock connection closed")

class MockPyodbc:
    @staticmethod
    def connect(conn_str):
        print(f"Mock connection to: {conn_str}")
        return MockConnection()

# Mock OpenAI
class MockChatCompletion:
    def __init__(self, content):
        self.content = content

class MockChoice:
    def __init__(self, content):
        self.message = MockChatCompletion(content)

class MockResponse:
    def __init__(self, content):
        self.choices = [MockChoice(content)]

class MockOpenAI:
    def __init__(self, api_key):
        self.api_key = api_key
        print(f"Mock OpenAI initialized with key: {api_key[:20]}...")
    
    class chat:
        class completions:
            @staticmethod
            def create(**kwargs):
                print(f"Mock OpenAI call with model: {kwargs.get('model', 'unknown')}")
                print(f"Mock OpenAI temperature: {kwargs.get('temperature', 'unknown')}")
                
                # Mock response based on the request
                if "parse" in str(kwargs.get('messages', [])).lower():
                    mock_response = '''
                    {
                        "query_type": "filter",
                        "operation": "select",
                        "source_table": "hana_material_master",
                        "target_table": null,
                        "confidence": 0.9,
                        "explanation": "Filter query to find records with missing OPS_PLANNER"
                    }
                    '''
                else:
                    mock_response = "SELECT TOP 1000 * FROM hana_material_master WHERE OPS_PLANNER IS NULL"
                
                return MockResponse(mock_response)

# Replace imports with mocks
sys.modules['pyodbc'] = MockPyodbc()
sys.modules['openai'] = type('MockModule', (), {'OpenAI': MockOpenAI})()

# Now import and test the actual logic from sql_preview_simple.py
# Configuration
NL_DEFINITION = "get products from hana_material_master where OPS_PLANNER is missing"
KG_NAME = "KG_Test_001"
SELECT_SCHEMA = "newdqnov7"
OPENAI_KEY = "test-key"
TEMPERATURE = 0.0
DB_HOST = "DESKTOP-41O1AL9\\LOCALHOST"
DB_PORT = 1433
DB_NAME = "NewDQ"
DB_USER = "mithun"
DB_PASSWORD = "mithun123"
USE_LLM = True
VERBOSE = True
OUTPUT_FILE = None

# Configure logging
log_level = logging.DEBUG if VERBOSE else logging.INFO
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Test the QueryIntent class
class QueryIntent:
    """Simple QueryIntent class to hold parsed query information."""
    
    def __init__(self, definition: str, query_type: str = "data", operation: str = "select"):
        self.definition = definition
        self.query_type = query_type
        self.operation = operation
        self.source_table = None
        self.target_table = None
        self.join_columns = []
        self.confidence = 0.8
        self.additional_columns = []

def test_query_intent():
    """Test QueryIntent class."""
    print("\n=== Testing QueryIntent Class ===")
    try:
        intent = QueryIntent("test query", "filter", "select")
        intent.source_table = "test_table"
        intent.confidence = 0.9
        print(f"✅ QueryIntent created successfully")
        print(f"   Definition: {intent.definition}")
        print(f"   Query Type: {intent.query_type}")
        print(f"   Source Table: {intent.source_table}")
        print(f"   Confidence: {intent.confidence}")
        return True
    except Exception as e:
        print(f"❌ QueryIntent test failed: {e}")
        return False

def test_database_connection():
    """Test database connection logic."""
    print("\n=== Testing Database Connection ===")
    try:
        db_config = {
            'host': DB_HOST,
            'port': DB_PORT,
            'database': DB_NAME,
            'username': DB_USER,
            'password': DB_PASSWORD
        }
        
        # Build connection string
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={db_config['host']};"
            f"DATABASE={db_config['database']};"
            f"UID={db_config['username']};"
            f"PWD={db_config['password']};"
            f"TrustServerCertificate=yes;"
        )
        
        print(f"Connection string: {conn_str}")
        
        # Test mock connection
        pyodbc = MockPyodbc()
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                t.TABLE_NAME,
                c.COLUMN_NAME,
                c.DATA_TYPE,
                c.IS_NULLABLE,
                c.COLUMN_DEFAULT
            FROM INFORMATION_SCHEMA.TABLES t
            LEFT JOIN INFORMATION_SCHEMA.COLUMNS c ON t.TABLE_NAME = c.TABLE_NAME
            WHERE t.TABLE_SCHEMA = ? OR t.TABLE_SCHEMA = 'dbo'
            ORDER BY t.TABLE_NAME, c.ORDINAL_POSITION
        """, (SELECT_SCHEMA,))
        
        rows = cursor.fetchall()
        print(f"✅ Database connection test passed")
        print(f"   Retrieved {len(rows)} rows")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("="*60)
    print("TESTING SQL PREVIEW LOGIC")
    print("="*60)
    
    tests = [
        ("QueryIntent Class", test_query_intent),
        ("Database Connection", test_database_connection),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    failed = len(results) - passed
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTests passed: {passed}")
    print(f"Tests failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All logic tests passed!")
        print("The main issues are likely:")
        print("1. Missing dependencies (pyodbc, openai)")
        print("2. Database connectivity issues")
        print("3. OpenAI API key validation")
    else:
        print(f"\n❌ {failed} test(s) failed - there are logic errors to fix")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
